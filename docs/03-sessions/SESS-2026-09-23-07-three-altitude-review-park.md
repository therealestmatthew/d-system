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

Run in the worktree after the review fixes, rebased on `dev` at `a81ca3f`.

- `uv run python -m src.governance` → `Governance OK: 35 systems, 338 documents, 31 memories, 294 backlog phases`
- `uv run pytest` → `1028 passed, 1 skipped, 1 warning`
- Also run for the `GOV-017` merge gate: `uv run ruff check src/ test/` → `All checks passed!`;
  `uv run mypy src/` → `Success: no issues found in 45 source files`.
- `uv run pytest test/test_adversarial_finding_schema.py` → `46 passed, 1 warning`. This covers
  the schema being valid draft-07, 31 structural cases on the finding and the review record
  (including rejected severities, an owner writing `escalated-g3`, a `dispositioned` record with an
  undispositioned finding, and a `returned` record carrying findings), and the two committed
  records.
- Entry check (`GOV-018` step 1 script, extracted from the document and run from
  that extract):
  - Sample non-conforming draft →
    `missing: Verification`, `missing: Boundaries`, `missing: Open questions`,
    `missing: Requirement coverage`, `missing: Concurrency`, exit 1. The draft's `## Open questions`
    heading is inside a fenced block and was correctly not counted.
  - Control (the same draft with those five sections added) → exit 0.
  - After the review's defect 1 fix: a draft whose `depends_on` is a block list naming `REQ-022`,
    with no `Requirement coverage` heading → `missing: Requirement coverage`, exit 1. An inline
    `depends_on` naming only a governance document, with all six required sections → exit 0. The
    sample and control give the same results as before.
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

## Review

An independent `general-purpose` sub-agent was not forked and received only the phase, the owner
rulings, the commit range `dev...HEAD` (`b35568f..71b4b11`) and this record. Its report, verbatim
apart from line wrapping:

> Independent review of phase-irs-06 (the three-altitude review procedure). I looked at the
> worktree /code/d-system-worktrees/phase-irs-06, range dev...HEAD, 5 commits b35568f..71b4b11.
> Both acceptance conditions are met. I found no blockers and no major defects, only four minor
> ones.
>
> **1. REQ-022 R10 (the procedure exists in writing and one review produces a findings record with
> dispositions): Met.** The procedure is written in GOV-018, with the engine prompt in PROMPT-038.
> It covers all three altitudes: plan, phase, and later-added phase.
> docs/08-governance/reviews/2026-09-23-plan-039.json has `status: dispositioned` and
> `altitudes_run [plan, phase, later-added-phase]`. It holds 8 findings (7 major, 1 minor). Every
> finding has a planner disposition: 6 escalated-g3 and 2 accepted-no-change. The phase-altitude
> target set matches the backlog as I read it with PyYAML: irs-02, 05 and 07–13 are queued under
> doc-idea-realization-system-plan; irs-01, 03 and 16 are complete, and irs-06 is active; irs-04,
> 14 and 15 carry `plan: doc-irs-orchestrator-design`, the child plan PLAN-039.01; irs-17 was
> first registered in 4d2412d on 2026-09-16, after ce7c21f, so it is correctly the later-added
> phase. pytest validates the record against the schema (the committed-review tests pass).
>
> **2. A non-conformant draft is returned before adversarial time is spent: Met.** I extracted the
> first bash block of GOV-018 into my scratchpad and ran it myself: sample-nonconforming-draft.md
> → `missing: Verification / Boundaries / Open questions / Requirement coverage / Concurrency`,
> exit 1. The `## Open questions` heading at line 29 sits inside a fence (lines 28–31) and is
> correctly not counted. sample-conforming-control.md → exit 0. PLAN-039 → 6 missing sections,
> exit 1, which matches the session record. The returned record has `status: returned`, empty
> `altitudes_run` and empty `findings`. The schema's if/else forces `entry_check.result` to be
> `returned`, with maxItems 0 on both arrays. GOV-018's claim that PLAN-030 to PLAN-043 all fail
> the check holds: each is missing between 2 and 7 sections when I ran the script.
>
> Other checks that held: the entry-check script against GOV-010's plan table (headings match row
> for row, fenced lines dropped, exact match, the Requirement coverage condition looks up the
> dependency's `kind`, the Concurrency condition counts phase ids outside fences; the one gap is
> defect 1). The schema's conditional rules do what the procedure says. Finding evidence sampled:
> F01, F04, F05, F06 and F08 check out against dev's backlog.yaml. Dispositions: all are
> `by: planner`, use only permitted values, and every one has a reason. Scope: every changed path
> is inside the deliverables, and the backlog.yaml diff touches only phase-irs-06's own entry.
>
> Defects and discrepancies:
> 1. **minor** — GOV-018:73 and the claim at GOV-018:86. The depends_on parser reads only the
>    inline form `depends_on: [a, b]`. A plan whose front matter uses the block-list form is
>    silently not checked for Requirement coverage, so a draft could pass that GOV-010 says should
>    be returned. This contradicts the "implements … exactly" claim.
> 2. **minor** — reviews/2026-09-23-plan-039.json, F07 evidence. It cites
>    "docs/08-governance/GOV-003-backlog-decisions.md:69" for the quote "phase-irs-17 additionally
>    depends on phase-irs-12, whose traced run…". That text is not in GOV-003; it is at
>    docs/03-sessions/SESS-2026-09-16-05-phase-review-remaining-decisions.md:69–70. The
>    dispatcher correctly kept the adversary's text unchanged. But the planner-stand-in disposition
>    says "Verified against the files" and did not catch the wrong citation.
> 3. **minor** — reviews/2026-09-23-sample-nonconforming-draft.json, `target.plan` points to a
>    gitignored path that will not exist on dev. The record's own `notes` and the session record
>    say so, but the target cannot be looked up after the merge.
> 4. **minor** — the schema does not enforce two rules the procedure states: the owner writes only
>    on a finding the planner escalated, and a finding's altitude appears in `altitudes_run`.
>    GOV-018 does not claim the schema enforces either.
>
> Verification: `uv run python -m src.governance` → `Governance OK: 35 systems, 338 documents, 31
> memories, 294 backlog phases`; `uv run pytest` (run once, in the worktree) → `1025 passed, 1
> skipped, 1 warning`; `git status --short` after pytest → empty.

