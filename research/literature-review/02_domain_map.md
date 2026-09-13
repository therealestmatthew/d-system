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
