---
schema_version: 1
id: doc-session-overview-page-snapshot-stamp
code: SESS-2026-10-04-02
title: Stamp the overview page and test it by content hash
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-delivery, sys-demo-overview]
depends_on: [doc-schema-consistency-testing]
---

# Stamp the overview page and test it by content hash

## Phase

`phase-sch-05` — Add the committed-output drift test for the overview page, re-scoped by owner
ruling of 2026-10-04 to the snapshot model: the page carries a source stamp with a content hash, and
the test checks the hash rather than comparing the page with a fresh run.

## Verification

Run in `/code/d-system-worktrees/phase-sch-05` on `agent/phase-sch-05`, branched from dev `451fdea`,
after the review fixes below.

`uv run pytest`

```
1410 passed, 1 skipped, 1 warning
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 425 documents, 36 memories, 347 backlog phases
```

Behavioural checks for the acceptance conditions, run against the committed page at `d802a5d`:

- Hand edit: replaced the first ` ideas` line ending in `_public/overview/index.html` with
  ` ideas (edited)` and ran
  `uv run pytest test/test_generate_overview.py -k committed_page_is_an_unedited`:
  `1 failed` with `AssertionError: _public/overview/index.html no longer matches its own content hash.
  It is generated; regenerate it with tools/generate_overview.py and do not edit it by hand.`
  Restored with `git checkout`.
- Recorded idea: ran `uv run python tools/append_idea.py add --title "Probe idea (worktree only,
  reverted)" ...` in the worktree (`created 000565`), then the full suite without regenerating the
  page: `3 failed, 1407 passed, 1 skipped`. Every overview test passed. The three failures were
  `test_ideas.py::test_the_committed_markdown_matches_regenerated_output`,
  `test_ideas.py::test_ideas_priority_yaml_is_governance_clean` and
  `test_tool_docs.py::test_every_paired_document_matches_regenerated_output`, the existing couplings
  an idea commit already regenerates for. The probe was reverted with `git checkout`.
- Private content: `tools/check_no_private_content.py` in the worktree checks 0 identifiers because
  `_private/` is absent there. Its `check_content()` was run on the five changed files with the
  primary checkout's identifier set: `identifiers checked: 31; violations: 0`.
- `uv run ruff check src/ test/`: `All checks passed!`; `uv run mypy src/`: `Success: no issues found
  in 47 source files`; `uv run mypy tools/generate_overview.py`: `Success: no issues found in 1
  source file`.

## Acceptance

- REQ-020 R08, as amended, holds: Met — the hand-edit check above fails with the intended message,
  and `test_a_hand_edit_to_the_committed_page_is_detected` asserts the same in the suite.
- Recording an idea or editing backlog.yaml without regenerating the page leaves the suite green:
  Met — the recorded-idea run above failed no overview test. The three failures in that run came from
  the pre-existing ideas.md, priority and tool-docs drift tests, which fail on any idea added without
  the regeneration an idea commit already includes; this phase leaves them unchanged and adds nothing
  an idea commit has to regenerate. No overview test reads backlog.yaml against the page.
- The stamp is the source commit and its own date, never the run time: Met —
  `test_stamp_is_the_source_commit_and_its_own_date`, `test_two_cli_runs_write_byte_identical_files`
  and `test_generation_does_not_depend_on_the_wall_clock` pass.
- The full suite still passes: Met — `1410 passed, 1 skipped`.

## Backlog

`status: active`, `next_action`: built and verified on `agent/phase-sch-05`; awaiting the owner's
merge approval through READY, then the completion edit on dev. `session`, `completion_evidence` and
`result` recorded on the phase line.

## Unresolved

- The stamp names `442c74eef837`, the branch commit the page was generated at. A fast-forward merge
  keeps that commit on dev. A rebase before merge rewrites it, and the page then has to be
  regenerated so the stamp names a commit that exists on dev.

## Review

Independent review by a fresh `demo-adversary` agent over `dev...HEAD` at `b253c0b`. Its findings,
condition by condition:

