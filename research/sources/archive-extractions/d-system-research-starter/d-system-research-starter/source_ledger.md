# Initial Source Ledger

This is a seed list, not a completed literature review. Dates and publication status should be verified during the formal review.

## 1. W3C PROV-O

**Title:** PROV-O: The PROV Ontology  
**Organization:** W3C  
**URL:** https://www.w3.org/TR/prov-o/

### Relevance
Foundational provenance model built around `Entity`, `Activity`, and `Agent`. It supports responsibility/association, derivation, generation, usage, roles, plans, and delegation.

### D-System collision
Very strong prior art for:
- state/entity lineage,
- transformation activity,
- actor provenance,
- role,
- delegation/authority relationships.

### Likely difference
D-System's candidate contribution would need to be above this layer: typed epistemic/lifecycle state transitions, conflict/convergence semantics, and retrieval behavior.

---

## 2. Event Sourcing Pattern

**Title:** Event Sourcing Pattern  
**Publisher:** Microsoft Azure Architecture Center  
**URL:** https://learn.microsoft.com/azure/architecture/patterns/event-sourcing

### Relevance
Defines append-only event storage in which events represent logical state changes and can serve as the authoritative history/system of record.

### D-System collision
Strong prior art for:
- append-only transitions,
- reconstructable history,
- current state as a projection of prior events.

### Likely difference
Event sourcing is a software architecture pattern, not by itself an epistemic knowledge model.

---

## 3. Provenance-Enhanced Statements in Knowledge Graphs

**Authors:** Fabio Vitali, Valentina Pasqual  
**Year:** 2026  
**Venue/status:** arXiv preprint  
**URL:** https://arxiv.org/abs/2606.15246

### Relevance
DEC interprets provenance predicates as epistemic stance and models agent-relative claims, cognitive worlds, factual commitment, disagreement, and controlled factualisation.

### D-System collision
Critical candidate for:
- provenance + epistemic semantics,
- different agents holding conflicting positions,
- disagreement without collapsing the base graph into inconsistency.

### Research priority
**CRITICAL_COLLISION**

---

## 4. Context Objects: A Temporal, Provenance-Aware Memory Primitive for Enterprise AI Agents

**Author:** Madhu Chamarty  
**Year:** 2026  
**Status:** SSRN working paper  
**URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6775102

### Relevance
Proposes a memory primitive where temporal validity, epistemic confidence, provenance lineage, organizational weight, and agent-use feedback are first-class retrieval properties.

### D-System collision
Critical candidate for:
- temporal validity,
- provenance,
- organizational/authority weight,
- epistemic confidence,
- agent retrieval.

### Research priority
**CRITICAL_COLLISION**

---

## 5. ENGRAM

**Title:** ENGRAM — Epistemic Node Graph for Retraction, Arbitration, and Memory  
**Year:** 2026  
**Type:** Open-source / technical system  
**URL:** https://engram-agents.org/

### Relevance
Describes a provenance-tracked knowledge graph for agents where claims and derivations accumulate, survive resets, and remain auditable, with explicit emphasis on retraction/arbitration/memory.

### D-System collision
Potentially strong overlap with:
- epistemic nodes,
- derivation lineage,
- arbitration,
- persistent agent memory.

### Research priority
**CRITICAL_COLLISION — inspect implementation and formal semantics**

---

## 6. The Loom

**Repository:** jpwinans/the-loom  
**Type:** Open-source system  
**URL:** https://github.com/jpwinans/the-loom

### Relevance
Event-sourced, bi-temporal, provenance-tracked knowledge graph for AI-agent memory. Every mutation is append-only; graph state can be queried historically. Facts carry evidence/confidence/basis and downstream beliefs may weaken when source confidence weakens.

### D-System collision
Critical candidate for:
- append-only KG memory,
- bi-temporality,
- evidence/confidence,
- provenance,
- causal/reasoning chains,
- propagation of source weakness.

### Research priority
**CRITICAL_COLLISION**

---

## 7. Micropublications

**Title:** Micropublications: a semantic model for claims, evidence, arguments and annotations in biomedical communications  
**Authors:** Tim Clark, Paolo N. Ciccarese, Carole A. Goble  
**Year:** 2014 (article; earlier preprint 2013)  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/

### Relevance
Models scientific claims, evidence, methods, attribution, support, challenge, disagreement, and defeasible evolution of accepted claims.

### D-System collision
Strong prior art for:
- claims + evidence,
- attribution,
- challenge/support graphs,
- defeasible reasoning,
- community reassessment over time,
- authority as one component of support.

### Research priority
**FOUNDATIONAL / CRITICAL**

---

## 8. Nanopublications

**Resource:** Nanopublication Guidelines  
**URL:** https://nanopub.net/guidelines/working_draft/

### Relevance
Separates assertion, assertion provenance, and publication information. Provenance may include derivation, actor, time, location, and generation method.

### D-System collision
Strong prior art for structured:
- assertion,
- provenance,
- attribution,
- derivation.

### Likely difference
Nanopublications do not by themselves appear to provide D-System's lifecycle/transition/convergence architecture.

---

## 9. Transparent, Traceable, Deterministic: Agentic Memory via Knowledge Graphs

**Authors:** Anna Lisa Gentile, Sungeun An, Chad Deluca  
**Organization:** IBM Research  
**Status:** Listed by IBM Research for ISWC 2026; current page should be checked for final publication timing/status  
**URL:** https://research.ibm.com/publications/transparent-traceable-deterministic-agentic-memory-via-knowledge-graphs

### Relevance
Explores knowledge graphs for conversational memory with structured updating, provenance tracing, and trustworthy/deterministic response generation.

### D-System collision
Relevant to:
- agent memory,
- graph-based consolidation,
- provenance,
- traceable retrieval/inference.

### Note
As of the initial seed search, the IBM page listed an ISWC 2026 publication date later than the repository-creation date. Treat as forthcoming until verified.
