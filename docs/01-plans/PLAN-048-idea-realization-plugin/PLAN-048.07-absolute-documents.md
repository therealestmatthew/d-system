---
schema_version: 1
id: doc-idea-realization-plugin-absolute-documents
code: PLAN-048.07
title: Idea-realization plugin — the governance documents as absolutes
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin]
depends_on: [doc-idea-realization-plugin, doc-realization-role-contracts]
parent: doc-idea-realization-plugin
---

# The governance documents as absolutes

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-07`. Covers `REQ-031` R20.
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
  PROMPT-038); F multi-session coordination (GOV-017, PROMPT-037). C runs first; the rest in
  parallel. Rejected: one session reading everything (D12 in the overview).
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

1. Dispatch family C; then A, B, D, E, F with C's extracted rules attached to A and E.
2. Write the thirteen plugin documents from the extractions.
3. Write the trace table.
4. Extend the R02 check with the history-word grep; run the suite.

Prerequisites: `phase-plug-04` and `phase-plug-06`, so the documents describe mechanisms that
exist in the plugin (the check, the skills, the generators, the templates).

## Acceptance and verification

As the backlog entry states. The case that must fail: the history-word grep over `docs/` finds
`incident`, `until 20`, `was broken`, `replaces` or `precedent`; a ledger still-standing rule
missing from every plugin document.

## Execution order

Runs after phase-plug-04 and phase-plug-06, alone on sys-plugin. Every plugin phase shares `sys-plugin` and the `plugins/idea-realization/` deliverable path, so the validator allows one at a time; the overview's Execution order section gives the full sequence.

## Out of scope

GOV-007, GOV-015, the ledger as a document, this repository's own documents.

## Open questions

- One session or two. Planner, at phase-fit; leans to one (the overview's Q2), split A–C / D–F if
  the adversary's size finding stands.
- Whether `role-contracts.md` keeps the 300,000-token ceiling as a number. Planner; leans to
  keeping it as the default the source states, since a target can amend it.
