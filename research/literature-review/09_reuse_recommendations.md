# Reuse recommendations

Standards, ontologies, models, and implementations this campaign found that D-System should inherit
rather than recreate, per `CLAUDE.md` §15's deliverable definition. Each recommendation is a
recorded finding from `04_evidence_matrix.csv`, not a design decision — this file does not revise
D-System's architecture (`CLAUDE.md` §2; that is synthesis-phase work by other dispatches) and
makes no code change. Every row below carries the `source_id` establishing it, so each
recommendation is traceable back to a specific deep-read, locator-cited matrix row.

**Coverage caveat, binding on this document.** This list is built from the 67 rows this campaign
deep-read, not the full candidate pool: 336 of 400 collision candidates surfaced by search have
never been deep-read, including 2 of the top prescore band's 32 candidates —
`dhar-vaidhyanathan-varma-agenticakm-2026` and `epistemic-sybil-resistance-multiplying-agents-2026`,
each a documented near-duplicate of a source this campaign did deep-read, under the partner ids
`dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` and `epistemic-sybil-resistance-bara-2026`
respectively. The 67 rows are not represented here as the strongest candidates the campaign could
have found, only as the strongest candidates it actually read. A future pass through the unread 336
could surface a better-fitting standard or implementation for any item below without contradicting
it. On search completeness more generally: this campaign's duplicate-discovery rate fell from 20.0%
(44/220, `phase-lit-06`) to 15.0% (58/387, `phase-lit-08`) when later searches targeted previously
neglected hypotheses — a trend toward more new material being found, and no claim of saturation is
made anywhere in this document.

---

## 1. Provenance vocabulary — W3C PROV-O, not a bespoke schema

**Inherit:** the Entity/Activity/Agent triple plus `wasAssociatedWith`/`actedOnBehalfOf`/derivation
relations as the raw vocabulary substrate for D-System's transition provenance (H2, H3, H7, H9).

**Matrix row:** `w3c-prov-o-2013` (Lebo, Sahoo, McGuinness, eds., W3C Recommendation, 30 April 2013,
https://www.w3.org/TR/prov-o/, `access_limitation: full_text`) — recorded in the row's own
`strongest_dsystem_overlap` field as "the single closest raw-vocabulary antecedent to D-System's
'transition provenance' primitive... structurally the same shape." Reference toolkits (ProvToolbox,
the `prov` Python library) and dozens of independent downstream systems implement it; two of this
campaign's own other rows (`evidence-graphs-fair-computation-defeasible-reasoning-2021`,
`procko-provtracer-erau-dissertation-2025`) build directly on it as their substrate.

**Why inherit rather than recreate:** a 2013 W3C Recommendation with over a decade of extensions and
tooling is a lower-risk foundation for actor/derivation provenance than an original schema, and
`06_hypothesis_tests.md`'s H3 finding — that rich, typed, multi-actor provenance representation is
"thoroughly known" — rests substantially on this standard and its extensions.

---

## 2. Belief-revision operators — AGM, not an ad hoc conflict rule

