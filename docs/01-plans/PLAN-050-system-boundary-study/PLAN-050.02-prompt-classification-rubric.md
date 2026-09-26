---
schema_version: 1
id: doc-system-boundary-study-prompt-rubric
code: PLAN-050.02
title: System boundary study — prompt classification rubric and pilot
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-gov-docs]
depends_on: [doc-system-boundary-study, doc-system-boundary-study-requirements, doc-prompt-pack-protocol]
parent: doc-system-boundary-study
---

# Prompt classification rubric and pilot

## Context and scope

`active` in the governed prompt corpus preserves lifecycle and precedent; it does not describe
reuse or navigation. `phase-bnd-02` creates a repeatable classification rubric before anyone
classifies the full corpus.

## Approach

Define independent fields for operational role, reuse disposition, precedent status, review
disposition, and default entry point. A field may have an unknown value; no prompt is forced into a
single composite category.

## Work and dependencies

At the revision produced by `phase-bnd-01`, measure the prompt count, define allowed values and
evidence rules, then pilot the rubric on PROMPT-006, PROMPT-010, PROMPT-020, and PROMPT-040. Resolve
only rubric ambiguity; do not classify the remaining corpus in this phase.

## Requirement coverage

This phase delivers the field model and pilot portion of R03 and records the baseline required by
R07. The complete R03 inventory is PLAN-050.03.

## Acceptance and verification

The rubric makes each field independently assignable and the four pilot prompts have cited rationale
for every field. Run governance, compare the measured count with the baseline command, and run
`git diff --check`.

## Out of scope

Changing prompt status, retiring any prompt, or declaring the full corpus classified.

## Open questions

None. Field values that fail the pilot become documented limitations for the next phase.
