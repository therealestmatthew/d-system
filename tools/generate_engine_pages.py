#!/usr/bin/env python3
"""Generate the idea realization engine's pages into `_public/engine/` — `REQ-036` R07-R16.

The engine (`ARCH-006`) carries an idea from capture to delivered work through nine stages and
five owner gates. These pages show where everything stands, as committed snapshots built from the
house family (`templates/html/house-page.html`, `templates/styles/house*.css`, `OPS-027`).

Inputs, all tracked: the idea log through `fold()` (never parsed here directly, R10), the backlog
(`docs/09-backlog/backlog.yaml`), plan front matter under `docs/01-plans/`, the house family
templates, and two facts from git, the commit the inputs were read at and that commit's date.

Determinism (R07, R08). Every page is a pure function of those inputs. The stamp is the source
commit and the commit's own date, never the time the generator ran, so two runs on one commit give
identical bytes. When an input has uncommitted changes the stamp says so, because the commit alone
would then misdescribe what was read. Pages are committed snapshots: nothing in CI compares them
with a fresh run, by the owner's ruling of 2026-09-30, since the idea log moves many times a day.

Every number on a page names its source, and where no record exists the page says "not recorded"
and names what is missing instead of estimating (R11). The derivation of each stage count and
gate queue is in `STAGES` and `GATES` below and is printed on the page beside the number.

    uv run python tools/generate_engine_pages.py                 # write _public/engine/
    uv run python tools/generate_engine_pages.py --out DIR       # write somewhere else
"""

from __future__ import annotations

import argparse
import html
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.ideas import AXES, SCHEMA, fold, load_events, statuses  # noqa: E402
from src.governance.__main__ import markdown_paths, parse_frontmatter  # noqa: E402
from src.governance.backlog import readiness  # noqa: E402
from tools import generate_house_css as house  # noqa: E402

OUT = ROOT / "_public" / "engine"

#: Paths whose uncommitted changes would make the commit stamp misdescribe what was read.
INPUT_PATHS = ("_data/ideas.jsonl", "docs/09-backlog", "docs/01-plans", "templates")

NOT_RECORDED = "not recorded"
UNCLASSIFIED = "unclassified"
NO_RECORDED_PLAN = "no recorded plan"


# ---- inputs ----------------------------------------------------------------------------------


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def source_stamp(root: Path = ROOT) -> dict[str, Any]:
    """The commit the inputs were read at, its date, and whether any input differs from it."""
    dirty = _git(root, "status", "--porcelain", "--", *INPUT_PATHS)
    return {
        "commit": _git(root, "rev-parse", "--short=12", "HEAD"),
        "date": _git(root, "show", "-s", "--format=%cs", "HEAD"),
        "dirty": bool(dirty),
    }


def load_plans(root: Path = ROOT) -> list[dict[str, Any]]:
    """Front matter of every plan document, sorted by code."""
    plans = []
    for path in markdown_paths(root, "docs/01-plans"):
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("kind") == "plan":
            plans.append({k: meta.get(k) for k in ("id", "code", "title", "status")})
    return sorted(plans, key=lambda plan: str(plan["code"]))


def load_inputs(root: Path = ROOT) -> dict[str, Any]:
    """Everything the pages read, gathered once."""
    backlog = yaml.safe_load((root / "docs" / "09-backlog" / "backlog.yaml").read_text("utf-8"))
    return {
        "ideas": fold(load_events(root / "_data" / "ideas.jsonl")),
        "phases": backlog["items"],
        "plans": load_plans(root),
        "stamp": source_stamp(root),
    }


# ---- derivations -----------------------------------------------------------------------------


def phase_states(phases: list[dict[str, Any]]) -> dict[str, str]:
    """Each phase's display state: its status, with queued split by `--ready`'s own function."""
    items = {phase["id"]: phase for phase in phases}
    return {
        key: readiness(item, items) if item["status"] == "queued" else item["status"]
        for key, item in items.items()
    }


