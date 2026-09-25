"""The idea writer and the fold: every refusal holds against a temporary log.

The log is append-only and permanent, so each test builds its own log under ``tmp_path`` and
exercises the writer's refusals, the fold's history rules, amendments, annotations, links,
classification and closing pointers against it. Nothing here reads a file outside the plugin.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import idea
import ideas
import paths
import pytest
import yaml  # type: ignore[import-untyped]
from conftest import PLUGIN_ROOT
from ideas import IdeaError, fold, identity, link_diagnostics, load_events

EPOCH = dt.datetime(2030, 1, 1, tzinfo=dt.UTC)


def iid(n: int) -> str:
    """An idea id, built rather than written, so no six-digit literal appears in the suite."""
    return f"{n:06d}"


def at(hours: int = 0, seconds: int = 0) -> str:
    """A fixed fixture instant, built rather than written as a calendar date."""
    return (EPOCH + dt.timedelta(hours=hours, seconds=seconds)).isoformat()


ONE, TWO, THREE, NINETY_NINE = iid(1), iid(2), iid(3), iid(99)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No configured value from the calling shell reaches a test."""
    for name in list(os.environ):
        if name.startswith(("IDEA_REALIZATION_", "CLAUDE_PLUGIN_OPTION_", "CLAUDE_PROJECT_DIR")):
            monkeypatch.delenv(name)


@pytest.fixture
def config(tmp_path: Path) -> paths.Config:
    return paths.resolve({"root": str(tmp_path)}, env={})


@pytest.fixture
def log(config: paths.Config) -> Path:
    return config.path("ideas_path")


def lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def state_of(log: Path) -> dict[str, dict[str, Any]]:
    return fold(load_events(log))


def cli(root: Path, *args: str) -> int:
    return idea.main([*args, "--root", str(root)])


# --- The writer's refusals -------------------------------------------------------------------


def test_status_change_appends_a_line_and_modifies_none(log: Path) -> None:
    """A status change appends one line; no existing line is rewritten."""
    idea.add("First", "Body", log)
    before = lines(log)

    idea.change_status(ONE, "triaged", log=log)
    after = lines(log)

    assert after[: len(before)] == before, "an existing line was rewritten"
    assert len(after) == len(before) + 1
    assert json.loads(after[-1])["event"] == "status"


def test_illegal_transition_is_refused_and_names_the_attempt(log: Path) -> None:
    """An illegal move names the attempted pair and leaves the log unchanged."""
    idea.add("First", "Body", log)
    idea.change_status(ONE, "reviewing", log=log)

    with pytest.raises(IdeaError) as excinfo:
        idea.change_status(ONE, "triaged", log=log)

    assert "reviewing -> triaged" in str(excinfo.value)
    assert len(lines(log)) == 2


def test_promotion_must_name_what_the_idea_became(log: Path) -> None:
    """open -> promoted without promoted_to is refused; with it, the target is recorded."""
    idea.add("First", "Body", log)

    with pytest.raises(IdeaError, match="promoted-to"):
        idea.change_status(ONE, "promoted", log=log)
    assert len(lines(log)) == 1, "a refused promotion must not reach the log"

    idea.change_status(ONE, "promoted", promoted_to=["DOC-016"], log=log)
    assert json.loads(lines(log)[-1])["promoted_to"] == ["DOC-016"]


def test_promotion_without_promoted_to_is_refused_by_the_cli(tmp_path: Path, log: Path,
                                                            capsys: pytest.CaptureFixture[str]
                                                            ) -> None:
    """The command line refuses the same promotion and appends nothing."""
    assert cli(tmp_path, "add", "--title", "T", "--body", "B") == 0
    before = lines(log)

    assert cli(tmp_path, "status", ONE, "promoted") == 1

    assert "promoted-to" in capsys.readouterr().err
    assert lines(log) == before
    assert cli(tmp_path, "status", ONE, "promoted", "--promoted-to", "DOC-016") == 0
    assert state_of(log)[ONE]["promoted_to"] == ["DOC-016"]


def test_a_second_discard_after_a_revisit_is_permanent(log: Path) -> None:
    """Once revisited and discarded again, the idea can be neither revisited nor moved."""
    idea.add("First", "Body", log)
    idea.change_status(ONE, "discarded", log=log)
    idea.revisit(ONE, log=log)
    assert state_of(log)[ONE]["status"] == "reviewing"

    idea.change_status(ONE, "discarded", log=log)
    before = lines(log)

    with pytest.raises(IdeaError, match="permanent"):
        idea.revisit(ONE, log=log)
    with pytest.raises(IdeaError, match="permanent"):
        idea.change_status(ONE, "reviewing", log=log)
    with pytest.raises(IdeaError, match="permanent"):
        idea.change_status(ONE, "discarded", log=log)
    assert lines(log) == before


def test_only_a_discarded_idea_can_be_revisited(log: Path) -> None:
    """A revisit reopens a discarded idea and nothing else."""
    idea.add("First", "Body", log)

    with pytest.raises(IdeaError, match="not discarded"):
        idea.revisit(ONE, log=log)


def test_an_invalid_event_never_reaches_the_log(log: Path) -> None:
    """Schema validation runs before the append, so a bad line is never written."""
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.append({"idea": "1", "event": "created", "at": "whenever"}, log)

    assert not log.exists()


# --- The replay validates history, not just single lines ------------------------------------
#
# Each fixture below is schema-shaped but historically impossible, built in memory and never
# written to a log, so each rule is shown to fail the replay itself, whichever caller runs it.


def test_fold_refuses_a_mismatched_from() -> None:
    """A status event's `from` must equal the status the replay has reached."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "title": "T", "body": "B"},
        {"idea": ONE, "event": "status", "at": at(1), "from": "triaged", "to": "reviewing"},
    ]
    with pytest.raises(IdeaError, match="from"):
        fold(events)


def test_fold_refuses_an_illegal_transition() -> None:
    """A pair outside the schema's transition table is refused."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "title": "T", "body": "B"},
        {"idea": ONE, "event": "status", "at": at(1), "from": "open", "to": "open"},
    ]
    with pytest.raises(IdeaError, match="illegal transition"):
        fold(events)


