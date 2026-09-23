"""Structuring: turn an agent's interpretation of a raw capture into staged records.

REQ-002 R3/R6/R7/R9/R10, ADR-007 sections 3-7. The interpretation itself — which entity a
capture describes, and what each field says — comes from whichever agent is structuring
the capture, as a *proposal*. This module does not read text for meaning. It checks the
proposal against the raw capture and the rules an agent may not break, then stages it:

- every field carries an evidence level, and every explicit or inferred quote must occur
  verbatim in the raw capture, which fixes its offsets (provenance, R6);
- a protected field — `promised_to`, `due_date`, a decision or its rationale, or any
  completion — at a non-explicit level without a review flag is rejected, naming the field
  (R7). The protected names are read from `schemas/evidence.schema.json`;
- a field naming a person, project or tag that does not exist is kept as written and the
  record is held; no person, project or tag record is ever created here (R10);
- the route comes from `routing.route_for`, and the record is written to `_capture/staging/`,
  never `_data/` (R12).

Nothing here waits on owner input. An ambiguous capture is structured as the agent's best
reading, flagged, and staged (R9). The raw record's channel is never read, so the same text
routes identically whichever channel captured it (R4).

A proposal is a mapping:

    {"entity_type": "commitment",
     "fields": {"description": {"value": "...", "level": "explicit", "quote": "..."},
                "due_date": {"value": "2026-10-01", "level": "inferred", "quote": "...",
                             "reason": "...", "review_flag": true}}}
"""

from __future__ import annotations

import datetime as dt
import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator  # type: ignore[import-untyped]
from referencing import Registry, Resource

from src.capture.raw import RAW_DIR
from src.capture.routing import route_for, stakes_for
from src.db.source_validation import data_root

ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = ROOT / "_capture" / "staging"
SCHEMAS = ROOT / "schemas"

#: Fields whose value names a person, and the fields holding names not yet resolved to one.
PERSON_FIELDS = ("promised_to", "owed_by")
PERSON_LIST_FIELDS = ("participants", "decided_by")
UNRESOLVED_NAME_FIELDS = ("participant_names", "decided_by_names")

#: `status` values that assert completion — "completion of anything" (ADR-007 section 4)
#: covers a status as much as the `completed` / `received` date fields.
COMPLETION_STATUSES = {"complete", "received"}


class StructuringError(ValueError):
    """A proposal was refused before anything was staged."""


