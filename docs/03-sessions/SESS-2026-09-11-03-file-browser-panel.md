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
  dist/assets/index-DXtxaY97.js   528.30 kB │ gzip: 145.09 kB

  (!) Some chunks are larger than 500 kB after minification. ...
  ✓ built in 1.06s
  ```
- `uv run python -m src.governance`:
  ```
  Governance OK: 18 systems, 161 documents, 16 memories, 119 backlog phases
  ```
- `uv run python tools/check_no_private_content.py` with the changes staged:
  ```
  note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
  check_no_private_content: OK (492 tracked files, 0 identifiers checked)
  ```
- Adversarial review (pack W05-A): not yet dispatched — blocked on the finding below.
- Playwright browser verification (pack W05-W): not yet dispatched — blocked on the finding below.

## Acceptance

- The tree matches the filesystem for a known folder; filters hide non-matching files and empty
  folders; the documentation-explorer preset re-scopes the tree (REQ-007 W09) — **Met**. W05-C1
  built this (commit `259ff7b`); W05-V1 (demo-validator-code) reviewed the diff against
  `dev...agent/phase-wb-05 -- ts/` and returned a clean PASS with no findings, confirming tree
  content comes only from phase-wb-01's `/search` route, filters structurally omit empty
  folders (never instantiated, not merely hidden), the documentation-explorer is one config
  preset of the same panel (not a second panel type), and the panel is the explorer slot's
  default-visible panel today (the only implemented admit in that slot).
- All five context-menu actions work — open-in-viewer lands in the chosen tab, inject-path
  appears un-executed on the active terminal, both copies place the expected strings, and the
  reveal request reaches the backend action route — **Not met**. W05-C2 (commit `7a6a439`) built
  reveal, open-in-viewer-with-tab-submenu, copy-relative-path and inject-path fully; the fifth
  action, copy-absolute-path, is blocked — see Unresolved.

## Backlog

- `status: active`, `agent: agent-demo-data`.
- `next_action`: Blocked on a prompt/reality mismatch reported to the coordinator — W05-C2's
  fifth context-menu action (copy-absolute-path) requires a backend route ADR-015 says should
  exist ("served from the backend's knowledge of the repository root") but phase-wb-01 never
  built one, and phase-wb-05's deliverable is `ts/src` only so this phase cannot add it. Awaiting
  the coordinator's decision (widen the deliverable to add the route, or descope the action)
  before dispatching W05-V2.
- `completion_evidence`: not recorded on `dev` yet — the files exist only on the unmerged
  `agent/phase-wb-05` worktree branch (`ts/src/stage/FileBrowserRegion.tsx`,
  `ts/src/stage/FileTreeContextMenu.tsx`, `ts/src/stage/panelBridge.ts`,
  `ts/src/workbench/panelRegistry.tsx`); citing them as `completion_evidence` on `dev` trips
  governance's evidence-exists check, so they are named here instead.
- `result`: 'In progress. W05-C1 (tree, filters, documentation-explorer preset) passed on the
  first creator/validator cycle: build clean, W05-V1 clean PASS with no findings (commits
  `259ff7b` claim-side, validated against `dev...agent/phase-wb-05 -- ts/`). W05-C2 (context
  menu, five actions) built four actions fully (reveal via the backend action route with refusal
  surfaced; open-in-viewer with a tab-target submenu, gated to .html/.svg; copy-relative-path;
  inject-path reusing the R12 mechanics, disabled when the terminal is dropped/absent) at commit
  `7a6a439`, build clean. The fifth action, copy-absolute-path, is blocked: ADR-015 states this
  action "is served from the backend''s knowledge of the repository root," but
  `src/api/routes/workbench.py` (phase-wb-01''s deliverable) exposes no route returning an
  absolute path — `/list` and `/search` return only repo-relative paths, and `/reveal`''s
  argument is a side-effecting opener invocation, not a path lookup. Adding such a route means
  editing `src/api/routes/workbench.py`, outside this phase''s `ts/src`-only deliverable. The
  creator did not fabricate a client-side path join (the repo root is a server-side fact) and did
  not touch the out-of-scope file; the menu item is present and shows a clear in-place message
  naming the gap rather than a broken or fake copy. Reported up per the coordinator''s standing
  instruction to stop and report rather than commit a file outside the declared deliverables.'

## Unresolved

Blocking finding, reported up: `phase-wb-05`'s W05-C2 action 4 (copy-absolute-path) cannot be
completed within the `ts/src`-only deliverable. ADR-015 ("Copy-absolute-path (W09) is served from
the backend's knowledge of the repository root") presupposes a backend route that does not exist —
phase-wb-01's `src/api/routes/workbench.py` ships `/list`, `/search`, `/reveal`, the idea route
and the backlog route, but nothing that resolves a repo-relative path to an absolute one. This is
either a gap in phase-wb-01's delivery against ADR-015, or a deliverable-widening decision for
phase-wb-05 (adding a small read route to `src/api/routes/workbench.py`) — a call reserved to the
coordinator/owner, not this agent, per the W03-G item-6 precedent. W05-V2, W05-G, W05-A and W05-W
are not yet dispatched pending that decision.
