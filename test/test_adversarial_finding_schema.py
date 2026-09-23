"""Contract tests for the adversarial finding and its review record (GOV-018, phase-irs-06).

`schemas/adversarial-finding.schema.json` defines one finding at its root and the review record
that holds findings at `definitions/review`. The structural rules are asserted here against a
fixture and deliberately broken copies of it. Two rules JSON Schema cannot express are asserted
directly against every record under `docs/08-governance/reviews/`: a record's `review_id` is its
filename, and finding ids are unique within a record and name only phases the record lists.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "adversarial-finding.schema.json"
REVIEWS_DIR = ROOT / "docs" / "08-governance" / "reviews"
REVIEW_FILES = sorted(REVIEWS_DIR.glob("*.json"))


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator(pointer: str = "") -> Draft7Validator:
    schema = _schema()
    registry: Registry[Any] = Registry().with_resource(
        schema["$id"], Resource.from_contents(schema)
    )
    return Draft7Validator(
        {"$ref": f"{schema['$id']}#{pointer}"},
        registry=registry,
        format_checker=Draft7Validator.FORMAT_CHECKER,
    )


def finding_errors(instance: Any) -> list[str]:
    return [error.message for error in _validator().iter_errors(instance)]


def review_errors(instance: Any) -> list[str]:
    return [error.message for error in _validator("/definitions/review").iter_errors(instance)]


def finding(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "F01",
        "altitude": "phase",
        "subject": "phase-irs-06",
        "severity": "major",
        "title": "The acceptance names no failing case.",
        "evidence": "backlog.yaml line 12760: the acceptance lists only the passing case.",
        "consequence": "A reviewer cannot tell a broken build from a working one.",
        "engine": "single-adversary",
        "author": "partition-adversary dispatched with PROMPT-038",
    }
    base.update(overrides)
    return base


def disposition(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "value": "accepted-no-change",
        "by": "planner",
        "recorded_by": "agent-builder-a",
        "date": "2026-09-23",
        "reason": "The failing case is stated in the phase's second acceptance line.",
    }
    base.update(overrides)
    return base


def review(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "review_id": "2026-09-23-plan-039",
        "procedure": "GOV-018",
        "date": "2026-09-23",
        "target": {"plan": "PLAN-039", "requirement": "REQ-022", "phases": ["phase-irs-06"]},
        "entry_check": {"result": "pass", "standard": "GOV-010", "detail": "All sections present."},
        "altitudes_run": ["plan", "phase", "later-added-phase"],
        "status": "open",
        "findings": [finding()],
    }
    base.update(overrides)
    return base


# --- the schema file itself --------------------------------------------------------


def test_schema_is_a_valid_draft7_schema() -> None:
    Draft7Validator.check_schema(_schema())


# --- one finding -------------------------------------------------------------------


def test_fixture_finding_validates() -> None:
    assert finding_errors(finding()) == []


def test_unknown_field_is_rejected() -> None:
    assert finding_errors(finding(invented_field="x"))


@pytest.mark.parametrize("severity", ["HIGH", "critical", "Blocker"])
def test_severity_outside_the_vocabulary_is_rejected(severity: str) -> None:
    assert finding_errors(finding(severity=severity))


@pytest.mark.parametrize("field", ["evidence", "consequence", "engine", "author"])
def test_required_field_missing_is_rejected(field: str) -> None:
    broken = finding()
    del broken[field]
    assert finding_errors(broken)


def test_engine_other_than_single_adversary_is_rejected() -> None:
    assert finding_errors(finding(engine="trio"))


def test_phase_altitude_needs_a_phase_id_as_subject() -> None:
    assert finding_errors(finding(subject="PLAN-039"))
    assert finding_errors(finding(altitude="later-added-phase", subject="PLAN-039"))
    assert finding_errors(finding(altitude="plan", subject="PLAN-039")) == []


def test_slug_is_optional_and_kebab_case() -> None:
    assert finding_errors(finding(slug="acceptance-without-failing-case")) == []
    assert finding_errors(finding(slug="Acceptance_Without"))


def test_aliases_need_a_slug() -> None:
    assert finding_errors(finding(aliases=["no-negative-case"]))
    assert (
        finding_errors(
            finding(slug="acceptance-without-failing-case", aliases=["no-negative-case"])
        )
        == []
    )


@pytest.mark.parametrize("value", ["fixed", "accepted-no-change", "rejected", "escalated-g3"])
def test_planner_may_write_every_disposition_value(value: str) -> None:
    assert finding_errors(finding(dispositions=[disposition(value=value)])) == []


def test_owner_cannot_escalate_to_g3() -> None:
    assert finding_errors(
        finding(dispositions=[disposition(value="escalated-g3", by="owner")])
    )


def test_escalated_finding_carries_the_owners_later_disposition() -> None:
    history = [
        disposition(value="escalated-g3", reason="Needs the owner's ruling on scope."),
        disposition(value="fixed", by="owner", recorded_by="repository-owner",
                    reason="PLAN-039, Decisions: amended."),
    ]
    assert finding_errors(finding(dispositions=history)) == []


@pytest.mark.parametrize("value", ["accepted", "wontfix", "deferred"])
def test_disposition_value_outside_the_vocabulary_is_rejected(value: str) -> None:
    assert finding_errors(finding(dispositions=[disposition(value=value)]))


def test_disposition_needs_a_reason() -> None:
    broken = disposition()
    del broken["reason"]
    assert finding_errors(finding(dispositions=[broken]))


# --- the review record -------------------------------------------------------------


def test_fixture_review_validates() -> None:
    assert review_errors(review()) == []


def test_dispositioned_review_requires_a_disposition_on_every_finding() -> None:
    settled = finding(dispositions=[disposition()])
    unsettled = finding(id="F02")
    assert review_errors(review(status="dispositioned", findings=[settled, unsettled]))
    assert review_errors(review(status="dispositioned", findings=[settled])) == []


def test_open_review_may_hold_findings_without_dispositions() -> None:
    assert review_errors(review(status="open", findings=[finding()])) == []


def returned_review(**overrides: Any) -> dict[str, Any]:
    base = review(
        status="returned",
        entry_check={
            "result": "returned",
            "standard": "GOV-010",
            "missing_sections": ["Open questions"],
            "detail": "No Open questions heading.",
        },
        altitudes_run=[],
        findings=[],
    )
    base.update(overrides)
    return base


def test_returned_review_validates() -> None:
    assert review_errors(returned_review()) == []


def test_returned_review_spends_no_adversarial_time() -> None:
    assert review_errors(returned_review(findings=[finding()]))
    assert review_errors(returned_review(altitudes_run=["plan"]))


def test_returned_entry_check_must_name_the_missing_sections() -> None:
    check = {"result": "returned", "standard": "GOV-010", "detail": "Failed."}
    assert review_errors(returned_review(entry_check=check))


def test_passing_entry_check_names_no_missing_sections() -> None:
    check = {
        "result": "pass",
        "standard": "GOV-010",
        "missing_sections": ["Open questions"],
        "detail": "x",
    }
    assert review_errors(review(entry_check=check))


def test_returned_entry_check_cannot_lead_to_an_open_review() -> None:
    check = {
        "result": "returned",
        "standard": "GOV-010",
        "missing_sections": ["Open questions"],
        "detail": "x",
    }
    assert review_errors(review(entry_check=check))


def test_reviewed_plan_must_run_at_least_one_altitude() -> None:
    assert review_errors(review(altitudes_run=[]))


# --- the committed review records --------------------------------------------------


def test_reviews_directory_holds_records() -> None:
    assert REVIEW_FILES, f"no review records under {REVIEWS_DIR}"


@pytest.mark.parametrize("path", REVIEW_FILES, ids=[path.name for path in REVIEW_FILES])
def test_committed_review_validates(path: Path) -> None:
    assert review_errors(json.loads(path.read_text(encoding="utf-8"))) == []


@pytest.mark.parametrize("path", REVIEW_FILES, ids=[path.name for path in REVIEW_FILES])
def test_committed_review_is_named_by_its_id(path: Path) -> None:
    assert json.loads(path.read_text(encoding="utf-8"))["review_id"] == path.stem


@pytest.mark.parametrize("path", REVIEW_FILES, ids=[path.name for path in REVIEW_FILES])
def test_committed_review_finding_ids_are_unique(path: Path) -> None:
    ids = [item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["findings"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("path", REVIEW_FILES, ids=[path.name for path in REVIEW_FILES])
def test_committed_review_findings_name_listed_phases(path: Path) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    listed = {
        "phase": set(record["target"].get("phases", [])),
        "later-added-phase": set(record["target"].get("later_added_phases", [])),
    }
    for item in record["findings"]:
        if item["altitude"] in listed:
            assert item["subject"] in listed[item["altitude"]], (
                f"{item['id']} names {item['subject']}, which the record does not list "
                f"at the {item['altitude']} altitude"
            )


def test_broken_copy_of_a_committed_review_fails() -> None:
    record = json.loads(REVIEW_FILES[0].read_text(encoding="utf-8"))
    broken = copy.deepcopy(record)
    broken["status"] = "no-such-status"
    assert review_errors(broken)
