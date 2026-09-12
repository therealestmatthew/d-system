"""Schema and invariant tests for the workbench layout data files
(`_data/workbench/layouts/*.json`, REQ-007 W16, ADR-016, idea `000098`).

`schemas/workbench-layout.schema.json` asserts structural shape via a Draft7 validator: a
malformed file (missing a required key, wrong type) fails here before it ships. JSON Schema
cannot express the relational invariants the W16 delta actually depends on — every panel's
`eligible_slots` naming real slots, the default assignment being *total* (every declared panel
assigned exactly once) and landing inside that panel's own eligibility, every
`default_visible_panel` entry naming a panel actually assigned to that slot, and every
`grid.areas` token naming a real slot — so those are asserted directly against the parsed JSON,
against both the two shipped layouts and deliberately-broken mutations of them.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "workbench-layout.schema.json"
LAYOUTS_DIR = ROOT / "_data" / "workbench" / "layouts"
LAYOUT_FILES = sorted(LAYOUTS_DIR.glob("*.json"))


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator() -> Draft7Validator:
    schema = _schema()
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _panel_eligibility(layout: dict[str, Any]) -> dict[str, set[str]]:
    return {panel["panel_id"]: set(panel["eligible_slots"]) for panel in layout["panels"]}


def _assert_every_panel_has_a_real_eligible_slot(layout: dict[str, Any]) -> None:
    slot_ids = {slot["slot_id"] for slot in layout["slots"]}
    for panel in layout["panels"]:
        assert panel["eligible_slots"], f"{panel['panel_id']} has no eligible slot"
        unknown = set(panel["eligible_slots"]) - slot_ids
        assert not unknown, f"{panel['panel_id']} names unknown slot(s) {unknown}"


def _assert_default_assignment_is_total_and_eligible(layout: dict[str, Any]) -> None:
    eligibility = _panel_eligibility(layout)
    assignment = layout["default_assignment"]
    assert set(assignment) == set(eligibility), (
        "default_assignment must cover every declared panel exactly once, no more, no less"
    )
    for panel_id, slot_id in assignment.items():
        assert slot_id in eligibility[panel_id], (
            f"{panel_id} defaults to slot {slot_id!r}, not one of its eligible slots "
            f"{eligibility[panel_id]}"
        )


def _assert_default_visible_panel_is_actually_assigned(layout: dict[str, Any]) -> None:
    assignment = layout["default_assignment"]
    slot_ids = {slot["slot_id"] for slot in layout["slots"]}
    for slot_id, panel_id in layout["default_visible_panel"].items():
        assert slot_id in slot_ids, f"default_visible_panel names unknown slot {slot_id!r}"
        assert assignment.get(panel_id) == slot_id, (
            f"default_visible_panel says {panel_id!r} is visible in {slot_id!r}, but "
            f"default_assignment assigns it to {assignment.get(panel_id)!r}"
        )


def _assert_grid_areas_name_real_slots(layout: dict[str, Any]) -> None:
    slot_ids = {slot["slot_id"] for slot in layout["slots"]}
    tokens = {
        token for row in layout["grid"]["areas"] for token in row.split() if token != "."
    }
    unknown = tokens - slot_ids
    assert not unknown, f"grid.areas names unknown slot(s) {unknown}"


# --- the two shipped layout files ------------------------------------------------------------


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_matches_schema(path: Path) -> None:
    errors = list(_validator().iter_errors(_load(path)))
    assert errors == [], [error.message for error in errors]


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_schema_version_is_bumped(path: Path) -> None:
    assert _load(path)["schema_version"] >= 2


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_every_panel_has_a_real_eligible_slot(path: Path) -> None:
    _assert_every_panel_has_a_real_eligible_slot(_load(path))


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_default_assignment_is_total_and_eligible(path: Path) -> None:
    _assert_default_assignment_is_total_and_eligible(_load(path))


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_default_visible_panel_is_actually_assigned(path: Path) -> None:
    _assert_default_visible_panel_is_actually_assigned(_load(path))


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_grid_areas_name_real_slots(path: Path) -> None:
    _assert_grid_areas_name_real_slots(_load(path))


def test_shipped_eligibility_matches_req_007_w16() -> None:
    """Terminal (bash), CMD, PowerShell and HTML Viewer are each eligible for both the terminal
    and main slots in both layouts; Overview is eligible for the main slot only, where it exists
    (layout 1 never shipped an overview panel and W16 does not add one); the notes strip and the
    explorer slot's three panels keep their single-slot homes unchanged."""
    shared_shell_and_viewer_ids = {"terminal", "terminal-cmd", "terminal-powershell", "html-viewer"}
    for path in LAYOUT_FILES:
        layout = _load(path)
        eligibility = _panel_eligibility(layout)
        for panel_id in shared_shell_and_viewer_ids:
            assert eligibility[panel_id] == {"terminal", "main"}, (
                f"{path.name}: {panel_id} must be eligible for exactly the terminal and main slots"
            )
        if "overview" in eligibility:
            assert eligibility["overview"] == {"main"}, (
                f"{path.name}: overview must be eligible for the main slot only"
            )
        assert eligibility["notes-strip"] == {"notes-strip"}
        for panel_id in ("file-browser", "idea-explorer", "backlog-explorer"):
            assert eligibility[panel_id] == {"explorer"}


