"""Tests for the GOV-010 mechanical section check (REQ-014 R20).

R20: a plan drafted by the planner agent is measurably conformant to the plan-quality standard -
checked against the standard's own named sections, not by inspection. Fixtures here are synthetic,
built in memory inside this test, per the owner's ruling for this phase; none of them reads
_data/ideas.jsonl or idea 000072.
"""

from __future__ import annotations

from src.governance.plan_quality import (
    check_plan_conformance,
    check_requirement_conformance,
    present_headings,
)

CONFORMANT_PLAN = """\
# PLAN-999: Fixture plan

## Context and scope

This fixture plan exists only to exercise the section check.

## Decisions

We decided X over Y because Y would have cost Z.

## Implementation phases

| Phase | Title |
|---|---|
| phase-fix-01 | Do the thing |

## Acceptance and verification

- The thing is done.

## Out of scope

- Everything else.

## Open questions

None outstanding.
"""

NON_CONFORMANT_PLAN = """\
# PLAN-998: Broken fixture plan

## Context and scope

Has context but nothing else GOV-010 requires.
"""


def test_conformant_fixture_plan_passes() -> None:
    result = check_plan_conformance(CONFORMANT_PLAN)
    assert result.conformant
    assert result.missing == ()


def test_non_conformant_fixture_plan_is_rejected_and_names_missing_sections() -> None:
    result = check_plan_conformance(NON_CONFORMANT_PLAN)
    assert not result.conformant
    # Design, Work, Verification, Boundaries and Open questions are all absent.
    assert any(m.startswith("Design") for m in result.missing)
    assert any(m.startswith("Work") for m in result.missing)
    assert any(m.startswith("Verification") for m in result.missing)
    assert any(m.startswith("Boundaries") for m in result.missing)
    assert any(m.startswith("Open questions") for m in result.missing)


def test_fenced_code_heading_does_not_count() -> None:
    draft = CONFORMANT_PLAN.replace(
        "## Open questions\n\nNone outstanding.\n",
        "```\n## Open questions\n```\n",
    )
    result = check_plan_conformance(draft)
    assert not result.conformant
    assert any(m.startswith("Open questions") for m in result.missing)


def test_requirement_coverage_heading_satisfies_both_rows_when_paired() -> None:
    draft = CONFORMANT_PLAN.replace(
        "## Acceptance and verification\n\n- The thing is done.\n",
        "## Requirement coverage\n\n- R01 is met by phase-fix-01.\n",
    )
    result = check_plan_conformance(
        draft,
        depends_on=["doc-fixture-requirement"],
        documents={"doc-fixture-requirement": {"kind": "requirement"}},
    )
    assert result.conformant


def test_requirement_coverage_missing_when_paired_but_absent() -> None:
    result = check_plan_conformance(
        CONFORMANT_PLAN,
        depends_on=["doc-fixture-requirement"],
        documents={"doc-fixture-requirement": {"kind": "requirement"}},
    )
    assert not result.conformant
    assert any(m.startswith("Requirement coverage") for m in result.missing)


def test_concurrency_section_required_once_two_phase_ids_appear() -> None:
    draft = CONFORMANT_PLAN.replace(
        "| phase-fix-01 | Do the thing |",
        "| phase-fix-01 | Do the thing |\n| phase-fix-02 | Do the other thing |",
    )
    result = check_plan_conformance(draft)
    assert not result.conformant
    assert any(m.startswith("Concurrency") for m in result.missing)

    conformant_draft = draft + "\n## Execution order and real concurrency\n\nSequential.\n"
    assert check_plan_conformance(conformant_draft).conformant


CONFORMANT_REQUIREMENT = """\
# REQ-999: Fixture requirement

## Problem being solved

Something was observed to fail.

## Requirements

| ID | Behaviour | Verification |
|---|---|---|
| R01 | The thing happens. | Run it and watch. |

## What this deliberately does not require

- Nothing else.
"""

NON_CONFORMANT_REQUIREMENT = """\
# REQ-998: Broken fixture requirement

## Problem being solved

Something was observed to fail.
"""


def test_conformant_fixture_requirement_passes() -> None:
    result = check_requirement_conformance(CONFORMANT_REQUIREMENT)
    assert result.conformant


def test_non_conformant_fixture_requirement_is_rejected_and_names_missing_sections() -> None:
    result = check_requirement_conformance(NON_CONFORMANT_REQUIREMENT)
    assert not result.conformant
    assert any(m.startswith("Requirements") for m in result.missing)
    assert any(m.startswith("Boundaries") for m in result.missing)


def test_requirement_row_with_empty_verification_cell_fails() -> None:
    draft = CONFORMANT_REQUIREMENT.replace(
        "| R01 | The thing happens. | Run it and watch. |",
        "| R01 | The thing happens. |  |",
    )
    result = check_requirement_conformance(draft)
    assert not result.conformant
    assert any(m.startswith("Requirements") for m in result.missing)


def test_present_headings_ignores_fenced_blocks() -> None:
    draft = "## Real heading\n\n```\n## Fake heading\n```\n"
    assert present_headings(draft) == {"Real heading"}
