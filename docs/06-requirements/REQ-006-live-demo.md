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
systems: [sys-demo-stage, sys-demo-overview, sys-api, sys-ui]
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
tools, the overview generation skill, and the timing constraint on the live segment. It does not
cover deployment (the stage runs only on the presentation machine), authentication, or any use of the
terminal capability outside the demo.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | A single stage page served by the existing FastAPI + Vite stack contains (a) an embedded terminal, (b) a talking-points panel that cycles owner-authored content loaded from a data file, and (c) an embedded panel showing the generated D-System overview page. | Load the page in a browser against the running dev stack and confirm all three elements are present and live; confirm the talking-points content changes when its data file changes, with no rebuild of page code. |
| R02 | The stage page fits the viewport at any common window size with zero page scrolling; elements resize dynamically and never overlap; content that does not fit is revealed in place via tabs, expanders or buttons. | Resize the browser across common sizes (at minimum 1280×720, 1366×768, 1920×1080, and a projector-safe 1024×768) and confirm no page scrollbar appears and no elements overlap; confirm hidden content is reachable through its in-place control at every size. |
| R03 | Hover-triggered popups collapse when the pointer leaves them; click-triggered popups are dismissible. | Trigger each popup on the stage page; move the pointer away from hover popups and confirm they collapse; open each click popup and confirm a visible dismiss action closes it. |
| R04 | The embedded terminal is xterm.js connected over a websocket to a real shell through a PTY adapter: POSIX `pty` + bash on Linux/macOS, ConPTY via `pywinpty` + cmd or PowerShell on Windows. The platform is auto-detected, a config override selects the shell, and `pywinpty` is a Windows-only optional dependency. | Type a command in the embedded terminal on Linux and on Windows and confirm real shell output; set the shell override and confirm the configured shell starts; confirm a Linux install succeeds without `pywinpty`. |
| R05 | The terminal websocket route mounts only when `D_SYSTEM_DEMO_TERMINAL=1` and binds to 127.0.0.1 only. | Start the server without the flag and confirm the route returns 404/absent; start it with the flag and confirm the route exists on 127.0.0.1 and is not reachable on a non-loopback interface. |
| R06 | The terminal works end to end on the actual presentation machine (Windows). | Run the documented smoke check on the presentation machine before the demo: start the stage with the flag set, open the page, run a command in the embedded terminal, and record the result in the demo runbook. |
| R07 | Deterministic scripts under `tools/` read the idea log via `fold()` (`src/db/ideas.py`), the backlog (`docs/09-backlog/backlog.yaml`), and `docs/08-governance/systems.yaml`, and emit chart-ready JSON plus consolidated inventories: idea metrics per idea `000071`, a concepts/terminology inventory, and a systems inventory. Same inputs produce same outputs; the scripts make no model calls. | Run each script twice against an unchanged repository and diff the outputs for byte equality; cross-check a sample of reported numbers with an independent read of the same sources; inspect the scripts for network or model-API calls. |
| R08 | A skill at `.claude/skills/d-system-overview/SKILL.md` orchestrates the overview scripts and renders `templates/html/` templates into a generated overview page under `_public/`. The skill calls the deterministic scripts and does not recompute their outputs. | Invoke the skill and confirm the page under `_public/` exists and embeds the scripts' outputs; compare a figure on the page with the corresponding script output and confirm they are identical; inspect the skill definition for any recomputation of script-owned numbers. |
| R09 | The live segment — ideation → triage → plan → build → test — completes in 15 minutes with a per-step timebox for each step. | Two timed dry-runs, recorded in the demo runbook with per-step times; both complete within 15 minutes with every step inside its timebox. |
