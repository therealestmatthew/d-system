# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""The mechanical section check for a plan draft.

A section is present when the draft has a line of ``## `` or ``### `` followed by one of that
section's accepted headings, exactly, case-sensitive, with nothing after it. Lines inside a fenced
code block do not count. Six sections are always required; two are conditional:

- ``Requirement coverage``, when ``depends_on`` names a document of kind ``requirement`` (looked
  up under the document root). A plan paired with a requirement satisfies Verification with the
  same heading.
- ``Concurrency``, when the draft names two or more distinct backlog phase ids, outside fenced
  lines.

It reads headings only; whether the sections say anything useful is a reviewer's judgement.

Exit codes: 0 when every draft has every section it needs; 1 when any section is missing, one
``<draft>: missing: <section>`` line each; 2 when a draft cannot be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path

import documents
import paths
import yaml

#: Section name, then its accepted headings. Every one of these is required.
REQUIRED: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Context", ("Context and scope", "Summary", "Outcome and scope")),
    ("Design", ("Decisions", "The chosen design", "Chosen design", "Design", "Approach",
                "This is an investigation plan", "This is a discovery plan")),
    ("Work", ("Implementation phases", "Work and dependencies", "Phases", "Work",
              "Ordered work and acceptance", "Sequencing")),
    ("Verification", ("Acceptance and verification", "Requirement coverage")),
    ("Boundaries", ("Out of scope", "What this plan does not do")),
    ("Open questions", ("Open questions", "Open question", "Open decisions")),
)
REQUIREMENT_COVERAGE = ("Requirement coverage", ("Requirement coverage",))
CONCURRENCY = ("Concurrency", ("Execution order and real concurrency", "Execution order"))

HEADING = re.compile(r"^#{2,3} (.+)$")
PHASE_ID = re.compile(r"phase-[a-z]+-[0-9]+")


def unfenced(text: str) -> list[str]:
    """The draft's lines, less every line inside a fenced code block and the fences themselves."""
    kept: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return kept


def depends_on(text: str) -> list[str]:
    """The front matter's ``depends_on`` ids; empty when the draft has no readable front matter."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return []
    try:
        meta = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    except yaml.YAMLError:
        return []
    value = meta.get("depends_on") if isinstance(meta, dict) else None
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def missing_sections(text: str, kinds: dict[str, str]) -> list[str]:
    """Every section the draft needs and lacks, in table order. ``kinds`` maps id to kind."""
    body = unfenced(text)
    headings = {match.group(1) for line in body if (match := HEADING.match(line))}
    needed = list(REQUIRED)
    if any(kinds.get(ref) == "requirement" for ref in depends_on(text)):
        needed.append(REQUIREMENT_COVERAGE)
    if len({found for line in body for found in PHASE_ID.findall(line)}) >= 2:
        needed.append(CONCURRENCY)
    return [name for name, accepted in needed if not headings & set(accepted)]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="plan-check",
        description="Check that each plan draft has the sections a plan needs, by heading.",
    )
    parser.add_argument("drafts", nargs="+", type=Path, help="plan draft files to check")
    paths.add_arguments(parser, ["docs_root", "exempt_files"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    kinds = documents.kinds_by_id(config)
    missing = 0
    for draft in args.drafts:
        try:
            text = draft.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{draft}: cannot read: {exc}", file=sys.stderr)
            return 2
        gaps = missing_sections(text, kinds)
        for name in gaps:
            print(f"{draft}: missing: {name}")
        missing += len(gaps)
        if not gaps:
            print(f"{draft}: OK")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
