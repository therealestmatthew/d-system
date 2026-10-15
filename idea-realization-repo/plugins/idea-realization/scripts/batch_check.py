# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Check batch compositions in the batches file against the backlog. Changes nothing.

A batch (``docs/batches.md``) is an owner-approved, ordered set of phases grouped into stages. The
batches file sits beside the backlog (``batches.yaml`` in the backlog's directory) and its shape is
``schemas/batches.schema.json``::

    schema_version: 1
    batches:
      - id: batch-login
        title: Login flow
        status: proposed          # proposed | approved | running | closed | superseded
        external_dependencies: [] # complete phases outside the batch that a member depends on
        stages:
          - phases: [<phase-id>, <phase-id>]
          - phases: [<phase-id>]

Structural rules, applied to every batch that is not ``closed`` or ``superseded``:

- batch ids are unique, and a ``superseded_by`` names a batch in the file;
- every phase id resolves in the backlog and appears once in the batch;
- the batch is dependency-closed: every ``depends_on`` edge of a member points to a member in an
  earlier stage, or to a complete phase outside the batch that ``external_dependencies`` lists;
- ``external_dependencies`` lists nothing that no member depends on;
- two phases in one stage do not collide: no shared system and no deliverable path that equals or
  contains the other's (``backlog.collisions``, the same function the claim check uses);
- every stage boundary follows from a real dependency edge (``backlog.dependency_closure``) or a
  real collision between a phase of the later stage and a phase of the stage before it.

Naming batch ids on the command line runs the composition check (``docs/batches.md`` section 3) on
those batches: the structural rules plus every member queued and unclaimed. Without ids, every
live batch gets the structural rules only, which is what ``check.py`` runs, because a running
batch's members are legitimately active or complete.

Exit codes: 0 when every checked batch is clean; 1 when any problem is found, one line each; 2 when
the batches file or the backlog cannot be read or is not valid, or a named batch does not exist.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from itertools import combinations
from pathlib import Path
from typing import Any

import documents
import paths
import yaml
from jsonschema import Draft7Validator, FormatChecker

import backlog

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "batches.schema.json"
FILENAME = "batches.yaml"
#: Batches kept as history: the backlog has moved on, so no rule is applied to them.
FINISHED = {"closed", "superseded"}


class Unreadable(ValueError):
    """The batches file or the backlog cannot be read or does not match its schema."""


def batches_path(config: paths.Config) -> Path:
    """The batches file: ``batches.yaml`` in the backlog's directory."""
    return config.path("backlog_path").parent / FILENAME


def _shown(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_batches(path: Path, shown: str) -> dict[str, Any]:
    """Read and schema-validate the batches file; ``Unreadable`` names every violation."""
    try:
        loaded = documents.load_yaml(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise Unreadable(f"{shown}: {exc}") from exc
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    issues = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(loaded))
    if issues:
        raise Unreadable("\n".join(
            f"{shown}:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
            for issue in issues))
    return dict(loaded)


def load_items(config: paths.Config) -> dict[str, Any]:
    """The backlog's phases by id, read and schema-validated the way the backlog check does."""
    from checks import backlog as backlog_feature

    errors, catalog = backlog_feature.load_catalog(config)
    if errors:
        raise Unreadable("\n".join(errors))
    return {item["id"]: item for item in catalog["items"]}


def _stage_of(batch: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    """Each member's 1-based stage, and a problem for every phase listed more than once."""
    name = batch["id"]
    position: dict[str, int] = {}
    errors: list[str] = []
    for index, stage in enumerate(batch["stages"], start=1):
        for key in stage["phases"]:
            if key in position:
                errors.append(f"{name}: {key} is listed twice (stages {position[key]} and "
                              f"{index})")
            else:
                position[key] = index
    return position, errors


def batch_problems(batch: dict[str, Any], items: dict[str, Any],
                   composition: bool = False) -> list[str]:
    """Every problem in one batch against the backlog's phases; empty means clean.

    ``composition`` adds the pre-run rule that every member is queued and unclaimed.
    """
    name = batch["id"]
    position, errors = _stage_of(batch)
    errors += [f"{name}: {key} does not resolve in the backlog"
               for key in position if key not in items]
    members = {key: items[key] for key in position if key in items}
    if composition:
        for key, item in members.items():
            if item["status"] != "queued":
                errors.append(f"{name}: {key} is {item['status']}, not queued")
            if item.get("agent"):
                errors.append(f"{name}: {key} is claimed by {item['agent']}")

    listed = set(batch.get("external_dependencies", []))
    needed: set[str] = set()
    for key, item in members.items():
        for dependency in item["depends_on"]:
            if dependency in position:
                if position[dependency] >= position[key]:
                    errors.append(
                        f"{name}: not dependency-closed: {key} (stage {position[key]}) depends "
                        f"on {dependency} (stage {position[dependency]}); a prerequisite must "
                        "sit in an earlier stage")
                continue
            needed.add(dependency)
            status = items[dependency]["status"] if dependency in items else "not in the backlog"
            if status != "complete":
                errors.append(f"{name}: not dependency-closed: {key} depends on {dependency}, "
                              f"which is outside the batch and {status}")
            elif dependency not in listed:
                errors.append(f"{name}: {key} depends on {dependency}, a complete phase outside "
                              "the batch that external_dependencies does not list")
    errors += [f"{name}: external_dependencies lists {dependency}, which no phase in the batch "
               "depends on" for dependency in sorted(listed - needed)]

    stages = [[key for key in dict.fromkeys(stage["phases"]) if key in members]
              for stage in batch["stages"]]
    for index, stage in enumerate(stages, start=1):
        for left, right in combinations(stage, 2):
            errors += [f"{name}: stage {index}: {left}/{right} {reason}"
                       for reason in backlog.collisions(members[left], members[right])]
    for index in range(1, len(stages)):
        earlier, later = stages[index - 1], stages[index]
        if not earlier or not later:
            continue  # a stage of unresolved ids is already reported
        justified = any(
            before in backlog.dependency_closure(after, items)
            or backlog.collisions(members[after], members[before])
            for after in later for before in earlier)
        if not justified:
            errors.append(f"{name}: the boundary between stages {index} and {index + 1} follows "
                          f"from no dependency edge or collision; stage {index + 1} could join "
                          f"stage {index}")
    return errors


def file_problems(registry: dict[str, Any], items: dict[str, Any],
                  composition_for: Sequence[str] = ()) -> list[str]:
    """Problems across the file: unique ids, successors, and each batch's rules.

    Batches named in ``composition_for`` get the composition check whatever their status; every
    other batch that is not finished gets the structural rules.
    """
    batches = registry["batches"]
    ids = [batch["id"] for batch in batches]
    errors = [f"{key}: duplicate batch id" for key in sorted({k for k in ids if ids.count(k) > 1})]
    for batch in batches:
        successor = batch.get("superseded_by")
        if successor is not None and successor not in ids:
            errors.append(f"{batch['id']}: superseded_by names unknown batch {successor}")
        if batch["id"] in composition_for:
            if batch["status"] in FINISHED:
                errors.append(f"{batch['id']}: is {batch['status']}; a finished batch is not "
                              "composed again")
            errors += batch_problems(batch, items, composition=True)
        elif batch["status"] not in FINISHED:
            errors += batch_problems(batch, items)
    return errors


def problems(config: paths.Config) -> list[str]:
    """Every structural problem in the batches file; an absent file has nothing to check."""
    path = batches_path(config)
    if not path.is_file():
        return []
    try:
        registry = load_batches(path, _shown(config, path))
        items = load_items(config)
    except Unreadable as exc:
        return str(exc).splitlines()
    return file_problems(registry, items)


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="Without batch ids, every live batch gets the structural rules; with ids, those "
               "batches get the composition check as well.")
    parser.add_argument("batch", nargs="*",
                        help="batch id to run the composition check on; repeatable")
    parser.add_argument("--batches", default=None,
                        help="batches file (default: batches.yaml beside the backlog)")
    paths.add_arguments(parser, ["backlog_path"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    path = Path(args.batches).resolve() if args.batches else batches_path(config)
    shown = _shown(config, path)
    if not path.is_file():
        if args.batch:
            print(f"no batches file at {shown}", file=sys.stderr)
            return 2
        print(f"no batches file at {shown}; nothing to check")
        return 0
    try:
        registry = load_batches(path, shown)
        items = load_items(config)
    except Unreadable as exc:
        print(exc, file=sys.stderr)
        return 2
    known = {batch["id"] for batch in registry["batches"]}
    missing = [key for key in args.batch if key not in known]
    if missing:
        print(f"{shown}: no batch {', '.join(missing)}", file=sys.stderr)
        return 2
    found = file_problems(registry, items, composition_for=args.batch)
    for line in found:
        print(line)
    if not found:
        checked = args.batch or [batch["id"] for batch in registry["batches"]
                                 if batch["status"] not in FINISHED]
        mode = "composition" if args.batch else "structure"
        print(f"OK ({mode}): {', '.join(checked) if checked else 'no live batches'}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