### What was done with each finding

1. **Fixed.** The script now reads `depends_on` in both the inline and the block-list form. The
   test results are under Verification.
2. **Fixed in the disposition, not in the finding.** F07's evidence stays as the adversary wrote
   it (`GOV-018` step 4). Its planner disposition now names the wrong citation and the correct
   location. I confirmed the correct location by reading those lines.
3. **Accepted, no change.** The sample draft is working material by design. The returned record
   carries the script output, which is the evidence the acceptance needs.
4. **Fixed.** The schema now rejects an owner disposition on a finding that has no planner
   `escalated-g3` entry, with a test. A new test checks that each committed record's finding
   altitudes appear in its `altitudes_run`. `GOV-018` step 5 says what the schema rejects.

## Decisions

- **Parked, then resumed on the owner's rulings.** The phase was claimed overnight and parked
  before any build work. The finding schema needed five rulings that no document made. The owner
  answered all five on the morning of 2026-09-23 (morning report, section 8, items 5 to 9):
  - the recurrence key is a slug plus aliases;
  - severity is `blocker | major | minor`;
  - the planner writes dispositions at stage 4 and the owner at G3, with the values `fixed`,
    `accepted-no-change`, `rejected` and `escalated-g3`;
  - storage is one JSON file per review under `docs/08-governance/reviews/`, with the test file
    added to the deliverables;
  - the engine and author fields are added now, and trio fields later as optional.
- **The deliverables widening landed on `dev` first** (`a81ca3f`), in a turn the Session Manager
  granted. My auto-mode permission check blocked the first attempt, and the owner approved the
  retry directly.
- **Four further owner rulings during the build**, all taken as recommended:
  - The demonstration review targets `PLAN-039` with `REQ-022`. It is the only plan where all three
    altitudes are real, and it runs under `GOV-010`'s exemption for pre-standard plans. No plan
    written since 2026-09-22 exists to review.
  - I write the dispositions as the stage-4 planner stand-in, without editing the plan.
  - The slug is optional on a finding, and the adversary proposes it.
  - The engine prompt is dispatched on the `partition-adversary` agent type because it is
    read-only.
- **The review record's file shape is `definitions/review` inside the finding schema.** The phase
  allows one schema file, and the finding stays the root, as the scope names it.
- **Phases already `active` or `complete` are not reviewed** at the phase altitudes, and a child
  plan is its own target. This is why `phase-irs-04`, `-14` and `-15` are outside this review, even
  though finding F02 counts them as part of `PLAN-039`'s coverage.

## Corrections

- My first disposition on F07 said the finding was "verified against the files" but missed a wrong
  citation in its evidence. The independent review caught it, and the disposition now says so.
- The first version of the entry-check script read `depends_on` in the inline form only, while the
  document claimed an exact implementation of `GOV-010`. Fixed as above.

## Left undone

- The six `escalated-g3` findings on `PLAN-039` need the owner's decision at G3. The list is under
  Unresolved. `phase-irs-06` may not edit the plan, `next_up` or other phases' lines.
- `PLAN-039.01`, the orchestrator child plan, has not been reviewed. Under `GOV-018` it is a
  separate target.
- No tool implements the entry check. The script lives in `GOV-018`, as the phase allows. A tool
  would widen a later phase.
