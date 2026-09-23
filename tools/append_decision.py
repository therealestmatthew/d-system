#!/usr/bin/env python3
"""The only sanctioned writer for `_data/gate-decisions.jsonl`, the decision inbox.

Thin CLI over `src.orchestrator.decisions.decide()`, validated against
`schemas/gate-decision.schema.json` before the line is appended. `src.orchestrator.tick`'s
`advance()` reads this file (via `decisions.load_decisions`/`latest_for_gate`) to find a
decision waiting to resume an interrupted gate. See `src/orchestrator/decisions.py` for the
dedup-key rationale.

Usage:
    uv run python tools/append_decision.py decide <run_id> --gate dispatch-authorization \\
        --decision approve --by repository-owner
    uv run python tools/append_decision.py decide <run_id> --gate G2 --decision amend \\
        --by repository-owner --notes "reordered next_up: phase-x before phase-y"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.orchestrator.decisions import LOG, DecisionError, decide  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Append a decision to the gate decision inbox. decision_seq is generated, "
            "never supplied."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_decide = sub.add_parser("decide", help="record an owner decision resuming a gate")
    p_decide.add_argument("run_id")
    p_decide.add_argument("--gate", required=True)
    p_decide.add_argument("--decision", required=True, choices=["approve", "reject", "amend"])
    p_decide.add_argument("--by", required=True, dest="decided_by")
    p_decide.add_argument("--notes")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        event = decide(args.run_id, args.gate, args.decision, args.decided_by, args.notes, log=LOG)
    except DecisionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"{event['decision']} {event['run_id']}/{event['gate']}#{event['decision_seq']} "
        f"at {event['at']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
