---
schema_version: 1
id: doc-session-capture-structuring-routing
code: SESS-2026-09-22-10
title: Capture structuring, evidence scoring and routing
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-capture]
depends_on: [doc-capture-build]
---

# Capture structuring, evidence scoring and routing

## Phase

`phase-cap-05` — Implement structuring, evidence scoring and routing.

## Verification

`uv run pytest test/test_capture_routing.py`

```text
62 passed, 2 warnings
```

`uv run mypy src/`

```text
Success: no issues found in 28 source files
```

## Acceptance

- Stakes-by-evidence matrix — **Met.** `test_each_matrix_cell_produces_the_stated_route` runs 33
  cases: each of the 11 entity types in `routing.STAKES` against explicit, inferred and guessed
  evidence. That covers all four stakes tiers, and each case asserts ADR-007's route.
  `test_an_unresolved_reference_holds_an_otherwise_clean_record` adds 7 cases showing that an
  unknown person, project or tag holds the record.
- Ambiguous capture completes non-interactively and is flagged — **Met.**
  `test_an_ambiguous_inbox_capture_completes_without_prompting_and_is_flagged` puts a vague note
  through `scan_inbox` and then `stage_capture`, with `input()` replaced by a function that fails
  the test and `sys.stdin` set to None. It completes, and the result is one staged record routed
  `flagged`.
- Unknown person creates no person record anywhere — **Met.**
  `test_a_capture_naming_an_unknown_person_creates_no_person_record` compares byte snapshots of a
  temporary data root and of the repository's `_data/` before and after, checks that staging holds
  only the commitment, and checks that the name is kept as written with the route `held`.
- Same fixture through all three channels — **Met.**
  `test_the_same_fixture_through_all_three_channels_routes_identically` captures one text through
  the session writer, the inbox scanner and the CLI's `main()`, then stages the same three
  proposals from each capture. The routes and evidence are identical once each record's own
  `capture_id` is removed.

## Backlog

`status: active`, `agent: agent-builder-b`, `session: doc-session-capture-structuring-routing`.
`next_action`: All acceptance conditions are met on agent/phase-cap-05; waiting for the
owner-approved merge onto dev, after which the completion edit is made.

## Unresolved

- REQ-002 R11: a new tag inside an existing category is held rather than created with an alert,
  as the owner ruled for this phase. The alert-and-create path is left to review and promotion
  (`phase-cap-06`).
- REQ-002's opening paragraph still says only R1, R2 and R5 are implemented. That document is not
  a deliverable of this phase.
