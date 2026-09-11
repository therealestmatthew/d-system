---
schema_version: 1
id: doc-prompt-workbench-build-kickoff
code: PROMPT-023
title: Workbench build kick-off — owner-ratified deltas and starting state for PROMPT-022
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-11'
systems: [sys-governance, sys-backlog]
depends_on: [doc-prompt-workbench-build-orchestration, doc-prompt-workbench-delegation-pack, doc-prompt-workbench-fixes-delegation-pack]
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

### 4. The fix build: `phase-wb-08`..`10` (owner-ratified 2026-09-11)

The owner ratified the fix-phase extension in the 2026-09-11 planning session (REQ-007 delta
rows W15–W18; delegation pack [PROMPT-024](PROMPT-024-workbench-fixes-delegation-pack.md);
completion authority extended in `GOV-003`). For the fix build, this delta governs:

- **Starting state (2026-09-11).** `phase-wb-01`..`07` are complete (the owner closed
  `phase-wb-06`/`07` on their own recorded results). `phase-wb-08`, `phase-wb-09` and
  `phase-wb-10` sit at the front of `next_up`, strictly sequential via `depends_on`. The
  dispatch source for wb-08/09 is PROMPT-024 — not PROMPT-021. The live demo is 2026-09-15.
- **Integration into `dev` is pre-approved for `phase-wb-08` and `phase-wb-09`** on delta 1's
  exact terms (green completion gate — including the new `W08-M` diagnosis convention — then
  merge, mark complete, report; critical concerns get the dual adversarial review before any
  pause). **`phase-wb-10` is not covered**: it is documentation-only, completes through
  `/session-close`, and its integration asks the owner.
- **Owner checks recorded here** (replacing the closed `phase-wb-07`'s checklist as their
  home): after `phase-wb-08` integrates, the owner confirms on the Windows presentation
  machine that the terminal and the HTML Viewer visibly fill their slots (REQ-007 W15's
  Windows half — launch with `D_SYSTEM_DEMO_TERMINAL=1` on backend AND frontend). After
  `phase-wb-09` integrates, the owner confirms the fresh-store PowerShell default and a
  two-shell round-trip (W17's Windows half). The coordinator reminds the owner at each point
  and records the results here or in the runbook; agent evidence never closes these.
- Deltas 2 (no descoping) and 3 (the bounded enhancement lane) apply to the fix build
  unchanged.

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

## The fix-build prompt (2026-09-11)

> You are the coordinator of the D-System workbench fix build. Read
> `docs/02-prompts/PROMPT-023-workbench-build-kickoff.md` (this document) in full — delta 4
> governs this build, and deltas 2 and 3 apply unchanged. Then execute
> `docs/02-prompts/PROMPT-022-workbench-build-orchestration.md`'s prompt block with the
> dispatch source swapped: the phases are `phase-wb-08` then `phase-wb-09` (backlog delta,
> `PLAN-022`), and every dispatch comes verbatim from
> `docs/02-prompts/PROMPT-024-workbench-fixes-delegation-pack.md` — including the `W08-M`
> diagnosis before `W08-C1`, whose report you attach to that creator dispatch. Integration of
> both phases is pre-approved behind a green gate; after each integration, remind the owner
> of the Windows checks delta 4 records and note their results. When `phase-wb-09` is
> complete, report that `phase-wb-10` (the runbook refresh) is ready for a documentation
> session — it is not yours to dispatch from this pack. Stop there.
