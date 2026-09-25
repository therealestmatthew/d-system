"""Tests for the ARCH-005 schema bundle (phase-idg-01, ADR-024).

The classification, the `component_of` link type, the `lineage` annotation kind, links to
governed documents, and the delivered/resolved/absorbed closes with their pointers. Each block
names the REQ-014 row or backlog acceptance condition it checks.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from src.db.ideas import INVERSE_LINK_TYPE, IdeaError, fold, load_events
from src.governance.__main__ import document_codes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "idea.schema.json").read_text(encoding="utf-8"))
ARCH_005 = ROOT / "docs" / "07-architecture" / "ARCH-005-idea-node-classification.md"

#: The last dev commit before this bundle changed the schema and the fold — the baseline
#: REQ-014 R07 compares against.
PRE_CHANGE = "0f142ce"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


append_idea = _load("append_idea")


@pytest.fixture
def log(tmp_path: Path) -> Path:
    return tmp_path / "ideas.jsonl"


def _errors(event: dict[str, Any]) -> list[str]:
    return [error.message for error in Draft7Validator(SCHEMA).iter_errors(event)]


def _classified(**fields: Any) -> dict[str, Any]:
    return {
        "idea": "000001", "event": "classified", "at": "2026-09-25T10:00:00+10:00",
        "eid": "e1", "author": "agent-classifier", **fields,
    }


KNOWLEDGE: dict[str, Any] = {
    "record_kind": "knowledge",
    "ontological": "artifact",
    "epistemic": "axiom",
    "lifecycle": "operational_task",
    "temporal": "as_of",
    "reasons": {
        "ontological": "names a schema file",
        "epistemic": "a defect in the title",
        "lifecycle": "one fix with a done-state",
        "temporal": "true at a commit",
    },
    "confidence": {"ontological": 0.9, "epistemic": 0.8, "lifecycle": 0.7, "temporal": 0.95},
}


def _head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


# --- R01: the classification is distinct fields, not tags --------------------------------


def test_each_arch_005_type_is_one_enum_token_on_its_own_field() -> None:
    properties = SCHEMA["properties"]
    assert properties["record_kind"]["enum"] == ["knowledge", "collection", "fixture", "reference"]
    assert properties["ontological"]["enum"] == [
        "concept", "artifact", "process", "event", "actor", "metric",
    ]
    assert properties["epistemic"]["enum"] == [
        "axiom", "hypothesis", "anti_pattern", "not_applicable",
    ]
    assert properties["lifecycle"]["enum"] == [
        "generative_seed", "strategic_directive", "operational_task",
        "retrospective_insight", "active", "deprecated",
    ]
    assert properties["temporal"]["enum"] == ["as_of", "standing"]
    arch = ARCH_005.read_text(encoding="utf-8")
    for label in ("Actor / Agent", "Metric / Standard", "Not Applicable / Agnostic",
                  "Active / Evergreen", "Deprecated / Archived", "As-of", "Standing"):
        assert label in arch, f"ARCH-005 no longer names {label!r}; the enum may have drifted"


def test_a_classification_written_as_a_tag_is_rejected() -> None:
    assert _errors(_classified(**KNOWLEDGE)) == []
    assert _errors(_classified(**KNOWLEDGE, tags=["axiom"]))
    assert _errors(_classified(**{**KNOWLEDGE, "epistemic": "Axiom / Ground Truth"}))


# --- R02: every knowledge record has every axis, with a reason ----------------------------


def test_a_knowledge_record_missing_an_axis_is_rejected() -> None:
    for axis in ("ontological", "epistemic", "lifecycle", "temporal"):
        partial = {key: value for key, value in KNOWLEDGE.items() if key != axis}
        assert _errors(_classified(**partial)), f"{axis} missing was accepted"


def test_every_axis_value_needs_a_reason_and_a_confidence() -> None:
    for field in ("reasons", "confidence"):
        thinned = {**KNOWLEDGE, field: dict(list(KNOWLEDGE[field].items())[1:])}
        assert _errors(_classified(**thinned)), f"a missing {field} entry was accepted"
    assert _errors(_classified(**{**KNOWLEDGE, "confidence": {**KNOWLEDGE["confidence"],
                                                               "temporal": 1.5}}))


def test_not_applicable_is_a_legal_epistemic_value() -> None:
    assert _errors(_classified(**{**KNOWLEDGE, "epistemic": "not_applicable"})) == []


def test_a_collection_carries_its_kind_and_no_axis_value() -> None:
    assert _errors(_classified(record_kind="collection",
                               reasons={"record_kind": "an anchor"})) == []
    assert _errors(_classified(record_kind="collection", ontological="concept"))
    assert _errors(_classified(record_kind="reference", reasons={"temporal": "x"}))
    assert _errors(_classified(record_kind="fixture", decompose=True))


def test_lifecycle_remedy_appears_exactly_on_a_retrospective_insight() -> None:
    insight = {**KNOWLEDGE, "lifecycle": "retrospective_insight"}
    assert _errors(_classified(**insight))
    assert _errors(_classified(**insight, lifecycle_remedy="generative_seed")) == []
    assert _errors(_classified(**KNOWLEDGE, lifecycle_remedy="operational_task"))


def test_classification_fields_belong_only_to_a_classified_event() -> None:
    created = {"idea": "000001", "event": "created", "at": "2026-09-25T10:00:00+10:00",
               "title": "t", "body": "b"}
    assert _errors(created) == []
    assert _errors({**created, "record_kind": "knowledge"})


def test_tie_breaks_are_arch_005_rule_ids() -> None:
    assert _errors(_classified(**KNOWLEDGE, tie_breaks=["E4", "L3"])) == []
    assert _errors(_classified(**KNOWLEDGE, tie_breaks=["Z9"]))


def test_the_latest_classification_wins_and_the_first_stays_in_the_log(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.classify("000001", "agent-classifier", KNOWLEDGE, log)
    second = {**KNOWLEDGE, "record_kind": "collection"}
    for axis in ("ontological", "epistemic", "lifecycle", "temporal"):
        second.pop(axis)
    second.pop("reasons")
    second.pop("confidence")
    event = append_idea.classify("000001", "repository-owner", second, log)
    events = load_events(log)
    assert sum(e["event"] == "classified" for e in events) == 2
    classification = fold(events)["000001"]["classification"]
    assert classification["record_kind"] == "collection"
    assert "ontological" not in classification
    assert classification["author"] == "repository-owner"
    assert classification["at"] == event["at"]


def test_a_knowledge_classification_folds_with_provenance_and_defaults(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.classify("000001", "agent-classifier", KNOWLEDGE, log)
    classification = fold(load_events(log))["000001"]["classification"]
    assert classification["decompose"] is False
    assert classification["tie_breaks"] == []
    assert classification["author"] == "agent-classifier"
    assert classification["reasons"] == KNOWLEDGE["reasons"]


def test_the_writer_refuses_an_invalid_or_unknown_classification(log: Path) -> None:
    append_idea.add("First", "Body", log)
    before = log.read_bytes()
    with pytest.raises(IdeaError, match="not classification fields"):
        append_idea.classify("000001", "agent-classifier", {**KNOWLEDGE, "tags": ["x"]}, log)
    with pytest.raises(IdeaError, match="invalid event"):
        append_idea.classify("000001", "agent-classifier", {"record_kind": "knowledge"}, log)
    assert log.read_bytes() == before


def test_classify_reads_its_classification_from_a_file(log: Path, tmp_path: Path,
                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    append_idea.add("First", "Body", log)
    monkeypatch.setattr(append_idea, "LOG", log)
    source = tmp_path / "classification.json"
    source.write_text(json.dumps(KNOWLEDGE), encoding="utf-8")
    assert append_idea.main(
        ["classify", "000001", "--author", "agent-classifier", "--file", str(source)]
    ) == 0
    assert fold(load_events(log))["000001"]["classification"]["temporal"] == "as_of"


# --- R04: a link may target a governed document ------------------------------------------


def test_the_document_registry_is_the_governance_one() -> None:
    codes = document_codes(ROOT)
    assert {"PLAN-029", "REQ-014", "ARCH-005", "ADR-024"} <= codes


def test_a_link_to_a_document_code_is_explicit_in_the_record(log: Path) -> None:
    append_idea.add("First", "Body", log)
    event, _ = append_idea.link("000001", "relates_to", None, log, target_code="PLAN-029")
    assert event["target_code"] == "PLAN-029" and "target" not in event
    (entry,) = fold(load_events(log))["000001"]["links"]
    assert entry["target_code"] == "PLAN-029"
    assert entry["target"] is None
    assert entry["retracted"] is False


def test_a_link_to_a_missing_document_code_is_refused(log: Path) -> None:
    append_idea.add("First", "Body", log)
    before = log.read_bytes()
    with pytest.raises(IdeaError, match="not a governed document code"):
        append_idea.link("000001", "relates_to", None, log, target_code="PLAN-999")
    assert log.read_bytes() == before


def test_only_extends_and_relates_to_may_point_at_a_document(log: Path) -> None:
    append_idea.add("First", "Body", log)
    for type_ in ("supersedes", "component_of"):
        with pytest.raises(IdeaError, match="cannot point at a document"):
            append_idea.link("000001", type_, None, log, target_code="PLAN-029")
    bad = {"idea": "000001", "event": "linked", "at": "2026-09-25T10:00:00+10:00",
           "type": "supersedes", "target_code": "PLAN-029"}
    assert _errors(bad)
    assert _errors({**bad, "type": "relates_to", "target": "000002"}), "both targets accepted"


def test_a_document_link_is_retracted_like_an_idea_link(log: Path) -> None:
    append_idea.add("First", "Body", log)
    event, _ = append_idea.link("000001", "extends", None, log, target_code="ADR-024")
    append_idea.retract_link("000001", event["eid"], log)
    (entry,) = fold(load_events(log))["000001"]["links"]
    assert entry["retracted"] is True
    assert entry["target_code"] is None


# --- R05: component_of and lineage --------------------------------------------------------


def test_component_of_is_written_and_folded_with_a_derived_inverse(log: Path) -> None:
    append_idea.add("Part", "Body", log)
    append_idea.add("Whole", "Body", log)
    append_idea.link("000001", "component_of", "000002", log)
    (entry,) = fold(load_events(log))["000001"]["links"]
    assert (entry["type"], entry["target"]) == ("component_of", "000002")
    assert INVERSE_LINK_TYPE["component_of"] == "has_component"


def test_lineage_is_the_owners_voice(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.annotate("000001", "repository-owner", "lineage", "pulled out of 000004", log)
    before = log.read_bytes()
    with pytest.raises(IdeaError, match="may only write kind=finding"):
        append_idea.annotate("000001", "agent-triage", "lineage", "from 000004", log)
    assert log.read_bytes() == before
    (annotation,) = fold(load_events(log))["000001"]["annotations"]
    assert annotation["kind"] == "lineage"


# --- The terminal statuses and their pointers ---------------------------------------------


def test_each_close_is_legal_and_terminal() -> None:
    transitions = append_idea.legal_transitions()
    for close in ("delivered", "resolved", "absorbed"):
        for source in ("open", "triaged", "reviewing"):
            assert (source, close) in transitions
        assert not any(source == close for source, _ in transitions), f"{close} has a way out"
    assert ("promoted", "delivered") in transitions
    assert ("promoted", "resolved") not in transitions
    assert ("promoted", "absorbed") not in transitions
    assert ("promoted", "discarded") not in transitions
    assert ("reviewing", "resolved") in transitions


@pytest.mark.parametrize("close", ["delivered", "resolved", "absorbed"])
def test_a_close_without_a_pointer_is_refused(log: Path, close: str) -> None:
    append_idea.add("First", "Body", log)
    before = log.read_bytes()
    with pytest.raises(IdeaError, match="needs a pointer"):
        append_idea.change_status("000001", close, log=log)
    assert log.read_bytes() == before
    bare = {"idea": "000001", "event": "status", "at": "2026-09-25T10:00:00+10:00",
            "from": "open", "to": close}
    assert _errors(bare), "the schema accepted a close with no pointer"


@pytest.mark.parametrize(
    ("pointer", "message"),
    [
        ({"doc": "PLAN-999"}, "not a governed document code"),
        ({"phase": "phase-nope-99"}, "not a phase in the backlog"),
        ({"commit": "deadbeefdeadbeef"}, "not a commit in this repository"),
    ],
)
def test_a_pointer_that_does_not_resolve_is_refused(
    log: Path, pointer: dict[str, str], message: str
) -> None:
    append_idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match=message):
        append_idea.change_status("000001", "resolved", log=log, closes_with=[pointer])


def test_a_close_records_every_resolving_pointer(log: Path) -> None:
    append_idea.add("First", "Body", log)
    pointers = [{"doc": "ADR-024"}, {"phase": "phase-idg-01"}, {"commit": _head()}]
    append_idea.change_status("000001", "delivered", log=log, closes_with=pointers)
    state = fold(load_events(log))["000001"]
    assert state["status"] == "delivered"
    assert state["closes_with"] == pointers


def test_a_pointer_names_exactly_one_kind() -> None:
    event = {"idea": "000001", "event": "status", "at": "2026-09-25T10:00:00+10:00",
             "from": "open", "to": "absorbed"}
    assert _errors({**event, "closes_with": [{"doc": "PLAN-029"}]}) == []
    assert _errors({**event, "closes_with": [{"doc": "PLAN-029", "phase": "phase-idg-01"}]})
    assert _errors({**event, "closes_with": [{"url": "https://example.com"}]})
    assert _errors({**event, "closes_with": []})


def test_a_pointer_on_any_other_move_is_refused(log: Path) -> None:
    append_idea.add("First", "Body", log)
    with pytest.raises(IdeaError, match="belongs to delivered, resolved or absorbed"):
        append_idea.change_status("000001", "triaged", log=log, closes_with=[{"doc": "PLAN-029"}])
    event = {"idea": "000001", "event": "status", "at": "2026-09-25T10:00:00+10:00",
             "from": "open", "to": "triaged", "closes_with": [{"doc": "PLAN-029"}]}
    assert _errors(event)


def test_promoted_accepts_a_later_move_to_delivered(log: Path) -> None:
    append_idea.add("First", "Body", log)
    append_idea.change_status("000001", "promoted", ["PLAN-029"], log=log)
    append_idea.change_status("000001", "delivered", log=log, closes_with=[{"doc": "ADR-024"}])
    state = fold(load_events(log))["000001"]
    assert state["status"] == "delivered"
    assert state["promoted_to"] == ["PLAN-029"]
    with pytest.raises(IdeaError, match="illegal transition"):
        append_idea.change_status("000001", "discarded", log=log)


def test_a_revisited_idea_moves_from_reviewing_to_resolved(log: Path) -> None:
    """000099 and 000129's route: discarded, revisited to reviewing, then resolved."""
    append_idea.add("First", "Body", log)
    append_idea.change_status("000001", "discarded", log=log)
    append_idea.revisit("000001", log)
    append_idea.change_status("000001", "resolved", log=log, closes_with=[{"doc": "GOV-003"}])
    assert fold(load_events(log))["000001"]["status"] == "resolved"


