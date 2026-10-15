#!/usr/bin/env python3
"""Fail when a tracked file leaks a confidential identifier or lives under the private directory.

Two identical copies exist: tools/check_confidential.py in the control repository, and the same
path in the product-repository template (templates/product-repo/), so a product repository's hook
and CI can run it without the control repository. It uses only the Python standard library.
Change both copies together; test/test_confidential.py fails when they differ.

Run before committing, or let the pre-commit hook run it:

    python3 tools/check_confidential.py

It checks the index, the content the next commit will carry: each tracked file's staged blob,
read with `git cat-file`, never the copy on disk. A change that is not staged is not checked, and a
staged identifier is caught even if the file on disk was edited back afterwards.

Two checks:

1. **Path check** (always runs). No tracked file may live under the private directory
   (`PRIVATE_DIR`). `.gitignore` stops an ordinary `git add`, but not `git add -f`; this does.

2. **Content check** (runs when the deny-list file exists). The deny-list is an untracked,
   gitignored text file, one identifier per line: client names, account ids, internal project
   names, anything that must never reach a tracked file. Blank lines and lines starting with `#`
   are ignored. Each identifier is matched case-insensitively, on word boundaries, against every
   tracked file's path and text. The file is per machine and is never committed, because a tracked
   list of the identifiers would be the leak it exists to prevent.

   Where the deny-list is read from, first match wins:

   - the path in the `PRIVATE_DENY_LIST` environment variable (CI writes its secret there). If
     the variable is set and the file does not exist, the check fails;
   - `.private/deny-list.txt` in the checkout being committed;
   - `.private/deny-list.txt` in the main checkout, found through `git rev-parse
     --git-common-dir`. A linked worktree has no `.private/` of its own, because the directory is
     untracked, so without this step the content check would be skipped in every worktree.

   When none exists the content check is skipped with a warning on standard error and the check
   still passes, so a developer who does not have the file yet can commit; the path check still
   runs. CI does not reach this case: both workflows (`.github/workflows/control-ci.yml` in the
   control repository and `templates/product-repo/.github/workflows/product-ci.yml` for the
   product repository) fail before the check when the `DENY_LIST` secret is empty, and always set
   `PRIVATE_DENY_LIST` when it is not.

   A deny-list that exists but names no identifier (empty, or only blank lines and comments) fails
   the check. It would otherwise report OK having checked nothing. This is also how CI catches a
   `DENY_LIST` secret that holds only comments, which the workflows' empty-secret test lets through.

3. **Commit message check** (``--message <file>``, run by the ``commit-msg`` hook). The same
   deny-list, matched the same way, against the whole message file git hands the hook, comment
   lines included. A commit message is as permanent and as widely copied as a file, and the
   content check never sees it. Only the deny-list is consulted; the index is not read.

       python3 tools/check_confidential.py --message .git/COMMIT_EDITMSG

4. **Push check** (``--pre-push <remote>``, run by the ``pre-push`` hook, which passes git's
   ref lines on standard input). The commit hooks see only commits made with ``git commit``; a
   rebase, a cherry-pick or ``--no-verify`` skips them. So for every ref being pushed (a deleted
   ref is skipped), every commit the remote does not yet have is checked on its own: its message,
   and each file it adds or changes, by path and by the lines it adds (against its first parent;
   a root commit against nothing). A leak a later commit removed is still refused, because the
   commit that added it is pushed too. A pushed annotated tag's own message is checked as well.
   The commits are those in ``<remote sha>..<local sha>``; for a new ref, or a remote tip this
   clone has not fetched (someone pushed first), those reachable from it and from no ref the
   remote is already known to have (``--not --remotes=<remote>``). A git error fails the push
   with a one-line reason, never a traceback.

       git push   # the hook runs: python3 tools/check_confidential.py --pre-push origin

Exit codes: 0 when nothing leaks; 1 when anything does, or when the deny-list names no
identifier, one line per violation.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRIVATE_DIR = ".private/"
DEFAULT_DENY_LIST = Path(PRIVATE_DIR) / "deny-list.txt"

# A blob with a NUL byte in its first BINARY_PROBE bytes is binary and its content is not scanned.
# Every other blob is scanned, whatever its file name says it is.
BINARY_PROBE = 8000
GITLINK = "160000"


def staged_blobs(root: Path) -> dict[str, str | None]:
    """Every path in the index, mapped to the object id of its staged blob, or None for a
    submodule gitlink, which has a path to check but no content."""
    result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root,
                            capture_output=True, check=True)
    blobs: dict[str, str | None] = {}
    for entry in result.stdout.decode("utf-8", errors="surrogateescape").split("\0"):
        if entry:
            meta, path = entry.split("\t", 1)
            mode, object_id, _stage = meta.split()
            blobs[path] = None if mode == GITLINK else object_id
    return blobs


def read_blobs(root: Path, object_ids: list[str]) -> dict[str, bytes]:
    """The content of each blob, read in one `git cat-file --batch` call."""
    if not object_ids:
        return {}
    unique = list(dict.fromkeys(object_ids))
    result = subprocess.run(["git", "cat-file", "--batch"], cwd=root, check=True,
                            input="\n".join(unique).encode() + b"\n", capture_output=True)
    out, contents, position = result.stdout, {}, 0
    for object_id in unique:
        header_end = out.index(b"\n", position)
        size = int(out[position:header_end].split()[2])
        start = header_end + 1
        contents[object_id] = out[start:start + size]
        position = start + size + 1
    return contents


def main_checkout(root: Path) -> Path | None:
    """The main checkout of the repository `root` belongs to: the parent of the common git
    directory. For a linked worktree this is the checkout it was added from; for the main checkout
    it is `root` itself. None when git cannot say."""
    result = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root,
                            capture_output=True, text=True, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = root / common
    return common.resolve().parent


def deny_list_candidates(root: Path) -> list[Path]:
    """Where to look for the deny-list when PRIVATE_DENY_LIST is not set, in order."""
    candidates = [root / DEFAULT_DENY_LIST]
    main = main_checkout(root)
    if main is not None and (main / DEFAULT_DENY_LIST).resolve() != candidates[0].resolve():
        candidates.append(main / DEFAULT_DENY_LIST)
    return candidates


def find_deny_list(root: Path) -> tuple[Path | None, list[Path]]:
    """The deny-list to use, or None, and every path that was looked at."""
    configured = os.environ.get("PRIVATE_DENY_LIST")
    if configured:
        return Path(configured), [Path(configured)]
    candidates = deny_list_candidates(root)
    for candidate in candidates:
        if candidate.is_file():
            return candidate, candidates
    return None, candidates


def warn_no_deny_list(searched: list[Path]) -> None:
    bar = "!" * 78
    lines = [bar,
             "WARNING: check_confidential found NO deny-list.",
             "Confidential identifiers were NOT checked.",
             "Only the private-directory path check ran.",
             "Looked in:"]
    lines += [f"  {path}" for path in searched]
    lines += ["Get the deny-list from the repository owner and save it as .private/deny-list.txt",
              "in the main checkout (worktrees read it from there), or set PRIVATE_DENY_LIST.",
              bar]
    print("\n".join(lines), file=sys.stderr)


def read_deny_list(path: Path) -> set[str] | None:
    """The identifiers in the deny-list, or None when the file does not exist."""
    if not path.is_file():
        return None
    identifiers: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if entry and not entry.startswith("#"):
            identifiers.add(entry)
    return identifiers


def check_paths(files: list[str]) -> list[str]:
    return [f"tracked file under the private directory: {f}"
            for f in files if f == PRIVATE_DIR.rstrip("/") or f.startswith(PRIVATE_DIR)]


def identifier_patterns(identifiers: set[str]) -> dict[str, re.Pattern[str]]:
    """Each identifier, matched case-insensitively on word boundaries (against lowered text)."""
    return {i: re.compile(r"(?<!\w)" + re.escape(i.lower()) + r"(?!\w)") for i in identifiers}


def check_message(text: str, identifiers: set[str], what: str = "commit message") -> list[str]:
    lowered = text.lower()
    return [f"{what}: matches deny-listed identifier '{identifier}'"
            for identifier, pattern in sorted(identifier_patterns(identifiers).items())
            if pattern.search(lowered)]


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True,
                          ).stdout.decode("utf-8", errors="surrogateescape")


def pushed_commits(root: Path, remote: str,
                   ref_lines: list[str]) -> tuple[list[str], list[str]]:
    """The commits a push would send, oldest first, and the annotated tag objects it pushes.
    ``ref_lines`` are git's pre-push lines:
    ``<local ref> <local sha> <remote ref> <remote sha>``."""
    commits: list[str] = []
    tags: list[str] = []
    for line in ref_lines:
        fields = line.split()
        if len(fields) != 4 or set(fields[1]) == {"0"}:
            continue  # malformed, or a delete: nothing is sent
        local, remote_sha = fields[1], fields[3]
        if git_out(root, "cat-file", "-t", local).strip() == "tag":
            tags.append(local)
        known = subprocess.run(["git", "cat-file", "-e", f"{remote_sha}^{{commit}}"], cwd=root,
                               capture_output=True, check=False).returncode == 0
        if set(remote_sha) == {"0"} or not known:
            # A new ref, or a remote tip this clone has not fetched (someone pushed first, so
            # the push will be refused as a non-fast-forward): send-able commits are those on no
            # ref this clone knows the remote has.
            listed = git_out(root, "rev-list", "--reverse", local, "--not",
                             f"--remotes={remote}")
        else:
            listed = git_out(root, "rev-list", "--reverse", f"{remote_sha}..{local}")
        for commit in listed.split():
            if commit not in commits:
                commits.append(commit)
    return commits, tags


def check_commit(root: Path, commit: str, identifiers: set[str]) -> list[str]:
    """One commit on its own: its message, and the paths and added lines of what it changes."""
    short = commit[:12]
    violations = check_message(git_out(root, "log", "-1", "--format=%B", commit), identifiers,
                               f"commit {short} message")
    parents = git_out(root, "rev-list", "--parents", "-n", "1", commit).split()[1:]
    base = parents[0] if parents else EMPTY_TREE
    changed = git_out(root, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=AMT",
                      base, commit).split("\0")
    patterns = identifier_patterns(identifiers)
    for path in (p for p in changed if p):
        violations += [f"commit {short}: {v}" for v in check_paths([path])]
        for identifier, pattern in patterns.items():
            if pattern.search(path.lower()):
                violations.append(f"commit {short}: {path}: path matches deny-listed identifier "
                                  f"'{identifier}'")
    if patterns:
        diff = git_out(root, "diff", "--no-color", "--no-ext-diff", "--no-renames", "-U0", base,
                       commit)
        current = "?"
        for line in diff.splitlines():
            if line.startswith("+++ "):
                current = line[6:] if line.startswith("+++ b/") else line[4:]
            elif line.startswith("+") and not current.startswith(PRIVATE_DIR):
                lowered = line[1:].lower()
                for identifier, pattern in patterns.items():
                    found = f"commit {short}: {current}: adds deny-listed identifier '{identifier}'"
                    if pattern.search(lowered) and found not in violations:
                        violations.append(found)
    return violations


def check_content(root: Path, blobs: dict[str, str | None], identifiers: set[str]) -> list[str]:
    if not identifiers:
        return []
    patterns = identifier_patterns(identifiers)
    candidates = {f: object_id for f, object_id in blobs.items()
                  if object_id is not None and not f.startswith(PRIVATE_DIR)}
    contents = read_blobs(root, list(candidates.values()))
    scanned = {f: object_id for f, object_id in candidates.items()
               if b"\0" not in contents[object_id][:BINARY_PROBE]}
    violations: list[str] = []
    for f in blobs:
        if f.startswith(PRIVATE_DIR):
            continue  # reported by check_paths
        lowered = f.lower()
        for identifier, pattern in patterns.items():
            if pattern.search(lowered):
                violations.append(f"{f}: path matches deny-listed identifier '{identifier}'")
        if f not in scanned:
            continue
        text = contents[scanned[f]].decode("utf-8", errors="ignore").lower()
        for identifier, pattern in patterns.items():
            if pattern.search(text):
                violations.append(f"{f}: matches deny-listed identifier '{identifier}'")
    return violations


def load_identifiers(root: Path, violations: list[str]) -> set[str] | None:
    """The deny-list's identifiers, or None when there is no deny-list (after the warning). A
    configured deny-list that is missing, or one that names nothing, is added to ``violations``."""
    deny_list, searched = find_deny_list(root)
    identifiers = read_deny_list(deny_list) if deny_list is not None else None
    if identifiers is None and os.environ.get("PRIVATE_DENY_LIST"):
        violations.append(f"PRIVATE_DENY_LIST is set but {deny_list} does not exist")
    elif identifiers is None:
        warn_no_deny_list(searched)
    elif not identifiers:
        violations.append(f"the deny-list {deny_list} names no identifiers (it is empty or holds "
                          "only blank lines and comments); nothing would be checked")
    return identifiers


def report_failure(violations: list[str]) -> int:
    print("check_confidential: FAILED")
    for violation in violations:
        print(f"  - {violation}")
    return 1


def main(root: Path = ROOT, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--message", type=Path, metavar="FILE",
                        help="check a commit message file instead of the index")
    parser.add_argument("--pre-push", metavar="REMOTE",
                        help="check every commit a push sends; git's ref lines on standard input")
    args = parser.parse_args([] if argv is None else argv)
    violations: list[str] = []
    if args.pre_push is not None:
        identifiers = load_identifiers(root, violations)
        try:
            commits, tags = pushed_commits(root, args.pre_push, sys.stdin.read().splitlines())
        except subprocess.CalledProcessError as error:
            reason = error.stderr.decode("utf-8", errors="replace").strip().splitlines()
            detail = f"{' '.join(error.cmd)}{': ' + reason[-1] if reason else ''}"
            message = (f"cannot list the commits this push sends ({detail}); nothing was "
                       "checked, so the push is refused")
            return report_failure([message])
        for tag in tags:
            violations += check_message(git_out(root, "cat-file", "tag", tag), identifiers or set(),
                                        f"tag {tag[:12]}")
        for commit in commits:
            violations += check_commit(root, commit, identifiers or set())
        if violations:
            return report_failure(violations)
        print(f"check_confidential: OK (push: {len(commits)} commits, "
              + ("content check SKIPPED, no deny-list)" if identifiers is None
                 else f"{len(identifiers)} identifiers checked)"))
        return 0
    if args.message is not None:
        identifiers = load_identifiers(root, violations)
        violations += check_message(args.message.read_text(encoding="utf-8", errors="ignore"),
                                    identifiers or set())
        if violations:
            return report_failure(violations)
        print("check_confidential: OK (commit message, "
              + ("content check SKIPPED, no deny-list)" if identifiers is None
                 else f"{len(identifiers)} identifiers checked)"))
        return 0

    blobs = staged_blobs(root)
    files = list(blobs)
    violations = check_paths(files)
    identifiers = load_identifiers(root, violations)
    violations += check_content(root, blobs, identifiers or set())

    if violations:
        return report_failure(violations)

    if identifiers is None:
        print(f"check_confidential: OK ({len(files)} tracked files, path check only; "
              "content check SKIPPED, no deny-list)")
    else:
        print(f"check_confidential: OK ({len(files)} tracked files, "
              f"{len(identifiers)} identifiers checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(argv=sys.argv[1:]))
