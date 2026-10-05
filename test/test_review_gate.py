"""Tests for the S3 next_up rule (REQ-028 R12, PLAN-045 D11).

The fixture table is REQ-028 R12's: a next_up phase with no record fails; with a dispositioned
record it passes; with a record whose finding's last disposition is escalated-g3 it fails; with an
open record it fails; a grandfathered phase with no record passes. The table runs through the
backlog audit on an isolated repository, so each failure is one the governance command exits 1 on.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from src.governance.__main__ import ROOT, audit, audit_backlog, audit_review_gate
from src.governance.review_gate import EXEMPT, REVIEWS_DIR, inspect_review_gate

PHASE = "phase-exa-01"
GRANDFATHERED = "phase-cap-08"


def phase(phase_id: str) -> dict[str, Any]:
    return {
        "id": phase_id,
        "title": "Example phase",
        "plan": "doc-example",
        "sources": ["doc-example"],
        "systems": ["sys-example"],
        "owner": "repository-owner",
        "status": "queued",
        "priority": 1,
        "session_budget": 1,
        "depends_on": [],
        "scope": ["Do the example."],
        "acceptance": ["The example is done.", "The example is checked."],
        "verification": ["uv run pytest"],
        "deliverables": ["schemas"],
        "next_action": "Do the example.",
    }


def finding(*values: str) -> dict[str, Any]:
    """A finding whose dispositions carry the given values, oldest first."""
    return {"id": "F01", "dispositions": [{"by": "planner", "value": value} for value in values]}


def record(status: str = "dispositioned", findings: list[dict[str, Any]] | None = None,
           phases: list[str] | None = None, later: list[str] | None = None) -> dict[str, Any]:
    target: dict[str, Any] = {"plan": "PLAN-001", "phases": [PHASE] if phases is None else phases}
    if later is not None:
        target["later_added_phases"] = later
    return {"review_id": "2026-10-05-plan-001", "target": target, "status": status,
            "findings": [finding("fixed")] if findings is None else findings}


def build(root: Path, next_up: list[str], records: dict[str, dict[str, Any]]) -> Path:
    """An isolated repository with `next_up` and the given review records."""
    shutil.copytree(ROOT / "schemas", root / "schemas")
    (root / "_data/projects").mkdir(parents=True)
    (root / "_data/tags.json").write_text('[{"id": "python"}]')
    (root / REVIEWS_DIR).mkdir(parents=True)
    registry = {
        "schema_version": 1,
        "owners": {"repository-owner": "Maintainer"},
        "systems": [
            {
                "id": "sys-example",
                "name": "Example",
                "domain": "governance",
                "status": "implemented",
                "owner": "repository-owner",
                "paths": ["schemas"],
                "depends_on": [],
                "description": "Example component",
            }
        ],
    }
    (root / "docs/08-governance/systems.yaml").write_text(json.dumps(registry))
    shutil.copy(ROOT / "docs/08-governance/codes.yaml", root / "docs/08-governance/codes.yaml")
    decisions = {
        "schema_version": 1, "id": "doc-decisions", "code": "GOV-001", "title": "Decisions",
        "kind": "governance", "status": "active", "owner": "repository-owner",
        "created": "2026-10-05", "updated": "2026-10-05", "systems": ["sys-example"],
        "depends_on": [],
    }
    (root / "docs/08-governance/GOV-001-decisions.md").write_text(
        "---\n" + json.dumps(decisions) + "\n---\n\n# Decisions\n"
    )
    # A plan naming every registered phase, so the plan-versus-registered check stays quiet.
    plan = {**decisions, "id": "doc-example", "code": "PLAN-001", "title": "Example",
            "kind": "plan", "status": "approved"}
    (root / "docs/01-plans").mkdir(parents=True)
    (root / "docs/01-plans/PLAN-001-example.md").write_text(
        "---\n" + json.dumps(plan) + "\n---\n\n# Example\n\n" + ", ".join(next_up) + "\n"
    )
    backlog = {
        "schema_version": 1,
        "updated": "2026-10-05",
        "decision_record": "doc-decisions",
        "next_up": next_up,
        "items": [phase(p) for p in next_up],
    }
    (root / "docs/09-backlog").mkdir(parents=True)
    (root / "docs/09-backlog/backlog.yaml").write_text(json.dumps(backlog))
    for name, body in records.items():
        (root / REVIEWS_DIR / name).write_text(json.dumps(body))
    return root


def errors_for(root: Path) -> list[str]:
    errors, _, result = audit(root)
    assert errors == []
    backlog_errors, catalog = audit_backlog(root, result)
    gate_errors = audit_review_gate(root, catalog)[0]
    assert sorted(backlog_errors) == sorted(gate_errors)
    return gate_errors


def refused(detail: str, phase_id: str = PHASE) -> str:
    return (
        f"next_up: {phase_id} has no dispositioned review record under {REVIEWS_DIR}/ "
        f"without an escalated-g3 finding ({detail}) (REQ-028 R12)"
    )


def test_a_next_up_phase_with_no_record_fails(tmp_path: Path) -> None:
    assert errors_for(build(tmp_path, [PHASE], {})) == [refused("no record lists it")]


def test_a_next_up_phase_with_a_dispositioned_record_passes(tmp_path: Path) -> None:
    assert errors_for(build(tmp_path, [PHASE], {"r.json": record()})) == []


def test_a_record_whose_finding_was_last_escalated_fails(tmp_path: Path) -> None:
    body = record(findings=[finding("fixed"), {**finding("escalated-g3"), "id": "F02"}])
    assert errors_for(build(tmp_path, [PHASE], {"r.json": body})) == [
        refused(f"{REVIEWS_DIR}/r.json has F02 escalated-g3")
    ]


def test_an_open_record_fails(tmp_path: Path) -> None:
    body = record(status="open", findings=[{"id": "F01"}])
    assert errors_for(build(tmp_path, [PHASE], {"r.json": body})) == [
        refused(f"{REVIEWS_DIR}/r.json is open")
    ]


def test_a_grandfathered_phase_with_no_record_passes(tmp_path: Path) -> None:
    assert errors_for(build(tmp_path, [GRANDFATHERED], {})) == []


def test_an_escalation_the_owner_later_resolved_passes(tmp_path: Path) -> None:
    """Only the last disposition counts: an owner's entry after escalated-g3 replaces it."""
    resolved = {"id": "F01", "dispositions": [
        {"by": "planner", "value": "escalated-g3"}, {"by": "owner", "value": "fixed"}]}
    body = record(findings=[resolved])
    assert errors_for(build(tmp_path, [PHASE], {"r.json": body})) == []


