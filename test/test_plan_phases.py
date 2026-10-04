"""Tests for the plan-versus-registered check (REQ-028 R09, PLAN-045 D8).

The fixture table is REQ-028 R09's: a plan dated 2026-09-23 with an unnamed registered phase fails
naming both; the same plan dated 2026-09-21 passes; a plan naming `phase-zzz-99` fails; the
repository as it stands passes. Each runs `audit_plan_phases` on an isolated repository; the
backlog audit returns its errors, and the governance command exits 1 on any of them.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from src.governance.__main__ import ROOT, audit, audit_backlog, audit_plan_phases
from src.governance.plan_phases import CUTOFF, inspect_plan_phases, named_phases

PLAN_PATH = "docs/01-plans/PLAN-001-example.md"


def plan_meta(created: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": "doc-example",
        "code": "PLAN-001",
        "title": "Example",
        "kind": "plan",
        "status": "approved",
        "owner": "repository-owner",
        "created": created,
        "updated": created,
        "systems": ["sys-example"],
        "depends_on": [],
    }


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


def build(root: Path, created: str, body: str, phases: list[str]) -> Path:
    """An isolated repository: one plan with `body`, and the given phases registered under it."""
    shutil.copytree(ROOT / "schemas", root / "schemas")
    (root / "_data/projects").mkdir(parents=True)
    (root / "_data/tags.json").write_text('[{"id": "python"}]')
    (root / "docs/08-governance").mkdir(parents=True)
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
    plan = root / PLAN_PATH
    plan.parent.mkdir(parents=True)
    plan.write_text("---\n" + json.dumps(plan_meta(created)) + "\n---\n\n" + body + "\n")
    decisions = {**plan_meta(created), "id": "doc-decisions", "code": "GOV-001",
                 "title": "Decisions", "kind": "governance", "status": "active"}
    record = root / "docs/08-governance/GOV-001-decisions.md"
    record.write_text("---\n" + json.dumps(decisions) + "\n---\n\n# Decisions\n")
    backlog = {
        "schema_version": 1,
        "updated": created,
        "decision_record": "doc-decisions",
        "items": [phase(p) for p in phases],
    }
    (root / "docs/09-backlog").mkdir(parents=True)
    (root / "docs/09-backlog/backlog.yaml").write_text(json.dumps(backlog))
    return root


def errors_for(root: Path) -> list[str]:
    errors, _, result = audit(root)
    assert errors == []
    backlog_errors, catalog = audit_backlog(root, result)
    plan_errors = audit_plan_phases(root, result, catalog)[0]
    assert sorted(backlog_errors) == sorted(plan_errors)
    return plan_errors


def test_recent_plan_with_an_unnamed_registered_phase_fails_naming_both(tmp_path: Path) -> None:
    root = build(tmp_path, "2026-09-23", "# Example\n\nThis plan names phase-exa-01 only.",
                 ["phase-exa-01", "phase-exa-02"])
    assert errors_for(root) == [
        f"{PLAN_PATH}: registered phase phase-exa-02 is not named in its plan doc-example"
    ]


def test_the_same_plan_dated_before_the_cutoff_passes(tmp_path: Path) -> None:
    root = build(tmp_path, "2026-09-21", "# Example\n\nThis plan names phase-exa-01 only.",
                 ["phase-exa-01", "phase-exa-02"])
    assert errors_for(root) == []


def test_a_plan_naming_an_unregistered_phase_fails(tmp_path: Path) -> None:
    root = build(tmp_path, "2026-09-21", "# Example\n\nphase-exa-01, then phase-zzz-99.",
                 ["phase-exa-01"])
    assert errors_for(root) == [f"{PLAN_PATH}: names unregistered phase phase-zzz-99"]


def test_the_cutoff_date_itself_is_checked(tmp_path: Path) -> None:
    assert CUTOFF.isoformat() == "2026-09-22"
    root = build(tmp_path, "2026-09-22", "# Example\n\nNo phases named.", ["phase-exa-01"])
    assert errors_for(root) == [
        f"{PLAN_PATH}: registered phase phase-exa-01 is not named in its plan doc-example"
    ]


def test_a_fully_named_recent_plan_passes(tmp_path: Path) -> None:
    root = build(tmp_path, "2026-09-23", "# Example\n\nphase-exa-01 and phase-exa-02.",
                 ["phase-exa-01", "phase-exa-02"])
    assert errors_for(root) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("phase-grd-03", {"phase-grd-03"}),
        ("`agent/phase-grd-03`, phase-ses-05.", {"phase-grd-03", "phase-ses-05"}),
        ("phase-abc-123 is not an id", set()),
        ("phase-xxx-nn and phase-* are placeholders", set()),
        ("phase-Abc-01 has a capital", set()),
    ],
)
def test_named_phases_uses_the_schema_pattern(text: str, expected: set[str]) -> None:
    assert named_phases(text) == expected


def test_non_plan_documents_are_ignored() -> None:
    documents = {
        "doc-req": {"kind": "requirement", "path": "r.md", "created": "2026-09-23"},
    }
    errors, counts = inspect_plan_phases(documents, [], lambda path: "phase-zzz-99")
    assert errors == []
    assert counts["plans"] == 0


def test_a_plan_record_without_a_path_is_skipped() -> None:
    documents = {"doc-plan": {"kind": "plan", "status": "approved"}}
    items = [{"id": "phase-exa-01", "plan": "doc-plan"}]
    errors, counts = inspect_plan_phases(documents, items, lambda path: "")
    assert errors == []
    assert counts["plans"] == 0


def test_repository_passes_and_reports_its_counts() -> None:
    errors, _, result = audit(ROOT)
    assert errors == []
    _, catalog = audit_backlog(ROOT, result)
    plan_errors, counts = audit_plan_phases(ROOT, result, catalog)
    assert plan_errors == []
    assert counts["recent_plans"] > 0
    assert counts["registered_phases_checked"] > 0
    assert counts["phase_ids_named"] > 0
def test_the_backlog_audit_carries_the_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """audit_backlog returns audit_plan_phases' errors, so the governance command exits 1."""
    from src.governance import __main__ as governance

    errors, _, result = audit(ROOT)
    monkeypatch.setattr(
        governance, "audit_plan_phases", lambda root, result, catalog: (["planted"], {})
    )
    assert "planted" in audit_backlog(ROOT, result)[0]
