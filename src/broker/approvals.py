"""Approval requests for actions the permissive-default enforcement point does not deny outright.

REQ-017 scope bullet 3 asks that anything sensitive route through an approval request carrying
scope, reason, expiry and an immutable decision record; scope bullet 4 asks for a surface to list
pending requests and record a decision against one. This module is that record and that surface's
backing logic (`__main__.py` exposes it as a CLI).

REQ-017 R04 — a full schema and policy for what counts as "sensitive" and how an approval taxonomy
is structured — is recorded open in ADR-022, the same as R02. This module does not attempt R04: it
does not define what should require approval, only what an approval record must contain once one
is requested. The four required fields (`scope`, `reason`, `expires_at`, `decision`) are validated
in code here rather than against a `schemas/` JSON Schema file, following the precedent
`src/governance/reservations.py` sets for a small, code-validated, append-only record that does
not warrant a schema of its own.

Storage is an append-only JSONL log, the same shape `src/governance/reservations.py` and the idea
event log (`src/db/ideas.py`) use: a request is one line, a decision is a second line for the same
id, and the current state of an approval is whichever record for its id was written last. Nothing
ever rewrites or deletes a line. That is what makes a decision immutable — there is no update
function, only `decide()`, which refuses to append a second decision for an id that already has
one.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import uuid
from pathlib import Path
from typing import Any, Literal

from src.broker.enforcement import DEFAULT_STATE_DIR

#: Filename for the append-only approval log inside a state directory.
APPROVAL_LOG_NAME = "approvals.jsonl"

Decision = Literal["approved", "denied"]


class ApprovalError(ValueError):
    """Raised for an invalid approval request or an invalid decision attempt (missing field,
    malformed expiry, a second decision on an already-decided approval, or a decision against an
    expired approval)."""


@dataclasses.dataclass(frozen=True)
class Approval:
    """One approval request, at whatever point in its life the caller is reading it.

    `decision` is `None` until `decide()` is called for this `id`, and is one of "approved" or
    "denied" afterward. `decided_at` and `decided_by` are `None` until then too.
    """

    id: str
    scope: str
    reason: str
    expires_at: str
    requested_at: str
    decision: Decision | None = None
    decided_at: str | None = None
    decided_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _now_iso() -> str:
    return _now().isoformat()


def _parse_expiry(expires_at: str) -> datetime.datetime:
    try:
        parsed = datetime.datetime.fromisoformat(expires_at)
    except (TypeError, ValueError) as exc:
        raise ApprovalError(f"expires_at must be an ISO 8601 timestamp: {expires_at!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.UTC)
    return parsed


def is_expired(approval: Approval, *, at: datetime.datetime | None = None) -> bool:
    """Whether `approval` has passed its expiry as of `at` (default: now)."""
    moment = at or _now()
    return _parse_expiry(approval.expires_at) <= moment


def _validate_new_fields(scope: str, reason: str, expires_at: str) -> None:
    if not isinstance(scope, str) or not scope.strip():
        raise ApprovalError("scope is required and must be a non-empty string")
    if not isinstance(reason, str) or not reason.strip():
        raise ApprovalError("reason is required and must be a non-empty string")
    _parse_expiry(expires_at)  # raises ApprovalError if malformed


def _log_path(state_dir: Path) -> Path:
    return state_dir / APPROVAL_LOG_NAME


def _append(state_dir: Path, approval: Approval) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    with _log_path(state_dir).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(approval.to_dict(), sort_keys=True) + "\n")


def _fold(state_dir: Path) -> dict[str, Approval]:
    """The current state of every approval under `state_dir`: the last record written for each
    id. A request line establishes an id; a decision line for the same id supersedes it. Never
    reads or trusts anything but the log itself."""
    path = _log_path(state_dir)
    if not path.is_file():
        return {}
    latest: dict[str, Approval] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        latest[record["id"]] = Approval(**record)
    return latest


def request(
    scope: str,
    reason: str,
    expires_at: str,
    *,
    state_dir: Path = DEFAULT_STATE_DIR,
) -> Approval:
    """Record a new approval request. Raises `ApprovalError` if any of `scope`, `reason` or
    `expires_at` is missing or malformed."""
    _validate_new_fields(scope, reason, expires_at)
    approval = Approval(
        id=str(uuid.uuid4()),
        scope=scope,
        reason=reason,
        expires_at=expires_at,
        requested_at=_now_iso(),
    )
    _append(state_dir, approval)
    return approval


def pending(state_dir: Path = DEFAULT_STATE_DIR) -> list[Approval]:
    """Every approval with no decision recorded yet and not expired, oldest request first. An
    expired, undecided approval is not pending — it is not honoured regardless of the decision
    someone might still try to record against it."""
    all_approvals = sorted(_fold(state_dir).values(), key=lambda a: a.requested_at)
    return [a for a in all_approvals if a.decision is None and not is_expired(a)]


def get(approval_id: str, *, state_dir: Path = DEFAULT_STATE_DIR) -> Approval:
    """The current state of one approval by id. Raises `ApprovalError` if no request with that id
    exists."""
    found = _fold(state_dir).get(approval_id)
    if found is None:
        raise ApprovalError(f"no approval request with id {approval_id!r}")
    return found


def decide(
    approval_id: str,
    decision: Decision,
    *,
    decided_by: str,
    state_dir: Path = DEFAULT_STATE_DIR,
) -> Approval:
    """Record `decision` ("approved" or "denied") against the approval named by `approval_id`.

    Raises `ApprovalError` if: no such approval exists, the approval already has a decision (a
    decision is never edited — this is what makes the record immutable), the approval has
    expired (an expired approval is not honoured, so it cannot be decided at all, not even to
    deny it), or `decision` is not one of the two allowed values.
    """
    if decision not in ("approved", "denied"):
        raise ApprovalError(f"decision must be 'approved' or 'denied', got {decision!r}")
    existing = get(approval_id, state_dir=state_dir)
    if existing.decision is not None:
        raise ApprovalError(
            f"approval {approval_id!r} already has a recorded decision "
            f"({existing.decision!r}); decisions are immutable"
        )
    if is_expired(existing):
        raise ApprovalError(f"approval {approval_id!r} has expired; it cannot be honoured")
    updated = dataclasses.replace(
        existing,
        decision=decision,
        decided_at=_now_iso(),
        decided_by=decided_by,
    )
    _append(state_dir, updated)
    return updated
