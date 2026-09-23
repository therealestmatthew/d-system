---
schema_version: 1
id: doc-session-three-altitude-review-park
code: SESS-2026-09-23-07
title: Three-altitude review procedure — parked for owner rulings, then built and run against PLAN-039
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-realization]
depends_on: [doc-idea-realization-system-plan]
---

# Three-altitude review procedure — parked for owner rulings, then built and run against PLAN-039

## Phase

`phase-irs-06` — Three-altitude review procedure with the interim adversarial engine. It writes
the review procedure (the whole plan, each phase in isolation, each later-added phase against the
standing plan), runs it with a single adversary, makes the plan-quality conformance check
(`GOV-010`) its entry condition, and defines `schemas/adversarial-finding.schema.json`, the one
finding format read by the gate queue (`phase-irs-13`) and the learning loop (`phase-irs-10`).

Claimed by `agent-builder-a` in `87cd88a`. Branch `agent/phase-irs-06`, worktree
`/code/d-system-worktrees/phase-irs-06`.

## Verification

Run in the worktree at `0df6bed`, rebased on `dev` at `a81ca3f`.

- `uv run python -m src.governance` → `Governance OK: 35 systems, 338 documents, 31 memories, 294 backlog phases`
- `uv run pytest` → `1025 passed, 1 skipped, 1 warning`
- Also run for the `GOV-017` merge gate: `uv run ruff check src/ test/` → `All checks passed!`;
  `uv run mypy src/` → `Success: no issues found in 45 source files`.
- `uv run pytest test/test_adversarial_finding_schema.py` → `43 passed, 1 warning`. This covers
  the schema being valid draft-07, 30 structural cases on the finding and the review record
  (including rejected severities, an owner writing `escalated-g3`, a `dispositioned` record with an
  undispositioned finding, and a `returned` record carrying findings), and the two committed
  records.
- Entry check (`GOV-018` step 1 script, extracted from the document and confirmed byte-identical to
  the tested copy):
  - Sample non-conforming draft →
    `missing: Verification`, `missing: Boundaries`, `missing: Open questions`,
    `missing: Requirement coverage`, `missing: Concurrency`, exit 1. The draft's `## Open questions`
    heading is inside a fenced block and was correctly not counted.
  - Control (the same draft with those five sections added) → exit 0.
  - `PLAN-039` → `missing: Context`, `Design`, `Verification`, `Boundaries`, `Open questions`,
    `Requirement coverage`, exit 1. `PLAN-039` is exempt as a pre-standard plan, so this is recorded
    for information only.

## Acceptance

- **REQ-022 R10 holds: the procedure exists in writing and one review produces a findings record
  with dispositions.** Met. The procedure is `GOV-018`, and the engine prompt is `PROMPT-038`.
  `docs/08-governance/reviews/2026-09-23-plan-039.json` records three altitudes run against
  `PLAN-039` and `REQ-022`: 8 findings (7 major, 1 minor), each with a planner disposition
  (6 `escalated-g3`, 2 `accepted-no-change`), status `dispositioned`, and valid against the schema.
- **A non-conformant draft is returned before adversarial time is spent on it.** Met.
  `docs/08-governance/reviews/2026-09-23-sample-nonconforming-draft.json` has status `returned`, no
  altitudes run and no findings. The schema rejects a `returned` record that has either (tests
  above). The script output is under Verification.

## Backlog

`phase-irs-06`: `status: active`. `next_action`: "Acceptance met and verified; awaiting the
owner-approved merge through the Session Manager (GOV-017), then completion."
`session: doc-session-three-altitude-review-park`, with the completion evidence and result recorded
on the phase line.

## Unresolved

- **Six findings on `PLAN-039` are escalated to the owner at G3.** Each needs an edit to the plan,
  to `next_up` or to another phase's backlog line, none of which `phase-irs-06` may make:
  - F01: `phase-irs-14` depends on `phase-irs-11`, but the plan's table omits the dependency and
    `next_up` orders `irs-14` first.
  - F02: `phase-irs-04`, `-14` and `-15` are registered under the child plan `PLAN-039.01`, but
    `PLAN-039` counts them as its own.
  - F04: `phase-irs-05`'s acceptance asks for session-length data that does not exist. Every phase
    has `session_budget: 1`.
  - F05: `phase-irs-09`'s acceptance does not test the unverifiable-capability path its scope
    requires.
  - F06: `phase-irs-07` says ratification is tested in `phase-irs-13`, but it belongs to
    `phase-irs-14`.
  - F07: `phase-irs-17` would force failures into `phase-irs-12`'s already-completed run.
- The sample non-conforming draft is gitignored working material (`_working/irs-06/`) and does not
  travel with the branch. Its evidence is the script output recorded above and in the returned
  record.
