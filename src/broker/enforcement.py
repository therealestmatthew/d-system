"""Tool-boundary capability enforcement, with a permissive default.

`check()` is the one function a tool boundary calls. It takes the name of a capability an agent
is about to exercise, decides whether it may proceed, and records the decision to an audit log
before returning. The permissive default: a capability not named in the caller's `denied` set is
allowed. ADR-022 ships this shape deliberately — the repository has no precedent for a
general-purpose capability taxonomy, so this module owns no built-in list of capabilities,
roles or denials. Every denial is supplied explicitly by the caller, per call.

Capability names are compared after normalisation: both `capability` and every entry of `denied`
are stripped of leading/trailing whitespace and case-folded before comparison, so `External_Network`
and `" external_network "` are refused when `external_network` is denied. The normalised name,
not the raw input, is what the `Decision` and the audit record carry — a caller reading the log
sees the name the comparison actually ran on.

This satisfies REQ-017 R01 (the broker exists and can refuse before any unattended work starts)
and R03 (a denied capability is stopped at the boundary, not trusted to a prompt). It does not
satisfy R02 (a run's capability set names specific actions, not a role) — that requires a real
capability taxonomy, which does not exist yet and is recorded open in ADR-022.

The mechanism is meant to sit at a real tool boundary: a caller that intercepts a tool call
before it runs, extracts a capability name from it, and calls `check()` (directly, or through
this package's CLI in `__main__.py`) before letting the call proceed. Nothing in this repository
does that yet — see the package docstring in `src/broker/__init__.py` for what the wiring would
be and why it is out of this phase's scope.

`record_refusal()` exists for the case `check()` itself cannot decide or cannot be trusted to
have decided correctly — a malformed call, a missing capability name, or a failure to write the
ordinary audit record. A decision the broker cannot make is a refusal, not a pass: this fail-closed
behaviour is what `src/broker/__main__.py`'s `check` subcommand relies on to guarantee every error
path exits with the blocking code, never the non-blocking one.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

#: Default location for the audit log when no caller-supplied directory is given. Gitignored
#: (`_working/` — see the repository .gitignore) so no run of this module writes a tracked file.
#: Every test in `test/test_broker.py` passes its own `tmp_path` instead of relying on this.
DEFAULT_STATE_DIR = Path("_working/broker")

#: Filename for the append-only audit log inside a state directory.
AUDIT_LOG_NAME = "audit.jsonl"


@dataclasses.dataclass(frozen=True)
class Decision:
    """The outcome of one `check()` call. Immutable: a decision is not edited after it is made,
    only appended to the audit log as one more record."""

    capability: str
    allowed: bool
    reason: str
    at: str
    context: dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def audit_log_path(state_dir: Path) -> Path:
    """Where the audit log lives under a given state directory."""
    return state_dir / AUDIT_LOG_NAME


def _append_audit(state_dir: Path, record: dict[str, Any]) -> None:
    """Write one record to the audit log. Raises `OSError` if `state_dir` cannot be created or
    written to — this is not swallowed here, because a caller that needs to know the write
    failed (to fail closed instead of silently succeeding) needs the exception to reach it."""
    state_dir.mkdir(parents=True, exist_ok=True)
    with audit_log_path(state_dir).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _try_append_audit(state_dir: Path, record: dict[str, Any]) -> bool:
    """Best-effort audit write for the refusal path: attempts `_append_audit` and swallows an
    `OSError` rather than propagating it. Used only by `record_refusal()`, which must be able to
    return a refusal even when `state_dir` itself is the reason the ordinary path failed — a
    refusal that cannot be logged is still a refusal, not a crash."""
    try:
        _append_audit(state_dir, record)
        return True
    except OSError:
        return False


def _normalize(capability: str) -> str:
    """Strip whitespace and case-fold, so capability names are compared and recorded the same
    way regardless of how a caller spells or pads them."""
    return capability.strip().casefold()


def record_refusal(
    *,
    reason: str,
    capability: str | None,
    state_dir: Path = DEFAULT_STATE_DIR,
    context: dict[str, Any] | None = None,
) -> Decision:
    """Record a forced refusal for a call this module could not evaluate through the ordinary
    `check()` path: a malformed payload, a missing capability name, or a failure to write the
    ordinary audit record. Always returns `allowed=False` — there is no code path through this
    function that permits a call. `reason` is a short machine-readable tag (for example
    `no-capability`, `malformed-payload`, `audit-write-failed`, `unexpected-error`) carried into
    the record's `reason` field. The write is best-effort: if `state_dir` cannot be written to
    either, this still returns the refusal `Decision` rather than raising, but the audit log ends
    up with nothing recorded for this call.
    """
    decision = Decision(
        capability=_normalize(capability) if capability else "(none)",
        allowed=False,
        reason=f"refused: {reason}",
        at=_now(),
        context=dict(context or {}),
    )
    _try_append_audit(state_dir, decision.to_dict())
    return decision


def read_audit_log(state_dir: Path) -> list[dict[str, Any]]:
    """Every record written to the audit log under `state_dir`, in the order they were written.
    Returns an empty list if no call has been recorded yet."""
    path = audit_log_path(state_dir)
    if not path.is_file():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def check(
    capability: str,
    *,
    denied: Iterable[str] = (),
    state_dir: Path = DEFAULT_STATE_DIR,
    context: dict[str, Any] | None = None,
) -> Decision:
    """Decide whether `capability` may proceed, and record the decision.

    Permissive default: `capability` is allowed unless it appears in `denied`. `denied` is
    supplied by the caller for this call; this function holds no state and no built-in policy
    between calls. `context` is arbitrary metadata about the call site (for example a tool name
    or tool input) carried into the audit record for traceability; it plays no part in the
    decision itself.

    `capability` and every entry of `denied` are normalised (`.strip().casefold()`) before
    comparison, and the normalised capability name is what the returned `Decision` and the audit
    record carry.

    Every call is recorded to the audit log under `state_dir`, allowed or denied. The record is
    written before this function returns, so a caller that crashes immediately after `check()`
    still leaves an audit trail of the decision it was given. If the write itself fails (for
    example `state_dir` is not writable), this raises `OSError` rather than returning a decision
    that was never actually logged — callers at a real tool boundary (see `__main__.py`'s `check`
    subcommand) must treat that as a refusal, not let the exception fail the call open.
    """
    normalized_capability = _normalize(capability)
    denied_set = {_normalize(name) for name in denied}
    allowed = normalized_capability not in denied_set
    decision = Decision(
        capability=normalized_capability,
        allowed=allowed,
        reason=(
            "denied by configured policy"
            if not allowed
            else "not in the configured denial set (permissive default)"
        ),
        at=_now(),
        context=dict(context or {}),
    )
    _append_audit(state_dir, decision.to_dict())
    return decision
