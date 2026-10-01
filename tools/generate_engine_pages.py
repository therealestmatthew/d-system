#!/usr/bin/env python3
"""Generate the idea realization engine's pages into `_public/engine/` — `REQ-036` R07-R14.

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

from src.db.ideas import fold, load_events  # noqa: E402
from src.governance.__main__ import markdown_paths, parse_frontmatter  # noqa: E402
from src.governance.backlog import readiness  # noqa: E402
from tools import generate_house_css as house  # noqa: E402

OUT = ROOT / "_public" / "engine"

#: Paths whose uncommitted changes would make the commit stamp misdescribe what was read.
INPUT_PATHS = ("_data/ideas.jsonl", "docs/09-backlog", "docs/01-plans", "templates")

NOT_RECORDED = "not recorded"


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
    body = "\n".join([stats, stages, gates, callout])
    return _page(
        inputs["stamp"],
        title="Pipeline overview",
        lede="Where every idea, plan and phase sits in the idea realization engine, stage by "
        "stage, and what is waiting for the owner at each gate.",
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


#: Output file name to renderer. Later phases add the ledger, trace and backlog pages here.
PAGES: dict[str, Callable[[dict[str, Any]], str]] = {
    "index.html": render_overview,
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
