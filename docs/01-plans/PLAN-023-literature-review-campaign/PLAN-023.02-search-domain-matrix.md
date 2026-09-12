---
schema_version: 1
id: doc-lit-campaign-domain-matrix
code: PLAN-023.02
title: Literature-review search-domain matrix — 72 domains assigned to Pass 1 phases with terminology variants and collision queries
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

# Literature-review search-domain matrix

Every search domain from the review instructions' §5, assigned to exactly one Pass 1 search
phase, with the terminology variants each search must cover and at least one pre-crafted
collision query in the methodology's Phase E style. No domain is left to a search agent's
judgment. Domain ids `D01`–`D72` follow the §5 order and are the ids every reproducibility-
ledger row carries (evidence contract, `PLAN-023.03`).

Within each phase, every domain traverses the methodology's search-strategy Phases A–E
(vocabulary discovery, backward chaining, forward chaining, system search, collision search);
the phase assignment below is a session grouping, not a substitute for that traversal. Variants
are minimums, not caps — Phase A vocabulary discovery extends them, and the extensions are
logged in the ledger. The collision queries are starting points for Phase E; Pass 3
(phase-lit-06) re-runs them per hypothesis with gap-driven additions.

## Phase assignment summary

| Pass 1 phase | Domains | Count |
|---|---|---|
| phase-lit-01 | D01–D20, D28–D32 | 25 |
| phase-lit-02 | D21–D27, D33–D45 | 20 |
| phase-lit-03 | D46–D72 | 27 |

## phase-lit-01 — knowledge representation, provenance and epistemics

| Id | Domain | Terminology variants (minimum) | Collision query (Phase E style) |
|---|---|---|---|
| D01 | Knowledge graphs | knowledge graph, ontology, RDF graph, property graph, knowledge base construction, entity-relation model | "knowledge graph" epistemic status lifecycle state classification |
| D02 | Semantic Web | Semantic Web, RDF/OWL, linked data, SPARQL, named graphs, reification | "named graph" provenance belief statement-level metadata |
| D03 | W3C PROV / provenance | W3C PROV, PROV-O, provenance ontology, prov:Activity/Agent/Entity, derivation, attribution, delegation | PROV-O reasoning lineage conflict resolution authority |
| D04 | Temporal knowledge graphs | temporal knowledge graph, TKG, time-aware embedding, temporal fact, quadruple (s,p,o,t) | "temporal knowledge graph" belief revision provenance |
| D05 | Bi-temporal systems | bi-temporal, valid time, transaction time, temporal versioning, as-of query | bitemporal knowledge base belief validity transaction time |
| D06 | Event sourcing | event sourcing, append-only log, CQRS, event store, projection, immutable log | "event sourced" knowledge graph state transition provenance |
| D07 | Belief revision / AGM | belief revision, AGM theory, belief contraction, belief update, epistemic entrenchment, iterated revision | AGM belief revision provenance implementation agent memory |
| D08 | Truth-maintenance systems | truth maintenance system, TMS, ATMS, JTMS, reason maintenance, dependency-directed backtracking, justification network | truth maintenance justification network assumption retraction impact |
| D09 | Epistemic logic | epistemic logic, knowledge operator, S5, common knowledge, dynamic epistemic logic | dynamic epistemic logic multi-agent knowledge base implementation |
| D10 | Doxastic logic | doxastic logic, belief operator, KD45, belief base, graded belief | doxastic logic belief base software agent architecture |
| D11 | Defeasible reasoning | defeasible reasoning, non-monotonic logic, default logic, defeaters, prima facie justification | defeasible reasoning knowledge base conflicting evidence provenance |
| D12 | Computational argumentation | argumentation framework, Dung semantics, abstract argumentation, structured argumentation, ASPIC+, argument attack/support | argumentation framework source reliability evidence graph |
| D13 | Truth discovery | truth discovery, source reliability estimation, fact-finding algorithms, conflicting claims resolution | "truth discovery" "source dependence" copying detection graph |
| D14 | Data fusion | data fusion, conflict resolution, source accuracy, copy detection, dependence-aware fusion | data fusion source dependence independent confirmation discount |
| D15 | Subjective logic | subjective logic, opinion triangle, uncertainty mass, trust fusion operators, Jøsang | subjective logic provenance trust fusion knowledge graph |
| D16 | Trust and reputation systems | trust model, reputation system, trust propagation, web of trust, domain authority | trust propagation domain authority claim arbitration multi-agent |
| D17 | Multi-agent belief systems | multi-agent beliefs, BDI, belief base merging, judgment aggregation, epistemic multi-agent systems | multi-agent belief merging conflicting sources provenance human agent |
| D18 | Scientific discourse representation | scientific discourse ontology, SWAN, SALT, discourse elements, claim-evidence networks, hypothesis ontology | scientific claim evidence network provenance corroboration ontology |
| D19 | Nanopublications | nanopublication, assertion graph, provenance graph, publication info graph, trusty URI | nanopublication assertion provenance independent corroboration |
| D20 | Micropublications | micropublication, claim network, evidence chain, statement-level citation | micropublications evidence chain claim support falsification |
| D28 | Data lineage | data lineage, dataflow provenance, lineage tracing, impact of upstream change | data lineage upstream change downstream impact knowledge |
| D29 | Evidence graphs | evidence graph, evidence network, Bayesian evidence combination, evidential reasoning | evidence graph independent sources confidence propagation |
| D30 | Temporal databases | temporal database, valid-time table, Allen intervals, temporal query, history table | temporal database belief state supersession history |
| D31 | Event calculus | event calculus, fluent, situation calculus, narrative reasoning, action effects | event calculus knowledge state fluent provenance reasoning history |
| D32 | Ontology evolution | ontology evolution, ontology versioning, change management, concept drift, schema evolution | ontology evolution change propagation dependent artifacts |

