---
schema_version: 1
id: doc-session-plugin-idea-system
code: SESS-2026-09-25-03
title: Idea-realization plugin idea system — writer, fold, render, priority queue, vocabulary, triage
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-ideas]
depends_on: [doc-idea-realization-plugin-idea-system]
---

# Idea-realization plugin idea system — writer, fold, render, priority queue, vocabulary, triage

## Phase

`phase-plug-02` — The idea system — writer, fold, render, priority queue, vocabulary, triage.

## Verification

Run in `../d-system-worktrees/phase-plug-02` on `agent/phase-plug-02`, rebased onto `dev` at
`dccf952`.

```text
$ cd plugins/idea-realization && uv run pytest
177 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (955 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 362 documents, 32 memories, 318 backlog phases
```

The worktree has no `_private/portfolio/`, so the tool's content check skipped. The same check
function (`confidential_identifiers` and `check_content` from `tools/check_no_private_content.py`),
run from the primary checkout against every file under `plugins/idea-realization/` in this branch,
reported: `31 identifiers checked over 40 plugin files; 0 problems`.

The acceptance-evidence tests, selected by name from the suite above:

```text
$ uv run pytest -q -k "promotion_must_name or promotion_without_promoted_to_is_refused_by_the_cli or second_discard_after_a_revisit or no_help_text_offers or twice_over_a_fixture or hand_edit_to_the_view or vocabulary or queue_naming or queue_dated or valid_priority_queue or triage_agent_cannot or triage_runs_no_link or source_references or schema_enums_equal or fold_matches_the_source"
35 passed, 142 deselected
```

## Acceptance

- The ported transition tests pass through the plugin's script; an open -> promoted without a
  pointer is refused; a second discard after the one revisit is refused; --help shows no time
  option — **Met.** `test_ideas.py` carries the ported writer tests (177 pass).
  `test_promotion_must_name_what_the_idea_became` and
  `test_promotion_without_promoted_to_is_refused_by_the_cli` (exit 1, nothing appended);
  `test_a_second_discard_after_a_revisit_is_permanent`; `test_no_help_text_offers_a_time_option`
  over the top-level help and all eleven subcommands. Reading of the second condition: the schema
  permits `reviewing -> discarded` after the revisit, so the discard itself is accepted and every
  later move — a further revisit, `reviewing`, another discard — is refused as permanent.
- render twice over a fixture log diffs to nothing; an edited rendered file fails check — **Met.**
  `test_rendering_twice_over_a_fixture_log_is_byte_identical`;
  `test_a_hand_edit_to_the_view_is_reported` (check names the view, `render_ideas.py --check`
  exits 1).
- The vocabulary test passes and fails on a fixture document missing one status — **Met.**
  `test_the_vocabulary_matches_the_schema`; `test_a_document_missing_one_status_fails` returns
  exactly `Statuses: absorbed is in the schema but not the document`.
- A fixture priority queue naming a promoted idea fails check naming the id — **Met.**
  `test_a_queue_naming_a_promoted_idea_fails_the_check`, with the unknown-idea, future-date and
  schema-invalid fixtures failing and a valid queue passing (REQ-031 R11).
- The idea-triage agent's tools exclude Edit and Write; the R02 check passes — **Met.**
  `test_the_triage_agent_cannot_edit_or_write_files` (tools `Read, Grep, Glob, Bash`);
  `test_triage_runs_no_link_or_promotion_command`; `test_no_source_references.py` passes over the
  whole plugin tree.

R23 (the schema's enums equal this repository's at the commit `phase-idg-01` landed):
`test_the_schema_enums_equal_the_source_schema`, with the source sets written into the test as
literals by owner ruling, since R21 bars the suite from reading this repository.
PLAN-048.02's fold-equality rule: `test_the_fold_matches_the_source_fold_on_a_fixture_log`; the
literal expected state was checked against `src.db.ideas.fold` on the same fixture before it was
committed (`source fold equals expected: True`).

## Backlog

`phase-plug-02`: `status: active`, `agent: agent-standby-builder`. `next_action`: every acceptance
condition met and the independent review recorded; waits for the owner's merge approval, relayed
by the Session Manager, then completion on `dev`. `session`, `completion_evidence` and `result`
recorded as interim evidence.

## Unresolved

- The merge onto `dev` and the completion edit wait for the owner's approval (contract item 4).
- The repository's own test suite, ruff and mypy are run after the final rebase, for READY, not
  here.
