---
schema_version: 1
id: doc-session-build-coordinator-commissioned
code: SESS-2026-09-16-06
title: Build coordinator commissioned and the queue partitioned into six batches
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-build-coordinator, doc-coordinator-protocol, doc-backlog-decisions, doc-prompt-pack-protocol, doc-session-phase-review-remaining-decisions]
---

# Build coordinator commissioned and the queue partitioned into six batches

Unclaimed, owner-directed work following `SESS-2026-09-16-04` and `-05`, which reviewed and
enhanced the twenty-nine queued phases. This session commissioned the coordinator that will build
them: [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md), plus the governance decision it
depends on.

## The partition

Twenty-nine phases in six dependency-closed batches of five (the last, four). Each batch's internal
order is a valid build order, and nothing in a batch depends on anything in a later one — verified
programmatically against `backlog.yaml`, not asserted.

`phase-lit-09` is excluded by the owner's instruction: it belongs to the literature-review campaign,
has its own coordinator and resume command, and conflicts with `phase-lit-07` while that is active.
It stays in `next_up`; the coordinator simply never claims it.

## What the constraints forced

The partition was designed twice. The first attempt used contiguous queue prefixes of five to seven
phases. Research into the governing documents then established three facts that broke it:

- `/session-close` was owner-only and the only path to `status: complete`.
- `max_active` is 3 (`src/governance/backlog.py:55-64`).
- A coordinator that cannot complete phases therefore **accumulates claims** and stalls at three.

Under those rules a batch could only ever be three mutually non-conflicting, dependency-independent
phases — and `collisions()` showed how scarce those are: of the twelve then-claimable phases, most
pairs collide on a shared system or a shared deliverable path. The owner's pre-approval of
completion removed the cap, which is what let the partition return to following the queue.

## The governance decision

`GOV-003` gained *Coordinator completion replaces owner-invoked /session-close*, which **supersedes
the session-close clause** of the 2026-09-16 master-plan ruling — "no standing owner-only rule is
delegated: `/session-close` remains owner-invoked per phase, batched but never automated". That
clause was recorded for this very pipeline, and the owner was shown it before ruling against it.
The same ruling's other half stands untouched: `next_up` ranking remains the owner's.

The replacement follows the demo track's proven pattern rather than plain pre-approval: a
coordinator may complete a phase only after green verification with output captured, an independent
adversarial review resolved, and owner-approved integration. Unlike the demo and workbench
exceptions, each confined to a phase prefix, this one is **repository-wide and standing** at the
owner's direction.

A second entry followed the same shape: the per-phase claim gate in `/session-start` step 2 is
covered by the owner's approval of the batch, with questions batched before the first claim instead
of raised phase by phase, and **a blocker given to an agent to resolve before it halts the run**.

The entry names the two documents that now contradict it — `.claude/commands/session-close.md`'s
owner-only section and the checkpoint skill's never-complete rule. **Neither was edited.** Their
wording is a decision for the owner, and `PROMPT-036` tells the coordinator they are knowingly
superseded so it does not stall on reading them.

## The adversarial review

`PROMPT-036` was reviewed before being committed: 2 blockers, 2 majors, 1 minor, all integrated.

- **Blocker.** The draft put a whole batch on one shared branch and worktree, contradicting
  `AGENTS.md:249` and `session-start.md:103-104` — both say the branch is *always* `agent/<phase-id>`
  and the worktree *always* `../d-system-worktrees/<phase-id>` — and colliding with the hand-off
  step that bundles `git worktree remove` and `git branch -d` into the merge. A coordinator
  following the protocol literally would have deleted the worktree after the first phase and left
  the second with nowhere to build. The owner independently raised the same question. Fixed by
  going per-phase, which dissolves the conflict entirely: the bundled cleanup then works as written.
- **Blocker.** The draft claimed each phase on a numeric check while `/session-start` step 2
  mandates an `AskUserQuestion` gate that stops until answered — silently overriding a documented
  stop-gate. Fixed by the owner's ruling and the `GOV-003` entry above, and stated in the prompt as
  a deviation rather than left implicit.
- **Major.** The prompt never mentioned the two documents `GOV-003` had flagged as contradicting
  it, so an agent reading them mid-run could have stalled. Now named explicitly.
- **Major.** Unlike both precedent coordinators, it never required reading `AGENTS.md` or `GOV-006`
  — while depending on the former's hand-off procedure. Now the first preflight step.
- **Minor.** Preflight lacked `git status --short` and `git branch --show-current`. Added.

The reviewer verified the batch table programmatically and found it sound: all twenty-nine
non-`phase-lit-09` entries appear exactly once, in `next_up` order, every phase `status: queued`,
every dependency resolving to an earlier or same-position phase.

## Four stated deviations

`PROMPT-036` records each rather than leaving it to be discovered: the coordinator claims (against
`GOV-008`'s "claims nothing", written for packs with sub-orchestrators this run does not have); the
dispatch templates are the prompts and are instantiated against each phase's own reviewed backlog
entry rather than composed freehand (against "authors no prompts"); the claim gate; and the two
superseded completion documents.

## Verification

- `Governance OK: 31 systems, 263 documents, 25 memories, 278 backlog phases`
- `580 passed, 2 warnings`
- `check_no_private_content: OK (670 tracked files, 0 identifiers checked)`, staged

## The coordinator protocol

The design knowledge behind `PROMPT-036` was extracted into
[GOV-013](../08-governance/GOV-013-coordinator-protocol.md) at the owner's request, so a future
coordinator-planning session inherits it rather than rediscovering it. It carries the constraint
questions that must be answered before any partition is drawn, the completion trap, the four ways a
shared batch worktree fails, questions-at-the-open, resolver-before-escalation, the
name-every-deviation rule, the check-the-decision-record rule, context and cost discipline, and a
nine-step checklist.

It was fact-checked before commit: 0 blockers, 4 majors, 5 minors — no false claims, every
quotation and all four cited incidents substantiated against the record. The majors were worth the
pass:

- **It violated its own rule.** `GOV-013` makes adversarial review of a coordinator prompt
  mandatory, while `GOV-008`'s stage-7 gate and `GOV-009`'s equivalent make it "optional and run
  only if the owner specifically requests it" — and `GOV-013` had not named that as a deviation,
  two sections after requiring every deviation be named. Now named, with the reasoning: the optional
  clause rests on an earlier pack audit having covered the substance, which does not reach a
  coordinator prompt written outside that methodology. Where one *is* produced by `GOV-008`'s full
  pipeline, its clause governs and `GOV-013` yields.
- **It required of `PROMPT-036` two things `PROMPT-036` did not do** — state that the partition was
  verified programmatically, and name which parameter the first run tests. Both claims lived only in
  this session record. Added to the pack, which is where a reader looks.
- **Cost and context discipline were in the pack but never extracted**, so a planning session
  reading only `GOV-013` would have missed the model-assignment rules, the fix-cycle cap, the
  descope ladder and selective injection. Both sections added.

The minors were a title breaking the siblings' convention, a gloss that undersized `GOV-008`, "days
earlier" where the record says one day, an unexplained deviation count, and the omitted
fixed-port-per-worktree rule. All corrected.

## Unresolved

- `.claude/commands/session-close.md` and `.claude/skills/checkpoint/SKILL.md` still tell an agent
  it may never complete a phase. `GOV-003` now says otherwise, repository-wide. The owner has been
  offered the choice and has not yet ruled on their wording.
- Batch 1 has not been run. The five-per-batch size is an estimate of what one coordinator can
  carry; the first run is the evidence that confirms or corrects it.
