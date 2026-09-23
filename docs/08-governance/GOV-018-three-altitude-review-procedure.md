---
schema_version: 1
id: doc-three-altitude-review-procedure
code: GOV-018
title: Three-altitude review procedure — the adversarial review of a plan, each of its phases, and each phase added after it
kind: governance
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-realization]
depends_on: [doc-idea-realization-system, doc-idea-realization-system-requirements, doc-realization-role-contracts, doc-plan-quality-standard]
---

# Three-altitude review procedure

This procedure is stage 5 of the idea realization pipeline (`ARCH-006`). It takes a plan and its
requirement from the planner (stage 4), checks the plan against the plan-quality standard
(`GOV-010`), and has an adversary attack it at three altitudes:

1. **The plan as a whole**, against its requirement.
2. **Each phase in isolation.**
3. **Each phase added after the plan**, against the plan as it stands.

The output is a review record: one JSON file under
[`docs/08-governance/reviews/`](reviews/), holding the entry check's result and every finding
with its disposition. The record's format is
[`schemas/adversarial-finding.schema.json`](../../schemas/adversarial-finding.schema.json): one
finding at its root, the file that holds findings at `definitions/review`. The gate queue
(`phase-irs-13`) and the learning loop (`phase-irs-10`) read that format.

The Adversary role's contract, its never-do list and its 300,000-token ceiling per dispatch are in
the role contracts (`GOV-014`). This document is the procedure that contract names; it does not
restate the contract.

## Roles

| Step | Who | Writes |
|---|---|---|
| Entry check | Whoever runs the review (the dispatcher) | The review record, when the draft is returned |
| Attack | The adversary, dispatched with [`PROMPT-038`](../02-prompts/PROMPT-038-single-adversary-engine.md) | Nothing. It is read-only and reports its findings in its reply |
| Recording | The dispatcher | The review record, from the adversary's reply, without changing any finding |
| Dispositions | The planner at stage 4; the owner at G3 for an escalated finding | The `dispositions` entries in the review record |

The owner's rulings of 2026-09-23 set the severity vocabulary, the disposition values and who writes
them, the storage location, the recurrence key, and the engine fields (morning report, section 8,
items 5 to 9).

## Step 1: the entry check

Before any adversarial time is spent, run `GOV-010`'s mechanical check on the plan. This is the
check `REQ-022` R09 requires. It reads section headings only, so it costs nothing to run.

From the repository root, with the plan's path as the argument:

```bash
#!/usr/bin/env bash
# GOV-010 mechanical check for one plan draft. Run from the repository root.
# Prints one line per missing section and exits 1 if any is missing.
draft=$1
body=$(awk '/^```/{f=!f; next} !f' "$draft")
missing=0
need() {  # need <section> <accepted headings, |-separated>
  grep -Eq "^#{2,3} ($2)\$" <<<"$body" || { echo "missing: $1"; missing=1; }
}
need "Context"        "Context and scope|Summary|Outcome and scope"
need "Design"         "Decisions|The chosen design|Chosen design|Design|Approach|This is an investigation plan|This is a discovery plan"
need "Work"           "Implementation phases|Work and dependencies|Phases|Work|Ordered work and acceptance|Sequencing"
need "Verification"   "Acceptance and verification|Requirement coverage"
need "Boundaries"     "Out of scope|What this plan does not do"
need "Open questions" "Open questions|Open question|Open decisions"
# Requirement coverage: when depends_on names a document of kind requirement.
deps=$(sed -n '2,/^---$/p' "$draft" | grep -m1 '^depends_on:' | tr -d '[]' | cut -d: -f2 | tr ',' ' ')
for dep in $deps; do
  if grep -lx "id: $dep" docs/*/*.md | xargs -r grep -qx "kind: requirement"; then
    need "Requirement coverage" "Requirement coverage"; break
  fi
done
# Concurrency: when the draft names two or more distinct phase ids.
if [ "$(grep -Eo 'phase-[a-z]+-[0-9]+' <<<"$body" | sort -u | wc -l)" -ge 2 ]; then
  need "Concurrency" "Execution order and real concurrency|Execution order"
fi
exit $missing
```

The script implements the plan table in `GOV-010` exactly: the accepted headings, the rule that
fenced lines do not count, and the two conditional sections. If `GOV-010`'s table changes, this
script changes with it. A requirement document's own row check (`GOV-010`, requirement table) is
not part of this entry check. The adversary reads the requirement at the plan altitude.

There are three outcomes:

- **Pass.** The script exits 0. Continue to step 2 and record `entry_check.result: pass`.
- **Returned.** The script exits 1. The plan goes back to the planner with the script's output.
  No adversary is dispatched. Write a review record with `status: returned`,
  `entry_check.result: returned`, the missing sections in `entry_check.missing_sections`, an empty
  `altitudes_run` and no findings. This is `ARCH-006` stage 4's failure path. A plan returned twice
  escalates to G3.
- **Exempt.** `GOV-010` applies only to plans written after 2026-09-22 (its Scope section), so an
  earlier plan is not checked. Record `entry_check.result: exempt` with the plan's `created` date
  as the reason, and continue to step 2. No plan written before that date passes the check.
  `PLAN-030` to `PLAN-043` all lack at least two required headings.

## Step 2: decide what each altitude covers

Write each list into the review record's `target` before dispatching. The adversary reviews what
the record names, and the record shows afterwards what was reviewed.

- **Plan altitude.** The plan and the requirement it depends on. A child plan (for example
  `PLAN-039.01` under `PLAN-039`) is its own target and gets its own review.
- **Phase altitude (`target.phases`).** Every phase in `docs/09-backlog/backlog.yaml` whose
  `plan` is this plan's `id`, that was in the plan's original phase set, and whose status is
  `queued`, `waiting` or `blocked`. A phase that is `active` or `complete` is not reviewed. Its
  work is already under way or done, so a finding could no longer change it before execution.
- **Later-added altitude (`target.later_added_phases`).** Phases with the same `plan` and status
  filter, registered in a later commit than the plan's original set. Find the commit that first
  registered each phase:

  ```bash
  git log --format='%h %ad %s' --date=short -S "id: phase-irs-17" --reverse -- docs/09-backlog/backlog.yaml | head -1
  ```

  The original set is the phases first registered in the same commit as the plan's earliest
  phases. Any phase first registered later is later-added.

Once any later-added phase exists, the third altitude is run. `GOV-014` forbids skipping it
because the first two altitudes came back clean. `altitudes_run` records which altitudes were
dispatched, so a skipped one shows in the record instead of looking like an altitude with no
findings.

## Step 3: dispatch the engine

The engine until the expander, minimalist and arbiter agents ship (`phase-agx-11`,
`phase-agx-12`) is a single adversary. It is a prompt, [`PROMPT-038`](../02-prompts/PROMPT-038-single-adversary-engine.md),
dispatched on the `partition-adversary` agent type. That type is used because it has no Edit or
Write tools and already ranks findings blocker, major and minor. Its partition charter does not
apply to this work; the prompt carries the plan-review brief. `GOV-014` records that this engine
has no agent file of its own, and this procedure does not create one.

Dispatch once per altitude, filling the prompt's placeholders with absolute paths. If the phase
altitude's phases would not fit in one dispatch under the ceiling, split them across dispatches.
Each dispatch still covers only the phase altitude.

What each altitude attacks is set out in `PROMPT-038`. In summary:

- **Plan:** every requirement row maps to a phase and every phase to a row; each decision names
  the alternative it rejected; every stage or step has a failure path; claims about the repository
  are true when checked.
- **Phase:** the phase fits one session; its acceptance is observable and names a failing case;
  its verification commands run; its declared `systems` and `deliverables` cover what its scope
  must touch; its `depends_on` names the phases whose output it reads.
- **Later-added phase:** it contradicts no decision in the plan; it duplicates no other phase's
  scope; the plan's dependency order still holds with it added; the plan or a decision record
  explains why it was added.

## Step 4: record the findings

The dispatcher writes the review record at `docs/08-governance/reviews/<review_id>.json`. The
`review_id` is the review date followed by the target in kebab case, for example
`2026-09-23-plan-039`. Each finding from the adversary's reply becomes one entry in `findings`,
numbered `F01` onwards in the order the replies were read. The dispatcher sets `status: open`.

The dispatcher copies the adversary's fields and does not edit them. It adds only the `id`, and
the `author` string naming the agent type and prompt. The `engine` is `single-adversary`. A
finding is never dropped at this step. A finding the dispatcher thinks is wrong is recorded as
reported, and the planner dispositions it `rejected`.

`slug` and `aliases` are optional. The adversary proposes them when a finding looks like an
instance of a recurring anti-pattern. Whoever records the finding in the anti-pattern store
(`phase-irs-10`) confirms or changes them. The store matches on an exact slug plus a list of
aliases per entry (owner ruling, batch-005 Q1).

Validate the record before committing it:

```bash
uv run pytest test/test_adversarial_finding_schema.py
```

## Step 5: dispositions

`GOV-014` requires every finding to carry a disposition. The owner ruled on 2026-09-23 that the
planner writes them during the stage-4 revision and the owner writes them at G3. Each disposition
is appended to the finding's `dispositions` list. The last entry is the current one.

| Value | Meaning | `reason` must say |
|---|---|---|
| `fixed` | The plan was changed | Where: the document and section, or the backlog line |
| `accepted-no-change` | The finding is correct and the plan stays as it is | Why no change is made |
| `rejected` | The finding is wrong | Why, with the evidence |
| `escalated-g3` | The planner cannot resolve it | What the owner must decide |

- The planner (`by: planner`) may write any of the four values.
- The owner (`by: owner`) writes a disposition only for a finding the planner escalated, and never
  writes `escalated-g3`. The schema rejects it.
- `ARCH-006` stage 5 allows one revision cycle. A blocker that is still unresolved after it is
  dispositioned `escalated-g3`.
- The adversary writes no disposition.

When every finding carries at least one disposition, set `status: dispositioned`. The schema then
rejects any finding without one. A `dispositioned` record goes to phase-fit (stage 6) with the
plan, and its `escalated-g3` findings go to the owner at G3.

This procedure does not define a second review of the revised plan. `ARCH-006` provides one
revision cycle, after which unresolved blockers go to G3.

## Engines after the trio ships

When `phase-agx-11` and `phase-agx-12` ship, the trio becomes the engine, and its adoption seam
belongs to whichever of those two phases lands second (`phase-irs-06` scope). The finding format
already has room for it. `engine` gains a value for the trio, and the trio's argument and ruling
fields are added as optional properties, so records written by the single adversary stay valid
(owner ruling, 2026-09-23).

## What this procedure does not cover

- **Splitting an oversized phase.** That is phase-fit, stage 6 (`phase-irs-05`).
- **Recording findings in the anti-pattern store.** That is `phase-irs-10`.
- **Presenting findings at a gate.** That is the gate queue (`phase-irs-13`).
- **Automatic dispatch.** A person or a session runs this procedure by hand until the orchestrator
  (`PLAN-039.01`) dispatches it.
- **A checker tool.** The entry check is the script above. No tool in `src/` or `tools/`
  implements it, and this procedure does not add one.

## First run

The first review under this procedure is
[`2026-09-23-plan-039`](reviews/2026-09-23-plan-039.json), against the idea realization plan
(`PLAN-039`) and its requirement (`REQ-022`). The entry check's return path was shown against a
sample draft, recorded as
[`2026-09-23-sample-nonconforming-draft`](reviews/2026-09-23-sample-nonconforming-draft.json).
