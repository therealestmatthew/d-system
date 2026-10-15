"""Review records, and the rule that a phase completes only on a passing gating review.

A record is written once, from the reviewer's reply, and only its ``outcomes`` grow afterwards.
This check keeps the set readable by every later reader: each file under ``<docs_root>/reviews/``
is valid against the verdict schema, its ``verdict_id`` is its file name, and its finding ids are
unique.

It also ties completion to review. A phase with ``status: complete`` needs a record for it with
``verdict: pass`` and ``gating: true``. When a product repository is set up, the phase must also
name its ``product_merge``, and that record must have judged the commit the merge brought in:
``product_merge`` itself when the branch was fast-forwarded (a repository with no remote, or an
older record), or the merge commit's second parent when a pull request was merged with a merge
commit. Where this machine has a verified product checkout, the commit must also be on the product
integration branch: a phase recorded complete whose product merge never landed is stranded, and is
reported as such.

Without a product checkout on this machine a merge commit's parents cannot be read, so a
``product_merge`` that no verdict names directly is left unchecked there, as landing is.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import paths
import product
import yaml
from jsonschema import Draft7Validator, FormatChecker

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "review-verdict.schema.json"
DIRECTORY = "reviews"
COMMIT = re.compile(r"[0-9a-f]{40}")


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


def known_commit(root: Path, commit: str) -> bool:
    """Whether the product checkout holds ``commit``."""
    return subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
                          capture_output=True, text=True, check=False).returncode == 0


def second_parent(root: Path, commit: str) -> str | None:
    """The second parent of a merge commit, or None for a commit with one parent."""
    found = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q",
                            f"{commit}^2^{{commit}}"],
                           capture_output=True, text=True, check=False)
    return found.stdout.strip() if found.returncode == 0 else None


def completion_errors(config: paths.Config, records: list[dict[str, Any]]) -> list[str]:
    """Every complete phase that no passing gating review supports."""
    two_repositories = product.read_record(config.root) is not None
    product_root, refused = product.verified_root(config) if two_repositories else (None, None)
    errors = []
    if refused:
        errors.append(f"product checkout refused, so product merges cannot be checked: {refused}")
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
        if not isinstance(merge, str) or not COMMIT.fullmatch(merge):
            errors.append(f"{key}: product_merge {merge!r} is not a full commit id")
            continue
        reviewed = {record["reviewed_commit"] for record in passing
                    if record["repository"] == "product"}
        if not reviewed:
            errors.append(f"{key}: no passing gating verdict judged its product_merge {merge}")
            continue
        if product_root is None:
            continue
        branch = product.load(config).integration_branch
        stranded = (f"{key}: stranded: recorded complete, but its product_merge {merge} is not on "
                    f"the product branch {branch} (see docs/two-repositories.md, A stranded phase)")
        if not known_commit(product_root, merge):
            errors.append(stranded)
            continue
        if merge not in reviewed and second_parent(product_root, merge) not in reviewed:
            errors.append(f"{key}: no passing gating verdict judged its product_merge {merge} "
                          "(fast-forward) or that merge commit's second parent")
            continue
        if not on_integration_branch(product_root, merge, branch):
            errors.append(stranded)
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