def test_fold_refuses_a_duplicate_creation() -> None:
    """An idea is created once."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "title": "T", "body": "B"},
        {"idea": ONE, "event": "created", "at": at(1), "title": "T2", "body": "B2"},
    ]
    with pytest.raises(IdeaError, match="already created"):
        fold(events)


def test_fold_refuses_an_unknown_idea() -> None:
    """Every event follows its idea's creation."""
    events = [{"idea": TWO, "event": "status", "at": at(0), "from": "open", "to": "triaged"}]
    with pytest.raises(IdeaError, match="no created event precedes"):
        fold(events)


def test_fold_refuses_a_second_revisit() -> None:
    """A discarded idea is revisited at most once."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "title": "T", "body": "B"},
        {"idea": ONE, "event": "status", "at": at(1), "from": "open", "to": "discarded"},
        {"idea": ONE, "event": "revisited", "at": at(2)},
        {"idea": ONE, "event": "status", "at": at(3), "from": "reviewing", "to": "discarded"},
        {"idea": ONE, "event": "revisited", "at": at(4)},
    ]
    with pytest.raises(IdeaError, match="already revisited"):
        fold(events)


def test_a_broken_log_is_reported_by_the_check(config: paths.Config, log: Path) -> None:
    """A log whose history the fold refuses is reported by the ideas check, not accepted."""
    from checks import ideas as ideas_check

    log.parent.mkdir(parents=True)
    log.write_text(
        json.dumps({"idea": ONE, "event": "created", "at": at(0), "title": "T", "body": "B"})
        + "\n"
        + json.dumps({"idea": ONE, "event": "status", "at": at(1), "from": "triaged",
                      "to": "reviewing"})
        + "\n",
        encoding="utf-8",
    )
    errors = ideas_check.check(config)
    assert any("from" in error for error in errors)


# --- Event identity and the amendment fold --------------------------------------------------
#
# `amend` never rewrites a line; it appends a correction naming its target by identity, never
# by position, so the pointer survives a rebase or a merge that interleaves two branches'
# appended lines. Title and body are required on every idea, so neither can be cleared; the
# schema's `field_shape` enforces that structurally.


def test_sibling_amendments_to_title_and_body_both_survive(log: Path) -> None:
    """Two amendments correcting different fields of one event both survive."""
    idea.add("Original title", "Original body", log)

    idea.amend(ONE, title="Corrected title", log=log)
    idea.amend(ONE, body="Corrected body", log=log)

    state = state_of(log)
    assert state[ONE]["title"] == "Corrected title"
    assert state[ONE]["body"] == "Corrected body"
    assert len(lines(log)) == 3, "an amendment appends; it never rewrites the target line"


def test_a_second_amendment_to_the_same_field_wins_without_reverting_the_first(
    log: Path,
) -> None:
    """Two amendments to the same field apply in append order; nothing is lost silently."""
    idea.add("Original title", "Body", log)
    idea.amend(ONE, title="First correction", log=log)
    idea.amend(ONE, title="Second correction", log=log)

    state = state_of(log)
    assert state[ONE]["title"] == "Second correction"
    assert state[ONE]["body"] == "Body", "an unrelated amendment left body untouched"


def test_amend_requires_at_least_one_field(log: Path) -> None:
    """An amendment that corrects nothing is refused before the append."""
    idea.add("Title", "Body", log)
    with pytest.raises(IdeaError, match="at least one"):
        idea.amend(ONE, log=log)
    assert len(lines(log)) == 1, "a refused amendment must not reach the log"


def test_amend_refuses_an_unknown_idea(log: Path) -> None:
    """Only an idea in the log can be amended."""
    with pytest.raises(IdeaError, match="no idea"):
        idea.amend(ONE, title="x", log=log)


def test_a_cleared_required_field_is_refused_by_the_schema(log: Path) -> None:
    """Required fields cannot be cleared: `field_shape.value` has no way to be null."""
    idea.add("Title", "Body", log)
    cleared = {
        "idea": ONE, "event": "amended", "at": at(0), "eid": "clear1",
        "amends": identity(json.loads(lines(log)[0])),
        "title": {"set": True, "value": None},
    }
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.append(cleared, log)


def test_fold_refuses_two_events_resolving_to_one_identity() -> None:
    """Two events with one identity make an `amends` pointer ambiguous, so the fold fails."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "dup", "title": "T", "body": "B"},
        {"idea": TWO, "event": "created", "at": at(1), "eid": "dup", "title": "T2",
         "body": "B2"},
    ]
    with pytest.raises(IdeaError, match="same identity"):
        fold(events)


def test_fold_refuses_an_amendment_targeting_an_absent_identity() -> None:
    """An amendment must name an event that is in the log."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "a", "title": "T", "body": "B"},
        {"idea": ONE, "event": "amended", "at": at(1), "eid": "b", "amends": "nowhere",
         "title": {"set": True, "value": "X"}},
    ]
    with pytest.raises(IdeaError, match="not in the log"):
        fold(events)


def test_fold_refuses_an_amendment_targeting_a_later_event() -> None:
    """A forward target, including a self-target, is refused, not just a foreign one."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "a", "title": "T", "body": "B"},
        {"idea": ONE, "event": "amended", "at": at(1), "eid": "b", "amends": "c",
         "title": {"set": True, "value": "X"}},
        {"idea": ONE, "event": "amended", "at": at(2), "eid": "c", "amends": "b",
         "title": {"set": True, "value": "Y"}},
    ]
    with pytest.raises(IdeaError, match="earlier in the log"):
        fold(events)


