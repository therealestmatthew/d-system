# Terminology Map — Literature Review Pass 1

draft — Pass 1 in progress

## D01 — Knowledge graphs

| D-System term | Field term | Established by |
|---|---|---|
| Knowledge state (`S = (O, E, L, Content, TemporalScope, Metadata)`) | Knowledge graph entity / triple | Ji, Pan, Cambria, Marttinen, Yu, "A Survey on Knowledge Graphs" (`ji-etal-kg-survey-2021`); Hogan et al., "Knowledge Graphs," ACM CSUR (`hogan-etal-kg-csur-2021`) |
| Lifecycle classification (`L`) | Knowledge graph lifecycle (creation, hosting, curation, deployment) | Simsek, Angele et al., "Knowledge Graph Lifecycle: Building and Maintaining Knowledge Graphs" (`simsek-angele-kg-lifecycle-2021`); Simsek, Umbrich, Fensel, "Towards a Knowledge Graph Lifecycle" (`simsek-umbrich-kg-lifecycle-pipeline-2020`) |
| Epistemic classification (`E`) / epistemic status | Uncertainty management / confidence in knowledge graph construction | "Uncertainty Management in the Construction of Knowledge Graphs: a Survey" (`kg-construction-uncertainty-survey-2024`) |
| Typed transition (`S_t --[T,P]--> S_t+1`) on a knowledge state | Explicit state-transition annotation (draft / under_review / accepted / rejected, no-backward-transition) | US Patent 11,544,323, "Annotations for enterprise knowledge graphs using multiple toolkits" (`uspto-11544323-kg-annotations-patent`) |
| Append-only history of a knowledge state | Versioned edit history of a knowledge graph entity | "Leveraging Wikidata's edit history in knowledge graph refinement tasks" (`wikidata-edit-history-kg-refinement-2022`) |
| Ontological classification (`O`) | Ontology / entity type (RDF/OWL class membership) | Hogan et al., "Knowledge Graphs," ACM CSUR (`hogan-etal-kg-csur-2021`) |
| Explicit epistemic-state node types (claim / open question / partial answer) | Epistemic state graph | "State Representation and Termination for Recursive Reasoning Systems" (`epistemic-state-graph-2026`) — flagged collision candidate against H1 |

## D02 — Semantic Web

| D-System term | Field term | Established by |
|---|---|---|
| Transition provenance attached to a knowledge-state edge | Named graph (statement-level metadata container) | Carroll, Bizer, Hayes, Stickler, "Named Graphs, Provenance and Trust," WWW 2005 (`carroll-etal-named-graphs-provenance-trust-2005`) — the historical ancestor of the whole D02 domain |
| Per-statement epistemic/belief annotation | Reification / singleton property / RDF-star (the three competing statement-level-metadata mechanisms) | Nguyen, Bodenreider, Sheth, "Singleton Property Triples" (`singleton-property-triples-2015`); benchmark comparison of all three (`benchmark-reification-singleton-rdfstar-2021`) |
| Conflicting or unresolved epistemic stance on a claim | Doxastic / Epistemic / Conjectural (DEC) statement classification, grouped into "cognitive worlds" | "Provenance-Enhanced Statements in Knowledge Graphs" (`provenance-enhanced-statements-dec-2026`) — flagged CRITICAL_COLLISION candidate against H1/H3 |
| Belief conflict / disagreement between actors over the same triple | Agnostic / atheistic belief annotation on RDF-star triples | eSPARQL (`esparql-agnostic-atheistic-beliefs-2024`) — flagged CRITICAL_COLLISION candidate against H1/H3 |
| Context package / temporal-scope-bearing container around evidence | Contextualized knowledge graph / provenance-aware knowledge representation | "Provenance-Aware Knowledge Representation: A Survey" (`provenance-aware-kr-survey-2020`) |
| Transition provenance over a knowledge-state update | Dynamic / temporal provenance model for RDF updates | "Dynamic Provenance for SPARQL Update" (`dynamic-provenance-sparql-update-2014`); "Temporal Provenance Model (TPM)" (`temporal-provenance-model-2012`) |

