---
schema_version: 1
id: doc-live-demo
code: PLAN-021
title: Live demo stage and overview build
kind: plan
status: draft
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview, sys-api, sys-ui, sys-html]
depends_on: [doc-live-demo-requirements, doc-demo-terminal-decision]
---

# Live demo stage and overview build

## Context and scope

[REQ-006](../06-requirements/REQ-006-live-demo.md) defines the observable contract: a single stage
page (embedded terminal, talking-points rotator, embedded generated overview), deterministic overview
tooling over the idea log, backlog and systems registry, an overview-generation skill, and a
15-minute live segment. The terminal capability's security posture is decided in
[ADR-013](../04-decisions/ADR-013-demo-terminal-capability.md). The build is executed by delegated
agents following the demo prompt pack ([PROMPT-010](../02-prompts/PROMPT-010-demo-agent-factory.md)
through [PROMPT-017](../02-prompts/PROMPT-017-demo-rehearsal-gate.md)); this plan carries the
structure the backlog phases implement.

## Build structure

Five phases in `docs/09-backlog/backlog.yaml`, tracked as `phase-demo-*`:

- **`phase-demo-01` — stage backend.** Terminal websocket route and PTY adapter
  (`src/api/routes/`, registered in `src/api/__init__.py`), plus any read routes the stage page
  needs. Gated and bound per ADR-013. Depends on nothing.
- **`phase-demo-03` — deterministic overview tools.** The scripts under `tools/` with their `OPS-*`
  documents (generated reference blocks via `tools/generate_tool_docs.py`) and tests. Depends on
  nothing; runs in parallel with `phase-demo-01`.
- **`phase-demo-02` — stage frontend.** xterm.js terminal, talking-points rotator (content loaded
  from a data file, not hardcoded), embedded overview panel, the zero-scroll layout, and the
  fallback layout. Depends on `phase-demo-01`.
- **`phase-demo-04` — overview generation.** The `d-system-overview` skill, `templates/html/` and
  `templates/styles/` template families, and generation into `_public/`. Depends on
  `phase-demo-03`.
- **`phase-demo-05` — demo content and readiness.** Final talking-points copy, the live-segment
  runbook, `tools/demo_reset.py` with its OPS document, the Windows setup checklist, and
  rehearsals. Depends on all four.

## Descope ladder

Applied in order when time runs short; each rung is independent of the ones below it:

1. Overview charts become tables.
2. Talking-points rotator loses transitions.
3. Embedded overview panel becomes an open-in-tab link.
4. Embedded terminal falls back to a side-by-side real terminal.

## Demo-day operational requirements

- **Windows machine setup checklist.** Produced by `phase-demo-05`: repository clone location, `uv`
  and Node versions, `pywinpty` install, `D_SYSTEM_DEMO_TERMINAL=1`, port assignments, browser and
  zoom level, and the R06 smoke check from REQ-006 run and recorded before the session.
- **Pre-demo git tag.** Tag the repository state before the session starts so anything recorded
  live (the idea log is append-only) is diffable against a known baseline afterwards.
- **Demo reset.** `tools/demo_reset.py` returns the demo-visible state to the rehearsed baseline —
  regenerated overview outputs and cleared scratch state — without touching the append-only idea
  log's history or any governed document.
- **Screen hygiene.** Nothing from `_private/` on screen; notifications off; the terminal starts in
  the repository root with a clean scrollback; browser profile free of personal tabs and bookmarks.
