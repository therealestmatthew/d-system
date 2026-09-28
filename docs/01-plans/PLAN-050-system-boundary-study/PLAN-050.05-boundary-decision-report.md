---
schema_version: 1
id: doc-system-boundary-study-decision-report
code: PLAN-050.05
title: System boundary study — governed boundary decision report
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
systems: [sys-gov-docs, sys-backlog]
depends_on: [doc-system-boundary-study, doc-system-boundary-study-requirements, doc-system-boundary-study-system-backlog-review]
parent: doc-system-boundary-study
---

# Governed boundary decision report

## Context and scope

`phase-bnd-04` turns the preceding working evidence into a governed draft architecture report before
the owner is asked to rely on it. It produces a recommendation and decision gate, never an extraction.

## Approach

Rebase onto current `dev`, reconcile all study inputs to that revision, and refresh any inventory
whose drift makes it unreliable. Compare at least three options, including retaining one repository,
against ownership, interfaces, release cadence, audience, costs, preconditions, and extraction
triggers.

## Work and dependencies

After the general review, reconcile source revisions, allocate an architecture code, write the draft
architecture report, and present the owner questions and conditional next actions. Stop there.

## Requirement coverage

This phase delivers R02, R05, R06, and the final reconciliation required by R07.

## Acceptance and verification

The report distinguishes the three core systems, framework, and adjacent-system dispositions; has
three options and explicit costs; and gives every owner question a decider, timing, recommendation,
and consequence. Run `--next-code architecture`, governance, and `git diff --check`.

**When a check fails** (added 2026-09-28). An owner question without a decider, decision point, recommendation or consequence fails acceptance. The phase then stays `active`, its session record quotes the failing output, and it is completed only after the check passes on a re-run (PLAN-050 overview, *Acceptance and verification*).

## Out of scope

Implementing an extraction, amending the system registry, changing prompt lifecycle, or making a
boundary decision on the owner's behalf.

## Open questions

Boundary direction, future portability, and prompt-lifecycle action are explicitly reserved for the
owner after reviewing the report.
