---
schema_version: 1
id: doc-workbench
code: PLAN-022
title: Workbench — the stage becomes the chartered management UI
kind: plan
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench-requirements, doc-workbench-terminal-decision, doc-workbench-api-decision, doc-workbench-layout-decision]
---

# Workbench — the stage becomes the chartered management UI

## Goal and inputs

Turn the integrated demo stage into the chartered management UI the owner ratified on 2026-09-10
([PROMPT-020](../02-prompts/PROMPT-020-workbench-pre-plan-package.md)): a configurable workbench
of panels, layouts and injection controls, presented at the live demo the week of 2026-09-15.
The contract is the workbench requirements ([REQ-007](../06-requirements/REQ-007-workbench.md),
rows W01–W14); the boundaries are the three workbench decisions — terminal capability
([ADR-014](../04-decisions/ADR-014-workbench-terminal-capability.md)), API surface
([ADR-015](../04-decisions/ADR-015-workbench-api-surface.md)) and layout persistence
([ADR-016](../04-decisions/ADR-016-workbench-layout-persistence.md)). The demo track
(`phase-demo-01`..`07`, [PLAN-021](PLAN-021-live-demo.md)) is the foundation, not a parallel
track; `phase-demo-05`'s reset tool, OPS document and Windows checklist survive unchanged and
are updated only by the rehearsal-refresh phase.

## Build structure

Seven phases in `docs/09-backlog/backlog.yaml`, tracked as `phase-wb-*`, each sized to one
build-session dispatch with the two-fix-cycle cap and the completion gate (the `GOV-003`
demo-track decision, extended to this track in that document):

- **`phase-wb-01` — workbench backend API.** The gated route family per ADR-015: injection-source
  enumeration with the curated-overrides file, repo-bounded directory listing and recursive file
  search, the `fold()`-only idea route, the backlog route with the `--ready`-shaped queue
  ordering, the reveal-in-explorer action, and ADR-014's session registry with the shell
  allowlist. REQ-007 W14 plus the backend halves of W04, W09–W12.
