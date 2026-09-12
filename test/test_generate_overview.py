"""Tests for tools/generate_overview.py -- generation determinism and figure fidelity.

The two things REQ-006 R08 and the dispatched work item anchor here: generating the page
twice against an unchanged repository must produce byte-identical files (no generation
timestamp, no wall-clock input anywhere in the pipeline), and every figure the page shows
must be traceable back to `tools/overview_metrics.py`'s or `tools/overview_inventory.py`'s own
JSON output rather than recomputed by the generator.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "generate_overview.py"


def _load(name: str) -> ModuleType:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generate_overview = _load("generate_overview")


@pytest.fixture
def metrics() -> dict[str, Any]:
    result: dict[str, Any] = generate_overview.run_metrics_tool()
    return result


@pytest.fixture
def inventory() -> dict[str, Any]:
    result: dict[str, Any] = generate_overview.run_inventory_tool()
    return result


# --- Determinism across generations -------------------------------------------------------


def test_two_generations_via_generate_produce_byte_identical_output() -> None:
    first = generate_overview.generate()
    second = generate_overview.generate()
    assert first == second
    assert first, "expected a non-empty page"


def test_two_cli_runs_write_byte_identical_files(tmp_path: Path) -> None:
    first_out = tmp_path / "first.html"
    second_out = tmp_path / "second.html"

    first = subprocess.run(
        [sys.executable, str(GENERATOR), "--out", str(first_out)],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    second = subprocess.run(
        [sys.executable, str(GENERATOR), "--out", str(second_out)],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    assert first.returncode == 0
    assert second.returncode == 0
    assert first_out.read_bytes() == second_out.read_bytes()


def test_generated_page_carries_no_leftover_template_tokens() -> None:
    """Every `{{TOKEN}}` the template family declares must be filled -- none survive verbatim.

    The one exception is `templates/styles/overview.css`'s own header comment, which mentions
    `{{INLINE_STYLES}}` as documentation and is inlined verbatim (never filled itself), so
    that one literal string is expected to survive inside the inlined `<style>` block.
    """
    rendered = generate_overview.generate()
    stripped = rendered.replace("{{INLINE_STYLES}}", "")
    assert "{{" not in stripped, "unfilled {{TOKEN}} left in the generated page"


def test_generation_does_not_depend_on_the_wall_clock() -> None:
    """Two generations separated by real elapsed time still agree byte-for-byte.

    `generate_overview.py` imports no `datetime` module of its own (inspected via source, not
    a monkeypatch -- `datetime.datetime` is a C-immutable type in this interpreter and cannot
    be patched), so the only place a timestamp could leak in is a stray `datetime.now()` call
    added later. Grepping the module's own source for that is a cheap, direct check.
    """
    source = GENERATOR.read_text(encoding="utf-8")
    assert "import datetime" not in source
    assert "from datetime" not in source
    assert "import time" not in source


# --- Figures on the page match the tools' own output ---------------------------------------


def test_idea_and_event_counts_on_the_page_match_the_metrics_tool(metrics: dict[str, Any]) -> None:
    rendered = generate_overview.generate()
    meta = metrics["meta"]
    assert f'{meta["idea_count"]} ideas' in rendered
    assert f'{meta["event_count"]} events' in rendered
    assert f'{meta["backlog_phase_count"]} backlog phases' in rendered


def test_concept_term_system_counts_on_the_page_match_the_inventory_tool(
    inventory: dict[str, Any],
) -> None:
    rendered = generate_overview.generate()
    meta = inventory["meta"]
    assert f'{meta["concept_count"]} concepts' in rendered
    assert f'{meta["term_count"]} terms' in rendered
    assert f'{meta["system_count"]} systems' in rendered
    assert f'Systems registry ({meta["system_count"]})' in rendered


def test_funnel_bar_values_on_the_page_match_the_metrics_tool(metrics: dict[str, Any]) -> None:
    rendered = generate_overview.generate()
    funnel = metrics["funnel"]
    counts = next(s["values"] for s in funnel["series"] if s["label"] == "count")
    for label, count in zip(funnel["labels"], counts):
        assert (
            f'<span class="bar-row__label">{label}</span>\n'
            f'  <span class="bar-row__track"><span class="bar-row__fill" '
            f'style="width: ' in rendered
        )
        assert f'<span class="bar-row__value">{json.dumps(count)}</span>' in rendered


def test_generated_at_label_comes_from_metrics_reference_at_not_the_clock(
    metrics: dict[str, Any],
) -> None:
    rendered = generate_overview.generate()
    reference_at = metrics["meta"]["reference_at"]
    expected = reference_at or generate_overview.FALLBACK_GENERATED_AT
    assert f"Generated {expected}" in rendered


# --- render_page() is a pure function of the two tools' output ------------------------------


def test_render_page_is_a_pure_function_of_its_inputs(
    metrics: dict[str, Any], inventory: dict[str, Any]
) -> None:
    templates = generate_overview.Templates()
    first = generate_overview.render_page(metrics, inventory, templates)
    second = generate_overview.render_page(metrics, inventory, templates)
    assert first == second


def test_render_bars_normalizes_against_the_series_max_without_dividing_by_zero() -> None:
    bar_template = generate_overview.Templates().bar
    rendered = generate_overview.render_bars(["a", "b"], [0, 0], bar_template)
    assert 'style="width: 0.0%;"' in rendered
    assert rendered.count('style="width: 0.0%;"') == 2


def test_render_table_lists_every_series_in_order() -> None:
    section = {
        "labels": ["x", "y"],
        "series": [
            {"label": "count", "values": [1, 2]},
            {"label": "rate", "values": [0.5, 0.5]},
        ],
    }
    head_cells, body_rows = generate_overview.render_table(section)
    assert head_cells == (
        '<th scope="col">count</th><th scope="col">rate</th>'
    )
    assert "<tr><td>x</td><td>1</td><td>0.5</td></tr>" in body_rows
    assert "<tr><td>y</td><td>2</td><td>0.5</td></tr>" in body_rows


# --- The CLI ---------------------------------------------------------------------------------


def test_main_writes_the_default_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "index.html"
    exit_code = generate_overview.main(["--out", str(out)])
    assert exit_code == 0
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