def linked_ideas(inputs: dict[str, Any]) -> set[str] | None:
    """Ideas some phase's `ideas` field names, or None when no phase carries the field at all."""
    phases = inputs["phases"]
    if not any("ideas" in phase for phase in phases):
        return None
    return {idea for phase in phases for idea in phase.get("ideas", [])}


def g2_queue(inputs: dict[str, Any]) -> list[str]:
    """Triaged ideas with no `promoted_to` and, where the field exists, no phase naming them."""
    linked = linked_ideas(inputs) or set()
    return sorted(
        key
        for key, idea in inputs["ideas"].items()
        if idea["status"] == "triaged" and not idea["promoted_to"] and key not in linked
    )


def _ideas_with(status: str) -> Callable[[dict[str, Any]], list[str]]:
    return lambda inputs: sorted(k for k, i in inputs["ideas"].items() if i["status"] == status)


def _plans_with(status: str) -> Callable[[dict[str, Any]], list[str]]:
    return lambda inputs: [str(p["code"]) for p in inputs["plans"] if p["status"] == status]


def _phases_in(*states: str) -> Callable[[dict[str, Any]], list[str]]:
    def select(inputs: dict[str, Any]) -> list[str]:
        current = phase_states(inputs["phases"])
        return sorted(key for key, state in current.items() if state in states)

    return select


#: The nine ARCH-006 stages: what each count is, where it comes from, and how it is computed.
#: A stage whose work leaves no structured record carries `None` and shows "not recorded".
STAGES: list[dict[str, Any]] = [
    {"n": 1, "name": "Capture", "counts": "ideas captured, all statuses",
     "source": "fold()", "select": lambda inputs: sorted(inputs["ideas"])},
    {"n": 2, "name": "Triage", "counts": "ideas with status open, waiting for triage",
     "source": "fold()", "select": _ideas_with("open")},
    {"n": 3, "name": "Partition", "counts": "triaged ideas not yet linked to a plan or phase",
     "source": "fold(); backlog ideas field", "select": g2_queue},
    {"n": 4, "name": "Planning", "counts": "plans whose front matter reads draft; the same set "
     "as the G3 queue", "source": "plan front matter", "select": _plans_with("draft")},
    {"n": 5, "name": "Adversarial review", "counts": NOT_RECORDED,
     "source": "no structured review record exists; reviews live in session records",
     "select": None},
    {"n": 6, "name": "Phase-fit check", "counts": NOT_RECORDED,
     "source": "no structured phase-fit record exists", "select": None},
    {"n": 7, "name": "Dependency mapping",
     "counts": "queued phases, dependencies mapped, unclaimed",
     "source": "backlog.yaml", "select": _phases_in("ready", "waiting")},
    {"n": 8, "name": "Execution", "counts": "active phases, claimed and in a worktree",
     "source": "backlog.yaml", "select": _phases_in("active")},
    {"n": 9, "name": "Realization check", "counts": "ideas with status delivered",
     "source": "fold()", "select": _ideas_with("delivered")},
]

#: The five gates and what is waiting at each, exactly as REQ-036 R14's table derives them.
GATES: list[dict[str, Any]] = [
    {"gate": "G1", "decision": "Idea approval", "waiting": "nothing waits: an idea is approved "
     "when it is written", "source": "fold()", "select": None, "kind": "count-only"},
    {"gate": "G2", "decision": "Track acceptance", "waiting": "triaged ideas with no promoted_to "
     "and no phase naming them", "source": "fold(); backlog ideas field", "select": g2_queue,
     "kind": "ideas"},
    {"gate": "G3", "decision": "Plan approval", "waiting": "plans whose front matter reads draft",
     "source": "plan front matter", "select": _plans_with("draft"), "kind": "plans"},
    {"gate": "G4 and G5", "decision": "Integration and completion review",
     "waiting": "active phases; integration is fast-forward-only and the completion edit follows "
     "the merge in the same turn, so the two gates have one queue", "source": "backlog.yaml",
     "select": _phases_in("active"), "kind": "phases"},
]


