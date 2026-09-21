"""Exercise code allocation, register consistency and the generated catalog."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.governance import reservations
from src.governance.__main__ import ROOT
from src.governance.codes import (
    allocated,
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
    # ADR-004, ADR-005 and ADR-019 are held for backlog phases that have not been written yet.
    assert next_code("adr", register, {}) == "ADR-020"
    assert next_code("adr", register, {"doc-a": doc("ADR-020", kind="adr")}) == "ADR-021"


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


def test_catalog_flag_writes_committed_file(monkeypatch: pytest.MonkeyPatch, capsys: Any) -> None:
    """--catalog must write docs/08-governance/catalog.md, not just print it.

    This is the test whose absence let the flag silently print without writing: a
    test that only checked stdout would have passed throughout that outage.
    """
    from src.governance.__main__ import main

    target = ROOT / "docs/08-governance/catalog.md"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text("CORRUPTED\n", encoding="utf-8")
        monkeypatch.setattr("sys.argv", ["governance", "--catalog"])
        exit_code = main()
        assert exit_code == 0
        restored = target.read_text(encoding="utf-8")
        assert restored == original
        # stdout must still carry the full rendered catalog, byte-identical to the
        # file, so the `--catalog > catalog.md` and `diff <(--catalog) catalog.md`
        # forms used elsewhere in the repository keep working.
        captured = capsys.readouterr()
        assert captured.out.rstrip("\n") == restored.rstrip("\n")
    finally:
        target.write_text(original, encoding="utf-8")


def test_catalog_flag_writes_nothing_when_audit_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failing audit must leave the existing catalog untouched, not truncate it.

    A shell redirect (`--catalog > catalog.md`) truncates its target before the
    command runs at all, so a failing validator used to destroy the catalog. The
    tool must refuse to write anything once the audit reports errors.
    """
    from src.governance import __main__ as governance_main

    target = ROOT / "docs/08-governance/catalog.md"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text("CORRUPTED\n", encoding="utf-8")
        monkeypatch.setattr(governance_main, "audit", lambda root: (["synthetic failure"], [], {}))
        monkeypatch.setattr("sys.argv", ["governance", "--catalog"])
        exit_code = governance_main.main()
        assert exit_code == 1
        assert target.read_text(encoding="utf-8") == "CORRUPTED\n"
    finally:
        target.write_text(original, encoding="utf-8")


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


# --- REQ-013 R05: allocation is collision-proof across concurrent worktrees -----------------
#
# The defect these cover is not arithmetic. `next_code()` was correct as a function; it was
# called against committed state alone, so two worktrees that both allocated before either
# merged computed the same code and discovered it at merge. This repository paid for that twice
# in session codes (`5b3848c`, `94f7978`) and once in the idea log (`65491d4`).
#
# R05's verification has two halves and the second is the one worth the machinery: "confirm the
# reservation is visible to the second caller before the first has merged". A test that only
# calls `reserve()` twice in one process proves mutual exclusion but not *sharing*, so the
# worktree tests below build a real git repository with real linked worktrees and check that a
# reservation taken in one is seen from the other with nothing committed anywhere.


@pytest.fixture
def repo_with_worktrees(tmp_path: Path) -> dict[str, Path]:
    """A real git repository with two linked worktrees, committed once so branches exist."""
    import subprocess

    primary = tmp_path / "primary"
    primary.mkdir()

    def git(*args: str, cwd: Path = primary) -> None:
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    git("init", "-b", "dev")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    (primary / "seed.txt").write_text("seed\n")
    git("add", "seed.txt")
    git("commit", "-m", "seed")

    first = tmp_path / "wt-first"
    second = tmp_path / "wt-second"
    git("worktree", "add", "-b", "agent/first", str(first), "dev")
    git("worktree", "add", "-b", "agent/second", str(second), "dev")
    return {"primary": primary, "first": first, "second": second}


def test_allocated_counts_a_pre_merge_reservation_as_spent(
    bare_register: dict[str, Any],
) -> None:
    """The reserved set joins committed documents and register holds as codes already gone."""
    documents = {"doc-a": doc("PLAN-001")}
    assert "PLAN-002" in allocated(bare_register, documents, {"PLAN-002"})
    assert next_code("plan", bare_register, documents) == "PLAN-002"
    assert next_code("plan", bare_register, documents, reserved={"PLAN-002"}) == "PLAN-003"


