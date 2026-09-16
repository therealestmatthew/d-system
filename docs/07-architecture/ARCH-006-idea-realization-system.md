---
schema_version: 1
id: doc-idea-realization-system
code: ARCH-006
title: Idea realization system
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-16'
systems: [sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-idea-record-system, doc-idea-graph-lifecycle, doc-agent-engineering-delegation, doc-autonomous-agent-operations, doc-repeatable-idea-partition]
---

# Idea realization system

The system-level map for idea `000247`: one pipeline from an idea spoken in conversation to a
delivered capability verified against that idea, with the owner's judgment applied at five named
gates and everything between them automated. This document is the super-high-level view — the
stages, the systems each stage rides on, the gate model, the authority model, and the hand-off
contracts. Each subsystem is designed in depth by its own sub-programme or by a child plan of
[PLAN-039](../01-plans/PLAN-039-idea-realization-system.md), the master plan.

## Objective, stated measurably

"As close to fully automated idea realization as possible" is a number, not a mood. The system's
primary metric is the **automation rate**: the fraction of stage transitions in a completed run
that required no human input. Secondary metrics: **cycle time** from idea capture to `delivered`,
and **rework rate** — units of work returned by a validator or reopened after integration. The
metrics are computed from the run ledger and the idea log, both of which already record events
with timestamps. Baselines are measured in `phase-irs-11` before any target is set.

## Owner rulings this architecture is built on

Recorded as findings on idea `000247`, dated 2026-09-15:

1. **Stack**: LangGraph for the pipeline state machine; Claude Agent SDK for agent execution
   ([ADR-018](../04-decisions/ADR-018-langgraph-orchestration.md)).
2. **Scope**: a superseding master plan that re-frames the idea graph and lifecycle programme
   (`PLAN-029`, P1), agent engineering and delegation (`PLAN-031`, P4), autonomous agent
   operations (`PLAN-032`, P5) and the repeatable idea partition (`PLAN-025`) as sub-programmes.
   Existing phases are not invalidated or renumbered.
3. **Gates**: five decision categories (below), everything between them automatable with an
   audit trail.
4. **Sequencing**: architecture and plan now; implementation phases gate on the P1/P4
   foundations they orchestrate, except where a ruling names an interim build.
5. **Trigger path**: a repo-native stopgap dispatch now; migration to P5's trigger gateway only
   if `phase-auto-01` rules that gateway should be built.
6. **Ordering authority**: agents map dependencies and propose orderings; the owner ranks.
   Cross-track priority is the owner's permanently.
7. **End state**: realization ends at a verified `delivered` status on the originating idea, not
   at merge.

## The gate model: five decision categories, not five interruptions

A **gate** is a category of decision reserved to the owner. It is not necessarily a separate
sitting: gate decisions queue, and the owner clears a queue in one session wherever the material
allows. The system's throughput is set by the owner's decision throughput, so gate presentation
is a first-class design concern: every gate item arrives decision-ready — the proposal, the
adversarial findings against it, and the evidence, pre-digested — never as a raw transcript.

| Gate | Decision | Where it pauses the pipeline |
|---|---|---|
| G1 Idea approval | An idea enters the log | Stage 1, per idea, in conversation — as today |
| G2 Track acceptance | The partition's tracks and new-plan-vs-amendment rulings stand | Stage 3, per partition run, one sitting. `PLAN-025`'s three check-ins consolidate into this gate where the material allows; the consolidation is an amendment to `PLAN-025` executed by `phase-irs-02`, recorded in `GOV-003` |
| G3 Plan approval | A plan, its phases, and their proposed ordering are approved after adversarial review | Stage 5/7 boundary, per plan. Ratifying or reordering the proposed `next_up` contribution happens here |
| G4 Integration | A branch merges into `dev` | Stage 8, per unit of work, batchable. Enforced at the tool boundary by P5's capability broker so an automated run cannot merge itself |
| G5 Completion review | A phase reaches `status: complete`; a delivered idea's evidence is accepted | Stages 8–9, **batched**: the owner runs `/session-close` over a queue of finished phases in one sitting. No standing owner-only rule is delegated |

