"""Structural eligibility and the slot-schema data it reads (ADR-031, REQ-011 R12).

`src/workbench/slot_matcher.py` decides whether a panel type may occupy a slot role from two data
files: `_data/workbench/panel-elements.json` (what each panel type is: a body kind and an ordered
list of bar elements) and `_data/workbench/slot-schemas.json` (what each role offers: a frame with
panel-filled bar sub-slots and a body that admits some body kinds). The rule is written a second
time in TypeScript (`ts/src/workbench/slotMatcher.ts`) because the workbench runs it in the
browser; `_data/workbench/matcher-cases.json` is the hand-written expected answer both sides are
held to. This module is the Python side of that pair, and it also checks the two data files against
their JSON Schemas and against each other, which JSON Schema cannot express.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from src.workbench.slot_matcher import (
    bar_leaves,
    eligible_roles,
    is_eligible,
    load_panel_elements,
    load_slot_schemas,
    role_frame_has_identity,
    route_bar,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data" / "workbench"
SLOT_SCHEMA_SCHEMA = ROOT / "schemas" / "workbench-slot-schemas.schema.json"
PANEL_ELEMENTS_SCHEMA = ROOT / "schemas" / "workbench-panel-elements.schema.json"
CASES_PATH = DATA / "matcher-cases.json"
REGISTRY_PATH = ROOT / "ts" / "src" / "workbench" / "panelRegistry.tsx"
TS_SRC = ROOT / "ts" / "src"
PY_SRC = ROOT / "src"


def _validator(path: Path) -> Draft7Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


SCHEMAS = load_slot_schemas()
ELEMENTS = load_panel_elements()
CASES: dict[str, Any] = json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _elements_for(panel: str) -> dict[str, Any]:
    if panel in CASES["synthetic_panels"]:
        synthetic: dict[str, Any] = CASES["synthetic_panels"][panel]
        return synthetic
    return ELEMENTS[panel]


# --- the data files against their JSON Schemas -------------------------------------------------


def test_slot_schemas_match_their_json_schema() -> None:
    errors = list(_validator(SLOT_SCHEMA_SCHEMA).iter_errors(SCHEMAS))
    assert errors == [], [error.message for error in errors]


def test_panel_elements_match_their_json_schema() -> None:
    data = json.loads((DATA / "panel-elements.json").read_text(encoding="utf-8"))
    errors = list(_validator(PANEL_ELEMENTS_SCHEMA).iter_errors(data))
    assert errors == [], [error.message for error in errors]


def test_a_malformed_slot_schema_fails_its_json_schema() -> None:
    broken = copy.deepcopy(SCHEMAS)
    broken["frames"]["standard"]["children"][0]["children"][1]["capacity"] = 0
    assert list(_validator(SLOT_SCHEMA_SCHEMA).iter_errors(broken))


def test_a_group_nested_inside_a_group_fails_the_depth_two_bound() -> None:
    """ADR-031 decision 3: a slot is a tree of depth two (frame, group, leaf)."""
    broken = copy.deepcopy(SCHEMAS)
    group = broken["frames"]["standard"]["children"][0]
    group["children"].append({"id": "inner", "children": [{"id": "x", "filled_by": "slot"}]})
    assert list(_validator(SLOT_SCHEMA_SCHEMA).iter_errors(broken))


# --- the two data files against each other -----------------------------------------------------


def _leaves(frame: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for node in frame["children"]:
        found.extend(node["children"] if "children" in node else [node])
    return found


def test_every_role_names_a_real_frame_and_real_body_kinds() -> None:
    body_kinds = set(SCHEMAS["element_types"]["body"])
    for role, role_schema in SCHEMAS["roles"].items():
        assert role_schema["frame"] in SCHEMAS["frames"], f"{role} names no frame"
        assert set(role_schema["body"]) <= body_kinds, f"{role} admits an undeclared body kind"


def test_every_frame_has_exactly_one_body_leaf_and_admits_only_declared_bar_types() -> None:
    bar_types = set(SCHEMAS["element_types"]["bar"])
    for name, frame in SCHEMAS["frames"].items():
        leaves = _leaves(frame)
        ids = [leaf["id"] for leaf in leaves]
        assert len(ids) == len(set(ids)), f"frame {name} repeats a sub-slot id"
        assert sum(1 for leaf in leaves if leaf.get("holds") == "body") == 1, name
        for leaf in leaves:
            assert set(leaf.get("admits", [])) <= bar_types, f"{name}/{leaf['id']}"
        assert sum(1 for node in frame["children"] if "children" in node) <= 1, (
            f"frame {name} has more than one group"
        )


def test_every_panel_element_configuration_uses_declared_vocabulary() -> None:
    bar_types = set(SCHEMAS["element_types"]["bar"])
    body_kinds = set(SCHEMAS["element_types"]["body"])
    for panel, elements in ELEMENTS.items():
        assert elements["body"] in body_kinds, f"{panel} has body kind {elements['body']!r}"
        assert set(elements["bar"]) <= bar_types, f"{panel} supplies an undeclared bar element"


def _registry_entries() -> dict[str, str]:
    """Panel type -> the key its `elements:` field reads, from the PANEL_REGISTRY literal."""
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    start = text.index("export const PANEL_REGISTRY")
    block = text[start:]
    entries: dict[str, str] = {}
    for match in re.finditer(
        r"^  (?:'([^']+)'|([A-Za-z_]\w*)): \{[^}]*?\belements: panelElements\['([^']+)'\]",
        block,
        flags=re.MULTILINE,
    ):
        entries[match.group(1) or match.group(2)] = match.group(3)
    return entries


def test_every_registry_entry_refers_to_its_own_panel_elements_entry() -> None:
    entries = _registry_entries()
    assert entries, "no registry entry refers to panel-elements.json"
    assert {key: ref for key, ref in entries.items() if key != ref} == {}
    assert set(entries) == set(ELEMENTS), "PANEL_REGISTRY and panel-elements.json disagree"


# --- the rule ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "case",
    CASES["cases"],
    ids=lambda c: f"{c['panel']}-in-{c['role']}",
)
def test_python_matcher_agrees_with_the_shared_cases(case: dict[str, Any]) -> None:
    got = is_eligible(_elements_for(case["panel"]), case["role"], SCHEMAS)
    assert got is case["eligible"]


def test_cases_cover_every_shipped_panel_type_in_every_role() -> None:
    covered = {(c["panel"], c["role"]) for c in CASES["cases"]}
    wanted = {(panel, role) for panel in ELEMENTS for role in SCHEMAS["roles"]}
    assert wanted <= covered, sorted(wanted - covered)


def test_bar_capacity_refuses_a_panel_with_more_controls_than_the_strip_has_room_for() -> None:
    """ADR-031 decision 4: the one negative bar-capacity case. The body kind fits (`ticker`) and
    the only reason the panel is refused is that its bar has two controls and the compact frame
    has room for one."""
    too_many = {"body": "ticker", "bar": ["help", "choice", "choice"]}
    fits = {"body": "ticker", "bar": ["help", "choice"]}
    assert not is_eligible(too_many, "strip", SCHEMAS)
    assert is_eligible(fits, "strip", SCHEMAS)
    # The same bar is fine where there is room, so the refusal is capacity and not the elements.
    assert is_eligible({"body": "table", "bar": ["help", "choice", "choice"]}, "explorer", SCHEMAS)


def test_only_the_inputs_of_the_rule_decide() -> None:
    """The panel type id, the slot id and the layout are not inputs (ADR-031 decision 4)."""
    elements = ELEMENTS["html-viewer"]
    renamed = copy.deepcopy(SCHEMAS)
    renamed["roles"]["main-area"] = renamed["roles"].pop("primary")
    assert is_eligible(elements, "main-area", renamed) == is_eligible(elements, "primary", SCHEMAS)
    assert is_eligible(elements, "no-such-role", SCHEMAS) is False


def test_routing_takes_sub_slots_in_declaration_order_and_respects_capacity() -> None:
    leaves = bar_leaves(SCHEMAS["frames"]["standard"])
    assert [leaf["id"] for leaf in leaves] == ["help", "controls"]
    assert route_bar(["help", "choice", "toggle"], leaves) == ["help", "controls", "controls"]
    assert route_bar(["help", "help"], leaves) is None
    assert route_bar(["choice"] * 5, leaves) == ["controls"] * 5
    assert route_bar(["choice"] * 6, leaves) is None


def test_overlapping_admits_spill_to_the_next_sub_slot_when_the_first_is_full() -> None:
    leaves = [
        {"id": "a", "admits": ["choice"], "capacity": 1},
        {"id": "b", "admits": ["choice", "action"], "capacity": 2},
    ]
    assert route_bar(["choice", "choice", "action"], leaves) == ["a", "b", "b"]
    assert route_bar(["choice", "choice", "choice", "action"], leaves) is None


def test_shipped_eligibility_by_role() -> None:
    by_panel = {panel: eligible_roles(elements, SCHEMAS) for panel, elements in ELEMENTS.items()}
    assert by_panel == {
        "terminal": ["primary", "secondary"],
        "terminal-cmd": ["primary", "secondary"],
        "terminal-powershell": ["primary", "secondary"],
        "notes-strip": ["strip"],
        "overview": ["primary", "secondary"],
        "html-viewer": ["primary", "secondary"],
        "file-browser": ["explorer"],
        "idea-explorer": ["explorer"],
        "backlog-explorer": ["explorer"],
    }


def test_the_strip_role_has_no_switcher_and_the_others_do() -> None:
    assert role_frame_has_identity("strip", SCHEMAS) is False
    for role in ("primary", "secondary", "explorer"):
        assert role_frame_has_identity(role, SCHEMAS) is True


# --- there is no allow-list anywhere (REQ-011 R12) ---------------------------------------------


def test_no_source_or_data_file_carries_a_per_panel_or_per_slot_allow_list() -> None:
    offenders: list[str] = []
    for path in sorted(TS_SRC.rglob("*.ts*")):
        if ".test." in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"eligible_slots|eligibleSlots|admits_panels|allowed_panels", text):
            offenders.append(path.relative_to(ROOT).as_posix())
    for path in sorted(PY_SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"eligible_slots|admits_panels|allowed_panels", text):
            offenders.append(path.relative_to(ROOT).as_posix())
    for path in sorted(DATA.rglob("*.json")):
        text = path.read_text(encoding="utf-8")
        if re.search(r'"(eligible_slots|admits_panels|allowed_panels)"', text):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == [], f"an eligibility list is back: {offenders}"


# --- the dev server's allow-list holds no symlink (ts/vite.config.ts server.fs.allow) ----------


def test_no_tracked_symlink_under_the_dev_server_allow_list() -> None:
    """`ts/vite.config.ts` lets the dev server serve `ts/` and `_data/workbench/`. Vite checks that
    list by path prefix without resolving symlinks, so a committed symlink under either directory
    that points elsewhere (at `_private/`, say) would be served. The config's own guard refuses such
    a request at run time; this check refuses the symlink before it is merged."""
    listing = subprocess.run(
        ["git", "ls-files", "-s", "-z", "--", "ts", "_data/workbench"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    entries = [entry for entry in listing.split(b"\0") if entry]
    assert entries, "git listed no files under ts/ or _data/workbench/"
    symlinks = [
        entry.split(b"\t", 1)[1].decode() for entry in entries if entry.startswith(b"120000 ")
    ]
    assert symlinks == [], f"tracked symlinks under the dev server's allow-list: {symlinks}"


# --- a panel never draws a top bar (ADR-031 decision 1, REQ-011 R13) ----------------------------


def test_no_panel_source_draws_a_top_bar() -> None:
    """The cheap second check beside the rendered count in `oneHeaderPerSlot.test.tsx` (which counts
    `header` and `role="banner"` elements per slot and is the real guarantee): the panel sources
    contain no header element, no banner role and no `.stage-region__header` class. A panel
    supplies bar elements through `BarElement` and the slot draws the one bar."""
    panel_sources = sorted((TS_SRC / "stage").glob("*Region.tsx")) + sorted(
        (TS_SRC / "stage" / "explorer").glob("*Region.tsx")
    )
    assert len(panel_sources) >= 8, "the panel sources were not found"
    bar = re.compile(r"<header\b|role=\"banner\"|stage-region__header(?![\w-])")
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in panel_sources
        if bar.search(path.read_text("utf-8"))
    ]
    assert offenders == [], f"panel sources that draw a top bar: {offenders}"
