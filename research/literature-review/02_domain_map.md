# Domain Map — Literature Review Pass 1

One entry per search domain (D01–D72, methodology §5), assembled from `03_source_inventory.csv`
and the corresponding sections of `01_terminology_map.md`. No new searching happens here — this
is a synthesis-of-record pass over what Pass 1 (`phase-lit-01` D01–D20+D28–D32, `phase-lit-02`
D21–D27+D33–D45, `phase-lit-03` D46–D72) already found.

Each entry gives: the tradition the domain covers (methodology §5/domain-matrix framing), its
top three canonical sources from the inventory by combined pre-score (fewer if the domain has
fewer rows), and which of H1–H11 the domain's own terminology-map section shows it bearing on.
Five domains (D41, D44, D67, D70, D72) carry no inline H-tag in their terminology-map prose;
for those, hypothesis relevance is inferred from the domain matrix's own framing and the rows'
content and flagged as such, not left blank and not silently tagged as if Pass 1 had marked it.

No verdict language is used below — a domain "bears on" a hypothesis in the sense that its
sources are relevant evidence to weigh, not that the hypothesis is confirmed or falsified.
Adjudication is `phase-lit-04` onward's task.

### D01 — Knowledge graphs

**Tradition.** Knowledge graph, ontology, RDF graph, property graph, knowledge base construction, entity-relation model.

**Canonical sources (inventory):**
- `simsek-angele-kg-lifecycle-2021` (4/2) — Simsek, Angele, Karle, Opdenplatz, Sommer, Umbrich, Fensel: Knowledge Graph Lifecycle: Building and Maintaining Knowledge Graphs, 2nd Worksh
- `epistemic-state-graph-2026` (4/2) — State Representation and Termination for Recursive Reasoning Systems, arXiv preprint
- `hogan-etal-kg-csur-2021` (3/2) — Hogan et al.: Knowledge Graphs, ACM Computing Surveys

**Bears on:** H1

*15 inventory rows tagged to this domain.*

### D02 — Semantic Web

**Tradition.** Semantic Web, RDF/OWL, linked data, SPARQL, named graphs, reification.

**Canonical sources (inventory):**
- `provenance-enhanced-statements-dec-2026` (5/3) — Provenance-Enhanced Statements in Knowledge Graphs (Doxastic-Epistemic-Conjectural framework), arXiv preprint
- `carroll-etal-named-graphs-provenance-trust-2005` (4/2) — Carroll, Bizer, Hayes, Stickler: Named Graphs, Provenance and Trust, WWW 2005
- `esparql-agnostic-atheistic-beliefs-2024` (4/2) — eSPARQL: Representing and Reconciling Agnostic and Atheistic Beliefs in RDF-star Knowledge Graphs, arXiv preprint

**Bears on:** H1, H3

*15 inventory rows tagged to this domain.*

### D03 — W3C PROV / provenance

**Tradition.** W3C PROV, PROV-O, provenance ontology, prov:Activity/Agent/Entity, derivation, attribution, delegation, epistemic provenance.

**Canonical sources (inventory):**
- `provenance-enhanced-statements-dec-2026` (5/3) — Provenance-Enhanced Statements in Knowledge Graphs (Doxastic-Epistemic-Conjectural framework), arXiv preprint
- `prov-agent-2025` (5/3) — PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows, arXiv preprint
- `w3c-prov-o-2013` (4/2) — PROV-O: The PROV Ontology, W3C Recommendation 30 Apr 2013

**Bears on:** H3, H7

*12 inventory rows tagged to this domain.*

### D04 — Temporal knowledge graphs

**Tradition.** Temporal knowledge graph, TKG, time-aware embedding, temporal fact, quadruple (s,p,o,t).

**Canonical sources (inventory):**
- `zep-graphiti-temporal-kg-agent-memory-2025` (4/4) — Rasmussen, Paliychuk, Beauvais, Ryan, Chalef: Zep: A Temporal Knowledge Graph Architecture for Agent Memory, arXiv preprint
- `temporal-belief-revision-kb-1994` (3/2) — A temporal approach to belief revision in knowledge bases, IEEE
- `temporal-provenance-model-2012-d04-recur` (3/2) — Temporal Provenance Model (TPM): Model and Query Language, arXiv preprint (duplicate of temporal-provenance-model-2012, D02)

