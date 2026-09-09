---
schema_version: 1
id: doc-capture-routing
code: ADR-007
title: Capture routing, provenance and the staging boundary
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-capture, sys-portfolio, sys-contracts]
depends_on: [doc-governance-protocol, doc-capture-system]
---

# Capture routing, provenance and the staging boundary

## Context

The repository stores 33 projects and 28 tags. It holds zero people, zero commitments and zero
tasks, and nothing defines how information gets in. Fourteen backlog phases across the `phase-sig-*`
and `phase-syn-*` tracks read commitment data that has no intake path; built today they would be
verified against empty tables.

The owner is the sole contributor. Capture therefore has to survive week three, which makes friction
the binding constraint rather than fidelity. Two priorities were stated, in order: **zero broken
promises**, then **nothing went quiet**. Capture completeness was explicitly *not* expected to reach
100% — some things will always stay in the owner's head, and a design that assumes otherwise fails.

Four tensions had to be settled rather than left to resolve by accident: friction against fidelity,
agent autonomy against trust, structure against premature commitment, and this repository's own rule
against duplicate bookkeeping.

## Decision

### 1. Raw capture is immutable and primary

Every capture is stored verbatim, with an identifier and a timestamp, **before** any interpretation
runs. Structured records reference the raw capture they came from. Raw text is never edited and never
deleted by an agent.

This is what makes a bad interpretation recoverable rather than lost, and it is the reason
re-derivation never needs to be built as a feature: the input survives, so the option stays open.

### 2. Three channels, one pipeline

| Channel | Use |
|---|---|
| Conversational session | Speaking to an agent directly; the agent structures what it hears |
| Inbox directory | Anything file-shaped — freeform notes, a pasted transcript, an email chain, an artifact |
| CLI quick-capture | A single command that appends a timestamped fragment in seconds |

A pasted transcript is an inbox file, not a fourth channel. All three produce the same raw capture
record and enter the same routing, so behaviour cannot diverge by entry point.

### 3. Evidence is scored per field, with provenance

Each field an agent fills carries an evidence level and a pointer back into the raw capture:

- **explicit** — the raw text states it.
- **inferred** — supported by surrounding context but not stated. A transcript with one other
  attendee makes "I'll send it over" a promise to that attendee.
- **guessed** — pattern match with no support in the text.

Per-field rather than per-record, because a single record-level flag forces the reviewer to re-read
the whole record to find what to check. Provenance is required, not optional: a confidence marker
that cannot be traced back to its source cannot be verified.

### 4. Four things an agent never invents

`promised_to`, `due_date`, a decision **and its rationale**, and completion of anything.

An agent may *assume* these from context — that is what `inferred` means — but an assumption in one
of these fields must carry a non-explicit evidence level and a review flag. **An unflagged
non-explicit value in a protected field is a validation failure, not a style problem**, and the write
is rejected.

### 5. Routing on stakes × evidence

Stakes are a property of the record type:

| Tier | Record types |
|---|---|
| Low | raw note, task |
| Medium | commitment, interaction, waiting-on, development event |
| High | decision |
| Structural | new person, new project, new tag, new tag category |

The routing table is the whole policy:

| Route | Condition | What it costs the owner |
|---|---|---|
| **clean** | every field explicit, and stakes low or medium | Nothing; promoted in bulk |
| **flagged** | any inferred or guessed field, or stakes high | One per-item decision |
| **held** | structural — a new durable identity | An identity call the agent may not make |

Reversibility does not appear as a factor because staging already guarantees it; channel does not
appear because it changes only *when* the owner sees a flag, never *whether* one is raised.

### 6. Ambiguity never interrupts capture

The agent does not stop to ask. It records its best interpretation, flags it with the reasoning, and
continues. The flag is visible immediately, so the owner may resolve it at once if they want to, but
nothing blocks on them. An agent that asks about everything moves the organising load back onto the
person the system exists to unload.

### 7. Staging is the write boundary

Agents write to a staging area. Promotion into `_data/` is an explicit owner action:

- **clean** items promote in bulk with one action;
- **flagged** items are decided individually;
- **held** items require the owner to make the identity call.

Review effort therefore scales with ambiguity, not with volume.

### 8. Private by default

Raw captures and staging are gitignored. Only deliberately promoted records enter tracked `_data/`.
The standing test for what may be committed is whether it **benefits the application** rather than
encoding the owner's personal prioritisation. This is consistent with
[PLAN-006](../01-plans/PLAN-006-confidentiality-sweep.md), which exists to separate tracked structure
from real content, and it means capture cannot make that problem worse while the sweep is pending.

### 9. Tags may grow inside the taxonomy, not beyond it

An agent applies existing tags freely and may create a new tag **within one of the six existing
categories**, but every new tag raises an alert in review. A new *category* is a held item requiring
approval. The taxonomy is a shared vocabulary; widening it silently makes every prior classification
harder to trust.

### 10. Corrections edit the record and log the correction

When the owner states a correction, the agent edits the record and appends a dated correction entry.
The raw capture is untouched. Re-deriving the record from raw text is not the mechanism: when the
owner already knows the answer, the owner is the authority, not the text.

## Alternatives considered

**Ask the owner before writing any record.** Highest fidelity, and rejected: it returns the
organising work to the owner and would end capture within weeks.

**Write directly into `_data/`, using the git diff as review.** Rejected on two counts. Private-by-
default requires the intake surface to be gitignored, and a diff cannot distinguish a confident
record from a guessed one — every line looks equally settled.

**One confidence flag per record.** Simpler schema, rejected because review then means re-reading
records rather than checking specific claims.

**Auto-promote clean items on a timer.** Lowest friction, rejected: records would enter the source
of truth having never been seen.

**Flag every commitment regardless of evidence.** Considered seriously, given that broken promises
are the worst failure mode. Rejected because an explicit, unambiguous promise carries no question for
the owner to answer, and padding the review pile with certainties is how review piles stop getting
cleared.

## Consequences

- Three locations hold capture data: raw, staging, `_data/`. This is not the duplicate bookkeeping
  GOV-001 forbids — raw is input, staging is proposal, `_data/` is accepted fact, and a given fact is
  authoritative in exactly one of them at a time.
- Every structured record carries provenance fields, which makes the schemas heavier than the
  existing entity shapes.
- The system can never assert a commitment the owner did not approve, which is what makes "zero
  broken promises" trustworthy rather than merely computed.
- Capture without a working review loop is a queue, not a system. Nothing in this decision delivers
  value until promotion is built; the plan orders phases accordingly.

## Revisit trigger

Revisit if flagged items routinely age past two weeks unreviewed — the pile is too large, so the
thresholds are wrong — or if bulk-approved clean items are corrected more than rarely, which would
mean `explicit` is being scored too generously.
