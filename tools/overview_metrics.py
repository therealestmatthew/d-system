#!/usr/bin/env python3
"""Chart-ready JSON metrics over the idea log and the backlog — idea `000071`'s metric set.

Every number here is read through the sanctioned readers — `load_events()` and `fold()` in
`src/db/ideas.py` — never by parsing `_data/ideas.jsonl` by hand, and through a plain
`yaml.safe_load` of `docs/09-backlog/backlog.yaml` for phase counts. The tool makes no model or
network call and asks the wall clock for nothing: every value is a pure function of the two
source files. Two runs against an unchanged repository produce byte-identical output — see
`meta.reference_at` below for how "age of open ideas" stays deterministic without `datetime.now()`.

Emitted, per idea `000071`'s candidate metric set: funnel counts and rates by status; cycle time
between statuses; annotation coverage; link-type distribution and orphan count; throughput by
day; and age of open ideas — plus backlog phase counts by status, the one metric this tool draws
from `docs/09-backlog/backlog.yaml` rather than the idea log. A status, transition, link type or
backlog status that has never occurred still appears with a zero value; it is never omitted.

Each section is shaped for a chart library: `{"labels": [...], "series": [{"label": ...,
"values": [...]}, ...]}`, with `values[i]` aligned to `labels[i]`. Every list is sorted and every
dict key is emitted in sorted order (`json.dumps(..., sort_keys=True)`), which is what makes two
runs byte-identical rather than merely equal.

    uv run python tools/overview_metrics.py               # print to stdout
    uv run python tools/overview_metrics.py --out FILE     # write to FILE instead
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from src.db.ideas import LINK_TYPES, IdeaError, fold, legal_transitions, load_events

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "docs" / "09-backlog" / "backlog.yaml"

#: `schemas/idea.schema.json`'s `status` enum, restated here as the fixed funnel vocabulary —
#: already alphabetical, so it doubles as the sorted label order.
STATUSES = ("discarded", "open", "promoted", "reviewing", "triaged")

#: `docs/09-backlog/backlog.yaml` items' `status` vocabulary (`schemas/backlog.schema.json`),
#: restated here rather than walked out of the schema — six fixed values duplicated once is
#: cheaper than a JSON-Schema walk for a tool that only needs the vocabulary, not the shape.
BACKLOG_STATUSES = ("active", "blocked", "cancelled", "complete", "deferred", "queued")

#: `revisited` re-enters `reviewing` from `discarded` outside the `status` event's own from/to
#: vocabulary (`src.db.ideas.legal_transitions`), so it is added once here to appear as a labeled
#: cycle-time transition alongside the nine the schema declares.
REVISIT_TRANSITION = ("discarded", "reviewing")


def _series(labels: list[str], **named_values: list[Any]) -> dict[str, Any]:
    """One chart-ready section: labels plus one or more value series aligned to them."""
    return {
        "labels": labels,
        "series": [
            {"label": name, "values": values} for name, values in sorted(named_values.items())
        ],
    }


def _parse_at(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _reference_at(events: list[dict[str, Any]]) -> datetime | None:
    """The latest event timestamp in the log, standing in for "now" in age calculations.

    Using the wall clock here would make two runs of this tool diverge by however many
    seconds passed between them. The latest timestamp already in the data does not — it is a
    fact about the log, not about when the tool happened to run.
    """
    if not events:
        return None
    return max(_parse_at(event["at"]) for event in events)


def funnel(state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Idea counts and rates by current status, every status present even at zero."""
    counts = dict.fromkeys(STATUSES, 0)
    for entry in state.values():
        counts[entry["status"]] += 1
    labels = sorted(STATUSES)
    total = sum(counts.values())
    count_values = [counts[status] for status in labels]
    rate_values = [round(counts[status] / total, 4) if total else 0.0 for status in labels]
    return _series(labels, count=count_values, rate=rate_values)