## D03 — W3C PROV / provenance

| D-System term | Field term | Established by |
|---|---|---|
| Typed transition (`T`) between knowledge states | `prov:Activity` | PROV-O, W3C Recommendation (`w3c-prov-o-2013`) |
| Transition provenance (`P`) — derivation, attribution, delegation | `prov:wasDerivedFrom` (derivation), `prov:wasAttributedTo` (attribution), `prov:actedOnBehalfOf` (delegation) | PROV-O (`w3c-prov-o-2013`); PROV-DM (`w3c-prov-dm-2013`); "The rationale of PROV" (`moreau-etal-rationale-of-prov-2015`) |
| Actor / authority | `prov:Agent` | PROV-O (`w3c-prov-o-2013`) |
| Provenance as conflict-resolution input (H3) | Provenance and trust on named graphs | Carroll et al., WWW 2005 (`carroll-etal-named-graphs-provenance-trust-2005`, cross-referenced from D02) |
| Development / agent-action provenance (H7) | Agentic-workflow provenance (agent- and LLM-centric PROV extension) | PROV-AGENT (`prov-agent-2025`) — flagged CRITICAL_COLLISION candidate against H3/H7 |
| Delegation with provenance for agent actions (H3) | Human Delegation Provenance (HDP / HDP-P) | "HDP-P: Human Delegation Provenance for Physical AI Agents" (`hdp-p-physical-ai-agents-2026`) — flagged collision candidate against H3 |
| Versioning / authorship lineage on a knowledge artifact | PAV (Provenance, Authoring, Versioning) ontology | Ciccarese, Soiland-Reyes, Belhajjame, Gray, Goble, Clark, "PAV ontology" (`pav-ontology-2013`) |
| Concrete applied use of transition provenance in a data pipeline | PROV-O used to represent lineage in statistical/record-linkage processes | Cotton, Duffes, Rizzolo (`cotton-etal-provo-lineage-statistical-processes-2019`) |

## D04 — Temporal knowledge graphs

| D-System term | Field term | Established by |
|---|---|---|
| `TemporalScope` component of the knowledge-state tuple | Temporal fact / quadruple `(s,p,o,t)` | TKG completion/representation-learning surveys (`tkg-completion-survey-2022`, `tkg-completion-taxonomy-survey-2023`, `tkg-survey-representation-learning-2024`); Know-Evolve (`know-evolve-tkg-2017`) |
| Typed transition (`T`) carrying a knowledge state forward in time | Time-aware / diachronic embedding of an evolving fact | ChronoR (`chronor-tkg-embedding-2021`); HyTE (`hyte-tkg-embedding-2018`); Diachronic Embedding (`diachronic-embedding-tkg-2020`) |
| Provenance-aware conflict resolution across a transition (H2, H3) | Temporal belief revision over a knowledge base | "A temporal approach to belief revision in knowledge bases," 1994 (`temporal-belief-revision-kb-1994`) — flagged collision candidate |
| Topology-aware context transfer for agent memory retrieval (H1, H2, H5, H6) | Temporally-aware knowledge-graph memory engine with episode / semantic-entity / community subgraph tiers | Zep / Graphiti (`zep-graphiti-temporal-kg-agent-memory-2025`) — flagged CRITICAL_COLLISION candidate; product framing at `getzep-product-blog-tkg-agent-memory` |
| Typed transition generalized beyond a single actor/object pair | Temporal fact generalized to n-ary hyper-relational quadruple-plus-qualifiers | "Temporal Fact Reasoning over Hyper-Relational Knowledge Graphs" (`hyper-relational-tkg-reasoning-2023`) |

## D05 — Bi-temporal systems

