---
schema_version: 1
id: doc-coordinator-protocol
code: GOV-013
title: Coordinator protocol — designing a session that drives many units of work to completion
kind: governance
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-22'
systems: [sys-backlog, sys-governance, sys-realization]
depends_on: [doc-prompt-pack-protocol, doc-research-protocol, doc-backlog-decisions, doc-build-coordinator]
---

# Coordinator protocol

How to design a **coordinator** — a session that drives many units of work to completion through
dispatched agents, holding almost nothing in its own context.

`GOV-008` governs the two-session methodology for multi-agent builds, from planning through the
pack audits to the kick-off record. `GOV-009` does the same for research campaigns. **This governs
the design of the coordinator that executes them**, and it is written for the planning session that
has to produce a coordinator prompt, not for the coordinator itself.

It was extracted from writing [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) on
2026-09-16, and every rule below earns its place from something that actually went wrong or nearly
did in that exercise. Where a rule cites an incident, the incident is the argument.

[GOV-016](GOV-016-batch-orchestration-protocol.md) governs the artifact this design produces work
for: how a batch is composed, verified, sequenced into stages, declared runnable and selected. Read
it when you are composing a batch; read this when you are designing the coordinator that runs one.
The *Partitioning* section below is the design-time view of what `GOV-016` then governs as a
durable table.

## Establish the constraints before designing anything

**The partition was designed twice.** The first attempt grouped phases into contiguous batches of
five to seven and was coherent, defensible and wrong — because it was drawn before anyone had read
the rules that govern claiming and completion. Reading them afterwards invalidated it outright.

Before proposing any batch size, ordering or loop shape, answer these **from the governing text,
not from memory**:

1. **Who may mark a unit done, and may the coordinator?** If it may not, the coordinator cannot
   complete anything, and everything below changes.
2. **What is the concurrency cap, and does the coordinator release units or accumulate them?**
3. **What collides with what?** Run the real collision function over the real candidates. Do not
   reason about it from the data model.
4. **Which gates stop the run and wait for a human?** Enumerate every one. A gate discovered
   mid-design is a redesign.
5. **What does the protocol already mandate about branches, worktrees and hand-off?** Coordinators
   do not get their own conventions.

Answering these costs one research dispatch. Not answering them cost a full redesign.

## The completion trap

This is the single fact that most shapes a coordinator's design, and it is not obvious:

> **A coordinator that cannot mark units complete accumulates claims, and stalls at the
> concurrency cap.**

Claims are released by completion, not by merging. If completion requires a human and the human is
not in the loop, the coordinator can start `max_active` units and then nothing. Batch size is
capped at the concurrency limit, and every unit in a batch must be mutually non-colliding **and**
dependency-independent — a far scarcer set than a queue prefix.

So the first design question is not "how big is a batch" but "can this coordinator finish
anything". If it cannot, either secure the authority or design for hand-off rather than completion.
Do not design a batch that silently assumes an authority nobody granted.

## Partitioning

- **Batches are dependency-closed.** Nothing in a batch depends on anything in a later batch.
- **Order within a batch is a valid build order.** A unit never precedes something it depends on.
- **Verify the partition programmatically against the source of truth**, and **state in the prompt
  that it was verified and how**. A hand-checked partition of thirty items is a partition nobody
  has checked, and a reader cannot tell the two apart unless the prompt says.
- **Every unit appears exactly once.** Confirm coverage, not just correctness — a dropped unit is
  invisible until the queue ends short.
- **Name exclusions explicitly, with the reason and the instruction.** If a unit is skipped, the
  prompt says which, why, and what the coordinator must *not* do about it — leaving it in the queue
  is usually right, and the coordinator must be told so or it will try to tidy it.
- Size the batch to the coordinator's context and wall-clock, once the completion question is
  settled. **The first batch is the evidence for the size**; say so in the prompt and record the
  answer in the close-out.

## One worktree per unit, never one per batch

**Every unit of work gets its own branch and worktree, named as the protocol names them.** A
coordinator does not invent a naming scheme.

A shared batch worktree fails four ways, and the first is fatal:

1. **The hand-off procedure deletes it.** `AGENTS.md` bundles `git worktree remove` and
   `git branch -d` into the same action as the merge. A coordinator following the protocol
   literally removes the shared worktree after the first unit merges, leaving the second nowhere to
   build. Nothing warns it; the procedure simply does what it says.
2. **Diffs stop being self-evident.** `git diff dev..branch` is only clean because every prior unit
   already merged — a correctness property that depends on history rather than on structure. One
   branch per unit makes the diff *be* the unit.
