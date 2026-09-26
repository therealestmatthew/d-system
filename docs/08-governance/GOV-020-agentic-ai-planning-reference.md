---
schema_version: 1
id: doc-agentic-ai-planning-reference
code: GOV-020
title: Agentic AI planning reference — anatomy of an executable plan
kind: governance
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-governance]
depends_on: [doc-governance-protocol, doc-backlog-protocol, doc-three-altitude-review-procedure]
---

# Agentic AI planning reference — anatomy of an executable plan

This is a practical reference for planning work that an agent, a person, or a sequence of agents
will implement over one or more sessions. It adds no new mandatory repository gate. Where it
conflicts with a governing instruction, the governing instruction wins.

An effective plan is an executable agreement: it tells a newly arriving contributor what outcome
to pursue, what they may change, how the work is sequenced, and what evidence is needed before
calling it complete. A checklist alone is not a plan; it does not preserve why the work exists,
how choices were made, or how to recognize a safe handoff.

## Repository mapping

For non-trivial work in this repository, this reference is not a shortcut around the formal
workflow: write the governed requirement (`REQ`) and plan (`PLAN`) documents before implementation,
then split the open plan into backlog phases. The plan retains rationale, decisions, boundaries,
and requirement coverage; `docs/09-backlog/backlog.yaml` is the sole authoritative execution-status
ledger. Its phases must cover open plans and carry the executable fields, evidence, and handoff
state. Follow the governing protocol (`GOV-001`), backlog protocol (`GOV-002`), and the repository
instructions (`AGENTS.md`) when using this reference here.

## The plan at a glance

Before writing detail, make the following legible in one screen or short summary:

| Question | A useful answer contains |
|---|---|
| What changes? | A user- or system-observable outcome, expressed without implementation assumptions. |
| Why now? | The problem, opportunity, or decision that makes the outcome valuable. |
| What is constrained? | Scope, non-goals, compatibility, privacy, budget, time, and authority boundaries. |
| What proves success? | Observable acceptance conditions and the evidence or command that checks each one. |
| Who acts next? | The current status, owner, prerequisite, and the next concrete action. |

If a capable agent cannot answer those questions from the plan and its cited sources, the plan is
not yet ready for execution.

## 1. Outcome, context, and boundaries

Start with the outcome, not a list of edits. Describe the current problem with enough evidence to
distinguish it from a guess, then name the changed behavior or artifact the work will deliver.
Separate these three items explicitly:

- **In scope:** the capabilities, users, interfaces, and data affected.
- **Out of scope:** tempting adjacent work that this effort will not absorb.
- **Constraints:** facts the implementation must respect, including existing contracts, security or
  privacy rules, operating limits, budgets, deadlines, and decisions that require owner approval.

Record assumptions and unknowns. An assumption can be used provisionally when it does not expand
authority or make an irreversible choice; otherwise it is an open decision and should stop the
relevant phase rather than be guessed through.

## 2. Requirements that can be observed

Write requirements as claims that someone can check. “Improve export performance” is an intention;
“the defined export completes within 30 seconds for the representative data set” is a claim with a
testable boundary. Each material requirement should name:

- its observable behavior or artifact;
- its applicable conditions and failure case;
- its verification method and expected result; and
- the phase that delivers the evidence.

Keep a simple coverage map when a plan has multiple requirements or phases. It exposes orphaned
requirements (nothing implements them) and orphaned phases (work that delivers no stated value).

| Requirement | Delivering phase | Evidence |
|---|---|---|
| Account data is available only to its authenticated owner. | API authorization | Integration test covering own, other, and anonymous requests. |
| Export output has the published shape. | Export contract | Schema or contract test plus one representative fixture. |

The table is an example pattern, not a substitute for the project’s requirement records.

## 3. Decisions, alternatives, and interfaces

Plans should retain the decisions that make their steps make sense. For every consequential choice,
record the chosen approach, the viable alternative rejected, the reason, and the trigger for
revisiting it. Link a decision record when the decision needs durable authority beyond the plan.

Name interfaces that cross phase or team boundaries: input and output shapes, ownership, error
behavior, versioning expectations, and the point at which the interface is considered stable.
Agents can then work concurrently against a stated contract instead of against each other’s
unmerged edits.

## 4. Modular phases and real dependencies

Split the plan into phases that each fit a session, produce a coherent increment, and have one
clear owner at a time. A phase is not merely a calendar slice. It should leave the system in a
valid state and be independently reviewable.

Each phase needs the following fields:

- **Goal and scope:** the single coherent outcome and the systems or files it may touch.
- **Inputs and dependencies:** prior artifacts, decisions, or phases it relies on.
- **Implementation sequence:** the smallest safe steps, including migration or rollout order.
- **Acceptance:** observable behavior, including at least one relevant negative or failure case.
- **Verification:** commands, tests, inspection points, and expected results.
- **Handoff:** changed contracts, evidence location, deferred work, and the exact next action.

Represent the dependency graph, not only a numbered list. Numbering is useful for a serial path;
a graph distinguishes work that must wait from work that can proceed in parallel. Parallel phases
must have disjoint ownership or an explicit shared-interface agreement. If two phases must edit the
same core behavior, sequence them or make that coordination a phase of its own.

## 5. Status, evidence, and completion over time

Use evidence-bearing transitions, but do not invent a second status ledger. In this repository the
backlog's stored states are `queued`, `active`, `blocked`, `deferred`, `complete`, and `cancelled`.
Readiness is derived: a queued phase whose prerequisites are complete is displayed as ready, and
“ready for review” is a handoff condition, not a stored state. `active` means someone is working
within declared scope. `complete` means acceptance conditions were actually checked and results
recorded. `blocked` and `deferred` name both the cause and the condition for resumption; neither is
a synonym for forgotten. `GOV-002` defines the authoritative transition diagram and schema.

At every meaningful pause, update the phase or session record with: what changed, checks run and
their actual results, decisions made, risks discovered, unresolved items, and the next action. This
is the continuity layer that lets a different agent resume safely without repeating discovery.

## 6. Verification, risk, and reversibility

Plan verification as work, rather than appending it at the end. Combine the checks appropriate to
the change: unit and integration tests, static checks, contract checks, manual acceptance review,
security or privacy review, migration validation, and production or rollout observation.

For each meaningful risk, write the early signal, mitigation, and recovery path. Pay particular
attention to irreversible actions, data changes, permissions, external side effects, and interface
breaks. A reversible rollout, feature flag, backup, or explicit stop gate is often part of the
implementation—not operational decoration.

Do not hide a failed check by retrying until it passes. Record the result, diagnose the cause, and
either fix it within scope or surface the decision needed to proceed.

## 7. Agent-ready execution rules

Agentic work benefits from a few explicit safeguards:

- Ground claims in inspected source, observed output, or cited decisions; label proposals as
  proposals.
- Give each agent bounded ownership, expected inputs and outputs, and a verification responsibility.
- Preserve the user’s authority for decisions that change scope, external commitments, money,
  privacy, or irreversibility.
- Prefer small, reviewable changes and checkpoints over a long opaque implementation run.
- Treat interfaces from unmerged peer work as provisional unless a shared contract says otherwise.
- Capture discoveries that are outside the phase as follow-up work instead of silently expanding
  the active plan.

An agent should be able to stop at any point without making the next agent reconstruct its intent
from a diff alone.

## A reusable phase summary

This is a portable, human-readable summary—not an execution ledger. In this repository, create or
update the actual phase in `docs/09-backlog/backlog.yaml` using `GOV-002`'s schema. In particular,
the authoritative record also names the plan and sources, priority, systems, deliverables,
`next_action`, verification, and (when needed) `blocked_reason` and `resume_when`.

```md
## Phase: <short outcome>
Status: queued
Owner: <role or agent>
Depends on: <phase, artifact, or decision>
Scope: <systems/files and boundaries>

Goal
<observable outcome>

Acceptance
- <success condition>
- <failure/negative condition>

Implementation
1. <small safe step>
2. <small safe step>

Verification
- <command or inspection> → <expected result>

Risk and recovery
- <risk> → <signal, mitigation, rollback or stop condition>

Handoff
- <evidence location, contract changes, deferred item, exact next action>
```

Adapt this summary to the project’s authoritative backlog and document schemas; do not create a
second competing status ledger.

## Plan-quality review before execution

Before implementation begins, review the plan adversarially. In this repository, use the
three-altitude review procedure (`GOV-018`): it reviews the plan, each queued phase, and every
later-added phase, then records and dispositions each finding. The reviewer should look for missing
requirements, unverifiable claims, phase overlap, hidden dependencies, invalid current-state
assumptions, unsafe migrations, unowned decisions, and absent failure paths.

The plan is ready when its outcome, boundaries, phase ownership, dependencies, acceptance evidence,
and recovery paths are coherent together—not when every heading has text beneath it.

## What this reference does not do

This reference does not replace the repository’s governance protocol, backlog protocol, decision
records, security practices, or owner approval. It does not prescribe one planning tool or require
every small fix to have a large multi-phase plan. Scale the artifact to the risk and duration of the
work, while retaining enough context and evidence for safe continuation.
