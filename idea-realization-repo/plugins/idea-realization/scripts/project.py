# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""What the whole team shares about this control repository, and the check that the checkout is it.

``.idea-realization/project.yaml`` is tracked (``schemas/project.schema.json``)::

    schema_version: 1
    control:
      integration_branch: dev
      remote: <git URL of this control repository>   # optional
      github: <org>/<repo>                           # optional
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

``control.integration_branch``, ``aws.region``, ``control.remote`` and ``control.github`` feed the
``integration_branch``, ``aws_region``, ``control_remote`` and ``control_github`` keys through
``paths.py``; ``show`` prints every value here, then the resolved repository keys and where each
came from. A value that starts with ``REPLACE-WITH-`` is a placeholder and counts as unset.

The repository URL may name a confidential organization, so a team can leave ``control.remote``
and ``control.github`` out of this file and set ``control_remote`` and ``control_github`` in each
machine's untracked ``.idea-realization/local.yaml`` (or ``IDEA_REALIZATION_CONTROL_REMOTE``),
which take precedence over this file.

``show`` and ``verify`` both compare the control checkout's ``origin`` with the resolved
``control_remote`` and exit 1 when they differ, so a session cannot record work in the wrong
repository. While ``control_remote`` is unset the comparison is skipped with a note naming
``local.yaml``. ``check.py`` and ``doctor.py`` run the same comparison.
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


def control_origin(config: paths.Config) -> tuple[str | None, str | None]:
    """``(problem, note)`` for the control checkout's ``origin`` against ``control_remote``.

    ``(None, None)`` when there is no ``project.yaml`` and no ``control_remote``; a note alone when
    the comparison is skipped or passes; a problem when the origin is missing or names another
    repository."""
    root = config.root
    remote = config.text("control_remote")
    if not remote:
        if read_record(root) is None:
            return None, None
        return None, ("not compared: control_remote is not set on this machine; set it in "
                      f"{paths.LOCAL_RECORD.as_posix()} (or IDEA_REALIZATION_CONTROL_REMOTE)")
    named = f"control_remote (from {config.sources.get('control_remote', '?')}) is {remote}"
    found = product.origin(root)
    if not found:
        return f"{root} has no origin remote; {named}", None
    if product.normalise_remote(found) != product.normalise_remote(remote):
        return (f"{root} has origin {found}, but {named}: this is not the control repository"), None
    return None, f"matches control_remote (from {config.sources.get('control_remote', '?')})"


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
    paths.add_arguments(parser, ["control_remote", "control_github"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    root = config.root
    record = read_record(root)
    if record is None:
        print(f"error: {RECORD.as_posix()} does not exist", file=sys.stderr)
        return 1
    if args.command == "show":
        for name, value in flatten(record):
            print(f"{name}: {value}" + ("  (placeholder: unset)" if is_placeholder(value) else ""))
        for name in ("control_remote", "control_github"):
            value = config.text(name)
            print(f"{name}: {value} (from {config.sources[name]})" if value
                  else f"{name}: (not set: {paths.LOCAL_RECORD.as_posix()})")
    problem, note = control_origin(config)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    print(f"origin: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
