"""Validate documentation and print a live systems/plan inventory.

Run: uv run python -m src.governance [--inventory]
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from jsonschema import Draft7Validator, FormatChecker  # type: ignore[import-untyped]

from src.db.ideas import fold, load_events
from src.db.source_validation import data_root
from src.governance.backlog import inspect_backlog, render_backlog
from src.governance.codes import inspect_codes, inspect_register, next_code, render_catalog
from src.governance.idea_priority import inspect_idea_priority

ROOT = Path(__file__).resolve().parents[2]
# Navigation and the user's execution input are explicitly exempt, not all README files.
# Directories that hold ungoverned material: parked ideas and notes that have not
# earned a code yet. See ADR-010. Anything here is exempt from front-matter rules.
EXEMPT_DIRS = ("docs/00-working/",)

EXEMPT = {
    "docs/README.md",
    "docs/09-backlog/README.md",
    "docs/08-governance/catalog.md",
    "docs/08-governance/GLOSSARY.md",
    *(
        f"docs/{folder}/README.md"
        for folder in (
            "01-plans",
            "02-prompts",
            "03-sessions",
            "04-decisions",
            "05-memories",
            "06-requirements",
            "07-architecture",
            "08-governance",
        )
    ),
    "brain/index.md",
    "docs/02-prompts/codex_governance_prompt.md",
}
MEMORY_DIRS = {
    "concept": "concepts",
    "entity": "entities",
    "procedure": "procedures",
    "episode": "episodes",
    "decision": "decisions",
}


class MetadataLoader(yaml.SafeLoader):  # type: ignore[misc]
    """Keep ISO dates as strings and reject duplicate keys, including YAML merges."""


MetadataLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in entries if tag != "tag:yaml.org,2002:timestamp"]
    for key, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def unique_mapping(loader: MetadataLoader, node: Any) -> dict[str, Any]:
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


MetadataLoader.add_constructor("tag:yaml.org,2002:map", unique_mapping)


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening front matter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing front matter delimiter") from exc
    if not "\n".join(lines[end + 1 :]).strip():
        raise ValueError("document body is empty")
    meta = yaml.load("\n".join(lines[1:end]), Loader=MetadataLoader)
    if not isinstance(meta, dict):
        raise ValueError("front matter must be a mapping")
    return meta


def public_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"expected repository-relative path: {value}")
    current = root
    for part in path.parts:
        if part in {"_private", ".git", "data", ".venv", "node_modules"}:
            raise ValueError(f"path is outside governance scope: {value}")
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink is outside governance scope: {value}")
    return current


def markdown_paths(root: Path, folder: str) -> list[Path]:
    base = public_path(root, folder)
    result = []
    for directory, dirs, files in os.walk(base, followlinks=False):
        for name in dirs:
            public_path(root, (Path(directory) / name).relative_to(root).as_posix())
        for name in sorted(files):
            if name.endswith(".md"):
                path = public_path(root, (Path(directory) / name).relative_to(root).as_posix())
                relative = path.relative_to(root).as_posix()
                if relative not in EXEMPT and not relative.startswith(EXEMPT_DIRS):
                    result.append(path)
    return sorted(result)


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


def audit(root: Path, today: date | None = None) -> tuple[list[str], list[str], dict[str, Any]]:
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    documents: dict[str, Any] = {}
    memories: dict[str, Any] = {}
    result: dict[str, Any] = {"systems": [], "documents": documents, "memories": memories}

    def read(value: str) -> str:
        return public_path(root, value).read_text(encoding="utf-8")

    def validate(value: Any, schema_name: str, location: str) -> bool:
        schema = json.loads(read(f"schemas/{schema_name}.schema.json"))
        Draft7Validator.check_schema(schema)
        issues = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value))
        for issue in issues:
            field = ".".join(str(part) for part in issue.absolute_path)
            errors.append(f"{location}:{field}: {issue.message}")
        return not issues

    def check_dates(meta: dict[str, Any], location: str) -> None:
        created = date.fromisoformat(meta["created"])
        updated = date.fromisoformat(meta.get("updated") or meta["created"])
        if updated < created or updated > today or created > today:
            errors.append(f"{location}: require created <= updated <= today")
        if meta.get("review_after") and date.fromisoformat(meta["review_after"]) < today:
            warnings.append(f"{location}: review overdue since {meta['review_after']}")

    try:
        registry = yaml.load(read("docs/08-governance/systems.yaml"), Loader=MetadataLoader)
        if not validate(registry, "systems", "systems.yaml"):
            return errors, warnings, result
        systems = {item["id"]: item for item in registry["systems"]}
        result["systems"] = registry["systems"]
        if len(systems) != len(registry["systems"]):
            errors.append("systems.yaml: duplicate system ID")
        owners = registry["owners"]
        result["owners"] = owners
        tags = {item["id"] for item in json.loads(read("_data/tags.json"))}
        # d-system is the existing repository memory scope, not a portfolio project row.
        projects = {"d-system"}
        # Deliberately not public_path(): that helper blocks _private/ everywhere else in
        # this module, on purpose, but ADR-009 requires this one lookup to follow
        # D_SYSTEM_DATA_ROOT onto the owner's real records when it is set, and _private/
        # is exactly where those records live.
        project_dir = data_root(root) / "projects"
        if project_dir.is_dir():
            for path in sorted(project_dir.glob("*.json")):
                projects.add(json.loads(path.read_text(encoding="utf-8"))["id"])
        for item in systems.values():
            if item["owner"] not in owners:
                errors.append(f"{item['id']}: unknown owner {item['owner']}")
            if item["status"] in {"implemented", "scaffold"} and not item["paths"]:
                errors.append(f"{item['id']}: implemented/scaffold system requires paths")
            for value in item["paths"]:
                if not public_path(root, value).exists():
                    errors.append(f"{item['id']}: missing path {value}")
            for dependency in item["depends_on"]:
                if dependency not in systems:
                    errors.append(f"{item['id']}: unknown system dependency {dependency}")
        errors.extend(
            cycle_errors({key: value["depends_on"] for key, value in systems.items()}, "systems")
        )
        register = yaml.load(read("docs/08-governance/codes.yaml"), Loader=MetadataLoader)
        if not validate(register, "codes", "codes.yaml"):
            return errors, warnings, result
        result["register"] = register
        kinds = set(json.loads(read("schemas/document.schema.json"))["properties"]["kind"]["enum"])
        errors.extend(inspect_register(register, kinds))
        for folder in ("docs", "brain"):
            for path in markdown_paths(root, folder):
                location = path.relative_to(root).as_posix()
                try:
                    meta = parse_frontmatter(path.read_text(encoding="utf-8"))
                    memory = folder == "brain"
                    if not validate(meta, "memory" if memory else "document", location):
                        continue
                    check_dates(meta, location)
                    collection = memories if memory else documents
                    if meta["id"] in collection:
                        errors.append(f"{location}: duplicate ID {meta['id']}")
                    collection[meta["id"]] = {"path": location, **meta}
                    for tag in meta.get("tags", []):
                        if tag not in tags:
                            errors.append(f"{location}: unknown tag {tag}")
                    if memory:
                        expected = f"brain/{MEMORY_DIRS[meta['type']]}/"
                        if not location.startswith(expected):
                            errors.append(f"{location}: memory type requires {expected}")
                        if meta.get("project") and meta["project"] not in projects:
                            errors.append(f"{location}: unknown project {meta['project']}")
                        if meta.get("scope") == "project" and not meta.get("project"):
                            errors.append(f"{location}: project scope requires project")
                        for system in meta.get("systems", []):
                            if system not in systems:
                                errors.append(f"{location}: unknown system {system}")
                        continue
                    states = {"draft", "active", "deprecated", "superseded"}
                    if meta["kind"] == "plan":
                        states |= {"approved", "complete"}
                    if meta["kind"] == "adr":
                        states = {"draft", "accepted", "deprecated", "superseded"}
                    if meta["status"] not in states:
                        errors.append(f"{location}: invalid status for kind {meta['kind']}")
                    if meta["owner"] not in owners:
                        errors.append(f"{location}: unknown owner {meta['owner']}")
                    for system in meta["systems"]:
                        if system not in systems:
                            errors.append(f"{location}: unknown system {system}")
                    if meta["status"] == "complete" and not meta.get("completion_evidence"):
                        errors.append(f"{location}: complete plan requires completion_evidence")
                    for value in meta.get("completion_evidence", []):
                        if not public_path(root, value).is_file():
                            errors.append(f"{location}: missing evidence file {value}")
                except (ValueError, yaml.YAMLError) as exc:
                    errors.append(f"{location}: {exc}")
        for key, meta in documents.items():
            for ref in (
                meta["depends_on"]
                + meta.get("supersedes", [])
                + ([meta["parent"]] if meta.get("parent") else [])
            ):
                if ref not in documents or ref == key:
                    errors.append(f"{meta['path']}: unresolved or self document reference {ref}")
            parent = documents.get(meta.get("parent"))
            if parent and (parent["kind"] != "plan" or meta["kind"] != "plan"):
                errors.append(f"{meta['path']}: parent is only valid between plans")
            for ref in meta.get("supersedes", []):
                if ref in documents and documents[ref]["status"] != "superseded":
                    errors.append(f"{meta['path']}: replaced document {ref} must be superseded")
            if meta["status"] == "superseded" and not any(
                key in other.get("supersedes", []) for other in documents.values()
            ):
                errors.append(f"{meta['path']}: superseded document has no replacement")
        for relation in ("depends_on", "supersedes", "parent"):
            graph = {
                key: ([meta["parent"]] if meta.get("parent") else [])
                if relation == "parent"
                else meta.get(relation, [])
                for key, meta in documents.items()
            }
            errors.extend(cycle_errors(graph, f"documents {relation}"))
        errors.extend(inspect_codes(register, documents, strict=True))
        for meta in memories.values():
            for ref in meta.get("related", []):
                if ref not in memories:
                    errors.append(f"{meta['path']}: unknown related memory {ref}")
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        errors.append(f"governance inputs: {exc}")
    return sorted(errors), sorted(warnings), result


def inventory(result: dict[str, Any]) -> str:
    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Live systems inventory",
        "",
        "| System | Domain | Maturity | Owner |",
        "|---|---|---|---|",
    ]
    for item in sorted(result["systems"], key=lambda entry: entry["id"]):
        lines.append(f"| {item['id']} | {item['domain']} | {item['status']} | {item['owner']} |")
    lines += [
        "",
        "## Open plans (draft, approved, active)",
        "",
        "| Plan | Status | Owner | Path |",
        "|---|---|---|---|",
    ]
    for key, meta in sorted(result["documents"].items()):
        if meta["kind"] == "plan" and meta["status"] in {"draft", "approved", "active"}:
            lines.append(f"| {key} | {meta['status']} | {meta['owner']} | {cell(meta['path'])} |")
    lines += ["", f"Documents: {len(result['documents'])}; memories: {len(result['memories'])}."]
    return "\n".join(lines)


def audit_backlog(
    root: Path, result: dict[str, Any], today: date | None = None
) -> tuple[list[str], dict[str, Any]]:
    """Validate the required backlog file after the documentation audit succeeds."""
    try:
        schema = json.loads(public_path(root, "schemas/backlog.schema.json").read_text())
        Draft7Validator.check_schema(schema)
        catalog = yaml.load(
            public_path(root, "docs/09-backlog/backlog.yaml").read_text(), Loader=MetadataLoader
        )
        issues = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(catalog))
        if issues:
            return [
                f"backlog:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
                for issue in issues
            ], {}
        errors = inspect_backlog(
            catalog,
            result["documents"],
            {item["id"] for item in result["systems"]},
            set(result["owners"]),
            lambda path: public_path(root, path).is_file(),
            today or date.today(),
        )
        return errors, catalog
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        return [f"backlog inputs: {exc}"], {}


def audit_idea_priority(root: Path, today: date | None = None) -> list[str]:
    """Validate docs/00-working/ideas-priority.yaml against the current idea log."""
    try:
        schema = json.loads(public_path(root, "schemas/idea-priority.schema.json").read_text())
        Draft7Validator.check_schema(schema)
        catalog = yaml.load(
            public_path(root, "docs/00-working/ideas-priority.yaml").read_text(),
            Loader=MetadataLoader,
        )
        issues = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(catalog))
        if issues:
            return [
                f"ideas-priority:{'.'.join(map(str, issue.absolute_path))}: {issue.message}"
                for issue in issues
            ]
        ideas = fold(load_events(public_path(root, "_data/ideas.jsonl")))
        return inspect_idea_priority(catalog, ideas, today or date.today())
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        return [f"ideas-priority inputs: {exc}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--inventory", action="store_true", help="Print derived Markdown inventory")
    output.add_argument(
        "--backlog", action="store_true", help="Print phases and source plan coverage"
    )
    output.add_argument("--ready", action="store_true", help="Print phases ready for one session")
    output.add_argument("--catalog", action="store_true", help="Print the generated code catalog")
    output.add_argument("--next-code", metavar="KIND", help="Print the next free code for a kind")
    parser.add_argument("--parent", metavar="DOC_ID", help="Allocate a sub-code under this plan")
    args = parser.parse_args()
    if args.parent and not args.next_code:
        parser.error("--parent only applies to --next-code")
    errors, warnings, result = audit(ROOT)
    catalog: dict[str, Any] = {}
    if not errors:
        backlog_errors, catalog = audit_backlog(ROOT, result)
        errors.extend(backlog_errors)
        errors.extend(audit_idea_priority(ROOT))
    for warning in warnings:
        print(f"WARNING {warning}")
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        return 1
    if args.next_code:
        try:
            print(next_code(args.next_code, result["register"], result["documents"], args.parent))
        except ValueError as exc:
            print(f"ERROR {exc}")
            return 1
    elif args.backlog or args.ready:
        print(render_backlog(catalog, result["documents"], ready_only=args.ready))
    elif args.catalog:
        print(render_catalog(result["register"], result["documents"], catalog["items"]))
    elif args.inventory:
        print(inventory(result))
    else:
        print(
            f"Governance OK: {len(result['systems'])} systems, "
            f"{len(result['documents'])} documents, {len(result['memories'])} memories, "
            f"{len(catalog['items'])} backlog phases"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
