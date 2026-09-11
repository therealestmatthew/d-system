---
schema_version: 1
id: doc-session-file-browser-panel
code: SESS-2026-09-11-03
title: File Browser panel (phase-wb-05) checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui]
depends_on: [doc-workbench]
---

# File Browser panel (phase-wb-05) checkpoint

## Phase

`phase-wb-05` — File Browser panel.

## Verification

- `cd ts && npm run build`:
  ```
  > d-system-ui@0.0.1 build
  > tsc -b && vite build

  vite v6.4.3 building for production...
  transforming...
  ✓ 52 modules transformed.
  rendering chunks...
  computing gzip size...
  dist/index.html                   0.39 kB │ gzip:   0.27 kB
  dist/assets/index-C1FZ2Xc5.css   20.09 kB │ gzip:   4.58 kB
  dist/assets/index-BNgKZzox.js   528.72 kB │ gzip: 145.09 kB

  (!) Some chunks are larger than 500 kB after minification. ...
  ✓ built in 1.21s
  ```
- `uv run python -m src.governance`:
  ```
  Governance OK: 18 systems, 162 documents, 16 memories, 119 backlog phases
  ```
- `uv run python tools/check_no_private_content.py` with the changes staged:
  ```
  note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
  check_no_private_content: OK (493 tracked files, 0 identifiers checked)
  ```
- `uv run pytest test/test_workbench_api.py -v` (the coordinator's added deliverable, the new
  `/absolute-path` route's own test file):
  ```
  41 passed, 2 warnings in 1.81s
  ```
- `uv run pytest` (full suite, run by W05-G/demo-validator-check):
  ```
  551 passed, 3 failed in 153.88s
  ```
  The 3 failures are all in `test/test_demo_terminal.py`
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`), each showing
  `pyenv: cannot rehash: couldn't acquire lock ... .pyenv-shim` — the recorded host-wide
  pyenv-rehash issue (ideas 000097/000099), not a phase failure. This phase's diff does not touch
  `test/test_demo_terminal.py` or `src/demo`.
- Adversarial review (pack W05-A): not yet dispatched — it is the coordinator's dispatch per the
  pack, not this orchestrator's.
- Playwright browser verification (pack W05-W): not yet dispatched — it is the coordinator's
  dispatch per the pack, not this orchestrator's.

## Acceptance

- The tree matches the filesystem for a known folder; filters hide non-matching files and empty
  folders; the documentation-explorer preset re-scopes the tree (REQ-007 W09) — **Met**. W05-C1
  built this (commit `8c99a32` post-rebase); W05-V1 (demo-validator-code) reviewed the diff
  against `dev...agent/phase-wb-05 -- ts/` and returned a clean PASS with no findings, confirming
  tree content comes only from phase-wb-01's `/search` route, filters structurally omit empty
  folders (never instantiated, not merely hidden), the documentation-explorer is one config
  preset of the same panel (not a second panel type), and the panel is the explorer slot's
  default-visible panel today (the only implemented admit in that slot).
- All five context-menu actions work — open-in-viewer lands in the chosen tab, inject-path
  appears un-executed on the active terminal, both copies place the expected strings, and the
  reveal request reaches the backend action route — **Met**. W05-C2 built reveal,
  open-in-viewer-with-tab-submenu, copy-relative-path and inject-path in its first pass (commit
  `a61a1d4` post-rebase). The fifth action, copy-absolute-path, needed a backend route ADR-015
  already specifies ("served from the backend's knowledge of the repository root") but
  phase-wb-01 never shipped; the coordinator ruled this an implementation-shortfall fix within
  phase-wb-05 (not a scope question) and widened the phase's deliverables on `dev` (commit
  `7b67f80`) to include `src/api/routes/workbench.py` and `test/test_workbench_api.py`. Fix cycle
  1 of 2 closed it: `demo-creator-py` added `GET /api/v1/workbench/absolute-path` under the
  existing gate and validation helper (commit `73c7676`), then `demo-creator-web` wired the menu
  action to it (commit `f186010`). W05-V2 (demo-validator-code) then returned a clean PASS on the
  full five-action diff, with one non-blocking note: a stale doc comment in
  `ts/src/workbench/panelRegistry.tsx:17-18` still describes the context menu as not yet built —
  a documentation-accuracy defect only, not fixed here (no functional finding to trigger a fix
  cycle). W05-G (demo-validator-check) then passed every item.

## Backlog

- `status: active`, `agent: agent-demo-data`.
- `next_action`: W05-C1/V1, W05-C2/V2 (including the coordinator-approved backend fix cycle) and
  W05-G all passed; this orchestrator's own verification commands are pasted above. Remaining
  before this phase can close: the coordinator's own W05-A (adversarial review) and W05-W
  (Playwright browser verification) dispatches, then the owner's integration decision and
  `/session-close`.
- `completion_evidence`: not recorded on `dev` yet — the files exist only on the unmerged
  `agent/phase-wb-05` worktree branch: `ts/src/stage/FileBrowserRegion.tsx`,
  `ts/src/stage/FileTreeContextMenu.tsx`, `ts/src/stage/panelBridge.ts`,
  `ts/src/workbench/panelRegistry.tsx`, `src/api/routes/workbench.py`,
  `test/test_workbench_api.py`; citing them as `completion_evidence` on `dev` trips governance's
  evidence-exists check, so they are named here instead.
- `result`: 'In progress. W05-C1 (tree, filters, documentation-explorer preset) passed
    first-cycle: build clean, W05-V1 clean PASS with no findings. W05-C2 (context menu) built 4
    of 5 actions first-cycle (reveal, open-in-viewer with tab submenu, copy-relative-path,
    inject-path). The 5th action, copy-absolute-path, needed a backend route
    (GET /api/v1/workbench/absolute-path) that ADR-015 specifies but phase-wb-01 never shipped;
    reported up as a blocking prompt/reality mismatch. The coordinator ruled it an
    implementation-shortfall fix inside this phase (W03-G item-6 precedent) and widened the
    deliverable on dev (commit 7b67f80) to add src/api/routes/workbench.py and
    test/test_workbench_api.py. Fix cycle 1 of 2 on the W05-C2 item: demo-creator-py added the
    GET-only, gated, resolved-path-validated route with 41 passing tests (commit 73c7676);
    demo-creator-web wired the frontend action to it (commit f186010). W05-V2 then passed clean
    on the full five-action diff (one non-blocking stale-comment note). W05-G
    (demo-validator-check) passed every item: governance OK, private-content OK, deliverable
    confirmed present, build clean, full pytest 551 passed/3 failed (environmental, ideas
    000097/000099), diff confined to the corrected scope (ts/, src/api/routes/workbench.py,
    test/test_workbench_api.py). This orchestrator re-ran the verification commands itself with
    matching results. W05-A and W05-W remain, dispatched by the coordinator rather than this
    orchestrator per the pack.'

## Unresolved

None blocking this orchestrator's charter. W05-A (adversarial review) and W05-W (Playwright
browser verification) are still open, but the pack assigns both as coordinator dispatches, not
`demo-orch-data` dispatches — this orchestrator's stop condition (deliverable exists, W05-G
green, verification output pasted) is met.
