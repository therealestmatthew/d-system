"""The idea realization engine pages — REQ-036 R07-R23.

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


@pytest.fixture(scope="module")
def ledger(inputs: dict) -> str:
    return gen.render_ledger(inputs)


@pytest.fixture(scope="module")
def backlog(inputs: dict) -> str:
    return gen.render_backlog(inputs)


@pytest.fixture(scope="module")
def pages(inputs: dict) -> dict[str, str]:
    return gen.render_all(inputs)


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
    names = sorted(str(p.relative_to(first)) for p in first.rglob("*.html"))
    assert names == sorted(str(p.relative_to(second)) for p in second.rglob("*.html"))
    assert names == sorted(gen.render_all(gen.load_inputs()))
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_stamp_is_the_source_commit_and_its_own_date(pages: dict[str, str]) -> None:
    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    date = subprocess.run(
        ["git", "-C", str(ROOT), "show", "-s", "--format=%cs", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    for name, page in pages.items():
        assert f"Source commit <code>{commit}</code>" in page, name
        assert f"Commit date {date}" in page, name


def test_uncommitted_input_changes_are_stated() -> None:
    stamp = {"commit": "0" * 12, "date": "2026-10-01", "dirty": True}
    assert "Inputs had uncommitted changes" in gen._stamp_meta(stamp)
    assert "uncommitted" not in gen._stamp_meta({**stamp, "dirty": False})


def test_no_ci_step_compares_the_pages_with_a_regeneration() -> None:
    for workflow in (ROOT / ".github" / "workflows").glob("*.y*ml"):
        text = workflow.read_text(encoding="utf-8")
        assert "_public/engine" not in text, workflow.name
        assert "generate_engine_pages" not in text, workflow.name


@pytest.mark.parametrize("name", sorted(gen.PAGES))
def test_each_committed_page_is_a_generated_page(name: str) -> None:
    committed = (ROOT / "_public" / "engine" / name).read_text(encoding="utf-8")
    assert committed.startswith("<!doctype html>")
    assert "Source commit <code>" in committed
    assert "Generated by tools/generate_engine_pages.py" in committed


# ---- R09, R10, R12: house family, fold() only, no script ----


def test_no_colour_literal_outside_the_house_token_css(pages: dict[str, str]) -> None:
    tokens_css = house.OUTPUT.read_text(encoding="utf-8")
    for name, page in pages.items():
        assert tokens_css in page, f"{name} does not inline the generated house.css"
        found = COLOUR_LITERAL.findall(page.replace(tokens_css, ""))
        assert not found, f"{name}: colour literals outside house.css: {found}"


def test_page_is_built_from_the_house_family(pages: dict[str, str]) -> None:
    for name, page in pages.items():
        assert house.COMPONENTS_CSS.read_text(encoding="utf-8") in page, name
        for cls in ('class="page"', 'class="stats"', 'class="callout"', 'class="tbl-wrap"'):
            assert cls in page, (name, cls)
    assert 'class="gate"' in pages["index.html"]


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


# ---- R15 and R16: the idea funnel and ledger ----


def _classified_ids() -> set[str]:
    """Ideas with a classified event, read from the raw event list rather than the folded record."""
    return {e["idea"] for e in load_events(ROOT / "_data" / "ideas.jsonl")
            if e.get("event") == "classified"}


def test_ledger_lists_every_folded_idea_exactly_once(ledger: str) -> None:
    ids = re.findall(r'<tr data-idea="([^"]+)">', ledger)
    assert len(ids) == len(set(ids)), "an idea appears twice"
    assert set(ids) == set(_ideas())


def test_ledger_row_carries_id_title_status_created_and_four_axes(ledger: str) -> None:
    ideas = _ideas()
    key = sorted(ideas)[0]
    row = re.search(rf'<tr data-idea="{key}">(.*?)</tr>', ledger)
    assert row
    cells = [html.unescape(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row.group(1))]
    idea = ideas[key]
    assert cells[:4] == [key, idea["title"], idea["status"], idea["created"][:10]]
    assert len(cells) == 4 + 4 + 1, "four axis columns and a trace column"


def test_funnel_counts_match_a_recount_and_sum_to_the_total(ledger: str) -> None:
    ideas = _ideas()
    counts = dict(re.findall(r'data-funnel="([^"]+)">(\d+)<', ledger))
    assert sum(int(n) for n in counts.values()) == len(ideas)
    for status in {i["status"] for i in ideas.values()}:
        assert counts[status] == str(sum(1 for i in ideas.values() if i["status"] == status))
    assert _figure(ledger, "stat", "ideas") == str(len(ideas))


@pytest.mark.parametrize("axis", ["ontological", "epistemic", "lifecycle", "temporal"])
def test_unclassified_equals_ideas_with_no_classified_event(ledger: str, axis: str) -> None:
    unclassified = len(set(_ideas()) - _classified_ids())
    assert _figure(ledger, f"axis-{axis}", "unclassified") == str(unclassified)
    counts = re.findall(rf'data-axis-{axis}="[^"]+">(\d+)<', ledger)
    assert sum(int(n) for n in counts) == len(_ideas())


def test_every_schema_axis_value_is_listed(ledger: str) -> None:
    import json

    schema = json.loads((ROOT / "schemas" / "idea.schema.json").read_text("utf-8"))
    properties = schema["properties"]
    for axis in ("ontological", "epistemic", "lifecycle", "temporal"):
        for value in properties[axis]["enum"]:
            _figure(ledger, f"axis-{axis}", value)


def test_a_classified_record_counts_under_its_value_or_its_record_kind(inputs: dict) -> None:
    ideas = dict(inputs["ideas"])
    first, second, *_ = sorted(ideas)
    knowledge = {"record_kind": "knowledge", "ontological": "process", "epistemic": "hypothesis",
                 "lifecycle": "operational_task", "temporal": "standing"}
    ideas[first] = {**ideas[first], "classification": knowledge}
    ideas[second] = {**ideas[second], "classification": {"record_kind": "fixture"}}
    data = gen.ledger_data({**inputs, "ideas": ideas})
    ontological = dict(data["axes"]["ontological"])
    assert ontological["process"] == 1
    assert ontological["no axes (fixture)"] == 1
    assert ontological["unclassified"] == len(ideas) - 2
    assert sum(ontological.values()) == len(ideas)
    assert data["classified"] == 2


def test_ideas_without_a_recorded_plan_say_so(inputs: dict, ledger: str) -> None:
    linked = {i for p in inputs["phases"] for i in p.get("ideas", [])}
    expected = sum(
        1 for key, idea in _ideas().items() if not idea["promoted_to"] and key not in linked
    )
    assert len(re.findall(rf'data-trace="[^"]+">{gen.NO_RECORDED_PLAN}<', ledger)) == expected


def test_overview_and_ledger_link_to_each_other(page: str, ledger: str) -> None:
    assert 'href="ideas.html"' in page
    assert 'href="index.html"' in ledger


# ---- R21 to R23: the backlog and batch graph ----


def _batch_tables() -> list[dict]:
    return [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "docs/09-backlog/batches").glob("batch-*.yaml"))
    ]


def _expected_states() -> dict[str, str]:
    """Each phase's state, through the governance readiness function and nothing of the page's."""
    from src.governance.backlog import readiness

    items = {p["id"]: p for p in _phases()}
    return {key: readiness(item, items) for key, item in items.items()}


def _row(page: str, key: str) -> str:
    match = re.search(rf'<tr data-phase="{re.escape(key)}"[^>]*>(.*?)</tr>', page)
    assert match, f"no row for {key}"
    return match.group(1)


def test_every_phase_appears_once_with_the_governance_state(backlog: str) -> None:
    rows = re.findall(r'<tr data-phase="([^"]+)" data-state="([^"]+)">', backlog)
    keys = [key for key, _ in rows]
    assert len(keys) == len(set(keys)), "a phase appears twice"
    assert dict(rows) == _expected_states()


def test_state_counts_sum_to_every_phase(backlog: str) -> None:
    expected = _expected_states()
    counts = dict(re.findall(r'data-state-count="([^"]+)">(\d+)<', backlog))
    assert sum(int(n) for n in counts.values()) == len(expected)
    for state in set(expected.values()):
        assert counts[state] == str(sum(1 for s in expected.values() if s == state)), state
    assert _figure(backlog, "stat", "phases") == str(len(expected))


def test_each_batch_matches_its_yaml(backlog: str) -> None:
    states = _expected_states()
    for table in _batch_tables():
        start = backlog.index(f'data-batch="{table["id"]}"')
        end = backlog.find('data-batch="', start + 1)
        block = backlog[start:end if end != -1 else len(backlog)]
        listed = re.findall(r'data-batch-phase="([^"]+)" data-stage="(\d+)"', block)
        expected = [(p["id"], str(s["stage"])) for s in table["stages"] for p in s["phases"]]
        assert listed == expected, table["id"]
        for key, _ in expected:
            assert f'data-node="{key}" data-node-state="{states[key]}"' in block, (table["id"], key)
        for entry in table.get("external_depends_on") or []:
            assert f'data-external="{entry["id"]}"' in block, (table["id"], entry["id"])
            assert f'data-node="{entry["id"]}"' in block, (table["id"], entry["id"])


def test_every_in_graph_dependency_is_drawn_as_an_edge(backlog: str) -> None:
    items = {p["id"]: p for p in _phases()}
    for table in _batch_tables():
        start = backlog.index(f'data-graph="{table["id"]}"')
        svg = backlog[start:backlog.index("</svg>", start)]
        drawn = set(re.findall(r'data-edge="([^&]+)&gt;([^"]+)"', svg))
        members = [p["id"] for s in table["stages"] for p in s["phases"]]
        expected = {(dep, key) for key in members for dep in items[key]["depends_on"]}
        assert drawn == expected, table["id"]


def test_the_graphs_are_static_svg(backlog: str) -> None:
    assert "<script" not in backlog.lower()
    assert backlog.count('<svg class="graph"') == len(_batch_tables())
    for svg in re.findall(r"<svg.*?</svg>", backlog, re.S):
        assert not re.search(r"\son[a-z]+=", svg), "an event handler in the graph"


def test_arrows_are_drawn_beneath_the_boxes(backlog: str) -> None:
    """An arrow that skips a stage passes behind the boxes between, not through their text."""
    for svg in re.findall(r"<svg.*?</svg>", backlog, re.S):
        if 'class="edge"' in svg:
            assert svg.rindex('class="edge"') < svg.index('<g class="node'), "an arrow over a box"


def test_every_waiting_phase_lists_its_unmet_dependencies(backlog: str) -> None:
    items = {p["id"]: p for p in _phases()}
    states = _expected_states()
    for key, state in states.items():
        if state != "waiting":
            continue
        unmet = re.findall(r'data-unmet="([^"]+)"', _row(backlog, key))
        assert unmet, f"{key} is waiting but lists no dependency"
        assert unmet == [d for d in items[key]["depends_on"] if items[d]["status"] != "complete"]
        for dependency in unmet:
            assert f"{dependency}</code> ({states[dependency]})" in _row(backlog, key)


def test_every_blocked_or_deferred_phase_shows_both_fields(backlog: str) -> None:
    for phase in _phases():
        if phase["status"] not in ("blocked", "deferred"):
            continue
        row = html.unescape(_row(backlog, phase["id"]))
        assert f"Reason: {phase['blocked_reason']}" in row, phase["id"]
        assert f"Resume when: {phase['resume_when']}" in row, phase["id"]


def test_a_missing_field_reads_not_recorded(inputs: dict) -> None:
    phases = [
        {k: v for k, v in p.items() if k != "resume_when"} if p["status"] == "deferred" else p
        for p in inputs["phases"]
    ]
    page = gen.render_backlog({**inputs, "phases": phases})
    key = next(p["id"] for p in phases if p["status"] == "deferred")
    assert f"Resume when: {gen.NOT_RECORDED}" in _row(page, key)


def test_the_layout_choice_is_stated_on_the_page(backlog: str) -> None:
    assert "the graph is drawn per batch table" in html.unescape(backlog)
    assert "not the orchestrator's batch graph" in html.unescape(backlog)


def test_overview_links_to_the_backlog_page(page: str, backlog: str) -> None:
    assert 'href="backlog.html"' in page
    assert 'href="index.html"' in backlog


# ---- R19 and R20: the per-idea trace pages ----


#: An idea with a known history: promoted through no plan of its own, linked by phase-idg-01
#: (complete) and phase-idg-14, both under PLAN-029, and carrying an owner ruling.
KNOWN_IDEA, KNOWN_PLAN, KNOWN_PHASE = "000236", "PLAN-029", "phase-idg-01"


def _linked_ideas() -> set[str]:
    """Ideas with promoted_to or named by a phase's ideas field, read without the generator."""
    named = {i for p in _phases() for i in p.get("ideas", [])}
    return {key for key, idea in _ideas().items() if idea["promoted_to"] or key in named}