| D-System term | Field term | Established by |
|---|---|---|
| `TemporalScope`'s dual clock (assertion time vs. real-world validity) | Valid time / transaction time | Jensen et al. consensus glossaries (`temporal-db-glossary-1994`, `temporal-db-glossary-1992`) |
| Querying a knowledge state as it stood at a past point | As-of query over a system-versioned table | MariaDB System-Versioned Tables (`mariadb-system-versioned-tables-docs`) |
| Epistemic classification (`E`) layered onto `TemporalScope` | Belief time — a proposed third temporal dimension alongside valid time and transaction time | "A Belief-Based Bitemporal Database Model" (`belief-based-bitemporal-db-model-2015`); "Towards Probabilistic Bitemporal Knowledge Graphs" (`probabilistic-bitemporal-kg-2018`); PRISMA-guided bitemporal review (`bitemporal-db-prisma-review-2026`) — flagged collision candidates against H2, H3 |
| Integrated bi-temporal + agent-native + evidence-grounded state model (H1, H2, H5, H6) | Agent-native bi-temporal graph management with validated temporal operators and trace-grounded answer checking | TGMS (`tgms-agent-native-bitemporal-graph-2026`); TRACE (`trace-state-aware-temporal-evidence-graphs-2026`) — flagged CRITICAL_COLLISION candidates |

## D06 — Event sourcing

| D-System term | Field term | Established by |
|---|---|---|
| Append-only history of a knowledge state | Event sourcing — capturing all state changes as a sequence of immutable events | Fowler, "Event Sourcing" (`fowler-event-sourcing-2005`) — the originating description, dated 12 Dec 2005; flagged collision candidate for H2 |
| Typed transition (`T`) recombined into a query-side projection | CQRS (Command Query Responsibility Segregation) | Fowler, "CQRS" (`fowler-cqrs-bliki`) |
| Append-only history with tamper-evident integrity | Authenticated append-only skip list | (`authenticated-append-only-skip-lists-2003`) |
| Event-sourced provenance of agentic development activity (H7, H8, H9) | Event sourcing for autonomous agents in LLM-based software engineering | ESAA (`esaa-event-sourcing-llm-agents-2026`) — flagged collision candidate |
| Append-only, auditable, forkable knowledge-and-execution substrate (H1, H2, H6, H7, H9) | Event-sourced reactive graph serving as the agent's own state | "The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems" (`log-is-the-agent-event-sourced-reactive-graphs-2026`) — flagged CRITICAL_COLLISION candidate, closest title/abstract match to D-System's architecture found across the whole dispatch |
| Event-centric knowledge state bridging D04 and D06 | Event Knowledge Graph (EKG) | EventKG (`eventkg-multilingual-2018`, `eventkg-hub-biographical-timelines-2019`); "What is Event Knowledge Graph: A Survey" (`what-is-event-knowledge-graph-survey-2023`) |

## D30 — Temporal databases

| D-System term | Field term | Established by |
|---|---|---|
| `TemporalScope`'s interval semantics | Allen's interval algebra (before / meets / overlaps / during / …) | Allen, "Maintaining Knowledge about Temporal Intervals," CACM 1983 (`allen-maintaining-knowledge-temporal-intervals-1983`) — the foundational paper for the whole domain |
| Append-only history table, queryable at any past point | History table / system-versioned temporal table, `FOR SYSTEM_TIME AS OF` | Microsoft SQL Server Temporal Tables (`mssql-temporal-tables-docs`); `temporal_tables` PostgreSQL extension (`temporal-tables-nearform-oss-github`) |
| Transition provenance combined with `TemporalScope` (H2, H3) | Update provenance carried through a temporal database | ProvSQL (`provsql-update-provenance-temporal-2025`, `provsql-temporal-features-docs`) — flagged collision candidate |
| Epistemic classification (`E`) layered onto append-only temporal history (H1, H4, H5) | Tri-temporal belief history — a third clock for agent memory, alongside valid time and transaction time | SurrealDB product blog (`surrealdb-tri-temporal-belief-history-blog`) — flagged as a high-priority lead, alongside Zep (D04) and TGMS (D05), of vendors independently converging on a D-System-like design |
| Independence-aware belief-state retrieval (H4, H5) | Structured belief state, precision-aware benchmark for LLM memory retrieval | (`structured-belief-state-llm-memory-benchmark-2026`) |

