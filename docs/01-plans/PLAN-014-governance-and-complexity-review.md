---
schema_version: 1
id: doc-governance-model
code: PLAN-014
title: Review the governance model and system complexity
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-contracts]
depends_on: [doc-governance-protocol]
---

# Review the governance model and system complexity

## Context and scope

Governance exists in two forms at once and nobody has decided whether that is correct. It is a
**document kind** — `governance` and `operation`, producing `GOV-*` and `OPS-*` in
`docs/08-governance/` — and simultaneously a **system**, `sys-governance` in `systems.yaml`.

The owner's framing is the one to test: perhaps governance is simply a type of system, and everything
governance-related sits inside it. If that holds, some current structure is redundant. If it does
not, the reason deserves recording.

The investigation is specified in
[PROMPT-005](../02-prompts/PROMPT-005-governance-model-review.md). This plan exists to give that work
a home and to hold whatever the resulting ADR decides.

## Why this plan is thin, and what that demonstrates

This plan carries one investigation phase and no predetermined outcome, because **the outcome is the
thing being investigated.** Writing more would be inventing conclusions ahead of the evidence.

Its existence is itself evidence for a question the investigation must answer. `phase-gov-02` could
not be queued without it: `schemas/backlog.schema.json` requires every phase to name a document of
kind `plan`, so an investigation with no plan behind it cannot enter the backlog at all. A plan was
therefore written to satisfy a schema rather than to record a decision.

That is the **fourth** occurrence in one day of the same pressure — after a course production plan, a
course extraction plan, and the governed/ephemeral split. The first three were scope creep from
outside. This one is internal and arguably legitimate, which makes it the clearest case: the
requirement that every phase name a plan is doing real work in keeping the backlog anchored, and also
manufacturing documents. Both are true, and
[PROMPT-003](../02-prompts/PROMPT-003-systems-review.md) should weigh them against each other with
this instance as data.

## Approach

1. Run PROMPT-005 and produce one ADR answering its five questions, every claim cited to a real
   document.
2. Run PROMPT-003 and produce an ADR per decision that changes the system.
3. Add phases for whatever those ADRs decide, under this plan.
4. If either concludes nothing should change, record why — a deliberately unchanged model is a result
   worth keeping.

**PROMPT-005 runs first and is narrower.** Both prompts ask whether `governance` and `operation`
should merge — PROMPT-005 question 3 and PROMPT-003 question 3. PROMPT-005 decides it; PROMPT-003
inherits that answer rather than re-opening it. Stated here because an unassigned overlap is exactly
the re-litigation PROMPT-003 warns about.

## What is already known

Do not re-derive it. Governance documents **already scope to subsystems** through the `systems`
field: `GOV-004` carries `sys-backlog` alone; `GOV-002` carries both `sys-backlog` and
`sys-governance`; `GOV-001`, `GOV-005` and `GOV-006` carry `sys-governance`; and `GOV-003` carries
four systems, none of them `sys-governance`. The scoping is real but not a clean partition —
`GOV-003` is the case any proposal must account for. Any proposal adding structure for that distinction must first explain what the
existing field fails to capture.

## Constraint

No schema is written before the ADR. Three of today's four corrections came from building structure
ahead of demonstrated need.
