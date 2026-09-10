"""Tests for tools/overview_metrics.py and tools/overview_inventory.py -- determinism and
independent recomputation.

Two things anchor the metrics half of this file. First, the acceptance criterion from idea
`000071` and REQ-006 R07: running the tool twice against an unchanged repository must produce
byte-identical output, both as a subprocess (the way it is actually run) and as a direct call to
`render()` (the way it is easiest to assert). Second, the funnel counts the tool reports must
match an independent recomputation over the same log via `fold()` -- the tool must not silently
diverge from the projection it is supposed to summarise. A handful of zero-row tests pin the
"zero counts appear as zero rows, never omitted" requirement against a synthetic single-idea log,
where every status, transition and link type but one is genuinely unseen.

The inventory half applies the same determinism criterion to `tools/overview_inventory.py`, plus
an independent recomputation of the systems inventory count against a direct
`yaml.safe_load()` of `docs/08-governance/systems.yaml`.
"""

from __future__ import annotations

import importlib.util
import json
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.db.ideas import LINK_TYPES, fold, legal_transitions, load_events

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS_REGISTRY = ROOT / "docs" / "08-governance" / "systems.yaml"
BACKLOG = ROOT / "docs" / "09-backlog" / "backlog.yaml"


def _load(name: str) -> Any:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


overview_metrics = _load("overview_metrics")
overview_inventory = _load("overview_inventory")
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


def test_cycle_time_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    by_idea: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_idea[event["idea"]].append(event)

    revisit = overview_metrics.REVISIT_TRANSITION
    transitions = sorted(legal_transitions() | {revisit})
    durations: dict[tuple[str, str], list[float]] = {t: [] for t in transitions}

    for idea_events in by_idea.values():
        entered_at: datetime | None = None
        for event in idea_events:
            kind = event["event"]
            if kind == "created":
                entered_at = datetime.fromisoformat(event["at"])
            elif kind == "status":
                assert entered_at is not None
                at = datetime.fromisoformat(event["at"])
                key = (event["from"], event["to"])
                durations[key].append((at - entered_at).total_seconds() / 3600)
                entered_at = at
            elif kind == "revisited":
                assert entered_at is not None
                at = datetime.fromisoformat(event["at"])
                durations[revisit].append((at - entered_at).total_seconds() / 3600)
                entered_at = at

    expected_counts = {t: len(v) for t, v in durations.items()}
    expected_medians = {
        t: round(statistics.median(v), 2) if v else 0.0 for t, v in durations.items()
    }

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["cycle_time"]
    labels = section["labels"]
    counts = _values(section, "count")
    medians = _values(section, "median_hours")

    expected_labels = [f"{source}->{target}" for source, target in transitions]
    assert labels == expected_labels
    for label, count, median in zip(labels, counts, medians):
        source, target = label.split("->", 1)
        assert count == expected_counts[(source, target)]
        assert median == expected_medians[(source, target)]


def test_annotation_coverage_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    state = fold(events)
    total = len(state)
    expected_annotated = sum(1 for entry in state.values() if len(entry["annotations"]) > 0)
    expected_unannotated = total - expected_annotated

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["annotation_coverage"]
    counts = dict(zip(section["labels"], _values(section, "count")))
    rates = dict(zip(section["labels"], _values(section, "rate")))

    assert counts["annotated"] == expected_annotated
    assert counts["unannotated"] == expected_unannotated
    assert rates["annotated"] == (round(expected_annotated / total, 4) if total else 0.0)
    assert rates["unannotated"] == (round(expected_unannotated / total, 4) if total else 0.0)


def test_link_distribution_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    state = fold(events)
    counts: Counter[str] = Counter()
    for entry in state.values():
        for link in entry["links"]:
            if not link["retracted"]:
                counts[link["type"]] += 1

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["link_distribution"]
    assert section["labels"] == sorted(LINK_TYPES)
    reported = dict(zip(section["labels"], _values(section, "count")))
    for link_type in LINK_TYPES:
        assert reported[link_type] == counts.get(link_type, 0)


def test_link_orphans_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    state = fold(events)
    touched: set[str] = set()
    for idea, entry in state.items():
        for link in entry["links"]:
            if link["retracted"]:
                continue
            touched.add(idea)
            if link["target"] is not None:
                touched.add(link["target"])
    expected_orphaned = sum(1 for idea in state if idea not in touched)
    expected_connected = len(state) - expected_orphaned

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["link_orphans"]
    assert section["labels"] == ["connected", "orphaned"]
    counts = dict(zip(section["labels"], _values(section, "count")))
    assert counts["connected"] == expected_connected
    assert counts["orphaned"] == expected_orphaned


def test_throughput_by_day_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    created_dates = [
        datetime.fromisoformat(event["at"]).date()
        for event in events
        if event["event"] == "created"
    ]

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["throughput_by_day"]

    if not created_dates:
        assert section["labels"] == []
        assert _values(section, "created") == []
        return

    counts = Counter(created_dates)
    start, end = min(created_dates), max(created_dates)
    expected_labels = []
    expected_values = []
    current = start
    one_day = timedelta(days=1)
    while current <= end:
        expected_labels.append(current.isoformat())
        expected_values.append(counts.get(current, 0))
        current += one_day

    assert section["labels"] == expected_labels
    assert _values(section, "created") == expected_values
    assert sum(expected_values) == len(created_dates)


