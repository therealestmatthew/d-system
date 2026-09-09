"""Behavioral checks for coverage, readiness and truthful session completion."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from src.governance.__main__ import ROOT, audit, audit_backlog
from src.governance.backlog import readiness, render_backlog

TODAY = date(2026, 9, 5)


def phase(**changes: Any) -> dict[str, Any]:
    return {
        "id": "phase-demo-01",
        "title": "One outcome",
        "plan": "doc-plan",
        "sources": ["doc-decisions"],
        "systems": ["sys-demo"],
        "owner": "repository-owner",
        "status": "queued",
        "priority": 1,
        "session_budget": 1,
        "depends_on": [],
        "scope": ["Produce one bounded result."],
        "acceptance": ["Result exists.", "Check passes."],
        "verification": ["Run a concrete check."],
        "deliverables": ["src/future.py"],
        "next_action": "Inspect the affected contract.",
        **changes,
    }


@pytest.fixture
def backlog_repo(tmp_path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas/backlog.schema.json").write_text(
        (ROOT / "schemas/backlog.schema.json").read_text()
    )
    (tmp_path / "docs/09-backlog").mkdir(parents=True)
    catalog = {
        "schema_version": 1,
        "updated": "2026-09-05",
        "decision_record": "doc-decisions",
        "items": [phase()],
    }
    result = {
        "documents": {
            "doc-plan": {"kind": "plan", "status": "approved"},
            "doc-decisions": {"kind": "governance", "status": "active"},
        },
        "systems": [{"id": "sys-demo"}],
        "owners": {"repository-owner": "Maintainer"},
    }
    return tmp_path, catalog, result


def check(fixture: tuple[Path, dict[str, Any], dict[str, Any]]) -> list[str]:
    root, catalog, result = fixture
    (root / "docs/09-backlog/backlog.yaml").write_text(json.dumps(catalog))
    return audit_backlog(root, result, TODAY)[0]


def test_repository_backlog_covers_all_open_plans() -> None:
    errors, _, result = audit(ROOT)
    assert errors == []
    errors, catalog = audit_backlog(ROOT, result)
    assert errors == []
    assert all(item["session_budget"] == 1 for item in catalog["items"])
    assert any(item["status"] == "deferred" for item in catalog["items"])


def test_read_only_queue_and_missing_future_deliverables(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    before = copy.deepcopy(catalog)
    assert check(backlog_repo) == []
    assert "ready" in render_backlog(catalog, result["documents"], ready_only=True)
    assert catalog == before
    assert not (root / "data").exists()
    assert not (root / "src/future.py").exists()


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"session_budget": 2}, "1 was expected"),
        ({"acceptance": ["Only one condition"]}, "too short"),
        ({"unexpected": True}, "Additional properties"),
        ({"status": "ready"}, "not one of"),
        ({"plan": "doc-decisions"}, "must reference a plan"),
        ({"sources": ["doc-missing"]}, "unknown source"),
        ({"systems": ["sys-missing"]}, "unknown system"),
        ({"owner": "missing"}, "unknown owner"),
        ({"depends_on": ["phase-missing-01"]}, "unresolved"),
        ({"status": "deferred"}, "requires blocked_reason"),
        ({"status": "blocked", "blocked_reason": "Missing input"}, "requires resume_when"),
        ({"status": "complete"}, "requires session and completion_evidence"),
        ({"completion_evidence": ["src/file.py"]}, "active, blocked or complete phase"),
        (
            {"status": "deferred", "blocked_reason": "x", "resume_when": "y", "result": "done"},
            "active, blocked or complete phase",
        ),
        (
            {"status": "cancelled", "blocked_reason": "Scope removed", "result": "done"},
            "active, blocked or complete phase",
        ),
        ({"deliverables": ["_private/secret"]}, "outside governance scope"),
    ],
)
def test_invalid_phase_fails(backlog_repo: Any, change: dict[str, Any], expected: str) -> None:
    backlog_repo[1]["items"][0].update(change)
    errors = check(backlog_repo)
    assert any(expected in error for error in errors), errors


def test_new_open_child_plan_requires_explicit_coverage(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    result["documents"]["doc-child"] = {"kind": "plan", "status": "draft", "parent": "doc-plan"}
    assert any("no non-cancelled phase: doc-child" in error for error in check(backlog_repo))
    catalog["items"][0]["sources"].append("doc-child")
    assert check(backlog_repo) == []


def test_cancelled_phase_does_not_hide_uncovered_plan(backlog_repo: Any) -> None:
    backlog_repo[1]["items"][0].update(status="cancelled", blocked_reason="Scope removed")
    assert any("no non-cancelled phase" in error for error in check(backlog_repo))


def test_duplicate_and_cyclic_phase_ids(backlog_repo: Any) -> None:
    catalog = backlog_repo[1]
    catalog["items"].append(phase())
    assert any("duplicate phase ID" in error for error in check(backlog_repo))
    catalog["items"][1].update(id="phase-demo-02", depends_on=["phase-demo-01"])
    catalog["items"][0]["depends_on"] = ["phase-demo-02"]
    assert any("dependency cycle" in error for error in check(backlog_repo))


def test_prerequisites_and_default_single_active_phase(backlog_repo: Any) -> None:
    catalog = backlog_repo[1]
    catalog["items"].append(phase(id="phase-demo-02", depends_on=["phase-demo-01"]))
    assert check(backlog_repo) == []
    index = {item["id"]: item for item in catalog["items"]}
    assert readiness(index["phase-demo-02"], index) == "waiting"
    index["phase-demo-02"]["status"] = "active"
    assert any("prerequisite" in error for error in check(backlog_repo))
    index["phase-demo-01"]["status"] = "active"
    assert any("at most 1 phases may be active" in error for error in check(backlog_repo))


def test_disjoint_phases_may_be_claimed_concurrently(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id="phase-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
        )
    )
    assert check(backlog_repo) == []
    report = render_backlog(catalog, result["documents"])
    assert "Active claims: 2 of 2 allowed." in report
    assert "agent/phase-demo-02" in report


def test_concurrent_claims_must_not_overlap(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id="phase-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["src/future.py"],
        )
    )
    assert any("share deliverable path src/future.py" in error for error in check(backlog_repo))
    catalog["items"][1]["deliverables"] = ["src"]
    assert any("share deliverable path src/future.py" in error for error in check(backlog_repo))
    catalog["items"][1]["deliverables"] = ["ts/src/other.tsx"]
    catalog["items"][1]["systems"] = ["sys-demo"]
    assert any("share system sys-demo" in error for error in check(backlog_repo))


def test_concurrent_claims_require_distinct_agents(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id="phase-demo-02",
            status="active",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
        )
    )
    assert any("requires an agent claim" in error for error in check(backlog_repo))
    catalog["items"][1]["agent"] = "agent-one"
    assert any("holds 2 active phases" in error for error in check(backlog_repo))


def test_dependency_linked_phases_never_run_concurrently(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="complete", session="doc-session", agent="agent-one")
    result["documents"]["doc-session"] = {"kind": "session", "status": "active"}
    catalog["items"].append(
        phase(
            id="phase-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
            depends_on=["phase-demo-01"],
        )
    )
    # A completed prerequisite is the only way a dependent phase becomes active at all.
    catalog["items"][0]["status"] = "active"
    errors = check(backlog_repo)
    assert any("dependency-linked" in error for error in errors), errors


def test_released_phase_drops_its_claim(backlog_repo: Any) -> None:
    backlog_repo[1]["items"][0].update(status="queued", agent="agent-one")
    assert any("must release its agent claim" in error for error in check(backlog_repo))


def test_completion_evidence_and_parent_rollup(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    catalog["items"][0].update(
        status="complete",
        session="doc-session",
        completion_evidence=["proof.txt"],
        result="Acceptance checks passed",
    )
    assert any("session must reference" in error for error in check(backlog_repo))
    result["documents"]["doc-session"] = {"kind": "session", "status": "active"}
    assert any("missing completion evidence" in error for error in check(backlog_repo))
    (root / "proof.txt").write_text("Actual implementation/check evidence")
    assert check(backlog_repo) == []
    result["documents"]["doc-plan"]["status"] = "complete"
    assert check(backlog_repo) == []
    catalog["items"].append(phase(id="phase-demo-02"))
    assert any("unfinished work belongs to closed plan" in error for error in check(backlog_repo))


def test_active_or_blocked_phase_may_record_interim_evidence(backlog_repo: Any) -> None:
    """A long or complex session can checkpoint real evidence before it closes (phase-ses-06)."""
    root, catalog, result = backlog_repo
    result["documents"]["doc-session"] = {"kind": "session", "status": "active"}
    (root / "proof.txt").write_text("Actual interim evidence, recorded mid-session")

    catalog["items"][0].update(
        status="active",
        session="doc-session",
        completion_evidence=["proof.txt"],
        result="Interim progress, not yet a completion claim",
    )
    assert check(backlog_repo) == []

    catalog["items"][0].update(
        status="blocked",
        blocked_reason="Waiting on an external input",
        resume_when="The input arrives",
    )
    assert check(backlog_repo) == []

    # Releasing the claim (queued/deferred/cancelled) drops the justification for interim evidence.
    catalog["items"][0].update(
        status="deferred", blocked_reason="Paused", resume_when="Input arrives"
    )
    assert any("active, blocked or complete phase" in error for error in check(backlog_repo))


def test_deferred_phase_does_not_become_ready(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    catalog["items"][0].update(
        status="deferred",
        blocked_reason="Need measured misses",
        resume_when="Evaluation demonstrates a gap",
    )
    assert check(backlog_repo) == []
    report = render_backlog(catalog, result["documents"], ready_only=True)
    assert "| phase-demo-01 |" not in report
    full_report = render_backlog(catalog, result["documents"])
    assert "Evaluation demonstrates a gap" in full_report


def test_missing_catalog_and_duplicate_yaml_fail(backlog_repo: Any) -> None:
    root, _, result = backlog_repo
    assert audit_backlog(root, result, TODAY)[0]
    (root / "docs/09-backlog/backlog.yaml").write_text("schema_version: 1\nschema_version: 2\n")
    assert any("duplicate YAML key" in error for error in audit_backlog(root, result, TODAY)[0])


def test_default_cli_enforces_coverage(backlog_repo: Any, monkeypatch: Any, capsys: Any) -> None:
    from src.governance import __main__ as cli

    root, catalog, result = backlog_repo
    result["documents"]["doc-new-plan"] = {"kind": "plan", "status": "approved"}
    (root / "docs/09-backlog/backlog.yaml").write_text(json.dumps(catalog))
    monkeypatch.setattr(cli, "ROOT", root)
    monkeypatch.setattr(cli, "audit", lambda _: ([], [], result))
    monkeypatch.setattr("sys.argv", ["governance"])
    assert cli.main() == 1
    assert "doc-new-plan" in capsys.readouterr().out


def test_next_up_promotes_phases_ahead_of_priority(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    """The queue is the insertion mechanism; IDs are never renumbered to reorder work."""
    _, catalog, result = backlog_repo
    catalog["items"] = [
        phase(id="phase-aaa-01", priority=1),
        phase(id="phase-zzz-01", priority=4),
    ]
    catalog["next_up"] = ["phase-zzz-01"]
    assert check(backlog_repo) == []
    rendered = render_backlog(catalog, result["documents"])
    rows = [line for line in rendered.split("\n") if line.startswith("| phase-")]
    assert rows[0].startswith("| phase-zzz-01"), rows
    assert rows[1].startswith("| phase-aaa-01"), rows
    assert "Queued to the front: phase-zzz-01." in rendered


def test_next_up_preserves_its_own_order(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    _, catalog, result = backlog_repo
    catalog["items"] = [phase(id=f"phase-aaa-0{n}") for n in (1, 2, 3)]
    catalog["next_up"] = ["phase-aaa-03", "phase-aaa-01"]
    assert check(backlog_repo) == []
    rows = [
        line for line in render_backlog(catalog, result["documents"]).split("\n")
        if line.startswith("| phase-")
    ]
    assert [row.split(" | ")[0] for row in rows[:3]] == [
        "| phase-aaa-03",
        "| phase-aaa-01",
        "| phase-aaa-02",
    ]


@pytest.mark.parametrize(
    ("queue", "items", "expected"),
    [
        (["phase-demo-99"], [phase()], "unknown phase phase-demo-99"),
        (
            ["phase-demo-01"],
            [phase(status="cancelled", blocked_reason="Superseded by another approach.")],
            "is cancelled; remove it",
        ),
    ],
)
def test_next_up_rejects_stale_entries(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
    queue: list[str],
    items: list[dict[str, Any]],
    expected: str,
) -> None:
    _, catalog, _ = backlog_repo
    catalog["items"] = items
    catalog["next_up"] = queue
    assert any(expected in error for error in check(backlog_repo))


def test_next_up_rejects_a_completed_phase(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    """A finished phase left in the queue would send the next session to redo it."""
    _, catalog, _ = backlog_repo
    catalog["items"] = [
        phase(
            status="complete",
            session="doc-session",
            completion_evidence=["schemas/backlog.schema.json"],
            result="Verified against the real command output.",
        )
    ]
    catalog["next_up"] = ["phase-demo-01"]
    assert any("is complete; remove it" in error for error in check(backlog_repo))


def test_backlog_without_next_up_still_orders_by_priority(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    _, catalog, result = backlog_repo
    catalog["items"] = [phase(id="phase-aaa-01", priority=3), phase(id="phase-zzz-01", priority=1)]
    assert check(backlog_repo) == []
    rows = [
        line for line in render_backlog(catalog, result["documents"]).split("\n")
        if line.startswith("| phase-")
    ]
    assert rows[0].startswith("| phase-zzz-01")
