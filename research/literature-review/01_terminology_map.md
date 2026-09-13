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
