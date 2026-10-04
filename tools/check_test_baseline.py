#!/usr/bin/env python3
"""Refuse a branch whose test run drops a test that passed on its base (REQ-028 R07).

A builder runs the suite twice before `READY` and compares the two JUnit XML reports
(GOV-017's merge gate, PROMPT-037 item 4):

    uv run pytest -q --junitxml=<base.xml>     # in a detached worktree of dev's tip
    uv run pytest -q --junitxml=<branch.xml>   # in the rebased branch worktree
    uv run python tools/check_test_baseline.py <base.xml> <branch.xml>

A test is identified by its JUnit `classname` and `name`, written `classname::name`, so a
parametrized case is its own test. Its outcome is `skipped` when the testcase carries a
`<skipped>` element, `failed` when it carries `<failure>` or `<error>`, and `passed` otherwise.

- exit 0: every test that passed in the base is present in the branch and not skipped there.
  Added tests, and tests already skipped or failing in the base, never fail the check.
- exit 1: one or more tests passed in the base and are missing from the branch or skipped there;
  each is printed with which of the two it is.
- exit 2: a report could not be read or parsed, or holds no testcase at all.

A test that passed in the base and fails in the branch is not this check's business: the
branch's own pytest run already fails on it. A nonzero result blocks the merge unless the owner
signs off naming the tests it accepts (REQ-028 R10, PLAN-045 D9).

See PLAN-045 D7 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-03.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PASSED = "passed"
SKIPPED = "skipped"
FAILED = "failed"


class ReportError(Exception):
    """A JUnit report that cannot be read, parsed or used."""


def outcomes(path: Path) -> dict[str, str]:
    """Map each test id in one JUnit XML report to `passed`, `skipped` or `failed`."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ReportError(f"{path}: {exc}") from None
    found: dict[str, str] = {}
    for case in root.iter("testcase"):
        test_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("skipped") is not None:
            found[test_id] = SKIPPED
        elif case.find("failure") is not None or case.find("error") is not None:
            found[test_id] = FAILED
        else:
            found[test_id] = PASSED
    if not found:
        raise ReportError(f"{path}: no testcase elements")
    return found


def compare(base: dict[str, str], branch: dict[str, str]) -> list[tuple[str, str]]:
    """Each test that passed in the base and is missing or skipped in the branch, sorted by id."""
    dropped: list[tuple[str, str]] = []
    for test_id, outcome in sorted(base.items()):
        if outcome != PASSED:
            continue
        if test_id not in branch:
            dropped.append((test_id, "missing"))
        elif branch[test_id] == SKIPPED:
            dropped.append((test_id, "skipped"))
    return dropped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare a base and a branch JUnit XML report; exit 1 on a dropped test"
    )
    parser.add_argument("base", type=Path, help="JUnit XML report of the base run (dev's tip)")
    parser.add_argument("branch", type=Path, help="JUnit XML report of the rebased branch run")
    args = parser.parse_args(argv)
    try:
        base = outcomes(args.base)
        branch = outcomes(args.branch)
    except ReportError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    dropped = compare(base, branch)
    passed = sum(1 for outcome in base.values() if outcome == PASSED)
    if not dropped:
        print(
            f"Test baseline OK: {passed} tests passed in the base; none is missing or skipped "
            f"in the branch ({len(branch)} tests in the branch, {len(base)} in the base)."
        )
        return 0
    print(f"{len(dropped)} tests passed in the base and are missing or skipped in the branch:")
    for test_id, how in dropped:
        print(f"  {how:<8} {test_id}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
