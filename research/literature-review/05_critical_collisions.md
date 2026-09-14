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
