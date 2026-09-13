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

### D25 — Human-AI collective intelligence

**Tradition.** Human-AI collaboration, collective intelligence, hybrid intelligence, human-in-the-loop knowledge curation.

**Canonical sources (inventory):**
- `omniscientist-coevolving-ecosystem-human-ai-scientists-2026` (4/4) — OmniScientist: Co-evolving Ecosystem of Human and AI Scientists, arXiv preprint
- `dynamics-human-ai-collective-knowledge-web-2026` (3/4) — Dynamics of Human-AI Collective Knowledge on the Web, ACM Web Conference 2026 (open-access arXiv copy; dynamical model of archive quality /
- `dynamics-human-ai-collective-knowledge-web-2026-acm-doi-dup` (3/4) — Dynamics of Human-AI Collective Knowledge on the Web, ACM Web Conference 2026 (publisher DOI form; duplicate of dynamics-human-ai-collective

**Bears on:** H1, H2, H3, H6, H11

*15 inventory rows tagged to this domain.*

### D26 — Decision provenance

**Tradition.** Decision provenance, decision trace, accountable decisions, PROV for decisions.

**Canonical sources (inventory):**
- `solozobov-verify-gated-completion-admission-control-2026` (4/4) — Solozobov: Verify-Gated Completion as Admission Control in a Governed Multi-Agent Runtime, arXiv preprint
- `singh-cobbe-norval-decision-provenance-accountable-systems-2019` (4/3) — Singh, Cobbe, Norval: Decision Provenance: Harnessing Data Flow for Accountable Systems, IEEE Access, 2019
- `singh-cobbe-norval-decision-provenance-accountable-systems-2019-preprint-dup` (4/3) — Singh, Cobbe, Norval: Decision Provenance: Harnessing Data Flow for Accountable Systems, arXiv preprint (duplicate of singh-cobbe-norval-dec

**Bears on:** H1, H2, H3, H7

*21 inventory rows tagged to this domain.*

### D27 — Decision intelligence

**Tradition.** Decision intelligence, decision modeling, decision records, DMN, decision automation.

**Canonical sources (inventory):**
- `dmn-omg-standard-spec` (4/2) — Decision Model and Notation (DMN), OMG standard specification (versions 1.0 through 1.7-beta found, a decade of active revision)
- `extracting-process-aware-decision-models-2024` (3/2) — Extracting Process-Aware Decision Models from Object-Centric Process Data, arXiv preprint
- `dmn-business-analytics-acm-2016` (3/2) — Enhancing Decision Model Notation (DMN) for Better Use in Business Analytics, ACM 2016

**Bears on:** H2, H3, H5, H9

*16 inventory rows tagged to this domain.*

### D28 — Data lineage

**Tradition.** Data lineage, dataflow provenance, lineage tracing, impact of upstream change.

**Canonical sources (inventory):**
- `provenance-semirings-pods-2007` (4/2) — Green, Karvounarakis, Tannen: Provenance Semirings, PODS 2007
- `dlprov-dataflow-provenance-dl-workflows-2025` (3/2) — DLProv, PeerJ Computer Science (data-centric provenance support for deep-learning workflow analysis)
- `openlineage-standard-oss-github` (3/2) — OpenLineage, GitHub repository (LF AI & Data Foundation open run/job/dataset lineage-event standard)

**Bears on:** H2, H3, H7, H9, H10

*14 inventory rows tagged to this domain.*

### D29 — Evidence graphs

**Tradition.** Evidence graph, evidence network, Bayesian evidence combination, evidential reasoning.

**Canonical sources (inventory):**
- `uspto-10445654-feedforward-evidence-graph-confidence-patent` (5/2) — Learning parameters in a feed forward probabilistic graphical model, US Patent 10,445,654
- `triple-confidence-measurement-kg-heterogeneous-evidences-2024` (4/2) — Triple Confidence Measurement in Knowledge Graph with Multiple Heterogeneous Evidences, World Wide Web journal
- `evidence-hierarchy-bayesian-object-classification-osint-2026` (4/2) — An Evidence Hierarchy for Bayesian Object Classification via OSINT-Aided Heterogeneous Sensor Fusion, arXiv preprint

**Bears on:** H3, H4

*11 inventory rows tagged to this domain.*

### D30 — Temporal databases

**Tradition.** Temporal database, valid-time table, Allen intervals, temporal query, history table.

**Canonical sources (inventory):**
- `provsql-update-provenance-temporal-2025` (4/2) — Demonstration of ProvSQL Update Provenance through Temporal Databases, ProvenanceWeek 2025
- `structured-belief-state-llm-memory-benchmark-2026` (3/2) — Structured Belief State and the First Precision-Aware Benchmark for LLM Memory Retrieval, arXiv preprint
- `surrealdb-tri-temporal-belief-history-blog` (3/2) — SurrealDB: Agent memory needs three clocks - tri-temporal belief history (product blog)

**Bears on:** H1, H2, H3, H4, H5

*18 inventory rows tagged to this domain.*

### D31 — Event calculus

**Tradition.** Event calculus, fluent, situation calculus, narrative reasoning, action effects.

**Canonical sources (inventory):**
- `epistemic-event-calculus-asp-2014` (4/3) — Ma, Miller, Morgenstern, Patkos: An Epistemic Event Calculus for ASP-based Reasoning About Knowledge of the Past, Present and Future, LPAR-1
- `kowalski-sergot-logic-based-calculus-events-1986` (3/2) — Kowalski, Sergot: A Logic-based Calculus of Events, New Generation Computing 4:67-94
- `thielscher-fluent-calculus-1999` (3/2) — Thielscher: From situation calculus to fluent calculus: State update axioms as a solution to the inferential frame problem, Artificial Intel

**Bears on:** H1, H2, H3, H7, H8, H9

*20 inventory rows tagged to this domain.*

### D32 — Ontology evolution

**Tradition.** Ontology evolution, ontology versioning, change management, concept drift, schema evolution.

**Canonical sources (inventory):**
- `obo-foundry-coordinated-ontology-evolution-2007` (3/3) — The OBO Foundry: Coordinated Evolution of Ontologies to Support Biomedical Data Integration, Nature Biotechnology
- `change-language-ontologies-knowledge-graphs-kgcl-2024` (4/2) — A Change Language for Ontologies and Knowledge Graphs (KGCL), arXiv preprint
- `ontology-change-management-change-patterns-2013` (4/2) — Ontology Change Management and Identification of Change Patterns, Journal on Data Semantics

**Bears on:** H1, H2, H6, H10

*19 inventory rows tagged to this domain.*

### D33 — Requirements engineering

**Tradition.** Requirements engineering, RE lifecycle, elicitation, specification, validation, goal-oriented RE (KAOS, i*).

**Canonical sources (inventory):**
- `iso-iec-ieee-29148-2018` (3/3) — ISO/IEC/IEEE International Standard
- `ali-etal-requirements-evolution-assumptions-reality-2011` (4/2) — Ali, Dalpiaz, Giorgini, Silva Souza: Requirements Evolution: From Assumptions to Reality, Springer book chapter (authorship/venue confirmed
- `uspto-8117539-bidirectional-trace-sync-patent` (4/2) — Method and system for bi-directionally synchronizing tracing relationships between a requirements repository and textual requirements docume

**Bears on:** H7, H8, H9

*24 inventory rows tagged to this domain.*

### D34 — Requirements traceability

**Tradition.** Requirements traceability, RTM, forward/backward traceability, trace links, pre/post-RS traceability.

**Canonical sources (inventory):**
- `ramesh-jarke-reference-models-traceability-2001` (4/3) — Ramesh, Jarke: Toward Reference Models for Requirements Traceability, IEEE Transactions on Software Engineering, 2001
- `gotel-finkelstein-traceability-problem-1994` (4/3) — Gotel, Finkelstein: An analysis of the requirements traceability problem, ICRE 1994
- `tracellm-2026-preprint` (4/3) — TraceLLM, arXiv preprint (preprint form of tracellm-2026, same title, both forms kept from LIT-02-S129's kept cell)

**Bears on:** H3, H7, H9

*30 inventory rows tagged to this domain.*

### D35 — Requirements provenance

**Tradition.** Requirements provenance, requirement origin, rationale capture, stakeholder attribution.

**Canonical sources (inventory):**
- `procko-provtracer-erau-dissertation-2025` (5/4) — Procko: On the Provenance of Software Systems: Automating Software Traceability with Knowledge Graph and Large Language Model Synergy (ProvT
- `ramesh-dhar-remap-rationale-capture-1992` (4/3) — Ramesh, Dhar: Supporting systems development by capturing deliberations during requirements engineering (REMAP), IEEE Transactions on Softwa
- `dibowski-full-traceability-provenance-kg-fois-2024-d35-recur` (4/3) — Dibowski: Full Traceability and Provenance for Knowledge Graphs, FOIS 2024 (duplicate of dibowski-full-traceability-provenance-kg-fois-2024,

**Bears on:** H3, H7

*15 inventory rows tagged to this domain.*

### D36 — Requirements evolution

**Tradition.** Requirements evolution, requirements change management, volatility, change propagation.

**Canonical sources (inventory):**
- `semantically-seeded-graph-propagated-impact-analysis-vision-2026` (4/3) — Toward Semantically-Seeded, Graph-Propagated Impact Analysis Across Software Artifacts: A Vision, arXiv preprint (names the blind spots of s
- `ali-etal-requirements-evolution-assumptions-reality-2011-d36-recur` (4/2) — Ali, Dalpiaz, Giorgini, Silva Souza: Requirements Evolution: From Assumptions to Reality, Springer book chapter (duplicate of ali-etal-requi
- `uspto-9202188-change-request-impact-analysis-patent` (4/2) — Impact analysis of change requests of information technology systems, US Patent 9,202,188

**Bears on:** H10

*31 inventory rows tagged to this domain.*

### D37 — Design rationale

**Tradition.** Design rationale, DR capture, argumentation-based design, rationale management systems.

**Canonical sources (inventory):**
- `bracewell-wallace-moss-knott-capturing-design-rationale-2009` (4/3) — Bracewell, R., Wallace, K., Moss, M., Knott, D.: Capturing design rationale, Computer-Aided Design, 2009
- `bracewell-ahmed-wallace-dred-design-folders-detc-2004` (4/3) — Bracewell, R.H., Ahmed, S., Wallace, K.M.: DRed and Design Folders: A Way of Capturing, Storing and Passing On Knowledge Generated During De
- `tang-jin-han-rationale-based-architecture-model-2007` (4/3) — Tang, A., Jin, Y., Han, J.: A rationale-based architecture model for design traceability and reasoning, Journal of Systems and Software, 200

**Bears on:** H7, H9, H10

*11 inventory rows tagged to this domain.*

### D38 — Architecture rationale

**Tradition.** Architecture rationale, architectural decision rationale, rationale documentation.

**Canonical sources (inventory):**
- `jansen-bosch-architecture-as-decisions-wicsa-2005` (5/4) — Jansen, A., Bosch, J.: Software Architecture as a Set of Architectural Design Decisions, WICSA 2005
- `iso-42010-2022-architecture-description-standard` (5/3) — ISO/IEC/IEEE 42010:2022, "Software, systems and enterprise
- `iso-42010-conceptual-model-working-group-page` (5/3) — ISO/IEC/IEEE 42010 Conceptual Model, the standard's own working-group-maintained reference page (iso-architecture.org)

**Bears on:** H7, H9

*19 inventory rows tagged to this domain.*

### D39 — Architecture knowledge management

**Tradition.** Architecture knowledge management, AKM, architectural knowledge vaporization, knowledge codification.

**Canonical sources (inventory):**
- `de-boer-architectural-knowledge-management-dissertation-2009` (5/4) — de Boer, R.C.: Architectural Knowledge Management: Supporting Architects and Auditors, VU Amsterdam PhD dissertation, 2009
- `dhar-vaidhyanathan-varma-agenticakm-2026` (5/4) — Dhar, R., Vaidhyanathan, K., Varma, V.: AgenticAKM: Enroute to Agentic Architecture Knowledge Management, AGENT'26 workshop @ ICSE 2026 (Rio
- `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` (5/4) — Dhar, R., Vaidhyanathan, K., Varma, V.: AgenticAKM: Enroute to Agentic Architecture Knowledge Management, arXiv preprint

**Bears on:** H1, H2, H6, H9, H10, H11

*21 inventory rows tagged to this domain.*

### D40 — Architecture Decision Records

**Tradition.** ADR, architecture decision record, MADR, decision log, superseded decisions.

**Canonical sources (inventory):**
- `kopp-armbruster-zimmermann-madr-format-tool-support-2018` (4/3) — Kopp, O., Armbruster, A., Zimmermann, O.: Markdown Architectural Decision Records: Format and Tool Support, ZEUS 2018 workshop, Dresden, 8-9
- `context-matters-automated-adr-generation-llms-2026` (4/3) — Context Matters: Evaluating Context Strategies for Automated ADR Generation Using LLMs, arXiv preprint, 2026
- `log4brains-oss-github` (4/3) — thomvaill/log4brains, GitHub repository

**Bears on:** H2, H9

*9 inventory rows tagged to this domain.*

### D41 — IBIS

**Tradition.** IBIS, issue-based information systems, gIBIS, Compendium, issue-position-argument.

**Canonical sources (inventory):**
- `conklin-begeman-gibis-hypertext-tool-cscw-1988` (5/3) — Conklin, J., Begeman, M.L.: gIBIS: a hypertext tool for exploratory policy discussion, Proceedings of the 1988 ACM Conference on Computer-Su
- `conklin-begeman-gibis-hypertext-tool-tois-1988-dup` (5/3) — Conklin, J., Begeman, M.L.: gIBIS: a hypertext tool for exploratory policy discussion, ACM Transactions on Information Systems, 1988
- `conklin-begeman-gibis-tool-all-reasons-jasis-1989` (4/3) — Conklin, J., Begeman, M.L.: gIBIS: A Tool for All Reasons, Journal of the American Society for Information Science, May 1989

**Bears on:** H3, H7, H9 (no inline H-tag in the terminology-map prose for this domain; inferred from the domain matrix framing and the rows' own content, not from a Pass-1 H-tag)

*10 inventory rows tagged to this domain.*

### D42 — QOC

**Tradition.** QOC, questions options criteria, design space analysis.

**Canonical sources (inventory):**
- `decision-oriented-programming-aporia-2026` (5/4) — Decision-Oriented Programming with Aporia, arXiv preprint, submitted 6 Apr 2026 (authors from UC San Diego, University of Pennsylvania, Corn
- `maclean-young-bellotti-moran-qoc-design-space-analysis-1991` (5/3) — MacLean, A., Young, R., Bellotti, V., Moran, T.: Questions, Options, and Criteria: Elements of Design Space Analysis, Human-Computer Interac
- `maclean-et-al-qoc-2020-reissue-dup` (5/3) — MacLean, A., Young, R.M., Bellotti, V.M.E., Moran, T.P.: Questions, Options, and Criteria: Elements of Design Space Analysis, chapter in Des

**Bears on:** H7, H8, H9

*7 inventory rows tagged to this domain.*

### D43 — Software traceability

**Tradition.** Software traceability, trace link, traceability information model, end-to-end traceability.

**Canonical sources (inventory):**
- `integrated-e2e-traceability-test-coverage-2014` (4/3) — An Integrated System for End-to-End Traceability and Requirements Test Coverage, ICSESS 2014
- `promota-model-driven-e2e-traceability-2026` (4/3) — ProMoTA
- `tefse2009-tim-origin-2009` (3/2) — Cleland-Huang, J., Chang, C.K., Christensen, M.: Getting Back to Basics: Promoting the Use of a Traceability Information Model in Practice,

**Bears on:** H9

*9 inventory rows tagged to this domain.*

### D44 — Trace-link recovery

**Tradition.** Trace link recovery, traceability recovery, IR-based tracing, LLM trace recovery.

**Canonical sources (inventory):**
- `antoniol-recovering-traceability-links-tse-2002` (5/3) — Antoniol, G., Canfora, G., Casazza, G., De Lucia, A., Merlo, E.: Recovering Traceability Links between Code and Documentation, IEEE Transact
- `transfer-learning-open-world-traceability-2022` (4/3) — Enhancing Automated Software Traceability by Transfer Learning from Open-World Data, arXiv preprint
- `usertrace-requirements-generation-traceability-2025` (4/3) — UserTrace: User-Level Requirements Generation and Traceability Recovery from Software Project Repositories, arXiv preprint

**Bears on:** H7, H9 (no inline H-tag in the terminology-map prose for this domain; inferred from the domain matrix framing and the rows' own content, not from a Pass-1 H-tag)

*25 inventory rows tagged to this domain.*

### D45 — Change impact analysis

**Tradition.** Change impact analysis, ripple effect, dependency analysis, impact propagation, program slicing.

**Canonical sources (inventory):**
- `assumptions-management-software-development-mapping-study-2018` (4/4) — Assumptions and Their Management in Software Development: A Systematic Mapping Study, Information and Software Technology (Elsevier), 2018 -
- `arnold-bohner-software-change-impact-analysis-book-1996` (5/3) — Arnold, R.S., Bohner, S.A.: Software Change Impact Analysis, IEEE Computer Society Press, 1996
- `weiser-program-slicing-tse-1984` (5/3) — Weiser, M.: Program Slicing, IEEE Transactions on Software Engineering, 1984

**Bears on:** H10

*28 inventory rows tagged to this domain.*

### D46 — Model-based systems engineering

**Tradition.** MBSE, SysML, model-centric engineering, system model integration.

**Canonical sources (inventory):**
- `model-based-digital-threads-sociotechnical-systems-2022` (4/4) — Model-Based Digital Threads for Socio-Technical Systems, Springer conference-proceedings chapter
- `us20250165226a1-ai-digital-thread-patent` (4/4) — Software-Code-Defined Digital Threads in Digital Engineering Systems with Artificial Intelligence (AI) Assistance, US Patent Application US2
- `cognitive-digital-thread-mbse-traceability-2025` (4/3) — Cognitive Digital Thread for Intelligent Traceability Establishment in MBSE, ISSE 2025

**Bears on:** H2, H3, H7

*20 inventory rows tagged to this domain.*

### D47 — Digital thread

**Tradition.** Digital thread, digital continuity, authoritative source of truth, lifecycle data integration.

**Canonical sources (inventory):**
- `model-based-digital-threads-sociotechnical-systems-2022-d47-recur` (4/4) — Model-Based Digital Threads for Socio-Technical Systems, Springer conference-proceedings chapter (duplicate of model-based-digital-threads-s
- `engineering-design-digital-thread-aiaa-2018` (3/3) — Engineering Design with Digital Thread, AIAA Journal 2018
- `engineering-design-digital-thread-aiaa-scitech-2018-dup` (3/3) — Engineering Design with Digital Thread, AIAA SciTech Jan 2018 (duplicate of engineering-design-digital-thread-aiaa-2018

**Bears on:** H2, H7

*20 inventory rows tagged to this domain.*

### D48 — Digital engineering

**Tradition.** Digital engineering, digital engineering ecosystem, model-based acquisition.

**Canonical sources (inventory):**
- `enterprise-architecture-digital-se-ecosystem-2022` (3/4) — Toward an Enterprise Architecture for a Digital Systems Engineering Ecosystem, Springer conference-proceedings chapter
- `pasoa-architecture-provenance-systems-2005` (4/3) — An Architecture for Provenance Systems, PASOA-project technical report, 2005 (no DOI assigned; OpenAlex record only)
- `model-management-ontology-kg-se-workflows-2025` (4/3) — Model management to support systems engineering workflows using ontology-based knowledge graphs, arXiv preprint

**Bears on:** H7

*8 inventory rows tagged to this domain.*

### D49 — Specification-driven development

**Tradition.** Specification-driven development, spec-first, contract-first, spec-as-source-of-truth.

**Canonical sources (inventory):**
- `agile-v-compliance-ready-ai-engineering-2026` (3/4) — Agile V: A Compliance-Ready Framework for AI-Augmented Engineering
- `specmap-llm-agent-datasheet-code-traceability-2026-d49-recur` (4/3) — SpecMap: Hierarchical LLM Agent for Datasheet-to-Code Traceability Link Recovery in Systems Engineering, arXiv preprint (duplicate of specma
- `github-spec-kit-oss` (2/3) — spec-kit, GitHub repository (github/spec-kit)

**Bears on:** H3, H7, H8, H9

*12 inventory rows tagged to this domain.*

### D50 — Executable specifications

**Tradition.** Executable specification, living documentation, specification by example, acceptance-test driven.

**Canonical sources (inventory):**
- `formalising-software-requirements-llms-2025` (3/2) — Formalising Software Requirements with Large Language Models, arXiv preprint
- `towards-traceable-test-driven-development-2009` (3/2) — Towards traceable test-driven development, IEEE TEFSE workshop, 2009
- `atdd-model-based-test-generation-2019` (3/2) — Enhancing Acceptance Test-Driven Development with Model-Based Test Generation, IEEE QRS-C, 2019

**Bears on:** H7, H9, H11

*15 inventory rows tagged to this domain.*

### D51 — Formal specification

**Tradition.** Formal specification, formal methods, Z, TLA+, Alloy, refinement.

**Canonical sources (inventory):**
- `verispecgen-intent-aligned-formal-spec-synthesis-traceable-refinement-2026` (4/3) — Ye, Z. et al. (incl. Microsoft Research authors): Intent-aligned Formal Specification Synthesis via Traceable Refinement (VeriSpecGen), arXi
- `oo-spec-to-implementation-formal-refinement-dissertation` (3/3) — From Object-Oriented Specification to Implementation: A Formal Refinement Methodology, PhD dissertation
- `formal-spec-refinement-implementation-path-planning-2016` (3/3) — Formal specification, refinement, and implementation of path planning, IEEE INNOVATIONS, 2016

**Bears on:** H7, H9, H10

*21 inventory rows tagged to this domain.*

### D52 — Behavior-driven development

**Tradition.** BDD, Gherkin, given-when-then, feature files, scenario-based testing.

**Canonical sources (inventory):**
- `scenario-driven-approach-traceability-icse-2001` (3/2) — A scenario-driven approach to traceability, ICSE 2001
- `agentic-ai-bdd-testing-llms-2025` (3/2) — Agentic AI for Behavior-Driven Development Testing Using Large Language Models, SCITEPRESS, 2025
- `law-to-gherkin-llm-behavioral-specs-food-safety-2025` (3/2) — From Law to Gherkin: A Human-Centred Quasi-Experiment on the Quality of LLM-Generated Behavioural Specifications from Food-Safety Regulation

**Bears on:** H7, H9, H11

*12 inventory rows tagged to this domain.*

### D53 — Software provenance

**Tradition.** Software provenance, code provenance, SBOM, supply-chain provenance, SLSA.

**Canonical sources (inventory):**
- `moreau-etal-open-provenance-model-v1.1-2010` (3/3) — Moreau, L. et al.: The Open Provenance Model core specification (OPM) v1.1, Future Generation Computer Systems, 2010
- `godfrey-understanding-software-artifact-provenance-2013` (3/2) — Godfrey, M.W.: Understanding software artifact provenance, Science of Computer Programming (invited paper, Paul Klint special issue), submit
- `slsa-spec-v0.1-provenance` (3/2) — SLSA Provenance Predicate, slsa.dev specification v0.1

**Bears on:** H2, H3, H9

*12 inventory rows tagged to this domain.*

### D54 — Build provenance

**Tradition.** Build provenance, reproducible builds, in-toto, attestation, artifact signing.

**Canonical sources (inventory):**
- `torres-arias-etal-in-toto-farm-to-table-usenix2019` (4/3) — Torres-Arias, S., Afzali, H., Kuppusamy, T.K., Curtmola, R., Cappos, J.: in-toto: Providing farm-to-table guarantees for bits and bytes, USE
- `kettle-attested-builds-verifiable-provenance-2026` (4/3) — Asad, A., Arko, A.: Kettle: Attested builds for verifiable software provenance, arXiv preprint, 2026
- `sok-taxonomy-attacks-oss-supply-chains-sp2023` (3/3) — SoK: Taxonomy of Attacks on Open-Source Software Supply Chains, IEEE S&P 2023

**Bears on:** H2, H3, H4, H9

*6 inventory rows tagged to this domain.*

### D55 — Artifact lineage

**Tradition.** Artifact lineage, artifact graph, derivation chain, pipeline lineage.

**Canonical sources (inventory):**
- `omnibor-verifiable-artifact-resolution-2024` (4/3) — OmniBOR: A System for Automatic, Verifiable Artifact Resolution across Software Supply Chains, arXiv preprint, 2024
- `omnibor-spec-repo-github-dedup` (4/3) — OmniBOR project specification repository (Artifact Identifier / Artifact Dependency Graph primary spec)
- `kettle-attested-builds-verifiable-provenance-2026` (4/3) — Asad, A., Arko, A.: Kettle: Attested builds for verifiable software provenance, arXiv preprint, 2026

**Bears on:** H2, H3, H11

*14 inventory rows tagged to this domain.*

### D56 — Agentic software engineering

**Tradition.** Agentic software engineering, AI software agents, autonomous coding, SWE agents, agent-driven development.

**Canonical sources (inventory):**
- `mise-en-place-agentic-coding-2026` (3/3) — Mise en Place for Agentic Coding: a deliberate-preparation context-engineering methodology, arXiv preprint
- `assistance-to-autonomy-sdlc-slr-2026` (3/3) — Assistance to Autonomy: A Systematic Literature Review of Agentic AI across the Software Development Life Cycle, arXiv preprint
- `hyperagent-generalist-se-2024` (3/3) — HyperAgent: Generalist Software Engineering Agents to Solve Coding Tasks at Scale, arXiv preprint

**Bears on:** H8, H9

*13 inventory rows tagged to this domain.*

### D57 — Coding-agent memory

**Tradition.** Coding agent memory, repository memory, project memory, codebase knowledge persistence.

**Canonical sources (inventory):**
- `shared-organizational-memory-enterprise-coding-agents-2026` (4/3) — Shared Organizational Memory for Enterprise Coding Agents, arXiv preprint (collection/curation/consumption memory pipeline)
- `dapi-memory-bank-oss` (4/3) — memory-bank, GitHub repository (dapi/memory-bank)
- `inside-the-scaffold-coding-agent-taxonomy-2026` (3/3) — Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures, arXiv preprint

**Bears on:** H8

*9 inventory rows tagged to this domain.*

### D58 — Cross-session coding agents

**Tradition.** Cross-session agent, session persistence, context carryover, resumable agents.

**Canonical sources (inventory):**
- `reasoner-executor-synthesizer-o1-context-2026` (3/3) — Reasoner-Executor-Synthesizer: Scalable Agentic Architecture with Static O(1) Context Window, arXiv preprint
- `active-context-compression-focus-agent-2026` (3/2) — Active Context Compression: Autonomous Memory Management in LLM Agents, arXiv preprint (the 'Focus Agent' consolidate-and-prune mechanism)
- `drawing-on-memory-dual-trace-cross-session-2026` (3/2) — Drawing on Memory: Dual-Trace Encoding Improves Cross-Session Recall in LLM Agents, arXiv preprint

**Bears on:** H2, H8

*7 inventory rows tagged to this domain.*

### D59 — Agent handoff

**Tradition.** Agent handoff, task handoff, context transfer, delegation protocol, baton passing.

**Canonical sources (inventory):**
- `context-lineage-assurance-non-human-identities-2025` (4/3) — Context Lineage Assurance for Non-Human Identities in Critical Multi-Agent Systems, arXiv preprint
- `a2a-protocol-spec-linux-foundation` (4/3) — Agent2Agent (A2A) Protocol specification, canonical repository (github.com/a2aproject/A2A)
- `awcp-workspace-delegation-protocol-2026` (3/3) — AWCP: A Workspace Delegation Protocol for Deep-Engagement Collaboration across Remote Agents, arXiv preprint

**Bears on:** H3, H5

*8 inventory rows tagged to this domain.*

### D60 — Agent checkpointing

**Tradition.** Agent checkpointing, state snapshot, resumption, recovery point, workflow checkpoint.

**Canonical sources (inventory):**
- `langgraph-checkpoint-library-oss` (4/4) — LangGraph checkpoint library (github.com/langchain-ai/langgraph, libs/checkpoint)
- `reasoning-provenance-beyond-checkpoints-2026` (4/3) — Reasoning Provenance for Autonomous AI Agents: Structured Behavioral Analytics Beyond State Checkpoints and Execution Traces, arXiv preprint
- `resume-means-resume-conformance-contract-2026` (4/3) — Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers, 

**Bears on:** H2, H3, H8

*8 inventory rows tagged to this domain.*

### D61 — Hierarchical task networks

**Tradition.** HTN, hierarchical task network, task decomposition, method decomposition.

**Canonical sources (inventory):**
- `mage-hierarchical-agent-memory-2026` (4/2) — MAGE: Memory as Agent-Guided Exploration, arXiv preprint, 2026
- `shop2-htn-planning-system-jair-2003` (2/1) — Nau, D. et al.: SHOP2: An HTN Planning System, Journal of Artificial Intelligence Research (JAIR) 20, 2003
- `georgievski-aiello-htn-survey-aij-2015` (2/1) — Georgievski, I., Aiello, M.: HTN planning: Overview, comparison, and beyond, Artificial Intelligence 222, 2015

**Bears on:** H1, H2, H5, H11

*6 inventory rows tagged to this domain.*

### D62 — AI planning

**Tradition.** AI planning, PDDL, plan representation, plan execution, replanning.

**Canonical sources (inventory):**
- `ghallab-nau-traverso-actors-view-position-paper-aij-2013` (3/2) — Ghallab, M., Nau, D., Traverso, P.: The Actor's View of Automated Planning and Acting: A Position Paper, Artificial Intelligence 208, 2013 -
- `ghallab-nau-traverso-automated-planning-acting-book-2016` (3/2) — Ghallab, M., Nau, D., Traverso, P.: Automated Planning and Acting, Cambridge University Press, 2016
- `hayashi-cho-ohsuga-planning-execution-knowledge-updates-2002` (3/2) — Hayashi, H., Cho, K., Ohsuga, A.: Integrating Planning, Action Execution, Knowledge Updates and Plan Modifications via Logic Programming, LN

**Bears on:** H2, H11

*7 inventory rows tagged to this domain.*

### D63 — Execution monitoring

**Tradition.** Execution monitoring, plan monitoring, discrepancy detection, expectation monitoring.

**Canonical sources (inventory):**
- `bounded-expectations-discrepancy-detection-gda-workshop` (4/3) — Bounded Expectations for Discrepancy Detection in Goal-Driven Autonomy, AAAI workshop paper (cdn.aaai.org/ocs/ws/ws1245/8829-38107-1-PB.pdf)
- `execution-monitoring-tbohne-oss` (3/2) — execution_monitoring (github.com/tbohne/execution_monitoring), T. Bohne
- `simplanner-execution-monitoring-replanning-dynamic-worlds-2001` (3/2) — SimPlanner: An Execution-Monitoring System for Replanning in Dynamic Worlds, LNCS/AI conference proceedings, 2001

**Bears on:** H2, H3, H10, H11

*7 inventory rows tagged to this domain.*

### D64 — Verification and validation

**Tradition.** V&V, verification and validation, test evidence, assurance case, safety case.

**Canonical sources (inventory):**
- `calinescu-dynamic-assurance-cases-self-adaptive-tse-2017` (4/3) — Calinescu, R. et al.: Engineering Trustworthy Self-Adaptive Software with Dynamic Assurance Cases, IEEE Transactions on Software Engineering
- `kelly-weaver-goal-structuring-notation-2004` (4/2) — Kelly, T., Weaver, R.: The Goal Structuring Notation - A Safety Argument Notation, DSN Workshop on Assurance Cases, 2004
- `harmonized-requirement-based-safety-assurance-argumentation-2025` (4/2) — Toward a Harmonized Approach: Requirement-based Structuring of a Safety Assurance Argumentation for Automated Vehicles, arXiv preprint, 2025

**Bears on:** H9, H11

*7 inventory rows tagged to this domain.*

### D65 — Runtime verification

**Tradition.** Runtime verification, monitor synthesis, temporal-logic monitoring, trace checking.

**Canonical sources (inventory):**
- `runtime-verification-self-adaptive-changing-requirements-2023` (4/3) — Runtime Verification of Self-Adaptive Systems with Changing Requirements, arXiv preprint, 2023
- `calinescu-self-adaptive-quantitative-verification-runtime-cacm-2012` (4/3) — Calinescu, R. et al.: Self-adaptive software needs quantitative verification at runtime, CACM, 2012
- `large-scale-trace-checking-mapreduce-2015` (2/1) — Efficient Large-scale Trace Checking Using MapReduce, arXiv preprint, 2015

**Bears on:** H11

*9 inventory rows tagged to this domain.*

### D66 — Requirements monitoring

**Tradition.** Requirements monitoring, requirements at runtime, awareness requirements, requirement reflection.

**Canonical sources (inventory):**
- `fickas-feather-requirements-monitoring-dynamic-environments-isre-1995` (4/3) — Fickas, S., Feather, M.S.: Requirements monitoring in dynamic environments, RE'95 (IEEE International Symposium on Requirements Engineering)
- `souza-lapouchnian-robinson-mylopoulos-awareness-requirements-seams-2011` (4/3) — Souza, V.E.S., Lapouchnian, A., Robinson, W.N., Mylopoulos, J.: Awareness Requirements for Adaptive Systems, SEAMS 2011
- `sawyer-bencomo-whittle-letier-requirements-reflection-icse-2010` (4/3) — Sawyer, P., Bencomo, N., Whittle, J., Letier, E.: Requirements Reflection: Requirements as Runtime Entities, ICSE 2010 NIER track

**Bears on:** H11

*10 inventory rows tagged to this domain.*

### D67 — Observability-driven development

**Tradition.** Observability-driven development, telemetry-informed development, production feedback.

**Canonical sources (inventory):**
- `event-sourced-observable-software-architectures-experience-report-2022` (4/3) — Event-sourced, observable software architectures: An experience report, Software: Practice and Experience, 2022
- `johnson-hackystat-software-project-telemetry-ieee-software-2005` (4/2) — Johnson, P.: Improving Software Development Management through Software Project Telemetry, IEEE Software, 2005
- `mind-the-metrics-telemetry-aware-ide-development-2025` (3/2) — Mind the Metrics: Patterns for Telemetry-Aware In-IDE AI Application Development using MCP, arXiv preprint, 2025

**Bears on:** H11 (no inline H-tag in the terminology-map prose for this domain; inferred from the domain matrix framing and the rows' own content, not from a Pass-1 H-tag)

*8 inventory rows tagged to this domain.*

### D68 — Self-adaptive systems

**Tradition.** Self-adaptive systems, adaptation logic, managed/managing system, models@runtime.

**Canonical sources (inventory):**
- `weyns-etal-forms-reference-model-taas-2012` (4/3) — Weyns, D. et al.: FORMS: Unifying Reference Model for Formal Specification of Distributed Self-Adaptive Systems, ACM Transactions on Autonom
- `cheng-delemos-etal-self-adaptive-systems-research-roadmap-2009` (3/3) — Cheng, B.H.C., de Lemos, R. et al.: Software Engineering for Self-Adaptive Systems: A Research Roadmap, Springer LNCS 5525, 2009 (Dagstuhl S
- `delemos-giese-etal-self-adaptive-systems-second-roadmap-2013` (3/3) — de Lemos, R., Giese, H. et al.: Software Engineering for Self-Adaptive Systems: A Second Research Roadmap, Springer LNCS 7475, 2013 (Dagstuh

**Bears on:** H1, H11

*7 inventory rows tagged to this domain.*

### D69 — MAPE-K

**Tradition.** MAPE-K, monitor-analyze-plan-execute, knowledge base loop, autonomic manager.

**Canonical sources (inventory):**
- `ibm-architectural-blueprint-autonomic-computing-whitepaper-2006` (4/4) — An Architectural Blueprint for Autonomic Computing, IBM technical white paper, 4th ed., June 2006
- `delaiglesia-weyns-mapek-formal-templates-taas-2015` (4/3) — De la Iglesia, D.G., Weyns, D.: MAPE-K Formal Templates to Rigorously Design Behaviors for Self-Adaptive Systems, ACM Transactions on Autono
- `arcaini-etal-modeling-analyzing-mapek-feedback-loops-seams2015` (4/3) — Arcaini, P., Camilli, M., Gargantini, A., Scandurra, P.: Modeling and Analyzing MAPE-K Feedback Loops for Self-Adaptation, SEAMS 2015

**Bears on:** H2, H3, H11

*6 inventory rows tagged to this domain.*

### D70 — Autonomic computing

**Tradition.** Autonomic computing, self-management, self-configuration, self-healing.

**Canonical sources (inventory):**
- `huebscher-mccann-survey-autonomic-computing-acm-csur-2008` (3/3) — Huebscher, M.C., McCann, J.A.: A survey of autonomic computing
- `ganek-corbi-dawning-autonomic-computing-era-ibm-sysj-2003` (3/3) — Ganek, A.G., Corbi, T.A.: The dawning of the autonomic computing era, IBM Systems Journal, vol 42(1), 2003
- `icac2004-policy-enablement-toolkit-autonomic-computing` (3/2) — A toolkit for policy enablement in autonomic computing, ICAC 2004

**Bears on:** H11 (no inline H-tag in the terminology-map prose for this domain; inferred from the domain matrix framing and the rows' own content, not from a Pass-1 H-tag)

*6 inventory rows tagged to this domain.*

### D71 — Continuous requirements engineering

**Tradition.** Continuous RE, just-in-time requirements, agile RE, requirements in DevOps.

**Canonical sources (inventory):**
- `oriol-etal-fame-continuous-requirements-elicitation-re2018` (4/3) — Oriol, M., Stade, M., Fotrousi, F. et al.: FAME: Supporting Continuous Requirements Elicitation by Combining User Feedback and Monitoring, R
- `requirements-management-devops-multivocal-mapping-2023` (3/3) — Requirements management in DevOps environments: a multivocal mapping study, Requirements Engineering, Springer, 2023
- `knauss-etal-acon-contextual-requirements-uncertainty-runtime-2016` (3/2) — Knauss, A., Damian, D., Franch, X. et al.: ACon: A learning-based approach to deal with uncertainty in contextual requirements at runtime, I

**Bears on:** H9, H11

*6 inventory rows tagged to this domain.*

### D72 — DevOps traceability

**Tradition.** DevOps traceability, CI/CD traceability, deployment traceability, release evidence.

**Canonical sources (inventory):**
- `gotel-finkelstein-traceability-problem-1994-d72-recur` (4/3) — Gotel, O.C.Z., Finkelstein, A.C.W.: An analysis of the requirements traceability problem, ICRE 1994 (duplicate of gotel-finkelstein-traceabi
- `slsa-framework-homepage-2023` (3/3) — SLSA (Supply-chain Levels for Software Artifacts), slsa.dev
- `sale-etal-requirement-traceability-accuracy-devops-2021` (3/3) — Sale, V.M., Thigale, S., Melinamath, B.C.: An Effective Approach for Accuracy of Requirement Traceability in DevOps, Springer, 2021

**Bears on:** H7, H9 (no inline H-tag in the terminology-map prose for this domain; inferred from the domain matrix framing and the rows' own content, not from a Pass-1 H-tag)

*6 inventory rows tagged to this domain.*

## Top-20 collision candidate list

**Status filter, decided and applied here.** The section dispatching this task names no
`status` filter for "the inventory's `collision_candidate: yes` rows ranked by pre-scores."
The inventory carries exactly one `collision_candidate: yes` row with `status: excluded`
(`structured-belief-state-llm-memory-benchmark-2026-d22-recur`) — a deliberate, preserved
cross-phase scoring disagreement (Pass 1a scored the same source `no` at D30 with identical
pre-scores; Pass 1b scored it `yes` at D22), left unresolved for `phase-lit-04` rather than
averaged away. Every other `excluded`/duplicate row carries `collision_candidate: no` by
convention; the flag lives on canonical (`candidate`-status) rows. **Decision: this ranking
includes only `status: candidate` rows.** Reason: `excluded` is a terminal state — the row has
already been dropped from further consideration for a documented reason — so promoting an
excluded row to a "deep-read candidate" list would contradict its own exclusion without
adjudicating it, which is explicitly Pass 2's job, not this pass's. This also means the
D22/D30 disagreement itself does not appear in the list below; it remains fully findable in
the inventory for `phase-lit-04` and is not touched here. Filtering to `candidate` status
leaves 365 eligible rows out of 366 total `collision_candidate: yes` rows.

**Ranking mechanics.** Rows are ranked by `component_prescore + architecture_prescore`
(descending), ties broken by `architecture_prescore` (descending), per the evidence contract's
scoring rubric (`PLAN-023.03`, "Similarity scoring") as read by the coordinator's addressing
facts. This produces two exact ties within the top 20, honestly reported rather than forced
into an artificial order:

- **Ranks 1–13** are a 13-way tie: all score `component=5, architecture=4` (sum 9). The two
  pre-scores are identical across all 13 rows, so no further contract-defined criterion
  separates them; they are listed in `source_id` alphabetical order, disclosed as a
  non-evidentiary ordering convenience only.
- **Ranks 14–20** are 7 of an 8-way tie at `component=4, architecture=4` (sum 8). All 8 rows
  are equally eligible for rank 14; capping the list at exactly 20 (per this section's own
  "a list of 20" requirement) forces a cut inside this tied group. The cut is made by
  `source_id` alphabetical order — again disclosed as arbitrary, not as a scoring difference.
  The row dropped by this cut is `zep-graphiti-temporal-kg-agent-memory-2025` (D04), which is
  otherwise tied with ranks 14–20 and would be rank 21 under the same alphabetical convention.

**Deep-read marking outcome — contract/section conflict, reported rather than resolved.** The
evidence contract's inventory schema (`PLAN-023.03`, "Source inventory format") defines
`status` with allowed values `candidate` / `deep_read` / `excluded` — the only field in the
13-column schema that could carry a "this row is a deep-read candidate" mark. But the
dispatching section is explicit that "status stays `candidate` until LIT-04 actually reads
them," i.e. this pass may not set `status: deep_read`. The contract's only marking mechanism
is therefore the one field the section forbids using at this stage, and no second field
exists to carry the mark instead. Per the coordinator's addressing facts, the inventory is
**not** edited to invent a new column or overload an existing one. This ranked list is the
deep-read designation for this pass; `03_source_inventory.csv` is unmodified by `LIT-03 C`.

| Rank | source_id | comp/arch | domain | Reason |
|---|---|---|---|---|
| 1 | `de-boer-architectural-knowledge-management-dissertation-2009` | 5/4 | D39 | 2009 dissertation naming "architectural knowledge vaporization" — the failure mode D-System's provenance/typed-transition claims (H2, H9) exist to prevent, described 15+ years earlier. |
| 1 | `decision-oriented-programming-aporia-2026` | 5/4 | D42 | Aporia (2026): an AI coding agent elicits design decisions as Questions, tracks them in a persistent Decision Bank, encodes each as an executable test suite traceable to code — the strongest single collision found across the whole dispatch against H7/H8/H9 at once, published this same year. |
| 1 | `dhar-vaidhyanathan-varma-agenticakm-2026` | 5/4 | D39 | AgenticAKM (AGENT'26 @ ICSE 2026): specialized agents for architecture Extraction/Retrieval/Generation/Validation collaborate to generate ADRs from code repositories — a direct H6/H8 collision, an explicitly agentic reframing of AKM postdating D-System's own conception. |
| 1 | `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` | 5/4 | D39 | Same AgenticAKM paper via its canonical arXiv identifier, kept per the two-identifier-form rule rather than collapsed into the row above. |
| 1 | `em-llm-human-inspired-episodic-memory-infinite-context-2024` | 5/4 | D23 | EM-LLM: organizes LLM context into episodic events via Bayesian-surprise plus graph-theoretic boundary refinement, retrieved via similarity-plus-temporal-contiguity modeled on human episodic recall — squarely on H5 (topology-aware context transfer). |
| 1 | `evidence-graphs-fair-computation-defeasible-reasoning-2021` | 5/4 | D11 | Treats computational provenance itself as a defeasible argument for a result's validity, combining an evidence graph, FAIR provenance and defeasible reasoning over conflicting evidence — close to D-System's provenance-as-conflict-resolution-input hypothesis (H3). |
| 1 | `graph-native-cognitive-memory-belief-revision-semantics-2026` | 5/4 | D07 | Proposes AGM-style formal belief-revision semantics over a graph-native, versioned, provenance-linked memory architecture for AI agents — directly overlapping D-System's state, transition and provenance models (H1/H2/H3/H5). |
| 1 | `jansen-bosch-architecture-as-decisions-wicsa-2005` | 5/4 | D38 | The field's foundational 2004/2005 paradigm shift reframing architecture as decisions-plus-rationale rather than structure alone — direct ancestor of current ADR practice, bearing on H7/H9. |
| 1 | `keim-kaplan-scattered-to-structured-akm-vision-2026` | 5/4 | D39 | An automated pipeline (2026) extracting architectural knowledge from heterogeneous artifacts, linking/reconciling it into a structured knowledge base for change-impact analysis and RAG-based QA — a direct, current H6/H10/H11 collision, publicly proposed the same month this campaign ran. |
| 1 | `lineagerag-2026` | 5/4 | D24 | LineageRAG induces "Evidence Demands," expands them through graph retrieval while explicitly preserving demand-passage provenance, then grounds supported demands in source text — a near-direct implementation of D-System's evidence/provenance/lineage framing (H3, H5, H9). |
| 1 | `log-is-the-agent-event-sourced-reactive-graphs-2026` | 5/4 | D06 | The single closest title-and-abstract match to D-System's own architecture found across the entire dispatch — event-sourced, reactive graph, auditable, forkable, agentic — against H1, H2, H6, H7 and H9. |
| 1 | `procko-provtracer-erau-dissertation-2025` | 5/4 | D35 | ERAU doctoral dissertation building "ProvTracer" on PROV-O and the Basic Formal Ontology — a full doctoral treatment of D-System's own combination of knowledge graph + LLM + provenance + software/requirements traceability. |
| 1 | `tgms-agent-native-bitemporal-graph-2026` | 5/4 | D05 | TGMS: an agent-native bi-temporal graph management system with validated temporal operators and trace-grounded answer checking — one of the closest single-paper matches to D-System's own bi-temporal, agent-native, evidence/trace-grounded architecture (H1, H2, H5, H6). |
| 14 | `assumptions-management-software-development-mapping-study-2018` | 4/4 | D45 | The single most directly on-point source found for H10's "assumption" framing specifically (as opposed to change-impact-analysis's usual change/requirement-centric framing) — surfaced by D45's own mandated collision query. |
| 14 | `ibm-architectural-blueprint-autonomic-computing-whitepaper-2006` | 4/4 | D69 | The actual origin document of the MAPE-K acronym and reference architecture — the primary source against which D-System's own control-loop terminology (H2, H11) must be checked. |
| 14 | `langgraph-checkpoint-library-oss` | 4/4 | D60 | LangGraph's checkpoint library: thread-scoped state snapshots per superstep with pluggable serialization, human-in-the-loop and time-travel debugging — the most directly comparable production system to D-System's own phase/checkpoint claims (H8). |
| 14 | `model-based-digital-threads-sociotechnical-systems-2022` | 4/4 | D46 | Spans the requirement-design-runtime chain named in this domain's own mandated collision query, bridging D46/D47 directly — bears on H2/H7. |
| 14 | `omniscientist-coevolving-ecosystem-human-ai-scientists-2026` | 4/4 | D25 | Proposes a co-evolving ecosystem of human and AI scientists — a direct H6-relevant end-to-end collision candidate for D-System's integrated human-agent knowledge-evolution hypothesis. |
| 14 | `solozobov-verify-gated-completion-admission-control-2026` | 4/4 | D26 | Introduces a packetized state model with context shaping, memory ownership rules, and decision traces for a governed multi-agent runtime — architecturally close to D-System's own state/transition/provenance framing (H1/H2). |
| 14 | `us20250165226a1-ai-digital-thread-patent` | 4/4 | D46 | US patent application naming both "digital thread" and "digital engineering" together with an AI-assisted, code-defined thread-generation mechanism — a strong D47/D48/H7 collision. |

*365 `status: candidate` rows carried `collision_candidate: yes` at the time this list was
built; entries beyond rank 20 do not appear here, per this section's own "a list of 20"
scope.*
