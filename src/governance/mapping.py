"""The Mapper role's only write path (GOV-014): depends_on/systems locks and the proposed
ordering it hands to Gate 3.

This module writes exactly two fields -- `depends_on` and `systems` -- for the named phases of
one approved plan into `docs/09-backlog/backlog.yaml`, runs the governance validator
(`src.governance`) against the result, and refuses the write (rolling the file back to its
original bytes) when that validator reports any error. It has no function that writes `next_up`,
or any field on any phase other than `depends_on`/`systems` for the phases it was explicitly
asked to lock.

The proposed ordering -- the artifact the owner ratifies at Gate 3 through phase-irs-04's `gate`
verb (built in phase-irs-14) -- is produced separately, as data conforming to the `ordering`
`$def` in `schemas/gate-decision.schema.json`. It is emitted to stdout or a caller-named path;
nothing in this module ever writes it into `backlog.yaml`'s `next_up`, which stays owner-reserved
(`ARCH-006`, `GOV-014`).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

#: {phase_id: {"depends_on": [phase_id, ...], "systems": [system_id, ...]}}
PhaseAssignments = dict[str, dict[str, list[str]]]

BACKLOG_RELATIVE = "docs/09-backlog/backlog.yaml"
_LOCKED_FIELDS = ("depends_on", "systems")


def _block_lines(field: str, values: list[str]) -> list[str]:
    lines = [f"  {field}:\n"]
    lines.extend(f"  - {value}\n" for value in values)
    return lines


def write_locks_text(text: str, assignments: PhaseAssignments) -> str:
    """Rewrite `backlog.yaml` text so each named phase's `depends_on`/`systems` block equals the
    list given in `assignments`. Every other line -- every other phase's blocks, `next_up`, and
    this file's own formatting everywhere else -- passes through unchanged, byte for byte.

    Modeled on `src.governance.backlog.backfill_ideas_text`'s line-surgery approach: drop an
    existing block and insert the replacement at the same position, rather than re-serialising
    the whole document (which would reflow every long string in it). A phase id not present in
    `assignments` is never touched, so a caller limited to "this plan's named phases" cannot
    reach any other phase's lock fields.
    """
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    phase: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("- id: "):
            phase = line[len("- id: ") :].strip()
        stripped = line.rstrip("\n")
        matched = None
        if phase in assignments:
            for candidate in _LOCKED_FIELDS:
                if stripped == f"  {candidate}:" or stripped.startswith(f"  {candidate}: "):
                    matched = candidate
                    break
        if matched is not None:
            output.extend(_block_lines(matched, assignments[phase][matched]))  # type: ignore[index]
            index += 1
            if stripped == f"  {matched}:":
                while index < len(lines) and lines[index].startswith("  - "):
                    index += 1
            continue
        output.append(line)
        index += 1
    return "".join(output)


def apply_phase_locks(
    root: Path,
    assignments: PhaseAssignments,
    validate: Callable[[Path], list[str]],
) -> tuple[int, list[str]]:
    """Write the named phases' `depends_on`/`systems`, validate, and roll back on any error.

    `validate(root)` is called once the candidate text has landed on disk and must return the
    governance validator's error list for the repository rooted at `root` -- empty means clean.
    In production that is `governance_errors`, below, which runs the real `src.governance`
    checks; tests inject a synthetic validator against a temp root, so no test run ever has to
    reach the real repository's own `docs/`, `schemas/` or `_data/` to exercise the rollback
    path. The write is atomic (temp file + `os.replace`) in both directions: landing the
    candidate and restoring the original.

    Never called with `"next_up"`, or any field name other than `depends_on`/`systems`, inside
    `assignments` -- `write_locks_text` only recognises those two field names, so there is no
    way to route a write to `next_up` through this function.
    """
    target = root / BACKLOG_RELATIVE
    original = target.read_text(encoding="utf-8")
    candidate = write_locks_text(original, assignments)
    if candidate == original:
        return 0, ["mapping: nothing to change"]
    _atomic_write(target, candidate)
    errors = validate(root)
    if errors:
        _atomic_write(target, original)
        return 1, [*errors, "mapping: governance check failed; backlog.yaml rolled back"]
    return 0, [f"mapping: wrote depends_on/systems for {', '.join(sorted(assignments))}"]


def _atomic_write(target: Path, text: str) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=".backlog-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, target)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def governance_errors(root: Path) -> list[str]:
    """Run the real governance validator (`src.governance`'s `audit` + `audit_backlog`) against
    the backlog currently on disk at `root`. Production use only -- tests supply their own
    `validate` callable instead of calling this against the real repository.
    """
    from src.governance.__main__ import audit, audit_backlog  # local: avoid import at module load

    errors, _warnings, result = audit(root)
    if errors:
        return errors
    backlog_errors, _catalog = audit_backlog(root, result)
    return backlog_errors


def build_ordering(entries: list[tuple[str, str]]) -> dict[str, list[dict[str, str]]]:
    """The proposed ordering document, as data conforming to the `ordering` `$def` in
    `schemas/gate-decision.schema.json`: `{"ordering": [{"phase": ..., "reason": ...}, ...]}`.

    `entries` is the mapper's own proposed position order, each paired with the prose reason it
    sits there -- this function does not decide the order or invent a reason; it only shapes
    the pairs it is given into the `$def`'s form.
    """
    return {"ordering": [{"phase": phase, "reason": reason} for phase, reason in entries]}


def ordering_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """The standalone `ordering` `$def`, pulled out of a loaded `gate-decision.schema.json`."""
    sub_schema: dict[str, Any] = schema["$defs"]["ordering"]
    return sub_schema


def validate_ordering(ordering: list[Any], schema: dict[str, Any]) -> list[str]:
    """Validate a bare ordering array (the `ordering` key's value) against the `ordering` `$def`
    of a loaded `gate-decision.schema.json` document. Returns one message per violation.
    """
    from jsonschema import Draft7Validator, FormatChecker  # type: ignore[import-untyped]

    sub_schema = dict(ordering_schema(schema))
    sub_schema["$defs"] = schema.get("$defs", {})
    validator = Draft7Validator(sub_schema, format_checker=FormatChecker())
    issues = list(validator.iter_errors(ordering))
    return [
        f"ordering:{'.'.join(map(str, issue.absolute_path))}: {issue.message}" for issue in issues
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI entry: write one plan's phase locks, then emit its proposed ordering.

    `--assignments` is a JSON file shaped `{phase_id: {"depends_on": [...], "systems": [...]}}`.
    `--ordering` is a JSON file shaped `[{"phase": ..., "reason": ...}, ...]` -- the mapper's own
    proposed position order with its reasons, decided before this runs. The ordering document is
    only emitted once the lock write passes governance; it is printed to stdout, or written to
    `--out` when given -- never into `backlog.yaml`.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignments", required=True, type=Path)
    parser.add_argument("--ordering", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="Write the ordering document here, not stdout.")
    args = parser.parse_args(argv)

    assignments: PhaseAssignments = json.loads(args.assignments.read_text(encoding="utf-8"))
    raw_entries = json.loads(args.ordering.read_text(encoding="utf-8"))
    entries = [(entry["phase"], entry["reason"]) for entry in raw_entries]

    code, lines = apply_phase_locks(ROOT, assignments, governance_errors)
    for line in lines:
        print(line, file=sys.stderr)
    if code != 0:
        return code

    doc = build_ordering(entries)
    schema = json.loads((ROOT / "schemas" / "gate-decision.schema.json").read_text())
    problems = validate_ordering(doc["ordering"], schema)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    text = json.dumps(doc, indent=2)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
