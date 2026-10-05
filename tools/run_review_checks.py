#!/usr/bin/env python3
"""Run a phase's declared checks at one commit in a detached worktree and record the evidence.

The build-review runner (REQ-030 R02, PLAN-047 D2). It takes a phase id and a commit and nothing
else:

    uv run python tools/run_review_checks.py <phase-id> <commit>

It reads the phase's `verification` list from `dev`'s `docs/09-backlog/backlog.yaml` (never from
the commit under review, so a branch cannot weaken its own list), creates a detached temporary
worktree at the commit, installs the environment there with `uv sync --extra dev`, and runs:

- each `verification` entry that is a command, in the order the backlog lists it;
- then each of the four GOV-017 gate checks that the list does not already contain.

An entry is a command when its first word, after any `NAME=value` assignments, is `cd` or a
program found on PATH. Any other entry is prose and is listed as not run. Commands run through
`bash -c` in the worktree with no stdin, one at a time, each limited to 30 minutes; a command that
hits the limit is killed and recorded as exit 124. A failing command is recorded with its exit code
and never retried.

Each command's combined stdout and stderr is written to its own evidence file under
`_working/review-checks/<phase-id>/<commit12>/` in the checkout running the tool, replacing the
previous run's files for that phase and commit. The manifest (command, exit code, file path,
sha256) is printed and written there as `manifest.json`. The worktree is removed afterwards,
whether the commands passed, failed or the run was interrupted.

Exit codes: 0 when every command that ran exited 0; 1 when any command failed or timed out; 2 when
the run is refused (unknown phase id, unresolvable commit, an extra argument, no readable `dev`
backlog, or the worktree could not be created) or an operating-system error stopped it partway.
A refused run leaves the previous evidence for that phase and commit untouched.

See REQ-030 R02 and PLAN-047 D2 (docs/01-plans/PLAN-047-reviewer-contract.md), phase-asr-02.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parent.parent

BACKLOG = "docs/09-backlog/backlog.yaml"
BACKLOG_REF = "dev"
EVIDENCE_DIR = Path("_working") / "review-checks"
WORKTREES = "d-system-worktrees"  # a sibling of the primary checkout, as AGENTS.md places them

# GOV-017's merge gate, step 1.
GATE_CHECKS = (
    "uv run python -m src.governance",
    "uv run pytest",
    "uv run ruff check src/ test/ tools/",
    "uv run mypy src/",
)
SETUP = ("uv sync --extra dev",)
TIMEOUT_SECONDS = 30 * 60
TIMEOUT_EXIT = 124

PHASE_ID = re.compile(r"^phase-[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


class Refused(Exception):
    """The run cannot start; nothing was created."""


@dataclass
class Entry:
    kind: str  # setup, verification, gate, or verification+gate
    command: str
    ran: bool
    exit_code: int | None = None
    file: str | None = None
    sha256: str | None = None
    note: str | None = None


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )


def resolve_commit(repo: Path, commit: str) -> str:
    result = _git(repo, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
    sha = result.stdout.strip()
    if result.returncode != 0 or not sha:
        raise Refused(f"commit {commit!r} does not resolve in {repo}")
    return sha


def load_phase(repo: Path, phase_id: str) -> tuple[dict[str, Any], str]:
    """The phase as `dev`'s backlog declares it, and the `dev` commit it was read from."""
    if not PHASE_ID.match(phase_id):
        raise Refused(f"{phase_id!r} is not a phase id")
    ref = _git(repo, "rev-parse", "--verify", "--quiet", f"{BACKLOG_REF}^{{commit}}")
    if ref.returncode != 0:
        raise Refused(f"{BACKLOG_REF} does not resolve in {repo}")
    shown = _git(repo, "show", f"{BACKLOG_REF}:{BACKLOG}")
    if shown.returncode != 0:
        raise Refused(f"{BACKLOG_REF} has no {BACKLOG}")
    try:
        backlog = yaml.safe_load(shown.stdout) or {}
    except yaml.YAMLError as exc:
        raise Refused(f"{BACKLOG_REF}'s {BACKLOG} is not valid YAML: {exc}") from exc
    items = (backlog.get("items") or []) if isinstance(backlog, dict) else []
    for item in items:
        if isinstance(item, dict) and item.get("id") == phase_id:
            return item, ref.stdout.strip()
    raise Refused(f"unknown phase id {phase_id!r}: not in {BACKLOG_REF}'s {BACKLOG}")


def is_command(entry: str) -> bool:
    """True when the entry's first word, past any NAME=value, is `cd` or a program on PATH."""
    words = entry.split()
    while words and ASSIGNMENT.match(words[0]):
        words.pop(0)
    if not words:
        return False
    return words[0] == "cd" or shutil.which(words[0]) is not None


def plan(
    verification: Sequence[str], gate_checks: Sequence[str], setup: Sequence[str]
) -> list[Entry]:
    """Every entry in run order: setup, the verification list, then gate checks not yet listed."""
    entries = [Entry("setup", command, ran=False) for command in setup]
    listed = set()
    for command in verification:
        kind = "verification+gate" if command in gate_checks else "verification"
        entries.append(Entry(kind, command, ran=False))
        listed.add(command)
    entries += [
        Entry("gate", command, ran=False) for command in gate_checks if command not in listed
    ]
    for entry in entries:
        if not is_command(entry.command):
            entry.note = "not run: not a command"
    return entries


