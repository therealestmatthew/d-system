"""Structural eligibility: may a panel type occupy a slot role? (ADR-031 decision 4, REQ-011 R12).

The authority is data: `_data/workbench/panel-elements.json` (each panel type's element
configuration) and `_data/workbench/slot-schemas.json` (each role's frame). Nothing here lists
which panels a slot admits. A panel type is eligible for a role when, and only when:

1. the role's body admits the panel's body kind; and
2. every element in the panel's `bar` list can be routed to a panel-filled bar sub-slot of the
   role's frame that admits its type, taking sub-slots in declaration order and respecting each
   sub-slot's capacity; and
3. every required sub-slot is satisfied (the body is required, and the panel always supplies it).

The panel type's id, the slot id and the layout are not inputs.

This is one half of a documented pair. The other half is `ts/src/workbench/slotMatcher.ts`, which
the workbench runs in the browser. The two are written separately on purpose (ADR-031 decision 4);
`test/test_workbench_slot_matcher.py` and `ts/src/workbench/slotMatcher.test.tsx` both read
`_data/workbench/matcher-cases.json` and fail if either side disagrees with it. Change the rule in
both files together.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "_data" / "workbench"
SLOT_SCHEMAS_PATH = DATA_DIR / "slot-schemas.json"
PANEL_ELEMENTS_PATH = DATA_DIR / "panel-elements.json"

Json = dict[str, Any]


def load_slot_schemas(path: Path = SLOT_SCHEMAS_PATH) -> Json:
    data: Json = json.loads(path.read_text(encoding="utf-8"))
    return data


def load_panel_elements(path: Path = PANEL_ELEMENTS_PATH) -> dict[str, Json]:
    """Panel type -> its element configuration (`body` kind and ordered `bar` element types)."""
    data: Json = json.loads(path.read_text(encoding="utf-8"))
    panels: dict[str, Json] = data["panels"]
    return panels


def bar_leaves(frame: Json) -> list[Json]:
    """The panel-filled bar sub-slots of a frame, in declaration order (depth two: frame, group,
    leaf, so the leaves are the children of the group that has any)."""
    leaves: list[Json] = []
    for node in frame["children"]:
        for leaf in node.get("children", []):
            if leaf.get("filled_by") == "panel" and leaf.get("holds") == "bar":
                leaves.append(leaf)
    return leaves


def route_bar(bar: list[str], leaves: list[Json]) -> list[str] | None:
    """The sub-slot id each bar element lands in, or None when some element has no place.

    Elements are taken in order; each goes to the first sub-slot that admits its type and still
    has room."""
    used = {leaf["id"]: 0 for leaf in leaves}
    routes: list[str] = []
    for element_type in bar:
        for leaf in leaves:
            if element_type in leaf["admits"] and used[leaf["id"]] < leaf["capacity"]:
                used[leaf["id"]] += 1
                routes.append(leaf["id"])
                break
        else:
            return None
    return routes


def is_eligible(elements: Json, role: str, schemas: Json) -> bool:
    """True when a panel with this element configuration may occupy `role`."""
    role_schema = schemas["roles"].get(role)
    if role_schema is None:
        return False
    if elements["body"] not in role_schema["body"]:
        return False
    frame = schemas["frames"][role_schema["frame"]]
    return route_bar(list(elements["bar"]), bar_leaves(frame)) is not None


def eligible_roles(elements: Json, schemas: Json) -> list[str]:
    """Every role in the schema file that `elements` may occupy, in the file's role order."""
    return [role for role in schemas["roles"] if is_eligible(elements, role, schemas)]


def eligible_slot_ids(
    panel_type: str,
    slot_ids: list[str],
    schemas: Json | None = None,
    panel_elements: dict[str, Json] | None = None,
) -> list[str]:
    """The slot ids (each one a role) from `slot_ids` that `panel_type` may occupy."""
    schemas = schemas if schemas is not None else load_slot_schemas()
    panel_elements = panel_elements if panel_elements is not None else load_panel_elements()
    elements = panel_elements.get(panel_type)
    if elements is None:
        return []
    return [slot_id for slot_id in slot_ids if is_eligible(elements, slot_id, schemas)]


def role_frame_has_identity(role: str, schemas: Json) -> bool:
    """True when the role's frame has an `identity` sub-slot, which is what carries the panel
    switcher. A role without one can hold one instance."""
    role_schema = schemas["roles"][role]
    frame = schemas["frames"][role_schema["frame"]]
    return any(
        leaf.get("id") == "identity"
        for node in frame["children"]
        for leaf in node.get("children", [])
    )
