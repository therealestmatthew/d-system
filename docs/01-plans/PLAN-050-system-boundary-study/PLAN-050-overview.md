---
schema_version: 1
id: doc-system-boundary-study
code: PLAN-050
title: System boundary study
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-gov-docs, sys-backlog]
depends_on: [doc-system-boundary-study-requirements, doc-system-audit, doc-idea-realization-system-plan, doc-prompt-pack-protocol]
---

# System boundary study

## Context and scope

This discovery plan assesses the boundaries among the personal-productivity system, the
idea-realization engine, the repository workbench, and the governance/framework layer. It also
accounts for every other registered system through an explicit disposition rather than forcing it
into those four concerns. The outcome is a governed draft architecture report for an owner decision,
not an extraction.

The detailed work is split into child plans. A phase reads its own child plan and the requirement it
cites; this overview is the map and completion gate, not required opening context for every phase.

## Chosen design

The study is evidence first, then synthesis. It records a revision baseline for each inventory,
separates reusable prompt characteristics into independent fields, and treats no repository split as
a valid recommended outcome. Raw working evidence may be staged under `docs/00-working/`, but the
final phase promotes every relied-upon finding into a governed draft architecture document.

## Phases

| Child plan | Phase | Outcome | Depends on |
|---|---|---|---|
| [PLAN-050.01](PLAN-050.01-system-inventory.md) | `phase-bnd-01` | Whole-registry ownership and interface inventory | — |
| [PLAN-050.02](PLAN-050.02-prompt-classification-rubric.md) | `phase-bnd-02` | Prompt classification rubric and pilot | `phase-bnd-01` |
| [PLAN-050.03](PLAN-050.03-prompt-corpus-inventory.md) | `phase-bnd-05` | Complete prompt-corpus inventory and navigation findings | `phase-bnd-02` |
| [PLAN-050.04](PLAN-050.04-system-backlog-review.md) | `phase-bnd-03` | General system and backlog portfolio review | `phase-bnd-05` |
| [PLAN-050.05](PLAN-050.05-boundary-decision-report.md) | `phase-bnd-04` | Governed boundary report and owner decision gate | `phase-bnd-03` |

## Requirement coverage

| Requirement | Child plan / phase |
|---|---|
| R01–R02 | PLAN-050.01 / `phase-bnd-01` |
| R03 | PLAN-050.02 and PLAN-050.03 / `phase-bnd-02`, `phase-bnd-05` |
| R04 | PLAN-050.04 / `phase-bnd-03` |
| R05–R06 | PLAN-050.05 / `phase-bnd-04` |
| R07 | Every child plan |

## Execution order and real concurrency

The phases are serial. Each produces an input the next phase consumes, and all write study
evidence through the same documentation/governance surface. The active-claim budget may add waiting
time; none of these phases assumes a free slot.

## Acceptance and verification

The study is complete only when the five child-plan outcomes exist, the final architecture report
reconciles its evidence to current `dev`, and the owner has the explicit decisions and conditional
next actions required by `REQ-033` R06. Each phase runs governance and records its actual results.

## Out of scope

Implementing a repository split, changing product behaviour, reading `_private/`, modifying prompt
lifecycle status, or reprioritising the backlog.

## Open questions

The owner decides boundary direction, future portability, and any prompt-lifecycle change only after
the final report. No open question authorises a change during the study.
