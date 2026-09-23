"""The daemon's process model: the shared `flock` lock, signal handling, start/stop/status.

PLAN-039.01 section 2: one daemon, one lock, and a tick that works alone. The lock is
`flock` on `data/orchestrator/lock`, taken exclusively and non-blocking by both the
daemon's own loop and a manual `tick` invocation -- whichever gets there first holds it;
the other exits with a message naming the holder rather than running concurrently.
`flock` is advisory and scoped to the holding process's open file descriptor, so a
`SIGKILL`'d holder loses the lock the instant the kernel closes its open descriptors: the very
next `acquire_lock()` call here succeeds without anyone needing to notice or clean up the
pid recorded inside the file (section 2, section 11's "the daemon crashes" row). Recovery
from a stale lock is a side effect of always locking through the kernel rather than trusting
the file's own content -- there is no separate "detect a stale lock" code path to write.

`start` runs the loop in the foreground of whatever process invokes it: it takes the lock,
installs `SIGTERM`/`SIGINT` handlers that ask the loop to stop after its current tick, and
returns once the lock is released. Backgrounding it (`&`, a supervisor) is the caller's
concern, not this module's -- there is no internal double-fork.

**Where the daemon runs.** `is_linked_worktree()` is `start`'s production check
(`git rev-parse --git-common-dir` versus `--git-dir`; they differ only inside a linked
worktree) and is injected into `run_daemon()` as `worktree_check` so tests can exercise both
branches without the real check ever refusing to run inside the linked worktree the test
suite itself executes from -- the production default stays strict.
"""

from __future__ import annotations

import contextlib
import errno
import fcntl
import json
import os
import signal
import subprocess
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from src.orchestrator import ledger
from src.orchestrator import tick as tick_mod

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK_PATH = ROOT / "data" / "orchestrator" / "lock"
DEFAULT_CHECKPOINT_DB = ROOT / "data" / "orchestrator" / "checkpoints.sqlite"

#: Seconds between ticks while the daemon loop is idle. A signal wakes the wait immediately,
#: so this bounds only how quickly a repo-internal watcher's wake-up is noticed, not shutdown
#: latency.
DEFAULT_POLL_INTERVAL = 5.0


class LockHeldError(Exception):
    """The lock at `lock_path` is already held by another process.

    Raised by `acquire_lock()` for both the daemon's own `start` (another daemon is already
    running) and a manual `tick` (the daemon is running) -- PLAN-039.01 section 2's "a
    manual tick while the daemon is alive ... exits with 'daemon holds the lock'".
    """

    def __init__(self, holder: dict[str, Any] | None) -> None:
        self.holder = holder
        message = "daemon holds the lock"
        if holder and "pid" in holder:
            message += f" (pid={holder['pid']}, started_at={holder.get('started_at', '?')})"
        super().__init__(message)


class LinkedWorktreeError(Exception):
    """`start` was invoked outside the primary checkout (PLAN-039.01 section 2)."""


def _read_holder(lock_path: Path) -> dict[str, Any] | None:
    """Best-effort read of the lock file's own pid/started_at record.

    Never authoritative -- a pid recorded here can outlive the process it names (the daemon
    crashed) or can already belong to something else entirely (pid reuse). It exists only to
    make `status` and a contended `tick`'s error message informative, per PLAN-039.01
    section 2 ("a stale pid in the file is informational only").
    """
    try:
        text = lock_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


@contextlib.contextmanager
def acquire_lock(lock_path: Path = DEFAULT_LOCK_PATH, *, blocking: bool = False) -> Iterator[None]:
    """Hold the exclusive `flock` at `lock_path` for the `with` block's lifetime.

    Non-blocking by default: the daemon's loop and a manual `tick` only ever compete with
    each other, both short-lived relative to a human waiting on a terminal, so the default
    is to fail fast with `LockHeldError` naming the holder rather than block indefinitely.
    `blocking=True` is exposed for a caller that explicitly wants to wait (PLAN-039.01
    section 2 names "waits or exits" as both legal); the CLI verbs built on this module use
    the non-blocking default.

    While held, the lock file's content is replaced with this process's pid and start time
    (`{"pid": ..., "started_at": ...}`) -- the record `status` and a contended acquirer's
    error message read. Releasing (including on a killed process, via the kernel) leaves
    that content in place; it is never treated as proof the lock is still held, only as
    informational context for whoever reads it next.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    flags = fcntl.LOCK_EX if blocking else (fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        fcntl.flock(fd, flags)
    except OSError as exc:
        os.close(fd)
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            raise LockHeldError(_read_holder(lock_path)) from None
        raise
    try:
        os.ftruncate(fd, 0)
        os.write(fd, json.dumps({"pid": os.getpid(), "started_at": ledger.now()}).encode("utf-8"))
        os.fsync(fd)
        yield
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def probe_lock(lock_path: Path = DEFAULT_LOCK_PATH) -> dict[str, Any]:
    """Report whether `lock_path` is currently held, without disturbing it either way.

    Takes and immediately releases the lock to test it -- this never overwrites the file's
    content, unlike `acquire_lock`, so a probe never clobbers the previous holder's record
    with its own pid. Used by `status` (report only) and `stop` (find the pid to signal).
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                return {"running": True, "holder": _read_holder(lock_path)}
            raise
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
            return {"running": False, "holder": _read_holder(lock_path)}
    finally:
        os.close(fd)