def test_fold_refuses_an_amendment_targeting_a_foreign_idea() -> None:
    """An amendment may only correct an event on its own idea."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "a", "title": "T", "body": "B"},
        {"idea": TWO, "event": "created", "at": at(1), "eid": "b", "title": "T2", "body": "B2"},
        {"idea": TWO, "event": "amended", "at": at(2), "eid": "c", "amends": "a",
         "title": {"set": True, "value": "X"}},
    ]
    with pytest.raises(IdeaError, match="same idea"):
        fold(events)


def test_a_nested_amendment_chain_resolves() -> None:
    """An amendment is itself correctable: A2 amends A1, which amends the base event."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "a", "title": "original",
         "body": "B"},
        {"idea": ONE, "event": "amended", "at": at(1), "eid": "a1", "amends": "a",
         "title": {"set": True, "value": "first correction"}},
        {"idea": ONE, "event": "amended", "at": at(2), "eid": "a2", "amends": "a1",
         "title": {"set": True, "value": "correction of the correction"}},
    ]
    assert fold(events)[ONE]["title"] == "correction of the correction"


def test_a_branch_merge_interleaving_leaves_every_amends_pointer_resolvable() -> None:
    """Identity, not position, is what a merge interleaving two ideas' lines cannot break."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0, 0), "eid": "a-created",
         "title": "idea A", "body": "B"},
        {"idea": TWO, "event": "created", "at": at(0, 1), "eid": "b-created",
         "title": "idea B", "body": "B"},
        {"idea": ONE, "event": "status", "at": at(0, 2), "eid": "a-status",
         "from": "open", "to": "triaged"},
        {"idea": TWO, "event": "amended", "at": at(0, 3), "eid": "b-amend",
         "amends": "b-created", "title": {"set": True, "value": "idea B corrected"}},
        {"idea": ONE, "event": "amended", "at": at(0, 4), "eid": "a-amend",
         "amends": "a-created", "body": {"set": True, "value": "B corrected"}},
    ]
    state = fold(events)
    assert state[ONE]["title"] == "idea A"
    assert state[ONE]["body"] == "B corrected"
    assert state[ONE]["status"] == "triaged"
    assert state[TWO]["title"] == "idea B corrected"


def test_an_amendment_that_explicitly_inherits_changes_nothing() -> None:
    """`{"set": false}` is schema-legal but a no-op; the fold must not fail on its missing value."""
    events = [
        {"idea": ONE, "event": "created", "at": at(0), "eid": "a", "title": "T", "body": "B"},
        {"idea": ONE, "event": "amended", "at": at(1), "eid": "b", "amends": "a",
         "title": {"set": False}},
    ]
    idea.validate(events[1])
    assert fold(events)[ONE]["title"] == "T"


def test_amend_survives_the_real_cli_and_is_refused_before_append_on_a_bad_target(
    tmp_path: Path, log: Path
) -> None:
    """The command line amends by identity and refuses an unknown idea without appending."""
    assert cli(tmp_path, "add", "--title", "T", "--body", "B") == 0
    assert cli(tmp_path, "amend", ONE, "--title", "Fixed") == 0
    assert state_of(log)[ONE]["title"] == "Fixed"

    before = lines(log)
    assert cli(tmp_path, "amend", NINETY_NINE, "--title", "x") == 1
    assert lines(log) == before, "a refused amendment must not reach the log"


# --- Annotations and typed relationships ----------------------------------------------------
#
# Annotations accumulate; an amendment corrects one annotation's own text, never the
# collection, and they are permitted on any idea, terminal included. Links assert a typed,
# one-directional edge whose inverse is derived, never stored; the only legal amendment
# retracts a link's target and never repoints it.


def test_annotations_accumulate_and_an_amendment_corrects_only_one(log: Path) -> None:
    """Correcting one annotation leaves its siblings untouched."""
    idea.add("Title", "Body", log)
    idea.annotate(ONE, ideas.OWNER, "note", "first thought", log=log)
    idea.annotate(ONE, ideas.OWNER, "assessment", "looks promising", log=log)

    annotations = state_of(log)[ONE]["annotations"]
    assert [a["text"] for a in annotations] == ["first thought", "looks promising"]

    idea.amend_annotation(ONE, annotations[0]["eid"], "corrected first thought", log=log)

    annotations = state_of(log)[ONE]["annotations"]
    assert [a["text"] for a in annotations] == ["corrected first thought", "looks promising"]
    assert len(lines(log)) == 4, "a correction appends; it never rewrites the annotation"


def test_amend_annotation_refuses_an_unknown_annotation(log: Path) -> None:
    """Only an annotation on the named idea can be corrected."""
    idea.add("Title", "Body", log)
    with pytest.raises(IdeaError, match="no annotation"):
        idea.amend_annotation(ONE, "missing", "text", log=log)


def test_annotations_are_permitted_on_terminal_ideas(log: Path) -> None:
    """An annotation extends the record, not the state machine."""
    idea.add("Title", "Body", log)
    idea.change_status(ONE, "discarded", log=log)

    idea.annotate(ONE, ideas.OWNER, "note", "why this was right to discard", log=log)

    state = state_of(log)
    assert state[ONE]["status"] == "discarded", "an annotation never moves status"
    assert len(state[ONE]["annotations"]) == 1


def test_a_non_owner_author_is_restricted_to_finding(log: Path) -> None:
    """An agent writes findings only, so the owner's voice stays unambiguous."""
    idea.add("Title", "Body", log)

    with pytest.raises(IdeaError, match="finding"):
        idea.annotate(ONE, "agent-blue", "note", "text", log=log)

    idea.annotate(ONE, "agent-blue", "finding", "text", log=log)
    assert state_of(log)[ONE]["annotations"][0]["author"] == "agent-blue"


def test_an_unknown_annotation_kind_is_refused_by_the_schema(log: Path) -> None:
    """An unknown kind fails validation rather than being accepted as free text."""
    idea.add("Title", "Body", log)
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.append({
            "idea": ONE, "event": "annotated", "at": at(0), "eid": "x",
            "author": ideas.OWNER, "kind": "opinion", "text": "t",
        }, log)