def _environment() -> dict[str, str]:
    """The caller's environment minus its virtualenv, so `uv run` uses the worktree's own."""
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)
    return env


def execute(command: str, cwd: Path, timeout: float) -> tuple[int, bytes, bool]:
    """Run once through bash; return exit code, combined output, and whether it timed out."""
    with subprocess.Popen(
        ["bash", "-c", command],
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=_environment(),
        start_new_session=True,
    ) as process:
        try:
            output, _ = process.communicate(timeout=timeout)
            return process.returncode, output, False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
            return TIMEOUT_EXIT, output, True


def default_worktree_parent(repo: Path) -> Path:
    """`../d-system-worktrees` beside the primary checkout, whichever checkout runs the tool."""
    common = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return Path(common).parent.parent / WORKTREES


def add_worktree(repo: Path, sha: str, parent: Path, phase_id: str) -> Path:
    try:
        parent.mkdir(parents=True, exist_ok=True)
        path = Path(tempfile.mkdtemp(prefix=f"review-{phase_id}-{sha[:12]}-", dir=parent))
    except OSError as exc:
        raise Refused(f"could not create a worktree directory under {parent}: {exc}") from exc
    result = _git(repo, "worktree", "add", "--detach", str(path), sha)
    if result.returncode != 0:
        shutil.rmtree(path, ignore_errors=True)
        raise Refused(f"git worktree add failed: {(result.stderr or result.stdout).strip()}")
    return path


def remove_worktree(repo: Path, path: Path) -> None:
    _git(repo, "worktree", "remove", "--force", str(path))
    shutil.rmtree(path, ignore_errors=True)
    _git(repo, "worktree", "prune")


def run(
    phase_id: str,
    commit: str,
    *,
    repo: Path = ROOT,
    gate_checks: Sequence[str] = GATE_CHECKS,
    setup: Sequence[str] = SETUP,
    worktree_parent: Path | None = None,
    timeout: float = TIMEOUT_SECONDS,
) -> tuple[int, dict[str, Any]]:
    """Run the phase's checks at the commit; return the exit code and the manifest."""
    phase, dev_sha = load_phase(repo, phase_id)
    sha = resolve_commit(repo, commit)
    entries = plan(phase.get("verification") or [], gate_checks, setup)

    parent = worktree_parent or default_worktree_parent(repo)
    worktree = add_worktree(repo, sha, parent, phase_id)
    # The previous run's evidence is replaced only once this run is certain to start.
    evidence = repo / EVIDENCE_DIR / phase_id / sha[:12]
    try:
        shutil.rmtree(evidence, ignore_errors=True)
        evidence.mkdir(parents=True)
        for number, entry in enumerate(entries, start=1):
            if entry.note is not None:
                continue
            code, output, timed_out = execute(entry.command, worktree, timeout)
            if timed_out:
                output += f"\n[run_review_checks: killed after {timeout:g} s]\n".encode()
                entry.note = "timed out"
            path = evidence / f"{number:02d}-{entry.kind}.txt"
            path.write_bytes(output)
            entry.ran = True
            entry.exit_code = code
            entry.file = path.relative_to(repo).as_posix()
            entry.sha256 = hashlib.sha256(output).hexdigest()
    finally:
        remove_worktree(repo, worktree)

    failed = any(entry.ran and entry.exit_code != 0 for entry in entries)
    manifest: dict[str, Any] = {
        "phase": phase_id,
        "commit": sha,
        "backlog": f"{BACKLOG_REF} {dev_sha}",
        "result": "failed" if failed else "passed",
        "entries": [asdict(entry) for entry in entries],
    }
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return (1 if failed else 0), manifest


def render(manifest: dict[str, Any]) -> str:
    lines = [
        f"phase {manifest['phase']} at {manifest['commit']} "
        f"(verification list from {manifest['backlog']}): {manifest['result']}",
        "",
        "| # | Kind | Command | Exit | File | sha256 |",
        "|---|---|---|---|---|---|",
    ]
    for number, entry in enumerate(manifest["entries"], start=1):
        exit_text = "—" if entry["exit_code"] is None else str(entry["exit_code"])
        if entry["note"]:
            exit_text = f"{exit_text} ({entry['note']})"
        lines.append(
            f"| {number} | {entry['kind']} | `{entry['command']}` | {exit_text} | "
            f"{entry['file'] or '—'} | {entry['sha256'] or '—'} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("phase_id", help="a phase id in dev's backlog, e.g. phase-asr-02")
    parser.add_argument("commit", help="the commit to check out and run the checks at")
    args = parser.parse_args(argv)
    try:
        code, manifest = run(args.phase_id, args.commit)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        # The worktree is already removed by run()'s cleanup; no manifest was written.
        print(f"stopped: {exc}", file=sys.stderr)
        return 2
    print(render(manifest))
    return code


if __name__ == "__main__":
    sys.exit(main())
