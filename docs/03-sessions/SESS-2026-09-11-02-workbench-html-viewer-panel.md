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

Recomputed at session close on `dev` (commit range `6a5d92e..392b052` — claim through the
completion commit; branch `agent/phase-wb-04` integrated fast-forward at `983164d`, completion
edit `392b052`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 55 modules transformed`, built in
  `1.11s` (the module count grew from the 49 recorded mid-session as later phases added panels;
  the chunk-size-over-500kB note remains Vite's informational warning, not an error).
- `uv run pytest` — `552 passed, 3 failed`. The three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`, all in
  `test/test_demo_terminal.py`) are the known host-wide `pyenv rehash` shim-lock contention
  (`pyenv: cannot rehash: couldn't acquire lock ...pyenv-shim`) — the recorded environmental
  defect (ideas 000097/000099), not a phase finding; this phase's diff does not touch `test/` or
  `src/demo`. The passed count grew from the mid-session `546` as later phases (wb-05 through
  wb-09) added tests on top.
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 165 documents, 16
  memories, 121 backlog phases` (document/phase counts reflect the repository's current state,
  not this phase's diff alone).
- `git add -A` then `uv run python tools/check_no_private_content.py` — `check_no_private_content:
  OK (500 tracked files, 31 identifiers checked)`.
- Adversarial review (`demo-adversary`, pack W04-A): 2 fix cycles, both resolved — see `## Backlog`
  below for the findings and fixes; re-verified clean after each (`beabb33`, `983164d`).
- Playwright browser verification (`demo-validator-web`, pack W04-W): passed every item with
  measured evidence per the backlog `result` field — dropdown scoping, search filtering, known
  overview figure render, on-disk change + refresh, dialog re-scope, `.svg` render, two-tab
  isolation, reload persistence, zero-scroll/non-overlap at all four sizes, no uncaught console
  errors.

## Acceptance

- The dropdown lists exactly the recursive .html/.svg files of the selected directory, filters
  by search, renders both an .html page and an .svg, refresh re-fetches a changed file, and the
  dialog re-scopes the directory (REQ-007 W07): **Met** — W04-V1 confirmed the file list comes
  only from phase-wb-01's `/search` and `/list` routes (no client-side walk, no native picker),
  the compatible set is exactly `.html`/`.svg`, refresh bumps a cache-busting token forcing a real
  re-fetch, and the overview page remains reachable as an ordinary dropdown entry. W04-W then
  confirmed the same live in a real browser, plus `.svg` render against a temporary fixture and
  dialog re-scoping.
- Two tabs hold different directory/search/page state, switch cleanly, and survive reload
  (REQ-007 W08): **Met** — W04-V2 confirmed directory/search/page are per-tab (`ViewerTab`), the
  header controls are single shared instances reading the active tab, state persists under the
  ADR-016 `html_viewer_tabs` key via `patchStoredState` with a synchronous lazy-init read to avoid
  an async hydration race, and the tab strip mirrors the terminal's own tab interaction pattern.
  W04-W confirmed two-tab isolation and reload persistence of both tabs live.

## Backlog

- `status: complete`, `agent: agent-demo-data` retained as the record of who did the work.
- `next_action`: None — phase complete: both work items passed first-cycle, W04-A clean after its
  two fix cycles, W04-W green on every item with measured evidence, and the branch integrated into
  `dev` fast-forward at `983164d` under PROMPT-023 delta 1 pre-approved integration (GOV-003
  completion gate, workbench extension). Completion edit `392b052`.
- `completion_evidence`: `ts/src/stage/HtmlViewerRegion.tsx`,
  `ts/src/stage/DirectoryPickerDialog.tsx`, `ts/src/workbench/panelRegistry.tsx`,
  `ts/src/workbench/storage.ts`, `ts/src/workbench/types.ts`, `ts/vite.config.ts`,
  `_data/workbench/layouts/layout-1.json`.
