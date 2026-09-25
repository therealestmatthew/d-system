"""The rendered idea view and the ideas check, over temporary fixture logs.

The view is generated from the log: rendering is deterministic, a hand edit or an unrendered
append is reported as stale, and the priority queue is validated against the folded log.
Nothing here reads a file outside the plugin.
"""

from __future__ import annotations

import datetime as dt
import os
import subprocess
from pathlib import Path

import idea
import ideas
import paths
import pytest
import render_ideas
from checks import ideas as ideas_check
from ideas import fold, load_events

TODAY = dt.date(2030, 1, 10)


def iid(n: int) -> str:
    """An idea id, built rather than written, so no six-digit literal appears in the suite."""
    return f"{n:06d}"


ONE, TWO, NINE = iid(1), iid(2), iid(9)


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


def state_of(log: Path) -> dict[str, dict[str, object]]:
    return fold(load_events(log))


def write_view(config: paths.Config) -> Path:
    view = config.path("ideas_view_path")
    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_text(render_ideas.render_view(config), encoding="utf-8")
    return view


def write_priority(config: paths.Config, next_up: list[str], updated: dt.date = TODAY) -> None:
    priority = config.path("priority_path")
    priority.parent.mkdir(parents=True, exist_ok=True)
    listed = ", ".join(f"'{item}'" for item in next_up)
    priority.write_text(
        f"schema_version: 1\nupdated: '{updated.isoformat()}'\nnext_up: [{listed}]\n",
        encoding="utf-8",
    )


def section(rendered: str, idea_id: str) -> str:
    start = rendered.index(f"## {idea_id} ·")
    end = rendered.find("\n---\n", start)
    return rendered[start:] if end == -1 else rendered[start:end]


# --- What the view shows --------------------------------------------------------------------


def test_rendered_findings_collapse_and_notes_stay_visible(log: Path) -> None:
    """Notes stay visible; a hundred findings collapse into one details block."""
    idea.add("Title", "Body", log)
    idea.annotate(ONE, ideas.OWNER, "note", "an owner note", log=log)
    for i in range(100):
        idea.annotate(ONE, "agent-blue", "finding", f"finding {i}", log=log)

    state = state_of(log)
    rendered = render_ideas.render(state)

    assert "an owner note" in rendered, "notes are the owner's voice and stay visible"
    assert "<details>" in rendered and "100 finding(s)" in rendered
    assert rendered.count("finding 0") == 1
    assert render_ideas.render(state) == rendered, "rendering stays deterministic"


def test_rendered_links_show_the_derived_inverse(log: Path) -> None:
    """The asserting idea shows the edge; its target shows the derived inverse."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    idea.link(ONE, "extends", TWO, log=log)

    rendered = render_ideas.render(state_of(log))

    assert f"extends → `{TWO}`" in section(rendered, ONE)
    assert f"extended_by ← `{ONE}`" in section(rendered, TWO)


def test_a_retracted_link_is_not_rendered(log: Path) -> None:
    """A retracted edge shows on neither side."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    event, _ = idea.link(ONE, "relates_to", TWO, log=log)
    idea.retract_link(ONE, ideas.identity(event), log=log)

    rendered = render_ideas.render(state_of(log))

    assert "**Links**" not in rendered


def test_the_view_reflects_a_revisit_and_a_promotion(log: Path) -> None:
    """The status line carries the revisit count and what the idea became."""
    idea.add("First", "Body", log)
    idea.change_status(ONE, "discarded", log=log)
    idea.revisit(ONE, log=log)
    idea.add("Second", "Body two", log)
    idea.change_status(TWO, "promoted", promoted_to=["DOC-016"], log=log)

    rendered = render_ideas.render(state_of(log))

    assert "revisited 1×" in rendered
    assert "became DOC-016" in rendered


