"""Tests for `tools/idea_dispatch.py` — the stopgap post-append hook and reconciling sweep.

`tools/append_idea.py` is the only sanctioned writer for `_data/ideas.jsonl` and is never edited
by this tool or these tests. Every test builds a temporary log, appends through the real writer,
then drives the dispatch hook or sweep against it with a stubbed dispatch callable — nothing here
spawns a real `claude` agent (per the phase's own instruction: tests stub the dispatch callable
and assert on what would be dispatched).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
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


@pytest.fixture
def claims_dir(tmp_path: Path) -> Path:
    return tmp_path / "idea-dispatch-claims"


def _fold(log: Path) -> dict[str, dict[str, Any]]:
    from src.db.ideas import fold, load_events

    return fold(load_events(log))


def _triaging_dispatch_fn(log: Path, calls: list[str]):
    """A stub that behaves like a *successful* real dispatch: writes a finding and triages."""

    def _dispatch(idea: str, title: str, body: str) -> "idea_dispatch.DispatchResult":
        calls.append(idea)
        append_idea.annotate(
            idea, "agent-idea-triage", "finding", f"scouted {title!r}", log=log
        )
        append_idea.change_status(idea, "triaged", log=log)
        return idea_dispatch.DispatchResult(idea, True, "dispatched")
    return _dispatch


def _killed_dispatch_fn(calls: list[str]):
    """A stub that behaves like a dispatch killed mid-run: reports failure, writes nothing."""

    def _dispatch(idea: str, title: str, body: str) -> "idea_dispatch.DispatchResult":
        calls.append(idea)
        return idea_dispatch.DispatchResult(idea, False, "killed mid-run")
    return _dispatch


# --- R06: appended idea is dispatched and triaged with no human action -----------------


def test_dispatch_triages_a_freshly_appended_idea_with_no_human_action(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    event = append_idea.add("Test idea", "Body text", log)
    idea_id = event["idea"]

    calls: list[str] = []
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]
    assert results[0].ok
    state = _fold(log)
    assert state[idea_id]["status"] == "triaged"
    assert any(a["kind"] == "finding" for a in state[idea_id]["annotations"])


def test_dispatch_never_touches_a_pre_watermark_idea(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]
    idea_dispatch.install(log, state_file)  # watermark now covers the pre-existing idea
    new_idea = append_idea.add("New idea", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [new_idea]
    assert pre_existing not in calls
    assert _fold(log)[pre_existing]["status"] == "open"  # untouched — batch /idea-triage owns it


def test_dispatch_does_not_redispatch_an_idea_already_sent(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]  # second call found nothing new to dispatch


def test_watch_dispatches_a_freshly_appended_idea_via_poll_with_no_human_action(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """The actual R06 trigger: `poll_once` is the tick `watch`'s loop calls. This drives one
    poll iteration explicitly (no thread, no real sleep) against a log that already has the
    watermark installed, appends a new idea through the real `append_idea.add` writer — the
    same call `tools/append_idea.py add` makes — and asserts the stubbed dispatch fired for it
    with no further action taken by the test beyond the poll itself."""
    idea_dispatch.install(log, state_file)

    event = append_idea.add("Test idea", "Body text", log)
    idea_id = event["idea"]

    calls: list[str] = []
    results = idea_dispatch.poll_once(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]
    assert results[0].ok
    assert _fold(log)[idea_id]["status"] == "triaged"


def test_watch_loop_ticks_and_dispatches_via_poll_once(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """Drives the actual `watch` loop (bounded to a couple of iterations, sleep stubbed out) to
    confirm the loop itself calls `poll_once` on each tick and picks up an idea appended before
    the loop starts — end-to-end through the real writer, no direct call to `dispatch`."""
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body text", log)["idea"]

    calls: list[str] = []
    sleeps: list[float] = []
    idea_dispatch.watch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
        interval=0.01,
        max_iterations=2,
        sleep_fn=sleeps.append,
    )

    assert calls == [idea_id]
    assert _fold(log)[idea_id]["status"] == "triaged"
    assert sleeps == [0.01]  # one sleep between the two ticks, none after the last


def test_watch_survives_a_raising_dispatch_fn_and_keeps_running(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """Failure isolation for the automatic trigger: a `dispatch_fn` that raises mid-tick must
    not kill the watcher — the next append is still picked up on a later tick, and the sweep
    remains the recovery path for the one that raised."""
    idea_dispatch.install(log, state_file)
    first_id = append_idea.add("First idea", "Body", log)["idea"]

    def _raising(idea: str, title: str, body: str):
        raise RuntimeError("simulated crash mid-dispatch")

    calls: list[str] = []
    second_id_holder: list[str] = []

    def _dispatch_fn(idea: str, title: str, body: str):
        if idea == first_id:
            return _raising(idea, title, body)
        return _triaging_dispatch_fn(log, calls)(idea, title, body)

    def _sleep(_seconds: float) -> None:
        # append the second idea between tick 1 (raises on first_id) and tick 2, simulating a
        # real append happening while the watcher is running with no human re-invoking anything
        second_id_holder.append(append_idea.add("Second idea", "Body", log)["idea"])

    idea_dispatch.watch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_dispatch_fn,
        interval=0.01,
        max_iterations=2,
        sleep_fn=_sleep,
    )

    second_id = second_id_holder[0]
    assert calls == [second_id]
    assert _fold(log)[first_id]["status"] == "open"  # left for sweep to recover
    assert _fold(log)[second_id]["status"] == "triaged"


# --- R07: a dispatch killed mid-run leaves the idea open; the sweep reconciles it ------


def test_sweep_reconciles_an_idea_left_open_by_a_killed_dispatch(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    kill_calls: list[str] = []
    dispatch_results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_killed_dispatch_fn(kill_calls),
    )
    assert not dispatch_results[0].ok
    assert _fold(log)[idea_id]["status"] == "open"  # nothing lost, but nothing triaged either

    sweep_calls: list[str] = []
    sweep_results = idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, sweep_calls),
    )

    assert sweep_calls == [idea_id]
    assert sweep_results[0].ok
    assert _fold(log)[idea_id]["status"] == "triaged"


def test_sweep_ignores_an_idea_already_triaged(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]
    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    sweep_calls: list[str] = []
    idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, sweep_calls),
    )

    assert sweep_calls == []  # already triaged — nothing left stuck


def test_sweep_ignores_a_pre_watermark_idea_left_open(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]
    idea_dispatch.install(log, state_file)

    calls: list[str] = []
    idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == []
    assert _fold(log)[pre_existing]["status"] == "open"


# --- Kill switch: _working/orchestrator-halt --------------------------------------------


def test_halt_flag_blocks_dispatch_entirely(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    append_idea.add("Test idea", "Body", log)
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert results == []
    assert calls == []


def test_halt_flag_blocks_sweep_entirely(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    append_idea.add("Test idea", "Body", log)
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    results = idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert results == []
    assert calls == []


def test_removing_halt_flag_restores_dispatch_with_no_other_state_change(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]
    halt_flag.write_text("", encoding="utf-8")

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )
    assert calls == []
    state_before = idea_dispatch._load_state(state_file)

    halt_flag.unlink()
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
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
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """A first `dispatch` call with no prior `install` installs from the log's current contents,
    so it does not retroactively pick up every idea already sitting in the log."""
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]

    calls: list[str] = []
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == []
    assert pre_existing not in calls
    assert state_file.exists()


def test_dispatch_self_install_warns_about_excluded_open_ideas(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Cycle-2 fix: silently excluding pre-existing open ideas from both dispatch and sweep is a
    permanent, invisible loss unless something says so. A first `dispatch` with no prior explicit
    `install` must print which open ideas it is leaving to the batch `/idea-triage` path."""
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]

    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, []),
    )

    captured = capsys.readouterr()
    assert pre_existing in captured.err
    assert "excluded" in captured.err


