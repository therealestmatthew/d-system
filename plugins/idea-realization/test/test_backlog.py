"""Behavioral checks for coverage, readiness and truthful session completion.

Ported from the source repository's backlog tests to fixture catalogs. Phase ids and dates are
built at run time so this file carries none for the plugin's source-reference check to flag.
"""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

import paths
import pytest
from backlog import (
    STALE_CLAIM_DAYS,
    claim_report_state,
    readiness,
    render_backlog,
    stale_claim_signal,
)
from checks import backlog as feature

PH = "phase"
TODAY = date(2030, 1, 5)


def phase(**changes: Any) -> dict[str, Any]:
    return {
        "id": f"{PH}-demo-01",
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
    (tmp_path / "backlog").mkdir()
    catalog = {
        "schema_version": 1,
        "updated": TODAY.isoformat(),
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


def config(root: Path) -> paths.Config:
    return paths.resolve({"root": str(root)}, env={})


def audit(root: Path, result: dict[str, Any]) -> list[str]:
    """The plugin's backlog path: read and schema-check the file, then run every rule."""
    errors, catalog = feature.load_catalog(config(root))
    if errors:
        return errors
    return feature.inspect(root, catalog, result["documents"],
                           {item["id"] for item in result["systems"]}, set(result["owners"]),
                           TODAY)


def check(fixture: tuple[Path, dict[str, Any], dict[str, Any]]) -> list[str]:
    root, catalog, result = fixture
    (root / "backlog/backlog.yaml").write_text(json.dumps(catalog))
    return audit(root, result)


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
        ({"depends_on": [f"{PH}-missing-01"]}, "unresolved"),
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
        ({"deliverables": [".git/config"]}, "outside the repository's tracked content"),
        ({"deliverables": ["../elsewhere"]}, "expected repository-relative path"),
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
    catalog["items"][1].update(id=f"{PH}-demo-02", depends_on=[f"{PH}-demo-01"])
    catalog["items"][0]["depends_on"] = [f"{PH}-demo-02"]
    assert any("dependency cycle" in error for error in check(backlog_repo))


def test_prerequisites_and_default_single_active_phase(backlog_repo: Any) -> None:
    catalog = backlog_repo[1]
    catalog["items"].append(phase(id=f"{PH}-demo-02", depends_on=[f"{PH}-demo-01"]))
    assert check(backlog_repo) == []
    index = {item["id"]: item for item in catalog["items"]}
    assert readiness(index[f"{PH}-demo-02"], index) == "waiting"
    index[f"{PH}-demo-02"]["status"] = "active"
    assert any("prerequisite" in error for error in check(backlog_repo))
    index[f"{PH}-demo-01"]["status"] = "active"
    assert any("at most 1 phases may be active" in error for error in check(backlog_repo))


def test_disjoint_phases_may_be_claimed_concurrently(backlog_repo: Any) -> None:
    root, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id=f"{PH}-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
        )
    )
    assert check(backlog_repo) == []
    report = render_backlog(catalog, result["documents"])
    assert "Active claims: 2 of 2 allowed." in report
    assert f"agent/{PH}-demo-02" in report


def test_concurrent_claims_must_not_overlap(backlog_repo: Any) -> None:
    _, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id=f"{PH}-demo-02",
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
            id=f"{PH}-demo-02",
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
            id=f"{PH}-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
            depends_on=[f"{PH}-demo-01"],
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
    catalog["items"].append(phase(id=f"{PH}-demo-02"))
    assert any("unfinished work belongs to closed plan" in error for error in check(backlog_repo))


def test_active_or_blocked_phase_may_record_interim_evidence(backlog_repo: Any) -> None:
    """A long or complex session can checkpoint real evidence before it closes."""
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
    assert f"| {PH}-demo-01 |" not in report
    full_report = render_backlog(catalog, result["documents"])
    assert "Evaluation demonstrates a gap" in full_report


def test_missing_catalog_and_duplicate_yaml_fail(backlog_repo: Any) -> None:
    root, _, result = backlog_repo
    assert audit(root, result)
    (root / "backlog/backlog.yaml").write_text("schema_version: 1\nschema_version: 2\n")
    assert any("duplicate YAML key" in error for error in audit(root, result))


