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
ANA, BEN = "ana", "ben"
#: The registered developers every code check is given.
TEAM = {ANA, BEN}


@pytest.fixture
def register() -> dict[str, Any]:
    """The template register the scaffold copies: the nine series, nothing held."""
    return dict(yaml.safe_load((PLUGIN_ROOT / "templates" / "codes.yaml").read_text()))


@pytest.fixture
def unscoped(register: dict[str, Any]) -> dict[str, Any]:
    """The template register with every series unscoped: codes without a handle, as allocated
    before series were scoped and still allocated in a series that says ``scoped: false``."""
    for entry in register["series"]:
        entry["scoped"] = False
    return register


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
        "series": "PLAN", "numbering": "counter", "handle": None, "number": 3, "sub": None,
        "stem": PLAN_3,
    }
    assert codes.parse_code(PLAN_3 + ".02")["sub"] == 2  # type: ignore[index]
    assert codes.parse_code(SESS_1) == {
        "series": "SESS", "numbering": "dated", "handle": None, "date": STAMP, "sequence": 1,
        "stem": SESS_1,
    }


@pytest.mark.parametrize("value", ["plan-1", code("PLAN", "1"), code("PLAN", "0001"),
                                   code("PLAN", "001.1"), "PLAN", ""])
def test_malformed_codes_are_rejected(value: str) -> None:
    assert codes.parse_code(value) is None


# --- Allocation ---------------------------------------------------------------------------


def test_counter_allocation_takes_the_next_number(unscoped: dict[str, Any]) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    assert codes.next_code("plan", unscoped, documents) == PLAN_2
    assert codes.next_code("adr", unscoped, documents) == code("ADR", "001")


def test_counter_allocation_skips_reserved_and_retired_codes(unscoped: dict[str, Any]) -> None:
    unscoped["reserved"] = [{"code": PLAN_1, "reason": "held for a planned document"}]
    assert codes.next_code("plan", unscoped, {}) == PLAN_2
    unscoped["retired"] = [{"code": PLAN_2, "reason": "withdrawn"}]
    assert codes.next_code("plan", unscoped, {}) == PLAN_3


def test_allocation_is_stable_across_repeated_runs(unscoped: dict[str, Any]) -> None:
    assert {codes.next_code("plan", unscoped, {}) for _ in range(3)} == {PLAN_1}


def test_dated_allocation_uses_the_date_and_a_same_day_sequence(unscoped: dict[str, Any]) -> None:
    assert codes.next_code("session", unscoped, {}, today=TODAY) == SESS_1
    documents = {"doc-s": doc(SESS_1, f"sessions/{SESS_1}-a.md", kind="session")}
    assert codes.next_code("session", unscoped, documents, today=TODAY) == code(
        "SESS", f"{STAMP}-02")
    later = date(2030, 1, 3)
    assert codes.next_code("session", unscoped, documents, today=later) == code(
        "SESS", f"{later.isoformat()}-01")


def test_sub_codes_allocate_under_their_parent(register: dict[str, Any]) -> None:
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-p/{PLAN_3}-overview.md"),
        "doc-c": doc(PLAN_3 + ".01", f"plans/{PLAN_3}-p/{PLAN_3}.01-c.md", parent="doc-p"),
    }
    assert codes.next_code("plan", register, documents, parent="doc-p") == PLAN_3 + ".02"


def test_a_pre_merge_reservation_counts_as_spent(unscoped: dict[str, Any]) -> None:
    assert codes.next_code("plan", unscoped, {}, reserved={PLAN_1}) == PLAN_2
    assert codes.next_code("adr", unscoped, {}, reserved={PLAN_1}) == code("ADR", "001")
    reserved = {SESS_1}
    assert codes.next_code("session", unscoped, {}, today=TODAY, reserved=reserved) == code(
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
    errors = codes.inspect_codes(register, documents, developers=TEAM)
    assert any(expected in error for error in errors), errors


def test_a_reserved_or_retired_code_on_a_document_is_rejected(register: dict[str, Any]) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    register["reserved"] = [{"code": PLAN_1, "reason": "planned"}]
    assert any("is reserved; remove the reservation" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))
    register["reserved"] = []
    register["retired"] = [{"code": PLAN_1, "reason": "withdrawn"}]
    assert any("is retired and can never be reused" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))


