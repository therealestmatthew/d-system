"""Promotion: the only capture path that writes to the data root — REQ-002 R12/R13/R15.

ADR-007 sections 7, 9 and 10.

Staged records become real only through an owner action here. There are four:

- **bulk promotion** of every `clean` staged record, and nothing else (R13);
- **promoting one** flagged or held record, with any field values the owner states. A
  value the owner sets is the owner's word, so it no longer counts as assumed;
- **creating an identity** — a person or project — from a held record. A new tag stays
  held: the owner ruled that capture-derived tags belong under the private data root (idea
  `000343`), and nothing reads a private tag file yet. A new tag category stays held too;
- **correcting** a promoted record: the record is edited in place and a dated entry naming
  the field, the previous value and the new one is appended to `corrections.jsonl` (R15).

Entity records go to the data root (`D_SYSTEM_DATA_ROOT`, else `_data/`, per ADR-009). Nothing
here writes the tracked `_data/tags.json`. Nothing here overwrites an existing record, and
promotion assigns every id itself, so a record can never be written over another or outside
the data root. Nothing here fills in a missing value either: a staged record that does not
validate against its entity schema stays staged, and the reason is reported. A promoted or discarded
staged record moves out of staging into `_capture/promoted/` or `_capture/discarded/`, so
the decision stays on disk; the raw capture is never touched (R2).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator  # type: ignore[import-untyped]
from referencing import Registry, Resource

from src.capture.structure import (
    STAGING_DIR,
    UNRESOLVED_NAME_FIELDS,
    KnownIdentities,
    StructuringError,
    unresolved_references,
)
from src.db.source_validation import data_root

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
PROMOTED_DIR = ROOT / "_capture" / "promoted"
DISCARDED_DIR = ROOT / "_capture" / "discarded"
TAGS_FILE = ROOT / "_data" / "tags.json"
CORRECTIONS_FILE = "corrections.jsonl"

#: A staged id, as `structure._new_id` makes it (schemas/staged-record.schema.json).
STAGED_ID = re.compile(r"^staged-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$")
#: A promoted record's id: a plain file stem, never a path.
RECORD_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class EntityKind:
    """Where a promoted record of one type lives, and how its id is numbered."""

    schema: str
    directory: str
    prefix: str | None  # None: the id is a kebab-case name the owner chooses


#: Staged `entity_type` -> destination. `note` and `tag-category` are absent on purpose: a
#: note has no entity schema, and a new category is a schema change.
KINDS: dict[str, EntityKind] = {
    "commitment": EntityKind("commitment", "commitments", "c-"),
    "task": EntityKind("task", "tasks", "t-"),
    "interaction": EntityKind("interaction", "interactions", "i-"),
    "decision": EntityKind("decision", "decisions", "d-"),
    "waiting-on": EntityKind("waiting-on", "waiting-on", "w-"),
    "development-event": EntityKind("development-event", "development-events", "de-"),
    "person": EntityKind("person", "people", None),
    "project": EntityKind("project", "projects", None),
}

#: Types that are themselves a new identity, decided with `create_identity`.
IDENTITY_TYPES = frozenset({"person", "project", "tag"})

#: Correctable record types, by schema name.
CORRECTABLE: dict[str, EntityKind] = {kind.schema: kind for kind in KINDS.values()}


class PromotionError(ValueError):
    """An owner action was refused; nothing was written."""


@dataclass
class Paths:
    """Every location promotion reads or writes, overridable for tests."""

    # Factories, so each default is read when a `Paths` is made rather than at import.
    staging: Path = field(default_factory=lambda: STAGING_DIR)
    promoted: Path = field(default_factory=lambda: PROMOTED_DIR)
    discarded: Path = field(default_factory=lambda: DISCARDED_DIR)
    data: Path = field(default_factory=lambda: data_root(ROOT))
    tags: Path = field(default_factory=lambda: TAGS_FILE)
    schemas: Path = field(default_factory=lambda: SCHEMAS)


@dataclass
class PromotionResult:
    """What an action did: `(staged id, where it went)` and `(staged id, why not)`."""

    promoted: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


def _validator(schemas: Path, name: str) -> Draft7Validator:
    registry: Registry[Any] = Registry().with_resources(
        (p.name, Resource.from_contents(json.loads(p.read_text(encoding="utf-8"))))
        for p in schemas.glob("*.schema.json")
    )
    schema = json.loads((schemas / f"{name}.schema.json").read_text(encoding="utf-8"))
    return Draft7Validator(schema, registry=registry, format_checker=Draft7Validator.FORMAT_CHECKER)


def _errors(validator: Draft7Validator, record: Mapping[str, Any]) -> str:
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    return "; ".join(
        f"{'.'.join(str(p) for p in e.absolute_path) or 'record'}: {e.message}" for e in errors
    )


def _tmp_file(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    return tmp


def _dump(record: Any) -> str:
    return json.dumps(record, ensure_ascii=False, indent=2) + "\n"


def _write_json(path: Path, record: Any) -> None:
    """Replace `path` atomically: a reader sees the old file or the new one, never half."""
    os.replace(_tmp_file(path, _dump(record)), path)


def _create_json(path: Path, record: Mapping[str, Any]) -> None:
    """Write a new file atomically, refusing if `path` already exists."""
    tmp = _tmp_file(path, _dump(record))
    try:
        os.link(tmp, path)
    except FileExistsError:
        raise PromotionError(f"{path} already exists; refusing to overwrite it") from None
    finally:
        tmp.unlink()


def _inside(base: Path, path: Path) -> Path:
    """Refuse a target that would land outside `base`, whatever the record's id says."""
    if not path.resolve().is_relative_to(base.resolve()):
        raise PromotionError(f"{path} is outside {base}; refusing to write it")
    return path


