---
schema_version: 1
id: doc-idea-realization-plugin-absolute-documents-two
code: PLAN-048.09
title: Idea-realization plugin — the governance documents as absolutes, part two
kind: plan
status: approved
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-absolutes]
depends_on: [doc-idea-realization-plugin, doc-idea-realization-plugin-absolute-documents]
parent: doc-idea-realization-plugin
---

# The governance documents as absolutes, part two

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-09`. Covers the second half of
`REQ-031` R20: families D (methodology: GOV-008, 009, 013, 016), E (role contracts and review:
GOV-014, 018, PROMPT-038) and F (multi-session coordination: GOV-017, PROMPT-037). Part one
([PLAN-048.07](PLAN-048.07-absolute-documents.md)) covers families A, B and C.

## Context and scope

The adversary's phase-altitude review found the single absolute-documents phase too large for one
session: about 3,765 source lines across six families, thirteen documents to write and a trace
table. The split follows the family sizes in analysis 05 §5: part one reads ~1,830 lines (A, B, C)
and writes four documents; this part reads ~1,935 lines (D, E, F) and writes nine, shorter ones —
the methodology and coordination documents lose their worked examples and roster, which is most of
their length.

## Decisions

- **This phase depends on part one for the ledger classification**, which family E needs (the
  completion-authority and review rulings live in the ledger). Rejected: re-dispatching family C
  here (the same 835 lines read twice, and two classifications that could disagree). Cost: the two
  parts run in sequence, not in parallel.
- **Worked examples bound to this repository's plans are dropped, not replaced** (GOV-010's
  P1–P11 illustrations, GOV-016's batch example, GOV-017's departures section). Rejected:
  inventing generic examples. Cost: shorter documents that state the rule and stop.
- **The session-manager starter messages ship as a template**, with the roster and board paths as
  placeholders, since a target running parallel sessions needs the message shapes and nothing else
  from the source.

## Work and dependencies

1. Dispatch families D, E and F in parallel, E with part one's trace table attached.
2. Write the nine documents named in the backlog entry.
3. Write `PLAN-048.09-trace.md`.

Prerequisite: `phase-plug-07`.

## Acceptance and verification

As the backlog entry states. The case that must fail: a document naming a source-repository prompt
code fails the R02 check; a still-standing ledger rule about review or role contracts missing from
every document.

## Execution order

Runs after phase-plug-07, on `sys-plugin-absolutes`; may run alongside phase-plug-03 if that phase
is still open. The overview's Execution order section gives the full sequence.

## Out of scope

Families A–C (part one); the mechanisms the documents describe (earlier phases).

## Open questions

- Whether `role-contracts.md` keeps the 300,000-token ceiling as a number. Planner; leans to
  keeping it as the default the source states, since a target can amend it.
