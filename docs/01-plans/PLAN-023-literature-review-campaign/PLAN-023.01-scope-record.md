---
schema_version: 1
id: doc-lit-campaign-scope
code: PLAN-023.01
title: Literature-review campaign scope record — research questions, hypothesis register and status vocabulary
kind: plan
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
depends_on:
- doc-research-protocol
parent: doc-lit-campaign
---

# Literature-review campaign scope record

The frozen statement of what the adversarial literature-review campaign answers, attacks and
reports. Content is carried from the authoritative methodology — the review instructions
(`research/literature-review/CLAUDE.md`) and the search protocol
(`research/protocols/literature_review_protocol.md`) — not restated in new words. Thesis
discipline (`GOV-009`): no agent renames a concept, narrows a hypothesis or rewrites this scope
to avoid a collision; a hypothesis change mid-campaign is a blocking finding for the owner.

## Research questions (carried from the search protocol, §2)

- **RQ1 — State representation.** How have prior systems represented knowledge state, epistemic
  status, temporal validity, lifecycle/workflow state, ontological type, and beliefs held by
  different actors?
- **RQ2 — Transition representation.** How have prior systems represented belief revision,
  decisions, state changes, supersession, retraction, validation/falsification, and execution
  and retrospective learning?
- **RQ3 — Provenance and actors.** How have prior systems modeled human actors, software
  agents, organizations/groups, delegation, authority, attribution, evidence and methods, and
  reasoning lineage?
- **RQ4 — Conflict resolution and trust.** How have systems resolved contradictory claims,
  competing beliefs, disagreements between agents, source reliability, domain-specific
  authority, evidence quality, and dependence between sources?
- **RQ5 — Convergence.** Has prior work used independent corroboration, provenance-path
  independence, repeated rediscovery/reaffirmation, or graph topology as an epistemic signal?
- **RQ6 — Agent memory and retrieval.** How do current agent-memory systems perform temporal
  retrieval, provenance-aware retrieval, contradiction handling, belief updating, confidence
  propagation, context selection, and explanation of why a belief is held?
- **RQ7 — Integrated architecture.** Does any existing framework substantially combine all of
  the above for a shared human-agent knowledge system?

## Hypothesis register

### H0 — the null hypothesis (the campaign works to support it)

> **H0: D-System is primarily a recombination of known ideas.**

H0 carries no falsification clause — it is the null. It stands unless some Hn survives
adversarial testing as `POTENTIALLY_DISTINCT` or stronger. A campaign in which nothing survives
the anti-novelty case is a successful research result, not a failure.

### H1–H11 (text and falsification criteria verbatim from the review instructions, §4)

The review instructions (`research/literature-review/CLAUDE.md`) are the authoritative register
text. The frozen cross-referenced register (`research/pre-literature-hypotheses.yaml`) phrases
several claims differently; the differences are noted below, never merged into a blended
phrasing.

