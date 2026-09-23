"""Tests for the review presentation — REQ-002 R11 and R14, ADR-007 sections 5, 7 and 9.

Review shows the claim, not the record: for each flagged or held item, the raw text, the
proposed record, and each assumed field with its level, quote and reason, highest stakes
first. Clean items are listed by id, since they promote in bulk. New tags raise an alert,
and a new tag category is shown as a proposal only. Review writes nothing.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]

from src.capture import promote, structure  # noqa: E402
from src.capture import raw as capture_raw  # noqa: E402
from src.capture.promote import Paths  # noqa: E402
from src.capture.review import build_review, format_review  # noqa: E402

CONTENT = (
    "Decided to drop the old parser because it was too slow. "
    "Promised Jordan the budget sheet by Friday. "
    "Maybe tidy the backlog. "
    "Task: book the venue, created 2026-09-20. "
    "Sam from finance called; tag it hiring."
)


def explicit(value: Any, quote: str) -> dict[str, Any]:
    return {"value": value, "level": "explicit", "quote": quote}


def inferred(value: Any, quote: str, reason: str, flag: bool | None = None) -> dict[str, Any]:
    spec = {"value": value, "level": "inferred", "quote": quote, "reason": reason}
    if flag is not None:
        spec["review_flag"] = flag
    return spec


DECISION = {
    "entity_type": "decision",
    "fields": {
        "decision": explicit("drop the old parser", "drop the old parser"),
        "rationale": explicit("too slow", "it was too slow"),
    },
}
COMMITMENT = {
    "entity_type": "commitment",
    "fields": {
        "description": explicit("send the budget sheet", "the budget sheet"),
        "promised_to": explicit("jordan-rivera", "Jordan"),
        "due_date": inferred("2026-09-25", "by Friday", "Friday of the capture week", flag=True),
    },
}
TASK = {
    "entity_type": "task",
    "fields": {
        "description": {
            "value": "tidy the backlog",
            "level": "guessed",
            "quote": None,
            "reason": "'maybe' reads as a possible task",
        }
    },
}
CLEAN_TASK = {
    "entity_type": "task",
    "fields": {
        "description": explicit("book the venue", "book the venue"),
        "status": explicit("open", "Task:"),
        "created": explicit("2026-09-20", "2026-09-20"),
    },
}
PERSON = {"entity_type": "person", "fields": {"name": explicit("Sam", "Sam")}}


@pytest.fixture
def paths(tmp_path: Path) -> Paths:
    data = tmp_path / "data"
    (data / "people").mkdir(parents=True)
    (data / "people" / "jordan-rivera.json").write_text(
        json.dumps({"id": "jordan-rivera", "name": "Jordan Rivera"}), encoding="utf-8"
    )
    tags = tmp_path / "tags.json"
    tags.write_text(json.dumps([]), encoding="utf-8")
    return Paths(
        staging=tmp_path / "staging",
        promoted=tmp_path / "promoted",
        discarded=tmp_path / "discarded",
        data=data,
        tags=tags,
        schemas=ROOT / "schemas",
    )


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    return tmp_path / "raw"


@pytest.fixture
def capture(raw_dir: Path) -> dict[str, Any]:
    return capture_raw.write_raw_capture(CONTENT, channel="session", raw_dir=raw_dir)


def stage(
    capture: dict[str, Any], raw_dir: Path, paths: Paths, *proposals: Any
) -> list[dict[str, Any]]:
    return structure.stage_capture(
        capture["id"],
        proposals,
        known=promote.known_identities(paths),
        raw_dir=raw_dir,
        staging_dir=paths.staging,
    )


def test_items_are_ordered_by_stakes_highest_first(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    # Staged lowest stakes first, so the order cannot come from staging order.
    stage(capture, raw_dir, paths, TASK, COMMITMENT, DECISION, PERSON)
    review = build_review(paths, raw_dir=raw_dir)
    assert [(i.entity_type, i.stakes) for i in review.items] == [
        ("person", "structural"),
        ("decision", "high"),
        ("commitment", "medium"),
        ("task", "low"),
    ]


def test_clean_items_are_listed_by_id_only(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    clean, _ = stage(capture, raw_dir, paths, CLEAN_TASK, COMMITMENT)
    review = build_review(paths, raw_dir=raw_dir)
    assert review.clean == [clean["id"]]
    assert clean["id"] not in {i.staged_id for i in review.items}


def test_a_clean_record_promotion_would_leave_staged_is_reported_with_its_reason(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    no_status = {
        "entity_type": "task",
        "fields": {"description": explicit("book the venue", "book the venue")},
    }
    note = {"entity_type": "note", "fields": {"text": explicit("book the venue", "book the venue")}}
    ready, incomplete, kept_note = stage(capture, raw_dir, paths, CLEAN_TASK, no_status, note)
    review = build_review(paths, raw_dir=raw_dir)
    assert review.clean == [ready["id"]]
    reasons = dict(review.blocked)
    assert set(reasons) == {incomplete["id"], kept_note["id"]}
    assert "status" in reasons[incomplete["id"]]
    assert "no entity schema for 'note'" in reasons[kept_note["id"]]
    text = format_review(review)
    assert "1 clean, ready to promote in bulk:" in text
    assert "2 clean but left staged by promotion:" in text


def test_each_flagged_item_shows_raw_text_proposal_and_every_assumed_field(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [staged] = stage(capture, raw_dir, paths, COMMITMENT)
    [item] = build_review(paths, raw_dir=raw_dir).items
    assert item.staged_id == staged["id"]
    assert item.raw_text == CONTENT
    assert item.proposed == staged["entity"]
    [assumed] = item.assumed
    assert (assumed.name, assumed.value, assumed.level) == ("due_date", "2026-09-25", "inferred")
    assert (assumed.quote, assumed.reason, assumed.review_flag) == (
        "by Friday",
        "Friday of the capture week",
        True,
    )


def test_a_guessed_field_shows_its_reason_with_no_quote(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    stage(capture, raw_dir, paths, TASK)
    [item] = build_review(paths, raw_dir=raw_dir).items
    [assumed] = item.assumed
    assert (assumed.level, assumed.quote) == ("guessed", None)
    assert assumed.reason == "'maybe' reads as a possible task"


def test_the_text_output_carries_every_part_of_the_claim(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    stage(capture, raw_dir, paths, CLEAN_TASK, COMMITMENT)
    text = format_review(build_review(paths, raw_dir=raw_dir))
    assert "1 clean, ready to promote in bulk:" in text
    assert "[flagged]" in text and "commitment (medium stakes)" in text
    assert f"raw: {CONTENT}" in text
    assert "assumed due_date = '2026-09-25' (inferred, flagged)" in text
    assert "quote: 'by Friday'" in text
    assert "reason: Friday of the capture week" in text


# --- R11: new tags alert, a new category is only proposed --------------------------------


def test_a_held_new_tag_raises_an_alert(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    tag = {
        "entity_type": "tag",
        "fields": {
            "id": explicit("hiring", "hiring"),
            "label": explicit("Hiring", "hiring"),
            "category": explicit("domain", "hiring"),
        },
    }
    stage(capture, raw_dir, paths, tag)
    [item] = build_review(paths, raw_dir=raw_dir).items
    [alert] = item.alerts
    assert alert.startswith("NEW TAG 'hiring' in category 'domain'")
    assert "stays held" in alert and "000343" in alert


def test_a_record_naming_an_unknown_tag_raises_an_alert(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    tagged = {
        "entity_type": "task",
        "fields": {
            "description": explicit("book the venue", "book the venue"),
            "tags": explicit(["hiring"], "hiring"),
        },
    }
    [staged] = stage(capture, raw_dir, paths, tagged)
    assert staged["route"] == "held"
    [item] = build_review(paths, raw_dir=raw_dir).items
    assert item.alerts == ["NEW TAG 'hiring'"]
    assert item.unresolved == ["tags='hiring'"]


def test_a_new_tag_category_is_shown_as_a_proposal_that_review_cannot_approve(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    category = {"entity_type": "tag-category", "fields": {"id": explicit("people-ops", "hiring")}}
    stage(capture, raw_dir, paths, category)
    [item] = build_review(paths, raw_dir=raw_dir).items
    assert item.route == "held" and item.stakes == "structural"
    [alert] = item.alerts
    assert alert.startswith("PROPOSED NEW TAG CATEGORY 'people-ops'")
    assert "schemas/tag.schema.json" in alert


def test_review_writes_nothing(capture: dict[str, Any], raw_dir: Path, paths: Paths) -> None:
    stage(capture, raw_dir, paths, CLEAN_TASK, COMMITMENT, DECISION, PERSON)
    root = paths.staging.parent

    def digest() -> dict[str, str]:
        return {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*"))
            if p.is_file()
        }

    before = digest()
    format_review(build_review(paths, raw_dir=raw_dir))
    assert digest() == before


def test_an_empty_staging_area_says_so(paths: Paths, raw_dir: Path) -> None:
    assert format_review(build_review(paths, raw_dir=raw_dir)) == "Nothing flagged or held.\n"


def test_cli_show_prints_the_review(
    capture: dict[str, Any],
    raw_dir: Path,
    paths: Paths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stage(capture, raw_dir, paths, COMMITMENT)
    monkeypatch.setattr(promote, "STAGING_DIR", paths.staging)
    monkeypatch.setattr(promote, "TAGS_FILE", paths.tags)
    monkeypatch.setenv("D_SYSTEM_DATA_ROOT", str(paths.data))
    monkeypatch.setattr("src.capture.review.RAW_DIR", raw_dir)

    spec = importlib.util.spec_from_file_location("review_cli", ROOT / "tools" / "review.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["review_cli"] = module
    spec.loader.exec_module(module)

    assert module.main(["show"]) == 0
    out = capsys.readouterr().out
    assert "[flagged]" in out and f"raw: {CONTENT}" in out
