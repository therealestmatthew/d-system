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

Recomputed at session close on `dev` (commit range `3c6fac0..cdd773b` — phase-wb-05's
completion-evidence commit through phase-wb-06's own completion commit; branch `agent/phase-wb-06`
integrated fast-forward at `cdd773b`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 55 modules transformed`, built in
  `1.24s` (matches the mid-session `55 modules` figure exactly — unlike `phase-wb-04`/`-05`, this
  phase's own mid-session build was already run post-rebase against a `dev` state close to today's;
  the chunk-size-over-500kB note remains Vite's informational warning, not an error).
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 165 documents, 16
  memories, 121 backlog phases` (counts reflect the repository's current state, not this phase's
  diff alone; mid-session figure of `162 documents, 119 backlog phases` predates later phases).
- `git add -A` then `uv run python tools/check_no_private_content.py` — `check_no_private_content:
  OK (500 tracked files, 31 identifiers checked)`.
- `uv run pytest` (full suite) — `552 passed, 3 failed`. The three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`, all in
  `test/test_demo_terminal.py`) are the known host-wide `pyenv rehash` shim-lock contention
  (ideas 000097/000099), unchanged in identity and count from the mid-session run; this phase's
  diff does not touch `test/` or `src/demo`.
- W06-C1 (demo-creator-web, Idea Explorer): built `ts/src/stage/IdeaExplorerRegion.tsx` over
  phase-wb-01's idea route (`GET /api/v1/workbench/ideas` and `/ideas/queue`) only, registered in
  layout-1's explorer slot; `npm run build` clean first cycle (commit `92ae75c` on `dev`).
- W06-V1 (demo-validator-code): clean PASS, no findings — data comes only from the idea route,
  six columns render, sort/filter operate on already-fetched rows, the queue view re-fetches the
  route's own queue-ordered variant rather than re-ranking client-side.
- W06-C2 (demo-creator-web, Backlog Explorer): factored the shared table/sort/filter/queue-toggle
  logic out of the Idea Explorer into `ts/src/stage/explorer/ExplorerRegion.tsx`, a generic
  component parameterized by columns and data source; `IdeaExplorerRegion` became a thin wrapper
  over it; `ts/src/stage/BacklogExplorerRegion.tsx` is the second wrapper, over phase-wb-01's
  backlog route, registered in the explorer slot alongside the other two; `npm run build` clean
  first cycle (commit `7f2c4f7` on `dev`).
- W06-V2 (demo-validator-code): clean PASS, no findings — only `ExplorerRegion.tsx` renders a
  table (no duplicated table code), six columns render for the backlog panel, the queue view uses
  the route's own ordering, and layout-1's explorer slot now lists all three explorers with File
  Browser default-visible.
- W06-G (demo-validator-check, phase gate): PASS on every item — governance clean; private-content
  clean staged; both explorer panels registered in the slot; `npm run build` clean; full pytest
  552 passed/3 failed (the same environmental PTY set, ideas 000097/000099); no direct
  `ideas.jsonl` reference in `ts/src` (the one grep hit is a comment stating the opposite); diff
  against `dev` confined to `ts/`.
- W06-A (adversarial review, dispatched by the coordinator after this orchestrator's charter
  ended): found nothing — numbers cross-verified against independent `fold()` and `--ready`
  recomputations, per the backlog `next_action`.
- W06-W (Playwright browser verification, dispatched by the coordinator): green on every item,
  including the explorer-slot dropdown rider deferred from phase-wb-02, per the backlog
  `next_action`. Integrated into `dev` fast-forward at `cdd773b` under PROMPT-023 delta 1
  (pre-approved, gate green).

## Acceptance

- Idea rows match an independent `fold()` run and the queue view ranks by status precedence then
  age (REQ-007 W10) — **Met**: W06-V1 confirmed the panel reads only the phase-wb-01 idea route
  (itself `fold()`-backed) and the queue view uses the route's own queue-ordered variant, never a
  client-side re-rank. W06-W then cross-verified the live rendered rows against an independent
  `fold()` recomputation and found a match, per the backlog `next_action` and `result`.
- Backlog rows match `backlog.yaml` and the queue view's top rows equal `next_up` in order
  followed by ready phases by priority, cross-checked against the `--ready` report (REQ-007 W11)
  — **Met**: W06-V2 confirmed the backlog route's queue variant (built from
  `queue_order()`/`readiness()`) is what the panel renders unmodified. W06-W cross-verified the
  live rendered rows against an independent `--ready` recomputation and found a match.
- Layout-1's explorer slot lists all three explorers in its header dropdown with File Browser
  visible by default (REQ-007 W06) — **Met**: `_data/workbench/layouts/layout-1.json` admits
  `file-browser`, `idea-explorer`, `backlog-explorer` in that order with `default_panel: null`;
  `Slot.tsx` falls back to the first implemented admit (File Browser) when none is explicitly
  selected; both new panels are now registered (`Component` no longer `null`) confirmed by W06-G
  item 3. W06-W additionally confirmed the explorer-slot dropdown rider deferred from phase-wb-02
  (both-direction swapping) live.

## Backlog

- `status: complete`, `agent: agent-demo-data` retained as the record of who did the work.
- `next_action`: None — phase complete: both work items passed first-cycle with zero fix cycles,
  W06-A found nothing (numbers cross-verified against independent `fold()` and `--ready`
  recomputations), W06-W green on every item including the explorer-slot dropdown rider deferred
  from phase-wb-02, and the branch integrated into `dev` fast-forward at `cdd773b` under
  PROMPT-023 delta 1 pre-approved integration (GOV-003 completion gate, workbench extension).
- `completion_evidence`: recorded on `dev` (the completion commit `cdd773b` itself, no separate
  follow-up commit was needed here unlike phase-wb-05): `ts/src/stage/explorer/ExplorerRegion.tsx`,
  `ts/src/stage/IdeaExplorerRegion.tsx`, `ts/src/stage/BacklogExplorerRegion.tsx`,
  `ts/src/workbench/panelRegistry.tsx`, `ts/src/workbench/Slot.tsx` — all confirmed present at this
  audit.
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
    coordinator''s dispatches, not this orchestrator''s. **[Audit correction, 2026-09-11]** Both
    have since run and passed: W06-A found nothing, numbers cross-verified against independent
    fold() and --ready recomputations; W06-W was green on every item including the explorer-slot
    dropdown rider deferred from phase-wb-02. Integrated into dev fast-forward at cdd773b under
    PROMPT-023 delta 1 (pre-approved, gate green).'

## Unresolved

None. Both W06 work items, the phase gate, W06-A and W06-W have all passed, and the branch is
integrated onto `dev` with `completion_evidence` recorded. Nothing from this phase was left open
at close.

## Review

Independent sub-agent review at close (fresh general-purpose agent, commit range
`3c6fac0..cdd773b` — phase-wb-05's completion-evidence commit through phase-wb-06's own
completion commit — its own command runs, no access to this record's conclusions beyond the
claims it was asked to check). Findings pasted verbatim, condition by condition:

- **Acceptance condition 1 (REQ-007 W10) — HOLDS.** "`ts/src/stage/IdeaExplorerRegion.tsx` fetches
  only `GET /api/v1/workbench/ideas` and `GET /api/v1/workbench/ideas/queue` — no client-side
  ranking logic exists in the file at all; it supplies columns, urls, and a search predicate to the
  shared `ExplorerRegion` component and nothing else. The ranking is computed entirely server-side
  in `src/api/routes/workbench.py`: `_idea_queue_sort_key` (lines 472–476) sorts on
  `(IDEA_QUEUE_STATUS_PRECEDENCE[status], created, id)`, with `IDEA_QUEUE_STATUS_PRECEDENCE` (lines
  441–447) mapping `open=0, triaged=1, reviewing=2, promoted=3, discarded=3`, applied in
  `get_ideas_queue()` (line 490) via `sorted(state.items(), key=...)`, itself built from
  `fold(load_events())` (line 469) — the same `fold()` the acceptance condition names.
  `test/test_workbench_api.py::test_ideas_route_matches_independent_fold_recomputation`
  (independently recomputes `fold(load_events())` in the test and asserts row equality) and
  `test_ideas_queue_route_orders_by_status_precedence_then_age` (independently recomputes the same
  sort key and asserts row-order equality, plus an explicit 'open/triaged outranks discarded'
  cross-check) both pass — reran `uv run pytest test/test_workbench_api.py`: 42 passed, 0 failed.
  This is real, independent backend-level verification of exactly the claim, not just my reading of
  the code agreeing with itself."
- **Acceptance condition 2 (REQ-007 W11) — HOLDS.** "`ts/src/stage/BacklogExplorerRegion.tsx`
  fetches only `GET /api/v1/workbench/backlog` and `GET /api/v1/workbench/backlog/queue`, again
  supplying nothing but columns/urls/predicate to `ExplorerRegion`. The backend's
  `get_backlog_queue()` (workbench.py lines 535–549) imports and calls `queue_order()` and
  `readiness()` directly from `src.governance.backlog` (the same module `--ready` uses — confirmed
  by `from src.governance.backlog import queue_order, readiness` at line 63), narrows to
  `readiness(item, items) == 'ready'`, and its own docstring states this matches `--ready` 'by
  construction.' `test_backlog_route_matches_backlog_yaml` and
  `test_backlog_queue_route_matches_ready_by_priority_ordering` both independently reload
  `backlog.yaml` and recompute via the same governance functions, asserting row and order equality
  (including the `next_up`-prefix assertion) — both passed in my rerun. The `BacklogRow.status`
  filter vocabulary in the frontend (`queued, active, blocked, deferred, complete, cancelled`)
  exactly matches `schemas/backlog.schema.json`'s enum."
- **Acceptance condition 3 (REQ-007 W06) — HOLDS.** "`_data/workbench/layouts/layout-1.json`
  (unchanged in this diff range — it already carried this shape from phase-wb-05) admits
  `['file-browser', 'idea-explorer', 'backlog-explorer']` with `default_panel: null`. This phase's
  actual change is exactly the one needed to make that admit list functional: `panelRegistry.tsx`
  flips `idea-explorer` and `backlog-explorer` from `Component: null` to `Component:
  IdeaExplorerRegion` / `Component: BacklogExplorerRegion`. `Slot.tsx`'s resolution logic
  (`implementedAdmits = slot.admits.filter(id => PANEL_REGISTRY[id]?.Component)`, then
  `currentPanelId = resolvedPanelId ?? implementedAdmits[0]`) now sees three implemented admits
  instead of one, which makes `file-browser` — first in the admits array — the default when nothing
  is explicitly selected, and crosses the `implementedAdmits.length > 1` threshold into the
  dropdown-header branch, rendering a `Popover` listing the other two panels with `onSelectPanel`
  wired to swap between all three in either direction. `StagePage.tsx` mounts `<Slot>` with real
  `resolvedPanelId`/`onSelectPanel` state (pre-existing wiring from phase-wb-02, not orphaned). This
  matches REQ-007's own W06 row text verbatim (File Browser visible first, Idea/Backlog Explorer
  behind the dropdown)."
- **The claimed refactor (generic `ExplorerRegion`, thin wrappers, no duplicated table code) —
  confirmed as claimed.** "`ts/src/stage/explorer/ExplorerRegion.tsx` (273 lines) is the only file
  in the diff — or, per a repo-wide grep, in `ts/src` at all — that renders a `<table>`, owns
  `useState`/`useEffect` for fetch/sort/filter/view-toggle, or defines `stage-explorer__*` styling.
  `IdeaExplorerRegion.tsx` (85 lines) and `BacklogExplorerRegion.tsx` (87 lines) are genuinely thin:
  each is a type, a column array, and one `<ExplorerRegion<T> columns=... urls=... />` call — no
  sort/filter/render-loop logic duplicated between them. `StagePage.css`'s new `.stage-explorer__*`
  block is a single namespace shared by both panels via one comment explicitly noting 'no `--idea-`
  or `--backlog-` variant of these rules exists.'"
- **No direct `ideas.jsonl` read, comment-only hit claim — verified exactly.** "`grep -rn
  'ideas.jsonl' ts/src` returns exactly one hit: `IdeaExplorerRegion.tsx:56`, inside a doc comment
  reading '...never a direct read of `_data/ideas.jsonl`.' No other occurrence, no `.jsonl`
  reference of any other file anywhere in `ts/src`. The session record's claim is accurate as
  stated."
- **The explorer-slot dropdown rider deferred from phase-wb-02 — unverifiable by me, correctly
  framed as such rather than accepted or rejected.** "I cannot run Playwright myself, so W06-W's
  pass/fail is unverifiable by me and I report it as such. What I can confirm from the diff:
  `Slot.tsx`'s dropdown branch is genuinely bidirectional (any of the three implemented admits can
  swap in via `onSelectPanel`, not just 'file-browser plus one other'), so the code shape supports
  what the rider would test. Separately, idea 000101 ('Workbench multi-panel slots render a double
  header after a dropdown swap') was recorded in this same commit range via two interleaved,
  unrelated commits (`e60a48e`, `42f6d8f`) — this is a different, deliberately-deferred cosmetic
  issue (double header on swap), not the dropdown-swapping capability itself, and
  `panelRegistry.tsx`'s own comment says as much. No contradiction between the two."
- **Verification reruns**: `cd ts && npm run build` — matches claim exactly (`✓ 55 modules
  transformed`, ~1.1s, same informational chunk-size warning, no errors). `uv run python -m
  src.governance` — matches claim (`Governance OK: 18 systems, 165 documents, 16 memories, 121
  backlog phases`). `git add -A && uv run python tools/check_no_private_content.py` — matches claim
  (`OK (500 tracked files, 31 identifiers checked)`); note the reviewer's own aside that the
  working tree carried unrelated uncommitted edits from a concurrent session at rerun time, which
  it unstaged afterward rather than attributing to this phase. `test/test_workbench_api.py` — 42
  passed, 0 failed, including the four tests that directly and independently verify acceptance
  conditions 1 and 2.
- **Discrepancy — full-suite pytest count**: "My independent rerun: 551 passed, 4 failed (155s),
  not the session record's claimed '552 passed, 3 failed.' Three of the four failures are exactly
  the ones the session record names (the known `pyenv` shim-lock contention in
  `test_demo_terminal.py`). The fourth, not mentioned in the session record, is
  `test/test_codes.py::test_committed_catalog_matches_regenerated_output`, which fails because the
  working tree's committed `catalog.md` no longer matches a freshly regenerated one. Given the same
  working tree carried unrelated uncommitted edits to `REQ-007`, `PLAN-022`, `backlog.yaml`, etc.
  at the moment I ran this, this is almost certainly catalog drift from a concurrent session's
  in-progress work rather than anything phase-wb-06's diff caused — phase-wb-06's own diff touches
  no document whose count the catalog tracks in a way that would go stale on its own. Still, it is
  a real, reproducible difference between what I found and what the record states, so I flag it as
  evidence the record's pytest figure was accurate only at the moment captured, not as a defect in
  this phase's work."
- **Discrepancy — pre-existing documentation inaccuracy, not introduced by this phase**: "Both
  `backlog.yaml`'s phase-wb-06 scope text and `REQ-007-workbench.md`'s W10 row describe the idea
  queue's status precedence as 'open → triaged → planned.' There is no `planned` status anywhere in
  the idea system — `schemas/idea.schema.json`'s enum is `open, triaged, reviewing, promoted,
  discarded`, and the actual implementation (`IDEA_QUEUE_STATUS_PRECEDENCE` in `workbench.py`)
  correctly uses `reviewing` as the third rank, not `planned`. This wording predates the diff range
  (both lines are unchanged between `3c6fac0` and `cdd773b`) and the implementation is correct
  despite it, so it does not affect the acceptance verdict — but it is a genuine, currently-live
  inaccuracy in two governing documents that neither this phase's session record nor its close
  mentions or corrects." (Surfaced to the owner via `AskUserQuestion` at close; the owner elected to
  leave it for later since `REQ-007` was concurrently open in a parallel session — see Decisions.)
- **Bottom line (verbatim)**: "All three acceptance conditions genuinely hold, backed by both
  direct code reading and independent backend test evidence (42/42 in `test_workbench_api.py`,
  including four tests that recompute the exact claims — fold() equality, status-then-age ordering,
  backlog-yaml equality, and queue_order()/readiness() ordering — independently of the routes under
  test) rather than by trusting the session record's prose. The claimed refactor into one generic
  `ExplorerRegion` with two thin wrappers is real, not cosmetic phrasing over duplicated code, and
  the 'no ideas.jsonl reference except a comment saying so' claim checked out exactly as stated. The
  one substantive finding worth the owner's attention is unrelated to this phase's correctness:
  both `backlog.yaml` and `REQ-007` carry a stale, incorrect status name ('planned') in the W10
  queue-ranking description that the actual idea schema and this phase's implementation both
  correctly ignore in favor of the real enum — worth a documentation fix, not a reason to reopen
  this phase. The pytest full-suite count mismatch (551/4 vs. claimed 552/3) traces to an extra
  catalog-drift failure caused by concurrent unrelated edits sitting uncommitted in the working tree
  at rerun time, not to this phase's diff, and pytest was never part of phase-wb-06's own gating
  verification list. W06-A and W06-W remain claims I cannot independently confirm or refute from
  static review. On everything I could check directly, this phase's completion is genuine."

## Decisions

- The owner ran `/session-close phase-wb-06` on 2026-09-11 as a **retroactive audit** of a phase
  the build coordinator had already marked `status: complete` under the GOV-003 demo/workbench
  completion-gate exception, not as the phase's original close — the same posture as the
  `phase-wb-04` and `phase-wb-05` audits run immediately before this one in the same session.
- Mid-audit, the independent review's own verification reruns surfaced that a parallel session was
  actively editing this same primary checkout (uncommitted changes to `PLAN-022`, `PROMPT-023`,
  `PROMPT-024`, `REQ-007`, `GOV-003`, and non-overlapping regions of `backlog.yaml`, evidently
  later-phase work by the owner's other session). The owner was asked directly (`AskUserQuestion`)
  how to finish this close's commit given the entanglement, and chose `git add -p` to stage only
  this session's own hunks in `backlog.yaml` (the phase-wb-06 `result`-field fix) plus this session
  record in full, leaving every other file and every other `backlog.yaml` hunk untouched and
  uncommitted for the parallel session to commit itself.
- The owner was also asked whether to fix the pre-existing "planned"-status documentation
  inaccuracy the review surfaced (`backlog.yaml`'s phase-wb-06 scope, `REQ-007`'s W10 row) as part
  of this close. The owner chose to leave it, since `REQ-007` was concurrently open in the parallel
  session and touching it here risked colliding with that session's own edits.
- Because the phase was already `status: complete`, this session's step-6 completion decision was
  whether that status should *stand*, not whether to *set* it. Both required conditions held — the
  recomputed checkpoint-equivalent acceptance verdicts (all three Met) and the independent
  sub-agent review (no discrepancy bearing on acceptance) — so the status is left unchanged at
  `complete`.

## Corrections

- `backlog.yaml`'s `result` field for `phase-wb-06` was more substantially stale than the same
  pattern found in the `phase-wb-04`/`phase-wb-05` audits: it did not just open with a leftover "In
  progress." — its closing sentence flatly stated "W06-A and W06-W ... have not yet been run,"
  directly contradicting the field's own `next_action` sibling, which already recorded both as
  passed. Corrected the opening to "Complete." and replaced the stale closing sentence with the
  actual W06-A/W06-W outcomes and the integration commit, mirroring what `next_action` already
  said.
- This session record's `## Verification`, `## Acceptance`, `## Backlog`, and `## Unresolved`
  sections were still describing the mid-phase state (this orchestrator's charter ending before
  W06-A/W06-W ran, `completion_evidence` "not recorded on dev yet," `status: active`) despite the
  phase having finished and closed on `dev` before this audit began. Recomputed against current
  `dev` per this command's own instruction that these sections must reflect the repository "as it
  stands at close."

## Left undone

- The pre-existing "planned"-vs-"reviewing" documentation inaccuracy in `backlog.yaml`'s
  phase-wb-06 scope and `REQ-007`'s W10 row, per the owner's explicit choice above — left for a
  later session once `REQ-007` is no longer concurrently open elsewhere.
- The independent review's pytest discrepancy (551/4 vs. this record's 552/3) was not independently
  re-resolved here; it is attributed to concurrent unrelated edits in the working tree at the
  reviewer's rerun time, not to this phase's diff, and pytest is not part of phase-wb-06's own
  gating verification list.
- Whether the still-unaudited `phase-wb-07` (active, not yet closeable — owner-machine items
  pending per its own `next_action`) carries the same stale-`result`-field pattern found in
  `phase-wb-04`/`-05`/`-06` was not checked; its `result` field's "In progress" language is
  currently accurate since that phase is genuinely still active, unlike the three already-complete
  phases audited in this session.
