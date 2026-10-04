#!/usr/bin/env python3
"""Refuse three patterns on lines a branch adds (REQ-028 R08).

A builder runs it before `READY` over the branch's own commits (GOV-017's merge gate, PROMPT-037
item 4):

    uv run python tools/check_diff_patterns.py dev..HEAD

For every Python file the range adds or modifies, it reads the file as it stands at `<head>` and
reports each of these whose line is an added line of the diff:

- a `# type: ignore` comment whose code list is not exactly `[import-untyped]` (a bare ignore, a
  different code, or more than one code);
- a `cast(Any, ...)` call (`cast` or `typing.cast`; `Any` or `typing.Any`);
- an `except` clause that is bare or catches `Exception` or `BaseException` (alone or in a tuple)
  and whose body is only `pass`. The line reported is the `except` line, so an `except` that was
  already there is not reported when only its body changes.

Comments are found with `tokenize` and calls and handlers with `ast`, so the same text inside a
string literal, or in a Markdown file, is never reported. Unchanged context lines and removed lines
are never reported. An `except` naming a specific exception type with a `pass` body is not
reported.

- exit 0: none of the three patterns on an added line;
- exit 1: one or more findings, each printed as `path:line: <pattern>: <the line>`;
- exit 2: the range is malformed, `git` failed, or a changed file does not parse at `<head>`.

A nonzero result blocks the merge unless the owner signs off naming the lines it accepts
(REQ-028 R10, PLAN-045 D9).

See PLAN-045 D7 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-03.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).parent.parent

IGNORE = re.compile(r"#\s*type:\s*ignore(?:\[(?P<codes>[^\]]*)\])?")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@")
BROAD = {"Exception", "BaseException"}


class CheckError(Exception):
    """The check could not run: a bad range, a git failure, or a file that does not parse."""


def git(root: Path, *args: str) -> str:
    try:
        done = subprocess.run(
            ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise CheckError(f"git {' '.join(args)}: {detail.strip()}") from None
    return done.stdout


def added_lines(root: Path, base: str, head: str) -> dict[str, set[int]]:
    """Map each added or modified Python file to the line numbers the range adds to it."""
    diff = git(
        root, "diff", "--unified=0", "--no-color", "--no-ext-diff", "--diff-filter=AMR",
        f"{base}..{head}", "--", "*.py",
    )
    found: dict[str, set[int]] = {}
    path: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            target = line[4:]
            path = target[2:] if target.startswith("b/") else None
            if path is not None:
                found.setdefault(path, set())
        elif path is not None and (match := HUNK.match(line)):
            start = int(match["start"])
            count = int(match["count"]) if match["count"] is not None else 1
            found[path].update(range(start, start + count))
    return {key: lines for key, lines in found.items() if lines}


def _names_any(node: ast.expr) -> bool:
    return (isinstance(node, ast.Name) and node.id == "Any") or (
        isinstance(node, ast.Attribute) and node.attr == "Any"
    )


def _is_cast(node: ast.Call) -> bool:
    func = node.func
    named = (isinstance(func, ast.Name) and func.id == "cast") or (
        isinstance(func, ast.Attribute) and func.attr == "cast"
    )
    return named and bool(node.args) and _names_any(node.args[0])


def _broad(handler: ast.ExceptHandler) -> bool:
    caught = handler.type
    if caught is None:
        return True
    names = caught.elts if isinstance(caught, ast.Tuple) else [caught]
    return any(
        (isinstance(n, ast.Name) and n.id in BROAD)
        or (isinstance(n, ast.Attribute) and n.attr in BROAD)
        for n in names
    )


def findings_in(path: str, source: str, lines: set[int]) -> list[tuple[int, str]]:
    """The patterns on the given lines of one file's source, as (line, pattern) pairs."""
    try:
        tree = ast.parse(source, filename=path)
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (SyntaxError, tokenize.TokenError) as exc:
        raise CheckError(f"{path}: does not parse at head: {exc}") from None
    found: list[tuple[int, str]] = []
    for token in tokens:
        if token.type != tokenize.COMMENT or token.start[0] not in lines:
            continue
        for match in IGNORE.finditer(token.string):
            codes = match["codes"]
            if codes is None or [c.strip() for c in codes.split(",")] != ["import-untyped"]:
                found.append((token.start[0], "type-ignore"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.lineno in lines and _is_cast(node):
            found.append((node.lineno, "cast-any"))
        if (
            isinstance(node, ast.ExceptHandler)
            and node.lineno in lines
            and _broad(node)
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Pass)
        ):
            found.append((node.lineno, "except-pass"))
    return sorted(set(found))


def check(root: Path, base: str, head: str) -> list[str]:
    """Every finding in the range, as printable `path:line: pattern: text` lines."""
    report: list[str] = []
    for path, lines in sorted(added_lines(root, base, head).items()):
        source = git(root, "show", f"{head}:{path}")
        text = source.splitlines()
        for number, pattern in findings_in(path, source, lines):
            report.append(f"{path}:{number}: {pattern}: {text[number - 1].strip()}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report added type-ignores, cast(Any, ...) and broad except/pass in a range"
    )
    parser.add_argument("range", help="The commit range, as <base>..<head>")
    parser.add_argument("--repo", type=Path, default=ROOT, help="Repository to read")
    args = parser.parse_args(argv)
    base, sep, head = args.range.partition("..")
    if not sep or not base or not head or head.startswith("."):
        print(f"ERROR range must be <base>..<head>, got {args.range!r}", file=sys.stderr)
        return 2
    try:
        report = check(args.repo, base, head)
    except CheckError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if not report:
        print(
            "Diff patterns OK: no added type-ignore, cast(Any, or broad except/pass "
            f"in {args.range}."
        )
        return 0
    print(f"{len(report)} added lines match a refused pattern in {args.range}:")
    for line in report:
        print(f"  {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
