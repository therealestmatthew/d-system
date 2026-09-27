# Coordinator

A coordinator is a session that drives many units of work to completion through dispatched agents
while holding almost nothing in its own context. This document is for the planning session that
writes a coordinator prompt. `prompt-packs.md` and `research-packs.md` govern the pack; `batches.md`
governs the batch the coordinator runs.

## 1. Establish the constraints first

Before proposing any batch size, order or loop shape, the design answers these questions from the
governing text, not from memory:

- Who may mark a unit done, and may the coordinator (`backlog-protocol.md`, section 10)?
- What is the concurrency cap, and are claims released or accumulated during the run?
- What collides, computed with the real collision function (`backlog-protocol.md`, section 7)?
- Which gates wait for a human?
- What does the protocol mandate for branches, worktrees and hand-off (`protocol.md`, sections 11
  and 12)?

## 2. The completion question

- Claims are released by completion, not by integration. A coordinator whose units cannot reach
  complete during the run accumulates claims and stalls at `max_active`.
- When units cannot be completed during the run, a batch holds at most `max_active` units, all
  mutually non-colliding and dependency-independent.
- The first design question is whether the coordinator can finish anything. Completion needs the
  owner's yes at integration for every unit. The design secures that or plans for hand-off; it
  never assumes an authority nobody granted.

## 3. Partitioning

- Batches are dependency-closed: nothing in a batch depends on a later batch.
- Order within a batch is a valid build order.
- The partition is verified by script against the backlog, and the prompt states that it was
  verified and how.
- Every unit appears exactly once; coverage is confirmed, not only correctness.
- Each exclusion is named with its reason and with what the coordinator must not do about it.
- Batch size is fitted to context and wall-clock time once completion is settled. The first batch
  is the evidence for the size, and the close-out records the answer.

## 4. One worktree per unit

- Every unit gets its own branch and worktree, named as `protocol.md` section 11 names them. A
  coordinator invents no naming scheme.
- A shared batch worktree fails: integration removes the worktree and deletes the branch, a diff
  stops being the unit, a failed unit entangles the next, and peers cannot read what is being
  worked.
- Each worktree has its own environment and an explicitly chosen port.
- The coordinator gets no worktree. Its repository writes are claim and completion commits on the
  integration branch. Session records belong in each unit's worktree, and its tracker is ignored
  working state.

## 5. Batch approval and questions at the open

- When the coordinator runs an owner-approved batch that names its phases in build order, that
  approval is the claim approval for those phases and stands in for the per-claim question of the
  `session-start` skill. `max_active` and the Conflicts column are still checked numerically before
  each claim, and a phase a peer holds is skipped untouched.
- Before claiming anything, a read-only reconnaissance agent per unit runs in parallel. Each
  reports what its unit requires, whether its acceptance is observable, and anything that would
  make a careful person decline to start it.
- The questions a per-claim gate would raise go to the owner as one batch before the first claim,
  with the recommendation first in each question.
- After that, the coordinator stops mid-batch only when a unit looks genuinely wrong (an acceptance
  condition nothing can verify, a missing deliverable, an undeclared dependency) or when an
  obstacle survives resolution.
- Every other question accumulates to the close-out, ranked by how much its answer changes
  (`reporting.md`).
- A blocker goes first to a resolver agent, which gets the blocker, the evidence, the unit's
  definition and the governing documents. Only a blocker it cannot settle reaches the owner, with
  its findings attached.

## 6. Deviations and the decision record

- Every deviation from a governing document is named in the prompt: what it displaces, why, and
  under whose authority. The test is whether an agent reading the displaced document mid-run would
  think the coordinator is misbehaving.
- Two instructions that together override a documented gate are a deviation, and they are written
  down as one.
- Before proposing a decision, the design searches the decision record for the rule it would
  change and puts the prior ruling in front of the owner. The new entry names the clause it
  displaces.
- The design looks for an earlier exception of the same shape and reuses its conditions.

## 7. The templates are the prompts

- A coordinator with no delegation pack carries dispatch templates. It fills a template from a
  unit's own fields and never composes a dispatch freehand. A unit that cannot fill a template is a
  blocking finding.
- Templates work only where unit definitions are rich enough to serve as specifications.
  Otherwise, a pack is written (`prompt-packs.md`).

## 8. Context discipline

- The coordinator never reads a plan, requirement or unit body. It reads only its tracker, its
  decisions file, returned summaries and the command output it must verify.
- Every return is bounded to a verdict, counts and the path of the file written, about fifteen
  lines. Detail goes in that file.
- A dispatch carries only the unit it concerns, never the pack or the queue.
- An agent that stops without writing its file is truncated. It is resumed, never restarted.

## 9. Cost and verification

- The model tiers, the fix-cycle cap and spend reporting are those of `prompt-packs.md` section 3.
- The descope ladder is decided before the run. Stopping cleanly mid-batch with the tracker current
  beats finishing degraded.
- The coordinator runs each unit's verification commands itself and keeps the real output. An
  agent's claim of a pass is not evidence.
- Validator inputs and commit-before-validate are as in `prompt-packs.md` section 3.
- A schema or test is never edited to make a failing check pass. A schema that rejects a change is
  saying the change is wrong.
- The independent adversarial review is a completion condition (`backlog-protocol.md`, section 10).

## 10. Review the coordinator prompt

A coordinator prompt written outside the prompt-pack or research-pack pipeline is adversarially
reviewed against the repository before it is committed. The review asks whether the authority it
invokes exists, whether the partition is real, whether the loop survives the actual commands, and
what it silently gets wrong. A prompt produced by that pipeline follows `prompt-packs.md` section 1,
stage 7.

## 11. Idempotence and the tracker

- The same prompt runs every batch, and every re-run is a resume. Only the batch identifier changes
  between runs.
- State lives in a tracker file, not in session memory. A dead session resumes from it.
- The coordinator is the tracker's only writer. Agents write only their own evidence files.
- Ignored evidence is copied out before a worktree is removed (`protocol.md`, section 11).
- A run never stops holding an unrecorded claim. The phase is handed off under
  `backlog-protocol.md` section 11, or the held claim is reported to the owner.

## 12. Checklist

1. Answer the constraint questions (section 1).
2. Search the decision record.
3. Settle the completion question before sizing.
4. Partition, and verify the partition by script.
5. Draft the prompt: a worktree per unit, no coordinator worktree, questions at the open, the
   resolver first, templates, the tracker.
6. Name every deviation.
7. Record new authority, naming the clause it displaces.
8. Review the prompt adversarially.
9. State which parameters the first run tests, and record the answer.