def test_a_correct_tree_produces_no_code_errors(register: dict[str, Any]) -> None:
    register["legacy"] = [PLAN_3, code("OPS", "001"), SESS_1]
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/{CHILD}-child.md", parent="doc-p"),
        "doc-g": doc(code("OPS", "001"), f"governance/{code('OPS', '001')}-run.md",
                     kind="operation"),
        "doc-s": doc(SESS_1, f"sessions/{SESS_1}-notes.md", kind="session"),
    }
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


def test_a_child_plan_may_sit_in_an_area_folder(register: dict[str, Any]) -> None:
    register["legacy"] = [PLAN_3]
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/An Area/{CHILD}-child.md", parent="doc-p"),
    }
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


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


# --- Handle-scoped codes -------------------------------------------------------------------
#
# A counter or dated code in a scoped series carries the allocating developer's handle
# (``<SERIES>-<handle>-NNN``, ``<SERIES>-<handle>-YYYY-MM-DD-NN``), and numbering counts per
# handle, so two developers allocating on separate machines never take the same code. Codes
# without a handle, written before the change, stay valid.

def scoped(series: str, handle: str, rest: str) -> str:
    return code(series, f"{handle}-{rest}")


def test_parse_code_reads_a_handle() -> None:
    value = scoped("PLAN", ANA, "004")
    assert codes.parse_code(value) == {
        "series": "PLAN", "numbering": "counter", "handle": ANA, "number": 4, "sub": None,
        "stem": value,
    }
    sub = codes.parse_code(value + ".02")
    assert sub is not None
    assert sub["stem"] == value
    dated = scoped("SESS", ANA, f"{STAMP}-03")
    assert codes.parse_code(dated) == {
        "series": "SESS", "numbering": "dated", "handle": ANA, "date": STAMP, "sequence": 3,
        "stem": dated,
    }
    legacy = codes.parse_code(PLAN_3)
    assert legacy is not None
    assert legacy["handle"] is None


@pytest.mark.parametrize("value", [
    scoped("PLAN", "Ana", "001"),            # upper-case handle
    scoped("PLAN", "1ana", "001"),           # handle starts with a digit
    scoped("PLAN", "a_b", "001"),            # underscore
    scoped("PLAN", "a" * 17, "001"),         # longer than sixteen characters
    scoped("PLAN", ANA, "01"),               # two-digit number
    scoped("PLAN", ANA, "001.1"),            # one-digit sub-code
    scoped("PLAN", f"{ANA}-{BEN}", "001"),   # two handles
    code("PLAN", "-001"),                    # empty handle
    scoped("SESS", ANA, f"{STAMP}-1"),       # one-digit dated sequence
])
def test_a_malformed_handle_scoped_code_is_rejected(
    register: dict[str, Any], value: str
) -> None:
    assert codes.parse_code(value) is None
    documents = {"doc-a": doc(value, f"plans/{value}-a.md")}
    assert any(f"malformed code {value}" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))


def test_two_developers_allocating_offline_get_different_codes(register: dict[str, Any]) -> None:
    """Each starts from the same committed tree and sees nothing of the other's allocation."""
    tree = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    ana = codes.next_code("plan", register, tree, handle=ANA)
    ben = codes.next_code("plan", register, tree, handle=BEN)
    assert (ana, ben) == (scoped("PLAN", ANA, "001"), scoped("PLAN", BEN, "001"))
    ana_s = codes.next_code("session", register, tree, today=TODAY, handle=ANA)
    ben_s = codes.next_code("session", register, tree, today=TODAY, handle=BEN)
    assert (ana_s, ben_s) == (scoped("SESS", ANA, f"{STAMP}-01"),
                              scoped("SESS", BEN, f"{STAMP}-01"))


def test_numbering_counts_per_handle(register: dict[str, Any]) -> None:
    ana_2, ben_7 = scoped("PLAN", ANA, "002"), scoped("PLAN", BEN, "007")
    documents = {
        "doc-a": doc(ana_2, f"plans/{ana_2}-a.md"),
        "doc-b": doc(ben_7, f"plans/{ben_7}-b.md"),
        "doc-l": doc(PLAN_3, f"plans/{PLAN_3}-l.md"),
    }
    assert codes.next_code("plan", register, documents, handle=ANA) == scoped("PLAN", ANA, "003")
    assert codes.next_code("plan", register, documents, handle=BEN) == scoped("PLAN", BEN, "008")
    reserved = {scoped("PLAN", ANA, "003")}
    assert codes.next_code("plan", register, documents, reserved=reserved,
                           handle=ANA) == scoped("PLAN", ANA, "004")


