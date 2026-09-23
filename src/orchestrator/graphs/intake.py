"""The `intake` graph -- stage 2, one run per idea (PLAN-039.01 section 1).

Three nodes and one gate:

    assemble -> dispatch_gate -(approve)-> triage -> done
                             \\-(reject/anything else)-> done

`assemble` computes nothing from a checkpoint -- it only stamps `refs["gate"]` so the gate
node has a name to surface. `dispatch_gate` is `gates.gate_node` unchanged: it contains only
its `interrupt()`, asking whether to dispatch a triage pass for this idea (the attended-only
rule, PLAN-039.01 section 2 and REQ-017 R01 -- nothing here dispatches without an owner
decision reaching this gate). `triage` calls the supplied `Dispatcher`; a rejected or
otherwise-decided gate skips straight to `done` without ever calling it. `done` is the
run's terminal node regardless of path.

The run itself is not terminal at `done` in every sense a checkpoint tracks -- `tick.py`
derives the run's true end (the idea leaving `open`) from the idea's own folded status
(`state.derive_intake_position`), not from this graph reaching `done`. A run whose gate
is still interrupted, and whose idea has meanwhile left `open` some other way (a human
triaged it directly), never resumes this graph at all: `tick.py` records it terminal by
re-deriving the position, matching the re-keying rule (ADR-018, `state.py`).
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from src.orchestrator import gates
from src.orchestrator.dispatch import Dispatcher, DispatchResult, unimplemented_dispatcher
from src.orchestrator.state import RunState

#: Placeholder per-dispatch ceiling. The role-contract-defined cap (phase-irs-03,
#: PLAN-039.01 section 8) is not this phase's scope; this constant exists so the skeleton's
#: one dispatch call has *some* budget_cap to record, not a real policy.
DEFAULT_BUDGET_CAP = 50_000

GATE_NAME = "dispatch-authorization"


def _assemble(state: RunState) -> dict[str, Any]:
    return {"refs": {**state["refs"], "gate": GATE_NAME}}


def _route_after_gate(state: RunState) -> str:
    decision = state["refs"].get("last_decision") or {}
    return "triage" if decision.get("decision") == "approve" else "done"


def _make_triage(dispatcher: Dispatcher):
    def triage(state: RunState) -> dict[str, Any]:
        result: DispatchResult = dispatcher(
            run_id=state["run_id"],
            role="idea-triage",
            refs=state["refs"],
            budget_cap=DEFAULT_BUDGET_CAP,
        )
        return {
            "refs": {
                **state["refs"],
                "triage_outcome": result.outcome,
                "triage_input_tokens": str(result.input_tokens),
                "triage_output_tokens": str(result.output_tokens),
            }
        }

    return triage


def _done(state: RunState) -> dict[str, Any]:
    return {"refs": {**state["refs"], "position": "done"}}


def build_graph(checkpointer: Any, dispatcher: Dispatcher = unimplemented_dispatcher):
    """Compile the intake graph against `checkpointer`, calling `dispatcher` on approval."""
    graph = StateGraph(RunState)
    graph.add_node("assemble", _assemble)
    graph.add_node("dispatch_gate", gates.gate_node)
    graph.add_node("triage", _make_triage(dispatcher))
    graph.add_node("done", _done)

    graph.add_edge(START, "assemble")
    graph.add_edge("assemble", "dispatch_gate")
    graph.add_conditional_edges(
        "dispatch_gate", _route_after_gate, {"triage": "triage", "done": "done"}
    )
    graph.add_edge("triage", "done")
    graph.add_edge("done", END)

    return graph.compile(checkpointer=checkpointer)
