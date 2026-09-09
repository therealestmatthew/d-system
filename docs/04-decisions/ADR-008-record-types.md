---
schema_version: 1
id: doc-record-types
code: ADR-008
title: Record types, optional parents and cadence semantics
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-contracts, sys-portfolio, sys-projection, sys-capture]
depends_on: [doc-governance-protocol, doc-capture-system, doc-capture-routing]
---

# Record types, optional parents and cadence semantics

## Context

The entity model has five shapes: project, commitment, task, person, tag. It was written before any
capture path existed, so nothing tested whether those five can hold what the owner actually needs to
retrieve.

The definition session established that they cannot. The owner needs to answer "who said what and
when", "what did we decide and why", "what is owed **to** me", and wants countable history for
meetings and personal development over time. None of those have a home. Separately, the owner wants
tasks that exist without a parent promise — a task may deserve to be tracked even when writing a
commitment for it would be ceremony.

Today a task is an array element inside a commitment's JSON, and `tasks.project_id` is derived from
its parent commitment. A task with no commitment has nowhere to live at all.

There are currently **zero** commitments and **zero** tasks. Every change below is therefore free of
migration cost, and gets more expensive the longer it waits.

## Decision

### 1. Four new record types

| Type | Holds | Answers |
|---|---|---|
| `interaction` | A dated meeting, call or exchange with participants and substance | "Who said what, and when" — and makes meetings countable |
| `decision` | A dated choice, its reasoning, and who was involved | "What did we decide and why", traceable in retrospect |
| `waiting_on` | Something another party owes the owner | "What has gone quiet" on the *inbound* side |
| `development_event` | Trainings, certifications, talks, milestones | Personal-development metrics over time |

`waiting_on` is the mirror of `commitment`, not a status on it: the owner is the creditor rather than
the debtor, so the staleness question, the follow-up behaviour and the person's role all differ.

`development_event` is kept as its own type rather than a tagged `interaction` because a training is
not an exchange with a stakeholder, and folding it in would make every count of "meetings" wrong.

### 2. Tasks become a first-class entity with optional parents

`_data/tasks/` gains its own source files. `task.commitment_id` and `task.project_id` are both
optional; either, both, or neither may be set. `commitment.project_id` likewise becomes optional, so
a standalone commitment need not be forced under a project.

This follows necessarily from allowing free-floating tasks: an entity that can exist without a parent
cannot be stored inside one. Keeping the embedded array for parented tasks and adding a second store
for the rest was rejected — one entity with two homes is exactly the duplicate bookkeeping the
governance protocol forbids, and every query would have to reassemble it.

Consequences that must be handled by the implementing phases:

- `sql/001_schema.sql` drops `NOT NULL` from `commitments.project_id`, `tasks.commitment_id` and
  `tasks.project_id`.
- `schemas/commitment.schema.json` drops `project_id` from `required` and drops the embedded `tasks`
  array; a new `schemas/task.schema.json` takes its place.
- `tools/rebuild_db.py` loads tasks from `_data/tasks/` instead of unpacking them from commitments.
- Any grouping by project must handle a null parent. Parentless records need an **unfiled** view, or
  free-floating items accumulate invisibly — which would defeat the point of capturing them.

### 3. People are referenced by name until identity is confirmed

`promised_to` stays a string and is joined to a person record only once the owner confirms the
identity. A first name in a note creates no person. This keeps the identity decision — a structural,
held-tier action under [ADR-007](ADR-007-capture-routing.md) — with the owner, while still letting
the promise be recorded immediately.

### 4. Cadence means review rhythm, and staleness is derived

`project.commitment_cadence` is renamed `review_cadence`: a policy the owner sets, stating how often
the project should be touched. Its vocabulary is `daily | weekly | biweekly | monthly | quarterly |
ad-hoc`.

`ongoing` is retired. It described activity status rather than a rhythm, `project.status` already
carries that, and it gave the staleness check nothing to compute against. Three projects currently
use it and must be reassigned by the owner; an agent does not pick a replacement.

`last_touched` is **derived at rebuild** as the latest activity date across a project's interactions,
commitments, tasks and decisions. It is never stored in `_data/`, because a hand-maintained activity
date is a number that drifts.

Staleness is then `today − last_touched > review_cadence`, which makes the owner's second priority —
nothing went quiet — countable from data the system already has.

The alternative reading of cadence, *expected commitment frequency*, gets no field. It is a count per
project per period, already computable; an active project with a cadence and no commitments over
several periods is a signal to derive, not a value to maintain.

### 5. `last_reviewed` is retained and means something different

`last_touched` says activity happened. `last_reviewed` says the owner deliberately sat down and
assessed the project. These are genuinely different questions and both are worth answering, so the
field stays hand-set. The distinction must be stated wherever either field is documented, or they
will collapse into each other in use.

## Alternatives considered

**Fold `development_event` into `interaction` with a tag.** Fewer types, rejected: it corrupts every
meeting metric, and the owner asked for both counts separately.

**Keep tasks embedded and add a separate store for unparented ones.** Avoids touching the current
shape, rejected as duplicate bookkeeping.

**Drop `commitment_cadence` entirely and derive staleness from status alone.** Rejected: without a
declared rhythm there is no threshold, so "gone quiet" would have no definition beyond an arbitrary
global constant.

**Drop `last_reviewed` as redundant.** Rejected once the two meanings were separated.

## Consequences

- Nine entity types instead of five. Each new one costs a schema, DDL, a loader branch, a Pydantic
  model and eventually routes — the cost is real and was accepted deliberately per type.
- The `phase-sig-*` and `phase-syn-*` tracks gain the data they were written against, and Stale Radar
  in particular becomes implementable against a defined threshold rather than a guess.
- Three projects hold a retired cadence value until the owner reassigns them; the projection must
  treat the old value as invalid rather than silently mapping it.
- Optional parents make an unfiled backlog possible. That is the intended behaviour and also the main
  risk: without a view that surfaces parentless records, free-floating tasks become a write-only pile.

## Revisit trigger

Revisit if a new type accumulates no records after the first sustained month of capture — it was
speculative and should be retired — or if the unfiled bucket grows without being drained, which would
mean optional parents removed the pressure to file that made the data useful.
