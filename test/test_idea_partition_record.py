"""The partition record's owner hold-out field (phase-idg-19, idea 000417).

`schemas/idea-partition-record.schema.json` gained an optional `held_out` list so an owner's
GATE 3 hold-out is recorded as such, rather than as an unbatched reason. The field is optional
so the record the owner accepted on 2026-09-23, written before it existed, still validates
unchanged.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "idea-partition-record.schema.json"
ACCEPTED = ROOT / "docs" / "00-working" / "idea-partition-2026-09-23.json"


def _errors(record: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return [error.message for error in Draft7Validator(schema).iter_errors(record)]


def _accepted() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(ACCEPTED.read_text(encoding="utf-8"))
    return record


def test_the_accepted_2026_09_23_record_still_validates_unchanged() -> None:
    record = _accepted()
    assert "held_out" not in record, "the accepted record predates the field"
    assert _errors(record) == []


def test_a_record_carrying_an_owner_hold_out_validates() -> None:
    record = copy.deepcopy(_accepted())
    moved = record["unbatched"].pop()
    record["held_out"] = [{"id": moved["id"], "reason": "Held out by the owner at GATE 3."}]

    assert _errors(record) == []


@pytest.mark.parametrize(
    "entry",
    [
        {"id": "000015"},
        {"reason": "no id"},
        {"id": "15", "reason": "not six digits"},
        {"id": "000015", "reason": ""},
        {"id": "000015", "reason": "extra field", "status": "set_aside"},
    ],
)
def test_a_malformed_hold_out_is_refused(entry: dict[str, Any]) -> None:
    record = copy.deepcopy(_accepted())
    record["held_out"] = [entry]

    assert _errors(record) != []


def test_the_partition_workflow_writes_hold_outs_to_the_new_field() -> None:
    """GATE 3 names the field, and the step 5 check counts hold-outs as placed."""
    for path in (
        ROOT / "agent-workflows" / "partition-ideas.md",
        ROOT / ".claude" / "skills" / "partition-ideas" / "SKILL.md",
    ):
        text = path.read_text(encoding="utf-8")
        assert '`held_out`' in text, path
        assert 'record.get("held_out", [])' in text, path
        assert "writes nothing to `_data/ideas.jsonl`" in text, path
