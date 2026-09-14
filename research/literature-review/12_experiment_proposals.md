# Experiment proposals

Experiments capable of distinguishing D-System's mechanisms from simpler baselines, per
`CLAUDE.md` §15's deliverable definition and this dispatch's instruction to tie each experiment to a
hypothesis that ended `POTENTIALLY_DISTINCT` or `INSUFFICIENT_EVIDENCE` in `06_hypothesis_tests.md`.

**Which hypotheses qualify.** Zero of the eleven hypotheses ended `POTENTIALLY_DISTINCT` — the
review-instructions' allowed-status vocabulary was used exactly, and `06_hypothesis_tests.md`'s own
summary table records nine of eleven hypothesis-readings at `LIKELY_ALREADY_KNOWN` or
`KNOWN_COMPONENT_NEW_INTEGRATION`. Three hypothesis-readings ended `INSUFFICIENT_EVIDENCE`: H1, H11,
and H4's frozen-register graph-topological phrasing specifically. This document ties one experiment
to each of the three.

**Why H4 is included despite its `status:` field reading `KNOWN_COMPONENT_NEW_INTEGRATION`.** H4's
YAML block in `06_hypothesis_tests.md` carries a single `status:` token
(`KNOWN_COMPONENT_NEW_INTEGRATION`) because the file's own status vocabulary permits only one token
per block and the block explicitly states it records "the review-instructions general phrasing's
verdict... as primary." But the same block's `assessment` field argues the two phrasings separately
and states outright: "the graph-topological reading stays `INSUFFICIENT_EVIDENCE`, unchanged from the
prior reconciliation." `08_surviving_distinctions.md` independently confirms this by placing "H4
(graph-topological phrasing)" in its own Category 3 — the `INSUFFICIENT_EVIDENCE` category — as a
distinct entry from "H4 (general phrasing)" in Category 2. Reading the block's own text rather than
only its single-token field, the graph-topological reading is an `INSUFFICIENT_EVIDENCE`
hypothesis-reading in every sense this dispatch's instruction cares about, and Experiment 2 below is
scoped to that reading specifically — not to H4's general phrasing, which is not included here because
`06_hypothesis_tests.md` treats it as settled at `KNOWN_COMPONENT_NEW_INTEGRATION` on a genuine
positive finding (Goldman 2001), not an unresolved search.

**Carried caveat, binding on Experiment 2.** Per the owner's ruling closing `phase-lit-08`, H4's
general/graph-topological split itself — including which reading each candidate source belongs to —
was pre-loaded by a coordinator dispatch's framing rather than independently derived by the worker
who ran the search, disclosed unprompted, and judged real and contestable on independent review.
Experiment 2 is scoped against the frozen register's own wording directly, not against the
coordinator's framing of it, to keep that dependency as small as it can be, but the caveat still
applies to how the experiment's target is defined.

**Coverage caveat, binding on this document.** Every experiment below is designed against the
comparators this campaign's 49 deep-read matrix rows actually found, not the full candidate pool: 340
of 387 collision candidates have never been deep-read, including 20 of the top prescore band's 32
candidates. A future search of that remainder could surface a stronger baseline than the ones named
here, which would strengthen rather than invalidate the experimental design. On search completeness:
the duplicate-discovery rate fell from 20.0% (44/220, `phase-lit-06`) to 15.0% (58/387,
`phase-lit-08`) — a trend, stated without asserting saturation, which this document does not claim
anywhere.

---

## Experiment 1 — Does independent tracking of D-System's O/E/L triple add measurable value over the
closest known baseline? (ties to H1)

**Hypothesis this tests:** H1 — Orthogonal ontological+epistemic+lifecycle classifications for
knowledge states, claimed uncommon in agent-memory systems. `06_hypothesis_tests.md`: six candidates
deep-read, none combining the right axis content with genuine independence and field maturity;
verdict `INSUFFICIENT_EVIDENCE` because the search satisfied condition 1 (dedicated, multi-strategy,
primary-text-verified) but not condition 2 (a mature comparator family whose closest member
instantiates the same mechanism).