The audit trail between gates is the run ledger (P5) plus the repository's own records; every
automated transition is reconstructible after the fact.

## The nine stages

Each row names the stage, the agent role that performs it, what existing work it rides on, and
its failure path. A stage with no failure path is a defect — the adversarial pass of 2026-09-15
found exactly that in the draft's stages 7 and 8, and this table is the correction.

| # | Stage | Role | Rides on | Gate | Failure path |
|---|---|---|---|---|---|
| 1 | Capture | Owner + assistant in conversation; sanctioned writer `tools/append_idea.py` | `PLAN-016`, exists | G1 | Owner declines; no event written |
| 2 | Triage | Triage agent, one per idea, dispatched on append | Existing `idea-triage` agent; **stopgap dispatch** (`phase-irs-01`) until/unless P5's gateway exists | — | Dispatch failure or agent stall: idea stays `open`; a sweep run reconciles the log against triage state and re-dispatches, so the stopgap degrades to batch, never to loss |
| 3 | Partition | Partition agent + `partition-adversary` | `PLAN-025` prompt pack; threshold or on-demand trigger | G2 | Adversary blocker: one revision cycle, then escalate to G2 with findings attached |
| 4 | Planning | Planner agent drafting requirement + plan per accepted track, decomposed to minimum scope | `phase-idg-12`, measured against the standard from `phase-idg-10`, living where `phase-idg-11` rules | — | Non-conformance to the standard: revise; twice non-conformant: escalate to G3 |
| 5 | Adversarial review | The three-altitude review **procedure** (whole plan; each phase in isolation; each later-added phase against the standing plan). The procedure is this plan's deliverable (`phase-irs-06`); P4's expander/minimalist/arbiter trio becomes its engine when `phase-agx-11`/`-12` ship, with single-adversary review as the engine until then | `PLAN-031` | G3 | Findings return to stage 4 for one revision cycle; unresolved blockers escalate to G3 |
| 6 | Phase-fit check | Phase-fit agent applying a **new** procedure for splitting an oversized backlog phase (`phase-irs-05`). Deliberately distinct from `phase-idg-05`, which decomposes compound *ideas* on the idea log — different object, different artifact | `PLAN-029` adjacency only | — | A split re-enters stage 5 at the phase altitude |
| 7 | Dependency mapping | Mapping agent writes `depends_on` and `systems` locks, validator-checked; **proposes** a `next_up` ordering | `src.governance` validator | G3 (ratification) | Validator rejection (cycle, unknown phase, collision): revise; twice rejected: escalate to G3 with the validator output |
| 8 | Execution | Developer agents in worktrees per `ADR-003`; validator agents (the demo build's code/check pattern) verify each diff against acceptance, seeing the requirement but never the developer's rationale | P5's supervised worker and run ledger where built; the claim protocol regardless | G4, G5 | Validator rejection: one revise cycle per finding class; second rejection parks the unit `blocked` with the finding, surfaced in the G5 queue. Stall or abandoned run: P5's abandoned-run review; the claim is released, the unit returns to `queued` |
| 9 | Realization check | Realization agent verifies the delivered capability against the originating idea's text, records evidence, proposes terminal `delivered` status; feeds the learning loop | Idea log (terminal status added by `phase-irs-09`); anti-pattern store (`phase-agx-03`) | G5 | Capability not verifiable against the idea: recorded as a finding on the idea, surfaced at G5 — never silently closed |

## Orchestration design

A LangGraph state machine whose nodes dispatch Claude Agent SDK agents. The design rules, argued
in full in `ADR-018`:

- **Thin state, repo wins.** Graph state carries only run identity, the current stage, and
  references into the durable records — `_data/ideas.jsonl`, `docs/09-backlog/backlog.yaml`,
  governed documents, the run ledger. If a checkpoint and the repository disagree, the
  repository is authoritative and the run re-derives its position from it.
- **Gates are interrupt nodes.** LangGraph's human-in-the-loop interrupt is the implementation
  of G2–G5; G1 happens before the graph starts. An interrupted run parks durably and any later
  session resumes it.
- **Checkpoints cover crashes, not rejections.** Semantic failure (a validator says no, an
  adversary finds a blocker) follows the stage's failure path above; checkpoint resume covers
  process death only.
- **Boundary against `phase-conc-04`**: that phase owns *claim-protocol* recovery — stale claims,
  orphaned worktrees, a claim held with a finding unwritten — for any agent, pipeline or not.
  The orchestrator owns *run-level* recovery: which stage a run is in and how it resumes. The
  orchestrator consumes `phase-conc-04`'s procedures; it does not redefine them. `PLAN-039`
  carries this de-duplication table.

## Authority model

What each role may write, and what stays the owner's. Every role gets a written contract
(inputs, outputs, never-do) in `PLAN-039`'s roster phase; the never-do column is the binding
half.

Owner-reserved, permanently: idea approval and `lineage` annotations; partition acceptance;
plan approval; `next_up` ranking and all cross-track priority; integration into `dev`; phase
completion via `/session-close`; edits to `AGENTS.md` and `CLAUDE.md`; deletions under
`_working/`; anything `_private/`.

Agent-writable, always with an audit trail: idea annotations of `kind: finding` and status
moves the writer permits; draft documents; backlog `depends_on` and `systems` on phases within
an approved plan; branch commits; run-ledger entries.

## Cost and safety controls

An unattended pipeline spends money unattended. Requirements `REQ-022` makes binding: per-run
token budgets with a hard cap that parks the run rather than exceeding it; a kill switch that
halts all dispatch; the confidentiality gate (`tools/check_no_private_content.py`, staged) run
mechanically inside stage 8 rather than left to habit; and validator independence grounded in
evidence — executed tests and repository checks, not persona prompts — because every agent here
is the same model and correlated blind spots are real. The owner spot-audits a sample of passed
validations; the sampling is a G5 activity.

## The learning loop

Stage 9's evidence, stage 8's validator rejections, and stage 5's recurring findings all feed
the anti-pattern store (`phase-agx-03`) and, through it, revisions to the plan-quality standard
(`phase-idg-10`). This is the difference between a conveyor and a machine that improves: the
pipeline's own failures are inputs to its next run. Wiring is `phase-irs-10`.

## Hand-off contracts

Every arrow in the pipeline names its artifact. The consumer reads the artifact, never the
producer's conversation.

| Producer → consumer | Artifact |
|---|---|
| Capture → triage | An `idea created` event in `_data/ideas.jsonl` |
| Triage → partition | A `finding` annotation and `triaged` status per idea |
| Partition → planning | An accepted partition record: tracks, member ideas, new-plan-vs-amendment ruling per track |
| Planning → review | A requirement and plan document pair per track, conformant to the plan-quality standard |
| Review → phase-fit | The plan plus a findings record with each finding's disposition |
| Phase-fit → mapping | The final phase set, each within one-session scope |
| Mapping → execution | Registered backlog phases with `depends_on`, `systems`, and a ratified ordering |
| Execution → realization | An integrated branch, its verification output, and a completion-reviewed phase |
| Realization → the log | Evidence annotations and a proposed terminal `delivered` status on the originating idea |

## What this document is not

It is not the plan (`PLAN-039` sizes and sequences the work), not the requirements (`REQ-022`
states what must be observably true), and not a claim that any of it exists. As of 2026-09-15
stages 1–3 exist in manual or batch form; everything else is planned work in the sub-programmes
or in `PLAN-039`'s own phases.
