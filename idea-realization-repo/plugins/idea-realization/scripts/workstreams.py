# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Show, claim and release workstreams, and check the registry that records them.

A workstream is an ownership layer, not a lock: ``<docs_root>/workstreams.yaml`` declares the paths
one developer owns, and every other developer's phases must keep their deliverables out of them::

    schema_version: 1
    workstreams:
      - id: ui
        title: User interface
        owner: ""            # developer handle when claimed; "" when open
        status: open         # open | claimed
        paths: [product:web/]
        interfaces: []

A claim is made by committing that file on the integration branch. Developers work on separate
machines, so a rejected push is the race signal: the developer pulls with rebase and runs ``check``
again. This script only edits the file and validates it; it never commits or pushes.

Subcommands:

- ``show`` prints one line per workstream: id, status, owner or ``-``, title and paths.
- ``claim <id>`` gives an open workstream to the current developer (``identity.handle``), then
  validates the result and restores the original file when validation fails.
- ``release <id>`` lets the current owner give a workstream back.
- ``check`` prints every problem ``problems`` finds.

``problems`` reports, one line each and sorted: schema violations; duplicate ids; a claimed
workstream whose owner is not a developer handle, or an open one with an owner; two workstreams
whose paths overlap; and an ``active`` or ``blocked`` phase whose agent is ``<handle>/<anything>``
and which declares a deliverable inside a workstream claimed by another developer, unless its
``cross_workstream`` list holds ``{workstream: <id>, approved_by: <owner>}`` for that workstream.
Paths outside every workstream are shared ground. Once the registry defines a workstream, an
``active`` or ``blocked`` phase whose agent carries no handle (``agent-builder`` rather than
``ana/agent-builder``) is a problem too, because nobody can tell whose paths it may touch. An
absent registry means the feature is not in use, and nothing is reported.

Writing the file uses ``yaml.safe_dump`` in the file's own key order, so comments are not kept.

Exit codes: 0 on success; 1 when a problem is found, the workstream is unknown, already claimed or
owned by someone else, the current developer cannot be resolved, or the claim fails validation;
2 when a configured path is refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from itertools import combinations
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import identity  # noqa: E402
import paths  # noqa: E402
import yaml  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

from backlog import path_conflict  # noqa: E402

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "workstreams.schema.json"
REGISTRY = "workstreams.yaml"
#: Phase states whose declared deliverables are being worked on now.
CHECKED_STATES = {"active", "blocked"}


def registry_path(config: paths.Config) -> Path:
    return config.path("docs_root") / REGISTRY


