---
schema_version: 1
id: doc-system-boundary-study-system-backlog-review
code: PLAN-050.04
title: System boundary study — system and backlog review
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
systems: [sys-gov-docs, sys-backlog]
depends_on: [doc-system-boundary-study, doc-system-boundary-study-requirements, doc-system-boundary-study-prompt-inventory]
parent: doc-system-boundary-study
---

# System and backlog review

## Context and scope

`phase-bnd-03` provides the bounded general review requested by the owner. It examines registry and
backlog signals as a portfolio; it does not audit every governed document or change priority.

## Approach

Measure maturity, plan/phase coverage, work-in-progress, dependency depth, lock collisions, blocked
work, and document-retrieval signals at one baseline revision. Separate measured observations from
interpretation and name any unavailable measure.

## Work and dependencies

After the prompt inventory completes, record a new baseline, run the applicable read-only
governance/backlog views, write the review with source citations and limits, and identify questions
for the final boundary report.

## Requirement coverage

This phase delivers R04 and records the baseline evidence required by R07.

## Acceptance and verification

The review includes all specified measures or explicitly names why one is unavailable; it makes no
change to any existing phase state, priority, queue, or registry entry. Run governance, review each
claim against its cited output, and run `git diff --check`.

**When a check fails** (added 2026-09-28). A measure reported without its command or source, or any change to an existing phase or registry entry in the diff, fails acceptance. The phase then stays `active`, its session record quotes the failing output, and it is completed only after the check passes on a re-run (PLAN-050 overview, *Acceptance and verification*).

## Out of scope

Reprioritising, claiming, completing, or changing any existing backlog phase.

## Open questions

None. Candidate actions are inputs to the final owner decision, not backlog changes.
