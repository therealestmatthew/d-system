# Literature Review Protocol

## 1. Objective

Determine whether D-System's architecture, mechanisms, or synthesis already exist in published research, standards, open-source systems, patents, technical reports, or adjacent academic traditions.

The review is adversarial: **the goal is to kill weak novelty claims, not defend them.**

---

## 2. Research questions

### RQ1 — State representation
How have prior systems represented:
- knowledge state,
- epistemic status,
- temporal validity,
- lifecycle/workflow state,
- ontological type,
- beliefs held by different actors?

### RQ2 — Transition representation
How have prior systems represented:
- belief revision,
- decisions,
- state changes,
- supersession,
- retraction,
- validation/falsification,
- execution and retrospective learning?

### RQ3 — Provenance and actors
How have prior systems modeled:
- human actors,
- software agents,
- organizations/groups,
- delegation,
- authority,
- attribution,
- evidence and methods,
- reasoning lineage?

### RQ4 — Conflict resolution and trust
How have systems resolved:
- contradictory claims,
- competing beliefs,
- disagreements between agents,
- source reliability,
- domain-specific authority,
- evidence quality,
- dependence between sources?

### RQ5 — Convergence
Has prior work used:
- independent corroboration,
- provenance-path independence,
- repeated rediscovery/reaffirmation,
- graph topology,
as an epistemic signal?

### RQ6 — Agent memory and retrieval
How do current agent-memory systems perform:
- temporal retrieval,
- provenance-aware retrieval,
- contradiction handling,
- belief updating,
- confidence propagation,
- context selection,
- explanation of why a belief is held?

### RQ7 — Integrated architecture
Does any existing framework substantially combine all of the above for a shared human-agent knowledge system?

---

## 3. Research domains

Search each domain independently before synthesis.

1. Knowledge graphs and Semantic Web
2. Provenance and W3C PROV
3. Temporal / bi-temporal knowledge graphs
4. Event sourcing and append-only architectures
5. Belief revision / AGM theory
6. Epistemic and doxastic logic
7. Defeasible reasoning
8. Computational argumentation
9. Truth discovery / data fusion
10. Subjective logic and trust models
11. Multi-agent belief systems
12. Scientific discourse representation
13. Nanopublications / micropublications
14. Agent memory / long-term memory
15. RAG and graph-RAG
16. Human-AI collective intelligence
17. Decision provenance / decision intelligence
18. Data lineage and evidence graphs
19. Temporal databases / event calculus
20. Knowledge evolution / ontology evolution

---

## 4. Search strategy

### Phase A — Vocabulary discovery

For each research domain:

1. Search broad review/survey queries.
2. Extract field-specific terminology.
3. Add terminology to `search_terms.md` or the agent's working query ledger.
4. Identify canonical authors, standards, datasets, benchmarks, and foundational papers.

Do not assume D-System vocabulary matches academic vocabulary.

Examples:
- `"belief revision" provenance knowledge graph`
- `"epistemic provenance" knowledge graph`
- `"argumentation framework" source reliability`
- `"truth discovery" source dependence`
- `"agent memory" provenance temporal knowledge graph`
- `"decision provenance" ontology`
- `"event sourced" knowledge graph`
- `"temporal knowledge graph" belief`
- `"multi-agent" conflicting beliefs knowledge graph`

### Phase B — Backward chaining

For every highly relevant paper:
- inspect references,
- identify theoretical ancestors,
- locate seminal papers,
- record which concept each ancestor contributes.

### Phase C — Forward chaining

Find papers that cite foundational/relevant work:
- later extensions,
- implementations,
- critiques,
- comparative evaluations,
- agentic-AI applications.

### Phase D — System search

Search:
- GitHub
- arXiv
- Semantic Scholar / OpenAlex / Crossref where available
- conference proceedings
- W3C standards
- technical blogs only as leads
- patents where relevant

Open-source systems should be evaluated separately from academic papers.

### Phase E — Collision search

For each D-System hypothesis, construct queries designed to find an exact collision.

Example for H4:
- `"provenance" "independent sources" knowledge graph confidence`
- `"source dependence" truth discovery graph`
- `"corroboration" provenance paths`
- `"independent evidence" epistemic graph`
- `"convergence" multi-agent belief provenance`

A novelty claim survives only after its strongest collision searches fail.

---

