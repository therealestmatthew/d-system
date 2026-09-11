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

Recomputed at session close on `dev` (commit range `392b052..3c6fac0` — phase-wb-04's completion
commit through phase-wb-05's own completion-evidence commit; branch `agent/phase-wb-05` integrated
fast-forward at `041cf45`, completion edit `a392a76`, evidence-listing follow-up `3c6fac0`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 55 modules transformed`, built in
  `1.18s` (module count grew from the mid-session `52` as later phases added panels; the
  chunk-size-over-500kB note remains Vite's informational warning, not an error).
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 165 documents, 16
  memories, 121 backlog phases` (counts reflect the repository's current state, not this phase's
  diff alone).
- `git add -A` then `uv run python tools/check_no_private_content.py` — `check_no_private_content:
  OK (500 tracked files, 31 identifiers checked)`.
- `uv run pytest` (full suite) — `552 passed, 3 failed`. The three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`, all in
  `test/test_demo_terminal.py`) are the known host-wide `pyenv rehash` shim-lock contention
  (ideas 000097/000099), unchanged in identity and count from the mid-session run; this phase's
  diff does not touch `test/test_demo_terminal.py` or `src/demo`.
- Adversarial review (pack W05-A, dispatched by the coordinator): returned 1 BLOCKER and 1 MINOR,
  both fixed in fix cycle 1 — see Acceptance.
- Playwright browser verification (pack W05-W, dispatched by the coordinator): passed every
  checklist item with measured evidence (tree/filters/preset, all five context-menu actions with
  clipboard strings asserted via a stub, inject un-executed, reveal 200, open-in-viewer into tab
  2, menu dismissal, zero-scroll/non-overlap at all four sizes). One real defect surfaced
  incidentally: a React duplicate-key warning in `FileBrowserRegion.tsx`'s `TreeLevel`, reproduced
  for `docs/04-decisions/README.md` and `docs/README.md`. Fixed in fix cycle 2 (the last for this
  gate) — see Acceptance. Integrated into `dev` fast-forward at `041cf45` under PROMPT-023 delta 1
  (pre-approved, gate green); post-rebase build, governance, staged private-content check and
  pytest (552 passed, 3 environmental PTY failures) reconfirmed by the coordinator at completion.

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

- `status: complete`, `agent: agent-demo-data` retained as the record of who did the work.
- `next_action`: None — phase complete: W05-A clean after its two fix cycles (oracle exclusion and
  stale-render key collision), W05-W green on every item with measured evidence, and the branch
  integrated into `dev` fast-forward at `041cf45` under PROMPT-023 delta 1 pre-approved integration
  (GOV-003 completion gate, workbench extension).
- `completion_evidence`: now recorded on `dev` (added in the follow-up commit `3c6fac0` once the
  files landed at `041cf45` and governance's evidence-exists check could see them):
  `ts/src/stage/FileBrowserRegion.tsx`, `ts/src/stage/FileTreeContextMenu.tsx`,
  `ts/src/stage/panelBridge.ts`, `ts/src/workbench/panelRegistry.tsx`,
  `src/api/routes/workbench.py`, `test/test_workbench_api.py` — all confirmed present at this
  audit.
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
    phase-wb-05 has now run and passed. Integrated into dev fast-forward at 041cf45 under
    PROMPT-023 delta 1 (pre-approved, gate green); completion_evidence recorded on dev in the
    follow-up commit 3c6fac0 once the files existed there for governance's evidence-exists check.'

## Unresolved

None. Both acceptance conditions are Met, W05-A and W05-W both passed (across their fix cycles),
and the branch is integrated onto `dev` with `completion_evidence` recorded. Nothing from this
phase was left open at close.

## Review

Independent sub-agent review at close (fresh general-purpose agent, commit range
`392b052..3c6fac0` — phase-wb-04's completion commit through phase-wb-05's own
completion-evidence follow-up — its own command runs from a detached worktree pinned to
`3c6fac0`, no access to this record's conclusions beyond the claims it was asked to check).
Findings pasted verbatim, condition by condition:

- **Acceptance condition 1 (REQ-007 W09) — HOLDS.** "`ts/src/stage/FileBrowserRegion.tsx` fetches
  the flat file list from `GET /api/v1/workbench/search` exactly once per context-folder change
  (line 292, `SEARCH_URL` constant at line 7) and builds the tree client-side (`buildTree`, lines
  99–128) from that list alone — no other data source. `buildTree` only ever creates a directory
  node while inserting a file that survived filtering under it (lines 108–123), so an
  empty/non-matching folder is structurally never instantiated, not merely hidden after the fact —
  this is what makes 'filters hide … empty folders' true rather than aspirational. On the backend,
  `src/api/routes/workbench.py`'s `GET /search` (line ~372) walks via `_walk_visible_tree`, which
  prunes `.git` and anything `git check-ignore` reports (lines 146–178) before descending, and
  returns files only (`is_file()` filter, line 390) — so the tree the frontend reconstructs is a
  faithful, exclusion-consistent mirror of the filesystem for any folder. The documentation-explorer
  mode is a plain data entry in `PRESETS` (`FileBrowserRegion.tsx` lines 63–70: `{id:
  'documentation', directory: 'docs', typeFilter: '.md'}`), applied by setting the same
  `contextFolder`/`typeFilter` state a manual browse would set (lines 512–517).
  `ts/src/workbench/panelRegistry.tsx` registers exactly one `file-browser` entry (line 70) — no
  second panel type exists for the documentation mode, satisfying the scope's explicit 'not a
  separate panel.' Reran `cd ts && npm run build` against `3c6fac0`: `tsc -b && vite build`
  succeeded, `✓ 52 modules transformed`, built in `1.13s` — clean, matching the module count the
  session record itself attributes to that point in history (it explains the later 55-module
  figure as growth from subsequent phases layered on top; I reproduced 55 modules by building
  current `dev` HEAD directly, confirming that explanation rather than taking it on faith)."
- **Acceptance condition 2 (five context-menu actions) — HOLDS.** "Read
  `ts/src/stage/FileTreeContextMenu.tsx` and `ts/src/stage/panelBridge.ts` in full at `3c6fac0`,
  plus every handler in `FileBrowserRegion.tsx`: Reveal — `handleReveal` (lines 387–417) POSTs to
  `/api/v1/workbench/reveal`; backend `reveal_in_explorer` (workbench.py line 602) validates the
  path, refuses excluded paths (400), and spawns `xdg-open`/`explorer.exe` via
  `_reveal_argv`/`_launch_reveal_opener` — pre-existing route from phase-wb-01, genuinely reached.
  Open in HTML Viewer with tab submenu — `handleOpenInViewer` (lines 479–483) calls
  `viewerHandle.openInTab`, which `HtmlViewerRegion.tsx`'s new effect (diff, lines 278–296)
  implements as a real `updateTab`/`setActiveTabId` call, not a stub; the submenu itself
  (`FileTreeContextMenu.tsx` lines 140–173) lists live tabs from `viewerBridge`. Copy relative path
  — `handleCopyRelativePath` (lines 422–431) writes `node.path` (the exact string `/search`
  returned) via `navigator.clipboard.writeText`. Copy absolute path — `handleCopyAbsolutePath`
  (lines 439–475) GETs `/api/v1/workbench/absolute-path` and clipboards the returned
  `absolute_path`. Inject path into terminal — `handleInjectPath` (lines 487–494) calls
  `terminalHandle.injectPath`, which `TerminalRegion.tsx`'s new effect (diff, lines 392–411)
  implements as `sendToActiveSession(path, false)` — the identical un-executed R12 path
  `InjectionDropdowns` already uses, not a separate/parallel mechanism. None of the five is a stub;
  each reaches a real backend call, a real clipboard write, or a real cross-panel bridge call into
  another panel's actual state-mutating function."
- **The `/absolute-path` exclusion fix — confirmed structurally equivalent to its siblings.**
  "Confirmed at `workbench.py` lines 400–415. It calls `resolve_repo_relative_path` (rule 2,
  identical to `/list`/`/search`/`/reveal`) and, as of `3c6fac0`, also calls
  `_is_reveal_excluded(resolved)` (line 413) — the same helper `/reveal` uses (line 610) and which
  itself delegates to `_git_ignored_paths`, the same function backing `/list`'s and `/search`'s
  `_visible_children`/`_walk_visible_tree`. This is genuinely the same exclusion mechanism reused,
  not a parallel or incomplete reimplementation. Diffed `8708efe` (original route, no exclusion
  check, would 200 on `.venv`) against `65d3909` (the fix) directly: the only change is `if not
  resolved.exists()` becoming `if not resolved.exists() or _is_reveal_excluded(resolved)`, still
  raising `404`. Reran `test/test_workbench_api.py` in the pinned worktree with a correctly
  gitignored `.venv` directory present: all 42 tests pass, including
  `test_absolute_path_route_404s_a_gitignored_path_never_confirming_existence`, which asserts
  `.venv` fixture-ignored via `_git_ignored_paths` and then asserts the route returns exactly
  `404`. This is a genuine, executing assertion, not a prose claim."
- **The duplicate-key fix mechanism — genuinely present.** "`FileBrowserRegion.tsx` at `3c6fac0`
  has `entriesFolder` state (line 277) set only inside the fetch's `.then` alongside `setEntries`
  (lines 299–301) — so it always lags one render behind `contextFolder` on a folder switch, exactly
  as claimed. The `tree` memo is gated on it (lines 343–346: `entriesFolder === contextFolder ?
  filteredEntries : []`), and the loading-state render is separately gated the same way (line 575:
  `loadState === 'loading' || entriesFolder !== contextFolder`). This is precisely the 'gate the
  tree build on `entriesFolder === contextFolder`' mechanism the session record describes, not a
  different or partial fix."
- **Reruns performed independently** (against `3c6fac0` unless noted): `cd ts && npm run build` —
  clean, `52 modules transformed`, `1.13s`. `uv run python -m src.governance` — `Governance OK: 18
  systems, 162 documents, 16 memories, 119 backlog phases` at `3c6fac0`; rerun on current `dev`
  HEAD gave `165 documents, 121 backlog phases`, matching this session record's figures —
  confirming the record's numbers were computed at present-day `dev`, not at the historical commit,
  exactly as its own parenthetical says. `git add -A && uv run python tools/check_no_private_content.py`
  run against the real repo (the throwaway worktree lacks gitignored `_private/portfolio/`):
  `check_no_private_content: OK (500 tracked files, 31 identifiers checked)` — an exact match.
  `uv run pytest test/test_workbench_api.py` at `3c6fac0` — `42 passed`, matching the claimed count
  and the claimed 'was 41' delta (verified directly against the `8708efe`→`65d3909` diff, which
  adds exactly one new test). Full `uv run pytest` at `3c6fac0` — `552 passed, 3 failed` in
  `152.65s`; the three failures are the identical `test/test_demo_terminal.py` tests the record
  names, with the identical `pyenv: cannot rehash … .pyenv-shim` root cause visible in the captured
  output — an exact match, not just an exact count.
- **Discrepancies found**: none substantive. Two cosmetic/process points: "(1) The build
  verification pasted in the session record (`55 modules`) was computed against current `dev` at
  session-close time, not against the `3c6fac0` endpoint the commit range names — the record's own
  parenthetical says as much, and I reproduced both numbers (52 at `3c6fac0`, 55 at current `dev`)
  to confirm the explanation holds rather than being a gloss over a real inconsistency. (2) The
  three 'fix cycle' commits reportedly authored on the unmerged `agent/phase-wb-05` branch
  (`65d3909`, `e700c85`, and by extension earlier branch commits) each have an identical-content
  counterpart on `dev` under a different hash (`4e02fed`, `041cf45`) with the same author, message
  and timestamp but a different parent — i.e., the branch was replayed/rebased onto `dev` before
  the final pointer move, rather than a literal `git merge --ff-only` of the branch's own original
  commit objects. The record's phrase 'integrated fast-forward at `041cf45`' is accurate for that
  final step in isolation but slightly overstates continuity with the branch commits it names
  elsewhere (`65d3909`, `e700c85`) as if they were the commits that landed on `dev`. This is a
  documentation-precision nit about how the integration was described, not a finding about what
  code actually shipped — the diffs are byte-identical between the branch commit and its `dev`
  counterpart in every case I checked."
- **Bottom line (verbatim)**: "Both acceptance conditions genuinely hold, independently verified
  against the actual diff and rerun commands rather than the session record's or backlog.yaml's
  claims: the tree is a structurally faithful, exclusion-consistent mirror of the filesystem built
  only from phase-wb-01's search route, filters and the documentation-explorer preset behave
  exactly as specified with the preset confirmed to be configuration rather than a second panel,
  and all five context-menu actions reach real, non-stub behavior including a `copy-absolute-path`
  backend route that applies the same repo-boundary-and-exclusion checks as its siblings and 404s a
  gitignored path exactly as its own test (which I reran and watched pass) asserts. The two items
  flagged by this phase's own history — the `/absolute-path` information-disclosure blocker and the
  React duplicate-key race — were both genuinely fixed by the mechanism the record describes, not
  merely claimed to be fixed. No discrepancy found rises above cosmetic imprecision in how the
  integration step was narrated; nothing here contradicts the phase's `status: complete`."

## Decisions

- The owner ran `/session-close phase-wb-05` on 2026-09-11 as a **retroactive audit** of a phase
  the build coordinator had already marked `status: complete` under the GOV-003 demo/workbench
  completion-gate exception, not as the phase's original close — the same posture as the
  `phase-wb-04` audit run immediately before this one in the same session. No implementation work
  was performed this session; the only edits were to this session record (recomputing `## Phase`
  through `## Unresolved` against current `dev` instead of the mid-phase state they had been
  frozen at) and one factual correction to `backlog.yaml` (below).
