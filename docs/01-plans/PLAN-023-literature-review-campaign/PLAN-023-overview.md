---
schema_version: 1
id: doc-lit-campaign
code: PLAN-023
title: Adversarial literature-review campaign — overview
kind: plan
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
- sys-backlog
depends_on:
- doc-research-protocol
- doc-prompt-literature-review-pre-plan-package
- doc-prompt-literature-review-pack-factory
---

# Adversarial literature-review campaign — overview

The campaign plan for the adversarial D-System literature review: the research pack's spine,
manufactured by executing the pack factory ([PROMPT-028](../../02-prompts/PROMPT-028-literature-review-pack-factory.md))
under the research pack protocol ([GOV-009](../../08-governance/GOV-009-research-protocol.md)).
The owner's seven ratified decisions are in Prompt A
([PROMPT-027](../../02-prompts/PROMPT-027-literature-review-pre-plan-package.md)) and are not
re-decided here. The content methodology — mission, H0, H1–H11, the 72 domains, scoring,
collision rules, the thirteen deliverables, stop conditions — lives in
`research/literature-review/CLAUDE.md` and `research/protocols/literature_review_protocol.md`
and wins on content; this plan and `GOV-009` govern process.

## The pack

| Artifact | Document |
|---|---|
| Campaign plan and phase graph (this file, including the descope ladder) | `PLAN-023` |
| Scope record — RQ1–RQ7, H0/H1–H11 with falsification criteria, status vocabulary | [`PLAN-023.01`](PLAN-023.01-scope-record.md) |
| Search-domain matrix — 72 domains → Pass 1 phases, variants, collision queries | [`PLAN-023.02`](PLAN-023.02-search-domain-matrix.md) |
| Evidence contract — extraction schema, ledger format, scoring, file locations | [`PLAN-023.03`](PLAN-023.03-evidence-contract.md) |
| Delegation pack — every prompt the execution sessions dispatch, verbatim | `PROMPT-029` |

What the pack deliberately omits: the coordinator prompt and the kick-off record are `GOV-009`
stages 6–8, written only after the stage-5 adversarial pack audit; every campaign deliverable
(`01`–`13`) is the execution sessions' output, not the pack's.

## Runway ruling (owner, 2026-09-12)

The planning estimate in Prompt A was four to six execution sessions. The honest estimate for
full variant coverage of 72 domains and 20–30 deep reads with the complete extraction schema is
**seven sessions (range six to eight)**, and the owner accepted it when confirming the pack
plan: **7 sessions stands (range 6–8)**, one phase per session as below. Runway remains
"whatever the passes need" (ratified decision 7): saturation is demonstrated against the
ledger, never squeezed into a budget, and the descope ladder below exists for emergencies only.

## Phase graph

Seven phases, sized one session each, dependency-ordered so no pass starts before the pass it
feeds on closes. All enter the backlog `queued` and are never added to `next_up` — demo work
wins every conflict (ratified decision 4); promotion to the queue front is the owner's act at
kick-off.

```text
phase-lit-01  Pass 1a  broad map: D01–D20, D28–D32 (knowledge representation,
      |                provenance, epistemics) — creates ledger + inventory
phase-lit-02  Pass 1b  broad map: D21–D27, D33–D45 (agent memory, decision
      |                intelligence, requirements and rationale)
phase-lit-03  Pass 1c  broad map: D46–D72 (digital thread, specification,
      |                agentic SE, runtime feedback) — closes Pass 1:
      |                terminology map, domain map, top-20 collision candidates
phase-lit-04  Pass 2a  deep reading: top collision candidates + backward chaining
      |
phase-lit-05  Pass 2b  deep reading: foundational works + forward chaining —
      |                completes the 20–30-source evidence matrix
phase-lit-06  Pass 3   adversarial hypothesis testing H1–H11, collision second
      |                reviews (R), 05 + 06 written
      |   ← OWNER CHECK-IN (ratified decision 3: the campaign's one pause)
phase-lit-07  Pass 4   synthesis: 07–13, adversarial synthesis review (A),
                       final stop-condition gate
```

The Pass 1 phases run sequentially (not in parallel) because all three append to one shared
reproducibility ledger and one running terminology map. The pre-synthesis owner check-in is
encoded as `phase-lit-07`'s stated entry condition in the backlog; the `depends_on` chain
guarantees no synthesis while any evidence phase is open. A critical issue mid-campaign — a
collision that falsifies scope, a methodology defect invalidating collected evidence — gets
`GOV-009`'s dual adversarial review first and pauses the campaign outside the gate only if it
survives unresolved.

