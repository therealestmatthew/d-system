#!/usr/bin/env python3
"""Render the D-System overview page from `tools/overview_metrics.py` and
`tools/overview_inventory.py` output.

This tool computes nothing itself. It runs the two phase-demo-03 tools as subprocesses —
exactly the way idea `000071` and REQ-006 R07 already verify them — parses their stdout JSON,
and fills the `templates/html/overview-*.html` + `templates/styles/overview.css` template
family with plain `{{TOKEN}}` string substitution, per the token contracts documented at the
top of each template. No figure on the page is computed here; every number is copied verbatim
from one of the two tools' own output (REQ-006 R08).

Deterministic end to end. `overview_metrics.py` and `overview_inventory.py` are themselves
deterministic (same inputs, same output bytes, no model or network call — see their own
docstrings), and this renderer adds no wall-clock or random input of its own: the page's
`{{GENERATED_AT}}` label is `overview_metrics.py`'s own `meta.reference_at` (the latest
timestamp already in the idea log, not `datetime.now()`), not a render-time timestamp — so
generating twice against an unchanged repository produces byte-identical bytes. This is a
narrower reading of `templates/html/overview-page.html`'s token-contract comment, which allows
`{{GENERATED_AT}}` to be wall-clock; the dispatched work item for this tool requires
generation-to-generation identity instead, so the wall clock is never consulted.

The committed page is a snapshot, not a live view (owner ruling 2026-10-04, REQ-020 R08). Its
`{{SOURCE_STAMP}}` names the commit the inputs were read at and that commit's own date, as
`tools/generate_engine_pages.py` stamps the engine pages, says when an input had uncommitted
changes, and carries a SHA-256 of the page body. Nothing compares the page against live idea
or backlog counts, so recording an idea leaves it valid; `content_hash_matches()` recomputes
the hash, so a hand edit to the committed page does not.

    uv run python tools/generate_overview.py               # write _public/overview/index.html
    uv run python tools/generate_overview.py --out FILE     # write elsewhere instead
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "html"
CSS = ROOT / "templates" / "styles" / "overview.css"
METRICS_SCRIPT = ROOT / "tools" / "overview_metrics.py"
INVENTORY_SCRIPT = ROOT / "tools" / "overview_inventory.py"
TARGET = ROOT / "_public" / "overview" / "index.html"

#: The metrics sections, in the fixed order `overview-page.html`'s token contract specifies
#: for `{{METRICS_SECTIONS}}`, each paired with the human title and the series label charted
#: as the primary bar list (`overview_metrics.py`'s own series names).
SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("funnel", "Idea funnel by status", "count"),
    ("cycle_time", "Cycle time between statuses (hours)", "count"),
    ("annotation_coverage", "Annotation coverage", "count"),
    ("link_distribution", "Link type distribution", "count"),
    ("link_orphans", "Linked vs. orphaned ideas", "count"),
    ("throughput_by_day", "Idea throughput by day", "created"),
    ("age_of_open_ideas", "Age of open ideas (days)", "age_days"),
    ("backlog_by_status", "Backlog phases by status", "count"),
)

FALLBACK_GENERATED_AT = "no idea-log events yet"

#: Paths whose uncommitted changes would make the commit stamp misdescribe what was read.
INPUT_PATHS = (
    "_data/ideas.jsonl",
    "docs/09-backlog/backlog.yaml",
    "docs/08-governance/systems.yaml",
    "brain",
    "templates",
)

#: The hash slot in the stamp. The page is hashed with the digest left empty, then filled.
HASH_PREFIX = "Content hash <code>sha256:"
_HASH_SLOT = re.compile(re.escape(HASH_PREFIX) + r"([0-9a-f]{64})</code>")


class Templates:
    """The `templates/html/overview-*.html` family and `overview.css`, read once."""

    def __init__(self, root: Path = TEMPLATES, css: Path = CSS) -> None:
        self.page = _read(root / "overview-page.html")
        self.metrics_section = _read(root / "overview-metrics-section.html")
        self.bar = _read(root / "overview-bar.html")
        self.concepts_panel = _read(root / "overview-concepts-panel.html")
        self.concept_row = _read(root / "overview-concept-row.html")
        self.term_row = _read(root / "overview-term-row.html")
        self.systems_panel = _read(root / "overview-systems-panel.html")
        self.system_row = _read(root / "overview-system-row.html")
        self.css = _read_css(css)


_LEADING_COMMENT = re.compile(r"^\s*<!--.*?-->\s*", re.DOTALL)


def _read(path: Path) -> str:
    """A template's body, with its leading `<!-- token contract -->` doc comment stripped.

    Every `templates/html/overview-*.html` file documents its own `{{TOKEN}}` names inside
    that opening comment — including the literal token text. A naive global `{{TOKEN}}`
    replace over the whole file would match those literal mentions too and corrupt the
    comment with substituted content, so the comment is dropped before substitution ever
    runs. `templates/styles/overview.css` is read as a substitution *value*, never filled
    itself, so its own `/* ... */` header is untouched by this.
    """
    text = path.read_text(encoding="utf-8")
    return _LEADING_COMMENT.sub("", text, count=1)


def _read_css(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fill(template: str, tokens: dict[str, str]) -> str:
    """Plain `{{TOKEN}}` string substitution — the contract every template documents."""
    rendered = template
    for key, value in tokens.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def _joined(values: list[Any]) -> str:
    """A tags/systems/depends_on array, joined for display; empty stays empty, never "None"."""
    return ", ".join(html.escape(str(value)) for value in values)


def _as_text(value: Any) -> str:
    """A scalar exactly as it appears in the source JSON — `json.dumps` on one value."""
    return html.escape(json.dumps(value))


def run_metrics_tool(script: Path = METRICS_SCRIPT) -> dict[str, Any]:
    """`tools/overview_metrics.py`'s own JSON, run as a subprocess and parsed, not recomputed."""
    result = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, capture_output=True, check=True
    )
    data: dict[str, Any] = json.loads(result.stdout)
    return data