def _unresolved(entity: Mapping[str, Any], paths: Paths, keep_names: bool) -> list[str]:
    try:
        found = unresolved_references(entity, known_identities(paths))
    except StructuringError as exc:
        raise PromotionError(str(exc)) from None
    if keep_names:
        found = [u for u in found if u.split("=", 1)[0] not in UNRESOLVED_NAME_FIELDS]
    return found


def load_staged(staging: Path = STAGING_DIR) -> list[dict[str, Any]]:
    """Every staged record, oldest first."""
    if not staging.is_dir():
        return []
    records = [json.loads(p.read_text(encoding="utf-8")) for p in staging.glob("*.json")]
    return sorted(records, key=lambda r: (r.get("staged_at", ""), r["id"]))


def _staged(staged_id: str, paths: Paths) -> dict[str, Any]:
    if not STAGED_ID.match(staged_id):
        raise PromotionError(f"{staged_id!r} is not a staged id")
    path = paths.staging / f"{staged_id}.json"
    if not path.is_file():
        raise PromotionError(f"no staged record {staged_id!r}")
    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return record


def _next_number(directory: Path, prefix: str, taken: set[str]) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}([0-9]+)$")
    existing = {p.stem for p in directory.glob("*.json")} if directory.is_dir() else set()
    numbers = [int(m.group(1)) for name in existing | taken if (m := pattern.match(name))]
    return f"{prefix}{max(numbers, default=0) + 1}"


def known_identities(paths: Paths) -> KnownIdentities:
    def ids(directory: Path) -> frozenset[str]:
        if not directory.is_dir():
            return frozenset()
        return frozenset(
            json.loads(p.read_text(encoding="utf-8"))["id"] for p in directory.glob("*.json")
        )

    tags = json.loads(paths.tags.read_text(encoding="utf-8")) if paths.tags.exists() else []
    return KnownIdentities(
        people=ids(paths.data / "people"),
        projects=ids(paths.data / "projects"),
        tags=frozenset(tag["id"] for tag in tags),
    )


def _assumed(staged: Mapping[str, Any], owner_set: Iterable[str]) -> list[str]:
    evidence: Mapping[str, Mapping[str, Any]] = staged.get("evidence") or {}
    stated = set(owner_set)
    return sorted(
        name
        for name, ev in evidence.items()
        if ev.get("level") != "explicit" and name not in stated
    )


