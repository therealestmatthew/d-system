"""Gate nodes, and turning a recorded decision into a graph resume.

A gate node contains only its `interrupt()` call and nothing else (PLAN-039.01 section 7).
LangGraph replays the containing node from its start on resume, so every other thing a gate
needs -- assembling the decision-ready payload, any dispatch, the ledger entry -- happens in
the node before it, checkpointed before the gate node begins. A bare `interrupt()` costs
nothing on resume and duplicates no work. This rule is enforced by convention and review
here, not by a runtime check: `gate_node` below is the only node body this package builds
that calls `interrupt()`, and every graph in `graphs/` is expected to route its gates
through it rather than interrupting inline.
"""

from __future__ import annotations

from typing import Any

from langgraph.types import Command, interrupt


def gate_node(state: dict[str, Any]) -> dict[str, Any]:
    """The entire body of a gate node.

    `state["refs"]` is surfaced as the interrupt's payload alongside the gate's name, so
    `status`/`gate` rendering (outside this phase's scope) has enough to show the owner what
    is waiting. The decision that resumes the interrupt is folded into `refs` under
    `last_decision`, becoming part of the state the next node sees -- never persisted
    anywhere else, per the thin-state rule; the ledger entry recording the decision is a
    separate write (`tools/append_decision.py`, `ledger.py`), not this function's job.
    """
    payload = {"gate": state["refs"].get("gate"), "refs": state["refs"]}
    decision = interrupt(payload)
    return {"refs": {**state["refs"], "last_decision": decision}}


def resume_command(decision: dict[str, Any]) -> Command:
    """Build the `Command` that resumes a thread interrupted at a gate with `decision`.

    `decision` is a gate-decision event's own shape (`schemas/gate-decision.schema.json`)
    minus its ledger bookkeeping fields -- at minimum `{"decision": "approve"|"reject"|
    "amend"}`. `tick.py`'s `advance()` is the only caller in this package; nothing else
    constructs a resume directly.
    """
    return Command(resume=decision)
