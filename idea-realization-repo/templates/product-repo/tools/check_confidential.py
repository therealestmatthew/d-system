#!/usr/bin/env python3
"""Fail when a tracked file leaks a confidential identifier or lives under the private directory.

This is a copy of the control repository's tools/check_confidential.py, so that this repository's
pre-commit hook and CI can run it without the control repository. It uses only the Python
standard library. Change both copies together.

Run before committing, or let the pre-commit hook (tools/install-hooks.sh) run it:

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


def check_content(root: Path, blobs: dict[str, str | None], identifiers: set[str]) -> list[str]:
    if not identifiers:
        return []
    patterns = {i: re.compile(r"(?<!\w)" + re.escape(i.lower()) + r"(?!\w)")
                for i in identifiers}
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


def main(root: Path = ROOT) -> int:
    blobs = staged_blobs(root)
    files = list(blobs)
    violations = check_paths(files)

    deny_list = deny_list_path(root)
    identifiers = read_deny_list(deny_list)
    if identifiers is None:
        print(f"note: deny-list {deny_list} not found — content check skipped "
              "(path check still ran)")
        identifiers = set()
    violations += check_content(root, blobs, identifiers)

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
