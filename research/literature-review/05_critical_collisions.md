# Critical collisions

One section per `critical_collision: yes` row in `04_evidence_matrix.csv` — 19 rows, derived
directly from that file (`component_overlap_score >= 4` and/or `architecture_overlap_score >= 4`
and/or a direct H1-H11 falsification claim and/or spanning four-plus adjacent stages of the
Reasoning→Knowledge-Update chain, per `research/literature-review/CLAUDE.md` §11). Each section
records the overlap, what the source would falsify if the overlap held at full strength, and
`second_review: pending` — no verdict here is anticipated; `LIT-06 X2` folds independent
reviewers' findings into `06_hypothesis_tests.md` after this section is written. Sections follow
the order the coordinator cross-checked the 19-row derivation against.

---

## 1. decision-oriented-programming-aporia-2026

Kasibatla, Rothkopf, Peleg, Pierce, Lerner, Goldstein, Polikarpova: *Decision-Oriented
Programming with Aporia*, arXiv:2604.05203, submitted 6 Apr 2026.

**Overlap.** component_overlap=4, architecture_overlap=3. The single strongest collision in its
own batch: a 2026 agentic coding tool built around D-System's own H7 (decisions as persistent,
structured, code-traceable objects), H9 (bidirectional decision<->code traceability via
generated test suites) and, more weakly, H8 (a goal-scoped elicit/decide/implement/validate loop
as an implicit context boundary) — evaluated in a 14-participant user study showing "79% lower
likelihood of mismatches between... mental model and the actual implementation" versus a
baseline coding agent (p.2). Explicitly self-described (Sec.2) as "an application of QOC" — the
1991 design-space-analysis notation (Sec.2, citing MacLean, Young, Bellotti & Moran 1991) — not
a new decision-representation primitive.

**What it would falsify.** At full strength this would falsify H7's claim that "software
functionality can be represented as downstream result of an append-only lineage connecting
ideas... decisions... requirements... artifacts... verification" and H9's bidirectional
traceability claim, at least for the decision-to-code segment of that chain. It does not, on the
evidence read, falsify H2 (transitions are edited/revoked in place, not append-only — "no
append-only transition history... decisions are edited/revoked in place") or H3/H4 (no
multi-actor provenance/authority/conflict model). It says nothing about H1, H5, H6, H10, or H11:
there is no upstream knowledge-construction system, no requirement/plan/deployment/runtime
stage, and Aporia is single-agent, single-goal, not a multi-actor or cross-session architecture.

second_review: disputed: both scores and the flag confirmed correct, but actor_model and
temporal_model were factually wrong and are corrected in the matrix.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3, flag fires on the
component trigger alone. H9 is the strongest of the three challenged hypotheses (H7;H8;H9); H7 is
not falsified because Aporia edits/revokes decisions destructively in place rather than
append-only; H8 is the weakest, correctly hedged.

**Independent reviewer position.** Re-derives the identical scores (component 4, architecture 3)
and concurs the flag rests entirely and correctly on the component trigger — the four-adjacent-
stages trigger does not fire (longest consecutive run is Execution->Artifact->Verification = 3,
broken by real gaps at Requirement and Plan). Concurs H9 is strongest and H7 is not falsified for
the same append-only-vs-destructive-edit reason. Diverges on two factual fields: `actor_model`
stated "a single coding agent" and "no multi-agent... actor model," but Sec.3.3 (p.4) — a section
the row's own evidence_locator never cites — describes Aporia internally orchestrating three
specialized agents (questioner, planner, implementer), each a separate Claude Code instance under
the Agent Client Protocol; the user-facing count of two actors is correct, but the system itself is
internally multi-agent. `temporal_model` was coded NOT_DETERMINABLE_FROM_ACCESS when Sec.6.3
directly states Aporia lacks a navigable history — a citable absence, not an unread gap. Also
identifies two citation-location errors (a misnumbered Pail reference, and the "application of QOC"
quote misattributed to Sec.2 rather than Sec.3.2).

**Resolution.** The reviewer's own bottom line is that neither hypothesis reading (over- or
understated) needs adjusting on this row — direction is "NEITHER." `actor_model` and
`temporal_model` are corrected in `04_evidence_matrix.csv`, along with the `verbatim_notes` and
`evidence_locator` citation errors. No score, flag, or hypotheses_challenged value is changed.

---

## 2. dhar-vaidhyanathan-varma-agenticakm-2026-arxiv

