"""The three-field thin graph state, and re-derivation of a run's position by kind.

ADR-018's boundary rule, restated as code: graph state carries run identity and references
into durable records, never copies of their content. Three fields, nothing else -- no
attempt counters, no budget totals. Those live in the run ledger (`ledger.py`) and are read
by folding it, which is what makes the checkpoint store disposable: deleting
`data/orchestrator/checkpoints.sqlite` resets nothing, because nothing besides `run_id`,
`kind` and `refs` ever lived only in a checkpoint (REQ-022 R16).

LangGraph offers no API that moves a thread's cursor to an arbitrary stage -- `update_state`
forks history and cannot cross an `interrupt()`. So reconcile never edits a checkpointed
thread: when a checkpoint and the repository disagree, the thread is abandoned and a new
thread is opened whose id names the re-derived position (`thread_id`, below). This is
re-keying, not rewinding, and it is the only mechanism the whole design uses for both
recovering from a corrupted checkpoint (R16) and for a gate's `amend` verb
(PLAN-039.01 section 7).
"""

from __future__ import annotations

from typing import Literal, TypedDict

RunKind = Literal["intake", "batch", "unit", "realization"]

#: The kinds this phase's skeleton actually builds a graph for. `batch`, `unit` and
#: `realization` are later phases' deliverables (PLAN-039.01 section 12); state re-derivation
#: for them is not implemented here rather than implemented against records that do not
#: yet exist in a stable shape.
IMPLEMENTED_KINDS: frozenset[RunKind] = frozenset({"intake"})


class RunState(TypedDict):
    """LangGraph's State schema for every run kind. Exactly three fields, always."""

    run_id: str
    kind: RunKind
    refs: dict[str, str]


def natural_key(kind: RunKind, primary_ref: str) -> str:
    """The idempotency key reconcile starts runs under (PLAN-039.01 section 4)."""
    return f"{kind}:{primary_ref}"


def thread_id(run_id: str, position: str) -> str:
    """The LangGraph thread id for `run_id` at `position`.

    Encoding the position in the thread id is what makes re-keying idempotent: re-deriving
    the same run at the same position twice names the same thread on purpose, and two
    different positions never collide. Abandoning a thread means simply never addressing it
    again -- LangGraph needs no explicit close.
    """
    return f"{run_id}:{position}"


def derive_intake_position(idea_status: str) -> str:
    """Where an intake run belongs, from the idea's own folded status alone (REQ-022 R16).

    This function reads no checkpoint -- it is the repository-wins half of the re-derivation
    rule (PLAN-039.01 section 3's table). `open` is the only status with unfinished work:
    the run has not yet asked whether to dispatch a triage pass. Every other legal status
    means the idea already left `open` by some transition, so the run's work is done,
    whether or not that transition happened through this run at all.
    """
    if idea_status == "open":
        return "dispatch_gate"
    if idea_status in {"triaged", "reviewing", "promoted", "discarded"}:
        return "done"
    raise ValueError(f"unknown idea status {idea_status!r}")


def derive_position(kind: RunKind, refs: dict[str, str]) -> str:
    """Dispatch to the per-kind re-derivation rule (PLAN-039.01 section 3's table).

    Only `intake` is implemented. The other three kinds' authoritative records (the
    partition record, a phase's status and worktree/branch state, evidence annotations) are read by
    graphs this phase does not build; calling this for an unimplemented kind is a
    programming error in the caller, not a data condition, so it raises rather than
    guessing.
    """
    if kind == "intake":
        return derive_intake_position(refs["idea_status"])
    raise NotImplementedError(
        f"re-derivation for run kind {kind!r} is not built by phase-irs-04 -- "
        f"see PLAN-039.01 section 12 for which phase owns it"
    )