def test_a_link_is_asserted_and_the_inverse_is_derived_not_stored(log: Path) -> None:
    """A link is stored once, on the idea asserting it."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)

    event, diagnostics = idea.link(ONE, "extends", TWO, log=log)
    assert diagnostics == []
    assert json.loads(lines(log)[-1]) == event

    state = state_of(log)
    assert state[ONE]["links"][0] == {
        "eid": identity(event), "type": "extends", "target": TWO,
        "retracted": False, "at": event["at"],
    }
    assert state[TWO]["links"] == [], "the inverse is derived at render time, never stored"


def test_a_link_never_mutates_its_target_only_retraction_is_legal(log: Path) -> None:
    """No shape repoints a link; retraction clears it and appends a correction."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    event, _ = idea.link(ONE, "relates_to", TWO, log=log)
    link_eid = identity(event)

    repoint = {
        "idea": ONE, "event": "amended", "at": at(0), "eid": "r",
        "amends": link_eid, "target": {"set": True, "value": THREE},
    }
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.append(repoint, log)

    idea.retract_link(ONE, link_eid, log=log)
    link = state_of(log)[ONE]["links"][0]
    assert link["retracted"] is True
    assert link["target"] is None
    assert len(lines(log)) == 4, "retraction appends a correction; the link line is untouched"


def test_selective_retraction_leaves_sibling_links_intact(log: Path) -> None:
    """Retracting one link by identity leaves the others live."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    idea.add("Third", "Body three", log)
    kept, _ = idea.link(ONE, "relates_to", TWO, log=log)
    dropped, _ = idea.link(ONE, "relates_to", THREE, log=log)

    idea.retract_link(ONE, identity(dropped), log=log)

    by_eid = {link["eid"]: link for link in state_of(log)[ONE]["links"]}
    assert by_eid[identity(kept)]["retracted"] is False
    assert by_eid[identity(dropped)]["retracted"] is True


def test_retract_link_refuses_an_unknown_link(log: Path) -> None:
    """Only a link on the named idea can be retracted."""
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="no link"):
        idea.retract_link(ONE, "missing", log=log)


def test_link_refuses_a_self_link_and_an_unknown_target(log: Path) -> None:
    """A link points at another idea that exists."""
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="itself"):
        idea.link(ONE, "relates_to", ONE, log=log)
    with pytest.raises(IdeaError, match="not a known idea"):
        idea.link(ONE, "relates_to", NINETY_NINE, log=log)


def test_an_extends_cycle_is_flagged_but_capture_still_succeeds(log: Path) -> None:
    """A cycle is a diagnostic, never a refusal: capture always wins."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    idea.link(ONE, "extends", TWO, log=log)

    _, diagnostics = idea.link(TWO, "extends", ONE, log=log)

    assert any("cycle" in d for d in diagnostics)
    assert state_of(log)[TWO]["links"][-1]["target"] == ONE, "the capture still succeeds"


def test_a_supersedes_edge_is_flagged_while_its_target_stays_working(log: Path) -> None:
    """Superseding a live idea is flagged until the target is discarded."""
    idea.add("Replacement", "Body", log)
    idea.add("Old", "Body two", log)

    _, diagnostics = idea.link(ONE, "supersedes", TWO, log=log)
    assert any("not discarded" in d for d in diagnostics)

    idea.change_status(TWO, "discarded", log=log)
    assert link_diagnostics(state_of(log)).get(ONE, []) == [], (
        "discarding the target clears the diagnostic without rejecting the historical link"
    )


def test_promoted_to_accepts_an_array_and_a_legacy_scalar_reads_as_a_singleton(
    log: Path,
) -> None:
    """`promoted_to` folds to a list whether written as a list or a scalar."""
    idea.add("First", "Body", log)
    idea.change_status(ONE, "promoted", promoted_to=["DOC-020", "DOC-004"], log=log)
    assert state_of(log)[ONE]["promoted_to"] == ["DOC-020", "DOC-004"]

    legacy_events = load_events(log)
    legacy_events[-1] = dict(legacy_events[-1])
    legacy_events[-1]["promoted_to"] = "DOC-020"
    assert fold(legacy_events)[ONE]["promoted_to"] == ["DOC-020"]


# --- Links to documents ---------------------------------------------------------------------


def write_document(config: paths.Config, code: str, name: str = "doc.md") -> None:
    docs = config.path("docs_root")
    docs.mkdir(parents=True, exist_ok=True)
    (docs / name).write_text(f"---\ncode: {code}\n---\n\n# A document\n", encoding="utf-8")


def test_a_document_link_needs_an_existing_code(config: paths.Config, log: Path) -> None:
    """A link may point at a document code that a document under the root declares."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)

    with pytest.raises(IdeaError, match="not a governed document code"):
        idea.link(ONE, "relates_to", None, log=log, target_code="DOC-002", config=config)

    event, _ = idea.link(ONE, "relates_to", None, log=log, target_code="DOC-001",
                         config=config)
    link = state_of(log)[ONE]["links"][0]
    assert link["target"] is None
    assert link["target_code"] == "DOC-001"
    assert link["retracted"] is False
    assert link["eid"] == identity(event)


def test_only_extends_and_relates_to_may_point_at_a_document(config: paths.Config,
                                                            log: Path) -> None:
    """A supersedes or component_of edge points at an idea, never a document."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="cannot point at a document"):
        idea.link(ONE, "supersedes", None, log=log, target_code="DOC-001", config=config)


