---
schema_version: 1
id: doc-session-engine-page-generator
code: SESS-2026-10-01-02
title: Engine page generator and the pipeline overview page
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-html]
depends_on: [doc-html-generation-design-system, doc-engine-pages-house-style-requirements]
---

# Engine page generator and the pipeline overview page

## Phase

`phase-des-09` — Build the engine page generator and the pipeline overview page.

## Verification

`uv run pytest`

```
1246 passed, 1 warning
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 414 documents, 34 memories, 347 backlog phases
```

`uv run ruff check src/ test/`

```
All checks passed!
```

`uv run python tools/check_no_private_content.py` (changes staged at commit time; run again on the
committed branch)

```
check_no_private_content: OK (1114 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so only the path check ran. The content check, which
needs the identifiers, has to run where they exist.

Not in the phase's list, run for the merge gate: `uv run mypy src/` gave
`Success: no issues found in 46 source files`.

Browser check of the committed page (R12), headless Chromium through the Playwright install in the
session scratch directory, at 1280x900:

```
light js true scrollWidth 1280 text 2453
dark js false scrollWidth 1280 text 2453
375 scrollWidth 375
```

The same 2453 characters of text render with JavaScript disabled. There is no horizontal page
scroll at 1280 or 375 pixels. A full-page screenshot was read and matches the house style.

Figures on the committed page (source commit `b45c7c31c9ed`, 2026-10-01): stages 1-9 are 522, 2,
371, 38, not recorded, not recorded, 195, 1, 0. Gates: G1 522, G2 371, G3 38, G4 and G5 1.

## Acceptance

- REQ-036 R07 and R08 (two runs byte-identical, commit stamp, no CI comparison): **Met**.
  `test_two_runs_into_temporary_directories_are_byte_identical`,
  `test_stamp_is_the_source_commit_and_its_own_date` and
  `test_no_ci_step_compares_the_pages_with_a_regeneration` pass. The stamp is the commit date
  (`%cs`), never the wall clock.
- REQ-036 R09, R10, R12 and R13 (no colour literal outside the token CSS, no direct idea-log read,
  full content without script, private check passes staged): **Met** for R09, R10 and R12, by
  `test_no_colour_literal_outside_the_house_token_css`,
  `test_the_generator_reads_the_idea_log_only_through_fold`, `test_pages_contain_no_script` and the
  browser check above. R13 is **Met** for the path check only. The content check skipped for want of
  `_private/portfolio/` in the worktree.
- REQ-036 R11 and R14 (an independent script reproduces every stage count and gate queue):
  **Met**. `test_stage_counts_match_an_independent_recount`,
  `test_gate_queues_match_an_independent_recount` and
  `test_headline_stats_match_an_independent_recount` recompute from the raw files with code that
  shares nothing with the generator's selectors except `fold()`. The G2 recount takes a second
  route, reading phase links from each phase's text through `named_ideas` rather than from the
  `ideas` field the generator reads. Stages 5 and 6 show "not recorded" and name the missing record.
  Stage 4 and G3 are the same set, and the page says so.

## Backlog

`status: active` (the completion edit is made on `dev` after the merge). `next_action`: built and
verified. Waiting on the owner's merge approval, then the completion edit on `dev`.

## Unresolved

R13's content check needs a run with the identifiers present. The Session Manager has run it at the
merge gate for earlier branches.

## Review

Independent review by a `demo-adversary` agent over `dev...HEAD` (commits `1913f26`, `b45c7c3`).
It ran the house, engine and tool-docs tests (54 passed), governance (OK), ruff (clean) and the
private-content check (path check only, 0 identifiers). It regenerated the page at HEAD into a
temporary directory and found it identical to the committed page apart from the stamp, which was
expected because the page had been generated before its own commit. Its findings, as reported:

- **Major — stage 4's count is identical to the G3 gate's.** Both resolve to plans whose front
  matter reads draft, so a plan already reviewed and waiting at G3 cannot be told from one still
  being drafted. "The page is transparent about the duplication ... which keeps this from being a
  blocker, but it is an invented reading beyond what R14 mandates." **Fixed:** the stage-4 row
  says it is the same set as the G3 queue, the page's notes explain that front matter does not
  record where a draft is, OPS-028 says the same, and a new test asserts both the equality and the
  note.
- **Major — the test's "independent recount" of G2 is a verbatim re-derivation of the same
  formula.** "A wrong interpretation ... baked into the generator would be reproduced exactly in
  the test." **Fixed:** the recount now reads phase links from each phase's own text through
  `src.governance.backlog.named_ideas`, not from the `ideas` field, and builds the set by
  subtraction. The test docstring states what is and is not independent.
- **Minor — the G2 fallback path is unreachable on today's data,** since `phase-des-08`'s backfill
  put the field on 100 phases. "No action needed." **Accepted:** the fallback is the owner's
  ruling for the case where the field is absent, and the test keeps it covered.
- **Minor — the scope names batch tables and git history of `dev` as inputs, which this page does
  not read.** "Page 1 needs neither ... not a finding against the diff." **Accepted:** the batch
  graph (`phase-des-12`) and the trace (`phase-des-11`) read them.

It found no discrepancies in determinism, the stamp, the absence of a CI comparison, colour
literals, the fold()-only read, scripts, escaping, scope boundaries, the OPS-028 reservation
removal or prose. Per-condition verdict: R07 and R08 Met. R09, R10 and R12 Met; R13 partially met
(the content check needs a run with identifiers present). R11 and R14 Met, with the two majors
above, both now fixed.

## Decisions

The nine stage counts are this phase's reading of `ARCH-006`. `REQ-036` R14 fixes only the gate
derivations. Each stage counts what sits at it now, and a stage whose work leaves no structured
record shows "not recorded" with the missing record named. Stages 5 and 6 are in that position.
Stage 7 counts queued phases, because a queued phase has had its dependencies mapped and is not
yet claimed. Stage 9 counts ideas with status `delivered`. Stage 4 shares its set with G3, and the
page says so.

The page inlines the committed `house.css` rather than regenerating it, so the page uses exactly
the stylesheet `OPS-027` governs.

The stamp records uncommitted changes to the inputs, because the commit alone would then
misdescribe what was read.

The owner ruled before the claim that G2 falls back to `promoted_to` alone, labelled, if the
backlog `ideas` field is absent. `phase-des-08` merged first, so the live page uses the field and
the fallback is covered by a test.

## Corrections

- Two engine tests failed on their first run because of the tests, not the generator. One searched
  for an apostrophe the page escapes. The other flagged the git-status path list, which names the
  idea log without reading it. Both were tightened.
- The preflight `pytest` ran before any file was created this time (1228 passed), so the
  `phase-des-07` mistake of writing a tool during the preflight run did not recur.

## Left undone

- The ledger, trace and backlog pages (`phase-des-10` to `-12`) extend `PAGES` in the same tool.
- R13's content check with identifiers present, for whoever holds the merge gate.
