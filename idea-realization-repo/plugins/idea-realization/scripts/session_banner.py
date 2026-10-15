# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Print the session banner: the resolved configuration a session starts from, and the mode menu.

A ``SessionStart`` hook runs this once per session. It prints, one line each:

- the repository root;
- the integration branch (``paths.py``) and the source it came from;
- the product checkout, or that it is not set on this machine;
- the developer handle (``identity.py``), or why it does not resolve;
- the demo date and the days left until it, and the code freeze date and the days left until it,
  from ``.idea-realization/project.yaml`` (``project.py``);
- the menu line ``Run /start to pick a mode (Planning, Implementing, Validating).``

A value that cannot be read is printed as ``(unavailable: <reason>)`` on its own line, and the
other lines still print. The banner never fails a session: every error, including a missing or
invalid configuration file, ends in exit 0 with a one-line note. It reads local files and runs
``git`` on this machine only; it makes no network call.

``--hook`` prints the banner as the JSON a Claude Code ``SessionStart`` hook returns: the banner as
``systemMessage``, which the person sees, and as ``additionalContext``, which the session's model
reads. Without it the banner is plain text.

Exit codes: always 0.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MENU = "Run /start to pick a mode (Planning, Implementing, Validating)."


def _one_line(error: BaseException) -> str:
    """An error's message on one line, so every banner entry stays one line."""
    return " ".join(str(error).split()) or type(error).__name__


def _days(day: str, today: datetime.date) -> str:
    """``<day> (<n> days left)``.

    A past day says how many days ago; an unparsed one is shown as is.
    """
    try:
        when = datetime.date.fromisoformat(str(day))
    except ValueError:
        return f"{day} (not a YYYY-MM-DD date)"
    left = (when - today).days
    if left > 0:
        return f"{when.isoformat()} ({left} day{'s' if left != 1 else ''} left)"
    if left == 0:
        return f"{when.isoformat()} (today)"
    return f"{when.isoformat()} ({-left} day{'s' if left != -1 else ''} ago)"


def _line(label: str, read: object) -> str:
    """``label: value``, or ``label: (unavailable: reason)`` when reading the value raised."""
    try:
        value = read() if callable(read) else read
    except Exception as error:  # noqa: BLE001 - the banner reports, it never fails
        value = f"(unavailable: {_one_line(error)})"
    return f"{label}: {value}"


def banner(root_flag: str | None, today: datetime.date) -> list[str]:
    """Every banner line. Raises only when the plugin's own modules cannot be imported."""
    import identity
    import paths
    import project

    config = paths.resolve({"root": root_flag})
    lines = [f"idea-realization session: {config.root}"]

    def branch() -> str:
        return f"{config.text('integration_branch')} (from {config.sources['integration_branch']})"

    def product_root() -> str:
        found = config.product_root()
        return str(found) if found is not None else "not set on this machine"

    def record() -> dict:
        found = project.read_record(config.root)
        if found is None:
            raise FileNotFoundError(f"{project.RECORD.as_posix()} does not exist")
        return found

    def demo() -> str:
        return _days(record()["demo"]["date"], today)

    def freeze() -> str:
        return _days(record()["demo"]["freeze"], today)

    lines += [_line("integration branch", branch), _line("product root", product_root),
              _line("handle", lambda: identity.handle(config)),
              _line("demo date", demo), _line("code freeze", freeze), MENU]
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the resolved configuration and the mode menu at session start.")
    parser.add_argument("--root", help="repository root (env IDEA_REALIZATION_ROOT, then "
                                       "CLAUDE_PROJECT_DIR; default: git top level)")
    parser.add_argument("--hook", action="store_true",
                        help="print the SessionStart hook JSON instead of plain text")
    parser.add_argument("--today", help="the date to count days from, YYYY-MM-DD (default: today)")
    try:
        args = parser.parse_args(argv)
    except SystemExit:  # --help, or a usage error argparse has already reported
        return 0
    try:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
        lines = banner(args.root, today)
    except BaseException as error:  # noqa: BLE001 - a session must start whatever happens here
        lines = [f"idea-realization session banner unavailable: {type(error).__name__}: "
                 f"{_one_line(error)}",
                 MENU]
    text = "\n".join(lines)
    if args.hook:
        print(json.dumps({"systemMessage": text,
                          "hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": text}}))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
