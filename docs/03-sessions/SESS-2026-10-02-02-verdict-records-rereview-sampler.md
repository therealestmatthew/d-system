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

Run in this worktree on `agent/phase-asr-03` rebased onto dev `e4f9496`. The phase-test count is from
after the review fixes (`b730755`); the full suite ran before them, and the post-rebase gate run sent
with READY is the final one:

```
$ uv run pytest test/test_review_verdict.py test/test_draw_rereview_sample.py
81 passed, 1 skipped, 1 warning in 0.46s
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

## Review

`demo-adversary`, dispatched fresh (not a fork) with the phase's scope, acceptance and verification,
the owner's four rulings, the range `dev...agent/phase-asr-03` and this record as claims to verify.
It re-ran every verification command and the full suite itself (`1387 passed, 1 skipped`).

First pass, at `6717154`, **verdict: reject**:

- Acceptance 1 (schema fixtures) — **Met.** "`test_valid_record_passes`, `test_record_without_model_fails`
  (asserts the single error is exactly `'model' is a required property`),
  `test_record_with_an_outcome_appended_passes` all pass."
- Acceptance 2 (sampler fixtures) — **Met.** It traced each of the four owner rulings to the code:
  `unconsidered()` for draws, the gating-only dict in `rejected_before()`, the excluded set built over
  all verdicts, and `math.ceil(len(rest) / RATE)`.
- **F01 (major)** — "the verdict record's `finding` definition structurally forbids the `consequence`
  field the coordinator must transcribe unchanged." With `additionalProperties: false` and no
  `consequence` property, a finding carrying one failed with "Additional properties are not allowed
  ('consequence' was unexpected)", against D4's "without changing a finding" and the phase's
  `next_action` to model the schema on `adversarial-finding.schema.json`. Minimal fix named: add
  `consequence`.
- **F02 (minor)** — "the draw record's `considered` and `sample[].verdict_id` fields accept any
  non-empty string, not the `verdict_id` pattern."
- "No other discrepancies survived attack."

Both fixed in `b730755`. F01: `consequence` added as optional, not required, because not every
reviewer type states one and a required field would make the coordinator invent text. F02: a shared
`definitions/verdict_id`, referenced by the root id, `considered`, `sample[].verdict_id` and
`outcome.verdict_id`. Two tests added.

Re-review of `b730755`, **verdict: pass**:

- "F01 — resolved." It validated a finding with, without, and with an empty `consequence`
  (errors `[]`, `[]`, `["'' should be non-empty"]`) and judged optional sufficient: "R05 does not
  mandate that every finding carry a consequence, only that the record format not discard one the
  reviewer wrote."
- "F02 — resolved." Non-id strings in all four fields are rejected by the pattern.
- Regression: `81 passed, 1 skipped`; ruff, mypy, governance and the catalog diff clean; the
  sampler's fixture ids still match the pattern.
- "New findings: None."

## Decisions

- **The owner ruled four points this session (2026-10-02)** that the plan text left open. Each draw
  is recorded as a file under `docs/08-governance/reviews/draws/`. Only gating verdicts are sampled,
  so a "rejection before pass" is a gating reject. The types excluded from re-reviewing a phase are
  every type with a verdict on it, gating or shadow. One in ten is rounded up. All four are in
  `OPS-030` and have tests.
- **"Since the last draw" means verdicts no earlier draw lists in `considered`**, not a date cutoff.
  Several draws on the same day therefore cannot overlap or leave a gap.
- **A sampled re-review is recorded with `gating: false`**, because the merge it would decide has
  already happened. That is what keeps re-reviews out of later draws. `OPS-030` states it, and
  `phase-asr-04`, which writes the coordinator's procedure, should carry it.
- **`--replay` was added** so that the seed claim can be checked: it re-runs a recorded draw and
  compares the drawn verdicts and reasons. It leaves the excluded types out of the comparison,
  because a later re-review adds a type to them.
- **The draw record lives in the same schema file** (`definitions/draw`), as the plan-review record
  lives in `adversarial-finding.schema.json`.
- **`verdict` is `pass` or `reject`.** A pass with findings is a `pass` whose `findings` list is not
  empty.

## Corrections

- The review found that the schema dropped a finding's `consequence` (F01). I had modelled the
  finding on the plan-review finding but left out a field reviewers write. Fixed in `b730755`.
- A line-number `sed` edit to a test file landed on a shifted line and broke a function header.
  Ruff caught it, and I repaired it before the first commit.

## Left undone

- Wiring: who writes verdict records, the sha256 check at the merge gate, and when the coordinator
  runs the sampler all belong to `phase-asr-04` (`REQ-030` R03, R04, R10).
- No verdict record or draw exists yet, so the committed-records test has no cases until the first
  one lands.
