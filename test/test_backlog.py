"""Behavioral checks for coverage, readiness and truthful session completion."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from src.governance.__main__ import ROOT, audit, audit_backlog
from src.governance.backlog import (
    STALE_CLAIM_DAYS,
    claim_report_state,
    readiness,
    render_backlog,
    stale_claim_signal,
)

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
        "register": {
            "series": [
                {"code": "PLAN", "kind": "plan", "numbering": "counter"},
                {"code": "ADR", "kind": "adr", "numbering": "counter"},
                {"code": "SESS", "kind": "session", "numbering": "dated"},
            ],
            "reserved": [{"code": "ADR-004", "reason": "Fixture reservation."}],
            "retired": [{"code": "PLAN-011", "reason": "Fixture retirement."}],
        },
    }
    return tmp_path, catalog, result


def reviewed(root: Path, *phases: str) -> None:
    """A dispositioned GOV-018 record listing `phases`, so they may sit in next_up (REQ-028 R12)."""
    reviews = root / "docs/08-governance/reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    record = {"target": {"phases": list(phases)}, "status": "dispositioned", "findings": []}
    (reviews / "fixture.json").write_text(json.dumps(record))


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
    reviewed(backlog_repo[0], "phase-zzz-01")
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
    reviewed(backlog_repo[0], "phase-aaa-03", "phase-aaa-01")
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


def test_stale_claim_signal_fires_on_branch_recency_alone() -> None:
    assert stale_claim_signal(STALE_CLAIM_DAYS, True) is None
    signal = stale_claim_signal(STALE_CLAIM_DAYS + 1, True)
    assert signal is not None and "no commit on its branch" in signal


def test_stale_claim_signal_fires_on_missing_worktree_alone() -> None:
    assert stale_claim_signal(0, False) == "worktree missing"
    assert stale_claim_signal(0, True) is None


def test_stale_claim_signal_does_not_flag_a_claim_with_no_branch_yet() -> None:
    """A claim recorded a moment ago, before its branch exists, is not proof of abandonment."""
    assert stale_claim_signal(None, None) is None


def test_claim_report_state_distinguishes_three_cases() -> None:
    assert claim_report_state(None) == "no signal evaluated"
    assert claim_report_state({"days_since_commit": None, "worktree_exists": None}) == (
        "no evidence: no agent/<phase-id> branch found"
    )
    assert claim_report_state({"days_since_commit": 0, "worktree_exists": True}) == "no"
    stale = claim_report_state(
        {"days_since_commit": STALE_CLAIM_DAYS + 5, "worktree_exists": True}
    )
    assert stale.startswith("STALE: ")


def test_ready_report_names_the_stale_signal_beside_a_live_claim(backlog_repo: Any) -> None:
    """REQ-013 R01: a stale claim is reported as a distinct state naming its signal, and a
    live claim in the same run is not flagged."""
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
    evidence = {
        "phase-demo-01": {"days_since_commit": 0, "worktree_exists": True},
        "phase-demo-02": {"days_since_commit": STALE_CLAIM_DAYS + 3, "worktree_exists": True},
    }
    report = render_backlog(catalog, result["documents"], claim_evidence=evidence)
    live_row = next(line for line in report.splitlines() if line.startswith("| phase-demo-01 "))
    stale_row = next(line for line in report.splitlines() if line.startswith("| phase-demo-02 "))
    assert live_row.rstrip("|").rstrip().endswith("no")
    assert "STALE:" in stale_row
    assert f"{STALE_CLAIM_DAYS + 3}d" in stale_row


def test_ready_report_names_the_stale_signal_in_ready_only_mode_too(backlog_repo: Any) -> None:
    """The active-claims table, and its stale column, render in --ready as well as --backlog."""
    root, catalog, result = backlog_repo
    catalog["items"][0].update(status="active", agent="agent-one")
    assert check(backlog_repo) == []
    evidence = {"phase-demo-01": {"days_since_commit": None, "worktree_exists": False}}
    report = render_backlog(
        catalog, result["documents"], ready_only=True, claim_evidence=evidence
    )
    row = next(line for line in report.splitlines() if line.startswith("| phase-demo-01 "))
    assert "STALE: worktree missing" in row


def test_no_governance_code_writes_a_claim_release() -> None:
    """REQ-013 R03's negative half: no code path in src/governance/ clobbers a peer's claim
    by writing status: queued over it. This is a grep, not a behavioral run, because the
    property being tested is the absence of a code path rather than one input/output pair.
    `inspect_backlog` and `render_backlog` legitimately *read* "queued" as one of several
    status strings; the forbidden shape is an *assignment* of "queued" to a status field."""
    assignment_patterns = (
        '["status"] = "queued"',
        "['status'] = 'queued'",
        "status: queued",
        "status='queued'",
        'status="queued"',
    )
    governance_src = ROOT / "src" / "governance"
    for path in governance_src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in assignment_patterns:
            assert pattern not in text, f"{path} contains a claim-release assignment: {pattern}"


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


def test_deliverable_claiming_unreserved_code_fails(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    catalog["items"] = [phase(deliverables=["docs/04-decisions/ADR-007-new-decision.md"])]
    errors = check((root, catalog, result))
    assert errors == [
        "phase-demo-01: deliverable docs/04-decisions/ADR-007-new-decision.md claims unreserved "
        "code ADR-007; reserve it under reserved: in docs/08-governance/codes.yaml, "
        "naming this phase"
    ]


def test_deliverable_naming_retired_code_fails_with_retired_message(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    catalog["items"] = [phase(deliverables=["docs/01-plans/PLAN-011-reissued.md"])]
    errors = check((root, catalog, result))
    assert errors == [
        "phase-demo-01: deliverable docs/01-plans/PLAN-011-reissued.md names retired code "
        "PLAN-011; a retired code is never reissued, so allocate a new one with --next-code"
    ]


def test_deliverables_naming_existing_or_reserved_codes_pass(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    result["documents"].update(
        {
            "doc-plan": {"kind": "plan", "status": "approved", "code": "PLAN-039"},
            "doc-sub": {"kind": "plan", "status": "complete", "code": "PLAN-039.01"},
            "doc-session": {"kind": "session", "status": "complete", "code": "SESS-2026-09-06-04"},
        }
    )
    catalog["items"] = [
        phase(
            deliverables=[
                "docs/01-plans/PLAN-039-parent.md",
                "docs/01-plans/PLAN-039.01-child.md",
                "docs/03-sessions/SESS-2026-09-06-04-a-session.md",
                "docs/04-decisions/ADR-004-reserved-decision.md",
                "AGENTS.md",
                "docs/09-backlog/backlog.yaml",
            ]
        )
    ]
    assert check((root, catalog, result)) == []


def test_unknown_dated_code_is_not_misread_as_counter_code(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    catalog["items"] = [phase(deliverables=["docs/03-sessions/SESS-2026-09-07-01-new.md"])]
    errors = check((root, catalog, result))
    assert len(errors) == 1
    assert "unreserved code SESS-2026-09-07-01;" in errors[0]


def test_code_shape_outside_its_series_numbering_is_not_a_code(backlog_repo: Any) -> None:
    """A counter series never issues dated codes, so a date after its prefix claims nothing."""
    root, catalog, result = backlog_repo
    catalog["items"] = [
        phase(
            deliverables=[
                "docs/04-decisions/ADR-2026-09-29-01-freeze-notice.md",
                "docs/03-sessions/SESS-001-not-dated.md",
            ]
        )
    ]
    assert check((root, catalog, result)) == []


def test_repository_reservation_only_deliverables_pass() -> None:
    """Every coded deliverable in the live backlog that exists only as a reservation passes."""
    from src.governance.backlog import deliverable_code

    errors, _, result = audit(ROOT)
    assert errors == []
    backlog_errors, catalog = audit_backlog(ROOT, result)
    assert backlog_errors == []
    numbering = {entry["code"]: entry["numbering"] for entry in result["register"]["series"]}
    existing = {meta["code"] for meta in result["documents"].values() if meta.get("code")}
    reserved = {entry["code"] for entry in result["register"]["reserved"]}
    reservation_only = {
        code
        for item in catalog["items"]
        for path in item["deliverables"]
        if (code := deliverable_code(path, numbering)) and code not in existing
    }
    assert reservation_only
    assert reservation_only <= reserved


def write_ideas(root: Path, *ids: str) -> None:
    """A minimal idea log: one `created` event per id, enough for fold() to know it."""
    (root / "_data").mkdir(exist_ok=True)
    events = [
        {
            "idea": idea,
            "event": "created",
            "at": "2026-09-06T14:45:00-04:00",
            "title": f"Fixture idea {idea}",
            "body": "Fixture.",
        }
        for idea in ids
    ]
    (root / "_data/ideas.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))


def test_ideas_field_rejects_an_id_the_idea_log_does_not_contain(backlog_repo: Any) -> None:
    """REQ-036 R17: a made-up id fails the validator, naming the phase and the id."""
    root, catalog, _ = backlog_repo
    write_ideas(root, "000417")
    catalog["items"] = [phase(ideas=["000417", "999999"])]
    errors = check(backlog_repo)
    assert errors == [
        "phase-demo-01: ideas names 999999, which is not in _data/ideas.jsonl"
    ]


def test_ideas_field_with_known_ids_passes(backlog_repo: Any) -> None:
    root, catalog, _ = backlog_repo
    write_ideas(root, "000417", "000453")
    catalog["items"] = [phase(ideas=["000417", "000453"])]
    assert check(backlog_repo) == []


@pytest.mark.parametrize("value", [["417"], ["0004170"], ["abcdef"], []])
def test_ideas_field_schema_rejects_malformed_ids(backlog_repo: Any, value: list[str]) -> None:
    root, catalog, _ = backlog_repo
    write_ideas(root, "000417")
    catalog["items"] = [phase(ideas=value)]
    assert any(error.startswith("backlog:items.0.ideas") for error in check(backlog_repo))


def test_ideas_field_without_an_idea_log_fails_rather_than_passing(backlog_repo: Any) -> None:
    # load_events reads a missing log as empty, so the id is reported as unknown.
    _, catalog, _ = backlog_repo
    catalog["items"] = [phase(ideas=["000417"])]
    assert check(backlog_repo) == [
        "phase-demo-01: ideas names 000417, which is not in _data/ideas.jsonl"
    ]


def test_named_ideas_reads_only_standalone_known_ids_in_the_phase_text() -> None:
    from src.governance.backlog import named_ideas

    item = phase(
        scope=["Build on idea 000417's design (000417 again), see commit 3da1295 and a000453."],
        acceptance=["Ideas 000046 and 999999 are named.", "1234567 is too long."],
        next_action="Read 000522 first.",
        # The plan and the other fields are never read, even when they name a known id.
        title="Mentions 000100",
        verification=["Check 000101"],
    )
    known = {"000046", "000100", "000101", "000417", "000453", "000522"}
    assert named_ideas(item, known) == ["000046", "000417", "000522"]


def test_backfill_text_edits_only_ideas_blocks_and_is_idempotent() -> None:
    import yaml

    from src.governance.__main__ import MetadataLoader
    from src.governance.backlog import backfill_ideas_text, idea_backfill_diff

    text = (
        "schema_version: 1\n"
        "next_up:\n"
        "- phase-demo-01\n"
        "items:\n"
        "- id: phase-demo-01\n"
        "  sources: []\n"
        "  ideas:\n"
        "  - '000999'\n"
        "  systems:\n"
        "  - sys-demo\n"
        "  scope:\n"
        "  - 'Long text naming idea 000417, wrapped across\n"
        "    two lines exactly as written.'\n"
        "  acceptance: []\n"
        "  next_action: Then 000453.\n"
        "- id: phase-demo-02\n"
        "  systems:\n"
        "  - sys-demo\n"
        "  scope:\n"
        "  - Nothing named.\n"
        "  acceptance: []\n"
        "  next_action: None.\n"
    )
    known = {"000417", "000453", "000999"}
    catalog = yaml.load(text, Loader=MetadataLoader)
    assert idea_backfill_diff(catalog, known) == {
        "phase-demo-01": (["000417", "000453"], ["000999"])
    }
    rewritten = backfill_ideas_text(text, catalog, known)
    assert rewritten == text.replace("  - '000999'\n", "  - '000417'\n  - '000453'\n")
    reparsed = yaml.load(rewritten, Loader=MetadataLoader)
    assert idea_backfill_diff(reparsed, known) == {}
    assert backfill_ideas_text(rewritten, reparsed, known) == rewritten


def test_check_mode_reports_and_backfill_mode_repairs(
    backlog_repo: Any, monkeypatch: Any, capsys: Any
) -> None:
    """REQ-036 R18: check mode reports missing and extra ids and writes nothing; the backfill
    writes them; check mode then reports no difference."""
    import yaml

    from src.governance import __main__ as cli

    root, catalog, result = backlog_repo
    write_ideas(root, "000417", "000453")
    catalog["items"] = [
        phase(scope=["Build idea 000417."], ideas=["000453"]),
    ]
    path = root / "docs/09-backlog/backlog.yaml"
    path.write_text(yaml.safe_dump(catalog, sort_keys=False))
    before = path.read_text()
    monkeypatch.setattr(cli, "ROOT", root)
    monkeypatch.setattr(cli, "audit", lambda _: ([], [], result))
    monkeypatch.setattr(cli, "audit_idea_priority", lambda _: [])
    monkeypatch.setattr(cli, "audit_status_regression", lambda _root, _catalog: ([], []))

    monkeypatch.setattr("sys.argv", ["governance", "--check-ideas"])
    assert cli.main() == 1
    out = capsys.readouterr().out
    assert "phase-demo-01: missing 000417; extra 000453" in out
    assert path.read_text() == before

    monkeypatch.setattr("sys.argv", ["governance", "--backfill-ideas"])
    assert cli.main() == 0
    assert yaml.safe_load(path.read_text())["items"][0]["ideas"] == ["000417"]

    monkeypatch.setattr("sys.argv", ["governance", "--check-ideas"])
    assert cli.main() == 0
    assert "0 phases differ (0 missing, 0 extra)" in capsys.readouterr().out


def test_repository_idea_field_matches_its_backfill() -> None:
    """REQ-036 R17 and R18 on the committed backlog: every id is known, and a re-run of the
    backfill would change nothing."""
    from src.governance.__main__ import idea_ids
    from src.governance.backlog import idea_backfill_diff

    errors, _, result = audit(ROOT)
    assert errors == []
    backlog_errors, catalog = audit_backlog(ROOT, result)
    assert backlog_errors == []
    assert any(item.get("ideas") for item in catalog["items"])
    assert idea_backfill_diff(catalog, idea_ids(ROOT)) == {}