## D31 — Event calculus

| D-System term | Field term | Established by |
|---|---|---|
| Knowledge state holding at a time-point | Fluent | Shanahan, "The Event Calculus Explained" (`event-calculus-explained-shanahan-1999`) |
| Typed transition triggered by an event and recorded append-only, no deletion (H2) | Event calculus's "narrative" — additions to a knowledge base modeling updates, framed explicitly for "narrative understanding" | Kowalski & Sergot, "A Logic-based Calculus of Events," New Generation Computing 1986 (`kowalski-sergot-logic-based-calculus-events-1986`) — the foundational paper for the whole domain; flagged collision candidate for H2 |
| Ontological classification (`O`)'s ancestor formalism (global states vs. local events) | Situation calculus | McCarthy, "Situation Calculus with Concurrent Events and Narrative" (`mccarthy-situation-calculus-concurrent-events-narrative-2001`) |
| Typed transition as an explicit state-update rule (frame-problem solution) | Fluent calculus's state update axioms | Thielscher, "From situation calculus to fluent calculus" (`thielscher-fluent-calculus-1999`) |
| Epistemic classification (`E`) fused with typed transitions across past/present/future (H1, H2, H3) | Epistemic event calculus — ASP-based reasoning about knowledge of the past, present and future | Ma, Miller, Morgenstern, Patkos, LPAR-19 2014 (`epistemic-event-calculus-asp-2014`) — flagged as the single strongest collision candidate found in this domain |
| Requirement/specification derivation from a reasoning trace (H7, H8, H9) | Event-calculus-plus-answer-set-programming reasoning over model-augmented system requirements | (`event-calculus-requirements-asp-2021`) |

## D07 — Belief revision / AGM theory

| D-System term | Field term | Established by |
|---|---|---|
| Typed transition (`T`) revising a knowledge state | AGM partial meet contraction and revision | Alchourrón, Gärdenfors, Makinson: "On the Logic of Theory Change" (`agm-partial-meet-contraction-revision-1985`) — the paper the whole domain is named for |
| Epistemic classification (`E`) as an ordering over how firmly a belief is held | Epistemic entrenchment | Gärdenfors, Makinson, TARK 1988 (`epistemic-entrenchment-gardenfors-makinson-tark-1988`); Gärdenfors, "Knowledge in Flux" (`gardenfors-knowledge-in-flux-1988`) |
| Typed transition applied repeatedly to the same knowledge state over time | Iterated belief revision/update, Darwiche-Pearl postulates | `darwiche-pearl-postulates-iterated-belief-update-investigation-2023`; `iterated-belief-change-computationally-2022` |
| Typed transition plus provenance packaged as agent infrastructure | AGM belief revision embedded in an LLM-agent runtime | epica (`epica-agm-agent-runtime-oss-github`) — flagged collision candidate |
| Integrated state + typed-transition + provenance model for agent memory (H1, H2, H3, H5) | Formal AGM belief-revision semantics over a graph-native, versioned, provenance-linked memory architecture | `graph-native-cognitive-memory-belief-revision-semantics-2026` — flagged CRITICAL_COLLISION candidate, this domain's closest match |
| Provenance/reliability as an input to whether a transition is accepted (H3, H10) | Reliability-conditional updating with a provenance-capped poisoning defense | `belief-based-agent-memory-reliability-conditional-updating-2026` |
| Provenance-grounded long-term memory for an agent (H3, H5) | Provenance-grounded agent memory | Eywa (`eywa-provenance-grounded-agent-memory-2026`) |
| Provenance as the input arbitrating between conflicting knowledge-state claims (H3) | Belief revision as rational inference | `belief-revision-rational-inference-2002` |

