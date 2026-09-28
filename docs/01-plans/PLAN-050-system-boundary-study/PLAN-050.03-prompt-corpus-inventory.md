---
schema_version: 1
id: doc-system-boundary-study-prompt-inventory
code: PLAN-050.03
title: System boundary study — prompt corpus inventory
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
systems: [sys-gov-docs]
depends_on: [doc-system-boundary-study, doc-system-boundary-study-requirements, doc-system-boundary-study-prompt-rubric]
parent: doc-system-boundary-study
---

# Prompt corpus inventory

## Context and scope

The full prompt corpus is too large to classify safely in the rubric-design phase. `phase-bnd-05`
applies the approved rubric to every governed prompt at one recorded revision and reports navigation
findings without changing any prompt.

## Approach

Use the rubric unchanged unless a documented contradiction makes it unworkable. Preserve the
baseline count and reconcile one inventory row per prompt, while treating field totals as
non-exclusive except where the rubric explicitly defines a primary navigation value.

## Work and dependencies

Read PLAN-050.02's rubric and baseline, classify every prompt at that revision, record citations,
reconcile the row count, and write navigation findings for the final report. This follows
`phase-bnd-02`.

## Execution order and real concurrency

Added 2026-09-28. This phase runs after `phase-bnd-02` and before `phase-bnd-03`. All three declare `sys-gov-docs`, so none of them can be active beside another; this phase reads `phase-bnd-02`'s rubric and `phase-bnd-03` follows it in the plan's order.

## Requirement coverage

This phase completes R03 and preserves R07's snapshot evidence.

## Acceptance and verification

Every prompt at the baseline has one row, the row count reconciles to the measured count, and the
four pilot rows remain consistent with PLAN-050.02. Run governance, rerun the count command, and
run `git diff --check`.

**When a check fails** (added 2026-09-28). A row count that differs from the measured count, or a pilot row that differs from PLAN-050.02, fails acceptance. The phase then stays `active`, its session record quotes the failing output, and it is completed only after the check passes on a re-run (PLAN-050 overview, *Acceptance and verification*).

## Out of scope

Inventing new lifecycle statuses, retiring prompts, or redesigning the prompt-pack protocol.

## Open questions

None. New taxonomy needs are reported to the final owner-decision phase.