def test_next_up_promotes_phases_ahead_of_priority(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    """The queue is the insertion mechanism; IDs are never renumbered to reorder work."""
    _, catalog, result = backlog_repo
    catalog["items"] = [
        phase(id=f"{PH}-aaa-01", priority=1),
        phase(id=f"{PH}-zzz-01", priority=4),
    ]
    catalog["next_up"] = [f"{PH}-zzz-01"]
    assert check(backlog_repo) == []
    rendered = render_backlog(catalog, result["documents"])
    rows = [line for line in rendered.split("\n") if line.startswith("| phase-")]
    assert rows[0].startswith(f"| {PH}-zzz-01"), rows
    assert rows[1].startswith(f"| {PH}-aaa-01"), rows
    assert f"Queued to the front: {PH}-zzz-01." in rendered


def test_next_up_preserves_its_own_order(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    _, catalog, result = backlog_repo
    catalog["items"] = [phase(id=f"{PH}-aaa-0{n}") for n in (1, 2, 3)]
    catalog["next_up"] = [f"{PH}-aaa-03", f"{PH}-aaa-01"]
    assert check(backlog_repo) == []
    rows = [
        line for line in render_backlog(catalog, result["documents"]).split("\n")
        if line.startswith("| phase-")
    ]
    assert [row.split(" | ")[0] for row in rows[:3]] == [
        f"| {PH}-aaa-03",
        f"| {PH}-aaa-01",
        f"| {PH}-aaa-02",
    ]


@pytest.mark.parametrize(
    ("queue", "items", "expected"),
    [
        ([f"{PH}-demo-99"], [phase()], f"unknown phase {PH}-demo-99"),
        (
            [f"{PH}-demo-01"],
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
    catalog["next_up"] = [f"{PH}-demo-01"]
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
    """A stale claim is reported as a distinct state naming its signal, and a
    live claim in the same run is not flagged."""
    root, catalog, result = backlog_repo
    result["systems"].append({"id": "sys-other"})
    catalog["max_active"] = 2
    catalog["items"][0].update(status="active", agent="agent-one")
    catalog["items"].append(
        phase(
            id=f"{PH}-demo-02",
            status="active",
            agent="agent-two",
            systems=["sys-other"],
            deliverables=["ts/src/other.tsx"],
        )
    )
    assert check(backlog_repo) == []
    evidence = {
        f"{PH}-demo-01": {"days_since_commit": 0, "worktree_exists": True},
        f"{PH}-demo-02": {"days_since_commit": STALE_CLAIM_DAYS + 3, "worktree_exists": True},
    }
    report = render_backlog(catalog, result["documents"], claim_evidence=evidence)
    live_row = next(line for line in report.splitlines() if line.startswith(f"| {PH}-demo-01 "))
    stale_row = next(line for line in report.splitlines() if line.startswith(f"| {PH}-demo-02 "))
    assert live_row.rstrip("|").rstrip().endswith("no")
    assert "STALE:" in stale_row
    assert f"{STALE_CLAIM_DAYS + 3}d" in stale_row


def test_ready_report_names_the_stale_signal_in_ready_only_mode_too(backlog_repo: Any) -> None:
    """The active-claims table and its stale column render in the ready-only report too."""
    root, catalog, result = backlog_repo
    catalog["items"][0].update(status="active", agent="agent-one")
    assert check(backlog_repo) == []
    evidence = {f"{PH}-demo-01": {"days_since_commit": None, "worktree_exists": False}}
    report = render_backlog(
        catalog, result["documents"], ready_only=True, claim_evidence=evidence
    )
    row = next(line for line in report.splitlines() if line.startswith(f"| {PH}-demo-01 "))
    assert "STALE: worktree missing" in row


def test_backlog_without_next_up_still_orders_by_priority(
    backlog_repo: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    _, catalog, result = backlog_repo
    catalog["items"] = [phase(id=f"{PH}-aaa-01", priority=3), phase(id=f"{PH}-zzz-01", priority=1)]
    assert check(backlog_repo) == []
    rows = [
        line for line in render_backlog(catalog, result["documents"]).split("\n")
        if line.startswith("| phase-")
    ]
    assert rows[0].startswith(f"| {PH}-zzz-01")


# --- The real scripts on a fixture repository ------------------------------------------------


class TargetRepo:
    """A scaffolded repository: the template registers, one system, one approved plan, a
    decisions document under a name of its own, a session record, and a backlog."""

    def __init__(self, root: Path) -> None:
        import shutil
        import subprocess

        import yaml
        from conftest import PLUGIN_ROOT

        self.root = root
        self.today = date.today()
        stamp = self.today.isoformat()
        docs = root / "docs"
        docs.mkdir(parents=True)
        for name in ("codes.yaml", "systems.yaml"):
            shutil.copy(PLUGIN_ROOT / "templates" / name, docs / name)
        registry = yaml.safe_load((docs / "systems.yaml").read_text())
        registry["systems"] = [
            {"id": sys_id, "name": sys_id, "domain": "application", "status": "planned",
             "owner": "repository-owner", "paths": [], "depends_on": [], "description": "A."}
            for sys_id in ("sys-core", "sys-other")
        ]
        (docs / "systems.yaml").write_text(yaml.safe_dump(registry))

        def document(folder: str, code: str, **meta: Any) -> None:
            front = {"schema_version": 1, "code": code, "owner": "repository-owner",
                     "created": stamp, "updated": stamp, "systems": [], "depends_on": [],
                     **meta}
            (docs / folder).mkdir(exist_ok=True)
            (docs / folder / f"{code}-{meta['id']}.md").write_text(
                "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# T\n\nBody.\n")

        document("plans", "PLAN" + "-001", id="doc-plan", title="Plan", kind="plan",
                 status="approved")
        document("governance", "GOV" + "-001", id="doc-choices", title="Choices",
                 kind="governance", status="active")
        document("sessions", "SESS" + f"-{stamp}-01", id="doc-session", title="Session",
                 kind="session", status="active")
        self.decisions = f"docs/governance/{'GOV' + '-001'}-doc-choices.md"
        self.catalog: dict[str, Any] = {
            "schema_version": 1, "updated": stamp, "decision_record": "doc-choices",
            "max_active": 2, "next_up": [],
            "items": [phase(plan="doc-plan", sources=[], systems=["sys-core"])],
        }
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)

    def write(self) -> None:
        import yaml

        (self.root / "backlog").mkdir(exist_ok=True)
        (self.root / "backlog" / "backlog.yaml").write_text(yaml.safe_dump(self.catalog))

    def run(self, script: str, *args: str) -> Any:
        import shutil
        import subprocess
        import sys

        from conftest import SCRIPTS

        uv = shutil.which("uv")
        runner = [uv, "run", "--quiet", "--no-project", "--script"] if uv else [sys.executable]
        return subprocess.run([*runner, str(SCRIPTS / script), *args, "--root", str(self.root)],
                              cwd=self.root.parent, capture_output=True, text=True, check=False)

    def check(self) -> Any:
        self.write()
        return self.run("check.py", "--feature", "backlog")


@pytest.fixture
def target(tmp_path: Path) -> TargetRepo:
    return TargetRepo(tmp_path / "target")


def test_a_clean_backlog_passes_the_real_check(target: TargetRepo) -> None:
    result = target.check()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "backlog: OK" in result.stdout


def test_two_active_phases_sharing_a_system_fail_naming_both(target: TargetRepo) -> None:
    first, second = f"{PH}-demo-01", f"{PH}-demo-02"
    target.catalog["items"][0].update(status="active", agent="agent-one")
    target.catalog["items"].append(phase(id=second, plan="doc-plan", sources=[],
                                         systems=["sys-core"], status="active",
                                         agent="agent-two", deliverables=["other/"]))
    result = target.check()
    assert result.returncode == 1
    assert f"{first}/{second}: concurrent phases share system sys-core" in result.stdout


def test_no_decision_record_passes_and_says_regression_did_not_run(target: TargetRepo) -> None:
    del target.catalog["decision_record"]
    result = target.check()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "status-regression not run" in result.stderr


def test_a_decision_record_resolving_to_no_document_fails(target: TargetRepo) -> None:
    target.catalog["decision_record"] = "doc-missing"
    result = target.check()
    assert result.returncode == 1
    assert "decision_record must reference governance or an ADR" in result.stdout


def test_the_scaffolded_seed_passes_the_check(tmp_path: Path) -> None:
    """A fresh repository's backlog seed has no phases and no decision_record, and is clean."""
    import scaffold

    root = tmp_path / "fresh"
    root.mkdir()
    fresh = paths.resolve({"root": str(root)}, env={})
    scaffold.scaffold(fresh, ["backlog", "documents"])
    notes: list[str] = []
    assert feature.audit(fresh, note=notes.append) == []
    assert any("status-regression not run" in line for line in notes)


def test_a_document_tree_with_errors_is_reported_not_guessed(target: TargetRepo) -> None:
    (target.root / "docs" / "systems.yaml").write_text("schema_version: 1\n")
    result = target.check()
    assert result.returncode == 1
    assert "not checked: the document tree has errors" in result.stdout


def test_a_repository_without_a_backlog_has_nothing_to_check(tmp_path: Path) -> None:
    assert feature.audit(paths.resolve({"root": str(tmp_path)}, env={})) == []


def test_ready_prints_the_queue_through_the_cli(target: TargetRepo) -> None:
    target.write()
    result = target.run("cli.py", "ready")
    assert result.returncode == 0, result.stderr
    assert f"| {PH}-demo-01 | One outcome | — | 1 | ready | — | — |" in result.stdout
    full = target.run("cli.py", "ready", "--all")
    assert "## Phase details" in full.stdout


def test_ready_refuses_a_broken_backlog(target: TargetRepo) -> None:
    target.catalog["items"][0]["status"] = "nonsense"
    target.write()
    result = target.run("cli.py", "ready")
    assert result.returncode == 1
    assert "nonsense" in result.stderr


def test_no_plugin_script_writes_a_claim_release() -> None:
    """No script clobbers a peer's claim by writing ``status: queued`` over it. A grep, because
    the property is the absence of a code path. Reading "queued" is fine; assigning it is not."""
    from conftest import SCRIPTS

    patterns = ('["status"] = "queued"', "['status'] = 'queued'", "status: queued",
                "status='queued'", 'status="queued"')
    for path in SCRIPTS.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            assert pattern not in text, f"{path} contains a claim-release assignment: {pattern}"


# --- The session skills --------------------------------------------------------------------


def skill(name: str) -> str:
    from conftest import PLUGIN_ROOT

    return (PLUGIN_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


PROHIBITION = ("never", "forbidden", "not", "only")


def test_checkpoint_names_the_complete_status_only_to_forbid_it() -> None:
    lines = [line for line in skill("checkpoint").splitlines() if "status: complete" in line]
    assert lines
    for line in lines:
        assert any(word in line.lower() for word in PROHIBITION), line


def test_session_close_states_the_three_completion_conditions() -> None:
    text = skill("session-close")
    assert "all three" in text
    for condition in ("Verification ran green",
                      "An independent review found no unresolved discrepancy",
                      "The branch is integrated with the owner's approval"):
        assert condition in text, condition


def test_no_skill_names_an_integration_branch() -> None:
    import re

    from conftest import PLUGIN_ROOT

    default = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())[
        "userConfig"]["integration_branch"]["default"]
    for path in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        for name in {default, "dev", "master", "trunk"}:
            assert not re.search(rf"(?<![\w/.-]){re.escape(name)}(?![\w/.-])", text), (path, name)


def test_the_backlog_skill_never_claims() -> None:
    text = skill("backlog")
    lines = [line for line in text.splitlines() if "status: active" in line]
    assert lines and all("forbidden" in line or "never" in line for line in lines), lines
    for command in ("git commit", "git push", "git worktree", "--claim", "agent: agent-"):
        assert command not in text, command


def test_the_session_skills_read_branch_and_directory_from_the_options() -> None:
    for name in ("session-start", "session-close"):
        text = skill(name)
        assert "CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}'" in text
        assert "CLAUDE_PLUGIN_OPTION_WORKTREE_DIR='${user_config.worktree_dir}'" in text
        assert "scripts/paths.py" in text
