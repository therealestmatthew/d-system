---
schema_version: 1
id: doc-session-panel-bridge-batch
code: SESS-2026-10-08-06
title: Extend the panel bridge to batch, multi-target actions (phase-wbf-04)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui]
depends_on: [doc-adr-bookmark-categories-batch-bridge]
---

# Extend the panel bridge to batch, multi-target actions (phase-wbf-04)

## Phase

`phase-wbf-04` (extend the panel bridge to batch, multi-target actions), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Builder B (`agent-builder-b`)
under the Session Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-04`, cut from
the run's integration branch `ccr-b69b05b4-tdcrux`.

## Outcome

`ts/src/stage/panelBridge.ts` now implements section 6 of
[`ADR-029`](../04-decisions/ADR-029-bookmark-categories-and-batch-bridge.md):

- `BridgeSlot` holds several handles keyed by panel-instance key. The key defaults to the channel
  id (`terminal`, `html-viewer`), so `register(handle)` and `unregister(handle)` behave as before
  for `HtmlViewerRegion.tsx`, `TerminalRegion.tsx` and `FileBrowserRegion.tsx`, none of which
  changed. `unregister` finds the entry by handle identity across keys. `get()` returns the most
  recently registered remaining handle and falls back to the previous one. `getAll()` returns an
  array replaced only on register and unregister.
- `ViewerBridgeHandle.openFiles?` is an optional member, so the existing handle literal in
  `HtmlViewerRegion.tsx` type-checks unchanged. `phase-wbf-05` implements it.
- `deliverBatch(paths, targets)` returns `{ requested, targets: [{ channel, key, absent, receipt?,
  error? }] }`. Absent targets are reported, registered ones still receive the list, a throwing
  target is recorded as `failed` without stopping the others, and nothing is queued.
- Additions beyond the ADR's named members: `useTerminalBridges()` and `useViewerBridges()` (hooks
  over `getAll()`, `null` when empty), `isBatchAvailable(targets)` (true when at least one listed
  target is registered), and `callOpenFiles` (the viewer's batch call).

`ts/src/stage/panelBridge.test.tsx` (28 tests, stub handles) proves the keyed-channel rules, the
R07 invariant (delivered plus declined equals requested, each path once) and the R08 absent and
partial cases.

## Acceptance

- REQ-012 R07: met. A batch of N distinct paths yields N entries across `delivered` and `declined`
  per target, including when the target omits a path, reports one twice, throws, or has no batch
  method. No file-passing path exists in `ts/src/stage/` outside `panelBridge.ts`: a grep for
  `openInTab`, `injectPath`, `openFiles`, `postMessage`, `CustomEvent`, `dispatchEvent`,
  `BroadcastChannel` and `window.__` finds only the two single-file context-menu calls in
  `FileBrowserRegion.tsx` (lines 480 and 488, one path each, through the bridge handles) and the
  handle definitions in `HtmlViewerRegion.tsx` and `TerminalRegion.tsx`.
- REQ-012 R08: met. With no target registered every target is `absent`, nothing is delivered, nothing
  throws, and `isBatchAvailable` is false. With some registered, the registered ones receive the
  list and the absent ones are named (best effort per target, as the ADR chose).

## Awaiting ratification

`ADR-029` is proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08). This phase
builds against its recommendation.

## Assumptions

1. `BatchTarget.call` is a function `(handle, paths) => BatchReceipt | undefined`, not a method name.
   The ADR marks the names indicative. A handle that lacks the method (or a `call` that returns
   `undefined`) is reported as `failed` for every path with `error: 'target has no batch method'`,
   not as `absent`, because a handle is registered.
2. Re-registering under an existing key moves that entry to the end, so it becomes the one `get()`
   returns. The ADR says the key replaces the handle and `get()` returns the most recently
   registered; this applies both literally.
3. The bridge normalizes whatever a target returns so the invariant holds even for a faulty handle:
   an omitted, duplicated, or both-delivered-and-declined path is declined `failed`; paths the
   target invented are dropped; an unknown reason becomes `failed`.
4. Duplicate paths in the request are collapsed to one occurrence in each target's call and
   receipt (`requested` keeps the caller's list as given). The ADR does not address duplicates;
   callers are expected to pass distinct paths.
5. `deliverBatch` is typed with a mapped tuple so each target's `call` is checked against its own
   channel's handle type without `any`.

## Evidence

- `cd ts && npm run build`: succeeds (`tsc -b && vite build`, `built in 2.13s`).
- `cd ts && npm test`: `Test Files 4 passed (4)`, `Tests 38 passed (38)`.
- `cd ts && npx eslint . --max-warnings 0`: no output (clean).
- `uv run python -m src.governance`: `Governance OK` (rerun after the catalog regeneration).
- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 50 source files`
- `uv run pytest`: 1 failed, 1661 passed, 1 skipped. The failure is
  `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`: it expects a
  refusal on an unwritable directory and the session runs as root, which ignores directory
  permissions. Not touched by this phase; not re-run to quiet and not skipped.

## Unresolved

Nothing outstanding for this phase. `phase-wbf-05` must implement `openFiles` in
`HtmlViewerRegion.tsx` and register through `deliverBatch`; until then a batch to the viewer reports
every path `failed`.
