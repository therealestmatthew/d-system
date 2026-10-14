#!/usr/bin/env python3
"""Fail when a tracked file leaks a confidential identifier or lives under the private directory.

Run before committing, or let the pre-commit hook run it:

    uv run python tools/check_confidential.py

It reads `git ls-files`, so it sees committed and staged files only: stage your changes first, or
an unstaged file is simply not checked.

Two checks:

1. **Path check** (always runs). No tracked file may live under the private directory
   (`PRIVATE_DIR`). `.gitignore` stops an ordinary `git add`, but not `git add -f`; this does.

2. **Content check** (runs when the deny-list file exists). The deny-list is an untracked,
   gitignored text file, one identifier per line: client names, account ids, internal project
   names, anything that must never reach a tracked file. Blank lines and lines starting with `#`
   are ignored. Each identifier is matched case-insensitively, on word boundaries, against every
   tracked file's path and text. The file is per machine and is never committed, because a tracked
   list of the identifiers would be the leak it exists to prevent.

   The deny-list is `.private/deny-list.txt` under the repository root, or the path in the
   `PRIVATE_DENY_LIST` environment variable. When it is missing the content check is skipped with
   a note; the path check still runs.

Exit codes: 0 when nothing leaks; 1 when anything does, one line per violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRIVATE_DIR = ".private/"
DEFAULT_DENY_LIST = Path(PRIVATE_DIR) / "deny-list.txt"

# Binary files a content scan should not open.
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".zip", ".gz", ".woff", ".woff2"}


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line]


def deny_list_path(root: Path) -> Path:
    configured = os.environ.get("PRIVATE_DENY_LIST")
    return Path(configured) if configured else root / DEFAULT_DENY_LIST


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


def check_content(root: Path, files: list[str], identifiers: set[str]) -> list[str]:
    patterns = {i: re.compile(r"(?<!\w)" + re.escape(i.lower()) + r"(?!\w)")
                for i in identifiers}
    violations: list[str] = []
    for f in files:
        if f.startswith(PRIVATE_DIR):
            continue  # reported by check_paths
        lowered = f.lower()
        for identifier, pattern in patterns.items():
            if pattern.search(lowered):
                violations.append(f"{f}: path matches deny-listed identifier '{identifier}'")
        path = root / f
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for identifier, pattern in patterns.items():
            if pattern.search(text):
                violations.append(f"{f}: matches deny-listed identifier '{identifier}'")
    return violations


def main(root: Path = ROOT) -> int:
    files = tracked_files(root)
    violations = check_paths(files)

    deny_list = deny_list_path(root)
    identifiers = read_deny_list(deny_list)
    if identifiers is None:
        print(f"note: deny-list {deny_list} not found — content check skipped "
              "(path check still ran)")
        identifiers = set()
    violations += check_content(root, files, identifiers)

    if violations:
        print("check_confidential: FAILED")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print(f"check_confidential: OK ({len(files)} tracked files, "
          f"{len(identifiers)} identifiers checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
