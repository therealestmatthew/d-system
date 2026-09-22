"""REQ-010: fail the governance check when a phase silently leaves `status: complete`.

Exercises `src.governance.regression` directly, on throwaway git repositories, so it never
touches this repository's own `backlog.yaml` or `GOV-003`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from src.governance.regression import audit, check, find_regressions, is_recorded

GOV003_HEADER = "# Accepted choices\n\n"


def phase(**changes: Any) -> dict[str, Any]:
    base = {
        "id": "phase-example",
        "status": "complete",
        "session": "SESS-2026-09-01-01",
        "completion_evidence": ["docs/foo.md"],
        "result": "done",
    }
    base.update(changes)
    return base


def catalog(*phases: dict[str, Any]) -> dict[str, Any]:
    return {"items": list(phases)}


# --- pure logic: find_regressions ---------------------------------------------------------


def test_find_regressions_flags_status_leaving_complete() -> None:
    prior = {"phase-example": phase()}
    current = {
        "phase-example": phase(
            status="queued", session=None, completion_evidence=None, result=None
        )
    }
    findings = find_regressions(prior, current)
    assert len(findings) == 1
    assert findings[0]["phase"] == "phase-example"
    assert findings[0]["from"] == "complete"
    assert findings[0]["to"] == "queued"
    assert set(findings[0]["lost"]) == {"session", "completion_evidence", "result"}


def test_find_regressions_flags_evidence_loss_while_staying_complete() -> None:
    prior = {"phase-example": phase()}
    current = {"phase-example": phase(completion_evidence=None)}
    findings = find_regressions(prior, current)
    assert len(findings) == 1
    assert findings[0]["to"] == "complete"
    assert findings[0]["lost"] == ["completion_evidence"]


def test_find_regressions_ignores_phase_never_complete() -> None:
    prior = {
        "phase-example": phase(status="active", session=None, completion_evidence=None, result=None)
    }
    current = {
        "phase-example": phase(status="queued", session=None, completion_evidence=None, result=None)
    }
    assert find_regressions(prior, current) == []


def test_find_regressions_ignores_phase_missing_from_either_side() -> None:
    prior = {"phase-example": phase()}
    assert find_regressions(prior, {}) == []
    assert find_regressions({}, {"phase-example": phase(status="queued")}) == []


def test_find_regressions_ignores_stable_complete() -> None:
    prior = {"phase-example": phase()}
    current = {"phase-example": phase()}
    assert find_regressions(prior, current) == []


# --- pure logic: is_recorded (R3) ---------------------------------------------------------


def test_is_recorded_true_when_working_copy_adds_entry() -> None:
    prior = GOV003_HEADER
    working = GOV003_HEADER + "phase-example was reopened because X.\n"
    assert is_recorded(prior, working, "phase-example") is True


def test_is_recorded_false_when_entry_names_a_different_phase() -> None:
    prior = GOV003_HEADER
    working = GOV003_HEADER + "phase-other was reopened because X.\n"
    assert is_recorded(prior, working, "phase-example") is False


def test_is_recorded_false_when_entry_predates_the_change() -> None:
    text = GOV003_HEADER + "phase-example was reopened long ago.\n"
    assert is_recorded(text, text, "phase-example") is False


def test_is_recorded_true_when_gov003_did_not_exist_before() -> None:
    working = "phase-example was reopened because X.\n"
    assert is_recorded(None, working, "phase-example") is True


# --- integration: a real git repository ----------------------------------------------------


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)


def init_repo(root: Path) -> None:
    run_git(root, "init", "-q")
    run_git(root, "config", "user.email", "test@example.com")
    run_git(root, "config", "user.name", "Test")


def write_backlog(root: Path, data: dict[str, Any]) -> None:
    (root / "backlog.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def write_gov003(root: Path, text: str) -> None:
    (root / "GOV-003.md").write_text(text, encoding="utf-8")


def commit(root: Path, message: str) -> None:
    run_git(root, "add", "-A")
    run_git(root, "commit", "-q", "-m", message)


def test_seeded_status_regression_fails_against_head(tmp_path: Path, monkeypatch: Any) -> None:
    """R1 + R5: a `complete -> queued` transition, uncommitted, fails against HEAD and names it."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")

    current = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))
    errors, warnings = audit(tmp_path, current)
    assert any("phase-example" in error for error in errors)
    assert any("complete -> queued" in error for error in errors)


