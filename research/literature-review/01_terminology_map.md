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

## D12 — Computational argumentation

| D-System term | Field term | Established by |
|---|---|---|
| Non-monotonic conflict resolution among competing knowledge-state claims (H3) | Abstract argumentation framework (arguments plus attack relation; conflict-free / admissible / complete / preferred / grounded / stable semantics) | Bench-Capon, Dunne, "Argumentation in artificial intelligence," Artificial Intelligence 2007 (`bench-capon-dunne-argumentation-ai-survey-2007`) — the domain's vocabulary-map anchor, covering Dung's framework |
| Rule/preference/defeat machinery deciding whether a transition is accepted (H3) | ASPIC+ structured argumentation | Modgil, Prakken, "The ASPIC+ framework for structured argumentation: a tutorial" (`modgil-prakken-aspicplus-tutorial-2013`) |
| Append-only growth of the argument/knowledge-state graph (H2) | Change in abstract argumentation frameworks via argument addition | `change-abstract-argumentation-frameworks-adding-argument` |
| Evidence attached to individual claims within a conflict-resolution structure, itself possibly unreliable (H3) | Argumentation frameworks with fallible evidence (AAFE) | Skiba, `skiba-argumentation-frameworks-fallible-evidence-2020`; extended in `evidence-retrieval-cost-reduction-argumentation-fallible-evidence-2022` |
| Provenance-weighted conflict resolution propagated through a graph (H3) | Labeled argumentation framework (source-reliability label algebra propagated over the attack graph) | `labeled-argumentation-framework-2015` |
| Evidence combined directly with argumentation-framework structure (H3, H4) | Evidential-based higher-order set argumentation framework | `evidential-higher-order-set-argumentation-framework-2026` |
| Typed-transition provenance generalized to attacks on attacks | AFRA: argumentation framework with recursive attacks | `afra-argumentation-framework-recursive-attacks` |
| Mature tooling answering this domain's implementation-availability question | Dung-style AF semantics solver (conflict-free / admissible / complete / preferred / grounded / stable) | `afsolver-oss-github` |
| Corroborating/reinforcing relation between knowledge states, formalized as independent of and paired with the conflict relation (H3 attack side vs. H4 convergence side) | Bipolar argumentation framework's support relation, paired with and independent of the attack relation | Cayrol, Lagasquie-Schiex, ECSQARU 2005 (`cayrol-lagasquie-schiex-bipolar-argumentation-acceptability-2005`) — the foundational paper pairing attack and support as independent relations, extending Dung's framework already anchored above; applied to explanation-generation in `computing-argumentative-explanations-bipolar-argumentation-2019` and extended to collective multi-argument relations in `splitting-argumentation-frameworks-collective-attacks-supports-2026` |

## D13 — Truth discovery

| D-System term | Field term | Established by |
|---|---|---|
| Source-reliability/authority weighting over conflicting claims | Truth discovery, source-reliability estimation | Li, Gao, Meng, Han, Su, Zhang, SIGKDD Explorations 2016 (`li-etal-truth-discovery-survey-2016`) — the domain's vocabulary-map anchor |
| Conflict resolution among competing knowledge-state claims from multiple providers (H3) | Fact-finding / TruthFinder framework | Yin, Han, Yu, SIGKDD 2007 (`yin-han-yu-truth-discovery-conflicting-providers-2007`) — the foundational fact-finding paper |
| Provenance/copying discount applied to conflicting sources so agreement is not counted as independent (H4) | Copying detection in truth discovery | Dong, Berti-Equille, Srivastava, VLDB 2009 (`dong-berti-equille-srivastava-truth-discovery-copying-detection-2009`) — one shared research lineage with the D14 data-fusion papers by the same authors, not an independent invention |
| Dependence-aware source weighting claimed as a protectable invention (anti-novelty evidence for H4) | Source-dependence patent | `uspto-8190546-dependency-sources-truth-discovery-patent` |
| Claim-level provenance grading modeled on a historical chain-of-narrators methodology (H3, H4) | Isnad-Rijal framework for claim-level provenance in multi-agent knowledge systems | `grading-narrators-isnad-rijal-claim-provenance-2026` — a striking direct collision |
| Current retrieval-augmented conflict resolution with explicit source-credibility incorporation | Automated fact-checking over conflicting evidence | `resolving-conflicting-evidence-automated-factchecking-2025` |
| Mature tooling answering this domain's implementation-availability question | truthdiscovery OSS library (multiple algorithms) | `truthdiscovery-oss-github` |

## D14 — Data fusion

| D-System term | Field term | Established by |
|---|---|---|
| Conflicting-claims resolution across database records (H3) — **terminology homonym**: this is *not* the sensor/signal-fusion sense of "data fusion" (autonomous-vehicle, remote-sensing and bioinformatics fusion are an unrelated field sharing only the name) | "Data fusion" in the conflicting-claims / record-integration sense | Dong, Berti-Equille, Srivastava, VLDB 2009 (`dong-berti-equille-srivastava-data-fusion-resolving-conflicts-2009`); homonym collision documented at ledger row `LIT-01-S153` (ten off-topic sensor/bio hits returned by the bare query) |
| Dependence-aware discounting of copying/correlated sources as a convergence input (H4) | Source-dependence-aware fusion (DEPEN Bayesian model; correlation-aware fusion) | One shared Dong/Berti-Equille/Srivastava research programme, not independent inventions: `integrating-conflicting-data-role-source-dependence-2009`, `fusing-data-with-correlations`, `scaling-up-copy-detection`, `sailing-information-ocean-source-dependence-2009`, with `domain-aware-multitruth-fusion-copy-based-authority-2022` as a later derivative |
| Independent-vs-derivative evidence discount, from a structurally distinct tradition converging on the same H4 concern | Dempster-Shafer contextual / rank-correlation discounting of dependent evidence | `fusion-dependent-evidence-rank-correlation-2017`; `contextual-discounting-belief-functions-theory` |
| Conflict resolution over graph-structured / linked knowledge state | Linked-data conflict resolution and fusion tooling | `linked-data-integration-conflicts`; `ld-fusiontool-oss-github` |
| Current trajectory toward learned, non-hand-coded conflict resolution | LLM-era end-to-end data integration | `automatic-end-to-end-data-integration-llm-2026` |

## D15 — Subjective logic

| D-System term | Field term | Established by |
|---|---|---|
| Epistemic classification (`E`) as a graded (belief, disbelief, uncertainty) state rather than a binary one | Subjective logic's opinion triangle and uncertainty mass | Josang, "Subjective Logic: A Formalism for Reasoning Under Uncertainty," Springer 2016 (`josang-subjective-logic-book-2016`) — the field's authoritative reference |
| Convergence/corroboration operator combining multiple sources' epistemic states (H4) | Subjective-logic fusion/discount operator family | `multi-source-fusion-operations-subjective-logic`; `subjective-logic-operators-trust-assessment-empirical-2014` |
| Provenance-weighted trust propagated over a graph of actors (H3) | Trust network analysis with subjective logic, over directed series-parallel graphs | Josang, Hayward, Pope, ACSC 2006 (`josang-hayward-pope-trust-network-analysis-subjective-logic-2006`) — this domain's strongest collision candidate |
| Source-reliability and evidence combined directly in one mechanism (H3) | Collaborative assessment of information-provider reliability and expertise using subjective logic | `collaborative-assessment-information-provider-reliability-sl-2011` |
| An adversarial counterpoint to the fusion-operator mechanism itself, appropriate to this campaign's own adversarial stance | "Can We Trust Subjective Logic For Information Fusion?" | `can-we-trust-subjective-logic-information-fusion` |
| Trust discount propagated along a provenance/referral path (H3, H4) | Subjective-logic trust discount for referral paths | `subjective-logic-trust-discount-referral-paths-2024` |
| Agentic knowledge verification framed directly as a confidence algebra (H1, H3) | trustandverify OSS implementation | `trustandverify-oss-github` |

## D16 — Trust and reputation systems

| D-System term | Field term | Established by |
|---|---|---|
| Domain-specific epistemic authority weighting trust propagation (H3) — **terminology homonym**: this is *not* Moz/SEO's "Domain Authority" ranking metric, an unrelated marketing-analytics measure sharing only the name | "Domain authority" in the epistemic-authority-over-a-graph sense | `domain-aware-trust-network-extraction-propagation-2016`; homonym collision documented at ledger row `LIT-01-S168` (BrightEdge SEO blog, excluded as a lead only) |
| Graph-based transitivity underlying provenance-weighted trust propagation (H3) | Trust transitivity in social networks (A trusts B, B trusts C, therefore A partially trusts C) | `trust-transitivity-social-networks` |
| Web-of-trust mechanism claimed as protectable IP (anti-novelty evidence for H3) | Distributed web-of-trust provisioning patent | `uspto-9866392-distributed-web-of-trust-patent` |
| Claim/evidence/actor primitives formalized as one of several named categories of inter-agent trust (H3) | Six-category inter-agent trust model: Brief, Claim, Proof, Stake, Reputation, Constraint | `inter-agent-trust-models-comparative-study-2025` — a striking direct collision with D-System's own primitive vocabulary |
| Multi-dimensional (not scalar) domain/topic-authority-aware propagation across agents (H3, H5) | TrustFlow topic-aware vector reputation propagation | `trustflow-topic-aware-reputation-propagation-2026` |
| Claim-level trust scoring propagated through a retrieval pipeline (H3) | ClaimTrust propagation scoring for retrieval-augmented generation | `claimtrust-propagation-trust-scoring-rag-2025` |
| Domain-authority-weighted epistemic reasoning for an autonomous knowledge system (H3) | Bayesian epistemology with weighted authority | `bayesian-epistemology-weighted-authority-2026` |
| Backward-traceability of trust/accountability through a system (H9) | Enforcing trust accountability with backward propagation | `enforcing-trust-accountability-backward-propagation-2026` |

## D17 — Multi-agent belief systems

| D-System term | Field term | Established by |
|---|---|---|
| Ground, primitive belief representation as the base of a multi-agent epistemic architecture (H1) — **terminology homonym**: this is *not* the POMDP/reinforcement-learning "belief state" sense, which dominated eight of ten hits on the bare query | "Belief base" in the knowledge-representation/epistemic-logic sense | `base-based-model-checking-multiagent-only-believing`; cross-referenced against D10's `rethinking-epistemic-logic-belief-bases-2020`; homonym collision documented at ledger row `LIT-01-S181` |
| Multiple agents' beliefs combined into one shared knowledge state (H1, H4) | Modal logic framework for multi-agent belief fusion | `modal-logic-framework-multiagent-belief-fusion` |
| Two named but formally distinct mechanisms for reconciling the same underlying multi-agent conflict | Belief merging versus judgment aggregation | Stanford Encyclopedia of Philosophy (`sep-belief-merging-judgment-aggregation-entry`); direct comparison in `everaere-belief-merging-vs-judgment-aggregation-2015` |
| Credibility-weighted merging of multiple agents' knowledge-state claims (H3) | Credibility accrual over existential-rules programs in multi-agent contexts | `merging-existential-rules-credibility-accrual-2020` |
| Belief, evidence and trust unified in one multi-agent representational framework (H3, H4) | Reasoning about belief, evidence and trust in a multi-agent setting | `reasoning-belief-evidence-trust-multiagent-setting` — this domain's strongest collision candidate |
| Append-only sequence of typed transitions over a shared belief state (H2) | Handling sequences of belief change in a multi-agent context | `handling-sequences-belief-change-multiagent-context` |
| Versioned, append-only agent-system state treated as a merge target | Semantic merging of versions of BDI agent systems | `semantic-merging-versions-bdi-agent-systems` |
| Independence-aware convergence applied to the agents themselves, not just their claims (H4) | Epistemic Sybil resistance — not letting derivative/duplicated agents count as independent confirmation | `epistemic-sybil-resistance-multiplying-agents-2026` — the multi-agent-AI analog of D13/D14's copying detection |
| Multi-agent epistemic planning explicitly over inconsistent beliefs, trust and deception (H3, H4) | Multi-agent epistemic planning with inconsistent beliefs, trust and lies | `multiagent-epistemic-planning-inconsistent-beliefs-trust-lies` |

## H4 — Independence-aware convergence (cross-domain)

Collision searches for H4 (independent reasoning/evidence paths arriving at equivalent states strengthen
epistemic weight; derivative agreement is discounted), logged under `domain_id: H4` rather than a `D`-numbered
research domain. Included here as its own section because the searches span multiple established fields
rather than mapping onto one.

