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

Run in `/code/d-system-worktrees/phase-sch-05` on `agent/phase-sch-05`, branched from dev `451fdea`.

`uv run pytest`

```
1410 passed, 1 skipped, 1 warning
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 424 documents, 36 memories, 347 backlog phases
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