def test_completion_evidence_removed_fails_against_head(tmp_path: Path, monkeypatch: Any) -> None:
    """R2: a phase that keeps `complete` while losing evidence still fails."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")

    current = catalog(phase(completion_evidence=None))
    errors, warnings = audit(tmp_path, current)
    assert any("phase-example" in error for error in errors)


def test_gov003_entry_permits_the_transition(tmp_path: Path, monkeypatch: Any) -> None:
    """R3: the same transition accompanied by a GOV-003 entry naming the phase exits clean;
    an entry naming a different phase does not."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")

    current = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))

    write_gov003(tmp_path, GOV003_HEADER + "phase-example reopened per owner ruling.\n")
    errors, warnings = audit(tmp_path, current)
    assert errors == []

    write_gov003(tmp_path, GOV003_HEADER + "phase-other reopened per owner ruling.\n")
    errors, warnings = audit(tmp_path, current)
    assert any("phase-example" in error for error in errors)


def test_unreadable_head_passes_with_a_note(tmp_path: Path, monkeypatch: Any) -> None:
    """A repository with no commits yet (no HEAD to read) passes with a one-line note."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)

    current = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))
    errors, warnings = audit(tmp_path, current)
    assert errors == []
    assert any("HEAD" in warning and "unreadable" in warning for warning in warnings)


def test_dev_relative_finding_warns_and_does_not_fail(tmp_path: Path, monkeypatch: Any) -> None:
    """R6: a regression already committed on this branch (arrived by merge) is invisible to the
    HEAD-relative check but shows up as a warning against `dev`, without failing the run."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")
    run_git(tmp_path, "branch", "dev")

    regressed = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))
    write_backlog(tmp_path, regressed)
    commit(tmp_path, "regression arrives already committed on this branch")

    errors, warnings = audit(tmp_path, regressed)
    assert errors == []
    assert any("phase-example" in warning and "dev" in warning for warning in warnings)


def test_head_relative_finding_still_fails_with_dev_warning_present(
    tmp_path: Path, monkeypatch: Any
) -> None:
    """A HEAD-relative regression still exits non-zero even when a dev-relative warning is also
    present for a different phase."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase(id="phase-a"), phase(id="phase-b")))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")
    run_git(tmp_path, "branch", "dev")

    # phase-a's regression already landed on this branch (dev-only warning).
    write_backlog(
        tmp_path,
        catalog(
            phase(
                id="phase-a",
                status="queued",
                session=None,
                completion_evidence=None,
                result=None,
            ),
            phase(id="phase-b"),
        ),
    )
    commit(tmp_path, "phase-a regression arrives already committed")

    # phase-b regresses only in the uncommitted working copy passed as `current` (HEAD-relative).
    current = catalog(
        phase(id="phase-a", status="queued", session=None, completion_evidence=None, result=None),
        phase(id="phase-b", status="queued", session=None, completion_evidence=None, result=None),
    )
    errors, warnings = audit(tmp_path, current)
    assert any("phase-b" in error for error in errors)
    assert any("phase-a" in warning and "dev" in warning for warning in warnings)


def test_unreachable_dev_notes_and_does_not_suppress_head(tmp_path: Path, monkeypatch: Any) -> None:
    """No `dev` ref at all: note it, keep the HEAD-relative check running unaffected."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")

    current = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))
    errors, warnings = audit(tmp_path, current)
    assert any("phase-example" in error for error in errors)
    assert any("dev" in warning and "unreadable" in warning for warning in warnings)


def test_check_returns_only_the_requested_severity(tmp_path: Path, monkeypatch: Any) -> None:
    """`check()` in isolation: an error-severity call never populates warnings and vice versa,
    for the same finding."""
    import src.governance.regression as regression

    monkeypatch.setattr(regression, "BACKLOG_PATH", "backlog.yaml")
    monkeypatch.setattr(regression, "DECISIONS_PATH", "GOV-003.md")
    init_repo(tmp_path)
    write_backlog(tmp_path, catalog(phase()))
    write_gov003(tmp_path, GOV003_HEADER)
    commit(tmp_path, "initial")

    current = catalog(phase(status="queued", session=None, completion_evidence=None, result=None))
    errors, warnings = check(tmp_path, "HEAD", "error", current, GOV003_HEADER)
    assert errors and not warnings

    errors, warnings = check(tmp_path, "HEAD", "warning", current, GOV003_HEADER)
    assert warnings and not errors
