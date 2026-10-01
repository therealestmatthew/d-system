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

Run in the worktree on `dev` `27baa84`, which carries the fix backfilling `000523` onto
`phase-dgov-06`'s `ideas` field, with the phase's commits on top.

```text
$ uv run pytest
PYTEST_RESULT
$ uv run python -m src.governance
GOV_RESULT
$ uv run python tools/check_no_private_content.py
PRIV_RESULT
```

The worktree has no `_private/portfolio/`, so the check above loads 0 identifiers. The changed files,
including `_public/engine/ideas.html` with every idea title, were scanned from the primary checkout
with its identifiers: SCAN_RESULT.

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
names the awaited owner-approved merge.

## Unresolved

- `OPS-028`'s generated text still names R07-R14 (see Decisions).

## Review

Independent review by a fresh `demo-adversary` sub-agent over `8340c90..HEAD` (`b1546be`,
`bc0f502`, `4b585b8`, `847fa61`, `ed8288e`). It ran the verification commands in the worktree and
reported, condition by condition:

1. **REQ-036 R15 — Met.** Both tests pass. The reviewer independently counted 523
   `<tr data-idea=...>` rows in `_public/engine/ideas.html` and a funnel of
   0+493+10+13+7+0+0+0+0=523. The funnel is built from `statuses()`, the full schema enum, so a status
   absent from the data still shows with 0.
2. **REQ-036 R16 — Met.** Both tests pass, and the corpus has 0 `classified` events. On the
   amendment risk: the schema's `amended` event accepts only `title`, `body`, `text`, `target` and
   `target_code`, and `classified` events are replace-only with no retraction shape. The raw-event
   recount and `fold()` therefore cannot disagree under the current schema. The `no axes (<kind>)`
   ruling is implemented and visible on the page.
3. **REQ-036 R07-R13 — Met.** `uv run pytest`: `3 failed, 1274 passed`, the three failures as
   recorded. The reviewer re-ran them in a throwaway worktree at `8340c90` with no branch changes and
   got identical failures and the same 373/372 mismatch, so the pre-existing claim holds. Governance
   OK. The R07-R12 tests pass over both pages. The `ideas.html` stamp `b1546be5bed8` is the parent of
   the regeneration commit, and `4b585b8` changed only the docstring, so the page is not stale.

Containment: `no undeclared changes`. All figures in the record reproduce: 523 ideas, the funnel,
and 385 "no recorded plan" plus 138 "trace page not yet generated".

Findings: no blockers, no majors.

- **Minor/note:** the module docstring still says R07-R14 although the module now implements
  R15/R16. This is deliberate and recorded under Corrections and Left undone. **Accepted.**
- **Note:** the reviewer could not rerun the R13 scan with identifiers, because it was read-only
  and limited to the worktree, so R13 rests on this session's primary-checkout scan (31 identifiers,
  0 hits). **Accepted;** the scan is re-run at merge time.

No discrepancies were found between the record and the reproduced evidence.

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

After the rebase onto `27baa84` the page shows 523 ideas, 0 classified and 523 unclassified. The
funnel reads open 0, triaged 493, reviewing 10, promoted 13, discarded 7, delivered 0, resolved 0,
absorbed 0, set_aside 0. 384 rows read "no recorded plan" and 139 read "trace page not yet
generated". The review saw 385 and 138, on `8340c90`. The difference is `000523`, which the
`dev` fix linked to `phase-dgov-06`.

The first build ran on `dev` `8340c90`, where three tests failed without this branch:
`phase-dgov-06`'s completion named `000523` in its `next_action` but not in its `ideas` field, and the
stage 3 and G2 recounts read 373 against 372. This was reported to the Session Manager. The owner
had the Batch Runner backfill the id on `dev` (`27baa84`), and this branch was rebased onto it.

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

- While `dev` was red, this phase's own `next_action` named idea `000523`, to explain the
  failure. On green `dev` that made `test_repository_idea_field_matches_its_backfill` fail for
  `phase-des-10`, because a backfill re-run would add the id to this phase's `ideas` field. The
  sentence was obsolete, so it was removed rather than the field changed.

- Widening the generator docstring's requirement range to R07-R16 made `OPS-028`, which is generated
  from that docstring, stale, and failed `test_every_paired_document_matches_regenerated_output`.
  `OPS-028` is not a deliverable of this phase, so `4b585b8` restored the range rather than widening
  the phase's paths.

## Left undone

- `OPS-028`'s generated text still names R07-R14. The next phase that declares `OPS-028` can widen
  the range.
- The trace pages are `phase-des-11`'s work.