- `result`: W04-C1/V1 (viewer panel and controls) and W04-C2/V2 (viewer tabs) each passed on the
  first creator/validator cycle, no fix cycles needed. W04-G's mechanical checklist passed apart
  from the 3 known-environmental PTY test failures. A pre-existing governance drift (this phase's
  own claim commit had not regenerated `docs/08-governance/catalog.md`) was caught by W04-G's
  pytest run and fixed on `dev` at `eb5c1cf`.

  W04-A (adversarial review) fix cycle 1 of 2 fixed 2 blockers (the file-serving dev route had no
  demo-gate, live on every plain `npm run dev`, ADR-015 rule 1; its boundary check did not
  resolve symlinks, so a symlink under the repo pointing outside it served the outside file's
  bytes, ADR-015 rule 2), 1 major (the viewer iframe had no `sandbox` attribute) and 1 minor
  (case-sensitive `.git` exclusion) — commit `300b6ac`: gated `serveRepositoryFiles` behind
  `D_SYSTEM_DEMO_TERMINAL=1` in the frontend process's own environment, added a `realpathSync`
  boundary check mirroring the backend's `Path.resolve()`, set `sandbox=""` on the viewer iframe,
  made the `.git` segment check case-insensitive.

  The re-review confirmed all four fix-cycle-1 fixes hold (each re-proven live) and found 1 new
  blocker plus 2 small items. Fix cycle 2 of 2 (last before owner escalation), commit `1f45371`:
  BLOCKER — the open-in-tab fallback served the same untrusted content as a full top-level
  navigation with no sandboxing (an iframe attribute cannot reach a top-level navigation),
  defeating the iframe sandbox fix in one click; per the owner-ratified constraint to keep the
  fallback rather than descope it, `serveRepositoryFiles` now sets
  `Content-Security-Policy: sandbox` on every response from `/workbench-file/*`, which applies to
  top-level navigations the same as to frames, blocking script execution and giving the document
  an opaque origin; the generated overview page has no `<script>` tags so it still renders
  through both the iframe and the open-in-tab path (confirmed live). FLAGGED — the `.git`
  segment check now strips trailing dots/spaces before the case-insensitive comparison, closing
  the Win32 trailing-dot/space path-stripping bypass (unprovable on this Linux worktree, string
  normalization verified correct here). MINOR — fixed a TOCTOU where the symlink-boundary check
  validated `realpathSync(resolved)` but `createReadStream` then re-opened the original path; now
  streams from the already-validated `realResolved` path. Everything the adversary held from fix
  cycle 1 (gate, symlink boundary, iframe sandbox, `.git` case-insensitivity) and from the
  original W04-A pass (refresh cache-busting, two-tab isolation, reload restoration, zero-scroll
  structure, registration) is untouched. Re-verified after fix cycle 2: `npm run build` clean,
  `uv run pytest` 546 passed/3 failed unchanged (environmental), governance and
  `check_no_private_content` both green.

  W04-W (coordinator-dispatched, `demo-validator-web`) then passed every item with measured
  evidence: dropdown lists exactly the selected directory's recursive `.html`/`.svg` files
  (substitute directories `_public` and `templates/html` — the pack's named fixture path
  `docs/07-architecture/diagrams/demo` exists only on the unmerged `agent/phase-demo-07` branch,
  recorded rather than rounded into a pass), search filtering, known overview figure render,
  on-disk change + refresh, dialog re-scope, `.svg` render (against a temporary untracked
  coordinator fixture, removed after), two-tab isolation and reload persistence of both tabs,
  zero-scroll and non-overlap at 1280x720/1366x768/1920x1080/1024x768, no uncaught console errors
  (only the intended sandbox script-blocking messages), and the deferred REQ-007 W06 rider from
  phase-wb-02: layout-2's overview/html-viewer slot dropdown swaps both directions and layout-1's
  single-admit slot renders a plain header. Integrated into `dev` fast-forward at `983164d` under
  PROMPT-023 delta 1 (pre-approved, gate green). Follow-on for `phase-wb-07`: demo launches must
  set `D_SYSTEM_DEMO_TERMINAL=1` on the frontend process too — the runbook's launch section did
  not yet say so at completion time.

## Unresolved

None. Both acceptance conditions are Met, W04-A and W04-W both passed clean, and the branch is
integrated onto `dev`. The one follow-on noted above (runbook launch-section update for the
frontend-process env var) was routed to `phase-wb-07` rather than left open here; idea 000105
(runbook lacks the HTML Viewer Embedded/Open-in-tab toggle) was recorded separately after this
phase closed.

## Review

