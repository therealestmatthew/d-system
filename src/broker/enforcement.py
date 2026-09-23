"""Tool-boundary capability enforcement, with a permissive default.

`check()` is the one function a tool boundary calls. It takes the name of a capability an agent
is about to exercise, decides whether it may proceed, and records the decision to an audit log
before returning. The permissive default: a capability not named in the caller's `denied` set is
allowed. ADR-022 ships this shape deliberately — the repository has no precedent for a
general-purpose capability taxonomy, so this module owns no built-in list of capabilities,
roles or denials. Every denial is supplied explicitly by the caller, per call.

This satisfies REQ-017 R01 (the broker exists and can refuse before any unattended work starts)
and R03 (a denied capability is stopped at the boundary, not trusted to a prompt). It does not
satisfy R02 (a run's capability set names specific actions, not a role) — that requires a real
capability taxonomy, which does not exist yet and is recorded open in ADR-022.

The mechanism is meant to sit at a real tool boundary: a caller that intercepts a tool call
before it runs, extracts a capability name from it, and calls `check()` (directly, or through
this package's CLI in `__main__.py`) before letting the call proceed. Nothing in this repository
does that yet — see the package docstring in `src/broker/__init__.py` for what the wiring would
be and why it is out of this phase's scope.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
from pathlib import Path
from typing import Any, Iterable

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
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def audit_log_path(state_dir: Path) -> Path:
    """Where the audit log lives under a given state directory."""
    return state_dir / AUDIT_LOG_NAME


def _append_audit(state_dir: Path, record: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    with audit_log_path(state_dir).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


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

    Every call is recorded to the audit log under `state_dir`, allowed or denied. The record is
    written before this function returns, so a caller that crashes immediately after `check()`
    still leaves an audit trail of the decision it was given.
    """
    denied_set = set(denied)
    allowed = capability not in denied_set
    decision = Decision(
        capability=capability,
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