def _schema(name: str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    return loaded


def protected_fields() -> frozenset[str]:
    """The never-invent field names, read from the schema rather than restated here."""
    names = _schema("evidence.schema.json")["definitions"]["protected_field_names"]["enum"]
    return frozenset(names)


def _staged_validator() -> Draft7Validator:
    evidence = _schema("evidence.schema.json")
    registry: Registry = Registry().with_resource(
        "evidence.schema.json", Resource.from_contents(evidence)
    )
    return Draft7Validator(_schema("staged-record.schema.json"), registry=registry)


@dataclass(frozen=True)
class KnownIdentities:
    """The people, projects and tags that already exist. Anything else is unresolved."""

    people: frozenset[str] = field(default_factory=frozenset)
    projects: frozenset[str] = field(default_factory=frozenset)
    tags: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def load(cls, root: Path = ROOT) -> KnownIdentities:
        """Read ids from the data root (people, projects) and the shared `_data/tags.json`."""
        entities = data_root(root)

        def ids(directory: Path) -> frozenset[str]:
            if not directory.is_dir():
                return frozenset()
            return frozenset(
                json.loads(p.read_text(encoding="utf-8"))["id"]
                for p in sorted(directory.glob("*.json"))
            )

        tags_file = root / "_data" / "tags.json"
        tags = json.loads(tags_file.read_text(encoding="utf-8")) if tags_file.exists() else []
        return cls(
            people=ids(entities / "people"),
            projects=ids(entities / "projects"),
            tags=frozenset(tag["id"] for tag in tags),
        )


def load_raw(capture_id: str, raw_dir: Path = RAW_DIR) -> dict[str, Any]:
    """Resolve a capture id to its raw record (REQ-002 R3). Unresolvable ids are refused."""
    path = raw_dir / f"{capture_id}.json"
    if not path.is_file():
        raise StructuringError(f"capture {capture_id!r} does not resolve to a raw record")
    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return record


def unresolved_references(entity: Mapping[str, Any], known: KnownIdentities) -> list[str]:
    """Name every field value that refers to a person, project or tag not yet known."""
    found: list[str] = []
    for name in PERSON_FIELDS:
        value = entity.get(name)
        if value is not None and value not in known.people:
            found.append(f"{name}={value!r}")
    for name in PERSON_LIST_FIELDS:
        found += [f"{name}={v!r}" for v in entity.get(name) or [] if v not in known.people]
    for name in UNRESOLVED_NAME_FIELDS:
        found += [f"{name}={v!r}" for v in entity.get(name) or []]
    project = entity.get("project_id")
    if project is not None and project not in known.projects:
        found.append(f"project_id={project!r}")
    found += [f"tags={t!r}" for t in entity.get("tags") or [] if t not in known.tags]
    return found


def _field_evidence(
    name: str, spec: Mapping[str, Any], capture_id: str, content: str
) -> dict[str, Any]:
    level = spec.get("level")
    quote = spec.get("quote")
    provenance: dict[str, Any] = {"capture_id": capture_id, "quote": quote}
    if quote is not None:
        start = content.find(quote)
        if start < 0:
            raise StructuringError(
                f"field {name!r}: quote {quote!r} does not occur in capture {capture_id}"
            )
        provenance["start"], provenance["end"] = start, start + len(quote)
    evidence: dict[str, Any] = {"level": level, "provenance": provenance}
    if spec.get("reason") is not None:
        evidence["reason"] = spec["reason"]
    if "review_flag" in spec:
        evidence["review_flag"] = spec["review_flag"]
    return evidence


def _check_never_invent(entity: Mapping[str, Any], evidence: Mapping[str, Any]) -> None:
    """Reject any protected value assumed without a review flag, naming each field."""
    protected = set(protected_fields())
    if entity.get("status") in COMPLETION_STATUSES:
        protected.add("status")
    offending = sorted(
        name
        for name in protected & evidence.keys()
        if evidence[name]["level"] != "explicit" and evidence[name].get("review_flag") is not True
    )
    if offending:
        raise StructuringError(
            "protected field(s) assumed without a review flag: " + ", ".join(offending)
        )


def _iso_utc(at: dt.datetime) -> str:
    return at.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _new_id(at: dt.datetime) -> str:
    return f"staged-{at.astimezone(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}-{os.urandom(3).hex()}"


def structure(
    raw: Mapping[str, Any],
    proposal: Mapping[str, Any],
    known: KnownIdentities,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Check one proposal against its raw capture and return the staged record."""
    capture_id: str = raw["id"]
    content: str = raw["content"]
    entity_type = proposal.get("entity_type")
    if not isinstance(entity_type, str):
        raise StructuringError("proposal has no entity_type")
    stakes_for(entity_type)  # an unknown type is refused before anything else is checked

    fields: Mapping[str, Mapping[str, Any]] = proposal.get("fields") or {}
    missing = sorted(name for name, spec in fields.items() if "level" not in spec)
    if missing:
        raise StructuringError(f"field(s) without an evidence level: {', '.join(missing)}")

    entity = {name: spec.get("value") for name, spec in fields.items()}
    evidence = {
        name: _field_evidence(name, spec, capture_id, content) for name, spec in fields.items()
    }
    _check_never_invent(entity, evidence)

    at = now or dt.datetime.now(dt.UTC)
    record: dict[str, Any] = {
        "id": _new_id(at),
        "capture_id": capture_id,
        "entity_type": entity_type,
        "route": route_for(
            entity_type,
            (e["level"] for e in evidence.values()),
            unresolved_references=bool(unresolved_references(entity, known)),
        ),
        "entity": entity,
        "evidence": evidence,
        "staged_at": _iso_utc(at),
    }

    errors = sorted(_staged_validator().iter_errors(record), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path) or 'record'}: {e.message}" for e in errors
        )
        raise StructuringError(f"refusing to stage an invalid record — {detail}")
    return record


def stage_capture(
    capture_id: str,
    proposals: Iterable[Mapping[str, Any]],
    known: KnownIdentities | None = None,
    raw_dir: Path = RAW_DIR,
    staging_dir: Path = STAGING_DIR,
) -> list[dict[str, Any]]:
    """Structure every proposal for one capture and write them to staging.

    All proposals are checked before any is written, so a refused proposal leaves staging
    exactly as it was. Returns the staged records written.
    """
    raw = load_raw(capture_id, raw_dir)
    identities = known if known is not None else KnownIdentities.load()
    records = [structure(raw, proposal, identities) for proposal in proposals]

    staging_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        path = staging_dir / f"{record['id']}.json"
        if path.exists():
            raise StructuringError(f"staged record id collision: {path}")
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records
