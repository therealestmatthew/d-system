"""The GOV-010 mechanical section check (REQ-014 R20 / REQ-022 R09's draft-side half).

`GOV-010` ("Plan and requirement quality standard") names the sections a plan or requirement must
carry and the headings accepted for each. This module is the mechanical half of that standard: it
reads a draft's Markdown, finds which named headings are present outside fenced code blocks, and
reports which required sections are missing. It does not judge the content-judgement rows (P1-P12,
Q1-Q5) GOV-010 also lists — those are for a human or adversary reader, not a mechanical check.

Deliberately out of scope here, per `phase-idg-12`'s declared boundary: the return-to-planner-or-
escalate revision loop (`REQ-022` R09) that would act on a failing check. This module only answers
"is this draft conformant, and if not, what is missing" — what happens next belongs to
`phase-irs-14`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
_FENCE_RE = re.compile(r"^```")


@dataclass(frozen=True)
class Section:
    """One row of GOV-010's section table."""

    name: str
    accepted_headings: tuple[str, ...]
    # True when the section is always required; otherwise `condition` decides, given the draft text.
    always: bool = True


@dataclass(frozen=True)
class ConformanceResult:
    conformant: bool
    missing: tuple[str, ...] = field(default_factory=tuple)
    present: tuple[str, ...] = field(default_factory=tuple)

    def describe(self) -> str:
        if self.conformant:
            return "conformant: every required section is present."
        return "missing section(s): " + ", ".join(self.missing)


# GOV-010's "### Plan sections" table. Requirement coverage is conditional (depends_on a
# requirement-kind document) and is handled separately below, since that condition needs a lookup
# outside the draft text (the dependency's document kind) that this module's caller supplies.
PLAN_SECTIONS: tuple[Section, ...] = (
    Section("Context", ("Context and scope", "Summary", "Outcome and scope")),
    Section(
        "Design",
        (
            "Decisions",
            "The chosen design",
            "Chosen design",
            "Design",
            "Approach",
            "This is an investigation plan",
            "This is a discovery plan",
        ),
    ),
    Section(
        "Work",
        (
            "Implementation phases",
            "Work and dependencies",
            "Phases",
            "Work",
            "Ordered work and acceptance",
            "Sequencing",
        ),
    ),
    Section("Verification", ("Acceptance and verification", "Requirement coverage")),
    Section("Boundaries", ("Out of scope", "What this plan does not do")),
    Section("Open questions", ("Open questions", "Open question", "Open decisions")),
)

# GOV-010's "### Requirement sections" table.
REQUIREMENT_SECTIONS: tuple[Section, ...] = (
    Section("Problem", ("Observed problem and scope", "Problem being solved")),
    Section("Requirements", ("Observable requirements and verification", "Requirements")),
    Section(
        "Boundaries",
        (
            "What each requirement is not",
            "Out of scope",
            "What this deliberately does not require",
            "Boundaries and open questions",
            "Boundaries and unresolved compatibility",
        ),
    ),
)

_REQUIREMENT_COVERAGE_HEADING = "Requirement coverage"
_CONCURRENCY_SECTION = Section(
    "Concurrency", ("Execution order and real concurrency", "Execution order")
)
_PHASE_ID_RE = re.compile(r"\bphase-[a-z]+-[0-9]+\b")
_REQUIREMENT_ROW_RE = re.compile(r"^\|\s*R[0-9]+\s*\|")


def present_headings(markdown: str) -> set[str]:
    """Every `##`/`###` heading text in `markdown`, outside fenced code blocks."""
    headings: set[str] = set()
    fenced = False
    for line in markdown.splitlines():
        if _FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = _HEADING_RE.match(line)
        if match:
            headings.add(match.group(2))
    return headings


def _check_sections(headings: set[str], sections: tuple[Section, ...]) -> tuple[bool, list[str]]:
    missing = []
    for section in sections:
        if not any(heading in headings for heading in section.accepted_headings):
            missing.append(f"{section.name} ({' / '.join(section.accepted_headings)})")
    return (not missing, missing)


def depends_on_requirement(depends_on: list[str], documents: dict[str, dict[str, object]]) -> bool:
    """True when any id in `depends_on` resolves to a `requirement`-kind document."""
    return any(documents.get(dep, {}).get("kind") == "requirement" for dep in depends_on)


def check_plan_conformance(
    markdown: str,
    *,
    depends_on: list[str] | None = None,
    documents: dict[str, dict[str, object]] | None = None,
) -> ConformanceResult:
    """GOV-010's plan-section check.

    `depends_on`/`documents` supply the one condition the draft text cannot answer on its own:
    whether a named dependency is a `requirement`-kind document, which satisfies Verification and
    Requirement coverage together via the single `Requirement coverage` heading. Omit both when the
    draft has no requirement pairing to check.
    """
    headings = present_headings(markdown)
    paired = depends_on_requirement(depends_on or [], documents or {})

    conformant, missing = _check_sections(headings, PLAN_SECTIONS)

    if paired and _REQUIREMENT_COVERAGE_HEADING not in headings:
        missing.append(f"Requirement coverage ({_REQUIREMENT_COVERAGE_HEADING})")
        conformant = False

    if len(set(_PHASE_ID_RE.findall(_strip_fences(markdown)))) >= 2:
        if not any(h in headings for h in _CONCURRENCY_SECTION.accepted_headings):
            missing.append(
                f"Concurrency ({' / '.join(_CONCURRENCY_SECTION.accepted_headings)})"
            )
            conformant = False

    return ConformanceResult(
        conformant=conformant, missing=tuple(missing), present=tuple(sorted(headings))
    )


def _strip_fences(markdown: str) -> str:
    fenced = False
    kept = []
    for line in markdown.splitlines():
        if _FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept)


def _requirement_rows_pass(markdown: str) -> bool:
    lines = _strip_fences(markdown).splitlines()
    rows = [line for line in lines if _REQUIREMENT_ROW_RE.match(line)]
    if not rows:
        return False
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 3 or not cells[2]:
            return False
    return True


def check_requirement_conformance(markdown: str) -> ConformanceResult:
    """GOV-010's requirement-section check, including the requirement-row check."""
    headings = present_headings(markdown)
    conformant, missing = _check_sections(headings, REQUIREMENT_SECTIONS)

    if not _requirement_rows_pass(markdown):
        missing.append("Requirements (no requirement row with a non-empty verification cell)")
        conformant = False

    return ConformanceResult(
        conformant=conformant, missing=tuple(missing), present=tuple(sorted(headings))
    )
