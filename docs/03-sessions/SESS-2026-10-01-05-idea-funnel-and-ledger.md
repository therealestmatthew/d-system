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
depends_on: []
---

# Idea funnel and ledger page

## Phase

`phase-des-10`: build the idea funnel and ledger page. The page goes into the engine generator that
`phase-des-09` built. It lists every idea in `fold()` once, with its status funnel and the four
ARCH-005 axis distributions (REQ-036 R15, R16), and leaves a trace slot for `phase-des-11`. The owner
approved the claim for `agent-standby-3` in session, and the Session Manager granted the claim turn
(claim commit `8bd31ea`). The branch is `agent/phase-des-10`.

## What was built

- `tools/generate_engine_pages.py`: `axis_vocabulary()` reads each axis's values and the record kinds
  that carry no axes from `schemas/idea.schema.json`; `axis_value()`; `ledger_data()`;
  `render_ledger()`; `trace_cell()`, the seam `phase-des-11` replaces; `ideas.html` in `PAGES`; and a
  link from the overview to the ledger.
- `_public/engine/ideas.html`, regenerated together with `index.html`.
- `test/test_engine_pages.py`: R15 and R16 recounts; a fixture-classified record test; the
  no-recorded-plan count; the cross-links; and the R07-R13 checks (stamp, committed-page shape,
  colour literals, house family) extended from the overview to every page.

At the source commit the page shows 523 ideas, 523 ledger rows, 0 classified and 523 unclassified. The
funnel reads open 0, triaged 493, reviewing 10, promoted 13, discarded 7, delivered 0, resolved 0,
absorbed 0, set_aside 0, which sums to 523. 385 rows read "no recorded plan"; 138 have a recorded plan
and read "trace page not yet generated". The page is 184,467 bytes.

## Decisions

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
- The generator docstring's requirement range stays R07-R14. `OPS-028` is generated from that
  docstring and is not a deliverable of this phase; widening the range made `OPS-028` stale and failed
  `test_every_paired_document_matches_regenerated_output` (fixed in `4b585b8`).

## Verification

Run in the worktree on `8340c90` with the phase's commits on top:

```text
$ uv run pytest -q
FAILED test/test_backlog.py::test_repository_idea_field_matches_its_backfill
FAILED test/test_engine_pages.py::test_stage_counts_match_an_independent_recount
FAILED test/test_engine_pages.py::test_gate_queues_match_an_independent_recount
4 failed, 1273 passed, 1 warning in 151.05s
```

The fourth failure (`test_tool_docs`) was this phase's, and `4b585b8` fixed it. The other three fail on
`dev` `8340c90` without this branch, and also fail with this phase's changes stashed:
`phase-dgov-06`'s completion added "idea 000523" to its `next_action` but not to its `ideas` field, so
the text route and the field disagree (stage 3 and G2: 373 against 372). This was reported to the
Session Manager. The fix is outside this phase.

```text
$ uv run python -m src.governance
Governance OK: 43 systems, 415 documents, 34 memories, 347 backlog phases
$ uv run python -m src.governance --containment phase-des-10
phase-des-10: no undeclared changes (dev...agent/phase-des-10)
```

R13: the worktree's `tools/check_no_private_content.py` loaded 0 identifiers, because
`_private/portfolio/` is absent there. The four changed files, including `ideas.html` with every idea
title, were therefore scanned from the primary checkout with its identifiers: 31 identifiers, 0 hits.

## Left undone

- `OPS-028`'s generated text still names R07-R14. The next phase that may edit it can widen the range.
- The trace pages themselves are `phase-des-11`.