def test_reservations_do_not_disturb_allocation_in_another_series(
    bare_register: dict[str, Any],
) -> None:
    """A held SESS code must not push the PLAN counter; series are independent."""
    documents = {"doc-a": doc("PLAN-001")}
    reserved = {"SESS-2026-09-21-01"}
    assert next_code("plan", bare_register, documents, reserved=reserved) == "PLAN-002"


def test_dated_allocation_skips_a_reserved_same_day_sequence(
    bare_register: dict[str, Any],
) -> None:
    """The session-code collision this phase exists for, at the arithmetic level."""
    documents: dict[str, Any] = {}
    first = next_code("session", bare_register, documents, today=TODAY)
    assert first == "SESS-2026-09-05-01"
    second = next_code("session", bare_register, documents, today=TODAY, reserved={first})
    assert second == "SESS-2026-09-05-02"
    assert first != second


def test_reserve_is_mutually_exclusive(tmp_path: Path) -> None:
    """Two callers racing for one code: exactly one wins, by O_EXCL rather than by a lock."""
    import subprocess

    subprocess.run(["git", "init", "-b", "dev"], cwd=tmp_path, check=True, capture_output=True)
    assert reservations.reserve(tmp_path, "PLAN-777") is True
    assert reservations.reserve(tmp_path, "PLAN-777") is False
    assert "PLAN-777" in reservations.active(tmp_path)
    assert reservations.release(tmp_path, "PLAN-777") is True
    assert reservations.release(tmp_path, "PLAN-777") is False
    assert "PLAN-777" not in reservations.active(tmp_path)


def test_reserve_refuses_a_code_that_would_escape_the_store(tmp_path: Path) -> None:
    """A code is a filename here, so a traversal attempt is rejected rather than normalised."""
    import subprocess

    subprocess.run(["git", "init", "-b", "dev"], cwd=tmp_path, check=True, capture_output=True)
    for bad in ("../escape", "PLAN/001", "", "plan-001"):
        with pytest.raises(ValueError):
            reservations.reserve(tmp_path, bad)


def test_two_worktrees_share_one_reservation_store(repo_with_worktrees: dict[str, Path]) -> None:
    """R05's second half: the reservation is visible to the second caller pre-merge.

    Nothing is committed in either worktree. If the store were a tracked file this assertion
    would fail, which is the argument against putting reservations in `codes.yaml` on `dev`.
    """
    first, second = repo_with_worktrees["first"], repo_with_worktrees["second"]
    assert reservations.reservation_dir(first) == reservations.reservation_dir(second)

    assert reservations.reserve(first, "SESS-2026-09-21-01") is True
    assert "SESS-2026-09-21-01" in reservations.active(second)
    assert reservations.reserve(second, "SESS-2026-09-21-01") is False


def test_two_worktrees_allocating_the_same_kind_get_different_codes(
    repo_with_worktrees: dict[str, Path], bare_register: dict[str, Any]
) -> None:
    """R05 itself, end to end, with nothing merged between the two allocations."""
    first, second = repo_with_worktrees["first"], repo_with_worktrees["second"]
    documents: dict[str, Any] = {}

    def allocate(root: Path) -> str:
        for _ in range(10):
            code = next_code(
                "session", bare_register, documents, today=TODAY, reserved=reservations.active(root)
            )
            if reservations.reserve(root, code):
                return code
        raise AssertionError("exhausted attempts")

    from_first = allocate(first)
    from_second = allocate(second)
    assert from_first == "SESS-2026-09-05-01"
    assert from_second == "SESS-2026-09-05-02"
    assert from_first != from_second


def test_prune_drops_a_satisfied_reservation_and_keeps_an_outstanding_one(
    repo_with_worktrees: dict[str, Path],
) -> None:
    """A reservation whose document has landed is released; one still in flight is not."""
    first = repo_with_worktrees["first"]
    reservations.reserve(first, "PLAN-900")
    reservations.reserve(first, "PLAN-901")
    dropped = reservations.prune(first, {"doc-landed": doc("PLAN-900")})
    assert dropped == ["PLAN-900"]
    assert reservations.active(first) == {"PLAN-901"}


def test_prune_drops_an_expired_reservation(repo_with_worktrees: dict[str, Path]) -> None:
    """An agent that allocated and never wrote cannot hold a hole in the series forever."""
    first = repo_with_worktrees["first"]
    reservations.reserve(first, "PLAN-902")
    assert reservations.prune(first, {}) == []
    later = time.time() + reservations.TTL_SECONDS + 1
    assert reservations.prune(first, {}, now=later) == ["PLAN-902"]
    assert reservations.active(first) == set()
