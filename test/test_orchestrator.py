"""Tests for the LangGraph orchestrator skeleton (`phase-irs-04`, ADR-018, PLAN-039.01).

Every test uses `tmp_path` for the idea log, run ledger, decision inbox, watermark and
checkpoint store; nothing here touches a real repository path. `_checkpointer_factory`
returns a new `SqliteSaver` connected to a *file* under `tmp_path` rather than `:memory:`
specifically so a test can simulate reconnecting from a fresh process (REQ-022 R17) or
losing the file entirely (REQ-022 R16) -- an in-memory database cannot model either.

Acceptance-row map, named directly rather than left to the reader to infer:

- REQ-022 R16 -- `test_r16_checkpoint_deletion_rekeys_thread_at_rederived_position`,
  `test_r16_checkpoint_corruption_rekeys_thread_at_rederived_position`
- REQ-022 R17 -- `test_r17_killed_run_resumes_at_its_gate`
- REQ-022 R18 -- `test_r18_run_reconstructible_from_ledger_alone`
- REQ-022 R19 -- `test_r19_orchestrator_package_defines_no_claim_recovery_logic`
- "No agent dispatch occurs without the owner-initiated dispatch flag" --
  `test_no_dispatch_without_the_owner_flag`, `test_dispatch_flag_permits_resuming_into_dispatch`
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

import pytest

from src.orchestrator import decisions as decisions_mod
from src.orchestrator import dispatch as dispatch_mod
from src.orchestrator import gates, ledger
from src.orchestrator import state as state_mod
from src.orchestrator import tick as tick_mod
from src.orchestrator.dispatch import DispatchResult
from src.orchestrator.graphs import intake as intake_mod

ROOT = Path(__file__).resolve().parents[1]


# --- fixtures and small helpers ---------------------------------------------------------------


def _now(offset_minutes: int = 0) -> str:
    return (
        (dt.datetime.now().astimezone() + dt.timedelta(minutes=offset_minutes))
        .replace(microsecond=0)
        .isoformat()
    )


def _write_idea(idea_log: Path, idea_id: str, at: str) -> None:
    event = {
        "idea": idea_id, "event": "created", "at": at, "eid": f"e-{idea_id}",
        "title": f"idea {idea_id}", "body": "body",
    }
    with idea_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def _checkpointer_factory(tmp_path: Path):
    """Returns `(db_path, make)`. `make()` is `tick.open_checkpoint_store`, the same safe-open
    path `__main__.py` uses -- so the R16 tests exercise real recovery, not a raw connection."""
    db = tmp_path / "checkpoints.sqlite"
    return db, lambda: tick_mod.open_checkpoint_store(db)


def _env(tmp_path: Path) -> dict[str, Path]:
    return {
        "idea_log": tmp_path / "ideas.jsonl",
        "run_log": tmp_path / "runs.jsonl",
        "decision_log": tmp_path / "gate-decisions.jsonl",
        "watermark_path": tmp_path / "watermark",
    }


def _bootstrap_and_backdate_watermark(env: dict[str, Path], checkpointer: Any) -> None:
    """First tick only sets the watermark; back-date it so later ticks see new ideas."""
    tick_mod.tick(**env, checkpointer=checkpointer)
    env["watermark_path"].write_text(_now(offset_minutes=-5), encoding="utf-8")


def _stub_dispatcher(outcome: str = "ok", input_tokens: int = 10, output_tokens: int = 5):
    calls: list[dict[str, Any]] = []

    def dispatcher(*, run_id: str, role: str, refs: dict[str, str], budget_cap: int):
        calls.append(
            {"run_id": run_id, "role": role, "refs": dict(refs), "budget_cap": budget_cap}
        )
        return DispatchResult(
            outcome=outcome, input_tokens=input_tokens, output_tokens=output_tokens
        )

    dispatcher.calls = calls  # type: ignore[attr-defined]
    return dispatcher


# --- state.py: thin state and per-kind re-derivation --------------------------------------------


def test_derive_intake_position_open_means_dispatch_gate() -> None:
    assert state_mod.derive_intake_position("open") == "dispatch_gate"


@pytest.mark.parametrize("status", ["triaged", "reviewing", "promoted", "discarded"])
def test_derive_intake_position_every_other_legal_status_means_done(status: str) -> None:
    assert state_mod.derive_intake_position(status) == "done"


def test_derive_intake_position_rejects_an_unknown_status() -> None:
    with pytest.raises(ValueError):
        state_mod.derive_intake_position("not-a-real-status")


def test_derive_position_dispatches_only_to_implemented_kinds() -> None:
    assert state_mod.derive_position("intake", {"idea_status": "open"}) == "dispatch_gate"
    for kind in ("batch", "unit", "realization"):
        with pytest.raises(NotImplementedError):
            state_mod.derive_position(kind, {})  # type: ignore[arg-type]


def test_thread_id_is_a_pure_function_of_run_id_and_position() -> None:
    assert state_mod.thread_id("run-1", "dispatch_gate") == state_mod.thread_id(
        "run-1", "dispatch_gate"
    )
    assert state_mod.thread_id("run-1", "dispatch_gate") != state_mod.thread_id("run-1", "done")


def test_run_state_carries_exactly_three_fields() -> None:
    assert set(state_mod.RunState.__annotations__) == {"run_id", "kind", "refs"}


# --- ledger.py: append-only writer, natural-key idempotency, reconstruction --------------------


def test_ledger_start_refuses_a_second_non_terminal_run_under_the_same_natural_key(
    tmp_path: Path,
) -> None:
    log = tmp_path / "runs.jsonl"
    ledger.start("intake", "intake:000001", {"idea_id": "000001"}, log=log)
    with pytest.raises(ledger.LedgerError):
        ledger.start("intake", "intake:000001", {"idea_id": "000001"}, log=log)


def test_ledger_start_permits_a_new_run_once_the_prior_one_is_terminal(tmp_path: Path) -> None:
    log = tmp_path / "runs.jsonl"
    first = ledger.start("intake", "intake:000001", {"idea_id": "000001"}, log=log)
    ledger.record(first["run_id"], "terminal", log, outcome="complete", position="done")
    second = ledger.start("intake", "intake:000001", {"idea_id": "000001"}, log=log)
    assert second["run_id"] != first["run_id"]


def test_ledger_reconstruct_requires_the_first_event_to_be_started() -> None:
    with pytest.raises(ledger.LedgerError):
        ledger.reconstruct([{"run_id": "r", "kind": "intake", "event": "position", "at": "x"}])


def test_ledger_append_refuses_an_event_that_fails_the_schema(tmp_path: Path) -> None:
    log = tmp_path / "runs.jsonl"
    with pytest.raises(ledger.LedgerError):
        ledger.append({"run_id": "r", "kind": "intake", "event": "started", "at": "x"}, log=log)
    assert not log.exists() or log.read_text() == ""


# --- decisions.py: dedup key ---------------------------------------------------------------------


def test_decide_computes_decision_seq_automatically(tmp_path: Path) -> None:
    log = tmp_path / "gate-decisions.jsonl"
    first = decisions_mod.decide("run-1", "G", "approve", "repository-owner", log=log)
    assert first["decision_seq"] == 1
    second = decisions_mod.decide("run-1", "G", "reject", "repository-owner", log=log)
    assert second["decision_seq"] == 2


def test_decide_refuses_a_stale_explicit_decision_seq(tmp_path: Path) -> None:
    log = tmp_path / "gate-decisions.jsonl"
    decisions_mod.decide("run-1", "G", "approve", "repository-owner", log=log)
    with pytest.raises(decisions_mod.DecisionError):
        decisions_mod.decide(
            "run-1", "G", "approve", "repository-owner", decision_seq=1, log=log
        )


def test_latest_for_gate_returns_none_when_no_decision_exists(tmp_path: Path) -> None:
    log = tmp_path / "gate-decisions.jsonl"
    assert decisions_mod.latest_for_gate("run-1", "G", decisions_mod.load_decisions(log)) is None


# --- gates.py: bare interrupt, resume command -----------------------------------------------------


def test_gate_node_surfaces_refs_and_folds_the_decision_back_in() -> None:
    """Exercised indirectly through the intake graph elsewhere; this checks the shape alone."""
    assert gates.resume_command({"decision": "approve"}).resume == {"decision": "approve"}


# --- dispatch.py: the kill switch's flag file, the unimplemented default -------------------------


def test_unimplemented_dispatcher_refuses_rather_than_guessing() -> None:
    with pytest.raises(NotImplementedError):
        dispatch_mod.unimplemented_dispatcher(run_id="r", role="x", refs={}, budget_cap=1)


def test_halt_and_resume_dispatch_toggle_the_flag_file(tmp_path: Path) -> None:
    flag = tmp_path / "orchestrator-halt"
    assert dispatch_mod.is_halted(flag) is False
    dispatch_mod.halt(flag)
    assert dispatch_mod.is_halted(flag) is True
    dispatch_mod.resume_dispatch(flag)
    assert dispatch_mod.is_halted(flag) is False


# --- tick.py: reconcile, start, the watermark -----------------------------------------------------


def test_first_tick_only_bootstraps_the_watermark(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _write_idea(env["idea_log"], "000001", _now())
    _, make = _checkpointer_factory(tmp_path)

    result = tick_mod.tick(**env, checkpointer=make())

    assert result == {"started": [], "rekeyed": [], "resumed": [], "closed": [], "deferred": []}
    assert env["watermark_path"].exists()


def test_ideas_created_before_the_watermark_are_never_started(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    # Backdate the watermark, then write an idea *before* it.
    env["watermark_path"].write_text(_now(), encoding="utf-8")
    _write_idea(env["idea_log"], "000001", _now(offset_minutes=-10))

    result = tick_mod.tick(**env, checkpointer=make())

    assert result["started"] == []


def test_a_new_open_idea_starts_a_run_and_reaches_its_gate(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())

    result = tick_mod.tick(**env, checkpointer=make())

    assert len(result["started"]) == 1
    events = ledger.load_events(env["run_log"])
    assert [e["event"] for e in events] == ["started", "gate_reached"]
    assert events[0]["natural_key"] == "intake:000001"


def test_reconcile_does_not_double_start_an_already_active_run(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())

    tick_mod.tick(**env, checkpointer=make())
    result = tick_mod.tick(**env, checkpointer=make())

    assert result["started"] == []
    # started + gate_reached, still just one run
    assert len(ledger.load_events(env["run_log"])) == 2


# --- the owner-initiated dispatch flag -----------------------------------------------------


def test_no_dispatch_without_the_owner_flag(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]
    decisions_mod.decide(
        run_id, intake_mod.GATE_NAME, "approve", "repository-owner", log=env["decision_log"]
    )
    dispatcher = _stub_dispatcher()

    result = tick_mod.tick(**env, checkpointer=make(), dispatcher=dispatcher, dispatch=False)

    assert dispatcher.calls == []  # type: ignore[attr-defined]
    assert result["deferred"] == [run_id]
    assert result["closed"] == []
    summary = ledger.fold(ledger.load_events(env["run_log"]))[run_id]
    assert summary["status"] == "active"


def test_dispatch_flag_permits_resuming_into_dispatch(tmp_path: Path) -> None:
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]
    decisions_mod.decide(
        run_id, intake_mod.GATE_NAME, "approve", "repository-owner", log=env["decision_log"]
    )
    dispatcher = _stub_dispatcher()

    result = tick_mod.tick(**env, checkpointer=make(), dispatcher=dispatcher, dispatch=True)

    assert len(dispatcher.calls) == 1  # type: ignore[attr-defined]
    assert dispatcher.calls[0]["run_id"] == run_id  # type: ignore[attr-defined]
    assert result["closed"] == [run_id]
    summary = ledger.fold(ledger.load_events(env["run_log"]))[run_id]
    assert summary["status"] == "terminal" and summary["outcome"] == "complete"


def test_a_rejected_gate_parks_rather_than_terminating_and_is_asked_again(tmp_path: Path) -> None:
    """A reject does not free the natural key -- the same run is re-asked, never duplicated."""
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]
    decisions_mod.decide(
        run_id, intake_mod.GATE_NAME, "reject", "repository-owner", log=env["decision_log"]
    )
    tick_mod.tick(**env, checkpointer=make(), dispatch=True)

    result = tick_mod.tick(**env, checkpointer=make())

    assert result["started"] == []
    assert run_id in result["rekeyed"]
    summary = ledger.fold(ledger.load_events(env["run_log"]))[run_id]
    assert summary["status"] == "parked"


def test_an_idea_that_leaves_open_outside_the_run_is_rekeyed_to_done(tmp_path: Path) -> None:
    from tools.append_idea import append as append_idea_event
    from tools.append_idea import build_status

    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]

    # A human triaged the idea directly, outside this run's own decision path.
    append_idea_event(
        build_status("000001", "open", "triaged", _now(), "e-status"), log=env["idea_log"]
    )

    result = tick_mod.tick(**env, checkpointer=make())

    assert run_id in result["rekeyed"]
    summary = ledger.fold(ledger.load_events(env["run_log"]))[run_id]
    assert summary["status"] == "terminal"
    assert summary["outcome"] == "idea-left-open-externally"


# --- REQ-022 R16: checkpoint loss re-derives and re-keys ------------------------------------------


def test_r16_checkpoint_deletion_rekeys_thread_at_rederived_position(tmp_path: Path) -> None:
    env = _env(tmp_path)
    db, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]

    db.unlink()  # the checkpoint store is gone

    result = tick_mod.tick(**env, checkpointer=make())

    assert run_id in result["rekeyed"]
    # The re-keyed thread reached the same, re-derived position: still interrupted at the gate.
    graph = intake_mod.build_graph(make())
    cfg = {"configurable": {"thread_id": state_mod.thread_id(run_id, "dispatch_gate")}}
    assert bool(graph.get_state(cfg).interrupts) is True
    # No duplicate run was started for the same natural key.
    started_events = [e for e in ledger.load_events(env["run_log"]) if e["event"] == "started"]
    assert len(started_events) == 1


def test_r16_checkpoint_corruption_rekeys_thread_at_rederived_position(tmp_path: Path) -> None:
    env = _env(tmp_path)
    db, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]

    # Corrupt the main file and its WAL/shared-memory side files -- SQLite in WAL mode (the
    # checkpointer's default) can otherwise silently recover the pre-corruption state from an
    # untouched -wal file, defeating the point of this test.
    for path in (db, db.with_name(db.name + "-wal"), db.with_name(db.name + "-shm")):
        if path.exists():
            path.write_bytes(b"this is not a sqlite database file")

    result = tick_mod.tick(**env, checkpointer=make())

    assert run_id in result["rekeyed"]
    started_events = [e for e in ledger.load_events(env["run_log"]) if e["event"] == "started"]
    assert len(started_events) == 1


# --- REQ-022 R17: a killed run resumes at its gate -----------------------------------------


def test_r17_killed_run_resumes_at_its_gate(tmp_path: Path) -> None:
    """Kill == discard the in-process checkpointer object; the file on disk survives."""
    env = _env(tmp_path)
    _, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]
    # "Kill" the process: nothing keeps the first checkpointer object alive past this point.

    decisions_mod.decide(
        run_id, intake_mod.GATE_NAME, "approve", "repository-owner", log=env["decision_log"]
    )
    dispatcher = _stub_dispatcher()
    # A fresh connection to the same file stands in for the daemon's next process.
    result = tick_mod.tick(**env, checkpointer=make(), dispatcher=dispatcher, dispatch=True)

    assert result["closed"] == [run_id]
    assert len(dispatcher.calls) == 1  # type: ignore[attr-defined]
    summary = ledger.fold(ledger.load_events(env["run_log"]))[run_id]
    assert summary["status"] == "terminal" and summary["outcome"] == "complete"


# --- REQ-022 R18: reconstruct one run from ledger entries alone ----------------------------


def test_r18_run_reconstructible_from_ledger_alone(tmp_path: Path) -> None:
    env = _env(tmp_path)
    db, make = _checkpointer_factory(tmp_path)
    _bootstrap_and_backdate_watermark(env, make())
    _write_idea(env["idea_log"], "000001", _now())
    start_result = tick_mod.tick(**env, checkpointer=make())
    run_id = start_result["started"][0]
    decisions_mod.decide(
        run_id, intake_mod.GATE_NAME, "approve", "repository-owner", log=env["decision_log"]
    )
    dispatcher = _stub_dispatcher(input_tokens=42, output_tokens=7)
    tick_mod.tick(**env, checkpointer=make(), dispatcher=dispatcher, dispatch=True)

    db.unlink()  # the checkpoint store is gone; reconstruction must not need it

    events = ledger.load_events(env["run_log"])
    grouped = ledger.by_run(events)
    summary = ledger.reconstruct(grouped[run_id])

    assert summary["natural_key"] == "intake:000001"
    assert summary["status"] == "terminal"
    assert summary["outcome"] == "complete"
    assert summary["decisions"] == [{"gate": intake_mod.GATE_NAME, "decision": "approve"}]
    assert summary["dispatches"][0]["result"] == {
        "outcome": "ok", "usage": {"input_tokens": 42, "output_tokens": 7}
    }
    # Also true of the whole-ledger fold, which is what tick.py itself relies on.
    assert ledger.fold(events)[run_id] == summary


# --- REQ-022 R19: no claim-recovery logic in this package ----------------------------------


def test_r19_orchestrator_package_defines_no_claim_recovery_logic() -> None:
    """Mirrors this phase's own verification command; a regression here fails loudly.

    A bare case-insensitive "claim" match is not itself a defect -- the package's own
    docstrings name the boundary rule (REQ-022 R19) by describing what it does *not* do.
    This test asserts that every match found is one of those two known, explainable
    boundary statements, so a *new* match (an actual claim-recovery helper creeping in)
    fails the test rather than passing silently alongside them.
    """
    paths = [
        *sorted((ROOT / "src" / "orchestrator").rglob("*.py")),
        ROOT / "tools" / "append_run.py",
        ROOT / "tools" / "append_decision.py",
    ]
    pattern = re.compile(r"claim", re.IGNORECASE)
    matches: list[str] = []
    for path in paths:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                matches.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")

    allowed_substrings = (
        "This package defines no claim-recovery logic",
        "retries or repairs a `_tmpagent/` claim",
    )
    unexplained = [m for m in matches if not any(a in m for a in allowed_substrings)]
    assert unexplained == [], f"unexplained 'claim' matches: {unexplained}"
    assert len(matches) == 2, (
        f"expected exactly the two known boundary-statement matches, found {matches}"
    )