## D08 — Truth maintenance systems

| D-System term | Field term | Established by |
|---|---|---|
| Append-only justification network with retraction and dependency-directed backtracking | (Justification-based) Truth Maintenance System | Doyle, "A Truth Maintenance System" (`doyle-truth-maintenance-system-1979`) — the foundational paper |
| Alternative/counterfactual knowledge states tracked as labelled contexts | Assumption-based Truth Maintenance System (ATMS) | de Kleer, 1986 (`dekleer-assumption-based-tms-1986`, `dekleer-extending-atms-1986`); retrospective in `dekleer-perspective-assumption-based-tms-1993` |
| Epistemic blast-radius when a fact/justification is retracted (H10) | Fact garbage collection in logic-based TMS | `aaai96-fact-garbage-collection-tms` |
| Typed transition's link from truth maintenance to non-monotonic logic (bridges to D11) | Rational reconstruction of nonmonotonic TMS | `rational-reconstruction-nonmonotonic-tms-1990` |
| Incremental change-impact propagation carried from classical TMS into modern KG materialisation (H2, H10) | Incremental Datalog materialisation maintenance | `datalog-materialisations-maintenance-revisited-2019` |
| Multi-agent, distributed provenance network for justification tracking (H3, H5) | Distributed ATMS for scalable reasoning | `distributed-atms-scalable-reasoning` |
| Convergence/independence signal from uncertainty-weighted justifications (H4) | Possibilistic ATMS with data fusion | `possibilistic-atms-data-fusion-2013` |
| Epistemic blast-radius applied to a knowledge structure rather than a fact base (H10) | Axiom pinpointing via ATMS | `axiom-pinpointing-atms` |

## D09 — Epistemic logic

| D-System term | Field term | Established by |
|---|---|---|
| Multi-agent knowledge state with shared/common knowledge | Epistemic logic for distributed systems (S5 knowledge operator, common knowledge) | Halpern, Moses, "Knowledge and Common Knowledge in a Distributed Environment" (`halpern-moses-knowledge-common-knowledge-distributed-1990`) — direct ancestor of D-System's distributed multi-agent framing (H1, H5) |
| Knowledge-classification axioms compared against belief-classification axioms (bridges to D10) | Systems for Knowledge and Belief (S5 vs. KD45) | `systems-for-knowledge-and-belief-1993` |
| Typed transition as an explicit "action model" applied to a multi-agent knowledge state | Dynamic Epistemic Logic (DEL) | van Ditmarsch, van der Hoek, Kooi monograph (`van-ditmarsch-van-der-hoek-kooi-del-monograph-2007`) |
| Deriving/verifying an implementation from a knowledge-based specification (H2, H7, H8) | Knowledge-based program implementation via epistemic model checking | `epistemic-model-checking-kb-program-anonymous-broadcast-2010`; `symbolic-synthesis-kb-program-implementations-synchronous-2013` |
| DEL applied to an actual multi-agent software-agent architecture (H1, H5, H6) | Dynamic-epistemic logic for mobile structured agents | `del-mobile-structured-agents-2012` — this domain's most direct collision hit |
| Formal knowledge state verified against program behavior (H2, H7, H9) | Program semantics and verification for knowledge-based multi-agent systems | `program-semantics-verification-kb-mas-2022` |
| Mature tooling for multi-agent knowledge-state verification (implementation-availability answer against H1, H6) | MCMAS model checker | `mcmas-open-source-model-checker-mas`; `docker-mcmas-oss-github` |

## D10 — Doxastic logic