- **`phase-wb-02` — layout engine and notes strip.** The slot model and configuration surface,
  the two shipped layout JSON files under `_data/workbench/layouts/`, slot-header dropdowns for
  multi-panel slots, localStorage selections per ADR-016; the notes strip replacing the
  talking-points panel (display-only, tooltip far left, one dropdown including the notes-file
  picker, fed by `phase-wb-01`'s listing route per ADR-015), retiring `TalkingPointsRegion`'s
  stale placeholder comment with it. W01, W05, W06.
- **`phase-wb-03` — terminal panel rework and shells.** The `(...)` ellipsis menu (collapse and
  drop move in; standalone controls go), drop-in-place info page with deactivated injection
  dropdowns, the Skills/Prompts/Agents dropdowns wired to `phase-wb-01`'s enumeration, and the
  bash/CMD/PowerShell panel options with unavailable-shell degradation. Also sweeps the recorded
  demo-track minors in this region: real `ts/public/demo-commands.json` copy and the websocket
  startup-race console warning. W02, W03, W04, W12 (Linux half).
- **`phase-wb-04` — HTML Viewer panel.** The viewer panel with refresh, the searchable recursive
  `.html`/`.svg` dropdown, the in-app directory dialog over `phase-wb-01`'s listing API, and
  terminal-style tabs with per-tab scope. W07, W08.
- **`phase-wb-05` — File Browser panel.** Context folder, collapsible filtered treeview, the
  five context-menu actions (reveal, open-in-viewer with tab submenu, copy relative, copy
  absolute, inject path), and the documentation-explorer configuration. W09.
- **`phase-wb-06` — Idea and Backlog explorers.** Both panels over `phase-wb-01`'s routes, with
  the standard and priority-queue views and the agreed columns. W10, W11.
- **`phase-wb-07` — rehearsal refresh.** The runbook rewritten to the final workbench UI in the
  rehearsal gate's step shape (`PROMPT-017`), the Windows checklist updated and executed on the
  presentation machine (REQ-006 R06 smoke check, CMD and PowerShell round-trips), and two
  owner-driven timed dry-runs closing REQ-006 R09's deferred conditions. W13. Never descoped.

Dependency order: **strictly sequential**, `phase-wb-01` → `phase-wb-02` → `phase-wb-03` →
`phase-wb-04` → `phase-wb-05` → `phase-wb-06` → `phase-wb-07`, each claimed only after its
predecessor integrates and completes, with the chain encoded as `depends_on` rather than left
to judgment. Three constraints force it (the 2026-09-10 pack audit's findings, accepted by the
owner): `demo-orch-stage`'s single claim id may hold only one active phase, so `phase-wb-01`
and `phase-wb-02` cannot run in parallel under it; the `max_active: 3` budget is already
two-thirds held by peers (`phase-port-01`, `phase-demo-07`), so a second simultaneous workbench
claim is rejected numerically; and `phase-wb-03`..`06` all deliver into `ts/src`, whose path
lock forbids parallel claims. Real data dependencies reinforce it: `phase-wb-02`'s notes-file
picker consumes `phase-wb-01`'s listing route, and `phase-wb-05`'s open-in-viewer submenu needs
`phase-wb-04`'s viewer tabs.

## Descope ladder

Emergencies only — the owner chose all four workstreams (`PROMPT-020` decision 6). Applied in
order when the week runs short; each rung is independent of the ones below it, and `phase-wb-07`
is never descoped. The canonical rung list lives in REQ-007's "Descope ladder" section; in
summary: (1) CMD/PowerShell become message-only entries; (2) queue views drop from the
explorers; (3) the File Browser menu reduces to reveal + open-in-viewer; (4) the HTML Viewer
loses tabs; (5) the Idea/Backlog explorers drop; (6) layout 2 drops; (7) the notes-file picker
drops.

## Execution model

The two-session shape that built the demo, reused: this plan and its pack are the factory
output, and a separate build session runs [PROMPT-022](../02-prompts/PROMPT-022-workbench-build-orchestration.md)
(coordinator) dispatching [PROMPT-021](../02-prompts/PROMPT-021-workbench-delegation-pack.md)
(delegation pack) verbatim — nothing authored mid-build. Conventions carry over from
`PROMPT-018` unchanged: idempotent prompts, worktrees at `../d-system-worktrees/<phase-id>` on
`agent/<phase-id>` from `dev`, ports 8010/5180, commit-before-validate, at most two fix cycles
per item, validators receiving diff + requirement + commands and never a creator's rationale,
truncated agents resumed rather than re-run. The model policy of `PROMPT-012` is binding: haiku
for mechanical gates, sonnet for judgment, opus never pre-assigned and used at most as a single
documented escalation. The agent roster is the demo roster with extended charters — no new
agents; `demo-orch-stage` orchestrates `phase-wb-01/02/03`, `demo-orch-data`
`phase-wb-04/05/06`, `demo-orch-content` `phase-wb-07`. Completion authority per `GOV-003`'s
demo-track decision, extended to `phase-wb-*` in that document: the coordinator marks a phase
complete after its gate (mechanical checks, adversarial review, browser verification where
applicable) and integration onto `dev` remains the owner's approval each time.

## Demo-week operational notes

- `tools/demo_reset.py`, `OPS-013` and the Windows checklist stay valid through the build;
  `phase-wb-07` is the only phase that edits the runbook and checklist, so rehearsal documents
  always describe the final UI (PROMPT-020 decision 7).
- The pre-demo git tag and reset semantics from PLAN-021's operational section stand unchanged.
- Deferred REQ-006 conditions (R06 Windows smoke check, owner-driven R09 timing) close in
  `phase-wb-07`, which is why it cannot be descoped.
- Idea `000087` is narrowed, not closed: ADR-014 adopts its session-registry half; the
  outside-the-page inject/read API remains the idea's open scope.