def test_the_cli_takes_pointers_by_kind(log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    append_idea.add("First", "Body", log)
    monkeypatch.setattr(append_idea, "LOG", log)
    assert append_idea.main(
        ["status", "000001", "absorbed", "--doc", "PLAN-029", "--phase", "phase-idg-01"]
    ) == 0
    assert fold(load_events(log))["000001"]["closes_with"] == [
        {"doc": "PLAN-029"}, {"phase": "phase-idg-01"},
    ]


# --- R07: every pre-change idea folds to identical state ----------------------------------


def _pre_change_fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Fold with the fold and schema as they stood at PRE_CHANGE."""
    def show(path: str) -> str:
        return subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{PRE_CHANGE}:{path}"],
            capture_output=True, text=True, check=True,
        ).stdout

    namespace: dict[str, Any] = {"__name__": "pre_change_ideas", "__file__": str(ROOT / "x" / "y")}
    exec(compile(show("src/db/ideas.py"), "pre_change_ideas", "exec"), namespace)
    old_schema = json.loads(show("schemas/idea.schema.json"))
    namespace["_schema"] = lambda: old_schema
    result: dict[str, dict[str, Any]] = namespace["fold"](events)
    return result


def _pre_change_events() -> list[dict[str, Any]]:
    text = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{PRE_CHANGE}:_data/ideas.jsonl"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def test_every_pre_change_idea_folds_to_identical_state() -> None:
    """Ideas nothing has touched since the change fold exactly as the old fold read them."""
    before = _pre_change_events()
    events = load_events(ROOT / "_data" / "ideas.jsonl")
    touched_since = {e["idea"] for e in events[len(before):]}
    old = _pre_change_fold(before)
    new = fold(events)
    untouched = sorted(set(old) - touched_since)
    assert len(untouched) > 400, "too few pre-change ideas left to compare"
    for idea in untouched:
        assert new[idea] == old[idea], f"{idea} folds differently after the schema change"


def test_the_log_before_the_change_is_a_byte_identical_prefix() -> None:
    before = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{PRE_CHANGE}:_data/ideas.jsonl"],
        capture_output=True, check=True,
    ).stdout
    now = (ROOT / "_data" / "ideas.jsonl").read_bytes()
    assert now.startswith(before)