def candidate(
    staged: Mapping[str, Any],
    overrides: Mapping[str, Any],
    paths: Paths,
    today: dt.date,
    taken: set[str],
    keep_names: bool,
) -> tuple[EntityKind, dict[str, Any]]:
    """Build and validate the entity a staged record would become, or raise with why not."""
    entity_type = staged["entity_type"]
    if entity_type in IDENTITY_TYPES:
        raise PromotionError(f"a new {entity_type} is an identity call; use create")
    kind = KINDS.get(entity_type)
    if kind is None:
        raise PromotionError(f"no entity schema for {entity_type!r}; it stays staged")

    entity = {**staged.get("entity", {}), **overrides}
    if "id" in entity:
        raise PromotionError(
            "promotion assigns the id; a proposal or --set may not supply one "
            f"(got {entity['id']!r})"
        )
    unresolved = _unresolved(entity, paths, keep_names)
    if unresolved:
        raise PromotionError("unresolved reference(s): " + ", ".join(unresolved))

    assert kind.prefix is not None
    record = {
        "id": _next_number(paths.data / kind.directory, kind.prefix, taken),
        **entity,
        "capture": {
            "capture_id": staged["capture_id"],
            "assumed_fields": _assumed(staged, overrides),
            "promoted": today.isoformat(),
        },
    }
    problems = _errors(_validator(paths.schemas, kind.schema), record)
    if problems:
        raise PromotionError(f"does not validate as a {kind.schema}: {problems}")
    return kind, record


def _archive(staged: Mapping[str, Any], outcome: Mapping[str, Any], directory: Path) -> None:
    _write_json(directory / f"{staged['id']}.json", {"staged": staged, **outcome})


def _finish_earlier_attempt(staged: Mapping[str, Any], paths: Paths) -> str | None:
    """Settle a staged record whose promotion was interrupted part-way.

    The archive entry is written before the record, so an entry whose record exists and
    came from this capture means the record was promoted and only the staged copy is left:
    remove it and report the record. Otherwise the write never happened — the file is
    missing, or another record has since taken that id — so drop the entry and the record
    is promoted afresh under a new id. Either way nothing is promoted twice or lost.

    The target is rebuilt from the entry's `record_id` under the current data root, not
    read from the stored absolute path, so a moved data root cannot misdirect it.
    """
    archive = paths.promoted / f"{staged['id']}.json"
    if not archive.is_file():
        return None
    entry = json.loads(archive.read_text(encoding="utf-8"))
    kind = KINDS.get(staged["entity_type"])
    record_id = entry.get("record_id", "")
    if kind is not None and RECORD_ID.match(record_id):
        target = _inside(paths.data, paths.data / kind.directory / f"{record_id}.json")
        if _promoted_from(target, record_id, staged["capture_id"]):
            (paths.staging / f"{staged['id']}.json").unlink(missing_ok=True)
            return str(target)
    archive.unlink()
    return None


def _promoted_from(target: Path, record_id: str, capture_id: str) -> bool:
    """Whether `target` is the record promoted from `capture_id`, not another one."""
    if not target.is_file():
        return False
    try:
        record = json.loads(target.read_text(encoding="utf-8"))
    except ValueError:
        return False
    capture = record.get("capture") if isinstance(record, dict) else None
    return (
        record.get("id") == record_id
        and isinstance(capture, dict)
        and capture.get("capture_id") == capture_id
    )