def run_inventory_tool(script: Path = INVENTORY_SCRIPT) -> dict[str, Any]:
    """`tools/overview_inventory.py`'s own JSON, run as a subprocess and parsed, not recomputed."""
    result = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, capture_output=True, check=True
    )
    data: dict[str, Any] = json.loads(result.stdout)
    return data


def _primary_values(section: dict[str, Any], primary_label: str) -> list[Any]:
    for series in section["series"]:
        if series["label"] == primary_label:
            values: list[Any] = series["values"]
            return values
    return []


def render_bars(labels: list[Any], values: list[Any], bar_template: str) -> str:
    """One `overview-bar.html` per label, normalized against the series' own max value."""
    numeric = [float(value) for value in values]
    peak = max(numeric) if numeric else 0.0
    parts = []
    for label, raw, magnitude in zip(labels, values, numeric):
        percent = 0.0 if peak == 0 else round(magnitude / peak * 100, 2)
        parts.append(
            _fill(
                bar_template,
                {
                    "BAR_LABEL": html.escape(str(label)),
                    "BAR_PERCENT": json.dumps(percent),
                    "BAR_VALUE": _as_text(raw),
                },
            )
        )
    return "".join(parts)


def render_table(section: dict[str, Any]) -> tuple[str, str]:
    """The `<th>` head cells and `<tr>` body rows behind a section's `<details>` fallback."""
    series = section["series"]
    head_cells = "".join(f'<th scope="col">{html.escape(s["label"])}</th>' for s in series)
    rows = []
    for index, label in enumerate(section["labels"]):
        cells = "".join(f"<td>{_as_text(s['values'][index])}</td>" for s in series)
        rows.append(f"<tr><td>{html.escape(str(label))}</td>{cells}</tr>")
    return head_cells, "".join(rows)


def render_metrics_section(
    section_id: str, title: str, primary_label: str, metrics: dict[str, Any], templates: Templates
) -> str:
    section = metrics[section_id]
    bars = render_bars(section["labels"], _primary_values(section, primary_label), templates.bar)
    head_cells, body_rows = render_table(section)
    return _fill(
        templates.metrics_section,
        {
            "SECTION_ID": section_id,
            "SECTION_TITLE": title,
            "SECTION_PRIMARY_LABEL": primary_label,
            "CHART_BARS": bars,
            "TABLE_HEAD_CELLS": head_cells,
            "TABLE_BODY_ROWS": body_rows,
        },
    )


def render_concepts_panel(inventory: dict[str, Any], templates: Templates) -> str:
    concept_rows = "".join(
        _fill(
            templates.concept_row,
            {
                "CONCEPT_ID": html.escape(entry["id"]),
                "CONCEPT_TITLE": html.escape(entry["title"]),
                "CONCEPT_TAGS": _joined(entry["tags"]),
                "CONCEPT_SYSTEMS": _joined(entry["systems"]),
            },
        )
        for entry in inventory["concepts"]
    )
    term_rows = "".join(
        _fill(
            templates.term_row,
            {
                "TERM": html.escape(entry["term"]),
                "TERM_CONCEPT_TITLE": html.escape(entry["concept_title"]),
                "TERM_CONCEPT_ID": html.escape(entry["concept_id"]),
            },
        )
        for entry in inventory["terms"]
    )
    return _fill(
        templates.concepts_panel,
        {
            "CONCEPT_COUNT": str(inventory["meta"]["concept_count"]),
            "TERM_COUNT": str(inventory["meta"]["term_count"]),
            "CONCEPT_ROWS": concept_rows,
            "TERM_ROWS": term_rows,
        },
    )