3. **Failure entangles.** A rejected or half-built unit leaves commits interleaved with the next
   unit's on a shared branch. Per-unit, you abandon one branch and the rest are untouched.
4. **Peers cannot read it.** `agent/<unit-id>` tells concurrent sessions what is being worked;
   `agent/build-b1` tells them nothing.

Each worktree gets its own environment and, where it runs a server, **its own explicitly chosen
port** — never a default and never a peer's. The only cost is environment setup per unit, which is
the cheapest item in any loop whose units are real work.

**The coordinator itself gets no worktree.** Its repository writes are claim and completion commits,
which must land in the primary checkout anyway, and session records, which belong in each unit's
worktree. Its tracker is gitignored working state, not repository content. A coordinator worktree
holds nothing that matters and invites work to be done in the wrong place.

## Questions at the open, not one per unit

A per-unit human gate defeats an unattended run. A coordinator that never asks produces work built
on guesses. The resolution is to **move the asking forward**:

- Before claiming anything, dispatch a **reconnaissance agent per unit, in parallel, read-only**.
  Each reads its unit and the documents it points at, and reports what the unit requires, whether
  its acceptance is observable, and **anything that would make a careful person decline to start
  it**.
- Put everything they raise to the owner in **one batch**, recommendation first in each option.
  This is the run's one scheduled interruption.
- Then run. Afterwards the coordinator stops only when a unit looks genuinely wrong — an acceptance
  condition nothing can verify, a missing deliverable, an undeclared dependency — or when a blocker
  survives the step below.

Everything else accumulates to the close-out, ranked by how much each answer changes.

## A blocker goes to an agent before it goes to the owner

When the run meets an obstacle, **dispatch a resolver first**. Give it the blocker, the evidence,
the unit's definition and the governing documents, and ask it to establish what is actually true
and what the options are.

Only a blocker the resolver cannot settle reaches the owner, and it arrives with the resolver's
findings attached. Most apparent blockers are a misreading of a governing document, and an agent
can settle those for the cost of one dispatch rather than the cost of the owner's attention and a
stalled run.

## Name every deviation; never override a rule silently

A coordinator prompt will deviate from some governing document. That is acceptable. **Deviating
without saying so is not.**

Every deviation in the prompt states what it displaces, why, and under whose authority. The test is
whether an agent reading the displaced document mid-run would conclude the coordinator is
misbehaving — if so, the prompt must say the document is knowingly superseded, or the agent will
stall or escalate on a rule that no longer applies.

`PROMPT-036` names four: the coordinator claims and its templates are the prompts (two clauses of
`GOV-008` displaced together); the per-unit claim gate is covered by batch approval; the two
completion documents are superseded; and completion authority itself rests on a decision-record
entry rather than on the command that previously held it.

**This document carries one of its own.** *Review the coordinator prompt before it runs*, below,
makes adversarial review mandatory. `GOV-008`'s stage-7 gate and `GOV-009`'s equivalent make it
"optional and run only if the owner specifically requests it", on the grounds that an earlier pack
audit covered the substance. A coordinator prompt written **outside** that two-session methodology
has had no such audit, so the justification does not reach it. Where a coordinator prompt is
produced by `GOV-008`'s or `GOV-009`'s full pipeline, their optional-review clause governs and this
one yields.

**The related failure is the silent stop-gate.** A draft of `PROMPT-036` had the coordinator claim
on a numeric check while the claim command required a human gate that "stops until answered". Both
instructions were defensible; together they silently overrode a documented gate. An adversarial
review caught it. Write deviations down and there is nothing to catch.

## Check the decision record before proposing a decision

**A new decision may reverse one already taken.** `PROMPT-036` needed coordinator completion; the
decision record already held a ruling, made the day before for that same pipeline, that completion
"remains owner-invoked per phase, batched but never automated".

Search the decision record for the rule you are about to change, and **put the prior ruling in
front of the owner before they rule again**. They may have forgotten it; they may have meant it.
Either way the new entry must name the clause it displaces, so a future reader finds the
supersession rather than a contradiction.

Look also for a **precedent**: the same record held two prior exceptions of exactly the shape being
requested, each with conditions attached. Reusing a proven pattern beats inventing one, and the
conditions are usually why it was safe.

## The templates are the prompts

`GOV-008` says a coordinator authors no prompts, and that a missing prompt is a blocking finding
rather than something to improvise. A coordinator with no pre-written delegation pack appears to
violate this by necessity.

It does not, if the prompt carries **dispatch templates** and the unit's own definition supplies
their content. The coordinator instantiates a template against a unit's fields; it never composes a
dispatch freehand. **If a unit's definition cannot fill a template, that is the blocking finding**
`GOV-008` intends — and it is a genuine signal that the unit is underspecified.