def test_a_link_names_exactly_one_target(config: paths.Config, log: Path) -> None:
    """An idea target and a document target are exclusive."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)
    idea.add("Second", "Body", log)
    with pytest.raises(IdeaError, match="exactly one"):
        idea.link(ONE, "relates_to", TWO, log=log, target_code="DOC-001", config=config)
    with pytest.raises(IdeaError, match="exactly one"):
        idea.link(ONE, "relates_to", None, log=log, config=config)


def test_a_document_link_is_retracted_by_clearing_its_code(config: paths.Config,
                                                           log: Path) -> None:
    """Retracting a document link clears `target_code`, and the fold marks it retracted."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)
    event, _ = idea.link(ONE, "extends", None, log=log, target_code="DOC-001", config=config)

    idea.retract_link(ONE, identity(event), log=log)

    assert json.loads(lines(log)[-1])["target_code"] == {"set": True, "value": None}
    link = state_of(log)[ONE]["links"][0]
    assert link["retracted"] is True
    assert link["target_code"] is None


def test_document_codes_skip_exempt_files_and_files_without_front_matter(
    config: paths.Config,
) -> None:
    """Only front matter declares a code; an exempt file is not read."""
    write_document(config, "DOC-001", "one.md")
    write_document(config, "DOC-002", "exempt.md")
    (config.path("docs_root") / "plain.md").write_text("# No front matter\n", encoding="utf-8")
    docs = config.path("docs_root")

    assert idea.document_codes(docs) == {"DOC-001", "DOC-002"}
    assert idea.document_codes(docs, (docs / "exempt.md",)) == {"DOC-001"}
    assert idea.document_codes(docs / "absent") == set()


# --- Closing pointers -----------------------------------------------------------------------


def commit_once(root: Path) -> str:
    """Make `root` a git repository with one commit and return that commit's hash."""
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), "-c", "user.name=fixture", "-c",
             "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", *args],
            capture_output=True, text=True, check=True,
        ).stdout.strip()

    git("init", "-q")
    (root / "file.txt").write_text("content\n", encoding="utf-8")
    git("add", "file.txt")
    git("commit", "-q", "-m", "fixture")
    return git("rev-parse", "HEAD")


PHASE = "phase-" + "x-1"


def write_backlog(config: paths.Config, *phase_ids: str) -> None:
    backlog = config.path("backlog_path")
    backlog.parent.mkdir(parents=True, exist_ok=True)
    items = "".join(f"  - id: {phase}\n" for phase in phase_ids)
    backlog.write_text(f"items:\n{items}", encoding="utf-8")


@pytest.mark.parametrize("target", ["delivered", "resolved", "absorbed"])
def test_a_close_needs_a_pointer(config: paths.Config, log: Path, target: str) -> None:
    """delivered, resolved and absorbed each name where the delivery happened."""
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="needs a pointer"):
        idea.change_status(ONE, target, log=log, config=config)
    assert len(lines(log)) == 1


def test_a_pointer_belongs_only_to_a_close(config: paths.Config, log: Path) -> None:
    """Any other transition refuses a pointer."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="pointer belongs to"):
        idea.change_status(ONE, "triaged", log=log, closes_with=[{"doc": "DOC-001"}],
                           config=config)


def test_a_document_pointer_must_resolve(config: paths.Config, log: Path) -> None:
    """A doc pointer names a code that a document declares."""
    write_document(config, "DOC-001")
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="not a governed document code"):
        idea.change_status(ONE, "delivered", log=log, closes_with=[{"doc": "DOC-009"}],
                           config=config)

    idea.change_status(ONE, "delivered", log=log, closes_with=[{"doc": "DOC-001"}],
                       config=config)
    state = state_of(log)[ONE]
    assert state["status"] == "delivered"
    assert state["closes_with"] == [{"doc": "DOC-001"}]


def test_a_phase_pointer_must_resolve(config: paths.Config, log: Path) -> None:
    """A phase pointer names an id in the backlog."""
    write_backlog(config, PHASE)
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="not a phase in the backlog"):
        idea.change_status(ONE, "resolved", log=log, closes_with=[{"phase": "phase-" + "x-2"}],
                           config=config)

    idea.change_status(ONE, "resolved", log=log, closes_with=[{"phase": PHASE}], config=config)
    assert state_of(log)[ONE]["closes_with"] == [{"phase": PHASE}]


def test_phase_ids_reads_the_backlog(config: paths.Config) -> None:
    """A missing backlog has no phases; a present one lists every item id."""
    assert idea.phase_ids(config.path("backlog_path")) == set()
    write_backlog(config, PHASE)
    assert idea.phase_ids(config.path("backlog_path")) == {PHASE}


def test_a_commit_pointer_must_resolve(tmp_path: Path, config: paths.Config,
                                       log: Path) -> None:
    """A commit pointer names a commit in the repository's history."""
    head = commit_once(tmp_path)
    idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="not a commit"):
        idea.change_status(ONE, "absorbed", log=log, closes_with=[{"commit": "0" * 40}],
                           config=config)

    idea.change_status(ONE, "absorbed", log=log, closes_with=[{"commit": head}], config=config)
    assert state_of(log)[ONE]["closes_with"] == [{"commit": head}]


def test_a_promoted_idea_is_delivered_through_the_cli(tmp_path: Path, config: paths.Config,
                                                      log: Path) -> None:
    """promoted moves on to delivered, with every pointer kind given on the command line."""
    head = commit_once(tmp_path)
    write_document(config, "DOC-001")
    write_backlog(config, PHASE)
    assert cli(tmp_path, "add", "--title", "T", "--body", "B") == 0
    assert cli(tmp_path, "status", ONE, "promoted", "--promoted-to", "DOC-001") == 0
    assert cli(tmp_path, "status", ONE, "delivered", "--commit", "0" * 40) == 1
    assert cli(tmp_path, "status", ONE, "delivered", "--doc", "DOC-001", "--phase", PHASE,
               "--commit", head) == 0

    state = state_of(log)[ONE]
    assert state["status"] == "delivered"
    assert state["closes_with"] == [{"doc": "DOC-001"}, {"phase": PHASE}, {"commit": head}]


# --- Classification -------------------------------------------------------------------------


