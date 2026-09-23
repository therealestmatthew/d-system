#!/usr/bin/env python3
"""Review staged captures and promote them into the source of truth — REQ-002 R11-R15.

Every subcommand is one owner decision, taken non-interactively so an agent can carry it
out in a conversation. Nothing prompts: an ambiguous or refused action exits non-zero and
says why, and writes nothing.

Usage:
    uv run python tools/review.py show
    uv run python tools/review.py promote --clean
    uv run python tools/review.py promote staged-... --set due_date=2026-10-01
    uv run python tools/review.py promote staged-... --keep-names
    uv run python tools/review.py create staged-... --set id=sam-lee
    uv run python tools/review.py discard staged-...
    uv run python tools/review.py correct commitment c-4 due_date 2026-10-08 --reason "moved"

`--set field=value` states a field value; the value is read as JSON when it parses
(`true`, `3`, `["a"]`, `null`) and as a plain string otherwise. A value the owner states is
the owner's word and no longer counts as assumed. `--keep-names` confirms that names in
`participant_names` or `decided_by_names` stay as plain text. Promotion writes to the data
root (`D_SYSTEM_DATA_ROOT`, else `_data/`); see `docs/08-governance/OPS-024-review.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.capture.promote import (  # noqa: E402
    PromotionError,
    correct,
    create_identity,
    discard,
    promote_clean,
    promote_one,
)
from src.capture.review import build_review, format_review  # noqa: E402


def _value(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _assignments(pairs: list[str] | None) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for pair in pairs or []:
        name, sep, text = pair.partition("=")
        if not sep or not name:
            raise PromotionError(f"--set expects field=value, not {pair!r}")
        values[name] = _value(text)
    return values


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review staged captures and promote them into the source of truth."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("show", help="list clean records and every flagged or held one")

    promote = commands.add_parser("promote", help="promote clean records, or one record")
    promote.add_argument("staged_id", nargs="?", help="promote: the staged record to promote")
    promote.add_argument("--clean", action="store_true", help="promote: every clean record")
    promote.add_argument(
        "--set", action="append", metavar="FIELD=VALUE", help="promote: state a field value"
    )
    promote.add_argument(
        "--keep-names", action="store_true", help="promote: keep *_names values as plain text"
    )

    create = commands.add_parser("create", help="create the person, project or tag held")
    create.add_argument("staged_id", help="create: the held person, project or tag record")
    create.add_argument(
        "--set", action="append", metavar="FIELD=VALUE", help="create: state a field value"
    )

    drop = commands.add_parser("discard", help="drop a staged record without promoting it")
    drop.add_argument("staged_id", help="discard: the staged record to drop")

    fix = commands.add_parser("correct", help="correct one field of a promoted record")
    fix.add_argument("record_type", help="correct: the record's schema, e.g. commitment")
    fix.add_argument("record_id", help="correct: the record's id, e.g. c-4")
    fix.add_argument("field", help="correct: the field to change")
    fix.add_argument("value", help="correct: the new value, read as JSON when it parses")
    fix.add_argument("--reason", default=None, help="correct: why, recorded in the log")
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "show":
        print(format_review(build_review()), end="")
        return 0

    if args.command == "promote":
        if args.clean == (args.staged_id is not None):
            raise PromotionError("give either --clean or one staged id")
        if args.clean:
            if args.set or args.keep_names:
                raise PromotionError("--set and --keep-names apply to one record, not --clean")
            result = promote_clean()
        else:
            result = promote_one(args.staged_id, _assignments(args.set), args.keep_names)
        for staged_id, target in result.promoted:
            print(f"promoted {staged_id} -> {target}")
        for staged_id, reason in result.skipped:
            print(f"left staged {staged_id}: {reason}")
        if not result.promoted and not result.skipped:
            print("nothing clean to promote")
        return 0

    if args.command == "create":
        print(f"created {create_identity(args.staged_id, _assignments(args.set))}")
        return 0

    if args.command == "discard":
        discard(args.staged_id)
        print(f"discarded {args.staged_id}")
        return 0

    entry = correct(args.record_type, args.record_id, args.field, _value(args.value), args.reason)
    print(
        f"corrected {entry['record_type']} {entry['record_id']} {entry['field']}: "
        f"{entry['previous']!r} -> {entry['new']!r}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return _run(_parser().parse_args(argv))
    except PromotionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
