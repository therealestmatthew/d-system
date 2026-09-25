# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Scan the governed document tree, check it, and render its catalog.

Run directly, this script is the ``catalog`` command: it scans the document root and, when the
tree is clean, writes ``<docs_root>/catalog.md``. The ``check`` command compares that committed
file with a fresh render, so a hand-edited or stale catalog fails.

What the scan reads, all under the configured document root (``docs_root``):

- every Markdown file, except ``catalog.md`` and the configured ``exempt_files``, as a governed
  document whose YAML front matter must satisfy ``schemas/document.schema.json``;
- ``codes.yaml``, the code register (``schemas/codes.schema.json``);
- ``systems.yaml``, the systems registry and owner directory (``schemas/systems.schema.json``).

**The contract other features rely on.** ``scan(config)`` returns a ``Scan``:

- ``documents`` — ``{document id: front matter}`` for every governed document, each mapping
  carrying two added keys: ``path``, the file's path relative to the repository root, and
  ``location``, its path relative to the document root;
- ``systems`` — ``{system id: registry entry}``;
- ``owners`` — ``{owner key: accountable role}``;
- ``register`` — the parsed code register;
- ``errors`` — every problem found, one line each; empty when the tree is clean.

A consumer, such as the backlog check, resolves document ids, system ids and owner keys against
these three mappings rather than scanning the tree itself, so there is one scanner.

Exit codes: 0 when the catalog was written; 1 when the document tree fails its check, in which
case nothing is written; 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import codes
import paths
import yaml
from jsonschema import Draft7Validator, FormatChecker

CATALOG = "catalog.md"
REGISTER = "codes.yaml"
REGISTRY = "systems.yaml"

#: The lifecycle statuses each kind may use. The schema's ``status`` enum is their union; this
#: table is the one place a kind's own subset is stated.
LIFECYCLE: dict[str, frozenset[str]] = {
    "plan": frozenset({"draft", "approved", "active", "complete", "deprecated", "superseded"}),
    "adr": frozenset({"draft", "accepted", "deprecated", "superseded"}),
    **{
        kind: frozenset({"draft", "active", "deprecated", "superseded"})
        for kind in ("architecture", "requirement", "prompt", "operation", "governance",
                     "session", "walkthrough")
    },
}


class MetadataLoader(yaml.SafeLoader):  # type: ignore[misc]
    """Keep ISO dates as strings and reject duplicate keys, including YAML merges."""


MetadataLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in entries if tag != "tag:yaml.org,2002:timestamp"]
    for key, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _unique_mapping(loader: MetadataLoader, node: Any) -> dict[str, Any]:
    loader.flatten_mapping(node)
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ValueError("YAML keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


MetadataLoader.add_constructor("tag:yaml.org,2002:map", _unique_mapping)


def load_yaml(text: str) -> Any:
    return yaml.load(text, Loader=MetadataLoader)


def parse_frontmatter(text: str) -> dict[str, Any]:
    """The YAML mapping between the opening and closing ``---``; the body must not be empty."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening front matter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing front matter delimiter") from exc
    if not "\n".join(lines[end + 1:]).strip():
        raise ValueError("document body is empty")
    meta = load_yaml("\n".join(lines[1:end]))
    if not isinstance(meta, dict):
        raise ValueError("front matter must be a mapping")
    return meta


def schema(name: str) -> dict[str, Any]:
    """One of the plugin's own schemas, read when first needed rather than at import."""
    loaded: dict[str, Any] = json.loads(
        (paths.PLUGIN_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8")
    )
    return loaded


def validate(value: Any, name: str, location: str) -> list[str]:
    validator = Draft7Validator(schema(name), format_checker=FormatChecker())
    return [
        f"{location}:{'.'.join(str(part) for part in issue.absolute_path)}: {issue.message}"
        for issue in sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))
    ]


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def markdown_files(config: paths.Config) -> tuple[list[Path], list[str]]:
    """Every governed Markdown file under the document root, and every symlink refused.

    Symlinks are never followed: a link could pull a file from outside the repository into the
    scan, so each one is reported rather than read.
    """
    docs_root = config.path("docs_root")
    exempt = {path.resolve() for path in config.paths("exempt_files")}
    exempt.add((docs_root / CATALOG).resolve())
    found: list[Path] = []
    refused: list[str] = []
    if not docs_root.is_dir():
        return found, refused
    for directory, dirs, files in os.walk(docs_root, followlinks=False):
        for name in sorted(dirs):
            if (Path(directory) / name).is_symlink():
                refused.append(f"{_relative(config.root, Path(directory) / name)}: "
                               "symlink is not followed")
        for name in sorted(files):
            path = Path(directory) / name
            if not name.endswith(".md"):
                continue
            if path.is_symlink():
                refused.append(f"{_relative(config.root, path)}: symlink is not followed")
                continue
            if path.resolve() not in exempt:
                found.append(path)
    return sorted(found), refused