| Id | Hypothesis (review-instructions text) | Falsify by finding |
|---|---|---|
| H1 | **Multi-dimensional state model.** Orthogonal ontological + epistemic + lifecycle classifications for knowledge states may be uncommon in agent-memory systems. | A materially equivalent established framework. |
| H2 | **Typed transition semantics as reasoning memory.** Explicit typed transitions between append-only knowledge states preserve reasoning history separately from semantic relationships. | Equivalent state-transition reasoning memory or provenance architecture. |
| H3 | **Provenance as conflict-resolution input.** Transition provenance includes actor identity, domain authority, evidence, method, lineage, and delegation and influences conflict resolution. | Equivalent provenance-aware arbitration/trust systems. |
| H4 | **Independence-aware convergence.** Independent reasoning/evidence paths arriving at equivalent states strengthen epistemic weight while derivative agreement is discounted. | Equivalent provenance/topology-aware corroboration over mixed human-agent knowledge. |
| H5 | **Topology-aware context transfer.** Context selection includes current state, reasoning lineage, supporting evidence, dissent, authority, convergence, and unresolved uncertainty. | Equivalent agent-memory retrieval architecture. |
| H6 | **Integrated human-agent collective knowledge evolution.** The full synthesis may be distinct even if primitives are known. | An existing framework that substantially subsumes D-System end-to-end. |
| H7 | **Development provenance.** Software functionality can be represented as downstream result of an append-only lineage connecting ideas, evidence, decisions, requirements, specifications, plans, execution phases, artifacts, verification, and runtime outcomes. | An established framework with materially equivalent end-to-end provenance. |
| H8 | **Phase-bounded context construction.** A planned development phase can serve as an explicit context boundary for agentic software engineering. | Equivalent task/session/context lifecycle in agentic development systems. |
| H9 | **Bidirectional epistemic traceability.** The system supports idea/knowledge → realized functionality/outcome, and functionality/artifact → reasoning/evidence/assumptions/decisions. | Equivalent bidirectional reasoning-to-runtime traceability. |
| H10 | **Epistemic blast-radius analysis.** Changing/falsifying an assumption, evidence source, or claim identifies downstream decisions, requirements, plans, artifacts, tests, and functionality that require reassessment. | Established impact-analysis systems performing materially equivalent epistemic dependency propagation. |
| H11 | **Runtime-to-knowledge closure.** Runtime telemetry, tests, incidents, and outcomes become provenance-bearing evidence updating the same knowledge structure that generated implementation intent. | Equivalent closed-loop knowledge → implementation → runtime evidence → knowledge architecture. |

### Wording differences against the frozen register (noted, not resolved)

`research/pre-literature-hypotheses.yaml` states each claim more hedged ("may provide a useful
…") and phrases the falsification clauses as instructions ("Find an established framework
that…") rather than criteria. Substantive differences a tester must not blur:

- **H1**: the frozen register scopes the claim to classifications "not commonly integrated in
  existing agent-memory systems" and adds "idea/action" to the lifecycle dimension.
- **H4**: the frozen register makes the topological character explicit ("graph-topological
  epistemic signal … discounted based on shared lineage").
- **H8**: the frozen register adds the consolidation half — context assembled from persistent
  lineage *and execution results consolidated back into persistent memory* — which the review
  instructions' one-line form omits. A challenger that defeats only the assembly half has not
  defeated the frozen register's full claim; record which phrasing the verdict addresses.
- **H10**: the frozen register distinguishes propagation "from epistemic change rather than
  only artifact/requirement change" — the sharper falsification bar; testers should quote it
  when assessing impact-analysis prior art.
- **H7/H9/H10/H11**: the frozen register names starting prior-art families
  (`prior_art_families_to_search`); the search-domain matrix (`PLAN-023.02`) subsumes all of
  them.

Verdicts in `06_hypothesis_tests.md` cite the review-instructions text as primary and note when
a frozen-register nuance changes the assessment.

### Known discrepancy (recorded, not resolved)

The search protocol's Pass 3 and stop conditions name only **H1–H6**; the review instructions
cover **H1–H11**. The pack follows the review instructions: all eleven hypotheses are tested
and all eleven need at least one serious challenger before the stop conditions hold. This
discrepancy is a finding for the owner and the stage-5 pack audit, recorded here so no search
agent rediscovers it as an ambiguity.

## Status vocabulary

Every hypothesis verdict and every source-level assessment uses exactly:

- `LIKELY_ALREADY_KNOWN`
- `KNOWN_COMPONENT_NEW_INTEGRATION`
- `POTENTIALLY_DISTINCT`
- `INSUFFICIENT_EVIDENCE`

`NOVEL` is permitted only under the methodology's stronger-scrutiny rule (substantially
stronger review and expert scrutiny — practically, not from this first formal review). **"No
prior work exists" is not a permitted verdict**: a failed search is recorded as a search that
failed, with its queries, in the reproducibility ledger.

## Boundaries

The campaign compares prior art against both the conceptual architecture and the architecture
actually encoded in the codebase (the frozen adversarial codebase review is the record of the
latter). Collisions are recorded first; architecture is revised only in the synthesis phase,
and only as recorded implications (`10_architecture_implications.md`), never as code. The
frozen baseline and the historical seed ledger are never modified.