**Baselines to compare against.** Two real, deep-read implementations give two distinct baseline
shapes, neither hypothetical:

1. **Derived-third-axis baseline**, from `mythologiq-agent-memory-oss`
   (github.com/MythologIQ-Labs-LLC/agent-memory): two independently-varying enums (`type`, an
   18-value ontological content-category enum; `state`, a 15-value lifecycle-stage enum) on one
   memory-unit record, with the epistemic dimension *derived* post-hoc from `evidence[]`,
   `signals[]`, `saturation`, and `certification.status` rather than tracked as a single
   independently-varying field.
2. **Wrong-content-but-genuinely-independent baseline**, from `subit-wiki-epistemic-hmm-oss`
   (github.com/sciganec/subit-wiki): three genuinely independent 2-valued axes (WHO/WHERE/WHEN,
   encoding discourse/rhetorical stance) combined into a 64-state code, decoded via a real,
   working log-space Viterbi HMM — the same combinatorial-state-space-plus-probabilistic-transition
   shape H1 and H2 propose together, applied to different axis content.

**Design.** Construct (or, where available, use real `_private/portfolio` knowledge-state histories,
subject to this campaign's constraint against touching that content) a corpus of knowledge-state
transition sequences labeled with ground-truth ontological type, epistemic status, and lifecycle
stage at each step. Run three conditions:

- **(a) MythologIQ-shape:** track ontological type and lifecycle stage as independent fields; derive
  epistemic status post-hoc from evidence/signal/certification fields, exactly as MythologIQ does.
- **(b) SUBIT-shape, D-System content substituted:** track all three of D-System's axes
  (ontological/epistemic/lifecycle) as genuinely independent fields, using SUBIT's
  combinatorial-state-plus-transition-decoder architecture as the implementation pattern rather than
  its own WHO/WHERE/WHEN content.
- **(c) D-System's proposed model** as documented in the conceptual architecture (`S = (O, E, L,
  Content, TemporalScope, Metadata)`).

**Metric.** For a held-out set of downstream tasks that plausibly depend on the epistemic axis being
tracked independently rather than derived (e.g., predicting which of two states should be preferred
in a later conflict, or which knowledge-lifecycle transition should fire next given a change in
epistemic status alone, holding ontological type and lifecycle stage fixed), measure prediction
accuracy or explanatory power under (a) versus (b)/(c). If (a)'s derived-epistemic-axis approach
performs indistinguishably from (b)/(c)'s independently-tracked approach on these tasks, that is
evidence H1's specific independence claim adds complexity without measurable benefit over the closest
real baseline. If (b)/(c) measurably outperform (a) on tasks specifically sensitive to the epistemic
axis varying independently of the other two, that is a positive result distinguishing D-System's
claim from the closest baseline this campaign found.

**What would close the `INSUFFICIENT_EVIDENCE` status either way.** A result favoring (a) does not by
itself prove H1's mechanism is absent from the wider field (per `06_hypothesis_tests.md`'s own rule,
that requires a mature comparator family, not an experiment against two candidates); it would,
however, give D-System's own architecture a concrete, evidence-based reason to adopt MythologIQ's
simpler derived-axis pattern (`10_architecture_implications.md`, §1.7) rather than carrying the
complexity of full independence by default.

---

## Experiment 2 — Does a graph-topological, mixed-human-agent-scope corroboration discount do
anything a naive extension of Goldman's proof or Bara's AI-agent-only formula does not? (ties to H4,
frozen-register graph-topological phrasing)

**Hypothesis this tests:** H4's frozen-register phrasing — "graph-topological epistemic signal...
discounted based on shared lineage" — kept separate from H4's general phrasing per
`06_hypothesis_tests.md`'s own rule against blending the two readings. Verdict for this reading:
`INSUFFICIENT_EVIDENCE`; condition 1 satisfied (32 queries, backward chaining to Townend/Eckhardt-Lee
and to Goldman/Mayo-Wilson, direct collision queries), condition 2 failed on maturity — the one
graph-topological formalization found (`epistemic-sybil-resistance-bara-2026`) is AI-agent-only with
its practical protocol left an open problem, and `barakat-corroboration-provenance-patterns-tapp2017`'s
discount term is an unimplemented sketch.

**Baselines to compare against.**

1. **Naive vote-counting**, the shape `extending-nanopublications-knowledge-provenance`'s PROV-K
   system actually implements: reliability from sufficiency/consistency counting over
   supporting-vs-conflicting sources, with no treatment of whether two supporting sources share a
   dependent origin.
2. **Bara's closed-form discount, extended naively to mixed scope**:
   `kappa_m = 1/(1+rho(m-1))` (Sec.5.2, Corollary 2 of `epistemic-sybil-resistance-bara-2026`) applied
   to a provenance DAG without modification, substituting D-System's mixed human-agent transition
   provenance for Bara's AI-agent-only report set — the most direct way to test whether the
   AI-agent-only scoping in the original paper was a genuine technical limitation or an
   unexercised generalization.
3. **Goldman's blind-follower discount**, applied narratively rather than graph-computed: the general
   reading's already-established mechanism (`goldman-experts-which-ones-should-you-trust-2001`),
   included as the baseline representing H4's *general* phrasing, which this experiment does not aim
   to re-test but does use as a floor — D-System's graph-topological mechanism should be expected to
   do at least as well as this narrative-only baseline to be worth its added complexity.

**Design.** Using D-System's actual transition-provenance data model (actor identity, domain
authority, evidence, method, lineage, delegation — H3's provenance fields), construct a test corpus of
corroborating claims with known ground-truth shared-ancestry structure spanning both human and agent
actors — for example, a human reviewer's judgment that derives from (and adds no independent
information beyond) an agent's earlier finding, alongside a genuinely independent second agent's
corroborating finding reached by a different method. Compute the epistemic weight each of the three
baselines and D-System's proposed mechanism assign to the corroborating set. The distinguishing
question is whether D-System's mechanism, once actually specified precisely enough to compute a
number, differs measurably from baseline 2 (Bara's formula extended naively to mixed scope) — or
whether it turns out to be the same computation under different names, which would mean the
"mixed-scope" extension bara-2026's Sec.9 left open is in fact straightforward, not a genuinely open
research problem.

**What would close the `INSUFFICIENT_EVIDENCE` status either way.** If baseline 2 handles the
mixed-scope case adequately once implemented, H4's graph-topological reading collapses cleanly into
`KNOWN_COMPONENT_NEW_INTEGRATION` alongside its general phrasing — the "open problem" Bara's Sec.9
names would turn out to be a straightforward engineering extension, not a genuine research gap. If
mixed human-agent scope requires machinery none of the three baselines have (for example, because
human "authority" and agent "method" are not commensurable in the way Bara's formula assumes
same-type report multiplicity to be), that is the positive finding distinguishing D-System's claim
from every found baseline, and it would be the first result in this campaign actually demonstrating
(not merely searching for) a gap in the graph-topological corroboration literature.

---

## Experiment 3 — Can D-System's proposed mechanism absorb novel runtime evidence types EvoReqs'
closed rule vocabulary cannot, and does it revise decision/rationale content rather than a derived
metric? (ties to H11)

**Hypothesis this tests:** H11 — runtime telemetry, tests, incidents, and outcomes become
provenance-bearing evidence updating the same knowledge structure that generated implementation
intent. Verdict: `INSUFFICIENT_EVIDENCE`. The awareness-requirements lineage (2010-2023,
peer-reviewed at ICSE/SEAMS) is a genuinely mature comparator family, satisfying the maturity half of
condition 2 where H1's did not — but its best-implemented member (EvoReqs, 2012) closes a
structurally different loop: ECA-triggered, code-executing mutation of a live requirements model over
a closed, analyst-authored vocabulary of anticipated responses, not evidence weighed into a
provenance-bearing knowledge revision. Every family member aimed at D-System's actual claim
(sawyer-bencomo 2010, souza-lapouchnian 2011, krentsel 2026) states it as unbuilt future work or a
research agenda.

**Baselines to compare against.**

1. **EvoReqs' rule-triggered baseline**, extended with D-System's data model but no genuinely
   evidence-derived revision logic: a closed, hand-authored set of ECA rules (`requirement-evolution-
   requirements-adaptive-systems-seams-2012`, implemented, open-source, github.com/vitorsouza/Zanshin)
   mapping specific anticipated AwReq-failure patterns to specific pre-authored requirement mutations.
2. **Bajaj's derived-metric baseline**: production defect-severity and incident-impact signals
   measurably changing a single requirement-linked risk score used in later release decisions
   (`bajaj-ai-augmented-closed-loop-quality-engineering-2026`, Sec.3.5-3.6) — the closest found
   instance of any quantitative before/after feedback loop, but revising a derived number rather than
   decision or rationale content.

**Design.** Using a corpus of real runtime evidence events — test failures, incident reports, or
telemetry anomalies drawn from `_private/portfolio` history where available (subject to this
campaign's constraint against writing that content into a tracked file; the experiment design itself,
not the corpus, is what belongs in this document) or a constructed equivalent otherwise — present each
event to baseline 1 (does it match a pre-authored rule? if not, a human must manually author a new
rule before the event can be absorbed), to baseline 2 (can the event update a derived risk score? if
the event does not map onto that score's inputs, it cannot be absorbed), and to D-System's proposed
mechanism (does the event become provenance-bearing evidence that revises the content of a decision or
requirement record, with actor/method/lineage recorded, per H3's provenance fields?). Measure, for
each baseline and for D-System's proposed mechanism: the proportion of real evidence events each
approach absorbs without a human pre-authoring a new rule or hand-mapping a new metric, and — for the
subset D-System's mechanism absorbs — whether the resulting revision touches decision/rationale
content (D-System's claim) or only a numeric feature (baseline 2's ceiling).

**What would close the `INSUFFICIENT_EVIDENCE` status either way.** If D-System's mechanism, run
against real evidence, turns out to require the same proportion of manual rule-authoring as EvoReqs
once its "arbitrary evidence" claim is actually implemented and tested, that is evidence the
mechanism is a relabeled instance of the same MAPE-K-family control-loop reaction
`06_hypothesis_tests.md` already distinguishes from D-System's claim — a negative but genuinely
informative result. If it demonstrably absorbs evidence types outside any pre-specified vocabulary
and produces decision/rationale-content revisions (not derived metrics), that would be the first
working instance in this campaign of the exact loop the awareness-requirements literature has named
without building for over a decade — directly answering open question Q10 in
`11_open_research_questions.md` with a result rather than a search.

---

## Summary

| Experiment | Hypothesis / reading | Baselines | Distinguishing question |
|---|---|---|---|
| 1 | H1 | MythologIQ (derived third axis), SUBIT-wiki-shape (independent axes, D-System content) | Does independent axis tracking beat post-hoc derivation on epistemic-status-sensitive tasks? |
| 2 | H4 (frozen-register, graph-topological phrasing only — see reasoning above) | PROV-K naive vote-counting, Bara's formula extended to mixed scope, Goldman's narrative discount as a floor | Does mixed human-agent scope need machinery none of the three baselines have? |
| 3 | H11 | EvoReqs (rule-triggered, closed vocabulary), Bajaj (derived metric) | Does D-System's mechanism absorb evidence types and revise content a closed-vocabulary or single-metric baseline cannot? |

All three experiments are designed to produce evidence bearing on `06_hypothesis_tests.md`'s
condition 2 (a mature comparator family whose best member instantiates the same mechanism) —
specifically, whether the closest baseline this campaign found already does what D-System claims once
actually run against it, or whether a real gap remains once tested rather than merely searched for.
None of the three experiments has been run by this dispatch; each is a proposal, tied explicitly to
the hypothesis-reading it targets and to the matrix rows establishing its baselines.
