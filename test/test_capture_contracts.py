"""Contract tests for the raw capture and staged-record schemas.

phase-cap-03 settles what a raw capture is, what a staged record is, and where both
live, before any writer exists (ADR-007, REQ-002). These tests validate the shapes in
isolation, the same way test_schemas.py validates the entity contracts: no writer, no
filesystem resolution, just the schema each future phase builds against.
"""

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def _registry() -> Registry[Any]:
    """Resolve cross-file $refs by schema filename, the id each schema declares."""
    return Registry().with_resources(
        (path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in SCHEMAS.glob("*.schema.json")
    )


def validator(name: str) -> Draft7Validator:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    return Draft7Validator(schema, registry=_registry())


def failing_paths(name: str, instance: Any) -> set[str]:
    """Every field named by a validation error, so a test can assert the field is named.

    A `required` error carries no path either — jsonschema raises it against the object,
    not the missing key — so the missing name is recovered by diffing the subschema's
    required list against the keys the failing instance actually has.
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
            if context.validator == "required" and isinstance(context.instance, dict):
                named.update(set(context.validator_value) - set(context.instance))
    return named


def is_valid(name: str, instance: Any) -> bool:
    return validator(name).is_valid(instance)


# --- the schema files themselves -------------------------------------------------


@pytest.mark.parametrize("name", ["capture", "staged-record"])
def test_schema_is_a_valid_draft7_schema(name: str) -> None:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)


# --- fixtures ----------------------------------------------------------------------

RAW_CAPTURE: dict[str, Any] = {
    "id": "raw-20260908T140501Z-a1b2c3",
    "captured_at": "2026-09-08T14:05:01Z",
    "channel": "cli",
    "content": "Call John about the Q3 deliverable by Friday.",
}

STAGED_RECORD: dict[str, Any] = {
    "id": "staged-20260908T140502Z-d4e5f6",
    "capture_id": "raw-20260908T140501Z-a1b2c3",
    "entity_type": "commitment",
    "route": "flagged",
    "entity": {
        "id": "c-1",
        "description": "Call John about the Q3 deliverable",
        "status": "open",
        "priority": "medium",
        "created": "2026-09-08",
        "promised_to": "John",
        "due_date": "2026-09-12",
    },
    "evidence": {
        "promised_to": {
            "level": "inferred",
            "provenance": {
                "capture_id": "raw-20260908T140501Z-a1b2c3",
                "quote": "Call John about the Q3 deliverable by Friday.",
            },
            "reason": "Only one other party named in the capture.",
            "review_flag": True,
        },
        "due_date": {
            "level": "inferred",
            "provenance": {
                "capture_id": "raw-20260908T140501Z-a1b2c3",
                "quote": "by Friday",
            },
            "reason": "Nearest Friday from the capture date.",
            "review_flag": True,
        },
    },
}


# --- R1 / acceptance: a raw capture validates and carries content, id, timestamp ---


def test_raw_capture_fixture_validates() -> None:
    assert is_valid("capture", RAW_CAPTURE)


@pytest.mark.parametrize("missing", ["id", "captured_at", "channel", "content"])
def test_raw_capture_requires_content_id_and_timestamp(missing: str) -> None:
    instance = {k: v for k, v in RAW_CAPTURE.items() if k != missing}
    assert missing in failing_paths("capture", instance)


def test_raw_capture_rejects_malformed_id() -> None:
    instance = {**RAW_CAPTURE, "id": "not-a-capture-id"}
    assert "id" in failing_paths("capture", instance)


def test_raw_capture_rejects_unknown_channel() -> None:
    instance = {**RAW_CAPTURE, "channel": "email"}
    assert "channel" in failing_paths("capture", instance)


def test_raw_capture_rejects_empty_content() -> None:
    instance = {**RAW_CAPTURE, "content": ""}
    assert "content" in failing_paths("capture", instance)


def test_raw_capture_source_path_defaults_null_for_non_inbox_channels() -> None:
    # source_path is optional; a cli/session capture need not carry one at all.
    assert "source_path" not in RAW_CAPTURE
    assert is_valid("capture", RAW_CAPTURE)


# --- R3 / acceptance: a staged record validates only with source ref and route ----


def test_staged_record_fixture_validates() -> None:
    assert is_valid("staged-record", STAGED_RECORD)


@pytest.mark.parametrize("missing", ["id", "capture_id", "entity_type", "route", "entity"])
def test_staged_record_requires_its_core_fields(missing: str) -> None:
    instance = {k: v for k, v in STAGED_RECORD.items() if k != missing}
    assert missing in failing_paths("staged-record", instance)


def test_staged_record_rejects_empty_capture_id() -> None:
    instance = {**STAGED_RECORD, "capture_id": ""}
    assert "capture_id" in failing_paths("staged-record", instance)


def test_staged_record_rejects_unknown_route() -> None:
    instance = {**STAGED_RECORD, "route": "auto-approved"}
    assert "route" in failing_paths("staged-record", instance)


def test_staged_record_accepts_each_legal_route() -> None:
    for route in ["clean", "flagged", "held"]:
        assert is_valid("staged-record", {**STAGED_RECORD, "route": route})


def test_staged_record_evidence_defaults_to_empty() -> None:
    instance = {k: v for k, v in STAGED_RECORD.items() if k != "evidence"}
    assert is_valid("staged-record", instance)


# --- REQ-002 R7, transitively enforced through the staged-record wrapper ----------


def test_staged_record_rejects_unflagged_assumption_on_a_protected_field() -> None:
    """due_date is protected (ADR-007 section 4): inferred without review_flag is rejected."""
    instance = copy.deepcopy(STAGED_RECORD)
    instance["evidence"]["due_date"]["review_flag"] = False
    assert "review_flag" in failing_paths("staged-record", instance)


def test_staged_record_accepts_a_flagged_assumption_on_a_protected_field() -> None:
    assert is_valid("staged-record", STAGED_RECORD)


# --- REQ-002 R16: raw, inbox and staging are all ignored --------------------------


@pytest.mark.parametrize(
    "relative_path",
    [
        "_capture/raw/raw-20260908T140501Z-a1b2c3.json",
        "_capture/inbox/dropped-note.md",
        "_capture/staging/staged-20260908T140502Z-d4e5f6.json",
    ],
)
def test_capture_locations_are_gitignored(relative_path: str) -> None:
    result = subprocess.run(
        ["git", "check-ignore", "-v", relative_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{relative_path} is not ignored: {result.stdout}{result.stderr}"
    )
