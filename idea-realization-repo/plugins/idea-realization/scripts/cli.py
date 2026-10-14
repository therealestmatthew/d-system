# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Run one feature command, such as ``ready``, ``next-code`` or ``catalog``.

Each feature contributes ``COMMANDS`` from ``scripts/checks/<feature>.py``; the command receives
every argument after its name. Exit 2 when the command is unknown.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence

from checks import features

Command = tuple[str, Callable[[list[str]], int]]


def commands() -> dict[str, Command]:
    table: dict[str, Command] = {}
    for name, module in features().items():
        for command, entry in getattr(module, "COMMANDS", {}).items():
            if command in table:
                raise SystemExit(f"command {command!r} is defined twice (second: {name})")
            table[command] = entry
    return table


def usage(table: dict[str, Command]) -> str:
    lines = ["usage: cli.py <command> [arguments]", "", "commands:"]
    lines += [f"  {name:<14} {help_text}" for name, (help_text, _) in sorted(table.items())]
    if not table:
        lines.append("  (none installed)")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    table = commands()
    if not args or args[0] in {"-h", "--help"}:
        print(usage(table))
        return 0
    if args[0] not in table:
        print(f"unknown command: {args[0]}\n\n{usage(table)}", file=sys.stderr)
        return 2
    return table[args[0]][1](args[1:])


if __name__ == "__main__":
    raise SystemExit(main())