1. R08 as amended (hand edit fails the test): **Holds.** It hand-edited the committed page, ran the
   test, saw `AssertionError: _public/overview/index.html no longer matches its own content hash...`,
   and restored the page.
2. Recording an idea or editing backlog.yaml leaves the suite green: **Does not hold.** The phase's
   own backlog.yaml edit already broke the suite (finding 1).
3. Stamp is the source commit and its date; two runs byte-identical: **Holds.** The stamp,
   CLI-determinism, wall-clock and generate-determinism tests all pass.
4. Full suite passes: **Does not hold.** `3 failed, 1407 passed, 1 skipped`:
   `test_backlog.py::test_repository_idea_field_matches_its_backfill`,
   `test_engine_pages.py::test_stage_counts_match_an_independent_recount`,
   `test_engine_pages.py::test_gate_queues_match_an_independent_recount`. This contradicted the
   record's `1410 passed`.

Findings:

1. **Blocker.** Commit `b253c0b` rewrote the phase's `next_action` and dropped the only text mention
   of `000106`, while the `ideas:` field still listed it. The backfill check and the engine pages'
   independent G2 recount (`'373' == '374'`) failed. Fix: restore the mention or drop the id from
   `ideas:`, then rerun the suite.
2. **Minor.** REQ-020's "What is genuinely open" item 2 still framed the gap as a missing comparison
   with a regeneration, which the amended R08 rejects, with no pointer between them.
3. **Informational.** The content hash is self-consistency, not tamper-evidence: an edit paired with
   a recomputed SHA-256 patched into the slot passes. Edits inside the stamp, body edits and a second
   injected hash are all caught. This holds against the acceptance wording, which covers an ordinary
   hand edit.
4. **No defect.** `INPUT_PATHS` covers everything the two overview tools read; the stamp follows
   `generate_engine_pages.py`'s pattern; `tools/demo_reset.py` and its tests call the generator only
   through the CLI and do not break; no file outside the declared deliverables changed.
5. **Noted.** The stamped commit `442c74eef837` survives a fast-forward merge but not a rebase; the
   record already discloses this.

Disposition: finding 1 fixed (the `000106` sentence is restored to `next_action`, matching the
`ideas:` field; the full suite reran green, above). Finding 2 fixed (item 2 now points to R08 and the
ruling). Finding 3 accepted: the owner's ruling asked for hand-edit detection, not tamper-evidence,
and a forger who recomputes the hash is outside that. Findings 4 and 5 need no change.

## Decisions

The phase was assigned as a comparison of the committed page with a fresh regeneration, modelled on
`test_ideas.py`. Before claiming, a read-only regeneration showed the committed page 1159 diff lines
out of date (144 ideas and 122 phases committed; 563 and 347 live). Because the page is built from
live counts, that test would have turned dev red on every idea or backlog commit, so the claim was
held and the question went to the owner.

The owner first answered "drop the test" in this session, then confirmed the Session Manager's
relayed ruling instead: treat the page as a stamped snapshot like the engine pages. A second relayed
ruling kept R08's hand-edit detection through a content hash in the stamp and amended R08 rather than
dropping it. The owner chose a `{{SOURCE_STAMP}}` template token, declared under sys-demo-overview
only, so phase-des-11 (sys-html) could run alongside. The page was regenerated after the code
commits so its stamp names a commit with clean inputs.

## Corrections

- The first version put the snapshot note in `tools/generate_overview.py`'s module docstring.
  `OPS-014` mirrors that docstring in a generated block, so `test_tool_docs.py` failed. The note moved
  to a comment beside `INPUT_PATHS` rather than widening the phase to `OPS-014`.
- The pre-review commit rewrote `next_action` without rerunning the full suite and dropped the
  `000106` mention, desyncing the ideas backfill (review finding 1). The record then claimed a suite
  result from before that edit. Fixed and rerun.

## Left undone

Merge onto dev and the completion edit, which wait for the owner's approval. If dev moves before the
merge and the branch is rebased, the overview page must be regenerated so its stamp names a commit
that exists on dev.
