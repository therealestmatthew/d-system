---
schema_version: 1
id: doc-prompt-demo-rehearsal-gate
code: PROMPT-017
title: Demo pack — rehearsal gate and demo-day readiness
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
depends_on:
- doc-prompt-demo-build-orchestration
---

# Demo pack — rehearsal gate and demo-day readiness

Child of the build orchestration prompt ([PROMPT-014](PROMPT-014-demo-build-orchestration.md)),
read at its Step 3. The build is done when this gate is green — not before.

## Fresh-eyes rehearsal

Dispatched to an agent that built nothing in this session, following
the runbook (a `phase-demo-05` deliverable) **literally** — a gap in the runbook is a finding, not
something the rehearser fills from memory. The rehearsal verifies, on the development machine:

1. Backend starts on 8010 with `D_SYSTEM_DEMO_TERMINAL=1`; frontend builds and serves on 5180.
2. The stage page loads; at 1280×720, 1920×1080 and a half-width window there is **zero page
   scrolling, no overlapping elements**, and every reveal control (tabs, expanders, popups)
   opens and collapses as required.
3. The embedded terminal connects, runs a real shell, and echoes interactive input.
4. The talking-points panel cycles the owner's content from its data file.
5. `tools/demo_reset.py` parks the pre-built overview skill and seeds the fallback audience idea;
   the live-rebuild path then runs end to end: idea recorded via the sanctioned writer, triaged,
   skill rebuilt from the pre-built deterministic tools, skill invoked, overview page generated
   into `_public/` and rendered in the embedded panel. Then reset restores the pre-built state.
6. The deterministic tools are run twice and produce identical output (determinism check).
7. The side-by-side fallback (page without embedded terminal + external terminal) is exercised
   once.

## Timed dry-runs

Two stopwatch-timed passes of the live segment (owner driving, coordinator observing):
`/orient` → `/idea` → `/idea-triage` → plan beat → skill rebuild → test. Each step has a timebox
from the runbook; a pass exceeding 15 minutes total triggers tightening (pre-agreed: shorten the
plan beat first, then pre-stage the `/orient` output). Every step's fallback is the same action:
un-park the pre-built skill and continue the narrative.

## Windows-machine gate (owner performs, coordinator guides)

The presentation machine is Windows; development is Linux, so this cannot be verified remotely:

1. Repo cloned; `uv sync --extra dev` and `npm install` complete; `pywinpty` installed.
2. Terminal adapter smoke check: websocket route serves a ConPTY-backed cmd or PowerShell (per
   the configured shell), xterm.js renders it, interactive input works.
3. The full rehearsal checklist above passes once on that machine.
4. Screen hygiene: demo shell launches with a cleaned environment and fresh history; nothing under
   `_private/` is opened at any point; only the owner types during the live segment.
5. A pre-demo git tag is created and `tools/demo_reset.py` is verified against it.

## Reporting

The gate's report lists every item above with pass/fail and real output for failures. Any red item
returns the relevant phase to work with an exact `next_action`; a green gate is reported to the
owner as demo-ready, with the runbook path and the start command sequence stated in full.
