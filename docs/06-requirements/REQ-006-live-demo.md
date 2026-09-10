---
schema_version: 1
id: doc-live-demo-requirements
code: REQ-006
title: Live demo requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview, sys-api, sys-ui, sys-brain]
depends_on: [doc-prompt-demo-agent-factory]
---

# Live demo requirements

## Observed problem and scope

The owner is presenting a live training session on skills and agents on 2026-09-10 (idea `000070`)
and needs a presentation stage built on this repository's real stack: one page that holds a working
terminal, the owner's talking points, and a generated overview of the D-System itself. The overview
must come from deterministic tooling over real repository data (metrics per idea `000071`), not from
slides or a model call at render time.

This requirement covers the stage page, the embedded terminal capability, the deterministic overview
tools, the overview generation skill, the timing constraint on the live segment, and a
skills-and-agents glossary and diagram library the owner presents from during the training content
(idea `000070`). It does not cover deployment (the stage runs only on the presentation machine),
authentication, or any use of the terminal capability outside the demo.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | A single stage page served by the existing FastAPI + Vite stack contains (a) an embedded terminal, (b) a talking-points panel that cycles owner-authored content loaded from a data file, and (c) an embedded panel showing the generated D-System overview page. | Load the page in a browser against the running dev stack and confirm all three elements are present and live; confirm the talking-points content changes when its data file changes, with no rebuild of page code. |
| R02 | The stage page fits the viewport at any common window size with zero page scrolling; elements resize dynamically and never overlap; content that does not fit is revealed in place via tabs, expanders or buttons. | Playwright-driven browser verification (`demo-validator-web`): resize across 1280×720, 1366×768, 1920×1080 and a projector-safe 1024×768, asserting mechanically (scroll extents and element bounding boxes, not screenshots alone) that no page scrolling exists and no elements overlap, and that hidden content is reachable through its in-place control at every size. |
| R03 | Hover-triggered popups collapse when the pointer leaves them; click-triggered popups are dismissible. | Playwright-driven browser verification (`demo-validator-web`): trigger each popup, move the pointer away from hover popups and assert they collapse; open each click popup and assert its visible dismiss action closes it. |
| R04 | The embedded terminal is xterm.js connected over a websocket to a real shell through a PTY adapter: POSIX `pty` + bash on Linux/macOS, ConPTY via `pywinpty` + cmd or PowerShell on Windows. The platform is auto-detected, a config override selects the shell, and `pywinpty` is a Windows-only optional dependency. | Type a command in the embedded terminal on Linux and on Windows and confirm real shell output; set the shell override and confirm the configured shell starts; confirm a Linux install succeeds without `pywinpty`. |
| R05 | The terminal websocket route mounts only when `D_SYSTEM_DEMO_TERMINAL=1` and binds to 127.0.0.1 only. | Start the server without the flag and confirm the route returns 404/absent; start it with the flag and confirm the route exists on 127.0.0.1 and is not reachable on a non-loopback interface. |
| R06 | The terminal works end to end on the actual presentation machine (Windows). | Run the documented smoke check on the presentation machine before the demo: start the stage with the flag set, open the page, run a command in the embedded terminal, and record the result in the demo runbook. |
| R07 | Deterministic scripts under `tools/` read the idea log via `fold()` (`src/db/ideas.py`), the backlog (`docs/09-backlog/backlog.yaml`), and `docs/08-governance/systems.yaml`, and emit chart-ready JSON plus consolidated inventories: idea metrics per idea `000071`, a concepts/terminology inventory, and a systems inventory. Same inputs produce same outputs; the scripts make no model calls. | Run each script twice against an unchanged repository and diff the outputs for byte equality; cross-check a sample of reported numbers with an independent read of the same sources; inspect the scripts for network or model-API calls. |
| R08 | A skill at `.claude/skills/d-system-overview/SKILL.md` orchestrates the overview scripts and renders `templates/html/` templates into a generated overview page under `_public/`. The skill calls the deterministic scripts and does not recompute their outputs. | Invoke the skill and confirm the page under `_public/` exists and embeds the scripts' outputs; compare a figure on the page with the corresponding script output and confirm they are identical; inspect the skill definition for any recomputation of script-owned numbers. |
| R09 | The live segment — orient → record an idea → triage it → plan beat → overview-skill rebuild → test, the step shape the rehearsal gate (`PROMPT-017`) defines — completes in 15 minutes with a per-step timebox for each step. | Two timed dry-runs, recorded in the demo runbook with per-step times; both complete within 15 minutes with every step inside its timebox. |
| R10 | The terminal region hosts up to four terminal sessions as tabs; each tab is an independent shell over its own websocket, and switching tabs or collapsing the region never terminates a session — scrollback and running processes survive. | Playwright-driven browser verification: start a long-running command in tab 1, switch to tab 2 and back, collapse and re-expand the region, and assert tab 1's scrollback and process are intact; assert a fifth tab cannot be opened. |
| R11 | Collapsing the terminal region and dropping terminal sessions are two separate controls. The drop control (descope rung 4) and closing an individual tab each require an explicit confirmation step before any session terminates. | Playwright-driven browser verification: activate the drop control and each tab close, assert nothing terminates before the confirm action, assert the session genuinely terminates after it, and assert collapse alone never terminates anything. |
| R12 | A command list loaded from a data file (`ts/public/demo-commands.json`; no command text hardcoded in components) is revealed in place within the terminal region; selecting an entry injects its command into the active terminal's input line without executing it, and entries marked `run: true` execute immediately. When the terminal route is absent the panel degrades alongside the existing absent-terminal message and nothing errors. | Playwright-driven browser verification: inject an entry and assert the text appears on the active tab's input line un-executed, then that Enter executes it; assert a `run: true` entry executes on selection; edit the data file and confirm the list changes with no rebuild of page code; load the stage with the flag unset and assert no errors. |
| R13 | A skills-and-agents glossary — `brain/concepts` memory entries covering LLM, Agent, Sub-agent, Tool, MCP, Context, Command and Skill, plus the owner-approved additional terms, each with a one-line entry for the advanced topics named out of scope for depth (hooks, agent permissions, observability, Agent SDK) — and a library of standalone SVG diagrams illustrating LLM-vs-agent, skill architecture, the agentic loop, sub-agents and context isolation, MCP architecture, and the command/skill/tool distinction, indexed by an `index.html` contact sheet, exist independently of the stage page and are viewable in a browser without the dev server running. | Regenerate both the unfiltered glossary (`tools/generate_glossary.py`) and the filtered one (`tools/generate_glossary.py --tag demo-glossary --out docs/00-working/demo-glossary.md`) and confirm every required term is present in the filtered output; open the index and each SVG directly from the filesystem in a browser and visually confirm each is legible at a projector-safe size and matches the corresponding glossary entry's terminology. |
