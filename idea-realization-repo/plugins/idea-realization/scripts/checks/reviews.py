"""Review records, and the rule that a phase completes only on a passing gating review.

A record is written once, from the reviewer's reply, and only its ``outcomes`` grow afterwards.
This check keeps the set readable by every later reader: each file under ``<docs_root>/reviews/``
is valid against the verdict schema, its ``verdict_id`` is its file name, and its finding ids are
unique.

It also ties completion to review. A phase with ``status: complete`` needs a record for it with
``verdict: pass`` and ``gating: true``. When a product repository is set up, the phase must also
name its ``product_merge``, that record must have judged exactly that commit, and, where this
machine has a verified product checkout, the commit must be on the product integration branch: a
phase recorded complete whose product merge never landed is stranded, and is reported as such.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import paths
import product
import yaml
from jsonschema import Draft7Validator, FormatChecker

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "review-verdict.schema.json"
DIRECTORY = "reviews"


def record_errors(path: Path, schema: dict[str, object]) -> tuple[list[str], dict[str, Any]]:
    """Every problem in one record file, one line each, and the record when it is valid."""
    name = path.name
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"{name}: {exc}"], {}
    issues = Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(record)
    errors = [f"{name}:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
              for issue in issues]
    if errors:
        return errors, {}
    if record["verdict_id"] != path.stem:
        errors.append(f"{name}: verdict_id {record['verdict_id']!r} is not the file name")
    ids = [finding["id"] for finding in record["findings"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{name}: duplicate finding id")
    return errors, record


def completed_phases(config: paths.Config) -> list[dict[str, Any]]:
    """Every ``status: complete`` phase in the backlog; none when there is no readable backlog."""
    try:
        loaded = yaml.safe_load(config.path("backlog_path").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    items = (loaded or {}).get("items") or []
    return [item for item in items if isinstance(item, dict) and item.get("status") == "complete"]


def on_integration_branch(root: Path, commit: str, branch: str) -> bool:
    """Whether ``commit`` is reachable from the product integration branch, local or fetched."""
    for ref in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
        known = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", ref],
                               capture_output=True, text=True, check=False)
        if known.returncode != 0:
            continue
        reached = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                                  "--end-of-options", commit, ref],
                                 capture_output=True, text=True, check=False)
        if reached.returncode == 0:
            return True
    return False


def completion_errors(config: paths.Config, records: list[dict[str, Any]]) -> list[str]:
    """Every complete phase that no passing gating review supports."""
    two_repositories = product.read_record(config.root) is not None
    product_root, _ = product.verified_root(config) if two_repositories else (None, None)
    errors = []
    for phase in completed_phases(config):
        key = phase.get("id", "?")
        passing = [record for record in records if record["phase"] == key
                   and record["verdict"] == "pass" and record["gating"]]
        if not passing:
            errors.append(f"{key}: complete without a passing gating verdict in {DIRECTORY}/")
            continue
        if not two_repositories:
            continue
        merge = phase.get("product_merge")
        if not merge:
            errors.append(f"{key}: complete without product_merge, the product commit it merged as")
            continue
        if not any(record["repository"] == "product" and record["reviewed_commit"] == merge
                   for record in passing):
            errors.append(f"{key}: no passing gating verdict judged its product_merge {merge}")
            continue
        if product_root is not None:
            branch = product.load(config).integration_branch
            if not on_integration_branch(product_root, merge, branch):
                errors.append(f"{key}: stranded: recorded complete, but its product_merge {merge} "
                              f"is not on the product branch {branch} (see "
                              "docs/two-repositories.md, A stranded phase)")
    return errors


def check(config: paths.Config) -> list[str]:
    directory = config.path("docs_root") / DIRECTORY
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    if directory.is_dir():
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json")):
            found, record = record_errors(path, schema)
            errors.extend(f"{DIRECTORY}/{line}" for line in found)
            if record:
                records.append(record)
    return errors + completion_errors(config, records)