def overview_data(inputs: dict[str, Any]) -> dict[str, Any]:
    """Every figure the pipeline overview shows, each with its derivation."""
    states = phase_states(inputs["phases"])
    stages = [
        {**stage, "items": stage["select"](inputs) if stage["select"] else None}
        for stage in STAGES
    ]
    gates = [{**gate, "items": gate["select"](inputs) if gate["select"] else None}
             for gate in GATES]
    ideas = inputs["ideas"]
    return {
        "stamp": inputs["stamp"],
        "ideas_total": len(ideas),
        "ideas_triaged": sum(1 for idea in ideas.values() if idea["status"] == "triaged"),
        "phases_total": len(states),
        "phases_complete": sum(1 for state in states.values() if state == "complete"),
        "phases_blocked": sorted(k for k, s in states.items() if s == "blocked"),
        "ideas_field_present": linked_ideas(inputs) is not None,
        "stages": stages,
        "gates": gates,
    }


def axis_vocabulary() -> tuple[dict[str, list[str]], list[str]]:
    """Each ARCH-005 axis's legal values, and the record kinds that carry no axis values.

    Read from the idea schema rather than restated, so a value added there reaches the page
    without a second edit. Only a knowledge record carries axis values; the other kinds carry none.
    """
    properties = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))["properties"]
    values = {axis: list(properties[axis]["enum"]) for axis in AXES}
    kinds = [kind for kind in properties["record_kind"]["enum"] if kind != "knowledge"]
    return values, kinds


def no_axes(kind: str) -> str:
    return f"no axes ({kind})"


def axis_value(idea: dict[str, Any], axis: str) -> str:
    """The idea's value on one axis, "unclassified" with no classified event, or the record kind
    of a classified record that carries no axis values."""
    classification = idea.get("classification")
    if not classification:
        return UNCLASSIFIED
    if classification["record_kind"] != "knowledge":
        return no_axes(classification["record_kind"])
    return str(classification[axis])


def ledger_data(inputs: dict[str, Any]) -> dict[str, Any]:
    """Every figure the idea funnel and ledger shows (REQ-036 R15, R16)."""
    ideas = inputs["ideas"]
    linked = linked_ideas(inputs) or set()
    values, kinds = axis_vocabulary()
    rows = [
        {
            "id": key,
            "title": idea["title"],
            "status": idea["status"],
            "created": str(idea["created"])[:10],
            "axes": {axis: axis_value(idea, axis) for axis in AXES},
            "has_plan": bool(idea["promoted_to"]) or key in linked,
        }
        for key, idea in sorted(ideas.items())
    ]
    funnel = [
        (status, sum(1 for row in rows if row["status"] == status)) for status in statuses()
    ]
    axes = {}
    for axis in AXES:
        buckets = [*values[axis], *(no_axes(kind) for kind in kinds), UNCLASSIFIED]
        axes[axis] = [
            (bucket, sum(1 for row in rows if row["axes"][axis] == bucket)) for bucket in buckets
        ]
    return {
        "total": len(ideas),
        "rows": rows,
        "funnel": funnel,
        "axes": axes,
        "classified": sum(1 for idea in ideas.values() if idea.get("classification")),
        "ideas_field_present": linked_ideas(inputs) is not None,
    }


# ---- rendering -------------------------------------------------------------------------------


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def _count_cell(attr: str, key: object, items: list[str] | None) -> str:
    if items is None:
        return f'<td class="num" data-{attr}="{_e(key)}">{NOT_RECORDED}</td>'
    return f'<td class="num" data-{attr}="{_e(key)}">{len(items)}</td>'


