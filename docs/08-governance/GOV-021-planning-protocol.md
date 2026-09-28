---
schema_version: 1
id: doc-planning-protocol
code: GOV-021
title: Planning protocol — the steps from an idea to completed work, in order, each pointing to where it is defined
kind: governance
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-28'
systems: [sys-gov-docs]
depends_on: [doc-idea-realization-system, doc-realization-role-contracts, doc-plan-quality-standard, doc-three-altitude-review-procedure, doc-batch-orchestration-protocol, doc-backlog-protocol, doc-prompt-pack-protocol, doc-governance-protocol, doc-document-code-protocol]
---

# Planning protocol

Written in an unclaimed session: owner-directed work with no backlog phase; no peer holds a lock
against it.

This is a list of the planning steps in order, from an idea to completed work (idea `000500`).
Each step says what happens, who does it, the gate if there is one, and where the step is
defined. Read the pointed-to document for how the step is done. This document adds no rule. The
owner's rulings are the exception, because no other document states them yet: those of 2026-09-27
recorded on idea `000500`, marked **Owner ruling**, and the owner's answers of 2026-09-28 on the
step order, marked **Owner ruling, 2026-09-28**.

The owner's statement of the protocol, as given: *"plan -> audit -> decompose plan into phases
-> audit phases -> further decomposition -> additional audit (repeat until still undetermined
criteria is met)... assign systems to phases, batch phases and order dependencies"*.

The gates G1 to G5 are the owner's decision categories in the idea realization system
(`ARCH-006`, "The gate model: five decision categories, not five interruptions"). Stage numbers below are `ARCH-006`'s ("The nine stages"). Role
contracts are in `GOV-014`, "Roles".

## Steps

### Before planning

1. **Capture.** The owner and the assistant record an idea through `tools/append_idea.py`. Gate
   **G1** (idea approval). Defined: `ARCH-006` stage 1; `PLAN-016`; `GOV-006`, "Capture new asks
   as ideas".
2. **Triage.** The triage agent writes a finding on the idea and moves it to `triaged`. No gate.
   Defined: `ARCH-006` stage 2; `GOV-014`, "Triage".
3. **Partition.** The partition agent groups triaged ideas into tracks, with a new-plan-or-amendment
   ruling per track; `partition-adversary` attacks the proposal. Gate **G2**, which `ARCH-006`
   names "Track acceptance" and the owner calls "partition acceptance": the tracks and rulings
   stand. Defined: `ARCH-006` stage 3 and the G2 row; `PLAN-025`; `PROMPT-034`; `GOV-014`,
   "Partition".

### Planning

4. **Pre-plan investigation (optional).** **Owner ruling:** an investigation, or prompt pack,
   before the plan is optional. It is tracked as a governed document when it will be re-run, has
   owner gates, or needs its own review; otherwise it lives in `docs/00-working/`. What the
   package contains: `GOV-008`, "1. Prompt A — the pre-plan package" and the template appendix.
   `GOV-008` does not itself say the package is optional (see Open questions). **Owner ruling,
   2026-09-28:** it comes before the requirement, as Prompt A does in `GOV-008`.
5. **Requirement.** **Owner ruling:** the requirement comes first, before the plan. The planner
   writes observable requirement rows with verification methods. Defined: `AGENTS.md`, "Before
   you start" item 3; `GOV-010`, "Requirement sections" and "Content judgements for
   requirements"; `ARCH-006` stage 4. How requirements are generated is idea `000502`.
6. **Plan.** The planner writes the plan against the plan-quality standard. Defined: `GOV-010`,
   "Plan sections" and "Content judgements for plans"; `ARCH-006` stage 4; `GOV-014`, "Planner".
   Code allocation: `GOV-005`, "Assigning a code"; front matter: `GOV-001`, "Front matter
   contract". Plan and plan-folder anatomy is idea `000505`.
