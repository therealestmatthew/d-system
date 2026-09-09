"""Tests for the idea record system — schema, writer, migration, projection and view.

The log is append-only and permanent, so these tests care about two different things. Most
build a temporary log and exercise the writer's refusals against it. A few assert facts about
the *committed* log and the shipped tooling, because those are the guarantees that cannot be
recovered once broken: a line that changed, a timestamp argument that reappeared, a migrator
that came back.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import duckdb
import pytest

from src.governance.idea_priority import inspect_idea_priority

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "_data" / "ideas.jsonl"
IDEAS_MD = ROOT / "docs" / "00-working" / "ideas.md"


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


append_idea = _load("append_idea")
generate_ideas_md = _load("generate_ideas_md")


@pytest.fixture
def log(tmp_path: Path) -> Path:
    return tmp_path / "ideas.jsonl"


def _lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --- The writer's refusals -------------------------------------------------------------


def test_status_change_appends_a_line_and_modifies_none(log: Path) -> None:
    append_idea.add("First", "Body", log)
    before = _lines(log)

    append_idea.change_status("000001", "triaged", log=log)
    after = _lines(log)

    assert after[: len(before)] == before, "an existing line was rewritten"
    assert len(after) == len(before) + 1
    assert json.loads(after[-1])["event"] == "status"


def test_illegal_transition_is_refused_and_names_the_attempt(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.change_status("000001", "reviewing", log=log)

    with pytest.raises(append_idea.IdeaError) as excinfo:
        append_idea.change_status("000001", "triaged", log=log)

    assert "reviewing -> triaged" in str(excinfo.value)
    assert _lines(log)[-1:] != [], "the log must be unchanged by a refusal"
    assert len(_lines(log)) == 2


def test_promotion_must_name_what_the_idea_became(log: Path) -> None:
    append_idea.add("First", "Body", log)

    with pytest.raises(append_idea.IdeaError, match="promoted-to"):
        append_idea.change_status("000001", "promoted", log=log)

    append_idea.change_status("000001", "promoted", promoted_to="PLAN-016", log=log)
    assert json.loads(_lines(log)[-1])["promoted_to"] == "PLAN-016"


def test_a_second_discard_after_a_revisit_is_permanent(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.change_status("000001", "discarded", log=log)
    append_idea.revisit("000001", log=log)
    assert append_idea.fold(append_idea.load_events(log))["000001"]["status"] == "reviewing"

    append_idea.change_status("000001", "discarded", log=log)

    with pytest.raises(append_idea.IdeaError, match="permanent"):
        append_idea.revisit("000001", log=log)
    with pytest.raises(append_idea.IdeaError, match="permanent"):
        append_idea.change_status("000001", "reviewing", log=log)


def test_only_a_discarded_idea_can_be_revisited(log: Path) -> None:
    append_idea.add("First", "Body", log)

    with pytest.raises(append_idea.IdeaError, match="not discarded"):
        append_idea.revisit("000001", log=log)


def test_an_invalid_event_never_reaches_the_log(log: Path) -> None:
    with pytest.raises(append_idea.IdeaError, match="refusing to append"):
        append_idea.append({"idea": "1", "event": "created", "at": "whenever"}, log)

    assert not log.exists()


# --- The replay validates history, not just single lines --------------------------------
#
# `fold()` is the single implementation `tools/append_idea.py`, `tools/rebuild_db.py` and
# `src/db/source_validation.py` all consume. Each fixture below is schema-shaped but
# historically impossible, and is built in memory — never written to a log a real caller
# could touch — so a mismatched `from`, an illegal transition, a duplicate creation, an
# unknown idea and a second revisit are all shown to fail the replay itself, independent of
# whichever caller happens to invoke it.


def test_fold_refuses_a_mismatched_from() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "status", "at": "2026-01-01T01:00:00Z",
         "from": "triaged", "to": "reviewing"},
    ]
    with pytest.raises(append_idea.IdeaError, match="from"):
        append_idea.fold(events)


def test_fold_refuses_an_illegal_transition() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "status", "at": "2026-01-01T01:00:00Z",
         "from": "open", "to": "open"},
    ]
    with pytest.raises(append_idea.IdeaError, match="illegal transition"):
        append_idea.fold(events)


def test_fold_refuses_a_duplicate_creation() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "created", "at": "2026-01-01T01:00:00Z",
         "title": "T2", "body": "B2"},
    ]
    with pytest.raises(append_idea.IdeaError, match="already created"):
        append_idea.fold(events)


def test_fold_refuses_an_unknown_idea() -> None:
    events = [
        {"idea": "000002", "event": "status", "at": "2026-01-01T00:00:00Z",
         "from": "open", "to": "triaged"},
    ]
    with pytest.raises(append_idea.IdeaError, match="no created event precedes"):
        append_idea.fold(events)


def test_fold_refuses_a_second_revisit() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "status", "at": "2026-01-01T01:00:00Z",
         "from": "open", "to": "discarded"},
        {"idea": "000001", "event": "revisited", "at": "2026-01-01T02:00:00Z"},
        {"idea": "000001", "event": "status", "at": "2026-01-01T03:00:00Z",
         "from": "reviewing", "to": "discarded"},
        {"idea": "000001", "event": "revisited", "at": "2026-01-01T04:00:00Z"},
    ]
    with pytest.raises(append_idea.IdeaError, match="already revisited"):
        append_idea.fold(events)


# --- Event identity and the amendment fold (phase-idea-07) -----------------------------
#
# `amend` never rewrites a line — it appends a correction naming what it changes by identity,
# never by position, so the pointer survives a rebase or a merge that interleaves two
# branches' appended lines (PLAN-017.03). Title and body are the only amendable fields; both
# are required on every idea, so — unlike a future optional contribution PLAN-017.04 adds —
# neither can be cleared. That boundary is enforced structurally by `field_shape` in the
# schema (`value` has no way to be null), so no separate business-rule test is needed for it.


def test_sibling_amendments_to_title_and_body_both_survive(log: Path) -> None:
    """Two amendments correcting different fields of one event both survive.

    Neither amendment reverts the other — each targets the same `created` event by identity
    and the fold merges the chain rather than keeping only the latest line.
    """
    append_idea.add("Original title", "Original body", log)

    append_idea.amend("000001", title="Corrected title", log=log)
    append_idea.amend("000001", body="Corrected body", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["title"] == "Corrected title"
    assert state["000001"]["body"] == "Corrected body"
    assert len(_lines(log)) == 3, "an amendment appends; it never rewrites the target line"


def test_a_second_amendment_to_the_same_field_wins_without_reverting_the_first(
    log: Path,
) -> None:
    """Two amendments to the same field apply in append order; nothing is lost silently."""
    append_idea.add("Original title", "Body", log)
    append_idea.amend("000001", title="First correction", log=log)
    append_idea.amend("000001", title="Second correction", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["title"] == "Second correction"
    assert state["000001"]["body"] == "Body", "an unrelated amendment left body untouched"


def test_amend_requires_at_least_one_field(log: Path) -> None:
    append_idea.add("Title", "Body", log)
    with pytest.raises(append_idea.IdeaError, match="at least one"):
        append_idea.amend("000001", log=log)
    assert len(_lines(log)) == 1, "a refused amendment must not reach the log"


def test_amend_refuses_an_unknown_idea(log: Path) -> None:
    with pytest.raises(append_idea.IdeaError, match="no idea"):
        append_idea.amend("000001", title="x", log=log)


def test_a_cleared_required_field_is_refused_by_the_schema(log: Path) -> None:
    """Required fields cannot be cleared — enforced structurally, not by a business rule.

    `field_shape.value` has no way to be null, so an amendment attempting to clear title or
    body is refused at the same schema check every event passes through, before it ever
    reaches the fold or the log.
    """
    append_idea.add("Title", "Body", log)
    cleared = {
        "idea": "000001", "event": "amended", "at": "2026-01-01T00:00:00Z", "eid": "clear1",
        "amends": append_idea.identity(json.loads(_lines(log)[0])),
        "title": {"set": True, "value": None},
    }
    with pytest.raises(append_idea.IdeaError, match="refusing to append"):
        append_idea.append(cleared, log)


def test_fold_refuses_two_events_resolving_to_one_identity() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "dup",
         "title": "T", "body": "B"},
        {"idea": "000002", "event": "created", "at": "2026-01-01T01:00:00Z", "eid": "dup",
         "title": "T2", "body": "B2"},
    ]
    with pytest.raises(append_idea.IdeaError, match="same identity"):
        append_idea.fold(events)


def test_fold_refuses_an_amendment_targeting_an_absent_identity() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "a",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T01:00:00Z", "eid": "b",
         "amends": "nowhere", "title": {"set": True, "value": "X"}},
    ]
    with pytest.raises(append_idea.IdeaError, match="not in the log"):
        append_idea.fold(events)


def test_fold_refuses_an_amendment_targeting_a_later_event() -> None:
    """A forward target — including a self-target — is refused, not just a foreign one."""
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "a",
         "title": "T", "body": "B"},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T01:00:00Z", "eid": "b",
         "amends": "c", "title": {"set": True, "value": "X"}},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T02:00:00Z", "eid": "c",
         "amends": "b", "title": {"set": True, "value": "Y"}},
    ]
    with pytest.raises(append_idea.IdeaError, match="earlier in the log"):
        append_idea.fold(events)


def test_fold_refuses_an_amendment_targeting_a_foreign_idea() -> None:
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "a",
         "title": "T", "body": "B"},
        {"idea": "000002", "event": "created", "at": "2026-01-01T01:00:00Z", "eid": "b",
         "title": "T2", "body": "B2"},
        {"idea": "000002", "event": "amended", "at": "2026-01-01T02:00:00Z", "eid": "c",
         "amends": "a", "title": {"set": True, "value": "X"}},
    ]
    with pytest.raises(append_idea.IdeaError, match="same idea"):
        append_idea.fold(events)


def test_a_nested_amendment_chain_resolves() -> None:
    """An amendment is itself correctable: A2 amends A1, which amends the base event."""
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "a",
         "title": "original", "body": "B"},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T01:00:00Z", "eid": "a1",
         "amends": "a", "title": {"set": True, "value": "first correction"}},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T02:00:00Z", "eid": "a2",
         "amends": "a1", "title": {"set": True, "value": "correction of the correction"}},
    ]
    state = append_idea.fold(events)
    assert state["000001"]["title"] == "correction of the correction"


def test_a_branch_merge_interleaving_leaves_every_amends_pointer_resolvable() -> None:
    """Identity, not position, is what a merge that interleaves two ideas' lines cannot break.

    Simulates two worktrees appending to two different ideas and the merge interleaving their
    lines by wall-clock order rather than keeping each idea's own block together. As long as
    each idea's own events stay in their own causal order, the amendment still resolves —
    nothing about it depended on being adjacent to its target or to seq.
    """
    events = [
        {"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z", "eid": "a-created",
         "title": "idea A", "body": "B"},
        {"idea": "000002", "event": "created", "at": "2026-01-01T00:00:01Z", "eid": "b-created",
         "title": "idea B", "body": "B"},
        {"idea": "000001", "event": "status", "at": "2026-01-01T00:00:02Z", "eid": "a-status",
         "from": "open", "to": "triaged"},
        {"idea": "000002", "event": "amended", "at": "2026-01-01T00:00:03Z", "eid": "b-amend",
         "amends": "b-created", "title": {"set": True, "value": "idea B corrected"}},
        {"idea": "000001", "event": "amended", "at": "2026-01-01T00:00:04Z", "eid": "a-amend",
         "amends": "a-created", "body": {"set": True, "value": "B corrected"}},
    ]
    state = append_idea.fold(events)
    assert state["000001"]["title"] == "idea A"
    assert state["000001"]["body"] == "B corrected"
    assert state["000001"]["status"] == "triaged"
    assert state["000002"]["title"] == "idea B corrected"


def test_amend_survives_the_real_cli_and_is_refused_before_append_on_a_bad_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = tmp_path / "ideas.jsonl"
    monkeypatch.setattr(append_idea, "LOG", log)
    assert append_idea.main(["add", "--title", "T", "--body", "B"]) == 0
    assert append_idea.main(["amend", "000001", "--title", "Fixed"]) == 0
    assert append_idea.fold(append_idea.load_events(log))["000001"]["title"] == "Fixed"

    before = _lines(log)
    exit_code = append_idea.main(["amend", "000099", "--title", "x"])
    assert exit_code == 1
    assert _lines(log) == before, "a refused amendment must not reach the log"


def test_a_broken_log_fails_the_rebuild_preflight_before_any_table_drops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The from-check runs in the preflight, before `rebuild_db.py` drops a single table.

    A log this broken must never be allowed to empty the database — `rebuild_db.py:88-90`
    drops every table before inserting, so today an invalid ideas log would take projects
    down with it if nothing caught it first.
    """
    from src.db.source_validation import validate_sources

    fake_root = tmp_path
    (fake_root / "_data").mkdir()
    (fake_root / "schemas").symlink_to(ROOT / "schemas")
    log = fake_root / "_data" / "ideas.jsonl"
    log.write_text(
        "\n".join([
            json.dumps({"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
                        "title": "T", "body": "B"}),
            json.dumps({"idea": "000001", "event": "status", "at": "2026-01-01T01:00:00Z",
                        "from": "triaged", "to": "reviewing"}),
        ])
        + "\n",
        encoding="utf-8",
    )

    errors = validate_sources(fake_root)
    assert any("from" in str(error) for error in errors)


