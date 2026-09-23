#!/usr/bin/env python3
"""Refuse an integration merge over a dirty primary checkout (phase-conc-02).

Run before `git merge --ff-only agent/<phase-id>` in step 9 of AGENTS.md's *Concurrent
agents: complete and hand off* section:

    uv run python tools/git-hooks/refuse_dirty_integration.py

It is a pre-merge script, not a git hook — it lives under `tools/git-hooks/` alongside the
repository's other git-adjacent tooling (`pre-commit`), not because git invokes it. Git has
no event that fires on `git stash`, so there is nothing to hook there (see the design note
in `OPS-001-operations.md`). The integration step is the one place this failure is actually
preventable, and it is where this script is meant to run — by hand, or wired into whatever
runs the merge.

Two independent checks, either of which refuses:

1. **A dirty working tree.** `git status --porcelain` in the primary checkout names every
   staged, unstaged and untracked path. Any of them blocks the merge; they are named in
   the refusal so the operator knows what they would be overwriting or discarding.

2. **A non-empty stash.** This is what makes the refusal survive `git stash`: a peer's
   uncommitted work stashed away still shows as a clean working tree, but the stash entry
   itself is the evidence that work is in flight. Refusing on a non-empty stash, not just
   a dirty tree, is what stops an agent from doing exactly what caused the 000041
   incident — stashing a peer's changes to make the checkout look mergeable.

The integration branch is configuration, not a hard-coded name: pass `--integration-branch`
or set `D_SYSTEM_INTEGRATION_BRANCH`. It defaults to `dev`, today's integration branch
(see AGENTS.md's *Concurrent agents: claim a phase* section), and is used only to name the
branch in the refusal message — this script does not need to switch to it or diff against
it, since the check is "is the checkout clean", not "is dev ahead".

Exit code 0 means the checkout is clean and the merge may proceed. Exit code 1 means the
integration is refused; the message names every dirty path and every stash entry found.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_INTEGRATION_BRANCH = "dev"


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def find_dirty_paths(repo: Path) -> list[str]:
    """Return every path `git status --porcelain` reports as staged, unstaged or untracked."""
    output = _run_git(repo, "status", "--porcelain")
    paths: list[str] = []
    for line in output.splitlines():
        if not line:
            continue
        # Porcelain format is "XY path" (or "XY orig -> path" for a rename); the path
        # starts after the two status letters and one space.
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def find_stash_entries(repo: Path) -> list[str]:
    """Return every entry in `git stash list`, most recent first, as git prints it."""
    output = _run_git(repo, "stash", "list")
    return [line for line in output.splitlines() if line]


def check(repo: Path, integration_branch: str) -> tuple[bool, str]:
    """Return (refused, message). refused is True when the merge must not proceed."""
    dirty_paths = find_dirty_paths(repo)
    stash_entries = find_stash_entries(repo)

    if not dirty_paths and not stash_entries:
        return False, f"Primary checkout is clean. Integration into '{integration_branch}' is not refused."

    lines = [f"Refused: integration into '{integration_branch}' cannot proceed."]

    if dirty_paths:
        lines.append(f"\n{len(dirty_paths)} uncommitted path(s) in the primary checkout:")
        lines.extend(f"  - {path}" for path in dirty_paths)

    if stash_entries:
        lines.append(
            f"\n{len(stash_entries)} stash entry(ies) in the primary checkout "
            "(git stash does not satisfy this refusal — see below):"
        )
        lines.extend(f"  - {entry}" for entry in stash_entries)

    lines.append(
        "\nCommit or let the owning agent finish before integrating. Stashing someone "
        "else's uncommitted work to clear this refusal is the 000041 incident; do not do it."
    )
    return True, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path to the primary checkout to inspect (default: current directory).",
    )
    parser.add_argument(
        "--integration-branch",
        default=os.environ.get("D_SYSTEM_INTEGRATION_BRANCH", DEFAULT_INTEGRATION_BRANCH),
        help=(
            "Name of the integration branch, used only in the refusal message "
            f"(default: '{DEFAULT_INTEGRATION_BRANCH}', or $D_SYSTEM_INTEGRATION_BRANCH)."
        ),
    )
    args = parser.parse_args(argv)

    refused, message = check(args.repo, args.integration_branch)
    print(message)
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
