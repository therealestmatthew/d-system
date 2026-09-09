#!/usr/bin/env python3
"""Single-command CLI quick-capture, and the inbox scanner — REQ-002 R5, ADR-007 section 2.

Writes raw records only; no interpretation, no structuring (phase-cap-05 does that). A
capture landing here can never be lost to a later structuring bug, because it is stored
before structuring ever runs.

Usage:
    uv run python tools/capture.py "Call John about the Q3 deliverable by Friday."
    echo "Call John about the Q3 deliverable by Friday." | uv run python tools/capture.py
    uv run python tools/capture.py --inbox

The text is a single positional argument, or stdin when omitted — never both. Piping
through stdin is the safer route for anything containing a backtick, `$(`, or a quote the
calling shell might evaluate; see `tools/append_idea.py`'s docstring for the incident that
made that lesson permanent here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.capture.raw import (  # noqa: E402
    INBOX_DIR,
    RAW_DIR,
    CaptureError,
    scan_inbox,
    write_raw_capture,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write one raw capture record, or drain the inbox into raw records."
    )
    parser.add_argument(
        "text", nargs="?", default=None, help="the capture text; omit to read from stdin"
    )
    parser.add_argument(
        "--inbox",
        action="store_true",
        help="scan _capture/inbox/ and convert every file there instead of taking text",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.inbox:
        if args.text is not None:
            print("error: --inbox takes no text argument", file=sys.stderr)
            return 1
        records, failures = scan_inbox(inbox_dir=INBOX_DIR, raw_dir=RAW_DIR)
        for record in records:
            print(f"captured {record['id']} from {record['source_path']}")
        for path, message in failures:
            print(f"error: {path}: {message}", file=sys.stderr)
        if not records and not failures:
            print("inbox empty — nothing to capture")
        return 1 if failures else 0

    content = args.text if args.text is not None else sys.stdin.read()
    if not content.strip():
        print(
            "error: no capture text given — pass it as an argument or pipe it on stdin",
            file=sys.stderr,
        )
        return 1

    try:
        record = write_raw_capture(content, channel="cli", raw_dir=RAW_DIR)
    except CaptureError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"captured {record['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
