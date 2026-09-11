---
schema_version: 1
id: doc-session-workbench-html-viewer-panel
code: SESS-2026-09-11-02
title: Demo data orchestration — HTML Viewer panel with tabs (phase-wb-04)
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui]
depends_on: [doc-workbench, doc-prompt-workbench-delegation-pack]
---

# Demo data orchestration — HTML Viewer panel with tabs (phase-wb-04)

## Phase

`phase-wb-04` — HTML Viewer panel with tabs: generalizes the overview panel into a panel that
displays a selected `.html`/`.svg` page via phase-wb-01's search/listing routes, with refresh, a
searchable file dropdown, an in-app repo-relative directory dialog, and terminal-session-style
tabs scoping directory/search/page per tab with ADR-016 persistence.

## Verification

Run in the worktree (`/code/d-system-worktrees/phase-wb-04`, branch `agent/phase-wb-04`, rebased
onto `dev` at `eb5c1cf` after the catalog regeneration below):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 49 modules transformed`, built
  in ~1.0-1.1s across every rerun including the post-rebase rerun (the chunk-size-over-500kB note
  is Vite's informational warning, not an error).
- `uv run pytest` — `546 passed, 3 failed`. The three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`, all in
  `test/test_demo_terminal.py`) are the known host-wide `pyenv rehash` shim-lock contention
  (`pyenv: cannot rehash: couldn't acquire lock ...pyenv-shim`) — the recorded environmental
  defect (ideas 000097/000099), not a phase finding; this phase's diff does not touch `test/` or
  `src/demo`.
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 160 documents, 16
  memories, 119 backlog phases`.
- `git add -A` then `uv run python tools/check_no_private_content.py` — `check_no_private_content:
  OK (488 tracked files, 0 identifiers checked)`.

## Acceptance

- The dropdown lists exactly the recursive .html/.svg files of the selected directory, filters
  by search, renders both an .html page and an .svg, refresh re-fetches a changed file, and the
  dialog re-scopes the directory (REQ-007 W07): **Met** — W04-V1 confirmed the file list comes
  only from phase-wb-01's `/search` and `/list` routes (no client-side walk, no native picker),
  the compatible set is exactly `.html`/`.svg`, refresh bumps a cache-busting token forcing a real
  re-fetch, and the overview page remains reachable as an ordinary dropdown entry.
- Two tabs hold different directory/search/page state, switch cleanly, and survive reload
  (REQ-007 W08): **Met** — W04-V2 confirmed directory/search/page are per-tab (`ViewerTab`), the
  header controls are single shared instances reading the active tab, state persists under the
  ADR-016 `html_viewer_tabs` key via `patchStoredState` with a synchronous lazy-init read to avoid
  an async hydration race, and the tab strip mirrors the terminal's own tab interaction pattern.

## Backlog

- `status: active`, `agent: agent-demo-data`.
- `next_action`: W04-G (phase gate) ran clean apart from the 3 known-environmental PTY failures;
  demo-orch-data's own verification commands are pasted above with real output. Remaining before
  this phase can close: coordinator-dispatched W04-A (adversarial review) and W04-W (Playwright
  browser verification), then integration into `dev` with the owner's approval.
- `completion_evidence`: `ts/src/stage/HtmlViewerRegion.tsx`,
  `ts/src/stage/DirectoryPickerDialog.tsx`, `ts/src/workbench/panelRegistry.tsx`,
  `ts/src/workbench/storage.ts`, `ts/src/workbench/types.ts`, `ts/vite.config.ts`,
  `_data/workbench/layouts/layout-1.json`.
- `result`: W04-C1/V1 (viewer panel and controls) and W04-C2/V2 (viewer tabs) each passed on the
  first creator/validator cycle, no fix cycles needed. W04-G's mechanical checklist passed;
  its only non-green item was the pytest run, whose 3 failures are the recorded environmental
  pyenv issue. A pre-existing governance drift (the `phase-wb-04` claim commit had not
  regenerated `docs/08-governance/catalog.md`) was caught by W04-G's pytest run
  (`test_codes.py::test_committed_catalog_matches_regenerated_output`) and fixed on `dev` at
  `eb5c1cf`; the worktree was rebased onto it.

## Unresolved

- W04-A (adversarial review) and W04-W (Playwright browser verification) are dispatched by the
  coordinator, not this orchestrator, per the pack (`PROMPT-021`) — not yet run.
- Integration into `dev` awaits the owner's explicit approval.
