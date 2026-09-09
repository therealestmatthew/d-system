---
schema_version: 1
id: doc-idea-plan-governance-delivery
code: PLAN-017.06
title: Governance integration and phase delivery
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Governance integration and phase delivery

## What we know

**This repository has never finished a large plan.** Two of twenty plans are complete; the largest
ever completed had six phases; no plan with eight or more phases has ever completed. Whatever this
architecture proposes has to land value in its first phase, because the base rate says the later
phases may not arrive.

**The complexity review is not available to run alongside this work.** `phase-gov-03` — *"Run the
systems review for scope creep and complexity"*, with a stated bias toward removal — is queued
behind `phase-gov-02`, which is queued behind `phase-term-02`. The recommendation that the review
run "alongside" the architecture was not actually executable. What is executable: the live repairs
need no schema change and can proceed now; the schema extensions genuinely wait.

**This plan set changed a governance rule to exist in the shape it does.** The four area folders the
owner asked for were rejected by `src/governance/codes.py`, which permitted no nesting inside a plan
folder. The rule was relaxed to allow exactly one area-folder level, and documented in `GOV-005`
where it had never been written down. `PROMPT-003` instructs the review session to add *"no new
system, kind, folder or schema"* — this is a folder-structure change made before that review, on the
owner's explicit decision, and it is recorded here so the review inherits it as a finding rather
than discovering it.

## What we propose

### Phase breakdown

Each phase fits one session and is independently valuable. The first depends on nothing in this
architecture beyond its own scope.

| Phase | Delivers | Needs a schema change? |
|---|---|---|
| **1. Safe writing and single-sourced replay** | `--title` stdin/file input, the corrected `.claude/commands/idea.md`, one replay module in `src/`, the `from` check, the two broken tests repaired with synthetic fixtures | No |
| **2. Plan status consistency** | The severity matrix in `src/governance/backlog.py`, attribution by `plan` OR `sources` counted once, reconciliation of every mislabelled plan found by a fresh inventory | No |
| **3. Activation before work** | `.claude/commands/backlog.md` ordering, and `AGENTS.md`/`GOV-001`/`GOV-002` updated together so they agree | No |
| **4. Event identity and amendments** | Optional `eid`, the `amended` event, identity-based `amends`, the merge-over-chain fold, the primary key change | Yes |
| **5. Annotations and links** | The `annotated` and `linked` events, three link types, derived inverses, validated `promoted_to` arrays | Yes |

Phases 4 and 5 depend on the complexity review completing. Phases 1-3 do not.

Splitting 2 from 3 is deliberate. The draft that preceded this document bundled four repairs, a full
plan re-inventory, activation-command changes and edits to three governance documents into one
session with thirteen deliverables — the shape the completion evidence says does not finish.

### Six children, and why that is not six projects

Each open plan needs at least one non-cancelled phase, and this plan set has six children. That
obligation is met by naming children in a phase's `sources`, not by inventing one phase per child:
phase 1 sources the writing and event-contract children, phase 2 and 3 source the plan-lifecycle
child, and so on. Document count and phase count are independent, and a category document exists to
hold a contract, not to justify a work item.

This was the failure in the preceding draft. It asserted that shared phases cover children through
`sources` while writing a single phase that named none of them — so the architecture violated the
very `L3` rule it exists to enforce, and only the code errors above it kept that hidden.

### Provenance is recorded, never enforced

Requiring plans to trace to ideas is **not built**. There are twenty-one plans and zero promoted
ideas; enforcing the rule would mean fabricating captures into the evidence log, and would require
resurrecting a migrator whose deletion was an acceptance condition of a completed phase. Genuine
promotions are recorded. A future proposal would need prospective evidence of lost provenance and a
capture process that manufactures no history.

### Governance documents change together or not at all

Activation ordering appears in `AGENTS.md`, `GOV-001`, `GOV-002` and `.claude/commands/backlog.md`.
A change to one without the others produces exactly the drift `GOV-005` was written to prevent.
Recommend amending the existing protocols rather than adding a second governance document
(`Q-H5`); the rules belong where agents already look.

## What is open

- **Whether phases 4 and 5 should wait for `phase-gov-03`, or whether the review should be promoted
  in `next_up` so it stops blocking them.** This is the owner's call and it is the most consequential
  open item in the plan set. Recommend promoting the review chain: the schema extensions are the
  larger commitment, and a review whose bias is removal should see them before they ship.
- `Q-A1`/`Q-H5`: whether `ADR-010` gains a successor ADR or an amendment. Recommend a narrowly
  scoped successor per `GOV-001`, preserving all existing text.
- Whether the area-folder rule survives the complexity review. It may not, and that is a legitimate
  outcome; the children would flatten and their codes would not change.
- `phase-idea-02`'s scope needs updating before it executes, to write findings through the sanctioned
  writer and to enter and leave `triaging`. The exact edit is not yet written.

## What it touches

`docs/09-backlog/backlog.yaml`, `docs/08-governance/codes.yaml`, the generated
`docs/08-governance/catalog.md`, `AGENTS.md`, `GOV-001`, `GOV-002`, `GOV-005`,
`.claude/commands/backlog.md`, `src/governance/codes.py`, `src/governance/backlog.py`, and the
headers of any plan the fresh inventory finds mislabelled.

## How it is verified

`R14`-`R16`, `R18`. `uv run python -m src.governance` exits 0 and the committed catalog matches its
regenerated output byte for byte. Every open plan, including all six children here, is named by a
non-cancelled phase. The naming rules accept a child in an area folder, reject a second nesting
level, reject an overview inside one, and still require the plan folder to announce the parent code.
Each proposed phase carries acceptance and verification criteria that a reviewer can check without
reading this document.

## Conflicts with other categories

`C08` and `C09` separate approval, status and claim ordering — counts derive consistency, never
consent. `C16` is live and self-referential: authoring this architecture is completed documentation
work under `PLAN-015`, which is itself `draft`, so the first repair's inventory must include this
plan set rather than treating the four-plan baseline as a closed list. `C13` reuses the existing
triage phase instead of duplicating it. `C15` bounds what plan history can be reconstructed at all.
