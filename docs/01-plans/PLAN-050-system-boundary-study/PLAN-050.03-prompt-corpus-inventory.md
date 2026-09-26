---
schema_version: 1
id: doc-system-boundary-study-prompt-inventory
code: PLAN-050.03
title: System boundary study — prompt corpus inventory
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
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

## Requirement coverage

This phase completes R03 and preserves R07's snapshot evidence.

## Acceptance and verification

Every prompt at the baseline has one row, the row count reconciles to the measured count, and the
four pilot rows remain consistent with PLAN-050.02. Run governance, rerun the count command, and
run `git diff --check`.

## Out of scope

Inventing new lifecycle statuses, retiring prompts, or redesigning the prompt-pack protocol.

## Open questions

None. New taxonomy needs are reported to the final owner-decision phase.
