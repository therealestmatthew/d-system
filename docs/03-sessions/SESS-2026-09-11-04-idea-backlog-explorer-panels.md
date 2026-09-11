---
schema_version: 1
id: doc-session-idea-backlog-explorer-panels
code: SESS-2026-09-11-04
title: Idea and Backlog explorer panels (phase-wb-06) checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui]
depends_on: [doc-workbench]
---

# Idea and Backlog explorer panels (phase-wb-06) checkpoint

## Phase

`phase-wb-06` — Idea and Backlog explorer panels.

## Verification

- `cd ts && npm run build` (orchestrator run, foreground, in the worktree after W06-G):
  ```
  > d-system-ui@0.0.1 build
  > tsc -b && vite build

  vite v6.4.3 building for production...
  transforming...
  ✓ 55 modules transformed.
  rendering chunks...
  computing gzip size...
  dist/index.html                   0.39 kB │ gzip:   0.26 kB
  dist/assets/index-DIS5rbP6.css   21.50 kB │ gzip:   4.75 kB
  dist/assets/index-DmTDyCMR.js   534.51 kB │ gzip: 146.70 kB

  (!) Some chunks are larger than 500 kB after minification. ...
  ✓ built in 1.11s
  ```
- `uv run python -m src.governance` (orchestrator run):
  ```
  Governance OK: 18 systems, 162 documents, 16 memories, 119 backlog phases
  ```
- `uv run python tools/check_no_private_content.py` with the changes staged (orchestrator run):
  ```
  note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
  check_no_private_content: OK (496 tracked files, 0 identifiers checked)
  ```
- `uv run pytest` (full suite, run by W06-G/demo-validator-check):
  ```
  552 passed, 3 failed
  ```
  The 3 failures are all in `test/test_demo_terminal.py`
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`), each showing
  `pyenv: cannot rehash: couldn't acquire lock ... .pyenv-shim` — the recorded host-wide
  pyenv-rehash issue (ideas 000097/000099), not a phase failure. This phase's diff does not touch
  `test/` or `src/demo`.
- W06-C1 (demo-creator-web, Idea Explorer): built `ts/src/stage/IdeaExplorerRegion.tsx` over
  phase-wb-01's idea route (`GET /api/v1/workbench/ideas` and `/ideas/queue`) only, registered in
  layout-1's explorer slot; `npm run build` clean first cycle (commit `79eb1a1`).
- W06-V1 (demo-validator-code): clean PASS, no findings — data comes only from the idea route,
  six columns render, sort/filter operate on already-fetched rows, the queue view re-fetches the
  route's own queue-ordered variant rather than re-ranking client-side.
- W06-C2 (demo-creator-web, Backlog Explorer): factored the shared table/sort/filter/queue-toggle
  logic out of the Idea Explorer into `ts/src/stage/explorer/ExplorerRegion.tsx`, a generic
  component parameterized by columns and data source; `IdeaExplorerRegion` became a thin wrapper
  over it; `ts/src/stage/BacklogExplorerRegion.tsx` is the second wrapper, over phase-wb-01's
  backlog route, registered in the explorer slot alongside the other two; `npm run build` clean
  first cycle (commit `13a6379`).
- W06-V2 (demo-validator-code): clean PASS, no findings — only `ExplorerRegion.tsx` renders a
  table (no duplicated table code), six columns render for the backlog panel, the queue view uses
  the route's own ordering, and layout-1's explorer slot now lists all three explorers with File
  Browser default-visible.
- W06-G (demo-validator-check, phase gate): PASS on every item — governance clean; private-content
  clean staged; both explorer panels registered in the slot; `npm run build` clean; full pytest
  552 passed/3 failed (the same environmental PTY set, ideas 000097/000099); no direct
  `ideas.jsonl` reference in `ts/src` (the one grep hit is a comment stating the opposite); diff
  against `dev` confined to `ts/`.

## Acceptance