Dhar, Vaidhyanathan, Varma: *AgenticAKM: Enroute to Agentic Architecture Knowledge Management*,
arXiv:2602.04445 (also AGENT'26 @ ICSE 2026), submitted 4 Feb 2026.

**Overlap.** component_overlap=4, architecture_overlap=3. A multi-agent pipeline
(Extraction/Retrieval/Generation/Validation) that reads a code repository, retrieves existing
architectural knowledge, generates ADRs in the field's standard rationale-bearing template, and
validates them against source code and prior ADRs with an iterative refinement loop — public
source at github.com/sa4s-serc/AgenticAKM. A direct 2026 agentic collision with H6 (integrated
human-agent knowledge evolution — "architect in the loop" is named future work, Sec.6) and H9
(bidirectional decision<->code traceability), and narrowly with H3/H10 (the Validator's
single-hop contradiction check against existing ADRs and its refinement loop).

**What it would falsify.** At full strength this would falsify H6's claim that "the full
synthesis may be distinct even if primitives are known," by being a working multi-agent
architecture-knowledge pipeline already spanning generation, retrieval, and validation. It would
not falsify H2 (refinement overwrites drafts rather than preserving prior versions — no
append-only history), H4 (no independence-aware convergence weighting across sources), or H7 as
D-System frames it (this system runs the traceability direction backward from D-System's own
H7 claim: requirements are retrieved to constrain decisions, not derived from them). It says
nothing about H1, H5, H8, H10, or H11 — the system recovers existing architecture from a
snapshot; it does not model the upstream idea/evidence/reasoning construction that produced it,
nor a persistent cross-session knowledge structure.

second_review: confirmed, with one factual correction (temporal_model). Reviewer would score H2 as
a stronger challenger than the row's "challenged" framing suggests.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3, flag fires on the
component trigger alone (with directly-falsifies for H6 arguably a second route). Falsifies H6's
"the full synthesis may be distinct" framing by being a working multi-agent AKM pipeline already
spanning generation, retrieval, and validation; does not falsify H2, H4, or H7 as D-System frames
it.

**Independent reviewer position.** Confirms both scores exactly and confirms the H6/H9
non-falsification conclusions via full-text read including a direct visual inspection of Figure 1
(needed because the diagram's box labels are not extractable by text-only PDF/HTML converters — one
of two independent extraction attempts on this source failed for exactly this reason). Finds one
factual error: `temporal_model` was coded NOT_DETERMINABLE_FROM_ACCESS, but the complete 4-page
preprint is the paper's entire content and was read in full — no temporal/versioning model exists
anywhere in it, so the correct code is NOT_APPLICABLE, per the evidence contract's own guidance that
absence is recorded only after reading a source's full scope.

**Resolution.** `temporal_model` corrected to NOT_APPLICABLE in `04_evidence_matrix.csv`. Direction
is "NEITHER" overstated nor understated on the row's own terms; no score, flag, or
hypotheses_challenged value is changed.

---

## 3. em-llm-human-inspired-episodic-memory-infinite-context-2024

Fountas, Benfeghoul, Oomerjee, Christopoulou, Lampouras, Bou-Ammar, Wang (Huawei Noah's Ark
Lab / UCL): *Human-inspired Episodic Memory for Infinite Context LLMs (EM-LLM)*, ICLR 2025
(arXiv:2407.09450, first posted Jul 2024).

**Overlap.** component_overlap=4, architecture_overlap=2. A peer-reviewed, publicly released
(github.com/em-llm/EM-LLM-model), rigorously evaluated mechanism for segmenting continuous LLM
context into bounded episodic units via Bayesian-surprise boundary detection, retrieved by a
combined similarity-plus-temporal-contiguity process, demonstrated at 10M-token scale. Directly
relevant precedent for any "episodic memory for agents" or "topology-aware context transfer"
claim (H5).

**What it would falsify.** At full strength this would falsify the narrow reading of H5 that
"context selection beyond plain semantic similarity is uncommon" — EM-LLM is a peer-reviewed,
scaled counter-example. It would not falsify H5's fuller claim, since it has no reasoning-
lineage-, evidence-, dissent-, authority-, or convergence-aware retrieval — it organizes and
retrieves raw token history for one LLM's own context window, with no human/agent actor modeled
by the method itself. It says nothing about H1-H4 or H6-H11: no knowledge-state ontology, no
provenance, no actor/authority model, no decision/requirement/artifact/verification linkage. Its
own segmentation and retrieval mechanisms are named (Sec.2.2) as a 2024/2025 computational
instantiation of a 2002-2017 cognitive-science lineage (Zacks & Swallow's Event Segmentation
Theory, Baldassano et al., Howard & Kahana's Temporal Context Model) — a derivative application,
not an independent invention, per this campaign's independence-discipline rule.

second_review: disputed: reviewer re-derives component_overlap to 3 (not 4) and argues the flag
should not stand; score and flag left unchanged as a recorded judgment dispute, not a factual
correction.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=2, flag fires on the
component trigger. A peer-reviewed, scaled (10M-token), publicly released mechanism directly
relevant to H5, falsifying only the narrow reading that "context selection beyond plain semantic
similarity is uncommon" — not H5's fuller epistemic-lineage/dissent/authority/convergence claim. No
other hypothesis touched.

**Independent reviewer position.** Confirms architecture_overlap=2 and the H5 non-falsification
conclusion via a full 39-page read including the specific retrieval mechanism section (Sec.3.4,
p.7) that the row's own evidence_locator never cites — its locator spans only pp.1-4 (abstract
through Sec.3.1/Fig.1), a span from which the row's substantive description is fully derivable
without needing the method section it is nominally about. On this basis the reviewer re-derives
component_overlap to 3: EM-LLM contributes three genuine primitives (surprise-based segmentation,
graph-modularity boundary refinement, similarity-plus-contiguity retrieval), clearing "multiple
relevant primitives" but not "strong mechanism overlap," because the actual selection criteria do
not substantially match D-System's mechanism — the row's own prose (retrieval_context_model,
strongest_difference) already states H5's epistemic dimensions are "entirely outside its scope" yet
assigns a component score that contradicts that same prose. Under the reviewer's re-derivation, the
sole trigger (component>=4) fails and critical_collision should read NO.

**Resolution.** This is a scoring judgment, not a factual error in the payload's terms —
recorded here as disputed per the coordinator's addressing; `component_overlap_score` and
`critical_collision` are left exactly as they stand in `04_evidence_matrix.csv`. Had the reviewer's
re-derivation been authorized, this row's flag would be dropped.

---

## 4. evidence-graphs-fair-computation-defeasible-reasoning-2021

Al Manir, Niestroy, Levinson, Clark: *Evidence Graphs: Supporting Transparent and FAIR
Computation, with Defeasible Reasoning on Data, Methods, and Results*, bioRxiv 2021 / IPAW
2020+2021 (Springer LNCS 12839).

**Overlap.** component_overlap=4, architecture_overlap=3. An OWL-formalized, PROV-O-extended
ontology (EVI, published at w3id.org/EVI# under MIT license) making support/challenge relations
among computational results, data, methods, and software first-class, transitively-propagating,
machine-reasoned graph edges — deployed at real scale (17,996-node evidence graph over a
5,957-infant NICU study) via the FAIRSCAPE microservices framework and a Stardog RDF store.
Structurally the closest single match in its batch to H2 (typed transitions preserving
reasoning/evidence relationships) and H3 (provenance as conflict-relevant input), and a working
precedent for H9's backward traceability and H10's narrow blast-radius propagation ("if C
challenges A and A supports B, then C challenges B").

**What it would falsify.** At full strength this would falsify H2's claim that typed,
append-only transitions preserving reasoning/evidence relationships (distinct from plain
semantic edges) are a useful, uncommon representation — EVI is exactly that, deployed. It would
not falsify H3 as D-System states it, since the paper is explicit that resolving a flagged
conflict "ultimately require[s] human judgment" — deliberately not automated arbitration. It
says nothing about H4 (no independence-aware convergence weighting), H1/H5-H8/H11 (no
epistemic/ontological state classification beyond support/challenge, no software-development
lifecycle at all — confined to the scientific-evidence side of D-System's proposed two-system
split), and no AI-agentic actors are modeled. Its argumentation-theoretic support/challenge
relations trace directly to Dung (1995), Cayrol & Lagasquie-Schiex (2005), and Toulmin (1958) —
a 2021 OWL-formalized instantiation of a 1958-2005 lineage, not an independent invention.

second_review: confirmed, with two factual corrections (derivative_ancestor, temporal_model).
Reviewer would score H2 as a STRONG rather than marginal challenger. Surfaces an open contract
question (see the "adjacent stages" note below).

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3; flag fires on the
component trigger, with directly-falsifies arguably a second independent route for H2. Structurally
the closest single match in its batch to H2 and H3; does not falsify H3's arbitration half (the
paper is explicit that resolving a flagged conflict "ultimately require[s] human judgment").

**Independent reviewer position.** Confirms both scores exactly and confirms the H2/H3/H9 mapping
via a complete bioRxiv v3 read (all 14 pages plus the full 73-item reference list). Goes further
than the row on H2: `directlySupports` is a first-class subproperty layered on but distinct from
base PROV `used`/`generatedBy`, deployed at 17,996-node production scale — the reviewer judges this
plausibly meets H2's own falsification bar ("equivalent... provenance architecture") and recommends
06 weigh it as a strong, not marginal, challenger. Finds two factual errors: `derivative_ancestor`
cited "Cayrol & Lagasquie-Schiex, On the Acceptability of Arguments in Bipolar Argumentation
Frameworks, 2005" — no such reference exists in this paper's 73-item bibliography; the paper's
actual cited works (Methods Sec.2, p.4, "as developed by Cayrol and others [31, 37, 38]") are three
different Cayrol & Lagasquie-Schiex papers (2009, 2010, 2013). `temporal_model` was coded
NOT_DETERMINABLE_FROM_ACCESS though the full text was read end to end and never addresses
versioning. Separately flags a contract-level ambiguity: under a strict-contiguous reading of
"adjacent stages" the four-adjacent-stages trigger does not fire (longest run is
Execution(partial)->Artifact->Verification(indirect) = 3); under a looser "any four, not necessarily
contiguous" reading it would fire (5 stages touched). `PLAN-023.03` does not specify which reading
applies. This does not change this row's outcome (the component trigger already fires) but will
elsewhere in the batch.

**Resolution.** `derivative_ancestor` and `temporal_model` corrected in `04_evidence_matrix.csv`.
The "adjacent stages" ambiguity is recorded here as an open contract question per the coordinator's
addressing — not resolved, and `PLAN-023.03` is not edited. No score, flag, or
hypotheses_challenged value is changed.

---

## 5. graph-native-cognitive-memory-belief-revision-semantics-2026

Park, Y.B. (Kumiho Inc.): *Graph-Native Cognitive Memory for AI Agents: Formal Belief Revision
Semantics for Versioned Memory Architectures*, arXiv:2603.17244, 18 Mar 2026.

**Overlap.** component_overlap=5, architecture_overlap=4 — the matrix's ceiling component score.
A graph-native memory architecture combining immutable versioned revisions, typed dependency/
provenance edges, mutable tag pointers, and URI-based addressing, formally proven to satisfy
several AGM/Hansson belief-revision postulates; production/commercial (core graph server at
kumiho.io, open-source SDK at github.com/KumihoIO). The closest single match in this campaign to
H2 (typed transition semantics preserving reasoning memory) and a strong precedent for H7/H9.

**What it would falsify.** At full strength this would falsify H2 outright — the paper's own
central contribution is a formal correspondence proof between AGM and a working, deployed
memory system's operational semantics, which is precisely H2's claim made rigorous. It would
weaken but not fully falsify H7/H9, since the formal correspondence is explicitly scoped
("a deliberately simple propositional logic over ground triples," with the Recovery postulate
rejected by design and K*7/K*8 left open) and the paper's own strongest benchmark result
(LoCoMo-Plus 93.3%) carries a self-disclosed independent-reproduction gap (mid-80% range). No
described conflict-arbitration, independence-aware convergence, or epistemic-blast-radius
mechanism was read in the sections covered — H3, H4, H10 are not addressed. The paper is
explicit about its own status: "we contribute not novel individual components... but a novel
architectural synthesis," self-identifying as a synthesis of concurrent 2025 systems (Graphiti,
Mem0, A-MEM) rather than a component-level invention, and naming Alchourron, Gardenfors &
Makinson (1985) as its own "central formal contribution" ancestor.

second_review: disputed: reviewer re-derives component_overlap to 4 (not 5) and architecture_overlap
to 3 (not 4); flag survives on the component trigger alone. Six factual corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=5, architecture_overlap=4 (the matrix's ceiling
component score). A graph-native memory architecture combining immutable versioned revisions, typed
dependency/provenance edges, and formal AGM/Hansson belief-revision correspondence proofs; the
closest single match in the campaign to H2. Falsifies H2 outright per the row; weakens but does not
fully falsify H7/H9. The paper self-identifies as "architectural synthesis," not component
invention.

**Independent reviewer position.** Both overlap scores overstated by one point each — component 4
not 5, architecture 3 not 4 — though the flag stands on the component trigger alone.
`Component`: the proof is scoped to "a deliberately simple propositional logic over ground triples"
with Recovery rejected and K*7/K*8 left open; no actor-authority arbitration or convergence/
independence weighting exists (confirmed absent, not merely unread); conflict handling is
last-write-wins supersession, which the paper itself contrasts with Letta's reconciliation.
`Architecture`: Requirement/Specification/Plan/Verification/Deployment/Runtime Evidence are
confirmed genuinely absent from the full text; Decision has no schema; Execution is TTL session
namespacing only — one deep subsystem (Artifact) plus one partial (Knowledge Update), not
"near end-to-end." Six fields were also miscoded NOT_DETERMINABLE_FROM_ACCESS or otherwise wrong
though the same freely available full text (arxiv.org/html/2603.17244) resolves them:
`conflict_trust_mechanism` and `change_impact_mechanism` are both specified (Sec.2.1, Sec.6.5);
`convergence_independence_mechanism` and `decision_representation` are confirmed absent, not merely
unread; `execution_unit_session_model` is TTL-scoped session keys only; `implementation_availability`
undersells a free self-hostable "Kumiho CE" tier alongside the paid cloud service.

**Resolution.** All six factually miscoded fields corrected in `04_evidence_matrix.csv`. No score,
flag, or hypotheses_challenged value is changed — the reviewer's score disagreement is recorded here
as a judgment dispute per the coordinator's addressing.

---

## 6. jansen-bosch-architecture-as-decisions-wicsa-2005

Jansen, A., Bosch, J.: *Software Architecture as a Set of Architectural Design Decisions*,
WICSA 2005 (read via the open-access republication as Ch.4 of Jansen's 2008 dissertation; the
WICSA proceedings version is paywalled on IEEE Xplore).

**Overlap.** component_overlap=5, architecture_overlap=4 — tied for the matrix's ceiling
component score. The field's foundational reframing of software architecture as a first-class
set of accumulated design decisions ("a software archictecture = dd1 + dd2 + ... + ddn," p.86),
with decisions explicitly capable of generating new requirements and explicitly required to have
a bilateral relationship with the system's actual realization — a near-literal 2005 precursor to
H7 (decisions deriving requirements) and H9 (decision-to-architecture traceability), and the
direct ancestor of the ADR-template mechanism dhar-vaidhyanathan-varma-agenticakm-2026-arxiv
(section 2, above) automates with agents.

**What it would falsify.** At full strength this would falsify H7 and H9's core claims for the
decision/requirement segment of the lifecycle — the paper states the requirement-generation
direction and the bilateral traceability requirement explicitly, twenty years before D-System.
It would not falsify H1 (no epistemic/ontological classification), H2 as D-System's fuller
typed-transition claim (no formal typed-transition schema comparable to Kumiho's AGM-grounded
graph), H3/H4 (no multi-actor authority or conflict-arbitration model), or H5/H6/H8/H10/H11 (no
knowledge-construction system upstream, no artifact/test/deployment/runtime linkage beyond a
named-but-undetailed bilateral goal, human-only, pre-agentic, 2005). Archium is evaluated on a
trivial illustrative example, not benchmarked or deployed. Its own reference list names Kruchten
(2004) as an immediate one-year predecessor and shares Perry & Wolf (1992) as an ultimate
ancestor with de-boer-architectural-knowledge-management-dissertation-2009 — confirming this is
one lineage, not an independent invention.

second_review: disputed: reviewer confirms component_overlap at 3 (not 4) and architecture_overlap
at 2 (agreed); flag left unchanged. Two factual corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=5, architecture_overlap=4 — tied for the matrix's
ceiling. The field's foundational 2005 reframing of architecture as accumulated decisions, a
near-literal precursor to H7/H9, twenty years before D-System. Falsifies H7/H9's core claims for the
decision/requirement segment; not evaluated or deployed at publication.

**Independent reviewer position.** Re-derives component_overlap to 3 ("multiple relevant
primitives") and architecture_overlap to 2, and finds the flag survives only through the
directly-falsifies trigger (genuine idea-level precursors), not mechanism-level equivalence, since
no typed provenance/actor schema, automation, or tool existed at publication — the paper's own
conclusion states "Ongoing and future work on Archium includes the development of tool support"
(Sec.4.8, p.99). The Athena case study is illustrated entirely with hand-drawn diagrams, never a
real system trace. Read pp.79-100 in full, including Sec.4.6/4.7 which the row's own
evidence_locator flagged as unread, and found no multi-actor model or retrieval mechanism anywhere
in those sections either — contrary to the row's NOT_DETERMINABLE_FROM_ACCESS coding for
`actor_model` and `retrieval_context_model`. The row's `implementation_availability` field
understated the gap by focusing on whether Archium "survives" today rather than stating plainly that
no tool existed at the time.

**Resolution.** `implementation_availability`, `actor_model`, and `retrieval_context_model`
corrected in `04_evidence_matrix.csv`. Component and architecture score disagreements are recorded
here as judgment disputes per the coordinator's addressing; `component_overlap_score`,
`architecture_overlap_score`, `critical_collision`, and `hypotheses_challenged` are left exactly as
scored. Had the reviewer's re-derivation been authorized, the correct basis for the flag would be
idea-level anticipation alone, not the mechanism-equivalence framing the row's narrative implies.

---

## 7. log-is-the-agent-event-sourced-reactive-graphs-2026

Nakajima, Y.: *The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable
Agentic Systems*, arXiv:2605.21997, submitted 21 May 2026. Open source (Apache-2.0):
github.com/yoheinakajima/activegraph.

**Overlap.** component_overlap=4, architecture_overlap=4. An event-sourced, append-only log as
the sole source of truth with graph state as a deterministic, replayable projection of it —
matching D-System's H2 transition-semantics claim at the mechanism level, combined with a total,
worked-example-verified provenance chain from goal to individual model call (H9's backward
direction) using D-System's own System-A vocabulary (claim, evidence, question) linked by typed
relations (supports, addresses, derived_from). Real, installable (pip-installable, quickstart
reproduces byte-identical output counts). Self-described by its own author as "recombination" of
event sourcing, CQRS, reactive dataflow, and 1980s Blackboard-era coordination.

**What it would falsify.** At full strength this would falsify H2 (transition semantics), H3's
provenance half (actor+lineage present), H5 (context reconstructable from the log), H7, and H9
simultaneously — it is the single broadest-spanning collision in the matrix by hypothesis count
(H2;H3;H5;H7;H9). It would not falsify H1 (no orthogonal ontological+epistemic+lifecycle state
classification), the authority half of H3 (no authority-weighted or trust-arbitrated multi-actor
provenance), H4 (no independence-aware convergence/corroboration scoring), H6/H8/H10/H11 (no
requirement/plan/specification objects or a development lifecycle at all — the worked domain is
investment diligence, not software development; no bitemporal/versioned time model, only
log-order sequencing). The paper explicitly reports "no large-scale empirical evaluation of task
performance" and names its own architectural ancestors directly: Nii's Blackboard Model (1986)
and the same author's own prior BabyAGI (2023) — "less a new idea than a vindication of an old
one" (Sec.8).

second_review: disputed: reviewer confirms component_overlap at 4 but re-derives architecture_overlap
to 3 (not 4); of the five challenged hypotheses only H2 and H9 survive per the reviewer. Four minor
locator/quote corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=4. An event-sourced,
append-only log as sole source of truth, matching H2 at the mechanism level, with a
worked-example-verified provenance chain (H9's backward direction). The single broadest-spanning
collision in the matrix by hypothesis count (H2;H3;H5;H7;H9). Self-described by its own author as
"recombination."

**Independent reviewer position.** Confirms component_overlap=4 (a genuine mechanism-level match to
H2, not naming coincidence) but re-derives architecture_overlap to 3, not 4 — coverage concentrates
in one subsystem (the log/replay/lineage substrate) with zero presence for Requirement,
Specification, Artifact-as-code, Verification, Deployment, and Runtime Evidence, confirmed by the
row's own fields. Of the five listed hypotheses, only two survive their own falsification bars: H2
and H9 (the strongest — demonstrated bidirectionally, Sec.6). H3 should drop (actor+lineage
provenance exists but zero arbitration logic — checked the GitHub README to confirm the row's own
NOT_DETERMINABLE flag resolves to "absent," and the row's own strongest_difference already concedes
this). H5 should drop (Sec.8 explicitly positions the paper as *rejecting* the memory/retrieval
category rather than instantiating it — shared word "topology," different mechanism). H7 should
drop, the largest overreach — H7's bar names a specific SDLC stage list, and the row's own
strongest_difference already states the worked domain (investment diligence) has "essentially no
analog" to software development. Four minor locator/quote corrections found: a Sec.3-vs-Sec.2
citation, a p.10-vs-p.11 page citation, an unsupported inference that a forking evaluator is
specified as human (Sec.7 never says so), and a dropped "patches" item from a budget-cap list.

**Resolution.** All four locator/quote corrections applied to `04_evidence_matrix.csv`
(`retrieval_context_model`, `verbatim_notes`, `human_agent_scope`, `execution_unit_session_model`).
The architecture-score disagreement and the recommendation to drop H3/H5/H7 from
`hypotheses_challenged` are recorded here as judgment disputes per the coordinator's addressing;
`architecture_overlap_score` and `hypotheses_challenged` are left exactly as scored. Had the
reviewer's re-derivation been authorized, this row's hypotheses_challenged would narrow from
H2;H3;H5;H7;H9 to H2;H9.

---

## 8. tgms-agent-native-bitemporal-graph-2026

Zhang, X.: *TGMS: An Agent-Native Bi-Temporal Graph Management System*, arXiv:2607.10265, v2
24 Jul 2026. Open source (Apache-2.0): github.com/zxf-work/tgms.

**Overlap.** component_overlap=4, architecture_overlap=2. A formally specified, empirically
validated bi-temporal transition model — assert/retract/correct distinguishing "the world
changed" from "we were wrong" while preserving both, with a tested bi-temporal-immutability
invariant — close to H2's transition-semantics claim, and a rigorously validated claim-
verification mechanism (100% detection of eight injected-error classes, zero false positives)
directly relevant to H3/H9. Evaluated across two storage backends and six model configurations —
one of the most thoroughly engineered implementations in this campaign.

**What it would falsify.** At full strength this would falsify H2's transition-semantics claim
for a general-purpose graph substrate, and would provide direct evidentiary support against the
naive form of H3 and H9 (claim-verification gated on evidence completeness). It would not
falsify H1 (no epistemic/ontological classification), the authority half of H3 (provenance
fields reserved but explicitly unused — "write-back... disabled pending provenance and
authorization policies," Sec.8), H4 (absent), or H5/H6/H7/H8/H10/H11 (no decision/requirement/
specification/plan/artifact/test/deployment concept anywhere; domain is temporal-graph question
answering over communication-network data, not software development; no human role in the
evaluated pipeline). The paper explicitly and specifically differentiates itself from Zep/
Graphiti and TOKI while sharing their bi-temporal foundation, naming Snodgrass (1999) as the
classical ancestor of all three — independent convergence on a shared 1999 mechanism, not three
independent inventions, exactly the pattern this campaign's independence rule is built to
detect. The paper's own Limitations section states "TGMS does not yet solve general temporal
graph question answering."

second_review: disputed: reviewer re-derives component_overlap to 3 (not 4); with architecture_overlap
at 2 (agreed) and no other trigger met, reads critical_collision as NO. Left unchanged. Corrections
applied to a miscoded field and cherry-picked verifier statistics.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=2. A formally specified,
empirically validated bi-temporal transition model close to H2, and a rigorously validated
claim-verification mechanism (100% detection of eight injected-error classes, zero false positives)
relevant to H3/H9. One of the most thoroughly engineered implementations in this campaign.

**Independent reviewer position.** Re-derives component_overlap to 3: the paper combines three
separately-known primitives for a narrow domain — the bi-temporal correction pattern, which the
paper itself calls "classical [24]" (Snodgrass 1999) and positions against Zep/Graphiti and TOKI as
sharing "the bi-temporal foundation"; typed tool-contract APIs in a cited lineage (Toolformer,
ToolGate, PAL); and evidence-cited claim verification in a cited lineage (RARR, FActScore,
Chain-of-Verification) — substantially the primitive itself applied to a new but generic domain, not
strong overlap with D-System's specific claims. With architecture_overlap at 2 (agreed) and no other
trigger met (H3's bar requires actor/authority arbitration, explicitly reserved-but-unused per
Sec.8: "write-back is schema-ready but disabled pending provenance and authorization policies"), the
reviewer reads `critical_collision` as NO on this row and flags it as a genuine judgment call for the
owner. Separately found the "100% detection" claim cherry-picked: Table 5 has eight mutation
classes, and two are materially worse — wrong-step citation detected in only 36/100 (36%) and entity
member dropped in 0/100 (0%), a gap the paper itself discloses (Sec.5.4: "invisible to trace
grounding by construction"). Also found `feedback_to_knowledge_mechanism` miscoded
NOT_DETERMINABLE_FROM_ACCESS when the full text (Sec.4.1) fully specifies the mechanism's design —
what is undetermined is its empirical performance, not its existence.

**Resolution.** `feedback_to_knowledge_mechanism`, `test_verification_linkage`,
`backward_traceability`, and `strongest_dsystem_overlap` corrected in `04_evidence_matrix.csv` to
remove the miscoding and the cherry-picked statistic. The score and flag disagreement is recorded
here as a judgment dispute per the coordinator's addressing; `component_overlap_score` and
`critical_collision` are left exactly as scored. Had the reviewer's re-derivation been authorized,
this row's flag would be dropped entirely.

---

## 9. langgraph-checkpoint-library-oss

LangChain AI: LangGraph checkpoint library (`langgraph-checkpoint`), github.com/langchain-ai/
langgraph/tree/main/libs/checkpoint.

**Overlap.** component_overlap=4, architecture_overlap=2. A production-grade, widely deployed
(41,574 GitHub stars on the parent repo, PyPI v4.2.0, MIT-licensed) instance of exactly the
resumable, forkable, timestamped execution-checkpoint mechanism H8 (phase-bounded context)
gestures toward: per-step snapshots, parent-chain lineage enabling backward walk and "time
travel" replay, and an explicit `source={"input","loop","update","fork"}` classification of how
each snapshot was produced. Comparison against the implemented system sharpens this: D-System's
own checkpoint mechanism (`.claude/skills/checkpoint/SKILL.md`) currently rewrites/overwrites
summary sections in place rather than retaining a parent-linked chain (adversarial codebase
review, `04_state_transition_audit.md`, E42) — on H8/H9, this OSS library's shipped behavior
exceeds D-System's own current implementation, not only its conceptual architecture.

**What it would falsify.** At full strength this would falsify H8 as the review-instructions
phrasing states it ("equivalent task/session/context lifecycle in agentic development systems")
and contribute to H9's backward-traceability claim for execution state specifically. It would
not falsify H8 under the frozen register's fuller phrasing, since `channel_values` is opaque
application state, not a typed knowledge object — no epistemic/ontological state classification
(H1), no actor/authority/provenance beyond run_id and parent linkage (H3 largely absent), no
independence-aware convergence (H4), and no requirement/specification/artifact/test/deployment
linkage anywhere (H7/H9's non-code portions absent). This is a narrow, single-purpose execution-
state persistence layer for one graph run, not a knowledge-management or development-provenance
system. Its Pregel-based execution model traces directly to Malewicz et al. (SIGMOD 2010) and
its checkpoint-and-resume pattern to Chandy & Lamport's distributed-snapshot algorithm (1985) —
recorded as ancestors per campaign discipline, not credited as novel.

second_review: disputed: scores, flag and factual fields hold, but reviewer disputes the
hypotheses_challenged framing for H8's consolidation half and H9. One completeness correction
applied to evidence_locator.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=2. A production-grade,
widely deployed (41,574 GitHub stars, PyPI v4.2.0) checkpoint mechanism gesturing toward H8:
per-step snapshots, parent-chain lineage, explicit `source` classification. D-System's own
checkpoint skill currently rewrites/overwrites in place rather than retaining a parent-linked chain
— on H8/H9, this OSS library's shipped behavior exceeds D-System's own current implementation.

**Independent reviewer position.** Confirms component_overlap=4 and architecture_overlap=2 exactly,
verified directly against the code (Checkpoint/CheckpointMetadata/BaseCheckpointSaver,
`channel_values: dict[str, Any]` confirmed opaque at both the checkpoint layer and the long-term
store layer). Disputes not the scores or flag but the `hypotheses_challenged` framing: the row's own
fields already document that `planning_model`, `decision_representation`, `requirement_derivation`,
and `specification_representation` are all NOT_APPLICABLE, and that `provenance_model` is
"mechanical... not epistemic" — yet `hypotheses_challenged` lists H8 and H9 as genuinely challenged
without that qualification. H8's assembly half is genuinely implemented (parent-chain lineage
walk); its consolidation half is not (every checkpoint is the same opaque state, just a new
version). H9 is the more overstated of the two: it requires bidirectional traceability tying
functionality to reasoning, evidence, assumptions, and decisions, and the parent chain ties
checkpoint-to-checkpoint mechanically, never to a decision, requirement, or evidence object — those
types do not exist in the interface. One completeness correction to `evidence_locator`: additional
DeltaChannel-beta functions (`delete_for_runs`, `prune`, `get_delta_channel_history`) are present in
the exact file read but uncited, and `copy_thread`'s line range needed correcting.

**Resolution.** `evidence_locator` corrected in `04_evidence_matrix.csv`. The
`hypotheses_challenged` framing dispute is recorded here per the coordinator's addressing;
`hypotheses_challenged` is left exactly as scored (H8;H9). Had the reviewer's framing been
authorized, H8 would carry an explicit assembly-only qualifier and H9 would be dropped.

---

## 10. model-based-digital-threads-sociotechnical-systems-2022

Pessoa, Pires, Moreira, Wu: *Model-Based Digital Threads for Socio-Technical Systems*, in
*Machine Learning for Smart Environments/Cities*, Springer ISRL vol.121, 2022.

**Overlap.** component_overlap=4, architecture_overlap=4. Fig.2.18 ("MBSE and the digital
thread") is a materially close structural analogue to H7/H9: a typed, directional (trace/
refine/realize) graph linking Requirement -> Use-Case/Specification -> Block-Definition/Internal-
Block-Diagram -> Detailed Models -> Implemented System -> Test Case -> Field Performance,
explicitly built "to compare expected behavior (requirements) and actual system performance" —
spanning five of the methodology's flagged adjacent stages (Requirement, Specification,
Artifact, Verification, Deployment/Runtime Evidence).

**What it would falsify.** At full strength this would falsify H7 and H9 for the requirement-
through-runtime segment of the lifecycle — an explicit, named design goal in a peer-reviewed
2022 chapter. It would not falsify H1 (no epistemic/ontological state classification), H3 (no
provenance actor/authority on any traceability link — explicitly named by the paper itself as an
unsolved "challenging problem," Sec.2.3.2), H4 (absent), or H11 (only gestured at as future
work). It has no upstream Idea/Reasoning/Decision/Evidence layer — the thread begins at
Requirement, so H7's full idea-to-requirement span is not addressed — and the case study covers
only two of the methodology's six defined lifecycle phases, in a systems-engineering (not
software-development) domain. Two corrections are recorded on this row during this campaign:
its own Sec.2.2.1 traces the term "digital thread" to a 2013 USAF report, while
us20250165226a1-ai-digital-thread-patent (section 13, below) traces the same term to a different,
2018 DAU/DoD document — two independently cited coinages for the same term, not one shared
ancestor as an earlier pass of this campaign mistakenly recorded (now withdrawn on this row). The
chapter's own methodology is itself an explicit refinement of Bickford et al. (2020, ref.[5]).

second_review: confirmed, reached via a different (green open-access) route. One factual correction
(source_type conference -> book-chapter).

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=4. Fig.2.18 is a
materially close structural analogue to H7/H9, spanning five of the methodology's flagged adjacent
stages (Requirement, Specification, Artifact, Verification, Deployment/Runtime Evidence). Falsifies
H7/H9 for the requirement-through-runtime segment; no upstream Idea/Reasoning/Decision/Evidence
layer.

**Independent reviewer position.** Confirms both scores exactly, reached through a legitimate green
open-access copy (University of Twente institutional repository) after the Springer paywall could
not be passed — read all 26 pages end to end, with pagination, section numbers, all 18 figures, and
every checked quote matching the row verbatim. Confirms this is the one row in the phase where the
four-adjacent-stages trigger fires cleanly under both a strict-contiguous reading (Artifact ->
Verification -> Deployment -> Runtime Evidence, four consecutive stages) and a loose reading (six
stages in pipeline order). Confirms H7 and H9 both survive their bars exactly as the row states.
Finds one factual error: `source_type` is listed as `conference`, but Crossref's authoritative
record for the DOI types it `book-chapter` (Intelligent Systems Reference Library, an edited
monograph series) — it was never presented at a conference.

**Resolution.** `source_type` corrected to `book-chapter` in `04_evidence_matrix.csv`. No score,
flag, or hypotheses_challenged value is changed.

---

## 11. omniscientist-coevolving-ecosystem-human-ai-scientists-2026

Shao et al. (Tsinghua / Zhongguancun Academy): *OmniScientist: Toward a Co-evolving Ecosystem
of Human and AI Scientists*, arXiv:2511.16931, v2 14 Dec 2025.

**Overlap.** component_overlap=4, architecture_overlap=4. The Omni Scientific Protocol's
ContributionLedger — an immutable, chronological, per-object record of typed actions (create/
refine/propose/approve), each carrying actor identity and timestamp, explicitly designed to move
"from Data Provenance to Contribution Provenance" — is one of the closest matches in the
campaign to combined H2+H3+H9. Its Unified Participant Model, empirically evaluated in an HLE
case study (Human-AI Collaboration Mode: 0.22 accuracy vs. 0.10 Human Solo vs. 0.00 AI Solo), is
a direct, quantified H6 challenger — among the most direct empirical H6 evidence found in this
campaign.

**What it would falsify.** At full strength this would falsify H6's claim that the full human-
agent collective-knowledge-evolution synthesis "may be distinct even if primitives are known" —
a working, evaluated ecosystem already exists, in the scientific-research domain. It would
falsify H9's backward-traceability claim within that domain ("the final scientific result...
can always be transparently traced back to all contributors") and contribute typed-transition
evidence to H2/H3. It would not falsify H1 (ScholarlyObjects are typed only by kind, not by an
O,E,L triple), H4 (REQUEST_DECISION escalates disagreement to human fiat rather than computing
evidential weight — no independence-aware convergence), or domain-authority weighting under H3
(all Participants hold symmetric protocol status). H7's later stages and H11's production-
runtime loop are not applicable by domain (scientific-paper production, not software
development), not falsified. The ContributionLedger is structurally a scientific-credit
specialization of the classical nanopublication (Groth, Gibson & Velterop, 2010) and PAV/PROV-O
provenance traditions, not a novel provenance primitive; OSP's communication layer is explicitly
built atop MCP, A2A, and SCP rather than invented from scratch (Sec.4.1).

second_review: confirmed; one minor factual correction (evaluation_method's QA-accuracy figure
attribution).

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=4. The ContributionLedger
is one of the closest matches in the campaign to combined H2+H3+H9; the Unified Participant Model is
a direct, quantified H6 challenger. Falsifies H6's "may be distinct" claim within the scientific-
research domain; does not falsify H1 or H4.

**Independent reviewer position.** Confirms both scores exactly via a complete 40-page read, and
confirms three of the flag's four trigger types independently justify it (component, architecture,
and four-adjacent-stages via Plan->Execution->Artifact->Verification). Confirms H6 is one of the
strongest H6 challengers in the campaign, weakened but not falsified — no O,E,L typing, no
independence-aware trust/convergence, no domain-authority weighting (all Participants are
protocol-symmetric by design). Direction is "NEITHER" overstated nor understated. Finds one minor
factual error: `evaluation_method` states the QA retrieval-accuracy figure (0.70->0.88) as if it
came from the same n=1000 metadata sample as the completeness/correctness metrics; the source
distinguishes these — metadata quality is measured at n=1000, but the QA-accuracy figure came from a
separate 100-QA-pair benchmark.

**Resolution.** `evaluation_method` corrected in `04_evidence_matrix.csv`. No score, flag, or
hypotheses_challenged value is changed.

---

## 12. solozobov-verify-gated-completion-admission-control-2026

Nguyen, H.-D., Tran, X.-T.: *Verify-Gated Completion as Admission Control in a Governed
Multi-Agent Runtime*, arXiv:2605.17998, v2 21 May 2026. (Inventory naming note: the source_id
slug names "Solozobov," but the paper's own title page lists only Nguyen and Tran — recorded as
a bibliographic identity mismatch, not corrected silently.)

**Overlap.** component_overlap=4, architecture_overlap=4. A five-plane architecture with a
formally specified task-state tuple, a fail-closed acceptance predicate gating every completion
claim, a packet-lineage provenance chain (common-ground -> claim -> evidence -> verify outcome),
a three-class memory-ownership taxonomy (canonical/archive-only/prompt-injectable) with an
explicit context compiler, and risk-tiered execution-unit boundaries — together one of the
closest structural matches in the campaign to combined H2, H5, H8, and H9. Its context compiler
is a more developed, explicitly-named version of exactly the context-selection discipline H5
proposes but, per the adversarial codebase review, does not yet fully implement.

**What it would falsify.** At full strength this would falsify H2 (packet-lineage typed
transitions), H5 (the context compiler's memory-tier discipline), H8 (risk-tiered execution-unit
boundaries as an explicit context boundary), and H9 (packet lineage as backward traceability)
together — the widest simultaneous four-hypothesis span found among the 19 collisions alongside
log-is-the-agent (section 7). It would not falsify H1 (the task-state tuple's dimensions are
governance/operational, not an O,E,L triple), H4 (its PGV redundant advisory check is not
corroboration across independent paths), or H7's early stages (success criteria are asserted at
task-ingest, not derived from upstream reasoning/evidence) or H10's full cross-artifact scope
(only single-claim recovery ownership). The paper is explicit that its released empirical slice
is "synthetic-heavy and concentrated" (1,784/1,801 non-production rows), so its quantitative
claims validate inspectability, not effectiveness. Its own Sec.2 names its architectural lineage
directly: continuous-delivery quality gates (Humble & Farley 2010; Forsgren, Humble & Kim 2018)
and IT-governance decision-rights models (Weill & Ross 2004) — an explicit inheritance, not an
independent invention. No public repository accompanies the internal reference implementation.

