"""Tests for `tools/idea_dispatch.py` — the stopgap post-append hook and reconciling sweep.

`tools/append_idea.py` is the only sanctioned writer for `_data/ideas.jsonl` and is never edited
by this tool or these tests. Every test builds a temporary log, appends through the real writer,
then drives the dispatch hook or sweep against it with a stubbed dispatch callable — nothing here
spawns a real `claude` agent (per the phase's own instruction: tests stub the dispatch callable
and assert on what would be dispatched).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


append_idea = _load("append_idea")
idea_dispatch = _load("idea_dispatch")


@pytest.fixture
def log(tmp_path: Path) -> Path:
    return tmp_path / "ideas.jsonl"


@pytest.fixture
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "idea-dispatch-state.json"


@pytest.fixture
def halt_flag(tmp_path: Path) -> Path:
    return tmp_path / "orchestrator-halt"


def _fold(log: Path) -> dict[str, dict[str, Any]]:
    from src.db.ideas import fold, load_events

    return fold(load_events(log))


def _triaging_dispatch_fn(log: Path, calls: list[str]):
    """A stub that behaves like a *successful* real dispatch: writes a finding and triages."""

    def _dispatch(idea: str, title: str, body: str, budget_tokens: int) -> "idea_dispatch.DispatchResult":
        calls.append(idea)
        append_idea.annotate(
            idea, "agent-idea-triage", "finding", f"scouted {title!r}", log=log
        )
        append_idea.change_status(idea, "triaged", log=log)
        return idea_dispatch.DispatchResult(idea, True, "dispatched")
    return _dispatch


def _killed_dispatch_fn(calls: list[str]):
    """A stub that behaves like a dispatch killed mid-run: reports failure, writes nothing."""

    def _dispatch(idea: str, title: str, body: str, budget_tokens: int) -> "idea_dispatch.DispatchResult":
        calls.append(idea)
        return idea_dispatch.DispatchResult(idea, False, "killed mid-run")
    return _dispatch


# --- R06: appended idea is dispatched and triaged with no human action -----------------


def test_dispatch_triages_a_freshly_appended_idea_with_no_human_action(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    event = append_idea.add("Test idea", "Body text", log)
    idea_id = event["idea"]

    calls: list[str] = []
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]
    assert results[0].ok
    state = _fold(log)
    assert state[idea_id]["status"] == "triaged"
    assert any(a["kind"] == "finding" for a in state[idea_id]["annotations"])


def test_dispatch_never_touches_a_pre_watermark_idea(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]
    idea_dispatch.install(log, state_file)  # watermark now covers the pre-existing idea
    new_idea = append_idea.add("New idea", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [new_idea]
    assert pre_existing not in calls
    assert _fold(log)[pre_existing]["status"] == "open"  # untouched — batch /idea-triage owns it


def test_dispatch_does_not_redispatch_an_idea_already_sent(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]  # second call found nothing new to dispatch


# --- R07: a dispatch killed mid-run leaves the idea open; the sweep reconciles it ------


def test_sweep_reconciles_an_idea_left_open_by_a_killed_dispatch(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    kill_calls: list[str] = []
    dispatch_results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_killed_dispatch_fn(kill_calls),
    )
    assert not dispatch_results[0].ok
    assert _fold(log)[idea_id]["status"] == "open"  # nothing lost, but nothing triaged either

    sweep_calls: list[str] = []
    sweep_results = idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, sweep_calls),
    )

    assert sweep_calls == [idea_id]
    assert sweep_results[0].ok
    assert _fold(log)[idea_id]["status"] == "triaged"


def test_sweep_ignores_an_idea_already_triaged(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]
    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    sweep_calls: list[str] = []
    idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, sweep_calls),
    )

    assert sweep_calls == []  # already triaged — nothing left stuck


def test_sweep_ignores_a_pre_watermark_idea_left_open(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]
    idea_dispatch.install(log, state_file)

    calls: list[str] = []
    idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == []
    assert _fold(log)[pre_existing]["status"] == "open"


# --- Kill switch: _working/orchestrator-halt --------------------------------------------


def test_halt_flag_blocks_dispatch_entirely(log: Path, state_file: Path, halt_flag: Path) -> None:
    idea_dispatch.install(log, state_file)
    append_idea.add("Test idea", "Body", log)
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert results == []
    assert calls == []


def test_halt_flag_blocks_sweep_entirely(log: Path, state_file: Path, halt_flag: Path) -> None:
    idea_dispatch.install(log, state_file)
    append_idea.add("Test idea", "Body", log)
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    results = idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert results == []
    assert calls == []


def test_removing_halt_flag_restores_dispatch_with_no_other_state_change(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )
    assert calls == []
    state_before = idea_dispatch._load_state(state_file)

    halt_flag.unlink()
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]
    assert results[0].ok
    # the only state change is the dispatch itself — watermark is untouched
    assert state_before["watermark"] == idea_dispatch._load_state(state_file)["watermark"]


# --- Watermark install ---------------------------------------------------------------


def test_install_watermarks_at_the_current_max_idea_id(log: Path, state_file: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body", log)

    state = idea_dispatch.install(log, state_file)

    assert state["watermark"] == 2
    assert state["dispatched"] == []


def test_install_on_an_empty_log_watermarks_at_zero(log: Path, state_file: Path) -> None:
    state = idea_dispatch.install(log, state_file)
    assert state["watermark"] == 0


def test_dispatch_self_installs_when_never_explicitly_installed(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    """A first `dispatch` call with no prior `install` installs from the log's current contents,
    so it does not retroactively pick up every idea already sitting in the log."""
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == []
    assert pre_existing not in calls
    assert state_file.exists()


# --- Budget ceiling: GOV-014's 300,000-token default is threaded through ---------------


def test_budget_ceiling_matches_gov_014_default() -> None:
    assert idea_dispatch.TRIAGE_TOKEN_CEILING == 300_000


def test_dispatch_passes_the_budget_ceiling_to_the_dispatch_callable(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    idea_dispatch.install(log, state_file)
    append_idea.add("Test idea", "Body", log)

    seen_budgets: list[int] = []

    def _dispatch(idea: str, title: str, body: str, budget_tokens: int):
        seen_budgets.append(budget_tokens)
        return idea_dispatch.DispatchResult(idea, True, "ok")

    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, dispatch_fn=_dispatch
    )

    assert seen_budgets == [idea_dispatch.TRIAGE_TOKEN_CEILING]


# --- CLI status ------------------------------------------------------------------------


def test_status_reports_not_installed_before_install(state_file: Path, halt_flag: Path) -> None:
    assert idea_dispatch._status(state_file, halt_flag) == "not installed"


def test_status_reports_watermark_and_halt_state_after_install(
    log: Path, state_file: Path, halt_flag: Path
) -> None:
    append_idea.add("First", "Body", log)
    idea_dispatch.install(log, state_file)

    report = idea_dispatch._status(state_file, halt_flag)

    assert "watermark: 000001" in report
    assert "halted: False" in report
