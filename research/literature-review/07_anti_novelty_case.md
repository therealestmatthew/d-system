# The anti-novelty case

Per the methodology (`research/literature-review/CLAUDE.md` §14), the strongest coherent argument
that D-System requires no new mechanism is that it decomposes without residue into fourteen
established components:

```text
Knowledge Graph + PROV-O + Event Sourcing + Belief Revision + Argumentation + Truth Discovery
+ Agent Memory + Design Rationale + Requirements Traceability + ADRs + Digital Thread
+ Software Provenance + Observability + MAPE-K
```

This document builds that case component by component, each backed by rows from
`04_evidence_matrix.csv` (67 rows, 30 flagged `critical_collision: yes`) with locators, then states
what is left once the decomposition is applied — the required last step per §14: "If nothing
remains, say so. That is a successful research result."

**Coverage caveat, carried forward from the owner's ruling and binding on everything below.** This
case is built from the 67 rows this campaign deep-read, not from the full candidate pool. 336 of
400 collision candidates surfaced by search have never been deep-read, including 2 of the 32
candidates in the top prescore band (band = max of the two prescores) — the campaign's own stop
condition was met by count of sources compared, not by coverage of that band. Every claim below that
a component "is established" rests on the sources actually read; it is not a claim that the 336
unread candidates would not sharpen or contest the picture. Separately, on search completeness: this
campaign's duplicate-discovery rate fell from 20.0% (44/220, `phase-lit-06`) to 15.0% (58/387,
`phase-lit-08`) when later searches targeted previously neglected hypotheses — a trend toward more
new material being found, not toward exhaustion, and no claim of saturation is made anywhere in this
document.

---

## 1. Knowledge Graph

D-System's candidate state abstraction (`S = (O, E, L, Content, TemporalScope, Metadata)`) and
transition abstraction (`S_t --[T,P]--> S_t+1`) presuppose a graph-native substrate: typed nodes,
typed edges, and addressable identity for both. This substrate, independent of what D-System layers
on top of it, is thoroughly established across the matrix's agent-memory and provenance rows:

