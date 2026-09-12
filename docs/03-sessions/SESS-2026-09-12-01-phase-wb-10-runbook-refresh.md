---
schema_version: 1
id: doc-session-phase-wb-10-runbook-refresh
code: SESS-2026-09-12-01
title: Runbook and checklist refresh for the post-fix workbench UI (phase-wb-10)
kind: session
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-demo-stage]
depends_on: [doc-workbench]
---

# Runbook and checklist refresh for the post-fix workbench UI (phase-wb-10)

## Phase

`phase-wb-10` — Runbook and checklist refresh for the post-fix workbench UI.

## Verification

`uv run python -m src.governance`:

```
Governance OK: 18 systems, 169 documents, 18 memories, 122 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged (run in the
`agent/phase-wb-10` worktree with the primary checkout's gitignored `_private/` temporarily
symlinked in, because an ignored directory never reaches a worktree and without it the identifier
half of the check silently skips):

```
check_no_private_content: OK (507 tracked files, 31 identifiers checked)
```

Grep of both documents for retired-dialog and bash-default phrasing (`panel picker`, `bash-first`,
`defaults correctly`, `per-slot`, `select "Terminal (bash)"`, `depending on configuration`,
`Opens a surface`): no hit describes the current UI. Remaining hits are the dated 2026-09-11
rehearsal-finding records (now annotated as superseded/resolved by phase-wb-08/09) and negations
in the new text ("no per-slot visible-panel selects").

## Acceptance

- Both documents describe only the post-fix UI; no reference to the retired per-slot
  configuration selects or a bash-first Windows default remains: **Met** — the grep above finds
  no current-UI reference; every instruction now names the assignment-only "Configure layout"
  dialog, switcher-only header dropdowns, and the platform-conditional fresh-store default
  (PowerShell on Windows, bash elsewhere), each verified against the integrated wb-09 code
  (`ts/src/workbench/LayoutConfigDialog.tsx`, `Slot.tsx`, `useWorkbenchLayouts.ts`,
  `_data/workbench/layouts/*.json`) rather than taken from the phase description.
- Both launch sections state the frontend flag requirement: **Met** — the runbook's Launch
  Command Reference and the checklist's Environment Variables section (plus the smoke-check
  launch step) state that `D_SYSTEM_DEMO_TERMINAL=1` must be set on the frontend process as well
  as the backend, or the `/workbench-file/*` route is absent and the HTML Viewer goes silently
  blank at HTTP 200 (owner-confirmed on Windows 2026-09-11; mechanism verified in
  `ts/vite.config.ts`).

## Backlog

- `status: active`, `agent: agent-fable` (claim committed on `dev` at `bf39c60`).
- `session: doc-session-phase-wb-10-runbook-refresh`.
- `completion_evidence: docs/00-working/demo-runbook.md, docs/00-working/demo-windows-setup.md`
  (both updated on branch `agent/phase-wb-10`, commit `54e8390`, pushed to `origin`).
- `next_action`: All acceptance conditions verified met on the branch; awaiting the owner's
  integration decision (phase-wb-10 is outside PROMPT-023 delta 4's pre-approval) and the
  owner-invoked /session-close.

## Unresolved

- Integration of `agent/phase-wb-10` into `dev` is the owner's call — this phase is
  documentation-only and explicitly outside the fixes pack's pre-approved integration.
- The Windows-machine confirmations the refreshed documents describe (PowerShell fresh-store
  default, two-shell round-trip, viewer fill) remain the blocked rehearsal phase
  (`phase-wb-07`)'s owner checks, unchanged by this session.
