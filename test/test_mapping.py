"""Behavioral checks for the Mapper role's write path (src/governance/mapping.py)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

from src.governance.mapping import (
    apply_phase_locks,
    build_ordering,
    validate_ordering,
    write_locks_text,
)
from src.governance.mapping import (
    main as mapping_main,
)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "gate-decision.schema.json"

BACKLOG_TEXT = """\
updated: '2026-09-05'
decision_record: doc-governance
max_active: 3
next_up:
- phase-alpha
- phase-beta
items:
- id: phase-alpha
  title: Alpha
  depends_on: []
  systems:
  - sys-alpha
  status: queued
- id: phase-beta
  title: Beta
  depends_on:
  - phase-alpha
  systems:
  - sys-beta
  - sys-gamma
  status: queued
- id: phase-gamma
  title: Gamma
  depends_on: []
  systems:
  - sys-gamma
  status: queued
"""


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def write_backlog(tmp_path: Path, text: str = BACKLOG_TEXT) -> Path:
    root = tmp_path / "repo"
    backlog_dir = root / "docs" / "09-backlog"
    backlog_dir.mkdir(parents=True)
    (backlog_dir / "backlog.yaml").write_text(text, encoding="utf-8")
    schema_dir = root / "schemas"
    schema_dir.mkdir(parents=True)
    (schema_dir / "gate-decision.schema.json").write_text(
        SCHEMA_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return root


def read_backlog(root: Path) -> str:
    return (root / "docs" / "09-backlog" / "backlog.yaml").read_text(encoding="utf-8")


# --- write_locks_text: surgical, leaves next_up and untouched phases byte-identical ---


def test_write_locks_text_edits_only_named_phases_fields():
    rewritten = write_locks_text(
        BACKLOG_TEXT,
        {"phase-beta": {"depends_on": ["phase-gamma"], "systems": ["sys-beta"]}},
    )
    assert "- phase-gamma" in rewritten
    # Alpha and Gamma, and next_up, are byte-identical to the original.
    assert "next_up:\n- phase-alpha\n- phase-beta\n" in rewritten
    assert "- id: phase-alpha\n  title: Alpha\n  depends_on: []\n  systems:\n  - sys-alpha\n" in (
        rewritten
    )
    assert (
        "- id: phase-gamma\n  title: Gamma\n  depends_on: []\n  systems:\n  - sys-gamma\n"
        in rewritten
    )


def test_apply_phase_locks_leaves_next_up_byte_identical(tmp_path):
    root = write_backlog(tmp_path)
    original = read_backlog(root)
    code, _lines = apply_phase_locks(
        root,
        {"phase-gamma": {"depends_on": ["phase-alpha"], "systems": ["sys-gamma", "sys-delta"]}},
        validate=lambda _root: [],
    )
    assert code == 0
    rewritten = read_backlog(root)
    original_next_up = original.split("items:")[0]
    rewritten_next_up = rewritten.split("items:")[0]
    assert original_next_up == rewritten_next_up


def test_apply_phase_locks_refused_write_leaves_file_unchanged(tmp_path):
    root = write_backlog(tmp_path)
    original = read_backlog(root)
    code, lines = apply_phase_locks(
        root,
        {"phase-gamma": {"depends_on": ["phase-missing"], "systems": ["sys-gamma"]}},
        validate=lambda _root: ["phase-gamma: unresolved dependency phase-missing"],
    )
    assert code == 1
    assert any("rolled back" in line for line in lines)
    assert read_backlog(root) == original


def test_apply_phase_locks_clean_validator_commits_the_write(tmp_path):
    root = write_backlog(tmp_path)
    code, lines = apply_phase_locks(
        root,
        {"phase-gamma": {"depends_on": ["phase-alpha"], "systems": ["sys-gamma"]}},
        validate=lambda _root: [],
    )
    assert code == 0
    assert any("wrote depends_on/systems for phase-gamma" in line for line in lines)
    assert "- phase-alpha" in read_backlog(root).split("id: phase-gamma")[1]


# --- the module exposes no next_up write path ---


def test_module_exposes_no_next_up_write():
    """The module may discuss next_up in prose (it must never write it), so the check is
    structural: the only fields write_locks_text ever recognises as writable are
    depends_on/systems, and no line in the module constructs a "next_up:" block the way
    _block_lines constructs a depends_on/systems one.
    """
    import src.governance.mapping as mapping_module

    assert mapping_module._LOCKED_FIELDS == ("depends_on", "systems")
    source = Path(mapping_module.__file__).read_text(encoding="utf-8")
    assert '"next_up:' not in source
    assert "'next_up:" not in source


# --- the ordering artifact: schema-shaped, carries a reason per entry ---


def test_build_ordering_validates_against_the_def_and_carries_reasons():
    schema = load_schema()
    doc = build_ordering(
        [
            ("phase-alpha", "No dependencies; nothing blocks it."),
            ("phase-beta", "Depends on phase-alpha, which lands first."),
        ]
    )
    problems = validate_ordering(doc["ordering"], schema)
    assert problems == []
    assert all(entry["reason"] for entry in doc["ordering"])


def test_validate_ordering_rejects_an_entry_missing_a_reason():
    schema = load_schema()
    problems = validate_ordering([{"phase": "phase-alpha", "reason": ""}], schema)
    assert problems != []


def test_validate_ordering_rejects_an_entry_missing_the_phase_field():
    schema = load_schema()
    problems = validate_ordering([{"reason": "Some reason."}], schema)
    assert problems != []


# --- the gate-decision schema itself: optional ordering, backward compatible ---


def existing_decision_line() -> dict:
    return {
        "run_id": "run-1",
        "gate": "G3",
        "decision": "approve",
        "decision_seq": 1,
        "at": "2026-10-12T00:00:00Z",
        "decided_by": "repository-owner",
    }


def test_existing_decision_line_without_ordering_still_validates():
    schema = load_schema()
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(existing_decision_line())) == []


def test_decision_line_accepts_a_valid_ordering():
    schema = load_schema()
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    decision = existing_decision_line()
    decision["ordering"] = build_ordering([("phase-alpha", "Goes first.")])["ordering"]
    assert list(validator.iter_errors(decision)) == []


def test_decision_line_rejects_a_malformed_ordering():
    schema = load_schema()
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    decision = existing_decision_line()
    decision["ordering"] = [{"phase": "phase-alpha"}]  # missing required "reason"
    assert list(validator.iter_errors(decision)) != []


# --- CLI wiring: writes locks, emits ordering, never touches next_up ---


def test_cli_emits_ordering_to_out_path_after_a_clean_write(tmp_path, monkeypatch):
    import src.governance.mapping as mapping_module

    root = write_backlog(tmp_path)
    monkeypatch.setattr(mapping_module, "ROOT", root)
    monkeypatch.setattr(mapping_module, "governance_errors", lambda _root: [])

    assignments_path = tmp_path / "assignments.json"
    assignments_path.write_text(
        json.dumps({"phase-gamma": {"depends_on": ["phase-alpha"], "systems": ["sys-gamma"]}}),
        encoding="utf-8",
    )
    ordering_path = tmp_path / "ordering.json"
    ordering_path.write_text(
        json.dumps([{"phase": "phase-gamma", "reason": "Needs phase-alpha first."}]),
        encoding="utf-8",
    )
    out_path = tmp_path / "proposed-ordering.json"

    code = mapping_main(
        [
            "--assignments",
            str(assignments_path),
            "--ordering",
            str(ordering_path),
            "--out",
            str(out_path),
        ]
    )
    assert code == 0
    emitted = json.loads(out_path.read_text(encoding="utf-8"))
    assert emitted == {
        "ordering": [{"phase": "phase-gamma", "reason": "Needs phase-alpha first."}]
    }
    assert read_backlog(root).split("items:")[0] == BACKLOG_TEXT.split("items:")[0]