## phase-lit-02 — agent memory, decision intelligence, requirements and rationale

| Id | Domain | Terminology variants (minimum) | Collision query (Phase E style) |
|---|---|---|---|
| D21 | Agent memory | agent memory, memory architecture, working/long-term memory, memory consolidation, cognitive architecture (SOAR, ACT-R) | "agent memory" provenance temporal belief update contradiction |
| D22 | Long-term memory for LLM agents | LLM agent memory, persistent memory, memory stream, reflection, MemGPT-style paging, vector memory | LLM agent long-term memory belief revision provenance retrieval |
| D23 | Episodic memory | episodic memory, autobiographical memory, episode segmentation, event boundaries, experience replay | episodic memory agent session boundary consolidation retrieval |
| D24 | RAG / Graph-RAG | retrieval-augmented generation, RAG, GraphRAG, hybrid retrieval, context assembly, chunking | GraphRAG provenance-aware retrieval reasoning lineage context selection |
| D25 | Human-AI collective intelligence | human-AI collaboration, collective intelligence, hybrid intelligence, human-in-the-loop knowledge curation | human-AI shared knowledge base co-evolution provenance authority |
| D26 | Decision provenance | decision provenance, decision trace, accountable decisions, PROV for decisions | "decision provenance" architecture knowledge graph downstream impact |
| D27 | Decision intelligence | decision intelligence, decision modeling, decision records, DMN, decision automation | decision intelligence lineage requirements implementation feedback |
| D33 | Requirements engineering | requirements engineering, RE lifecycle, elicitation, specification, validation, goal-oriented RE (KAOS, i*) | goal-oriented requirements knowledge evolution assumption revision |
| D34 | Requirements traceability | requirements traceability, RTM, forward/backward traceability, trace links, pre/post-RS traceability | requirements traceability matrix reasoning evidence bidirectional runtime |
| D35 | Requirements provenance | requirements provenance, requirement origin, rationale capture, stakeholder attribution | requirements provenance origin evidence decision lineage |
| D36 | Requirements evolution | requirements evolution, requirements change management, volatility, change propagation | requirements change propagation downstream artifacts impact assessment |
| D37 | Design rationale | design rationale, DR capture, argumentation-based design, rationale management systems | design rationale capture retrieval impact assumption change |
| D38 | Architecture rationale | architecture rationale, architectural decision rationale, rationale documentation | architecture rationale traceability code requirements runtime |
| D39 | Architecture knowledge management | architecture knowledge management, AKM, architectural knowledge vaporization, knowledge codification | architecture knowledge management decision evidence lineage tool |
| D40 | Architecture Decision Records | ADR, architecture decision record, MADR, decision log, superseded decisions | ADR supersession lineage automated impact analysis |
| D41 | IBIS | IBIS, issue-based information systems, gIBIS, Compendium, issue-position-argument | IBIS issue position argument software traceability implementation |
| D42 | QOC | QOC, questions options criteria, design space analysis | QOC design space analysis decision traceability |
| D43 | Software traceability | software traceability, trace link, traceability information model, end-to-end traceability | software traceability reasoning decisions tests runtime end-to-end |
| D44 | Trace-link recovery | trace link recovery, traceability recovery, IR-based tracing, LLM trace recovery | automated trace recovery rationale evidence links code |
| D45 | Change impact analysis | change impact analysis, ripple effect, dependency analysis, impact propagation, program slicing | "impact analysis" assumption requirements code test propagation |

## phase-lit-03 — digital thread, specification-driven development, software provenance, agentic SE and runtime feedback