- **graph-native-cognitive-memory-belief-revision-semantics-2026** (Kumiho): "a graph-native memory
  architecture combining immutable versioned revisions, typed dependency/provenance edges, mutable
  tag pointers and URI-based addressing" (`strongest_dsystem_overlap`), commercially deployed
  (kumiho.io / github.com/KumihoIO), component_overlap=4 (re-derived on review from the first
  assessment's 5), architecture_overlap=3.
- **zep-graphiti-temporal-kg-agent-memory-2025**: a bi-temporal property-graph memory with
  four-timestamp edges, commercially deployed (getzep.com), component_overlap=4, architecture_overlap=3.
- **tgms-agent-native-bitemporal-graph-2026**: a formally specified, empirically validated bi-temporal
  graph substrate, open source (github.com/zxf-work/tgms), component_overlap=4 (disputed on review to
  3; left as scored per the owner's ruling that disputes are recorded, not applied),
  architecture_overlap=2.
- **mythologiq-agent-memory-oss**: a JSON-Schema-defined graph-of-records substrate with two
  independently-varying enum axes on one node type, confirmed by direct schema read, component_overlap=4,
  architecture_overlap=3.

Graph-native, typed-node/typed-edge memory for agents is a mature, multi-implementation, partly
commercial pattern as of 2025-2026. Nothing about using a graph as the underlying data structure is
contested anywhere in this matrix. (Zep/Graphiti and TGMS also share one uncredited 1999 ancestor —
Snodgrass's valid-time/transaction-time distinction — for their bi-temporal *substrate*
specifically, per TGMS's own Sec.7 and this matrix's `derivative_ancestor` fields; that shared
ancestry bears on the bi-temporal mechanism, not on the graph-structure claim made here, so it is
noted rather than treated as double-counting this component.)

---

## 2. PROV-O

D-System's transition provenance (actor identity, domain authority, evidence, method, lineage,
delegation — H3) is, at the vocabulary level, a re-statement of the W3C's 2013 provenance
standard:

- **w3c-prov-o-2013**: "the single closest raw-vocabulary antecedent to D-System's 'transition
  provenance' primitive (H2, H3, H7, H9): Entity/Activity/Agent plus generation/usage/derivation/
  attribution/association/delegation is structurally the same shape" (`strongest_dsystem_overlap`),
  citing the standard's own Overview (§1) and Activities-and-Agents (§4) sections for
  `wasAssociatedWith`/`actedOnBehalfOf`.
- **evidence-graphs-fair-computation-defeasible-reasoning-2021** (EVI): "an extension of W3C PROV,
  based on argumentation theory, which enables defeasible reasoning," deployed at 17,996-node scale
  over real NICU data (bioRxiv v3, Introduction/Methods), component_overlap=4, architecture_overlap=3.
- **log-is-the-agent-event-sourced-reactive-graphs-2026**: a total, worked-example-verified
  provenance/lineage chain using D-System's own vocabulary (claim, evidence, question) linked by
  typed relations, open source (Apache-2.0, pip-installable), component_overlap=4.
- **procko-provtracer-erau-dissertation-2025**: "an automated, ambient... capture pipeline producing
  a standards-grounded (PROV-O+BFO) provenance knowledge graph explicitly aimed at 'traceability,'
  'explainability,' 'reproducibility,' and extracting 'developer rationale'" — a 2025 dissertation
  applying PROV-O specifically to the software-development side D-System also targets.

A typed, multi-actor, standards-grounded provenance vocabulary — the raw material H3 needs — is a
2013 W3C Recommendation with a decade of extensions (EVI, 2021) and direct 2025-2026 application to
both agent memory and software-development rationale capture. Nothing in the sources this campaign
read disputes that the vocabulary itself is established — a claim bounded, like every claim in this
document, by the coverage caveat above (336 of 400 candidates never deep-read).

---

## 3. Event Sourcing

D-System's append-only transition history (H2) and phase-bounded execution units (H8) both
presuppose an event-sourced architecture: state as the fold of an immutable event log, not a
mutable record.

- **log-is-the-agent-event-sourced-reactive-graphs-2026**: "an event-sourced, append-only log as the
  sole source of truth with graph state as a deterministic, replayable projection/fold of it"
  (`strongest_dsystem_overlap`), self-described by its own author (Sec.8) as a "recombination" of
  event sourcing, CQRS, reactive dataflow, and 1980s Blackboard-era coordination (Nii 1986, matrix
  row `nii-blackboard-model-problem-solving-1986`).
- **burckhardt-et-al-durable-functions-stateful-serverless-2021**: "the append-only, typed, replayable
  history log as the sole mechanism reconstructing an execution unit's state," with a formally
  proven-correct replay theorem (Thm 6.4), Microsoft Research (Sec.3.2.3, "eternal orchestrations,
  continue-as-new").
- **langgraph-checkpoint-library-oss**: per-superstep persisted checkpoints with parent-chain lineage,
  production-grade (41,574 GitHub stars, PyPI v4.2.0), demonstrably exceeding D-System's own shipped
  checkpoint mechanism on the parent-chain dimension (adversarial codebase review, `04_state_transition_audit.md`, E42, as recorded on this matrix row).

Event sourcing as a general pattern is a decades-old, widely-implemented architecture; its
application to agentic-system state (log-is-the-agent) and to durable execution-unit state
(Durable Functions, LangGraph) is current, production-grade, and multiply independent.

---

## 4. Belief Revision

D-System's implicit model of a knowledge state that can be revised when new, possibly conflicting,
information arrives maps onto the belief-revision literature founded by AGM (1985):

- **agm-partial-meet-contraction-revision-1985**: "the single most formally rigorous TYPED
  belief-transition system in this batch: two named, axiomatically-constrained operators
  (contraction, revision) over a closed belief set, with a genuine... conflict-resolution rule via
  epistemic entrenchment" — the named ancestor cited directly by both `graph-native-cognitive-memory`
  and `decision-oriented-programming-aporia-2026`.
- **graph-native-cognitive-memory-belief-revision-semantics-2026**: a formal correspondence proof
  between the AGM postulates and a deployed memory system's operational semantics — the paper's
  central contribution, self-described as "not novel individual components... but a novel
  architectural synthesis."
- **memtx-transactional-belief-commit-2026**: retraction triggering typed, machine-verified cascading
  repair of derived records (Sec.3.4, 5.5M-state bounded enumeration, zero violations) — belief
  revision with a formally verified propagation guarantee.
- **toki-bitemporal-operator-algebra-contradiction-2026**: a semiring-based provenance algebra with
  four soundness theorems proving three axes orthogonal (Sec.2.2, 3.1, 3.3) — orthogonality proven,
  not merely asserted, though (see §5 of `06_hypothesis_tests.md`, H1) on a different triple than
  D-System's O/E/L.

Belief revision, as a formal discipline with axioms, proofs, and multiple 2026 agentic
instantiations (Kumiho, MemTX), is mature and thoroughly documented in this matrix.

---

## 5. Argumentation

D-System's H3 (provenance influencing conflict resolution) and the general notion of claims that
support or challenge one another map onto computational argumentation theory:

- **evidence-graphs-fair-computation-defeasible-reasoning-2021** (EVI): typed support/challenge
  relations, transitively propagating, tracing directly to Dung (1995), Cayrol & Lagasquie-Schiex
  (multiple 2009-2013 papers per the corrected `derivative_ancestor` field), and Toulmin (1958) —
  "a 2021 OWL-formalized instantiation of a 1958-2005 lineage, not an independent invention"
  (matrix row `strongest_dsystem_overlap`). The paper states directly that resolving a flagged
  conflict "ultimately require[s] human judgment" — deliberately not automated.

Support/challenge argumentation graphs over evidence are a mature, decades-old formal tradition
with a real, 17,996-node deployed 2021 instantiation. The one point this campaign found the field
consistently declining to cross — automating the arbitration step on top of the argumentation graph
— is addressed in §H3 of `06_hypothesis_tests.md` and is the "new integration" half of that
hypothesis's status, not a gap in the argumentation component itself.

---

## 6. Truth Discovery

D-System's H4 (independence-aware convergence: independent corroboration strengthens weight,
derivative agreement is discounted) is the organizing question of the truth-discovery literature:

- **dong-berti-equille-srivastava-truth-discovery-copying-detection-2009**: "the HMM-detected
  copier/independent classification feeding a Bayesian truth-decision model that discounts copied
  (derivative) votes is the named foundational instance of 'discount agreement that shares an
  ancestor rather than counting it as independent corroboration'" — the field's own named
  foundational precedent, though scoped to a fixed, closed set of structured web sources rather than
  a derivation-graph topology.
- **goldman-experts-which-ones-should-you-trust-2001**: a peer-reviewed, general,
  agent-model-agnostic, closed-form Bayesian proof (Sec.4, Eqs.1-6') that a "blind follower" of
  another witness adds zero extra evidential weight — foundational to an entire expert-testimony
  sub-literature, extended by `reliability-testimonial-norms-scientific-communities-synthese`
  (Mayo-Wilson 2014, eight proven theorems, 4,500-network simulations on how topology affects
  reliability).
- **provenance-based-interpretation-multi-agent-information-analysis-2020** (DIVE): a real, live,
  implemented system with three confidence-propagation policies over multi-path corroborating
  evidence (Fig.2), at a demonstrated (not merely stated) mixed human-machine scope — though the
  topology-aware, shared-lineage-discount half is named only as future work (Sec.3.3).
- **epistemic-sybil-resistance-bara-2026**: a closed-form, graph-topological discount
  (kappa_m = 1/(1+rho(m-1)), Sec.5.2 Corollary 2) for corroborating reports sharing an evidentiary
  root — the closest graph-topological formalization found, but scoped to AI-agent report
  multiplicity only, with practical protocol left as an open problem (Sec.9).

The general principle H4 states — independent corroboration counts, derivative agreement does not —
is a foundational, 25-year-old, mathematically proven result (Goldman 2001) with a direct
2009 computational instantiation (Dong et al.) and a 2026 graph-topological formalization (Bara).
`06_hypothesis_tests.md`'s H4 block, re-derived clean-room by `LIT-09 H4R` (2026-09-19) from the
evidence alone, now assesses both the review-instructions' general phrasing and the frozen
register's sharper graph-topological phrasing of H4 at the same status, `LIKELY_ALREADY_KNOWN`,
retiring the general/graph-topological split this section previously carried. Two further 2026
sources found after that split was first drawn — `grading-narrators-isnad-rijal-claim-provenance-2026`
(ISNAD) and `not-all-agreement-counts-as-corroboration-2026` (PACT), neither among the bullets above —
close the thin graph-topological coverage the split had rested on; see `06_hypothesis_tests.md`'s H4
block for their full assessment. The coordinator-pre-framing caveat this section previously carried
is resolved along with the split: `H4R` was dispatched to re-derive the split, or its absence,
clean-room from the evidence and without being told what to conclude, and its finding is that the
split does not hold. This document reports that status; it does not re-derive it.

---

## 7. Agent Memory

D-System's Knowledge Construction & Management system, considered purely as a persistent store an
agent reads from and writes to, is one instance of a densely populated 2024-2026 field:

- **zep-graphiti-temporal-kg-agent-memory-2025**, **mythologiq-agent-memory-oss**,
  **subit-wiki-epistemic-hmm-oss**, **eywa-provenance-grounded-memory-joshi-2026**,
  **burns-groth-agentic-ontological-notebook-memory-2026**, **em-llm-human-inspired-episodic-memory-infinite-context-2024**,
  **symbolic-memory-prolog-oss**, **solozobov-verify-gated-completion-admission-control-2026**: eight
  distinct agent-memory systems in this matrix alone, spanning commercial (Zep), peer-reviewed/ICLR
  (EM-LLM), and open-source single-author (MythologIQ, SUBIT, symbolic-memory) implementations.
- `06_hypothesis_tests.md`'s H1 block records that two of these — MythologIQ and SUBIT — come closer
  than any other source found in the whole campaign to D-System's specific orthogonal
  ontological+epistemic+lifecycle triple, without either one actually combining the right axis
  *content* with genuine independence and field maturity (see §"What remains," below).

Agent memory as a category, and even multi-axis classification schemes on memory records within
that category, are established and actively worked ground. What is not established anywhere in this
matrix is D-System's specific three-axis content combined with proven independence and an
established (not single-author, weeks-old) comparator family — this is the one genuine hole this
component leaves, carried forward below.

---

## 8. Design Rationale

D-System's H7/H9 decision-provenance claims are close to a direct restatement of the
design-rationale tradition founded by Jansen & Bosch (2005):

- **jansen-bosch-architecture-as-decisions-wicsa-2005**: "a software archictecture = dd1 + dd2 +
  ... + ddn" (p.86; [sic], the paper's own typo, preserved per the matrix's `verbatim_notes`) —
  architecture as an accumulated, non-overwritten set of decision objects, with decisions
  explicitly capable of generating new requirements and an explicit bilateral-traceability
  requirement, 2005. component_overlap=5 in the first assessment (re-derived on review to 3;
  disputed and unapplied per the owner's ruling).
- **zimmermann-et-al-managing-architectural-decision-models-2009**: a formal extension of Jansen &
  Bosch ("Our metamodel extends that from [1] and [5]," p.5) adding a typed outcome-status
  lifecycle (open/implied/resolved), 8 integrity constraints, and per-outcome actor provenance
  (`changedBy`) — evaluated on 389 real decision issues via the publicly deployed Architectural
  Decision Knowledge Wiki (200+ users), though the review found the triggers/integrity-constraint
  engine itself "implemented in an advanced prototype that is not yet publicly available" (Sec.6.3).
- **de-boer-architectural-knowledge-management-dissertation-2009**: names "architectural knowledge
  vaporization" as its central problem, 15+ years before D-System's own conception, proposing
  decisions-plus-rationale-plus-alternatives as first-class knowledge objects.
- **decision-oriented-programming-aporia-2026**: a 2026 agentic coding tool self-described (Sec.2) as
  "an application of QOC" (MacLean, Young, Bellotti & Moran 1991) — a 2026 instantiation of a
  35-year-old design-rationale notation.

The idea that architectural/implementation decisions should be persistent, structured, first-class
knowledge objects distinct from the artifacts they produce is a 20+-year-old organizing idea of an
entire research tradition (IBIS, QOC, Jansen & Bosch, Zimmermann et al.), with a direct 2026 agentic
application.

---

## 9. Requirements Traceability

D-System's H7/H9 also restate the requirements-traceability tradition's central promise —
bidirectional linkage from requirement to implementation and back:

- **model-based-digital-threads-sociotechnical-systems-2022**: Fig.2.18, a typed, directional
  (trace/refine/realize) graph spanning Requirement -> Specification -> Implementation -> Test Case
  -> Field Performance, explicitly built "to compare expected behavior (requirements) and actual
  system performance," peer-reviewed book chapter (Crossref-confirmed).
- **assumptions-management-software-development-mapping-study-2018**: a 134-study systematic mapping
  documenting "Assumptions Tracing and Monitoring" as the least-studied and least-tooled of twelve
  assumption-management activities — evidence the traceability *problem space* is well-surveyed even
  where specific tooling (H10's target) is thin.
- The awareness-requirements lineage — **sawyer-bencomo-whittle-letier-requirements-reflection-icse-2010**,
  **souza-lapouchnian-robinson-mylopoulos-awareness-requirements-seams-2011**,
  **requirement-evolution-requirements-adaptive-systems-seams-2012** (EvoReqs, implemented, OSGi,
  open-source), **runtime-verification-self-adaptive-changing-requirements-2023** — a 2010-2023,
  peer-reviewed, multi-venue (ICSE, SEAMS) body of work on requirements as runtime-introspectable,
  monitorable objects.

Requirements traceability, including its runtime-monitoring and self-adaptive extensions, is a
mature, multi-decade, multi-venue academic tradition. As `06_hypothesis_tests.md`'s H11 block
records in detail, this tradition repeatedly names the specific loop D-System's H11 proposes
(runtime evidence revising the requirements/knowledge structure itself) without building it as a
general, evidence-driven mechanism — the field's most-implemented member (EvoReqs) closes a
narrower, rule-triggered loop over a closed, analyst-authored vocabulary instead.

---

## 10. ADRs

Architecture Decision Records are the applied, tooling-facing sibling of the design-rationale
tradition (§8), and are separately represented in the matrix as an automation target:

- **dhar-vaidhyanathan-varma-agenticakm-2026-arxiv** (AgenticAKM): a multi-agent
  Extraction/Retrieval/Generation/Validation pipeline that reads a code repository and generates
  ADRs in the field's standard rationale-bearing template, validating them against source code and
  prior ADRs, public source (github.com/sa4s-serc/AgenticAKM), component_overlap=4.
- **jansen-bosch-architecture-as-decisions-wicsa-2005** and
  **zimmermann-et-al-managing-architectural-decision-models-2009** (§8, above) are ADRs' direct
  theoretical ancestors — Zimmermann et al.'s outcome-status/integrity-constraint model is the
  formal ADR metamodel AgenticAKM's template instantiates.

Generating, validating, and iteratively refining ADRs with a multi-agent pipeline is a working,
publicly available 2026 system built directly on the 2005-2009 ADR lineage — not a gap.

---

## 11. Digital Thread

D-System's H7 (idea-to-runtime lineage) restates the systems-engineering "digital thread" concept,
independently coined and independently applied at least twice in this matrix:

- **model-based-digital-threads-sociotechnical-systems-2022**: traces "digital thread" to a 2013 USAF
  report (Sec.2.2.1); Fig.2.18 (§9, above) is a structural analogue spanning five of the
  methodology's flagged adjacent stages.
- **us20250165226a1-ai-digital-thread-patent** (Roper et al., Istari Digital): a granted US patent
  (US12461717B2) whose specification describes digital threads "linked across different stages...
  from concept, design, testing, to production," commercially operated as the "Interconnected
  Digital Engineering Platform"; its own "digital thread" definition cites the DAU/DoD Digital
  Engineering Strategy (2018) — a different coinage than the 2022 chapter's 2013 USAF citation, two
  independent namings of the same underlying concept, not one shared ancestor. Per the owner's
  ruling on this campaign, a patent's whole published disclosure — specification and claims together
  — is prior art; read that way, this source contributes stage-spanning evidence against H7/H9. Read
  strictly against the granted claims alone (the position an unresolved, owner-flagged scoring-rule
  dispute on this row would require), the contribution narrows to the intent-to-code-artifact segment
  specifically.

Digital thread, as a named concept describing exactly D-System's idea-to-runtime lineage claim, has
two independent 2013-2018 governmental coinages, a 2022 peer-reviewed academic treatment, and a
granted 2025 US patent commercially operated as a product.

---

## 12. Software Provenance

Distinct from the general PROV-O substrate (§2), software-specific provenance — tracking where a
piece of code, a decision, or a requirement came from across a development lifecycle — is directly
represented:

- **procko-provtracer-erau-dissertation-2025**: an automated, ambient (screenshot/input-event-driven,
  GPT-inferred) capture pipeline producing a PROV-O+BFO provenance knowledge graph aimed at
  "traceability," "explainability," "reproducibility," and extracting "developer rationale" — a 2025
  dissertation converging, independently, on the same "knowledge vaporization" problem
  `de-boer-architectural-knowledge-management-dissertation-2009` names 15+ years earlier.
- **us20250165226a1-ai-digital-thread-patent** (§11, above): granted, commercially operated software
  provenance from intent to generated code artifact, with feedback-based model retraining.
- **omniscientist-coevolving-ecosystem-human-ai-scientists-2026**: its ContributionLedger is "a
  scientific-credit specialization of the classical nanopublication (Groth, Gibson & Velterop, 2010)
  and PAV/PROV-O provenance traditions" applied to a development-adjacent (scientific-production)
  pipeline, empirically evaluated (HLE case study, 0.22 vs. 0.10 vs. 0.00 accuracy).

Automated capture of development-time provenance, including decision rationale specifically, is an
active 2025 dissertation topic and a granted 2025 patent, independently converging on the same
underlying problem D-System's Implementation & Experience system addresses.

---

## 13. Observability

D-System's H11 (runtime telemetry becoming provenance-bearing evidence) presupposes an
observability layer feeding structured signals upstream. This exists as a working mechanism, though
narrower in scope than H11 claims:

- **bajaj-ai-augmented-closed-loop-quality-engineering-2026**: "the only ranked H11 source that both
  implements a runtime-evidence-to-upstream-artifact feedback formula and reports quantitative
  before/after results" — production defect-severity and incident-impact signals measurably changing
  a requirement-linked risk score used in later release decisions (Sec.3.5-3.6) — though the
  "knowledge structure" revised is a single derived numeric feature, not the requirement's content or
  any decision/rationale artifact, and the dataset is semi-synthetic.
- **tgms-agent-native-bitemporal-graph-2026** and **mythologiq-agent-memory-oss** both implement
  runtime-trace-correlation as a named, schema-level artifact type (the latter's
  `runtime-trace-correlation` schema, part of its decision -> execution -> runtime-evidence ->
  knowledge-update chain, confirmed against the implementing code on review).

Feeding structured runtime signals back into an upstream artifact is a working, quantitatively
evaluated 2026 mechanism (Bajaj et al.) and a modeled schema element in at least one open-source
memory system (MythologIQ). What is not demonstrated anywhere in this matrix is that mechanism
operating on decision- or rationale-bearing knowledge specifically, rather than a single derived
metric or opaque execution state — the same gap §9's discussion of H11 names.

---

## 14. MAPE-K

D-System's overall closed-loop framing — observe, reason, act, and feed the result back into
knowledge that also drives the next action — restates the Monitor-Analyze-Plan-Execute-over-Knowledge
control loop:

- **ibm-architectural-blueprint-autonomic-computing-whitepaper-2006**: "an extremely widely cited,
  foundational, vendor-neutral control-loop architecture... for closing the loop between observed
  system state and corrective action — structurally the deepest and most explicit ancestor available
  to this campaign for D-System['s runtime-to-knowledge claim]." (The primary whitepaper itself could
  not be directly retrieved after seven independent access attempts across dead IBM hosting domains
  and a rate-limited archive.org; this row's assessment rests on the paper's extremely well
  documented secondary coverage, recorded here per the campaign's access-limitation discipline —
  `access_limitation: secondary_coverage`, not presented as a full-text read.) Its "Knowledge" is
  short-lived, single-control-loop operational state, not an append-only, cross-session history, and
  the architecture is explicitly oriented toward reducing human involvement.
- **requirement-evolution-requirements-adaptive-systems-seams-2012** (EvoReqs, §9 above): the
  campaign's strongest *built* instance of a MAPE-K-shaped loop closing onto a requirements model
  specifically — but the mutation vocabulary is closed and hand-authored, a rule-triggered control-
  loop reaction, not evidence-driven revision of arbitrary scope.

MAPE-K is a foundational, near-universally cited 2003-2006 control-loop pattern, and its
requirements-specific 2012 instantiation (EvoReqs) is real and implemented. What MAPE-K's own
2006 framing and EvoReqs' 2012 implementation share, and what distinguishes both from D-System's H11
claim, is addressed directly below.

---

## What remains after the decomposition

Fourteen for fourteen, every one of D-System's named components has an established, evidenced,
often multiply-independent precedent in this matrix. That is the anti-novelty case at full strength,
and it is strong: fourteen of fourteen decomposition targets are backed by primary-text-read,
locator-cited matrix rows, several with formal proofs (AGM, MemTX, toki), production deployments
(Zep, Kumiho, LangGraph), or granted patents (Istari).

Against that decomposition, `06_hypothesis_tests.md`'s eleven hypothesis verdicts place nine of the
eleven at `LIKELY_ALREADY_KNOWN` (H2, H4, H7, H8's review-instructions phrasing, H9) or
`KNOWN_COMPONENT_NEW_INTEGRATION` (H3, H5, H6, H8's frozen-register
phrasing, H10) — every one of these is a case where the decomposition above accounts fully for the
mechanism, and what D-System adds is combination, not invention. That is not "nothing remains" in
the trivial sense; recombining fourteen established components into one coherent two-system
architecture is itself a genuine act of design, and H6's own verdict (`KNOWN_COMPONENT_NEW_INTEGRATION`)
records that no single found system substantially subsumes D-System's specific two-system,
dual-domain pairing even though each half has an independently demonstrated analog elsewhere
(OmniScientist for the knowledge-construction side, AgenticAKM/the ADR lineage for the
development-lifecycle side). But per this campaign's own stated method (§14, and the operating
distinction between `NOVEL` and the four permitted statuses), "known components, integrated" is not
a mechanism gap; it is exactly what a successful anti-novelty case is supposed to find, and this
document finds it for nine of eleven hypotheses.

Two points do not fully decompose, and it would misrepresent the campaign's own findings to claim
otherwise. Both carry `INSUFFICIENT_EVIDENCE` in `06_hypothesis_tests.md` — a status this
document must not upgrade, since re-deriving hypothesis status is exactly the reconciliation task
item 0 of this dispatch already performed, and this file does not repeat or second-guess it. Naming
them here is not a claim that they survive the decomposition as distinct; it is a report of what the
decomposition itself could not close, which `08_surviving_distinctions.md` then carries forward
under its own, separate discipline. (H4's graph-topological reading previously stood here as a third
point; `06_hypothesis_tests.md`'s H4 block now assesses that reading, together with the general
phrasing, at `LIKELY_ALREADY_KNOWN` — see §6 above — so it has no subject left in this list and is
removed rather than carried as an empty entry.)

1. **H1's specific axis content.** Agent memory (§7) is a mature field, and two of its members
   (MythologIQ, SUBIT) come structurally close to an orthogonal multi-axis classification — but
   neither combines D-System's specific ontological+epistemic+lifecycle *content* with genuine
   independence and an established comparator family. `06_hypothesis_tests.md`'s own two-condition
   rule is explicit about why this does not license `POTENTIALLY_DISTINCT`: the search satisfied
   condition 1 (a dedicated, multi-strategy, primary-text-verified search) but not condition 2 (a
   mature comparator family whose best member instantiates the same mechanism) — the closest
   candidates are ten-weeks-old, single-author, unreviewed repositories, not an established
   tradition. This is a hole in the *search's findings*, not a proven gap in the *field*.

2. **H11's runtime-to-knowledge closure into decision/rationale content.** §13-14 above establish
   that runtime signals feeding back into an upstream artifact is real and quantitatively evaluated
   (Bajaj), and that a requirements-specific closed loop is real and implemented (EvoReqs) — but the
   first closes onto a single derived metric, and the second closes onto a closed, hand-authored
   mutation vocabulary rather than evidence-derived revision of the knowledge structure's actual
   content. The field that names this exact gap most directly (the 2010-2023 awareness-requirements
   lineage) states it, repeatedly and explicitly, as future work rather than building it. As
   `06_hypothesis_tests.md`'s H11 block puts it: a mature field that has spent over a decade naming
   this exact gap, and still has not searched up a working instance of it, is evidence worth
   weighing in synthesis, but is not, by this file's own rule, sufficient on its own to call the
   mechanism absent from the wider field.

Neither of these two is a distinctiveness claim. Each is, precisely, a point where this campaign's
search — bounded by the coverage caveat stated at the top of this document — could not complete the
decomposition either way. The decomposition is not a failure at these two points; it is where the
decomposition's own evidentiary bar (a mature, on-topic comparator family whose best member shows the
same mechanism) was not met by what this campaign found, distinguished explicitly from a bar this
campaign proved could not be met. That distinction, and what if anything should be inherited or
investigated further at each of the two points, is `08_surviving_distinctions.md`'s task.
