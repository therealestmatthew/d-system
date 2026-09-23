---
schema_version: 1
id: doc-session-capture-review-promotion
code: SESS-2026-09-23-02
title: Capture review and promotion into the source of truth
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-capture, sys-portfolio]
depends_on: [doc-capture-build]
---

# Capture review and promotion into the source of truth

## Phase

`phase-cap-06` — Build review and promotion into the source of truth.

## Verification

```
$ uv run pytest test/test_capture_review.py
11 passed, 2 warnings
$ uv run pytest test/test_capture_promotion.py
25 passed, 2 warnings
```

Also run in the worktree, which the phase does not list:

```
$ uv run python -m src.governance
Governance OK: 35 systems, 327 documents, 30 memories, 293 backlog phases
$ uv run pytest -q
907 passed, 1 skipped, 2 warnings
$ uv run ruff check src/capture tools/review.py test/test_capture_promotion.py test/test_capture_review.py
All checks passed!
$ uv run mypy src/capture
Success: no issues found in 6 source files
```

A mutation check: changing bulk promotion to take every route made
`test_bulk_promotion_moves_only_clean_records` fail. Reverting the change made it pass.

## Acceptance

- `Bulk promotion moves only clean records; a mixed batch leaves flagged and held staged.` —
  **Met.** `test_bulk_promotion_moves_only_clean_records` stages one clean, one flagged and one
  held record, runs bulk promotion, and asserts that only the clean one reaches the data root
  and that the other two stay in staging.
- `No capture path other than promotion writes to _data/.` — **Met.** "`_data/`" here means the
  data root: `D_SYSTEM_DATA_ROOT` when set, else `_data/`, per `ADR-009`.
  `test_no_capture_path_other_than_promotion_writes_to_the_data_root` hashes the data root and
  the tags file. It then runs inbox scanning, CLI capture, structuring and review, and asserts
  both are unchanged. Promotion then changes the data root.
- `A correction records the field, the previous value and the new one, and the prior value stays
  readable.` — **Met.**
  `test_a_correction_records_field_previous_and_new_and_keeps_the_prior_value` and
  `test_corrections_append_and_never_rewrite` check the entry and the log. A refused correction
  changes nothing, and the raw capture is untouched.

These verdicts are the author's. The independent review below is still to run.

## Backlog

`status: active`, held by `agent-builder-a`. `next_action`: build done and verified in the
worktree; the independent review runs next, then READY per `GOV-017`.

## Unresolved

- The independent review has not run yet.
- On `dev` at `4634856`, `ruff check src/ test/` reports 16 findings and `mypy src/` reports one
  error, all in files this phase does not touch (`src/broker/`, `src/governance/__main__.py`,
  `test/test_broker.py`, `test/test_governance.py`, `test/test_idea_dispatch.py`). CI runs both.
  Reported to the Session Manager; not fixed here.
