"""Build boundary-overview.html, the one-page view of the system boundary validation.

Run from the repository root:

    uv run python docs/00-working/boundary-study/build_boundary_overview.py            # write the HTML
    uv run python docs/00-working/boundary-study/build_boundary_overview.py --markdown # print report tables

Every figure is read from git at a named commit, so the page and the validation report draw on
the same numbers. The only hand-entered data are the validation's per-prompt default-entry-point
values (validation-report.md, section 2), which are a judgement, not a count.

Ungoverned working file for the 2026-09-28 validation (ran unclaimed: owner-directed work with no
backlog phase; no peer holds a lock against it).
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

TIP = "9772c21"  # origin/dev when the validation ran
INVENTORY_BASE = "2fd11e9"  # phase-bnd-01 baseline (system inventory, boundary map)
PROMPT_BASE = "7e3a067"  # phase-bnd-05 baseline (prompt corpus inventory)
REVIEW_BASE = "4f3848e"  # phase-bnd-03 baseline (portfolio review)
RECONCILED = "0c47c27"  # ARCH-012 reconciliation revision
DATE = "2026-09-28"
OUT = Path("docs/00-working/boundary-study/boundary-overview.html")


def show(commit: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], check=True, capture_output=True, text=True
    ).stdout


def prompt_codes(commit: str) -> list[str]:
    out = subprocess.run(
        ["git", "grep", "-l", "^kind: prompt$", commit, "--", "docs"],
        check=True, capture_output=True, text=True,
    ).stdout
    return sorted(re.search(r"PROMPT-\d+", line).group(0) for line in out.splitlines())  # type: ignore[union-attr]


def backlog(commit: str) -> dict:
    data = yaml.safe_load(show(commit, "docs/09-backlog/backlog.yaml"))
    items = data["items"]
    done = {p["id"] for p in items if p["status"] == "complete"}
    status = Counter(p["status"] for p in items)
    queued = [p for p in items if p["status"] == "queued"]
    ready = sum(1 for p in queued if all(d in done for d in p.get("depends_on") or []))
    return {
        "max_active": data["max_active"],
        "total": len(items),
        "complete": status["complete"],
        "active": status["active"],
        "deferred": status["deferred"],
        "blocked": status["blocked"],
        "ready": ready,
        "waiting": len(queued) - ready,
        "active_ids": [p["id"] for p in items if p["status"] == "active"],
    }


def registry(commit: str) -> list[dict]:
    return yaml.safe_load(show(commit, "docs/08-governance/systems.yaml"))["systems"]


# --- Concerns: the study's dispositions (system-interface-inventory.md), in a fixed order -------

CONCERNS = [
    # key, label, short label, what it owns (ARCH-012 concern table / inventory labels)
    ("personal-productivity core", "Personal-productivity core", "Personal",
     "Portfolio source records, memory, capture and retrieval"),
    ("idea-realization core", "Idea-realization core", "Realization",
     "The idea-to-delivery pipeline; orchestration still planned"),
    ("workbench core", "Workbench core", "Workbench",
     "Browser layout, panels, viewers, explorers, terminal"),
    ("cross-cutting framework", "Governance / framework", "Framework",
     "Validation, claims, backlog, CI and governance prose"),
    ("shared foundation", "Shared foundation", "Shared",
     "Schemas, DuckDB projection, HTTP API"),
    ("adjacent", "Adjacent", "Adjacent",
     "Related but separately bounded: plugin package, research, framework templates, demo kit"),
    ("incubating", "Incubating", "Incubating",
     "Planned systems with no present runtime (per the registry)"),
    ("retired", "Retired", "Retired", "Kept only as registry history"),
]
CONCERN_KEYS = [c[0] for c in CONCERNS]

# Registry entries whose `planned` status tracked code and completed phases contradict at TIP.
CONTESTED = {
    "sys-plugin": "plugins/idea-realization/ exists; phase-plug-01 to -09 complete",
    "sys-plugin-core": "phase-plug-01 and -08 complete",
    "sys-plugin-ideas": "phase-plug-02 complete",
    "sys-plugin-partition": "phase-plug-03 complete",
    "sys-plugin-backlog": "phase-plug-04 complete",
    "sys-plugin-documents": "phase-plug-05 complete",
    "sys-plugin-generators": "phase-plug-06 complete",
    "sys-plugin-absolutes": "phase-plug-07 and -09 complete",
    "sys-demo-overview": "tools/generate_overview.py exists; phase-demo-03 and -04 complete",
}


def dispositions() -> dict[str, str]:
    text = show(TIP, "docs/00-working/boundary-study/system-interface-inventory.md")
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\| `(sys-[a-z0-9-]+)` \| ([^|]+) \|", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


# --- Prompts: study value (prompt-corpus-inventory.md) and the validation's value ---------------

D, P, S, O, N = (
    "direct-operational-entry", "planning-sequence-start", "sequence-factory-step",
    "owner-launched-campaign", "no-default-known",
)
# code: (validation value, agreement, basis)
VALIDATION_ENTRY: dict[str, tuple[str, str, str]] = {
    "PROMPT-001": (D, "firm", "'Feed this prompt to a Claude instance' (line 17); no document names it as a step"),
    "PROMPT-002": (P, "agree", "definition session ending in requirement, plan and phases"),
    "PROMPT-003": (P, "agree", "ends in ADRs and phases; close call: requires PROMPT-004 first"),
    "PROMPT-004": (P, "agree", "first of the 004 then 003 sequence; close call: writes content, not a plan"),
    "PROMPT-005": (P, "agree", "ends in one ADR and phases; close call: run after PROMPT-004"),
    "PROMPT-006": (D, "agree", "rubric pilot"),
    "PROMPT-007": (P, "agree", "turns a triaged idea into a requirement, plan and phases"),
    "PROMPT-008": (D, "agree", "'run it repeatedly to advance the backlog'"),
    "PROMPT-009": (D, "firm", "'Reusable, and deliberately read-only. Run it periodically' (line 20), the same framing as PROMPT-008"),
    "PROMPT-010": (S, "agree", "rubric pilot"),
    "PROMPT-011": (S, "agree", "'Child of ... PROMPT-010, read at its Step 1'"),
    "PROMPT-012": (S, "agree", "'Child of ... PROMPT-010, read at its Step 2'"),
    "PROMPT-013": (S, "agree", "'Child of ... PROMPT-010, read at its Steps 3 and 4'"),
    "PROMPT-014": (O, "agree", "the demo build's pasted coordinator; no separate kick-off"),
    "PROMPT-015": (S, "firm", "'Child of ... PROMPT-014, read at its Step 1', the wording the inventory marks as a step for PROMPT-011"),
    "PROMPT-016": (S, "close", "'Child of ... PROMPT-014. Binding on the coordinator'; the study read it as a reference with no start"),
    "PROMPT-017": (S, "firm", "'Child of ... PROMPT-014, read at its Step 3'"),
    "PROMPT-018": (S, "firm", "delegation pack 'Every prompt the build coordinator sends', the shape of 021, 024, 029 and 032, all steps in the inventory"),
    "PROMPT-019": (O, "agree", "single dated dispatch for phase-demo-07; close call with a direct entry"),
    "PROMPT-020": (P, "agree", "rubric pilot"),
    "PROMPT-021": (S, "agree", "delegation pack"),
    "PROMPT-022": (S, "close", "coordinator; its kick-off PROMPT-023 is what is pasted and 'wins' where they differ"),
    "PROMPT-023": (O, "agree", "pasteable kick-off for the workbench build"),
    "PROMPT-024": (S, "agree", "delegation pack"),
    "PROMPT-025": (P, "agree", "Prompt A pre-plan package"),
    "PROMPT-026": (S, "agree", "Prompt B factory"),
    "PROMPT-027": (P, "agree", "Prompt A pre-plan package"),
    "PROMPT-028": (S, "agree", "Prompt B factory"),
    "PROMPT-029": (S, "agree", "delegation pack"),
    "PROMPT-030": (S, "close", "coordinator; its kick-off PROMPT-031 is what is pasted"),
    "PROMPT-031": (O, "agree", "kick-off record for the literature review"),
    "PROMPT-032": (S, "agree", "delegation pack"),
    "PROMPT-033": (O, "agree", "kick-off record for idea batching"),
    "PROMPT-034": (S, "agree", "pack a workflow dispatches verbatim"),
    "PROMPT-035": (O, "agree", "dated one-run review kickoff"),
    "PROMPT-036": (D, "agree", "generic, idempotent coordinator the owner pastes every batch"),
    "PROMPT-037": (D, "firm", "'a kickoff the owner pastes into the Session Manager session' (lines 17-20); nothing sequences it"),
    "PROMPT-038": (S, "agree", "dispatch prompt for GOV-018 step 3"),
    "PROMPT-040": (O, "agree", "rubric pilot"),
    "PROMPT-041": (D, "agree", "phase runner for this study, run directly each session"),
}
TIP_ONLY = {"PROMPT-042": (O, "new", "dated investigation pack with an owner-pasted kickoff (lines 596-607)")}

GROUPS = [
    ("Direct entry or planning start", (D, P)),
    ("Sequence step", (S,)),
    ("Owner-launched campaign", (O,)),
    ("No known entry", (N,)),
]


def study_entry() -> dict[str, str]:
    text = show(TIP, "docs/00-working/boundary-study/prompt-corpus-inventory.md")
    out = {}
    for line in text.splitlines():
        if line.startswith("| PROMPT-"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            out[cells[0]] = cells[5]
    return out


def group_counts(values: list[str]) -> list[int]:
    return [sum(1 for v in values if v in vals) for _, vals in GROUPS]


# --- Gather ---------------------------------------------------------------------------------------


def gather() -> dict:
    disp = dispositions()
    reg_tip = registry(TIP)
    reg_base = registry(RECONCILED)
    study = study_entry()
    base_codes = prompt_codes(PROMPT_BASE)
    tip_codes = prompt_codes(TIP)
    assert set(study) == set(base_codes) == set(VALIDATION_ENTRY), "prompt sets differ"
    assert set(tip_codes) - set(base_codes) == set(TIP_ONLY), "tip-only prompts differ"
    val_base = [VALIDATION_ENTRY[c][0] for c in base_codes]
    val_tip = val_base + [TIP_ONLY[c][0] for c in TIP_ONLY]
    systems = []
    for s in reg_tip:
        systems.append({
            "id": s["id"], "name": s["name"], "status": s["status"],
            "concern": disp[s["id"]], "contested": CONTESTED.get(s["id"]),
        })
    assert len(systems) == len(disp) == 43
    return {
        "systems": systems,
        "maturity_base": Counter(s["status"] for s in reg_base),
        "maturity_tip": Counter(s["status"] for s in reg_tip),
        "prompts_base": len(base_codes),
        "prompts_tip": len(tip_codes),
        "study_groups": group_counts([study[c] for c in base_codes]),
        "val_base_groups": group_counts(val_base),
        "val_tip_groups": group_counts(val_tip),
        "study": study,
        "backlog_base": backlog(RECONCILED),
        "backlog_review": backlog(REVIEW_BASE),
        "backlog_tip": backlog(TIP),
    }


# --- Markdown for the report ----------------------------------------------------------------------


def markdown(g: dict) -> str:
    lines = ["| System | Registry status at tip | Concern | Source of the assignment |", "|---|---|---|---|"]
    for s in sorted(g["systems"], key=lambda x: (CONCERN_KEYS.index(x["concern"]), x["id"])):
        src = "system-interface-inventory.md, `" + s["id"] + "` row"
        if s["contested"]:
            src += f"; contested: registry says {s['status']}, but {s['contested']}"
        lines.append(f"| `{s['id']}` | {s['status']} | {s['concern']} | {src} |")
    lines += ["", "| Prompt | Study value | Validation value | Agreement | Basis |", "|---|---|---|---|---|"]
    for code, (val, agr, basis) in {**VALIDATION_ENTRY, **TIP_ONLY}.items():
        lines.append(f"| {code} | {g['study'].get(code, '(not in study)')} | {val} | {agr} | {basis} |")
    lines += ["", f"study groups {g['study_groups']}; validation at baseline {g['val_base_groups']}; "
              f"validation at tip {g['val_tip_groups']}"]
    return "\n".join(lines)


# --- HTML -----------------------------------------------------------------------------------------

E = html.escape

CSS = """
:root{color-scheme:light;
 --page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#6b6a65;--grid:#e1e0d9;
 --base:#c3c2b7;--ring:rgba(11,11,11,.12);
 --c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a;--c4:#eda100;--c5:#e87ba4;--c6:#008300;--c7:#4a3aa7;--c8:#9a998f;
 --m-impl:#0b0b0b;--m-scaf:#6b6a65;--m-plan:#c3c2b7;--m-ret:#e1e0d9;
 --ok-bg:#e3f1e3;--ok-ink:#0b4d0b;--drift-bg:#fdf1d6;--drift-ink:#5c3d00;--err-bg:#fbe3e3;--err-ink:#7a1616;}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;
 --page:#0d0d0d;--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#a3a29a;--grid:#2c2c2a;
 --base:#383835;--ring:rgba(255,255,255,.14);
 --c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300;--c7:#9085e9;--c8:#77766f;
 --m-impl:#ffffff;--m-scaf:#a3a29a;--m-plan:#55544f;--m-ret:#2c2c2a;
 --ok-bg:#12301a;--ok-ink:#b6e8b6;--drift-bg:#3a2c08;--drift-ink:#f6d98f;--err-bg:#3d1414;--err-ink:#f7b9b9;}}
:root[data-theme="dark"]{color-scheme:dark;
 --page:#0d0d0d;--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#a3a29a;--grid:#2c2c2a;
 --base:#383835;--ring:rgba(255,255,255,.14);
 --c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300;--c7:#9085e9;--c8:#77766f;
 --m-impl:#ffffff;--m-scaf:#a3a29a;--m-plan:#55544f;--m-ret:#2c2c2a;
 --ok-bg:#12301a;--ok-ink:#b6e8b6;--drift-bg:#3a2c08;--drift-ink:#f6d98f;--err-bg:#3d1414;--err-ink:#f7b9b9;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 48px}
header.top{padding:8px 0 20px;border-bottom:1px solid var(--grid);margin-bottom:24px}
h1{font-size:26px;line-height:1.2;margin:0 0 6px}
h2{font-size:18px;margin:0 0 4px}
h3{font-size:14px;margin:0 0 6px}
.meta{color:var(--ink2);font-size:13px;margin:0}
.note{color:var(--ink2);font-size:13px;margin:6px 0 0}
section{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:18px 16px;margin:0 0 18px}
.cap{color:var(--ink2);font-size:13px;margin:0 0 14px}
.num{font-variant-numeric:tabular-nums}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:6px;flex:none}
.k-personal-productivity-core{--c:var(--c1)}.k-idea-realization-core{--c:var(--c2)}.k-workbench-core{--c:var(--c3)}
.k-cross-cutting-framework{--c:var(--c4)}.k-shared-foundation{--c:var(--c5)}.k-adjacent{--c:var(--c6)}
.k-incubating{--c:var(--c7)}.k-retired{--c:var(--c8)}
.sw{background:var(--c)}
.grid{display:grid;gap:12px}
.cmap{grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.card{border:1px solid var(--ring);border-left:5px solid var(--c);border-radius:8px;padding:10px 12px;background:var(--page)}
.card h3{display:flex;align-items:center;gap:4px;justify-content:space-between}
.card h3 span.t{display:flex;align-items:center}
.card p{margin:0 0 8px;color:var(--ink2);font-size:13px}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font:12px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:2px 6px;border-radius:5px;border:1px solid var(--ring);background:var(--surface);white-space:nowrap}
.chip.contested{outline:2px dashed var(--ink2);outline-offset:-1px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--ink2);margin:10px 0 0}
.two{grid-template-columns:minmax(0,1fr)}
@media (max-width:640px){table.fig thead{display:none}table.fig,table.fig tbody,table.fig tr,table.fig td{display:block;width:100%}
 table.fig tr{border-bottom:1px solid var(--grid);padding:6px 0}table.fig td{border:0;padding:2px 0;text-align:left}
 table.fig td.num::before{content:attr(data-label) ": ";color:var(--ink2);font-size:12px}}
