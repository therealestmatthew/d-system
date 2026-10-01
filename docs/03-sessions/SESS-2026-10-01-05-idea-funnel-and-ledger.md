---
schema_version: 1
id: doc-session-idea-funnel-and-ledger
code: SESS-2026-10-01-05
title: Idea funnel and ledger page
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Idea funnel and ledger page

## Phase

`phase-des-10`: build the idea funnel and ledger page.

## Verification

Run in the worktree on `dev` `8340c90` with the phase's commits on top.

```text
$ uv run pytest
FAILED test/test_backlog.py::test_repository_idea_field_matches_its_backfill
FAILED test/test_engine_pages.py::test_stage_counts_match_an_independent_recount
FAILED test/test_engine_pages.py::test_gate_queues_match_an_independent_recount
3 failed, 1274 passed, 1 warning
```

These three fail on `dev` `8340c90` without this branch, and also fail with this phase's changes
stashed. `phase-dgov-06`'s completion commit added "idea 000523" to that phase's `next_action` but
not to its `ideas` field. The text route and the field therefore disagree: stage 3 and G2 read 373
against a recount of 372. The Session Manager has been told; the fix is outside this phase.

```text
$ uv run python -m src.governance
Governance OK: 43 systems, 416 documents, 34 memories, 347 backlog phases
$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (1120 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so the check above loaded 0 identifiers. The changed files,
including `_public/engine/ideas.html` with every idea title, were scanned from the primary checkout
with its identifiers: 31 identifiers, 0 hits.

## Acceptance

- REQ-036 R15 holds — **Met.** `test_ledger_lists_every_folded_idea_exactly_once` and
  `test_funnel_counts_match_a_recount_and_sum_to_the_total` pass. The page shows 523 rows and a
  funnel summing to 523.
- REQ-036 R16 holds — **Met.** `test_unclassified_equals_ideas_with_no_classified_event` passes on
  all four axes, recounted from raw `classified` events: 523 unclassified, 0 classified.
- REQ-036 R07 to R13 still hold with this page added — **Met.** The determinism, stamp,
  committed-page, colour-literal, house-family, fold-only and no-script tests all pass over both
  pages. R13 passes on the primary-checkout scan above.

## Backlog

`phase-des-10`: `status: active`, `session: doc-session-idea-funnel-and-ledger`. Its `next_action`
names the awaited owner-approved merge and the `dev` test drift.

## Unresolved

- The three `dev`-side test failures above block a green four-check gate until `phase-dgov-06`'s
  `ideas` field names `000523`.
- `OPS-028`'s generated text still names R07-R14 (see Decisions).

## Decisions

The owner approved the claim for `agent-standby-3` in session, and the Session Manager granted the
claim turn (claim commit `8bd31ea`). The work was built on `agent/phase-des-10`.

`tools/generate_engine_pages.py` gained these:
- `axis_vocabulary()`, which reads each axis's values and the record kinds that carry no axes from
  `schemas/idea.schema.json`;
- `axis_value()`, `ledger_data()` and `render_ledger()`;
- `trace_cell()`, the seam `phase-des-11` replaces;
- `ideas.html` in `PAGES`, and a link from the overview to the ledger and back.

`test/test_engine_pages.py` recounts R15 and R16 independently. It adds a fixture-classified record
test, the no-recorded-plan count and the cross-links. The R07-R13 checks now cover every page instead
of only the overview.

At the source commit the page shows 523 ideas, 0 classified and 523 unclassified. The funnel reads
open 0, triaged 493, reviewing 10, promoted 13, discarded 7, delivered 0, resolved 0, absorbed 0,
set_aside 0. 385 rows read "no recorded plan" and 138 read "trace page not yet generated".

Owner rulings in this session, 2026-10-01, given through AskUserQuestion:

- A classified collection, fixture or reference record carries no axis values. It counts under
  "no axes (<kind>)" in each axis distribution, and its ledger cell says the same, so the buckets
  still sum to all ideas.
- Each axis distribution lists every value the schema allows, zeros included.
- The overview links to the ledger, and the ledger links back.

Agent's own choices:

- A row with a recorded plan reads "trace page not yet generated". "Recorded plan" means
  `promoted_to`, or a phase `ideas` field naming the idea, which matches `phase-des-11`'s scope.
- The created date is the first ten characters of the folded `created` timestamp, the date as
  recorded.
- The R16 recount reads `classified` events from the raw event list rather than the folded record,
  so it does not share the generator's route.

## Corrections

- Widening the generator docstring's requirement range to R07-R16 made `OPS-028`, which is generated
  from that docstring, stale, and failed `test_every_paired_document_matches_regenerated_output`.
  `OPS-028` is not a deliverable of this phase, so `4b585b8` restored the range rather than widening
  the phase's paths.

## Left undone

- `OPS-028`'s generated text still names R07-R14. The next phase that declares `OPS-028` can widen
  the range.
- The trace pages are `phase-des-11`'s work.
