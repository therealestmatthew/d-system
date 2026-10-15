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

Stranding is judged against ``origin``, not only this checkout's refs, because a checkout that has
not fetched does not know a peer's merge. When the local refs do not contain the commit, the check
asks ``origin`` where the branch is (``git ls-remote``, which fetches nothing). It reports stranded
only when this checkout holds that tip and the commit is not in its history. When origin cannot be
read, or its tip is a commit this checkout has not fetched, it prints a ``cannot tell`` note that
says to fetch and run the check again.

Without a product checkout on this machine (control CI is always in this state) every check that
reads only the control records still runs and still fails: a passing gating verdict for this phase
on the product repository, and full commit ids in ``product_merge`` and ``reviewed_commit``. When
``product_merge`` is the reviewed commit, a fast-forward, the records agree and nothing more is
said. Any other ``product_merge`` can only be a merge commit whose second parent was reviewed, and
its parents are in the product repository, so the check prints a ``not checked`` note for that
phase naming the reviewed commit, rather than passing it silently.

Notes go to standard error and never change the exit code.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
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


def is_ancestor(root: Path, commit: str, ref: str) -> bool:
    """Whether ``commit`` is reachable from ``ref`` in the product checkout."""
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                           "--end-of-options", commit, ref],
                          env=paths.git_env(), capture_output=True, text=True,
                          check=False).returncode == 0


def on_integration_branch(root: Path, commit: str, branch: str) -> bool:
    """Whether ``commit`` is reachable from the product integration branch, local or fetched."""
    for ref in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
        known = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", ref],
                               env=paths.git_env(), capture_output=True, text=True, check=False)
        if known.returncode == 0 and is_ancestor(root, commit, ref):
            return True
    return False


def origin_tip(root: Path, branch: str) -> str | None:
    """Where ``origin`` has the integration branch now, read with ``git ls-remote`` (no fetch):
    a commit id, ``""`` when origin has no such branch, or None when origin could not be read."""
    try:
        found = subprocess.run(["git", "-C", str(root), "ls-remote", "--heads", "origin",
                                f"refs/heads/{branch}"],
                               capture_output=True, text=True, check=False, timeout=60,
                               env=paths.git_env({**os.environ, "GIT_TERMINAL_PROMPT": "0"}))
    except (OSError, subprocess.TimeoutExpired):
        return None
    if found.returncode != 0:
        return None
    return found.stdout.split()[0] if found.stdout.split() else ""


def known_commit(root: Path, commit: str) -> bool:
    """Whether the product checkout holds ``commit``."""
    return subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
                          env=paths.git_env(), capture_output=True, text=True,
                          check=False).returncode == 0


def second_parent(root: Path, commit: str) -> str | None:
    """The second parent of a merge commit, or None for a commit with one parent."""
    found = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q",
                            f"{commit}^2^{{commit}}"],
                           env=paths.git_env(), capture_output=True, text=True, check=False)
    return found.stdout.strip() if found.returncode == 0 else None


def landing_errors(root: Path, key: str, merge: str, branch: str,
                   note: Callable[[str], None]) -> list[str]:
    """``[stranded]`` when ``merge`` is not on the product integration branch, after the local
    refs and then ``origin`` itself were asked; a note and no error when it cannot be told."""
    if known_commit(root, merge) and on_integration_branch(root, merge, branch):
        return []
    # The local refs can be behind origin: a peer's merge this checkout never fetched, or a
    # fast-forward of a commit it holds on another branch. Ask origin where the branch is now.
    tip = origin_tip(root, branch)
    fetch = f"fetch the product checkout (git -C {root} fetch origin) and run the check again"
    if tip is None:
        note(f"{key}: cannot tell whether product_merge {merge} landed: origin could not be read "
             f"for {branch}; {fetch}")
        return []
    if tip and not known_commit(root, tip):
        note(f"{key}: cannot tell whether product_merge {merge} landed: the product checkout is "
             f"behind origin ({branch} is at {tip[:12]} there, which this checkout has not "
             f"fetched); {fetch}")
        return []
    if tip and known_commit(root, merge) and is_ancestor(root, merge, tip):
        return []
    where = f"{branch} at origin ({tip[:12]})" if tip else f"{branch}, which origin does not have"
    return [f"{key}: stranded: recorded complete, but its product_merge {merge} is not on the "
            f"product branch {where} (see docs/two-repositories.md, A stranded phase)"]


def completion_errors(config: paths.Config, records: list[dict[str, Any]],
                      note: Callable[[str], None]) -> list[str]:
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
            # Everything that reads only the control records has run above. A product_merge
            # equal to a reviewed commit is a fast-forward and the records agree; any other
            # value can only be a merge commit, and its second parent is in the product
            # repository.
            if merge not in reviewed and not refused:
                judged = ", ".join(sorted(reviewed))
                note(f"{key}: product_merge {merge} not checked: no product checkout is "
                     f"configured on this machine (product_root). It is not the reviewed commit "
                     f"{judged}, so it passes only as a merge commit whose second parent is that "
                     "commit, and reading its parents needs the product repository")
            continue
        branch = product.load(config).integration_branch
        if known_commit(product_root, merge) and merge not in reviewed \
                and second_parent(product_root, merge) not in reviewed:
            errors.append(f"{key}: no passing gating verdict judged its product_merge {merge} "
                          "(fast-forward) or that merge commit's second parent")
            continue
        errors.extend(landing_errors(product_root, key, merge, branch, note))
    return errors


def audit(config: paths.Config, note: Callable[[str], None] | None = None) -> list[str]:
    """Every review problem. Notes (what could not be checked here) go to ``note``, by default
    standard error; they never change the exit code."""
    note = note or (lambda line: print(f"reviews: {line}", file=sys.stderr))
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
    return errors + completion_errors(config, records, note)


def check(config: paths.Config) -> list[str]:
    return audit(config)
