---
schema_version: 1
id: doc-ephemeral-working-plans
code: PLAN-015
title: Ephemeral working plans and the working directory
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-governance-protocol]
---

# Ephemeral working plans and the working directory

> **Code note.** This document was first written as `PLAN-011`. That code had already been issued
> twice the same day — to a course production plan and a course extraction plan, both deleted — which
> [GOV-005](../08-governance/GOV-005-document-codes.md) forbids: a code reaching `dev` is never
> reused. `PLAN-011` is retired and this document carries `PLAN-015`.

## Context and scope

`docs/01-plans/` holds plans for building **this system**. On 2026-09-06 two plans in a row were
filed there that did not qualify, and the second failure is the instructive one.

The first was a plan to *produce* a git course — obviously a different product. The second replaced
it with a plan to *extract* that course into its own repository. That looked correct, because
extraction touches this repository directly. It was still wrong: extraction is a **one-off task**,
not a statement about how the system works. Once the course is gone, the plan describes nothing.

The distinction the first correction missed:

> A governed plan says **how the system should work** and outlives the work.
> An ephemeral plan says **how one task gets done** and dies with it.

Both attempts were shaped by the same pressure. `schemas/backlog.schema.json` requires every phase to
name a `plan`, so any work worth queueing appears to need a governed plan behind it. That pressure
manufactures governed documents for ungoverned work.

## Approach

> **Amended 2026-09-06 by the owner (`SESS-2026-09-06-10`).** Two rules below are reversed.
>
> **`_working/` is gitignored.** It was committed but informal; it is now local only. The absence of
> ceremony was always the point, and requiring a commit was ceremony. Two files predate this and stay
> tracked by explicit exception in `.gitignore`: `.gitkeep`, which anchors the directory, and one
> other file, which a since-completed phase named as a deliverable and followed in its
> `next_action`.
>
> **Nothing in `_working/` is deleted without the owner's explicit approval.** The rule below —
> *"Ephemeral plans are deleted, not archived"* — is withdrawn. Deleting is no longer the intended
> end state, and no agent may prune the directory as part of closing a phase. The reasoning that
> deletion prevents clutter still holds; what changed is who decides, and the answer is the owner,
> every time. The open question at the foot of this document is answered by the same rule: pruning
> happens neither on a schedule nor at phase close, but on request.
>
> **The consequence, stated plainly.** An ignored file does not reach a git worktree. Agents working
> in `../d-system-worktrees/` will not see task detail placed in `_working/`, because a sibling
> worktree receives tracked content only. This session demonstrated it: the brief, both audits and
> the synthesis that `_working/CODEX-PROMPT.md` instructed an agent to read existed solely in the
> primary checkout. A phase whose `next_action` points into `_working/` must therefore be run from
> the primary checkout, or its detail must be handed to the agent directly.
>
> **`_tmpagent/` answers that consequence.** Added the same day, tracked rather than ignored, it
> holds the files agents in sibling worktrees need to read. Its contract lives in
> [`_tmpagent/AGENTS.md`](../../_tmpagent/AGENTS.md): a file is read-only once active, every reader
> claims it by naming the branch or plan using it, every claim is closed by an explicit line, and a
> file is eligible for deletion only when no claim remains open. The ledger is
> `_tmpagent/claims.jsonl`, append-only in the same shape as `_data/ideas.jsonl`.
>
> The two directories now split cleanly by audience. `_working/` is the owner's — local, private to
> the primary checkout, deleted only on request. `_tmpagent/` is the agents' — shared, committed,
> and cleaned up through a lifecycle that records who still needs a file and where.
>
> *How phases reference ephemeral work* below still holds, with one routing change: task detail that
> an agent in a worktree has to read goes in `_tmpagent/`, not `_working/`.
>
> The claims contract is **convention, not code**. No test reads the ledger and no validator fails
> on it, which is a deliberate choice at one file and a debt if the directory grows. The failure
> mode to watch for is a ledger that stops matching reality; the fix then is a check, not a
> stricter rule.

**`_working/` is the home for ephemeral plans.** It is already committed but informal, and — verified
against `src/governance/__main__.py:209` — it is **not scanned by the governance audit**, which walks
only `docs/`, `plans/` and `brain/`. So a file there needs no code, no front matter and no catalog
entry. That is the property that makes it the right location: the absence of ceremony is the point,
not an oversight to be corrected later.

**The test for where a plan belongs.** Ask what remains true after the work finishes:

| If the document... | It belongs in |
|---|---|
| describes how the system should behave from now on | `docs/01-plans/` |
| describes steps for a task that will not recur | `_working/` |
| would need rewriting rather than deleting once done | `docs/01-plans/` |
| becomes meaningless once its subject leaves the repository | `_working/` |

Extraction fails every governed test: after the course leaves, the plan is not stale, it is *void*.

**Ephemeral plans are deleted, not archived.** Deleting is the intended end state. What survives is
the evidence, and it survives in places that already exist:

- the backlog phase, with its `completion_evidence`,
- the project record in `_data/projects/`,
- the commit history,
- a session record where the work warranted one.

Keeping a dead plan "for reference" recreates the clutter this plan exists to prevent. If something
in it deserved to outlive the task, it was a governed document in the first place and should be
promoted rather than retained.

**How phases reference ephemeral work.** A phase still requires a governed `plan`, and that
requirement stands — it is what stops the backlog filling with unanchored tasks. Phases doing
one-off work name **this plan**, because this plan is the policy under which such work is done. The
task detail lives in `_working/` and is linked from the phase's `next_action` or scope. The governed
document explains the *category*; the ephemeral file explains the *instance*.

## Deliverables

- This plan, as the standing policy.
- One ephemeral file — the extraction detail for a since-completed phase, moved out of
  `docs/01-plans/` and deleted once that phase finished.
- That phase re-anchored to this plan.

## Consequences

- `docs/01-plans/` stops accumulating documents that describe finished, non-recurring work.
- `_working/` becomes meaningful rather than a vague scratchpad, with a stated lifecycle.
- Anything in `_working/` may be changed without governance noticing or caring, which is the
  intended behaviour. It may **not** be deleted on that basis — see the amendment above.

## Open question

> **Answered 2026-09-06 by the owner.** Neither. `_working/` is pruned on request and only on
> request. The question below stands as the record of what was undecided and why.

Whether `_working/` should be pruned on a schedule or only when a phase closes. Left undecided — it
does not block anything, and a rule with no observed failure behind it is the sort of complexity
[PROMPT-003](../02-prompts/PROMPT-003-systems-review.md) exists to catch.