7. **Audit the plan.** The entry check (the `GOV-010` mechanical check), then an adversary at the
   plan altitude. A plan returned twice escalates to G3. Defined: `GOV-018`, "Step 1: the entry
   check" and steps 2 to 5; `ARCH-006` stage 5.
8. **Decompose the plan into phases.** Each phase is one outcome that fits one session, with
   acceptance, verification and deliverables. Defined: `GOV-002`, "Every item carries its session
   contract" and "Capture before implementation" item 2; `ARCH-006` stage 4 ("decomposed to
   minimum scope").
9. **Audit the phases.** An adversary attacks each phase in isolation. Findings return to the
   planner for one revision cycle; unresolved blockers escalate to G3. Defined: `GOV-018`, phase
   altitude (steps 2 to 5); `ARCH-006` stage 5.
10. **Further decomposition and re-audit, repeated.** The phase-fit check splits a phase that does
    not fit one session; each split re-enters review at the phase altitude. Defined: `ARCH-006`
    stage 6; `GOV-014`, "Phase-fit". A phase added after the plan is reviewed against the standing
    plan. Defined: `ARCH-006` stage 5 (the third altitude); `GOV-018`, later-added altitude. The
    phase-fit procedure is not yet defined (`phase-irs-05`, queued).
    **Owner ruling, stop rule:** the loop stops by default when every phase fits one session by a
    measured heuristic. The heuristic is not yet defined (idea `000445`, `phase-irs-05`).
    **Owner ruling, 2026-09-28, until the heuristic exists:** the loop stops when the phase-altitude
    audit proposes no further split; any doubt goes to the owner at G3.
    **Owner ruling, exception:** when the audit proposes no split but the heuristic says the phase
    does not fit, the case escalates to G3 with both results, and the owner chooses: split by
    hand, accept with a recorded reason, or adjust the heuristic. The owner: *"We still need to
    figure out the Heuristics. Once that is finalized maybe we change this to audit wins or always
    split."*
11. **Assign systems and order dependencies.** The mapper writes each phase's `systems` and
    `depends_on`, the `src.governance` validator checks them, and the mapper proposes a `next_up`
    ordering. Rejected twice: escalate to G3 with the validator output. Defined: `ARCH-006`
    stage 7, including its "Rides on" column; `GOV-014`, "Mapper"; `GOV-002`, "State and dependency rules" and "Concurrent
    phases". The mapping agent is not yet built (`phase-irs-07`, queued).
12. **Plan approval.** Gate **G3**: the owner approves the plan and its phases, and ratifies or
    reorders the proposed `next_up`. Escalated findings are decided here. Defined: `ARCH-006`, the
    G3 row; `GOV-018`, "Step 5: dispositions"; `GOV-002`, "Inserting work at the front";
    `GOV-001`, "Lifecycle and review". Steps 7 to 12 differ from `ARCH-006` and `GOV-018` in
    order; see Open questions 3 to 5.
13. **Batch.** The owner composes batches of queued phases; each composition is verified by
    script, and stages follow real dependency edges and collisions. Defined: `GOV-016`,
    "Composition is the owner's", "Verify a composition before declaring it runnable" and
    "Stages: permission, not instruction".

### Execution and after

14. **Execute.** A developer claims a phase and works it in its own worktree. Defined: `AGENTS.md`,
    "Concurrent agents: claim a phase" and "Concurrent agents: work in a worktree"; `GOV-002`,
    "Selecting and running a session"; `ADR-003`; `ARCH-006` stage 8; `GOV-014`, "Developer".
15. **Validate.** Validators check each diff against the requirement text, never the developer's
    rationale, by executed commands. Defined: `ARCH-006` stage 8; `GOV-014`, "Validator" and "The
    evidence rule for validators". The execution harness is not yet built (`phase-irs-08`, queued).
16. **Integrate.** Gate **G4**: the owner decides whether a branch merges into `dev`. Defined:
    `ARCH-006`, the G4 row; `AGENTS.md`, "Confidentiality and publishing" and "Concurrent agents:
    complete and hand off" steps 8 and 9.