def test_a_sub_code_follows_its_parents_stem_whoever_allocates(register: dict[str, Any]) -> None:
    parent = scoped("PLAN", ANA, "001")
    child = parent + ".01"
    documents = {
        "doc-p": doc(parent, f"plans/{parent}-p/{parent}-overview.md"),
        "doc-c": doc(child, f"plans/{parent}-p/{child}-c.md", parent="doc-p"),
    }
    assert codes.next_code("plan", register, documents, parent="doc-p",
                           handle=BEN) == parent + ".02"
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


@pytest.mark.parametrize("kind", ["plan", "requirement", "adr", "architecture", "prompt",
                                  "operation", "session", "walkthrough"])
def test_allocation_without_a_handle_refuses(register: dict[str, Any], kind: str) -> None:
    with pytest.raises(ValueError, match="carry the allocating developer's handle"):
        codes.next_code(kind, register, {}, today=TODAY)


def test_governance_codes_stay_unscoped(register: dict[str, Any]) -> None:
    """Governance rules are the team's, not one developer's: the series takes no handle."""
    assert codes.next_code("governance", register, {}) == code("GOV", "001")
    assert codes.next_code("governance", register, {}, handle=ANA) == code("GOV", "001")
    value = scoped("GOV", ANA, "001")
    documents = {"doc-g": doc(value, f"governance/{value}-g.md", kind="governance")}
    assert any("GOV codes carry no handle" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))


def test_unscoped_codes_written_before_the_change_still_validate(
    register: dict[str, Any],
) -> None:
    register["legacy"] = [PLAN_3, SESS_1, code("OPS", "001")]
    ana_1 = scoped("PLAN", ANA, "001")
    ana_s = scoped("SESS", ANA, f"{STAMP}-01")
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/{CHILD}-child.md", parent="doc-p"),
        "doc-l": doc(SESS_1, f"sessions/{SESS_1}-notes.md", kind="session"),
        "doc-a": doc(ana_1, f"plans/{ana_1}-a.md"),
        "doc-s": doc(ana_s, f"sessions/{ana_s}-notes.md", kind="session"),
        "doc-o": doc(code("OPS", "001"), f"governance/{code('OPS', '001')}-run.md",
                     kind="operation"),
    }
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


def test_a_duplicate_is_refused_in_either_form(register: dict[str, Any]) -> None:
    register["legacy"] = [PLAN_1]
    ana_1 = scoped("PLAN", ANA, "001")
    documents = {
        "doc-a": doc(ana_1, f"plans/{ana_1}-a.md"),
        "doc-b": doc(ana_1, f"plans/{ana_1}-b.md"),
        "doc-c": doc(PLAN_1, f"plans/{PLAN_1}-c.md"),
        "doc-d": doc(PLAN_1, f"plans/{PLAN_1}-d.md"),
        "doc-e": doc(scoped("PLAN", BEN, "001"), f"plans/{scoped('PLAN', BEN, '001')}-e.md"),
    }
    errors = codes.inspect_codes(register, documents, developers=TEAM)
    assert any(f"duplicate code {ana_1}" in e for e in errors), errors
    assert any(f"duplicate code {PLAN_1}" in e for e in errors), errors
    assert len([e for e in errors if "duplicate" in e]) == 2, errors


def test_a_handle_must_be_a_registered_developer(register: dict[str, Any]) -> None:
    zed = scoped("PLAN", "zed", "001")
    documents = {"doc-z": doc(zed, f"plans/{zed}-z.md")}
    assert any("handle zed is not a developer" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))


def test_a_scoped_filename_and_folder_follow_the_code(register: dict[str, Any]) -> None:
    parent = scoped("PLAN", ANA, "001")
    documents = {
        "doc-p": doc(parent, f"plans/{PLAN_1}-p/{parent}-overview.md"),
    }
    assert any(f"containing folder must start with {parent}-" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))
    documents = {"doc-p": doc(parent, f"plans/{PLAN_1}-p.md")}
    assert any(f"filename must start with {parent}-" in e
               for e in codes.inspect_codes(register, documents, developers=TEAM))


def test_held_codes_may_carry_a_handle(register: dict[str, Any]) -> None:
    register["reserved"] = [{"code": scoped("PLAN", ANA, "001"), "reason": "planned"}]
    assert codes.inspect_register(register, KINDS) == []
    assert codes.next_code("plan", register, {}, handle=ANA) == scoped("PLAN", ANA, "002")


