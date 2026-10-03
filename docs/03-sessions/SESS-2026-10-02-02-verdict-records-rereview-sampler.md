---
schema_version: 1
id: doc-session-verdict-records-rereview-sampler
code: SESS-2026-10-02-02
title: Build-review verdict records and the seeded re-review sampler
kind: session
status: active
owner: repository-owner
created: '2026-10-02'
updated: '2026-10-02'
systems: [sys-gov-docs]
depends_on: [doc-reviewer-contract]
---

# Build-review verdict records and the seeded re-review sampler

## Phase

`phase-asr-03` — Build-review verdict records and the seeded re-review sampler.

Assigned by Session Manager to Session 2 - Builder B (agent-builder-b), with the owner's approval in
this session. Claimed on dev at `73bd6ab` inside a granted turn. Work is on `agent/phase-asr-03` in
`../d-system-worktrees/phase-asr-03`.

## Verification

Run in this worktree on `agent/phase-asr-03` rebased onto dev `e4f9496`:

```
$ uv run pytest test/test_review_verdict.py test/test_draw_rereview_sample.py
79 passed, 1 skipped, 1 warning in 0.44s
$ uv run ruff check src/ test/ tools/draw_rereview_sample.py
All checks passed!
$ uv run mypy src/ tools/draw_rereview_sample.py
Success: no issues found in 48 source files
$ uv run python -m src.governance --catalog
421 documents — adr: 23, architecture: 12, governance: 19, operation: 26, plan: 81, prompt: 43, requirement: 35, session: 182.
$ uv run python -m src.governance
Governance OK: 43 systems, 421 documents, 34 memories, 347 backlog phases
$ git diff --exit-code docs/08-governance/catalog.md
(no output, exit 0)
```

The skipped test is `test_committed_verdict_record_is_valid_and_named_by_its_id`, parametrized over
the files in `docs/08-governance/reviews/verdicts/`. No verdict record exists yet, so it has no
cases. It runs on the first committed record.

The four GOV-017 gate checks, same tree:

```
$ uv run ruff check src/ test/
All checks passed!
$ uv run mypy src/
Success: no issues found in 47 source files
$ uv run pytest -q
1387 passed, 1 skipped, 1 warning in 247.16s (0:04:07)
```

The private-content check run in the worktree reads no identifiers (`_private/` is not there). The
new and changed files were checked against the primary checkout's identifiers by calling the tool's
own `confidential_identifiers()` and `check_content()`: `31 identifiers checked, 0 violations`.

A real run against the repository, which holds no verdict records yet:

```
$ uv run python tools/draw_rereview_sample.py --dry-run
No gating verdicts since the last draw; nothing drawn and nothing written.
(exit 0)
```

## Acceptance

- Schema fixtures — **Met.** `test_valid_record_passes`, `test_record_without_model_fails` (the only
  error is `'model' is a required property`) and `test_record_with_an_outcome_appended_passes`, in
  the first run above.
- Sampler fixtures — **Met.** `test_the_same_seed_gives_the_same_sample` (and that 50 seeds give
  more than one sample), `test_a_once_rejected_phase_is_always_in_the_sample` over 20 seeds among
  30 other passes, and `test_the_original_reviewer_type_is_excluded_as_re_reviewer`, in the first
  run above.

## Backlog

`phase-asr-03`: `status: active`, `agent: agent-builder-b`. Not completed here: completion follows
the review, READY and the owner-approved merge (contract item 4).

## Unresolved

- No `docs/08-governance/reviews/verdicts/` or `draws/` directory is committed. Git does not track
  an empty directory. The first verdict record (written under `phase-asr-04`'s wiring) creates the
  first, and the tool creates `draws/` on its first draw.
