---
schema_version: 1
id: doc-session-bookmark-category-decision
code: SESS-2026-10-08-01
title: Decide the bookmark category storage, reference and batch-bridge model (phase-wbf-03)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui, sys-contracts]
depends_on: [doc-adr-bookmark-categories-batch-bridge]
---

# Decide the bookmark category storage, reference and batch-bridge model (phase-wbf-03)

## Phase

`phase-wbf-03` (decide the bookmark category storage, reference and batch-bridge model), group
`G49` of [`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Builder B
(`agent-builder-b`) under the Session Manager's pre-approved run of 2026-10-08. Branch
`agent/phase-wbf-03`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`.

## Outcome

One decision record, [`ADR-029`](../04-decisions/ADR-029-bookmark-categories-and-batch-bridge.md),
covering `000111` (file bookmark categories) and `000120` (extend the panel bridge to batch,
multi-target actions). Nothing was built. The record's recommendation:

- **Storage:** one JSON file per category under the data root, `<data root>/workbench/bookmarks/`.
  Private with `D_SYSTEM_DATA_ROOT` set, tracked fictional examples with it unset. Browser storage
  and an always-tracked directory are argued against.
- **Reference:** an immutable slug `category_id`; rename changes the display name only; the server
  resolves entries to `present`, `missing` or `excluded`.
- **Path validity:** repository-relative forward-slash paths, validated on write by the existing
  rule, never auto-pruned.
- **Write surface:** six routes under the `ADR-015` gate, the first write routes in the workbench
  API.
- **Consuming surfaces:** File Browser and HTML Viewer in `wbf-05`; terminal injection dropdowns and
  the rotator image source (`000132`) admitted by the contract and deferred.
- **Batch bridge:** keyed multi-handle `BridgeSlot`, per-target batch method returning a receipt
  (every path delivered or declined), one `deliverBatch` entry point with explicit targets,
  best-effort partial delivery, no queueing, no throwing.

## Status of the decision

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** The ADR front matter
is `status: draft`. `phase-wbf-04` and `phase-wbf-05` build against it.

## Evidence

- `uv run python -m src.governance`: `Governance OK: 45 systems, 457 documents, 37 memories, 347
  backlog phases`, exit 0, after the catalog was regenerated. Before regeneration it reported the
  catalog differing from the rendered one, as expected.
- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 50 source files`
- `uv run pytest`: 5 failed, 1649 passed, 1 skipped. The five failures are environmental and
  unrelated to a documentation change: the worktree's repository is shallow
  (`git rev-parse --is-shallow-repository` prints `true`), so
  `test_repository_history_reports_the_known_phase_prog_cases`,
  `test_a_known_idea_traces_to_the_git_log_and_the_fold`, and the two
  `test_idea_classification.py` tests cannot read commits such as `0f142ce` (`git show` exit 128);
  and `test_an_unwritable_worktree_parent_is_refused` did not raise because the session runs as
  root (uid 0), which ignores directory permissions. Not re-run to quiet, not skipped.
- `cd ts && npm test`: not run. `ts/node_modules` is absent (`vitest: not found`) and this phase
  touched nothing under `ts/`.

## Assumptions

1. "Data root" for categories means `data_root()` in `src/db/source_validation.py`, the same
   resolution entities use. No other reading was found, but the workbench routes do not call it
   today.
2. Entries are files only, not directories. `000111` says "files".
3. The HTML Viewer's set-open policy (fill empty tabs, then add up to the cap, never replace a tab
   holding a page) is a recommendation. Neither `000111` nor `000120` states one.
4. Display names are unique case-insensitively and category ids are not reserved after deletion.
   Neither is in the source ideas.
5. Method and type names in the batch contract are indicative; the properties are binding.

## Awaiting ratification

The six items under "Open items for the owner" in the ADR: storage location (departs from
`000111`'s leaning toward tracked), the first write routes, `wbf-05` scope, viewer placement
policy, partial-target behavior, and no rename tracking or auto-prune.

## Unresolved

- `phase-wbf-05`'s entry lists `ts/src/stage/` as its only deliverable but declares `sys-api` and
  verifies with `uv run pytest`. The routes, schema, example category and tests fall outside that
  deliverable. Not edited here; the entry needs widening before it is claimed.
- A category of more than four viewer-compatible files cannot fully open in the HTML Viewer while
  its tab cap is four.
