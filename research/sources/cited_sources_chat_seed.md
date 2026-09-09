# D-System — Complete Source Ledger Cited in This Conversation

**Purpose:** Consolidated, deduplicated inventory of external sources cited or explicitly relied upon in the D-System discussion so far.

**Scope note:** This ledger includes the research/technical sources cited during the D-System architecture discussion, the later ideation-to-implementation discussion, naming-collision checks, and the earlier career-fit comparison that formed part of this conversation context. Repeated citations are listed once.

**Verification note:** URLs were rechecked on 2026-09-09 where practical. Some publisher pages block automated retrieval, but their cited URLs are preserved exactly. Inclusion here means the source was cited in the conversation; it does **not** mean its claims have yet passed the formal D-System literature review.

---

## A. Provenance, knowledge graphs, epistemic representation, and temporal history

### 1. W3C PROV-O

**Title:** PROV-O: The PROV Ontology  
**Organization:** World Wide Web Consortium (W3C)  
**Published:** 2013-04-30  
**URL:** https://www.w3.org/TR/prov-o/

**Why it was cited:** Foundational provenance ontology defining concepts including Entity, Activity, Agent, derivation, association, generation, usage, roles, and delegation. Used as an important ancestor/collision for D-System's state-transition-provenance model.

---

### 2. Event Sourcing Pattern

**Title:** Event Sourcing Pattern  
**Publisher:** Microsoft Azure Architecture Center  
**URL:** https://learn.microsoft.com/azure/architecture/patterns/event-sourcing

**Why it was cited:** Established software architecture pattern for retaining append-only state-changing events and reconstructing current/prior state from event history.

---

### 3. Provenance-Enhanced Statements in Knowledge Graphs

**Title:** Provenance-Enhanced Statements in Knowledge Graphs  
**Authors:** Fabio Vitali, Valentina Pasqual  
**Year:** 2026  
**Type:** arXiv preprint  
**URL:** https://arxiv.org/abs/2606.15246

**Why it was cited:** Strong collision for epistemic interpretation of provenance, agent-relative statements, disagreement, and transitions toward accepted/factualized states without simply deleting prior epistemic positions.

---

### 4. Context Objects: A Temporal, Provenance-Aware Memory Primitive for Enterprise AI Agents

**Title:** Context Objects: A Temporal, Provenance-Aware Memory Primitive for Enterprise AI Agents  
**Author:** Madhu Chamarty  
**Year:** 2026  
**Type:** SSRN working paper/preprint  
**URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6775102

**Why it was cited:** Strong collision around temporal validity, provenance lineage, epistemic confidence, organizational weight, and retrieval for agent memory.

---

### 5. ENGRAM

**Title / Project:** ENGRAM — Epistemic Node Graph for Retraction, Arbitration, and Memory  
**Type:** Technical/open-source agent-memory system  
**URL:** https://engram-agents.org/

**Why it was cited:** Strong overlap with provenance-tracked agent memory, derivational claims, arbitration, retraction, and persistent auditable reasoning.

---

### 6. The Loom

**Project:** The Loom  
**Repository:** jpwinans/the-loom  
**Type:** Open-source knowledge-graph memory/reasoning engine  
**URL:** https://github.com/jpwinans/the-loom

**Why it was cited:** Event-sourced, bi-temporal, provenance-tracked KG for AI-agent memory with evidence/confidence and historical reconstruction.

---

### 7. Transparent, Traceable, Deterministic: Agentic Memory via Knowledge Graphs

**Title:** Transparent, Traceable, Deterministic: Agentic Memory via Knowledge Graphs  
**Authors listed by IBM:** Anna Lisa Gentile, Sungeun An, Chad Deluca  
**Organization:** IBM Research  
**Status when cited:** Listed for ISWC 2026; publication timing/status should be verified during formal review  
**URL:** https://research.ibm.com/publications/transparent-traceable-deterministic-agentic-memory-via-knowledge-graphs

**Why it was cited:** Knowledge-graph-based agent memory emphasizing structured updating, provenance, traceability, and deterministic/transparent retrieval and response generation.

---

### 8. Full Traceability and Provenance for Knowledge Graphs

**Title:** Full Traceability and Provenance for Knowledge Graphs  
**Author:** Henrik Dibowski  
**Published online:** 2024-12-13  
**Venue:** Formal Ontology in Information Systems (FOIS 2024) proceedings  
**DOI:** 10.3233/FAIA241309  
**URL:** https://journals.sagepub.com/doi/10.3233/FAIA241309

**Why it was cited:** Prior art for retaining fine-grained KG change deltas, detailed provenance, complete historical reconstruction, and restoration of prior KG states.

