# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""What the whole team shares about this control repository, and the check that the checkout is it.

``.idea-realization/project.yaml`` is tracked (``schemas/project.schema.json``)::

    schema_version: 1
    control:
      remote: <git URL of this control repository>
      github: <org>/<repo>
      integration_branch: dev
    demo:
      date: 'YYYY-MM-DD'
      freeze: 'YYYY-MM-DD'
      tag_prefix: demo-
    urls:
      hackathon_portal: <URL>
      demo_app: <URL>
      team_chat: <URL>
    aws:
      region: <region>

``control.integration_branch`` and ``aws.region`` feed the ``integration_branch`` and
``aws_region`` keys through ``paths.py``; ``show`` prints every value here. A value that starts
with ``REPLACE-WITH-`` is a placeholder and counts as unset.

``show`` and ``verify`` both compare the control checkout's ``origin`` with ``control.remote`` and
exit 1 when they differ, so a session cannot record work in the wrong repository. While
``control.remote`` is a placeholder the comparison is skipped with a note. ``check.py`` and
``doctor.py`` run the same comparison.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paths  # noqa: E402
import product  # noqa: E402

RECORD = paths.PROJECT_RECORD


def read_record(root: Path) -> dict[str, Any] | None:
    """The tracked record, validated; None when this repository has none."""
    return paths.read_yaml_record(root / RECORD, "project.schema.json")


def is_placeholder(value: object) -> bool:
    return isinstance(value, str) and value.startswith(paths.PLACEHOLDER)


def control_origin(root: Path) -> tuple[str | None, str | None]:
    """``(problem, note)`` for the control checkout's ``origin`` against ``control.remote``.

    ``(None, None)`` when there is no record, a note alone when the comparison is skipped or
    passes, and a problem when the origin is missing or names another repository."""
    record = read_record(root)
    if record is None:
        return None, None
    remote = record["control"]["remote"]
    if is_placeholder(remote):
        return None, (f"not compared: {RECORD.as_posix()} control.remote is still a placeholder")
    found = product.origin(root)
    if not found:
        return f"{root} has no origin remote; {RECORD.as_posix()} control.remote is {remote}", None
    if product.normalise_remote(found) != product.normalise_remote(remote):
        return (f"{root} has origin {found}, but {RECORD.as_posix()} control.remote is {remote}: "
                "this is not the control repository"), None
    return None, f"matches {RECORD.as_posix()} control.remote"


def flatten(record: dict[str, Any], prefix: str = "") -> list[tuple[str, str]]:
    """``(dotted.key, value)`` for every value in the record, in file order."""
    rows: list[tuple[str, str]] = []
    for name, value in record.items():
        if isinstance(value, dict):
            rows += flatten(value, f"{prefix}{name}.")
        else:
            rows.append((f"{prefix}{name}", str(value)))
    return rows


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Show the shared project configuration and check the control origin.")
    parser.add_argument("command", choices=("show", "verify"))
    paths.add_arguments(parser, [])
    args = parser.parse_args(argv)
    root = paths.repository_root(args.root)
    record = read_record(root)
    if record is None:
        print(f"error: {RECORD.as_posix()} does not exist", file=sys.stderr)
        return 1
    if args.command == "show":
        for name, value in flatten(record):
            print(f"{name}: {value}" + ("  (placeholder: unset)" if is_placeholder(value) else ""))
    problem, note = control_origin(root)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    print(f"origin: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
