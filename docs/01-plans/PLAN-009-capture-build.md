---
schema_version: 1
id: doc-capture-build
code: PLAN-009
title: Build the capture and structuring system
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-capture, sys-contracts, sys-portfolio, sys-projection]
depends_on: [doc-capture-system, doc-capture-routing, doc-record-types, doc-capture-requirements]
---

# Build the capture and structuring system

## Context and scope

[PLAN-007](PLAN-007-capture-and-structuring-system.md) was a discovery plan: its single phase ran the
definition session and deferred everything else until the owner's answers existed. They now do. This
plan is that session's output — the build work, in dependency order.

The decisions are fixed by [ADR-007](../04-decisions/ADR-007-capture-routing.md) and
[ADR-008](../04-decisions/ADR-008-record-types.md); the contract is
[REQ-002](../06-requirements/REQ-002-capture-requirements.md). This plan does not restate them. It
says what gets built, in what order, and why that order.

Scope is intake through promotion: raw capture, structuring, routing, review, promotion into
`_data/`, and the projection of the expanded entity model. Out of scope: scheduled prompting,
durable off-disk storage, and any signal or synthesis output, all of which have their own tracks.

## Ordering rationale

Contracts precede code because every later phase validates against them, and because the schema
changes are free only while the tables are empty. Raw intake precedes structuring so that a failure
in interpretation can never cost a capture. Review precedes seeding because capture without
promotion is a queue, not a system — seeding before the review loop exists would produce a staging
pile with no way out of it. Projection is independent of the capture pipeline and depends only on the
contracts, so it can run in parallel with intake work.

## Work and dependencies

### Phase 2 — entity contracts (`phase-cap-02`)

Write the schemas for the expanded model: `task`, `interaction`, `decision`, `waiting_on`,
`development_event`, plus the shared evidence-and-provenance shape every agent-filled field carries.
Make `commitment.project_id` optional, remove the embedded `tasks` array, rename
`project.commitment_cadence` to `review_cadence` and retire `ongoing`.

No DDL, no loader, no code. Schemas only, so the contract is settled before anything is written
against it. The three projects using `ongoing` are surfaced for the owner to reassign; the phase does
not pick values for them.

### Phase 3 — raw capture and staging contracts (`phase-cap-03`)

Define what a raw capture record is, what a staged record is, where both live, and the ignore rules
that keep them untracked. Establishes the boundary REQ-002 R12 and R16 are verified against, before
any code can write across it.

### Phase 4 — raw intake (`phase-cap-04`)

The CLI quick-capture command and the inbox directory path. These write raw records **only** — no
interpretation, no structuring. Splitting intake from structuring is what makes R1 and R2 hold under
a failure: if structuring breaks, captures still land.

### Phase 5 — structuring and routing (`phase-cap-05`)

Evidence scoring per field, provenance back into the raw text, the never-invent validation rules, and
the clean/flagged/held routing table. The largest phase, and the one whose fixtures define correct
behaviour for everything downstream.

### Phase 6 — review and promotion (`phase-cap-06`)

Bulk promotion of clean records, per-item decisions on flagged and held ones, the identity call for
new people, projects and tags, and dated corrections on promoted records. This is the only path into
`_data/`, and until it exists nothing captured can become real.

### Phase 7 — projection (`phase-cap-07`)

DDL and loader for the new types, nullable parents on commitments and tasks, tasks loaded from
`_data/tasks/` instead of unpacked from commitments, derived `last_touched`, and the unfiled view
that keeps parentless records visible. Depends only on phase 2.

### Phase 8 — seed real content (`phase-cap-08`)

The first sustained capture run: real interactions, commitments and tasks flowing through the whole
pipeline, plus the owner's cadence reassignments. The phase's own output is the evidence that the
pipeline works end to end, and it must respect the structure/content boundary set by
[PLAN-006](PLAN-006-confidentiality-sweep.md).

### Phase 9 — confirm the downstream tracks are unblocked (`phase-cap-09`)

Verify against real rows, and record the row counts, that the dependent tracks can now be built.

## How this unblocks the signal and synthesis tracks

Fourteen phases were written against data that did not exist. This is what each needs and where it
now comes from:

| Phase | Needs | Provided by |
|---|---|---|
| `phase-sig-02` Stale Radar | Activity dates and a staleness threshold | Derived `last_touched` and `review_cadence` (phase 7); real activity (phase 8) |
| `phase-sig-03` Accountability Ledger | Commitments with a person and a due date | Promoted commitments (phases 6, 8) |
| `phase-sig-04` Project Health Signal | Commitment and task state per project | Phases 6-8 |
| `phase-sig-05` Cognitive Load Estimator | Open commitments and tasks, including unfiled | Phases 6-8, plus the unfiled view |
| `phase-sig-06`, `phase-sig-08` Commitment Velocity | Commitments closing over time | Phase 8, accumulating |
| `phase-syn-01` Context packs | Interactions and decisions per project | New record types (phases 2, 7, 8) |
| `phase-syn-02` Session briefing | Today's commitments and recent interactions | Phases 6-8 |
| `phase-syn-03` Weekly review | Stale set, promises due, what went quiet | Phases 7, 8 |
| `phase-syn-04` Portfolio digest | All of the above over a month | Phase 8, accumulating |

Two of these need *accumulated* history rather than merely non-empty tables. Velocity and the monthly
digest cannot be meaningfully verified the day capture starts, and phase 9 records that distinction
rather than declaring them ready.

`phase-sig-03` also gains a second source that did not exist when it was written: `waiting_on`
records make the ledger two-sided, covering what is owed to the owner as well as by them. That is a
scope change to an existing phase, not something this plan silently absorbs — it is recorded here for
the owner to decide when that phase is claimed.

## Acceptance and verification

```bash
uv run python -m src.governance
uv run python -m src.governance --backlog
uv run pytest
```

Each phase carries its own acceptance conditions and verification commands in
`docs/09-backlog/backlog.yaml`. The plan as a whole is complete when every requirement in REQ-002 has
a passing verification, and `commitments`, `interactions` and `tasks` are non-empty after a rebuild.

## Open questions

Held in [REQ-002](../06-requirements/REQ-002-capture-requirements.md) with their revisit conditions:
durable off-disk storage, scheduled prompting, and the three projects holding a retired cadence
value. Recording them here as well would be the duplicate bookkeeping the protocol forbids.