- The owner flagged a parallel session working directly in this same primary checkout on
  enhancements from a later phase (`phase-wb-08`/`phase-wb-09`, per the hand-off docs already on
  `dev`). To avoid sweeping in that session's uncommitted work, this close's commit (step 8) stages
  only the two files this session actually changed by name, rather than `git add -A` as the command
  otherwise directs — a deliberate, owner-confirmed deviation from the literal instruction, scoped
  to this close only.
- Because the phase was already `status: complete`, this session's step-6 completion decision was
  whether that status should *stand*, not whether to *set* it. Both required conditions held — the
  recomputed checkpoint-equivalent acceptance verdicts (both Met) and the independent sub-agent
  review (no discrepancies rising above cosmetic) — so the status is left unchanged at `complete`.

## Corrections

- `backlog.yaml`'s `result` field for `phase-wb-05` opened with "In progress (evidence lives on
  the unmerged `agent/phase-wb-05` worktree branch, not yet on dev, so not cited as
  `completion_evidence` here)" — stale as soon as the follow-up commit `3c6fac0` actually recorded
  `completion_evidence` on `dev`, and doubly stale next to `status: complete`. Corrected to
  "Complete." in this session; no other wording in the field changed. This is the same class of
  leftover mid-phase language corrected in the `phase-wb-04` audit immediately before this one —
  worth checking the remaining `phase-wb-*` `result` fields for the same pattern before they are
  each audited in turn.
- This session record's `## Verification`, `## Backlog`, and `## Unresolved` sections were still
  describing the mid-phase state (`52 modules`, `completion_evidence` "not recorded on dev yet,"
  `status: active`) despite the phase having finished and closed on `dev` before this audit began.
  Recomputed against current `dev` (`a7a35ec` at the time of this edit) per this command's own
  instruction that these sections must reflect the repository "as it stands at close."

## Left undone

- The independent review's discrepancy 2 (the `agent/phase-wb-05` branch was replayed/rebased onto
  `dev` before the fast-forward pointer move, so the commit hashes named elsewhere in this record —
  `65d3909`, `e700c85` — are not literally the commits sitting on `dev`, even though their content
  is byte-identical to `4e02fed`/`041cf45`) was not corrected in the body text above; it is
  recorded here rather than rewritten throughout, matching the precedent set in the `phase-wb-04`
  audit for cosmetic hash discrepancies.
- Whether the other already-complete `phase-wb-*` records carry the same stale "In progress"
  leading sentence this one and `phase-wb-04`'s did was not checked here — flagged for whoever
  audits the next one.
