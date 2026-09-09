"""Contract tests for the entity schemas.

These validate the shapes themselves, not any code that reads them: phase-cap-02 settles
the contract before anything is written against it. The four things an agent never
invents (ADR-007) are enforced here as validation failures, because an unflagged
non-explicit value in a protected field is a rejected write, not a style problem.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

NEW_TYPES = ["task", "interaction", "decision", "waiting-on", "development-event"]


def _registry() -> Registry[Any]:
    """Resolve cross-file $refs by schema filename, the id each schema declares."""
    return Registry().with_resources(
        (path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in SCHEMAS.glob("*.schema.json")
    )


def validator(name: str) -> Draft7Validator:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    return Draft7Validator(
        schema, registry=_registry(), format_checker=Draft7Validator.FORMAT_CHECKER
    )


def failing_paths(name: str, instance: Any) -> set[str]:
    """Every field named by a validation error, so a test can assert the field is named.

    An additionalProperties error carries no path — it is raised against the object, not
    the offending key — so the unexpected keys are recovered from the subschema instead.
    """
    named: set[str] = set()
    for error in validator(name).iter_errors(instance):
        for context in [error, *error.context] if error.context else [error]:
            named.update(str(part) for part in context.absolute_path)
            if context.validator == "additionalProperties" and isinstance(
                context.instance, dict
            ):
                allowed = set(context.schema.get("properties", {}))
                named.update(set(context.instance) - allowed)
    return named


# --- the schema files themselves -------------------------------------------------


@pytest.mark.parametrize("name", [*NEW_TYPES, "evidence", "commitment", "project"])
def test_schema_is_a_valid_draft7_schema(name: str) -> None:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)


# --- fixtures for each new record type -------------------------------------------

FIXTURES: dict[str, dict[str, Any]] = {
    "task": {
        "id": "t-1",
        "description": "Draft the migration note",
        "status": "open",
        "created": "2026-09-06",
    },
    "interaction": {
        "id": "i-1",
        "date": "2026-09-06",
        "type": "meeting",
        "summary": "Reviewed the intake design and agreed to stage before promoting.",
    },
    "decision": {
        "id": "d-1",
        "date": "2026-09-06",
        "decision": "Stage captured records before they reach _data/",
        "rationale": "A git diff cannot distinguish a confident record from a guessed one.",
    },
    "waiting-on": {
        "id": "w-1",
        "description": "Signed statement of work back from the client",
        "requested": "2026-09-01",
        "status": "open",
    },
    "development-event": {
        "id": "de-1",
        "date": "2026-09-06",
        "type": "certification",
        "title": "Passed the platform certification exam",
    },
}


@pytest.mark.parametrize("name", NEW_TYPES)
def test_fixture_validates(name: str) -> None:
    assert not list(validator(name).iter_errors(FIXTURES[name]))


@pytest.mark.parametrize("name", NEW_TYPES)
def test_unknown_field_is_rejected(name: str) -> None:
    assert failing_paths(name, {**FIXTURES[name], "invented_field": "x"})


# --- tasks have optional parents (REQ-002 R18) -----------------------------------


@pytest.mark.parametrize(
    "parents",
    [
        {},
        {"commitment_id": "c-1"},
        {"project_id": "d-system"},
        {"commitment_id": "c-1", "project_id": "d-system"},
    ],
    ids=["neither", "commitment-only", "project-only", "both"],
)
def test_task_validates_with_any_combination_of_parents(parents: dict[str, str]) -> None:
    assert not list(validator("task").iter_errors({**FIXTURES["task"], **parents}))


def test_commitment_validates_without_a_project() -> None:
    commitment = {
        "id": "c-1",
        "description": "Send the revised estimate",
        "status": "open",
        "priority": "high",
        "created": "2026-09-06",
    }
    assert not list(validator("commitment").iter_errors(commitment))


def test_commitment_rejects_an_embedded_tasks_array() -> None:
    """Tasks moved to _data/tasks/; one entity with two homes is duplicate bookkeeping."""
    commitment = {
        "id": "c-1",
        "description": "Send the revised estimate",
        "status": "open",
        "priority": "high",
        "created": "2026-09-06",
        "tasks": [{"id": "t-1", "description": "Draft it"}],
    }
    assert "tasks" in failing_paths("commitment", commitment)


# --- format checking (phase-rel-11): a string check passes, a date check rejects ---


def test_malformed_date_fails_a_date_check_not_only_a_string_check() -> None:
    """2026-13-45 satisfies {"type": "string"} — the format checker is what catches it.

    Mirrors src/db/source_validation.py's preflight, which already enforces format:
    a malformed date used to pass this suite while failing the rebuild. Both now agree.
    """
    commitment = {
        "id": "c-1",
        "description": "Send the revised estimate",
        "status": "open",
        "priority": "high",
        "created": "2026-13-45",
    }
    assert "created" in failing_paths("commitment", commitment)


# --- cadence (REQ-002 R23) --------------------------------------------------------


def project_fixture(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "d-system",
        "name": "d-system",
        "status": "active",
        "category": "system",
        "type": "system",
    }
    return {**base, **overrides}


def test_retired_cadence_value_fails_and_names_the_field() -> None:
    assert "review_cadence" in failing_paths(
        "project", project_fixture(review_cadence="ongoing")
    )


def test_old_cadence_field_name_is_rejected() -> None:
    assert failing_paths("project", project_fixture(commitment_cadence="weekly"))


@pytest.mark.parametrize(
    "cadence", ["daily", "weekly", "biweekly", "monthly", "quarterly", "ad-hoc", None]
)
def test_accepted_cadence_values(cadence: str | None) -> None:
    assert not list(
        validator("project").iter_errors(project_fixture(review_cadence=cadence))
    )


def test_project_rejects_a_stored_last_touched() -> None:
    """R21: last_touched exists only in the projection."""
    assert failing_paths("project", project_fixture(last_touched="2026-09-06"))


# --- evidence and protected fields (REQ-002 R6, R7) -------------------------------

PROTECTED = json.loads((SCHEMAS / "evidence.schema.json").read_text(encoding="utf-8"))[
    "definitions"
]["protected_field_names"]["enum"]


def evidence(level: str, **extra: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "level": level,
        "provenance": {"capture_id": "cap-1", "quote": "I will send it over"},
    }
    if level != "explicit":
        entry["reason"] = "Only one other attendee, so the promise is to them."
    return {**entry, **extra}


@pytest.mark.parametrize("field", PROTECTED)
def test_protected_field_at_explicit_needs_no_flag(field: str) -> None:
    assert not list(validator("evidence").iter_errors({field: evidence("explicit")}))


@pytest.mark.parametrize("field", PROTECTED)
@pytest.mark.parametrize("level", ["inferred", "guessed"])
def test_protected_field_unflagged_at_non_explicit_fails_and_names_the_field(
    field: str, level: str
) -> None:
    assert field in failing_paths("evidence", {field: evidence(level)})


@pytest.mark.parametrize("field", PROTECTED)
@pytest.mark.parametrize("level", ["inferred", "guessed"])
def test_protected_field_passes_once_flagged_for_review(field: str, level: str) -> None:
    instance = {field: evidence(level, review_flag=True)}
    assert not list(validator("evidence").iter_errors(instance))


def test_protected_field_flagged_false_still_fails() -> None:
    instance = {"due_date": evidence("inferred", review_flag=False)}
    assert "due_date" in failing_paths("evidence", instance)


def test_unprotected_field_may_be_inferred_without_a_flag() -> None:
    assert not list(validator("evidence").iter_errors({"description": evidence("inferred")}))


def test_evidence_requires_provenance() -> None:
    assert failing_paths("evidence", {"description": {"level": "explicit"}})


def test_non_explicit_evidence_requires_a_reason() -> None:
    instance = {
        "description": {
            "level": "inferred",
            "provenance": {"capture_id": "cap-1", "quote": "send it over"},
        }
    }
    assert failing_paths("evidence", instance)


def test_explicit_evidence_requires_a_quote() -> None:
    instance = {"description": {"level": "explicit", "provenance": {"capture_id": "cap-1"}}}
    assert failing_paths("evidence", instance)


def test_guessed_evidence_may_have_no_quote() -> None:
    instance = {
        "description": {
            "level": "guessed",
            "provenance": {"capture_id": "cap-1", "quote": None},
            "reason": "Pattern match on the phrase 'by Friday' with nothing supporting it.",
        }
    }
    assert not list(validator("evidence").iter_errors(instance))


# --- what a promoted record keeps of its origin (GOV-003) -------------------------


@pytest.mark.parametrize("name", NEW_TYPES + ["commitment"])
def test_record_carries_a_capture_source(name: str) -> None:
    fixture = FIXTURES.get(
        name,
        {
            "id": "c-1",
            "description": "Send the revised estimate",
            "status": "open",
            "priority": "high",
            "created": "2026-09-06",
        },
    )
    instance = {
        **fixture,
        "capture": {
            "capture_id": "cap-1",
            "assumed_fields": ["due_date"],
            "promoted": "2026-09-06",
        },
    }
    assert not list(validator(name).iter_errors(instance))


@pytest.mark.parametrize("name", NEW_TYPES + ["commitment"])
def test_capture_source_may_be_null_for_hand_authored_records(name: str) -> None:
    fixture = FIXTURES.get(
        name,
        {
            "id": "c-1",
            "description": "Send the revised estimate",
            "status": "open",
            "priority": "high",
            "created": "2026-09-06",
        },
    )
    assert not list(validator(name).iter_errors({**fixture, "capture": None}))


def test_capture_source_requires_an_identifier() -> None:
    instance = {**FIXTURES["task"], "capture": {"assumed_fields": ["due_date"]}}
    assert failing_paths("task", instance)


def test_promoted_record_does_not_carry_per_field_evidence() -> None:
    """GOV-003: full evidence scoring stays on the staged record."""
    instance = {**FIXTURES["task"], "evidence": {"description": evidence("explicit")}}
    assert failing_paths("task", instance)


# --- the real source data matches the contract ------------------------------------


@pytest.mark.parametrize(
    "path", sorted((ROOT / "_data/projects").glob("*.json")), ids=lambda p: p.stem
)
def test_every_source_project_validates(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    assert not list(validator("project").iter_errors(document))
