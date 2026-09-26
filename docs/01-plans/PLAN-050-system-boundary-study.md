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
workbench. It also contains adjacent, incubating, legacy, and retired systems that cannot honestly
be forced into those three concerns. They share source files, documentation, and governance history,
so extracting one before the data and interface seams are explicit would make the repository harder
to operate rather than simpler. The prompt corpus has the related problem that its active documents
preserve both recurring workflows and build-specific precedents under the same lifecycle label.

This is a discovery plan. Its outcome is a decision-ready boundary report, not a repository split.
The first three phases may use `docs/00-working/boundary-study/` for working evidence, but the final
phase promotes the relied-upon findings into a governed draft architecture report with a code
allocated at that time. A later owner-approved decision may amend `systems.yaml` or create one or
more extraction plans.

## This is an investigation plan

The study uses repository evidence rather than historical inference. It classifies the registry's
components by responsibility and actual data/capability crossings; inventories prompts through
independent role, reuse, precedent, review, and entry-point fields; conducts a bounded portfolio
review of systems and backlog; and compares viable boundary options against observed dependencies.

The chosen approach is staged evidence before recommendation. Starting with an extraction proposal
would force a desired answer onto unresolved questions about ownership, portability, and release
cadence. Keeping all systems in one repository is therefore an equal candidate, not a failure to
act.

## Implementation phases

| Phase | Outcome | Requirements | Depends on |
|---|---|---|---|
| `phase-bnd-01` | A reproducible whole-registry system-and-interface inventory, including adjacent-system dispositions. | R01, R02, R07 | — |
| `phase-bnd-02` | A complete governed-prompt inventory using independent classification fields and navigation findings. | R03, R07 | `phase-bnd-01` |
| `phase-bnd-03` | A bounded general review of the system registry and backlog portfolio. | R04, R07 | `phase-bnd-02` |
| `phase-bnd-04` | A governed draft architecture report that compares boundary options, recommends one next step, and stops for owner direction. | R02, R05, R06, R07 | `phase-bnd-03` |

The phases produce evidence first and recommend only after all three inventories/reviews exist.
`phase-bnd-04` does not implement its recommendation: its next action is an owner decision followed,
if needed, by a separately governed ADR or extraction plan.

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-bnd-01` | Whole-registry inventory with evidence citations and dispositions |
| R02 | `phase-bnd-01`, `phase-bnd-04` | Dependency map, then boundary options and rules |
| R03 | `phase-bnd-02` | Complete prompt inventory with independent fields |
| R04 | `phase-bnd-03` | Bounded system-and-backlog portfolio review |
| R05 | `phase-bnd-04` | Options matrix with costs, preconditions, and triggers |
| R06 | `phase-bnd-04` | Governed owner-decision section and conditional next actions |
| R07 | `phase-bnd-01`, `phase-bnd-02`, `phase-bnd-03`, `phase-bnd-04` | Revision records and final drift reconciliation |

Every requirement maps to a phase, and every phase carries at least one requirement.

## Execution order and real concurrency

The phases are deliberately serial. Each produces an input the next phase relies on, and the study
uses the documentation and backlog systems that the repository's claim checker treats as shared
locks. The current active-claim budget may further delay them; no phase assumes a free slot. The
phases declare the systems whose documentation or backlog records they edit, not every system they
read; no phase is authorised to change an analysed system's implementation.

## Acceptance and verification

The study is ready for an owner decision when the three evidence/review phases have completed, the
prompt inventory reconciles to its recorded baseline, the final report has been promoted to a
governed draft architecture document, the boundary report compares no fewer than three options,
and its recommendation gives reversible next actions. Each phase records its source revision and
runs the governance check. The final reviewer verifies that the report makes no unsupported claim
about private data or an unbuilt capability.

## Out of scope

- Extracting a repository, publishing a package or plugin, or changing a remote.
- Reading or moving any `_private/` content.
- Changing schemas, APIs, workbench features, the idea lifecycle, prompt status, or governance
  policy based on preliminary findings.
- Reprioritising, completing, or otherwise changing backlog phases as part of the general review.
- Treating a component's current `systems.yaml` status as evidence that it belongs in a particular
  future repository.

## Open questions

- **Boundary direction:** The repository owner decides after `phase-bnd-04`; the recommendation
  should lean toward the smallest reversible separation that matches observed ownership and release
  cadence.
- **Future public portability:** The owner decides before any extraction plan; the study will state
  whether a boundary should remain private, become a local plugin, or be prepared for publication.
- **Prompt lifecycle model:** The owner decides from `phase-bnd-04`'s consolidated report; the study
  recommends an independent-field classification model but does not impose new status values.
