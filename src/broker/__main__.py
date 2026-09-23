"""CLI surface for the capability and approval broker.

Run: uv run python -m src.broker <subcommand>

Subcommands:

- `check` — the tool-boundary call, and the one a `PreToolUse` hook runs. `--capability NAME`
  names the capability this call is checking; a real `PreToolUse` payload has no `capability`
  field of its own, so the supported wiring is one hook entry per capability, with the hook's
  command naming the capability explicitly (see `src/broker/__init__.py` for the exact form).
  Reads the raw hook payload as JSON from stdin — `tool_name`, `tool_input` and any other fields
  are carried into the audit record as `context`, and a `capability` field in that JSON is used
  only if `--capability` is not given (`--capability` takes precedence). Denials are supplied on
  the command line with repeatable `--deny CAPABILITY` flags — this CLI owns no built-in policy,
  matching `enforcement.check()`'s permissive default. Capability names are normalised
  (whitespace-stripped, case-folded) before comparison. Prints the decision as JSON to stdout.

  **Exit code contract, and it is fail-closed on every path:** exit 0 means the capability was
  evaluated and allowed. Exit 2 means the call is blocked — either because the capability was
  evaluated and denied, or because this command could not evaluate the call at all (no capability
  named, malformed JSON on stdin, a `--state-dir` that could not be written to, or any other
  unexpected error). A decision the broker cannot make is a refusal, not a pass: there is no path
  through this subcommand that exits anything other than 0 or 2. Every refusal, including a
  refusal caused by a failure to evaluate the call, is recorded to the audit log wherever the log
  itself is writable, tagged with a short reason (`no-capability`, `malformed-payload`,
  `audit-write-failed`, `unexpected-error`, `interrupted`, or the ordinary `denied by configured
  policy`).

  The exit code is decided before anything is written to stdout or stderr, and writing the output
  is never allowed to change it: a broken pipe, a closed stdout, or any other `OSError` while
  printing the decision is swallowed, and this command still exits 0 or 2 as already decided. A
  `BrokenPipeError` specifically also gets its underlying stream redirected to `os.devnull`, so
  the interpreter's own shutdown-time flush of the broken stream cannot fail again and override
  the exit code with Python's own broken-pipe exit status (observed as 120 before this fix; see
  `docs/03-sessions/` for the phase's fix-cycle-2 session record). `KeyboardInterrupt` during
  `check` is treated the same as any other failure to evaluate the call: exit 2. `SIGTERM` is
  handled from the moment `check` starts and exits the process with code 2 immediately (via
  `os._exit`, bypassing any further Python-level flushing that could change the code). `SIGKILL`
  cannot be handled by any process, this one included, and simply kills the process outright —
  that is not a refusal and nothing here changes that; a caller relying on `check` for a real
  denial must not treat an unexplained process death as equivalent to a recorded refusal.
- `request` — record a new approval request (`--scope`, `--reason`, `--expires` required).
- `list-pending` — print every pending (undecided, unexpired) approval as JSON.
- `decide` — record a decision (`--id`, `--decision approved|denied`, `--by`) against an
  approval. Fails if the approval already has a decision or has expired.

Every subcommand takes `--state-dir` for where the audit log and approval log live; it defaults
to `_working/broker` (gitignored — see `src/broker/enforcement.py`). Tests never rely on this
default; they always pass their own `tmp_path`.

Nothing in this repository invokes this module automatically yet. See the docstring in
`src/broker/__init__.py` for the intended wiring — a `PreToolUse` hook entry per capability, with
`--capability` naming the capability and the hook's matcher selecting which tools it applies to —
and why building that wiring (a `.claude/settings.json` change) is outside this phase's declared
deliverables (`src/broker/`, `test/test_broker.py`).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from pathlib import Path
from typing import IO

from src.broker import approvals, enforcement


def _install_sigterm_fail_closed() -> None:
    """SIGTERM received at any point during `check` exits the process with code 2, immediately.

    Uses `os._exit()` rather than raising or calling `sys.exit()`: a normal exit still runs
    Python's interpreter-shutdown machinery (buffered-stream flushing, `atexit` callbacks), any
    of which failing could change the process's final exit code the way a broken stdout did
    before this fix (F6). `os._exit()` terminates immediately with exactly the code given, and
    nothing downstream of the signal can override it.

    Best-effort: `signal.signal()` raises `ValueError` off the main thread, which this catches
    and ignores rather than letting installation itself become a new failure mode. `SIGKILL`
    cannot be caught by any process — no handler here or anywhere else changes that; a `SIGKILL`
    is not a refusal, it is the process simply ceasing to exist, and a caller must not treat the
    two as equivalent.
    """
    try:
        signal.signal(signal.SIGTERM, lambda signum, frame: os._exit(2))
    except (ValueError, OSError):
        pass


def _write_best_effort(stream: IO[str], text: str) -> None:
    """Write one line to `stream`, swallowing any `OSError` — a broken pipe, a closed file
    descriptor, anything else that makes the write itself fail. Callers use this only after the
    exit code has already been decided, so a failed write never changes what this process exits
    with (F6)."""
    try:
        stream.write(text + "\n")
        stream.flush()
    except BrokenPipeError:
        # A later, interpreter-shutdown flush of the same broken stream would raise again and
        # Python overrides the process exit code to 120 when that happens during shutdown.
        # Redirecting the underlying file descriptor to devnull makes that final flush succeed
        # silently, so the exit code this function's caller already decided on is what the
        # process actually exits with.
        try:
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            try:
                os.dup2(devnull_fd, stream.fileno())
            finally:
                os.close(devnull_fd)
        except OSError:
            pass
    except OSError:
        pass


def _cmd_check(args: argparse.Namespace) -> int:
    """The tool-boundary call. Fail-closed: every path through this function returns 0 (the
    capability was evaluated and allowed) or 2 (the call is blocked — evaluated and denied, or
    not evaluable at all, or interrupted). There is no path that returns anything else.

    The exit code is fully decided before any output is attempted (F6): a failure to write the
    decision to stdout, or the refusal message to stderr, never changes the code this function
    returns. `KeyboardInterrupt` during evaluation is caught and treated as a refusal, same as
    any other failure to evaluate the call. `SIGTERM` is handled separately, from the moment this
    function starts (`_install_sigterm_fail_closed`), and exits the process directly rather than
    returning through this function at all.
    """
    _install_sigterm_fail_closed()

    state_dir = Path(args.state_dir)
    payload: dict[str, object] = {}
    capability: str | None = None
    reason = "unexpected-error"
    stderr_message: str | None = None
    decision: enforcement.Decision | None = None

    try:
        raw = sys.stdin.read()
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            reason = "malformed-payload"
            raise ValueError(f"invalid JSON on stdin: {exc}") from exc
        if not isinstance(parsed, dict):
            reason = "malformed-payload"
            raise ValueError("tool-call payload on stdin must be a JSON object")
        payload = parsed

        capability = args.capability or payload.get("capability")
        if not capability:
            reason = "no-capability"
            raise ValueError(
                "no capability named: pass --capability (the supported PreToolUse wiring), "
                "or a 'capability' field in the stdin payload"
            )

        try:
            decision = enforcement.check(
                capability,
                denied=args.deny,
                state_dir=state_dir,
                context=payload,
            )
        except OSError as exc:
            reason = "audit-write-failed"
            raise ValueError(f"could not write the audit record: {exc}") from exc
    except KeyboardInterrupt:
        reason = "interrupted"
        stderr_message = f"denied ({reason}): interrupted"
    except Exception as exc:  # fail closed: any error here is a refusal, never a silent pass
        stderr_message = f"denied ({reason}): {exc}"

    if stderr_message is not None:
        # The decision could not be evaluated at all: this is always a refusal, and the exit
        # code is fixed at 2 before anything is written.
        exit_code = 2
        enforcement.record_refusal(
            reason=reason,
            capability=capability,
            state_dir=state_dir,
            context=payload,
        )
        _write_best_effort(sys.stderr, stderr_message)
        return exit_code

    assert decision is not None  # the only way past the try/except above without an exception
    exit_code = 0 if decision.allowed else 2
    _write_best_effort(sys.stdout, json.dumps(decision.to_dict(), sort_keys=True))
    return exit_code


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
    check.add_argument(
        "--capability",
        default=None,
        help="Capability name for this call. Takes precedence over a 'capability' field in the "
        "stdin payload; a real PreToolUse payload never has one, so this is the supported wiring.",
    )
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
