---
schema_version: 1
id: doc-realization-role-contracts
code: GOV-014
title: Idea realization pipeline role contracts
kind: governance
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-governance]
depends_on: [doc-idea-realization-system, doc-idea-realization-system-requirements, doc-irs-orchestrator-design]
---

# Idea realization pipeline role contracts

One written contract per agent role in the idea-realization pipeline mapped by
[ARCH-006](../07-architecture/ARCH-006-idea-realization-system.md)'s stage table: triage,
partition, planner, adversary, phase-fit, mapper, developer, validator and realization. Stage 1
(capture) is the owner and assistant in conversation, not an agent role, and carries no contract
here.

Each contract states what the role receives, what it must produce, and its binding never-do —
"the never-do column is the binding half" (`ARCH-006`, Authority model). `PLAN-039.01` §8's
dispatch adapter binds the role contract for every dispatch; this document is that source. Where
a role already has an agent definition under `.claude/agents/`, this document is the authority and
the agent definition is updated to match it, not the reverse.

## Owner-reserved, permanently

Reproduced verbatim from `ARCH-006`'s authority model so no contract below can drift from it:

> idea approval and `lineage` annotations; partition acceptance; plan approval; `next_up` ranking
> and all cross-track priority; integration into `dev`; phase completion via `/session-close`;
> edits to `AGENTS.md` and `CLAUDE.md`; deletions under `_working/`; anything `_private/`.

No role contract below grants any agent any item on this list. Every "proposes" in a contract's
outputs is deliberate: the artifact named is a proposal awaiting the gate that reserves the
decision, never the decision itself. `REQ-022` R03 is checked by grepping the contracts for a
reservation and finding it absent from all nine.

Agent-writable, always with an audit trail (also from `ARCH-006`, stated once here rather than
repeated in each contract): idea annotations of `kind: finding` and status moves the writer
permits; draft documents; backlog `depends_on` and `systems` on phases within an approved plan;
branch commits; run-ledger entries.

## The evidence rule for validators

A validator's verdict is grounded in **executed tests and repository checks** — commands actually
run, in the worktree, with their real output captured — never in a persona assertion of confidence
or a claim about what the code "should" do. Every agent in this pipeline is the same underlying
model; a validator that judges by impression rather than by execution shares the developer's blind
spots instead of catching them. This rule binds the validator contract below and is restated there
because `REQ-022` R23 checks it against that contract specifically.

## Per-dispatch token-budget ceiling

`PLAN-039.01` §8 requires every role contract to carry its own per-dispatch ceiling: the
authoritative spend counter is run-level (the SDK's reported usage, summed from the ledger), but a
single in-flight dispatch can overshoot between checks, so each role also carries a ceiling that
bounds one dispatch's worst-case overshoot. `phase-irs-11` builds the enforcement; this is the
source it reads.

No source document sets a number, and no role's actual dispatch cost has been measured yet — the
pipeline has not run. This contract sets one **initial default ceiling of 300,000 tokens per
dispatch, for every role**, rather than inventing differentiated figures with no evidence behind
them. A role may be given a different ceiling only by an owner ruling recorded as an amendment to
this document, once real dispatch data from `phase-irs-11`'s baselines gives a reason to differ.

## Roles

### Triage

- **Inputs:** an `idea created` event in `_data/ideas.jsonl` (Capture → Triage, `ARCH-006` hand-off
  table); the idea's own id, title and body.
- **Outputs:** a `finding` annotation, and the `triaged` status move (Triage → Partition). The
  finding names related plans, phases, documents and overlapping ideas; it never asserts a
  decision about them.
- **Never-do:** never conclude an idea should be declined or merged — state overlap, do not act on
  it; never write a `linked` event, only a `PROPOSED LINK:` line; never call `status ...
  promoted`, only a `PROPOSED PROMOTION:` line; never call any idea-log verb besides `annotate`
  and the permitted `open` → `triaged` move; never invent a relationship not actually verified by
  reading the target.
- **Existing agent definition:** `.claude/agents/idea-triage.md` — updated by this phase to carry
  the per-dispatch ceiling.
- **Per-dispatch ceiling:** 300,000 tokens.

### Partition

- **Inputs:** ideas at `triaged` status (Triage → Partition); `PLAN-025`'s prompt pack and corpus
  selection; the threshold or on-demand trigger that fires the stage.
- **Outputs:** a *proposed* partition record — tracks, member ideas, and a new-plan-vs-amendment
  ruling per track — plus `partition-adversary`'s findings against it (Partition → Planning, once
  accepted). The record is a proposal until G2 accepts it; the agent's own output artifact is
  never described as "accepted."
