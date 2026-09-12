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