def _stamp_meta(stamp: dict[str, Any]) -> str:
    parts = [
        f"<span>Source commit <code>{_e(stamp['commit'])}</code></span>",
        f"<span>Commit date {_e(stamp['date'])}</span>",
    ]
    if stamp["dirty"]:
        parts.append("<span>Inputs had uncommitted changes when generated</span>")
    return "".join(parts)


def _waiting_list(gate: dict[str, Any], plans: dict[str, dict[str, Any]],
                  phases: dict[str, dict[str, Any]]) -> str:
    items = gate["items"]
    if not items:
        return ""
    if gate["kind"] == "plans":
        rows = "".join(
            f'<tr><td class="id">{_e(code)}</td><td>{_e(plans[code]["title"])}</td></tr>'
            for code in items
        )
        head = "<tr><th>Plan</th><th>Title</th></tr>"
    elif gate["kind"] == "phases":
        rows = "".join(
            f'<tr><td class="id">{_e(key)}</td><td>{_e(phases[key]["title"])}</td>'
            f'<td>{_e(phases[key].get("agent", ""))}</td></tr>'
            for key in items
        )
        head = "<tr><th>Phase</th><th>Title</th><th>Agent</th></tr>"
    else:
        return (
            f"<details><summary>{len(items)} idea ids</summary>"
            f"<p>{' '.join(f'<code>{_e(i)}</code>' for i in items)}</p></details>"
        )
    return (
        f"<details><summary>{len(items)} waiting at {_e(gate['gate'])}</summary>"
        f'<div class="tbl-wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>'
        "</details>"
    )


def render_overview(inputs: dict[str, Any]) -> str:
    """The pipeline overview page: the nine stages and what is waiting at each gate."""
    data = overview_data(inputs)
    plans = {str(plan["code"]): plan for plan in inputs["plans"]}
    phases = {phase["id"]: phase for phase in inputs["phases"]}

    stats = (
        '<div class="stats">'
        f'<div><span class="lab">Ideas captured</span><span class="v acc" data-stat="ideas">'
        f'{data["ideas_total"]}</span><span class="d">fold() of the idea log</span></div>'
        f'<div><span class="lab">Triaged</span><span class="v" data-stat="triaged">'
        f'{data["ideas_triaged"]}</span><span class="d">status triaged now</span></div>'
        f'<div><span class="lab">Phases complete</span><span class="v" data-stat="complete">'
        f'{data["phases_complete"]}</span><span class="d">of {data["phases_total"]} in '
        "backlog.yaml</span></div>"
        '<div><span class="lab">Owner gates</span><span class="v">5</span>'
        '<span class="d">G1 to G5, ARCH-006</span></div>'
        "</div>"
    )
    stage_rows = "".join(
        f'<tr><td class="num">{stage["n"]}</td><td>{_e(stage["name"])}</td>'
        f'{_count_cell("stage", stage["n"], stage["items"])}'
        f'<td>{_e(stage["counts"])}</td><td>{_e(stage["source"])}</td></tr>'
        for stage in data["stages"]
    )
    stages = (
        '<section class="section"><h2>Stages</h2>'
        "<p>Each count is what sits at that stage now, read from the named source.</p>"
        '<div class="tbl-wrap"><table><thead><tr><th class="num">#</th><th>Stage</th>'
        '<th class="num">Count</th><th>What is counted</th><th>Source</th></tr></thead>'
        f"<tbody>{stage_rows}</tbody></table></div></section>"
    )
    gate_blocks = []
    for gate in data["gates"]:
        count = (
            f'<span class="v" data-gate="{_e(gate["gate"])}">{len(gate["items"])}</span>'
            if gate["items"] is not None
            else f'<span class="v" data-gate="{_e(gate["gate"])}">'
            f'{data["ideas_total"]}</span>'
        )
        gate_blocks.append(
            '<div class="section">'
            f'<h3><span class="gate">{_e(gate["gate"])}</span> {_e(gate["decision"])}</h3>'
            f"<p>{count} — {_e(gate['waiting'])}. Source: {_e(gate['source'])}.</p>"
            f"{_waiting_list(gate, plans, phases)}</div>"
        )
    gates = '<section class="section"><h2>Gates</h2>' + "".join(gate_blocks) + "</section>"

    notes = [
        "G1 shows ideas captured, not a queue: the owner approves an idea in conversation, "
        "and the sanctioned writer records it only after that.",
        "Stages 5 and 6 show not recorded: adversarial reviews and phase-fit checks are written "
        "into session records as prose, with no structured record to count.",
        "Stage 4 and the G3 queue are the same plans by construction. Plan front matter does not "
        "record whether a draft is still being written, under review, or waiting for approval, "
        "so every draft plan is counted at stage 4 and listed at G3.",
    ]
    if data["ideas_field_present"]:
        notes.append(
            "Phase links come from backlog phases' ideas field, which names the ideas each "
            "phase's own scope, acceptance and next_action mention."
        )
    else:
        notes.append(
            "Phase links: not recorded. No backlog phase carries an ideas field yet, so G2 "
            "counts triaged ideas without promoted_to only."
        )
    if data["phases_blocked"]:
        notes.append(
            "Blocked phases, not counted in any stage: "
            + ", ".join(data["phases_blocked"]) + "."
        )
    callout = (
        '<div class="callout"><span class="lab">How to read this page</span>'
        + "".join(f"<p>{_e(note)}</p>" for note in notes)
        + "</div>"
    )
    pages = (
        '<p>Every idea, its status and its four axis values: '
        '<a href="ideas.html">idea funnel and ledger</a>.</p>'
    )
    body = "\n".join([stats, pages, stages, gates, callout])
    return _page(
        inputs["stamp"],
        title="Pipeline overview",
        lede="Where every idea, plan and phase sits in the idea realization engine, stage by "
        "stage, and what is waiting for the owner at each gate.",
        body=body,
    )