def test_poll_once_self_install_also_warns(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pre_existing = append_idea.add("Pre-existing", "Body", log)["idea"]

    idea_dispatch.poll_once(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, []),
    )

    captured = capsys.readouterr()
    assert pre_existing in captured.err


def test_explicit_install_does_not_warn(
    log: Path, state_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The explicit `install` command is the operator choosing this behavior on purpose — it
    should stay quiet. Only the silent self-install path needs the warning."""
    append_idea.add("Pre-existing", "Body", log)

    idea_dispatch.install(log, state_file)

    captured = capsys.readouterr()
    assert captured.err == ""


def test_self_install_with_no_open_ideas_prints_nothing(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty log has nothing to exclude — no warning is warranted."""
    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, []),
    )

    captured = capsys.readouterr()
    assert captured.err == ""


# --- Budget ceiling: GOV-014's 300,000-token default is recorded, not transmitted -------
#
# Cycle-2 fix: `claude --help` exposes no per-invocation token-budget flag (only
# `--max-budget-usd`, a dollar figure, and `--autocompact`, a context-window size — neither is a
# token ceiling), so `budget_tokens` was dropped from `default_dispatch` and from `DispatchFn`
# entirely rather than kept as a parameter nothing ever reads. `TRIAGE_TOKEN_CEILING` stays as a
# documented constant for traceability against GOV-014, but is no longer threaded through a
# dispatch call at all.


