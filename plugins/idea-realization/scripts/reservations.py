# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Pre-merge reservations for document codes, shared by every worktree of one repository.

Allocating a code from committed state alone is not enough: two worktrees that allocate the same
kind before either merges read the same committed state and compute the same code, and the
second discovers the collision only at merge. A reservation has to be visible to the second
caller before the first has merged, which rules out every tracked file, the code register
included: a reservation committed on one branch is invisible on another until it merges.

The one location every worktree of a repository already shares, with no commit and no merge, is
the git common directory: ``git rev-parse --git-common-dir`` resolves to the same ``.git`` from
the primary checkout and from every linked worktree. Reservations live there, untracked, and
never enter history. A reservation is machine-local state about work in flight, meaningless to a
fresh clone.

Mutual exclusion is the filesystem's. Each reservation is one file created with
``O_CREAT | O_EXCL``, which the kernel guarantees to be atomic: of two callers racing for the
same code, exactly one create succeeds and the loser tries the next candidate. A crash between the
create and the write leaves an empty file, which still holds its code; ``prune`` falls back to the
file's mtime so such a reservation still expires.

**A reservation is released by time or by hand, never by observing that the document exists.**
The document scan reads the local working tree, so an allocating worktree would retire its own
reservation while its document is still unmerged and invisible to peers, and the next peer would
be handed the same code. A reservation whose document has landed costs nothing: the allocator
skips that code anyway.

Run directly, this script lists the reservations held, or releases one that ``next-code`` took
for a document that will never be written.

Exit codes: 0 on success; 1 when ``--release`` names a code no reservation holds, or outside a
git repository; 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import paths

#: Directory name under the git common directory.
RESERVATION_DIR = "code-reservations"

#: How long an unreleased reservation stands before an allocation prunes it. A reservation is
#: normally held for the minutes between ``next-code`` and writing the document, so a fortnight
#: only ever collects reservations whose session ended without writing one.
TTL_SECONDS = 14 * 24 * 60 * 60

#: Codes are ``[A-Z]+`` plus digits, dots and hyphens, so they are already safe as filenames.
#: This is asserted rather than assumed: a code that fails it would escape the directory.
_SAFE = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.")


def _common_dir(root: Path) -> Path:
    """The ``.git`` directory shared by the primary checkout and every linked worktree."""
    completed = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    return Path(completed.stdout.strip())


def reservation_dir(root: Path) -> Path:
    """Where reservations live for the repository containing ``root``.

    Raises ``subprocess.CalledProcessError`` outside a git repository, deliberately: an allocator
    that silently falls back to no reservations is the defect this module removes.
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
    """Every code currently reserved. Callers prune before relying on this."""
    return {name for name, _ in _entries(reservation_dir(root))}


def _age(directory: Path, name: str, meta: dict[str, Any], moment: float) -> float:
    """How long a reservation has stood, in seconds.

    The stamp inside the file is preferred but not trusted: a reservation written by a crashed
    process is empty, and one edited by hand may hold anything. The file's own mtime is a sound
    lower bound either way, so a damaged reservation still expires on schedule.
    """
    stamp = meta.get("at")
    if isinstance(stamp, (int, float)) and not isinstance(stamp, bool):
        return moment - float(stamp)
    try:
        return moment - (directory / name).stat().st_mtime
    except OSError:
        return 0.0


def prune(root: Path, now: float | None = None) -> list[str]:
    """Drop expired reservations; return what was dropped. Expiry is the only automatic release."""
    directory = reservation_dir(root)
    moment = time.time() if now is None else now
    dropped = []
    for name, meta in _entries(directory):
        if _age(directory, name, meta, moment) > TTL_SECONDS:
            try:
                (directory / name).unlink()
            except FileNotFoundError:
                # A peer pruned the same reservation between listing and unlinking.
                continue
            dropped.append(name)
    return dropped


def reserve(root: Path, code: str, holder: str | None = None) -> bool:
    """Claim ``code`` atomically. True when this caller won it, False when a peer holds it."""
    _check(code, "reserve")
    directory = reservation_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"code": code, "at": time.time(), "holder": holder or _holder(root)}, sort_keys=True
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

    Validated on exactly the same terms as ``reserve``: this function unlinks a file named by
    operator input, so ``../config`` must never reach ``unlink``.
    """
    _check(code, "release")
    try:
        (reservation_dir(root) / code).unlink()
    except FileNotFoundError:
        return False
    return True


def _check(code: str, verb: str) -> None:
    """Reject anything that is not a bare code before it is used as a filename.

    ``.`` and ``..`` are built entirely from permitted characters, so they are excluded by name.
    """
    if not code or code in {".", ".."} or not set(code) <= _SAFE:
        raise ValueError(f"refusing to {verb} malformed code {code!r}")


def _holder(root: Path) -> str:
    """The branch and worktree a reservation was taken from, for the listing."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        branch = "unknown"
    return f"{branch} @ {root}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="release-code",
        description="List the pre-merge code reservations held under the git common directory, "
                    "or release one taken by next-code for a document that will not be written.",
    )
    parser.add_argument("code", nargs="?", help="the code to release; omit to list reservations")
    paths.add_arguments(parser, [])
    args = parser.parse_args(argv)
    root = paths.repository_root(args.root)
    try:
        if args.code is None:
            entries = _entries(reservation_dir(root))
            for name, meta in entries:
                print(f"{name}  {meta.get('holder', 'unknown holder')}")
            if not entries:
                print("no reservations held")
            return 0
        if release(root, args.code):
            print(f"released {args.code}")
            return 0
        print(f"no reservation held for {args.code}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    except subprocess.CalledProcessError:
        print(f"{root} is not inside a git repository", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