**Inherit:** the contraction and revision operators, and the epistemic-entrenchment ranking that
governs them, as the formal basis for how a D-System knowledge state is revised under new or
conflicting information (H2's transition semantics).

**Matrix row:** `agm-partial-meet-contraction-revision-1985` (Alchourron, Gardenfors, Makinson,
*Journal of Symbolic Logic* 50(2), 1985, pp.510-530, DOI 10.2307/2274239,
`access_limitation: secondary_coverage`) — recorded as "the single most formally rigorous TYPED
belief-transition system in this batch: two named, axiomatically-constrained operators... with a
genuine conflict-resolution rule via epistemic entrenchment," and the directly-named ancestor cited
by both `graph-native-cognitive-memory-belief-revision-semantics-2026` and
`decision-oriented-programming-aporia-2026`.

**Reference implementation to study, not necessarily adopt wholesale:**
`graph-native-cognitive-memory-belief-revision-semantics-2026` (Kumiho; arxiv:2603.17244,
`access_limitation: preprint_version`) publishes a formal correspondence proof between the AGM
postulates and a deployed graph-memory system's operational semantics, with an open-source SDK,
MCP plugin, and benchmark suite at github.com/KumihoIO plus a free self-hostable "Kumiho CE" binary.
Its own correspondence is explicitly scoped to "a deliberately simple propositional logic over
ground triples" (per `06_hypothesis_tests.md`'s H2 block) — a scope-matched starting point, not a
drop-in replacement for D-System's fuller epistemic model.

**Why inherit rather than recreate:** AGM is a 40-year-old axiomatic foundation with a direct 2026
operational correspondence proof already published against a graph-memory architecture close to
D-System's own; building a new conflict/revision rule from first principles duplicates work with a
worked, formally-verified precedent.

---

## 3. Temporal model — SQL:2011 system-versioned tables / TSQL2, not a bespoke `TemporalScope`

**Inherit:** the transaction-time, system-versioned table pattern (and, where bi-temporal tracking is
needed, the valid-time dimension alongside it) as the substrate for D-System's `TemporalScope` field
in its candidate state abstraction.

**Matrix row:** `snodgrass-developing-time-oriented-database-applications-sql-1999` (Snodgrass,
Morgan Kaufmann, 1999, ISBN 1-55860-436-7, https://www2.cs.arizona.edu/~rts/tdbbook.pdf,
`access_limitation: full_text`) — its techniques were adopted directly into the TSQL2 language
proposal this same author co-developed, and influenced the SQL:2011 temporal-table standard
(system-versioned and application-time-period tables); the matrix row calls it "among the most
consequential unreleased-as-software works in this campaign in terms of real standardization
impact."

**Modern reference implementation:** `zep-graphiti-temporal-kg-agent-memory-2025` (arxiv:2501.13956,
`access_limitation: full_text`) implements a four-timestamp bi-temporal edge model in a commercial,
production-deployed property graph — a worked 2025 instance of the same underlying discipline at
agent-memory scale, open-source at the Graphiti component (github.com/getzep/graphiti).

**Why inherit rather than recreate:** a formalized, standardized temporal-table discipline with a
direct 2025 property-graph instantiation removes the need to design bi-temporal semantics for
`TemporalScope` from scratch, and reduces the risk of the informal temporal-consistency bugs a
standards-grounded model is built to avoid.

---

## 4. Decision/requirement provenance — the Jansen & Bosch / Zimmermann et al. ADR metamodel, not a
   bespoke decision object

**Inherit:** architecture as an accumulated, non-overwritten set of typed decision objects
(Jansen & Bosch's `architecture = dd1 + dd2 + ... + ddn`), extended with Zimmermann et al.'s typed
outcome-status lifecycle (open/implied/resolved), eight integrity constraints, and per-outcome actor
provenance (`changedBy`) — as the representation for D-System's decision/requirement nodes (H7, H9).

**Matrix rows:** `jansen-bosch-architecture-as-decisions-wicsa-2005` (WICSA 2005, pp.109-119, DOI
10.1109/wicsa.2005.61, `access_limitation: full_text`) and
`zimmermann-et-al-managing-architectural-decision-models-2009` (*Journal of Systems and Software*
82(8), 1249-1267, 2009, DOI 10.1016/j.jss.2009.01.039, `access_limitation: full_text`), the latter an
explicit formal extension of the former ("Our metamodel extends that from [1] and [5]," p.5).

**Reference implementation:** Zimmermann et al.'s row records a working, publicly deployed
Architectural Decision Knowledge Wiki (ADkwiki, launched March 2008, 200+ users, evaluated on 389
real decision issues) — a genuine, evaluated tool implementing the metamodel, though its
triggers/integrity-constraint engine is recorded in the same row as "implemented in an advanced
prototype that is not yet publicly available" (Sec.6.3) as of that paper's writing. Jansen & Bosch's
own tool, Archium, is recorded as not having existed at time of publication ("future work," Sec.4.8).

**Why inherit rather than recreate:** this is a 20-year, twice-formalized lineage with a deployed,
evaluated tool and a typed outcome-status lifecycle that already solves the open/implied/resolved
state machine D-System's decision nodes would otherwise need to design independently.

---

## 5. Design-rationale notation — QOC, via its direct 2026 agentic instantiation

**Inherit:** the Questions/Options/Criteria design-rationale notation (MacLean, Young, Bellotti &
Moran, 1991) as the elicitation structure for decisions, rather than an original decision-elicitation
format.

**Matrix row:** `decision-oriented-programming-aporia-2026` (arxiv:2604.05203,
`access_limitation: preprint_version`), which is self-described in its own Sec.2 as "an application
of QOC" — a working 2026 VS Code extension ("Aporia") evaluated in a 14-participant user study
against Claude Code as baseline, though not established as a maintained public open-source release
in the sections read.

**Why inherit rather than recreate:** QOC is a 35-year-old notation with a direct 2026 agentic-coding
instantiation already evaluated against a comparable baseline (an AI coding assistant); adopting the
notation, or studying Aporia's elicitation loop directly, is lower-risk than inventing a new
decision-elicitation format for D-System's plan/decision boundary.

---

## 6. Argumentation/defeasible-reasoning ontology — EVI, as a PROV-O-extended pattern to study

**Inherit:** the pattern of typed, transitively-propagating support/challenge edges over a PROV-O
graph, with defeasible (non-monotonic, human-arbitrated) resolution, as a starting structure for
D-System's claim/evidence graph (H3).

**Matrix row:** `evidence-graphs-fair-computation-defeasible-reasoning-2021` (Al Manir, Niestroy,
Levinson, Clark; bioRxiv 2021, also Springer LNCS 12839, IPAW 2020/2021,
biorxiv.org/content/10.1101/2021.03.29.437561, `access_limitation: full_text`) — the EVI ontology
(OWL 2) is published under MIT license at https://w3id.org/EVI# with a GitHub-archived OWL file and
Zenodo archival, deployed via the FAIRSCAPE microservices framework over a Stardog RDF quad store,
evaluated at 17,996-node scale on real NICU data spanning 5,957 infants.

**Why inherit rather than recreate:** the ontology is publicly released, standards-grounded (PROV-O
extension), and proven at real scale; its deliberate choice not to automate arbitration ("Challenges
do not invalidate, they present an opposing view. They ultimately require human judgment as to their
validity and strength") is itself a design signal worth carrying forward (see
`10_architecture_implications.md`), not just its schema.

---

## 7. Independence-discount arithmetic — Goldman's blind-follower proof, as the weighting formula's
   theoretical basis

**Inherit:** the closed-form result that a "blind follower" of another witness contributes zero
additional evidential weight, while genuinely independent witnesses do add weight, as the
mathematical basis for D-System's convergence/discount computation (H4).

**Matrix row:** `goldman-experts-which-ones-should-you-trust-2001` (Goldman, *Philosophy and
Phenomenological Research* 63(1), 2001, pp.85-110, DOI 10.1111/j.1933-1592.2001.tb00093.x,
`access_limitation: full_text`) — a peer-reviewed, general, agent-model-agnostic Bayesian proof
(Sec.4, Eqs.1-6), foundational to an entire expert-testimony sub-literature formally extended by
`reliability-testimonial-norms-scientific-communities-synthese` (Mayo-Wilson, 2014, eight proven
theorems plus ~4,500-network simulations, code published per the author's website,
`access_limitation: preprint_version`).

**Related, narrower formalization for graph-topological computation specifically:**
`epistemic-sybil-resistance-bara-2026` (arxiv:2609.01873, `access_limitation: full_text`) gives a
closed-form discount `kappa_m = 1/(1+rho(m-1))` for corroborating reports sharing an evidentiary root,
scoped to AI-agent report multiplicity only, with the practical protocol left as an explicit open
problem (Sec.9) and no deployed aggregator. `06_hypothesis_tests.md`'s H4 block — re-derived
clean-room by `LIT-09 H4R` (2026-09-19) — finds bara-2026 no longer stands alone as the
graph-topological family: two further 2026 sources, `grading-narrators-isnad-rijal-claim-provenance-2026`
(ISNAD) and `not-all-agreement-counts-as-corroboration-2026` (PACT), join it, and ISNAD specifically
combines graph topology, a computed shared-lineage discount, and a confirmed mixed human-agent scope
in one source. This entry remains a study target rather than a settled reuse recommendation because
no row reaches a confirmed component_overlap of 5 ("materially equivalent mechanism") — see
`10_architecture_implications.md`'s H4 discussion for the fuller implication.

**Why inherit rather than recreate:** the discount-for-dependence principle is a 25-year-old, proven
result; deriving equivalent arithmetic independently would duplicate settled mathematics.
`06_hypothesis_tests.md`'s H4 block rests its unified `LIKELY_ALREADY_KNOWN` verdict — covering
both the review-instructions' general phrasing and the frozen register's graph-topological phrasing
at the same status — in part on this Goldman/Mayo-Wilson pairing, together with the ISNAD/PACT
graph-topological sources named above.

---

## 8. Digital-thread stage graph — the trace/refine/realize typed-edge pattern

**Inherit:** the typed, directional (trace/refine/realize) graph spanning
Requirement -> Specification -> Implementation -> Test Case -> Field Performance as a starting
taxonomy for D-System's own cross-lifecycle stage linkage (H7, H9), rather than devising an original
stage-edge typing from scratch.

**Matrix row:** `model-based-digital-threads-sociotechnical-systems-2022` (Pessoa, Pires, Moreira, Wu;
*Machine Learning for Smart Environments/Cities*, Springer ISRL vol.121, pp.27-52, 2022, DOI
10.1007/978-3-030-97516-6_2, `access_limitation: full_text`), Fig.2.18. This is a peer-reviewed book
chapter's methodology and case-study model, not a released tool (SysML models built in a fictional
case study; no shipped software from the chapter itself).

**Complementary, commercially-operated precedent:** `us20250165226a1-ai-digital-thread-patent`
(Roper et al., Istari Digital; US Patent Application US20250165226A1, since granted as
US12461717B2, https://patents.google.com/patent/US20250165226A1/en,
`access_limitation: full_text`) — per the owner's ruling on this campaign, a patent's whole published
disclosure (specification and claims together) is prior art; the specification describes digital
threads "linked across different stages... from concept, design, testing, to production," and the
assignee commercially operates the described system as the "Interconnected Digital Engineering
Platform." No license or code is granted by the patent itself, and this dispatch did not
independently verify the shipped commercial product's current feature set against the patent's
specific claims.

**Why inherit rather than recreate:** two independent 2013-2018 governmental namings of the same
concept, a peer-reviewed academic treatment, and a granted, commercially-operated patent together
give a mature stage-typing vocabulary to start from, rather than inventing new stage-transition
semantics.

---

## 9. ADR generation/validation pipeline pattern — AgenticAKM's Extraction/Retrieval/
   Generation/Validation loop

**Inherit:** the four-stage Extraction/Retrieval/Generation/Validation pipeline pattern for
generating and cross-checking decision-rationale artifacts (ADRs) against source code and prior
decisions, as a starting point for any D-System capability that auto-derives decision records from
implementation state.

**Matrix row:** `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` (Dhar, Vaidhyanathan, Varma; arXiv
preprint, also AGENT'26 workshop @ ICSE 2026, ACM DOI 10.1145/3786167.3788416, arxiv:2602.04445,
`access_limitation: preprint_version`) — a working research prototype with public source at
github.com/sa4s-serc/AgenticAKM (read directly from the paper's own footnote); not established from
the sections read whether the repository is maintained beyond the paper's own experiments.

**Why inherit rather than recreate:** this is a 2026, publicly-sourced, multi-agent pipeline already
built directly on the Jansen & Bosch / Zimmermann et al. ADR lineage (recommendation 4 above) —
adopting or adapting its pipeline shape is lower-risk than designing an original ADR-generation
architecture independently of it.

---

## 10. Durable, replayable execution-unit state — the Durable Functions replay theorem, for the
    assembly half of phase-bounded execution

**Inherit:** the append-only, typed, replayable history-log pattern — with Durable Functions' formally
proven replay-correctness theorem — as the reconstruction mechanism for a D-System execution unit's
state (H8's assembly half), and the LangGraph checkpoint library as a production reference
implementation of parent-linked, forkable, resumable checkpoints specifically.

**Matrix rows:** `burckhardt-et-al-durable-functions-stateful-serverless-2021` (*Proc. ACM Program.
Lang.* 5, OOPSLA, Article 133, 2021, DOI 10.1145/3485510, `access_limitation: full_text`) — a
formally proven-correct replay theorem (Thm 6.4), shipping as production Azure Durable Functions
(github.com/Azure/durabletask); and `langgraph-checkpoint-library-oss`
(github.com/langchain-ai/langgraph/tree/main/libs/checkpoint, `access_limitation: full_text`) —
per-superstep persisted checkpoints with parent-chain lineage enabling backward walk and replay,
production-grade (41,574 GitHub stars on the parent repository, PyPI v4.2.0, first-party
Postgres/SQLite/Redis backends).

**Recorded implementation gap (not a recommendation to act on here, only to note):** the matrix row
for `langgraph-checkpoint-library-oss` records, citing the adversarial codebase review
(`04_state_transition_audit.md`, E42), that D-System's own shipped checkpoint mechanism currently
rewrites/overwrites summary sections in place rather than retaining a parent-linked chain of past
checkpoints — on this specific dimension, LangGraph's shipped behavior already exceeds D-System's
current implementation, not only its conceptual architecture. This is carried into
`10_architecture_implications.md` rather than acted on here.

**Why inherit rather than recreate:** a formally proven replay theorem and a 41,574-star production
checkpoint library both already solve the parent-chain, replayable-execution-unit problem D-System's
phase mechanism needs; the field's own literature (`burns-groth-agentic-ontological-notebook-memory-2026`)
separately names what LangGraph's checkpoints do *not* solve (typed, ontological knowledge
consolidation, as opposed to opaque key-value state) — the gap D-System would still need to design
for itself, addressed in recommendation 11 and in `10_architecture_implications.md`.

---

## 11. Nanopublication / multi-source claim provenance pattern — PROV-K, for claim-level corroboration
    at scale

**Inherit:** the pattern of extending a nanopublication-style claim record with a dedicated
provenance/trust ontology layer (PROV-K) linking each claim to multiple supporting and conflicting
sources with a certainty degree, as a starting schema for D-System's multi-source claim/evidence
records — while noting explicitly what it does *not* solve (independence-aware discounting; see
recommendation 7 and `10_architecture_implications.md`).

**Matrix row:** `extending-nanopublications-knowledge-provenance` (Giachelle, Marchesin, Menotti,
Silvello; IRCDL 2025, CEUR-WS Vol-3937 paper 10, https://ceur-ws.org/Vol-3937/paper10.pdf,
`access_limitation: full_text`) — deployed at real scale (197,511 extended nanopublications:
156,172 ReliableFact + 41,339 ContrastingEvidence), source released at
github.com/mntlra/knowledgeProvenance, ontology published at prov-k.dei.unipd.it/ontology/, archived
in bulk on Zenodo.

**Why inherit rather than recreate:** this is a real, large-scale, publicly-released system solving
the same multi-source-claim-representation problem D-System's evidence layer needs, immediately
reusable as schema and tooling, with its one documented gap (no independence/shared-lineage discount)
already covered separately by recommendation 7.

---

## Summary table

| # | Recommendation | Inherit instead of recreating | Matrix row(s) |
|---|---|---|---|
| 1 | Provenance vocabulary | W3C PROV-O | `w3c-prov-o-2013` |
| 2 | Belief-revision operators | AGM contraction/revision | `agm-partial-meet-contraction-revision-1985`, `graph-native-cognitive-memory-belief-revision-semantics-2026` |
| 3 | Temporal model | SQL:2011 system-versioned tables / TSQL2, bi-temporal edges | `snodgrass-developing-time-oriented-database-applications-sql-1999`, `zep-graphiti-temporal-kg-agent-memory-2025` |
| 4 | Decision/requirement provenance | Jansen & Bosch / Zimmermann et al. ADR metamodel | `jansen-bosch-architecture-as-decisions-wicsa-2005`, `zimmermann-et-al-managing-architectural-decision-models-2009` |
| 5 | Decision elicitation notation | QOC, via Aporia | `decision-oriented-programming-aporia-2026` |
| 6 | Argumentation/claim ontology | EVI (PROV-O extension) | `evidence-graphs-fair-computation-defeasible-reasoning-2021` |
| 7 | Independence-discount arithmetic | Goldman (2001) / Mayo-Wilson (2014) | `goldman-experts-which-ones-should-you-trust-2001`, `reliability-testimonial-norms-scientific-communities-synthese` (study target only: `epistemic-sybil-resistance-bara-2026`) |
| 8 | Cross-lifecycle stage typing | Digital-thread trace/refine/realize graph | `model-based-digital-threads-sociotechnical-systems-2022`, `us20250165226a1-ai-digital-thread-patent` |
| 9 | ADR generation/validation pipeline | AgenticAKM's Extraction/Retrieval/Generation/Validation loop | `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` |
| 10 | Replayable execution-unit state | Durable Functions replay theorem + LangGraph checkpoint library | `burckhardt-et-al-durable-functions-stateful-serverless-2021`, `langgraph-checkpoint-library-oss` |
| 11 | Multi-source claim provenance | PROV-K nanopublication extension | `extending-nanopublications-knowledge-provenance` |

Eleven recommendations, each traced to at least one deep-read, primary-text-verified matrix row.
None of these is presented as covering D-System's full proposed mechanism on its own — several
(recommendations 7, 10, 11 specifically) are paired in the table with a named, unresolved gap the
source itself does not close. Closing those specific gaps, where the literature could not, is the
subject of `11_open_research_questions.md` and `12_experiment_proposals.md`.
