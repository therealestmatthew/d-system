"""Review records: every verdict under ``<docs_root>/reviews/`` validates and names itself.

A record is written once, from the reviewer's reply, and only its ``outcomes`` grow afterwards. This
check keeps the set readable by every later reader: each file is valid against the verdict schema,
its ``verdict_id`` is its file name, and its finding ids are unique.
"""

from __future__ import annotations

import json
from pathlib import Path

import paths
from jsonschema import Draft7Validator, FormatChecker

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "review-verdict.schema.json"
DIRECTORY = "reviews"


def record_errors(path: Path, schema: dict[str, object]) -> list[str]:
    """Every problem in one record file, one line each."""
    name = path.name
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"{name}: {exc}"]
    issues = Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(record)
    errors = [f"{name}:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
              for issue in issues]
    if errors:
        return errors
    if record["verdict_id"] != path.stem:
        errors.append(f"{name}: verdict_id {record['verdict_id']!r} is not the file name")
    ids = [finding["id"] for finding in record["findings"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{name}: duplicate finding id")
    return errors


def check(config: paths.Config) -> list[str]:
    directory = config.path("docs_root") / DIRECTORY
    if not directory.is_dir():
        return []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors: list[str] = []
    for path in sorted(directory.glob("*.json")):
        errors.extend(f"{DIRECTORY}/{line}" for line in record_errors(path, schema))
    return errors
