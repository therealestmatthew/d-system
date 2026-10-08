"""Schema and invariant tests for the workbench layout data files
(`_data/workbench/layouts/*.json`, REQ-007 W16, ADR-016, ADR-031, idea `000098`).

`schemas/workbench-layout.schema.json` asserts structural shape via a Draft7 validator: a
malformed file (missing a required key, wrong type) fails here before it ships. A layout carries no
eligibility list (REQ-011 R12): which slots a panel may occupy is computed by the structural matcher
(`src/workbench/slot_matcher.py`) from `panel-elements.json` and `slot-schemas.json`, so a layout
that carries `eligible_slots` fails the schema. JSON Schema cannot express the relational
invariants the layout depends on — every slot id naming a role in the slot schemas, every panel
having at least one structurally eligible slot in this layout, the default assignment being
*total* (every declared panel assigned exactly once) and landing inside that eligibility, every
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

from src.workbench.slot_matcher import (
    eligible_slot_ids,
    load_panel_elements,
    load_slot_schemas,
    role_frame_has_identity,
)

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
    """Panel id -> the slots of this layout it is structurally eligible for (REQ-011 R12)."""
    slot_ids = [slot["slot_id"] for slot in layout["slots"]]
    return {
        panel["panel_id"]: set(eligible_slot_ids(panel["panel_id"], slot_ids))
        for panel in layout["panels"]
    }


def _assert_every_panel_has_a_real_eligible_slot(layout: dict[str, Any]) -> None:
    elements = load_panel_elements()
    for panel_id, eligible in _panel_eligibility(layout).items():
        assert panel_id in elements, f"{panel_id} has no entry in panel-elements.json"
        assert eligible, f"{panel_id} has no structurally eligible slot in {layout['layout_id']}"


def _assert_every_slot_names_a_role(layout: dict[str, Any]) -> None:
    roles = set(load_slot_schemas()["roles"])
    unknown = {slot["slot_id"] for slot in layout["slots"]} - roles
    assert not unknown, f"slot id(s) {sorted(unknown)} name no role in slot-schemas.json"


def _assert_identityless_roles_hold_one_panel(layout: dict[str, Any]) -> None:
    """A frame with no `identity` sub-slot has no panel switcher (ADR-031 decision 2), so a layout
    may not assign more than one panel to its role."""
    schemas = load_slot_schemas()
    counts: dict[str, int] = {}
    for slot_id in layout["default_assignment"].values():
        counts[slot_id] = counts.get(slot_id, 0) + 1
    for slot_id, count in counts.items():
        if not role_frame_has_identity(slot_id, schemas):
            assert count <= 1, f"{slot_id} has no panel switcher but is assigned {count} panels"


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
    """Version 3 renamed the slot ids to role names; version 4 removed `eligible_slots` (ADR-031
    decision 10). The version is part of the browser storage key, so dropping a bump would leave
    browsers reading selections written against a shape the files no longer have."""
    assert _load(path)["schema_version"] >= 4


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_slot_ids_never_equal_a_panel_id(path: Path) -> None:
    """REQ-007's slot naming rule (`brain/concepts/terms-workbench-ui.md`, REQ-011 R03): a slot id
    names the slot's role and may never equal a panel id. Every panel id in a layout file is a
    panel type name, so this also keeps a slot from being named for a panel type."""
    layout = _load(path)
    slot_ids = {slot["slot_id"] for slot in layout["slots"]}
    panel_ids = {panel["panel_id"] for panel in layout["panels"]}
    assert slot_ids & panel_ids == set(), (
        f"{path.name}: slot ids equal panel ids {sorted(slot_ids & panel_ids)}"
    )


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_every_panel_has_a_real_eligible_slot(path: Path) -> None:
    _assert_every_panel_has_a_real_eligible_slot(_load(path))


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_every_slot_names_a_role(path: Path) -> None:
    _assert_every_slot_names_a_role(_load(path))


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_shipped_layout_identityless_roles_hold_one_panel(path: Path) -> None:
    _assert_identityless_roles_hold_one_panel(_load(path))


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
    """The structural rule reproduces REQ-007 W16 as amended by ADR-031: Terminal (bash), CMD,
    PowerShell and HTML Viewer are each eligible for both the secondary and primary slots in both
    layouts; Overview, an embedded document like the HTML Viewer, is eligible for both as well
    where it exists (layout 1 never shipped an overview panel); the notes strip and the explorer
    slot's three panels keep their single-slot homes unchanged."""
    shared_shell_and_viewer_ids = {"terminal", "terminal-cmd", "terminal-powershell", "html-viewer"}
    for path in LAYOUT_FILES:
        layout = _load(path)
        eligibility = _panel_eligibility(layout)
        for panel_id in shared_shell_and_viewer_ids:
            assert eligibility[panel_id] == {"secondary", "primary"}, (
                f"{path.name}: {panel_id} must be eligible for exactly the secondary and primary "
                "slots"
            )
        if "overview" in eligibility:
            assert eligibility["overview"] == {"secondary", "primary"}, (
                f"{path.name}: overview must be eligible for the secondary and primary slots"
            )
        assert eligibility["notes-strip"] == {"strip"}
        for panel_id in ("file-browser", "idea-explorer", "backlog-explorer"):
            assert eligibility[panel_id] == {"explorer"}


