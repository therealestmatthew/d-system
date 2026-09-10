"""Tests for tools/overview_metrics.py -- determinism and independent recomputation.

Two things anchor this file. First, the acceptance criterion from idea `000071` and REQ-006 R07:
running the tool twice against an unchanged repository must produce byte-identical output, both
as a subprocess (the way it is actually run) and as a direct call to `render()` (the way it is
easiest to assert). Second, the funnel counts the tool reports must match an independent
recomputation over the same log via `fold()` -- the tool must not silently diverge from the
projection it is supposed to summarise. A handful of zero-row tests pin the "zero counts appear
as zero rows, never omitted" requirement against a synthetic single-idea log, where every status,
transition and link type but one is genuinely unseen.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from src.db.ideas import LINK_TYPES, fold, legal_transitions, load_events

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


overview_metrics = _load("overview_metrics")
append_idea = _load("append_idea")


@pytest.fixture
def log(tmp_path: Path) -> Path:
    return tmp_path / "ideas.jsonl"


@pytest.fixture
def backlog(tmp_path: Path) -> Path:
    path = tmp_path / "backlog.yaml"
    path.write_text(
        "schema_version: 1\n"
        "items:\n"
        "- id: phase-a\n"
        "  status: queued\n"
        "- id: phase-b\n"
        "  status: complete\n",
        encoding="utf-8",
    )
    return path


def _values(section: dict[str, Any], series_label: str) -> list[Any]:
    for series in section["series"]:
        if series["label"] == series_label:
            return list(series["values"])
    raise KeyError(series_label)


# --- Determinism over the real, committed repository ------------------------------------


def test_two_subprocess_runs_produce_byte_identical_stdout() -> None:
    first = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "overview_metrics.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    second = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "overview_metrics.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    assert first.stdout == second.stdout
    assert first.stdout, "expected non-empty output"


def test_render_is_deterministic_across_in_process_calls() -> None:
    events = load_events()
    backlog_items = overview_metrics.load_backlog_items()
    assert overview_metrics.render(events, backlog_items) == overview_metrics.render(
        events, backlog_items
    )


def test_output_is_valid_json_with_sorted_keys_and_a_trailing_newline() -> None:
    events = load_events()
    backlog_items = overview_metrics.load_backlog_items()
    rendered = overview_metrics.render(events, backlog_items)
    parsed = json.loads(rendered)
    assert rendered.endswith("\n")
    assert json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=True) + "\n" == rendered


# --- Funnel counts against an independent recomputation ----------------------------------


def test_funnel_counts_match_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    state = fold(events)
    expected = Counter(entry["status"] for entry in state.values())

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    funnel = metrics["funnel"]
    labels = funnel["labels"]
    counts = _values(funnel, "count")
    assert labels == sorted(overview_metrics.STATUSES)

    reported = dict(zip(labels, counts))
    for status in overview_metrics.STATUSES:
        assert reported[status] == expected.get(status, 0)
    assert sum(reported.values()) == len(state)


# --- Zero rows, never omitted -------------------------------------------------------------


def test_funnel_reports_zero_for_statuses_never_reached(log: Path) -> None:
    append_idea.add("Only idea", "Body", log)
    state = fold(load_events(log))
    section = overview_metrics.funnel(state)
    assert section["labels"] == sorted(overview_metrics.STATUSES)
    counts = dict(zip(section["labels"], _values(section, "count")))
    assert counts["open"] == 1
    for status in ("discarded", "promoted", "reviewing", "triaged"):
        assert counts[status] == 0


def test_cycle_time_reports_every_legal_transition_even_unseen(log: Path) -> None:
    append_idea.add("Only idea", "Body", log)
    events = load_events(log)
    section = overview_metrics.cycle_time(events)
    expected_labels = sorted(
        f"{source}->{target}"
        for source, target in legal_transitions() | {overview_metrics.REVISIT_TRANSITION}
    )
    assert section["labels"] == expected_labels
    assert all(count == 0 for count in _values(section, "count"))
    assert all(median == 0.0 for median in _values(section, "median_hours"))


def test_annotation_coverage_zero_row_when_nothing_annotated(log: Path) -> None:
    append_idea.add("Only idea", "Body", log)
    state = fold(load_events(log))
    section = overview_metrics.annotation_coverage(state)
    assert section["labels"] == ["annotated", "unannotated"]
    assert _values(section, "count") == [0, 1]
    assert _values(section, "rate") == [0.0, 1.0]


def test_link_distribution_and_orphans_zero_row_with_no_links(log: Path) -> None:
    append_idea.add("Only idea", "Body", log)
    state = fold(load_events(log))

    distribution = overview_metrics.link_distribution(state)
    assert distribution["labels"] == sorted(LINK_TYPES)
    assert all(count == 0 for count in _values(distribution, "count"))

    orphans = overview_metrics.link_orphans(state)
    assert orphans["labels"] == ["connected", "orphaned"]
    assert _values(orphans, "count") == [0, 1]


def test_throughput_and_age_are_empty_series_for_an_empty_log(log: Path) -> None:
    events = load_events(log)  # missing file -> no events
    state = fold(events)

    throughput = overview_metrics.throughput_by_day(events)
    assert throughput["labels"] == []
    assert _values(throughput, "created") == []

    age = overview_metrics.age_of_open_ideas(state, overview_metrics._reference_at(events))
    assert age["labels"] == []
    assert _values(age, "age_days") == []


def test_backlog_by_status_zero_row_for_unused_statuses(backlog: Path) -> None:
    items = overview_metrics.load_backlog_items(backlog)
    section = overview_metrics.backlog_by_status(items)
    assert section["labels"] == sorted(overview_metrics.BACKLOG_STATUSES)
    counts = dict(zip(section["labels"], _values(section, "count")))
    assert counts["queued"] == 1
    assert counts["complete"] == 1
    for status in ("active", "blocked", "cancelled", "deferred"):
        assert counts[status] == 0


def test_load_backlog_items_missing_file_is_empty(tmp_path: Path) -> None:
    assert overview_metrics.load_backlog_items(tmp_path / "nope.yaml") == []


# --- The CLI --------------------------------------------------------------------------------


def test_main_writes_to_out_path(tmp_path: Path) -> None:
    out = tmp_path / "metrics.json"
    exit_code = overview_metrics.main(["--out", str(out)])
    assert exit_code == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert "meta" in written
    assert written["meta"]["event_count"] >= 0
