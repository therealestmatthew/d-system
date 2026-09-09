# CLAUDE.md — D-System Adversarial Literature Review

## Mission

Conduct an adversarial literature review of D-System after the codebase review has established what the system actually implements and what conceptual claims it makes.

The objective is not to prove novelty.

The objective is to determine:

1. which D-System components are established prior art,
2. which terminology should be replaced with established terminology,
3. which mechanisms are known but recombined,
4. which integrations are uncommon,
5. which proposed mechanisms appear genuinely underexplored,
6. which claims are falsified by prior work,
7. what should be inherited rather than reinvented,
8. and what research questions remain after the strongest prior art is considered.

The default null hypothesis is:

> **H0: D-System is primarily a recombination of known ideas.**

Try to support H0.

Only retain distinctiveness claims that survive serious attempts to falsify them.

---

# 1. Inputs

Before searching, read all available D-System research artifacts, including where present:

- architecture.md
- novelty_hypotheses.md
- literature_review_protocol.md
- source_ledger.md
- knowledge_glossary.md
- terminology_investigation.md
- two_system_architecture.md
- implementation_glossary.md
- development_traceability_model.md
- phase_context_contract.md
- research_expansion.md
- research_agent_addendum.md
- adversarial codebase review outputs
- complete cited-source seed ledger

Treat the **adversarial codebase review** as especially important.

The literature review must compare prior art against both:

1. the conceptual architecture,
2. the architecture actually encoded in the codebase.

---

# 2. Do not mutate the thesis during search

During evidence collection:

- do not rewrite D-System to avoid collisions,
- do not rename a concept merely because prior art uses the same mechanism,
- do not quietly narrow a hypothesis to preserve novelty,
- do not treat terminology differences as mechanism differences.

Record collisions first.

Revise architecture only in the later synthesis phase.

---

# 3. Working architecture to challenge

D-System currently explores two coupled systems.

## A. Knowledge Construction & Management

Potential primitives/concepts include:

- information,
- idea,
- state,
- claim,
- belief,
- observation,
- evidence,
- inference,
- conclusion,
- decision,
- directive,
- provenance,
- memory,
- experience,
- context,
- actor,
- authority,
- reliability,
- conflict,
- convergence,
- history,
- transition.

Candidate state abstraction:

```text
S = (O, E, L, Content, TemporalScope, Metadata)
```

where:

- `O` = ontological classification,
- `E` = epistemic classification,
- `L` = lifecycle classification.

Candidate transition abstraction:

```text
S_t --[T, P]--> S_t+1
```

where:

- `T` = typed transition,
- `P` = provenance.

## B. Implementation & Experience

Potential primitives/concepts include:

- requirement,
- constraint,
- acceptance criterion,
- specification,
- design,
- plan,
- phase,
- task,
- development session,
- context package,
- artifact,
- implementation,
- functionality,
- verification,
- test,
- deployment,
- telemetry,
- outcome,
- feedback.

Candidate full lifecycle:

```text
Idea
 -> Reasoning
 -> Decision
 -> Requirement
 -> Specification
 -> Plan
 -> Phase
 -> Implementation
 -> Verification
 -> Deployment
 -> Runtime Observation
 -> Experience
 -> Revised Knowledge
```

Do not assume this lifecycle is new.

---

# 4. Existing hypotheses to attack

## H1 — Multi-dimensional state model

Orthogonal ontological + epistemic + lifecycle classifications for knowledge states may be uncommon in agent-memory systems.

### Falsify by finding:
A materially equivalent established framework.

---

## H2 — Typed transition semantics as reasoning memory

Explicit typed transitions between append-only knowledge states preserve reasoning history separately from semantic relationships.

### Falsify by finding:
Equivalent state-transition reasoning memory or provenance architecture.

---

## H3 — Provenance as conflict-resolution input

Transition provenance includes actor identity, domain authority, evidence, method, lineage, and delegation and influences conflict resolution.

### Falsify by finding:
Equivalent provenance-aware arbitration/trust systems.

---

## H4 — Independence-aware convergence

Independent reasoning/evidence paths arriving at equivalent states strengthen epistemic weight while derivative agreement is discounted.

