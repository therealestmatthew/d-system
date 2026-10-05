---
schema_version: 1
id: doc-session-next-up-review-gate
code: SESS-2026-10-05-03
title: 'The S3 next_up rule: governance refuses a queued phase with no dispositioned review record'
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-governance, sys-backlog, sys-gov-docs]
depends_on: [doc-deterministic-guards]
---

# The S3 next_up rule: governance refuses a queued phase with no dispositioned review record

## Phase

`phase-grd-04` — The S3 next_up rule: refuse a queued phase with no dispositioned GOV-018 review
record. Claimed by agent-standby-3 (Session 3 - Standby Builder) on the Session Manager's overnight
ASSIGN, reassigned from Builder B; claim commit `869c5d4` on `dev`.

## Verification

All run in the worktree on `agent/phase-grd-04` at `97f6829`, rebased onto `dev` `1d5e161`.

`uv run pytest test/test_review_gate.py`:

```
40 passed, 1 warning in 6.46s
```

`uv run python -m src.governance --catalog`: exit 0.

`uv run python -m src.governance`:

```
Governance OK: 45 systems, 442 documents, 37 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0.

`uv run ruff check src/ test/`:

```
All checks passed!
```

`uv run mypy src/`:

```
Success: no issues found in 49 source files
```

The repository's own result under the new check (`audit_review_gate` on the worktree):

```
([], {'records': 13, 'phases_checked': 3, 'phases_exempt': 16})
```

The 19 `next_up` phases: `phase-grd-04`, `phase-asr-04` and `phase-asr-05` are checked; the other 16
are in the exempt set. `phase-grd-04` is cleared by `2026-09-23-plan-045-later-added.json`, and
`phase-asr-04` and `phase-asr-05` by `2026-09-24-plan-047.json`. Both records are dispositioned, and
neither has a finding whose last disposition is `escalated-g3`. No phase is refused.

## Acceptance

- Fixtures (no record 1; dispositioned record 0; last disposition `escalated-g3` 1; `open` record
  1; grandfathered phase with no record 0) — **Met.** `test/test_review_gate.py` carries all five,
  each run through `audit_backlog` on an isolated repository so the failure is one the governance
  command exits 1 on. The reviewer separately reproduced exit 1 from the real CLI on a scratch copy.
- Review records for `phase-gov-01` and `phase-dgov-06` exist before merge, and the repository
  passes the new check — **Met.** `2026-09-23-plan-010.json` (`phase-gov-01`) and
  `2026-09-23-plan-030.json` (`phase-dgov-06`) are on `dev` and both are dispositioned. The repository
  passes with 3 phases checked and 16 exempt, and no phase is refused, so none is put to the owner.

## Backlog

`status: active`, `agent: agent-standby-3`, `session: doc-session-next-up-review-gate`.
`next_action`: "Built and reviewed on agent/phase-grd-04 (SESS-2026-10-05-03); waits for the
owner-approved merge and the completion edit on dev." `completion_evidence` and `result` are written
in the completion edit on `dev`, after the merge.

## Unresolved

- The merge needs the owner. Earlier this session the auto-mode permission classifier refused a
  fast-forward of `dev` ("Modify Shared Resources") even with the Session Manager's relayed approval.
  The claim commit on `dev` (`869c5d4`) went through. If the merge turn is refused the same way,
  this branch waits for the owner.

## Review

Independent review by a `demo-adversary` subagent, given the phase's scope, acceptance and
verification lists and the commit range `dev...HEAD`, never this record. Its report, condition by
condition:

> **Verdict: PASS WITH FINDINGS.** One major robustness gap found by direct exploit; every
> acceptance condition holds against the real repository and the branch's own fixtures. No scope
> violations, no doc-text drift, no exit-code sleight of hand.
>
> 1. **Fixtures** — Met. The five-case table is in `test/test_review_gate.py`. Not taken on faith
>    from the unit tests: on a scratch copy with `phase-rel-04` (non-exempt, uncovered) inserted
>    into `next_up`, the real CLI gave `EXIT: 1` and `ERROR next_up: phase-rel-04 has no
>    dispositioned review record under docs/08-governance/reviews/ without an escalated-g3 finding
>    (no record lists it) (REQ-028 R12)`.
> 2. **Exempt exactly REQ-028 R12's 19, as a literal list** — Met. `EXEMPT` and R12's list are
>    identical, and `test_the_exemption_is_exactly_req_028_r12s_nineteen` parses the requirement row
>    and asserts set equality. (Note, not a defect: `next_up` has drifted from the snapshot by
>    design; the three non-exempt entries, `phase-grd-04`, `phase-asr-04` and `phase-asr-05`, are
>    each covered by a clean, dispositioned record.)
> 3. **Rule named in GOV-018 and GOV-002** — Met. Both insertions sit beside the existing
>    `next_up`/dispositioned language, and the text matches the code's last-disposition semantics.
> 4. **Records for `phase-gov-01` and `phase-dgov-06`; repository passes** — Met. Both records exist
>    on `dev` and are dispositioned. The unmodified repository refuses nothing.
>
> Verification run in the worktree: `test_review_gate.py` 33 passed; `--catalog` exit 0; catalog diff
> exit 0; governance OK, 45 systems; ruff clean; mypy clean, 49 files. The diff touches exactly the
> five declared files. `audit_review_gate` is wired into `audit_backlog`, which every governance mode
> calls.
>
> **Finding (major):** `review_gate.py` `listed_phases` and `audit_review_gate`'s
> `except (OSError, ValueError)`. A record whose `target` is a non-object (for example
> `"target": "phase-rel-04"`) raises `AttributeError`, so the governance command stops with a
> traceback instead of a named error. None of the 13 current records has this shape; the gap is
> latent. Minimal fix: catch the wider exceptions, or check `target`'s shape first.
>
> Held under attack: last-disposition-only semantics, including escalated-then-owner-fixed; one
> clearing record suffices and every failing one is named; subdirectories excluded; the returned
> sample draft and the escalated F04 (plan-039) and F01 (plan-050) do no live harm, because their
> phases are exempt or not in `next_up`.

The finding is fixed in `97f6829`. `shape_error` checks each
record's `target`, phase lists, findings and dispositions before the gate reads it. A wrongly shaped
record is now reported as `review gate inputs: <path> <what is wrong>`, and seven parametrised cases
in `test_a_wrongly_shaped_record_is_a_named_error` cover it. The fix was not re-reviewed. Its tests
reproduce the reviewer's exact case and pass.

## Decisions

- **Only the record files directly in `docs/08-governance/reviews/` are read.** The directory's
  subdirectories are reserved for build-review verdicts and sampler draws (`REQ-030`). Those are a
  different record and list no plan's phases. Reading them recursively would let a verdict file
  count as a plan review.
- **One clearing record is enough, and a refusal names every record that failed and why.** If two
  records list a phase and one is `open`, the phase passes on the other. When none clears it, the
  error lists each listing record with its status or its escalated finding ids, so the fix is
  visible without opening the files.
- **The exempt set is pinned to the requirement's text by a test**, not only to a count. The set
  cannot grow, or drift from `REQ-028` R12, without a failing test.
- **Claim narrowing.** The Session Manager's overnight assumption narrowed the phase's
  `docs/08-governance/` deliverable to GOV-018, GOV-002 and `reviews/` in the claim commit.
  `reviews/` was not written to: the records the acceptance needs were already on `dev`.

## Corrections

- The first fixture build failed: the governance audit requires every phase's `plan` to name a plan
  document. The fixture now writes a plan that names its phases, so the plan-versus-registered
  check (`REQ-028` R09) stays quiet and each test isolates this rule.
- A wrongly shaped record crashed the check (the review finding above); fixed before `READY`.

## Left undone

Nothing in scope. The completion edit (`status: complete`, `completion_evidence`, `result`, removing
`phase-grd-04` from `next_up`) is made on `dev` in the merge turn, after the owner-approved merge.
