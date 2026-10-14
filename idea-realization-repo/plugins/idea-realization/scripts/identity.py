# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Who is working: the developer handle that scopes every identifier a developer allocates.

A team of developers on separate machines cannot coordinate identifier allocation through files a
branch cannot see, so each identifier carries its author instead: an idea id, a phase's agent and a
workstream's owner all name a developer handle.

A developer is an entry in the ``owners`` map of ``<docs_root>/systems.yaml`` whose value is an
object with ``emails``::

    owners:
      repository-owner: The person accountable for this repository.
      ana:
        description: Ana, user interface workstream.
        emails: [ana@example.com]

The handle is resolved in this order:

1. the environment variable ``IDEA_REALIZATION_HANDLE`` (it must still name a developer);
2. the owner whose ``emails`` contain ``git config user.email`` in the repository root.

A handle is lower-case letters and digits, starting with a letter, at most 16 characters, so it can
sit inside an identifier without ambiguity.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paths  # noqa: E402

HANDLE_ENV = "IDEA_REALIZATION_HANDLE"
HANDLE_PATTERN = re.compile(r"^[a-z][a-z0-9]{0,15}$")
REGISTRY = "systems.yaml"


class IdentityError(ValueError):
    """The current developer could not be resolved to a handle."""


def developers(docs_root: Path) -> dict[str, list[str]]:
    """Every owner that names emails, as handle -> lower-cased emails."""
    registry = docs_root / REGISTRY
    if not registry.exists():
        return {}
    loaded: Any = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
    found: dict[str, list[str]] = {}
    for key, value in (loaded.get("owners") or {}).items():
        if isinstance(value, dict) and value.get("emails"):
            found[str(key)] = [str(email).strip().lower() for email in value["emails"]]
    return found


def git_email(root: Path) -> str:
    """``git config user.email`` in ``root``, lower-cased; empty when unset."""
    result = subprocess.run(["git", "-C", str(root), "config", "user.email"],
                            capture_output=True, text=True, check=False)
    return result.stdout.strip().lower()


def handle(config: paths.Config, env: Mapping[str, str] | None = None) -> str:
    """The current developer's handle, or ``IdentityError`` saying what is missing."""
    env = os.environ if env is None else env
    team = developers(config.path("docs_root"))
    for name in team:
        if not HANDLE_PATTERN.match(name):
            raise IdentityError(f"developer handle {name!r} must match {HANDLE_PATTERN.pattern}")
    chosen = env.get(HANDLE_ENV, "").strip()
    if chosen:
        if chosen not in team:
            raise IdentityError(f"{HANDLE_ENV}={chosen!r} is not a developer in {REGISTRY} owners")
        return chosen
    email = git_email(config.root)
    if not email:
        raise IdentityError("git config user.email is not set, so no developer handle resolves")
    matches = [name for name, emails in team.items() if email in emails]
    if len(matches) != 1:
        reason = "no" if not matches else "more than one"
        raise IdentityError(f"{reason} developer in {REGISTRY} owners lists the email {email!r}")
    return matches[0]


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the current developer's handle.")
    paths.add_arguments(parser, ["docs_root"])
    config = paths.resolve(parser.parse_args(argv))
    try:
        print(handle(config))
    except IdentityError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
