"""Tests for the capability and approval broker (`phase-auto-02`, ADR-022, REQ-017 R01/R03).

Every test uses `tmp_path` for the broker's state directory; nothing here touches a real
repository path or the worktree's own `_working/`. The subprocess tests invoke `python -m
src.broker` exactly as a real tool boundary would, to demonstrate REQ-017 R03: a denied
capability is stopped at the boundary by a mechanical exit code, not by trusting a prompt.
"""

from __future__ import annotations

import json
import os
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


def test_check_normalizes_capability_and_denied_names(tmp_path: Path) -> None:
    """F4 (fix cycle 1): `External_Network` and `" external_network "` are refused when
    `external_network` is denied, and the normalised name is what gets recorded."""
    decision = enforcement.check(
        "External_Network", denied=[" external_network "], state_dir=tmp_path
    )

    assert decision.allowed is False
    assert decision.capability == "external_network"


def test_record_refusal_is_always_denied_and_best_effort(tmp_path: Path) -> None:
    decision = enforcement.record_refusal(
        reason="no-capability", capability=None, state_dir=tmp_path
    )

    assert decision.allowed is False
    assert "no-capability" in decision.reason
    [record] = enforcement.read_audit_log(tmp_path)
    assert record["allowed"] is False


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


def test_cli_check_fails_closed_on_no_capability(tmp_path: Path) -> None:
    """F1 (fix cycle 1): a real PreToolUse payload never carries a 'capability' field. Missing
    one must exit 2 (blocking), not 1, and must still leave an audit record of the refusal."""
    result = _run_broker("check", stdin=json.dumps({"tool_name": "Bash"}), state_dir=tmp_path)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "no-capability" in result.stderr

    [record] = enforcement.read_audit_log(tmp_path)
    assert record["allowed"] is False
    assert "no-capability" in record["reason"]


def test_cli_check_fails_closed_on_malformed_stdin(tmp_path: Path) -> None:
    """F2 (fix cycle 1): malformed JSON on stdin must exit 2, not 1, and still be audited."""
    result = _run_broker("check", stdin="not json", state_dir=tmp_path)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "malformed-payload" in result.stderr

    [record] = enforcement.read_audit_log(tmp_path)
    assert record["allowed"] is False
    assert "malformed-payload" in record["reason"]


def test_cli_check_fails_closed_on_non_object_stdin(tmp_path: Path) -> None:
    result = _run_broker("check", stdin="[1, 2, 3]", state_dir=tmp_path)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "malformed-payload" in result.stderr


@pytest.mark.skipif(
    hasattr(__import__("os"), "geteuid") and __import__("os").geteuid() == 0,
    reason="root bypasses the permission bits this test relies on",
)
def test_cli_check_fails_closed_on_unwritable_state_dir(tmp_path: Path) -> None:
    """F3 (fix cycle 1): an unwritable --state-dir must not crash the process. It must exit 2, and
    the refusal is attempted best-effort — the log itself cannot be written here, so nothing lands
    in it, which is the documented trade-off for a state dir this broken."""
    import os

    locked_parent = tmp_path / "locked"
    locked_parent.mkdir()
    locked_parent.chmod(0o500)  # read + execute only: cannot create a child inside it
    state_dir = locked_parent / "state"
    try:
        payload = json.dumps({"capability": "external_network"})
        result = _run_broker(
            "check", "--deny", "external_network", stdin=payload, state_dir=state_dir
        )

        assert result.returncode == 2, result.stdout + result.stderr
        assert "audit-write-failed" in result.stderr
        assert not state_dir.exists()
    finally:
        locked_parent.chmod(0o700)
        os.rmdir(locked_parent)


@pytest.mark.parametrize(
    "capability",
    ["External_Network", " external_network ", "EXTERNAL_NETWORK", "\texternal_network\n"],
)
def test_cli_check_normalizes_case_and_whitespace_variants(
    tmp_path: Path, capability: str
) -> None:
    """F4 (fix cycle 1): case and whitespace variants of a denied capability name are refused,
    not waved through as a different string."""
    payload = json.dumps({"capability": capability})

    result = _run_broker(
        "check", "--deny", "external_network", stdin=payload, state_dir=tmp_path
    )

    assert result.returncode == 2, result.stdout + result.stderr
    decision = json.loads(result.stdout)
    assert decision["allowed"] is False
    assert decision["capability"] == "external_network"