def render_systems_panel(inventory: dict[str, Any], templates: Templates) -> str:
    system_rows = "".join(
        _fill(
            templates.system_row,
            {
                "SYSTEM_ID": html.escape(entry["id"]),
                "SYSTEM_NAME": html.escape(entry["name"]),
                "SYSTEM_DOMAIN": html.escape(entry["domain"]),
                "SYSTEM_STATUS": html.escape(str(entry["status"]).lower()),
                "SYSTEM_DEPENDS_ON": _joined(entry["depends_on"]),
            },
        )
        for entry in inventory["systems"]
    )
    return _fill(
        templates.systems_panel,
        {
            "SYSTEM_COUNT": str(inventory["meta"]["system_count"]),
            "SYSTEM_ROWS": system_rows,
        },
    )


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def source_stamp() -> dict[str, Any]:
    """The commit the inputs were read at, its date, and whether any input differs from it."""
    dirty = _git("status", "--porcelain", "--", *INPUT_PATHS)
    return {
        "commit": _git("rev-parse", "--short=12", "HEAD"),
        "date": _git("show", "-s", "--format=%cs", "HEAD"),
        "dirty": bool(dirty),
    }


def render_stamp(stamp: dict[str, Any]) -> str:
    """The stamp markup, with the content hash slot left empty for `_seal()` to fill."""
    parts = [
        f"Source commit <code>{html.escape(stamp['commit'])}</code>",
        f"Commit date {html.escape(stamp['date'])}",
    ]
    if stamp["dirty"]:
        parts.append("Inputs had uncommitted changes when generated")
    parts.append(HASH_PREFIX + "</code>")
    return "\n      &middot; ".join(parts)


def _digest(unsealed: str) -> str:
    return hashlib.sha256(unsealed.encode("utf-8")).hexdigest()


def _seal(unsealed: str) -> str:
    """Fill the empty hash slot with the SHA-256 of the page as it stands with the slot empty."""
    empty_slot = HASH_PREFIX + "</code>"
    assert unsealed.count(empty_slot) == 1, "expected exactly one empty content hash slot"
    return unsealed.replace(empty_slot, HASH_PREFIX + _digest(unsealed) + "</code>")


def content_hash_matches(page: str) -> bool:
    """Whether the page's recorded content hash is the hash of its own body.

    False when the page carries no hash, carries more than one, or was edited after it was
    generated.
    """
    found: list[str] = _HASH_SLOT.findall(page)
    if len(found) != 1:
        return False
    unsealed = _HASH_SLOT.sub(lambda _: HASH_PREFIX + "</code>", page)
    return _digest(unsealed) == found[0]


def render_page(
    metrics: dict[str, Any],
    inventory: dict[str, Any],
    templates: Templates,
    stamp: dict[str, Any],
) -> str:
    """The full self-contained page, every figure copied verbatim from the two tools."""
    metrics_sections = "".join(
        render_metrics_section(section_id, title, primary_label, metrics, templates)
        for section_id, title, primary_label in SECTIONS
    )
    generated_at = metrics["meta"]["reference_at"] or FALLBACK_GENERATED_AT
    unsealed = _fill(
        templates.page,
        {
            "PAGE_TITLE": "D-System Overview",
            "INLINE_STYLES": templates.css,
            "GENERATED_AT": html.escape(generated_at),
            "IDEA_COUNT": str(metrics["meta"]["idea_count"]),
            "EVENT_COUNT": str(metrics["meta"]["event_count"]),
            "BACKLOG_PHASE_COUNT": str(metrics["meta"]["backlog_phase_count"]),
            "CONCEPT_COUNT": str(inventory["meta"]["concept_count"]),
            "TERM_COUNT": str(inventory["meta"]["term_count"]),
            "SYSTEM_COUNT": str(inventory["meta"]["system_count"]),
            "METRICS_SECTIONS": metrics_sections,
            "CONCEPTS_PANEL": render_concepts_panel(inventory, templates),
            "SYSTEMS_PANEL": render_systems_panel(inventory, templates),
            "SOURCE_STAMP": render_stamp(stamp),
        },
    )
    return _seal(unsealed)


def generate(templates: Templates | None = None) -> str:
    """Run both tools and render the page — the whole pipeline, no computation of its own."""
    metrics = run_metrics_tool()
    inventory = run_inventory_tool()
    return render_page(metrics, inventory, templates or Templates(), source_stamp())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=TARGET,
        help="write the page here (default: _public/overview/index.html)",
    )
    args = parser.parse_args(argv)

    rendered = generate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
