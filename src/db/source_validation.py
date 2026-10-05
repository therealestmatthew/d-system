"""Validate every source file before the rebuild touches the database.

`tools/rebuild_db.py` drops every table and recreates it. Until this preflight existed
it did that first and discovered bad input afterwards, which turned one malformed file
into an empty database. Worse, a brain memory with unreadable front matter was skipped
in silence — the rebuild reported success with the entry missing.

So the contract here is narrow and deliberate: read entity content (`data_root()`, honouring
`D_SYSTEM_DATA_ROOT`), `_data/tags.json`, `_data/ideas.jsonl` and `brain/`, validate them
against the schemas in `schemas/`, and return every problem found with the file and the
field that caused it. Nothing in this module connects to DuckDB, creates `data/`, or
stops at the first error — a caller fixing source files wants the whole list.

Schemas see one record at a time, so two checks run across records afterwards
(`validate_identities`): every reference to a tag, project, person, commitment or memory
must name a record that exists, and no two records of one kind may share an ID. Both name
every source record involved.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from jsonschema import Draft7Validator  # type: ignore[import-untyped]
from referencing import Registry, Resource

from src.db.ideas import IdeaError, fold

ROOT = Path(__file__).resolve().parents[2]


def data_root(root: Path) -> Path:
    """Resolve where entity content actually lives: `D_SYSTEM_DATA_ROOT` if set, else
    `root / "_data"`.

    Per ADR-009, `_data/tags.json` and `_data/ideas.jsonl` are shared taxonomy and
    development-process data, not portfolio content, so they are read from the tracked
    `_data/` unconditionally and never go through this function. Only the entity
    directories in `ENTITY_DIRECTORIES` (projects, people, commitments, tasks, ...)
    honour the override — that is what lets a fresh clone validate against the tracked
    fictional set while the owner's own machine validates the real one.
    """
    override = os.environ.get("D_SYSTEM_DATA_ROOT")
    if not override:
        return root / "_data"
    path = Path(override)
    return path if path.is_absolute() else root / path

#: Source directory -> the schema each file in it must satisfy. A directory that does
#: not exist yet is not an error; the capture pipeline creates them as records appear.
ENTITY_DIRECTORIES: dict[str, str] = {
    "projects": "project",
    "people": "person",
    "commitments": "commitment",
    "tasks": "task",
    "interactions": "interaction",
    "decisions": "decision",
    "waiting-on": "waiting-on",
    "development-events": "development-event",
}

#: Files under brain/ that carry no memory front matter by design.
BRAIN_EXCLUDED = {"index.md"}

#: The memory `project` value for this repository itself. It is a repository scope, not a
#: portfolio project, so no `_data/projects/` record backs it (ADR-001) and none should.
REPOSITORY_MEMORY_SCOPE = "d-system"

#: Record kind -> (field, kind it refers to). A field holds either one ID or a list of
#: them; null and absent mean "no reference". `promised_to` and `owed_by` are left out on
#: purpose: their schemas allow the name as written until an identity is confirmed
#: (ADR-008), so an unknown value there is not an error.
REFERENCES: dict[str, tuple[tuple[str, str], ...]] = {
    "tag": (("related", "tag"),),
    "project": (("tags", "tag"), ("stakeholders", "person")),
    "person": (("projects", "project"),),
    "commitment": (("project_id", "project"), ("tags", "tag")),
    "task": (("commitment_id", "commitment"), ("project_id", "project"), ("tags", "tag")),
    "interaction": (("project_id", "project"), ("participants", "person"), ("tags", "tag")),
    "decision": (("project_id", "project"), ("decided_by", "person"), ("tags", "tag")),
    "waiting-on": (("project_id", "project"), ("tags", "tag")),
    "development-event": (("project_id", "project"), ("tags", "tag")),
    "memory": (("project", "project"), ("tags", "tag"), ("related", "memory")),
}


@dataclass(frozen=True)
class SourceError:
    """One problem in one file. `field` is empty when the file itself is unreadable."""

    path: str
    field: str
    message: str

    def __str__(self) -> str:
        location = f"{self.path}: {self.field}" if self.field else self.path
        return f"{location}: {self.message}"


@dataclass(frozen=True)
class SourceRecord:
    """One record that passed its schema, kept for the cross-record checks."""

    kind: str
    path: str
    document: dict[str, Any]


def _registry(schemas: Path) -> Registry[Any]:
    """Resolve cross-file $refs by filename, which is the $id each schema declares."""
    return Registry().with_resources(
        (path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in schemas.glob("*.schema.json")
    )


class _Validators:
    """Schemas are read once per run and shared across every file they validate."""

    def __init__(self, schemas: Path) -> None:
        self._schemas = schemas
        self._registry = _registry(schemas)
        self._cache: dict[str, Draft7Validator] = {}

    def get(self, name: str) -> Draft7Validator:
        if name not in self._cache:
            schema = json.loads(
                (self._schemas / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            self._cache[name] = Draft7Validator(
                schema,
                registry=self._registry,
                # Without this, "2026-13-45" is just a string and a bad date reaches
                # DuckDB as a cast failure mid-insert, after the tables are gone.
                format_checker=Draft7Validator.FORMAT_CHECKER,
            )
        return self._cache[name]


def _field_of(error: Any) -> str:
    """Name the field an error is about.

    An additionalProperties error carries no instance path — it is raised against the
    object, not the offending key — so the unexpected keys are recovered from the
    subschema. Without this the diagnostic would say only that a file is invalid.
    """
    if error.absolute_path:
        return ".".join(str(part) for part in error.absolute_path)
    if error.validator == "additionalProperties" and isinstance(error.instance, dict):
        unexpected = set(error.instance) - set(error.schema.get("properties", {}))
        if unexpected:
            return ", ".join(sorted(unexpected))
    return ""


def _validate(
    validators: _Validators, schema: str, document: Any, path: str
) -> list[SourceError]:
    return [
        SourceError(path, _field_of(error), error.message)
        for error in validators.get(schema).iter_errors(document)
    ]


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def validate_entities(
    root: Path, validators: _Validators, records: list[SourceRecord] | None = None
) -> list[SourceError]:
    """Every JSON file under the entity content root, against the schema its directory
    implies. `tags.json` is shared taxonomy (ADR-009) and always read from the tracked
    `_data/`, independent of `data_root()`.

    Each record that passes its schema is appended to `records`, when given.
    """
    errors: list[SourceError] = []
    data = data_root(root)

    tags_path = root / "_data" / "tags.json"
    if tags_path.exists():
        name = _relative(tags_path, root)
        try:
            tags = json.loads(tags_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(SourceError(name, "", f"invalid JSON: {exc}"))
        else:
            if not isinstance(tags, list):
                errors.append(SourceError(name, "", "expected a list of tags"))
            else:
                for index, tag in enumerate(tags):
                    location = f"{name}[{index}]"
                    tag_errors = _validate(validators, "tag", tag, location)
                    errors.extend(tag_errors)
                    if not tag_errors and records is not None:
                        records.append(SourceRecord("tag", location, tag))

    for directory, schema in ENTITY_DIRECTORIES.items():
        source = data / directory
        if not source.is_dir():
            continue
        for path in sorted(source.glob("*.json")):
            name = _relative(path, root)
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(SourceError(name, "", f"invalid JSON: {exc}"))
                continue
            document_errors = _validate(validators, schema, document, name)
            errors.extend(document_errors)
            if not document_errors and records is not None:
                records.append(SourceRecord(schema, name, document))
    return errors


def split_front_matter(text: str) -> tuple[str, str] | None:
    """Split a brain entry into its YAML front matter and its body.

    Returns None when the file has no front matter at all, which the caller reports
    rather than skipping — a memory the rebuild cannot read is a memory that silently
    disappears from the database.
    """
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def _normalize_yaml_dates(value: Any) -> Any:
    """Render YAML's date objects back as ISO strings so the schema can check them.

    Brain entries write `created: 2026-09-05` unquoted, and PyYAML resolves that to a
    `datetime.date` rather than the string the schema declares. Converting is lossless
    and cannot hide a bad date: YAML only produces a date object for something it
    already parsed as one, so `2026-13-45` stays a string and still fails the format
    check below.
    """
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _normalize_yaml_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_yaml_dates(item) for item in value]
    return value


def validate_memories(
    root: Path, validators: _Validators, records: list[SourceRecord] | None = None
) -> list[SourceError]:
    """Every brain entry's front matter, against `schemas/memory.schema.json`.

    Each entry that passes is appended to `records`, when given.
    """
    errors: list[SourceError] = []
    brain = root / "brain"
    if not brain.is_dir():
        return errors

    for path in sorted(brain.rglob("*.md")):
        if path.name in BRAIN_EXCLUDED:
            continue
        name = _relative(path, root)
        split = split_front_matter(path.read_text(encoding="utf-8"))
        if split is None:
            errors.append(SourceError(name, "", "missing YAML front matter"))
            continue
        try:
            meta = yaml.safe_load(split[0])
        except yaml.YAMLError as exc:
            errors.append(SourceError(name, "", f"unreadable front matter: {exc}"))
            continue
        if meta is None:
            errors.append(SourceError(name, "", "empty front matter"))
            continue
        if not isinstance(meta, dict):
            errors.append(SourceError(name, "", "front matter is not a mapping"))
            continue
        meta = _normalize_yaml_dates(meta)
        meta_errors = _validate(validators, "memory", meta, name)
        errors.extend(meta_errors)
        if not meta_errors and records is not None:
            records.append(SourceRecord("memory", name, meta))
    return errors


def validate_ideas(root: Path, validators: _Validators) -> list[SourceError]:
    """Every line of `_data/ideas.jsonl`, against `schemas/idea.schema.json`.

    The log is append-only, so a line that reaches it is permanent — there is no correction
    path, only a longer history containing the mistake. Validating here means a hand-edited
    or hand-appended line is caught before the projection reads it, rather than after.

    History is checked too, with the same replay `tools/append_idea.py` and
    `tools/rebuild_db.py` use: an event about an idea with no preceding `created`, a `status`
    event whose `from` does not match the status the replay actually reached, an illegal
    transition, a duplicate `created` or a second `revisited` each fail here, before the
    rebuild drops a table — a schema validating one line at a time cannot see any of them.
    """
    errors: list[SourceError] = []
    log = root / "_data" / "ideas.jsonl"
    if not log.exists():
        return errors

    name = _relative(log, root)
    events: list[Any] = []
    for number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        location = f"{name}:{number}"
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(SourceError(location, "", f"invalid JSON: {exc}"))
            continue
        line_errors = _validate(validators, "idea", event, location)
        errors.extend(line_errors)
        if not line_errors and isinstance(event, dict):
            events.append(event)

    if not errors:
        try:
            fold(events)
        except IdeaError as exc:
            errors.append(SourceError(name, "", str(exc)))
    return errors


def _referenced_ids(value: Any) -> list[tuple[str, str]]:
    """(suffix, id) pairs for one reference field: `[i]` per list item, `` for a scalar."""
    if isinstance(value, str):
        return [("", value)]
    if isinstance(value, list):
        return [(f"[{i}]", item) for i, item in enumerate(value) if isinstance(item, str)]
    return []


def validate_identities(records: Iterable[SourceRecord]) -> list[SourceError]:
    """Cross-record checks no single-record schema can make.

    A duplicate ID within one kind is reported on every record after the first, naming
    the first — two task files claiming `t-1` under different commitments both appear.
    An unknown reference is reported on the record holding it, naming the field and the
    missing ID. A memory's `project` may also be `REPOSITORY_MEMORY_SCOPE`.

    Only records that passed their schema arrive here, so a malformed file is reported
    once, by its schema, and not again as a cascade of broken references.
    """
    records = list(records)
    errors: list[SourceError] = []
    known: dict[str, dict[str, str]] = {}
    for record in records:
        identifier = record.document.get("id")
        if not isinstance(identifier, str):
            continue
        first = known.setdefault(record.kind, {}).setdefault(identifier, record.path)
        if first != record.path:
            errors.append(
                SourceError(
                    record.path,
                    "id",
                    f"duplicate {record.kind} ID '{identifier}', also defined in {first}",
                )
            )

    for record in records:
        for field, target in REFERENCES.get(record.kind, ()):
            for suffix, identifier in _referenced_ids(record.document.get(field)):
                if identifier in known.get(target, {}):
                    continue
                if (
                    record.kind == "memory"
                    and field == "project"
                    and identifier == REPOSITORY_MEMORY_SCOPE
                ):
                    continue
                errors.append(
                    SourceError(
                        record.path, f"{field}{suffix}", f"unknown {target} '{identifier}'"
                    )
                )
    return errors


def validate_sources(root: Path | None = None) -> list[SourceError]:
    """Validate every source file. Returns an empty list when the tree is loadable.

    Reads only `_data/`, `brain/` and `schemas/`. It never opens a database connection
    and never creates `data/`, so a failed rebuild leaves the previous database intact.
    """
    root = ROOT if root is None else root
    validators = _Validators(root / "schemas")
    records: list[SourceRecord] = []
    return (
        validate_entities(root, validators, records)
        + validate_memories(root, validators, records)
        + validate_ideas(root, validators)
        + validate_identities(records)
    )


def format_errors(errors: Iterable[SourceError]) -> str:
    """One error per line, grouped by file in the order they were found."""
    return "\n".join(f"  {error}" for error in errors)
