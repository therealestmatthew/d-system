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
systems: [sys-portfolio, sys-capture, sys-projection, sys-retrieval, sys-realization, sys-plugin, sys-wb-layout, sys-governance]
depends_on: [doc-system-boundary-study-requirements, doc-system-audit, doc-idea-realization-system-plan, doc-prompt-pack-protocol]
---

# System boundary study

## Context and scope

The repository currently contains three concerns with different origins and likely different
audiences: the private personal-productivity system, the idea-realization engine, and the repository
workbench. They share source files, documentation, and governance history, so extracting one before
the data and interface seams are explicit would make the repository harder to operate rather than
simpler. The prompt corpus has the related problem that its 39 active documents preserve both
recurring workflows and build-specific precedents under the same lifecycle label.

This is a discovery plan. Its outcome is a decision-ready boundary report, not a repository split.
All study evidence is written under `docs/00-working/boundary-study/` because it remains a proposal
until the owner selects a direction. A later owner-approved decision may promote findings to an ADR,
amend `systems.yaml`, or create one or more extraction plans.

## This is an investigation plan

The study uses repository evidence rather than historical inference. It classifies the registry's
components by responsibility and actual data/capability crossings; inventories prompts by what an
operator can do with them; and compares viable boundary options against observed dependencies.

The chosen approach is staged evidence before recommendation. Starting with an extraction proposal
would force a desired answer onto unresolved questions about ownership, portability, and release
cadence. Keeping all systems in one repository is therefore an equal candidate, not a failure to
act.

## Implementation phases

| Phase | Outcome | Requirements | Depends on |
|---|---|---|---|
| `phase-bnd-01` | A reproducible system-and-interface evidence inventory, grouped by candidate concern and cross-cutting foundation. | R01, R02, R06 | — |
| `phase-bnd-02` | A complete governed-prompt inventory with reuse classification and navigation findings. | R03, R06 | — |
| `phase-bnd-03` | A decision-ready boundary report that compares options, recommends one next step, and stops for owner direction. | R02, R04, R05, R06 | `phase-bnd-01`, `phase-bnd-02` |

The phases produce evidence first and recommend only after both inventories exist. `phase-bnd-03`
does not implement its recommendation: its next action is an owner decision followed, if needed,
by a separately governed ADR or extraction plan.

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-bnd-01` | System-and-interface inventory with evidence citations |
| R02 | `phase-bnd-01`, `phase-bnd-03` | Dependency map, then boundary options and rules |
| R03 | `phase-bnd-02` | Complete prompt inventory and category totals |
| R04 | `phase-bnd-03` | Options matrix with costs, preconditions, and triggers |
| R05 | `phase-bnd-03` | Owner-decision section and conditional next actions |
| R06 | `phase-bnd-01`, `phase-bnd-02`, `phase-bnd-03` | Logged read-only evidence and review of each scope |

Every requirement maps to a phase, and every phase carries at least one requirement.

## Execution order and real concurrency

`phase-bnd-01` and `phase-bnd-02` have no dependency and write separate evidence files. They both
read the governance corpus but do not edit it, so they may run concurrently after their claims are
checked against then-active phases. `phase-bnd-03` reads both inventories and writes the sole
recommendation file, so it begins only after both complete. All phases declare only existing systems
they analyse; no phase is authorised to change those systems.

## Acceptance and verification

The study is ready for an owner decision when the three requirement groups have mapped evidence,
the prompt inventory reconciles to the governed count, the boundary report compares no fewer than
three options, and its recommendation gives reversible next actions. Each phase runs the governance
check and records the actual output in its session record. The final reviewer verifies that the
report makes no unsupported claim about private data or an unbuilt capability.

## Out of scope

- Extracting a repository, publishing a package or plugin, or changing a remote.
- Reading or moving any `_private/` content.
- Changing schemas, APIs, workbench features, the idea lifecycle, prompt status, or governance
  policy based on preliminary findings.
- Treating a component's current `systems.yaml` status as evidence that it belongs in a particular
  future repository.

## Open questions

- **Boundary direction:** The repository owner decides after `phase-bnd-03`; the recommendation
  should lean toward the smallest reversible separation that matches observed ownership and release
  cadence.
- **Future public portability:** The owner decides before any extraction plan; the study will state
  whether a boundary should remain private, become a local plugin, or be prepared for publication.
- **Prompt lifecycle model:** The owner decides after reviewing `phase-bnd-02`; the study recommends
  a classification model but does not impose new status values.
