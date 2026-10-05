"""Tests for the requirement-mandatory rule (REQ-015 R01-R03; rule stated in GOV-001).

R01: the rule, applied to five plans chosen without regard to outcome, gives the same answer for
a second reader — here, an independent re-implementation of the rule written directly in the
test, not a second call into the module under test.

R03: a fixture plan meeting the mandatory condition with no paired requirement document fails the
enforcement check and is named; a fixture plan on the grandfather list still passes. Per the
owner's ruling for this phase, the fixture plan is built in memory inside this test and never
written under docs/ — governance must never see it as part of the real corpus.
"""

from __future__ import annotations

from typing import Any

from src.governance.__main__ import ROOT, audit, audit_backlog
from src.governance.requirement_rule import (
    GRANDFATHERED_PLAN_IDS,
    inspect_requirement_pairing,
    is_paired,
    phase_counts,
    render_classification,
    requirement_mandatory,
    unpaired_mandatory_plans,
)


def plan_meta(doc_id: str, depends_on: list[str], path: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": doc_id,
        "code": "PLAN-999",
        "title": "Fixture plan",
        "kind": "plan",
        "status": "active",
        "owner": "repository-owner",
        "created": "2026-10-05",
        "updated": "2026-10-05",
        "systems": [],
        "depends_on": depends_on,
        "path": path,
    }


def requirement_meta(doc_id: str, path: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": doc_id,
        "code": "REQ-999",
        "title": "Fixture requirement",
        "kind": "requirement",
        "status": "draft",
        "owner": "repository-owner",
        "created": "2026-10-05",
        "updated": "2026-10-05",
        "systems": [],
        "depends_on": [],
        "path": path,
    }


def backlog_item(item_id: str, plan: str) -> dict[str, Any]:
    return {"id": item_id, "plan": plan}


# --- R01: the rule gives the same answer for a second reader -------------------------------


def second_reader_mandatory(plan_id: str, items: list[dict[str, Any]]) -> bool:
    """An independent re-derivation of the rule: count backlog items naming this plan."""
    count = sum(1 for item in items if item.get("plan") == plan_id)
    return count > 1


def test_rule_agrees_with_a_second_reader_on_five_real_plans() -> None:
    errors, _warnings, result = audit(ROOT)
    assert errors == []
    _backlog_errors, catalog = audit_backlog(ROOT, result)
    items = catalog["items"]

    # Five plans chosen without regard to outcome: the first, a middle, and the last few plan
    # ids that sort lexically from the real corpus's plan documents.
    documents = result["documents"]
    plan_ids = sorted(
        doc_id for doc_id, meta in documents.items() if meta.get("kind") == "plan"
    )
    chosen = [plan_ids[0], plan_ids[len(plan_ids) // 3], plan_ids[len(plan_ids) // 2],
              plan_ids[-2], plan_ids[-1]]
    assert len(chosen) == 5

    counts = phase_counts(items)
    for plan_id in chosen:
        via_module = requirement_mandatory(counts.get(plan_id, 0))
        via_second_reader = second_reader_mandatory(plan_id, items)
        assert via_module == via_second_reader, plan_id


# --- R02: the classification states a number -----------------------------------------------


def test_classification_states_a_number_not_several() -> None:
    errors, _warnings, result = audit(ROOT)
    assert errors == []
    _backlog_errors, catalog = audit_backlog(ROOT, result)
    output = render_classification(result["documents"], catalog["items"])
    assert "Unpaired mandatory plans: " in output
    tail = output.rsplit("Unpaired mandatory plans: ", 1)[1].rstrip(".\n")
    assert tail.isdigit()


def test_real_corpus_unpaired_mandatory_plans_are_all_grandfathered() -> None:
    """Classifying the real corpus today finds only ids already on the grandfather list."""
    errors, _warnings, result = audit(ROOT)
    assert errors == []
    _backlog_errors, catalog = audit_backlog(ROOT, result)
    unpaired = unpaired_mandatory_plans(result["documents"], catalog["items"])
    unpaired_ids = {plan_id for plan_id, _meta in unpaired}
    assert unpaired_ids <= GRANDFATHERED_PLAN_IDS
    assert len(unpaired) == len(GRANDFATHERED_PLAN_IDS)


# --- R03: enforcement fails an unpaired fixture plan and names it; grandfathered ones pass ---


def test_fixture_plan_meeting_mandatory_condition_with_no_requirement_fails_and_is_named() -> None:
    documents = {
        "doc-fixture-plan": plan_meta(
            "doc-fixture-plan", [], "docs/01-plans/PLAN-999-fixture.md"
        ),
    }
    items = [
        backlog_item("phase-fixture-01", "doc-fixture-plan"),
        backlog_item("phase-fixture-02", "doc-fixture-plan"),
    ]

    errors = inspect_requirement_pairing(documents, items)

    assert len(errors) == 1
    assert "docs/01-plans/PLAN-999-fixture.md" in errors[0]
    assert "doc-fixture-plan" in errors[0]


def test_fixture_plan_paired_with_a_requirement_passes() -> None:
    documents = {
        "doc-fixture-plan": plan_meta(
            "doc-fixture-plan", ["doc-fixture-requirement"], "docs/01-plans/PLAN-999-fixture.md"
        ),
        "doc-fixture-requirement": requirement_meta(
            "doc-fixture-requirement", "docs/06-requirements/REQ-999-fixture.md"
        ),
    }
    items = [
        backlog_item("phase-fixture-01", "doc-fixture-plan"),
        backlog_item("phase-fixture-02", "doc-fixture-plan"),
    ]

    assert inspect_requirement_pairing(documents, items) == []


def test_fixture_plan_meeting_mandatory_condition_but_grandfathered_passes() -> None:
    grandfathered_id = next(iter(GRANDFATHERED_PLAN_IDS))
    documents = {
        grandfathered_id: plan_meta(grandfathered_id, [], "docs/01-plans/PLAN-998-fixture.md"),
    }
    items = [
        backlog_item("phase-fixture-01", grandfathered_id),
        backlog_item("phase-fixture-02", grandfathered_id),
    ]

    assert inspect_requirement_pairing(documents, items) == []


def test_single_phase_plan_is_not_mandatory() -> None:
    documents = {
        "doc-fixture-plan": plan_meta(
            "doc-fixture-plan", [], "docs/01-plans/PLAN-999-fixture.md"
        ),
    }
    items = [backlog_item("phase-fixture-01", "doc-fixture-plan")]

    assert inspect_requirement_pairing(documents, items) == []
    assert unpaired_mandatory_plans(documents, items) == []


def test_is_paired_requires_requirement_kind_dependency() -> None:
    documents = {
        "doc-other-plan": plan_meta("doc-other-plan", [], "docs/01-plans/PLAN-997.md"),
    }
    assert is_paired(["doc-other-plan"], documents) is False
    assert is_paired([], documents) is False