KNOWLEDGE: dict[str, Any] = {
    "record_kind": "knowledge",
    "ontological": "concept",
    "epistemic": "hypothesis",
    "lifecycle": "generative_seed",
    "temporal": "standing",
    "reasons": {"ontological": "names a concept", "epistemic": "unproven",
                "lifecycle": "a starting point", "temporal": "no time bound"},
    "confidence": {"ontological": 0.9, "epistemic": 0.7, "lifecycle": 0.8, "temporal": 0.6},
}


def test_the_latest_classification_replaces_the_whole_of_the_one_before(log: Path) -> None:
    """An axis the reclassification leaves out is not inherited from the earlier one."""
    idea.add("First", "Body", log)
    idea.classify(ONE, "agent-blue", KNOWLEDGE, log)
    first = state_of(log)[ONE]["classification"]
    assert first["ontological"] == "concept"
    assert first["decompose"] is False
    assert first["tie_breaks"] == []
    assert first["author"] == "agent-blue"

    idea.classify(ONE, ideas.OWNER, {"record_kind": "reference"}, log)
    second = state_of(log)[ONE]["classification"]
    assert second["record_kind"] == "reference"
    assert "ontological" not in second
    assert second["author"] == ideas.OWNER
    assert len(lines(log)) == 3, "the earlier classification stays in the log"


def test_a_classification_is_checked_against_the_schema(log: Path) -> None:
    """A knowledge record carries every axis; any other kind carries none."""
    idea.add("First", "Body", log)
    missing_axis = {k: v for k, v in KNOWLEDGE.items() if k != "temporal"}
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.classify(ONE, "agent-blue", missing_axis, log)
    with pytest.raises(IdeaError, match="refusing to append"):
        idea.classify(ONE, "agent-blue", {"record_kind": "fixture", "ontological": "concept"},
                      log)
    with pytest.raises(IdeaError, match="not classification fields"):
        idea.classify(ONE, "agent-blue", {"record_kind": "fixture", "colour": "blue"}, log)
    assert len(lines(log)) == 1


def test_classification_is_read_from_a_file_by_the_cli(tmp_path: Path, log: Path) -> None:
    """The command line reads the classification as JSON, never from a shell argument."""
    source = tmp_path / "classification.json"
    source.write_text(json.dumps(KNOWLEDGE), encoding="utf-8")
    assert cli(tmp_path, "add", "--title", "T", "--body", "B") == 0
    assert cli(tmp_path, "classify", ONE, "--author", "agent-blue", "--file", str(source)) == 0
    assert state_of(log)[ONE]["classification"]["lifecycle"] == "generative_seed"


# --- The safe write path: `--file` and stdin bypass the shell entirely ----------------------


def test_dangerous_prose_survives_the_real_cli_via_file(tmp_path: Path, log: Path) -> None:
    """`--file` never puts prose in a shell argument, so it reaches the log unchanged.

    A sentinel file is what a shell evaluating the embedded commands would create.
    """
    sentinel = tmp_path / "sentinel"
    dangerous_title = "Title with `touch " + str(sentinel) + "` inside it"
    dangerous_body = (
        "Body with $(touch " + str(sentinel) + "), \"quotes\", 'quotes',\n"
        "a newline, and non-ASCII Ünïcødé 日本語."
    )
    source = tmp_path / "idea.md"
    source.write_text(f"{dangerous_title}\n{dangerous_body}", encoding="utf-8")

    assert cli(tmp_path, "add", "--file", str(source)) == 0

    assert not sentinel.exists(), "a sentinel command embedded in prose executed"
    stored = json.loads(lines(log)[0])
    assert stored["title"] == dangerous_title
    assert stored["body"] == dangerous_body


def test_dangerous_prose_survives_the_real_cli_via_stdin(
    tmp_path: Path, log: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same safe route, fed from stdin instead of a file."""
    dangerous_body = "Body with `backticks`, $(subst), \"quotes\" and a newline.\nSecond line."

    monkeypatch.setattr(sys, "stdin", io.StringIO(f"A safe title\n{dangerous_body}"))
    assert cli(tmp_path, "add") == 0

    stored = json.loads(lines(log)[0])
    assert stored["title"] == "A safe title"
    assert stored["body"] == dangerous_body


def test_file_and_title_together_are_refused(tmp_path: Path) -> None:
    """`--file` replaces `--title`/`--body`; argparse allows the combination, main() must not."""
    source = tmp_path / "idea.md"
    source.write_text("Title\nBody", encoding="utf-8")

    parser_args = idea._parser().parse_args(["add", "--file", str(source), "--title", "X"])
    with pytest.raises(IdeaError, match="not both"):
        idea._read_add_input(parser_args)


def test_the_transition_table_comes_from_the_schema() -> None:
    """Two copies of a rule is one copy and one liability."""
    schema = json.loads(ideas.SCHEMA.read_text(encoding="utf-8"))
    declared = {
        (option["properties"]["from"]["const"], option["properties"]["to"]["const"])
        for branch in schema["allOf"]
        if branch.get("if", {}).get("properties", {}).get("event", {}).get("const") == "status"
        for option in branch["then"]["oneOf"]
    }
    assert ideas.legal_transitions() == declared
    assert not any(source in ideas.TERMINAL_STATES for source, _ in declared), (
        "a terminal state is never a from; the only exit from discarded is a revisited event"
    )


# --- The writer offers no way to supply a timestamp -----------------------------------------


def test_the_writer_exposes_no_timestamp_argument() -> None:
    """Asserted against the interface: the option does not exist on any subcommand."""
    parser = idea._parser()
    options: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                options.extend(o for a in sub._actions for o in a.option_strings)
                options.extend(a.dest for a in sub._actions)
        options.extend(action.option_strings)

    forbidden = {"--at", "--time", "--timestamp", "--date", "--when", "at", "timestamp"}
    assert forbidden.isdisjoint(options), f"a timestamp argument reappeared: {sorted(options)}"


SUBCOMMANDS = ["add", "status", "revisit", "amend", "annotate", "amend-annotation", "link",
               "retract-link", "classify", "list", "show"]
TIME_OPTION = re.compile(r"--(?:at|time|timestamp|date|when)\b")


@pytest.mark.parametrize("args", [["--help"]] + [[name, "--help"] for name in SUBCOMMANDS],
                         ids=lambda args: " ".join(args))
def test_no_help_text_offers_a_time_option(args: list[str],
                                           capsys: pytest.CaptureFixture[str]) -> None:
    """`--help` on the writer and every subcommand shows no time or date option."""
    with pytest.raises(SystemExit) as excinfo:
        idea.main(args)
    assert excinfo.value.code == 0
    shown = capsys.readouterr().out
    assert "usage:" in shown
    assert not TIME_OPTION.search(shown), shown


# --- Read-only commands ---------------------------------------------------------------------


def test_list_and_show_write_nothing(tmp_path: Path, log: Path,
                                     capsys: pytest.CaptureFixture[str]) -> None:
    """`list` and `show` print the folded state and never append."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body", log)
    idea.change_status(TWO, "triaged", log=log)
    idea.amend(ONE, title="First corrected", log=log)
    before = lines(log)
    capsys.readouterr()

    assert cli(tmp_path, "list", "--status", "open") == 0
    assert capsys.readouterr().out == f"{ONE} | open | First corrected\n"
    assert cli(tmp_path, "show", TWO) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "triaged"
    assert cli(tmp_path, "show", NINETY_NINE) == 1
    assert lines(log) == before