def trace_cell(row: dict[str, Any]) -> str:
    """The ledger's trace column. phase-des-11 replaces the linked case with the trace page link."""
    text = "trace page not yet generated" if row["has_plan"] else NO_RECORDED_PLAN
    return f'<td data-trace="{_e(row["id"])}">{_e(text)}</td>'


def _distribution(attr: str, counts: list[tuple[str, int]], total: int) -> str:
    rows = "".join(
        f'<tr><td>{_e(label)}</td><td class="num" data-{attr}="{_e(label)}">{count}</td></tr>'
        for label, count in counts
    )
    return (
        '<div class="tbl-wrap"><table><thead><tr><th>Value</th><th class="num">Ideas</th>'
        f"</tr></thead><tbody>{rows}"
        f'<tr><td>Total</td><td class="num">{total}</td></tr></tbody></table></div>'
    )


def render_ledger(inputs: dict[str, Any]) -> str:
    """The idea funnel and ledger page: every idea once, the status funnel, the axis views."""
    data = ledger_data(inputs)
    total = data["total"]

    stats = (
        '<div class="stats">'
        f'<div><span class="lab">Ideas</span><span class="v acc" data-stat="ideas">{total}'
        '</span><span class="d">fold() of the idea log</span></div>'
        f'<div><span class="lab">Classified</span><span class="v" data-stat="classified">'
        f'{data["classified"]}</span><span class="d">with a classified event</span></div>'
        f'<div><span class="lab">Unclassified</span><span class="v" data-stat="unclassified">'
        f'{total - data["classified"]}</span><span class="d">no classified event</span></div>'
        "</div>"
    )
    funnel = (
        '<section class="section"><h2>Funnel</h2>'
        "<p>Ideas at each status now, in the schema's status order. Source: fold().</p>"
        f'{_distribution("funnel", data["funnel"], total)}</section>'
    )
    axis_blocks = "".join(
        f'<div class="section"><h3>{_e(axis.capitalize())}</h3>'
        f'{_distribution("axis-" + axis, data["axes"][axis], total)}</div>'
        for axis in AXES
    )
    axes = (
        '<section class="section"><h2>Classification axes</h2>'
        "<p>Each ARCH-005 axis, every value the idea schema allows. An idea with no classified "
        'event counts as unclassified. A collection, fixture or reference record carries no '
        "axis values and counts under its record kind. Source: fold(); schemas/idea.schema.json."
        f"</p>{axis_blocks}</section>"
    )
    head = "".join(f"<th>{_e(axis.capitalize())}</th>" for axis in AXES)
    rows = "".join(
        f'<tr data-idea="{_e(row["id"])}"><td class="id">{_e(row["id"])}</td>'
        f'<td>{_e(row["title"])}</td><td>{_e(row["status"])}</td><td>{_e(row["created"])}</td>'
        + "".join(f"<td>{_e(row['axes'][axis])}</td>" for axis in AXES)
        + trace_cell(row)
        + "</tr>"
        for row in data["rows"]
    )
    ledger = (
        '<section class="section"><h2>Ledger</h2>'
        "<p>Every idea in fold(), once, by id. Created is the date the idea was captured.</p>"
        '<div class="tbl-wrap"><table><thead><tr><th>Idea</th><th>Title</th><th>Status</th>'
        f"<th>Created</th>{head}<th>Trace</th></tr></thead><tbody>{rows}</tbody></table></div>"
        "</section>"
    )
    notes = [
        "Trace: an idea with a recorded plan, through promoted_to or a backlog phase's ideas "
        "field, gets a trace page in a later phase. Until then its row says so. Every other idea "
        f"reads {NO_RECORDED_PLAN}.",
    ]
    if not data["ideas_field_present"]:
        notes.append(
            "Phase links: not recorded. No backlog phase carries an ideas field yet, so only "
            "promoted_to counts as a recorded plan."
        )
    callout = (
        '<div class="callout"><span class="lab">How to read this page</span>'
        + "".join(f"<p>{_e(note)}</p>" for note in notes)
        + "</div>"
    )
    back = '<p>Back to the <a href="index.html">pipeline overview</a>.</p>'
    body = "\n".join([stats, back, funnel, axes, ledger, callout])
    return _page(
        inputs["stamp"],
        title="Idea funnel and ledger",
        lede="Every captured idea once, how many sit at each status, and how the ideas spread "
        "across the four ARCH-005 classification axes.",
        body=body,
    )