## 5. Source priority

Prefer, in order:

1. Standards / normative specifications
2. Peer-reviewed papers
3. Major conference proceedings
4. University / industrial research publications
5. Preprints
6. Mature open-source implementations
7. Technical reports
8. Blog posts / product pages as leads only

A product page does not establish academic novelty.

---

## 6. Inclusion criteria

Include a source when it contributes materially to at least one D-System component:

- state classification,
- epistemic representation,
- temporal validity,
- state transitions,
- append-only history,
- provenance,
- actor attribution,
- authority/trust,
- evidence lineage,
- conflict resolution,
- convergence/corroboration,
- memory retrieval,
- knowledge transfer,
- human-agent collaboration.

---

## 7. Exclusion criteria

Exclude or mark low-priority:

- generic RAG papers with no relevant memory/provenance mechanism,
- generic KG papers with no overlap beyond graph storage,
- opinion pieces with no implementation or formalism,
- duplicated derivative summaries,
- marketing claims unsupported by technical detail.

Do not delete excluded records if they were reviewed; mark the exclusion reason.

---

## 8. Evidence extraction

For every included source, populate `evidence_matrix_template.csv`.

Minimum extraction:

- bibliographic identity,
- source type,
- research domain,
- problem addressed,
- state model,
- transition model,
- provenance model,
- actor model,
- conflict/trust mechanism,
- convergence/independence mechanism,
- temporal model,
- retrieval mechanism,
- human-agent scope,
- implementation availability,
- evaluation method,
- strongest overlap with D-System,
- strongest difference,
- which novelty hypothesis it challenges,
- confidence in interpretation,
- verbatim locator/quote notes,
- URL/DOI.

Never record "supports novelty" merely because a paper omits a feature. Absence requires a careful reading of scope and implementation.

---

## 9. Similarity scoring

Use two separate scores.

### Component overlap score (0-5)
- 0 = unrelated
- 1 = adjacent
- 2 = shares one relevant primitive
- 3 = shares multiple primitives
- 4 = strongly overlaps a D-System mechanism
- 5 = materially equivalent mechanism

### Architecture overlap score (0-5)
- 0 = unrelated architecture
- 1 = shared broad objective
- 2 = partial conceptual overlap
- 3 = substantial subsystem overlap
- 4 = near end-to-end overlap
- 5 = architecture substantially subsumes D-System

Scores are triage tools, not conclusions.

---

## 10. Agent workflow

### Pass 1 — Broad map
Goal: 75-150 candidate sources across all domains.

Output:
- candidate ledger,
- terminology map,
- top 20 collision candidates.

### Pass 2 — Deep reading
Deep-read the top collision candidates and foundational works.

Output:
- completed evidence matrix,
- conceptual dependency map,
- overlap notes.

### Pass 3 — Adversarial novelty test
For each hypothesis H1-H6:
- identify strongest prior-art candidate,
- articulate the best argument that D-System is not distinct,
- determine whether the hypothesis survives,
- identify what would need to change to become distinct.

### Pass 4 — Synthesis
Produce:
- prior-art taxonomy,
- architecture comparison,
- novelty assessment,
- revised D-System model,
- unanswered questions,
- recommended experiments.

---

## 11. Reproducibility requirements

Every search agent must log:

- query text,
- search provider/database,
- date,
- result identifiers,
- source-selection rationale,
- duplicate handling,
- exclusion reason.

Every factual comparison must be traceable to a source.

Do not rely on generated summaries without checking primary material.

---

## 12. Stop conditions

The initial literature review may stop when:

1. Every research domain has been searched with at least several terminology variants.
2. Citation chaining has been performed on the strongest collision candidates.
3. Each H1-H6 has at least one serious prior-art challenger.
4. New searches produce mostly duplicates or low-value adjacency.
5. The strongest 20-30 sources have been deeply compared.

This is the point for a first research memo, not a final novelty claim.

---

## 13. Expected final deliverable

The literature review should answer:

1. Which D-System components are established prior art?
2. Which are adaptations of known ideas?
3. Which combinations appear uncommon?
4. Which mechanisms may be technically distinct?
5. What terminology should D-System adopt from existing fields?
6. What should D-System avoid reinventing?
7. What formal research questions remain?
8. What experiments could demonstrate practical value?
9. Is there enough distinction to justify a paper, prototype, or both?