second_review: disputed: reviewer confirms component_overlap at 4 but re-derives architecture_overlap
to 3 (not 4); flag stands via component-overlap plus the stage-span trigger firing independently, not
via architecture-overlap. Two factual corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=4. A five-plane
architecture with a formally specified acceptance predicate, packet-lineage provenance, a
three-class memory-ownership taxonomy, and risk-tiered execution-unit boundaries — one of the
closest structural matches in the campaign to combined H2, H5, H8, and H9.

**Independent reviewer position.** Confirms component_overlap=4 (independently verified the
fail-closed acceptance predicate and the three-class memory taxonomy against the text) but
re-derives architecture_overlap to 3: the row's own fields mark `requirement_derivation`,
`specification_representation`, and `planning_model` all NOT_APPLICABLE — the entire front half of
D-System's pipeline has no real analog, so "near end-to-end" overstates roughly half the pipeline
being untouched by mechanism. The four-adjacent-stages trigger fires independently regardless
(Execution->Artifact->Verification->Deployment carries real mechanism), so `critical_collision: yes`
is correct but rests on component-overlap plus stage-span, not architecture-overlap as the row's
narrative implies. Confirms all four listed hypotheses (H2;H5;H8;H9) survive their bars, with H8
splitting cleanly (assembly half strongly challenged, consolidation half largely intact per the
paper's own "Scaffold" self-rating). Finds two factual errors: `memory_model`'s "98.58% rule
agreement (n=2044)" conflates two different denominators — 98.58% (1,526/1,548) applies only to the
finalized-outcome subset, while n=2044 is the total shadow-evaluation pool. `derivative_ancestor`
omits a third self-cited ancestor: DAPPER (Google's distributed-tracing paper, ref.[20]), cited for
the causal-stitching event-logging mechanism (Sec.8.1).

**Resolution.** `memory_model` and `derivative_ancestor` corrected in `04_evidence_matrix.csv`. The
architecture-score disagreement is recorded here as a judgment dispute per the coordinator's
addressing; `architecture_overlap_score` is left exactly as scored.

---

## 13. us20250165226a1-ai-digital-thread-patent

Roper et al. (Istari Digital, Inc.): *Software-Code-Defined Digital Threads in Digital
Engineering Systems with Artificial Intelligence (AI) Assistance*, US Patent Application
US20250165226A1 (published 2025-05-22; since GRANTED as US12461717B2, confirmed via the
patent's own legal-status metadata).

**Overlap.** component_overlap=3, architecture_overlap=4. The specification describes digital
threads "linked across different stages... from concept, design, testing, to production," with
physical-prototype sensor data "compared with the DTw's simulations to confirm the product's
performance and verify its design" — a genuine multi-stage span structurally relevant to H7/H9.
The specifically claimed invention (Claims 1, 2, 3, 25) is narrower: an intent input generates a
stored code artifact (the digital thread), and feedback on that artifact retrains the generating
model — concretely matching D-System's artifact-linkage and feedback-to-knowledge primitives.

**What it would falsify.** At full strength — reading the background/preferred-embodiment
material rather than only the granted claims — this would contribute stage-spanning evidence
against H7 and H9. Read strictly against the claims actually granted, the falsification is much
narrower: no requirement/decision/specification stage between intent and generated script (H7's
early stages absent from the claims themselves), no actor/authority/provenance model beyond
training-triplet lineage (H3 largely absent), no ontological/epistemic state classification
(H1), and no independence-aware convergence (H4). The domain is engineering-model integration
scripting (CAD/simulation tool interoperability), not general software or knowledge-management
provenance. The patent's own cited-references list traces the claimed intent-to-code mechanism to
established machine-programming/text-to-code lineages (Intel, Microsoft, IBM prior patents,
2020-2024), not a sui generis invention. Its own "digital thread" definition cites the DAU/DoD
Digital Engineering Strategy (2018) — a different named source than
model-based-digital-threads-sociotechnical-systems-2022's 2013 USAF citation (section 10, above);
this campaign's earlier assumption that both sources shared one 2013 ancestor is wrong and is
withdrawn on that row.

second_review: disputed, with an explicit provenance caveat on the scoring rule itself. One factual
correction applied regardless of that dispute.

### Review — 2026-09-14

**First assessment position.** component_overlap=3, architecture_overlap=4. At full strength —
reading background/preferred-embodiment material — this would contribute stage-spanning evidence
against H7/H9; read strictly against the granted claims, the falsification is much narrower.

**Independent reviewer position.** ***Coordinator-note on the scoring rule's provenance***: the
"score the claims, not the specification" instruction the reviewer applied came from the
coordinator's addressing, not from any governed document — the evidence contract and methodology
are silent on how to score a patent, and the contract's `source_type` enum has no patent bucket
(idea 000148). The reviewer itself flagged this as "a defensible policy choice for someone else to
make explicitly." Under that rule, re-derives `architecture_overlap` to 3 (not 4): claims cover
Execution and Artifact solidly, but Requirement, Decision, Specification-of-the-software-system,
Deployment, and Runtime-Evidence-in-production are absent from every claim — that material lives
only in unclaimed specification background. Under claims-only scoring, no trigger fires and the flag
should not stand as scored. Verified the granted claims (US12461717B2) are textually identical to
the published application's claims. Found one factual error unrelated to the scoring-rule dispute:
`change_impact_mechanism` was coded NOT_APPLICABLE, but claim 18 claims to "predict a change in one
or more items... based on a change in one of the items" and claim 19 restates this for the reverse
direction — a real, narrow, pairwise change-propagation primitive the row missed entirely.

**Resolution.** `change_impact_mechanism` corrected in `04_evidence_matrix.csv` — this correction
stands independent of the scoring-rule dispute. The architecture-score/flag dispute is recorded here
as conditional on a rule the owner has not ruled on and is **not folded in as settled**;
`architecture_overlap_score` and `critical_collision` are left exactly as scored, and
`PLAN-023.03`'s evidence contract is not edited to add a patent-scoring rule.

---

## 14. zep-graphiti-temporal-kg-agent-memory-2025

Rasmussen, Paliychuk, Beauvais, Ryan, Chalef (Zep AI): *Zep: A Temporal Knowledge Graph
Architecture for Agent Memory*, arXiv:2501.13956, v1 20 Jan 2025.

**Overlap.** component_overlap=4, architecture_overlap=3. Graphiti's bi-temporal edge model
(four timestamps: t_created/t_expired transactional, t_valid/t_invalid world-time) with
LLM-mediated contradiction detection and recency-prioritized edge invalidation is a direct
match to H2's typed-transition claim; its three-stage Search-Rerank-Constructor retrieval
pipeline (including breadth-first traversal to incorporate "recently mentioned entities and
relationships") directly matches H5's topology-aware context-transfer claim; its bidirectional
episode-to-fact indices are a direct H9 primitive. Commercial, production-deployed (getzep.com),
built on the open-source Graphiti component.

**What it would falsify.** At full strength this would falsify H2 (bi-temporal typed
transitions), H5 (topology/recency-aware retrieval), and H9 (bidirectional indices, though "not
directly examined in this paper's experiments" per its own Sec.2.1) together. It would not
falsify H1 beyond the episodic/semantic/community subgraph-membership distinction (only
partially present), H3 (edge invalidation is purely recency-based — "Graphiti consistently
prioritizes new information" — not evidence- or authority-weighted), H4 (absent), or H6-H8/H10-
H11 (no decision/requirement/specification/plan/artifact/verification/deployment concept
anywhere — scoped entirely to D-System's Knowledge-Construction side, with humans present only
as message-author data, not a distinguished participant class). Its bi-temporal model is
presented as "a novel advancement... in LLM-based knowledge graph construction" but silently
inherits the classical valid-time/transaction-time distinction (Snodgrass 1999) that
tgms-agent-native-bitemporal-graph-2026 (section 8, above) names explicitly and that this Zep
paper's 28-entry reference list does not cite — one shared 1999 ancestor and two derivative
LLM-era applications, not two independent inventions of bi-temporal novelty.

second_review: confirmed; reviewer's one push-back is that H9's inclusion should carry the same
domain-absence caveat given to H7/H8/H11. No factual corrections needed.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3. Graphiti's bi-temporal
edge model with LLM-mediated contradiction detection directly matches H2; its retrieval pipeline
matches H5; bidirectional episode-to-fact indices are a direct H9 primitive. Falsifies H2, H5, and
H9 together at full strength.

**Independent reviewer position.** Confirms both scores exactly via a complete 12-page read
(including the full 28-entry reference list, which the reviewer checked in full and confirmed does
not cite Snodgrass or temporal-database theory — the paper frames its "novel advancement" only
relative to prior LLM/RAG memory systems). Confirms H2 and H5 are genuinely challenged, though H2
meets only the state-transition half of its bar and not the provenance half (no actor/method/
evidence field on the transition, only four bitemporal timestamps). Pushes back specifically on H9:
the row's own cited mechanism (bidirectional episode<->entity indices, Sec.2.1) is explicitly "not
directly examined in this paper's experiments," and Zep has zero decision/requirement/artifact/
verification/deployment concepts — structurally the same "not applicable by domain" situation the
row already gives H7/H8/H11, which it oddly omits H9 from. Recommends H9 not be counted as seriously
challenged by this source. No factual corrections found — every checked field matched the source
exactly, and the locator spans the full document, not a page-4 cap.

**Resolution.** The H9-inclusion push-back is recorded here as a judgment dispute per the
coordinator's addressing; `hypotheses_challenged` is left exactly as scored (H2;H5;H9). Had the
reviewer's recommendation been authorized, this row's hypotheses_challenged would narrow to H2;H5.

---

## 15. zimmermann-et-al-managing-architectural-decision-models-2009

Zimmermann, Koehler, Leymann, Polley, Schuster: *Managing Architectural Decision Models with
Dependency Relations, Integrity Constraints, and Production Rules*, Journal of Systems and
Software 82(8), 1249-1267 (2009).

**Overlap.** component_overlap=4, architecture_overlap=3. The most formally complete decision-
representation and constraint-production-rule mechanism found in the campaign: an explicit
outcome-status lifecycle field (open/implied/resolved), a formally proved typed-transition
mechanism (triggers, governed by 8 integrity constraints), per-outcome actor provenance
(changedBy), and requirement-to-decision linkage (decisionDrivers/justification) — strong,
multi-primitive overlap with H2 and H7. Working tool: the Architectural Decision Knowledge Wiki,
publicly available since March 2008, evaluated on 389 real decision issues.

**What it would falsify.** At full strength this would falsify H2 (a formally proved typed-
transition mechanism with actor provenance) and H7 (requirement-to-decision linkage,
requirements as first-class dependency-graph nodes) for the decision/requirement segment. It
would not falsify H1 (no epistemic/ontological classification alongside the lifecycle status),
H3/H4 (no independence-aware convergence, and the decision graph's own logical consistency is
the only thing checked — not evidence or authority weighting), or H5/H6/H8-H11 (the mechanism
never leaves the decision-and-requirement layer: no specification, plan, execution, artifact,
test, deployment, or runtime-evidence linkage; work-breakdown-structure and health-checking ideas
are explicitly named future work, Sec.7). The paper states directly (Sec.3, p.5) "Our metamodel
extends that from [1] and [5]" — [5] is jansen-bosch-architecture-as-decisions-wicsa-2005
(section 6, above) — a direct formal extension of an already-matrixed collision, not an
independent confirmation; its own novel contribution is the integrity-constraint/production-rule
formalization and the outcome-status/changedBy fields that go beyond Jansen & Bosch's original
model.

second_review: disputed: flag and both scores independently reproduced and confirmed, but the row's
own narrative overstates implementation maturity. Flag rests on a single trigger, not convergent
evidence. Four factual corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3. The most formally
complete decision-representation mechanism found in the campaign: an explicit outcome-status
lifecycle, a formally proved typed-transition mechanism, per-outcome actor provenance, and
requirement-to-decision linkage. Falsifies H2 and H7 for the decision/requirement segment. Working
tool evaluated on 389 real decision issues.

**Independent reviewer position.** Independently reproduces both scores exactly via a full 36-page
read (identity separately verified at Crossref). Confirms the flag fires correctly by the single
component trigger, but finds the row's narrative reads as a stronger case than the single-trigger
reality — worth recording explicitly. The load-bearing finding: the paper's own words (Sec.6.3,
p.33) state "the integrity constraint checks, heuristics for balanced architectural decision models,
and production rules are implemented in an advanced prototype that is not yet publicly available."
The publicly deployed tool (the Architectural Decision Knowledge Wiki, 200+ users, 600+ downloads)
implements only the basic CRUD metamodel — not the triggers/integrity-constraint engine the
component score actually rests on. That engine exists (not aspirational future work) but lives in a
non-public prototype, separate from both the industrially validated content and the widely used
wiki — the row's `implementation_availability` is technically true but elides this split. Confirms
H2 and H7 both survive, with H2 not fully equivalent (ADOutcome's status mutates in place, no
versioned history of prior states preserved as distinct entities). Finds four locator/precision
corrections: the outcome-status definition quote is cited to "p.16, Sec.4" but is actually at
Definition 14, PDF p.22 (a 6-page discrepancy); two Sec.3 quotes cited to p.4-5/p.5 are actually on
PDF p.6; `evidence_locator`'s claim that this PDF's pagination "matches" the published JSS pagination
is false (it carries its own internal 1-36 numbering; DOI/Crossref identity is unaffected);
`temporal_model` omits a `validUntil: Timestamp` attribute visible in Fig.1 (p.5), though it is never
elaborated further and the substantive NOT_APPLICABLE conclusion holds.

**Resolution.** `verbatim_notes`, `evidence_locator`, and `temporal_model` corrected in
`04_evidence_matrix.csv`. The implementation-maturity overstatement is a narrative concern the
reviewer raises against the row's framing, not a scored field; no score, flag, or
hypotheses_challenged value is changed.

---

## 16. burns-groth-agentic-ontological-notebook-memory-2026

Burns, G.A., Groth, P.: *Complex Knowledge Curation using Agentic Ontological Notebook Memory*,
CAIS '26 (ACM, 5 pages). Open source: github.com/sciknow-io/skillful-alhazen.

**Overlap.** component_overlap=4, architecture_overlap=3. A genuine, empirically evaluated
ontological-vs-epistemic-vs-derivational state distinction (domain things vs. Artifact/Fragment/
Note ICE hierarchy) close in spirit to H1's O+E+L triple; explicit per-note actor attribution and
a full backward provenance chain to source (H3); and a named, working closed loop from
operational curation failures back into schema/ontological design (H11) — the strongest H11
match found in this campaign. All three are working, demonstrated mechanisms with a public
benchmark (github.com/sciknow-io/alhazen-skill-dismech), not merely proposed.

**What it would falsify.** At full strength this would falsify H1's "uncommon in agent-memory
systems" framing (a working system already does something close), contribute actor-attribution
evidence to H3, and falsify H11's claim that runtime-to-knowledge closure is unexplored — the
loop from curation failure to GitHub issue to schema change is real and benchmarked. It would
not falsify H2 (no typed transition-with-provenance primitive linking states the way D-System's
S_t--[T,P]-->S_t+1 does), H4 (no conflict/trust or independence/convergence mechanism at all), or
H5-H10 (no decision/requirement/specification/plan representation beyond one skill's narrow
success-criteria entities; the O/E/L-like classification is per-skill and domain-specific, not
universal; H11's feedback loop closes onto ontology/schema refinement specifically, not the
broader idea->decision->requirement->code->runtime lineage H7/H9/H10 target). The paper positions
itself in its own Related Work as architecturally distinct from every memory system it cites
(MemGPT/Letta, LangGraph, Zep/Graphiti, Mem0, Cognee) rather than an extension of any one — its
domain-thing/ICE split draws on the established Information Artifact Ontology (Ceusters 2013),
a vocabulary borrowing, not a mechanism inheritance from a single ancestor.

second_review: disputed -- THE FLAG DOES NOT SURVIVE per re-derived scores; left unchanged.
Recommends dropping H3 as a challenger and downgrading H11. Three factual corrections applied.

### Review — 2026-09-14

**First assessment position.** component_overlap=4, architecture_overlap=3. A genuine ontological-
vs-epistemic-vs-derivational state distinction close in spirit to H1; explicit per-note actor
attribution and full backward provenance (H3); a named, working closed loop from curation failures
back into schema design (H11) — the strongest H11 match found in this campaign, "a working,
demonstrated mechanism... not merely proposed."

**Independent reviewer position.** Re-derives component_overlap to 3 and architecture_overlap to 2
(both down one point); no trigger fires under either adjacency reading (longest contiguous run is 2:
Reasoning and Knowledge Update, separated by an unbroken run of absent stages). The state model is a
type *hierarchy* (ICE subtypes exist only under Information Content Entities), not orthogonal axes
applied uniformly. Recommends dropping H3 entirely as a challenger: the provenance chain has zero
conflict/trust use, and H3's operative clause is that provenance *influences conflict resolution* —
`conflict_trust_mechanism` is confirmed NOT_APPLICABLE by direct read, so the chain illustrates the
gap H3 claims to fill rather than closing it. Most significantly, finds the row's central H11 claim
unsupported by the primary text: field 27 quotes Sec.2's mechanism description verbatim but drops
the immediately preceding sentence, "We are developing a feedback loop for iterative refinement"
(present-progressive, not completed), and the schema-deficit-to-GitHub-issue loop never appears in
Section 4 (the paper's own Demonstration section) — no example, instance, or evaluation anywhere.
Section 6 (Conclusion & Future Work), which the row's evidence_locator never cites, states plainly:
"Our future work focuses on developing the virtuous cycle of using experience of the systems' use
curation work to improve schema + code design as an automated agentic loop." Recommends downgrading
this source from "strongest H11 match found" to a background/adjacent data point, and downgrading
`interpretation_confidence` from high to medium, since a high-confidence read should not have missed
the source's own future-work framing of its central claim.

**Resolution.** `evidence_locator`, `feedback_to_knowledge_mechanism`, `strongest_dsystem_overlap`,
and `interpretation_confidence` corrected in `04_evidence_matrix.csv` to state the loop as
in-progress rather than demonstrated and to extend the locator to the sections that establish this.
The score, flag, and hypotheses_challenged disagreements are recorded here as judgment disputes per
the coordinator's addressing; `component_overlap_score`, `architecture_overlap_score`,
`critical_collision`, and `hypotheses_challenged` (H1;H3;H11) are left exactly as scored. Had the
reviewer's re-derivation been authorized, this row's flag would be dropped and H3 removed from
hypotheses_challenged.

---

## 17. epistemic-sybil-resistance-bara-2026

Bara, M.: *Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence*,
arXiv:2609.01873, 1 Sep 2026.

**Overlap.** component_overlap=4, architecture_overlap=2. The provenance-DAG-based discount of
corroboration from reports sharing an evidentiary root is the single closest primary-source
match found in this campaign to H4's claim — both the DAG structure and the discounting
arithmetic (kappa_m = 1/(1+rho(m-1)), Sec.5.2 Corollary 2) are explicit and formal, not
analogical. Found only in this phase's Pass 3 collision search, after five prior phases at zero
challengers for H4.

**What it would falsify.** At full strength this would falsify H4 — a closed-form,
graph-topological discount for shared-ancestry corroboration is exactly what H4, and especially
the frozen register's "graph-topological... discounted based on shared lineage" phrasing,
describes. It would not fully falsify H4 as D-System frames it, because the paper is explicitly
scoped to AI-agent report multiplicity only — no human witnesses, no mixed human-agent
corroboration are modeled or evaluated, which is explicitly outside H4's "mixed human-agent
knowledge" scope — and the "topology" is a flat root-sharing DAG used solely to test conditional
independence of reports, not a general reasoning-lineage/transition graph carrying decision,
requirement, or artifact nodes as D-System's own lineage graph would. The paper's own Sec.9
leaves practical provenance authentication and information-theoretic estimation from raw reports
as open problems — design guidance, not a deployed aggregator. No prior mechanism is named as an
ancestor; the formalization is presented as this paper's own original contribution, situated
against classical Sybil-resistance and jury/testimony epistemology as conceptual framing only.
Given this hypothesis's thin evidence count (one challenger), this section records the overlap
without treating it as settled in either direction — that judgment belongs to
`06_hypothesis_tests.md`'s `INSUFFICIENT_EVIDENCE` verdict, not to this collision analysis.

second_review: pending

---

## 18. eywa-provenance-grounded-memory-joshi-2026

Joshi, R.: *Eywa: Provenance-Grounded Long-Term Memory for AI Agents*, arXiv:2605.30771, May
2026.

**Overlap.** component_overlap=4, architecture_overlap=3. Independently tracking ontological
type, epistemic status/tier, and lifecycle state on the same memory object (Table 2, Sec.4.3) is
the closest primary-source, real-implemented match found in this campaign to H1's orthogonal
ontological+epistemic+lifecycle claim, combined with an explicit, auditable provenance link from
every derived belief back to its immutable source evidence. Real, implemented, evaluated system;
per-question artifacts published at eywa.to/research.

**What it would falsify.** At full strength this would falsify H1's "uncommon in agent-memory
systems" framing directly — this is exactly such a system, exactly doing that. It would
contribute evidence toward H5 (retrieval combining evidence provenance with query-type weighting,
Sec.4.5). It would not falsify H1 under a strict reading requiring a formally orthogonal (O,E,L)
triple applied uniformly system-wide (the three dimensions here are a memory-object taxonomy and
a two-tier capture/validation pipeline, per the paper's own framing), nor H3 (no authority/
delegation provenance), H4 (no independence-aware convergence discounting), or H7/H9/H10/H11 (no
reach beyond conversational memory into decisions, requirements, code, tests, deployment, or
runtime evidence — confined to the Reasoning/Knowledge-Update ends of D-System's proposed
lifecycle). No prior mechanism is credited by the paper for the ontological/epistemic/lifecycle
classification or the evidence-first provenance design; it positions itself against contemporary
LLM-agent memory benchmarks (LoCoMo/LongMemEval/BEAM) rather than a named earlier system.

second_review: pending

---

## 19. memtx-transactional-belief-commit-2026

Li, Wang, Lu, Chen, Li, Song, Zheng, Cai: *MemTX: Transactional Belief Commit for Stateful
Agent Memory*, arXiv:2607.23929, v2 28 Jul 2026.

**Overlap.** component_overlap=4, architecture_overlap=2. Retraction -> typed cascading repair
of derived records and tool side effects, machine-verified for completeness, is the strongest
primary-source match found in this campaign for H10's epistemic-blast-radius claim — proven, not
just claimed, for one memory system's dependency graph (5.5 million enumerated protocol states,
zero violations). Read from the abstract only in this pass; access_limitation=abstract_only, so
several fields remain NOT_DETERMINABLE_FROM_ACCESS.

**What it would falsify.** At full strength this would falsify H10's core mechanism claim —
retracting/falsifying a claim triggers verified, cascading reassessment of everything downstream
— for the scope of one memory store's internal state. It would not falsify H10 as D-System's
fuller cross-lifecycle claim states it, since the cascade is scoped to a single shared memory
store's internal derived records and tool-call side effects, not D-System's proposed propagation
into requirements, plans, specifications, artifacts, and tests. It would not falsify H4 (no
independence-aware convergence/discounting mechanism confirmed) or H1 (no ontological/epistemic/
lifecycle state triple confirmed) — both NOT_DETERMINABLE_FROM_ACCESS pending a full-text read
this dispatch did not perform. Multi-AI-agent only; no human actor or authority model. No
ancestor is named for the cascading-repair mechanism itself; the paper situates itself against
unspecified prior agent-memory systems that "treat every accepted write as immediately
actionable truth" (its stated gap). A full-text read (currently abstract-only) is recorded as an
open item for whichever pass next revisits this row, not resolved here.

second_review: pending
