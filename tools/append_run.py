#!/usr/bin/env python3
"""The only sanctioned writer for `_data/runs.jsonl`, the orchestrator's run ledger.

Thin CLI over `src.orchestrator.ledger` — every subcommand below is that module's own
`start()`/`record()` functions, validated against `schemas/run.schema.json` before the line
is appended. `src.orchestrator.tick` calls those functions directly; this script exists so a
human can write the identical events by hand for a manual correction. See
`src/orchestrator/ledger.py` for the append-only-log rationale and the natural-key
idempotency guarantee `start` enforces.

Usage:
    uv run python tools/append_run.py start --kind intake --natural-key intake:000123 \\
        --ref idea_id=000123 --ref idea_status=open
    uv run python tools/append_run.py position <run_id> --position dispatch_gate
    uv run python tools/append_run.py dispatched <run_id> --role idea-triage --budget-cap 50000
    uv run python tools/append_run.py dispatch-result <run_id> --outcome ok \\
        --input-tokens 1200 --output-tokens 340
    uv run python tools/append_run.py gate-reached <run_id> --gate dispatch-authorization \\
        --position dispatch_gate
    uv run python tools/append_run.py gate-decided <run_id> --gate dispatch-authorization \\
        --decision approve
    uv run python tools/append_run.py parked <run_id> --reason "budget cap reached"
    uv run python tools/append_run.py abandoned <run_id> --reason "idea left open externally"
    uv run python tools/append_run.py terminal <run_id> --outcome complete --position done
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.orchestrator.ledger import LOG, LedgerError, record, start  # noqa: E402


def _parse_refs(pairs: list[str]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise LedgerError(f"--ref must be KEY=VALUE, got {pair!r}")
        key, _, value = pair.partition("=")
        refs[key] = value
    return refs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append an event to the run ledger. Timestamps and run_id are generated."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="open a new run under a natural key")
    p_start.add_argument(
        "--kind", required=True, choices=["intake", "batch", "unit", "realization"]
    )
    p_start.add_argument("--natural-key", required=True, dest="natural_key")
    p_start.add_argument(
        "--ref", action="append", default=[], metavar="KEY=VALUE",
        help="one reference field, repeatable",
    )

    p_position = sub.add_parser("position", help="record the thread reaching a named node")
    p_position.add_argument("run_id")
    p_position.add_argument("--position", required=True)

    p_dispatched = sub.add_parser("dispatched", help="record an agent invocation")
    p_dispatched.add_argument("run_id")
    p_dispatched.add_argument("--role", required=True)
    p_dispatched.add_argument("--budget-cap", required=True, type=int, dest="budget_cap")

    p_result = sub.add_parser("dispatch-result", help="record a dispatch's outcome and usage")
    p_result.add_argument("run_id")
    p_result.add_argument("--outcome", required=True)
    p_result.add_argument("--input-tokens", required=True, type=int, dest="input_tokens")
    p_result.add_argument("--output-tokens", required=True, type=int, dest="output_tokens")

    p_gate = sub.add_parser("gate-reached", help="record an interrupt() being hit")
    p_gate.add_argument("run_id")
    p_gate.add_argument("--gate", required=True)
    p_gate.add_argument("--position", required=True)

    p_decided = sub.add_parser("gate-decided", help="record a decision resuming a gate")
    p_decided.add_argument("run_id")
    p_decided.add_argument("--gate", required=True)
    p_decided.add_argument("--decision", required=True, choices=["approve", "reject", "amend"])

    p_parked = sub.add_parser(
        "parked", help="record the run waiting on something other than a gate"
    )
    p_parked.add_argument("run_id")
    p_parked.add_argument("--reason", required=True)

    p_abandoned = sub.add_parser("abandoned", help="record a thread being abandoned/re-keyed")
    p_abandoned.add_argument("run_id")
    p_abandoned.add_argument("--reason", required=True)

    p_terminal = sub.add_parser("terminal", help="record the run reaching its end state")
    p_terminal.add_argument("run_id")
    p_terminal.add_argument("--outcome", required=True)
    p_terminal.add_argument("--position", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "start":
            event = start(args.kind, args.natural_key, _parse_refs(args.ref), log=LOG)
        elif args.command == "position":
            event = record(args.run_id, "position", LOG, position=args.position)
        elif args.command == "dispatched":
            event = record(
                args.run_id, "dispatched", LOG, role=args.role, budget_cap=args.budget_cap
            )
        elif args.command == "dispatch-result":
            event = record(
                args.run_id,
                "dispatch_result",
                LOG,
                outcome=args.outcome,
                usage={
                    "input_tokens": args.input_tokens,
                    "output_tokens": args.output_tokens,
                },
            )
        elif args.command == "gate-reached":
            event = record(
                args.run_id, "gate_reached", LOG, gate=args.gate, position=args.position
            )
        elif args.command == "gate-decided":
            event = record(
                args.run_id, "gate_decided", LOG, gate=args.gate, decision=args.decision
            )
        elif args.command == "parked":
            event = record(args.run_id, "parked", LOG, reason=args.reason)
        elif args.command == "abandoned":
            event = record(args.run_id, "abandoned", LOG, reason=args.reason)
        else:
            event = record(
                args.run_id, "terminal", LOG, outcome=args.outcome, position=args.position
            )
    except LedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{event['event']} {event['run_id']} at {event['at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
