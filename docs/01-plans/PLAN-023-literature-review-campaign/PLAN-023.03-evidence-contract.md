---
schema_version: 1
id: doc-lit-campaign-evidence-contract
code: PLAN-023.03
title: Literature-review evidence contract — extraction schema, reproducibility ledger format, scoring rules and file locations
kind: plan
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
depends_on: []
parent: doc-lit-campaign
---

# Literature-review evidence contract

The schema every extraction fills, the reproducibility-ledger format every search appends to,
the scoring and collision rules carried verbatim from the methodology, and the file locations
under `research/` — fixed here, the decision Prompt A delegated to the pack. The delegation
pack's first kickoff (`LIT-01 K`) creates the files; no file exists until the campaign runs.

## File locations (fixed)

| File | Path | Created by | Format |
|---|---|---|---|
| Reproducibility ledger | `research/literature-review/00_search_ledger.csv` | LIT-01 K | CSV, one row per search |
| Source inventory (deliverable 03) | `research/literature-review/03_source_inventory.csv` | LIT-01 K | CSV, one row per candidate source |
| Evidence matrix (deliverable 04) | `research/literature-review/04_evidence_matrix.csv` | LIT-04 K | CSV, one row per deep-read source |

The `00_` prefix keeps the ledger sorted ahead of the thirteen deliverables while marking it as
infrastructure rather than one of them. All other deliverables (`01`, `02`, `05`–`13`) are
Markdown files in `research/literature-review/` named exactly as the methodology's §15 lists
them. The historical seed ledger (`research/sources/source_ledger.md`) and the seed inventory
(`research/sources/cited_sources_chat_seed.md`) are never modified; validation outcomes for
seed sources are recorded in `13_validated_bibliography.md` only.

## Reproducibility ledger format

One row per search, appended at the time the search runs. **A search that logged nothing did
not happen.** Columns:

| Column | Content |
|---|---|
| `search_id` | `LIT-<phase>-S<seq>` e.g. `LIT-01-S014`; unique, monotonically increasing per phase |
| `domain_id` | The matrix domain the search served (`D01`–`D72`), so "domains searched with variants" is computable from the ledger. Cross-domain Phase E collision searches use the hypothesis id (`H1`–`H11`) instead |
| `pass` | `1`, `2`, `3` or `4` |
| `strategy_phase` | `A` vocabulary, `B` backward chain, `C` forward chain, `D` system search, `E` collision |
| `query` | Verbatim query text |
| `provider` | Provider or endpoint (web search, arXiv API, Semantic Scholar, OpenAlex, Crossref, GitHub, W3C, …) |
| `date` | ISO date the search ran |
| `filters` | Date ranges, field filters, venue filters; `none` if none |
| `result_ids` | Identifiers of results inspected (DOIs, arXiv ids, URLs), `;`-separated |
| `kept` | Identifiers added to the inventory/matrix from this search |
| `inclusion_rationale` | Why kept rows were kept (short) |
| `exclusion_rationale` | Why inspected-but-dropped rows were dropped (short) |
| `duplicate_handling` | Ids already present and how deduplicated; `none` if none |
| `chain_decision` | For strategy B/C rows: which citations were followed and why |

## Source inventory format (deliverable 03)

