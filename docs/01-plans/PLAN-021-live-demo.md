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

## Execution sequence

The build runs as two sessions, each driven by one pasteable prompt, with everything either
session needs authored before it starts — no prompt is written mid-build:

1. **The agent factory session** ([PROMPT-010](../02-prompts/PROMPT-010-demo-agent-factory.md))
   produced this plan, REQ-006, ADR-013, the five backlog phases, the eight demo agents under
   `.claude/agents/`, and the delegation prompt pack. Its child specifications —
   [PROMPT-011](../02-prompts/PROMPT-011-demo-governance-docs-spec.md) (governance documents),
   [PROMPT-012](../02-prompts/PROMPT-012-demo-agent-roster-spec.md) (agent roster),
   [PROMPT-013](../02-prompts/PROMPT-013-demo-delegation-pack-spec.md) (delegation pack and
   validation gate) — are read lazily, one per step. A validation gate certifies the output
   before anything builds.
2. **The build session** ([PROMPT-014](../02-prompts/PROMPT-014-demo-build-orchestration.md)) is a
   coordinator only: it claims the phases below, dispatches the three orchestrator agents with
   their pre-crafted prompts verbatim, and verifies their reports independently. Its children —
   [PROMPT-015](../02-prompts/PROMPT-015-demo-phase-protocol.md) (phase protocol),
   [PROMPT-016](../02-prompts/PROMPT-016-demo-guardrails.md) (budgets, descope ladder, escalation),
   [PROMPT-017](../02-prompts/PROMPT-017-demo-rehearsal-gate.md) (the rehearsal gate that defines
   done) — are likewise read only when reached. Every delegation prompt is idempotent, so one-shot
   completion and multi-session resume are the same prompt.

The commentary behind these choices: creation and validation are separated (creators never grade
their own work, validators never see the creator's rationale); models are tiered by task shape
(haiku for mechanical gates, sonnet for judgment, opus only as a single documented escalation);
and the coordinator holds no authorship so that everything it executes was reviewable before the
session began.

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
- **Recorded-dry-run fallback.** The second timed dry-run is screen-recorded, and a successful
  recording is a rehearsal-gate deliverable (`PROMPT-017`): the last-resort fallback if the API or
  network fails on stage, narrated live over the video. The runbook names the recording's path on
  the presentation machine.
- **Pre-approved permission allowlist.** The live-demo session runs on an allowlist built from the
  rehearsal transcripts, scoped to the specific commands and paths the live segment uses, so the
  segment runs without permission pauses while the write fences stay in place. Blanket auto-accept
  is never used.

## Vision

The demo is the first realized slice of two standing ambitions rather than a one-off prop. The
overview page is the first working product of the HTML generation framework that
[PLAN-003](PLAN-003-dynamic-html-generation/PLAN-003-overview.md) designs and the `phase-html-*`
track queues: source data rendered through templates into pages, deterministically. The pattern it
demonstrates — deterministic scripts compute, Claude orchestrates them and keeps the page current —
is the division of labor the whole platform is meant to run on: model calls are spent on judgment
and coordination, never on recomputing what a script computes the same way every time.

The demo's own construction is the other half of the vision: the factory pattern (roster, prompt
pack, validation gate, then a coordinator that only spends what was pre-built) is reusable for any
future multi-agent build here, and speaks directly to the agent-engineering idea family
(`000078`–`000082`). After demo day, the intended trajectory is: the overview page regenerates as
repository state changes; the stage page's workflow-triggering grows into the UI that `CLAUDE.md`
already names as the platform's purpose; and what the audience watched — idea to triage to plan to
working software under governance — remains the repository's actual operating loop, not a
performance of it.

## Afterlife

Owner decision, 2026-09-10: everything the demo produces is kept as real work, not reverted. The
idea recorded from the audience stays in the append-only log; the `phase-demo-*` phases are closed
through `/session-close` like any other phase; and the generated overview page becomes a maintained
feature of the repository rather than a prop.
