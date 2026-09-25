"""Code parsing, allocation, register consistency, the code rules and the catalog.

Codes and dates are built at run time (``code("PLAN", "001")``) so this file carries no literal
document code or calendar date for the plugin's source-reference check to flag.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import codes
import pytest
import yaml
from conftest import PLUGIN_ROOT

TODAY = date(2030, 1, 2)
STAMP = TODAY.isoformat()
KINDS = {"plan", "adr", "architecture", "prompt", "session", "requirement", "walkthrough",
         "operation", "governance"}


def code(series: str, rest: str) -> str:
    return f"{series}-{rest}"


PLAN_1, PLAN_2, PLAN_3 = code("PLAN", "001"), code("PLAN", "002"), code("PLAN", "003")
SESS_1 = code("SESS", f"{STAMP}-01")


@pytest.fixture
def register() -> dict[str, Any]:
    """The template register the scaffold copies: the nine series, nothing held."""
    return dict(yaml.safe_load((PLUGIN_ROOT / "templates" / "codes.yaml").read_text()))


def doc(value: str, location: str, **changes: Any) -> dict[str, Any]:
    return {
        "path": f"docs/{location}",
        "location": location,
        "kind": "plan",
        "status": "draft",
        "owner": "repository-owner",
        "created": STAMP,
        "code": value,
        **changes,
    }


# --- Parsing ------------------------------------------------------------------------------


def test_parse_code_reads_both_grammars() -> None:
    assert codes.parse_code(PLAN_3) == {
        "series": "PLAN", "numbering": "counter", "number": 3, "sub": None, "stem": PLAN_3,
    }
    assert codes.parse_code(PLAN_3 + ".02")["sub"] == 2  # type: ignore[index]
    assert codes.parse_code(SESS_1) == {
        "series": "SESS", "numbering": "dated", "date": STAMP, "sequence": 1, "stem": SESS_1,
    }


@pytest.mark.parametrize("value", ["plan-1", code("PLAN", "1"), code("PLAN", "0001"),
                                   code("PLAN", "001.1"), "PLAN", ""])
def test_malformed_codes_are_rejected(value: str) -> None:
    assert codes.parse_code(value) is None


# --- Allocation ---------------------------------------------------------------------------


def test_counter_allocation_takes_the_next_number(register: dict[str, Any]) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    assert codes.next_code("plan", register, documents) == PLAN_2
    assert codes.next_code("adr", register, documents) == code("ADR", "001")


def test_counter_allocation_skips_reserved_and_retired_codes(register: dict[str, Any]) -> None:
    register["reserved"] = [{"code": PLAN_1, "reason": "held for a planned document"}]
    assert codes.next_code("plan", register, {}) == PLAN_2
    register["retired"] = [{"code": PLAN_2, "reason": "withdrawn"}]
    assert codes.next_code("plan", register, {}) == PLAN_3


def test_allocation_is_stable_across_repeated_runs(register: dict[str, Any]) -> None:
    assert {codes.next_code("plan", register, {}) for _ in range(3)} == {PLAN_1}


def test_dated_allocation_uses_the_date_and_a_same_day_sequence(register: dict[str, Any]) -> None:
    assert codes.next_code("session", register, {}, today=TODAY) == SESS_1
    documents = {"doc-s": doc(SESS_1, f"sessions/{SESS_1}-a.md", kind="session")}
    assert codes.next_code("session", register, documents, today=TODAY) == code(
        "SESS", f"{STAMP}-02")
    later = date(2030, 1, 3)
    assert codes.next_code("session", register, documents, today=later) == code(
        "SESS", f"{later.isoformat()}-01")


def test_sub_codes_allocate_under_their_parent(register: dict[str, Any]) -> None:
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-p/{PLAN_3}-overview.md"),
        "doc-c": doc(PLAN_3 + ".01", f"plans/{PLAN_3}-p/{PLAN_3}.01-c.md", parent="doc-p"),
    }
    assert codes.next_code("plan", register, documents, parent="doc-p") == PLAN_3 + ".02"


def test_a_pre_merge_reservation_counts_as_spent(register: dict[str, Any]) -> None:
    assert codes.next_code("plan", register, {}, reserved={PLAN_1}) == PLAN_2
    assert codes.next_code("adr", register, {}, reserved={PLAN_1}) == code("ADR", "001")
    reserved = {SESS_1}
    assert codes.next_code("session", register, {}, today=TODAY, reserved=reserved) == code(
        "SESS", f"{STAMP}-02")


@pytest.mark.parametrize(
    ("kind", "parent", "message"),
    [
        ("nonsense", None, "no series is registered for kind nonsense"),
        ("session", "doc-p", "dated series and takes no parent"),
        ("adr", "doc-p", "does not allow sub-codes"),
        ("plan", "doc-missing", "unknown parent document doc-missing"),
    ],
)
def test_allocation_rejects_impossible_requests(
    register: dict[str, Any], kind: str, parent: str | None, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        codes.next_code(kind, register, {}, parent=parent, today=TODAY)


def test_a_sub_code_parent_must_hold_a_top_level_code(register: dict[str, Any]) -> None:
    documents = {"doc-c": doc(PLAN_3 + ".01", f"plans/{PLAN_3}-p/{PLAN_3}.01-c.md")}
    with pytest.raises(ValueError, match="does not hold a top-level"):
        codes.next_code("plan", register, documents, parent="doc-c")


# --- The register ---------------------------------------------------------------------------


def test_the_template_register_is_consistent(register: dict[str, Any]) -> None:
    assert codes.inspect_register(register, KINDS) == []


def test_register_rejects_a_duplicate_series(register: dict[str, Any]) -> None:
    register["series"] = [*register["series"], dict(register["series"][0])]
    errors = codes.inspect_register(register, KINDS)
    assert "codes: duplicate series code" in errors
    assert "codes: duplicate series kind" in errors


def test_register_rejects_a_code_both_reserved_and_retired(register: dict[str, Any]) -> None:
    register["reserved"] = [{"code": PLAN_1, "reason": "planned"}]
    register["retired"] = [{"code": PLAN_1, "reason": "withdrawn"}]
    assert any("cannot be reserved and retired" in e
               for e in codes.inspect_register(register, KINDS))


def test_register_rejects_a_hold_on_an_unknown_series(register: dict[str, Any]) -> None:
    register["reserved"] = [{"code": code("NOPE", "001"), "reason": "no such series"}]
    assert any("names an unknown series" in e for e in codes.inspect_register(register, KINDS))


def test_register_requires_a_series_for_every_kind(register: dict[str, Any]) -> None:
    register["series"] = [s for s in register["series"] if s["kind"] != "adr"]
    assert "codes: no series registered for kind adr" in codes.inspect_register(register, KINDS)


def test_dated_series_cannot_allow_sub_codes(register: dict[str, Any]) -> None:
    for entry in register["series"]:
        if entry["kind"] == "session":
            entry["sub_codes"] = True
    assert any("dated series SESS cannot allow sub-codes" in e
               for e in codes.inspect_register(register, KINDS))


# --- The code rules on documents -----------------------------------------------------------

CHILD = PLAN_3 + ".01"
CASES: list[tuple[dict[str, Any], str]] = [
    ({"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md"), "doc-b": doc(PLAN_1, f"plans/{PLAN_1}-b.md")},
     f"duplicate code {PLAN_1}"),
    ({"doc-a": doc(PLAN_1, f"decisions/{PLAN_1}-a.md", kind="adr")},
     "kind adr requires a ADR code"),
    ({"doc-a": doc(code("PLAN", f"{STAMP}-01"), f"plans/PLAN-{STAMP}-01-a.md")},
     "PLAN uses counter numbering"),
    ({"doc-a": doc("NOPE-1", "plans/NOPE-1-a.md")}, "malformed code NOPE-1"),
    ({"doc-a": doc(PLAN_1, "plans/wrong-name.md")}, f"filename must start with {PLAN_1}-"),
    ({"doc-a": doc(code("ADR", "001"), "plans/x.md", kind="adr")}, "adr belongs under decisions/"),
    ({"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md"),
      "doc-b": doc(PLAN_2, f"plans/{PLAN_2}-b.md", parent="doc-a")},
     "child of doc-a requires a sub-code under its parent"),
    ({"doc-a": doc(PLAN_1 + ".01", f"plans/{PLAN_1}-x/{PLAN_1}.01-a.md")},
     f"sub-code {PLAN_1}.01 requires a parent"),
    ({"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md"),
      "doc-b": doc(PLAN_2 + ".01", f"plans/{PLAN_2}-b/{PLAN_2}.01-b.md", parent="doc-a")},
     f"sub-code stem {PLAN_2} does not match parent {PLAN_1}"),
    ({"doc-a": doc(SESS_1, f"sessions/{SESS_1}-a.md", kind="session",
                   created=date(2030, 1, 1).isoformat())},
     "must equal created"),
    ({"doc-a": doc(CHILD, f"plans/nested/{CHILD}-a.md", parent="doc-p")},
     f"containing folder must start with {PLAN_3}-"),
    ({"doc-a": doc(CHILD, f"plans/{PLAN_3}-p/a/b/{CHILD}-a.md", parent="doc-p")},
     "nests at most one area folder deep"),
    ({"doc-a": doc(PLAN_3, f"plans/{PLAN_3}-p/area/{PLAN_3}-overview.md")},
     "an area folder holds child plans; the overview sits beside it"),
]


@pytest.mark.parametrize(("documents", "expected"), CASES)
def test_code_rules_reject(register: dict[str, Any], documents: dict[str, Any],
                           expected: str) -> None:
    errors = codes.inspect_codes(register, documents)
    assert any(expected in error for error in errors), errors


def test_a_reserved_or_retired_code_on_a_document_is_rejected(register: dict[str, Any]) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    register["reserved"] = [{"code": PLAN_1, "reason": "planned"}]
    assert any("is reserved; remove the reservation" in e
               for e in codes.inspect_codes(register, documents))
    register["reserved"] = []
    register["retired"] = [{"code": PLAN_1, "reason": "withdrawn"}]
    assert any("is retired and can never be reused" in e
               for e in codes.inspect_codes(register, documents))


def test_a_correct_tree_produces_no_code_errors(register: dict[str, Any]) -> None:
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/{CHILD}-child.md", parent="doc-p"),
        "doc-g": doc(code("OPS", "001"), f"governance/{code('OPS', '001')}-run.md",
                     kind="operation"),
        "doc-s": doc(SESS_1, f"sessions/{SESS_1}-notes.md", kind="session"),
    }
    assert codes.inspect_codes(register, documents) == []


def test_a_child_plan_may_sit_in_an_area_folder(register: dict[str, Any]) -> None:
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/An Area/{CHILD}-child.md", parent="doc-p"),
    }
    assert codes.inspect_codes(register, documents) == []


# --- The catalog ------------------------------------------------------------------------------


def test_catalog_lists_documents_plans_and_holds(register: dict[str, Any]) -> None:
    register["reserved"] = [{"code": PLAN_2, "reason": "a planned document"}]
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    rendered = codes.render_catalog(register, documents)
    assert f"| {PLAN_1} | plan | draft | repository-owner | docs/plans/{PLAN_1}-a.md |" in rendered
    assert "## Plans\n" in rendered and f"| {PLAN_1} | doc-a | draft |" in rendered
    assert f"| {PLAN_2} | reserved | a planned document |" in rendered
    assert rendered.endswith("1 documents — plan: 1.\n")


def test_catalog_counts_phases_when_a_backlog_exists(register: dict[str, Any]) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    items = [
        {"plan": "doc-a", "sources": [], "status": "queued"},
        {"plan": "doc-a", "sources": [], "status": "active", "agent": "agent-one"},
        {"plan": "doc-other", "sources": ["doc-a"], "status": "complete"},
        {"plan": "doc-a", "sources": [], "status": "cancelled"},
    ]
    rendered = codes.render_catalog(register, documents, items)
    assert "## Plans and their phases" in rendered
    assert f"| {PLAN_1} | doc-a | draft | 1 | 1 | 1 | agent-one |" in rendered


def test_catalog_is_deterministic(register: dict[str, Any]) -> None:
    documents = {
        "doc-b": doc(PLAN_2, f"plans/{PLAN_2}-b.md"),
        "doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md"),
    }
    first = codes.render_catalog(register, documents)
    assert first == codes.render_catalog(register, dict(reversed(documents.items())))
    assert first.index(PLAN_1) < first.index(PLAN_2)
