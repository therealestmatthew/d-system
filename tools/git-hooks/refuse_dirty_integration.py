#!/usr/bin/env python3
"""Refuse an integration merge over a dirty primary checkout (phase-conc-02).

Run by hand, in the primary checkout, immediately before
`git merge --ff-only agent/<phase-id>`:

    uv run python tools/git-hooks/refuse_dirty_integration.py

Nothing invokes this automatically yet — see the placement note in `OPS-001-operations.md`
for exactly what is and is not wired up today.

It is a pre-merge script, not a git hook — it lives under `tools/git-hooks/` alongside the
repository's other git-adjacent tooling (`pre-commit`), not because git invokes it. Git has
no event that fires on `git stash`, so there is nothing to hook there (see the design note
in `OPS-001-operations.md`). The integration step is the one place this failure is actually
preventable, and it is where this script is meant to run — by hand, or wired into whatever
runs the merge.

However it is invoked, it always inspects the **primary checkout**, never whatever path or
worktree it happens to run from or be pointed at with `--repo`. `--repo` (or the current
directory, if `--repo` is omitted) is resolved to the primary checkout via
`git rev-parse --git-common-dir`: for a non-bare repository, the primary checkout's work
tree is that common `.git` directory's parent, the same value from every worktree the
repository has (`resolve_primary_checkout`). This is deliberate — an agent could otherwise
run the guard against its own feature worktree by mistake (sibling paths are similar and
easy to transpose) and see a false "not refused" while the actual primary checkout, which
is what the merge lands on, is dirty.

Two independent checks against the primary checkout, either of which refuses:

1. **A dirty working tree.** `git status --porcelain` names every staged, unstaged and
   untracked path. Any of them blocks the merge; they are named in the refusal so the
   operator knows what they would be overwriting or discarding.

2. **A non-empty stash.** This is deliberate, not a side effect: "clean" for this guard
   means no working-tree changes *and* no stash entries, because a stash sitting in the
   primary checkout is itself uncommitted work — the same class of thing `AGENTS.md`'s
   hand-off procedure means by "never stash a peer's uncommitted work." A peer's dirty
   file stashed away still shows a clean working tree to check 1 alone, so refusing on the
   stash too is what stops an agent from stashing a peer's changes to make the checkout
   look mergeable, which is the `000041` incident. One consequence accepted deliberately:
   a single pre-existing, unrelated stash blocks every future integration until its owner
   restores and commits it, or drops it — see `OPS-001-operations.md` for the tradeoff.

The integration branch is configuration, not a hard-coded name: pass `--integration-branch`
or set `D_SYSTEM_INTEGRATION_BRANCH`. It defaults to `dev`, today's integration branch
(see AGENTS.md's *Concurrent agents: claim a phase* section), and is used only to name the
branch in the refusal message — this script does not need to switch to it or diff against
it, since the check is "is the checkout clean", not "is dev ahead".

Exit code 0 means the primary checkout is clean (no dirty paths, no stash entries) and the
merge may proceed. Exit code 1 means the integration is refused; the message names every
dirty path and every stash entry found, and states plainly that a stash entry counts as
uncommitted work that must be restored and committed, or dropped, before integrating.
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


def resolve_primary_checkout(repo: Path) -> Path:
    """The primary checkout's work tree, whatever worktree or subdirectory `repo` names.

    `git rev-parse --git-common-dir` returns the same `.git` directory for the primary
    checkout and every linked worktree of one repository. For a non-bare repository that
    directory's parent is the primary checkout's work tree — this is true whether `repo`
    already *is* the primary checkout (where the common dir is simply `repo/.git`) or a
    linked worktree (where git reports the common dir's real, absolute location inside the
    primary checkout).
    """
    common_dir = _run_git(repo, "rev-parse", "--git-common-dir").strip()
    common_path = Path(common_dir)
    if not common_path.is_absolute():
        common_path = (repo / common_path).resolve()
    else:
        common_path = common_path.resolve()
    return common_path.parent


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
    """Return (refused, message). refused is True when the merge must not proceed.

    `repo` is resolved to the primary checkout before either check runs, so the result is
    the same regardless of which worktree or subdirectory `repo` names.
    """
    primary = resolve_primary_checkout(repo)
    dirty_paths = find_dirty_paths(primary)
    stash_entries = find_stash_entries(primary)

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
            "\nA stash entry counts as uncommitted work. Restore and commit it, or have its "
            "owner drop it deliberately, before integrating — do not pop it yourself to clear "
            "this refusal."
        )

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
        help=(
            "Path to inspect (default: current directory) -- resolved to the primary "
            "checkout regardless of which worktree or subdirectory it names."
        ),
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
