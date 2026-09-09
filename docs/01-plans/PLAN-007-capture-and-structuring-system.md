---
schema_version: 1
id: doc-capture-system
code: PLAN-007
title: Define and build the capture and structuring system
kind: plan
status: complete
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-06'
completion_evidence:
- docs/04-decisions/ADR-007-capture-routing.md
- docs/04-decisions/ADR-008-record-types.md
- docs/06-requirements/REQ-002-capture-requirements.md
- docs/01-plans/PLAN-009-capture-build.md
systems: [sys-portfolio, sys-contracts, sys-brain]
depends_on: [doc-governance-protocol]
---

# Define and build the capture and structuring system

## Context and scope

The repository can store people, commitments and tasks. Nothing defines how information gets in.
There is no capture workflow, no intake format, and no rule for how raw thought becomes a structured
record. The portfolio holds 33 projects and 28 tags but zero people, zero commitments and zero
tasks.

Fourteen backlog phases depend on that missing data. The Accountability Ledger, Cognitive Load
Estimator and Commitment Velocity signals all read commitments, as do all four synthesis workflows.
Built today, they would be verified against empty tables.

The owner is the sole contributor, so the system's value depends almost entirely on whether capture
is low-friction enough to sustain, and on how much organising work the agents absorb rather than
hand back.

## This is a discovery plan

This plan does not specify the capture system. It cannot: the design turns on answers only the owner
holds — what the system should return and when, how raw information reaches them, how much the agent
should infer versus ask, and where the line between structure and personal content falls.

The first phase runs a definition session against
[PROMPT-002](../02-prompts/PROMPT-002-capture-and-structuring-system.md), which carries the
interview, the current entity shapes and the design tensions to settle. **That session's output —
requirements, a build plan and its own backlog phases — becomes the rest of this plan's work.**
Phases beyond `phase-cap-01` are deliberately absent rather than guessed at.

## Work and dependencies

### Phase 1 — run the definition session

Read PROMPT-002 and follow it. Interview the owner in small batches, record the answers as
decisions with their reasoning, and produce a requirements document, a build plan and backlog phases
for it. Write no implementation code.

The phase is complete when a reader who was not in the session can tell, from the committed
documents alone, what gets captured, in what form, what the agent decides unaided, and what it must
ask about.

### Subsequent phases

Added by phase 1's output, and now held in
[PLAN-009](PLAN-009-capture-build.md) as `phase-cap-02` through `phase-cap-09`. This plan's own work
is finished; the session record is
[SESS-2026-09-06-01](../03-sessions/SESS-2026-09-06-01-capture-definition.md). Any phase that produces real portfolio content must respect the
structure/content boundary set by [PLAN-006](PLAN-006-confidentiality-sweep.md); capture will
generate exactly the personal material that plan exists to keep out of the tracked tree.

## Acceptance and verification

```bash
uv run python -m src.governance
uv run python -m src.governance --backlog
```

The governance check must pass with the new documents, and the backlog must cover this plan with
phases that did not exist before the session.

## Open questions

Every substantive question is held in PROMPT-002 and answered during phase 1. Recording them twice
would be the duplicate bookkeeping the protocol forbids.