## Deliverable coverage

Each of the thirteen campaign deliverables is owned by the phase whose backlog `deliverables`
list it — a deliverable no phase produces is impossible by construction. `01`–`03` are built
incrementally from `phase-lit-01` on; the completing phase owns each.

| Deliverable | Owning phase |
|---|---|
| `01_terminology_map.md`, `02_domain_map.md`, `03_source_inventory.csv` | phase-lit-03 |
| `04_evidence_matrix.csv` | phase-lit-05 |
| `05_critical_collisions.md`, `06_hypothesis_tests.md` | phase-lit-06 |
| `07_anti_novelty_case.md` … `12_experiment_proposals.md`, `13_validated_bibliography.md` | phase-lit-07 |

The reproducibility ledger (`00_search_ledger.csv`) is infrastructure, not one of the thirteen;
`phase-lit-01`'s kickoff creates it and every later phase appends (evidence contract,
`PLAN-023.03`).

## Stop conditions as the completion gate

The campaign is complete when the methodology's stop conditions are **measured, not asserted**,
by `phase-lit-07`'s final gate: every one of the 72 domains searched with terminology variants
(computed from the ledger's domain-id column); backward and forward chaining on the strongest
collisions (ledger chain decisions); every H1–H11 with at least one serious challenger
(evidence matrix, hypotheses-challenged field); the strongest 20–30 sources deeply compared
(matrix row count); saturation demonstrated by duplicate rates in late searches; every critical
collision second-reviewed. This produces a first research memo, not a final novelty claim.

## Standing constraints

`GOV-009`'s standing rules bind every campaign agent: thesis discipline (record collisions,
never mutate the thesis; architecture revised only in synthesis, only as recorded
implications), evidence hygiene (ledger rows for every search, generated summaries are leads
never evidence, derivative sources never counted independent), agent hygiene (search,
extraction and review are separate dispatches; reviewers get sources and evidence rows, never
rationale), cost protocol (Haiku for mechanical gates, Sonnet standard everywhere else, Opus at
most one documented escalation per campaign, at most two fix cycles per item). Provider
constraint per ratified decision 5: web search and free/open APIs only; paywalled sources
assessed from abstract/preprint/secondary coverage with the limitation recorded on the evidence
row. The frozen baseline (Prompt A's inventory) and the historical seed ledger are never
modified. The second reviewer for critical collisions runs as a **pack-supplied prompt on a
general-purpose agent** (owner ruling, 2026-09-12) — no committed charter; the delegation
pack's `R` sections carry the reviewer prompt verbatim.

## Descope ladder (drafter's proposal — ratified at the stage-5 pack-audit gate)

Emergencies only. **No rung is taken without the owner's explicit direction** (`GOV-009`); a
campaign that stops early stops at a phase boundary with resume state in its session record.
Rungs in order, first cut first:

1. **Fold near-synonym domains into their parents for Pass 1 breadth** — doxastic logic (D10)
   under epistemic logic (D09), micropublications (D20) under nanopublications (D19), digital
   engineering (D48) under digital thread (D47), autonomic computing (D70) under MAPE-K (D69),
   QOC (D42) under IBIS/design rationale (D41/D37) — survey plus the pre-crafted collision
   query only, each fold logged in the ledger as a fold, not silently skipped.
2. **Reduce Pass 2 deep reads from 20–30 to the top 15** by collision pre-score. Every
   `CRITICAL_COLLISION` always keeps its deep read regardless of this rung.
3. **Drop forward citation chaining (Phase C) for non-critical sources.** Backward chaining
   stays everywhere — ancestry is what the independence rules depend on.
4. **Thin synthesis deliverables 09, 10 and 12** (reuse recommendations, architecture
   implications, experiment proposals) to structured findings lists. 07, 08 and 11 are never
   thinned — the anti-novelty case and what survives it are the campaign's point.
5. **Restrict seed-ledger validation to seeds actually cited in synthesis claims**, with
   `13_validated_bibliography.md` recording the restriction explicitly.

Never cut, at any rung: at least one serious challenger per H1–H11; second reviews of critical
collisions; the reproducibility ledger; the anti-novelty case; the hypothesis tests; any pass
wholesale. Domains and depth are surrendered before any hypothesis or any pass.