def stop_daemon(
    lock_path: Path = DEFAULT_LOCK_PATH, *, sig: signal.Signals = signal.SIGTERM
) -> dict[str, Any]:
    """Signal the process holding `lock_path`'s lock (`SIGTERM` by default) to stop.

    Graceful: the daemon's own signal handler finishes its current tick and releases the
    lock (PLAN-039.01 section 2: "`stop` signals the daemon (SIGTERM), which finishes the
    current tick and releases the lock"). Idempotent against a lock that is not held, or
    whose recorded pid is already gone (a stale record from a killed daemon) -- both are
    reported rather than raised, since there is nothing left to stop.
    """
    info = probe_lock(lock_path)
    if not info["running"]:
        return {"stopped": False, "reason": "no daemon holds the lock"}
    holder = info["holder"]
    if not holder or "pid" not in holder:
        return {"stopped": False, "reason": "lock is held but no pid was recorded"}
    pid = int(holder["pid"])
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        return {
            "stopped": False,
            "reason": f"pid {pid} is not running (stale lock; the next start recovers it)",
        }
    return {"stopped": True, "pid": pid}


def is_linked_worktree(root: Path = ROOT) -> bool:
    """Whether `root` is a linked worktree rather than the primary checkout.

    `git rev-parse --git-common-dir` names the shared `.git` every worktree of a repository
    points at; `--git-dir` names the directory git actually reads for *this* checkout. They
    are the same path only in the primary checkout -- a linked worktree's `--git-dir` is its
    own private directory under the common one's `worktrees/` subdirectory. PLAN-039.01
    section 2 names this exact pair of commands as the check.
    """

    def _git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        common_dir = Path(_git("rev-parse", "--git-common-dir"))
        git_dir = Path(_git("rev-parse", "--git-dir"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    if not common_dir.is_absolute():
        common_dir = root / common_dir
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    return common_dir.resolve() != git_dir.resolve()


def run_daemon(
    *,
    lock_path: Path = DEFAULT_LOCK_PATH,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    worktree_check: Callable[[], bool] = is_linked_worktree,
    tick_kwargs: dict[str, Any] | None = None,
    max_ticks: int | None = None,
    stop_event: threading.Event | None = None,
) -> int:
    """Run the daemon loop in the foreground: take the lock, tick, wait, repeat.

    Returns the number of ticks run. Raises `LinkedWorktreeError` if `worktree_check()`
    says this is a linked worktree (checked before the lock is even attempted), and
    `LockHeldError` if another daemon already holds the lock. Both are caller-facing
    refusals the CLI turns into an exit code and a message; neither leaves the lock touched.

    `worktree_check` defaults to `is_linked_worktree` (the strict, production check) but is
    a parameter specifically so tests can supply a stub -- the test suite itself runs from a
    linked worktree, and the real check must not be the thing that makes daemon tests
    impossible to run there.

    `SIGTERM` and `SIGINT` both ask the loop to stop after the tick in progress finishes
    (never mid-tick): the handler only sets `stop_event`, which the loop checks between
    ticks and during its poll wait. `stop_event` defaults to a fresh `threading.Event` but
    is a parameter so a caller (a test in the same process) could drive shutdown without a
    real signal; the process-level tests in `test/test_daemon.py` use real signals.
    """
    if worktree_check():
        raise LinkedWorktreeError(
            "the daemon refuses to start in a linked worktree -- run it in the primary "
            "checkout (PLAN-039.01 section 2)"
        )

    tick_kwargs = dict(tick_kwargs or {})
    checkpoint_db = tick_kwargs.pop("checkpoint_db", DEFAULT_CHECKPOINT_DB)
    checkpointer = tick_mod.open_checkpoint_store(checkpoint_db)
    event = stop_event if stop_event is not None else threading.Event()

    def _handle_signal(signum: int, frame: Any) -> None:
        event.set()

    previous_term = signal.signal(signal.SIGTERM, _handle_signal)
    previous_int = signal.signal(signal.SIGINT, _handle_signal)
    ticks_run = 0
    try:
        with acquire_lock(lock_path, blocking=False):
            while not event.is_set():
                tick_mod.tick(checkpointer=checkpointer, **tick_kwargs)
                ticks_run += 1
                if max_ticks is not None and ticks_run >= max_ticks:
                    break
                event.wait(poll_interval)
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)
    return ticks_run
