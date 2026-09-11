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

- `cd ts && npm run build` (re-run after the W05-G fix cycle 2 duplicate-key fix):
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
  dist/assets/index-CBwMI6Is.js   528.80 kB │ gzip: 145.12 kB

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
- `uv run pytest test/test_workbench_api.py -v` (re-run after the W05-A fix cycle, includes the
  new gitignore-exclusion test):
  ```
  42 passed, 2 warnings in 1.87s
  ```
- `uv run pytest` (full suite, re-run after the W05-A fix cycle):
  ```
  552 passed, 3 failed in 153.51s (0:02:33)
  ```
  The 3 failures are unchanged from before the fix cycle, all in `test/test_demo_terminal.py`
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`), each showing
  `pyenv: cannot rehash: couldn't acquire lock ... .pyenv-shim` — the recorded host-wide
  pyenv-rehash issue (ideas 000097/000099), not a phase failure. This phase's diff does not touch
  `test/test_demo_terminal.py` or `src/demo`.
- Adversarial review (pack W05-A, dispatched by the coordinator): returned 1 BLOCKER and 1 MINOR,
  both fixed in fix cycle 1 — see Acceptance.
- Playwright browser verification (pack W05-W, dispatched by the coordinator): passed every
  checklist item with measured evidence (tree/filters/preset, all five context-menu actions with
  clipboard strings asserted via a stub, inject un-executed, reveal 200, open-in-viewer into tab
  2, menu dismissal, zero-scroll/non-overlap at all four sizes). One real defect surfaced
  incidentally: a React duplicate-key warning in `FileBrowserRegion.tsx`'s `TreeLevel`, reproduced
  for `docs/04-decisions/README.md` and `docs/README.md`. Fixed in fix cycle 2 (the last for this
  gate) — see Acceptance.

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
  cycle). W05-G (demo-validator-check) then passed every item. The coordinator's W05-A
  (adversarial review) then found 1 BLOCKER: `GET /absolute-path` applied only ADR-015 rule 2
  (repo-boundary), never rule 3 (gitignore/`_private` exclusion), making it an existence/location
  oracle over content `/list`, `/search` and `/reveal` all hide (`.venv` returned 200 with its
  absolute path where the sibling routes make it invisible or refuse it). Fix cycle 1 of 2 on
  this W05-A finding: `demo-creator-py` reused the existing `_is_reveal_excluded` helper in
  `get_absolute_path`, folding an excluded path into the same 404 as a nonexistent one (matching
  "not shown, not merely refused"), corrected the route's docstring, and added a test asserting
  `.venv` 404s (commit `65d3909`, combined with the fix below). The review's 1 MINOR — the same
  stale `panelRegistry.tsx` comment W05-V2 had already flagged non-blocking — was fixed in the
  same cycle by `demo-creator-web` (also `65d3909`). Re-verified: `test/test_workbench_api.py`
  42 passed (was 41), full suite 552 passed/3 failed (unchanged environmental set), build clean,
  governance clean, private-content clean. The coordinator then dispatched W05-W (Playwright
  browser verification), which passed every item and surfaced one incidental defect: a React
  "two children with the same key" warning when rendering `docs/` (both `docs/README.md` and
  `docs/04-decisions/README.md` implicated). Fix cycle 2 of 2 (the last before owner escalation),
  commit `e700c85`: `demo-creator-web` reproduced it live with a real dev server and Playwright
  (confirming `TreeLevel`'s keys and `buildTree`'s path construction were already correct in
  isolation) and found the actual mechanism — a one-render race where `setContextFolder` commits
  before the `useEffect` that re-fetches `entries` runs, so `buildTree` briefly receives the new
  `contextFolder` paired with the *previous* folder's `entries`; a stale entry whose path doesn't
  share the new prefix falls through `buildTree`'s unstripped-path fallback and collides with a
  real node under the new folder. Fixed by tracking which folder `entries` was actually fetched
  for (`entriesFolder`) and gating both the `tree` memo and the loading-state render on
  `entriesFolder === contextFolder`, so the mismatched pairing is never fed to `buildTree` — the
  UI shows "Loading…" for that one render instead. Confirmed gone via a live Playwright repro
  against `docs/` (including an expanded `docs/04-decisions/`) both before (warning present) and
  after (clean) the fix.

## Backlog

- `status: active`, `agent: agent-demo-data`.
- `next_action`: W05-C1/V1, W05-C2/V2 (including the coordinator-approved backend fix cycle),
  W05-G, W05-A's fix cycle 1 (blocker + minor), and W05-W with its fix cycle 2 (React
  duplicate-key, the last fix cycle for this phase's gate) have all passed; this orchestrator's
  own verification commands are pasted above. Remaining before this phase can close: the owner's
  integration decision and `/session-close` — no further coordinator dispatch is outstanding
  against this orchestrator per the pack.
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
    (demo-validator-check) passed every item. The coordinator then dispatched W05-A (adversarial
    review), which found 1 BLOCKER (the new /absolute-path route applied only ADR-015 rule 2, not
    rule 3, making it a gitignore/_private existence oracle - proven live against .venv) and 1
    MINOR (the same stale panelRegistry.tsx comment W05-V2 had already flagged non-blocking).
    Fix cycle 1 of 2 on this finding, commit 65d3909: demo-creator-py reused the existing
    _is_reveal_excluded helper to fold excluded paths into the routes 404 branch, corrected the
    docstring, and added a gitignore-exclusion test; demo-creator-web corrected the comment.
    Re-verified: test/test_workbench_api.py 42 passed (was 41), full suite 552 passed/3 failed
    (same environmental set, ideas 000097/000099), build clean, governance clean, private-content
    clean. The coordinator then dispatched W05-W (Playwright browser verification), which passed
    every checklist item with measured evidence and surfaced one incidental defect: a React
    duplicate-key warning rendering docs/ (docs/README.md and docs/04-decisions/README.md).
    Fix cycle 2 of 2 (the last before owner escalation), commit e700c85: demo-creator-web
    reproduced it live (real dev server + Playwright) and found the actual mechanism - a
    one-render race where buildTree briefly receives the new contextFolder paired with the
    previous folders stale entries before the re-fetch effect runs, producing a colliding path
    via buildTrees unstripped-path fallback. Fixed by tracking which folder entries was actually
    fetched for and gating the tree build on that matching contextFolder. Confirmed gone via a
    live before/after Playwright repro. Re-verified: npm run build clean (foreground, pasted
    above). Every dispatch this pack assigns to this orchestrator or the coordinator for
    phase-wb-05 has now run and passed.'

## Unresolved

None blocking this orchestrator's charter. Every W05 work item, the phase gate, and both rounds
of coordinator-dispatched review (W05-A, W05-W) have passed, each fix cycle within the two-cycle
limit. What remains is the owner's integration decision and `/session-close` — neither of which
this orchestrator performs.
