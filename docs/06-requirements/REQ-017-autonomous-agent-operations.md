---
schema_version: 1
id: doc-autonomous-agent-operations-requirements
code: REQ-017
title: Autonomous agent operations requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-adr-multi-agent-concurrency, doc-prompt-pack-protocol]
---

# Autonomous agent operations requirements

## Observed problem and scope

Every agent workflow in this repository starts in a chat session and dies with it. There is no way to
trigger work from outside one, no record that survives an interruption, no process that drains queued
work, and — most consequentially — nothing that authorises what an agent may *do* at runtime.

Five ideas describe the missing layer, deliberately decomposed from one proposal so each could be
evaluated alone. All four partition analysts placed them in one programme, control included, which is
the strongest membership signal in the set because it cannot be inherited framing.

1. **No external trigger protocol exists at all.** The repository has owner-invoked commands and
   planned agent workflows, and no way for a filesystem event, a schedule, a webhook or a CLI call to
   start one (`000028`).

2. **Partial progress is lost.** Work either finishes in one conversation or it does not survive.
   `000029` names the case that produced it: a session limit ended one of that session's own agents
   mid-task. There is no run record carrying a correlation id, the triggering payload, the model and
   tool versions, a context-pack hash, budget, timeout, retries, checkpoints or disposition — so
   nothing can resume without repeating side effects already applied.

3. **Nothing drains a queue or notices a stalled run.** No supervised process enforces concurrency
   limits or quiet hours, heartbeats its progress, or marks work abandoned for review rather than
   silently retrying a run whose side effects may be half-applied (`000030`).

4. **Nothing authorises an agent's actions at runtime.** The repository governs documents and phase
   claims — the backlog lock table, the concurrency protocol — but no capability set bounds what an
   agent may actually do, and no approval path carries scope, reason, expiry and an immutable
   decision. Denied capabilities must be enforced at the tool boundary, not described in a prompt an
   agent can misread (`000031`).

5. **A heavier coordination proposal exists and is already ruled on.** `000020` proposes an MCP server
   as the authoritative interface for documents, claims and worktrees, a vector database behind it,
   and a Librarian agent curating context bundles. The owner ruled on 2026-09-13: **kept, sequenced
   behind `000128`** — build the light `_tmpagent/` mechanism first, revisit only if it proves
   insufficient. This requirement carries that ruling rather than re-opening it.

**This programme is the most speculative in the partition**, and the honest statement of its evidence
base is that almost all of it is anticipated rather than observed — with one exception. The unattended
run of 2026-09-15 executed ten programme-finalize phases with no chat session driving each step, using
none of this infrastructure: no gateway, no ledger, no worker, no broker. What it used instead was a
person granting scoped advance authority in writing, and an agent recording every departure. That is
evidence about which of the five pieces is actually load-bearing, and `R01` is written from it.

This requirement covers the autonomous agent operations programme (`P5`). It does **not** cover
retrieval or the knowledge graph — that is `P6` — nor how agents are instructed and scoped, which is
`P4`. The boundary is that `P4` designs the agent, `P5` runs it with nobody watching, and `P6` gives
it something to read.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The capability broker exists and denies a capability *before* any trigger, ledger or worker can start unattended work. | Attempt an unattended run before the broker is in place and confirm it is refused. This is the `000031` gate, and the ordering is the requirement: a gate built after the things it gates has never gated anything. |
| R02 | Every agent run carries an explicit, narrow capability set — named actions, not a role. | Read a run's capability set for specific named actions such as repository read, source mutation, external network, publication. A set naming a role rather than actions does not satisfy this. |
| R03 | A denied capability is enforced at the tool boundary, and an agent that attempts it is stopped rather than trusted not to try. | Give an agent a prompt instructing it to use a denied capability and confirm the attempt fails at the boundary. A denial enforced only in prompt text fails this row — that is the distinction `000031` exists to draw. |
| R04 | Anything sensitive routes through an approval request carrying scope, reason, expiry and an immutable decision record. | Request one and read the record for all four. Confirm the decision cannot be edited after the fact. Confirm an expired approval is not honoured. |
| R05 | A trigger gateway accepts filesystem, scheduled, webhook and CLI events and normalises each into one event shape. | Fire one of each and confirm all four produce an event carrying source, payload hash, received time and requested workflow. |
| R06 | The same trigger delivered twice produces one run, not two. | Deliver a duplicate payload and confirm deduplication by payload hash. A gateway that runs work twice on a retried webhook is worse than no gateway. |
| R07 | The gateway is provider-neutral and does not hard-code a model or tool. | Read the interface for provider-specific names. `000028` makes this explicit, and the separation from the execution layer is what makes it checkable. |
| R08 | Every run is persisted with a correlation id, the triggering payload's hash, model and tool versions, a context-pack hash, budget, timeout, retry count, checkpoints, produced artifacts and final disposition. | Read a completed run's record for all ten. A missing field is a defect; this list is `000029`'s own, reproduced rather than summarised, with model and tool versions counted as the single field it writes them as. |
| R09 | An interrupted run resumes without repeating completed side effects. | Interrupt a run mid-way, resume it, and confirm the side effects of completed steps occurred exactly once. Resuming by re-running from the start satisfies neither this row nor `000029`. |
| R10 | The execution adapter is provider-neutral, so the ledger does not encode one model's shape. | Read the adapter for hard-coded provider names. Confirm a second provider could be added without changing the run schema. |
| R11 | A supervised worker drains queued runs and enforces concurrency limits and quiet hours. | Queue more work than the limit and confirm the excess waits. Set quiet hours and confirm work queued inside them does not start. |
| R12 | A run whose heartbeat goes stale is marked abandoned for review, never silently retried. | Kill a worker mid-run and confirm the run is marked abandoned and surfaced, not restarted. `000030`'s point is that a half-applied run must not be retried blind. |
| R13 | Killing and restarting the worker resumes queued work correctly. | Kill it, restart it, and confirm queued runs proceed and in-flight runs are handled per `R12`. |
| R14 | There is a review surface for abandoned runs, and an abandoned run can be resolved from it. | Abandon a run, find it on the surface, and resolve it. An abandoned run nothing lists is indistinguishable from a lost one. |
| R15 | `000020` is revisited only after `000128`'s light mechanism has shipped and been used, and the revisit records whether it proved insufficient with evidence. | Read the revisit for named cases where the `_tmpagent/` mechanism fell short, or for a statement that it did not. "Revisit only if the light version proves insufficient" is the owner's ruling of 2026-09-13; a revisit that re-argues the decision without the evidence has not honoured it. |
| R16 | Nothing in this programme duplicates the claim protocol that already works. | Confirm no component becomes a second authority over phase claims. `backlog.yaml` is the lock table and the governance validator is the lock check; `000020`'s MCP proposal would replace both, which is part of why it is sequenced behind the light alternative rather than built. |

## What each requirement is not

**R01 is an ordering requirement, not a feature.** It is satisfiable only by building the broker
first. Every other row in this requirement describes a component; this one describes a sequence, and
it is the one the phase's acceptance names.

**R03 is the whole of `000031`'s value.** A capability model that describes denials in a prompt is a
longer prompt. The row asks for enforcement at the tool boundary because that is the only version an
agent cannot misread.

**R09 is not retry.** Re-running an interrupted workflow from the beginning is easy and wrong: the
side effects of completed steps happen twice. The row asks for resumption, which needs the
checkpoints `R08` persists.

**R15 does not license building `000020`.** The owner's ruling stands until evidence changes it, and
the row requires the evidence to be named. A revisit concluding "still not needed" fully satisfies it,
and is the expected outcome.
