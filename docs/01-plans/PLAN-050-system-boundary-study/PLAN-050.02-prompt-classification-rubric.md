---
schema_version: 1
id: doc-system-boundary-study-prompt-rubric
code: PLAN-050.02
title: System boundary study — prompt classification rubric and pilot
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
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

## Execution order and real concurrency

Added 2026-09-28. This phase runs after `phase-bnd-01` and before `phase-bnd-05`. All three declare `sys-gov-docs`, so none of them can be active beside another, and `phase-bnd-05` reads this phase's rubric.

## Requirement coverage

This phase delivers the field model and pilot portion of R03 and records the baseline required by
R07. The complete R03 inventory is PLAN-050.03.

## Acceptance and verification

The rubric makes each field independently assignable and the four pilot prompts have cited rationale
for every field. Run governance, compare the measured count with the baseline command, and run
`git diff --check`.

**When a check fails** (added 2026-09-28). A pilot field with no cited rationale, or a measured count that differs from the baseline command's output, fails acceptance. The phase then stays `active`, its session record quotes the failing output, and it is completed only after the check passes on a re-run (PLAN-050 overview, *Acceptance and verification*).

## Out of scope

Changing prompt status, retiring any prompt, or declaring the full corpus classified.

## Open questions

None. Field values that fail the pilot become documented limitations for the next phase.