---

### 9. IEEE source on Truth Discovery

**IEEE document identifier:** 10587116  
**Publisher:** IEEE Xplore  
**URL:** https://ieeexplore.ieee.org/document/10587116

**Why it was cited:** Used when discussing truth-discovery methods for reconciling conflicting claims, estimating source reliability, and handling dependent/independent sources.

**Formal-review action:** Recover the complete title, authors, venue, DOI, and exact mechanism before using this as evidence in any paper.

---

### 10. Subjective Logic / Multi-source Belief Fusion Source

**ScienceDirect PII:** S1566253515000202  
**Publisher:** Elsevier / ScienceDirect  
**URL:** https://www.sciencedirect.com/science/article/abs/pii/S1566253515000202

**Why it was cited:** Used as an example of formal multi-source belief fusion / trust reasoning related to D-System's proposed actor reliability and evidence aggregation.

**Formal-review action:** Recover and verify the complete bibliographic record and ensure the paper actually supports the specific use made of it.

---

## B. Scientific claims, evidence, provenance, and argumentation

### 11. Nanopublications

**Resource:** Nanopublications  
**URL:** https://nanopub.net/

**Why it was cited:** Nanopublications separate assertions from assertion provenance and publication information, providing established structured provenance for scientific claims.

---

### 12. Nanopublication Guidelines — Working Draft

**Resource:** Nanopublication Guidelines  
**URL:** https://nanopub.net/guidelines/working_draft/

**Why it appears in the D-System materials:** Included in the initial source ledger generated during this conversation as the more specific guidance resource for assertion/provenance/publication-information modeling.

---

### 13. Provenance-driven nanopublications: representing source lineage and trust networks for multi-source assertions

**Title:** Provenance-driven nanopublications: representing source lineage and trust networks for multi-source assertions  
**Authors shown by publisher:** Laura Menotti, Stefano Marchesin, Fabio Giachelle, et al.; Gianmaria Silvello  
**Published:** 2025-10-24  
**Journal:** International Journal on Digital Libraries  
**DOI:** 10.1007/s00799-025-00431-x  
**URL:** https://link.springer.com/article/10.1007/s00799-025-00431-x

**Why it was cited:** Multi-source assertions, provenance/source lineage, trust networks, support/refutation, and LLM-assisted evaluation of assertions.

---

### 14. Micropublications

**Title:** Micropublications: a semantic model for claims, evidence, arguments and annotations in biomedical communications  
**Authors:** Tim Clark, Paolo N. Ciccarese, Carole A. Goble  
**Published:** 2014  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/

**Why it was cited:** Mature prior art for claims, evidence, methods, support, challenge, disagreement, attribution, and defeasible evolution of scientific belief.

---

### 15. The Semantic Units Framework

**Title:** The Semantic Units Framework, a technology-agnostic representational approach to FAIR and CLEAR knowledge infrastructures  
**Journal:** Scientific Data  
**Year:** 2026  
**URL:** https://www.nature.com/articles/s41597-026-07588-3

**Why it was cited:** Used in discussing explicit representation of epistemic distinctions, statements held by different agents, and disagreements without collapsing every represented proposition into an asserted global truth.

---

## C. Requirements, design rationale, traceability, and software evolution

### 16. NASA SWE-059

**Title:** SWE-059 — Bidirectional Traceability Between Software Requirements and Software Design  
**Organization:** NASA Software Engineering Handbook  
**URL:** https://swehb.nasa.gov/spaces/7150/pages/16449675/SWE-059%2B-%2BBidirectional%2BTraceability%2BBetween%2BSoftware%2BRequirements%2Band%2BSoftware%2BDesign

**Why it was cited:** Established bidirectional traceability between requirements and design, including downstream impact analysis across design, documentation, source code, and tests.

---

### 17. AREL / Architecture Rationale and Traceability Paper

**ScienceDirect PII:** S0164121206002287  
**Publisher:** Elsevier / ScienceDirect  
**URL:** https://www.sciencedirect.com/science/article/pii/S0164121206002287

**Why it was cited:** Architecture rationale representation with forward change-impact tracing and backward root-cause/rationale tracing; a major collision for D-System's rationale-to-implementation lineage.

**Formal-review action:** Recover and verify full title, authors, year, venue, DOI, and exact AREL semantics from the primary paper.

---

### 18. Architecture Decision Record

**Title:** Architecture Decision Record  
**Author / site:** Martin Fowler  
**URL:** https://martinfowler.com/bliki/ArchitectureDecisionRecord.html

