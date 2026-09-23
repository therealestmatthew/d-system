"""The tick scheduler: reconcile, start and advance -- the whole scheduler as one callable.

`tick()` is PLAN-039.01 section 2's whole description of the scheduler: reconcile against
the records, start runs whose start condition holds, advance every non-interrupted run, and
write ledger entries. It takes no lock itself -- the daemon that eventually wraps this in
`flock` is `phase-irs-16`'s deliverable, not this phase's; a caller running `tick()` twice
concurrently against the same files is racing the ledger's own file writes, which is exactly
why the daemon owns the lock and this module does not pretend to.

**Attended-only, conservatively.** `dispatch=False` (the default) still reconciles and
starts new runs -- reaching a gate's `interrupt()` dispatches nothing, so that always
happens. But *no* gate is resumed unless `dispatch=True`, even for a `reject` decision that
would itself call no dispatcher. This is more conservative than REQ-017 R01 strictly
requires (only an `approve` resume can reach `triage`'s dispatch call), chosen because it
makes the guarantee trivial to state and to verify: no call into `graphs/intake.py`'s
`triage` node happens on any tick where `dispatch` is not `True`, full stop.

**Re-keying, read as "recreate what the records prove, never rewind."** `state.py`'s
`derive_intake_position` is the single source of truth for where a run belongs; this module
never trusts a checkpoint's own idea of where it is. Two situations follow that rule:

- The idea already left `open` by some means (a human triaged it directly, without this run
  ever reaching a decision) -- the run is terminal regardless of what its thread was doing,
  recorded as `abandoned` then `terminal`.
- The idea is still `open` but the thread has no pending interrupt to resume -- either it was
  never advanced this process, or its checkpoint store was deleted or corrupted (REQ-022
  R16). Either way, `_advance_to_gate` is called again: LangGraph opens a fresh checkpoint at
  the same thread id (`state.thread_id` is a pure function of `run_id` and the re-derived
  position, never of checkpoint content), replays `assemble` and hits `interrupt()` again.
  Nothing is lost, because nothing besides `run_id`/`kind`/`refs` and the ledger's own
  entries was ever the source of truth.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver

from src.db.ideas import fold as fold_ideas
from src.db.ideas import load_events as load_idea_events
from src.orchestrator import decisions as decisions_mod
from src.orchestrator import gates, ledger
from src.orchestrator import state as state_mod
from src.orchestrator.dispatch import Dispatcher, unimplemented_dispatcher
from src.orchestrator.graphs.intake import DEFAULT_BUDGET_CAP, GATE_NAME
from src.orchestrator.graphs.intake import build_graph as build_intake_graph

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IDEA_LOG = ROOT / "_data" / "ideas.jsonl"
DEFAULT_RUN_LOG = ledger.LOG
DEFAULT_DECISION_LOG = decisions_mod.LOG
DEFAULT_WATERMARK = ROOT / "data" / "orchestrator" / "watermark"


def open_checkpoint_store(path: Path) -> SqliteSaver:
    """Open the SQLite checkpoint store at `path`, recreating it if missing or corrupt.

    REQ-022 R16's "the checkpoint store is deleted or corrupted" is handled here, at the
    point a checkpointer is opened, rather than inside `tick()`'s per-run loop -- matching
    PLAN-039.01 section 11's failure-path table, which treats a corrupt checkpointer as a
    precondition `tick()` re-derives against, not a condition `tick()` detects mid-run.
    A missing file is simply created (`sqlite3.connect` does this for free). A corrupt one
    is moved aside with a timestamped suffix rather than deleted outright, so the evidence
    survives for anyone who wants to look at it later, and a fresh store is opened in its
    place. Nothing under `data/orchestrator/` is load-bearing (PLAN-039.01 section 5) --
    every thread this loses is re-created by the next tick's reconcile pass, at whatever
    position the repository's own records prove.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    try:
        saver = SqliteSaver(conn)
        saver.setup()  # forces the table-creation script now, not lazily on first real use
        return saver
    except sqlite3.DatabaseError:
        conn.close()
        stamp = ledger.now().replace(":", "")
        side_files = (path.name + "-wal", path.name + "-shm")
        for candidate in (path, *(path.with_name(name) for name in side_files)):
            if candidate.exists():
                candidate.rename(candidate.with_name(f"{candidate.name}.corrupt-{stamp}"))
        conn = sqlite3.connect(str(path), check_same_thread=False)
        return SqliteSaver(conn)