def _shown(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return str(path)


def schema_errors(registry: Any) -> list[str]:
    """Every schema violation, as ``<location>: <message>``."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    found = sorted(Draft7Validator(schema).iter_errors(registry),
                   key=lambda error: list(map(str, error.absolute_path)))
    return [f"{'.'.join(map(str, error.absolute_path)) or 'file'}: {error.message}"
            for error in found]


def registry_errors(registry: dict[str, Any], team: set[str]) -> list[str]:
    """Duplicate ids, owners that do not fit the status, and overlapping paths."""
    errors: list[str] = []
    streams = registry["workstreams"]
    seen: set[str] = set()
    for stream in streams:
        if stream["id"] in seen:
            errors.append(f"duplicate workstream id {stream['id']}")
        seen.add(stream["id"])
        owner = stream["owner"]
        if stream["status"] == "claimed" and owner not in team:
            errors.append(f"workstream {stream['id']} is claimed but its owner {owner!r} is not a "
                          "developer handle (an owners key with emails in systems.yaml)")
        if stream["status"] == "open" and owner != "":
            errors.append(f"workstream {stream['id']} is open but names owner {owner!r}; an open "
                          "workstream's owner is \"\"")
    for left, right in combinations(streams, 2):
        for first in left["paths"]:
            for second in right["paths"]:
                if path_conflict(first, second):
                    errors.append(f"workstreams {left['id']} and {right['id']} overlap: "
                                  f"{left['id']} path {first}, {right['id']} path {second}")
    return errors


def _approved(phase: dict[str, Any], stream: dict[str, Any]) -> bool:
    approvals = phase.get("cross_workstream") or []
    if not isinstance(approvals, list):
        return False
    return any(isinstance(entry, dict) and entry.get("workstream") == stream["id"]
               and entry.get("approved_by") == stream["owner"] for entry in approvals)


def phase_errors(registry: dict[str, Any], catalog: Any) -> list[str]:
    """Every working phase's deliverable inside a workstream another developer claimed."""
    if not isinstance(catalog, dict) or not isinstance(catalog.get("items"), list):
        return []
    claimed = [stream for stream in registry["workstreams"] if stream["status"] == "claimed"]
    errors: list[str] = []
    for phase in catalog["items"]:
        if not isinstance(phase, dict) or phase.get("status") not in CHECKED_STATES:
            continue
        agent = phase.get("agent")
        if not isinstance(agent, str):
            continue  # an unclaimed working phase is the backlog check's to report
        if "/" not in agent:
            if registry["workstreams"]:
                errors.append(f"phase {phase.get('id')} is claimed without a developer handle "
                              "(agent must be <handle>/agent-...)")
            continue
        handle = agent.split("/", 1)[0]
        for deliverable in phase.get("deliverables") or []:
            if not isinstance(deliverable, str):
                continue
            for stream in claimed:
                if stream["owner"] == handle or _approved(phase, stream):
                    continue
                if any(path_conflict(deliverable, owned) for owned in stream["paths"]):
                    errors.append(f"phase {phase.get('id')} (agent handle {handle}) declares "
                                  f"deliverable {deliverable} inside workstream {stream['id']} "
                                  f"owned by {stream['owner']}")
    return errors


def problems(config: paths.Config) -> list[str]:
    """Every problem in the registry and in the phases that touch it, one line each, sorted."""
    registry_file = registry_path(config)
    if not registry_file.exists():
        return []
    name = _shown(config, registry_file)
    try:
        registry = yaml.safe_load(registry_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{name}: not valid YAML: {exc}"]
    invalid = schema_errors(registry)
    if invalid:
        return [f"{name}: {line}" for line in invalid]
    team = set(identity.developers(config.path("docs_root")))
    errors = [f"{name}: {line}" for line in registry_errors(registry, team)]
    backlog_file = config.path("backlog_path")
    if backlog_file.is_file():
        backlog_name = _shown(config, backlog_file)
        try:
            catalog = yaml.safe_load(backlog_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{backlog_name}: not valid YAML: {exc}")
        else:
            errors += [f"{backlog_name}: {line}" for line in phase_errors(registry, catalog)]
    return sorted(errors)


def _find(registry: dict[str, Any], stream_id: str) -> dict[str, Any] | None:
    return next((s for s in registry.get("workstreams") or [] if s.get("id") == stream_id), None)


def _load_for_edit(config: paths.Config) -> tuple[Path, str, dict[str, Any]]:
    """The registry's path, original text and parsed content; ``LookupError`` when unusable."""
    registry_file = registry_path(config)
    if not registry_file.exists():
        raise LookupError(f"no workstream registry at {_shown(config, registry_file)}")
    original = registry_file.read_text(encoding="utf-8")
    try:
        registry = yaml.safe_load(original)
    except yaml.YAMLError as exc:
        raise LookupError(f"{_shown(config, registry_file)}: not valid YAML: {exc}") from exc
    if not isinstance(registry, dict):
        raise LookupError(f"{_shown(config, registry_file)}: not a mapping")
    return registry_file, original, registry


def _write_validated(config: paths.Config, registry_file: Path, original: str,
                     registry: dict[str, Any]) -> list[str]:
    """Write the edit, validate it, and restore the original text when validation fails."""
    registry_file.write_text(yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
                             encoding="utf-8")
    found = problems(config)
    if found:
        registry_file.write_text(original, encoding="utf-8")
    return found


def show(config: paths.Config) -> int:
    registry_file = registry_path(config)
    if not registry_file.exists():
        print(f"no workstream registry at {_shown(config, registry_file)}; workstreams are not in "
              "use")
        return 0
    try:
        _, _, registry = _load_for_edit(config)
    except LookupError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for stream in registry.get("workstreams") or []:
        owner = stream.get("owner") or "-"
        print(f"{stream.get('id')}  {stream.get('status')}  {owner}  {stream.get('title')}  "
              f"{', '.join(map(str, stream.get('paths') or []))}")
    return 0


def _edit(config: paths.Config, stream_id: str,
          change: Callable[[dict[str, Any], str], str | None]) -> int:
    """Shared body of ``claim`` and ``release``: resolve, refuse or change, write, validate."""
    try:
        handle = identity.handle(config)
        registry_file, original, registry = _load_for_edit(config)
    except (identity.IdentityError, LookupError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    stream = _find(registry, stream_id)
    if stream is None:
        print(f"error: unknown workstream {stream_id!r}", file=sys.stderr)
        return 1
    refusal = change(stream, handle)
    if refusal:
        print(f"error: {refusal}", file=sys.stderr)
        return 1
    found = _write_validated(config, registry_file, original, registry)
    if found:
        print("error: the edit fails validation, so the registry was restored:", file=sys.stderr)
        for line in found:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


def _claim(stream: dict[str, Any], handle: str) -> str | None:
    if stream.get("status") != "open":
        return f"workstream {stream['id']} is already claimed by {stream.get('owner') or '-'}"
    stream["owner"], stream["status"] = handle, "claimed"
    return None


def _release(stream: dict[str, Any], handle: str) -> str | None:
    if stream.get("status") != "claimed" or stream.get("owner") != handle:
        holder = stream.get("owner") or "nobody"
        return (f"workstream {stream['id']} is owned by {holder}; only its owner may release it "
                f"(you are {handle})")
    stream["owner"], stream["status"] = "", "open"
    return None


def claim(config: paths.Config, stream_id: str) -> int:
    code = _edit(config, stream_id, _claim)
    if code == 0:
        name = _shown(config, registry_path(config))
        branch = config.values["integration_branch"]
        print(f"claimed workstream {stream_id}. Next:\n"
              f"  1. commit only {name}\n"
              f"  2. push it to the integration branch ({branch})\n"
              "  3. if the push is rejected, another claim landed first: pull with rebase and run "
              "`workstreams.py check` again before pushing")
    return code


def release(config: paths.Config, stream_id: str) -> int:
    code = _edit(config, stream_id, _release)
    if code == 0:
        name = _shown(config, registry_path(config))
        print(f"released workstream {stream_id}. Commit only {name} and push it to the "
              "integration branch.")
    return code


def check(config: paths.Config) -> int:
    found = problems(config)
    for line in found:
        print(line)
    return 1 if found else 0


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workstreams",
        description="Show, claim or release a workstream, or check the workstream registry.",
    )
    common = argparse.ArgumentParser(add_help=False)
    paths.add_arguments(common, ["docs_root", "backlog_path"])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", parents=[common],
                   help="one line per workstream: id, status, owner, title, paths")
    for name, text in (("claim", "claim an open workstream for the current developer"),
                       ("release", "release a workstream the current developer owns")):
        sub.add_parser(name, parents=[common], help=text).add_argument("id", help="workstream id")
    sub.add_parser("check", parents=[common],
                   help="print every registry and phase problem; exit 1 if any")
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    if args.command == "show":
        return show(config)
    if args.command == "claim":
        return claim(config, args.id)
    if args.command == "release":
        return release(config, args.id)
    return check(config)


COMMANDS: dict[str, tuple[str, Callable[[list[str]], int]]] = {
    "workstreams": ("show, claim or release a workstream, or check the registry", main),
}


if __name__ == "__main__":
    raise SystemExit(main())
