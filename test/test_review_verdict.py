"""Contract tests for the build-review verdict and draw records (REQ-030 R05, phase-asr-03).

`schemas/review-verdict.schema.json` defines one verdict record at its root and the re-review
sampler's draw record at `definitions/draw`. The structural rules are asserted here against a
fixture and deliberately broken copies of it. Two rules JSON Schema cannot express are asserted
directly against every record under `docs/08-governance/reviews/verdicts/`: a record's
`verdict_id` is its filename, and finding ids are unique within a record.
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
SCHEMA_PATH = ROOT / "schemas" / "review-verdict.schema.json"
VERDICT_FILES = sorted((ROOT / "docs" / "08-governance" / "reviews" / "verdicts").glob("*.json"))
SHA = "0123456789abcdef" * 4


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


def verdict_errors(instance: Any) -> list[str]:
    return [error.message for error in _validator().iter_errors(instance)]


def draw_errors(instance: Any) -> list[str]:
    return [error.message for error in _validator("/definitions/draw").iter_errors(instance)]


def finding(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "F01",
        "severity": "major",
        "title": "The sampler draws shadow verdicts.",
        "evidence": "02-verification.txt: the draw lists 2026-10-02-phase-asr-01-review-judge.",
    }
    base.update(overrides)
    return base


def outcome(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "kind": "sampled-rereview",
        "date": "2026-10-09",
        "recorded_by": "agent-session-manager",
        "detail": "Re-reviewed at the same commit; the re-review passed it with no findings.",
        "draw_id": "2026-10-09-01",
        "reviewer_type": "demo-validator-code",
        "verdict": "pass",
    }
    base.update(overrides)
    return base


def verdict(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "verdict_id": "2026-10-02-phase-asr-03-demo-adversary",
        "date": "2026-10-02",
        "phase": "phase-asr-03",
        "reviewed_commit": "73bd6ab" + "0" * 33,
        "reviewer": {"type": "demo-adversary", "definition_sha256": SHA},
        "model": "claude-opus-5-5",
        "verdict": "pass",
        "gating": True,
        "findings": [finding()],
        "raw_reply_sha256": SHA,
        "outcomes": [],
    }
    base.update(overrides)
    return base


def draw(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "draw_id": "2026-10-09-01",
        "date": "2026-10-09",
        "seed": 4021,
        "rate": 10,
        "considered": ["2026-10-02-phase-asr-03-demo-adversary"],
        "sample": [
            {
                "phase": "phase-asr-03",
                "verdict_id": "2026-10-02-phase-asr-03-demo-adversary",
                "reason": "one-in-ten",
                "excluded_reviewer_types": ["demo-adversary", "review-judge"],
            }
        ],
    }
    base.update(overrides)
    return base


# --- the schema file itself --------------------------------------------------------


def test_schema_is_a_valid_draft7_schema() -> None:
    Draft7Validator.check_schema(_schema())


# --- the three acceptance fixtures (REQ-030 R05) -----------------------------------


def test_valid_record_passes() -> None:
    assert verdict_errors(verdict()) == []


def test_record_without_model_fails() -> None:
    broken = verdict()
    del broken["model"]
    assert verdict_errors(broken) == ["'model' is a required property"]


def test_record_with_an_outcome_appended_passes() -> None:
    record = verdict()
    record["outcomes"].append(outcome())
    assert verdict_errors(record) == []


# --- the rest of the verdict record ------------------------------------------------


@pytest.mark.parametrize(
    "field",
    ["verdict_id", "date", "phase", "reviewed_commit", "reviewer", "verdict", "gating",
     "findings", "raw_reply_sha256", "outcomes"],
)
def test_required_field_missing_is_rejected(field: str) -> None:
    broken = verdict()
    del broken[field]
    assert verdict_errors(broken)


def test_unknown_field_is_rejected() -> None:
    assert verdict_errors(verdict(invented_field="x"))


def test_reviewer_needs_its_definition_sha256() -> None:
    assert verdict_errors(verdict(reviewer={"type": "demo-adversary"}))
    assert verdict_errors(verdict(reviewer={"type": "demo-adversary", "definition_sha256": "abc"}))


@pytest.mark.parametrize("value", ["passed", "fail", "pass-with-findings"])
def test_verdict_outside_the_vocabulary_is_rejected(value: str) -> None:
    assert verdict_errors(verdict(verdict=value))


def test_gating_is_a_boolean() -> None:
    assert verdict_errors(verdict(gating="false"))
    assert verdict_errors(verdict(gating=False)) == []


def test_reviewed_commit_is_a_full_sha() -> None:
    assert verdict_errors(verdict(reviewed_commit="73bd6ab"))


def test_verdict_id_names_the_date_phase_and_reviewer() -> None:
    assert verdict_errors(verdict(verdict_id="2026-10-02-demo-adversary"))
    assert verdict_errors(verdict(verdict_id="2026-10-02-phase-asr-03-demo-adversary-2")) == []


def test_findings_may_be_empty() -> None:
    assert verdict_errors(verdict(findings=[])) == []


def test_finding_needs_evidence_and_a_known_severity() -> None:
    no_evidence = finding()
    del no_evidence["evidence"]
    assert verdict_errors(verdict(findings=[no_evidence]))
    assert verdict_errors(verdict(findings=[finding(severity="critical")]))


def test_finding_keeps_the_reviewers_consequence() -> None:
    stated = finding(consequence="Shadow verdicts would be re-reviewed as if they had gated.")
    assert verdict_errors(verdict(findings=[stated])) == []
    assert verdict_errors(verdict(findings=[finding(consequence="")]))


@pytest.mark.parametrize("field", ["draw_id", "reviewer_type", "verdict"])
def test_sampled_rereview_outcome_needs_its_draw_reviewer_and_verdict(field: str) -> None:
    broken = outcome()
    del broken[field]
    assert verdict_errors(verdict(outcomes=[broken]))


def test_other_outcomes_carry_no_rereview_fields() -> None:
    overturned = {
        "kind": "owner-overturned",
        "date": "2026-10-03",
        "recorded_by": "repository-owner",
        "detail": "Owner held the merge at G4: the OPS document names the wrong path.",
    }
    assert verdict_errors(verdict(outcomes=[overturned])) == []
    assert verdict_errors(verdict(outcomes=[{**overturned, "reviewer_type": "demo-adversary"}]))


def test_unknown_outcome_kind_is_rejected() -> None:
    assert verdict_errors(verdict(outcomes=[outcome(kind="re-reviewed")]))


# --- the draw record ---------------------------------------------------------------


def test_valid_draw_passes() -> None:
    assert draw_errors(draw()) == []


def test_draw_with_an_empty_sample_passes() -> None:
    assert draw_errors(draw(sample=[])) == []


def test_draw_rate_is_ten() -> None:
    assert draw_errors(draw(rate=5))


def test_draw_considers_at_least_one_verdict() -> None:
    assert draw_errors(draw(considered=[]))


def test_drawn_entry_needs_an_excluded_type_and_a_known_reason() -> None:
    record = draw()
    record["sample"][0]["excluded_reviewer_types"] = []
    assert draw_errors(record)
    record = draw()
    record["sample"][0]["reason"] = "picked"
    assert draw_errors(record)


def test_draw_names_only_verdict_ids() -> None:
    assert draw_errors(draw(considered=["not-a-verdict"]))
    record = draw()
    record["sample"][0]["verdict_id"] = "phase-asr-03"
    assert draw_errors(record)


def test_draw_id_is_a_date_and_counter() -> None:
    assert draw_errors(draw(draw_id="2026-10-09"))


def test_breaking_one_copy_does_not_touch_the_fixture() -> None:
    record = verdict()
    broken = copy.deepcopy(record)
    broken["reviewer"]["type"] = "Demo Adversary"
    assert verdict_errors(broken)
    assert verdict_errors(record) == []


# --- committed records -------------------------------------------------------------


@pytest.mark.parametrize("path", VERDICT_FILES, ids=lambda p: p.stem)
def test_committed_verdict_record_is_valid_and_named_by_its_id(path: Path) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    assert verdict_errors(record) == []
    assert record["verdict_id"] == path.stem
    ids = [f["id"] for f in record["findings"]]
    assert len(ids) == len(set(ids)), f"duplicate finding ids in {path.name}"
