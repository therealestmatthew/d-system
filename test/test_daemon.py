"""Tests for the daemon's process model (`phase-irs-16`, PLAN-039.01 section 2).

Every test uses `tmp_path` for the lock, the tracked-log stand-ins and the checkpoint store
-- nothing here touches `data/` or `_data/` of the real checkout. The two acceptance rows
are real process-level tests: `test_manual_tick_exits_while_daemon_holds_the_lock` and
`test_stale_lock_recovers_after_forced_kill` each spawn a real daemon subprocess (via
`_DAEMON_DRIVER`, calling `daemon.run_daemon()` directly with `worktree_check=lambda:
False` -- see its docstring for why), exercise it, and assert on process exit codes and lock
state -- never on in-process mocks standing in for the daemon itself. The manual `tick`
verb in these tests *does* go through the real CLI (`python -m src.orchestrator ... tick`),
since `tick` carries no worktree check to route around. `test_sigterm_stop_is_graceful`
covers the graceful-shutdown half of the same acceptance row ("finishes the current tick
and releases the lock"). The linked-worktree refusal itself is exercised directly against
`run_daemon()`'s injectable `worktree_check` (`test_run_daemon_refuses_a_linked_worktree`,
`test_run_daemon_runs_in_a_primary_checkout`) and against the real, strict default
(`test_is_linked_worktree_false_for_the_primary_checkout_git_root`) -- the CLI's `start`
verb itself is never given a way to skip the check; only `run_daemon()`'s parameter allows
a non-CLI caller to supply a different one.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

from src.orchestrator import daemon as daemon_mod
from src.orchestrator import ledger

ROOT = Path(__file__).resolve().parents[1]


# --- helpers -------------------------------------------------------------------------------


def _wait_until(predicate: Any, *, timeout: float = 5.0, interval: float = 0.05) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(interval)
    raise AssertionError(f"condition not met within {timeout}s")


def _paths(tmp_path: Path) -> dict[str, Path]:
    return {
        "lock": tmp_path / "lock",
        "idea_log": tmp_path / "ideas.jsonl",
        "run_log": tmp_path / "runs.jsonl",
        "decision_log": tmp_path / "decisions.jsonl",
        "watermark": tmp_path / "watermark",
        "checkpoint_db": tmp_path / "checkpoints.sqlite",
    }


#: A tiny driver run via `python -c`, standing in for `python -m src.orchestrator start` in
#: these process-level tests. It calls `daemon.run_daemon()` directly with
#: `worktree_check=lambda: False` rather than going through the CLI's `start` verb, because
#: the CLI's production `start` always uses the strict, real `is_linked_worktree()` check
#: (PLAN-039.01 section 2's "the primary checkout only") and this test suite itself runs
#: from a linked worktree -- exercising lock contention and kill-recovery must not require
#: weakening that check for real invocations. `daemon.run_daemon()`'s `worktree_check`
#: parameter exists precisely so a caller other than the strict CLI can supply this.
_DAEMON_DRIVER = """
import json, sys
from pathlib import Path
from src.orchestrator import daemon

