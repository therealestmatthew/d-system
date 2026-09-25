"""The status-regression check: a phase must not silently leave ``status: complete``.

Ported from the source repository's regression tests to throwaway git repositories. The decisions
document is whatever the catalog's ``decision_record`` names, so these tests give it a name of
their own. Phase ids are built at run time for the plugin's source-reference check.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml
from regression import audit, check, find_regressions, is_recorded
from test_backlog import PH, TargetRepo
from test_backlog import phase as full_phase

HEADER = "# Accepted choices\n\n"
BACKLOG = "backlog.yaml"
DECISIONS = "choices.md"
BRANCH = "trunk"


def phase(**changes: Any) -> dict[str, Any]:
    base = {
        "id": "phase-example",
        "status": "complete",
        "session": "doc-session",
        "completion_evidence": ["docs/foo.md"],
        "result": "done",
    }
    base.update(changes)
    return base


def reopened(**changes: Any) -> dict[str, Any]:
    return phase(status="queued", session=None, completion_evidence=None, result=None, **changes)


def catalog(*phases: dict[str, Any]) -> dict[str, Any]:
    return {"items": list(phases)}


# --- pure logic: find_regressions ---------------------------------------------------------


def test_find_regressions_flags_status_leaving_complete() -> None:
    findings = find_regressions({"phase-example": phase()}, {"phase-example": reopened()})
    assert len(findings) == 1
    assert findings[0]["phase"] == "phase-example"
    assert findings[0]["from"] == "complete"
    assert findings[0]["to"] == "queued"
    assert set(findings[0]["lost"]) == {"session", "completion_evidence", "result"}


def test_find_regressions_flags_evidence_loss_while_staying_complete() -> None:
    findings = find_regressions({"phase-example": phase()},
                                {"phase-example": phase(completion_evidence=None)})
    assert len(findings) == 1
    assert findings[0]["to"] == "complete"
    assert findings[0]["lost"] == ["completion_evidence"]


def test_find_regressions_ignores_phase_never_complete() -> None:
    prior = {"phase-example": phase(status="active", session=None, completion_evidence=None,
                                    result=None)}
    assert find_regressions(prior, {"phase-example": reopened()}) == []


def test_find_regressions_ignores_phase_missing_from_either_side() -> None:
    assert find_regressions({"phase-example": phase()}, {}) == []
    assert find_regressions({}, {"phase-example": phase(status="queued")}) == []


def test_find_regressions_ignores_stable_complete() -> None:
    assert find_regressions({"phase-example": phase()}, {"phase-example": phase()}) == []


# --- pure logic: is_recorded --------------------------------------------------------------


def test_is_recorded_true_when_working_copy_adds_entry() -> None:
    working = HEADER + "phase-example was reopened because X.\n"
    assert is_recorded(HEADER, working, "phase-example") is True


def test_is_recorded_false_when_entry_names_a_different_phase() -> None:
    working = HEADER + "phase-other was reopened because X.\n"
    assert is_recorded(HEADER, working, "phase-example") is False


def test_is_recorded_false_when_entry_predates_the_change() -> None:
    text = HEADER + "phase-example was reopened long ago.\n"
    assert is_recorded(text, text, "phase-example") is False


def test_is_recorded_true_when_the_decisions_document_did_not_exist_before() -> None:
    assert is_recorded(None, "phase-example was reopened because X.\n", "phase-example") is True


def test_is_recorded_defeats_prefix_collision() -> None:
    """A longer id that starts with the target must not silence it."""
    target, longer = f"{PH}-lit-07", f"{PH}-lit-070"
    assert is_recorded(HEADER, HEADER + f"{longer} was reopened because X.\n", target) is False


def test_is_recorded_defeats_suffix_collision() -> None:
    target = f"{PH}-lit-07"
    assert is_recorded(HEADER, HEADER + f"mega{target} was reopened because X.\n",
                       target) is False


def test_is_recorded_true_for_a_bare_prose_mention() -> None:
    working = HEADER + "See the writeup: phase-example needed a second look.\n"
    assert is_recorded(HEADER, working, "phase-example") is True


def test_is_recorded_defeats_commented_out_mention() -> None:
    working = HEADER + "<!-- phase-example was reopened because X. -->\n"
    assert is_recorded(HEADER, working, "phase-example") is False


def test_is_recorded_defeats_commented_out_mention_even_with_visible_text_around() -> None:
    working = HEADER + "Some visible text.\n<!-- phase-example was reopened. -->\nMore text.\n"
    assert is_recorded(HEADER, working, "phase-example") is False


# --- integration: a real git repository ----------------------------------------------------


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    run_git(tmp_path, "init", "-q")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    run_git(tmp_path, "config", "user.name", "Test")
    return tmp_path


def write_backlog(root: Path, data: dict[str, Any]) -> None:
    (root / BACKLOG).write_text(yaml.safe_dump(data), encoding="utf-8")


def write_decisions(root: Path, text: str) -> None:
    (root / DECISIONS).write_text(text, encoding="utf-8")


def commit(root: Path, message: str) -> None:
    run_git(root, "add", "-A")
    run_git(root, "commit", "-q", "-m", message)


def run(root: Path, current: dict[str, Any]) -> tuple[list[str], list[str]]:
    return audit(root, current, BACKLOG, DECISIONS, BRANCH)


def seed(root: Path, *phases: dict[str, Any]) -> None:
    write_backlog(root, catalog(*(phases or (phase(),))))
    write_decisions(root, HEADER)
    commit(root, "initial")


def test_seeded_status_regression_fails_against_head(repo: Path) -> None:
    seed(repo)
    errors, _ = run(repo, catalog(reopened()))
    assert any("phase-example" in error and "complete -> queued" in error for error in errors)


def test_completion_evidence_removed_fails_against_head(repo: Path) -> None:
    seed(repo)
    errors, _ = run(repo, catalog(phase(completion_evidence=None)))
    assert any("phase-example" in error for error in errors)


def test_a_decisions_entry_permits_the_transition(repo: Path) -> None:
    seed(repo)
    write_decisions(repo, HEADER + "phase-example reopened per owner ruling.\n")
    assert run(repo, catalog(reopened()))[0] == []
    write_decisions(repo, HEADER + "phase-other reopened per owner ruling.\n")
    assert any("phase-example" in error for error in run(repo, catalog(reopened()))[0])


def test_unreadable_head_passes_with_a_note(repo: Path) -> None:
    errors, warnings = run(repo, catalog(reopened()))
    assert errors == []
    assert any("HEAD" in warning and "unreadable" in warning for warning in warnings)


def test_integration_branch_finding_warns_and_does_not_fail(repo: Path) -> None:
    seed(repo)
    run_git(repo, "branch", BRANCH)
    write_backlog(repo, catalog(reopened()))
    commit(repo, "regression arrives already committed on this branch")
    errors, warnings = run(repo, catalog(reopened()))
    assert errors == []
    assert any("phase-example" in warning and BRANCH in warning for warning in warnings)


def test_head_finding_still_fails_with_an_integration_branch_warning_present(repo: Path) -> None:
    seed(repo, phase(id="phase-a"), phase(id="phase-b"))
    run_git(repo, "branch", BRANCH)
    write_backlog(repo, catalog(reopened(id="phase-a"), phase(id="phase-b")))
    commit(repo, "phase-a regression arrives already committed")
    errors, warnings = run(repo, catalog(reopened(id="phase-a"), reopened(id="phase-b")))
    assert any("phase-b" in error for error in errors)
    assert any("phase-a" in warning and BRANCH in warning for warning in warnings)


def test_unreachable_integration_branch_notes_and_does_not_suppress_head(repo: Path) -> None:
    seed(repo)
    errors, warnings = run(repo, catalog(reopened()))
    assert any("phase-example" in error for error in errors)
    assert any(BRANCH in warning and "unreadable" in warning for warning in warnings)


def test_check_returns_only_the_requested_severity(repo: Path) -> None:
    seed(repo)
    current = catalog(reopened())
    errors, warnings = check(repo, "HEAD", "error", current, HEADER, BACKLOG, DECISIONS)
    assert errors and not warnings
    errors, warnings = check(repo, "HEAD", "warning", current, HEADER, BACKLOG, DECISIONS)
    assert warnings and not errors


# --- integration: the real check, the decisions document found through decision_record ------


def completed(target: TargetRepo) -> dict[str, Any]:
    return full_phase(plan="doc-plan", sources=[], systems=["sys-core"], status="complete",
                      session="doc-session", completion_evidence=[target.decisions],
                      result="Verified.")


def test_the_real_check_reports_a_regression_and_honours_the_named_decisions_document(
    tmp_path: Path,
) -> None:
    target = TargetRepo(tmp_path / "target")
    run_git(target.root, "config", "user.email", "test@example.com")
    run_git(target.root, "config", "user.name", "Test")
    target.catalog["items"] = [completed(target)]
    target.write()
    commit(target.root, "a complete phase")

    item = target.catalog["items"][0]
    item["status"] = "queued"
    for field in ("session", "completion_evidence", "result"):
        del item[field]
    result = target.check()
    assert result.returncode == 1
    assert f"status-regression (HEAD): {PH}-demo-01 complete -> queued" in result.stdout

    decisions = target.root / target.decisions
    decisions.write_text(decisions.read_text() + f"\n{PH}-demo-01 reopened by ruling.\n")
    result = target.check()
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_real_check_warns_against_the_configured_integration_branch(tmp_path: Path) -> None:
    target = TargetRepo(tmp_path / "target")
    run_git(target.root, "config", "user.email", "test@example.com")
    run_git(target.root, "config", "user.name", "Test")
    target.catalog["items"] = [completed(target)]
    target.write()
    commit(target.root, "a complete phase")
    run_git(target.root, "branch", BRANCH)
    item = target.catalog["items"][0]
    item["status"] = "queued"
    for field in ("session", "completion_evidence", "result"):
        del item[field]
    target.write()
    commit(target.root, "the regression arrives by merge")
    result = target.run("check.py", "--feature", "backlog", "--integration-branch", BRANCH)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"status-regression ({BRANCH}): {PH}-demo-01 complete -> queued" in result.stderr