def test_the_rebuild_survives_an_amendment_that_explicitly_inherits(
    tmp_path: Path,
) -> None:
    """`{"set": false}` with no `value` is schema-legal but pointless — a no-op amendment.

    No writer emits this shape (`amend()` only sets fields it is given a replacement for),
    but the schema does not forbid it, so a hand-crafted or future-writer-produced event
    could. `title.get("value")`/`body.get("value")` in `tools/rebuild_db.py` must not raise
    `KeyError` on the missing `value` key the way a bare subscript would.
    """
    rebuild_db = _load("rebuild_db")

    fake_root = tmp_path
    (fake_root / "_data").mkdir()
    (fake_root / "schemas").symlink_to(ROOT / "schemas")
    log = fake_root / "_data" / "ideas.jsonl"
    log.write_text(
        "\n".join([
            json.dumps({"idea": "000001", "event": "created", "at": "2026-01-01T00:00:00Z",
                        "eid": "a", "title": "T", "body": "B"}),
            json.dumps({"idea": "000001", "event": "amended", "at": "2026-01-01T01:00:00Z",
                        "eid": "b", "amends": "a", "title": {"set": False}}),
        ])
        + "\n",
        encoding="utf-8",
    )

    rebuild_db.rebuild(fake_root)

    conn = duckdb.connect(str(fake_root / "data" / "d_system.duckdb"))
    row = conn.execute(
        "SELECT title FROM idea_events WHERE event = 'amended'"
    ).fetchone()
    assert row == (None,), "an explicit inherit carries no value to record"