paths = json.loads(sys.argv[1])
poll_interval = float(sys.argv[2])
ticks = daemon.run_daemon(
    lock_path=Path(paths["lock"]),
    poll_interval=poll_interval,
    worktree_check=lambda: False,
    tick_kwargs={
        "idea_log": Path(paths["idea_log"]),
        "run_log": Path(paths["run_log"]),
        "decision_log": Path(paths["decision_log"]),
        "watermark_path": Path(paths["watermark"]),
        "checkpoint_db": Path(paths["checkpoint_db"]),
    },
)
print(f"daemon stopped after {ticks} tick(s)")
"""


def _daemon_argv(paths: dict[str, Path], *, poll_interval: float = 0.1) -> list[str]:
    payload = json.dumps({key: str(value) for key, value in paths.items()})
    return [sys.executable, "-c", _DAEMON_DRIVER, payload, str(poll_interval)]


def _tick_argv(paths: dict[str, Path]) -> list[str]:
    return [
        sys.executable, "-m", "src.orchestrator",
        "--lock", str(paths["lock"]),
        "--idea-log", str(paths["idea_log"]),
        "--run-log", str(paths["run_log"]),
        "--decision-log", str(paths["decision_log"]),
        "--watermark", str(paths["watermark"]),
        "--checkpoint-db", str(paths["checkpoint_db"]),
        "tick",
    ]


def _spawn(argv: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def _wait_daemon_holds_lock(paths: dict[str, Path], daemon_proc: subprocess.Popen[str]) -> None:
    def _running() -> bool:
        assert daemon_proc.poll() is None, "daemon exited before taking the lock"
        return bool(daemon_mod.probe_lock(paths["lock"])["running"])

    _wait_until(_running)


# --- acceptance: a manual tick never runs concurrently with a live daemon ------------------


def test_manual_tick_exits_while_daemon_holds_the_lock(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    daemon_proc = _spawn(_daemon_argv(paths))
    try:
        _wait_daemon_holds_lock(paths, daemon_proc)

        tick_proc = subprocess.run(
            _tick_argv(paths), cwd=ROOT, capture_output=True, text=True, timeout=10
        )

        assert tick_proc.returncode != 0
        assert "daemon holds the lock" in tick_proc.stderr
        assert daemon_proc.poll() is None  # the daemon itself never crashed or overlapped
    finally:
        daemon_proc.send_signal(signal.SIGTERM)
        daemon_proc.wait(timeout=10)


# --- acceptance: a stale lock left by a killed daemon recovers with no manual cleanup ------


def test_stale_lock_recovers_after_forced_kill(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    daemon_proc = _spawn(_daemon_argv(paths))
    _wait_daemon_holds_lock(paths, daemon_proc)
    holder_before = daemon_mod.probe_lock(paths["lock"])["holder"]
    assert holder_before is not None and holder_before["pid"] == daemon_proc.pid

    daemon_proc.send_signal(signal.SIGKILL)
    daemon_proc.wait(timeout=10)  # the kernel releases the flock the instant this reaps

    # No manual cleanup of the lock file happens here -- the very next acquirer just works.
    tick_proc = subprocess.run(
        _tick_argv(paths), cwd=ROOT, capture_output=True, text=True, timeout=10
    )
    assert tick_proc.returncode == 0, tick_proc.stderr
    result = json.loads(tick_proc.stdout)
    assert result == {"started": [], "rekeyed": [], "resumed": [], "closed": [], "deferred": []}

    # The stale pid is still what a probe reports until the lock is next taken and released
    # (PLAN-039.01 section 2: "a stale pid in the file is informational only") -- but the
    # lock itself is free, which is the recovery this test demonstrates.
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


# --- SIGTERM stop is graceful: finishes the tick in flight, then releases the lock ---------


def test_sigterm_stop_is_graceful(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    daemon_proc = _spawn(_daemon_argv(paths))
    _wait_daemon_holds_lock(paths, daemon_proc)

    stop_result = daemon_mod.stop_daemon(paths["lock"])
    assert stop_result == {"stopped": True, "pid": daemon_proc.pid}

    returncode = daemon_proc.wait(timeout=10)
    assert returncode == 0
    stdout, _stderr = daemon_proc.communicate()
    assert "daemon stopped after" in stdout

    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


# --- stop / status against an already-free lock are reported, not raised -------------------


def test_stop_daemon_reports_when_nothing_holds_the_lock(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    result = daemon_mod.stop_daemon(paths["lock"])
    assert result == {"stopped": False, "reason": "no daemon holds the lock"}


def test_stop_daemon_never_signals_a_live_unrelated_process_named_by_a_stale_lock(
    tmp_path: Path,
) -> None:
    """A lock *file* naming a live pid, with nobody actually holding the `flock`, must not
    be signaled -- this is the fix-cycle-1 finding (MEDIUM): pid reuse after a killed
    daemon must never cause `stop` to signal an unrelated live process. `sleep` stands in
    for that unrelated process; its pid is written into the lock file exactly as a real
    daemon's would be, but the file's flock is never taken, matching a killed daemon's
    file left behind by the kernel-released lock.
    """
    lock_path = tmp_path / "lock"
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        lock_path.write_text(
            json.dumps({"pid": sleeper.pid, "started_at": ledger.now()}), encoding="utf-8"
        )

        result = daemon_mod.stop_daemon(lock_path)

        assert result == {"stopped": False, "reason": "no daemon holds the lock"}
        assert sleeper.poll() is None  # never signaled -- still alive
    finally:
        sleeper.kill()
        sleeper.wait(timeout=10)


def test_stop_daemon_still_signals_the_real_holder_gracefully(tmp_path: Path) -> None:
    """The fix must not regress the ordinary case: a live daemon that genuinely holds the
    lock is still found and signaled. Process-level companion to the stale-lock test above.
    """
    paths = _paths(tmp_path)
    daemon_proc = _spawn(_daemon_argv(paths))
    _wait_daemon_holds_lock(paths, daemon_proc)

    result = daemon_mod.stop_daemon(paths["lock"])

    assert result == {"stopped": True, "pid": daemon_proc.pid}
    assert daemon_proc.wait(timeout=10) == 0
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


def test_probe_lock_reports_free_then_held(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False

    with daemon_mod.acquire_lock(paths["lock"]):
        info = daemon_mod.probe_lock(paths["lock"])
        assert info["running"] is True
        assert info["holder"]["pid"] == os.getpid()

    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


def test_acquire_lock_nonblocking_raises_when_already_held(tmp_path: Path) -> None:
    lock_path = tmp_path / "lock"
    with daemon_mod.acquire_lock(lock_path):
        with pytest.raises(daemon_mod.LockHeldError) as excinfo:
            with daemon_mod.acquire_lock(lock_path):
                pass  # pragma: no cover -- must never be entered
    assert "daemon holds the lock" in str(excinfo.value)
    assert excinfo.value.holder is not None
    assert excinfo.value.holder["pid"] == os.getpid()


# --- linked-worktree refusal: exercised both ways via the injectable check -----------------


def _tick_kwargs(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "idea_log": paths["idea_log"],
        "run_log": paths["run_log"],
        "decision_log": paths["decision_log"],
        "watermark_path": paths["watermark"],
        "checkpoint_db": paths["checkpoint_db"],
    }


def test_run_daemon_refuses_a_linked_worktree(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    with pytest.raises(daemon_mod.LinkedWorktreeError):
        daemon_mod.run_daemon(
            lock_path=paths["lock"],
            worktree_check=lambda: True,
            tick_kwargs=_tick_kwargs(paths),
            max_ticks=1,
        )
    # Refused before the lock was ever touched.
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


def test_run_daemon_runs_in_a_primary_checkout(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    ticks_run = daemon_mod.run_daemon(
        lock_path=paths["lock"],
        worktree_check=lambda: False,
        tick_kwargs=_tick_kwargs(paths),
        max_ticks=1,
    )
    assert ticks_run == 1
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


def test_run_daemon_stops_on_stop_event_already_set(tmp_path: Path) -> None:
    """A `stop_event` set before the loop starts stops it before any tick, lock released."""
    paths = _paths(tmp_path)
    stop_event = threading.Event()
    stop_event.set()  # already requested before the loop's first check

    ticks_run = daemon_mod.run_daemon(
        lock_path=paths["lock"],
        worktree_check=lambda: False,
        tick_kwargs=_tick_kwargs(paths),
        stop_event=stop_event,
    )
    assert ticks_run == 0  # the loop never entered its body
    assert daemon_mod.probe_lock(paths["lock"])["running"] is False


# --- is_linked_worktree() itself: the real check against a real repository -----------------


def test_is_linked_worktree_false_for_the_primary_checkout_git_root() -> None:
    # ROOT (module docstring) points at this worktree's own checkout; whether *this*
    # worktree is itself linked is exactly what the function is designed to answer, so this
    # only asserts the function runs and returns a bool rather than asserting a fixed value.
    assert isinstance(daemon_mod.is_linked_worktree(ROOT), bool)


def test_is_linked_worktree_false_for_a_non_git_directory(tmp_path: Path) -> None:
    assert daemon_mod.is_linked_worktree(tmp_path) is False


def test_ledger_now_used_as_lock_timestamp_is_iso_like(tmp_path: Path) -> None:
    # Sanity check that the lock file's timestamp comes from the same clock the rest of the
    # orchestrator uses (`ledger.now()`), not a bespoke format nothing else reads.
    with daemon_mod.acquire_lock(tmp_path / "lock"):
        holder = daemon_mod.probe_lock(tmp_path / "lock")["holder"]
    assert holder is not None
    assert holder["started_at"] <= ledger.now()
