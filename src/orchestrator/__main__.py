"""CLI surface for the orchestrator skeleton: `tick`, `gate`, `halt`, `resume-dispatch`.

Run: `uv run python -m src.orchestrator <subcommand>`

`start`/`stop`/`status` and the `flock` lock are `phase-irs-16`'s deliverables, not this
phase's (PLAN-039.01 section 2) -- this module exposes only the four verbs that make sense
without a daemon process: a manual tick, recording a gate decision, and the kill switch.

- `tick` runs one call to `src.orchestrator.tick.tick()` against the tracked logs and the
  checkpoint store under `data/orchestrator/`. `--dispatch` is the owner-initiated flag
  REQ-017 R01 requires before any gate resumes into a dispatch; omitting it still starts new
  runs and advances them to their gate, but never resumes one.
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

from src.orchestrator import decisions as decisions_mod
from src.orchestrator import dispatch as dispatch_mod
from src.orchestrator import tick as tick_mod

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHECKPOINT_DB = ROOT / "data" / "orchestrator" / "checkpoints.sqlite"


def _cmd_tick(args: argparse.Namespace) -> int:
    checkpointer = tick_mod.open_checkpoint_store(args.checkpoint_db)
    result = tick_mod.tick(
        idea_log=args.idea_log,
        run_log=args.run_log,
        decision_log=args.decision_log,
        watermark_path=args.watermark,
        checkpointer=checkpointer,
        dispatch=args.dispatch,
    )
    print(json.dumps(result, indent=2))
    if any(result["started"] + result["rekeyed"] + result["resumed"] + result["closed"]):
        print(
            "reminder: the run ledger and/or decision inbox have uncommitted appends "
            "(PLAN-039.01 section 5) -- commit at the next natural sitting.",
            file=sys.stderr,
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
        description="Orchestrator skeleton CLI: tick, gate, halt, resume-dispatch."
    )
    parser.add_argument("--idea-log", type=Path, default=tick_mod.DEFAULT_IDEA_LOG)
    parser.add_argument("--run-log", type=Path, default=tick_mod.DEFAULT_RUN_LOG)
    parser.add_argument("--decision-log", type=Path, default=tick_mod.DEFAULT_DECISION_LOG)
    parser.add_argument("--watermark", type=Path, default=tick_mod.DEFAULT_WATERMARK)
    parser.add_argument("--checkpoint-db", type=Path, default=DEFAULT_CHECKPOINT_DB)
    parser.add_argument("--halt-flag", type=Path, default=dispatch_mod.HALT_FLAG)

    sub = parser.add_subparsers(dest="command", required=True)

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
    if args.command == "tick":
        return _cmd_tick(args)
    if args.command == "gate":
        return _cmd_gate(args)
    if args.command == "halt":
        return _cmd_halt(args)
    return _cmd_resume_dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
