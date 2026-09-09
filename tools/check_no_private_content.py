#!/usr/bin/env python3
"""Fail when a tracked file leaks private portfolio content or paths.

Run before committing, or as a gate in CI / a pre-commit hook:
    uv run python tools/check_no_private_content.py

Two independent checks:

1. **Path check** (always runs). No file `git ls-files` reports may live under a
   private path (see PRIVATE_PATH_PREFIXES below). This catches `git add -f` of a
   private file, which `.gitignore` alone cannot: ignore rules only stop an
   unqualified `git add`.

2. **Content check** (runs only when `_private/portfolio/` exists on disk, i.e. on
   the owner's machine — never in a fresh clone or CI, so CI only ever runs the path
   check). The confidential-identifier list is derived at runtime from the real
   portfolio itself and is never written to a tracked file, since a tracked list of
   real client names and project IDs would be exactly the leak this script exists to
   prevent. Two kinds of identifier:

   - Every hyphenated project filename stem (a compound real project ID is content
     per ADR-009).
   - Any filename prefix shared by two or more projects, *unless* that token (or a
     tag id/label containing it) already appears in the tracked `_data/tags.json` —
     a repeated prefix that is also a deliberately-kept public tag (e.g. a platform
     name) is vocabulary, not a client identifier; one that is not is folded out of
     the tag registry on purpose, which is the signal that it is one.

   Matches use word boundaries against tracked file paths and content (case
   insensitive).

   EXEMPT_IDENTIFIERS silences specific known non-leaks: an identifier that
   coincidentally matches a structural document's own name (same string, different
   referent). It does not silence a path-check violation.

See PLAN-006 (docs/01-plans/PLAN-006-confidentiality-sweep.md) and phase-priv-04.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent

PRIVATE_PATH_PREFIXES = (
    "_private/",
    "_private/portfolio/",
    "_private/portfolio/projects/",
)

# Binary/large files a content grep should not open.
CONTENT_CHECK_SKIP_SUFFIXES = {".duckdb", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}

MIN_SHARED_PREFIX_COUNT = 2

# identifier -> one-line reason it is a known false positive, not a real leak.
EXEMPT_IDENTIFIERS: dict[str, str] = {
    "artifact-code-generation": (
        "shares its name with the structural document "
        "docs/02-prompts/PROMPT-001-artifact-code-generation-system.md, which is "
        "correctly named for its own generic purpose (ADR-009's test) — not a leak "
        "of the real project of the same name."
    ),
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line]


def check_paths(files: list[str]) -> list[str]:
    violations = []
    for f in files:
        if any(f == p.rstrip("/") or f.startswith(p) for p in PRIVATE_PATH_PREFIXES):
            violations.append(f"tracked file under a private path: {f}")
    return violations


def confidential_identifiers() -> set[str]:
    portfolio = ROOT / "_private" / "portfolio" / "projects"
    if not portfolio.is_dir():
        return set()

    stems = [p.stem for p in portfolio.glob("*.json")]
    identifiers: set[str] = {s for s in stems if "-" in s}

    tags_path = ROOT / "_data" / "tags.json"
    tag_text = ""
    if tags_path.is_file():
        tags = json.loads(tags_path.read_text(encoding="utf-8"))
        tag_text = " ".join(f"{t.get('id', '')} {t.get('label', '')}" for t in tags).lower()

    prefix_counts = Counter(s.split("-", 1)[0] for s in stems)
    for prefix, count in prefix_counts.items():
        if count >= MIN_SHARED_PREFIX_COUNT and prefix.lower() not in tag_text:
            identifiers.add(prefix)

    return identifiers - set(EXEMPT_IDENTIFIERS)


def check_content(files: list[str], identifiers: set[str]) -> list[str]:
    if not identifiers:
        return []

    patterns = {i: re.compile(r"\b" + re.escape(i.lower()) + r"\b") for i in identifiers}
    violations = []
    for f in files:
        path = ROOT / f
        if any(f == p.rstrip("/") or f.startswith(p) for p in PRIVATE_PATH_PREFIXES):
            continue  # already reported by check_paths
        f_low = f.lower()
        for identifier, pattern in patterns.items():
            if pattern.search(f_low):
                violations.append(f"{f}: path matches confidential identifier '{identifier}'")
        if path.suffix.lower() in CONTENT_CHECK_SKIP_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for identifier, pattern in patterns.items():
            if pattern.search(text):
                violations.append(f"{f}: matches confidential identifier '{identifier}'")
    return violations


def main() -> int:
    files = tracked_files()
    violations = check_paths(files)

    identifiers = confidential_identifiers()
    violations += check_content(files, identifiers)

    if not identifiers:
        print(
            "note: _private/portfolio/ not found — content check skipped "
            "(path check still ran; this is expected in CI / a fresh clone)"
        )

    if violations:
        print("check_no_private_content: FAILED")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(
        f"check_no_private_content: OK ({len(files)} tracked files, "
        f"{len(identifiers)} identifiers checked)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
