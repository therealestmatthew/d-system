---
schema_version: 1
id: doc-session-phase-wb-08-panel-fixes
code: SESS-2026-09-11-07
title: phase-wb-08 panel rendering fixes — checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-demo-stage]
depends_on: [doc-workbench]
---

# phase-wb-08 panel rendering fixes — checkpoint

## Phase

`phase-wb-08` — Panel rendering fixes — terminal fill, HTML Viewer, File Browser scroll.

## Verification

- `cd ts && npm run build` (run in `/code/d-system-worktrees/phase-wb-08`):
  ```
  > d-system-ui@0.0.1 build
  > tsc -b && vite build

  vite v6.4.3 building for production...
  transforming...
  ✓ 55 modules transformed.
  rendering chunks...
  computing gzip size...
  dist/index.html                   0.39 kB │ gzip:   0.26 kB
  dist/assets/index-B1tZ8Cks.css   21.54 kB │ gzip:   4.76 kB
  dist/assets/index-DBfMsaLB.js   534.51 kB │ gzip: 146.70 kB
  ✓ built
  ```
  (500 kB chunk-size warning is pre-existing, not introduced by this change.)
- `uv run python -m src.governance` (run in `/code/d-system-worktrees/phase-wb-08`):
  `Governance OK: 18 systems, 166 documents, 16 memories, 122 backlog phases`
- `uv run python tools/check_no_private_content.py` with changes staged (run in
  `/code/d-system-worktrees/phase-wb-08`): `check_no_private_content: OK (501 tracked files, 0
  identifiers checked)`
- Adversarial review (`demo-adversary`, pack `W08-A`): not dispatched this session — per
  `GOV-003`'s completion-gate decision this is the coordinator's dispatch, not the
  orchestrator's.
- Pre-fix diagnosis (`demo-validator-web`, pack `W08-M`): done by the coordinator (resumed past
  two turn-limit truncations of the orchestrator's own dispatch attempts) — full report
  recorded the height-chain break at `.stage-workbench-slot__body` (missing `display: flex`)
  and distinguished the HTML Viewer's launch-flag gap from a height collapse.
- Playwright browser verification (`demo-validator-web`, pack `W08-W`): not dispatched this
  session — coordinator's dispatch per the same completion-gate decision.
- `uv run pytest` (run in `/code/d-system-worktrees/phase-wb-08`, after merging the worktree
  branch with `dev`'s catalog-regeneration fix): `552 passed, 3 failed` — the three failures
  are the known environmental PTY failures in `test_demo_terminal.py` (ideas `000097`/`000099`),
  unchanged in kind and count from before this phase's work.
- `git diff dev...agent/phase-wb-08 --stat`: `ts/src/stage/StagePage.css | 17 +++++++++++++++++`
  — the diff touches nothing outside `ts/`.

## Acceptance

- Shell panel xterm fill at all four sizes, both layouts, with readable round-trip output (REQ-007
  W15): Not met — the code fix is committed and W08-V1 confirmed it is generic (no hard-coded
  geometry), but live confirmation across all four window sizes is `W08-W`'s job, not yet
  dispatched.
- Zero page scroll and no overlapping regions at all four sizes, both layouts: Not met — same
  reason; not yet live-verified post-fix.
- Layout-switch persistence guard (MARKER round-trip, no new websocket): Not met — not yet
  live-verified.
- HTML Viewer renders a known figure in both layouts with the diagnosis stating the confirmed
  cause (REQ-007 W15, viewer half): Partially — the diagnosis (`W08-M`) confirmed the
  no-flag blank state is the launch-flag gap (runbook scope, `phase-wb-10`), not code, and the
  creator's fix addresses only the layout-2 height-collapse half per that confirmation; live
  re-confirmation that the viewer renders correctly in both layouts is `W08-W`'s job, not yet
  dispatched.
- File Browser internal scroll, last entry reachable, no page scroll (REQ-007 W18): Not met —
  the fix is committed (same shared root cause as the terminal fix) and W08-V1 confirmed no
  hard-coded height was introduced, but live confirmation is `W08-W`'s job, not yet dispatched.
- Windows confirmations: Not applicable here — explicitly an owner check belonging to
  `phase-wb-07`'s checklist, blocked behind `phase-wb-10`.

## Backlog

- `status: active`, `agent: agent-demo-stage` (unchanged from the claim).
- `next_action`: Dispatch the coordinator-owned completion gate (`W08-A` adversarial review,
  `W08-W` Playwright browser verification) against commit `073676b` on `agent/phase-wb-08`
  (merged with `dev` at `84937bb`); the creator fix and its code-review pass (`W08-V1`) and the
  mechanical phase gate (`W08-G`) are both green.
- Evidence: `agent/phase-wb-08` commit `073676b` (the fix), `d34ac7a` on `dev` (unrelated
  catalog-regeneration fix required for the pytest suite to pass), `84937bb` (merge of `dev`
  into the phase branch). W08-V1 and W08-G verdicts and the W08-M diagnosis report are recorded
  above and in this session's conversation transcript; no separate evidence file was created.

## Unresolved

- The completion gate (`W08-A`, `W08-W`) is outstanding, and per `GOV-003` it is the
  coordinator's dispatch, not this orchestrator's — the phase cannot be marked complete until
  that gate is green and the owner approves integration.
- Two W08-M diagnosis dispatches attempted by this orchestrator were both cut off by the
  subagent's turn limit before producing a report; no `SendMessage`-equivalent tool was
  available to this orchestrator to resume a specific truncated agent (only the coordinator
  could resume it). This is a standing tooling gap worth the coordinator's attention if it
  recurs on other phases.