One row per candidate source encountered in Pass 1. Columns: `source_id` (stable slug),
`citation`, `year`, `url_or_doi`, `source_type` (standard / peer-reviewed / conference /
preprint / OSS / tech report / lead), `domain_ids` (matrix domains it belongs to),
`found_by` (ledger `search_id`), `component_prescore` (0–5), `architecture_prescore` (0–5),
`collision_candidate` (`yes`/`no` — the top-20 list is the `yes` rows ranked),
`dedup_of` (source_id if duplicate), `status` (`candidate` / `deep_read` / `excluded`),
`exclusion_reason` (per the protocol's §7; excluded rows are marked, never deleted).

## Evidence matrix extraction schema (deliverable 04)

One row per deeply read source. Every field below is required; `NOT_APPLICABLE` and
`NOT_DETERMINABLE_FROM_ACCESS` are permitted values, blank is not. Fields carry the review
instructions' §9 set plus the search protocol's §8 minimums plus the contract additions marked
(+):

1. `source_id` (links back to the inventory row and its ledger provenance)
2. `citation` — full citation
3. `url_doi` — canonical URL/DOI
4. `source_type`
5. `research_domain` — matrix domain ids
6. `problem_addressed`
7. `state_model`
8. `transition_model`
9. `provenance_model`
10. `actor_model`
11. `temporal_model`
12. `conflict_trust_mechanism`
13. `convergence_independence_mechanism`
14. `memory_model`
15. `retrieval_context_model`
16. `decision_representation`
17. `requirement_derivation`
18. `specification_representation`
19. `planning_model`
20. `execution_unit_session_model`
21. `artifact_code_linkage`
22. `test_verification_linkage`
23. `deployment_linkage`
24. `runtime_observation_linkage`
25. `feedback_to_knowledge_mechanism`
26. `forward_traceability`
27. `backward_traceability`
28. `change_impact_mechanism`
29. `human_agent_scope`
30. `implementation_availability`
31. `evaluation_method`
32. `strongest_dsystem_overlap`
33. `strongest_difference`
34. `hypotheses_challenged` — subset of `H1`–`H11`, `;`-separated; the field the Pass 3 gate
    counts challengers from
35. `component_overlap_score` — 0–5, rubric below
36. `architecture_overlap_score` — 0–5, rubric below
37. `critical_collision` — `yes`/`no` per the flag rules below
38. `derivative_ancestor` (+) — `source_id` or citation of the shared ancestor when this source
    inherits its mechanism; `none` when independent. Five papers inheriting one mechanism are
    one primary lineage plus four derivative applications, never five confirmations
39. `access_limitation` (+) — `full_text` / `abstract_only` / `preprint_version` /
    `secondary_coverage`; ratified decision 5 requires paywalled assessments to say so rather
    than present as full reads
40. `evidence_locator` — section/page/figure for every load-bearing claim; a claim that cannot
    be traced is removed, not softened
41. `interpretation_confidence` — `high` / `medium` / `low`
42. `verbatim_notes` — short quotes with locators
43. `second_review` (+) — for `critical_collision: yes` rows after Pass 3: `confirmed` /
    `disputed: <summary>` / `pending`; filled only by the independent R reviewer

## Similarity scoring (verbatim from the methodology)

**Component overlap, 0–5**: 0 unrelated · 1 adjacent · 2 one relevant primitive · 3 multiple
relevant primitives · 4 strong mechanism overlap · 5 materially equivalent mechanism.

**Architecture overlap, 0–5**: 0 unrelated · 1 broad objective only · 2 partial architecture ·
3 substantial subsystem overlap · 4 near end-to-end overlap · 5 materially subsumes D-System.

Scores are triage aids, not conclusions.

## CRITICAL_COLLISION flag rules (verbatim from the methodology)

Flag a source `critical_collision: yes` if any of:

- component overlap ≥ 4,
- architecture overlap ≥ 4,
- it directly falsifies any of H1–H11,
- it spans at least four adjacent stages in: Reasoning → Decision → Requirement →
  Specification → Plan → Execution → Artifact → Verification → Deployment → Runtime Evidence →
  Knowledge Update.

Every critical collision receives a second independent review (delegation pack `R` sections):
a different agent, receiving the source and the evidence row, never the first assessment's
rationale. Disagreements are recorded in `05_critical_collisions.md`, not averaged away.

## Negative evidence and verdicts

Assessments use only the scope record's status vocabulary. "No prior work exists" is never
written; a failed collision search is a ledger row with its queries and empty `kept`. Absence
of a feature in a paper is recorded only after reading its scope — never inferred from an
abstract silence (an `abstract_only` access limitation caps `interpretation_confidence` at
`medium` for absence claims).

## Seed-source promotion (methodology §16)

A seed source from `research/sources/` enters `13_validated_bibliography.md` only after all
five steps, recorded per source: (1) bibliographic identity verified; (2) primary source
inspected; (3) cited interpretation confirmed; (4) exact supporting location recorded;
(5) status updated — in the validated bibliography, never by editing the seed ledger. A seed
source that fails a step is listed with the failing step named, not silently dropped.