| D-System term | Field term | Established by |
|---|---|---|
| Belief operator distinct from the knowledge operator, coupled to trust (H3) | Doxastic logic, KD45 | `belief-info-acquisition-trust-mas-modal-logic-2003`; foundational critique in `kd45-is-not-a-doxastic-logic` |
| Multi-dimensional/graded epistemic state (H1) applied to belief rather than binary knowledge | Graded belief / ranking theory | `huber-belief-revision-ii-ranking-theory`; `qualitative-probabilistic-models-full-belief-2017`; `cogwed-computationally-grounded-weighted-doxastic-logic` |
| Convergence/independence hypothesis applied to graded rather than binary belief (H4) | Graded distributed belief | `graded-distributed-belief-2025` |
| Primitive-state-plus-derived-structure architecture (H1): the belief base itself as the ground representation, not a derived possible-worlds structure | Belief bases as the primitive of epistemic/doxastic logic | `rethinking-epistemic-logic-belief-bases-2020` — this domain's strongest collision candidate; precursor `in-praise-of-belief-bases-aaai-2018`; extension `exploiting-belief-bases-rich-epistemic-structures-2019`; originating monograph `hansson-textbook-belief-dynamics-1999` |
| Doxastic/belief-desire structure deployed as actual software agent architecture | BDI (belief-desire-intention) architecture | `uspto-11481658-bdi-multi-agent-architecture-patent`; `wooldridge-logical-modelling-computational-mas-thesis` |
| Belief coupled to justification and revisability (H3) | Revisable justified belief | `revisable-justified-belief-preliminary-report-2015` |
| Belief-base revision integrated into a working non-monotonic reasoning system (bridges to D11) | Belief base revision for answer set programming | `belief-base-revision-unified-asp-2020` |
| Cross-domain anchor bridging belief-change theory to working systems (D07, D08, D10) | Implementation roadmap for belief change | `doyle-to-agm-survey-implementation-roadmap-belief-change-2026` |

## D11 — Defeasible reasoning

| D-System term | Field term | Established by |
|---|---|---|
| Non-monotonic conflict resolution among competing knowledge-state claims (H3) | Defeasible reasoning, defeaters (rebutting/undercutting) | Pollock, "Defeasible Reasoning" (`pollock-defeasible-reasoning-1987`) — this domain's mandated variant terms trace here; surveyed in `sep-defeasible-reasoning-entry`, `epistemic-defeaters-routledge-encyclopedia` |
| Default reasoning and argumentation unified as one abstract conflict-resolution framework (H3) | Assumption-based argumentation (ABA) | `aba-argumentation-theoretic-default-reasoning-1997` |
| Rule/fact knowledge base with conflicting-evidence resolution, the most implemented formalism | Defeasible Logic Programming (DeLP) | `delp-argumentative-approach-garcia-simari-2004`; packaged as server/API in `delp-servers-contextual-queries-explanations-2014`; OSS at `depysible-delp-python-oss-github`, `delores-defeasible-logic-reasoner-oss-github`, `rp-delp-solver-oss-github` |
| Theory-to-implementation anchor: a defeaters framework wired into an actual running reasoner (H2, H7, H8) | OSCAR | `pollock-defeasible-reasoning-oscar-2000` |
| Defeasible reasoning applied directly to a knowledge-graph state model (H1, H2, H3) | Defeasible reasoning with knowledge graphs | `defeasible-reasoning-knowledge-graphs-2023` |
| Provenance itself treated as a defeasible argument for a result's validity (H3) | Evidence graphs: FAIR computation with defeasible reasoning over data, methods and results | `evidence-graphs-fair-computation-defeasible-reasoning-2021` — this domain's strongest collision candidate |
| Defeasible conflict-resolution bridged to epistemic-logic-style knowledge representation (cross-relevant to D09) | Reasoning about knowledge using defeasible logic | `walton-reasoning-about-knowledge-defeasible-logic` |
| Defeasible-conditional semantics connected to a concrete knowledge-base reasoning system | Defeasible conditionals via answer set programming | `defeasible-conditionals-answer-set-programming-2026` |