| D-System term | Field term | Established by |
|---|---|---|
| H4 itself: independent paths converging on a claim strengthen it; derivative agreement does not (H4) | Corroboration via provenance patterns — confirmation/witness patterns derived across abstraction levels to estimate a claim's reliability from other sources' reports | Barakat, TaPP 2017 (`barakat-corroboration-provenance-patterns-tapp2017`) — the single most directly on-topic paper this entire campaign has produced for H4 |
| Provenance directly informing whether an aggregate claim should be believed (H3, H4) | Digital provenance's interpretation / verification / corroboration triad | `digital-provenance-interpretation-verification-corroboration-2005` |
| H4's own thesis restated in the literature's own words: agreement alone is not corroboration without provenance-aware independence | Provenance-conserving multi-view fusion, distinguishing agreement from corroboration | `not-all-agreement-counts-as-corroboration-2026` |
| Confidence propagated jointly with provenance over a knowledge graph (H3, H4) | Provenance of query-result probabilities in uncertain knowledge graphs | `computing-maintaining-provenance-query-result-probabilities-ukg` |
| Philosophical grounding for why independence, not mere multiplicity, confers epistemic weight | Robustness and independent evidence (philosophy of science) | Schupbach, Philosophy of Science 2017 (`schupbach-robustness-independent-evidence-2017`) |
| Independent/dependent evidential relations formalized within a probabilistic-argumentation graph, bridging to D12 | Epistemic graphs | `hunter-thimm-epistemic-graphs` |
| Temporal/evolving-information dimension combined with multi-agent provenance for convergence (H2, H4) | Chronology of multi-agent interactions for provenance of evolving information | `chronology-multiagent-interactions-provenance-evolving-info` |

## D18 — Scientific discourse representation

| D-System term | Field term | Established by |
|---|---|---|
| Claim / hypothesis / evidence primitives linked by typed relationships (H1, H3) | HypER (Hypotheses, Evidence and Relationships) approach | de Waard, Schneider, CEUR-WS Vol-523, ISWC 2009 SWASD workshop (`hyper-scientific-knowledge-claims-2009`) — the anchor this domain's mandated variants trace to |
| Discourse-element ontological classification (`O`) of a passage (background / hypothesis / method / result / conclusion) | Discourse Elements Ontology (DEO) | sparontologies.github.io canonical spec (`deo-discourse-elements-ontology-spec`); implementation at `deo-oss-github`; standards-track W3C-adjacent counterpart in biomedicine, SWAN (`swan-biomedical-discourse-ontology-2008`, `w3c-hcls-swan-ontology-note`) |
| Claim + evidence + provenance + argumentative-relation unified in one representation (H1, H3) | Reasoning and Discourse Ontology (RDO), introduced by the SEE paper | `see-reasoning-discourse-ontology-2014` |
| Epistemic classification (`E`) of a hypothesis as a confidence-weighted state, not binary (H1) | HELO (HypothEsis and Law Ontology) — hypotheses/models/laws/conclusions linked to probability of truth | `helo-representation-research-hypotheses`; extended in `representation-probabilistic-scientific-knowledge` |
| Typed transition (`T`) as a citation edge between claims, forming a network (H2, H4) | Typed claim network | `typed-claim-network-scientific-literature` |
| Evidence lineage / evidence-type classification attached to a conclusion (H3) | Evidence and Conclusion Ontology (ECO) | OBO Foundry registry (`eco-evidence-conclusion-ontology-obo-registry`); community-standard papers `eco-nucleic-acids-research-standard-paper`, `eco-go-annotations-protocol-chapter` |
| Provenance-based corroboration/certainty grading of a knowledge-state link, outside the scientific-publishing domain proper (H3, H4) | Evidential-link grading and corroboration for intelligence analysis (patent family) | `uspto-9472115-grading-ontological-links-certainty-patent`; `uspto-11244113-evidential-links-corroboration-patent` — access-limited: assessed from search-snippet text only, patent PDFs not machine-readable |
| Vocabulary-map anchor surveying claim/evidence/provenance ontologies as one field (Phase A) | Survey of 23 assertion, evidence and provenance ontologies | `bridging-scientific-knowledge-gap-reproducibility-survey-2025` |
| Rhetorical/document-structure annotation of a paper's own claims, tied to authoring tooling (H1) | SALT (Semantically Annotated LaTeX) and its LaTeX-annotation descendants | `salt-semantically-annotated-latex-2007`; `scikgtex-latex-annotation-2023`; `seal-semantically-enriched-latex-authoring-2022` |

## D19 — Nanopublications

| D-System term | Field term | Established by |
|---|---|---|
| Knowledge state packaged as content + provenance + publication-metadata, separated into three graphs (H1) | Nanopublication anatomy (assertion / provenance / publication-info graphs) | Groth, Gibson, Velterop, 2010 (`anatomy-of-a-nanopublication-2010`) — the foundational paper for the whole domain |
| Append-only, content-addressed, immutable identifier for a knowledge unit (H2) | Trusty URIs | Kuhn, Dumontier, ESWC 2014 (`trusty-uris-kuhn-dumontier-2014`); journal extension `trusty-uris-verifiable-reliable-tkde-2015` |
| Independence-aware convergence via a dedicated component tracking supporting/conflicting evidence bodies behind an assertion (H3, H4) | Proposed fourth nanopublication component: knowledge provenance | `extending-nanopublications-knowledge-provenance` — a direct, explicit collision arising inside the nanopublication model itself |
| Decentralized, actor-run publishing architecture for knowledge units, without a central publisher (H5, H6) | Decentralized nanopublication server network; "publishing without publishers" | `decentralized-provenance-aware-nanopublication-publishing`; `nanopub-server-oss-github`; `nanopub-services-oss-github`; `publishing-without-publishers-decentralized-dissemination` |
| Underspecified or unresolved epistemic status attached to an assertion (H1) | Underspecified scientific claims in nanopublications | `underspecified-scientific-claims-nanopublications` |
| Community-run de facto specification standing in for a ratified standard (reuse candidate) | nanopub.org guidelines — no dedicated W3C Recommendation governs nanopublications specifically | `nanopublication-guidelines-spec` |
| Provenance model designed specifically for an assertion-bearing knowledge unit, distinct from the assertion itself (H3) | Supporting nanopublication provenance | `supporting-nanopublication-provenance-2011` — an early companion to the founding anatomy paper, not an independent invention |
| Assertion-level knowledge unit generalized into an explicit claim network (bridges to D20) (H1, H4) | Nanopublication-based claim networks | `physician-suicide-claims-nanopublications-claim-networks-2022` |

## D20 — Micropublications

Nine Pass 1 searches in this domain resolved to only five distinct kept sources, with eight of the nine
rows (`LIT-01-S217`–`LIT-01-S225`, excepting the rate-limited `LIT-01-S224`) converging on the same
canonical paper. Recorded here rather than silently collapsed: per the protocol's stop conditions (§12),
a late-search duplicate rate this high is itself evidence of domain saturation, not merely a small
literature.

| D-System term | Field term | Established by |
|---|---|---|
| Claim + evidence + argument + annotation semantic model with statement-level citation and transitive evidence-chain closure (H1, H2, H3) | Micropublications | Clark, Ciccarese, Mitchell, 2014 (`micropublications-semantic-model-claims-evidence-2014`) — the founding paper for three of this domain's four mandated variants at once |
| Claim / contribution / named-entity network laid over the Linked Open Data cloud (H1, H4) | Semantic representation of scientific literature | `semantic-representation-scientific-literature-claims-lod-2015` — an earlier system in the same claim-network lineage as D18's typed claim network |
| Implementation-standard vocabulary counterpart to the conceptual claim/evidence model (reuse candidate) | Micropublication OWL vocabulary (mp) | `micropublication-owl-vocabulary-mp` |
| Applied domain-specific implementation of the model for evidence synthesis (H3) | DIKB-Micropublication (drug-drug interaction evidence) | `dikb-micropublication-oss-github` |
| Incentivized community curation extending the model to unpublished/negative data (H6) | Micropublication for community curation | `micropublication-incentivizing-community-curation-2018` |

## D28 — Data lineage

