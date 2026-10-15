# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""The product repository this control repository drives.

The control repository holds every governed record: ideas, plans, the backlog, session and review
records. The code is built in a separate product repository. What is the same on every machine is
tracked in ``.idea-realization/product.yaml``::

    schema_version: 1
    name: <product name>
    integration_branch: main
    ci_workflow: none
    remote: <git URL of the product repository>   # optional
    github: <org>/<repo>                          # optional

The repository's URL and GitHub name are the ``product_remote`` and ``product_github`` keys
(``paths.py``): ``--product-remote``, then ``IDEA_REALIZATION_PRODUCT_REMOTE``, then this machine's
untracked ``.idea-realization/local.yaml``, then the plugin option, then the tracked ``remote`` and
``github`` above. A team whose URL names a confidential organization leaves them out of
``product.yaml`` and sets them in ``local.yaml`` on every machine.

Where the product checkout sits differs per machine, so it is configured, never tracked: the
``product_root`` key (``--product-root``, ``IDEA_REALIZATION_PRODUCT_ROOT``, ``local.yaml``, then
the plugin option). ``product_worktree_dir`` names where product worktrees go, beside the product
checkout.

A declared path names its repository with a prefix: ``product:src/api/`` is a path in the product
repository, and a path with no prefix is a path in the control repository.

Before any script acts on the product checkout it calls ``verify``, which refuses unless the
checkout's ``origin`` is the resolved ``product_remote``, so a wrong path cannot send work into the
wrong repository. While ``product_remote`` is unset (or a ``REPLACE-WITH-`` placeholder) ``verify``
refuses and names ``local.yaml``; ``show`` prints it as not set.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paths  # noqa: E402

RECORD = Path(".idea-realization") / "product.yaml"
SCHEMA = paths.PLUGIN_ROOT / "schemas" / "product.schema.json"
PREFIX = "product:"
CONTROL_PREFIX = "control:"
LOCAL_HINT = paths.LOCAL_RECORD.as_posix()


class ProductError(ValueError):
    """The product repository is not configured, or does not match the tracked record."""


@dataclass(frozen=True)
class Product:
    name: str
    remote: str
    integration_branch: str
    ci_workflow: str
    root: Path
    worktree_dir: Path
    github: str = ""


def split(value: str) -> tuple[str, str]:
    """``("product", path)`` for a ``product:`` path, else ``("control", path)``."""
    if value.startswith(PREFIX):
        return "product", value.removeprefix(PREFIX)
    return "control", value


def split_command(command: str) -> tuple[str, str]:
    """Where a verification command runs: the product worktree unless prefixed ``control:``."""
    if command.startswith(CONTROL_PREFIX):
        return "control", command.removeprefix(CONTROL_PREFIX).strip()
    return "product", command


def record_errors(record: object) -> list[str]:
    """Schema problems in a loaded ``product.yaml``, one line each."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return [f"{RECORD.as_posix()}:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
            for issue in Draft7Validator(schema).iter_errors(record)]


def read_record(root: Path) -> dict[str, str] | None:
    """The tracked record, or None when this repository drives no product repository."""
    location = root / RECORD
    if not location.is_file():
        return None
    loaded = yaml.safe_load(location.read_text(encoding="utf-8"))
    errors = record_errors(loaded)
    if errors:
        raise ProductError("; ".join(errors))
    return dict(loaded)


def normalise_remote(url: str) -> str:
    """Compare remotes without a trailing ``.git`` or slash, and without the URL scheme form."""
    url = url.strip().rstrip("/")
    url = url.removesuffix(".git")
    # git@host:owner/repo and https://host/owner/repo name the same repository.
    match = re.match(r"^[\w.-]+@([\w.-]+):(.+)$", url)
    if match:
        return f"{match.group(1)}/{match.group(2)}".lower()
    return re.sub(r"^[a-z+]+://([^@/]+@)?", "", url).lower()


def load(config: paths.Config) -> Product:
    """The configured product repository, unverified. ``ProductError`` names what is missing."""
    record = read_record(config.root)
    if record is None:
        raise ProductError(f"{RECORD.as_posix()} does not exist: no product repository is set up")
    root = config.product_root()
    if root is None:
        raise ProductError(f"product_root is not set on this machine (set it in {LOCAL_HINT}, "
                           "--product-root or IDEA_REALIZATION_PRODUCT_ROOT): no product "
                           "checkout is known")
    if not root.is_dir():
        raise ProductError(f"product_root {root} is not a directory")
    worktrees = config.product_worktree_dir(root)
    return Product(record["name"], config.text("product_remote"), record["integration_branch"],
                   record.get("ci_workflow", "none"), root, worktrees,
                   config.text("product_github"))


def origin(root: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def verify(config: paths.Config) -> Product:
    """The product repository, after confirming its checkout's ``origin`` is ``product_remote``."""
    product = load(config)
    if not product.remote:
        raise ProductError(f"product_remote is not set on this machine: set it in {LOCAL_HINT} "
                           "(or IDEA_REALIZATION_PRODUCT_REMOTE); refusing to act on a product "
                           "checkout whose repository cannot be confirmed")
    found = origin(product.root)
    if not found:
        raise ProductError(f"{product.root} has no origin remote; expected {product.remote}")
    if normalise_remote(found) != normalise_remote(product.remote):
        raise ProductError(f"{product.root} has origin {found}, but product_remote (from "
                           f"{config.sources.get('product_remote', '?')}) is {product.remote}: "
                           "refusing to act on the wrong repository")
    return product


def verified_root(config: paths.Config) -> tuple[Path | None, str | None]:
    """The product checkout for a check to read: ``(root, None)`` once verified, ``(None, None)``
    when this machine has no product checkout configured, and ``(None, reason)`` when one is
    configured but refused. A check never reads product paths from a refused checkout."""
    if read_record(config.root) is None or config.product_root() is None:
        return None, None
    try:
        return verify(config).root, None
    except ProductError as error:
        return None, str(error)


def resolve(config: paths.Config, value: str) -> tuple[str, Path | None]:
    """Where a declared path lives: (repository, absolute path), with None for an unconfigured
    product checkout. The path is not checked for existence."""
    repository, relative = split(value)
    if repository == "control":
        return repository, config.root / relative
    root, _ = verified_root(config)
    return repository, None if root is None else root / relative


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Show the product repository and check that its checkout matches the record.")
    parser.add_argument("command", choices=("show", "verify"))
    paths.add_arguments(parser, ["product_root", "product_worktree_dir", "product_remote",
                                 "product_github"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    try:
        product = verify(config) if args.command == "verify" else load(config)
    except ProductError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"name: {product.name}")
    print(f"remote: {product.remote or '(not set: product_remote in ' + LOCAL_HINT + ')'}"
          + (f"  (from {config.sources['product_remote']})" if product.remote else ""))
    print(f"integration_branch: {product.integration_branch}")
    print(f"ci_workflow: {product.ci_workflow}")
    print(f"github: {product.github or '(not set)'}"
          + (f"  (from {config.sources['product_github']})" if product.github else ""))
    print(f"root: {product.root}")
    print(f"worktree_dir: {product.worktree_dir}")
    if args.command == "verify":
        print("origin: matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
