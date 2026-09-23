"""Tests for the capability and approval broker (`phase-auto-02`, ADR-022, REQ-017 R01/R03).

Every test uses `tmp_path` for the broker's state directory; nothing here touches a real
repository path or the worktree's own `_working/`. The subprocess tests invoke `python -m
src.broker` exactly as a real tool boundary would, to demonstrate REQ-017 R03: a denied
capability is stopped at the boundary by a mechanical exit code, not by trusting a prompt.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.broker import approvals, enforcement

ROOT = Path(__file__).resolve().parents[1]


# --- enforcement: permissive default and audit trail -----------------------------------------


def test_permissive_default_allows_an_unconfigured_capability(tmp_path: Path) -> None:
    decision = enforcement.check("repository_read", state_dir=tmp_path)

    assert decision.allowed is True
    assert decision.capability == "repository_read"


def test_denied_capability_is_refused(tmp_path: Path) -> None:
    decision = enforcement.check(
        "external_network", denied=["external_network"], state_dir=tmp_path
    )

    assert decision.allowed is False
    assert "denied" in decision.reason


def test_denial_set_is_per_call_not_global(tmp_path: Path) -> None:
    """No built-in policy: the same capability is allowed or denied purely by what the caller
    passes on that call, confirming this module owns no taxonomy of its own (R02 stays open)."""
    denied_call = enforcement.check("publication", denied=["publication"], state_dir=tmp_path)
    allowed_call = enforcement.check("publication", denied=[], state_dir=tmp_path)

    assert denied_call.allowed is False
    assert allowed_call.allowed is True


def test_every_call_is_recorded_to_the_audit_log(tmp_path: Path) -> None:
    enforcement.check("repository_read", state_dir=tmp_path)
    enforcement.check("external_network", denied=["external_network"], state_dir=tmp_path)

    records = enforcement.read_audit_log(tmp_path)

    assert len(records) == 2
    assert records[0]["capability"] == "repository_read"
    assert records[0]["allowed"] is True
    assert records[1]["capability"] == "external_network"
    assert records[1]["allowed"] is False


def test_audit_record_carries_call_context(tmp_path: Path) -> None:
    enforcement.check(
        "source_mutation",
        denied=["source_mutation"],
        state_dir=tmp_path,
        context={"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}},
    )

    [record] = enforcement.read_audit_log(tmp_path)

    assert record["context"]["tool_name"] == "Edit"


# --- enforcement CLI: R03 demonstrated at a real process boundary ------------------------------


def _run_broker(*args: str, stdin: str, state_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.broker", *args, "--state-dir", str(state_dir)],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_cli_check_allows_by_default_with_exit_code_zero(tmp_path: Path) -> None:
    payload = json.dumps({"capability": "repository_read", "tool_name": "Read"})

    result = _run_broker("check", stdin=payload, state_dir=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    decision = json.loads(result.stdout)
    assert decision["allowed"] is True


def test_cli_check_blocks_a_denied_capability_with_exit_code_two(tmp_path: Path) -> None:
    """The mechanism REQ-017 R03 requires: an agent prompted to use a denied capability is
    stopped mechanically at the boundary. This feeds the CLI a tool-call payload naming a denied
    capability and asserts the blocking exit code and the recorded refusal — independent of
    whatever the prompt that produced the call said."""
    payload = json.dumps(
        {"capability": "external_network", "tool_name": "Bash", "tool_input": {"command": "curl"}}
    )

    result = _run_broker(
        "check", "--deny", "external_network", stdin=payload, state_dir=tmp_path
    )

    assert result.returncode == 2, result.stdout + result.stderr
    decision = json.loads(result.stdout)
    assert decision["allowed"] is False
    assert decision["capability"] == "external_network"

    records = enforcement.read_audit_log(tmp_path)
    assert len(records) == 1
    assert records[0]["allowed"] is False
    assert records[0]["context"]["tool_name"] == "Bash"


def test_cli_check_rejects_a_payload_naming_no_capability(tmp_path: Path) -> None:
    result = _run_broker("check", stdin=json.dumps({"tool_name": "Bash"}), state_dir=tmp_path)

    assert result.returncode == 1
    assert "no capability" in result.stderr


def test_cli_check_rejects_malformed_stdin(tmp_path: Path) -> None:
    result = _run_broker("check", stdin="not json", state_dir=tmp_path)

    assert result.returncode == 1
    assert "invalid JSON" in result.stderr


# --- approvals: the four required fields, immutability and expiry ------------------------------


def _future(hours: int = 1) -> str:
    import datetime

    return (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    ).isoformat()


def _past(hours: int = 1) -> str:
    import datetime

    return (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    ).isoformat()


def test_request_records_all_four_required_fields(tmp_path: Path) -> None:
    approval = approvals.request(
        "external_network", "download a dependency wheel", _future(), state_dir=tmp_path
    )

    assert approval.scope == "external_network"
    assert approval.reason == "download a dependency wheel"
    assert approval.expires_at
    assert approval.decision is None


@pytest.mark.parametrize(
    "scope,reason,expires",
    [
        ("", "reason given", None),
        ("scope given", "", None),
        ("scope given", "reason given", "not-a-timestamp"),
    ],
)
def test_request_rejects_a_missing_or_malformed_field(
    tmp_path: Path, scope: str, reason: str, expires: str | None
) -> None:
    with pytest.raises(approvals.ApprovalError):
        approvals.request(scope, reason, expires or _future(), state_dir=tmp_path)


def test_pending_lists_undecided_requests(tmp_path: Path) -> None:
    approval = approvals.request("scope", "reason", _future(), state_dir=tmp_path)

    pending = approvals.pending(state_dir=tmp_path)

    assert [row.id for row in pending] == [approval.id]


def test_decide_records_a_decision_and_removes_it_from_pending(tmp_path: Path) -> None:
    approval = approvals.request("scope", "reason", _future(), state_dir=tmp_path)

    decided = approvals.decide(
        approval.id, "approved", decided_by="owner", state_dir=tmp_path
    )

    assert decided.decision == "approved"
    assert decided.decided_by == "owner"
    assert approvals.pending(state_dir=tmp_path) == []


def test_decision_cannot_be_edited_after_the_fact(tmp_path: Path) -> None:
    approval = approvals.request("scope", "reason", _future(), state_dir=tmp_path)
    approvals.decide(approval.id, "approved", decided_by="owner", state_dir=tmp_path)

    with pytest.raises(approvals.ApprovalError, match="immutable"):
        approvals.decide(approval.id, "denied", decided_by="someone-else", state_dir=tmp_path)

    # The first decision still stands, unaltered by the rejected second attempt.
    assert approvals.get(approval.id, state_dir=tmp_path).decision == "approved"


def test_expired_approval_is_not_pending(tmp_path: Path) -> None:
    approval = approvals.request("scope", "reason", _past(), state_dir=tmp_path)

    assert approvals.pending(state_dir=tmp_path) == []
    assert approvals.is_expired(approvals.get(approval.id, state_dir=tmp_path))


def test_expired_approval_is_not_honoured_by_decide(tmp_path: Path) -> None:
    approval = approvals.request("scope", "reason", _past(), state_dir=tmp_path)

    with pytest.raises(approvals.ApprovalError, match="expired"):
        approvals.decide(approval.id, "approved", decided_by="owner", state_dir=tmp_path)

    assert approvals.get(approval.id, state_dir=tmp_path).decision is None


def test_decide_rejects_an_unknown_id(tmp_path: Path) -> None:
    with pytest.raises(approvals.ApprovalError):
        approvals.decide("does-not-exist", "approved", decided_by="owner", state_dir=tmp_path)


# --- approvals CLI ------------------------------------------------------------------------------


def test_cli_request_list_pending_and_decide_round_trip(tmp_path: Path) -> None:
    request_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.broker",
            "request",
            "--scope",
            "external_network",
            "--reason",
            "download a dependency wheel",
            "--expires",
            _future(),
            "--state-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert request_result.returncode == 0, request_result.stdout + request_result.stderr
    approval_id = json.loads(request_result.stdout)["id"]

    list_result = subprocess.run(
        [sys.executable, "-m", "src.broker", "list-pending", "--state-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert request_result.returncode == 0
    assert approval_id in list_result.stdout

    decide_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.broker",
            "decide",
            "--id",
            approval_id,
            "--decision",
            "approved",
            "--by",
            "owner",
            "--state-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert decide_result.returncode == 0, decide_result.stdout + decide_result.stderr
    assert json.loads(decide_result.stdout)["decision"] == "approved"