| Id | Domain | Terminology variants (minimum) | Collision query (Phase E style) |
|---|---|---|---|
| D46 | Model-based systems engineering | MBSE, SysML, model-centric engineering, system model integration | MBSE requirement design verification runtime thread provenance |
| D47 | Digital thread | digital thread, digital continuity, authoritative source of truth, lifecycle data integration | "digital thread" requirements design code test runtime evidence |
| D48 | Digital engineering | digital engineering, digital engineering ecosystem, model-based acquisition | digital engineering knowledge provenance decision lifecycle |
| D49 | Specification-driven development | specification-driven development, spec-first, contract-first, spec-as-source-of-truth | specification driven agent development lineage verification |
| D50 | Executable specifications | executable specification, living documentation, specification by example, acceptance-test driven | executable specification traceability implementation verification loop |
| D51 | Formal specification | formal specification, formal methods, Z, TLA+, Alloy, refinement | formal specification refinement traceability implementation evidence |
| D52 | Behavior-driven development | BDD, Gherkin, given-when-then, feature files, scenario-based testing | BDD scenarios requirements traceability runtime verification |
| D53 | Software provenance | software provenance, code provenance, SBOM, supply-chain provenance, SLSA | software provenance decision reasoning artifact lineage |
| D54 | Build provenance | build provenance, reproducible builds, in-toto, attestation, artifact signing | build attestation lineage requirements decision traceability |
| D55 | Artifact lineage | artifact lineage, artifact graph, derivation chain, pipeline lineage | artifact lineage idea decision requirement code test chain |
| D56 | Agentic software engineering | agentic software engineering, AI software agents, autonomous coding, SWE agents, agent-driven development | agentic software engineering knowledge provenance phase context |
| D57 | Coding-agent memory | coding agent memory, repository memory, project memory, codebase knowledge persistence | coding agent persistent memory session knowledge provenance |
| D58 | Cross-session coding agents | cross-session agent, session persistence, context carryover, resumable agents | "cross-session" coding agent context carryover memory architecture |
| D59 | Agent handoff | agent handoff, task handoff, context transfer, delegation protocol, baton passing | agent handoff context package lineage evidence transfer |
| D60 | Agent checkpointing | agent checkpointing, state snapshot, resumption, recovery point, workflow checkpoint | agent checkpoint resume context state provenance |
| D61 | Hierarchical task networks | HTN, hierarchical task network, task decomposition, method decomposition | HTN task decomposition context boundary execution memory |
| D62 | AI planning | AI planning, PDDL, plan representation, plan execution, replanning | AI planning execution monitoring knowledge update replanning |
| D63 | Execution monitoring | execution monitoring, plan monitoring, discrepancy detection, expectation monitoring | plan execution monitoring outcome knowledge revision |
| D64 | Verification and validation | V&V, verification and validation, test evidence, assurance case, safety case | assurance case evidence requirements claims argumentation |
| D65 | Runtime verification | runtime verification, monitor synthesis, temporal-logic monitoring, trace checking | "runtime verification" requirements feedback knowledge base update |
| D66 | Requirements monitoring | requirements monitoring, requirements at runtime, awareness requirements, requirement reflection | requirements monitoring runtime evidence requirement revision loop |
| D67 | Observability-driven development | observability-driven development, telemetry-informed development, production feedback | observability telemetry development decision feedback knowledge |
| D68 | Self-adaptive systems | self-adaptive systems, adaptation logic, managed/managing system, models@runtime | self-adaptive system knowledge model runtime evidence adaptation |
| D69 | MAPE-K | MAPE-K, monitor-analyze-plan-execute, knowledge base loop, autonomic manager | MAPE-K knowledge base development lifecycle integration |
| D70 | Autonomic computing | autonomic computing, self-management, self-configuration, self-healing | autonomic computing knowledge provenance policy evolution |
| D71 | Continuous requirements engineering | continuous RE, just-in-time requirements, agile RE, requirements in DevOps | continuous requirements engineering runtime feedback knowledge |
| D72 | DevOps traceability | DevOps traceability, CI/CD traceability, deployment traceability, release evidence | DevOps traceability commit requirement deployment runtime evidence |

## Reconciliation of the search protocol's 20-domain list

The search protocol (§3) lists 20 research domains; the review instructions list 72. Every one
of the 20 maps onto domains above — none is unsubsumed, so no 73rd row and no deletion:

| Protocol domain (§3) | Subsumed by |
|---|---|
| 1. Knowledge graphs and Semantic Web | D01, D02 |
| 2. Provenance and W3C PROV | D03 |
| 3. Temporal / bi-temporal knowledge graphs | D04, D05 |
| 4. Event sourcing and append-only architectures | D06 |
| 5. Belief revision / AGM theory | D07 |
| 6. Epistemic and doxastic logic | D09, D10 |
| 7. Defeasible reasoning | D11 |
| 8. Computational argumentation | D12 |
| 9. Truth discovery / data fusion | D13, D14 |
| 10. Subjective logic and trust models | D15, D16 |
| 11. Multi-agent belief systems | D17 |
| 12. Scientific discourse representation | D18 |
| 13. Nanopublications / micropublications | D19, D20 |
| 14. Agent memory / long-term memory | D21, D22, D23 |
| 15. RAG and graph-RAG | D24 |
| 16. Human-AI collective intelligence | D25 |
| 17. Decision provenance / decision intelligence | D26, D27 |
| 18. Data lineage and evidence graphs | D28, D29 |
| 19. Temporal databases / event calculus | D30, D31 |
| 20. Knowledge evolution / ontology evolution | D32 |

The protocol's Phase A example queries and its H4 collision examples are carried into the
delegation pack's S sections for the domains they belong to (D07, D12, D13, D21, D26, D06,
D04, D17 and the H4 set), so nothing from the shorter list is lost.