def test_the_catalog_groups_codes_by_handle(register: dict[str, Any]) -> None:
    ana_1, ben_1 = scoped("PLAN", ANA, "001"), scoped("PLAN", BEN, "001")
    documents = {
        "doc-b": doc(ben_1, f"plans/{ben_1}-b.md"),
        "doc-a": doc(ana_1, f"plans/{ana_1}-a.md"),
        "doc-l": doc(PLAN_2, f"plans/{PLAN_2}-l.md"),
    }
    rendered = codes.render_catalog(register, documents)
    assert rendered.index(PLAN_2) < rendered.index(ana_1) < rendered.index(ben_1)


def test_the_code_patterns_in_the_schemas_accept_both_forms() -> None:
    import json
    import re

    document = json.loads((PLUGIN_ROOT / "schemas" / "document.schema.json").read_text())
    register_schema = json.loads((PLUGIN_ROOT / "schemas" / "codes.schema.json").read_text())
    patterns = [
        re.compile(document["properties"]["code"]["pattern"]),
        re.compile(register_schema["definitions"]["ledgerEntry"]["properties"]["code"]["pattern"]),
    ]
    good = [PLAN_1, CHILD, SESS_1, scoped("PLAN", ANA, "001"), scoped("PLAN", ANA, "001") + ".02",
            scoped("SESS", ANA, f"{STAMP}-01")]
    bad = [scoped("PLAN", "Ana", "001"), scoped("PLAN", "a" * 17, "001"),
           scoped("PLAN", ANA, "01")]
    for pattern in patterns:
        assert all(pattern.match(value) for value in good)
        assert not any(pattern.match(value) for value in bad)


# --- Legacy codes and the developer set ------------------------------------------------------
#
# A code without a handle in a scoped series is valid only when the register's ``legacy`` list
# names it (or, for a sub-code, names its parent's code): the codes that existed before the series
# was scoped. Nothing new without a handle can enter a scoped series. The developer set is always
# given; an empty set (no registry) refuses every handle.


def test_an_unscoped_code_in_a_scoped_series_needs_a_legacy_entry(
    register: dict[str, Any],
) -> None:
    documents = {"doc-a": doc(PLAN_1, f"plans/{PLAN_1}-a.md")}
    assert any(f"{PLAN_1} carries no developer handle and is not in the register's legacy list"
               in e for e in codes.inspect_codes(register, documents, developers=TEAM))
    register["legacy"] = [PLAN_1]
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


def test_a_legacy_parents_sub_codes_need_no_entry_of_their_own(
    register: dict[str, Any],
) -> None:
    register["legacy"] = [PLAN_3]
    documents = {
        "doc-p": doc(PLAN_3, f"plans/{PLAN_3}-set/{PLAN_3}-overview.md"),
        "doc-c": doc(CHILD, f"plans/{PLAN_3}-set/{CHILD}-child.md", parent="doc-p"),
    }
    assert codes.inspect_codes(register, documents, developers=TEAM) == []
    assert codes.next_code("plan", register, documents, parent="doc-p",
                           handle=ANA) == PLAN_3 + ".02"


def test_an_unscoped_series_needs_no_legacy_entry(register: dict[str, Any]) -> None:
    gov = code("GOV", "004")
    documents = {"doc-g": doc(gov, f"governance/{gov}-g.md", kind="governance")}
    assert codes.inspect_codes(register, documents, developers=TEAM) == []


@pytest.mark.parametrize(("value", "message"), [
    ("plan-1", "malformed or names an unknown series"),
    (code("NOPE", "001"), "malformed or names an unknown series"),
    (scoped("PLAN", ANA, "001"), "carries a handle"),
    (code("GOV", "001"), "GOV is unscoped"),
    (CHILD, "a sub-code"),
])
def test_the_register_rejects_a_bad_legacy_entry(
    register: dict[str, Any], value: str, message: str
) -> None:
    register["legacy"] = [value]
    assert any(f"codes: legacy code {value}" in e and message in e
               for e in codes.inspect_register(register, KINDS))


def test_the_template_register_has_an_empty_legacy_list(register: dict[str, Any]) -> None:
    assert register["legacy"] == []


def test_the_developer_set_is_always_given() -> None:
    import inspect

    parameter = inspect.signature(codes.inspect_codes).parameters["developers"]
    assert parameter.default is inspect.Parameter.empty
    assert "None" not in str(parameter.annotation)


def test_no_registry_refuses_every_handle(register: dict[str, Any]) -> None:
    value = scoped("PLAN", ANA, "001")
    documents = {"doc-a": doc(value, f"plans/{value}-a.md")}
    assert any(f"handle {ANA} is not a developer" in e
               for e in codes.inspect_codes(register, documents, developers=set()))