def test_shipped_defaults_reproduce_the_pre_delta_arrangement() -> None:
    """Defaults reproduce the pre-delta arrangement: shells default to the terminal slot with
    bash visible, and HTML Viewer defaults to the main slot (with Overview behind it in layout 2)
    — so a cleared browser looks unchanged (REQ-007 W16)."""
    for path in LAYOUT_FILES:
        layout = _load(path)
        assignment = layout["default_assignment"]
        for shell_id in ("terminal", "terminal-cmd", "terminal-powershell"):
            assert assignment[shell_id] == "terminal"
        assert assignment["html-viewer"] == "main"
        assert layout["default_visible_panel"]["terminal"] == "terminal"
        # `main` only needs an explicit default-visible entry when more than one panel is
        # assigned there by default (layout 2, where overview sits behind html-viewer); layout 1
        # assigns only html-viewer to main, so no entry is required there.
        if "main" in layout["default_visible_panel"]:
            assert layout["default_visible_panel"]["main"] == "html-viewer"
        if "overview" in assignment:
            assert assignment["overview"] == "main"


# --- deliberately malformed / invalid mutations fail before they ship ------------------------


def test_malformed_layout_file_fails_schema() -> None:
    malformed = {"schema_version": 2, "layout_id": "broken"}  # missing name/slots/panels/etc.
    errors = list(_validator().iter_errors(malformed))
    assert errors


def test_panel_with_no_eligible_slot_fails_schema() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["panels"][0]["eligible_slots"] = []
    errors = list(_validator().iter_errors(layout))
    assert errors


def test_panel_with_no_eligible_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["panels"][0]["eligible_slots"] = []
    with pytest.raises(AssertionError):
        _assert_every_panel_has_a_real_eligible_slot(layout)


def test_default_assignment_to_an_ineligible_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    target_panel = layout["panels"][0]
    ineligible_slot = next(
        slot["slot_id"]
        for slot in layout["slots"]
        if slot["slot_id"] not in target_panel["eligible_slots"]
    )
    layout["default_assignment"][target_panel["panel_id"]] = ineligible_slot
    with pytest.raises(AssertionError):
        _assert_default_assignment_is_total_and_eligible(layout)


def test_default_assignment_missing_a_panel_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    del layout["default_assignment"][layout["panels"][0]["panel_id"]]
    with pytest.raises(AssertionError):
        _assert_default_assignment_is_total_and_eligible(layout)


def test_default_visible_panel_naming_an_unassigned_panel_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["default_visible_panel"]["terminal"] = "html-viewer"
    layout["default_assignment"]["html-viewer"] = "main"
    with pytest.raises(AssertionError):
        _assert_default_visible_panel_is_actually_assigned(layout)


def test_grid_area_naming_an_unknown_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["grid"]["areas"][0] = layout["grid"]["areas"][0] + " nonexistent-slot"
    with pytest.raises(AssertionError):
        _assert_grid_areas_name_real_slots(layout)
