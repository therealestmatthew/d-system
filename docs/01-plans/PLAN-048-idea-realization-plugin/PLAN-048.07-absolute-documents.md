---
schema_version: 1
id: doc-idea-realization-plugin-absolute-documents
code: PLAN-048.07
title: Idea-realization plugin — the governance documents as absolutes, part one
kind: plan
status: approved
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-absolutes]
depends_on: [doc-idea-realization-plugin, doc-realization-role-contracts]
parent: doc-idea-realization-plugin
---

# The governance documents as absolutes, part one

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-07`. Covers the first half of
`REQ-031` R20: families A (core protocol and codes), B (reporting) and C (the ledger triage).
Families D, E and F are [PLAN-048.09](PLAN-048.09-absolute-documents-two.md), `phase-plug-09`,
after the adversary found the single phase too large for one session.
The owner's instruction, 2026-09-25: the plugin's governance and protocol documents are "written as
absolutes and facts — exclude any reference to decisions or old states that have been overridden",
and the work of extracting them is distributed across the agent crew.

## Context and scope

Analysis 05 classifies the sixteen governance documents, the two prompts and `AGENTS.md`: portable
(GOV-008, 013, 016), portable with substitution (GOV-001, 002, 005, 006, 009, 010, 017, 018,
PROMPT-038, AGENTS.md), this-repository-only (GOV-003, 004, 007, 014's pipeline binding, 015,
PROMPT-037's roster). §2 estimates each document's narrative share and quotes what an absolute
rewrite drops; §1 names the ten still-standing rules in the decision ledger and the entries that
are history. §5 proposes six families. The owner excluded GOV-007 and GOV-015.

## Decisions

- **Six analyst dispatches, one per family, each returning one-line absolutes with source lines.**
  Families: A core protocol and codes (GOV-001, 002, 005, AGENTS.md); B reporting (GOV-006);
  C ledger triage (GOV-003, 004 — classification only, its output feeds A, E and the idea
  documents); D methodology (GOV-008, 009, 013, 016); E role contracts and review (GOV-014, 018,
  PROMPT-038); F multi-session coordination (GOV-017, PROMPT-037). C runs first, then A and B in
  this phase; D, E and F in `phase-plug-09`, E with C's classification from this phase's trace
  table. Rejected: one session reading everything (D12 in the overview).
- **The plugin's document set mirrors the source set minus the excluded and the ledger**, one
  document per source, named by role (`protocol.md`, `backlog-protocol.md`, `document-codes.md`,
  `reporting.md`, `prompt-packs.md`, `research-packs.md`, `coordinator.md`, `batches.md`,
  `role-contracts.md`, `plan-review.md`, `adversary-prompt.md`, `multi-session.md`,
  `session-manager-messages.md`). Rejected: one merged document (a reader cannot find a rule).
- **Names of things are roles, not instances**: "the integration branch", "the worktree
  directory", "the coordinator", "the owner". The `main`/`dev` drift in GOV-001 and GOV-002 (idea
  `000461`) does not reach the plugin because the branch is never named.
- **GOV-010's worked examples are dropped**, leaving the mechanical table and the judgements
  P1–P11, Q1–Q5, T1–T2 stated abstractly (analysis 05 §2 note). Rejected: inventing generic
  examples (prose that performs).
- **The trace table lives in this repository** (`PLAN-048.07-trace.md` in this folder), one row
  per plugin rule: plugin document and section, source document and line. The plugin never cites
  it (R02).

## Work and dependencies

1. Dispatch family C; then A and B with C's extracted rules attached to A.
2. Write `protocol.md`, `backlog-protocol.md`, `document-codes.md` and `reporting.md`.
3. Write the trace table, including C's classification of every ledger entry.
4. Write `test/test_no_history.py`; run the suite.

Prerequisites: `phase-plug-04` and `phase-plug-06`, so the documents describe mechanisms that
exist in the plugin (the check, the skills, the generators, the templates).

## Acceptance and verification

As the backlog entry states. The case that must fail: the history-word grep over `docs/` finds
`incident`, `until 20`, `was broken`, `replaces` or `precedent`; a ledger still-standing rule
missing from every plugin document.

## Execution order

Runs after phase-plug-04 and phase-plug-06 (wave 4), alongside phase-plug-03 if still open; phase-plug-09 follows it.

## Out of scope

GOV-007, GOV-015, the ledger as a document, this repository's own documents.

## Open questions

- None open. The one-session-or-two question was settled by the split into this phase and
  `phase-plug-09`.
