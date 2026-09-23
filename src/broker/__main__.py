"""CLI surface for the capability and approval broker.

Run: uv run python -m src.broker <subcommand>

Subcommands:

- `check` — the tool-boundary call. Reads a tool-call payload as JSON from stdin (at minimum a
  `capability` field; any other fields, such as `tool_name` or `tool_input`, are carried into the
  audit record as context but play no part in the decision). Denials are supplied on the command
  line with repeatable `--deny CAPABILITY` flags — this CLI owns no built-in policy, matching
  `enforcement.check()`'s permissive default. Prints the decision as JSON to stdout. Exit code 0
  means the capability is allowed; exit code 2 means it is denied. This is the exit-code contract
  a process boundary (for example a pre-execution hook) blocks a call on.
- `request` — record a new approval request (`--scope`, `--reason`, `--expires` required).
- `list-pending` — print every pending (undecided, unexpired) approval as JSON.
- `decide` — record a decision (`--id`, `--decision approved|denied`, `--by`) against an
  approval. Fails if the approval already has a decision or has expired.

Every subcommand takes `--state-dir` for where the audit log and approval log live; it defaults
to `_working/broker` (gitignored — see `src/broker/enforcement.py`). Tests never rely on this
default; they always pass their own `tmp_path`.

Nothing in this repository invokes this module automatically yet. See the docstring in
`src/broker/__init__.py` for the intended wiring (a Claude Code `PreToolUse` hook piping the
tool-call JSON to `check` on stdin) and why building that wiring is outside this phase's
declared deliverables (`src/broker/`, `test/test_broker.py`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.broker import approvals, enforcement


def _cmd_check(args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        print(f"invalid JSON on stdin: {exc}", file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print("tool-call payload on stdin must be a JSON object", file=sys.stderr)
        return 1

    capability = payload.get("capability") or args.capability
    if not capability:
        print(
            "no capability named: pass --capability, or a 'capability' field in the stdin payload",
            file=sys.stderr,
        )
        return 1

    decision = enforcement.check(
        capability,
        denied=args.deny,
        state_dir=Path(args.state_dir),
        context=payload,
    )
    print(json.dumps(decision.to_dict(), sort_keys=True))
    return 0 if decision.allowed else 2


def _cmd_request(args: argparse.Namespace) -> int:
    try:
        approval = approvals.request(
            args.scope,
            args.reason,
            args.expires,
            state_dir=Path(args.state_dir),
        )
    except approvals.ApprovalError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(approval.to_dict(), sort_keys=True))
    return 0


def _cmd_list_pending(args: argparse.Namespace) -> int:
    rows = approvals.pending(state_dir=Path(args.state_dir))
    print(json.dumps([row.to_dict() for row in rows], sort_keys=True))
    return 0


def _cmd_decide(args: argparse.Namespace) -> int:
    try:
        approval = approvals.decide(
            args.id,
            args.decision,
            decided_by=args.by,
            state_dir=Path(args.state_dir),
        )
    except approvals.ApprovalError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(approval.to_dict(), sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m src.broker", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Decide whether a capability may proceed.")
    check.add_argument("--capability", default=None, help="Capability name, if not in stdin JSON.")
    check.add_argument(
        "--deny",
        action="append",
        default=[],
        help="A denied capability name. Repeatable. Nothing is denied unless named here.",
    )
    check.add_argument("--state-dir", default=str(enforcement.DEFAULT_STATE_DIR))
    check.set_defaults(func=_cmd_check)

    req = sub.add_parser("request", help="Record a new approval request.")
    req.add_argument("--scope", required=True)
    req.add_argument("--reason", required=True)
    req.add_argument("--expires", required=True, help="ISO 8601 expiry timestamp.")
    req.add_argument("--state-dir", default=str(enforcement.DEFAULT_STATE_DIR))
    req.set_defaults(func=_cmd_request)

    listp = sub.add_parser("list-pending", help="List pending, unexpired approval requests.")
    listp.add_argument("--state-dir", default=str(enforcement.DEFAULT_STATE_DIR))
    listp.set_defaults(func=_cmd_list_pending)

    dec = sub.add_parser("decide", help="Record a decision against an approval request.")
    dec.add_argument("--id", required=True, dest="id")
    dec.add_argument("--decision", required=True, choices=["approved", "denied"])
    dec.add_argument("--by", required=True, help="Who recorded the decision.")
    dec.add_argument("--state-dir", default=str(enforcement.DEFAULT_STATE_DIR))
    dec.set_defaults(func=_cmd_decide)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
