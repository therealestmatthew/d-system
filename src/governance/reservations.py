"""Pre-merge reservations for document codes, shared across every worktree of one repository.

`next_code()` is a pure function of *committed* state. That is the defect `SESS-2026-09-08-07`
demonstrates and `REQ-013` R05 forbids: two worktrees that allocate the same kind before either
merges read the same committed state and therefore compute the same code. This repository has
paid for it twice — `5b3848c` and `94f7978` are both renumbers after a session-code collision,
and `65491d4` is the same failure in the idea log.

A reservation has to be visible to the second caller *before the first has merged*, which rules
out every tracked file, `codes.yaml` on `dev` included:

- a worktree cannot check out `dev` at all (`fatal: 'dev' is already used by worktree at ...`),
  so it cannot commit a reservation there even if the protocol allowed it;
- reading `git show dev:docs/08-governance/codes.yaml` returns committed state, which is the
  defect rather than a fix for it;
- `_tmpagent/` is tracked, so a reservation written there is invisible until it merges.

The one location every worktree of a repository already shares, with no commit and no merge, is
the **git common directory** — `git rev-parse --git-common-dir` resolves to the same `.git` from
the primary checkout and from every linked worktree. Reservations live there, untracked, and
never enter history. That also scopes them correctly: a reservation is machine-local state about
work in flight on this machine, and it is meaningless to a fresh clone.

Mutual exclusion is the filesystem's, not ours. Each reservation is one file created with
`O_CREAT | O_EXCL`, which the kernel guarantees to be atomic: of two callers racing for the same
code, exactly one create succeeds and the loser retries with the next candidate. No lock file and
no ordering assumption. A crash between the create and the write leaves an empty file, which still
holds its code — `prune()` falls back to the file's mtime so such a reservation still expires
rather than holding a code forever.

**A reservation is released by time or by hand, never by observing that the document exists.**
Judging a reservation "satisfied" because its code appears on a scanned document was the obvious
rule and it is wrong: `audit()` walks the *local* working tree, so an allocating worktree would
retire its own reservation while the document is still unmerged and invisible to peers — and the
next peer to allocate would be handed the same code, with nothing committed anywhere. That is the
collision this module exists to prevent, reintroduced by its own cleanup. A reservation whose
document has landed is harmless by comparison: it only makes the allocator skip a code that is
genuinely spent.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

#: Directory name under the git common directory. Named for what it holds rather than for this
#: repository, since the common directory is shared by every worktree but by nothing else.
RESERVATION_DIR = "code-reservations"

#: How long an unsatisfied reservation stands before an allocation may prune it. Generous by
#: design: a reservation is normally held for the minutes between `--next-code` and writing the
#: document, so a fortnight only ever collects reservations whose session ended without writing.
#: Documented in `GOV-005`; the wall clock here decides nothing about a code's value, only when an
#: abandoned hole is reclaimed.
TTL_SECONDS = 14 * 24 * 60 * 60

#: Codes are `[A-Z]+` plus digits, dots and hyphens, so they are already safe as filenames. This
#: is asserted rather than assumed — a code that fails it would escape the reservation directory.
_SAFE = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.")


def _common_dir(root: Path) -> Path:
    """The `.git` directory shared by the primary checkout and every linked worktree."""
    completed = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(completed.stdout.strip())


def reservation_dir(root: Path) -> Path:
    """Where reservations live for the repository containing `root`.

    Raises `subprocess.CalledProcessError` outside a git repository, which is deliberate: an
    allocator that silently falls back to no reservations is the defect this module removes.
    """
    return _common_dir(root) / RESERVATION_DIR


def _entries(directory: Path) -> list[tuple[str, dict[str, Any]]]:
    if not directory.is_dir():
        return []
    found = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        try:
            found.append((path.name, json.loads(path.read_text())))
        except (OSError, ValueError):
            # An unreadable reservation still holds its code. Treat it as opaque rather than
            # deleting it: the code it names may already be written into a document somewhere.
            found.append((path.name, {}))
    return found


def active(root: Path) -> set[str]:
    """Every code currently reserved, satisfied or not. Callers prune before relying on this."""
    return {name for name, _ in _entries(reservation_dir(root))}


def _age(directory: Path, name: str, meta: dict[str, Any], moment: float) -> float:
    """How long a reservation has stood, in seconds.

    The stamp inside the file is preferred, but it is not trusted: a reservation written by a
    crashed process is empty, and one edited by hand may hold anything. Either way the file's own
    mtime is a sound lower bound, so a damaged reservation expires on schedule instead of holding
    its code forever.
    """
    stamp = meta.get("at")
    if isinstance(stamp, (int, float)) and not isinstance(stamp, bool):
        return moment - float(stamp)
    try:
        return moment - (directory / name).stat().st_mtime
    except OSError:
        return 0.0


def prune(root: Path, now: float | None = None) -> list[str]:
    """Drop expired reservations; return what was dropped.

    Expiry is the *only* automatic release. See this module's docstring for why "the document
    exists, so the reservation is satisfied" is not a safe rule: it is judged against the local
    working tree, and applying it hands a peer a code that is already spent on an unmerged branch.

    A reservation for a code that has since landed is left standing until it expires. That costs
    nothing — the allocator would skip that code anyway, because the document now carries it.
    """
    directory = reservation_dir(root)
    moment = time.time() if now is None else now
    dropped = []
    for name, meta in _entries(directory):
        if _age(directory, name, meta, moment) > TTL_SECONDS:
            try:
                (directory / name).unlink()
            except FileNotFoundError:
                # A peer pruned the same reservation between listing and unlinking. Both agree it
                # should go, so there is nothing to reconcile.
                continue
            dropped.append(name)
    return dropped


def reserve(root: Path, code: str, holder: str | None = None) -> bool:
    """Claim `code` atomically. True when this caller won it, False when a peer already holds it.

    `O_CREAT | O_EXCL` is the whole mechanism: the kernel admits exactly one creator, so two
    callers racing for one code cannot both be told they have it.
    """
    _check(code, "reserve")
    directory = reservation_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"code": code, "at": time.time(), "holder": holder or _holder(root)},
        sort_keys=True,
    )
    try:
        handle = os.open(directory / code, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(handle, "w") as stream:
        stream.write(payload)
    return True


def release(root: Path, code: str) -> bool:
    """Drop one reservation by name. True when it existed, False when it did not.

    Validated on exactly the same terms as `reserve()`. The asymmetry is worth naming because it
    was there and it was the dangerous way round: `reserve()` only ever *creates* a file, while
    this function *unlinks* one, and it took operator input from `--release-code` straight through
    to `unlink`. `../config` would have removed the repository's git config.
    """
    _check(code, "release")
    try:
        (reservation_dir(root) / code).unlink()
    except FileNotFoundError:
        return False
    return True


def _check(code: str, verb: str) -> None:
    """Reject anything that is not a bare code before it is used as a filename.

    `.` and `..` are excluded explicitly: both are built entirely from permitted characters, so a
    character-set test alone lets them through to name a directory rather than a reservation.
    """
    if not code or code in {".", ".."} or not set(code) <= _SAFE:
        raise ValueError(f"refusing to {verb} malformed code {code!r}")


def _holder(root: Path) -> str:
    """The branch and worktree a reservation was taken from, for the report and for triage."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = completed.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        branch = "unknown"
    return f"{branch} @ {root}"