This only works where unit definitions are rich enough to serve as specifications. Where they are
not, write the pack.

## Context discipline is the coordinator's whole job

A coordinator exists so that the expensive reading happens somewhere other than the session holding
the plan. If it starts reading units itself, it becomes a worker with extra steps and runs out of
context halfway through the batch.

- **The coordinator never reads a plan, a requirement or a unit body.** Agents read; it routes. It
  opens its tracker, its decisions file, agents' returned summaries, and the exact command output it
  must verify itself.
- **Bound every return.** Agents report a verdict, counts, and the path of the file they wrote —
  fifteen lines is a workable cap. Detail goes in a file the coordinator opens only if it must.
- **Inject selectively.** A dispatch carries the unit it concerns and nothing else — never the whole
  pack, never the whole queue. `GOV-008` and `GOV-009` both make this a standing rule; it matters
  more for a coordinator, because it dispatches many times.
- **An agent that stops with no file written is truncated, not finished.** Resume it; never restart
  it. A fresh agent re-pays the entire reading bill.

## Cost protocols

Inherited from `GOV-008` and `GOV-009`, and restated because a coordinator multiplies them by the
number of units:

- **Haiku for mechanical gates. Sonnet is the standard model for judgment work. Opus is never
  pre-assigned**, and is used at most as a single documented escalation for a whole run, only when
  it is genuinely necessary.
- **Cap the fix cycles** — two per unit is the standing figure. What survives them is reported, not
  looped on. An unbounded fix loop is how a coordinator spends a batch's budget on one unit.
- **Have a descope ladder before you need one.** Decide in advance what gets dropped when the runway
  runs short — which units, which optional checks — so the decision is not made under pressure at
  the end. Stopping cleanly mid-batch with the tracker current always beats finishing degraded.
- **Report spend posture in the close-out**: loop counts, any escalation, wall-clock against the
  runway. A coordinator that cannot say what it spent cannot be sized better next time.

## Verification discipline

- **The coordinator runs the unit's verification commands itself and keeps the real output.** An
  agent's claim that a command passed is not evidence that it passed.
- **Validators receive the diff, the requirement text and the commands — never the creator's
  rationale or report.** A validator told why the code is right reviews the explanation.
- **Commit before validate.** Truncated agents are **resumed, never re-run**.
- **Never edit a schema or a test to make a failing check pass.** A schema that rejects a change is
  telling you the change is wrong. In this exercise an agent was instructed to set a value a schema
  forbade; it reverted and reported instead of relaxing the constraint, which is the only reason a
  bad instruction did not become a repository-wide change.
- **An adversarial review is a completion condition, not a courtesy**, wherever a coordinator holds
  completion authority it did not previously have. It is what the owner's synchronous judgement was
  traded for.

## Review the coordinator prompt before it runs

A coordinator prompt is high-leverage: a defect in it is paid once per unit. **Have it adversarially
reviewed before it is committed**, against the repository rather than against its own claims —
does the authority it invokes exist, is the partition real, does the loop survive contact with the
actual commands, and what does it silently get wrong.

`PROMPT-036`'s review returned two blockers, two majors and a minor. The worst would have left the
second unit of every batch with nowhere to build.

## Idempotence and the tracker

- **The same prompt runs every batch, and every re-run is a resume.** Only the batch identifier
  changes between runs.
- **State lives in a tracker file, not in the session's memory.** The coordinator re-reads it
  instead of remembering, and a dead session resumes from it with nothing lost.
- **The coordinator is the tracker's only writer**; agents write only their own evidence files, so
  no two writers ever share a file.
- **Copy gitignored evidence out before removing a worktree.** A merge never carries it and the
  removal destroys it.
- **Never leave a unit claimed-but-unbuilt without recording it.** That is a lock nobody can see the
  reason for. If the run stops holding a claim, say so explicitly so the owner can release it.

## Checklist for a coordinator-planning session

1. Research the governing documents first; answer the five constraint questions above from the text.
2. Check the decision record for a rule you are about to change, and for a precedent to reuse.
3. Settle the completion question before sizing anything.
4. Partition, and verify the partition programmatically.
5. Draft the prompt: one worktree per unit, no coordinator worktree, questions at the open, resolver
   before escalation, templates as prompts, tracker as memory.
6. Name every deviation and what it displaces.
7. Record any new authority in the decision record, naming the clause it supersedes.
8. Have the prompt adversarially reviewed, and integrate the findings before committing.
9. Say in the prompt which of its parameters the first run is meant to test, and record the answer.
