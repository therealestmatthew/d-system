"""Tests for structuring, evidence scoring and routing — REQ-002 R3/R4/R6-R10, ADR-007 3-7.

phase-cap-05 takes an agent's proposal for a raw capture, checks it against the raw text
and the never-invent rules, routes it on stakes crossed with evidence, and stages it. The
fixtures here define correct routing for everything downstream: the matrix test is the
routing table, cell by cell.
"""

from __future__ import annotations

import builtins
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]

from src.capture import raw as capture_raw  # noqa: E402
from src.capture import routing, structure  # noqa: E402
from src.capture.structure import KnownIdentities, StructuringError  # noqa: E402

CONTENT = (
    "Told Jordan I'd send the automation deck by Friday. "
    "Decided to drop the old parser because it was too slow. "
    "Someone mentioned a workshop, maybe."
)

KNOWN = KnownIdentities(
    people=frozenset({"jordan-rivera"}),
    projects=frozenset({"automation-toolkit"}),
    tags=frozenset({"ai-tools"}),
)


def _load_cli() -> Any:
    spec = importlib.util.spec_from_file_location("capture", ROOT / "tools" / "capture.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["capture"] = module
    spec.loader.exec_module(module)
    return module


capture_cli = _load_cli()


def explicit(value: Any, quote: str) -> dict[str, Any]:
    return {"value": value, "level": "explicit", "quote": quote}


def inferred(value: Any, quote: str, flag: bool | None = None) -> dict[str, Any]:
    spec = {"value": value, "level": "inferred", "quote": quote, "reason": "read from context"}
    if flag is not None:
        spec["review_flag"] = flag
    return spec


def guessed(value: Any, flag: bool | None = None) -> dict[str, Any]:
    spec = {"value": value, "level": "guessed", "quote": None, "reason": "pattern match only"}
    if flag is not None:
        spec["review_flag"] = flag
    return spec


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    return tmp_path / "raw"


@pytest.fixture
def staging_dir(tmp_path: Path) -> Path:
    return tmp_path / "staging"


@pytest.fixture
def capture(raw_dir: Path) -> dict[str, Any]:
    return capture_raw.write_raw_capture(CONTENT, channel="session", raw_dir=raw_dir)


def _stage(capture: dict[str, Any], raw_dir: Path, staging_dir: Path, *proposals: Any) -> Any:
    return structure.stage_capture(
        capture["id"], proposals, known=KNOWN, raw_dir=raw_dir, staging_dir=staging_dir
    )


# --- R8: the stakes-by-evidence matrix ---------------------------------------------------

EVIDENCE_CELLS = {
    "explicit": explicit("the old parser", "the old parser"),
    "inferred": inferred("the old parser", "too slow"),
    "guessed": guessed("the old parser"),
}

EXPECTED_ROUTE = {
    "low": {"explicit": "clean", "inferred": "flagged", "guessed": "flagged"},
    "medium": {"explicit": "clean", "inferred": "flagged", "guessed": "flagged"},
    "high": {"explicit": "flagged", "inferred": "flagged", "guessed": "flagged"},
    "structural": {"explicit": "held", "inferred": "held", "guessed": "held"},
}

MATRIX = [
    (entity_type, stakes, level)
    for entity_type, stakes in routing.STAKES.items()
    for level in EVIDENCE_CELLS
]


def test_matrix_covers_every_stakes_tier_and_evidence_level() -> None:
    assert {s for _, s, _ in MATRIX} == {"low", "medium", "high", "structural"}
    assert {lvl for _, _, lvl in MATRIX} == {"explicit", "inferred", "guessed"}


@pytest.mark.parametrize(("entity_type", "stakes", "level"), MATRIX)
def test_each_matrix_cell_produces_the_stated_route(
    capture: dict[str, Any],
    raw_dir: Path,
    staging_dir: Path,
    entity_type: str,
    stakes: str,
    level: str,
) -> None:
    proposal = {
        "entity_type": entity_type,
        "fields": {
            "description": explicit("drop the old parser", "drop the old parser"),
            "notes": EVIDENCE_CELLS[level],
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == EXPECTED_ROUTE[stakes][level]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("promised_to", "Dana"),
        ("owed_by", "Dana"),
        ("project_id", "unknown-project"),
        ("tags", ["brand-new-tag"]),
        ("participants", ["dana"]),
        ("participant_names", ["Dana"]),
        ("decided_by_names", ["Dana"]),
    ],
)
def test_an_unresolved_reference_holds_an_otherwise_clean_record(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path, field: str, value: Any
) -> None:
    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("send the automation deck", "send the automation deck"),
            field: explicit(value, "Jordan"),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == "held"
    assert record["entity"][field] == value  # kept as written, not resolved or dropped


def test_known_references_do_not_hold(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("send the automation deck", "send the automation deck"),
            "promised_to": explicit("jordan-rivera", "Told Jordan"),
            "project_id": explicit("automation-toolkit", "automation deck"),
            "tags": explicit(["ai-tools"], "automation"),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == "clean"


def test_routing_refuses_an_unknown_entity_type() -> None:
    with pytest.raises(routing.RoutingError, match="meeting-note"):
        routing.route_for("meeting-note", ["explicit"])


# --- R6: evidence and provenance per field -----------------------------------------------


def test_every_field_carries_its_level_and_located_provenance(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {
        "entity_type": "decision",
        "fields": {
            "decision": explicit("Drop the old parser", "Decided to drop the old parser"),
            "rationale": explicit("It was too slow", "because it was too slow"),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    for name, evidence in record["evidence"].items():
        provenance = evidence["provenance"]
        assert evidence["level"] == "explicit"
        assert provenance["capture_id"] == capture["id"]
        assert CONTENT[provenance["start"]:provenance["end"]] == provenance["quote"], name


def test_a_quote_absent_from_the_raw_text_is_refused(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {"entity_type": "task", "fields": {"description": explicit("x", "not in text")}}
    with pytest.raises(StructuringError, match="description"):
        _stage(capture, raw_dir, staging_dir, proposal)
    assert not staging_dir.exists()


def test_a_field_without_an_evidence_level_is_refused(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {"entity_type": "task", "fields": {"description": {"value": "x"}}}
    with pytest.raises(StructuringError, match="description"):
        _stage(capture, raw_dir, staging_dir, proposal)


def test_an_inferred_field_without_a_reason_is_refused(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    spec = {"value": "x", "level": "inferred", "quote": "Jordan"}
    proposal = {"entity_type": "task", "fields": {"notes": spec}}
    with pytest.raises(StructuringError, match="reason"):
        _stage(capture, raw_dir, staging_dir, proposal)


# --- R3: every staged record names a resolvable source ----------------------------------


def test_an_unresolvable_capture_id_is_refused(raw_dir: Path, staging_dir: Path) -> None:
    proposal = {"entity_type": "task", "fields": {"description": guessed("x")}}
    with pytest.raises(StructuringError, match="does not resolve"):
        structure.stage_capture(
            "raw-20260101T000000Z-abcdef", [proposal], known=KNOWN,
            raw_dir=raw_dir, staging_dir=staging_dir,
        )
    assert not staging_dir.exists()


def test_staged_records_are_written_and_name_their_capture(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposals = [
        {"entity_type": "task", "fields": {"description": explicit("send deck", "send the")}},
        {"entity_type": "note", "fields": {"description": explicit("workshop", "a workshop")}},
    ]
    records = _stage(capture, raw_dir, staging_dir, *proposals)
    on_disk = [json.loads(p.read_text()) for p in staging_dir.glob("*.json")]
    assert sorted(records, key=lambda r: r["id"]) == sorted(on_disk, key=lambda r: r["id"])
    assert {r["capture_id"] for r in on_disk} == {capture["id"]}


# --- R7: the never-invent rules -----------------------------------------------------------


@pytest.mark.parametrize(
    ("entity_type", "field", "spec"),
    [
        ("commitment", "promised_to", inferred("jordan-rivera", "Told Jordan")),
        ("commitment", "due_date", inferred("2026-10-02", "by Friday")),
        ("decision", "decision", inferred("Drop the old parser", "the old parser")),
        ("decision", "rationale", guessed("Maintenance cost")),
        ("commitment", "completed", guessed("2026-09-22")),
        ("waiting-on", "received", inferred("2026-09-22", "send the automation deck")),
    ],
)
def test_a_protected_field_assumed_without_a_flag_fails_naming_the_field(
    capture: dict[str, Any],
    raw_dir: Path,
    staging_dir: Path,
    entity_type: str,
    field: str,
    spec: dict[str, Any],
) -> None:
    proposal = {"entity_type": entity_type, "fields": {field: spec}}
    with pytest.raises(StructuringError, match=field):
        _stage(capture, raw_dir, staging_dir, proposal)
    assert not staging_dir.exists()


def test_a_flagged_assumption_in_a_protected_field_is_staged_and_flagged(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("send the automation deck", "send the automation deck"),
            "due_date": inferred("2026-10-02", "by Friday", flag=True),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == "flagged"
    assert record["evidence"]["due_date"]["review_flag"] is True


def test_a_completion_status_is_protected_too(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {"entity_type": "task", "fields": {"status": guessed("complete")}}
    with pytest.raises(StructuringError, match="status"):
        _stage(capture, raw_dir, staging_dir, proposal)

    flagged = {"entity_type": "task", "fields": {"status": guessed("complete", flag=True)}}
    [record] = _stage(capture, raw_dir, staging_dir, flagged)
    assert record["route"] == "flagged"


def test_an_explicit_protected_field_needs_no_flag(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("send the automation deck", "send the automation deck"),
            "promised_to": explicit("jordan-rivera", "Told Jordan"),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == "clean"


def test_protected_names_come_from_the_evidence_schema() -> None:
    schema = json.loads((ROOT / "schemas" / "evidence.schema.json").read_text())
    names = set(schema["definitions"]["protected_field_names"]["enum"])
    assert structure.protected_fields() == names


# --- R9: an ambiguous capture completes non-interactively and is flagged ----------------


def test_an_ambiguous_inbox_capture_completes_without_prompting_and_is_flagged(
    tmp_path: Path, raw_dir: Path, staging_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_prompts(*_: Any, **__: Any) -> str:
        raise AssertionError("capture must never wait on owner input")

    monkeypatch.setattr(builtins, "input", no_prompts)
    monkeypatch.setattr(sys, "stdin", None)

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "call-notes.txt").write_text("Said I'd look into it for them next week.")
    [raw], failures = capture_raw.scan_inbox(inbox_dir=inbox, raw_dir=raw_dir)
    assert failures == []

    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("look into it", "look into it"),
            "promised_to": inferred("jordan-rivera", "for them", flag=True),
            "due_date": inferred("2026-09-29", "next week", flag=True),
        },
    }
    [record] = structure.stage_capture(
        raw["id"], [proposal], known=KNOWN, raw_dir=raw_dir, staging_dir=staging_dir
    )
    assert record["route"] == "flagged"
    assert [p.name for p in staging_dir.iterdir()] == [f"{record['id']}.json"]


# --- R10: an unknown person creates no person record anywhere ---------------------------


def _snapshot(*dirs: Path) -> dict[str, bytes]:
    return {
        str(p): p.read_bytes()
        for d in dirs
        if d.exists()
        for p in sorted(d.rglob("*"))
        if p.is_file()
    }


def test_a_capture_naming_an_unknown_person_creates_no_person_record(
    tmp_path: Path, raw_dir: Path, staging_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    people = root / "_data" / "people"
    people.mkdir(parents=True)
    person = {"id": "jordan-rivera", "name": "Jordan"}
    (people / "jordan-rivera.json").write_text(json.dumps(person))
    (root / "_data" / "tags.json").write_text("[]")
    monkeypatch.delenv("D_SYSTEM_DATA_ROOT", raising=False)
    known = KnownIdentities.load(root)
    assert known.people == {"jordan-rivera"}

    repo_data_before = _snapshot(ROOT / "_data")
    tmp_data_before = _snapshot(root / "_data")

    raw = capture_raw.write_raw_capture(
        "Promised Dana Okafor the budget sheet.", channel="cli", raw_dir=raw_dir
    )
    proposal = {
        "entity_type": "commitment",
        "fields": {
            "description": explicit("send the budget sheet", "the budget sheet"),
            "promised_to": explicit("Dana Okafor", "Dana Okafor"),
        },
    }
    [record] = structure.stage_capture(
        raw["id"], [proposal], known=known, raw_dir=raw_dir, staging_dir=staging_dir
    )

    assert record["route"] == "held"
    assert record["entity"]["promised_to"] == "Dana Okafor"
    assert _snapshot(root / "_data") == tmp_data_before
    assert _snapshot(ROOT / "_data") == repo_data_before
    staged = [json.loads(p.read_text()) for p in staging_dir.glob("*.json")]
    assert [r["entity_type"] for r in staged] == ["commitment"]
    assert list(raw_dir.glob("*.json")) == [raw_dir / f"{raw['id']}.json"]


# --- R4: the same text routes identically through every channel -------------------------


def test_the_same_fixture_through_all_three_channels_routes_identically(
    tmp_path: Path, raw_dir: Path, staging_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = capture_raw.write_raw_capture(CONTENT, channel="session", raw_dir=raw_dir)

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "note.txt").write_text(CONTENT, encoding="utf-8")
    [inbox_raw], _ = capture_raw.scan_inbox(inbox_dir=inbox, raw_dir=raw_dir)

    before = set(raw_dir.glob("*.json"))
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)
    assert capture_cli.main([CONTENT]) == 0
    [cli_path] = set(raw_dir.glob("*.json")) - before
    cli_raw = json.loads(cli_path.read_text(encoding="utf-8"))

    assert [r["channel"] for r in (session, inbox_raw, cli_raw)] == ["session", "inbox", "cli"]

    proposals = [
        {
            "entity_type": "commitment",
            "fields": {
                "description": explicit("send the automation deck", "send the automation deck"),
                "promised_to": inferred("jordan-rivera", "Told Jordan", flag=True),
                "due_date": explicit("2026-09-25", "by Friday"),
            },
        },
        {
            "entity_type": "decision",
            "fields": {
                "decision": explicit("Drop the old parser", "drop the old parser"),
                "rationale": explicit("Too slow", "too slow"),
            },
        },
        {"entity_type": "note", "fields": {"description": guessed("a workshop")}},
    ]

    def comparable(raw: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
        records = structure.stage_capture(
            raw["id"], proposals, known=KNOWN, raw_dir=raw_dir, staging_dir=staging_dir
        )
        out = []
        for record in records:
            evidence = json.loads(json.dumps(record["evidence"]))
            for field_evidence in evidence.values():
                assert field_evidence["provenance"].pop("capture_id") == raw["id"]
            out.append((record["entity_type"], record["route"], evidence))
        return out

    session_result = comparable(session)
    assert [route for _, route, _ in session_result] == ["flagged", "flagged", "flagged"]
    assert comparable(inbox_raw) == session_result
    assert comparable(cli_raw) == session_result


# --- Review findings: malformed references, truthy flags, atomic staging ---------------


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("participants", 5),
        ("participants", "dana"),
        ("tags", "ai-tools"),
        ("decided_by_names", [3]),
        ("promised_to", ["jordan-rivera"]),
        ("project_id", 7),
    ],
)
def test_a_reference_field_of_the_wrong_shape_is_refused_naming_it(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path, field: str, value: Any
) -> None:
    proposal = {"entity_type": "interaction", "fields": {field: explicit(value, "Jordan")}}
    with pytest.raises(StructuringError, match=field):
        _stage(capture, raw_dir, staging_dir, proposal)
    assert not staging_dir.exists()


@pytest.mark.parametrize("flag", ["true", 1, "yes"])
def test_a_truthy_non_boolean_review_flag_does_not_count_as_a_flag(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path, flag: Any
) -> None:
    spec = inferred("2026-10-02", "by Friday")
    spec["review_flag"] = flag
    proposal = {"entity_type": "commitment", "fields": {"due_date": spec}}
    with pytest.raises(StructuringError, match="due_date"):
        _stage(capture, raw_dir, staging_dir, proposal)
    assert not staging_dir.exists()


def test_a_high_stakes_record_with_an_unresolved_reference_is_held_not_flagged(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path
) -> None:
    proposal = {
        "entity_type": "decision",
        "fields": {
            "decision": explicit("Drop the old parser", "drop the old parser"),
            "decided_by_names": explicit(["Dana"], "Jordan"),
        },
    }
    [record] = _stage(capture, raw_dir, staging_dir, proposal)
    assert record["route"] == "held"


def test_an_id_collision_leaves_staging_untouched(
    capture: dict[str, Any], raw_dir: Path, staging_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(structure, "_new_id", lambda _at: "staged-20260922T000000Z-000000")
    proposals = [
        {"entity_type": "task", "fields": {"description": explicit("send deck", "send the")}},
        {"entity_type": "note", "fields": {"description": explicit("workshop", "a workshop")}},
    ]
    with pytest.raises(StructuringError, match="collision"):
        _stage(capture, raw_dir, staging_dir, *proposals)
    assert not staging_dir.exists()

    [record] = _stage(capture, raw_dir, staging_dir, proposals[0])
    with pytest.raises(StructuringError, match="collision"):
        _stage(capture, raw_dir, staging_dir, proposals[0], proposals[1])
    assert [p.name for p in staging_dir.iterdir()] == [f"{record['id']}.json"]