def test_budget_ceiling_matches_gov_014_default() -> None:
    assert idea_dispatch.TRIAGE_TOKEN_CEILING == 300_000


def test_default_dispatch_does_not_accept_a_budget_tokens_argument() -> None:
    """The parameter is gone, not merely unused — `default_dispatch` takes exactly (idea, title,
    body), matching `DispatchFn`'s three-argument contract."""
    import inspect

    params = list(inspect.signature(idea_dispatch.default_dispatch).parameters)
    assert params == ["idea", "title", "body"]


# --- CLI status ------------------------------------------------------------------------


def test_status_reports_not_installed_before_install(state_file: Path, halt_flag: Path) -> None:
    assert idea_dispatch._status(state_file, halt_flag) == "not installed"


def test_status_reports_watermark_and_halt_state_after_install(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    append_idea.add("First", "Body", log)
    idea_dispatch.install(log, state_file)

    report = idea_dispatch._status(state_file, halt_flag)

    assert "watermark: 000001" in report
    assert "halted: False" in report


# --- Cycle-2 fix: in-flight claim guard against double dispatch (finding 1, major) -------
#
# Adversary reproduction: `poll_once` racing `sweep` on the same idea fired the stub dispatch
# twice for one idea, because "dispatched" state was only recorded after a dispatch *returned*
# and `sweep` re-dispatched anything `fold()` still showed `open` with no in-flight marker. The
# fix: an atomically-created per-idea claim file (`O_CREAT | O_EXCL`) under
# `_working/idea-dispatch-claims/`, held for the duration of the `dispatch_fn` call and released
# after, checked by `dispatch`, `poll_once`, and `sweep` alike — so any of them, or two of them at
# once, dispatch a given idea at most once concurrently.


def test_a_live_claim_blocks_a_concurrent_dispatch_on_the_same_idea(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """Simulates the adversary's reproduction directly: while one dispatch is in flight (inside
    its own `dispatch_fn`), a second dispatch path (here, `sweep`) is attempted on the same idea
    and must find it already claimed."""
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    outer_calls: list[str] = []
    inner_calls: list[str] = []

    def _outer_dispatch(idea: str, title: str, body: str):
        outer_calls.append(idea)
        # a concurrent sweep, attempted while this dispatch still holds the claim
        idea_dispatch.sweep(
            log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
            dispatch_fn=_triaging_dispatch_fn(log, inner_calls),
        )
        return idea_dispatch.DispatchResult(idea, True, "ok")

    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_outer_dispatch,
    )

    assert outer_calls == [idea_id]
    assert inner_calls == []  # blocked — the outer dispatch still held the claim


def test_two_back_to_back_dispatch_calls_yield_exactly_one_dispatch_when_a_claim_is_pre_held(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """A cruder version of the same guarantee: pre-create a live claim file (as if another
    process holds it right now) and confirm `dispatch` skips that idea entirely rather than
    firing a second dispatch."""
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    claims_dir.mkdir(parents=True, exist_ok=True)
    (claims_dir / f"{idea_id}.claim").touch()  # freshly created — very much not stale

    calls: list[str] = []
    results = idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == []
    assert results == []
    assert _fold(log)[idea_id]["status"] == "open"  # untouched — still claimed elsewhere


def test_a_stale_claim_does_not_block_the_sweep(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """R07 must keep holding: a claim left behind by a dispatch whose process died mid-run cannot
    be allowed to permanently block recovery. A claim older than `CLAIM_STALE_SECONDS` is taken
    over rather than honored."""
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    claims_dir.mkdir(parents=True, exist_ok=True)
    stale_claim = claims_dir / f"{idea_id}.claim"
    stale_claim.touch()
    stale_time = time.time() - idea_dispatch.CLAIM_STALE_SECONDS - 60
    os.utime(stale_claim, (stale_time, stale_time))

    calls: list[str] = []
    results = idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, calls),
    )

    assert calls == [idea_id]
    assert results[0].ok
    assert _fold(log)[idea_id]["status"] == "triaged"
    assert not stale_claim.exists()  # released after the takeover dispatch completed


def test_claim_is_released_after_a_successful_dispatch(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_triaging_dispatch_fn(log, []),
    )

    assert not (claims_dir / f"{idea_id}.claim").exists()


def test_claim_is_released_even_when_the_dispatch_fn_raises(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    """The claim must not be leaked on failure — otherwise a raising `dispatch_fn` would itself
    become a source of permanent (if eventually stale-recoverable) lockout."""
    idea_dispatch.install(log, state_file)
    idea_id = append_idea.add("Test idea", "Body", log)["idea"]

    def _raising(idea: str, title: str, body: str):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        idea_dispatch.dispatch(
            log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
            dispatch_fn=_raising,
        )

    assert not (claims_dir / f"{idea_id}.claim").exists()


# --- Cycle-2 fix: halt flag re-checked per candidate inside dispatch()/sweep() (finding 2) ---
#
# `poll_once` already re-checked the halt flag before every individual idea; `dispatch` and
# `sweep` checked it only once at entry, which contradicted OPS-016's claim that all three
# commands check "before every dispatch attempt". Both loops now re-check per candidate.


def test_dispatch_rechecks_the_halt_flag_before_each_candidate_not_just_once(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    first_id = append_idea.add("First", "Body", log)["idea"]
    second_id = append_idea.add("Second", "Body", log)["idea"]

    calls: list[str] = []

    def _dispatch_fn(idea: str, title: str, body: str):
        calls.append(idea)
        if idea == first_id:
            halt_flag.write_text("", encoding="utf-8")  # halt dropped mid-batch
        return idea_dispatch.DispatchResult(idea, True, "ok")

    idea_dispatch.dispatch(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_dispatch_fn,
    )

    assert calls == [first_id]  # second idea never attempted
    assert _fold(log)[second_id]["status"] == "open"


def test_sweep_rechecks_the_halt_flag_before_each_candidate_not_just_once(
    log: Path, state_file: Path, halt_flag: Path, claims_dir: Path
) -> None:
    idea_dispatch.install(log, state_file)
    first_id = append_idea.add("First", "Body", log)["idea"]
    second_id = append_idea.add("Second", "Body", log)["idea"]

    calls: list[str] = []

    def _dispatch_fn(idea: str, title: str, body: str):
        calls.append(idea)
        if idea == first_id:
            halt_flag.write_text("", encoding="utf-8")  # halt dropped mid-batch
        return idea_dispatch.DispatchResult(idea, False, "still open")

    idea_dispatch.sweep(
        log=log, state_file=state_file, halt_flag=halt_flag, claims_dir=claims_dir,
        dispatch_fn=_dispatch_fn,
    )

    assert calls == [first_id]  # second idea never attempted, left for the next sweep
    assert _fold(log)[second_id]["status"] == "open"