@media (min-width:860px){.two{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.xsvg{width:100%;max-width:520px;height:auto;display:block;margin:0 auto}
.xsvg text{font:600 11px system-ui,-apple-system,"Segoe UI",sans-serif;fill:var(--ink)}
.xsvg .n{font-weight:700;font-size:11px}
ol.edges{margin:0;padding-left:0;list-style:none;font-size:13.5px}
ol.edges li{display:flex;gap:8px;padding:6px 0;border-bottom:1px solid var(--grid)}
ol.edges li:last-child{border-bottom:0}
.bn{flex:none;display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;border:1.5px solid var(--ink);font-size:11px;font-weight:700}
.bn.plan{border-style:dashed}.bn.found{background:var(--ink);color:var(--surface)}
.pro{color:var(--ink2);font-size:12.5px;display:block}
.bars{display:grid;gap:8px}
.brow{display:grid;grid-template-columns:minmax(110px,190px) minmax(0,1fr) auto;gap:10px;align-items:center;font-size:13px}
.track{display:flex;height:18px;gap:2px;min-width:0}
.seg{height:100%;border-radius:2px}
.seg:first-child{border-radius:4px 2px 2px 4px}.seg:last-child{border-radius:2px 4px 4px 2px}.seg:only-child{border-radius:4px}
.m-implemented{background:var(--m-impl)}.m-scaffold{background:var(--m-scaf)}.m-planned{background:var(--m-plan)}.m-retired{background:var(--m-ret);outline:1px solid var(--base);outline-offset:-1px}
.m-built{background:repeating-linear-gradient(135deg,var(--m-plan) 0 3px,var(--m-scaf) 3px 5px)}
.lbl{display:flex;align-items:center;min-width:0}
.lbl span{overflow-wrap:anywhere}
.gb{display:grid;grid-template-columns:minmax(120px,210px) minmax(0,1fr);gap:4px 10px;align-items:center;font-size:13px}
.gb .bar{height:14px;border-radius:0 4px 4px 0;min-width:2px}
.gb .ser{display:flex;align-items:center;gap:8px}
.gb .ser span{font-size:12px;color:var(--ink2);min-width:0}
.gb .glab{grid-row:span var(--span);align-self:center}
@media (max-width:560px){.gb{grid-template-columns:minmax(0,1fr)}.gb .glab{grid-row:auto;margin-top:4px}.gsep{display:none}}
.s-study{background:var(--m-plan)}.s-base{background:var(--m-scaf)}.s-tip{background:var(--m-impl)}
.gsep{grid-column:1/-1;height:6px}
.meter{display:flex;gap:6px;margin:6px 0}
.slot{min-width:56px;padding:0 6px;white-space:nowrap;height:26px;border-radius:5px;border:1.5px solid var(--base);display:grid;place-items:center;font-size:11px;font-weight:600}
.slot.on{background:var(--m-impl);color:var(--surface);border-color:var(--m-impl)}
.slot.on.self{background:var(--m-scaf);border-color:var(--m-scaf)}
.opts{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.opt{border:1px solid var(--ring);border-radius:8px;padding:12px;background:var(--page);display:flex;flex-direction:column;gap:6px}
.opt dl{margin:0;font-size:13px}
.opt dt{font-weight:600;color:var(--ink2);font-size:12px;text-transform:uppercase;letter-spacing:.03em;margin-top:6px}
.opt dd{margin:2px 0 0}
.verdict{border-radius:6px;padding:7px 9px;font-size:13px}
.v-study{border:1px solid var(--base)}
.v-val{border:1.5px solid var(--ink)}
.tag{display:inline-block;font-size:11.5px;font-weight:700;padding:1px 7px;border-radius:10px;white-space:nowrap}
.t-correct{background:var(--ok-bg);color:var(--ok-ink)}.t-drift{background:var(--drift-bg);color:var(--drift-ink)}.t-error{background:var(--err-bg);color:var(--err-ink)}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{font-size:12px;color:var(--ink2);font-weight:600}
td.num,th.num{text-align:right}
.steps{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.steps ul{margin:0;padding-left:18px;font-size:13px}
.steps li{margin:0 0 6px}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
footer{color:var(--ink2);font-size:12.5px;border-top:1px solid var(--grid);padding-top:14px}
footer p{margin:0 0 6px}
"""

STATUS_ORDER = ["implemented", "scaffold", "planned", "retired"]


def sw(key: str) -> str:
    return f'<span class="sw k-{key.replace(" ", "-")}" aria-hidden="true"></span>'


def concern_map(g: dict) -> str:
    cards = []
    marks = {"implemented": "●", "scaffold": "◐", "planned": "○", "retired": "×"}
    for key, label, _short, owns in CONCERNS:
        members = sorted((s for s in g["systems"] if s["concern"] == key), key=lambda s: s["id"])
        chips = "".join(
            f'<span class="chip{" contested" if s["contested"] else ""}" '
            f'title="{E(s["name"])} ({s["status"]}{"; " + E(s["contested"]) if s["contested"] else ""})">'
            f'{marks[s["status"]]} {E(s["id"].removeprefix("sys-"))}</span>'
            for s in members
        )
        cards.append(
            f'<div class="card k-{key.replace(" ", "-")}"><h3><span class="t">{sw(key)}{E(label)}</span>'
            f'<span class="num">{len(members)}</span></h3><p>{E(owns)}</p><div class="chips">{chips}</div></div>'
        )
    return (
        '<div class="grid cmap">' + "".join(cards) + "</div>"
        '<p class="legend"><span>● implemented</span><span>◐ scaffold</span><span>○ planned</span>'
        '<span>× retired</span><span><span class="chip contested">dashed</span> registry says planned; '
        "tracked code and completed phases say built</span><span>Names drop the <code>sys-</code> prefix.</span></p>"
    )


# Crossings: (number, from, to, label, kind) kind: current | planned | found
EDGES = [
    (1, "personal-productivity core", "shared foundation", "Portfolio and memory files rebuilt into DuckDB", "current"),
    (2, "shared foundation", "personal-productivity core", "Read-only context CLI over the projection", "current"),
    (3, "personal-productivity core", "idea-realization core", "The idea log is the pipeline's source", "current"),
    (4, "cross-cutting framework", "idea-realization core", "Phase lifecycle and validation", "current"),
    (5, "cross-cutting framework", "personal-productivity core", "Claim, validation and CI rules", "current"),
    (6, "cross-cutting framework", "workbench core", "Repository-state inputs (backlog.yaml) and development rules", "current"),
    (7, "workbench core", "shared foundation", "HTTP API and the loopback-gated terminal backend", "current"),
    (8, "adjacent", "personal-productivity core", "Adapters (planned)", "planned"),
    (9, "adjacent", "cross-cutting framework", "Packaging and analysis (planned; the plugin package is now built)", "planned"),
    (10, "personal-productivity core", "workbench core", "Idea state read by the workbench API through fold() (src/api/routes/workbench.py:532)", "found"),
]
PROHIBITED = [
    ("Personal ↔ shared", "DuckDB never becomes the authority for portfolio or memory records."),
    ("Personal ↔ realization", "The pipeline never changes idea lineage or owner approvals outside the record and gates."),
    ("Realization ↔ framework", "Governance never decides product priority, integration or completion."),
    ("Workbench ↔ shared", "A panel never owns or bypasses the terminal backend's loopback gating."),
    ("Framework → all", "Framework systems never become the authority for portfolio content or workbench user state."),
    ("Adjacent → cores", "A planned system is never presented as an implemented interface."),
]

# Node boxes in a 360 x 330 viewBox: key -> (x, y, w, h, line1, line2)
NODES = {
    "shared foundation": (8, 8, 96, 58, "Shared", "foundation"),
    "personal-productivity core": (132, 8, 96, 58, "Personal", "core"),
    "adjacent": (256, 8, 96, 58, "Adjacent and", "incubating"),
    "workbench core": (8, 132, 96, 58, "Workbench", "core"),
    "idea-realization core": (132, 132, 96, 58, "Realization", "core"),
    "cross-cutting framework": (8, 262, 344, 50, "Governance / framework", "(applies to every concern)"),
}


def crossings_svg() -> str:
    def color(key: str) -> str:
        idx = CONCERN_KEYS.index(key if key != "adjacent" else "adjacent") + 1
        return f"var(--c{idx})"

    parts = [
        '<svg class="xsvg" viewBox="0 0 360 322" role="img" aria-labelledby="xs-t xs-d">'
        '<title id="xs-t">Crossings between concerns</title>'
        '<desc id="xs-d">Boxes are concerns; numbered arrows are crossings listed beside the diagram. '
        "Dashed arrows are planned; the filled number is a crossing the study's map omits.</desc>"
        "<defs>"
        '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="var(--ink2)"/></marker></defs>'
    ]
    for key, (x, y, w, h, l1, l2) in NODES.items():
        c = color(key)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="var(--surface)" stroke="{c}" stroke-width="2.5"/>'
            f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{c}"/>'
            f'<text x="{x + w / 2 + 3}" y="{y + h / 2 - 3}" text-anchor="middle">{E(l1)}</text>'
            f'<text x="{x + w / 2 + 3}" y="{y + h / 2 + 12}" text-anchor="middle" style="font-weight:400">{E(l2)}</text>'
        )
    # (number, path d, label x, label y, kind)
    lines = [
        (1, "M130,30 L106,30", 118, 16, "current"),  # personal -> shared
        (2, "M106,46 L130,46", 118, 61, "current"),  # shared -> personal (drawn short; numbers carry it)
        (3, "M180,68 L180,130", 180, 99, "current"),  # personal -> realization
        (4, "M180,260 L180,192", 180, 226, "current"),  # framework -> realization
        (5, "M242,260 L242,100 L216,100 L216,68", 242, 196, "current"),  # framework -> personal
        (6, "M56,260 L56,192", 56, 226, "current"),  # framework -> workbench
        (7, "M56,130 L56,68", 56, 99, "current"),  # workbench -> shared
        (8, "M254,38 L230,38", 242, 22, "planned"),  # adjacent -> personal
        (9, "M304,68 L304,260", 304, 164, "planned"),  # adjacent -> framework
        (10, "M144,68 L100,130", 122, 99, "found"),  # personal -> workbench
    ]
    for n, d, lx, ly, kind in lines:
        dash = ' stroke-dasharray="5 4"' if kind == "planned" else ""
        parts.append(f'<path d="{d}" fill="none" stroke="var(--ink2)" stroke-width="1.6"{dash} marker-end="url(#ah)"/>')
    for n, d, lx, ly, kind in lines:
        fill = "var(--ink)" if kind == "found" else "var(--surface)"
        tfill = "var(--surface)" if kind == "found" else "var(--ink)"
        dash = ' stroke-dasharray="3 2"' if kind == "planned" else ""
        parts.append(
            f'<circle cx="{lx}" cy="{ly}" r="8.5" fill="{fill}" stroke="var(--ink)" stroke-width="1.3"{dash}/>'
            f'<text class="n" x="{lx}" y="{ly + 4}" text-anchor="middle" style="fill:{tfill}">{n}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def crossings(g: dict) -> str:
    items = []
    short = {c[0]: c[2] for c in CONCERNS}
    for n, a, b, label, kind in EDGES:
        cls = {"planned": " plan", "found": " found"}.get(kind, "")
        extra = {"planned": " (planned)", "found": " (found by the validation; not in the study's map)"}.get(kind, "")
        items.append(
            f'<li><span class="bn{cls}">{n}</span><span><strong>{short[a]} → {short[b]}</strong>{E(extra)}'
            f'<span class="pro">{E(label)}</span></span></li>'
        )
    pro = "".join(f"<li><span class=\"bn\">⊘</span><span><strong>{E(a)}</strong><span class=\"pro\">{E(b)}</span></span></li>" for a, b in PROHIBITED)
    return (
        '<div class="grid two"><div>' + crossings_svg() + "</div><div><h3>Allowed crossings</h3>"
        f'<ol class="edges">{"".join(items)}</ol></div></div>'
        f'<h3 style="margin-top:14px">Prohibited ownership crossings (one per boundary)</h3><ol class="edges">{pro}</ol>'
    )


def maturity(g: dict) -> str:
    rows = []
    total = Counter(s["status"] for s in g["systems"])
    built = sum(1 for s in g["systems"] if s["contested"])

    def bar(counts: Counter, contested: int, scale: int) -> str:
        segs = []
        for st in STATUS_ORDER:
            n = counts.get(st, 0)
            if st == "planned" and contested:
                if n - contested:
                    segs.append(f'<span class="seg m-planned" style="width:{(n - contested) / scale * 100:.2f}%" title="planned: {n - contested}"></span>')
                segs.append(f'<span class="seg m-built" style="width:{contested / scale * 100:.2f}%" title="planned in the registry but built: {contested}"></span>')
            elif n:
                segs.append(f'<span class="seg m-{st}" style="width:{n / scale * 100:.2f}%" title="{st}: {n}"></span>')
        return '<span class="track">' + "".join(segs) + "</span>"

    def label(counts: Counter) -> str:
        return " · ".join(f"{counts[s]} {s[:4]}." for s in STATUS_ORDER if counts.get(s))

    rows.append(
        f'<div class="brow"><span class="lbl"><strong>All 43 systems</strong></span>{bar(total, built, 43)}'
        f'<span class="num">{total["implemented"]} impl. · {total["scaffold"]} scaf. · {total["planned"]} plan. · {total["retired"]} ret.</span></div>'
    )
    for key, label_, _s, _o in CONCERNS:
        mem = [s for s in g["systems"] if s["concern"] == key]
        c = Counter(s["status"] for s in mem)
        con = sum(1 for s in mem if s["contested"])
        rows.append(
            f'<div class="brow"><span class="lbl">{sw(key)}<span>{E(label_)}</span></span>{bar(c, con, 17)}'
            f'<span class="num">{label(c)}</span></div>'
        )
    return (
        '<div class="bars">' + "".join(rows) + "</div>"
        '<p class="legend"><span><span class="sw" style="background:var(--m-impl)"></span>implemented</span>'
        '<span><span class="sw" style="background:var(--m-scaf)"></span>scaffold</span>'
        '<span><span class="sw" style="background:var(--m-plan)"></span>planned</span>'
        '<span><span class="sw m-built"></span>planned in the registry, built in code</span>'
        '<span><span class="sw m-retired"></span>retired</span>'
        "<span>Per-concern bars share one scale (17 systems = full width).</span></p>"
    )


def prompts(g: dict) -> str:
    rows = []
    series = [
        ("s-study", f"Study ({g['prompts_base']} prompts)", g["study_groups"]),
        ("s-base", f"Validation, same baseline ({g['prompts_base']})", g["val_base_groups"]),
        ("s-tip", f"Validation at tip ({g['prompts_tip']})", g["val_tip_groups"]),
    ]
    for i, (name, _v) in enumerate(GROUPS):
        rows.append(f'<div class="glab" style="--span:3"><strong>{E(name)}</strong></div>')
        for cls, sname, vals in series:
            n = vals[i]
            rows.append(
                f'<div class="ser"><span class="bar {cls}" style="width:{n / 20 * 100 * 0.8:.2f}%" title="{E(sname)}: {n}"></span>'
                f'<span><strong class="num">{n}</strong> · {E(sname.split(" (")[0])}</span></div>'
            )
        rows.append('<div class="gsep"></div>')
    return (
        '<div class="gb">' + "".join(rows) + "</div>"
        '<p class="legend"><span><span class="sw s-study"></span>Study (inventory at 7e3a067)</span>'
        '<span><span class="sw s-base"></span>Validation re-classification, same 40 prompts</span>'
        '<span><span class="sw s-tip"></span>Validation at tip, with PROMPT-042 added</span></p>'
    )


def backlog_view(g: dict) -> str:
    b0, b1 = g["backlog_base"], g["backlog_tip"]
    keys = [("complete", "Complete"), ("ready", "Ready"), ("waiting", "Waiting"), ("deferred", "Deferred"),
            ("blocked", "Blocked"), ("active", "Active")]
    scale = max(max(b0[k] for k, _ in keys), max(b1[k] for k, _ in keys))
    rows = []
    for k, name in keys:
        rows.append(f'<div class="glab" style="--span:2"><strong>{name}</strong></div>')
        for cls, lab, b in (("s-base", f"Study ({RECONCILED})", b0), ("s-tip", f"Tip ({TIP})", b1)):
            rows.append(
                f'<div class="ser"><span class="bar {cls}" style="width:{b[k] / scale * 80:.2f}%" title="{lab}: {b[k]}"></span>'
                f'<span><strong class="num">{b[k]}</strong> · {lab.split(" (")[0]}</span></div>'
            )
        rows.append('<div class="gsep"></div>')

    def meter(b: dict, who: list[str]) -> str:
        cells = []
        for i in range(b["max_active"]):
            if i < len(who):
                self_ = " self" if who[i].startswith("phase-bnd") else ""
                cells.append(f'<span class="slot on{self_}" title="{who[i]}">{who[i].removeprefix("phase-")}</span>')
            else:
                cells.append('<span class="slot" title="free">free</span>')
        return '<div class="meter">' + "".join(cells) + "</div>"

    return (
        '<div class="grid two"><div><h3>Phases by state</h3><div class="gb">' + "".join(rows) + "</div>"
        f'<p class="legend"><span><span class="sw s-base"></span>Study: {b0["total"]} phases at {RECONCILED}</span>'
        f'<span><span class="sw s-tip"></span>Tip: {b1["total"]} phases at {TIP}</span></p></div>'
        f'<div><h3>Active claims against <code>max_active</code> = {b1["max_active"]}</h3>'
        f'<p class="cap" style="margin:0">Study ({RECONCILED}): {b0["active"]} of {b0["max_active"]}</p>{meter(b0, b0["active_ids"])}'
        f'<p class="cap" style="margin:0">Tip ({TIP}): {b1["active"]} of {b1["max_active"]}</p>{meter(b1, b1["active_ids"])}'
        '<p class="note">At the study\'s revision three slots held plugin build phases and the lighter slot held the '
        "study's own phase. This branch adds nine deferred phases (phase-bnd-06 to -14), which are not counted "
        "in the tip bars.</p></div></div>"
    )


OPTIONS = [
    ("A", "One repository, explicit contracts",
     "All four concerns and the framework", "Nothing now; ownership and crossings are written down and checked",
     "Lowest. Needs discipline so the boundaries hold; registry statuses must be corrected first",
     "A concern shows an independent audience, release need and stable contract",
     "Recommended now.",
     "Still the lowest-cost fit: the realization core has one registered system, and it is planned; the idea log is read by the workbench API and the pipeline, and one backlog lock table covers all work. Two supporting statements need correcting (claim load, plugin)."),
    ("B", "Prepare selective extraction",
     "Source records (portfolio, idea log) and everything not extracted",
     "One proven capability: the plugin, the workbench or the framework",
     "Versioning, compatibility, publishing, cross-repository governance",
     "A candidate meets all five preconditions: contract, independent tests, audience, maintainer, change pressure",
     "Conditional future path; do not nominate a candidate yet.",
     "Stronger than the study shows: the idea-realization plugin is already packaged for other repositories with 497 tests, but CI does not run them, 3 fail, and no audience or release cadence is recorded."),
    ("C", "Split now into four repositories",
     "Nothing across concerns", "Personal, realization, workbench and framework, each versioned",
     "High: migration, duplicated governance, external contracts for planned systems, loss of atomic changes",
     "Every concern has stable ownership, interfaces, release need and migration resources",
     "Rejected.",
     "The corrected evidence strengthens the rejection: the realization core has no implemented system to move, and the workbench reads the idea log directly."),
]


def options() -> str:
    cards = []
    for letter, name, keeps, seps, cost, trig, study, val in OPTIONS:
        cards.append(
            f'<div class="opt"><h3>Option {letter}: {E(name)}</h3><dl>'
            f"<dt>Keeps together</dt><dd>{E(keeps)}</dd><dt>Separates</dt><dd>{E(seps)}</dd>"
            f"<dt>Cost</dt><dd>{E(cost)}</dd><dt>Extraction trigger</dt><dd>{E(trig)}</dd></dl>"
            f'<div class="verdict v-study"><strong>Study (ARCH-012):</strong> {E(study)}</div>'
            f'<div class="verdict v-val"><strong>Validation re-assessment:</strong> {E(val)}</div></div>'
        )
    return '<div class="grid opts">' + "".join(cards) + "</div>"


def figures(g: dict) -> str:
    b0, br, b1 = g["backlog_base"], g["backlog_review"], g["backlog_tip"]
    mb, mt = g["maturity_base"], g["maturity_tip"]
    sg, vb, vt = g["study_groups"], g["val_base_groups"], g["val_tip_groups"]

    def split(v: list[int]) -> str:
        return " / ".join(str(x) for x in v)

    def mat(m: Counter) -> str:
        return " / ".join(str(m[s]) for s in STATUS_ORDER)

    rows = [
        ("Governed prompts", "40", str(g["prompts_base"]), str(g["prompts_tip"]), "drift"),
        ("Entry-point split (direct or planning / step / campaign / none)", "13 / 14 / 12 / 1", split(vb), split(vt), "error"),
        ("Registry (implemented / scaffold / planned / retired)", "17 / 4 / 21 / 1", mat(mb), mat(mt), "correct"),
        ("Claim limit fully occupied", "4 of 4", f"{b0['active']} of {b0['max_active']}", f"{b1['active']} of {b1['max_active']}", "drift"),
        ("Phases at reconciliation (total; complete / active / deferred / ready / waiting)",
         "323; 117 / 4 / 8 / 84 / 110",
         f"{b0['total']}; {b0['complete']} / {b0['active']} / {b0['deferred']} / {b0['ready']} / {b0['waiting']}",
         f"{b1['total']}; {b1['complete']} / {b1['active']} / {b1['deferred']} / {b1['ready']} / {b1['waiting']} (+{b1['blocked']} blocked)",
         "drift"),
        ("Portfolio review phases (complete / ready / waiting)", "116 / 84 / 111",
         f"{br['complete']} / {br['ready']} / {br['waiting']}", f"{b1['complete']} / {b1['ready']} / {b1['waiting']}", "drift"),
        ("Navigation prose: campaigns or sequence steps", "Twenty-three", "26 (12 + 14 in its own table)", "—", "error"),
    ]
    body = "".join(
        f"<tr><td><strong>{E(a)}</strong></td><td class=\"num\" data-label=\"Study says\">{E(b)}</td>"
        f"<td class=\"num\" data-label=\"At the study's baseline\">{E(c)}</td><td class=\"num\" data-label=\"At tip\">{E(d)}</td>"
        f'<td><span class="tag t-{v}">{v}</span></td></tr>'
        for a, b, c, d, v in rows
    )
    return (
        '<div class="tw"><table class="fig"><thead><tr><th>Figure</th><th class="num">Study says</th>'
        '<th class="num">At the study\'s baseline</th><th class="num">At tip</th><th>Verdict</th></tr></thead>'
        f"<tbody>{body}</tbody></table></div>"
        '<p class="note"><span class="tag t-correct">correct</span> right at its baseline and now · '
        '<span class="tag t-drift">drift</span> right at its baseline, changed since · '
        '<span class="tag t-error">error</span> wrong at its own baseline. The report\'s section 2 lists every other '
        "figure checked (documents, memories, plans, dependency depth, lock collisions, tests), all correct at baseline.</p>"
    )


STEPS = [
    ("A", "One repository, explicit contracts", [
        ("phase-bnd-06", "Governed concern and interface contract"),
        ("phase-bnd-07", "Registry concern field, rejected when missing or unknown"),
        ("phase-bnd-08", "Defined entry-point values; every prompt classified"),
        ("phase-bnd-14", "Independent check and the prompt operating index"),
        ("phase-bnd-09", "Retrieval measured against a fixed question set"),
    ]),
    ("B", "Prepare selective extraction", [
        ("phase-bnd-10", "Plugin, workbench and governance engine against the five preconditions"),
        ("phase-bnd-11", "Extraction discovery for the named candidate; no code moved"),
    ]),
    ("C", "Split now", [
        ("phase-bnd-12", "Migration architecture plan"),
        ("phase-bnd-13", "Cross-repository governance design"),
    ]),
]


def steps() -> str:
    cols = []
    for letter, name, phases in STEPS:
        lis = "".join(f"<li><code>{p}</code> {E(t)}</li>" for p, t in phases)
        cols.append(f'<div class="opt"><h3>Option {letter}: {E(name)}</h3><ul>{lis}</ul></div>')
    return (
        '<div class="grid steps">' + "".join(cols) + "</div>"
        '<p class="note">All nine are <code>deferred</code> until the owner chooses at ARCH-012\'s decision gate; '
        "<code>--ready</code> offers none of them and none is in <code>next_up</code>.</p>"
    )


def page(g: dict) -> str:
    sections = [
        ("Concern map", "Each registered system in the concern the study's inventory assigned it. 43 systems; the "
         "idea-realization core holds one, and it is planned.", concern_map(g)),
        ("Crossings", "What crosses between concerns, from the study's boundary map, with the one read it omits.",
         crossings(g)),
        ("Registry maturity", "Registry status per concern at tip. Nine of the 21 planned entries have built code.",
         maturity(g)),
        ("Prompt entry points", "Where each governed prompt is started from. The study's split does not reproduce at "
         "its own baseline.", prompts(g)),
        ("Backlog and claim load", "Phase states and active claims, at the study's revision and at tip.",
         backlog_view(g)),
        ("Options A, B and C", "What each option commits to, the study's recommendation and the validation's "
         "re-assessment. This page does not choose.", options()),
        ("Figures check", "The study's headline figures re-derived at its own baseline and at tip.", figures(g)),
        ("Next steps", "Deferred backlog phases registered for each option.", steps()),
    ]
    body = "".join(
        f'<section aria-labelledby="s{i}"><h2 id="s{i}">{i}. {E(t)}</h2><p class="cap">{E(c)}</p>{h}</section>'
        for i, (t, c, h) in enumerate(sections, 1)
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>System Boundary Overview</title>"
        '<meta name="description" content="The system boundary study at a glance, with the 2026-09-28 validation.">'
        f"<style>{CSS}</style></head><body><main>"
        '<header class="top"><h1>System boundary at a glance</h1>'
        f'<p class="meta">Figures from <code>origin/dev</code> at <code>{TIP}</code> and the study\'s baselines · {DATE}</p>'
        '<p class="note">Validation of the system boundary study (ARCH-012, REQ-033, PLAN-050). Ran unclaimed: '
        "owner-directed work with no backlog phase; no peer holds a lock against it. The owner chooses A, B or C.</p>"
        "</header>"
        f"{body}"
        "<footer><p><strong>Sources.</strong> <code>docs/00-working/boundary-study/validation-report.md</code> (figures, "
        "per-system concern table, per-prompt classification, re-assessment) and "
        "<code>docs/08-governance/reviews/2026-09-28-plan-050.json</code> (review record). Study evidence: "
        "<code>docs/00-working/boundary-study/</code> and <code>ARCH-012</code>.</p>"
        "<p>Generated by <code>docs/00-working/boundary-study/build_boundary_overview.py</code>.</p></footer>"
        "</main></body></html>\n"
    )


def main() -> None:
    g = gather()
    if "--markdown" in sys.argv:
        print(markdown(g))
        return
    OUT.write_text(page(g), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
