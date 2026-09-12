---
schema_version: 1
id: doc-prompt-demo-governance-docs-spec
code: PROMPT-011
title: Demo pack — governance documents specification
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
- sys-backlog
depends_on:
- doc-prompt-demo-agent-factory
---

# Demo pack — governance documents specification

Child of the agent factory prompt ([PROMPT-010](PROMPT-010-demo-agent-factory.md)), read at its
Step 1. Specifies every governance document the factory session writes before any agent or prompt is
authored. Everything here is written on `dev` in the primary checkout.

## 1. Requirements document (`--next-code requirement`)

`docs/06-requirements/REQ-NNN-live-demo.md`. Every statement observable, each with a verification
method. It must cover, at minimum:

- **Stage page**: a single page served by the existing FastAPI + Vite stack containing (a) an
  embedded terminal, (b) a talking-points panel that cycles owner-authored content, (c) an embedded
  panel showing the generated D-System overview page. Layout requirements are hard: the page fits
  the viewport at any common window size with **zero page scrolling**, elements resize dynamically
  and never overlap; anything that does not fit is revealed in place via tabs, expanders or buttons;
  hover-triggered popups collapse when the pointer leaves, click-triggered popups are dismissible.
- **Embedded terminal**: xterm.js connected over a websocket to a real shell through a PTY adapter —
  POSIX `pty` + bash on Linux/macOS, ConPTY via `pywinpty` + cmd or PowerShell on Windows —
  platform auto-detected with a config override for shell choice (`pywinpty` is a Windows-only
  optional dependency). The route mounts **only** when `D_SYSTEM_DEMO_TERMINAL=1` and binds to
  127.0.0.1. Verification includes a smoke check on the actual presentation machine (Windows).
- **Deterministic overview tools**: scripts under `tools/` that read the idea log via `fold()`
  (`src/db/ideas.py`), the backlog, and `docs/08-governance/systems.yaml`, and emit chart-ready
  JSON plus consolidated inventories (metrics per idea `000071`; concepts/terminology; systems).
  Deterministic: same inputs, same outputs, no model calls.
- **Overview skill**: `.claude/skills/d-system-overview/SKILL.md` that orchestrates those tools and
  renders `templates/html/` templates into a generated overview page under `_public/`. The skill
  calls the deterministic scripts; it does not recompute their outputs.
- **Live segment**: the ideation→triage→plan→build→test flow completes in 15 minutes with per-step
  timeboxes, verified by two timed dry-runs.

## 2. Plan document (`--next-code plan`)

`docs/01-plans/PLAN-NNN-live-demo.md`, covering the build's structure (the five phases below), the
descope ladder verbatim — (1) overview charts become tables, (2) talking-points rotator loses
transitions, (3) embedded overview panel becomes an open-in-tab link, (4) embedded terminal falls
back to a side-by-side real terminal — and the demo-day operational requirements (Windows machine
setup checklist, pre-demo git tag, demo-reset, screen hygiene, the recorded-dry-run fallback, the
pre-approved permission allowlist). State the afterlife explicitly (owner decision, 2026-09-10):
everything the demo produces is kept as real work — the audience idea stays in the log, the demo
phases are closed via `/session-close`, and the overview page becomes a maintained feature.

## 3. ADR (`--next-code decision`)

The shell-over-websocket capability is a new class for this repository (nothing here shells out
today). Record: localhost-only binding, env-flag gating, demo-only intent, never deployed, the
cross-platform adapter design, and the explicit rejection of exposing it by default.

## 4. Backlog phases

Five phases in `docs/09-backlog/backlog.yaml`, each one session, with scope, acceptance,
verification and deliverables; append the `phase-demo-*` track to `docs/09-backlog/README.md`;
put the runnable demo phases at the front of `next_up` (the owner has accepted that `phase-ses-01`
waits). Declare systems **disjoint from `sys-governance` and `sys-delivery`** (held by the peer's
`phase-port-01`); add new entries to `docs/08-governance/systems.yaml` for the terminal/overview
capability as needed, and verify the Conflicts column is `—` for every demo phase.

- `phase-demo-01` — stage backend: terminal websocket route + PTY adapter + any read routes the
  page needs (`src/api/routes/`, registered in `src/api/__init__.py`). Depends on nothing.
- `phase-demo-03` — deterministic overview tools + their OPS docs (via
  `tools/generate_tool_docs.py`) + tests. Depends on nothing; runs in parallel with 01.
- `phase-demo-02` — stage frontend: xterm.js, talking-points rotator (content loaded from a data
  file, not hardcoded), overview panel, the zero-scroll layout, fallback layout. Depends on 01.
- `phase-demo-04` — overview skill + `templates/html/` + `templates/styles/` + generation into
  `_public/`. Depends on 03.
- `phase-demo-05` — demo content and readiness: final talking-points copy, the live-segment
  runbook, `tools/demo_reset.py` (+ OPS doc), Windows setup checklist, rehearsals. Depends on all.

Phase verification lists include, at minimum: `uv run pytest`, `uv run ruff check src/ test/`,
`uv run mypy src/`, `npm run build` (frontend phases), `uv run python -m src.governance`, and the
staged private-content check.

## 5. Idea log

Through `tools/append_idea.py` only: annotate `000070` (the skills-and-agents demo idea) that this
plan realizes it, link the new plan code when allocated; annotate `000071` that its metrics design
is subsumed into the overview tools. Do not create new ideas for work this plan already covers.
Regenerate `docs/00-working/ideas.md` afterwards.