17. **Complete.** Gate **G5**: `/session-close` is the only way a phase reaches `complete`,
    invoked by the owner or by a coordinator once `GOV-003`'s three conditions hold. Defined:
    `.claude/commands/session-close.md`; `GOV-003`, "Coordinator completion replaces
    owner-invoked /session-close, repository-wide"; `ARCH-006`, the G5 row; `AGENTS.md`,
    "Session backlog".
18. **Realization check.** The realization agent verifies the delivered capability against the
    originating idea's text and proposes the terminal `delivered` status, which G5 accepts.
    Defined: `ARCH-006` stage 9; `GOV-014`, "Realization". Not yet built (`phase-irs-09`, queued).
19. **Learning loop.** Realization evidence, validator rejections and recurring review findings
    feed the anti-pattern store and revisions to the plan-quality standard. Defined: `ARCH-006`,
    "The learning loop". Not yet built (`phase-irs-10`, `phase-agx-03`, both queued).

## Out of scope

- Archiving one-time plans and prompts: idea `000501`.
- How requirements are generated: idea `000502`.
- Plan and plan-folder anatomy: idea `000505`.
- The phase-fit heuristic itself: idea `000445` and `phase-irs-05`.

## Open questions

1. **`GOV-008` does not say the pre-plan package is optional.** Its pipeline treats Prompt A as a
   governed prompt document ("The pipeline", stage 1) and names no ungoverned case. Step 4 carries
   the owner's ruling; `GOV-008` needs an amendment to match. **Owner ruling, 2026-09-28:** amend
   `GOV-008` once, with the plan-folder standard's work, after idea `000501` separates one-time
   prompts from reusable ones.
2. **Settled 2026-09-28: the interim stop rule.** The stop rule needs the heuristic, which does not
   exist yet. The owner ruled that until it does, the loop stops when the phase-altitude audit
   proposes no further split, and any doubt goes to the owner at G3 (step 10).
3. **Steps 7 to 9 audit the plan before it has phases; the documents assume the phases already
   exist.** **Owner ruling, 2026-09-28:** keep the order as stated and flag the difference.
   `GOV-018`'s plan altitude checks that "every requirement row maps to a phase and every phase to
   a row" (step 3). `GOV-002` fails the governance check for any draft plan with no phase
   ("Capture before implementation" item 3). `ARCH-006` stage 4 has the planner write the plan
   already decomposed to minimum scope, and stage 5 reviews the plan and its phases together.
4. **Step 11 assigns `systems` and `depends_on` after the loop; the backlog requires them
   earlier.** **Owner ruling, 2026-09-28:** keep this order, which matches `ARCH-006` stage 7, and
   flag the difference. `schemas/backlog.schema.json` requires both fields on every
   registered phase. `GOV-018`'s phase altitude reviews phases read from
   `docs/09-backlog/backlog.yaml` and checks their `systems` and `depends_on` (step 3). `GOV-014`
   says only the mapper registers a phase ("Phase-fit", never-do), so under `GOV-014` the phases
   `GOV-018` reviews would not be registered yet.
5. **Step 13 places batching after the dependencies and G3.** The owner's statement reads "assign
   systems to phases, batch phases and order dependencies". **Owner ruling, 2026-09-28:** order
   the steps as dependencies, then G3, then batching, because `GOV-016` verifies a batch against
   `depends_on` edges that must already exist ("Verify a composition before declaring it
   runnable", check 3). `ARCH-006` has no batching stage.
6. **Settled 2026-09-28: who may run `/session-close` (step 17).** `GOV-003` records an owner
   decision of 2026-09-16 that a coordinator may mark a phase `complete` once all three of its
   conditions hold, and `.claude/commands/session-close.md` says the same. `AGENTS.md`, "Session
   backlog", and `ARCH-006`'s G5 row were amended to match on 2026-09-28 with the owner's approval.

The owner ruled on 2026-09-28 that Open questions 3 and 4 stay as they are, with both sides
unchanged, until a planning session resolves them.
