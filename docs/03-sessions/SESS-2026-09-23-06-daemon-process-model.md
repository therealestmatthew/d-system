---
schema_version: 1
id: doc-session-daemon-process-model
code: SESS-2026-09-23-06
title: Daemon process model - lock, signal handling and start/stop/status
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems:
- sys-realization
depends_on:
- doc-irs-orchestrator-design
- doc-idea-realization-system-plan
---

# Daemon process model - lock, signal handling and start/stop/status

## Phase

`phase-irs-16`, claimed as `agent-coord` by Session 5 - Batch Runner during the overnight sprint of
2026-09-23 (claim commit `ef9a2a0`). The claim was pre-approved by the owner's overnight delegated
authority. It was worked on `agent/phase-irs-16` in `/code/d-system-worktrees/phase-irs-16`, per
`PLAN-039.01` §2 and §10. The owner-approved narrowed deliverables were `src/orchestrator/daemon.py`,
`src/orchestrator/__main__.py` (edit) and `test/test_daemon.py`, and the build stayed inside them.
`tick.py` did not change.

## What was built

- `src/orchestrator/daemon.py`: the lock, the linked-worktree check, the daemon loop, and the
  support functions for `stop` and `status`.
  - **Lock.** An exclusive `flock` on `data/orchestrator/lock`, non-blocking by default. While
    the lock is held, the file records `{"pid", "started_at"}`, and that record is informational
    only (PLAN-039.01 §2). `acquire_lock(blocking=True)` exists, but no CLI verb uses it.
  - **Stale-lock recovery.** The kernel releases a `flock` when the holder's descriptors close,
    so after a daemon is killed with SIGKILL, the next `start` or `tick` acquires the lock
    without any cleanup code.
  - **Signals.** SIGTERM and SIGINT set an event that the loop checks between ticks, so a tick
    in flight always finishes before the lock is released. Handlers are process-global, so
    there is one `run_daemon()` loop per process.
  - **Worktree refusal.** `start` refuses when `git rev-parse --git-common-dir` differs from
    `--git-dir`. The check can be injected only through `run_daemon(worktree_check=...)`. The
    CLI has no flag or environment variable that weakens it.
  - **Stop.** `stop` first probes the lock with a non-blocking `flock`. If the probe acquires
    the lock, no daemon is live, and no signal is sent. Only a lock that is actually held leads
    to a SIGTERM to the recorded pid. The window between the failed probe and `os.kill()` is
    documented in the docstring.
- `src/orchestrator/__main__.py`: new `start`, `stop` and `status` verbs and a `--lock` argument.
  A manual `tick` now takes the same lock and exits 1 with `daemon holds the lock` when the
  daemon holds it.
- `test/test_daemon.py`: 14 tests. The acceptance rows are process-level and use real
  subprocesses, `flock` and signals:
  - `test_manual_tick_exits_while_daemon_holds_the_lock` covers lock contention.
  - `test_stale_lock_recovers_after_forced_kill` covers SIGKILL followed by a tick with no
    manual cleanup.
  - `test_sigterm_stop_is_graceful` covers graceful shutdown.
  - `test_stop_daemon_never_signals_a_live_unrelated_process_named_by_a_stale_lock` and
    `test_stop_daemon_still_signals_the_real_holder_gracefully` came from fix cycle 1.

## Review

- **Validator: PASS** on both acceptance conditions, on real processes with no mocks.
- **Adversary (first pass).** The adversary confirmed that the acceptance genuinely holds. It
  checked this with mutations:
  - removing the tick's lock acquisition makes the contention test fail;
  - neutering the SIGTERM handler makes the graceful-stop test time out.

  It raised one MEDIUM finding: `stop` trusted the lock file's pid, so a reused pid could make
  `stop` signal an unrelated process. Fix cycle 1 of 2 fixed it with the lock probe described
  above. The LOW findings were that no test writes under the real `data/` (confirmed) and that
  the signal handlers are process-global (now documented).
- **Adversary (re-attack on fix commit `ef0baa9`).** The MEDIUM finding is fixed. Restoring the
  old `stop` body makes the unrelated-process test fail and actually signal the stand-in process,
  which reproduces the original bug. The probe is `LOCK_NB`, is released at once and never writes
  the file. No regressions: 14 of 14 pass. The remaining window between the failed probe and
  `os.kill()` was **downgraded to LOW and accepted**. It is the inherent race of any pid-file kill,
  and the risk is small because `stop` is single-instance and driven by the owner.

A creator attempt to add a test-only `--unsafe-skip-worktree-check` flag to `start` was blocked by
the harness safety classifier and dropped. The tests drive `run_daemon()` directly instead.

## Verification (post-rebase onto dev `806d3e2`, worktree)

- `uv run python -m src.governance`: exit 0, "Governance OK: 35 systems, 334 documents, 31 memories, 293 backlog phases"
- `uv run pytest`: exit 0, "982 passed, 1 skipped, 1 warning"
- `uv run ruff check src/ test/`: exit 0, "All checks passed!"
- `uv run mypy src/`: exit 0, "Success: no issues found in 45 source files"

In one full run before the rebase, `test_codes.py::test_catalog_flag_writes_committed_file`
failed, because the branch was behind dev and a dev-relative status-regression warning leaked into
`--catalog` stdout. The failure cleared after the rebase. It has been sent to Ideation as an idea.

## Not decided in this phase

An owner ruling of 2026-09-22 is recorded on idea `000334` (annotation `e18d7d9fb25b4f094`). It
says that whether to inject, adapt or recreate the Session Manager system in the automated system
"is decided in the later daemon-process phase (phase-irs-16)". That decision is not in this phase's
backlog scope or acceptance, and **it was not made or encoded here**. It is parked for the owner
under the overnight authority's §3.

## Evidence

Gitignored, in the primary checkout's `_working/build-batch-002/`: `phase-irs-16-build.md`,
`phase-irs-16-validation.md`, `phase-irs-16-adversary.md`, and `tracker.md`.