**Why it was cited:** ADR practices preserve architectural decisions, context and consequences, including supersession rather than silently rewriting prior decisions.

---

## D. Agent memory and agentic software engineering

### 19. CTIM-Rover

**Title:** From Knowledge to Noise: CTIM-Rover and the Pitfalls of Episodic Memory in Software Engineering Agents  
**Venue:** ACL Anthology / REALM 2025  
**URL:** https://aclanthology.org/2025.realm-1.30/

**Why it was cited:** Research into cross-task episodic memory for software-engineering agents, including the important negative result that retained memory can become noise rather than automatically improving agent performance.

---

### 20. Continuum — GitHub implementation

**Repository:** AnasNafees1802/continuum  
**Type:** Open-source implementation  
**URL:** https://github.com/AnasNafees1802/continuum

**Why it was cited:** Example of preserving project/session state, decisions, open threads, and handoff information for coding-agent continuity across sessions.

---

## E. Naming-collision sources

These were cited not as theoretical prior art, but to show that candidate names were already in use.

### 21. ContextForge

**Site:** ContextForge Memory  
**URL:** https://contextforge.dev/

**Why it was cited:** Existing persistent-memory product for coding assistants/agents; cited to reject `ContextForge` as a D-System name.

---

### 22. Continuum

**Site:** Continuum — verifiable memory for AI coding assistants  
**URL:** https://www.continuum.rest/

**Why it was cited:** Existing AI coding-assistant memory project; cited as evidence that `Continuum` is already heavily occupied as a product/project name.

---

### 23. TraceWeave

**Repository:** nripankadas07/traceweave  
**Type:** Open-source agent-trajectory forensics project  
**URL:** https://github.com/nripankadas07/traceweave

**Why it was cited:** Existing project using the `TraceWeave` name; cited to reject that candidate name.

---

## F. Career-context sources cited earlier in this conversation

These are not D-System prior art, but they were cited in the broader conversation when assessing whether the work could support a frontier-lab research/engineering trajectory. They are included for completeness.

### 24. OpenAI — Research Scientist

**Title:** Research Scientist  
**Organization:** OpenAI  
**URL:** https://openai.com/careers/research-scientist-san-francisco/

**Why it was cited:** Current role requirements were used to distinguish an interesting architecture idea from the research record normally expected for a Research Scientist role.

---

### 25. OpenAI — Research Engineer / Research Scientist / AI Systems Engineer, RSI

**Title:** Research Engineer / Research Scientist / AI Systems Engineer, RSI  
**Organization:** OpenAI  
**URL:** https://openai.com/careers/research-engineer-research-scientist-ai-systems-engineer-rsi-san-francisco/

**Why it was cited:** The Recursive Self-Improvement team's work on automating research workflows, evaluation, long-horizon experiments, and feedback loops was identified as unusually aligned with the user's D-System/agentic-systems interests.

---

### 26. Anthropic Careers

**Resource:** Anthropic Careers  
**Organization:** Anthropic  
**URL:** https://www.anthropic.com/careers

**Why it was cited:** Used to identify then-current Research Engineer / Research Scientist and knowledge/alignment-related roles relevant to the user's research/engineering trajectory.

---

# Completeness checklist

Unique sources captured in this ledger: **26**

Categories:

- Provenance / KG / epistemic / temporal: 10
- Scientific claims / evidence / argumentation: 5
- Requirements / design rationale / traceability: 3
- Agent memory / software engineering: 2
- Naming collision checks: 3
- Career-context sources: 3

## Known verification gaps before formal literature review

The following should be bibliographically resolved before being used in a formal research memo:

1. IEEE Xplore document `10587116` — recover exact title/authors/DOI and verify source-dependence claims.
2. ScienceDirect `S1566253515000202` — recover full bibliographic identity and verify the exact subjective-logic/belief-fusion claim.
3. ScienceDirect `S0164121206002287` — recover full bibliographic identity and verify the AREL/design-rationale interpretation.
4. SSRN `6775102` — verify current version/status and whether a later peer-reviewed version exists.
5. ENGRAM — inspect repository/specification and distinguish project claims from implemented behavior.
6. IBM ISWC 2026 paper — verify final publication status and proceedings record.
7. Any naming source — re-check availability/trademark/package/domain status if naming decisions are made later.

---

# Recommended repository placement

```text
research/
  sources/
    cited_sources_chat_seed.md   <- this file
```

During the formal review, do **not** overwrite this seed inventory. Create a separate validated bibliography so the project preserves the distinction between:

```text
sources we encountered/cited during ideation
                vs.
sources independently validated during formal review
```

That separation is itself consistent with D-System's provenance philosophy.