# --- The fold matches the source fold, and the schema's enums match the source schema -------

def _iid(number: int) -> str:
    return f"{number:06d}"


def _at(minute: int) -> str:
    return dt.datetime(2030, 1, 1, 0, minute, tzinfo=dt.UTC).isoformat()


def _digest(event: dict[str, Any]) -> str:
    """An event's identity when it carries no ``eid``, computed independently of ``ideas.py``."""
    encoded = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


A, B, C, D = _iid(1), _iid(2), _iid(3), _iid(4)
LEGACY_CREATED = {"idea": D, "event": "created", "at": _at(0), "title": "Legacy", "body": "No eid"}
COMMIT = "ab" * 4

FIXTURE_EVENTS: list[dict[str, Any]] = [
    {"idea": A, "event": "created", "at": _at(1), "eid": "ev-1", "title": "Alpha", "body": "A"},
    {"idea": B, "event": "created", "at": _at(2), "eid": "ev-2", "title": "Beta", "body": "B body"},
    {"idea": C, "event": "created", "at": _at(3), "eid": "ev-3", "title": "Gamma", "body": "C"},
    LEGACY_CREATED,
    {"idea": A, "event": "amended", "at": _at(4), "eid": "ev-4", "amends": "ev-1",
     "title": {"set": True, "value": "Alpha, corrected"}},
    {"idea": A, "event": "amended", "at": _at(5), "eid": "ev-5", "amends": "ev-4",
     "title": {"set": True, "value": "Alpha, corrected twice"}},
    {"idea": D, "event": "amended", "at": _at(6), "eid": "ev-6", "amends": _digest(LEGACY_CREATED),
     "body": {"set": True, "value": "Legacy body, corrected"}},
    {"idea": A, "event": "status", "at": _at(7), "eid": "ev-7", "from": "open", "to": "triaged"},
    {"idea": A, "event": "status", "at": _at(8), "eid": "ev-8", "from": "triaged",
     "to": "promoted", "promoted_to": "DOC-001"},
    {"idea": A, "event": "status", "at": _at(9), "eid": "ev-9", "from": "promoted",
     "to": "delivered", "closes_with": [{"doc": "DOC-001"}, {"commit": COMMIT}]},
    {"idea": B, "event": "annotated", "at": _at(10), "eid": "ev-10", "author": "agent-x",
     "kind": "finding", "text": "First finding"},
    {"idea": B, "event": "amended", "at": _at(11), "eid": "ev-11", "amends": "ev-10",
     "text": {"set": True, "value": "First finding, corrected"}},
    {"idea": B, "event": "annotated", "at": _at(12), "eid": "ev-12", "author": "repository-owner",
     "kind": "note", "text": "A note"},
    {"idea": B, "event": "linked", "at": _at(13), "eid": "ev-13", "type": "extends", "target": A},
    {"idea": B, "event": "linked", "at": _at(14), "eid": "ev-14", "type": "relates_to",
     "target_code": "DOC-002"},
    {"idea": B, "event": "linked", "at": _at(15), "eid": "ev-15", "type": "component_of",
     "target": C},
    {"idea": B, "event": "amended", "at": _at(16), "eid": "ev-16", "amends": "ev-15",
     "target": {"set": True, "value": None}},
    {"idea": B, "event": "amended", "at": _at(17), "eid": "ev-17", "amends": "ev-14",
     "target_code": {"set": True, "value": None}},
    {"idea": C, "event": "status", "at": _at(18), "eid": "ev-18", "from": "open",
     "to": "discarded"},
    {"idea": C, "event": "revisited", "at": _at(19), "eid": "ev-19"},
    {"idea": C, "event": "classified", "at": _at(20), "eid": "ev-20", "author": "agent-x",
     "record_kind": "reference"},
    {"idea": C, "event": "classified", "at": _at(21), "eid": "ev-21", "author": "agent-x",
     "record_kind": "knowledge", "ontological": "process", "epistemic": "hypothesis",
     "lifecycle": "retrospective_insight", "temporal": "as_of",
     "lifecycle_remedy": "operational_task",
     "reasons": {"ontological": "o", "epistemic": "e", "lifecycle": "l", "temporal": "t"},
     "confidence": {"ontological": 0.9, "epistemic": 0.5, "lifecycle": 0.7, "temporal": 1},
     "tie_breaks": ["E4"]},
    {"idea": C, "event": "status", "at": _at(22), "eid": "ev-22", "from": "reviewing",
     "to": "resolved", "closes_with": [{"phase": "phase-" + "x-1"}]},
]