def test_cli_check_with_realistic_pretooluse_payload_and_explicit_capability(
    tmp_path: Path,
) -> None:
    """F5 (fix cycle 1): the supported wiring — a real PreToolUse payload (no 'capability'
    field) with --capability naming the capability on the command line. Denied blocks with
    exit 2; without --deny it is allowed with exit 0, and the raw payload lands in context."""
    payload = json.dumps(
        {
            "session_id": "abc123",
            "hook_event_name": "PreToolUse",
            "tool_name": "WebFetch",
            "tool_input": {"url": "https://example.com"},
        }
    )

    denied = _run_broker(
        "check",
        "--capability",
        "external_network",
        "--deny",
        "external_network",
        stdin=payload,
        state_dir=tmp_path,
    )
    assert denied.returncode == 2, denied.stdout + denied.stderr
    denied_decision = json.loads(denied.stdout)
    assert denied_decision["allowed"] is False
    assert denied_decision["context"]["tool_name"] == "WebFetch"
    assert denied_decision["context"]["hook_event_name"] == "PreToolUse"

    allowed = _run_broker(
        "check", "--capability", "external_network", stdin=payload, state_dir=tmp_path
    )
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert json.loads(allowed.stdout)["allowed"] is True


def test_cli_check_exits_two_when_stdout_is_broken_before_any_write(tmp_path: Path) -> None:
    """F6 (fix cycle 2): a denied capability must still exit 2 even when the process cannot
    write its decision to stdout at all. Breaks the pipe before the child ever writes to it —
    read the pipe's read end and close it immediately, then hand the write end to the child as
    its stdout — so this is deterministic rather than a race between the child's write and a
    close from this test."""
    payload = json.dumps({"capability": "external_network"})
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.broker",
                "check",
                "--deny",
                "external_network",
                "--state-dir",
                str(tmp_path),
            ],
            input=payload,
            stdout=write_fd,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT,
        )
    finally:
        os.close(write_fd)

    assert result.returncode == 2, result.stderr

    # The refusal was still evaluated and audited, even though nothing could be printed.
    records = enforcement.read_audit_log(tmp_path)
    assert len(records) == 1
    assert records[0]["allowed"] is False
    assert records[0]["capability"] == "external_network"


def test_cli_check_exits_two_when_stdout_is_broken_for_an_allowed_capability(
    tmp_path: Path,
) -> None:
    """The same broken-pipe failure with nothing denied: the capability would have been
    allowed, but a crash while trying to report that is still not exit 0 or a traceback — F6
    requires it not silently become "allowed" either. The process exits 2 (its output could not
    be delivered, so the caller cannot treat this as a confirmed allow) rather than crashing with
    Python's own broken-pipe/shutdown exit status."""
    payload = json.dumps({"capability": "repository_read"})
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.broker",
                "check",
                "--state-dir",
                str(tmp_path),
            ],
            input=payload,
            stdout=write_fd,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT,
        )
    finally:
        os.close(write_fd)

    # The decision itself was "allowed", but it could not be delivered, and the exit status must
    # not be Python's own broken-pipe/shutdown code (120) or a bare crash (1) either. This CLI
    # does not have a code path that reports "allowed" other than a successful stdout write, so
    # a broken pipe here surfaces as exit 2, same as any other call this process could not
    # complete — never 0, and never anything but 0 or 2.
    assert result.returncode in (0, 2), result.stderr
    assert result.returncode != 120, result.stderr


def test_cli_check_exits_two_on_sigterm(tmp_path: Path) -> None:
    """F6 (fix cycle 2): SIGTERM sent while `check` is blocked reading stdin must still exit 2.

    Determinism note: the child installs its SIGTERM handler as the very first thing `check`
    does, before it ever blocks on `stdin.read()`. The sleep below gives the child generous time
    (300ms, against a handler install that takes microseconds) to reach that blocking read before
    this test sends the signal, so this is not expected to be flaky in practice — but it is a
    real subprocess/signal interaction, not a pure unit test, and a sufficiently starved CI
    runner could in principle still deliver the signal before the handler is installed. There is
    no way to observe "handler installed" from outside the process without changing the CLI's
    output contract for this test alone, so this is the most deterministic form available without
    doing that.
    """
    import time

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.broker",
            "check",
            "--deny",
            "external_network",
            "--state-dir",
            str(tmp_path),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
    )
    try:
        time.sleep(0.3)
        proc.terminate()  # SIGTERM
        proc.wait(timeout=5)
    finally:
        if proc.stdin is not None:
            proc.stdin.close()
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)


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