def _promote(
    records: Iterable[Mapping[str, Any]],
    paths: Paths,
    today: dt.date,
    overrides: Mapping[str, Any] | None = None,
    keep_names: bool = False,
) -> PromotionResult:
    """Promote each record in turn. A failure skips that record and the batch continues.

    Order per record: the archive entry, then the record (created, never overwritten), then
    the staged copy is removed. See `_finish_earlier_attempt` for recovery.
    """
    result = PromotionResult()
    taken: set[str] = set()
    for staged in records:
        try:
            finished = _finish_earlier_attempt(staged, paths)
            if finished is not None:
                result.promoted.append((staged["id"], finished))
                continue
            kind, record = candidate(staged, overrides or {}, paths, today, taken, keep_names)
            target = _inside(paths.data, paths.data / kind.directory / f"{record['id']}.json")
            archive = paths.promoted / f"{staged['id']}.json"
            _archive(
                staged,
                {
                    "action": "promoted",
                    "record_id": record["id"],
                    "target": str(target),
                    "on": today.isoformat(),
                },
                paths.promoted,
            )
            try:
                _create_json(target, record)
            except BaseException:
                archive.unlink(missing_ok=True)
                raise
            taken.add(record["id"])
            (paths.staging / f"{staged['id']}.json").unlink()
        except (ValueError, KeyError, OSError) as exc:
            # ValueError covers PromotionError and a corrupt JSON file; KeyError a staged
            # record missing a required field. Either skips this record only.
            why = str(exc) if isinstance(exc, PromotionError) else f"{type(exc).__name__}: {exc}"
            result.skipped.append((staged.get("id", "?"), why))
            continue
        result.promoted.append((staged["id"], str(target)))
    return result


def promote_clean(paths: Paths | None = None, today: dt.date | None = None) -> PromotionResult:
    """Promote every clean staged record and no other (REQ-002 R13)."""
    where = paths or Paths()
    clean = [r for r in load_staged(where.staging) if r.get("route") == "clean"]
    return _promote(clean, where, today or dt.date.today())


def promote_one(
    staged_id: str,
    overrides: Mapping[str, Any] | None = None,
    keep_names: bool = False,
    paths: Paths | None = None,
    today: dt.date | None = None,
) -> PromotionResult:
    """Promote one staged record on the owner's decision, whatever its route.

    `overrides` are field values the owner states. `keep_names` confirms that names in
    `participant_names` / `decided_by_names` stay as plain text rather than becoming people.
    """
    where = paths or Paths()
    staged = _staged(staged_id, where)
    result = _promote([staged], where, today or dt.date.today(), overrides, keep_names)
    if result.skipped:
        raise PromotionError(f"{staged_id}: {result.skipped[0][1]}")
    return result


def create_identity(
    staged_id: str,
    overrides: Mapping[str, Any] | None = None,
    paths: Paths | None = None,
    today: dt.date | None = None,
) -> str:
    """Create the person, project or tag a held record proposes. Returns where it went."""
    where = paths or Paths()
    staged = _staged(staged_id, where)
    entity_type = staged["entity_type"]
    if entity_type == "tag-category":
        raise PromotionError(
            "a new tag category changes schemas/tag.schema.json; it stays held as a proposal"
        )
    if entity_type not in IDENTITY_TYPES:
        raise PromotionError(f"{entity_type!r} is not an identity; use promote")
    if entity_type == "tag":
        raise PromotionError(
            "a tag from a capture belongs under the private data root, not the tracked "
            "_data/tags.json (owner ruling, idea 000343); nothing reads a private tag file "
            "yet, so the tag stays held"
        )

    record = {**staged.get("entity", {}), **(overrides or {})}
    problems = _errors(_validator(where.schemas, entity_type), record)
    if problems:
        raise PromotionError(f"does not validate as a {entity_type}: {problems}")

    try:
        kind = KINDS[entity_type]
        target = _inside(where.data, where.data / kind.directory / f"{record['id']}.json")
        _create_json(target, record)
    except OSError as exc:
        raise PromotionError(f"could not write the {entity_type}: {exc}") from exc

    _archive(
        staged,
        {
            "action": "created",
            "record_id": record["id"],
            "on": (today or dt.date.today()).isoformat(),
        },
        where.promoted,
    )
    (where.staging / f"{staged_id}.json").unlink()
    return str(target)


