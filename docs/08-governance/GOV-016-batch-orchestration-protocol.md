---
schema_version: 1
id: doc-batch-orchestration-protocol
code: GOV-016
title: Batch orchestration protocol — composing, sequencing and selecting batches of backlog work
kind: governance
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-backlog, sys-governance]
depends_on: [doc-coordinator-protocol, doc-build-coordinator, doc-backlog-decisions, doc-backlog-protocol]
---

# Batch orchestration protocol

How a set of queued backlog phases becomes a **batch** — composed, verified, sequenced, declared
runnable, selected by a coordinator, and closed.

`GOV-013` governs how to **design** a coordinator: the session that drives many units of work to
completion through dispatched agents. This governs the **artifact that coordinator consumes** and
the lifecycle around it. The division is deliberate — `GOV-013` is read by the planning session that
writes a coordinator prompt; this is read by whoever composes a batch and by the coordinator that
runs one.

The mechanism it governs has three parts:

- **The contract** — [`schemas/batch.schema.json`](../../schemas/batch.schema.json), which defines
  what a batch table may say.
- **The tables** — [`docs/09-backlog/batches/*.yaml`](../09-backlog/batches/README.md), one file per
  batch.
- **The coordinator** — [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md), which selects a
  table and builds it.

It was written on 2026-09-22, when the batch table was abstracted out of `PROMPT-036`. Before that
the partition lived inside the prompt, where it went stale the moment a batch was built or a phase
was ranked into the queue — and a stale table inside a prompt is invisible, because nothing
regenerates it and nothing checks it.

## A batch table holds no phase facts

A table records **grouping, sequencing and parallelism only**. Scope, acceptance, verification,
`systems`, `deliverables` and `depends_on` live in `backlog.yaml` and are never restated.

The one deliberate exception is `title`, copied into each entry so a table can be read without
opening the backlog. It is convenience, and the backlog wins wherever the two disagree. Every other
duplication is drift waiting to happen: the table is edited rarely, the backlog constantly, and
nothing reconciles them.

## Composition is the owner's

Composing a batch, and superseding one, is the owner's decision. A coordinator never composes a
table, never adds one, and never edits a composition — not to correct a defect it finds, and not to
absorb a phase that was ranked into the queue mid-run. A composition that turns out to be wrong is a
decision to put to the owner, exactly as a defect in a governed document is.

What a coordinator may write is the selected table's `status` and `updated` and nothing else. This
mirrors the backlog rule that an agent edits only its own phase's line: the narrowest possible write
on a shared file, so a concurrent reader can never be confused about who changed what.

## Verify a composition before declaring it runnable

A table is declared `queued` only after its composition has been checked **against the repository by
script**, and the check is recorded in `provenance` and `verified`. The check establishes:

1. Every phase id resolves in `backlog.yaml`.
2. Every phase is `queued` and unclaimed.
3. Every `depends_on` edge resolves either to a phase earlier in the batch's own order, or to a
   phase outside the batch that is `complete` — which is what *dependency-closed* means and the only
   thing that makes a batch runnable in isolation.
4. Every external dependency appears in `external_depends_on`, so the closure is stated rather than
   implied.
5. Every stage boundary follows from a real dependency edge or a real collision, computed with the
   actual collision rule rather than reasoned about from the data model.

`GOV-013`'s first lesson applies here in full: the original partition was drawn before anyone read
the rules that govern claiming, and reading them afterwards invalidated it outright. A composition
asserted without a recorded check is the failure `provenance` exists to prevent.

**`verified` is history, not a licence.** The coordinator re-verifies before running however recent
the block is, because the queue moves between sessions — the batch this protocol was written
alongside had two phases ranked ahead of it after its partition was checked.

## Stages: permission, not instruction

Stages run in listed order, and a stage opens only when every phase in the one before is `complete`
and integrated. Phases inside one stage carry no dependency edge between them and no shared system
or overlapping deliverable path.

`parallel: true` says the claim validator **will admit** these phases together. It does not say to
run them together. The coordinator still checks `max_active` and the Conflicts column numerically
before every claim, and a parallel stage runs serially when a peer's claims leave room for one. The
table describes the work; the lock table describes the moment.

Two consequences worth stating, because both were nearly got wrong:

- **Collision, not dependency, is usually what serializes a batch.** In `batch-002`, five of seven
  phases declare `sys-governance`, so the validator refuses any two of them at once regardless of
  dependencies. A phase with an empty `after` can still be forced into the last stage. That is what
  `conflicts_with` records, and it must be read as a lock rather than as slack to reclaim.
- **The collision rule is prefix-based on deliverable paths, not exact-match.** A table drawn with
  exact matching declares parallelism that does not exist — `tools/git-hooks/` and `tools/` are a
  collision, and an exact-match check calls them disjoint. Compute collisions with the real
  function.

## Selection must be deterministic, and ask only when it genuinely cannot be

A coordinator discovers tables rather than being told which to run, so the same prompt resumes an
interrupted batch without anyone remembering a number. The rule:

1. Exactly one table `in_progress` — run it, as a resume.
2. None `in_progress` — the lowest-`sequence` `queued` table.
3. Ask the owner only when the choice is genuinely ambiguous: more than one `in_progress`, two
   runnable tables sharing a `sequence`, or a batch named at kickoff that is not the rule's pick.
4. Nothing runnable — report an empty queue and stop.

`superseded` and `complete` tables are never selected. An owner naming a batch overrides the rule,
and the coordinator says which table the rule would have picked before proceeding.

The `sequence` field exists precisely so that several `queued` tables are not ambiguous. Asking on
every kickoff because more than one batch is waiting would move the organising load back onto the
person the coordinator exists to unload — `GOV-006`'s rule against blocking on a question that can
be answered.

## Status is run state, and it lives on the trunk

`queued` runnable and unstarted · `in_progress` a run is open, resume it · `complete` every phase
complete · `superseded` composition replaced, kept for history, never selected, names its
replacement.

The coordinator moves `queued` → `in_progress` when it claims the batch's first phase, and
`in_progress` → `complete` when the last phase completes. A batch that ends with phases outstanding
**stays `in_progress`** — that is what makes the next session's selection rule resume it rather than
skip past.

These edits land on `dev` in the primary checkout, alongside the claim commits, for the same reason
the lock table does: run state recorded only in a worktree is invisible to the next coordinator, and
a state nobody else can read is not state.

## Supersede rather than edit

Once a run has opened against a table, its composition is frozen. A batch whose membership needs to
change gets a **new table** that supersedes the old one, and the old table's `status` becomes
`superseded` with `superseded_by` naming its replacement.

Editing a composition mid-run makes the tracker and the table disagree about what the batch is,
and the tracker is the thing that survives a dead session. Superseding keeps the record of what was
actually attempted, which is what a later re-partition reads.

## What is not yet enforced

Nothing validates these tables mechanically. Idea `000316` holds the governance check that would —
schema validation, phase-id resolution, stage boundaries proved against `depends_on`, a table whose
declared status contradicts its phases, more than one table `in_progress`. Until it exists, every
guarantee above rests on the composing session running the check by hand and recording it in
`provenance`.

This is stated rather than hidden because the gap has a shape: the selection rule's step 1 assumes
at most one table is `in_progress`, and nothing currently prevents two.