def test_the_view_shows_a_document_link_classification_and_closing_pointers(
    tmp_path: Path, config: paths.Config, log: Path
) -> None:
    """A document link renders its code, a classification its axes, a close its pointers."""
    docs = config.path("docs_root")
    docs.mkdir(parents=True)
    (docs / "doc.md").write_text("---\ncode: DOC-001\n---\n\n# A document\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.name=fixture", "-c",
         "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
         "commit", "-q", "--allow-empty", "-m", "fixture"],
        check=True,
    )
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()

    idea.add("First", "Body", log)
    idea.link(ONE, "relates_to", None, log=log, target_code="DOC-001", config=config)
    idea.classify(ONE, "agent-blue", {
        "record_kind": "knowledge",
        "ontological": "concept",
        "epistemic": "hypothesis",
        "lifecycle": "generative_seed",
        "temporal": "standing",
        "reasons": {"ontological": "names a concept", "epistemic": "unproven",
                    "lifecycle": "a starting point", "temporal": "no time bound"},
        "confidence": {"ontological": 0.9, "epistemic": 0.7, "lifecycle": 0.8,
                       "temporal": 0.6},
        "tie_breaks": ["O1"],
    }, log)
    idea.change_status(ONE, "delivered", log=log,
                       closes_with=[{"doc": "DOC-001"}, {"commit": head}], config=config)

    rendered = section(render_ideas.render(state_of(log)), ONE)

    assert "relates_to → document `DOC-001`" in rendered
    assert "None" not in rendered
    assert "record kind `knowledge`" in rendered
    assert "- ontological: `concept` (0.9) — names a concept" in rendered
    assert "- temporal: `standing` (0.6) — no time bound" in rendered
    assert "tie-breaks applied: O1" in rendered
    assert f"closed with doc `DOC-001`, commit `{head}`" in rendered
    assert "Status: `delivered`" in rendered


def test_an_empty_log_renders_to_the_header_alone(tmp_path: Path) -> None:
    """With no log and no priority file, the view is exactly the seeded header."""
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert render_ideas.render_view(config) == render_ideas.HEADER


# --- Rendering is deterministic -------------------------------------------------------------


def test_rendering_twice_over_a_fixture_log_is_byte_identical(tmp_path: Path, log: Path) -> None:
    """Two runs of the renderer over the same log write the same bytes."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    idea.annotate(ONE, "agent-blue", "finding", "a finding", log=log)
    idea.link(TWO, "extends", ONE, log=log)
    view = paths.resolve({"root": str(tmp_path)}, env={}).path("ideas_view_path")

    assert render_ideas.main(["--root", str(tmp_path)]) == 0
    first = view.read_bytes()
    assert render_ideas.main(["--root", str(tmp_path)]) == 0
    assert view.read_bytes() == first
    assert render_ideas.main(["--root", str(tmp_path), "--check"]) == 0


# --- A stale view is reported ---------------------------------------------------------------


def test_a_current_view_passes(config: paths.Config, log: Path) -> None:
    """A view matching a fresh render has no error."""
    idea.add("First", "Body", log)
    write_view(config)
    assert render_ideas.stale_view_errors(config) == []
    assert ideas_check.check(config, TODAY) == []


def test_an_idea_appended_without_rerendering_fails_naming_the_view(
    config: paths.Config, log: Path
) -> None:
    """An append the view does not reflect is reported until the view is re-rendered."""
    idea.add("First", "Body", log)
    write_view(config)
    idea.add("Scratch idea for the staleness test", "Appended without re-rendering.", log)

    errors = render_ideas.stale_view_errors(config)
    assert len(errors) == 1
    assert errors[0].startswith("ideas/ideas.md differs")

    write_view(config)
    assert render_ideas.stale_view_errors(config) == []


def test_a_missing_view_fails(config: paths.Config, log: Path) -> None:
    """A log without its view is reported as missing."""
    idea.add("First", "Body", log)
    errors = render_ideas.stale_view_errors(config)
    assert errors and errors[0].startswith("ideas/ideas.md is missing")


def test_a_hand_edit_to_the_view_is_reported(tmp_path: Path, config: paths.Config, log: Path,
                                             capsys: pytest.CaptureFixture[str]) -> None:
    """Editing the rendered file makes the check name the view and `--check` exit 1."""
    idea.add("First", "Body", log)
    view = write_view(config)
    view.write_text(view.read_text(encoding="utf-8").replace(f"## {ONE}", f"## {ONE} (edited)"),
                    encoding="utf-8")

    errors = ideas_check.check(config, TODAY)
    assert len(errors) == 1
    assert "ideas/ideas.md" in errors[0]

    capsys.readouterr()
    assert render_ideas.main(["--root", str(tmp_path), "--check"]) == 1
    assert "ideas/ideas.md differs" in capsys.readouterr().err


def test_a_repository_without_the_feature_gets_no_report(config: paths.Config) -> None:
    """With neither a log nor a view, the ideas check reports nothing."""
    assert ideas_check.check(config, TODAY) == []


def test_a_schema_invalid_line_is_reported(config: paths.Config, log: Path) -> None:
    """A log line that fails the schema is reported by position."""
    log.parent.mkdir(parents=True)
    log.write_text('{"idea": "1", "event": "created", "at": "whenever"}\n', encoding="utf-8")
    errors = ideas_check.check(config, TODAY)
    assert errors and all("event 1" in error for error in errors)


# --- The priority queue ---------------------------------------------------------------------


def test_render_lists_the_priority_queue_first_in_order(log: Path) -> None:
    """The queue comes before every idea section, in the order given."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)

    rendered = render_ideas.render(state_of(log), [TWO, ONE])

    queue_pos = rendered.index("## Priority queue")
    first_entry = rendered.index(f"`{TWO}` — Second")
    second_entry = rendered.index(f"`{ONE}` — First")
    first_heading = rendered.index(f"## {ONE}")
    assert queue_pos < first_entry < second_entry < first_heading


