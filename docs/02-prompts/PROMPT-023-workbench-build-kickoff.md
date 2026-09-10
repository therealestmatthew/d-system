---
schema_version: 1
id: doc-prompt-workbench-build-kickoff
code: PROMPT-023
title: Workbench build kick-off — owner-ratified deltas and starting state for PROMPT-022
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-governance, sys-backlog]
depends_on: [doc-prompt-workbench-build-orchestration, doc-prompt-workbench-delegation-pack]
---

# Workbench build kick-off — owner-ratified deltas and starting state for PROMPT-022

The owner reviewed the workbench planning pack on 2026-09-10 and approved the build. This is the
pasteable kick-off for the build session. It exists so the coordinator prompt
([PROMPT-022](PROMPT-022-workbench-build-orchestration.md)) stays generic and re-runnable while
the owner's session-specific rulings live in one owner-ratified place. **Where this document and
PROMPT-022 differ, this document wins** — every delta below is the owner's explicit instruction,
recorded verbatim in intent.

## Starting state (2026-09-10)

- All seven `phase-wb-*` phases are `queued`; the demo track through `phase-demo-06` is complete
  and integrated. Start at `phase-wb-01`.
- Two peers are `active` and hold two of the three `max_active` slots: `phase-port-01` and
  `phase-demo-07`. The sequential workbench chain fits the remaining slot; never hold a second
  workbench claim.
- The live demo is the week of 2026-09-15. The runway is real but not short enough to panic:
  see delta 2.

## Owner-ratified deltas to PROMPT-022

### 1. Integration into `dev` is pre-approved for `phase-wb-01`..`06`

PROMPT-022 step 2 says to ask the owner before every merge. For this build the owner has
pre-approved integration of `phase-wb-01` through `phase-wb-06`: when a phase's completion gate
is green (mechanical checks, adversarial review, browser verification where applicable, branch
rebases cleanly), merge it into `dev`, mark it complete, and report — do not stop to ask.

The exception is a **critical concern**: a design or functionality impact that would be
prohibitively expensive to address later. On finding one, do not pause immediately — first run a
dual review: dispatch an adversarial, opinionated agent to challenge the concern and attempt a
solution, and weigh its result against the finding. Only if the concern survives that review and
remains unsolved do you pause for the owner. Otherwise resolve it and keep moving.

`phase-wb-07` is unchanged: its owner-machine conditions close only on the owner's recorded
results, and its close-out waits on the owner.

### 2. No descoping without the owner's explicit direction

REQ-007's descope ladder is not the coordinator's to pull, at any rung, under any schedule
pressure. If the build falls behind, report the slip and the rung you would propose — then keep
building until the owner answers. This overrides every "rung taken and reported" reading of
PROMPT-022 and PROMPT-016 for this track.

### 3. A bounded enhancement lane

During each phase the orchestrator may run an idea-scout pass over the work in flight: look for
improvements beyond the letter of the pack. Two outcomes are permitted:

- **Implement now, note for review**: only if the enhancement is logical, reasonable, a net
  benefit to the product, and touches neither a REQ-007 requirement row's stated behavior nor
  the overall functionality of the program. Each one implemented is recorded as a note in the
  phase report, flagged for the owner's later review.
- **Record, do not build**: anything that would change a stated design requirement or overall
  functionality is captured through the sanctioned idea writer (`tools/append_idea.py`) and left
  for the owner. No exceptions.

This lane is the only permitted deviation from "pre-crafted prompts dispatched verbatim". It
never extends a phase past its budget, never adds a fix cycle, and a scout pass that finds
nothing is the normal result.

## The prompt

> You are the coordinator of the D-System workbench build. Read
> `docs/02-prompts/PROMPT-023-workbench-build-kickoff.md` (this document) in full — its three
> owner-ratified deltas govern you and override PROMPT-022 where they differ. Then execute
> `docs/02-prompts/PROMPT-022-workbench-build-orchestration.md`'s prompt block exactly as
> written, with the deltas applied: integration of `phase-wb-01`..`06` is pre-approved behind a
> green gate (critical concerns get the dual adversarial review before any pause), nothing is
> descoped without the owner's explicit direction, and the bounded enhancement lane of this
> document is open. Start at `phase-wb-01`. Stop where PROMPT-022 stops: `phase-wb-07`'s
> owner-machine conditions and close-out wait on the owner.