- **Never-do:** never accept its own partition — acceptance is G2, owner-reserved; never proceed
  past an adversary blocker without one revision cycle first; never treat convergence between
  proposal and adversary review as substitute for the owner's acceptance.
- **Existing agent definition:** `.claude/agents/partition-adversary.md` covers the adversarial
  half of this stage and is general-purpose across the repository, not idea-realization-specific;
  updated by this phase to carry the per-dispatch ceiling for its use in this pipeline. No agent
  definition exists yet for the partition-drafting half; none is created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Planner

- **Inputs:** an accepted partition record — tracks, member ideas, new-plan-vs-amendment ruling
  per track (Partition → Planning); triage's prior findings and links for the member ideas, so the
  draft does not duplicate coverage triage already established; the plan-quality standard
  (`phase-idg-10`).
- **Outputs:** a requirement and plan document pair per track, conformant to the plan-quality
  standard, decomposed to minimum scope per `ARCH-006` stage 4's duty (Planning → Review). Drafts
  land where `phase-idg-11` defines, not directly under `docs/01-plans/`.
- **Never-do:** never allocate a document code; never mark an idea `promoted`; never decide plan
  approval — that is G3, owner-reserved; never leave a phase table undecomposed for a later stage
  to split, when the standard requires minimum-scope phases at draft time.
