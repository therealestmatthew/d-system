"""CLI surface for the orchestrator: `start`, `stop`, `status`, `tick`, `gate`,
`halt`, `resume-dispatch`.

Run: `uv run python -m src.orchestrator <subcommand>`

- `start` runs the daemon loop in the foreground (PLAN-039.01 section 2): takes the shared
  `flock` lock at `--lock`, ticks, waits `--poll-interval` seconds or until a wake, repeats,
  until `SIGTERM`/`SIGINT` asks it to stop after its current tick. Refuses to run in a linked
  worktree -- the primary checkout only. `src.orchestrator.daemon` owns the lock, the
  worktree check and the signal handling.
- `stop` sends `SIGTERM` to whatever process holds `--lock`'s lock and reports whether one
  was found; the daemon's own handler finishes its tick and releases the lock.
- `status` reports whether the lock is held and, if so, the holder's pid and start time.
- `tick` runs one call to `src.orchestrator.tick.tick()` against the tracked logs and the
  checkpoint store under `data/orchestrator/`, taking the same lock `start` does
  (non-blocking): a manual tick while the daemon is alive exits with "daemon holds the
  lock" rather than running concurrently (PLAN-039.01 section 2). `--dispatch` is the
  owner-initiated flag REQ-017 R01 requires before any gate resumes into a dispatch;
  omitting it still starts new runs and advances them to their gate, but never resumes one.
- `gate` records an owner decision (`--decision approve|reject|amend`) through
  `src.orchestrator.decisions.decide()` -- the sanctioned writer `tools/append_decision.py`
  also calls. The run resumes at the next `tick --dispatch`, not immediately; this command
  only writes the decision.
- `halt` / `resume-dispatch` operate the kill switch's flag file
  (`src.orchestrator.dispatch.HALT_FLAG`). Enforcement -- checking the flag immediately
  before every dispatch -- is `phase-irs-11`'s deliverable; these verbs ship with the
  skeleton per PLAN-039.01 section 9.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.orchestrator import daemon as daemon_mod
from src.orchestrator import decisions as decisions_mod
from src.orchestrator import dispatch as dispatch_mod
from src.orchestrator import tick as tick_mod

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHECKPOINT_DB = ROOT / "data" / "orchestrator" / "checkpoints.sqlite"


def _cmd_tick(args: argparse.Namespace) -> int:
    try:
        with daemon_mod.acquire_lock(args.lock, blocking=False):
            checkpointer = tick_mod.open_checkpoint_store(args.checkpoint_db)
            result = tick_mod.tick(
                idea_log=args.idea_log,
                run_log=args.run_log,
                decision_log=args.decision_log,
                watermark_path=args.watermark,
                checkpointer=checkpointer,
                dispatch=args.dispatch,
            )
    except daemon_mod.LockHeldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    if any(result["started"] + result["rekeyed"] + result["resumed"] + result["closed"]):
        print(
            "reminder: the run ledger and/or decision inbox have uncommitted appends "
            "(PLAN-039.01 section 5) -- commit at the next natural sitting.",
            file=sys.stderr,
        )
    return 0


def _cmd_start(args: argparse.Namespace) -> int:
    tick_kwargs = {
        "idea_log": args.idea_log,
        "run_log": args.run_log,
        "decision_log": args.decision_log,
        "watermark_path": args.watermark,
        "checkpoint_db": args.checkpoint_db,
        "dispatch": args.dispatch,
    }
    try:
        ticks_run = daemon_mod.run_daemon(
            lock_path=args.lock,
            poll_interval=args.poll_interval,
            tick_kwargs=tick_kwargs,
        )
    except daemon_mod.LinkedWorktreeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except daemon_mod.LockHeldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"daemon stopped after {ticks_run} tick(s)")
    return 0


def _cmd_stop(args: argparse.Namespace) -> int:
    result = daemon_mod.stop_daemon(args.lock)
    if not result["stopped"]:
        print(result["reason"])
        return 0
    print(f"stop signal sent to pid {result['pid']}")
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    info = daemon_mod.probe_lock(args.lock)
    if not info["running"]:
        print("no daemon running")
        return 0
    holder = info["holder"] or {}
    print(
        f"daemon running -- pid={holder.get('pid', '?')} "
        f"started_at={holder.get('started_at', '?')}"
    )
    return 0


def _cmd_gate(args: argparse.Namespace) -> int:
    try:
        event = decisions_mod.decide(
            args.run_id, args.gate, args.decision, args.by, args.notes, log=args.decision_log
        )
    except decisions_mod.DecisionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"{event['decision']} {event['run_id']}/{event['gate']}#{event['decision_seq']} "
        f"recorded -- resumes at the next tick --dispatch"
    )
    return 0


def _cmd_halt(args: argparse.Namespace) -> int:
    dispatch_mod.halt(args.halt_flag)
    print(f"halted -- {args.halt_flag} written")
    return 0


def _cmd_resume_dispatch(args: argparse.Namespace) -> int:
    dispatch_mod.resume_dispatch(args.halt_flag)
    print(f"resumed -- {args.halt_flag} removed")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Orchestrator CLI: start, stop, status, tick, gate, halt, resume-dispatch."
    )
    parser.add_argument("--idea-log", type=Path, default=tick_mod.DEFAULT_IDEA_LOG)
    parser.add_argument("--run-log", type=Path, default=tick_mod.DEFAULT_RUN_LOG)
    parser.add_argument("--decision-log", type=Path, default=tick_mod.DEFAULT_DECISION_LOG)
    parser.add_argument("--watermark", type=Path, default=tick_mod.DEFAULT_WATERMARK)
    parser.add_argument("--checkpoint-db", type=Path, default=DEFAULT_CHECKPOINT_DB)
    parser.add_argument("--halt-flag", type=Path, default=dispatch_mod.HALT_FLAG)
    parser.add_argument("--lock", type=Path, default=daemon_mod.DEFAULT_LOCK_PATH)

    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="run the daemon loop in the foreground")
    p_start.add_argument(
        "--dispatch", action="store_true",
        help="owner-initiated: allow this daemon's ticks to resume gates into a dispatch",
    )
    p_start.add_argument(
        "--poll-interval", type=float, default=daemon_mod.DEFAULT_POLL_INTERVAL,
        help="seconds to wait between ticks while idle",
    )

    sub.add_parser("stop", help="signal the running daemon to stop gracefully")
    sub.add_parser("status", help="report whether a daemon holds the lock")

    p_tick = sub.add_parser("tick", help="reconcile, start and advance runs -- one pass")
    p_tick.add_argument(
        "--dispatch", action="store_true",
        help="owner-initiated: allow this tick to resume gates, including into a dispatch",
    )

    p_gate = sub.add_parser("gate", help="record an owner decision resuming a gate")
    p_gate.add_argument("run_id")
    p_gate.add_argument("--gate", required=True)
    p_gate.add_argument("--decision", required=True, choices=["approve", "reject", "amend"])
    p_gate.add_argument("--by", required=True)
    p_gate.add_argument("--notes")

    sub.add_parser("halt", help="arm the kill switch")
    sub.add_parser("resume-dispatch", help="disarm the kill switch")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "start":
        return _cmd_start(args)
    if args.command == "stop":
        return _cmd_stop(args)
    if args.command == "status":
        return _cmd_status(args)
    if args.command == "tick":
        return _cmd_tick(args)
    if args.command == "gate":
        return _cmd_gate(args)
    if args.command == "halt":
        return _cmd_halt(args)
    return _cmd_resume_dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