### Falsify by finding:
Equivalent provenance/topology-aware corroboration over mixed human-agent knowledge.

---

## H5 — Topology-aware context transfer

Context selection includes current state, reasoning lineage, supporting evidence, dissent, authority, convergence, and unresolved uncertainty.

### Falsify by finding:
Equivalent agent-memory retrieval architecture.

---

## H6 — Integrated human-agent collective knowledge evolution

The full synthesis may be distinct even if primitives are known.

### Falsify by finding:
An existing framework that substantially subsumes D-System end-to-end.

---

## H7 — Development provenance

Software functionality can be represented as downstream result of an append-only lineage connecting ideas, evidence, decisions, requirements, specifications, plans, execution phases, artifacts, verification, and runtime outcomes.

### Falsify by finding:
An established framework with materially equivalent end-to-end provenance.

---

## H8 — Phase-bounded context construction

A planned development phase can serve as an explicit context boundary for agentic software engineering.

### Falsify by finding:
Equivalent task/session/context lifecycle in agentic development systems.

---

## H9 — Bidirectional epistemic traceability

The system supports:

- idea/knowledge -> realized functionality/outcome,
- functionality/artifact -> reasoning/evidence/assumptions/decisions.

### Falsify by finding:
Equivalent bidirectional reasoning-to-runtime traceability.

---

## H10 — Epistemic blast-radius analysis

Changing/falsifying an assumption, evidence source, or claim identifies downstream decisions, requirements, plans, artifacts, tests, and functionality that require reassessment.

### Falsify by finding:
Established impact-analysis systems performing materially equivalent epistemic dependency propagation.

---

## H11 — Runtime-to-knowledge closure

Runtime telemetry, tests, incidents, and outcomes become provenance-bearing evidence updating the same knowledge structure that generated implementation intent.

### Falsify by finding:
Equivalent closed-loop knowledge -> implementation -> runtime evidence -> knowledge architecture.

---

# 5. Search domains

Search broadly across:

1. Knowledge graphs
2. Semantic Web
3. W3C PROV / provenance
4. Temporal knowledge graphs
5. Bi-temporal systems
6. Event sourcing
7. Belief revision / AGM
8. Truth-maintenance systems
9. Epistemic logic
10. Doxastic logic
11. Defeasible reasoning
12. Computational argumentation
13. Truth discovery
14. Data fusion
15. Subjective logic
16. Trust and reputation systems
17. Multi-agent belief systems
18. Scientific discourse representation
19. Nanopublications
20. Micropublications
21. Agent memory
22. Long-term memory for LLM agents
23. Episodic memory
24. RAG / Graph-RAG
25. Human-AI collective intelligence
26. Decision provenance
27. Decision intelligence
28. Data lineage
29. Evidence graphs
30. Temporal databases
31. Event calculus
32. Ontology evolution
33. Requirements engineering
34. Requirements traceability
35. Requirements provenance
36. Requirements evolution
37. Design rationale
38. Architecture rationale
39. Architecture knowledge management
40. Architecture Decision Records
41. IBIS
42. QOC
43. Software traceability
44. Trace-link recovery
45. Change impact analysis
46. Model-based systems engineering
47. Digital thread
48. Digital engineering
49. Specification-driven development
50. Executable specifications
51. Formal specification
52. Behavior-driven development
53. Software provenance
54. Build provenance
55. Artifact lineage
56. Agentic software engineering
57. Coding-agent memory
58. Cross-session coding agents
59. Agent handoff
60. Agent checkpointing
61. Hierarchical task networks
62. AI planning
63. Execution monitoring
64. Verification and validation
65. Runtime verification
66. Requirements monitoring
67. Observability-driven development
68. Self-adaptive systems
69. MAPE-K
70. Autonomic computing
71. Continuous requirements engineering
72. DevOps traceability

Do not stop at the terminology used by D-System.

---

# 6. Vocabulary translation requirement

Before concluding that a concept is uncommon, search for established synonyms.

Examples:

```text
D-System                     Search alternatives

Phase                        episode, work package, task boundary,
                             execution unit, checkpoint, planning step

Epistemic blast radius       change impact, rationale impact,
                             assumption dependency, impact propagation

Knowledge-to-code lineage    traceability, digital thread,
                             architecture rationale, artifact provenance

Context package              execution context, task context,
                             working set, session state, agent memory

Convergence                  corroboration, source fusion,
                             consensus, independent evidence

Transition provenance        derivation history, process provenance,
                             decision provenance, activity provenance

Runtime-to-knowledge loop    runtime verification, feedback control,
                             requirements monitoring, MAPE-K
```

Terminology novelty is not mechanism novelty.

---

# 7. Search strategy

## Phase A — Vocabulary discovery

Find:

- surveys,
- standards,
- canonical models,
- major taxonomies,
- historically important papers,
- terminology used by each field.

Build a terminology map before deep comparison.

---

## Phase B — Backward citation chaining

For strong candidate sources:

- inspect references,
- identify theoretical ancestors,
- identify earlier equivalent mechanisms.

Do not credit a recent paper with inventing a mechanism if it is inherited.

---

## Phase C — Forward citation chaining

Find:

- extensions,
- critiques,
- replications,
- implementations,
- newer systems using the same mechanism.

---

## Phase D — System search

Search:

- arXiv,
- Semantic Scholar,
- OpenAlex,
- Crossref,
- ACM,
- IEEE,
- Springer,
- Elsevier,
- W3C,
- GitHub,
- university labs,
- industrial research,
- patents where useful.

Blogs and product pages are leads, not sufficient evidence for research claims.

---

## Phase E — Collision search

Construct queries specifically intended to find systems that already do what D-System claims.

Examples:

```text
"provenance" "independent sources" knowledge graph confidence
"source dependence" truth discovery graph
"architecture rationale" requirements code traceability
"decision provenance" software architecture knowledge graph
"assumption" impact analysis requirements code
"agent memory" coding "session" persistent
"runtime verification" requirements feedback knowledge
"digital thread" requirements design code test runtime
```

---

# 8. Source priority

Prefer:

1. standards,
2. peer-reviewed papers,
3. major conference papers,
4. university/industrial research,
5. high-quality preprints,
6. mature open-source systems,
7. technical reports,
8. blogs/product pages only as discovery leads.

Do not use generated summaries as evidence.

---

# 9. Evidence extraction

For every relevant source, record:

- full citation,
- canonical URL/DOI,
- source type,
- research domain,
- problem addressed,
- state model,
- transition model,
- provenance model,
- actor model,
- temporal model,
- conflict/trust mechanism,
- convergence/independence mechanism,
- memory model,
- retrieval/context model,
- decision representation,
- requirement derivation,
- specification representation,
- planning model,
- execution-unit/session model,
- artifact/code linkage,
- test/verification linkage,
- deployment linkage,
- runtime observation linkage,
- feedback-to-knowledge mechanism,
- forward traceability,
- backward traceability,
- change-impact mechanism,
- implementation availability,
- evaluation method,
- strongest D-System overlap,
- strongest difference,
- hypotheses challenged,
- evidence locator,
- interpretation confidence.

---

# 10. Similarity scoring

## Component overlap

Score 0–5:

- 0 = unrelated
- 1 = adjacent
- 2 = one relevant primitive
- 3 = multiple relevant primitives
- 4 = strong mechanism overlap
- 5 = materially equivalent mechanism

## Architecture overlap

Score 0–5:

- 0 = unrelated
- 1 = broad objective only
- 2 = partial architecture
- 3 = substantial subsystem overlap
- 4 = near end-to-end overlap
- 5 = materially subsumes D-System

Scores are triage aids, not conclusions.

---

# 11. Critical collision rules

Flag a source as `CRITICAL_COLLISION` if:

- component overlap >= 4,
- architecture overlap >= 4,
- it directly falsifies H1-H11,
- or it spans at least four adjacent stages in:

```text
Reasoning
 -> Decision
 -> Requirement
 -> Specification
 -> Plan
 -> Execution
 -> Artifact
 -> Verification
 -> Deployment
 -> Runtime Evidence
 -> Knowledge Update
```

Every critical collision should receive a second independent review.

---

# 12. Independence requirement

Do not treat multiple derivative sources as independent confirmation of novelty or prior art.

Track shared ancestry.

If five papers inherit the same mechanism from one foundational paper, record:

```text
1 primary mechanism lineage
+ 4 derivative applications
```

not five independent inventions.

This same rule applies when evaluating D-System's convergence hypothesis.

---

# 13. Negative evidence discipline

Do not write:

> "No prior work exists."

unless a rigorous search justifies it.

Prefer:

- `LIKELY_ALREADY_KNOWN`
- `KNOWN_COMPONENT_NEW_INTEGRATION`
- `POTENTIALLY_DISTINCT`
- `INSUFFICIENT_EVIDENCE`

Avoid `NOVEL` unless supported by substantially stronger review and expert scrutiny.

---

# 14. Required adversarial arguments

Before writing any distinctiveness claim, formulate the strongest case that D-System is simply:

```text
Knowledge Graph
+ PROV-O
+ Event Sourcing
+ Belief Revision
+ Argumentation
+ Truth Discovery
+ Agent Memory
+ Design Rationale
+ Requirements Traceability
+ ADRs
+ Digital Thread
+ Software Provenance
+ Observability
+ MAPE-K
```

Then identify exactly what remains after that decomposition.

If nothing remains, say so.

That is a successful research result.

---

# 15. Required deliverables

Create:

```text
research/literature-review/
```

and produce:

## `01_terminology_map.md`

Map D-System terms to established terminology.

## `02_domain_map.md`

Summarize each research tradition and its relevance.

## `03_source_inventory.csv`

Broad candidate inventory.

## `04_evidence_matrix.csv`

Deep structured comparisons.

## `05_critical_collisions.md`

Detailed analysis of strongest prior-art matches.

## `06_hypothesis_tests.md`

For H1-H11:

```yaml
hypothesis:
strongest_challenger:
evidence:
assessment:
status:
```

Allowed statuses:

- `LIKELY_ALREADY_KNOWN`
- `KNOWN_COMPONENT_NEW_INTEGRATION`
- `POTENTIALLY_DISTINCT`
- `INSUFFICIENT_EVIDENCE`

## `07_anti_novelty_case.md`

Make the strongest coherent argument that D-System does not require any new mechanism.

## `08_surviving_distinctions.md`

Only after the anti-novelty case, list mechanisms/integrations that remain potentially distinctive.

## `09_reuse_recommendations.md`

Identify standards, ontologies, models, and implementations D-System should inherit rather than recreate.

## `10_architecture_implications.md`

Explain what the literature implies for the conceptual architecture and existing implementation.

## `11_open_research_questions.md`

Questions not resolved by prior art.

## `12_experiment_proposals.md`

Experiments capable of distinguishing D-System mechanisms from simpler baselines.

## `13_validated_bibliography.md`

A validated bibliography separate from the original conversational seed ledger.

---

# 16. Seed-source handling

The repository may contain a source ledger assembled during ideation.

Treat it as:

```text
SEED SOURCES ENCOUNTERED
```

not:

```text
VALIDATED BIBLIOGRAPHY
```

For each seed source:

1. verify bibliographic identity,
2. inspect the primary source,
3. confirm the cited interpretation,
4. record exact supporting location,
5. update status.

Never silently alter the historical seed ledger.

---

# 17. Reproducibility

Log:

- query,
- database/provider,
- date searched,
- filters,
- result IDs,
- inclusion rationale,
- exclusion rationale,
- duplicate handling,
- citation-chain decisions.

Every major synthesis claim should be traceable to primary evidence.

---

# 18. Stop conditions

The first formal review can stop when:

- all major domains have been searched with terminology variants,
- strongest collisions have backward and forward citation chaining,
- H1-H11 each have at least one serious challenger,
- strongest 20–30 sources have been deeply compared,
- additional searches mostly yield duplicates or clearly adjacent work,
- critical collisions have received second review.

This produces a first research memo.

It does not establish final novelty.

---

# 19. Final synthesis principle

The review should answer three separate questions:

### What is already known?

Identify established theory, standards, and mechanisms.

### What is a new integration, if anything?

Identify combinations that are uncommon but composed of known parts.

### What may require new mechanism design?

Identify only the capabilities not adequately explained by existing work.

Do not collapse these categories.

The goal is not to make D-System sound original.

The goal is to find the most defensible description of what it actually is.