**Bears on:** H1, H2, H3, H5, H6

*19 inventory rows tagged to this domain.*

### D05 — Bi-temporal systems

**Tradition.** Bi-temporal, valid time, transaction time, temporal versioning, as-of query.

**Canonical sources (inventory):**
- `tgms-agent-native-bitemporal-graph-2026` (5/4) — TGMS: An Agent-Native Bi-Temporal Graph Management System - Validated Temporal Operators and Trace-Grounded Answer Checking, arXiv preprint
- `belief-based-bitemporal-db-model-2015` (4/3) — A Belief-Based Bitemporal Database Model, Springer LNCS chapter
- `probabilistic-bitemporal-kg-2018` (4/3) — Towards Probabilistic Bitemporal Knowledge Graphs, WWW 2018 companion proceedings

**Bears on:** H1, H2, H3, H5, H6

*17 inventory rows tagged to this domain.*

### D06 — Event sourcing

**Tradition.** Event sourcing, append-only log, CQRS, event store, projection, immutable log.

**Canonical sources (inventory):**
- `log-is-the-agent-event-sourced-reactive-graphs-2026` (5/4) — The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems, arXiv preprint
- `provenance-enhanced-statements-dec-2026-d06-recur` (5/3) — Provenance-Enhanced Statements in Knowledge Graphs (Doxastic-Epistemic-Conjectural framework), arXiv preprint (duplicate of provenance-enhan
- `esaa-event-sourcing-llm-agents-2026` (4/3) — ESAA: Event Sourcing for Autonomous Agents in LLM-Based Software Engineering, arXiv preprint

**Bears on:** H1, H2, H6, H7, H8, H9

*24 inventory rows tagged to this domain.*

### D07 — Belief revision / AGM

**Tradition.** Belief revision, AGM theory, belief contraction, belief update, epistemic entrenchment, iterated revision.

**Canonical sources (inventory):**
- `graph-native-cognitive-memory-belief-revision-semantics-2026` (5/4) — Graph-Native Cognitive Memory for AI Agents: Formal Belief Revision Semantics for Versioned Memory Architectures, arXiv preprint
- `eywa-provenance-grounded-agent-memory-2026` (4/3) — Eywa: Provenance-Grounded Long-Term Memory for AI Agents, arXiv preprint
- `epica-agm-agent-runtime-oss-github` (4/2) — epica, GitHub repository (embeddable Rust runtime for formal AGM belief revision in LLM agents, MCP-native)

**Bears on:** H1, H2, H3, H5, H10

*14 inventory rows tagged to this domain.*

### D08 — Truth-maintenance systems

**Tradition.** Truth maintenance system, TMS, ATMS, JTMS, reason maintenance, dependency-directed backtracking, justification network.

**Canonical sources (inventory):**
- `datalog-materialisations-maintenance-revisited-2019` (3/2) — Maintenance of Datalog Materialisations Revisited, Artificial Intelligence
- `dekleer-assumption-based-tms-1986` (3/2) — de Kleer: An Assumption-Based TMS, Artificial Intelligence
- `doyle-truth-maintenance-system-1979` (3/2) — Doyle: A Truth Maintenance System, Artificial Intelligence

**Bears on:** H2, H3, H4, H5, H10

*16 inventory rows tagged to this domain.*

### D09 — Epistemic logic

**Tradition.** Epistemic logic, knowledge operator, S5, common knowledge, dynamic epistemic logic.

**Canonical sources (inventory):**
- `del-mobile-structured-agents-2012` (3/3) — A Dynamic-Epistemic Logic for Mobile Structured Agents, arXiv preprint
- `program-semantics-verification-kb-mas-2022` (3/3) — Program Semantics and a Verification Technique for Knowledge-Based Multi-Agent Systems, arXiv preprint
- `epistemic-model-checking-kb-program-anonymous-broadcast-2010` (4/2) — Epistemic Model Checking for Knowledge-Based Program Implementation: an Application to Anonymous Broadcast, arXiv preprint

**Bears on:** H1, H2, H5, H6, H7, H8, H9

*16 inventory rows tagged to this domain.*

### D10 — Doxastic logic

**Tradition.** Doxastic logic, belief operator, KD45, belief base, graded belief.

**Canonical sources (inventory):**
- `rethinking-epistemic-logic-belief-bases-2020` (4/3) — Rethinking Epistemic Logic with Belief Bases, Artificial Intelligence
- `uspto-11481658-bdi-multi-agent-architecture-patent` (3/3) — US Patent 11,481,658: Real-Time Multi-Agent BDI Architecture with Agent Migration and Methods Thereof
- `graded-distributed-belief-2025` (3/2) — Graded Distributed Belief, arXiv preprint

**Bears on:** H1, H3, H4

*16 inventory rows tagged to this domain.*

### D11 — Defeasible reasoning

**Tradition.** Defeasible reasoning, non-monotonic logic, default logic, defeaters, prima facie justification.

**Canonical sources (inventory):**
- `evidence-graphs-fair-computation-defeasible-reasoning-2021` (5/4) — Evidence Graphs: Supporting Transparent and FAIR Computation, with Defeasible Reasoning on Data, Methods, and Results, bioRxiv preprint (DOI
- `pollock-defeasible-reasoning-oscar-2000` (3/3) — Pollock: Defeasible Reasoning in OSCAR, arXiv preprint
- `aba-argumentation-theoretic-default-reasoning-1997` (3/2) — Bondarenko, Dung, Kowalski, Toni: An Abstract, Argumentation-Theoretic Approach to Default Reasoning, Artificial Intelligence

**Bears on:** H1, H2, H3, H7, H8

*17 inventory rows tagged to this domain.*

### D12 — Computational argumentation

**Tradition.** Argumentation framework, Dung semantics, abstract argumentation, structured argumentation, ASPIC+, argument attack/support.

**Canonical sources (inventory):**
- `evidential-higher-order-set-argumentation-framework-2026` (4/2) — Evidential-Based Higher-Order Set Argumentation Framework, arXiv preprint
- `labeled-argumentation-framework-2015` (4/2) — A labeled argumentation framework, Journal of Applied Logic
- `skiba-argumentation-frameworks-fallible-evidence-2020` (4/2) — Skiba: Abstract Argumentation Frameworks with Fallible Evidence, Frontiers in Artificial Intelligence and Applications

**Bears on:** H2, H3, H4

*17 inventory rows tagged to this domain.*

### D13 — Truth discovery

**Tradition.** Truth discovery, source reliability estimation, fact-finding algorithms, conflicting claims resolution.

**Canonical sources (inventory):**
- `grading-narrators-isnad-rijal-claim-provenance-2026` (5/3) — Grading the Narrators: An Isnad-Rijal Framework for Claim-Level Provenance in Multi-Agent Knowledge Systems, arXiv preprint
- `yin-han-yu-truth-discovery-conflicting-providers-2007` (4/2) — Yin, Han, Yu: Truth discovery with multiple conflicting information providers on the web, SIGKDD 2007
- `resolving-conflicting-evidence-automated-factchecking-2025` (4/2) — Resolving conflicting evidence in automated fact-checking, IJCAI 2025

**Bears on:** H3, H4

*11 inventory rows tagged to this domain.*

### D14 — Data fusion

**Tradition.** Data fusion, conflict resolution, source accuracy, copy detection, dependence-aware fusion.

**Canonical sources (inventory):**
- `dong-berti-equille-srivastava-data-fusion-resolving-conflicts-2009` (4/2) — Dong, Berti-Equille, Srivastava: Data fusion: resolving data conflicts for integration, VLDB 2009
- `fusing-data-with-correlations` (4/2) — Dong, Berti-Equille, Srivastava: Fusing Data with Correlations, arXiv preprint
- `sailing-information-ocean-source-dependence-2009` (4/2) — Dong, Berti-Equille, Srivastava: Sailing the Information Ocean with Awareness of Currents: Discovery and Application of Source Dependence, C

**Bears on:** H3, H4

*15 inventory rows tagged to this domain.*

### D15 — Subjective logic

**Tradition.** Subjective logic, opinion triangle, uncertainty mass, trust fusion operators, Jøsang.

**Canonical sources (inventory):**
- `josang-hayward-pope-trust-network-analysis-subjective-logic-2006` (4/3) — Josang, Hayward, Pope: Trust Network Analysis with Subjective Logic, ACSC 2006
- `collaborative-assessment-information-provider-reliability-sl-2011` (4/2) — Collaborative Assessment of Information Provider's Reliability and Expertise Using Subjective Logic, CollaborateCom 2011
- `subjective-logic-trust-discount-referral-paths-2024` (4/2) — On Subjective Logic Trust Discount for Referral Paths, FUSION 2024

**Bears on:** H1, H3, H4

*18 inventory rows tagged to this domain.*

### D16 — Trust and reputation systems

**Tradition.** Trust model, reputation system, trust propagation, web of trust, domain authority.

**Canonical sources (inventory):**
- `inter-agent-trust-models-comparative-study-2025` (5/3) — Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint in Agentic Web Protocol Design, arXiv
- `claimtrust-propagation-trust-scoring-rag-2025` (5/3) — ClaimTrust: Propagation Trust Scoring for RAG Systems, arXiv preprint
- `domain-aware-trust-network-extraction-propagation-2016` (4/3) — Domain-aware trust network extraction for trust propagation in large-scale heterogeneous trust networks, Knowledge-Based Systems

**Bears on:** H3, H5, H9

*20 inventory rows tagged to this domain.*

### D17 — Multi-agent belief systems

**Tradition.** Multi-agent beliefs, BDI, belief base merging, judgment aggregation, epistemic multi-agent systems.

**Canonical sources (inventory):**
- `reasoning-belief-evidence-trust-multiagent-setting` (5/3) — Reasoning About Belief, Evidence and Trust in a Multi-agent Setting
- `epistemic-sybil-resistance-multiplying-agents-2026` (5/3) — Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence, arXiv preprint
- `rethinking-epistemic-logic-belief-bases-2020-d17-recur` (4/3) — Rethinking Epistemic Logic with Belief Bases, arXiv preprint (duplicate of rethinking-epistemic-logic-belief-bases-2020, D10)

**Bears on:** H1, H2, H3, H4

*25 inventory rows tagged to this domain.*

### D18 — Scientific discourse representation

**Tradition.** Scientific discourse ontology, SWAN, SALT, discourse elements, claim-evidence networks, hypothesis ontology.

**Canonical sources (inventory):**
- `see-reasoning-discourse-ontology-2014` (4/2) — SEE: structured representation of scientific evidence in the biomedical domain using Semantic Web techniques (introduces the Reasoning and D
- `uspto-9472115-grading-ontological-links-certainty-patent` (4/2) — Grading ontological links based on certainty of evidential statements, US Patent 9,472,115 (assessed from search-result snippet text only; p
- `uspto-11244113-evidential-links-corroboration-patent` (4/2) — Evaluating evidential links based on corroboration for intelligence analysis, US Patent 11,244,113 (assessed from search-result snippet text

**Bears on:** H1, H2, H3, H4

*29 inventory rows tagged to this domain.*

### D19 — Nanopublications

**Tradition.** Nanopublication, assertion graph, provenance graph, publication info graph, trusty URI.

**Canonical sources (inventory):**
- `decentralized-provenance-aware-nanopublication-publishing` (3/3) — Decentralized provenance-aware publishing with nanopublications, PeerJ Computer Science
- `anatomy-of-a-nanopublication-2010` (4/2) — Groth, Gibson, Velterop: The anatomy of a nanopublication, Information Services & Use
- `extending-nanopublications-knowledge-provenance` (4/2) — Extending Nanopublications with Knowledge Provenance to support corroboration across independent sources, CEUR-WS Vol-3937

**Bears on:** H1, H2, H3, H4, H5, H6

*24 inventory rows tagged to this domain.*

### D20 — Micropublications

**Tradition.** Micropublication, claim network, evidence chain, statement-level citation.

**Canonical sources (inventory):**
- `micropublications-semantic-model-claims-evidence-2014` (4/3) — Clark, Ciccarese, Mitchell: Micropublications: a Semantic Model for Claims, Evidence, Arguments and Annotations in Biomedical Communications
- `typed-claim-network-scientific-literature` (3/2) — Reading Between the Citations: A Typed Claim Network for Scientific Literature, arXiv preprint
- `physician-suicide-claims-nanopublications-claim-networks-2022` (3/2) — Representing Physician Suicide Claims as Nanopublications: Proof-of-Concept Study Creating Claim Networks, JMIR

**Bears on:** H1, H2, H3, H4, H6

*7 inventory rows tagged to this domain.*

### D21 — Agent memory

**Tradition.** Agent memory, memory architecture, working/long-term memory, memory consolidation, cognitive architecture (SOAR, ACT-R).

**Canonical sources (inventory):**
- `graph-native-cognitive-memory-belief-revision-semantics-2026-d21-recur` (5/4) — Graph-Native Cognitive Memory for AI Agents: Formal Belief Revision Semantics for Versioned Memory Architectures, arXiv preprint (duplicate 
- `zep-graphiti-temporal-kg-agent-memory-2025-d21-recur` (4/4) — Rasmussen, Paliychuk, Beauvais, Ryan, Chalef: Zep: A Temporal Knowledge Graph Architecture for Agent Memory, arXiv preprint (duplicate of ze
- `toki-bitemporal-operator-algebra-contradiction-2026` (4/3) — TOKI: Bitemporal Operator Algebra for Contradiction Resolution, arXiv preprint

**Bears on:** H1, H2, H3, H4, H7

*27 inventory rows tagged to this domain.*

### D22 — Long-term memory for LLM agents

**Tradition.** LLM agent memory, persistent memory, memory stream, reflection, MemGPT-style paging, vector memory.

**Canonical sources (inventory):**
- `mitigating-provenance-role-collapse-typed-memory-2026` (5/3) — Mitigating Provenance-Role Collapse in Long-Term Agents via Typed Memory Representation, arXiv preprint
- `eywa-provenance-grounded-agent-memory-2026-d22-recur` (4/3) — Eywa: Provenance-Grounded Long-Term Memory for AI Agents, arXiv preprint (duplicate of eywa-provenance-grounded-agent-memory-2026, D07)
- `agent-traces-to-trust-evidence-provenance-survey-2026` (4/3) — From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents, arXiv preprint

**Bears on:** H1, H2, H3, H4, H5, H7, H9, H11

*20 inventory rows tagged to this domain.*

### D23 — Episodic memory

**Tradition.** Episodic memory, autobiographical memory, episode segmentation, event boundaries, experience replay.

**Canonical sources (inventory):**
- `em-llm-human-inspired-episodic-memory-infinite-context-2024` (5/4) — Fountas, Benfeghoul, Oomerjee, Christopoulou, Lampouras, Bou-Ammar, Wang: Human-inspired Episodic Memory for Infinite Context LLMs (EM-LLM),
- `em-llm-model-oss-github` (4/3) — em-llm/EM-LLM-model, GitHub repository (official EM-LLM implementation)
- `kurby-zacks-segmentation-perception-memory-events-2008` (3/2) — Kurby, Zacks: Segmentation in the Perception and Memory of Events, Trends in Cognitive Sciences, 2008

**Bears on:** H1, H2, H5

*26 inventory rows tagged to this domain.*

### D24 — RAG / Graph-RAG

**Tradition.** Retrieval-augmented generation, RAG, GraphRAG, hybrid retrieval, context assembly, chunking.

**Canonical sources (inventory):**
- `lineagerag-2026` (5/4) — LineageRAG, arXiv preprint
- `graphrag-prompt-engineering-requirement-traceability-2024` (4/3) — Leveraging Graph-RAG and Prompt Engineering to Enhance LLM-Based Automated Requirement Traceability and Compliance Checks, arXiv preprint
- `dibowski-full-traceability-provenance-kg-fois-2024` (4/3) — Dibowski: Full Traceability and Provenance for Knowledge Graphs, FOIS 2024

**Bears on:** H3, H4, H5, H7, H9

*25 inventory rows tagged to this domain.*