- **Existing agent definition:** none. `phase-idg-12` is the implementation phase for this role
  (idea `000072`'s planner bullet, struck by `phase-prog-06`); this contract is the prose role
  contract only and creates no agent-definition file.
- **Per-dispatch ceiling:** 300,000 tokens.

### Adversary

- **Inputs:** a requirement and plan document pair (Planning → Review); the three-altitude review
  procedure — whole plan, each phase in isolation, each later-added phase against the standing
  plan (`ARCH-006` stage 5; the procedure itself is `phase-irs-06`'s deliverable).
- **Outputs:** the plan plus a findings record with each finding's disposition (Review →
  Phase-fit). A finding is never silently dropped; every finding carries a disposition, even if
  that disposition is "accepted as-is, no change."
- **Never-do:** never approve the plan — G3 is owner-reserved; never resolve a finding by
  authoring the fix into the plan itself, beyond naming the minimal fix; never treat a second
  clean review as license to skip the third altitude (later-added phases against the standing
  plan) once phases start accumulating.
- **Existing agent definition:** none specific to this pipeline stage. `partition-adversary.md` is
  a different, partition-scoped role (see above); the single-adversary engine that stands in for
  P4's expander/minimalist/arbiter trio until `phase-agx-11`/`-12` ship has no agent-definition
  file yet, and none is created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Phase-fit

- **Inputs:** the plan plus its findings record with dispositions (Review → Phase-fit); the
  phase-fit procedure for splitting an oversized backlog phase (`phase-irs-05`'s deliverable),
  deliberately distinct from `phase-idg-05`'s idea-level decomposition — different object,
  different artifact.
- **Outputs:** the final phase set, each within one-session scope (Phase-fit → Mapping). A split
  phase re-enters review at the phase altitude rather than proceeding straight to mapping.
- **Never-do:** never decompose an *idea* — that is `phase-idg-05`'s object, not this role's; never
  register a phase directly to the backlog — that is the mapper's output, not this role's; never
  skip re-review after a split.
- **Existing agent definition:** none; none created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Mapper

- **Inputs:** the final phase set, each within one-session scope (Phase-fit → Mapping).
- **Outputs:** registered backlog phases carrying `depends_on` and `systems`, checked by
  `src.governance`'s validator, and a *proposed* `next_up` ordering (Mapping → Execution, once
  ratified). The ordering is a proposal until G3 ratifies, amends or rejects it; the agent's own
  output is never described as "ratified."
- **Never-do:** never rank `next_up` or set cross-track priority itself — that is owner-reserved,
  permanently, under both this contract's reserved list and `ARCH-006`'s; never register a phase
  the validator rejects without revising first; on a second rejection, never proceed without
  escalating to G3 with the validator output attached.
- **Existing agent definition:** none; none created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Developer

- **Inputs:** a registered backlog phase, claimed under the `ADR-003` protocol unchanged, in its
  own worktree.
- **Outputs:** a branch and diff meeting the phase's acceptance criteria, ready for validation
  (Execution stage; consumed by the validator role below, and — once integrated by the owner-
  reserved G4 decision — by realization).
- **Never-do:** never integrate its own branch into `dev` — G4 is owner-reserved; never mark its
  own phase complete — completion via `/session-close` is owner-reserved; never skip the staged
  confidentiality check (`tools/check_no_private_content.py`) before any push; never edit
  `AGENTS.md` or `CLAUDE.md`; never touch `_private/`; never delete anything under `_working/`
  without the owner's explicit approval.
- **Existing agent definition:** none specific to this pipeline. `ARCH-006` stage 8 says developer
  agents work "in worktrees per `ADR-003`, unchanged" — an existing protocol, not an existing
  agent-definition file — so none is created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Validator

- **Inputs:** exactly the requirement text and the diff. Never the developer's rationale, even if
  it leaks into the dispatch — `REQ-022` R13 is checked by inspecting validator dispatch prompts
  for exactly this boundary, and `ARCH-006` stage 8 states it explicitly: validators "see the
  requirement but never the developer's rationale."
- **Outputs:** a pass/fail verdict grounded in the evidence rule above, with findings and the
  verbatim output of every verification command run (Execution → Realization, once the phase is
  completion-reviewed). A rejected unit's finding is attached and surfaces in the G5 queue on a
  second rejection, per `ARCH-006` stage 8's failure path.
- **Never-do:** never accept the developer's rationale as evidence, even if it leaks into its
  inputs; never edit the diff or fix a finding itself; never mark a phase complete — that is
  owner-reserved via `/session-close`; never merge or integrate — G4 is owner-reserved; never
  substitute a persona assertion ("this looks correct") for an executed check.
- **Evidence rule (restated for `REQ-022` R23):** every verdict traces to executed tests and
  repository checks captured in the report; a claim with no command behind it is not evidence.
- **Owner spot-audit sampling rule (G5 activity, per `ARCH-006`'s cost and safety controls):** at
  each G5 sitting, the owner spot-audits at least one in ten of that sitting's passed validations,
  selected at random from the sitting's queue. Any unit that was rejected once before it passed is
  audited every time, never sampled. The rate is this contract's initial rule; the owner may
  change it by amendment once G5 sittings give real data on where validators actually miss.
- **Existing agent definition:** none specific to this pipeline. `ARCH-006` stage 8 names "the
  demo build's code/check pattern" (`.claude/agents/demo-validator-code.md`,
  `.claude/agents/demo-validator-check.md`) as the pattern to follow, not as agent definitions this
  pipeline reuses — those files belong to the live-demo and workbench build track and are not
  updated by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

### Realization

- **Inputs:** an integrated branch, its verification output, and a completion-reviewed phase
  (Execution → Realization); the originating idea's text, read from the idea log.
- **Outputs:** evidence annotations and a *proposed* terminal `delivered` status on the
  originating idea (Realization → the log). The terminal status is reached only through G5; the
  agent's own output is never described as the idea reaching `delivered`.
- **Never-do:** never write a terminal `delivered` status itself — G5 completion review is owner-
  reserved; never close an idea silently when the capability is not verifiable against the idea's
  text — that case is a recorded finding surfaced at G5, per `ARCH-006` stage 9's failure path,
  never a quiet non-result.
- **Existing agent definition:** none; none created by this phase.
- **Per-dispatch ceiling:** 300,000 tokens.

## What this document is not

It does not build any of the nine agents; most have no `.claude/agents/` file yet and this phase
creates none. It does not set the actual run-level token budget or the kill switch — those are
`phase-irs-11`'s build, reading the per-dispatch ceilings recorded here. It does not rule on
`phase-auto-01`'s trigger-gateway question or any other open sequencing decision in `PLAN-039`.
