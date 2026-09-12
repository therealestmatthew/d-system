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
