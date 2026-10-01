"""The idea realization engine pages — REQ-036 R07-R14.

Every figure on the pipeline overview is recomputed here by code that shares nothing with the
generator's own `STAGES` and `GATES` selectors except `fold()`, which is the sanctioned reader the
requirement mandates for both (R10). Most figures have one plausible computation. G2 does not, so
its recount takes a different route from the generator: phase links from each phase's text rather
than its `ideas` field, and the set built by subtraction. A count that drifts fails here.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.ideas import fold, load_events  # noqa: E402
from tools import generate_engine_pages as gen  # noqa: E402
from tools import generate_house_css as house  # noqa: E402

COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")


@pytest.fixture(scope="module")
def inputs() -> dict:
    return gen.load_inputs()


@pytest.fixture(scope="module")
def page(inputs: dict) -> str:
    return gen.render_overview(inputs)


def _figure(page: str, attr: str, key: str) -> str:
    match = re.search(rf'data-{attr}="{re.escape(key)}">([^<]+)<', page)
    assert match, f"no data-{attr}={key!r} on the page"
    return match.group(1)


# ---- independent recomputation, from the raw inputs ----


def _ideas() -> dict:
    return fold(load_events(ROOT / "_data" / "ideas.jsonl"))


def _phases() -> list[dict]:
    return yaml.safe_load((ROOT / "docs/09-backlog/backlog.yaml").read_text("utf-8"))["items"]


def _draft_plans() -> list[str]:
    codes = []
    for path in sorted((ROOT / "docs/01-plans").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        meta = yaml.safe_load(text.split("---\n", 2)[1]) or {}
        if meta.get("kind") == "plan" and meta.get("status") == "draft":
            codes.append(str(meta["code"]))
    return codes


def _queued_split() -> tuple[int, int]:
    """(queued phases, active phases), computed without the generator."""
    phases = _phases()
    queued = sum(1 for p in phases if p["status"] == "queued")
    active = sum(1 for p in phases if p["status"] == "active")
    return queued, active


def _g2() -> set[str]:
    """G2 by a second route: phase links read from each phase's own text, not its ideas field.

    The generator reads the backlog `ideas` field. This reads the text that field was backfilled
    from, through `named_ideas`, and builds the set by subtraction. If the field and the text ever
    disagree, this recount and the page disagree, and the test says so.
    """
    from src.governance.backlog import named_ideas

    ideas = _ideas()
    known = set(ideas)
    linked_from_text = {i for p in _phases() for i in named_ideas(p, known)}
    triaged = {key for key, idea in ideas.items() if idea["status"] == "triaged"}
    promoted = {key for key, idea in ideas.items() if idea["promoted_to"]}
    return triaged - promoted - linked_from_text


# ---- R14 and R11: every figure matches its stated derivation ----


def test_stage_counts_match_an_independent_recount(page: str) -> None:
    ideas = _ideas()
    queued, active = _queued_split()
    expected = {
        "1": str(len(ideas)),
        "2": str(sum(1 for i in ideas.values() if i["status"] == "open")),
        "3": str(len(_g2())),
        "4": str(len(_draft_plans())),
        "5": gen.NOT_RECORDED,
        "6": gen.NOT_RECORDED,
        "7": str(queued),
        "8": str(active),
        "9": str(sum(1 for i in ideas.values() if i["status"] == "delivered")),
    }
    for stage, value in expected.items():
        assert _figure(page, "stage", stage) == value, f"stage {stage}"


def test_gate_queues_match_an_independent_recount(page: str) -> None:
    _, active = _queued_split()
    assert _figure(page, "gate", "G1") == str(len(_ideas()))
    assert _figure(page, "gate", "G2") == str(len(_g2()))
    assert _figure(page, "gate", "G3") == str(len(_draft_plans()))
    assert _figure(page, "gate", "G4 and G5") == str(active)


def test_headline_stats_match_an_independent_recount(page: str) -> None:
    ideas, phases = _ideas(), _phases()
    assert _figure(page, "stat", "ideas") == str(len(ideas))
    assert _figure(page, "stat", "triaged") == str(
        sum(1 for i in ideas.values() if i["status"] == "triaged")
    )
    assert _figure(page, "stat", "complete") == str(
        sum(1 for p in phases if p["status"] == "complete")
    )


def test_every_draft_plan_is_listed_under_g3(page: str) -> None:
    for code in _draft_plans():
        assert f'<td class="id">{code}</td>' in page, code


def test_stages_without_a_record_say_so_and_name_the_gap(page: str) -> None:
    for stage in (5, 6):
        assert _figure(page, "stage", str(stage)) == gen.NOT_RECORDED
    assert "no structured review record exists" in page
    assert "no structured phase-fit record exists" in page


def test_stage_4_and_g3_are_stated_to_be_the_same_set(page: str) -> None:
    assert _figure(page, "stage", "4") == _figure(page, "gate", "G3")
    assert "Stage 4 and the G3 queue are the same plans by construction" in page


def test_g2_falls_back_when_no_phase_carries_the_ideas_field(inputs: dict) -> None:
    stripped = {
        **inputs,
        "phases": [{k: v for k, v in p.items() if k != "ideas"} for p in inputs["phases"]],
    }
    expected = {
        key for key, idea in inputs["ideas"].items()
        if idea["status"] == "triaged" and not idea["promoted_to"]
    }
    assert gen.linked_ideas(stripped) is None
    assert set(gen.g2_queue(stripped)) == expected
    assert "Phase links: not recorded." in gen.render_overview(stripped)


def test_the_ideas_field_is_used_when_present(inputs: dict, page: str) -> None:
    assert gen.linked_ideas(inputs) is not None
    assert "Phase links come from backlog phases' ideas field" in html.unescape(page)


def test_queued_phases_split_by_the_governance_readiness_function(inputs: dict) -> None:
    from src.governance.backlog import readiness

    items = {p["id"]: p for p in inputs["phases"]}
    states = gen.phase_states(inputs["phases"])
    for key, item in items.items():
        if item["status"] == "queued":
            assert states[key] == readiness(item, items)
        else:
            assert states[key] == item["status"]


# ---- R07 and R08: determinism, the stamp, and no currency gate ----


def test_two_runs_into_temporary_directories_are_byte_identical(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    assert gen.main(["--out", str(first)]) == 0
    assert gen.main(["--out", str(second)]) == 0
    names = sorted(p.name for p in first.iterdir())
    assert names == sorted(p.name for p in second.iterdir()) == sorted(gen.PAGES)
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_stamp_is_the_source_commit_and_its_own_date(page: str) -> None:
    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    date = subprocess.run(
        ["git", "-C", str(ROOT), "show", "-s", "--format=%cs", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert f"Source commit <code>{commit}</code>" in page
    assert f"Commit date {date}" in page


def test_uncommitted_input_changes_are_stated() -> None:
    stamp = {"commit": "0" * 12, "date": "2026-10-01", "dirty": True}
    assert "Inputs had uncommitted changes" in gen._stamp_meta(stamp)
    assert "uncommitted" not in gen._stamp_meta({**stamp, "dirty": False})


def test_no_ci_step_compares_the_pages_with_a_regeneration() -> None:
    for workflow in (ROOT / ".github" / "workflows").glob("*.y*ml"):
        text = workflow.read_text(encoding="utf-8")
        assert "_public/engine" not in text, workflow.name
        assert "generate_engine_pages" not in text, workflow.name


def test_the_committed_overview_is_a_generated_page() -> None:
    committed = (ROOT / "_public" / "engine" / "index.html").read_text(encoding="utf-8")
    assert committed.startswith("<!doctype html>")
    assert "Source commit <code>" in committed
    assert "Generated by tools/generate_engine_pages.py" in committed


# ---- R09, R10, R12: house family, fold() only, no script ----


def test_no_colour_literal_outside_the_house_token_css(page: str) -> None:
    tokens_css = house.OUTPUT.read_text(encoding="utf-8")
    assert tokens_css in page, "the page does not inline the generated house.css"
    found = COLOUR_LITERAL.findall(page.replace(tokens_css, ""))
    assert not found, f"colour literals outside house.css: {found}"


def test_page_is_built_from_the_house_family(page: str) -> None:
    assert house.COMPONENTS_CSS.read_text(encoding="utf-8") in page
    for cls in ('class="page"', 'class="stats"', 'class="callout"', 'class="gate"'):
        assert cls in page


def test_the_generator_reads_the_idea_log_only_through_fold() -> None:
    source = (ROOT / "tools" / "generate_engine_pages.py").read_text(encoding="utf-8")
    for line in source.splitlines():
        reads = "open(" in line or "read_text(" in line or "read_bytes(" in line
        if reads and "ideas" in line:
            assert "load_events" in line, f"reads the idea log directly: {line.strip()}"
    assert "fold(load_events(" in source
    assert "json.loads" not in source


def test_pages_contain_no_script(inputs: dict) -> None:
    for name, text in gen.render_all(inputs).items():
        assert "<script" not in text.lower(), name