def test_shipped_defaults_reproduce_the_pre_delta_arrangement() -> None:
    """Defaults reproduce the pre-delta arrangement: shells default to the secondary slot with
    bash visible, and HTML Viewer defaults to the primary slot (with Overview behind it in layout 2)
    — so a cleared browser looks unchanged (REQ-007 W16)."""
    for path in LAYOUT_FILES:
        layout = _load(path)
        assignment = layout["default_assignment"]
        for shell_id in ("terminal", "terminal-cmd", "terminal-powershell"):
            assert assignment[shell_id] == "secondary"
        assert assignment["html-viewer"] == "primary"
        assert layout["default_visible_panel"]["secondary"] == "terminal"
        # `primary` only needs an explicit default-visible entry when more than one panel is
        # assigned there by default (layout 2, where overview sits behind html-viewer); layout 1
        # assigns only html-viewer to primary, so no entry is required there.
        if "primary" in layout["default_visible_panel"]:
            assert layout["default_visible_panel"]["primary"] == "html-viewer"
        if "overview" in assignment:
            assert assignment["overview"] == "primary"


# --- deliberately malformed / invalid mutations fail before they ship ------------------------


def test_malformed_layout_file_fails_schema() -> None:
    malformed = {"schema_version": 2, "layout_id": "broken"}  # missing name/slots/panels/etc.
    errors = list(_validator().iter_errors(malformed))
    assert errors


@pytest.mark.parametrize("path", LAYOUT_FILES, ids=lambda p: p.stem)
def test_layout_carrying_an_eligibility_list_fails_the_schema(path: Path) -> None:
    """REQ-011 R12: there is no per-panel allow-list anywhere, so a layout that carries one is
    rejected rather than ignored (ADR-031 decision 4)."""
    layout = copy.deepcopy(_load(path))
    layout["panels"][0]["eligible_slots"] = ["primary"]
    errors = list(_validator().iter_errors(layout))
    assert errors
    assert any("eligible_slots" in error.message for error in errors)


def test_a_version_3_layout_fails_the_schema() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["schema_version"] = 3
    assert list(_validator().iter_errors(layout))


def test_panel_with_no_eligible_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    # Without a primary or secondary slot no terminal has a structurally eligible home.
    layout["slots"] = [s for s in layout["slots"] if s["slot_id"] in {"strip", "explorer"}]
    with pytest.raises(AssertionError):
        _assert_every_panel_has_a_real_eligible_slot(layout)


def test_slot_id_naming_no_role_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["slots"][0]["slot_id"] = "sidebar"
    with pytest.raises(AssertionError):
        _assert_every_slot_names_a_role(layout)


def test_two_panels_in_a_role_without_a_switcher_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["default_assignment"]["file-browser"] = "strip"
    layout["default_assignment"]["idea-explorer"] = "strip"
    with pytest.raises(AssertionError):
        _assert_identityless_roles_hold_one_panel(layout)


def test_default_assignment_to_an_ineligible_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    target_panel = layout["panels"][0]
    eligible = _panel_eligibility(layout)[target_panel["panel_id"]]
    ineligible_slot = next(
        slot["slot_id"] for slot in layout["slots"] if slot["slot_id"] not in eligible
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
    layout["default_visible_panel"]["secondary"] = "html-viewer"
    layout["default_assignment"]["html-viewer"] = "primary"
    with pytest.raises(AssertionError):
        _assert_default_visible_panel_is_actually_assigned(layout)


def test_grid_area_naming_an_unknown_slot_fails_invariant() -> None:
    layout = copy.deepcopy(_load(LAYOUT_FILES[0]))
    layout["grid"]["areas"][0] = layout["grid"]["areas"][0] + " nonexistent-slot"
    with pytest.raises(AssertionError):
        _assert_grid_areas_name_real_slots(layout)
