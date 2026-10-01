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
1245 passed, 1 warning
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

Figures on the committed page (source commit `2666f3c38005`, 2026-10-01): stages 1-9 are 522, 2,
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
  shares nothing with the generator's selectors except `fold()`. Stages 5 and 6 show
  "not recorded" and name the missing record.

## Backlog

`status: active` (the completion edit is made on `dev` after the merge). `next_action`: built and
verified. Waiting on the owner's merge approval, then the completion edit on `dev`.

## Unresolved

R13's content check needs a run with the identifiers present. The Session Manager has run it at the
merge gate for earlier branches.
