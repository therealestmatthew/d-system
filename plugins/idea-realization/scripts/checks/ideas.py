"""The ideas feature's check: the log replays, the priority queue is valid, the view is current.

``check(config)`` reports, one line each:

- a log line that fails the idea schema, or a history the fold refuses;
- a priority file that fails its schema, is dated in the future, or names an idea that is
  unknown or not ``open`` or ``triaged``;
- a rendered view that differs from a fresh render of the log and priority file.

A repository with neither an idea log nor a rendered view has not installed the feature, and
gets no report.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import paths
import yaml  # type: ignore[import-untyped]
from ideas import SCHEMA, IdeaError, fold, load_events
from jsonschema import Draft7Validator  # type: ignore[import-untyped]
from render_ideas import stale_view_errors

PRIORITY_SCHEMA = paths.PLUGIN_ROOT / "schemas" / "idea-priority.schema.json"

#: An idea already past scouting has nothing left for the priority queue to order.
QUEUEABLE_STATES = {"open", "triaged"}


def _validator(schema: Path) -> Draft7Validator:
    loaded = json.loads(schema.read_text(encoding="utf-8"))
    return Draft7Validator(loaded, format_checker=Draft7Validator.FORMAT_CHECKER)


def _shown(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return str(path)


def inspect_idea_priority(
    catalog: dict[str, Any], ideas: dict[str, dict[str, Any]], today: dt.date | None = None,
    name: str = "priority file",
) -> list[str]:
    """Errors in the priority file given the current folded state of the idea log."""
    errors: list[str] = []
    today = today or dt.date.today()

    if dt.date.fromisoformat(catalog["updated"]) > today:
        errors.append(f"{name}: updated {catalog['updated']} is in the future")

    for idea in catalog["next_up"]:
        if idea not in ideas:
            errors.append(f"{name}: next_up names unknown idea {idea}")
            continue
        status = ideas[idea]["status"]
        if status not in QUEUEABLE_STATES:
            errors.append(
                f"{name}: {idea} is {status}, not open or triaged — remove it from next_up"
            )
    return errors


def log_errors(log: Path, name: str) -> list[str]:
    """Every log line that fails the schema; the fold's own refusals are reported separately."""
    validator = _validator(SCHEMA)
    errors = []
    for position, event in enumerate(load_events(log), start=1):
        for error in sorted(validator.iter_errors(event), key=lambda e: list(e.absolute_path)):
            where = ".".join(str(p) for p in error.absolute_path) or "event"
            errors.append(f"{name}: event {position}: {where}: {error.message}")
    return errors


def priority_errors(
    config: paths.Config, state: dict[str, dict[str, Any]], today: dt.date | None = None
) -> list[str]:
    priority = config.path("priority_path")
    if not priority.is_file():
        return []
    name = _shown(config, priority)
    try:
        catalog = yaml.safe_load(priority.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{name}: not valid YAML: {exc}"]
    invalid = sorted(_validator(PRIORITY_SCHEMA).iter_errors(catalog),
                     key=lambda e: list(e.absolute_path))
    if invalid:
        return [f"{name}: {'.'.join(str(p) for p in e.absolute_path) or 'file'}: {e.message}"
                for e in invalid]
    return inspect_idea_priority(catalog, state, today, name)


def check(config: paths.Config, today: dt.date | None = None) -> list[str]:
    log = config.path("ideas_path")
    if not log.exists() and not config.path("ideas_view_path").exists():
        return []
    name = _shown(config, log)
    try:
        errors = log_errors(log, name)
        if errors:
            return errors
        state = fold(load_events(log))
    except IdeaError as exc:
        return [f"{name}: {exc}"]
    return priority_errors(config, state, today) + stale_view_errors(config)
