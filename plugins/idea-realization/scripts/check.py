# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Run every installed feature's check against the target repository.

Each feature contributes ``check(config)`` from ``scripts/checks/<feature>.py``. Exit 0 when every
check is clean, 1 when any reports a problem, 2 when a named feature has no check.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import paths
from checks import features


def main(argv: Sequence[str] | None = None) -> int:
    available = {name: module for name, module in features().items() if hasattr(module, "check")}
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--feature", action="append", default=None,
                        help=f"run only this feature's check; repeatable (available: "
                             f"{', '.join(available) or 'none'})")
    paths.add_arguments(parser)
    args = parser.parse_args(argv)
    selected = args.feature or list(available)
    unknown = [name for name in selected if name not in available]
    if unknown:
        print(f"no check for feature: {', '.join(unknown)}", file=sys.stderr)
        return 2
    config = paths.resolve(args)
    problems = 0
    for name in selected:
        found = available[name].check(config)
        for line in found:
            print(f"{name}: {line}")
        problems += len(found)
        if not found:
            print(f"{name}: OK")
    if not selected:
        print("no feature checks installed")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