def discard(staged_id: str, paths: Paths | None = None, today: dt.date | None = None) -> None:
    """Drop a staged record without promoting it. It moves to `_capture/discarded/`."""
    where = paths or Paths()
    staged = _staged(staged_id, where)
    _archive(
        staged,
        {"action": "discarded", "on": (today or dt.date.today()).isoformat()},
        where.discarded,
    )
    (where.staging / f"{staged_id}.json").unlink()


def correct(
    record_type: str,
    record_id: str,
    field_name: str,
    value: Any,
    reason: str | None = None,
    paths: Paths | None = None,
    today: dt.date | None = None,
) -> dict[str, Any]:
    """Edit one field of a promoted record and append the dated correction (REQ-002 R15).

    The corrected record must still validate, and may not name a person, project or tag that
    does not exist; `id` and `capture` cannot be corrected. Both are checked before anything
    is written. The entry is then appended and fsynced before the record is replaced, so the
    previous value is on disk before it leaves the record. Returns the correction entry.
    """
    where = paths or Paths()
    kind = CORRECTABLE.get(record_type)
    if kind is None:
        raise PromotionError(
            f"cannot correct a {record_type!r}; expected one of {sorted(CORRECTABLE)}"
        )
    if field_name in {"id", "capture"}:
        raise PromotionError(f"{field_name!r} cannot be corrected")
    if not RECORD_ID.match(record_id):
        raise PromotionError(f"{record_id!r} is not a record id")
    path = _inside(where.data, where.data / kind.directory / f"{record_id}.json")
    if not path.is_file():
        raise PromotionError(f"no {record_type} {record_id!r} in {where.data}")

    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    previous = record.get(field_name)
    if field_name in record and previous == value:
        raise PromotionError(f"{field_name!r} already holds {value!r}")
    corrected = {**record, field_name: value}
    problems = _errors(_validator(where.schemas, kind.schema), corrected)
    if problems:
        raise PromotionError(f"the corrected record would not validate: {problems}")
    # A correction may not name a person, project or tag that does not exist, any more than
    # a promotion may (REQ-002 R10). Plain names in *_names fields are the owner's word.
    unresolved = [u for u in _unresolved(corrected, where, keep_names=True)]
    if unresolved:
        raise PromotionError("unresolved reference(s): " + ", ".join(unresolved))

    entry = {
        "record_type": record_type,
        "record_id": record_id,
        "field": field_name,
        "previous": previous,
        "new": value,
        "corrected": (today or dt.date.today()).isoformat(),
        "reason": reason,
    }
    if field_name not in record:
        entry["previous_absent"] = True
    problems = _errors(_validator(where.schemas, "correction"), entry)
    if problems:
        raise PromotionError(f"refusing an invalid correction entry: {problems}")

    # The entry is appended first. If writing the record then fails, the log holds a value
    # the record does not, which is visible; the other order could lose the previous value.
    # A crash part-way through an earlier append can leave a last line with no newline; start
    # this entry on a fresh line so it is not joined onto the torn one.
    try:
        with (where.data / CORRECTIONS_FILE).open("a+b") as log:
            log.seek(0, os.SEEK_END)
            torn = False
            if log.tell() > 0:
                log.seek(-1, os.SEEK_END)
                torn = log.read(1) != b"\n"
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            log.write((("\n" if torn else "") + line).encode("utf-8"))
            log.flush()
            os.fsync(log.fileno())
        _write_json(path, corrected)
    except OSError as exc:
        raise PromotionError(f"could not record the correction: {exc}") from exc
    return entry


def corrections(
    record_type: str, record_id: str, paths: Paths | None = None
) -> list[dict[str, Any]]:
    """Every correction to one record, oldest first.

    A line that does not parse is a torn append from a crash. The entry is written before
    the record, so a torn entry was never applied; it is skipped rather than hiding every
    other entry behind a parse error.
    """
    where = paths or Paths()
    log = where.data / CORRECTIONS_FILE
    if not log.exists():
        return []
    entries = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return [
        e
        for e in entries
        if e.get("record_type") == record_type and e.get("record_id") == record_id
    ]