| D-System term | Field term | Established by |
|---|---|---|
| Provenance classification taxonomy (why-recorded / what's-described / how-represented / dissemination) applied to a knowledge state's transition history | Data provenance taxonomy in e-science | Simmhan, Plale, Gannon survey (`data-provenance-survey-simmhan-2005`) — the domain's vocabulary-map anchor, its classification dimensions directly paralleling D-System's own state/transition/provenance primitives |
| Backward traceability from a derived artifact to its upstream sources (H9) | Data lineage / lineage tracing | Cui, Widom, Wiener, the founding "data lineage" paper (`tracing-lineage-view-data-warehousing-2000`); second canonical survey (`lineage-retrieval-scientific-data-survey-2005`) |
| Provenance combined algebraically as it propagates through a chain of transitions (H2, H3) | Provenance semirings — provenance as a semiring-annotated (k-relation) algebra over query operators | Green, Karvounarakis, Tannen, PODS 2007 (`provenance-semirings-pods-2007`) — this domain's strongest theoretical collision candidate |
| Epistemic blast-radius: a changed upstream knowledge state propagating to every dependent downstream artifact (H10) | Upstream/downstream impact analysis over a data-lineage graph | confirmed as established industrial framing across this domain's Phase E collision searches (vendor tooling only; no independent academic mechanism found beyond the lineage-graph systems below) |
| Standardized, cross-platform event model for an append-only transition history (H2, H7) | OpenLineage run/job/dataset lineage-event standard | `openlineage-standard-oss-github` — the domain's standards-tier anchor, playing a role analogous to PROV-O's in D03 |
| Development/agentic provenance applied to tracing training-data ancestry through an ML pipeline (H7) | Multi-agent data-lineage uncovering for post-training LLM data | `tracing-roots-multiagent-data-lineage-llm-2026` — the closest match in this domain to D-System's own agentic framing of lineage |
| Provenance/lineage as an input directly enforcing downstream policy compliance (H3) | Lineage-grounded policy enforcement ("Honest Computing") | `honest-computing-lineage-policy-enforcement-2024` |
| Formal reconstruction of a lineage graph from an unannotated system (H9) | Theoretical model for data-lineage reconstruction | `theoretical-model-data-lineage-reconstruction-2020` |
| Ontological classification layered directly onto a lineage graph (bridges to D32) | Relational-database data-lineage ontology | `relational-db-data-lineage-ontology-2026` — flagged for this dispatch's own D28/D32 cross-check |

## D29 — Evidence graphs

Two compound terms in this domain are homonyms across independent traditions, surfaced across
`LIT-01-S241`–`LIT-01-S254`; per Block C's rule against treating a terminology difference as a
mechanism difference (and its converse, never treating a shared name as a shared mechanism), each
sense is recorded on its own row rather than merged. Six senses total: three of "evidence graph,"
three of "evidence network." Pass 1 records the homonymy only; which tradition, if any, shares
D-System's actual mechanism is for `phase-lit-04`'s deep reading to decide.

| D-System term | Field term | Established by |
|---|---|---|
| Evidence combined into a graph structure feeding a confidence/inference outcome — **homonym sense 1 of 3** ("evidence graph"): network forensics | Evidence graph (forensic-analysis sense) | Building Evidence Graphs for Network Forensics Analysis, ACSAC 2005 (`building-evidence-graphs-network-forensics-2005`) — the founding paper of this sense; later forensics-tradition derivatives (attack-graph mapping, vulnerability reasoning) are the same lineage, not independent inventions |
| Evidence combined into a graph structure feeding a confidence/inference outcome — **homonym sense 2 of 3** ("evidence graph"): fact-verification NLP | Evidence graph (graph-based evidence aggregation and reasoning for claim verification) | GEAR, ACL 2019 (`gear-graph-evidence-aggregating-reasoning-fact-verification-2019`) — primary lineage; Evidence-aware Fake News Detection with GNNs, 2022 (`evidence-aware-fake-news-detection-gnn-2022`) is a derivative application of the same mechanism, not an independent second invention |
| Evidence combined into a graph structure feeding a confidence/inference outcome — **homonym sense 3 of 3** ("evidence graph"): FAIR-computation / defeasible reasoning | Evidence graphs: transparent, FAIR computation with defeasible reasoning over data, methods and results | bioRxiv paper (`evidence-graphs-fair-computation-defeasible-reasoning-2021`) — already inventoried under D11 (found_by `LIT-01-S134`, flagged there as a critical-collision candidate); re-confirmed as the same source from this domain's own sweep at `LIT-01-S251`, not re-added to the inventory per dedup discipline |
| Graded (belief/disbelief/uncertainty) epistemic state combined across sources — **homonym sense 1 of 3** ("evidence network"): colloquial Bayesian-belief-network usage | "Evidence network" (Bayesian-belief-network colloquialism) | no single anchor paper — homonym collision documented at ledger row `LIT-01-S242` (generic Bayesian-network tutorial/encyclopedic material and industrial patents, no evidence-graph-specific mechanism beyond standard BN inference) |
| Independent bodies of evidence combined into one confidence estimate across a federation of sources — **homonym sense 2 of 3** ("evidence network"): network meta-analysis / health technology assessment | Evidence network (network meta-analysis: the graph of direct/indirect treatment comparisons across clinical trials) | no source kept — homonym collision documented at ledger row `LIT-01-S245`; an established, independent second meaning confirmed by methods/guidance literature for clinical-trial evidence synthesis specifically, not a general-purpose evidence-graph mechanism |
| Provenance-linked evidence marshaled toward a conclusion, with actor/testimony reliability as an explicit factor (H3, H4) — **homonym sense 3 of 3** ("evidence network"): Wigmore/Schum legal-evidence marshaling | Evidence network / inference network (Wigmore's chart method, extended by Schum into probabilistic inference networks for legal/forensic evidence marshaling) | Schum, "Inference Networks and the Evaluation of Evidence: Alternative Analyses" (`schum-inference-networks-evaluation-evidence-2013`) — a decades-old, independently-developed tradition, this domain's strongest collision candidate for D-System's evidence/provenance/corroboration primitives taken together |
| Confidence combined from multiple heterogeneous evidences attached to a knowledge-graph triple (H4) | Triple confidence measurement with multiple heterogeneous evidences | `triple-confidence-measurement-kg-heterogeneous-evidences-2024` |
| Evidence-graph confidence recursively propagated from parent to child through a DAG of provenance-weighted edges (H3, H4) | Feed-forward probabilistic graphical model over an evidence graph, confidence propagation | US Patent 10,445,654 (`uspto-10445654-feedforward-evidence-graph-confidence-patent`) — an explicit patent claim on essentially the same mechanism as D-System's H3/H4, per this domain's own collision-search rationale |
| Independent-source confidence combination formalized outside any graph structure, from a wholly separate field (H4) | Propagating imprecision: combining confidence intervals from independent sources (frequentist statistics) | `propagating-imprecision-confidence-intervals-independent-sources-2011` |
| Belief-function combination across evidence from multiple sources, historically prior to today's KG-confidence literature (H3, H4) | Dempster-Shafer evidential reasoning | `metaprobability-dempster-shafer-evidential-reasoning-2013` |

## D32 — Ontology evolution

| D-System term | Field term | Established by |
|---|---|---|
| Epistemic blast-radius: propagating a changed knowledge state to every dependent element (H10) | Ontology evolution — "the consistent management and propagation of changes to dependent elements" | Flouris, Manakanatas, Kondylakis, Plexousakis, Antoniou, classification and survey, Knowledge Engineering Review 2008 (`ontology-change-classification-survey-flouris-2008`) — the domain's vocabulary-map anchor, its own definition echoing D-System's H10 almost verbatim |
| Append-only, queryable history of every change applied to a knowledge structure (H2) | Version log for ontology change detection | Plessers, De Troyer, ISWC 2005 (`ontology-change-detection-version-log-plessers-2005`) — a version-log mechanism directly structurally paralleling D-System's own append-only knowledge-state history |
| Typed transition applied to a shared conceptual schema, historically prior to the ontology-specific literature (bridges to D28) | Schema evolution | Roddick's founding annotated bibliography, ACM SIGMOD Record 1992 (`schema-evolution-annotated-bibliography-roddick-1992`); this domain's own contrast paper (`ontology-evolution-not-same-schema-evolution-2004`) argues the two are distinct problems despite the shared "evolution" vocabulary |
| Typed transition (`T`) classified into a taxonomy of recurring change types (H2) | Change patterns in ontology change management | `ontology-change-management-change-patterns-2013` |
| Epistemic blast-radius reconciling a user-driven change against dependent instance data (H10) | User-driven ontology evolution management | Motik, Maedche, Volz, 2002 (`user-driven-ontology-evolution-management-motik-2002`) |
| Declarative language specifying and propagating a knowledge-structure change to dependent artifacts (H10) | KGCL — a change language for ontologies and knowledge graphs | `change-language-ontologies-knowledge-graphs-kgcl-2024` — the domain's strongest recent systems match for change-propagation-to-dependents |
| Coordinated versioning discipline across many mutually-dependent knowledge structures at once (H6, H10) | The OBO Foundry — coordinated evolution of ontologies to support biomedical data integration | `obo-foundry-coordinated-ontology-evolution-2007` — this domain's strongest architecture-level collision candidate, a real-world federation of dependent-ontology coordination |
| Typed transition explicitly bridged to formal belief-revision operators over a knowledge structure (H1, H2) | On belief change and ontology evolution | `belief-change-ontology-evolution-dissertation-2006` — an explicit theoretical bridge between the D07 (AGM) and D32 traditions |
| Ontological classification drifting continuously rather than through discrete versioned changes (H1) | Semantic concept drift over an ontology stream | Chen, Lecue, IJCAI 2017 (`learning-ontology-streams-semantic-concept-drift-2017`) — bridges the ML "concept drift" sense to the ontology-evolution sense, contrasted against the general ML definition (`what-is-concept-drift-how-to-measure-2010`) to keep the two vocabulary senses distinct |
| Mature tooling answering this domain's implementation-availability question | Protege — the field's dominant open-source ontology editor and substrate for change-management extensions | `protege-oss-github` |

## D21 — Agent memory

| D-System term | Field term | Established by |
|---|---|---|
| Memory interpretation via transition lineage (architecture.md Sec.7): working state vs. persistent knowledge | Cognitive architecture's working-memory buffer vs. declarative/procedural long-term memory | Rosenbloom, Laird, Newell, Soar founding paper, 1991 (`soar-preliminary-analysis-1991`); An Analysis and Comparison of ACT-R and Soar (`analysis-comparison-act-r-soar-2022`); A Standard Model of the Mind (`standard-model-of-the-mind-2017`) — this domain's mandated "cognitive architecture (SOAR, ACT-R)" vocabulary source |
| Same working/long-term split carried into a language-agent architecture | Cognitive Architectures for Language Agents (CoALA) | Sumers, Yao, Narasimhan, Griffiths (`coala-cognitive-architectures-language-agents-2023`) — the well-known SOAR/ACT-R-to-LLM-agent bridge paper |
| Multi-dimensional state model (H1) applied empirically to memory structures | Empirical taxonomy of agent-memory structures | Anatomy of Agentic Memory (`anatomy-of-agentic-memory-2026`) |
| Memory-stream state plus a reflection-based consolidation transition (H1, H2) | Memory stream / reflection | Park, O'Brien, Cai, Morris, Liang, Bernstein, Generative Agents, UIST 2023 (`generative-agents-interactive-simulacra-2023`) — the founding source for D22's own "memory stream"/"reflection" mandated variants, kept here under its UIST DOI and cross-referenced from D22 per S1's explicit cross-domain flag (domain_ids `D21; D22`) |
| Typed transition (`T`) plus provenance combined into a bitemporal contradiction-resolution algebra (H2, H3) | Bitemporal operator algebra with K-semiring provenance and confidence | TOKI (`toki-bitemporal-operator-algebra-contradiction-2026`) — flagged collision candidate, structurally close to D-System's transition+provenance model |
| Provenance as conflict-resolution input via reliability-conditioned updating rather than naive overwrite (H3) | Reliability-conditional updating with a provenance-capped poisoning defense | `belief-based-agent-memory-reliability-conditional-updating-2026-d21-recur` (duplicate of the D07 canonical row `belief-based-agent-memory-reliability-conditional-updating-2026`) — flagged collision candidate |
| Epistemic classification (`E`) maintained under incomplete observation (H1, H3) | Belief memory under partial observability, explicit belief state | Belief Memory (`belief-memory-partial-observability-2026`) — flagged collision candidate |
| Typed-transition/append-only state model (H2) | Formal AGM belief-revision semantics over a graph-native, versioned memory architecture | `graph-native-cognitive-memory-belief-revision-semantics-2026-d21-recur` (duplicate of the D07 canonical row) — this domain's strongest collision candidate, "structurally near-identical" per S1's own extraction |
| Multi-dimensional state model naming a gap D-System claims to fill (H1) | Four-layer Knowledge / Memory / Wisdom / Intelligence decomposition with distinct persistence semantics per layer | The Missing Knowledge Layer in Cognitive Architectures for AI Agents (`missing-knowledge-layer-cognitive-architectures-2026`) — names the CoALA/JEPA-era gap in exactly the dimension D-System claims to fill |
| Development provenance and convergence applied to the field's own lineage (H4, H7) | Mechanism-level review of lineage, convergence and migration gaps from cognitive architectures to language agents | `cognitive-architectures-to-language-agents-review-2026` |
| Working/long-term memory tiering as commodity OSS infrastructure | redis/agent-memory-server — working-memory events promoted in the background to long-term storage | `redis-agent-memory-server-oss-github` |

## D22 — Long-term memory for LLM agents

| D-System term | Field term | Established by |
|---|---|---|
| Tiered state representation between active and archival storage | MemGPT-style paging — OS-virtual-memory analogy (main context / recall storage / archival storage) | Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez, MemGPT (`memgpt-llms-as-operating-systems-2023`) — the founding paper for this domain's own "MemGPT-style paging" mandated variant |
| Same paging concept elevated to peer-reviewed / OS-branded system status | Memory OS of AI Agent; AIOS: LLM Agent Operating System | `memory-os-of-ai-agent-emnlp-2025`; `aios-llm-agent-operating-system-2024` |
| Vocabulary-map anchor for this domain (Phase A, peer-reviewed) | A Survey on the Memory Mechanism of Large Language Model-based Agents | Zhang, Dai, Bo, Ma, Li, Chen, Zhu, Dong, Wen, ACM TOIS 2025 (`survey-memory-mechanism-llm-agents-toi-2025`) |
| Typed transition (`T`) plus provenance almost exactly matching D-System's own framing (H2, H3) | Typed memory representation mitigating provenance-role collapse | `mitigating-provenance-role-collapse-typed-memory-2026` — this domain's strongest collision candidate |
| Ontological/epistemic/lifecycle state model with typed provenance transitions (H1, H2, H3, H5) | Provenance graph with immutable evidence roots, beliefs as derived/annotated nodes | Eywa: `eywa-provenance-grounded-agent-memory-2026-d22-recur` (duplicate of the D07 canonical row `eywa-provenance-grounded-agent-memory-2026`) |
| Provenance/evidence-lineage vocabulary spanning four hypotheses at once (H3, H7, H9, H11) | Evidence tracing and execution provenance in LLM agents | From Agent Traces to Trust survey (`agent-traces-to-trust-evidence-provenance-survey-2026`) |
| Per-item origin/timestamp/evidence-pointer provenance under an anti-fabrication guarantee (H3) | "Citation lock" provenance-aware long-term memory | Agent Zero Memory (`agent-zero-memory-provenance-aware-2026`) |
| Runtime-to-knowledge closure (H11) applied to agent memory | Experience extraction closing a feedback loop into insight governance | `closing-feedback-loop-insight-governance-verbal-rl-2026` |
| Independence-aware belief-state retrieval (H4, H5) | Structured belief state, first precision-aware benchmark for LLM memory retrieval | `structured-belief-state-llm-memory-benchmark-2026-d22-recur` (duplicate of the D30 canonical row `structured-belief-state-llm-memory-benchmark-2026`) — collision_candidate disagreement between the two independent Pass 1 readings (D30: no: D22 here: yes, per S1's framing as one of "five direct H2/H3/H5 collision candidates") preserved rather than resolved |
| Retrieval/context-model choice between raw and extracted representations | Verbatim chunks vs. extracted artifacts, controlled ablation | `verbatim-chunks-beat-extracted-artifacts-ablation-2026` — also relevant to D24's chunking variant |

## D23 — Episodic memory

D-System's own architecture notes leave open "should D-System distinguish episodic and semantic memory?"
(`research/architecture/terminology_investigation.md` Sec. "Memory vs. Knowledge") without resolving it.
This domain's field literature has debated the analogous distinction since Tulving 1972 without resolving
it either — recorded here as a genuine open question shared across both traditions, not a collision.

| D-System term | Field term | Established by |
|---|---|---|
| D-System's own open question of episodic-vs-semantic state classification (H1) | Tulving's founding episodic/semantic distinction (1972) and its subsequent revisions | Renoult, Rugg, historical perspective, Neuropsychologia 2020 (`renoult-rugg-historical-perspective-tulving-2020`); The History of Episodic Memory, Phil Trans R Soc B 2024 (`history-of-episodic-memory-phil-trans-2024`) |
| Typed transition (`T`) boundary marking where one knowledge-state episode ends and the next begins (H1, H2) | Event Segmentation Theory — perceptual/memory event boundaries at points of prediction failure | Zacks, Tversky, Event Structure in Perception and Conception, Psychological Bulletin 2001 (`zacks-tversky-event-structure-perception-conception-2001`) — the domain's founding paper; Kurby, Zacks review, Trends in Cognitive Sciences 2008 (`kurby-zacks-segmentation-perception-memory-events-2008`) |
| Formal/computational model of the same transition-boundary mechanism | Computational model of event segmentation from perceptual prediction | Reynolds, Zacks, Braver, Cognitive Science 2007 (`reynolds-zacks-braver-computational-model-event-segmentation-2007`) |
| Transition-boundary detection reframed around prediction error, paralleling D-System's own transition/surprise-adjacent framing (H2) | Prediction error and event segmentation in episodic memory | `prediction-error-event-segmentation-episodic-memory-2024` |
| Consolidation (phase_context_contract.md Sec.4) rediscovered under a different name | Experience replay in reinforcement learning | Systematic review, Neurocomputing 2026 (`experience-replay-rl-systematic-review-neurocomputing-2026`); cross-tradition bridge to hippocampal replay (`learning-offline-memory-replay-biological-artificial-rl-2021`) |
| Consolidation carried into the LLM-agent lifelong-learning setting | Lifelong Learning of LLM-based Agents: A Roadmap | `lifelong-learning-llm-agents-roadmap-2025` |
| Topology-aware context transfer (H5): Bayesian-surprise event boundaries plus two-stage similarity-and-temporal-contiguity retrieval, explicitly modeled on human episodic recall | EM-LLM | Fountas et al., Human-inspired Episodic Memory for Infinite Context LLMs (`em-llm-human-inspired-episodic-memory-infinite-context-2024`); official implementation (`em-llm-model-oss-github`) — this domain's strongest collision candidate, and the direct computational implementation of the Event Segmentation Theory row above |
| Same surprise-based event-boundary mechanism, operationalized independently of EM-LLM | nemori (LLM-powered boundary detection with transitional masking); embers-diaries (time-gap / tag-shift / tag-rarity "surprise" grouping) | `nemori-oss-github`; `embers-diaries-oss-github` |
| What counts as "truly episodic" retrieval versus familiarity-based retrieval — bearing on how strictly D-System's own episodic claims should be read | Hippocampal activation dissociating episodic from familiarity-based retrieval | `hippocampus-truly-episodic-memories-retrieval-2012` |
| Clinical/diagnostic vocabulary distinguishing episodic from semantic autobiographical memory | Episodic and Semantic Autobiographical Memory in Mild Cognitive Impairment, systematic review | `episodic-semantic-am-mci-systematic-review-2023` |

## D24 — RAG / Graph-RAG

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor and founding paper for this domain's own name | Retrieval-augmented generation (RAG) | Lewis et al., NeurIPS 2020 (`lewis-rag-knowledge-intensive-nlp-2020`) — the paper the domain's own mandated name traces to, the same founding-paper-as-domain-name pattern as D06 (Fowler/event sourcing) and D19 (Groth/Gibson/Velterop/nanopublications) |
| Knowledge transfer / retrieval primitive (architecture.md Sec.9) richer than nearest-neighbor search, already the subject of a filed claim (anti-novelty evidence for H0) | "Retrieval-augmented generation for large language models" | US Patent 12,517,941 (`uspto-rag-large-language-models-patent`) |
| Graph-topology-aware retrieval founding this domain's own second mandated name | GraphRAG — local-to-global community summarization (Leiden community detection over an LLM-extracted entity/claim graph) | Edge et al., Microsoft Research (`edge-et-al-graphrag-local-to-global-2024`) — the direct source of "GraphRAG" |
| Topology-aware context transfer (H5) combined with provenance/evidence/reasoning lineage inside a graph-retrieval pipeline (H3, H5, H9) | "Evidence Demands" expanded through graph retrieval while explicitly preserving demand-passage provenance | LineageRAG (`lineagerag-2026`) — the strongest collision candidate found across this dispatch's four domains |
| Graph-topology retrieval combined directly with development/requirement provenance (H7, H9) | Graph-RAG and prompt engineering for automated requirement traceability and compliance checking | `graphrag-prompt-engineering-requirement-traceability-2024` |
| Provenance and traceability as first-class knowledge-graph properties, reached from the formal-ontology tradition rather than the GraphRAG/LLM tradition (H3, H4, H7, H9) | Full Traceability and Provenance for Knowledge Graphs | Dibowski, FOIS 2024 (`dibowski-full-traceability-provenance-kg-fois-2024`) — independent cross-tradition convergence on the same problem, evidence against treating either tradition as sole prior art |
| Reasoning-aware retrieval relevant to topology-aware context transfer (H5) | Neurosymbolic retrievers; graph-LLM-agent integration for reasoning and retrieval | `neurosymbolic-retrievers-rag-2026`; `integrating-graphs-llms-agents-reasoning-retrieval-2026` |
| Context assembly / chunking — this domain's own mandated variant terms | Query-adaptive semantic chunking; domain-oriented controlled-RAG design | `query-adaptive-semantic-chunking-rag-2026`; `dcd-domain-oriented-design-controlled-rag-2026` |
| Hybrid retrieval — this domain's own mandated variant term | HybridRAG — knowledge-graph and vector retrieval integrated explicitly | `hybridrag-2024` |
| Ecosystem consolidation around the graph-topology-retrieval pattern as commodity tooling | microsoft/graphrag (official reference implementation, now maintenance-mode); hkuds/lightrag (EMNLP 2025-backed lightweight alternative) | `microsoft-graphrag-oss-github`; `hkuds-lightrag-oss-github` |

## D25 — Human-AI collective intelligence

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor for multi-agent/human-agent shared cognition (H6) | Collective intelligence — the empirically-measured "c factor" for group performance | Woolley, Chabris, Pentland, Hashmi, Malone, Science 2010 (`woolley-evidence-collective-intelligence-factor-2010`); narrative synthesis, Woolley, Aggarwal, Malone, Current Directions in Psychological Science 2015 (`woolley-aggarwal-malone-collective-intelligence-group-performance-2015`) |
| Second vocabulary-map anchor: human-agent collaboration (architecture.md's actor model) formalized as a design taxonomy | Hybrid intelligence — Dellermann et al.'s taxonomy of design knowledge for human-AI systems, and the field's canonical definitional paper | `dellermann-taxonomy-design-knowledge-hybrid-intelligence-2019`; `dellermann-hybrid-intelligence-bise-2019` |
| Same human-agent collaboration space, a second, independently-constructed taxonomy cross-checking the first | Human-AI interaction-pattern taxonomy (systematic review, AI-assisted decision making) | `human-ai-interaction-patterns-taxonomy-systematic-review-2024` |
| Human-agent knowledge curation with an authority/review step (H3, H6) | "Human-in-the-loop knowledge curation" — an applied term-of-art confirmed across independent domains (biological knowledgebases; clinical-trial data stewardship), not one paper's coinage | `human-in-the-loop-knowledge-curation-biological-knowledgebase-2026`; `human-in-the-loop-knowledge-curation-clinical-trial-2026` |
| Typed transition (H1, H2) combined with argumentation-style belief update, surfaced inside a named "hybrid intelligence" venue | Hypothesis updating by combining knowledge graphs and argumentation | `hypothesis-updating-knowledge-graphs-argumentation-2024` — flagged collision candidate |
| Shared human-AI knowledge base with capture and provenance attribution, but no conflict-resolution mechanism (H3, H6) | claude-collective-intelligence — SessionEnd-hook knowledge capture with git-based team sync | `ideaflowco-claude-collective-intelligence-oss-github` — falsification-relevant per its own first-hand inspection (`LIT-02-S059`): real capture+attribution overlap, explicit gap on authority/conflict-resolution, downgraded from an initial collision-candidate flag to a data point on what is *not* yet solved in this domain |
| Human-AI knowledge-base co-evolution modeled as an end-to-end ecosystem (H6) | OmniScientist — co-evolving ecosystem of human and AI scientists | `omniscientist-coevolving-ecosystem-human-ai-scientists-2026` — flagged collision candidate |
| Same co-evolution space, an agency/dimensions/dynamics framing | Cognitio Emergens — agency, dimensions and dynamics in human-AI knowledge co-creation | `cognitio-emergens-human-ai-knowledge-cocreation-2025` — flagged collision candidate |
| Knowledge-base co-evolution modeled as a feedback dynamical system (H11) | Dynamics of Human-AI Collective Knowledge on the Web — archive quality / model skill / human skill / query volume fitted to Wikipedia's pre/post-ChatGPT knowledge flow | `dynamics-human-ai-collective-knowledge-web-2026` — this domain's strongest collision candidate, the closest field analog to D-System's own feedback-to-knowledge mechanism |
| Name collision noted, not a mechanism match | "Open Collective" (a crowdfunding platform) shares only the word "collective" with this domain's collective-intelligence vocabulary | no source kept — name-only collision noted at ledger row `LIT-02-S057`, per the campaign's shared-name-is-not-shared-mechanism discipline |

## D26 — Decision provenance

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor and founding paper for this domain's own name (H3, H7) | Decision provenance — "harnessing data flow for accountable systems," exposing the decision pipeline (inputs to, and flow-on effects from, automated decisions) | Singh, Cobbe, Norval, IEEE Access 2019 (`singh-cobbe-norval-decision-provenance-accountable-systems-2019`) — the field's foundational, most-cited decision-provenance paper; flagged collision candidate |
| Same decision-provenance lineage extended into a new application domain, not an independent confirmation (methodology Sec.12 independence rule) | Towards an accountable Internet of Things: a call for reviewability | `towards-accountable-iot-reviewability-2021` |
| Append-only ledger recording a decision's inputs/policy-checks/outcome (H2, H3) — this domain's own mandated "decision trace" variant | "Decision trace" — implemented as a real, active OSS project (Context/Evidence/Logic/Outcome fields; no explicit typed-transition or state-machine semantics found) | `logicoflife-decision-trace-oss-github` (first-hand inspected at `LIT-02-S075`); corroborated independently by a second, simpler tool, `luciferforge-ai-trace-oss-github` |
| PROV-O extended specifically to model decisions and their causes (H2, H3) — this domain's own mandated "PROV for decisions" variant | DecPROV — an ontology extending PROV-O, derived from the W3C Decisions and Decision-Making Incubator Group's "Decision Ontology (DO)"; explicit limitation: cannot represent normative/future decisions, only already-made ones — a point of difference from D-System's forward-looking decision primitives | Car, MODSIM2017 (`car-decprov-modsim2017-2017`, flagged collision candidate); GitHub source `nicholascar-decprov-ont-oss-github`; canonical spec `decprov-ontology-spec-promsns`; peer-reviewed application `case-based-reasoning-decprov-decision-support-2019` |
| The general PROV-O standard itself, recurring outside its home domain | PROV-O: The PROV Ontology | already inventoried as `w3c-prov-o-2013` under D03 (`LIT-01-S009`); recurs here at `LIT-02-S068` as the expected cross-phase adjacency (D26 borders phase-lit-01's D03/D28 sweeps) — the domain-specific finding is DecPROV, above, not the general standard, recorded as `w3c-prov-o-2013-d26-recur` rather than re-kept |
| Single-author decision-governance-evidence research programme spanning six preprints (H1, H2, H3, H7) — recorded as one primary lineage plus derivative/extension papers, never six independent inventions (methodology Sec.12; the campaign's own derivative_ancestor discipline) | Decision Trace Schema / Decision Event Schema (DES); Governed Auditable Decisioning Under Uncertainty; Decision Evidence Maturity Model (DEMM); Property-Level Reconstructability of Agent Decisions; Verify-Gated Completion (a packetized state model with context shaping, memory ownership rules, and decision traces) | Solozobov, six arXiv preprints Jan-Jun 2026, authorship/lineage confirmed at `LIT-02-S081`: `solozobov-decision-trace-schema-governance-evidence-2026`, `solozobov-governed-auditable-decisioning-uncertainty-2026`, `solozobov-decision-evidence-maturity-model-2026`, and two priority reads flagged for the deep-read phase, `solozobov-property-level-reconstructability-agent-decisions-2026` and `solozobov-verify-gated-completion-admission-control-2026` (architecturally closest to D-System's own state/transition/provenance framing, H1/H2); the sixth preprint, DEMM-Bench (arxiv:2606.20634), was reviewed as the lineage's benchmark companion but not separately kept |
| Architecture decisions combined with knowledge-graph traceability and cross-architecture impact analysis (bridges to D39/D40) | Architecture Knowledge Graphs — a next step in architecture knowledge management | `architecture-knowledge-graphs-workshop-paper` — flagged collision candidate, spanning decision, specification and knowledge-update stages at once |
| Decision/change provenance recorded on a knowledge graph at triple granularity, a concrete technical mechanism (H2, H3) | KAPPS — knowledge-based CPPS architecture for the circular factory, provenance via SPARQL UPDATE | `kapps-knowledge-based-cpps-circular-factory-2026` — flagged collision candidate |
| Ontology explicitly for decision-provenance-quality assessment in executive decision-making, an independent cross-tradition corroboration of DecPROV | Assessing Knowledge Provenance Quality for CEO Decision Support: an OWL-DL ontological framework | `assessing-knowledge-provenance-quality-ceo-decision-support-eckm` — a D26xD27 crossover per its own framing |
| Provenance/accountability reached via a structurally different trust mechanism (blockchain consensus/immutability, not D-System's actor/authority model) | A blockchain-based approach for data accountability and provenance tracking | `blockchain-data-accountability-provenance-tracking-2017` — a contrast case, not a structural match |
| Vendor self-declared "standard" with no independent adoption found | VeritasChain's "Verifiable AI Provenance (VAP)" framework | no source kept — vendor self-promotion (Medium posts, a self-hosted spec page, paid press-release syndication), IETF/ISO standardization stated as pursued but not achieved; excluded at ledger row `LIT-02-S076` per campaign discipline against treating vendor content as evidence |
| Recurring vendor-content operation running equivalent SEO copy under multiple decision-related keywords across two domains | elixirdata.co — "decision trace" / "decision lineage" / "SOC decision-traceability infrastructure" / "ontology for AI agents" blog posts | no source kept — vendor blog content excluded at ledger rows `LIT-02-S079`, `LIT-02-S080` and `LIT-02-S092` (the last of these explicitly names it "the clearest single instance in this dispatch of one vendor operation inflating apparent prior art across multiple mandated variants and domains") |

## D27 — Decision intelligence

D27's five mandated variants split sharply on academic grounding: DMN carries real peer-reviewed
literature and a mature multi-vendor OSS ecosystem, while "decision intelligence" and "decision
automation" returned zero peer-reviewed anchors across web search, OpenAlex and Semantic Scholar
(`LIT-02-S082`, `LIT-02-S086`, `LIT-02-S087`) — recorded here as an honestly thin sub-domain, not
smoothed over by vendor material or manufactured rows.

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor for this domain's most academically-grounded variant (H2, H3) | DMN — Decision Model and Notation, OMG standard | `dmn-omg-standard-spec` — a decade of active revision (versions 1.0 through 1.7-beta found); by a wide margin the strongest academic anchor of this domain's five mandated variants; flagged collision candidate |
| DMN's own expression language, this domain's own mandated variant term | FEEL — Friendly Enough Expression Language | established by the OMG DMN standard itself (`dmn-omg-standard-spec`), per ledger row `LIT-02-S084` |
| Alternative decision-modeling methodology contrasted against DMN | TDM — The Decision Model (von Halle & Goldberg) | no source kept — named only in a practitioner comparison article (ModernAnalyst) excluded as practitioner content at `LIT-02-S084` |
| Market-positioning rename of the same product category — this domain's own vendor-vocabulary hazard | DMS — Decision Management Systems, positioned by vendor marketing as BRMS's successor ("Business Rules Management Systems are out, Decision Management Systems are in") | no source kept — named only in vendor blog content (sapiens.com) excluded at `LIT-02-S086`; added to this domain's term set despite the source itself carrying no evidentiary weight |
| Formal peer-reviewed treatment of decision logic embedded in business-process models (H2) | Formal Model of Business Processes Integrated with Business Rules | `formal-model-business-processes-business-rules-2018`; deepened by an independent University of Queensland doctoral thesis on the same integration theme, `uq-thesis-business-processes-business-rules-2017` |
| DMN combined with process-mining / object-centric process data (H5, H9) | Extracting process-aware decision models from object-centric process data | `extracting-process-aware-decision-models-2024` |
| DMN structuring and constraining LLM behavior, bridging to D-System's own agent-governance concerns (H3; cross-relevant to D25) | DMN-Guided Prompting — a framework for controlling LLM behavior | `dmn-guided-prompting-llm-behavior-2025` |
| Mature multi-vendor, cross-language OSS ecosystem establishing DMN as a real, multiply-implemented interoperable standard (source-priority tier 6) | jdmn (Goldman Sachs' own Java DMN engine); camunda-engine-dmn (BPM-vendor engine); dmn-tck/tck (cross-vendor conformance test suite); pyDMNrules (independent Python implementation) | `goldmansachs-jdmn-oss-github`; `camunda-engine-dmn-oss-github`; `dmn-tck-oss-github`; `pydmnrules-oss-github` |
| Named-term disambiguation: this domain's own "decision records" (business-rules/decision-table capture) checked against D40's Architecture Decision Records | "Decision records" — decision-table capture from business rules, not architectural rationale records | `business-rules-capture-decision-processing-patent` (representative patent-form data point) — zero hits conflating the two terms found at ledger row `LIT-02-S085`; the two domains do not collide on this term |
| This domain's two market-discourse-only mandated variants, recorded as a genuine gap rather than papered over | "Decision intelligence" (Gartner-popularized market category, attributed by secondary sources to Google's 2018 "Decision Intelligence Engineering" function under Cassie Kozyrkov, with an earlier claimed 1994 James G. March coinage); "decision automation" (vendor/BRMS-vs-DMS market discourse) | no peer-reviewed or standards anchor found for either term across three providers — three explicit zero-yield ledger rows, `LIT-02-S082`, `LIT-02-S086`, `LIT-02-S087` |
| Direct patent-form usage of the exact mandated "decision intelligence" term, distinct from Gartner/Kozyrkov market discourse | "Decision intelligence system and method" | `decision-intelligence-system-method-patent` — a real prior-art data point despite the term's absence from peer-reviewed literature |
| "X intelligence" framing bridging to requirements engineering (cross-relevant to D34-D36) | Requirements Intelligence with OpenReq Analytics (EU OpenReq project) | `requirements-intelligence-openreq-analytics-2019` |

## D33 — Requirements engineering

| D-System term | Field term | Established by |
|---|---|---|
| `Idea -> Reasoning -> Decision -> Requirement -> Specification` (lifecycle stages) | Requirements engineering process: elicitation, modelling and analysis, communication, agreement, evolution | Nuseibeh, Easterbrook: "Requirements Engineering: A Roadmap," ACM FOSE 2000 (`nuseibeh-easterbrook-re-roadmap-2000`) — the field's most-cited framing and this domain's primary Phase A anchor |
| `Requirement` / `Specification` lifecycle boundary, tracked institutionally rather than ad hoc | Elicitation, specification, validation, management as named lifecycle stages | ISO/IEC/IEEE 29148:2018, "Systems and software engineering — Life cycle processes — Requirements engineering" (`iso-iec-ieee-29148-2018`) — the standing standard defining the BRS/StRS/OpsCon/SyRS/SRS document family; flagged collision candidate as the domain's single most authoritative vocabulary anchor |
| Typed transition (`T`) applied to a requirement, with formal derivation semantics | Goal refinement (KAOS: goal decomposition into sub-goals/requirements via formal refinement patterns) | Darimont, van Lamsweerde: "Formal Refinement Patterns for Goal-Driven Requirements Elaboration," 1996 (`darimont-lamsweerde-formal-refinement-patterns-1996`); van Lamsweerde: "Goal-oriented requirements engineering: a guided tour," ISRE 2001 (`lamsweerde-gore-guided-tour-2001`) — the canonical KAOS methodology paper, flagged collision candidate |
| Actor / strategic-dependency modelling underlying requirement derivation | i* framework — strategic actors, goals, dependencies in early-phase requirements | Yu: "Towards modelling and reasoning support for early-phase requirements engineering," ISRE 1997 (`yu-early-phase-re-modelling-reasoning-1997`) — the original i* paper; compared directly against KAOS at WER'09 (`werneck-etal-comparing-gore-frameworks-2009`) |
| Assumption revision as a trigger for requirement-level knowledge update (H7, H9) | Requirements evolution driven by invalidated assumptions in a goal model | Ali, Dalpiaz, Giorgini, Silva Souza: "Requirements Evolution: From Assumptions to Reality," 2011 (`ali-etal-requirements-evolution-assumptions-reality-2011`) — flagged collision candidate; empirically corroborated by "How Do Requirements Evolve During Elicitation?" (`how-requirements-evolve-during-elicitation-2022`) |
| Machine-checked requirement with linked metadata, an industrial `Specification` implementation | TRLC ("Treat Requirements Like Code") — BMW domain-specific language for requirements-as-code with cross-artifact linkage | `trlc-bmw-oss-github` — industrial (automotive-grade) OSS evidence that requirement specification and cross-artifact linkage are already formalized outside D-System |
| Requirement provenance/history at the repository level, an industrial `Requirement` implementation | Bi-directional synchronization between a requirements repository and textual requirement documents | US Patent 8,117,539 (`uspto-8117539-bidirectional-trace-sync-patent`) — flagged collision candidate, direct industrial prior art for keeping a requirement's canonical record and its rendered document in sync |
| GenAI/LLM applied across the full elicitation-to-validation lifecycle (thesis-adjacent, cross-relevant to H7/H8) | Generative AI for Requirements Engineering | Systematic literature review, 2024 (`genai-for-re-slr-2024`) — a meta-survey, not itself a mechanism; useful as a map of where the field's own agentic-RE literature currently sits |

## D34 — Requirements traceability

| D-System term | Field term | Established by |
|---|---|---|
| Bidirectional epistemic traceability (H9) | Forward traceability / backward traceability; trace links | Gotel, Finkelstein: "An analysis of the requirements traceability problem," ICRE 1994 (`gotel-finkelstein-traceability-problem-1994`) — the foundational pre-RS/post-RS distinction, this domain's single most important Phase A anchor; restated as a state-of-the-field keynote at SANER 2019 (`forward-backward-traceability-keynote-2019`) |
| Development provenance link-typing (H7) | Four canonical trace-link types (reference model) | Ramesh, Jarke: "Toward Reference Models for Requirements Traceability," IEEE TSE 2001 (`ramesh-jarke-reference-models-traceability-2001`) — three-year practitioner study, a second primary Phase A anchor independent of Gotel/Finkelstein |
| `RTM` as D-System might casually call a trace view | Requirements Traceability Matrix (RTM) | No academic anchor found under this exact acronym — S3's own search (`LIT-02-S117`) found RTM reads as industry/compliance vocabulary layered onto the academic "trace link" concept; the field's own grounding is Ramesh & Jarke's link-type taxonomy and Gotel & Finkelstein's forward/backward definition, not "RTM" itself |
| Context package / knowledge-to-code lineage, tool-independent interchange | ReqIF — OMG Requirements Interchange Format | `reqif-omg-spec-1-2` — decade-old industrial practice (originating from the German automotive HIS consortium) for structured, tool-independent trace-link interchange |
| Knowledge-to-code lineage as a maintained OSS mechanism | Eclipse Capra — user-definable traceability metamodel linking arbitrary artefacts (models, code, issue-tracker tasks), with change-impact-analysis use | `eclipse-capra-oss-github` |
| LLM/agent reasoning constructing evidence links between artifacts (H7, H9) — the sharpest, most current collision cluster in this dispatch | Automated requirements traceability / traceability link recovery (TLR) via LLM prompt engineering and RAG | TraceLLM, kept under both its preprint and published-journal identifiers (`tracellm-2026-preprint`, `tracellm-2026`); LiSSA (`lissa-generic-tlr-rag-2025`); R2Code (`r2code-self-reflective-req-to-code-traceability-2026`); "Who's Who?" architecture-entity-recognition traceability (`whos-who-llm-traceability-architecture-entity-recognition-2025`); all flagged collision candidates |
| Provenance-aware conflict resolution over trace links (H3, H9) | Confidence-calibrated / trust-aware knowledge graphs for software-artifact traceability | "Trust-Aware Multi-Agent Traceability" (`trust-aware-multiagent-traceability-2026`); "Embedding Traceability in Large Language Model Code Generation" ACM FSE 2025 (`embedding-traceability-llm-codegen-fse-2025`); both flagged collision candidates |
| Execution/reasoning provenance for agent-based work generally (cross-relevant to D22, already inventoried there) | Evidence tracing and execution provenance in LLM agents | "From Agent Traces to Trust" survey, 2026 — cross-phase duplicate of `agent-traces-to-trust-evidence-provenance-survey-2026` (D22); recorded under D34 as `agent-traces-to-trust-evidence-provenance-survey-2026-d34-recur` per dedup discipline |
| Field's own forward-looking statement of what remains unsolved in traceability (bears on this whole domain's open-questions framing) | CoEST Grand Challenge of Traceability (2007, 2012, 2017 "Next Ten Years") | Cleland-Huang et al., `cleland-huang-traceability-trends-future-directions-fose-2014`; `grand-challenge-traceability-v1-2012`; `grand-challenges-traceability-next-ten-years-2017` |

## D35 — Requirements provenance

**Negative vocabulary finding, recorded plainly rather than smoothed over:** "requirements provenance" is
**not established RE vocabulary as an exact composite phrase.** S3's dedicated search on the mandated
variant (`LIT-02-S136`) returned almost no RE-specific literature — results were dominated by biomedical
workflow provenance, generic data/supply-chain/IoT provenance vendor content, and an off-topic pharma
preprint. The field instead uses "origin," "rationale," and "traceability" as separate terms (S137–S139),
never fused into "requirements provenance" itself. This is treated here as a genuine gap, not mapped to a
near-neighbour field term that would imply the phrase is in use when it is not.

A second, narrower vocabulary collision was found for the domain's "stakeholder attribution" variant
(`LIT-02-S139`): the exact phrase collides heavily with tax law's constructive-ownership rules and academic-
publishing authorship ethics, not RE literature. The field's own term for the underlying concept is
"viewpoints" or "stakeholder roles."

| D-System term | Field term | Established by |
|---|---|---|
| Reasoning/decision provenance behind a requirement (H7) — the domain's true Phase A anchor, standing in for the absent exact phrase above | Rationale capture — REMAP (an IBIS-based process-knowledge model preserving alternatives, arguments and decisions behind a requirement) | Ramesh, Dhar: "Supporting systems development by capturing deliberations during requirements engineering," IEEE TSE 1992 (`ramesh-dhar-remap-rationale-capture-1992`) — flagged collision candidate, closely paralleling D-System's own reasoning → decision → requirement lifecycle stages; extended to change propagation (bridging to D36) at `ramesh-dhar-remap-change-propagation-1993` |
| A second, independent rationale-capture mechanism, negotiation-flavoured | WinWin — captures win conditions, issues, options and agreements during stakeholder negotiation | Boehm, Kitapci: "The WinWin Approach: Using a Requirements Negotiation Tool for Rationale Capture and Use" (`boehm-kitapci-winwin-rationale-capture`) — addresses both rationale capture and stakeholder attribution |
| Stakeholder viewpoint as an attribution unit on a requirement | Viewpoints framework for requirements definition | `stakeholder-viewpoints-requirements-definition-1996` |
| Requirement origin tied to a structured elicitation-source taxonomy, not just "a stakeholder said so" | Taxonomy of elicitation information sources | `stakeholders-only-source-elicitation-taxonomy-2016` |
| D-System's own combination (knowledge graph + LLM + provenance + software/requirements traceability) attempted end-to-end — the strongest single collision found in this dispatch | ProvTracer — PROV-O- and Basic-Formal-Ontology-based system automating software traceability via knowledge graph + LLM synergy | Procko, "On the Provenance of Software Systems: Automating Software Traceability with Knowledge Graph and Large Language Model Synergy," ERAU doctoral dissertation, 2025 (`procko-provtracer-erau-dissertation-2025`) — flagged collision candidate |
| Rigorous non-software definition of provenance-for-traceability, an outside-the-field cross-check | Metrological traceability | `provenance-metrological-traceability-2025` |
| Formal-ontology treatment of the same KG+traceability+provenance combination the ERAU dissertation attempts computationally (cross-relevant to D24, already inventoried there) | Full traceability and provenance for knowledge graphs | Dibowski, FOIS 2024 — cross-phase duplicate of `dibowski-full-traceability-provenance-kg-fois-2024` (D24); recorded under D35 as `dibowski-full-traceability-provenance-kg-fois-2024-d35-recur` per dedup discipline |
| Rationale recovered post-hoc from ordinary development artifacts, an alternative to D-System's explicit-capture assumption | Rationale mining from communication channels (commit/email/chat archives) | `rationale-mining-oss-email-archives-2021`; `rationale-mining-dev-chat-messages-2017` |
| Non-repudiable attribution applied to a decision-lineage record (H3) | Non-repudiable provenance for clinical decision support | `non-repudiable-provenance-clinical-decision-support-2020` — flagged collision candidate, a directly transferable non-repudiation/attribution mechanism from a decision-support (not RE) domain |

## D36 — Requirements evolution

**Sharpest terminology finding of this dispatch, requiring precise handling:** "blast radius" — the exact
term D-System's own H10 hypothesis is named after ("epistemic blast-radius analysis") — has independently
become live industry vocabulary for AI-coding-agent change impact (`LIT-02-S163`; reportedly reaching
mainstream usage via an Amazon internal memo, March 2026, describing AI-linked production incidents as
"high blast radius"). Two genuine arXiv papers use the exact term and are kept as evidence of its currency
(`blast-radius-agentic-coding-memory-2026`, `beyond-code-generation-agentic-sdlc-2026`) — **but their
mechanisms diverge from H10 rather than colliding with it.** `blast-radius-agentic-coding-memory-2026` is
LLM context/token-window management (reversible context eviction to cut token consumption), not epistemic
or requirements-change impact propagation. `beyond-code-generation-agentic-sdlc-2026` uses "high-blast-
radius changes" as an SDLC triage category reserving expert review, closer in spirit to change-impact
assessment but still not H10's dependency-propagation mechanism. Both are scored and flagged accordingly
(`collision_candidate: no`, low component/architecture prescores) precisely so that a shared name does not
inflate this domain's prior-art count in the direction that flatters H0 — the same discipline `LIT-02 X1`
applied in declining to map Baddeley's "Episodic Buffer" onto a D-System term on name alone.

| D-System term | Field term | Established by |
|---|---|---|
| Requirement instability treated as intrinsic to development rather than an engineering defect — this domain's foundational anchor | The change and evolution of requirements as a challenge to the practice of software engineering | Harker, Eason, Dobson, ISRE 1993 (`harker-eason-dobson-requirements-change-evolution-1993`) — the single most important Phase A anchor; this domain, unlike D35's "requirements provenance," is thoroughly and explicitly named and studied as its own sub-field |
| A `Requirement`'s measurable rate of change over the lifecycle | Requirements volatility (measurement) | Nurmuliani, Zowghi, Powell, ASWEC 2004 (`nurmuliani-zowghi-requirements-volatility-aswec-2004`) — canonical empirical volatility-measurement study; tracked institutionally at `nasa-swehb-swe-200-requirements-volatility-metrics` |
| Structured process governing a `Requirement`'s post-baseline modification | Requirements change management | Systematic review, Information and Software Technology 2018 (`re-change-management-systematic-review-2018`) |
| Epistemic blast-radius analysis (H10) — direct, non-diverging articulation of the gap H10 claims to address | Semantically-seeded, graph-propagated impact analysis across software artifacts, naming the blind spots of both semantic-only and structural-only impact tools | `semantically-seeded-graph-propagated-impact-analysis-vision-2026` — the closest non-"blast-radius" match to H10 found in this dispatch |
| Industrial `T` (typed transition) propagating a requirement change to downstream artifacts | Change-request impact analysis / requirements-management semantics modeling | US Patent 9,202,188 (`uspto-9202188-change-request-impact-analysis-patent`); US Patent 7,373,343 (`uspto-7373343-requirements-management-semantics-patent`); both flagged collision candidates as direct industrial prior art for H10 |
| Cross-domain resurfacing of items first kept under D33/D35, confirming this domain's proximity to goal-oriented RE and rationale capture | "Requirements Evolution: From Assumptions to Reality" (D33); "How Do Requirements Evolve During Elicitation?" (D33); "Managing inconsistencies in an evolving specification" (D33); REMAP's change-propagation chapter (D35) | `ali-etal-requirements-evolution-assumptions-reality-2011-d36-recur`; `how-requirements-evolve-during-elicitation-2022-d36-recur`; `gotel-finkelstein-managing-inconsistencies-evolving-spec-1995-d36-recur`; `ramesh-dhar-remap-change-propagation-1993-d36-recur` |

## D37 — Design rationale

D37 opens a six-domain lineage (D37 design rationale &rarr; D38 architecture rationale &rarr; D39
architecture knowledge management &rarr; D40 Architecture Decision Records) that runs, decade by
decade, from general design theory into today's git-native ADR practice. D-System's own
decision/rationale apparatus sits at the end of a traceable, 55-year vocabulary lineage, not outside
it.

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor and this domain's own taxonomy of itself (H7, H9) | Design rationale — the field's own survey structure: approaches, representation, capture and retrieval | Regli, Hu, Atwood, Sun, Engineering with Computers 2000 (`regli-hu-atwood-sun-design-rationale-survey-2000`), authorship independently verified rather than assumed from memory (`LIT-02-S173`); the field's second, earlier Phase A survey is Jarczyk, Loffler, Shipman, HICSS 1992 (`jarczyk-loffler-shipman-design-rationale-se-survey-1992`) |
| Foundational concepts/techniques/use text underlying D-System's own decision+rationale pairing | Design Rationale: Concepts, Techniques, and Use | Moran, Carroll (eds.), Lawrence Erlbaum 1996, cited via its 2020 Routledge reissue DOI (`moran-carroll-design-rationale-concepts-techniques-use-1996`) — the same reissue volume recurs at D42's QOC founding paper |
| Cost/benefit analysis of capturing reasoning behind a decision — directly bears on whether D-System's own argumentation/decision apparatus repeats a known tradeoff | Argumentation-based design rationale: what use at what cost? | Buckingham Shum, Hammond, IJHCS 1994 (`buckingham-shum-hammond-argumentation-based-design-rationale-1994`) — same Buckingham Shum authorship lineage spanning D35 (`hypermedia-argumentation-based-rationale-2005`) and D41 (Compendium), tracked as one research program rather than independent confirmations (methodology Sec.12) |
| DR capture tooling, this domain's own mandated "DR capture" variant and the strongest reuse-recommendation candidate in D37 | DRed (Design Rationale editor) — a two-decade-mature, commercially-adopted capture tool built directly on IBIS | Bracewell, Ahmed, Wallace, ASME DETC 2004 (`bracewell-ahmed-wallace-dred-design-folders-detc-2004`); extended in Bracewell, Wallace, Moss, Knott, Computer-Aided Design 2009 (`bracewell-wallace-moss-knott-capturing-design-rationale-2009`) — both flagged collision candidates; a five-year conference-then-journal lineage, not two independent tools |
| The field's own two edited-volume self-consolidations, a decade apart — the field naming itself as a field | Rationale Management in Software Engineering (2006); Rationale-Based Software Engineering (2008) | Dutoit, McCall, Mistrik, Paech (eds.), Springer 2006 (`dutoit-mccall-mistrik-paech-rationale-management-se-2006`) — the umbrella-book unit, distinct from its WinWin (D35) and Buckingham Shum (D35) chapters already inventoried; Burge, Carroll, McCall, Mistrik (eds.), Springer 2008 (`burge-carroll-mccall-mistrik-rationale-based-se-2008`) |
| Rationale capture extended past developers to a new actor class, showing the field active well past its 1990s-2000s core | On user rationale in software engineering | Kurtanovic, Maalej, Requirements Engineering 2018 (`kurtanovic-maalej-user-rationale-se-2018`) |
| Direct H10 (epistemic blast-radius) challengers, expressed in 1990s/2000s design-rationale vocabulary instead of D-System's own — surfaced by D37's own mandated collision query and cross-referenced at D38 | A rationale-based architecture model for design traceability and reasoning; Software Engineering Using RATionale (SERAT) — impact assessment when requirements, development criteria and assumptions change, by inferring over captured rationale | Tang, Jin, Han, JSS 2007 (`tang-jin-han-rationale-based-architecture-model-2007`); Burge, Brown, JSS 2008 (`burge-brown-serat-software-engineering-using-rationale-2008`) — both flagged collision candidates |
| Negative vocabulary finding, recorded plainly: naive "design rationale" + "knowledge graph"/"GitHub" queries collide with unrelated modern ML and namesake-project usage | "Rationale" overloaded by LLM chain-of-thought/explanation literature; "design rationale" as a GitHub search term collides with generic design-tool repositories | Two zero-yield ledger rows, `LIT-02-S178` (arXiv/web), `LIT-02-S179` (GitHub) — the field's actual named systems (gIBIS, DRed, SIBYL, JANUS) were found only via named-author/named-system queries, not generic phrase search |

## D38 — Architecture rationale

**The strongest Phase A anchor across all six domains, and one of this dispatch's three
mandatory findings:** ISO/IEC/IEEE 42010:2022, the international standard for architecture
description, defines **"architecture rationale"** as a first-class conceptual element — "the
explanation, justification or reasoning about architecture decisions that have been made and
architectural alternatives not chosen" — using D-System's own mandated term verbatim, and
*requires* architecture descriptions to record it, including linkage to "stakeholder concerns and
other requirements" and to "alternatives not chosen." A standards body owns this term. It is not
D-System's coinage and not a single paper's; it is normative international practice, restated here
plainly rather than treated as a near-neighbour analogy.

| D-System term | Field term | Established by |
|---|---|---|
| Architecture rationale as a first-class, standardized concept — the field's own name for D-System's mandated term, defined by a standards body rather than a single research paper (H9) | ISO/IEC/IEEE 42010:2022, "Software, systems and enterprise — Architecture description" — architecture rationale as required content, linked to stakeholder concerns/requirements and to alternatives not chosen | `iso-42010-2022-architecture-description-standard` (ISO catalog entry); `iso-42010-conceptual-model-working-group-page` (the standard's own working-group-maintained conceptual model) — both flagged collision candidates, together the single strongest Phase A anchor in this six-domain dispatch |
| The field's own foundational 2005 reframing of architecture-as-decisions, the paradigm shift D-System's own decision-centric framing also assumes (H7) | Software Architecture as a Set of Architectural Design Decisions | Jansen, Bosch, WICSA 2005 (`jansen-bosch-architecture-as-decisions-wicsa-2005`) — the field's single most foundational paper; flagged collision candidate |
| Co-foundational 2005 paper, direct ancestor of current ADR practice (bridges to D40) | Architecture Decisions: Demystifying Architecture | Tyree, Akerman, IEEE Software 2005 (`tyree-akerman-architecture-decisions-demystifying-2005`) — flagged collision candidate; Nygard's 2011 ADR format (D40) explicitly credits this lineage |
| Decision ontology classifying decision types — this domain's own "architecture rationale" variant reaching all the way back to a 2004 workshop paper with no resolvable DOI | An Ontology of Architectural Design Decisions — existence (ontocrises), property (diacrises) and executive (pericrises) decisions | Kruchten, 2nd Groningen Workshop on Software Variability Management, 2004 (`kruchten-ontology-architectural-design-decisions-2004`), kept via direct URL, no DOI exists for this workshop paper (confirmed at `LIT-02-S197`); flagged collision candidate |
| Early (pre-2005), directly on-topic precedent for D-System's own low-friction capture claim — one of the four sources in this dispatch with no resolvable DOI | Automated Capture and Retrieval of Architectural Rationale — ubiquitous-computing (SAAMPad) augmentation of SAAM sessions for non-disruptive rationale capture | Richter, Schuchhardt, Abowd, WICSA1, 1999 (`richter-schuchhardt-abowd-automated-capture-architectural-rationale-1999`), kept via direct URL after a zero-yield Crossref search (`LIT-02-S197`) and a 403 on the Georgia Tech repository (`LIT-02-S201`); flagged collision candidate; a second, independent WICSA-lineage source on the same problem is Smolander, Paivarinta, "Practical Rationale for Describing Software Architecture," IFIP 2002 (`smolander-paivarinta-practical-rationale-describing-architecture-2002`) |
| Explicit model relating architectural decisions to their rationale, this domain's core mechanism paper, triangulated by three independent routes (`LIT-02-S181`, `LIT-02-S192`, `LIT-02-S199`) | Design decisions and design rationale in software architecture | Ali Babar, Lago, JSS 2009 (`babar-lago-design-decisions-rationale-architecture-2009`) — flagged collision candidate; its companion paper on the same relationship is Gilson, Englebert, "Rationale, decisions and alternatives traceability for architecture design," ECSA 2011 companion volume (`gilson-englebert-rationale-decisions-alternatives-traceability-2011`), also flagged collision candidate — **a ledger discrepancy is recorded here rather than resolved silently: `LIT-02-S192` and `LIT-02-S199`'s own duplicate_handling text describes the Gilson/Englebert DOI as "already kept under D37 at LIT-02-S181," but LIT-02-S181's actual `kept` cell contains only the Tang/Jin/Han DOI, not this one** — this row is that identifier's only real inventory entry |
| Retrospective/backward decision recovery, directly relevant to H9 — a research line spanning a decade | Documenting after the fact: Recovering architectural design decisions (2008); Recovering Architectural Design Decisions (2018); Uncovering Architectural Design Decisions (2017, precursor) | Jansen, Bosch, Avgeriou, JSS 2008 (`jansen-bosch-avgeriou-documenting-after-the-fact-2008`); Shahbazian et al., ICSA 2018 (`shahbazian-et-al-recovering-architectural-design-decisions-2018`); Shahbazian, Lee, Le, Medvidovic, arXiv 2017 (`shahbazian-lee-le-medvidovic-uncovering-architectural-design-decisions-2017`) — the 2017/2018 pair is one Shahbazian decision-recovery lineage, not independent confirmations (methodology Sec.12) |
| Tool support and general-treatment adjacents rounding out the domain's core mechanism cluster | Architecture Decisions (book chapter, 2014); Tool Support for Architectural Decisions (2007); Design rationale capture in software architecture (2014 doctoral symposium) | van der Ven, Bosch (`van-der-ven-bosch-architecture-decisions-chapter-2014`); Jansen, van der Ven, Avgeriou, Hammer (`jansen-van-der-ven-avgeriou-hammer-tool-support-architectural-decisions-2007`); Schubanz (`schubanz-design-rationale-capture-software-architecture-2014`) — fulfils the D37/`LIT-02-S177` forward reference |
| Second forward reference from D37/`LIT-02-S177`, fulfilled here with a weaker identifier form rather than left unresolved | Guidance for Design Rationale Capture to Support Software Evolution — practitioner guidelines despite "more than thirty years of research on the topic" | `guidance-design-rationale-capture-software-evolution-2014`, kept via ResearchGate URL after a zero-yield Crossref search (`LIT-02-S203`); a real, sobering "known but under-adopted" finding for the campaign's reuse-recommendation question |
| Direct, current (2025) collision: LLMs generating architecture-decision rationale from developer discourse, on top of D-System's own LLM-driven rationale-generation ambition (H7) | Using LLMs in Generating Design Rationale for Software Architecture Decisions | Zhou, Li, Liang, Zhang, Shahin, Li, Yang, arXiv 2025 (`zhou-li-liang-llms-generating-design-rationale-2025`) — flagged collision candidate |
| The field's major decision-making-techniques survey, this domain's own vocabulary-consolidation anchor | Decision-making techniques for software architecture design | Falessi, Cantone, Kazman, Kruchten, ACM Computing Surveys 2011 (`falessi-cantone-kazman-kruchten-decision-making-techniques-2011`) |

## D39 — Architecture knowledge management

**The second of this dispatch's three mandatory findings:** "architectural knowledge vaporization"
— architectural knowledge lost when the people who made decisions leave or forget — names the exact
failure mode D-System's provenance and typed-transition claims (H2, H9) exist to prevent. The term
was given its definitive full-length treatment in Remco C. de Boer's 2009 VU Amsterdam PhD
dissertation, *Architectural Knowledge Management: Supporting Architects and Auditors* — 15+ years
before D-System's own conception. **A precision correction to the coordinator's own framing, recorded
rather than silently fixed:** the addressing block cites `10.1007/978-3-642-23798-0_27` alongside "de
Boer's 2009 dissertation" as though naming one source; Crossref confirms that DOI is actually a
*different*, later paper — Tofan, Galster, Avgeriou, "Reducing Architectural Knowledge Vaporization by
Applying the Repertory Grid Technique" (2011) — not the dissertation itself. Both are real, both are
kept, and both are cited below as the two distinct sources they are.

| D-System term | Field term | Established by |
|---|---|---|
| The failure mode D-System's provenance/typed-transition apparatus exists to prevent, coined and given definitive treatment 15+ years earlier (H2, H9) | Architectural knowledge vaporization — architectural knowledge lost when its owners leave or forget | de Boer, *Architectural Knowledge Management: Supporting Architects and Auditors*, VU Amsterdam PhD dissertation, 2009 (`de-boer-architectural-knowledge-management-dissertation-2009`), kept via direct URL (no DOI exists for the dissertation record); flagged collision candidate — the definitive full-length treatment, distinct from the two Tofan/Galster/Avgeriou repertory-grid papers below |
| A specific elicitation technique proposed to reduce vaporization, and its companion short-paper — same authors, same year, same technique, two legitimate venues, not independent confirmations (methodology Sec.12) | Reducing Architectural Knowledge Vaporization by Applying the Repertory Grid Technique (2011); Capturing tacit architectural knowledge using the repertory grid technique (NIER track, 2011) | Tofan, Galster, Avgeriou (`reducing-architectural-knowledge-vaporization-repertory-grid-2011`, `capturing-tacit-architectural-knowledge-repertory-grid-nier-2011`) |
| Vaporization extended eight years forward into a delivery context closer to D-System's own operating assumptions (agile, distributed) | Towards a reduction in architectural knowledge vaporization during agile global software development | Borrego, Moran, Palacio, Vizcaino, Garcia, Information and Software Technology 2019 (`borrego-et-al-vaporization-agile-gsd-2019`) |
| Vocabulary-map anchor and this domain's own foundational formulation, iterated across two consecutive years by the same authors (H1, H9) | Building up and Exploiting Architectural Knowledge (2005 workshop); Building Up and Reasoning About Architectural Knowledge (2006 book chapter) | Kruchten, Lago, van Vliet (`kruchten-lago-van-vliet-building-exploiting-architectural-knowledge-wicsa-2005`); Kruchten, Lago, van Vliet, LNCS 2006 (`kruchten-lago-van-vliet-building-reasoning-architectural-knowledge-2006`) — co-foundational with the paper below; both flagged collision candidates |
| Co-foundational paper naming the field alongside the above, from the same VU Amsterdam/Groningen research programme that produced the vaporization dissertation | Architectural Knowledge: Getting to the Core | de Boer, Farenhorst, Lago, van Vliet, Clerc, Jansen, LNCS 2007 (`de-boer-farenhorst-architectural-knowledge-getting-to-core-2007`) — flagged collision candidate |
| The field's own decade retrospective, its state-of-field consolidation, and a five-author roster spanning both D38 and D39's founding names | 10 years of software architecture knowledge management: Practice and future (2016, publication year corrected from the DOI's apparent 2015); Architectural knowledge and rationale (2007) | Capilla, Jansen, Tang, Avgeriou, Ali Babar, JSS (`capilla-et-al-ten-years-akm-practice-future-2016`); Avgeriou, Kruchten, Lago, Grisham, Perry, ACM SIGSOFT SEN (`avgeriou-et-al-architectural-knowledge-rationale-sen-2007`) |
| The field's own name for itself as an edited-volume unit, and its tool-technologies chapter | Software Architecture Knowledge Management: Theory and Practice | Ali Babar, Dingsoyr, Lago, van Vliet (eds.), Springer 2009 (`ali-babar-dingsoyr-lago-van-vliet-akm-book-2009`); chapter: Liang, Avgeriou, "Tools and Technologies for Architecture Knowledge Management" (`liang-avgeriou-tools-technologies-akm-chapter-2009`) |
| Named "second-generation" AKM tooling this domain itself compares — one of the four sources in this dispatch with no resolvable DOI | ADkwik — Web 2.0 Collaboration System for Architectural Decision Engineering, adding collaborative/Web-2.0 decision workflow to the PAKME/Knowledge Architect generation | Schuster, Zimmermann, Pautasso, SEKE 2007 (`schuster-zimmermann-pautasso-adkwik-seke-2007`), kept via ResearchGate URL after a zero-yield Crossref search (`LIT-02-S212`); flagged collision candidate; the field's own dedicated tool-comparison survey is Tang, Avgeriou, Jansen, Capilla, Ali Babar, "A comparative study of architecture knowledge management tools," JSS 2010 (`tang-et-al-comparative-study-akm-tools-2010`) |
| Codified architecture knowledge applied to runtime product-line evolution — an unusually direct precedent for D-System's own runtime-to-knowledge closure hypothesis (H11) | Codifying architecture knowledge to support online evolution of software product lines | Weyns, Michalik, SHARK workshop 2011 (`weyns-michalik-codifying-architecture-knowledge-product-lines-2011`) — flagged collision candidate |
| Early state-of-the-field challenges/approaches/tools framing, two years before the field's 2009 edited-volume consolidation | Architecture Knowledge Management: Challenges, Approaches, and Tools | Ali Babar, Gorton, ICSE'07 Companion (`ali-babar-gorton-akm-challenges-approaches-tools-2007`) |
| Three independent 2024-2026 papers converging on "LLMs generating/managing architectural decisions" as an active, crowded contemporary research line — the first two from one research group extending its own prior work, not independent inventions (methodology Sec.12) | Can LLMs Generate Architectural Design Decisions? (2024); DRAFT-ing Architectural Design Decisions using LLMs (2025); AgenticAKM: Enroute to Agentic Architecture Knowledge Management (2026, an explicitly agentic reframing, kept under both its ResearchGate and canonical arXiv identifiers per the two-identifier-form rule) | `can-llms-generate-architectural-design-decisions-2024`; Dhar, Kakran, Karan, Vaidhyanathan, Varma, `dhar-et-al-draft-architectural-design-decisions-llms-2025`; Dhar, Vaidhyanathan, Varma, `dhar-vaidhyanathan-varma-agenticakm-2026` and `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` — all three flagged collision candidates |
| A direct, current H6/H10/H11 collision publicly proposed as future work in the same month this campaign runs: an automated pipeline extracting architectural knowledge from heterogeneous artifacts, linking/reconciling it into a structured knowledge base for change-impact analysis and RAG question-answering — close to D-System's own knowledge-construction-plus-retrieval architecture | From Scattered to Structured: A Vision for Automating Architectural Knowledge Management | Keim, Kaplan, arXiv 2026 (`keim-kaplan-scattered-to-structured-akm-vision-2026`) — flagged collision candidate; fulfils a D38/`LIT-02-S187` forward reference left unfulfilled until `LIT-02-S245` closed it |
| Fourth source in this dispatch with no resolvable identifier in the ledger at all (not merely no DOI) — resolved by the extraction worker's own verification search rather than left unfulfilled, per the coordinator's explicit instruction to carry it | A Pattern **driven** Approach against Architectural Knowledge Vaporization — documents architectural decisions about pattern application, reusing patterns' generic architectural knowledge to preserve rationale | van Heesch, Avgeriou, EuroPLoP 2009 (`van-heesch-avgeriou-pattern-driven-approach-vaporization-2009`) — the ledger's own D39/`LIT-02-S248` row explicitly excluded this source ("noted but not kept... not independently verified"); found and logged at `LIT-02-S253`. **Title correction recorded plainly:** the coordinator's dispatch names it "Pattern-**based**"; DBLP, Semantic Scholar and the author's own hosted copy all give "Pattern-**driven**" — treated as the same paper (same authors, venue, year, subject) with the title corrected rather than silently perpetuated |

## D40 — Architecture Decision Records

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor: the practitioner-coined founding artifact of current ADR practice, building on D38's 2005 academic reframing (Jansen & Bosch; Tyree & Akerman) but as a lightweight, version-controlled, git-native practice | "Documenting Architecture Decisions" (blog post, 2011) | Nygard (`nygard-documenting-architecture-decisions-2011`) — flagged collision candidate despite its blog-post form, per the campaign's source-priority discipline (format, not importance, drives the type field); real institutional-scale adoption confirmed at UK (Ministry of Justice OPG, GOV.UK Publishing), US-federal (simpler.grants.gov) and Texas A&M examples (`LIT-02-S216`, `LIT-02-S217`, `LIT-02-S244`) |
| This domain's dominant structured template, decomposing Nygard's Y-statement format into decision drivers/context/consequences/follow-ups | MADR — Markdown Architectural Decision Records | Kopp, Armbruster, Zimmermann, ZEUS 2018 workshop, CEUR-WS Vol-2072 (`kopp-armbruster-zimmermann-madr-format-tool-support-2018`) — flagged collision candidate, the closest thing to a peer-reviewed MADR specification; the living template repository is `adr-madr-github-template-repo` |
| The field's own supersession discipline, restating D-System's append-only-transition model (H2) as a lightweight, vendor-endorsed practitioner convention: once accepted, an ADR is "never reopened or changed — instead superseded," the new record explicitly referencing the old one | "Decision log" / "superseded decisions" (ArchitectureDecisionRecord bliki entry) | Fowler (`fowler-architecture-decision-record-bliki`) — flagged collision candidate; AWS's and Microsoft's own prescriptive-guidance pages confirm this as current, vendor-endorsed practice rather than a niche idea |
| Personal (single-author), unpublished but concrete implementation-availability data point for automated ADR-supersession-lineage tooling — a `vault adr audit` CLI performing collision detection across a named "Talon supersession chain" | ADR-0173 personal vault system | `joelclaw-adr-vault-supersession-audit-lead` (`LIT-02-S219`, confirmed by direct inspection at `LIT-02-S220`) — a lead, not research evidence, per the methodology's grey-literature discipline |
| Current, active empirical-mining research on ADRs at scale (H9); a 550-repository study finding decision drivers and alternatives "under-documented" in real-world ADRs — an empirical baseline any D-System ADR-quality claim should be measured against | A Text Mining and Classification Approach for Analyzing Architecture Decision Records | Miccio Palermo, Tommasel, Diaz-Pace, arXiv 2026 (`miccio-palermo-et-al-text-mining-classification-adrs-2026`) |
| Direct, current collision: automated ADR generation via LLMs, paralleling D-System's own decision-generation ambitions | Context Matters: Evaluating Context Strategies for Automated ADR Generation Using LLMs | arXiv 2026 (`context-matters-automated-adr-generation-llms-2026`) — flagged collision candidate |
| Rationale extracted post-hoc from ordinary development artifacts (issue logs), bridging D37 and D40, an alternative to D-System's explicit-capture assumption | DRMiner — extracting latent design rationale from Jira issue logs via LLM prompt tuning | ASE 2024 (`drminer-latent-design-rationale-jira-issue-logs-2024`) |
| Mature multi-vendor reuse-recommendation candidate for D-System's own decision-log UI question, evidenced by real third-party adoption (Commanded ecosystem, BetssonGroup fork, multiple independent repos) | log4brains — docs-as-code ADR tool, IDE-native logging, automatic static-site publishing via CI/CD | `log4brains-oss-github` — flagged collision candidate, the strongest reuse-recommendation candidate found in D40 |

## D41 — IBIS

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor and absolute historical origin, 56 years before D-System's own conception — originally for political-decision coordination on "wicked problems," not software (a vocabulary transplant later performed by gIBIS) | IBIS — Issues as Elements of Information Systems | Kunz, Rittel, UC Berkeley Center for Planning and Development Research Working Paper No. 131, July 1970 (`kunz-rittel-ibis-issues-elements-information-systems-1970`), kept via direct URL (no DOI exists for a 1970 working paper); flagged collision candidate |
| The pivotal transplant of IBIS into software design rationale (D37) — one of the most-cited sources encountered in this entire campaign | gIBIS — graphical, hypertext Issue-Based Information System | Conklin, Begeman, CSCW 1988 (`conklin-begeman-gibis-hypertext-tool-cscw-1988`) — flagged collision candidate; the identical-title, identical-year ACM TOIS journal version (`conklin-begeman-gibis-hypertext-tool-tois-1988-dup`) is a conference/extended-journal republication of the same paper, not an independent source (methodology Sec.12) |
| Distinct follow-up paper in the same gIBIS lineage, not a republication of the above | gIBIS: A Tool for All Reasons | Conklin, Begeman, JASIS 1989 (`conklin-begeman-gibis-tool-all-reasons-jasis-1989`) — flagged collision candidate |
| IBIS's three-node model, D-System's own actor/provenance/conflict primitives expressed as a graph-link vocabulary 55 years earlier — this domain's own mandated variant | Issue-Position-Argument model — issue/position/argument nodes linked by generalizes/specializes/responds-to/questions/is-suggested-by/supports/objects-to relations | Confirmed directly at `LIT-02-S231`; extended with a formal uncertainty/confidence mechanism (fuzzy reasoning) by Cao, Protzen, Design Studies 1999 (`cao-protzen-ibis-fuzzy-reasoning-design-studies-1999`) — flagged collision candidate, an early precedent for combining argumentation structure with epistemic confidence |
| Implementation lineage from research tool to field practice, paralleling D-System's own ambition to move from architecture to daily-use tool | gIBIS &rarr; QuestMap (commercial) &rarr; Compendium (open-source); Dialogue Mapping (real-time IBIS facilitation methodology) | Conklin, *Dialogue Mapping: Building Shared Understanding of Wicked Problems*, 2005 (`conklin-dialogue-mapping-questmap-book-2005`), kept via bibliographic-identity fallback only, not as evidence content itself |
| This domain's own icon-based issue/idea/argument/decision node vocabulary, building directly on gIBIS/QuestMap — a single research program spanning D35 (`hypermedia-argumentation-based-rationale-2005`), D37 and D41 in this campaign's own matrix | Compendium — argumentation/sensemaking tool | Buckingham Shum, Selvin, Sierhuis, Conklin, COMMA 2010 (`buckingham-shum-et-al-compendium-comma-2010`), flagged collision candidate; community site `compendiuminstitute-org-lead` |
| Sobering reuse-recommendation data point: the strongest historical IBIS tooling is dead code | Compendium — final release 2.1.3, January 2014, now unmaintained for over a decade; at least one community reimplementation (pycompendium) and one federation experiment (IBIS-Server) | `pycompendium-oss-github`; `knowledgegarden-ibis-server-oss-github` |
| Negative vocabulary finding, recorded plainly: even the field's own unabbreviated name collides with the much larger modern KR/KG literature, and the bare acronym collides with an unrelated dataframe library, a federated encyclopedia, a neurosurgical platform, a braille printer and a genomics tool | "Issue-based information systems" (generic KR/KG collision); bare "IBIS" (GitHub namesake collision) | Two zero-yield/collision ledger rows, `LIT-02-S230` (phrase collision), `LIT-02-S232` (GitHub acronym collision) — the field's actual history was found only via named-author queries (`LIT-02-S224`, `LIT-02-S225`) |
| REMAP already answers this domain's own mandated collision query, rather than a new IBIS-traceability system existing separately | REMAP "enlarges the Issue-Position-Argument model of IBIS" to support software requirements traceability | Cross-domain confirmation: `ramesh-dhar-remap-rationale-capture-1992` (D35) is the field's own answer to `LIT-02-S234`'s verbatim D41 collision query — triangulation, not a gap |

## D42 — QOC

**The third of this dispatch's three mandatory findings, and the strongest single collision found
across all six domains:** `arxiv:2604.05203`, "Decision-Oriented Programming with Aporia" (submitted
April 2026; authors from UC San Diego, University of Pennsylvania, Cornell, Technion and University at
Buffalo). An AI coding agent proactively elicits design decisions from the programmer as Questions,
tracks them in a persistent, editable Decision Bank, and encodes each decision as an executable test
suite traceable to code — explicitly built on QOC, under different vocabulary, in an AI-pair-
programming setting, addressing D-System's own H7 (development provenance), H8 (phase-bounded
context) and H9 (bidirectional traceability) at once. Scored honestly on the rubric rather than
softened: component overlap 5 (materially equivalent mechanism — explicit structured decisions,
proactive elicitation, persistent bank, executable-test traceability to code), architecture overlap 4
(near end-to-end across the Implementation & Experience half of D-System's own two coupled systems,
though it does not touch belief/convergence/authority on the Knowledge Construction side).

| D-System term | Field term | Established by |
|---|---|---|
| Vocabulary-map anchor and founding document — the exact 1991 HCI notation D-System's own decision/rationale apparatus might be compared against | QOC — Questions, Options, and Criteria: Elements of Design Space Analysis | MacLean, Young, Bellotti, Moran, Human-Computer Interaction 1991 (`maclean-young-bellotti-moran-qoc-design-space-analysis-1991`) — flagged collision candidate; produced at Xerox's Cambridge/EuroPARC lab; the 2020 Routledge-reissue chapter DOI (same reissue volume as D37's Moran & Carroll book) is the same paper republished, not an independent source (`maclean-et-al-qoc-2020-reissue-dup`, dedup of the 1991 paper) |
| Field's own explicit scope limitation, recorded rather than smoothed over: QOC is presented as HCI-specific tooling, not general-purpose decision/rationale infrastructure — a scope D-System's own apparatus is not bound by | "The design domain in which researchers are most actively working is user interface design" | Confirmed directly at `LIT-02-S238`; zero new identifier, a negative/scope finding in its own right |
| QOC's three-part structure independently reinvented into new decision-governance contexts — this domain's own mandated "questions options criteria" variant | QOC DAO — Questions/Options/Criteria applied to blockchain-governance decision-making for an AI-driven decentralized autonomous organization | arXiv 2025 (`qoc-dao-ai-driven-dao-2025`) |
| Early empirical application of QOC as a post-hoc design-space-analysis notation | An Application of Process Tracing & Design Space Analysis (QOC) | `application-process-tracing-design-space-analysis-qoc` |
| AI/LLM techniques applied directly on top of the 1991 QOC notation for transparent, insightful decision-making — a direct precedent for D-System's own decision/rationale-plus-AI combination | AI-Enhanced QOC-Analysis: A Framework for Transparent and Insightful Decision-Making | Schmidt, Pehlke, Jansen, IFIP AICT 2024 (`schmidt-pehlke-jansen-ai-enhanced-qoc-analysis-2024`) — flagged collision candidate |
| Broader, independently-useful survey of design-decisions-in-code tooling generally, surfaced alongside the Aporia collision | A Survey of Tool Support for Working with Design Decisions in Code | Mehrpour, LaToza, ACM Computing Surveys 2024 (`mehrpour-latoza-survey-tool-support-design-decisions-code-2024`) |
| Negative vocabulary finding, recorded plainly: QOC is genuinely ambiguous outside its own literature — AcronymFinder lists 15 distinct meanings, with "Quality of Care" and "Qatar Olympic Committee" dominating general search above the HCI design-rationale sense | Bare "QOC" acronym | Deliberate bare-acronym collision test, `LIT-02-S243`, paralleling the AKM test at D39/`LIT-02-S215` and the IBIS GitHub test at D41/`LIT-02-S232` — zero results on the page concerned design rationale at all |
