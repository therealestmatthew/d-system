"""Exercise code allocation, register consistency and the generated catalog."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.governance.__main__ import ROOT
from src.governance.codes import (
    inspect_codes,
    inspect_register,
    next_code,
    parse_code,
    render_catalog,
)

TODAY = date(2026, 9, 5)
KINDS = {
    "plan",
    "adr",
    "architecture",
    "prompt",
    "session",
    "requirement",
    "walkthrough",
    "operation",
    "governance",
}


@pytest.fixture
def register() -> dict[str, Any]:
    return dict(yaml.safe_load((ROOT / "docs/08-governance/codes.yaml").read_text()))


@pytest.fixture
def bare_register(register: dict[str, Any]) -> dict[str, Any]:
    """Real series definitions with nothing held.

    Allocator arithmetic must not shift when the repository legitimately reserves
    or retires a code; tests asserting exact next codes use this instead of the
    live register. Coverage of the live register stays in the validation tests.
    """
    return {**register, "reserved": [], "retired": []}


def doc(code: str, **changes: Any) -> dict[str, Any]:
    return {
        "path": "docs/01-plans/example.md",
        "kind": "plan",
        "status": "draft",
        "owner": "repository-owner",
        "created": "2026-09-05",
        "code": code,
        **changes,
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("PLAN-003", {"series": "PLAN", "numbering": "counter", "number": 3, "sub": None}),
        ("PLAN-003.01", {"series": "PLAN", "numbering": "counter", "number": 3, "sub": 1}),
        ("SESS-2026-09-05-02", {"series": "SESS", "numbering": "dated", "sequence": 2}),
    ],
)
def test_parse_code_reads_both_grammars(value: str, expected: dict[str, Any]) -> None:
    parsed = parse_code(value)
    assert parsed is not None
    assert expected.items() <= parsed.items()


@pytest.mark.parametrize(
    "value", ["PLAN-3", "PLAN-0003", "plan-003", "PLAN-003.1", "SESS-2026-09-05"]
)
def test_malformed_codes_are_rejected(value: str) -> None:
    assert parse_code(value) is None


def test_counter_allocation_skips_reserved_codes(register: dict[str, Any]) -> None:
    # ADR-004 and ADR-005 are held for backlog phases that have not been written yet.
    assert next_code("adr", register, {}) == "ADR-006"
    assert next_code("adr", register, {"doc-a": doc("ADR-006", kind="adr")}) == "ADR-007"


def test_counter_allocation_skips_retired_codes(register: dict[str, Any]) -> None:
    register["retired"] = [{"code": "ARCH-001", "reason": "Withdrawn during review."}]
    assert next_code("architecture", register, {}) == "ARCH-002"


def test_allocation_is_stable_across_repeated_runs(bare_register: dict[str, Any]) -> None:
    documents = {"doc-a": doc("PLAN-001")}
    first = next_code("plan", bare_register, documents)
    assert first == next_code("plan", bare_register, documents) == "PLAN-002"


def test_dated_allocation_uses_the_document_date(register: dict[str, Any]) -> None:
    assert next_code("session", register, {}, today=TODAY) == "SESS-2026-09-05-01"
    documents = {
        "doc-a": doc("SESS-2026-09-05-01", kind="session"),
        "doc-b": doc("SESS-2026-09-04-09", kind="session"),
    }
    # A previous day's higher sequence must not advance today's counter.
    assert next_code("session", register, documents, today=TODAY) == "SESS-2026-09-05-02"


def test_sub_codes_allocate_under_their_parent(bare_register: dict[str, Any]) -> None:
    documents = {"doc-parent": doc("PLAN-003")}
    assert next_code("plan", bare_register, documents, parent="doc-parent") == "PLAN-003.01"
    documents["doc-child"] = doc("PLAN-003.01", parent="doc-parent")
    assert next_code("plan", bare_register, documents, parent="doc-parent") == "PLAN-003.02"
    # A sub-code never advances the top-level counter.
    assert next_code("plan", bare_register, documents) == "PLAN-004"


@pytest.mark.parametrize(
    ("kind", "parent", "expected"),
    [
        ("session", "doc-parent", "takes no parent"),
        ("adr", "doc-parent", "does not allow sub-codes"),
        ("plan", "doc-missing", "unknown parent document"),
        ("nonsense", None, "no series is registered"),
    ],
)
def test_allocation_rejects_impossible_requests(
    register: dict[str, Any], kind: str, parent: str | None, expected: str
) -> None:
    with pytest.raises(ValueError, match=expected):
        next_code(kind, register, {"doc-parent": doc("PLAN-003")}, parent=parent)


def test_sub_code_parent_must_hold_a_top_level_code(register: dict[str, Any]) -> None:
    documents = {"doc-parent": doc("PLAN-003.01")}
    with pytest.raises(ValueError, match="does not hold a top-level"):
        next_code("plan", register, documents, parent="doc-parent")


def test_register_rejects_a_duplicate_series(register: dict[str, Any]) -> None:
    register["series"].append(dict(register["series"][0]))
    errors = inspect_register(register, KINDS)
    assert any("duplicate series code" in error for error in errors)


def test_register_rejects_a_code_that_is_both_reserved_and_retired(
    register: dict[str, Any],
) -> None:
    register["retired"] = [{"code": "ADR-004", "reason": "Withdrawn after reservation."}]
    errors = inspect_register(register, KINDS)
    assert any("ADR-004 cannot be reserved and retired" in error for error in errors)


def test_register_rejects_a_hold_on_an_unknown_series(register: dict[str, Any]) -> None:
    register["reserved"].append({"code": "NOPE-001", "reason": "No such series."})
    errors = inspect_register(register, KINDS)
    assert any("unknown series" in error for error in errors)


def test_register_requires_a_series_for_every_kind(register: dict[str, Any]) -> None:
    register["series"] = [entry for entry in register["series"] if entry["kind"] != "adr"]
    assert any("no series registered for kind adr" in e for e in inspect_register(register, KINDS))


def test_dated_series_cannot_allow_sub_codes(register: dict[str, Any]) -> None:
    for entry in register["series"]:
        if entry["code"] == "SESS":
            entry["sub_codes"] = True
    assert any("cannot allow sub-codes" in error for error in inspect_register(register, KINDS))


def test_committed_catalog_matches_regenerated_output() -> None:
    """The committed file is generated output; drift is a build failure, not a merge conflict."""
    from src.governance.__main__ import audit, audit_backlog

    errors, _, result = audit(ROOT)
    assert errors == []
    backlog_errors, catalog = audit_backlog(ROOT, result)
    assert backlog_errors == []
    rendered = render_catalog(result["register"], result["documents"], catalog["items"])
    committed = Path(ROOT / "docs/08-governance/catalog.md").read_text(encoding="utf-8")
    assert committed.rstrip("\n") == rendered.rstrip("\n")


def test_catalog_reports_documents_holds_and_phase_rollup(register: dict[str, Any]) -> None:
    documents = {"doc-a": doc("PLAN-001", path="docs/01-plans/PLAN-001-a.md")}
    items = [
        {"plan": "doc-a", "sources": [], "status": "active", "agent": "agent-blue"},
        {"plan": "doc-a", "sources": [], "status": "complete"},
        {"plan": "doc-a", "sources": [], "status": "cancelled"},
    ]
    rendered = render_catalog(register, documents, items)
    row = "| PLAN-001 | plan | draft | repository-owner | docs/01-plans/PLAN-001-a.md |"
    assert row in rendered
    assert "| PLAN-001 | doc-a | draft | 0 | 1 | 1 | agent-blue |" in rendered
    assert "| ADR-004 | reserved |" in rendered
    assert "1 documents — plan: 1." in rendered


def coded(code: str, path: str, **changes: Any) -> dict[str, Any]:
    return doc(code, path=path, **changes)


@pytest.mark.parametrize(
    ("documents", "expected"),
    [
        (
            {
                "doc-a": coded("PLAN-001", "docs/01-plans/PLAN-001-a.md"),
                "doc-b": coded("PLAN-001", "docs/01-plans/PLAN-001-b.md"),
            },
            "duplicate code PLAN-001",
        ),
        (
            {"doc-a": coded("PLAN-001", "docs/04-decisions/PLAN-001-a.md", kind="adr")},
            "kind adr requires a ADR code",
        ),
        (
            {"doc-a": coded("PLAN-2026-09-05-01", "docs/01-plans/PLAN-2026-09-05-01-a.md")},
            "PLAN uses counter numbering",
        ),
        (
            {"doc-a": coded("NOPE-1", "docs/01-plans/NOPE-1-a.md")},
            "malformed code NOPE-1",
        ),
        (
            {"doc-a": coded("PLAN-001", "docs/01-plans/wrong-name.md")},
            "filename must start with PLAN-001-",
        ),
        (
            {"doc-a": coded("ADR-001", "docs/01-plans/ADR-001-a.md", kind="adr")},
            "adr belongs under docs/04-decisions/",
        ),
        (
            {"doc-a": coded("PLAN-001", "docs/01-plans/ADR-004-a.md")},
            "filename must start with PLAN-001-",
        ),
        (
            {"doc-a": coded("ADR-004", "docs/04-decisions/ADR-004-a.md", kind="adr")},
            "ADR-004 is reserved; remove the reservation in this change",
        ),
        (
            {
                "doc-a": coded("PLAN-001", "docs/01-plans/PLAN-001-a.md"),
                "doc-b": coded("PLAN-002", "docs/01-plans/PLAN-002-b.md", parent="doc-a"),
            },
            "child of doc-a requires a sub-code under its parent",
        ),
        (
            {"doc-a": coded("PLAN-001.01", "docs/01-plans/PLAN-001.01-a.md")},
            "sub-code PLAN-001.01 requires a parent",
        ),
        (
            {
                "doc-a": coded("PLAN-001", "docs/01-plans/PLAN-001-a.md"),
                "doc-b": coded("PLAN-002.01", "docs/01-plans/PLAN-002.01-b.md", parent="doc-a"),
            },
            "sub-code stem PLAN-002 does not match parent PLAN-001",
        ),
        (
            {
                "doc-a": coded("SESS-2026-09-05-01", "docs/03-sessions/SESS-2026-09-05-01-a.md",
                               kind="session", created="2026-09-04"),
            },
            "code date 2026-09-05 must equal created 2026-09-04",
        ),
        (
            {"doc-a": coded("PLAN-003.01", "docs/01-plans/nested/PLAN-003.01-a.md",
                            parent="doc-p")},
            "containing folder must start with PLAN-003-",
        ),
        (
            {"doc-a": coded("PLAN-003.01", "docs/01-plans/PLAN-003-p/a/b/PLAN-003.01-a.md",
                            parent="doc-p")},
            "nests at most one area folder deep",
        ),
        (
            {"doc-a": coded("PLAN-003.01", "docs/01-plans/nested/area/PLAN-003.01-a.md",
                            parent="doc-p")},
            "containing folder must start with PLAN-003-",
        ),
        (
            {"doc-a": coded("PLAN-003", "docs/01-plans/PLAN-003-p/area/PLAN-003-overview.md")},
            "an area folder holds child plans; the overview sits beside it",
        ),
    ],
)
def test_strict_rules_reject(
    register: dict[str, Any], documents: dict[str, Any], expected: str
) -> None:
    errors = inspect_codes(register, documents, strict=True)
    assert any(expected in error for error in errors), errors


def test_a_document_without_a_code_is_rejected(register: dict[str, Any]) -> None:
    documents = {"doc-a": {"path": "docs/01-plans/a.md", "kind": "plan", "created": "2026-09-05"}}
    errors = inspect_codes(register, documents, strict=True)
    assert any("missing code; run --next-code plan" in error for error in errors)


def test_retired_codes_can_never_be_reused(register: dict[str, Any]) -> None:
    register["retired"] = [{"code": "PLAN-001", "reason": "Plan withdrawn before approval."}]
    documents = {"doc-a": doc("PLAN-001", path="docs/01-plans/PLAN-001-a.md")}
    errors = inspect_codes(register, documents, strict=True)
    assert any("PLAN-001 is retired and can never be reused" in error for error in errors)


def test_a_correct_tree_produces_no_code_errors(register: dict[str, Any]) -> None:
    documents = {
        "doc-p": doc("PLAN-003", path="docs/01-plans/PLAN-003-set/PLAN-003-overview.md"),
        "doc-c": doc(
            "PLAN-003.01",
            path="docs/01-plans/PLAN-003-set/PLAN-003.01-child.md",
            parent="doc-p",
        ),
        "doc-s": doc(
            "SESS-2026-09-05-01",
            path="docs/03-sessions/SESS-2026-09-05-01-notes.md",
            kind="session",
        ),
    }
    assert inspect_codes(register, documents, strict=True) == []


def test_a_child_plan_may_sit_in_an_area_folder(register: dict[str, Any]) -> None:
    """Area folders group a large plan set for a reader; their names are labels, not codes."""
    documents = {
        "doc-p": doc("PLAN-003", path="docs/01-plans/PLAN-003-set/PLAN-003-overview.md"),
        "doc-c": doc(
            "PLAN-003.01",
            path="docs/01-plans/PLAN-003-set/The Idea Lifecycle/PLAN-003.01-child.md",
            parent="doc-p",
        ),
    }
    assert inspect_codes(register, documents, strict=True) == []


def test_missing_code_is_tolerated_before_enforcement(register: dict[str, Any]) -> None:
    """The backfill commits relied on this gate; keep it honest."""
    documents = {"doc-a": {"path": "docs/01-plans/anything.md", "kind": "plan",
                           "created": "2026-09-05"}}
    assert inspect_codes(register, documents, strict=False) == []
    assert inspect_codes(register, documents, strict=True) != []