- Idea rows match an independent `fold()` run and the queue view ranks by status precedence then
  age (REQ-007 W10) — **Met** for the code path: W06-V1 confirmed the panel reads only the
  phase-wb-01 idea route (itself `fold()`-backed) and the queue view uses the route's own
  queue-ordered variant, never a client-side re-rank. An independent `fold()` cross-check against
  live rendered data is W06-W's job (coordinator-dispatched, not yet run by this orchestrator).
- Backlog rows match `backlog.yaml` and the queue view's top rows equal `next_up` in order
  followed by ready phases by priority, cross-checked against the `--ready` report (REQ-007 W11)
  — **Met** for the code path: W06-V2 confirmed the backlog route's queue variant (built from
  `queue_order()`/`readiness()`) is what the panel renders unmodified. Live cross-check against
  `--ready` output is W06-W's job.
- Layout-1's explorer slot lists all three explorers in its header dropdown with File Browser
  visible by default (REQ-007 W06) — **Met**: `_data/workbench/layouts/layout-1.json` admits
  `file-browser`, `idea-explorer`, `backlog-explorer` in that order with `default_panel: null`;
  `Slot.tsx` falls back to the first implemented admit (File Browser) when none is explicitly
  selected; both new panels are now registered (`Component` no longer `null`) confirmed by W06-G
  item 3.

## Backlog

- `status: active`, `agent: agent-demo-data`.
- `next_action`: W06-C1/V1 and W06-C2/V2 have both passed clean on their first cycle; W06-G (phase
  gate) has passed every item. Remaining against this orchestrator's charter: none — the pack
  assigns W06-A (adversarial review) and W06-W (Playwright browser verification) to the
  coordinator, not this orchestrator. Outstanding before the phase can close: the coordinator's
  W06-A/W06-W dispatch, then the owner's integration decision and `/session-close`.
- `completion_evidence`: not recorded on `dev` yet — the files exist only on the unmerged
  `agent/phase-wb-06` worktree branch: `ts/src/stage/IdeaExplorerRegion.tsx`,
  `ts/src/stage/BacklogExplorerRegion.tsx`, `ts/src/stage/explorer/ExplorerRegion.tsx`,
  `ts/src/workbench/panelRegistry.tsx`, `ts/src/workbench/Slot.tsx`, `ts/src/stage/StagePage.css`;
  citing them as `completion_evidence` on `dev` trips governance's evidence-exists check, so they
  are named here instead.
- `result`: 'In progress. W06-C1 (Idea Explorer) passed first-cycle: build clean, W06-V1 clean
    PASS with no findings — idea data comes only from the phase-wb-01 idea route, six columns
    render, sort/filter work on route data, queue view uses the route's own ordering. W06-C2
    (Backlog Explorer) passed first-cycle, factoring the shared table/sort/filter/queue-toggle
    surface out of the Idea Explorer into ts/src/stage/explorer/ExplorerRegion.tsx so both panels
    are thin wrappers over one generic component — build clean, W06-V2 clean PASS with no
    findings (no duplicated table code, six columns render, queue view uses route ordering, all
    three explorers listed in the slot with File Browser default-visible). W06-G
    (demo-validator-check) passed every item: governance OK, private-content OK staged,
    deliverable confirmed, build clean, full pytest 552 passed/3 failed (environmental, ideas
    000097/000099), no direct ideas.jsonl reference, diff confined to ts/. This orchestrator's own
    verification commands (npm run build, governance, check_no_private_content) are pasted above,
    all clean. No fix cycles were needed on either work item. W06-A and W06-W are the
    coordinator''s dispatches, not this orchestrator''s, and have not yet been run.'

## Unresolved

None blocking this orchestrator's charter. Both W06 work items and the phase gate have passed
clean on their first cycle, with zero fix cycles used out of the two-cycle allowance. What remains
is the coordinator's W06-A (adversarial review) and W06-W (Playwright browser verification)
dispatch, then the owner's integration decision and `/session-close` — none of which this
orchestrator performs.