def test_the_later_added_altitude_counts(tmp_path: Path) -> None:
    body = record(phases=[], later=[PHASE])
    assert errors_for(build(tmp_path, [PHASE], {"r.json": body})) == []


def test_one_clearing_record_is_enough_and_every_failing_one_is_named(tmp_path: Path) -> None:
    records = {"a.json": record(status="open"), "b.json": record()}
    assert errors_for(build(tmp_path / "one", [PHASE], records)) == []
    records = {"a.json": record(status="open"), "c.json": record(status="returned")}
    assert errors_for(build(tmp_path / "two", [PHASE], records)) == [
        refused(f"{REVIEWS_DIR}/a.json is open; {REVIEWS_DIR}/c.json is returned")
    ]


def test_a_record_for_another_phase_does_not_clear_it(tmp_path: Path) -> None:
    body = record(phases=["phase-exa-02"])
    assert errors_for(build(tmp_path, [PHASE], {"r.json": body})) == [
        refused("no record lists it")
    ]


def test_records_in_subdirectories_are_not_read(tmp_path: Path) -> None:
    root = build(tmp_path, [PHASE], {})
    (root / REVIEWS_DIR / "verdicts").mkdir()
    (root / REVIEWS_DIR / "verdicts" / "v.json").write_text(json.dumps(record()))
    assert errors_for(root) == [refused("no record lists it")]


def test_an_unreadable_record_is_an_error(tmp_path: Path) -> None:
    root = build(tmp_path, [PHASE], {})
    (root / REVIEWS_DIR / "broken.json").write_text("{not json")
    errors = errors_for(root)
    assert len(errors) == 1
    assert errors[0].startswith("review gate inputs: ")


@pytest.mark.parametrize(
    ("body", "problem"),
    [
        ([], "is not a JSON object"),
        ({"target": "phase-exa-01", "status": "dispositioned"}, "target is not an object"),
        ({"target": {"phases": "phase-exa-01"}}, "target.phases is not a list"),
        ({"target": {"later_added_phases": {}}}, "target.later_added_phases is not a list"),
        ({"target": {"phases": []}, "findings": {}}, "findings is not a list"),
        ({"target": {"phases": []}, "findings": ["F01"]}, "a finding is not an object"),
        ({"target": {"phases": []}, "findings": [{"id": "F01", "dispositions": ["fixed"]}]},
         "finding F01 has dispositions that are not a list of objects"),
    ],
)
def test_a_wrongly_shaped_record_is_a_named_error(
    tmp_path: Path, body: Any, problem: str
) -> None:
    """A hand-written record with the wrong shape fails by name, not with a traceback."""
    root = build(tmp_path, [PHASE], {})
    (root / REVIEWS_DIR / "bad.json").write_text(json.dumps(body))
    assert errors_for(root) == [f"review gate inputs: {REVIEWS_DIR}/bad.json {problem}"]


def test_the_exemption_is_exactly_req_028_r12s_nineteen() -> None:
    requirement = (ROOT / "docs/06-requirements/REQ-028-deterministic-guards.md").read_text()
    row = next(line for line in requirement.splitlines() if line.startswith("| R12 |"))
    listed = row.split("are exempt:", 1)[1].split("|", 1)[0]
    named = {part.strip(" `") for part in listed.split(",")}
    assert len(EXEMPT) == 19
    assert EXEMPT == named


@pytest.mark.parametrize("phase_id", sorted(EXEMPT))
def test_every_exempt_phase_passes_with_no_record(phase_id: str) -> None:
    assert inspect_review_gate([phase_id], {})[0] == []


def test_repository_passes_and_reports_its_counts() -> None:
    errors, _, result = audit(ROOT)
    assert errors == []
    _, catalog = audit_backlog(ROOT, result)
    gate_errors, counts = audit_review_gate(ROOT, catalog)
    assert gate_errors == []
    assert counts["records"] > 0
    assert counts["phases_checked"] + counts["phases_exempt"] == len(catalog["next_up"])


def test_the_backlog_audit_carries_the_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """audit_backlog returns audit_review_gate's errors, so the governance command exits 1."""
    from src.governance import __main__ as governance

    errors, _, result = audit(ROOT)
    monkeypatch.setattr(governance, "audit_review_gate", lambda root, catalog: (["planted"], {}))
    assert "planted" in audit_backlog(ROOT, result)[0]
