---
schema_version: 1
id: doc-session-phase-wb-10-runbook-refresh
code: SESS-2026-09-12-02
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
Governance OK: 18 systems, 170 documents, 18 memories, 122 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged (run in the
`agent/phase-wb-10` worktree with the primary checkout's gitignored `_private/` temporarily
symlinked in, because an ignored directory never reaches a worktree and without it the identifier
half of the check silently skips):

```
check_no_private_content: OK (509 tracked files, 31 identifiers checked)
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

- `status: complete` (set by the owner-invoked /session-close, 2026-09-12), `agent: agent-fable`
  (claim committed on `dev` at `bf39c60`).
- `session: doc-session-phase-wb-10-runbook-refresh`.
- `completion_evidence: docs/00-working/demo-runbook.md, docs/00-working/demo-windows-setup.md`
  (both updated on branch `agent/phase-wb-10`; the deliverables commit is `93bb924` after the
  rebase onto the peer session's close commit).
- Removed from `next_up`.

## Unresolved

- The Windows-machine confirmations the refreshed documents describe (PowerShell fresh-store
  default, two-shell round-trip, viewer fill) remain the blocked rehearsal phase
  (`phase-wb-07`)'s owner checks, unchanged by this session; that phase's `resume_when` is now
  satisfied on the phase-wb-10 side.

## Review

Independent sub-agent review (fresh non-fork agent, given the phase boundary, the range
`dev...agent/phase-wb-10`, and the session record; it ran the verification commands itself).
Findings pasted verbatim:

> **Acceptance condition 1 — post-fix UI only, no retired per-slot selects or bash-first
> default: HOLDS.** Full diff `dev...agent/phase-wb-10` touches only 5 files, all under `docs/`
> (the two deliverables, the session record, `catalog.md`, `backlog.yaml`). Nothing under
> `src/`, `ts/`, `tools/`, `test/`, `schemas/`, `sql/`, no OPS document — "documentation only"
> holds. Timeboxes are untouched by the diff. My own grep of both documents for retired
> phrasing (`panel picker`, `bash-first`, `defaults correctly`, `per-slot`, `select "Terminal
> (bash)"`, `depending on configuration`, `Opens a surface`, `default to CMD`, plus broader
> patterns) found no hit describing the current UI. Surviving hits are: (a) negations in new
> text ("no per-slot visible-panel selects", 3 places), (b) the unrelated notes-file picker,
> and (c) the dated 2026-09-11 rehearsal-finding records — finding 4 and finding 6, both of
> which carry the claimed annotations, verbatim present. Spot-checked the new descriptions
> against code, read-only: `useWorkbenchLayouts.ts` (platform-conditional fresh-store default
> via `/api/v1/workbench/platform`, PowerShell when `windows`, bash fallback when route
> absent), `LayoutConfigDialog.tsx` (layout radio group, "Panel assignment" legend, per-panel
> eligible-slot selection, `displacedPanelId` in-place confirm with Confirm/Cancel),
> `vite.config.ts` (`/workbench-file/` route registered only when
> `env.D_SYSTEM_DEMO_TERMINAL === '1'`). The documents' claims match the code.
>
> **Acceptance condition 2 — both launch sections state the frontend flag requirement:
> HOLDS.** Runbook "Launch Command Reference" and the Windows checklist "Environment
> Variables" section (plus the smoke-check launch step) each state the flag must be set on
> both processes and the silently-blank-viewer consequence. Both verified in the diff and the
> on-disk files.
>
> **Verification reruns (my own):** `uv run python -m src.governance` → `Governance OK: 18
> systems, 170 documents, 18 memories, 122 backlog phases` — pass.
> `uv run python tools/check_no_private_content.py` with `_private` symlinked in →
> `check_no_private_content: OK (509 tracked files, 31 identifiers checked)` — both halves
> ran; pass. Retired-phrasing grep — clean, as above.
>
> **Discrepancies between the session record and what I observed:** (1) Stale commit hash
> `54e8390` in the session record and the backlog `result` — the branch was rebased and the
> deliverables commit is now `93bb924` (identical message); the content claim is true, the
> cited hash points off-branch. (2) The committed session record's verification outputs were
> stale ("169 documents", "507 tracked files" vs. reruns giving 170 and 509), with the
> correction sitting uncommitted in the worktree — it needs to be committed before session
> close. (3) `origin/agent/phase-wb-10` still held the pre-rebase history; the deliverable
> documents are byte-identical between the two tips, but the rebased branch needed pushing.
> None of these affect the two acceptance conditions themselves — both HOLD on the branch as
> committed.

All three discrepancies were resolved in the close commit: hashes corrected to `93bb924`, the
verification-count correction committed, and the rebased branch pushed.

## Decisions

- The owner directed integration and close from a mobile session (2026-09-12): the agent was
  told to perform the merge commands itself rather than the owner running them, and later to
  proceed with /session-close once the peer session had closed. Integration of this
  documentation-only phase was explicitly outside PROMPT-023 delta 4's pre-approval, so both
  steps waited on these explicit owner instructions.
- Historical rehearsal findings 4 (CMD default) and 6 (clipped terminal, idea 000104) were
  annotated as superseded/resolved by phase-wb-09/phase-wb-08 rather than rewritten — dated
  finding records are history, and rewriting them would falsify what the 2026-09-11 passes
  observed.
- Every control name and dialog text in the refreshed documents was verified against the
  integrated wb-08/09 frontend code before writing, per the owner's standing verify-in-code
  expectation, rather than taken from the phase description.
- The mid-close session-code collision (two sessions allocating `SESS-2026-09-12-01`) was
  resolved by this branch renumbering to `SESS-2026-09-12-02`, per AGENTS.md's
  the-agent-integrating-second-renumbers rule; the peer's idea-triage sweep kept `-01`.

## Corrections

- The first integration attempt was halted mid-procedure: AGENTS.md's hand-off step 6 found
  the primary checkout dirty with the peer session's then-uncommitted work. The merge waited
  until the peer's close commit (`e4b5cab`) landed; that pause is the rule working, but the
  session record briefly carried a "pushed" claim that the subsequent rebase made stale — the
  review caught it, and the close commit fixed hash, counts and push state.
- Three PTY terminal tests failed twice during the gate runs. Root cause was environmental,
  not the repository: every spawned bash triggers pyenv's rehash hook, which stalls 60 seconds
  on a stale lock file (`~/.pyenv/shims/.pyenv-shim`) that concurrent test runs recreate.
  Cleared twice; the full suite then passed. This machine issue will likely recur.
- The post-rebase suite also surfaced one genuinely failing test on committed `dev`
  (`test_ideas_queue_route_orders_by_status_precedence_then_age`, whose fixture assumed an
  open idea while the peer's sweep had triaged everything). It was the peer session's to fix
  and their close commit fixed it; nothing was changed for it on this branch.

## Left undone

- Nothing within this phase's boundary. The blocked rehearsal phase (`phase-wb-07`) remains
  the owner's: its `resume_when` — phase-wb-10 complete and the owner at the Windows
  presentation machine — is now half-satisfied, and its owner-machine checks (R06 smoke
  check, W12/W17 shell checks, W15 fill confirmations, both R09 timed dry-runs) run against
  the documents this session refreshed.
- The recurring pyenv stale-lock slowdown on this machine is noted in Corrections; it is an
  environment matter outside the repository and was deliberately not turned into a repo
  change or idea without the owner's direction.