def cycle_time(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Elapsed hours between entering and leaving a status, per legal transition.

    Walks the raw events in log order, tracking each idea's current status and when it was
    entered (the `created` event for `open`, the prior `status`/`revisited` event's `at`
    otherwise). `status` and `revisited` events carry no amendable field (`AMENDABLE_FIELDS`
    in `src/db/ideas.py` is `title`/`body`/`text`/`target`), so reading `from`/`to`/`at` off
    the raw event is exactly what `fold()` itself would see.
    """
    transitions = sorted(legal_transitions() | {REVISIT_TRANSITION})
    labels = [f"{source}->{target}" for source, target in transitions]
    durations: dict[tuple[str, str], list[float]] = {t: [] for t in transitions}
    entered_at: dict[str, datetime] = {}

    for event in events:
        idea = event["idea"]
        kind = event["event"]
        if kind == "created":
            entered_at[idea] = _parse_at(event["at"])
        elif kind == "status":
            at = _parse_at(event["at"])
            transition = (event["from"], event["to"])
            durations[transition].append((at - entered_at[idea]).total_seconds() / 3600)
            entered_at[idea] = at
        elif kind == "revisited":
            at = _parse_at(event["at"])
            durations[REVISIT_TRANSITION].append((at - entered_at[idea]).total_seconds() / 3600)
            entered_at[idea] = at

    count_values = [len(durations[t]) for t in transitions]
    median_values = [
        round(statistics.median(durations[t]), 2) if durations[t] else 0.0 for t in transitions
    ]
    return _series(labels, count=count_values, median_hours=median_values)


def annotation_coverage(state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """How many ideas carry at least one annotation, versus how many carry none."""
    annotated = sum(1 for entry in state.values() if entry["annotations"])
    total = len(state)
    unannotated = total - annotated
    labels = ["annotated", "unannotated"]
    counts = {"annotated": annotated, "unannotated": unannotated}
    count_values = [counts[label] for label in labels]
    rate_values = [round(counts[label] / total, 4) if total else 0.0 for label in labels]
    return _series(labels, count=count_values, rate=rate_values)


def link_distribution(state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Non-retracted outbound links, by type — every declared link type present at zero."""
    counts = dict.fromkeys(LINK_TYPES, 0)
    for entry in state.values():
        for link in entry["links"]:
            if link["retracted"]:
                continue
            counts[link["type"]] += 1
    labels = sorted(LINK_TYPES)
    return _series(labels, count=[counts[label] for label in labels])


def _orphan_ideas(state: dict[str, dict[str, Any]]) -> list[str]:
    """Ideas touched by no non-retracted link, as either the source or the target of one."""
    connected: set[str] = set()
    for idea, entry in state.items():
        for link in entry["links"]:
            if link["retracted"]:
                continue
            connected.add(idea)
            if link["target"] is not None:
                connected.add(link["target"])
    return sorted(idea for idea in state if idea not in connected)


def link_orphans(state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Count of ideas with no link at all, versus ideas touched by at least one."""
    orphaned = len(_orphan_ideas(state))
    connected = len(state) - orphaned
    labels = ["connected", "orphaned"]
    return _series(labels, count=[connected, orphaned])


def throughput_by_day(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Ideas created per calendar day, gap-filled across the observed range.

    Filling every day between the first and last `created` event — not just the days that
    actually saw one — is what keeps a quiet day a zero row instead of a missing one.
    """
    created_days = sorted(
        _parse_at(event["at"]).date() for event in events if event["event"] == "created"
    )
    if not created_days:
        return _series([], created=[])
    counts: dict[date, int] = {}
    for day in created_days:
        counts[day] = counts.get(day, 0) + 1
    start, end = created_days[0], created_days[-1]
    all_days = [
        date.fromordinal(ordinal) for ordinal in range(start.toordinal(), end.toordinal() + 1)
    ]
    labels = [day.isoformat() for day in all_days]
    values = [counts.get(day, 0) for day in all_days]
    return _series(labels, created=values)


def age_of_open_ideas(
    state: dict[str, dict[str, Any]], reference_at: datetime | None
) -> dict[str, Any]:
    """Days since creation, for every idea currently `open`, against `reference_at`."""
    open_ideas = sorted(idea for idea, entry in state.items() if entry["status"] == "open")
    if reference_at is None:
        return _series(open_ideas, age_days=[0.0 for _ in open_ideas])
    values = [
        round((reference_at - _parse_at(state[idea]["created"])).total_seconds() / 86400, 2)
        for idea in open_ideas
    ]
    return _series(open_ideas, age_days=values)


def load_backlog_items(path: Path = BACKLOG) -> list[dict[str, Any]]:
    """Every phase in the backlog. A missing file is an empty backlog, not an error."""
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items: list[dict[str, Any]] = list(data.get("items", []))
    return items


def backlog_by_status(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Phase counts by execution status — every declared status present at zero."""
    counts = dict.fromkeys(BACKLOG_STATUSES, 0)
    for item in items:
        counts[item["status"]] += 1
    labels = sorted(BACKLOG_STATUSES)
    return _series(labels, count=[counts[label] for label in labels])


def build_metrics(
    events: list[dict[str, Any]], backlog_items: list[dict[str, Any]]
) -> dict[str, Any]:
    """Every metric section, assembled from one fold of the log and one read of the backlog."""
    state = fold(events)
    reference_at = _reference_at(events)
    return {
        "meta": {
            "idea_count": len(state),
            "event_count": len(events),
            "backlog_phase_count": len(backlog_items),
            "reference_at": reference_at.isoformat() if reference_at else None,
        },
        "funnel": funnel(state),
        "cycle_time": cycle_time(events),
        "annotation_coverage": annotation_coverage(state),
        "link_distribution": link_distribution(state),
        "link_orphans": link_orphans(state),
        "throughput_by_day": throughput_by_day(events),
        "age_of_open_ideas": age_of_open_ideas(state, reference_at),
        "backlog_by_status": backlog_by_status(backlog_items),
    }


def render(events: list[dict[str, Any]], backlog_items: list[dict[str, Any]]) -> str:
    """The full JSON document, deterministically ordered and newline-terminated."""
    metrics = build_metrics(events, backlog_items)
    return json.dumps(metrics, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=None, help="write the JSON here instead of stdout"
    )
    args = parser.parse_args(argv)

    try:
        rendered = render(load_events(), load_backlog_items())
    except IdeaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
