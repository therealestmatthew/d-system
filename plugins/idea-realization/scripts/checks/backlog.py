"""The backlog feature: its check and the ``ready`` command.

``check`` validates the backlog file against ``schemas/backlog.schema.json``, then runs every rule
in ``backlog.py`` against the documents, systems and owners the document scan
(``documents.scan``) reports, then the status-regression check (``regression.py``) when the
catalog names a ``decision_record``. A repository without a backlog file has nothing to check.

Regression warnings, and the note that the regression check did not run, go to standard error:
they never change the exit code.

``ready`` prints the phase queue — ``next_up`` first, then priority and id — with each phase's
readiness, prerequisites and the active phases it would collide with, and a stale-claim signal
beside each active claim, read from its ``agent/<phase-id>`` branch and worktree.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import backlog
import documents
import paths
import regression
import yaml
from jsonschema import Draft7Validator, FormatChecker

SCHEMA = paths.PLUGIN_ROOT / "schemas" / "backlog.schema.json"
#: Path parts a phase may never declare: git's own directory and a virtual environment.
REFUSED_PARTS = {".git", ".venv", "node_modules"}


def repository_path(root: Path, value: str) -> Path:
    """Resolve a declared path inside the repository, refusing escapes and symlinks."""
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"expected repository-relative path: {value}")
    current = root
    for part in path.parts:
        if part in REFUSED_PARTS:
            raise ValueError(f"path is outside the repository's tracked content: {value}")
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink is not a declarable path: {value}")
    return current


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_catalog(config: paths.Config) -> tuple[list[str], dict[str, Any]]:
    """Read and schema-validate the backlog. Returns (errors, catalog)."""
    location = relative(config.root, config.path("backlog_path"))
    try:
        catalog = documents.load_yaml(config.path("backlog_path").read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"{location}: {exc}"], {}
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    issues = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(catalog))
    if issues:
        return [f"{location}:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
                for issue in issues], {}
    return [], catalog


def inspect(root: Path, catalog: dict[str, Any], documents: dict[str, Any], systems: set[str],
            owners: set[str], today: date) -> list[str]:
    """Every rule in ``backlog.inspect_backlog``, with declared paths resolved under ``root``."""
    return backlog.inspect_backlog(catalog, documents, systems, owners,
                                   lambda value: repository_path(root, value).is_file(), today)


def audit(config: paths.Config, today: date | None = None,
          note: Callable[[str], None] | None = None) -> list[str]:
    """Every backlog problem. Warnings and notes go to ``note``; they are never problems."""
    note = note or (lambda line: print(f"backlog: {line}", file=sys.stderr))
    if not config.path("backlog_path").is_file():
        return []
    errors, catalog = load_catalog(config)
    if errors:
        return errors
    scanned = documents.scan(config, today)
    if scanned.errors:
        return ["not checked: the document tree has errors (see the documents check); the "
                "backlog resolves its plans, systems and owners through it"]
    root = config.root
    errors = inspect(root, catalog, scanned.documents, set(scanned.systems),
                     set(scanned.owners), today or date.today())
    record = catalog.get("decision_record")
    if record is None:
        note("status-regression not run: the backlog names no decision_record, so a reopened "
             "phase has nowhere to be recorded")
        return errors
    document = scanned.documents.get(record)
    if document is None:
        return errors  # inspect_backlog already reports the unresolved decision_record
    found, warnings = regression.audit(
        root, catalog, relative(root, config.path("backlog_path")), document["path"],
        config.text("integration_branch"),
    )
    for warning in warnings:
        note(warning)
    return sorted(errors + found)


def check(config: paths.Config) -> list[str]:
    return audit(config)


def claim_evidence(root: Path, phase_ids: list[str], today: date) -> dict[str, dict[str, Any]]:
    """The two staleness signals per active claim, from read-only git commands.

    A phase whose ``agent/<phase-id>`` branch has no commits here contributes no evidence, which
    ``backlog.claim_report_state`` reports as such rather than as not-stale.
    """
    try:
        listing = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                                 capture_output=True, text=True, check=True).stdout
        listing_available = True
    except (OSError, subprocess.CalledProcessError):
        listing, listing_available = "", False
    branches = {line.split("refs/heads/", 1)[1] for line in listing.splitlines()
                if line.startswith("branch ") and "refs/heads/" in line}
    evidence: dict[str, dict[str, Any]] = {}
    for phase_id in phase_ids:
        branch = f"agent/{phase_id}"
        try:
            committed = subprocess.run(
                ["git", "log", "-1", "--format=%ad", "--date=short", branch], cwd=root,
                capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            committed = ""
        if not committed:
            evidence[phase_id] = {"days_since_commit": None, "worktree_exists": None}
            continue
        evidence[phase_id] = {
            "days_since_commit": (today - date.fromisoformat(committed)).days,
            "worktree_exists": (branch in branches) if listing_available else None,
        }
    return evidence


def ready(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="ready",
        description="Print the phase queue: next_up first, then priority and id, with readiness, "
                    "prerequisites, conflicts with active phases and a stale-claim signal. Reads "
                    "only. Exit 1 when the backlog or document tree fails its check.",
    )
    parser.add_argument("--all", action="store_true",
                        help="every phase with full details, not only the ready ones")
    paths.add_arguments(parser, ["backlog_path", "docs_root", "exempt_files",
                                 "integration_branch"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    if not config.path("backlog_path").is_file():
        print(f"no backlog at {relative(config.root, config.path('backlog_path'))}; run the "
              "scaffold for the backlog feature", file=sys.stderr)
        return 1
    errors, catalog = load_catalog(config)
    scanned = documents.scan(config)
    if errors or scanned.errors:
        for error in errors or scanned.errors:
            print(error, file=sys.stderr)
        return 1
    active = [item["id"] for item in catalog["items"] if item["status"] == "active"]
    evidence = claim_evidence(config.root, active, date.today())
    print(backlog.render_backlog(catalog, scanned.documents, ready_only=not args.all,
                                 claim_evidence=evidence))
    return 0


COMMANDS: dict[str, tuple[str, Callable[[list[str]], int]]] = {
    "ready": ("print the phase queue with readiness and conflicts (--all for details)", ready),
}