# --- Annotations and typed relationships (phase-idea-08) --------------------------------
#
# `annotated` events accumulate — an amendment corrects one annotation's own text, never the
# collection — and are permitted on any idea, terminal included, because they extend the
# record rather than the state machine (PLAN-017.04). `linked` events assert a typed,
# one-directional edge whose inverse is derived, never stored; the only legal amendment
# retracts a link's target, and never repoints it.


def test_annotations_accumulate_and_an_amendment_corrects_only_one(log: Path) -> None:
    append_idea.add("Title", "Body", log)
    append_idea.annotate("000001", "repository-owner", "note", "first thought", log=log)
    append_idea.annotate("000001", "repository-owner", "assessment", "looks promising", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    annotations = state["000001"]["annotations"]
    assert [a["text"] for a in annotations] == ["first thought", "looks promising"]

    target_eid = annotations[0]["eid"]
    append_idea.amend_annotation("000001", target_eid, "corrected first thought", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    annotations = state["000001"]["annotations"]
    assert [a["text"] for a in annotations] == ["corrected first thought", "looks promising"]
    assert len(_lines(log)) == 4, "a correction appends; it never rewrites the annotation"


def test_annotations_are_permitted_on_terminal_ideas(log: Path) -> None:
    append_idea.add("Title", "Body", log)
    append_idea.change_status("000001", "discarded", log=log)

    append_idea.annotate("000001", "repository-owner", "note", "why this was right to discard",
                          log=log)

    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["status"] == "discarded", "an annotation never moves status"
    assert len(state["000001"]["annotations"]) == 1


def test_a_non_owner_author_is_restricted_to_finding(log: Path) -> None:
    append_idea.add("Title", "Body", log)

    with pytest.raises(append_idea.IdeaError, match="finding"):
        append_idea.annotate("000001", "agent-blue", "note", "text", log=log)

    append_idea.annotate("000001", "agent-blue", "finding", "text", log=log)
    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["annotations"][0]["author"] == "agent-blue"


def test_an_unknown_annotation_kind_is_refused_by_the_schema(log: Path) -> None:
    append_idea.add("Title", "Body", log)
    with pytest.raises(append_idea.IdeaError, match="refusing to append"):
        append_idea.append({
            "idea": "000001", "event": "annotated", "at": "2026-01-01T00:00:00Z", "eid": "x",
            "author": "repository-owner", "kind": "opinion", "text": "t",
        }, log)


def test_a_link_is_asserted_and_the_inverse_is_derived_not_stored(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)

    event, diagnostics = append_idea.link("000001", "extends", "000002", log=log)
    assert diagnostics == []
    assert json.loads(_lines(log)[-1]) == event

    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["links"][0] == {
        "eid": append_idea.identity(event), "type": "extends", "target": "000002",
        "retracted": False, "at": event["at"],
    }
    assert state["000002"]["links"] == [], "the inverse is derived at render time, never stored"


def test_a_link_never_mutates_its_target_only_retraction_is_legal(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)
    event, _ = append_idea.link("000001", "relates_to", "000002", log=log)
    link_eid = append_idea.identity(event)

    repoint = {
        "idea": "000001", "event": "amended", "at": "2026-01-01T00:00:00Z", "eid": "r",
        "amends": link_eid, "target": {"set": True, "value": "000003"},
    }
    with pytest.raises(append_idea.IdeaError, match="refusing to append"):
        append_idea.append(repoint, log)

    append_idea.retract_link("000001", link_eid, log=log)
    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["links"][0]["retracted"] is True
    assert state["000001"]["links"][0]["target"] is None
    assert len(_lines(log)) == 4, "retraction appends a correction; the link line is untouched"


def test_selective_retraction_leaves_sibling_links_intact(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)
    append_idea.add("Third", "Body three", log)
    kept, _ = append_idea.link("000001", "relates_to", "000002", log=log)
    dropped, _ = append_idea.link("000001", "relates_to", "000003", log=log)

    append_idea.retract_link("000001", append_idea.identity(dropped), log=log)

    state = append_idea.fold(append_idea.load_events(log))
    by_eid = {link["eid"]: link for link in state["000001"]["links"]}
    assert by_eid[append_idea.identity(kept)]["retracted"] is False
    assert by_eid[append_idea.identity(dropped)]["retracted"] is True


def test_link_refuses_a_self_link_and_an_unknown_target(log: Path) -> None:
    append_idea.add("First", "Body", log)
    with pytest.raises(append_idea.IdeaError, match="itself"):
        append_idea.link("000001", "relates_to", "000001", log=log)
    with pytest.raises(append_idea.IdeaError, match="not a known idea"):
        append_idea.link("000001", "relates_to", "000099", log=log)


def test_an_extends_cycle_is_flagged_but_capture_still_succeeds(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)
    append_idea.link("000001", "extends", "000002", log=log)

    _, diagnostics = append_idea.link("000002", "extends", "000001", log=log)

    assert any("cycle" in d for d in diagnostics)
    state = append_idea.fold(append_idea.load_events(log))
    assert state["000002"]["links"][-1]["target"] == "000001", "the capture still succeeds"


def test_a_supersedes_edge_is_flagged_while_its_target_stays_working(log: Path) -> None:
    append_idea.add("Replacement", "Body", log)
    append_idea.add("Old", "Body two", log)

    _, diagnostics = append_idea.link("000001", "supersedes", "000002", log=log)
    assert any("not discarded" in d for d in diagnostics)

    append_idea.change_status("000002", "discarded", log=log)
    state = append_idea.fold(append_idea.load_events(log))
    assert append_idea.link_diagnostics(state).get("000001", []) == [], (
        "discarding the target clears the diagnostic without rejecting the historical link"
    )


def test_promoted_to_accepts_an_array_and_a_legacy_scalar_reads_as_a_singleton(
    log: Path,
) -> None:
    append_idea.add("First", "Body", log)
    append_idea.change_status(
        "000001", "promoted", promoted_to=["PLAN-020", "REQ-004"], log=log
    )
    state = append_idea.fold(append_idea.load_events(log))
    assert state["000001"]["promoted_to"] == ["PLAN-020", "REQ-004"]

    legacy_events = append_idea.load_events(log)
    legacy_events[-1] = dict(legacy_events[-1])
    legacy_events[-1]["promoted_to"] = "PLAN-020"  # the pre-array shape, unwrapped
    state = append_idea.fold(legacy_events)
    assert state["000001"]["promoted_to"] == ["PLAN-020"]


def test_rendered_findings_collapse_and_notes_stay_visible(log: Path) -> None:
    append_idea.add("Title", "Body", log)
    append_idea.annotate("000001", "repository-owner", "note", "an owner note", log=log)
    for i in range(100):
        append_idea.annotate("000001", "agent-blue", "finding", f"finding {i}", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    rendered = generate_ideas_md.render(state)

    assert "an owner note" in rendered, "notes are the owner's voice and stay visible"
    assert "<details>" in rendered and "100 finding(s)" in rendered
    assert rendered.count("finding 0") == 1
    assert generate_ideas_md.render(state) == rendered, "rendering stays deterministic"


def test_rendered_links_show_the_derived_inverse(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)
    append_idea.link("000001", "extends", "000002", log=log)

    state = append_idea.fold(append_idea.load_events(log))
    rendered = generate_ideas_md.render(state)

    first_section = rendered[rendered.index("## 000001"):rendered.index("## 000002")]
    second_section = rendered[rendered.index("## 000002"):]
    assert "extends → `000002`" in first_section
    assert "extended_by ← `000001`" in second_section


# --- The safe write path: `--file` and stdin bypass the shell entirely ------------------


def test_dangerous_prose_survives_the_real_cli_via_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--file` never puts prose in a shell argument, so it reaches the log unchanged.

    Idea 000019 was corrupted by shell command substitution inside a double-quoted `--body`
    — the calling shell evaluated the backticks before this script ever saw the text. This
    drives the actual argparse/main() entry point (real CLI parsing and dispatch, not just
    the underlying function) against an isolated log, with a sentinel file that a shell
    evaluating the embedded commands would create.
    """
    log = tmp_path / "ideas.jsonl"
    sentinel = tmp_path / "sentinel"
    dangerous_title = "Title with `touch " + str(sentinel) + "` inside it"
    dangerous_body = (
        "Body with $(touch " + str(sentinel) + "), \"quotes\", 'quotes',\n"
        "a newline, and non-ASCII Ünïcødé 日本語."
    )
    source = tmp_path / "idea.md"
    source.write_text(f"{dangerous_title}\n{dangerous_body}", encoding="utf-8")

    monkeypatch.setattr(append_idea, "LOG", log)
    exit_code = append_idea.main(["add", "--file", str(source)])

    assert exit_code == 0
    assert not sentinel.exists(), "a sentinel command embedded in prose executed"
    stored = json.loads(_lines(log)[0])
    assert stored["title"] == dangerous_title
    assert stored["body"] == dangerous_body


def test_dangerous_prose_survives_the_real_cli_via_stdin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same safe route, fed from stdin instead of a file."""
    log = tmp_path / "ideas.jsonl"
    dangerous_body = "Body with `backticks`, $(subst), \"quotes\" and a newline.\nSecond line."

    monkeypatch.setattr(append_idea, "LOG", log)
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"A safe title\n{dangerous_body}"))
    exit_code = append_idea.main(["add"])

    assert exit_code == 0
    stored = json.loads(_lines(log)[0])
    assert stored["title"] == "A safe title"
    assert stored["body"] == dangerous_body


def test_file_and_title_together_are_refused(tmp_path: Path) -> None:
    """`--file` replaces `--title`/`--body`; argparse allows the combination, main() must not."""
    source = tmp_path / "idea.md"
    source.write_text("Title\nBody", encoding="utf-8")

    parser_args = append_idea._parser().parse_args(["add", "--file", str(source), "--title", "X"])
    with pytest.raises(append_idea.IdeaError, match="not both"):
        append_idea._read_add_input(parser_args)


def test_the_transition_table_comes_from_the_schema() -> None:
    """Two copies of a rule is one copy and one liability."""
    schema = json.loads((ROOT / "schemas" / "idea.schema.json").read_text(encoding="utf-8"))
    declared = {
        (option["properties"]["from"]["const"], option["properties"]["to"]["const"])
        for branch in schema["allOf"]
        if branch.get("if", {}).get("properties", {}).get("event", {}).get("const") == "status"
        for option in branch["then"]["oneOf"]
    }
    assert append_idea.legal_transitions() == declared
    assert not any(source == "discarded" for source, _ in declared), (
        "discarded must never be a from — the only exit is a revisited event"
    )


# --- The writer offers no way to supply a timestamp ------------------------------------


def test_the_writer_exposes_no_timestamp_argument() -> None:
    """Asserted against the interface, not against behaviour.

    A behavioural test says the guard held on the inputs it happened to try. This says the
    option does not exist, which is the claim the design actually makes: the migration used a
    separate tool that was deleted, so nothing shipped can stamp a chosen time.
    """
    parser = append_idea._parser()
    options: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                options.extend(o for a in sub._actions for o in a.option_strings)
                options.extend(a.dest for a in sub._actions)
        options.extend(action.option_strings)

    forbidden = {"--at", "--time", "--timestamp", "--date", "--when", "at", "timestamp"}
    assert forbidden.isdisjoint(options), f"a timestamp argument reappeared: {sorted(options)}"


def test_the_one_time_migrator_is_gone() -> None:
    """It had one job. Keeping it would leave a second writer able to stamp any time."""
    assert not (ROOT / "tools" / "backfill_ideas.py").exists()


# --- The committed log is append-only --------------------------------------------------


def test_no_committed_line_in_the_log_is_ever_altered() -> None:
    """The committed file must remain a line-for-line prefix of the current one.

    This is the guarantee the whole design rests on, so it is checked against git rather than
    against a recorded digest — a digest has to be updated on every append, and a check that
    is routinely updated is a check that will be updated over a real change.
    """
    committed = subprocess.run(
        ["git", "show", "HEAD:_data/ideas.jsonl"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if committed.returncode != 0:
        pytest.skip("_data/ideas.jsonl is not committed yet")

    was = [line for line in committed.stdout.splitlines() if line.strip()]
    now = _lines(LOG)

    assert now[: len(was)] == was, (
        "a committed line changed. The log is append-only: a status change appends an event, "
        "and nothing already written is ever edited or removed."
    )


def test_every_migrated_idea_kept_its_original_timestamp() -> None:
    """The migration preserved the recorded times rather than restamping them.

    Pinned deliberately. These were observed against a clock as the ideas arrived, so
    restamping would collapse real data into one instant and nothing else in the tree
    would notice.
    """
    expected = {
        "000001": "2026-09-06T14:45:00-04:00", "000002": "2026-09-06T14:47:00-04:00",
        "000003": "2026-09-06T14:49:00-04:00", "000004": "2026-09-06T14:51:00-04:00",
        "000005": "2026-09-06T14:53:00-04:00", "000006": "2026-09-06T14:55:00-04:00",
        "000007": "2026-09-06T14:57:00-04:00", "000008": "2026-09-06T14:59:00-04:00",
        "000009": "2026-09-06T15:01:00-04:00", "000010": "2026-09-06T15:03:00-04:00",
        "000011": "2026-09-06T15:05:00-04:00", "000012": "2026-09-06T15:07:00-04:00",
        "000013": "2026-09-06T15:09:00-04:00",
    }
    created = {
        event["idea"]: event["at"]
        for event in append_idea.load_events(LOG)
        if event["event"] == "created"
    }
    for idea, at in expected.items():
        assert created.get(idea) == at, f"idea {idea} was restamped"


# --- The markdown view is generated ----------------------------------------------------


def test_the_committed_markdown_matches_regenerated_output() -> None:
    rendered = generate_ideas_md.render(
        append_idea.fold(append_idea.load_events(LOG)), generate_ideas_md.load_next_up()
    )
    assert IDEAS_MD.read_text(encoding="utf-8") == rendered, (
        "docs/00-working/ideas.md is generated. Regenerate it with "
        "tools/generate_ideas_md.py; do not edit it by hand."
    )


def test_regenerating_twice_produces_identical_output() -> None:
    state = append_idea.fold(append_idea.load_events(LOG))
    assert generate_ideas_md.render(state) == generate_ideas_md.render(state)


def test_a_hand_edit_to_the_markdown_is_detected() -> None:
    rendered = generate_ideas_md.render(append_idea.fold(append_idea.load_events(LOG)))
    tampered = rendered.replace("## 000001", "## 000001 (edited)", 1)
    assert tampered != rendered
    assert IDEAS_MD.read_text(encoding="utf-8") != tampered


def test_the_view_reflects_a_revisit_and_a_promotion(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.change_status("000001", "discarded", log=log)
    append_idea.revisit("000001", log=log)
    append_idea.add("Second", "Body two", log)
    append_idea.change_status("000002", "promoted", promoted_to="PLAN-016", log=log)

    rendered = generate_ideas_md.render(append_idea.fold(append_idea.load_events(log)))

    assert "revisited 1×" in rendered
    assert "became PLAN-016" in rendered


# --- The projection ---------------------------------------------------------------------


@pytest.fixture
def projected() -> duckdb.DuckDBPyConnection:
    """The committed log, loaded into an in-memory database using the shipped DDL."""
    ddl = (ROOT / "sql" / "001_schema.sql").read_text(encoding="utf-8")
    clean = "\n".join(
        line for line in ddl.splitlines() if not line.strip().startswith("--")
    )
    conn = duckdb.connect(":memory:")
    for statement in (s.strip() for s in clean.split(";") if s.strip()):
        conn.execute(statement)

    counters: dict[str, int] = {}
    for event in append_idea.load_events(LOG):
        idea = event["idea"]
        counters[idea] = counters.get(idea, 0) + 1
        promoted_to = event.get("promoted_to")
        conn.execute(
            "INSERT INTO idea_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                idea, append_idea.identity(event), counters[idea], event["event"], event["at"],
                event.get("title"), event.get("body"),
                event.get("from"), event.get("to"),
                [promoted_to] if isinstance(promoted_to, str) else promoted_to,
                event.get("amends"),
                event.get("author"), event.get("kind"), event.get("text"),
                event.get("type"), event.get("target"),
            ],
        )
    return conn


SYNTHETIC_TRANSITIONS_IDEA = "999999"
"""A fabricated idea id, never present in `_data/ideas.jsonl`.

The real log keeps growing — the idea-triage agent (`phase-idea-02`) appends a `finding`
annotation plus a `status` transition to whichever idea it processes, so no real idea's event
count is stable across sessions. A fixture id shared with any real idea would silently
collide with whatever that idea has accumulated by the time a test runs. Using an id no real
idea will ever have makes the fixture self-contained instead.
"""


@pytest.fixture
def projected_with_transitions(
    projected: duckdb.DuckDBPyConnection,
) -> duckdb.DuckDBPyConnection:
    """`projected`, plus an entirely synthetic idea with out-of-instant-order transitions.

    Never written to `_data/ideas.jsonl` and never sharing an id with a real idea (see
    `SYNTHETIC_TRANSITIONS_IDEA`) — self-contained, so accumulating real events on any real
    idea between test runs cannot affect it. `seq` here is assigned in *file* order but
    deliberately does not match *time* order — 16:00-04:00 (seq 2) is a real instant 30
    minutes after 14:30-05:00 (seq 3) — which is exactly what a git merge interleaving two
    worktrees' appended lines can produce. `seq` is a per-idea append ordinal, not a clock;
    nothing about the log format guarantees the two agree.
    """
    idea = SYNTHETIC_TRANSITIONS_IDEA
    synthetic = [
        (
            idea, "synthetic-0", 1, "created", "2026-09-06T14:45:00-04:00",
            "Synthetic idea for seq-vs-time ordering tests", "Body", None, None, None,
        ),
        (
            idea, "synthetic-1", 2, "status", "2026-09-06T16:00:00-04:00",
            None, None, "open", "triaged", None,
        ),
        (
            idea, "synthetic-2", 3, "status", "2026-09-06T14:30:00-05:00",
            None, None, "triaged", "reviewing", None,
        ),
    ]
    for row_idea, ident, seq, event, at, title, body, frm, to, promoted in synthetic:
        projected.execute(
            "INSERT INTO idea_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                row_idea, ident, seq, event, at, title, body, frm, to, promoted, None,
                None, None, None, None, None,
            ],
        )
    return projected


def test_time_in_each_state_is_queryable_without_parsing_markdown(
    projected_with_transitions: duckdb.DuckDBPyConnection,
) -> None:
    """Duration-in-state must never go negative, including across a real transition.

    The window orders by `occurred_at`, not `seq`: `seq` is a per-idea append ordinal, not a
    timestamp, and nothing about the log format guarantees the two agree — a branch merge
    can interleave two worktrees' appended lines in an order their real instants disagree
    with. Ordering the window by the timestamp itself is correct regardless.
    """
    rows = projected_with_transitions.execute(
        """
        WITH timeline AS (
            SELECT idea,
                   CASE WHEN event = 'created' THEN 'open'
                        WHEN event = 'revisited' THEN 'reviewing'
                        ELSE status_to END AS state,
                   occurred_at,
                   LEAD(occurred_at) OVER (PARTITION BY idea ORDER BY occurred_at) AS next_at
            FROM idea_events
        )
        SELECT state, count(*),
               sum(date_diff('second', occurred_at, coalesce(next_at, now())))
        FROM timeline GROUP BY state
        """
    ).fetchall()

    assert rows, "no states projected"
    assert all(seconds is not None and seconds >= 0 for _, _, seconds in rows)

    # Ordering the same window by `seq` instead reproduces a real negative duration: seq 2
    # (16:00-04:00) precedes seq 3 (14:30-05:00) in the file, but seq 3 is the earlier
    # instant, so `seq`-ordered LEAD looks backward in time for the 'triaged' row.
    by_seq = projected_with_transitions.execute(
        f"""
        WITH timeline AS (
            SELECT status_to, occurred_at,
                   LEAD(occurred_at) OVER (PARTITION BY idea ORDER BY seq) AS next_at
            FROM idea_events WHERE idea = '{SYNTHETIC_TRANSITIONS_IDEA}'
        )
        SELECT date_diff('second', occurred_at, next_at) FROM timeline WHERE status_to = 'triaged'
        """
    ).fetchone()
    assert by_seq == (-1800,), "fixture no longer reproduces the seq-ordering defect"


def test_timestamp_columns_can_actually_be_read_into_python(
    projected: duckdb.DuckDBPyConnection,
) -> None:
    """Fetch a timestamp, do not merely aggregate over one.

    DuckDB returns TIMESTAMP WITH TIME ZONE through pytz, so without that dependency every
    query returning occurred_at or created raises instead of yielding a row — while count(),
    sum() and date_diff() over the same column keep working. The first tests written here
    only aggregated, so they passed against tables no caller could read. This asserts the
    row comes back.
    """
    row = projected.execute(
        "SELECT idea, occurred_at FROM idea_events ORDER BY occurred_at LIMIT 1"
    ).fetchone()

    assert row is not None
    idea, occurred_at = row
    assert idea == "000001"
    assert isinstance(occurred_at, dt.datetime)
    assert occurred_at.tzinfo is not None, "an instant without an offset cannot be ordered"
    assert occurred_at == dt.datetime.fromisoformat("2026-09-06T14:45:00-04:00")


def test_mixed_offsets_compare_as_the_same_instant(
    projected_with_transitions: duckdb.DuckDBPyConnection,
) -> None:
    """A later offset does not mean a later instant, and ordering must follow the instant.

    The synthetic idea's seq 2 (-04:00) and seq 3 (-05:00) are deliberately out of instant
    order to prove the point: `seq` disagreeing with real time is possible, so anything
    computing a duration must order by `occurred_at`, never by `seq`.
    """
    by_seq = [
        row[0]
        for row in projected_with_transitions.execute(
            f"SELECT occurred_at FROM idea_events WHERE idea = '{SYNTHETIC_TRANSITIONS_IDEA}' "
            "ORDER BY seq"
        ).fetchall()
    ]
    assert by_seq != sorted(by_seq), "fixture no longer mixes offsets out of instant order"

    by_instant = [
        row[0]
        for row in projected_with_transitions.execute(
            f"SELECT occurred_at FROM idea_events WHERE idea = '{SYNTHETIC_TRANSITIONS_IDEA}' "
            "ORDER BY occurred_at"
        ).fetchall()
    ]
    assert by_instant == sorted(by_instant)

    same = projected_with_transitions.execute(
        "SELECT TIMESTAMPTZ '2026-09-06 15:09:00-04:00' = TIMESTAMPTZ '2026-09-06 14:09:00-05:00'"
    ).fetchone()
    assert same is not None and same[0]


def test_any_past_moment_is_reconstructible(
    projected: duckdb.DuckDBPyConnection,
) -> None:
    """The reason idea_events is retained in full and never folded away."""
    at_fifteen_hundred = projected.execute(
        """
        SELECT count(*) FROM idea_events
        WHERE event = 'created' AND occurred_at <= TIMESTAMPTZ '2026-09-06 15:00:00-04:00'
        """
    ).fetchone()
    assert at_fifteen_hundred is not None
    assert at_fifteen_hundred[0] == 8, "eight ideas existed at that instant"


# --- The shipped tooling ----------------------------------------------------------------


def test_the_custom_tool_wraps_the_writer_without_duplicating_it() -> None:
    wrapper = ROOT / ".claude" / "commands" / "idea.md"
    assert wrapper.exists()
    text = wrapper.read_text(encoding="utf-8")
    assert "tools/append_idea.py" in text, "the wrapper must invoke the sanctioned writer"
    assert "ideas.jsonl" in text


def test_adr_010_records_that_the_storage_moved() -> None:
    text = (ROOT / "docs" / "04-decisions" / "ADR-010-idea-staging.md").read_text(
        encoding="utf-8"
    )
    assert "_data/ideas.jsonl" in text
    assert "PLAN-016" in text
    assert "generated" in text


# --- The priority queue (PLAN-019) -------------------------------------------------------


def test_render_lists_the_priority_queue_first_in_order(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.add("Second", "Body two", log)
    state = append_idea.fold(append_idea.load_events(log))

    rendered = generate_ideas_md.render(state, ["000002", "000001"])

    queue_pos = rendered.index("## Priority queue")
    first_entry = rendered.index("`000002` — Second")
    second_entry = rendered.index("`000001` — First")
    first_heading = rendered.index("## 000001")
    assert queue_pos < first_entry < second_entry < first_heading


def test_render_with_no_priority_queue_omits_the_section(log: Path) -> None:
    append_idea.add("First", "Body", log)
    state = append_idea.fold(append_idea.load_events(log))

    assert "## Priority queue" not in generate_ideas_md.render(state, [])
    assert "## Priority queue" not in generate_ideas_md.render(state)


def test_inspect_idea_priority_accepts_open_and_triaged_ideas() -> None:
    ideas = {
        "000001": {"status": "open"},
        "000002": {"status": "triaged"},
    }
    catalog = {"updated": "2026-01-01", "next_up": ["000002", "000001"]}
    assert inspect_idea_priority(catalog, ideas, dt.date(2026, 1, 2)) == []


def test_inspect_idea_priority_rejects_unknown_and_terminal_ideas() -> None:
    ideas = {"000001": {"status": "promoted"}}
    catalog = {"updated": "2026-01-01", "next_up": ["000001", "000002"]}

    errors = inspect_idea_priority(catalog, ideas, dt.date(2026, 1, 2))

    assert any("000001 is promoted" in error for error in errors)
    assert any("unknown idea 000002" in error for error in errors)


def test_inspect_idea_priority_rejects_a_future_updated_date() -> None:
    catalog = {"updated": "2026-01-05", "next_up": []}

    errors = inspect_idea_priority(catalog, {}, dt.date(2026, 1, 1))

    assert any("in the future" in error for error in errors)


def test_ideas_priority_yaml_is_governance_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.governance"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ideas-priority" not in result.stdout