Independent sub-agent review at close (fresh general-purpose agent, commit range
`6a5d92e..392b052` — the phase-wb-03 close commit through this phase's completion edit — its own
command runs, no access to this record's conclusions beyond the claims it was asked to check).
Findings pasted verbatim, condition by condition:

- **Acceptance condition 1 (REQ-007 W07) — HOLDS.** "The file list is genuinely backend-sourced,
  not client-walked or hardcoded. `HtmlViewerRegion.tsx:44-47` (`buildSearchUrl`) calls `GET
  /api/v1/workbench/search` with `ext=.html&ext=.svg` query params. That route
  (`src/api/routes/workbench.py:373-394`) predates this phase (introduced in `phase-wb-01`, commit
  `50d8f47`) and is genuinely recursive — it calls `_walk_visible_tree(resolved)`, distinct from
  `/list`'s one-level `_visible_children`. This phase did not modify `workbench.py` at all (absent
  from the diff's file list), so the route's behavior is inherited, not newly asserted.
  Compatible-extension set is exactly `.html`/`.svg`: `HtmlViewerRegion.tsx:21`:
  `const COMPATIBLE_EXTENSIONS = ['.html', '.svg']` — no third extension, no wildcard. Search input
  filters client-side against the fetched list, a legitimate design choice (avoids a round trip per
  keystroke) that still satisfies 'filters by the search input.' Both an `.html` page and an `.svg`
  render through the same iframe path — no format-specific branch; the `<iframe src={embedSrc}>` is
  fed by `/workbench-file/<path>` regardless of extension, and the backend's
  `CONTENT_TYPE_BY_EXTENSION` map in `vite.config.ts` serves `.svg` as `image/svg+xml` and `.html`
  as `text/html`. Refresh genuinely forces a re-fetch, not a cached response: `refreshToken` state
  increments on click and is both appended as a cache-busting query param on the iframe `src`
  (`?v=${refreshToken}`) and a dependency of the file-existence check effect; independently, the
  server route sets `Cache-Control: no-store` on every response, so even without the client-side
  token a browser cache would not intervene — two independent mechanisms, not one relied upon
  alone. The directory dialog re-scopes the directory and is fed exclusively by `GET
  /api/v1/workbench/list` (`DirectoryPickerDialog.tsx`), never a native OS picker, and calls
  `onSelectDirectory` which updates the active tab's `directory` field, re-triggering the search
  effect."
- **Acceptance condition 2 (REQ-007 W08) — HOLDS.** "State is genuinely per-tab, not shared.
  `ViewerTab` (`HtmlViewerRegion.tsx`) carries `directory`, `searchText`, `selectedFile` per tab id;
  `updateTab(id, patch)` scopes writes to one tab by id; switching tabs re-derives the shared header
  controls' displayed values from that tab's own fields — a genuine per-tab model, not a single
  shared state object relabeled. Header controls are genuinely shared single instances acting on
  `activeTab`, matching the requirement's 'shared header controls' — confirmed by there being
  exactly one `<Popover>` file picker and one `<DirectoryPickerDialog>` in the render tree, not one
  per tab. Persistence is real and correctly scoped: `saveHtmlViewerTabs`
  (`ts/src/workbench/storage.ts:141-156`) writes through the pre-existing `patchStoredState` helper
  (confirmed present and reused, not new) under the ADR-016 shared key, merging rather than
  overwriting — so this write cannot clobber the layout engine's or notes strip's own fields,
  matching the 'ADR-016 selections split' scope language. `loadInitialTabs` reads synchronously via
  `useRef` lazy-init on first render (no async hydration race that could otherwise clobber a
  just-restored state with a placeholder tab) — a real design decision with a stated reason, not
  just an assertion. Reload-survival follows directly from write-on-every-tabs/activeTabId-change
  plus synchronous read-on-mount; I did not run the Playwright browser pass myself (out of my reach
  per the task), but the code path that would produce that behavior is genuinely present and
  coherent, not merely claimed in the session record's prose."
- **Named security fixes — all confirmed present in code at `392b052`.** "Checked directly in
  `ts/vite.config.ts` and `HtmlViewerRegion.tsx`, not inferred from commit messages alone: (1)
  demo-flag gate — `...(env.D_SYSTEM_DEMO_TERMINAL === '1' ? [serveRepositoryFiles()] : [])` in the
  `plugins` array, confirmed present, unset means the route is never registered. (2) symlink
  realpath boundary check — `const realResolved = realpathSync(resolved); if (realResolved !==
  realRepoRoot && !realResolved.startsWith(realRepoRoot + sep)) { ...403... }`, present, and
  `realRepoRoot` is itself computed via `realpathSync(repoRoot)` at module load, so a symlinked
  worktree checkout can't widen its own boundary. (3) TOCTOU fix — `createReadStream(realResolved)`
  streams from the already-validated realpath, not a re-opened `resolved`, confirmed by direct read
  of the final code. (4) iframe `sandbox=""` — present, no tokens (maximally restrictive). (5)
  `Content-Security-Policy: sandbox` on `/workbench-file/*` — present, applied unconditionally to
  every response. (6) `.git` exclusion, case-insensitive and trailing-dot/space-stripped —
  `segment.replace(/[. ]+$/, '').toLowerCase() === '.git'`, matches the claimed Win32 bypass closure
  exactly. Both fix-cycle commits (`300b6ac`, `1f45371`) were inspected individually via `git show
  --stat`; their diffs match both their own commit messages and the final state at `392b052` — the
  two-cycle adversarial narrative in the session record is a real sequence of commits, not a
  retrospectively-written story."
- **Reruns performed independently**: `cd ts && npm run build` — succeeded, `✓ 55 modules
  transformed`, built in `1.01s` (matches the session record's `55 modules`/`1.11s` claim, timing
  trivially different run-to-run, module count exact). `uv run python -m src.governance` — exit 0,
  `Governance OK: 18 systems, 165 documents, 16 memories, 121 backlog phases`, matches exactly.
  `git add -A && uv run python tools/check_no_private_content.py` — `check_no_private_content: OK
  (500 tracked files, 31 identifiers checked)`, matches exactly. Did not rerun `uv run pytest` (the
  3-failure claim concerns `test_demo_terminal.py`, environmental PTY/pyenv contention unrelated to
  this phase's diff, which touches no `test/` or `src/demo` file — confirmed by the diff's file
  list) or the Playwright/adversarial passes (outside a sub-agent's reach; their claimed code
  effects were instead verified directly, above). Confirmed `392b052` is a genuine ancestor of
  current `dev` HEAD (`d102c51`) via `git merge-base --is-ancestor`, and that `6a5d92e` is the
  phase-wb-03 close commit immediately preceding this phase's claim — the stated commit range is
  accurate, not approximate.
- **Discrepancies found**: none. "Every specific, checkable claim in both the session record and
  `backlog.yaml`'s `result` field — the route provenance, the extension filter, the refresh
  mechanism, the per-tab state model, the persistence merge-safety, and each of the five named
  security fixes — was independently verifiable in the actual diff or by rerunning the command, and
  each one held. The one place the record itself flags an honesty gap (W04-W substituting
  `_public`/`templates/html` for a fixture path that only exists on an unmerged branch, 'recorded
  rather than rounded into a pass') is itself a good sign — it is disclosure, not a discrepancy I
  found; I have no way to independently confirm or deny the Playwright pass's substance, but the
  record's own candor about its limits argues against the report having been polished into false
  confidence elsewhere."
- **Bottom line (verbatim)**: "Both acceptance conditions genuinely hold on the evidence available
  to independent review: the HTML Viewer panel's file list, extension filter, refresh, directory
  dialog, and tab-state model are all backed by real, traceable code wired to pre-existing backend
  routes rather than asserted behavior, and all five named security fixes from the two-cycle
  adversarial review are verifiably present in the code at the completion commit, not merely
  claimed in prose. Every mechanical verification command I could rerun (`npm run build`,
  governance, private-content check) reproduced the session record's exact claimed output. I found
  no discrepancy, substantive or cosmetic, between what the session record and `backlog.yaml`
  assert and what the diff and my own reruns support — this phase's `status: complete` marking
  stands up to independent audit."

## Decisions

- The owner ran `/session-close phase-wb-04` on 2026-09-11 as a **retroactive audit** of a phase the
  build coordinator had already marked `status: complete` under the GOV-003 demo/workbench
  completion-gate exception, not as the phase's original close — consistent with GOV-003's own text
  that "the owner reads the session records and may run `/session-close` afterwards as an audit of
  phases already complete." No implementation work was performed this session; the only edits were
  to the session record (recomputing `## Phase` through `## Unresolved` against current `dev`
  instead of the mid-phase state they had been frozen at) and one factual correction to
  `backlog.yaml` (below).
- Because the phase was already `status: complete`, this session's step-6 completion decision was
  whether that status should *stand*, not whether to *set* it. Both required conditions held — the
  recomputed checkpoint-equivalent acceptance verdicts (both Met) and the independent sub-agent
  review (no discrepancies) — so the status is left unchanged at `complete`.

## Corrections

- `backlog.yaml`'s `result` field for `phase-wb-04` opened with the sentence "In progress." even
  though the phase carries `status: complete` and the rest of the same field narrates the phase all
  the way through W04-W and integration — a leftover from when the field was first written
  mid-phase and never updated for the final state. Corrected to "Complete." in this session; no
  other wording in the field changed.
- This session record's `## Verification`, `## Acceptance`, `## Backlog`, and `## Unresolved`
  sections were still describing the mid-phase state (`546 passed`/`49 modules`, W04-W "not yet
  run," integration "awaits the owner's explicit approval," `status: active`) despite the phase
  having finished and closed on `dev` before this audit began. Recomputed against current `dev`
  (`d102c51`) per this command's own instruction that these sections must reflect the repository
  "as it stands at close," not the last mid-session checkpoint.

## Left undone

- The `phase-wb-07` runbook follow-on this phase surfaced (demo launches must set
  `D_SYSTEM_DEMO_TERMINAL=1` on the frontend process, not just the backend) was routed to
  `phase-wb-07` rather than fixed here; this audit did not verify whether `phase-wb-07`'s own work
  actually picked it up — that is that phase's own close's concern, not this one's.
- Idea 000105 (runbook lacks the HTML Viewer Embedded/Open-in-tab toggle), recorded after this
  phase closed, remains open in the idea system; this audit did not triage it.
