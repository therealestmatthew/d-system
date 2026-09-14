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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

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

second_review: pending

---