def load_watermark(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def write_watermark(path: Path, at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(at, encoding="utf-8")


def _created_at(idea_events: list[dict[str, Any]], idea_id: str) -> str:
    for event in idea_events:
        if event["idea"] == idea_id and event["event"] == "created":
            return str(event["at"])
    raise KeyError(f"no created event for idea {idea_id!r}")


def _has_pending_interrupt(graph: Any, run_id: str, position: str) -> bool:
    """Whether the checkpoint store still shows this thread interrupted.

    A checkpoint store deleted, corrupted or otherwise unreadable (REQ-022 R16) is not
    distinguished from "no checkpoint yet" here: either way, the caller's answer is the
    same -- re-derive from the records and recreate the interrupt (`_advance_to_gate`)
    rather than trust a checkpoint this function could not even read.
    """
    cfg = {"configurable": {"thread_id": state_mod.thread_id(run_id, position)}}
    try:
        snapshot = graph.get_state(cfg)
    except Exception:
        return False
    return bool(snapshot.interrupts)


def _advance_to_gate(
    graph: Any, run_id: str, refs: dict[str, str], run_log: Path
) -> None:
    """Invoke the graph from its start; it runs `assemble` and interrupts at the gate.

    Idempotent to call more than once for the same run: replaying `assemble` touches only
    in-memory graph state, never the repository, so re-deriving here (a checkpoint that was
    lost or never written this process) never double-writes anything durable.
    """
    cfg = {"configurable": {"thread_id": state_mod.thread_id(run_id, "dispatch_gate")}}
    graph.invoke({"run_id": run_id, "kind": "intake", "refs": refs}, config=cfg)
    ledger.record(run_id, "gate_reached", run_log, gate=GATE_NAME, position="dispatch_gate")


def _resume_gate(
    graph: Any, run_id: str, decision: dict[str, Any], run_log: Path
) -> None:
    """Resume the interrupted gate with `decision`, then record what happened.

    Only `approve` ends the run: it dispatches the triage pass and the run's part in this
    idea's story is over. `reject` (and `amend`, treated the same here -- intake has no G3
    artifact to re-key against) leaves the run active and parked rather than terminal: the
    underlying LangGraph thread has reached its own `done` node and is no longer
    interrupted, but the *run* is not done, so the next tick's `_advance_to_gate` re-invokes
    the same thread fresh, which LangGraph starts over from `assemble` and interrupts again
    -- the owner is asked again rather than the natural key being freed for a duplicate run.
    """
    cfg = {"configurable": {"thread_id": state_mod.thread_id(run_id, "dispatch_gate")}}
    ledger.record(run_id, "gate_decided", run_log, gate=GATE_NAME, decision=decision["decision"])
    output = graph.invoke(gates.resume_command(decision), config=cfg)
    if decision["decision"] != "approve":
        ledger.record(
            run_id, "parked", run_log,
            reason=f"gate {GATE_NAME!r} decided {decision['decision']!r} -- asked again next tick",
        )
        return
    ledger.record(
        run_id, "dispatched", run_log, role="idea-triage", budget_cap=DEFAULT_BUDGET_CAP
    )
    ledger.record(
        run_id,
        "dispatch_result",
        run_log,
        outcome=output["refs"].get("triage_outcome", "unknown"),
        usage={
            "input_tokens": int(output["refs"].get("triage_input_tokens", 0)),
            "output_tokens": int(output["refs"].get("triage_output_tokens", 0)),
        },
    )
    ledger.record(run_id, "terminal", run_log, outcome="complete", position="done")


def tick(
    *,
    idea_log: Path = DEFAULT_IDEA_LOG,
    run_log: Path = DEFAULT_RUN_LOG,
    decision_log: Path = DEFAULT_DECISION_LOG,
    watermark_path: Path = DEFAULT_WATERMARK,
    checkpointer: Any,
    dispatcher: Dispatcher = unimplemented_dispatcher,
    dispatch: bool = False,
) -> dict[str, list[str]]:
    """Run one tick: reconcile, start, advance. Returns what it did, by run id.

    `checkpointer` is required and never defaulted -- a tick with no checkpointer is a
    caller error, not something this function should paper over with an in-memory one that
    silently discards state between calls.
    """
    result: dict[str, list[str]] = {
        "started": [], "rekeyed": [], "resumed": [], "closed": [], "deferred": [],
    }

    watermark = load_watermark(watermark_path)
    if watermark is None:
        # PLAN-039.01 section 4: the watermark initializes to *now* on first start. Ideas
        # already open are deliberately not swept into dispatch by this bootstrap tick.
        write_watermark(watermark_path, ledger.now())
        return result

    idea_events = load_idea_events(idea_log)
    idea_state = fold_ideas(idea_events)
    graph = build_intake_graph(checkpointer, dispatcher)

    # 1. Start runs for ideas that should have one and do not yet.
    active_keys = ledger.active_natural_keys(ledger.load_events(run_log))
    for idea_id, idea in idea_state.items():
        if idea["status"] != "open":
            continue
        if _created_at(idea_events, idea_id) <= watermark:
            continue
        natural_key = state_mod.natural_key("intake", idea_id)
        if natural_key in active_keys:
            continue
        refs = {"idea_id": idea_id, "idea_status": "open"}
        started = ledger.start("intake", natural_key, refs, log=run_log)
        _advance_to_gate(graph, started["run_id"], refs, run_log)
        result["started"].append(started["run_id"])

    # 2. Reconcile and advance every active intake run.
    run_summaries = ledger.fold(ledger.load_events(run_log))
    pending_decisions = decisions_mod.load_decisions(decision_log)
    for run_id, summary in run_summaries.items():
        if summary["kind"] != "intake" or summary["status"] in ("terminal", "abandoned"):
            continue
        idea_id = summary["refs"]["idea_id"]
        current_status = idea_state[idea_id]["status"] if idea_id in idea_state else "discarded"
        desired_position = state_mod.derive_intake_position(current_status)

        if desired_position == "done":
            # The idea left 'open' by some means this run never decided -- re-key to done.
            ledger.record(
                run_id, "abandoned", run_log,
                reason="idea left open outside this run's own resume path",
            )
            ledger.record(
                run_id, "terminal", run_log,
                outcome="idea-left-open-externally", position="done",
            )
            result["rekeyed"].append(run_id)
            continue

        if not _has_pending_interrupt(graph, run_id, "dispatch_gate"):
            # Checkpoint lost, corrupted, or never written this process (REQ-022 R16):
            # re-derive from the records and recreate the interrupt at the same position.
            _advance_to_gate(graph, run_id, summary["refs"], run_log)
            result["rekeyed"].append(run_id)

        applied = len([d for d in summary["decisions"] if d["gate"] == GATE_NAME])
        inbox = decisions_mod.for_gate(run_id, GATE_NAME, pending_decisions)
        if len(inbox) <= applied:
            continue  # still waiting on an owner decision
        next_decision = inbox[applied]

        if not dispatch:
            result["deferred"].append(run_id)
            continue

        _resume_gate(graph, run_id, next_decision, run_log)
        result["closed"].append(run_id)

    return result