def test_render_with_no_priority_queue_omits_the_section(log: Path) -> None:
    """An empty or absent queue renders no queue section."""
    idea.add("First", "Body", log)
    state = state_of(log)

    assert "## Priority queue" not in render_ideas.render(state, [])
    assert "## Priority queue" not in render_ideas.render(state)


def test_the_view_renders_the_priority_file(config: paths.Config, log: Path) -> None:
    """The priority file on disk feeds the rendered queue."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    write_priority(config, [TWO])
    assert render_ideas.load_next_up(config.path("priority_path")) == [TWO]
    assert f"1. `{TWO}` — Second" in render_ideas.render_view(config)


def test_inspect_idea_priority_accepts_open_and_triaged_ideas() -> None:
    """Open and triaged ideas may be queued."""
    state = {ONE: {"status": "open"}, TWO: {"status": "triaged"}}
    catalog = {"updated": TODAY.isoformat(), "next_up": [TWO, ONE]}
    assert ideas_check.inspect_idea_priority(catalog, state, TODAY) == []


def test_inspect_idea_priority_rejects_unknown_and_terminal_ideas() -> None:
    """An unknown idea or one past scouting is named."""
    state = {ONE: {"status": "promoted"}}
    catalog = {"updated": TODAY.isoformat(), "next_up": [ONE, TWO]}

    errors = ideas_check.inspect_idea_priority(catalog, state, TODAY)

    assert any(f"{ONE} is promoted" in error for error in errors)
    assert any(f"unknown idea {TWO}" in error for error in errors)


def test_inspect_idea_priority_rejects_a_future_updated_date() -> None:
    """The queue cannot be dated after today."""
    future = TODAY + dt.timedelta(days=4)
    catalog = {"updated": future.isoformat(), "next_up": []}

    errors = ideas_check.inspect_idea_priority(catalog, {}, TODAY)

    assert any("in the future" in error for error in errors)


def test_a_valid_priority_queue_passes_the_check(config: paths.Config, log: Path) -> None:
    """A queue of open and triaged ideas, dated today, with a current view, is clean."""
    idea.add("First", "Body", log)
    idea.add("Second", "Body two", log)
    idea.change_status(TWO, "triaged", log=log)
    write_priority(config, [TWO, ONE])
    write_view(config)
    assert ideas_check.check(config, TODAY) == []


def test_a_queue_naming_an_unknown_idea_fails_the_check(config: paths.Config,
                                                        log: Path) -> None:
    """The check names the unknown id."""
    idea.add("First", "Body", log)
    write_priority(config, [ONE, NINE])
    write_view(config)
    errors = ideas_check.check(config, TODAY)
    assert errors == [f"ideas/priority.yaml: next_up names unknown idea {NINE}"]


def test_a_queue_naming_a_promoted_idea_fails_the_check(config: paths.Config,
                                                        log: Path) -> None:
    """The check names the queued idea that is no longer open or triaged."""
    idea.add("First", "Body", log)
    idea.change_status(ONE, "promoted", promoted_to=["DOC-001"], log=log)
    write_priority(config, [ONE])
    write_view(config)
    errors = ideas_check.check(config, TODAY)
    assert len(errors) == 1
    assert f"{ONE} is promoted, not open or triaged" in errors[0]


def test_a_queue_dated_in_the_future_fails_the_check(config: paths.Config, log: Path) -> None:
    """The check names the future date."""
    idea.add("First", "Body", log)
    future = TODAY + dt.timedelta(days=1)
    write_priority(config, [ONE], updated=future)
    write_view(config)
    errors = ideas_check.check(config, TODAY)
    assert len(errors) == 1
    assert f"updated {future.isoformat()} is in the future" in errors[0]


def test_a_queue_failing_its_schema_fails_the_check(config: paths.Config, log: Path) -> None:
    """A malformed queue is reported by its schema before any cross-file check."""
    idea.add("First", "Body", log)
    priority = config.path("priority_path")
    priority.write_text("schema_version: 1\nnext_up: ['1']\n", encoding="utf-8")
    write_view(config)
    errors = ideas_check.check(config, TODAY)
    assert errors and all(error.startswith("ideas/priority.yaml") for error in errors)