def _page(stamp: dict[str, Any], title: str, lede: str, body: str) -> str:
    styles = (
        house.OUTPUT.read_text(encoding="utf-8")
        + "\n"
        + house.COMPONENTS_CSS.read_text(encoding="utf-8")
    )
    template = house._strip_leading_comment(house.PAGE.read_text(encoding="utf-8"))
    return house.fill(
        template,
        {
            "ROOT_ATTRS": "",
            "PAGE_TITLE": f"{title} — idea realization engine",
            "INLINE_STYLES": styles,
            "KICKER": "d-system · idea realization engine",
            "HEADING": _e(title),
            "LEDE": _e(lede),
            "META": _stamp_meta(stamp),
            "BODY": body,
            "FOOTER": "Generated by tools/generate_engine_pages.py from the idea log, "
            "backlog.yaml and plan front matter at the source commit above. A committed "
            "snapshot: regenerate to bring it up to date.",
        },
    )


#: Output file name to renderer. Later phases add the trace and backlog pages here.
PAGES: dict[str, Callable[[dict[str, Any]], str]] = {
    "index.html": render_overview,
    "ideas.html": render_ledger,
}


def render_all(inputs: dict[str, Any]) -> dict[str, str]:
    """Every engine page, keyed by its file name under the output directory."""
    return {name: render(inputs) for name, render in PAGES.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the idea realization engine pages.")
    parser.add_argument("--out", type=Path, default=OUT, help="output directory")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in render_all(load_inputs()).items():
        (args.out / name).write_text(text, encoding="utf-8")
        print(f"wrote {args.out / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