def test_age_of_open_ideas_matches_independent_recomputation_over_the_real_log() -> None:
    events = load_events()
    state = fold(events)
    reference_at = max((datetime.fromisoformat(e["at"]) for e in events), default=None)
    open_ideas = sorted(idea for idea, entry in state.items() if entry["status"] == "open")

    metrics = overview_metrics.build_metrics(events, overview_metrics.load_backlog_items())
    section = metrics["age_of_open_ideas"]
    assert section["labels"] == open_ideas

    if reference_at is None:
        assert _values(section, "age_days") == [0.0 for _ in open_ideas]
        return

    expected_ages = [
        round(
            (reference_at - datetime.fromisoformat(state[idea]["created"])).total_seconds()
            / 86400,
            2,
        )
        for idea in open_ideas
    ]
    assert _values(section, "age_days") == expected_ages


def test_backlog_by_status_matches_independent_recomputation_over_the_real_backlog() -> None:
    data = yaml.safe_load(BACKLOG.read_text(encoding="utf-8")) or {}
    items = data.get("items", [])
    counts = Counter(item["status"] for item in items)

    metrics = overview_metrics.build_metrics(load_events(), overview_metrics.load_backlog_items())
    section = metrics["backlog_by_status"]
    assert section["labels"] == sorted(overview_metrics.BACKLOG_STATUSES)
    reported = dict(zip(section["labels"], _values(section, "count")))
    for status in overview_metrics.BACKLOG_STATUSES:
        assert reported[status] == counts.get(status, 0)
    assert sum(reported.values()) == len(items)


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


# --- tools/overview_inventory.py -----------------------------------------------------------
# --- Determinism over the real, committed repository ------------------------------------


def test_inventory_two_subprocess_runs_produce_byte_identical_stdout() -> None:
    first = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "overview_inventory.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    second = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "overview_inventory.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    assert first.stdout == second.stdout
    assert first.stdout, "expected non-empty output"


def test_inventory_render_is_deterministic_across_in_process_calls() -> None:
    concepts = overview_inventory.load_concepts()
    systems = overview_inventory.load_systems()
    assert overview_inventory.render(concepts, systems) == overview_inventory.render(
        concepts, systems
    )


def test_inventory_output_is_valid_json_with_sorted_keys_and_a_trailing_newline() -> None:
    concepts = overview_inventory.load_concepts()
    systems = overview_inventory.load_systems()
    rendered = overview_inventory.render(concepts, systems)
    parsed = json.loads(rendered)
    assert rendered.endswith("\n")
    assert json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=True) + "\n" == rendered


# --- Systems inventory count against an independent recomputation ------------------------


def test_systems_inventory_count_matches_the_registry_entry_count() -> None:
    registry = yaml.safe_load(SYSTEMS_REGISTRY.read_text(encoding="utf-8"))
    expected_ids = sorted(entry["id"] for entry in registry["systems"])

    inventory = overview_inventory.build_inventory(
        overview_inventory.load_concepts(), overview_inventory.load_systems()
    )
    reported_ids = sorted(entry["id"] for entry in inventory["systems"])

    assert reported_ids == expected_ids
    assert inventory["meta"]["system_count"] == len(registry["systems"])
    assert len(inventory["systems"]) == len(registry["systems"])


def test_systems_inventory_rows_carry_id_name_domain_status_and_dependency_edges() -> None:
    inventory = overview_inventory.build_inventory(
        overview_inventory.load_concepts(), overview_inventory.load_systems()
    )
    for row in inventory["systems"]:
        assert set(row) == {"id", "name", "domain", "status", "depends_on"}
        assert row["depends_on"] == sorted(row["depends_on"])
    assert inventory["systems"] == sorted(inventory["systems"], key=lambda row: row["id"])


# --- Concepts and terminology inventory -----------------------------------------------------


def test_concepts_inventory_rows_are_sorted_and_carry_their_tags_and_systems() -> None:
    inventory = overview_inventory.build_inventory(
        overview_inventory.load_concepts(), overview_inventory.load_systems()
    )
    concepts = inventory["concepts"]
    assert concepts == sorted(concepts, key=lambda row: row["id"])
    for row in concepts:
        assert set(row) == {"id", "title", "tags", "systems"}
        assert row["tags"] == sorted(row["tags"])
        assert row["systems"] == sorted(row["systems"])
    assert inventory["meta"]["concept_count"] == len(concepts)


def test_terms_inventory_extracts_every_heading_from_a_grouped_glossary_concept() -> None:
    inventory = overview_inventory.build_inventory(
        overview_inventory.load_concepts(), overview_inventory.load_systems()
    )
    terms = inventory["terms"]
    assert terms == sorted(terms, key=lambda row: (row["term"].lower(), row["concept_id"]))
    phase_terms = [row for row in terms if row["term"] == "Phase"]
    assert phase_terms
    assert phase_terms[0]["concept_id"] == "mem-concept-terms-plans-and-work"
    assert inventory["meta"]["term_count"] == len(terms)


def test_inventory_reports_zero_counts_as_zero_for_an_empty_registry_and_no_concepts() -> None:
    inventory = overview_inventory.build_inventory([], [])
    assert inventory["meta"] == {"concept_count": 0, "term_count": 0, "system_count": 0}
    assert inventory["concepts"] == []
    assert inventory["terms"] == []
    assert inventory["systems"] == []


def test_load_systems_missing_file_is_empty(tmp_path: Path) -> None:
    assert overview_inventory.load_systems(tmp_path / "nope.yaml") == []


# --- The CLI --------------------------------------------------------------------------------


def test_inventory_main_writes_to_out_path(tmp_path: Path) -> None:
    out = tmp_path / "inventory.json"
    exit_code = overview_inventory.main(["--out", str(out)])
    assert exit_code == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert "meta" in written
    assert written["meta"]["system_count"] >= 0