def cycle_errors(graph: dict[str, list[str]], label: str) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    errors = []

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"{label}: dependency cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return errors


@dataclass
class Scan:
    """Everything the document root holds, and every problem found in it."""

    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    systems: dict[str, dict[str, Any]] = field(default_factory=dict)
    owners: dict[str, str] = field(default_factory=dict)
    register: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _read_registers(config: paths.Config, result: Scan) -> bool:
    """Load and check the systems registry and the code register. False when either is unusable."""
    docs_root = config.path("docs_root")
    loaded: dict[str, Any] = {}
    for name, filename in (("systems", REGISTRY), ("codes", REGISTER)):
        path = docs_root / filename
        location = _relative(config.root, path)
        if not path.is_file():
            result.errors.append(f"{location}: missing; run the scaffold for the documents feature")
            continue
        try:
            value = load_yaml(path.read_text(encoding="utf-8"))
        except (ValueError, yaml.YAMLError) as exc:
            result.errors.append(f"{location}: {exc}")
            continue
        problems = validate(value, name, location)
        result.errors.extend(problems)
        if not problems:
            loaded[name] = value
    if len(loaded) != 2:
        return False

    registry = loaded["systems"]
    result.owners = dict(registry["owners"])
    result.systems = {item["id"]: item for item in registry["systems"]}
    location = _relative(config.root, docs_root / REGISTRY)
    if len(result.systems) != len(registry["systems"]):
        result.errors.append(f"{location}: duplicate system id")
    for item in result.systems.values():
        if item["owner"] not in result.owners:
            result.errors.append(f"{item['id']}: unknown owner {item['owner']}")
        if item["status"] in {"implemented", "scaffold"} and not item["paths"]:
            result.errors.append(f"{item['id']}: implemented or scaffold system requires paths")
        for value in item["paths"]:
            if not (config.root / value).exists():
                result.errors.append(f"{item['id']}: missing path {value}")
        for dependency in item["depends_on"]:
            if dependency not in result.systems:
                result.errors.append(f"{item['id']}: unknown system dependency {dependency}")
    result.errors.extend(cycle_errors(
        {key: value["depends_on"] for key, value in result.systems.items()}, "systems"
    ))

    result.register = loaded["codes"]
    kinds = set(schema("document")["properties"]["kind"]["enum"])
    result.errors.extend(codes.inspect_register(result.register, kinds))
    return True


def _check_document(config: paths.Config, meta: dict[str, Any], location: str,
                    result: Scan, today: date) -> None:
    created = date.fromisoformat(meta["created"])
    updated = date.fromisoformat(meta["updated"])
    if updated < created or updated > today or created > today:
        result.errors.append(f"{location}: require created <= updated <= today")
    if meta["status"] not in LIFECYCLE[meta["kind"]]:
        result.errors.append(f"{location}: invalid status {meta['status']} for kind {meta['kind']}")
    if meta["owner"] not in result.owners:
        result.errors.append(f"{location}: unknown owner {meta['owner']}")
    for system in meta["systems"]:
        if system not in result.systems:
            result.errors.append(f"{location}: unknown system {system}")
    if meta["status"] == "complete" and not meta.get("completion_evidence"):
        result.errors.append(f"{location}: complete document requires completion_evidence")
    for value in meta.get("completion_evidence", []):
        evidence = Path(value)
        if evidence.is_absolute() or ".." in evidence.parts or not \
                (config.root / evidence).is_file():
            result.errors.append(f"{location}: missing evidence file {value}")


def _check_references(result: Scan) -> None:
    documents = result.documents
    for key, meta in documents.items():
        refs = (meta["depends_on"] + meta.get("supersedes", [])
                + ([meta["parent"]] if meta.get("parent") else []))
        for ref in refs:
            if ref not in documents or ref == key:
                result.errors.append(f"{meta['path']}: unresolved or self document reference {ref}")
        parent = documents.get(meta.get("parent", ""))
        if parent and (parent["kind"] != "plan" or meta["kind"] != "plan"):
            result.errors.append(f"{meta['path']}: parent is only valid between plans")
        for ref in meta.get("supersedes", []):
            if ref in documents and documents[ref]["status"] != "superseded":
                result.errors.append(f"{meta['path']}: replaced document {ref} must be superseded")
        if meta["status"] == "superseded" and not any(
            key in other.get("supersedes", []) for other in documents.values()
        ):
            result.errors.append(f"{meta['path']}: superseded document has no replacement")
    for relation in ("depends_on", "supersedes", "parent"):
        graph = {
            key: ([meta["parent"]] if meta.get("parent") else [])
            if relation == "parent" else meta.get(relation, [])
            for key, meta in documents.items()
        }
        result.errors.extend(cycle_errors(graph, f"documents {relation}"))