def _git_lines(*args: str) -> list[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.splitlines()


def _git_show(spec: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", spec], capture_output=True, text=True, check=True
    ).stdout


def _gate_rows(page: str, gate: str) -> dict[str, str]:
    """Each row of one gate on a trace page, keyed by its subject, unescaped."""
    rows = re.findall(
        rf'<tr data-gate-entry="{re.escape(html.escape(gate))}" data-subject="([^"]+)">(.*?)</tr>',
        page,
    )
    return {html.unescape(subject): html.unescape(row) for subject, row in rows}


def test_trace_pages_are_exactly_the_linked_ideas(pages: dict[str, str]) -> None:
    traced = {name[len("trace/"):-len(".html")] for name in pages if name.startswith("trace/")}
    assert traced == _linked_ideas()


def test_ledger_links_each_traced_idea_and_no_other(ledger: str) -> None:
    linked = _linked_ideas()
    for key in _ideas():
        cell = re.search(rf'data-trace="{key}">(.*?)</td>', ledger)
        assert cell, key
        if key in linked:
            assert cell.group(1) == f'<a href="trace/{key}.html">trace</a>', key
        else:
            assert cell.group(1) == gen.NO_RECORDED_PLAN, key


def test_a_stale_trace_page_is_removed(tmp_path: Path) -> None:
    stale = tmp_path / "trace" / "999999.html"
    stale.parent.mkdir(parents=True)
    stale.write_text("old", encoding="utf-8")
    assert gen.main(["--out", str(tmp_path)]) == 0
    assert not stale.exists()


def test_the_line_scan_reads_the_same_complete_phases_as_yaml() -> None:
    text = (ROOT / "docs/09-backlog/backlog.yaml").read_text(encoding="utf-8")
    assert gen._complete_phases(text) == {p["id"] for p in _phases() if p["status"] == "complete"}


def _first_plan_approval(code: str) -> tuple[str, str]:
    """The earliest first-parent commit where the plan reads a G3 status, walking every version
    of its file and reading the front matter's status line."""
    path = next((ROOT / "docs/01-plans").rglob(f"{code}-*.md")).relative_to(ROOT)
    for line in _git_lines("log", "--first-parent", "--reverse", "--format=%H %cs", "--follow",
                           "--", str(path)):
        commit, date = line.split()
        text = _git_show(f"{commit}:{path}")
        status = re.search(r"^status: (\w+)$", text.split("---\n", 2)[1], re.M)
        if status and status.group(1) in ("approved", "active", "complete"):
            return commit[:12], date
    raise AssertionError(f"{code} never read a G3 status")


def _first_completion(phase: str) -> tuple[str, str]:
    """The earliest first-parent commit where the phase reads complete, reading every version of
    backlog.yaml (not only the generator's -G candidates) and matching the status key in the
    phase's own block. A regex, not YAML: commit 5ec45ea's backlog.yaml does not parse."""
    path = "docs/09-backlog/backlog.yaml"
    block = re.compile(rf"^- id: {re.escape(phase)}\n(?:  .*\n|\n)*", re.M)
    for line in _git_lines("log", "--first-parent", "--diff-merges=first-parent", "-s", "--reverse",
                           "--format=%H %cs", "--", path):
        commit, date = line.split()
        match = block.search(_git_show(f"{commit}:{path}"))
        if match and re.search(r"^  status: complete$", match.group(0), re.M):
            return commit[:12], date
    raise AssertionError(f"{phase} never read complete")


def test_a_known_idea_traces_to_the_git_log_and_the_fold(pages: dict[str, str]) -> None:
    idea = _ideas()[KNOWN_IDEA]
    page = pages[f"trace/{KNOWN_IDEA}.html"]

    g1 = _gate_rows(page, "G1")["captured"]
    assert f"<td data-date>{idea['created'][:10]}</td>" in g1
    assert "fold(): the idea's created event" in g1

    assert gen.NOT_RECORDED in _gate_rows(page, "G2")["partition"]
    assert "no structured partition record exists" in _gate_rows(page, "G2")["partition"]

    commit, date = _first_plan_approval(KNOWN_PLAN)
    g3 = _gate_rows(page, "G3")[KNOWN_PLAN]
    assert f"<td data-date>{date}</td>" in g3 and f"<code data-commit>{commit}</code>" in g3
    assert "front matter reads approved, active or complete" in g3

    commit, date = _first_completion(KNOWN_PHASE)
    g45 = _gate_rows(page, "G4 and G5")[KNOWN_PHASE]
    assert f"<td data-date>{date}</td>" in g45 and f"<code data-commit>{commit}</code>" in g45
    assert "backlog.yaml shows the phase complete" in g45

    rulings = [note for note in idea["annotations"] if note["kind"] == "assessment"]
    assert rulings, "the known idea carries an owner ruling"
    shown = html.unescape(page)
    for note in rulings:
        assert note["text"] in shown
    assert page.count('data-gate-entry="Ruling"') == len(rulings)


def test_every_trace_names_a_source_for_every_gate_entry(pages: dict[str, str]) -> None:
    for name, page in pages.items():
        if not name.startswith("trace/"):
            continue
        rows = re.findall(r"<tr data-gate-entry=.*?</tr>", page)
        assert rows, name
        for row in rows:
            source = re.search(r"<td data-source>([^<]+)</td>", row)
            assert source and source.group(1).strip(), (name, row)
        assert 'data-gate-entry="G2"' in page, name


def test_a_trace_shows_capture_then_plan_then_phases_then_delivery(pages: dict[str, str]) -> None:
    page = pages[f"trace/{KNOWN_IDEA}.html"]
    order = [page.index(f"<h2>{n}. {title}</h2>")
             for n, title in enumerate(("Capture", "Plan", "Phases", "Delivery"), start=1)]
    assert order == sorted(order)
    states = _expected_states()
    for key, state in re.findall(r'<tr data-phase="([^"]+)" data-state="([^"]+)">', page):
        assert states[key] == state, key


def test_a_promotion_to_a_non_plan_is_not_recorded_at_g3(inputs: dict) -> None:
    key = next(k for k, i in inputs["ideas"].items()
               if i["promoted_to"] and not any(
                   t in {str(p["code"]) for p in inputs["plans"]}
                   or t in {str(p["id"]) for p in inputs["plans"]} for t in i["promoted_to"]))
    data = gen.trace_data(inputs, key)
    target = data["plans"][0]
    assert target["g3"]["date"] == gen.NOT_RECORDED
    assert "is not a plan document" in target["g3"]["note"]


def test_a_shallow_history_dates_nothing(inputs: dict) -> None:
    shallow = {"shallow": True, "root_commits": [], "plans": {}, "phases": {}}
    data = gen.trace_data({**inputs, "history": shallow}, KNOWN_IDEA)
    for entry in [p["g3"] for p in data["plans"]] + [r["g45"] for r in data["phases"]]:
        assert entry["date"] == gen.NOT_RECORDED and "shallow clone" in entry["note"]