#: What the source repository's fold produced for ``FIXTURE_EVENTS`` when this plugin's fold was
#: ported from it. The port changed only path handling, so the two must agree exactly.
EXPECTED_STATE: dict[str, dict[str, Any]] = {
    A: {"title": "Alpha, corrected twice", "body": "A", "status": "delivered",
        "created": _at(1), "updated": _at(9), "revisits": 0, "promoted_to": ["DOC-001"],
        "annotations": [], "links": [],
        "closes_with": [{"doc": "DOC-001"}, {"commit": COMMIT}]},
    B: {"title": "Beta", "body": "B body", "status": "open", "created": _at(2),
        "updated": _at(15), "revisits": 0, "promoted_to": None,
        "annotations": [
            {"eid": "ev-10", "author": "agent-x", "kind": "finding",
             "text": "First finding, corrected", "at": _at(10)},
            {"eid": "ev-12", "author": "repository-owner", "kind": "note", "text": "A note",
             "at": _at(12)},
        ],
        "links": [
            {"eid": "ev-13", "type": "extends", "target": A, "retracted": False, "at": _at(13)},
            {"eid": "ev-14", "type": "relates_to", "target": None, "retracted": True,
             "at": _at(14), "target_code": None},
            {"eid": "ev-15", "type": "component_of", "target": None, "retracted": True,
             "at": _at(15)},
        ]},
    C: {"title": "Gamma", "body": "C", "status": "resolved", "created": _at(3),
        "updated": _at(22), "revisits": 1, "promoted_to": None, "annotations": [], "links": [],
        "classification": {
            "record_kind": "knowledge", "ontological": "process", "epistemic": "hypothesis",
            "lifecycle": "retrospective_insight", "temporal": "as_of",
            "lifecycle_remedy": "operational_task", "decompose": False,
            "reasons": {"ontological": "o", "epistemic": "e", "lifecycle": "l", "temporal": "t"},
            "confidence": {"ontological": 0.9, "epistemic": 0.5, "lifecycle": 0.7,
                           "temporal": 1},
            "tie_breaks": ["E4"], "eid": "ev-21", "author": "agent-x", "at": _at(21)},
        "closes_with": [{"phase": "phase-" + "x-1"}]},
    D: {"title": "Legacy", "body": "Legacy body, corrected", "status": "open",
        "created": _at(0), "updated": _at(0), "revisits": 0, "promoted_to": None,
        "annotations": [], "links": []},
}


def test_the_fold_matches_the_source_fold_on_a_fixture_log() -> None:
    """Amendments, chained amendments, a legacy event, links, retractions, classification."""
    assert ideas.fold(FIXTURE_EVENTS) == EXPECTED_STATE


#: The schema enums this plugin's idea schema must carry: the source repository's, copied from
#: the commit the classification fields landed in.
SOURCE_ENUMS: dict[str, list[str]] = {
    "event": ["created", "status", "revisited", "amended", "annotated", "linked", "classified"],
    "kind": ["note", "finding", "assessment", "lineage"],
    "type": ["extends", "supersedes", "relates_to", "component_of"],
    "record_kind": ["knowledge", "collection", "fixture", "reference"],
    "ontological": ["concept", "artifact", "process", "event", "actor", "metric"],
    "epistemic": ["axiom", "hypothesis", "anti_pattern", "not_applicable"],
    "lifecycle": ["generative_seed", "strategic_directive", "operational_task",
                  "retrospective_insight", "active", "deprecated"],
    "temporal": ["as_of", "standing"],
    "lifecycle_remedy": ["operational_task", "generative_seed"],
    "tie_breaks": ["O1", "O2", "O3", "O4", "O5", "O6", "E1", "E2", "E3", "E4",
                   "L1", "L2", "L3", "L4", "L5"],
    "status": ["open", "triaged", "reviewing", "promoted", "discarded", "delivered", "resolved",
               "absorbed"],
}


def test_the_schema_enums_equal_the_source_schema() -> None:
    """The record kind, each axis and every other enum equal the source schema's, as sets."""
    schema = json.loads(ideas.SCHEMA.read_text(encoding="utf-8"))
    found = {name: set(node.get("items", node)["enum"])
             for name, node in schema["properties"].items()
             if "enum" in node or "enum" in node.get("items", {})}
    found["status"] = set(schema["definitions"]["status"]["enum"])
    assert found == {name: set(values) for name, values in SOURCE_ENUMS.items()}


# --- The triage agent and skill cannot write links or promotions ---------------------------


def _front_matter(path: Path) -> dict[str, Any]:
    loaded: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])
    return loaded


def test_the_triage_agent_cannot_edit_or_write_files() -> None:
    agent = PLUGIN_ROOT / "agents" / "idea-triage.md"
    tools = {tool.strip() for tool in str(_front_matter(agent)["tools"]).split(",")}
    assert "Edit" not in tools and "Write" not in tools
    assert tools, "the agent must declare its tools; an absent list grants every tool"


def test_triage_runs_no_link_or_promotion_command() -> None:
    """Every writer command in the triage agent and skill is annotate, list, show or triaged."""
    for path in (PLUGIN_ROOT / "agents" / "idea-triage.md",
                 PLUGIN_ROOT / "skills" / "idea-triage" / "SKILL.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "idea.py" not in line:
                continue
            assert not re.search(r"idea\.py\S*\s+(link|retract-link)\b", line), (path, line)
            assert not re.search(r"idea\.py\S*\s+status\b.*\bpromoted\b", line), (path, line)


def test_the_triage_search_list_is_a_documented_option() -> None:
    key = paths.KEYS["triage_search"]
    assert key.kind == "paths" and key.default
    skill = (PLUGIN_ROOT / "skills" / "idea-triage" / "SKILL.md").read_text(encoding="utf-8")
    assert "${user_config.triage_search}" in skill