def scan(config: paths.Config, today: date | None = None) -> Scan:
    """Read and check the registers and every governed document. See the module docstring."""
    today = today or date.today()
    result = Scan()
    if not _read_registers(config, result):
        return result
    docs_root = config.path("docs_root")
    files, refused = markdown_files(config)
    result.errors.extend(refused)
    for path in files:
        location = _relative(config.root, path)
        try:
            meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            result.errors.append(f"{location}: {exc}")
            continue
        problems = validate(meta, "document", location)
        if problems:
            result.errors.extend(problems)
            continue
        if meta["id"] in result.documents:
            result.errors.append(f"{location}: duplicate id {meta['id']}")
            continue
        _check_document(config, meta, location, result, today)
        result.documents[meta["id"]] = {
            **meta, "path": location, "location": _relative(docs_root, path),
        }
    _check_references(result)
    result.errors.extend(codes.inspect_codes(result.register, result.documents))
    result.errors = sorted(result.errors)
    return result


def kinds_by_id(config: paths.Config) -> dict[str, str]:
    """Each readable document's kind, by id, without checking anything else.

    For callers that need one fact from front matter, such as ``plan_check.py`` resolving a
    ``depends_on`` id, on a tree that may not yet pass the full check.
    """
    found: dict[str, str] = {}
    for path in markdown_files(config)[0]:
        try:
            meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError):
            continue
        if isinstance(meta.get("id"), str) and isinstance(meta.get("kind"), str):
            found[meta["id"]] = meta["kind"]
    return found


def backlog_items(config: paths.Config) -> list[dict[str, Any]] | None:
    """The backlog's phases when the repository has a backlog file, else None."""
    path = config.path("backlog_path")
    if not path.is_file():
        return None
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = loaded.get("items", []) if isinstance(loaded, dict) else []
    return [item for item in items if isinstance(item, dict)]


def render(config: paths.Config, result: Scan) -> str:
    return codes.render_catalog(result.register, result.documents, backlog_items(config))


def catalog_path(config: paths.Config) -> Path:
    return config.path("docs_root") / CATALOG


def check(config: paths.Config, today: date | None = None) -> list[str]:
    """Every problem in the document tree; when there are none, whether the catalog is current.

    A repository where the documents feature was never set up, with neither register under the
    document root, has nothing to check and reports nothing.
    """
    docs_root = config.path("docs_root")
    if not (docs_root / REGISTER).exists() and not (docs_root / REGISTRY).exists():
        return []
    result = scan(config, today)
    if result.errors:
        return result.errors
    try:
        rendered = render(config, result)
    except (OSError, yaml.YAMLError, AttributeError) as exc:
        return [f"{_relative(config.root, config.path('backlog_path'))}: {exc}"]
    target = catalog_path(config)
    location = _relative(config.root, target)
    if not target.is_file():
        return [f"{location}: is missing; run the catalog command and commit it"]
    if target.read_text(encoding="utf-8") != rendered:
        return [f"{location}: differs from the rendered catalog; run the catalog command and "
                "commit it, and never edit it by hand"]
    return []


def write_catalog(target: Path, rendered: str) -> None:
    """Write atomically, so a reader never sees half a catalog."""
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=".catalog-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        os.replace(tmp_name, target)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="catalog",
        description="Regenerate <docs_root>/catalog.md from the governed documents, the code "
                    "register and, when one exists, the backlog. Writes nothing when the "
                    "document tree fails its check.",
    )
    paths.add_arguments(parser, ["docs_root", "exempt_files", "backlog_path"])
    config = paths.resolve(parser.parse_args(argv))
    result = scan(config)
    if result.errors:
        for error in result.errors:
            print(error, file=sys.stderr)
        print("catalog not written: fix the document tree first", file=sys.stderr)
        return 1
    target = catalog_path(config)
    write_catalog(target, render(config, result))
    print(f"wrote {_relative(config.root, target)} ({len(result.documents)} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
