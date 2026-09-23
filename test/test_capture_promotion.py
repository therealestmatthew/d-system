"""Tests for promotion and corrections — REQ-002 R2, R10, R12, R13, R15; ADR-007 sections 7-10.

phase-cap-06's acceptance:
- bulk promotion moves only clean records, and a mixed batch leaves flagged and held staged;
- no capture path other than promotion writes to the data root;
- a correction records the field, the previous value and the new one, and the prior value
  stays readable.

Every test works in a temporary tree: a data root, a tags file, raw and staging
directories, and the real schemas.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]

from src.capture import (  # noqa: E402
    promote,  # noqa: E402
    review,
    structure,
)
from src.capture import raw as capture_raw  # noqa: E402
from src.capture.promote import Paths, PromotionError  # noqa: E402

TODAY = dt.date(2026, 9, 23)

CONTENT = (
    "Task: book the venue for the offsite, created 2026-09-20. "
    "Promised Jordan the budget sheet by Friday. "
    "Sam wants the logo files. "
    "Met Priya and Lee about hiring on 2026-09-21."
)


def explicit(value: Any, quote: str) -> dict[str, Any]:
    return {"value": value, "level": "explicit", "quote": quote}


def inferred(value: Any, quote: str, flag: bool | None = None) -> dict[str, Any]:
    spec = {"value": value, "level": "inferred", "quote": quote, "reason": "read from context"}
    if flag is not None:
        spec["review_flag"] = flag
    return spec


CLEAN_TASK = {
    "entity_type": "task",
    "fields": {
        "description": explicit("book the venue for the offsite", "book the venue for the offsite"),
        "status": explicit("open", "Task:"),
        "created": explicit("2026-09-20", "2026-09-20"),
    },
}

FLAGGED_COMMITMENT = {
    "entity_type": "commitment",
    "fields": {
        "description": explicit("send the budget sheet", "the budget sheet"),
        "promised_to": explicit("jordan-rivera", "Jordan"),
        "due_date": inferred("2026-09-25", "by Friday", flag=True),
        "status": explicit("open", "Promised"),
        "priority": inferred("medium", "Promised"),
        "created": inferred("2026-09-20", "2026-09-20"),
    },
}

HELD_COMMITMENT = {
    "entity_type": "commitment",
    "fields": {
        "description": explicit("send the logo files", "the logo files"),
        "promised_to": explicit("Sam", "Sam"),
        "status": explicit("open", "wants"),
        "priority": explicit("low", "wants"),
        "created": explicit("2026-09-20", "2026-09-20"),
    },
}


@pytest.fixture
def paths(tmp_path: Path) -> Paths:
    data = tmp_path / "data"
    (data / "people").mkdir(parents=True)
    (data / "people" / "jordan-rivera.json").write_text(
        json.dumps({"id": "jordan-rivera", "name": "Jordan Rivera"}), encoding="utf-8"
    )
    (data / "tasks").mkdir()
    (data / "tasks" / "t-3.json").write_text(
        json.dumps(
            {"id": "t-3", "description": "existing", "status": "open", "created": "2026-09-01"}
        ),
        encoding="utf-8",
    )
    tags = tmp_path / "tags.json"
    tags.write_text(
        json.dumps([{"id": "ai-tools", "label": "AI tools", "category": "tech"}]),
        encoding="utf-8",
    )
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


def tree_digest(directory: Path) -> dict[str, str]:
    return {
        str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(directory.rglob("*"))
        if p.is_file()
    }


def staged_ids(paths: Paths) -> set[str]:
    return {p.stem for p in paths.staging.glob("*.json")}


# --- R13: bulk promotion moves only clean records ---------------------------------------


def test_mixed_batch_routes_as_expected(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    records = stage(capture, raw_dir, paths, CLEAN_TASK, FLAGGED_COMMITMENT, HELD_COMMITMENT)
    assert [r["route"] for r in records] == ["clean", "flagged", "held"]


def test_bulk_promotion_moves_only_clean_records(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    clean, flagged, held = stage(
        capture, raw_dir, paths, CLEAN_TASK, FLAGGED_COMMITMENT, HELD_COMMITMENT
    )

    result = promote.promote_clean(paths, today=TODAY)

    assert [staged_id for staged_id, _ in result.promoted] == [clean["id"]]
    assert result.skipped == []
    assert staged_ids(paths) == {flagged["id"], held["id"]}
    assert not (paths.data / "commitments").exists()
    promoted = json.loads((paths.data / "tasks" / "t-4.json").read_text(encoding="utf-8"))
    assert promoted["description"] == "book the venue for the offsite"
    assert promoted["capture"] == {
        "capture_id": capture["id"],
        "assumed_fields": [],
        "promoted": "2026-09-23",
    }
    archived = json.loads((paths.promoted / f"{clean['id']}.json").read_text(encoding="utf-8"))
    assert archived["action"] == "promoted" and archived["record_id"] == "t-4"


def test_bulk_promotion_numbers_after_existing_and_within_the_batch(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    stage(capture, raw_dir, paths, CLEAN_TASK, CLEAN_TASK)
    promote.promote_clean(paths, today=TODAY)
    assert sorted(p.stem for p in (paths.data / "tasks").glob("*.json")) == ["t-3", "t-4", "t-5"]


def test_a_clean_record_that_does_not_validate_stays_staged_with_the_reason(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    no_created = {
        "entity_type": "task",
        "fields": {"description": explicit("book the venue", "book the venue")},
    }
    note = {"entity_type": "note", "fields": {"text": explicit("offsite", "offsite")}}
    incomplete, kept_note = stage(capture, raw_dir, paths, no_created, note)
    assert incomplete["route"] == kept_note["route"] == "clean"

    result = promote.promote_clean(paths, today=TODAY)

    assert result.promoted == []
    reasons = dict(result.skipped)
    assert "created" in reasons[incomplete["id"]] and "status" in reasons[incomplete["id"]]
    assert "no entity schema for 'note'" in reasons[kept_note["id"]]
    assert staged_ids(paths) == {incomplete["id"], kept_note["id"]}
    assert tree_digest(paths.data / "tasks") == {
        "t-3.json": hashlib.sha256((paths.data / "tasks" / "t-3.json").read_bytes()).hexdigest()
    }


# --- promotion never overwrites, never duplicates, never leaves the data root -----------


def _with_id(task_id: str) -> dict[str, Any]:
    return {
        "entity_type": "task",
        "fields": {**CLEAN_TASK["fields"], "id": explicit(task_id, "Task:")},
    }


def test_a_proposal_carrying_its_own_id_is_refused_not_written_over_a_record(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    before = tree_digest(paths.data)
    [staged] = stage(capture, raw_dir, paths, _with_id("t-3"))
    result = promote.promote_clean(paths, today=TODAY)
    assert result.promoted == []
    assert "promotion assigns the id" in dict(result.skipped)[staged["id"]]
    assert tree_digest(paths.data) == before
    assert staged_ids(paths) == {staged["id"]}


def test_the_owner_cannot_set_an_id_either(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [staged] = stage(capture, raw_dir, paths, FLAGGED_COMMITMENT)
    with pytest.raises(PromotionError, match="promotion assigns the id"):
        promote.promote_one(staged["id"], {"id": "c-1"}, paths=paths, today=TODAY)


def test_duplicate_supplied_ids_in_one_batch_lose_nothing(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    first, second = stage(capture, raw_dir, paths, _with_id("t-10"), _with_id("t-10"))
    result = promote.promote_clean(paths, today=TODAY)
    assert result.promoted == []
    assert staged_ids(paths) == {first["id"], second["id"]}


def test_an_id_that_would_escape_the_data_root_is_refused(
    capture: dict[str, Any], raw_dir: Path, paths: Paths, tmp_path: Path
) -> None:
    stage(capture, raw_dir, paths, _with_id("t-9/../../../ESCAPED"))
    promote.promote_clean(paths, today=TODAY)
    assert not list(tmp_path.rglob("ESCAPED*"))


def test_the_record_writer_refuses_an_existing_file(paths: Paths) -> None:
    existing = paths.data / "tasks" / "t-3.json"
    before = existing.read_bytes()
    with pytest.raises(PromotionError, match="already exists"):
        promote._create_json(existing, {"id": "t-3"})
    assert existing.read_bytes() == before


def test_a_failure_mid_batch_skips_that_record_and_writes_nothing_for_it(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [clean] = stage(capture, raw_dir, paths, CLEAN_TASK)
    paths.promoted.parent.mkdir(parents=True, exist_ok=True)
    paths.promoted.write_text("not a directory", encoding="utf-8")
    before = tree_digest(paths.data)

    result = promote.promote_clean(paths, today=TODAY)

    assert result.promoted == [] and [s for s, _ in result.skipped] == [clean["id"]]
    assert tree_digest(paths.data) == before
    assert staged_ids(paths) == {clean["id"]}


def test_an_interrupted_promotion_is_finished_not_repeated(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [clean] = stage(capture, raw_dir, paths, CLEAN_TASK)
    staged_copy = (paths.staging / f"{clean['id']}.json").read_bytes()
    promote.promote_clean(paths, today=TODAY)
    # Simulate a crash after the record was written but before the staged copy was removed.
    (paths.staging / f"{clean['id']}.json").write_bytes(staged_copy)

    result = promote.promote_clean(paths, today=TODAY)

    assert result.promoted == [(clean["id"], str(paths.data / "tasks" / "t-4.json"))]
    assert sorted(p.stem for p in (paths.data / "tasks").glob("*.json")) == ["t-3", "t-4"]
    assert staged_ids(paths) == set()


def test_an_archive_entry_with_no_record_is_promoted_afresh(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [clean] = stage(capture, raw_dir, paths, CLEAN_TASK)
    paths.promoted.mkdir(parents=True)
    (paths.promoted / f"{clean['id']}.json").write_text(
        json.dumps({"target": str(paths.data / "tasks" / "t-4.json")}), encoding="utf-8"
    )
    result = promote.promote_clean(paths, today=TODAY)
    assert [s for s, _ in result.promoted] == [clean["id"]]
    assert (paths.data / "tasks" / "t-4.json").exists()


def test_an_interrupted_promotion_never_settles_on_another_records_file(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    first, second = stage(capture, raw_dir, paths, CLEAN_TASK, FLAGGED_COMMITMENT)
    # A crash left `first` with an archive entry for t-4 but no record ...
    paths.promoted.mkdir(parents=True)
    (paths.promoted / f"{first['id']}.json").write_text(
        json.dumps(
            {
                "action": "promoted",
                "record_id": "t-4",
                "target": str(paths.data / "tasks" / "t-4.json"),
            }
        ),
        encoding="utf-8",
    )
    # ... and another record has since been promoted as t-4.
    (paths.data / "tasks" / "t-4.json").write_text(
        json.dumps(
            {
                "id": "t-4",
                "description": "someone else",
                "status": "open",
                "created": "2026-09-22",
                "capture": {"capture_id": "cap-other", "assumed_fields": [], "promoted": "x"},
            }
        ),
        encoding="utf-8",
    )

    result = promote.promote_clean(paths, today=TODAY)

    assert result.promoted == [(first["id"], str(paths.data / "tasks" / "t-5.json"))]
    record = json.loads((paths.data / "tasks" / "t-5.json").read_text(encoding="utf-8"))
    assert record["capture"]["capture_id"] == first["capture_id"]
    other = json.loads((paths.data / "tasks" / "t-4.json").read_text(encoding="utf-8"))
    assert other["description"] == "someone else"


def test_a_pending_promotion_reserves_its_id_from_a_record_of_the_same_capture(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    first, second = stage(capture, raw_dir, paths, CLEAN_TASK, FLAGGED_COMMITMENT)
    assert first["capture_id"] == second["capture_id"]
    task_two = {**CLEAN_TASK, "fields": {**CLEAN_TASK["fields"]}}
    task_two["fields"]["description"] = explicit("book the venue", "book the venue")
    [third] = stage(capture, raw_dir, paths, task_two)
    # A crash left `first` with an archive entry for t-4 but no record.
    paths.promoted.mkdir(parents=True)
    (paths.promoted / f"{first['id']}.json").write_text(
        json.dumps(
            {
                "action": "promoted",
                "record_id": "t-4",
                "target": str(paths.data / "tasks" / "t-4.json"),
            }
        ),
        encoding="utf-8",
    )
    # A record from the same capture, promoted meanwhile, must not take t-4.
    promote.promote_one(third["id"], paths=paths, today=TODAY)
    assert not (paths.data / "tasks" / "t-4.json").exists()

    result = promote.promote_clean(paths, today=TODAY)

    assert first["id"] in {s for s, _ in result.promoted}
    descriptions = sorted(
        json.loads(p.read_text(encoding="utf-8"))["description"]
        for p in (paths.data / "tasks").glob("*.json")
    )
    assert descriptions == ["book the venue", "book the venue for the offsite", "existing"]
    assert first["id"] not in staged_ids(paths)


@pytest.mark.parametrize("entry", ["[1, 2]", '{"record_id": 4}', "{torn"])
def test_a_malformed_archive_entry_is_dropped_and_the_record_promoted_afresh(
    capture: dict[str, Any], raw_dir: Path, paths: Paths, entry: str
) -> None:
    [clean] = stage(capture, raw_dir, paths, CLEAN_TASK)
    paths.promoted.mkdir(parents=True)
    (paths.promoted / f"{clean['id']}.json").write_text(entry, encoding="utf-8")
    result = promote.promote_clean(paths, today=TODAY)
    assert [s for s, _ in result.promoted] == [clean["id"]]


@pytest.mark.parametrize("bad_id", ["../data/people/jordan-rivera", "staged-other"])
def test_a_staged_file_whose_id_is_not_its_own_is_refused_before_any_write(
    capture: dict[str, Any], raw_dir: Path, paths: Paths, bad_id: str
) -> None:
    [clean] = stage(capture, raw_dir, paths, CLEAN_TASK)
    staged_file = paths.staging / f"{clean['id']}.json"
    staged_file.write_text(json.dumps({**clean, "id": bad_id}), encoding="utf-8")
    before = tree_digest(paths.data)
    with pytest.raises(PromotionError):
        promote.promote_clean(paths, today=TODAY)
    with pytest.raises(PromotionError):
        promote.discard(clean["id"], paths=paths, today=TODAY)
    assert tree_digest(paths.data) == before
    assert staged_file.exists()


@pytest.mark.parametrize("action", ["promote", "create", "discard"])
def test_a_staged_id_that_is_a_path_is_refused(
    action: str, capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    before = tree_digest(paths.data)
    traversal = "../data/people/jordan-rivera"
    with pytest.raises(PromotionError, match="is not a staged id"):
        if action == "promote":
            promote.promote_one(traversal, paths=paths, today=TODAY)
        elif action == "create":
            promote.create_identity(traversal, paths=paths, today=TODAY)
        else:
            promote.discard(traversal, paths=paths, today=TODAY)
    assert tree_digest(paths.data) == before


# --- flagged and held records: one owner decision each ----------------------------------


def test_promoting_a_flagged_record_keeps_its_assumed_fields(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [flagged] = stage(capture, raw_dir, paths, FLAGGED_COMMITMENT)
    promote.promote_one(flagged["id"], paths=paths, today=TODAY)
    record = json.loads((paths.data / "commitments" / "c-1.json").read_text(encoding="utf-8"))
    assert record["capture"]["assumed_fields"] == ["created", "due_date", "priority"]


def test_a_value_the_owner_states_is_no_longer_assumed(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [flagged] = stage(capture, raw_dir, paths, FLAGGED_COMMITMENT)
    promote.promote_one(flagged["id"], {"due_date": "2026-09-26"}, paths=paths, today=TODAY)
    record = json.loads((paths.data / "commitments" / "c-1.json").read_text(encoding="utf-8"))
    assert record["due_date"] == "2026-09-26"
    assert record["capture"]["assumed_fields"] == ["created", "priority"]


def test_a_held_record_is_refused_until_its_reference_resolves(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [held] = stage(capture, raw_dir, paths, HELD_COMMITMENT)
    with pytest.raises(PromotionError, match="promised_to='Sam'"):
        promote.promote_one(held["id"], paths=paths, today=TODAY)
    assert staged_ids(paths) == {held["id"]}
    assert not (paths.data / "commitments").exists()

    promote.promote_one(held["id"], {"promised_to": "jordan-rivera"}, paths=paths, today=TODAY)
    assert (paths.data / "commitments" / "c-1.json").exists()
    assert staged_ids(paths) == set()


def test_plain_names_are_kept_only_on_the_owners_confirmation(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    meeting = {
        "entity_type": "interaction",
        "fields": {
            "date": explicit("2026-09-21", "2026-09-21"),
            "type": explicit("meeting", "Met"),
            "summary": explicit("hiring", "about hiring"),
            "participant_names": explicit(["Priya", "Lee"], "Priya and Lee"),
        },
    }
    [held] = stage(capture, raw_dir, paths, meeting)
    assert held["route"] == "held"
    with pytest.raises(PromotionError, match="participant_names"):
        promote.promote_one(held["id"], paths=paths, today=TODAY)

    promote.promote_one(held["id"], keep_names=True, paths=paths, today=TODAY)
    record = json.loads((paths.data / "interactions" / "i-1.json").read_text(encoding="utf-8"))
    assert record["participant_names"] == ["Priya", "Lee"]


# --- identity decisions -----------------------------------------------------------------


def test_creating_a_held_person_writes_the_person_and_unblocks_references(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    person = {"entity_type": "person", "fields": {"name": explicit("Sam", "Sam")}}
    held_person, held_commitment = stage(capture, raw_dir, paths, person, HELD_COMMITMENT)

    with pytest.raises(PromotionError, match="identity call"):
        promote.promote_one(held_person["id"], paths=paths, today=TODAY)
    with pytest.raises(PromotionError, match="id"):
        promote.create_identity(held_person["id"], paths=paths, today=TODAY)

    target = promote.create_identity(held_person["id"], {"id": "sam-lee"}, paths=paths, today=TODAY)
    assert target == str(paths.data / "people" / "sam-lee.json")

    promote.promote_one(held_commitment["id"], {"promised_to": "sam-lee"}, paths=paths, today=TODAY)
    assert staged_ids(paths) == set()


def test_a_new_tag_from_a_capture_stays_held(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    # Owner ruling (idea 000343): capture-derived tags go under the private data root, and
    # nothing reads a private tag file yet, so the tracked tags file is never written here.
    tag = {
        "entity_type": "tag",
        "fields": {
            "id": explicit("hiring", "hiring"),
            "label": explicit("Hiring", "hiring"),
            "category": inferred("domain", "hiring"),
        },
    }
    before = paths.tags.read_bytes()
    [held] = stage(capture, raw_dir, paths, tag)
    with pytest.raises(PromotionError, match="000343"):
        promote.create_identity(held["id"], paths=paths, today=TODAY)
    assert paths.tags.read_bytes() == before
    assert staged_ids(paths) == {held["id"]}


def test_a_new_tag_category_stays_held(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    category = {"entity_type": "tag-category", "fields": {"id": explicit("people-ops", "hiring")}}
    [held] = stage(capture, raw_dir, paths, category)
    with pytest.raises(PromotionError, match="tag.schema.json"):
        promote.create_identity(held["id"], paths=paths, today=TODAY)
    assert staged_ids(paths) == {held["id"]}


def test_discard_moves_the_record_out_of_staging_without_promoting_it(
    capture: dict[str, Any], raw_dir: Path, paths: Paths
) -> None:
    [flagged] = stage(capture, raw_dir, paths, FLAGGED_COMMITMENT)
    promote.discard(flagged["id"], paths=paths, today=TODAY)
    assert staged_ids(paths) == set()
    assert (paths.discarded / f"{flagged['id']}.json").exists()
    assert not (paths.data / "commitments").exists()


# --- R12: no capture path but promotion writes to the data root -------------------------


def test_no_capture_path_other_than_promotion_writes_to_the_data_root(
    tmp_path: Path, raw_dir: Path, paths: Paths
) -> None:
    before = tree_digest(paths.data)
    tags_before = paths.tags.read_bytes()

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "note.txt").write_text(CONTENT, encoding="utf-8")
    capture_raw.scan_inbox(inbox_dir=inbox, raw_dir=raw_dir)
    capture = capture_raw.write_raw_capture(CONTENT, channel="cli", raw_dir=raw_dir)
    stage(capture, raw_dir, paths, CLEAN_TASK, FLAGGED_COMMITMENT, HELD_COMMITMENT)
    review.format_review(review.build_review(paths, raw_dir=raw_dir))
    [held] = [r["id"] for r in promote.load_staged(paths.staging) if r["route"] == "held"]
    promote.discard(held, paths=paths, today=TODAY)

    assert tree_digest(paths.data) == before
    assert paths.tags.read_bytes() == tags_before

    promote.promote_clean(paths, today=TODAY)
    assert tree_digest(paths.data) != before


# --- R15 and R2: corrections -------------------------------------------------------------


@pytest.fixture
def promoted_commitment(capture: dict[str, Any], raw_dir: Path, paths: Paths) -> Path:
    [flagged] = stage(capture, raw_dir, paths, FLAGGED_COMMITMENT)
    promote.promote_one(flagged["id"], paths=paths, today=TODAY)
    return paths.data / "commitments" / "c-1.json"


def test_a_correction_records_field_previous_and_new_and_keeps_the_prior_value(
    promoted_commitment: Path, paths: Paths
) -> None:
    entry = promote.correct(
        "commitment", "c-1", "due_date", "2026-09-30", reason="moved", paths=paths, today=TODAY
    )
    assert entry == {
        "record_type": "commitment",
        "record_id": "c-1",
        "field": "due_date",
        "previous": "2026-09-25",
        "new": "2026-09-30",
        "corrected": "2026-09-23",
        "reason": "moved",
    }
    record = json.loads(promoted_commitment.read_text(encoding="utf-8"))
    assert record["due_date"] == "2026-09-30"
    assert promote.corrections("commitment", "c-1", paths) == [entry]


def test_corrections_append_and_never_rewrite(promoted_commitment: Path, paths: Paths) -> None:
    promote.correct("commitment", "c-1", "due_date", "2026-09-30", paths=paths, today=TODAY)
    log = paths.data / promote.CORRECTIONS_FILE
    first = log.read_bytes()
    promote.correct("commitment", "c-1", "priority", "high", paths=paths, today=TODAY)
    assert log.read_bytes().startswith(first)
    history = promote.corrections("commitment", "c-1", paths)
    assert [(e["field"], e["previous"], e["new"]) for e in history] == [
        ("due_date", "2026-09-25", "2026-09-30"),
        ("priority", "medium", "high"),
    ]


def test_every_correction_entry_validates_against_its_schema(
    promoted_commitment: Path, paths: Paths
) -> None:
    promote.correct("commitment", "c-1", "notes", "called ahead", paths=paths, today=TODAY)
    validator = promote._validator(paths.schemas, "correction")
    for line in (paths.data / promote.CORRECTIONS_FILE).read_text(encoding="utf-8").splitlines():
        assert list(validator.iter_errors(json.loads(line))) == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("status", "maybe", "would not validate"),
        ("id", "c-9", "cannot be corrected"),
        ("capture", None, "cannot be corrected"),
        ("due_date", "2026-09-25", "already holds"),
    ],
)
def test_a_refused_correction_changes_nothing(
    promoted_commitment: Path, paths: Paths, field: str, value: Any, message: str
) -> None:
    before = tree_digest(paths.data)
    with pytest.raises(PromotionError, match=message):
        promote.correct("commitment", "c-1", field, value, paths=paths, today=TODAY)
    assert tree_digest(paths.data) == before


def test_a_correction_leaves_the_raw_capture_untouched(
    promoted_commitment: Path, paths: Paths, raw_dir: Path
) -> None:
    before = tree_digest(raw_dir)
    promote.correct("commitment", "c-1", "due_date", "2026-09-30", paths=paths, today=TODAY)
    assert tree_digest(raw_dir) == before


def test_a_correction_may_not_name_an_unknown_person_or_tag(
    promoted_commitment: Path, paths: Paths
) -> None:
    before = tree_digest(paths.data)
    with pytest.raises(PromotionError, match="promised_to='nobody'"):
        promote.correct("commitment", "c-1", "promised_to", "nobody", paths=paths, today=TODAY)
    with pytest.raises(PromotionError, match="tags='no-such-tag'"):
        promote.correct("commitment", "c-1", "tags", ["no-such-tag"], paths=paths, today=TODAY)
    assert tree_digest(paths.data) == before


def test_correcting_an_absent_field_says_it_was_absent(
    promoted_commitment: Path, paths: Paths
) -> None:
    entry = promote.correct("commitment", "c-1", "notes", "called ahead", paths=paths, today=TODAY)
    assert entry["previous"] is None and entry["previous_absent"] is True
    second = promote.correct("commitment", "c-1", "completed", None, paths=paths, today=TODAY)
    assert second["previous_absent"] is True
    third = promote.correct("commitment", "c-1", "due_date", None, paths=paths, today=TODAY)
    assert "previous_absent" not in third


def test_a_correction_that_cannot_be_logged_leaves_the_record_unchanged(
    promoted_commitment: Path, paths: Paths
) -> None:
    (paths.data / promote.CORRECTIONS_FILE).mkdir()
    before = promoted_commitment.read_bytes()
    with pytest.raises(PromotionError, match="could not record the correction"):
        promote.correct("commitment", "c-1", "priority", "high", paths=paths, today=TODAY)
    assert promoted_commitment.read_bytes() == before


@pytest.mark.parametrize("record_id", ["../people/jordan-rivera", "../../outside/c-1", "C-1"])
def test_a_correction_to_a_path_rather_than_a_record_id_is_refused(
    promoted_commitment: Path, paths: Paths, tmp_path: Path, record_id: str
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "c-1.json").write_bytes(promoted_commitment.read_bytes())
    before = tree_digest(tmp_path)
    with pytest.raises(PromotionError, match="is not a record id"):
        promote.correct("commitment", record_id, "priority", "high", paths=paths, today=TODAY)
    assert tree_digest(tmp_path) == before


def test_a_torn_log_line_does_not_swallow_the_next_correction(
    promoted_commitment: Path, paths: Paths
) -> None:
    promote.correct("commitment", "c-1", "due_date", "2026-09-30", paths=paths, today=TODAY)
    log = paths.data / promote.CORRECTIONS_FILE
    # A crash part-way through an append leaves a last line with no newline.
    with log.open("a", encoding="utf-8") as handle:
        handle.write('{"record_type": "commitment", "record_id": "c-1", "fi')

    promote.correct("commitment", "c-1", "priority", "high", paths=paths, today=TODAY)

    history = promote.corrections("commitment", "c-1", paths)
    assert [(e["field"], e["previous"], e["new"]) for e in history] == [
        ("due_date", "2026-09-25", "2026-09-30"),
        ("priority", "medium", "high"),
    ]


def test_a_tear_inside_a_multibyte_character_does_not_hide_other_corrections(
    promoted_commitment: Path, paths: Paths
) -> None:
    promote.correct("commitment", "c-1", "due_date", "2026-09-30", paths=paths, today=TODAY)
    log = paths.data / promote.CORRECTIONS_FILE
    with log.open("ab") as handle:
        handle.write('{"record_type": "commitment", "reason": "café'.encode()[:-1])

    promote.correct("commitment", "c-1", "priority", "high", paths=paths, today=TODAY)

    history = promote.corrections("commitment", "c-1", paths)
    assert [e["field"] for e in history] == ["due_date", "priority"]


# --- the CLI ---------------------------------------------------------------------------


def _load_cli() -> Any:
    spec = importlib.util.spec_from_file_location("review_cli", ROOT / "tools" / "review.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["review_cli"] = module
    spec.loader.exec_module(module)
    return module


review_cli = _load_cli()


@pytest.fixture
def cli_paths(paths: Paths, monkeypatch: pytest.MonkeyPatch) -> Paths:
    monkeypatch.setattr(promote, "STAGING_DIR", paths.staging)
    monkeypatch.setattr(promote, "PROMOTED_DIR", paths.promoted)
    monkeypatch.setattr(promote, "DISCARDED_DIR", paths.discarded)
    monkeypatch.setattr(promote, "TAGS_FILE", paths.tags)
    monkeypatch.setenv("D_SYSTEM_DATA_ROOT", str(paths.data))
    return paths


def test_cli_promotes_clean_and_one_record_and_corrects(
    capture: dict[str, Any],
    raw_dir: Path,
    cli_paths: Paths,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, flagged, _ = stage(
        capture, raw_dir, cli_paths, CLEAN_TASK, FLAGGED_COMMITMENT, HELD_COMMITMENT
    )
    assert review_cli.main(["promote", "--clean"]) == 0
    assert review_cli.main(["promote", flagged["id"], "--set", "due_date=2026-09-26"]) == 0
    assert review_cli.main(["correct", "commitment", "c-1", "priority", "high"]) == 0
    out = capsys.readouterr().out
    assert "promoted" in out and "'medium' -> 'high'" in out
    assert (cli_paths.data / "tasks" / "t-4.json").exists()


def test_cli_refuses_ambiguous_promotion_and_exits_non_zero(
    cli_paths: Paths, capsys: pytest.CaptureFixture[str]
) -> None:
    assert review_cli.main(["promote"]) == 1
    assert review_cli.main(["promote", "--clean", "--keep-names"]) == 1
    assert review_cli.main(["promote", "staged-00000000T000000Z-000000"]) == 1
    assert "error:" in capsys.readouterr().err


def test_cli_reports_a_malformed_value_as_an_error_not_a_traceback(
    capture: dict[str, Any],
    raw_dir: Path,
    cli_paths: Paths,
    capsys: pytest.CaptureFixture[str],
) -> None:
    [flagged] = stage(capture, raw_dir, cli_paths, FLAGGED_COMMITMENT)
    assert review_cli.main(["promote", flagged["id"], "--set", "tags=hiring"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: ") and "field 'tags' must be a list of strings" in err


def test_cli_refuses_to_create_a_tag(
    capture: dict[str, Any],
    raw_dir: Path,
    cli_paths: Paths,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tag = {
        "entity_type": "tag",
        "fields": {
            "id": explicit("hiring", "hiring"),
            "label": explicit("Hiring", "hiring"),
            "category": explicit("domain", "hiring"),
        },
    }
    [held] = stage(capture, raw_dir, cli_paths, tag)
    assert review_cli.main(["create", held["id"]]) == 1
    assert "000343" in capsys.readouterr().err


def test_cli_set_reads_json_when_it_parses() -> None:
    assert review_cli._assignments(["a=3", "b=true", "c=[1]", "d=text", "e=null"]) == {
        "a": 3,
        "b": True,
        "c": [1],
        "d": "text",
        "e": None,
    }
