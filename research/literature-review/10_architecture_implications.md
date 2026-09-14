# Architecture implications

What the literature this campaign read implies for D-System's conceptual architecture
(`research/literature-review/CLAUDE.md` §3) and for the architecture actually encoded in the
codebase, per `CLAUDE.md`'s requirement that the review compare prior art against both. This file
records implications only. It makes no code change, no edit outside `research/literature-review/`,
and no architecture revision — per `CLAUDE.md` §2, revising D-System's architecture is later
synthesis-phase work by other dispatches, not this file's job. Each implication below is anchored to
a specific hypothesis verdict in `06_hypothesis_tests.md` or a specific matrix row.

**Coverage caveat, binding on this document.** Every implication below is bounded by what this
campaign's 49 deep-read matrix rows actually found, not by the full candidate pool: 340 of 387
collision candidates have never been deep-read, including 20 of the top prescore band's 32
candidates. An implication phrased as "the literature does not show X" means this campaign's search
did not surface a source showing X, not that no such source exists. On search completeness: the
duplicate-discovery rate fell from 20.0% (44/220, `phase-lit-06`) to 15.0% (58/387, `phase-lit-08`)
when later searches targeted previously neglected ground — a trend, stated without asserting
saturation, which this document does not claim anywhere.

---

## 1. Implications for the conceptual architecture

### 1.1 The provenance/decision/requirement layer should be built on established vocabulary, not
    invented from scratch

H2, H7, and H9 all landed `LIKELY_ALREADY_KNOWN`, and H3 at `KNOWN_COMPONENT_NEW_INTEGRATION` — the
densest, most heavily-corroborated region of the whole review (H9 alone drew eighteen of the
matrix's 49 rows). The conceptual architecture's transition-provenance primitive, decision objects,
and bidirectional traceability claim are, on the literal wording of these hypotheses, restatements of
PROV-O, the AGM/ADR/digital-thread lineages, and requirements-traceability research respectively (see
`09_reuse_recommendations.md`, recommendations 1, 2, 4, 8). The implication for the conceptual
architecture is not that these primitives are wrong to keep — the campaign's own method treats
"known components, integrated" as a successful finding, not a defect (`CLAUDE.md` §14) — but that
documenting them as established, vocabulary-mapped concepts rather than original inventions is what
the evidence supports, and what any downstream design or requirements document describing them
should reflect.

### 1.2 H3's conflict-resolution step is where the architecture should mark an explicit, separately-
    gated decision point, not an implicit consequence of having provenance

H3 found that two independent, mature 2021-2026 provenance systems (EVI and TGMS) built rich,
typed, multi-actor provenance machinery and then deliberately declined to automate conflict
arbitration on top of it — EVI's own text states resolution "ultimately require[s] human judgment,"
and TGMS explicitly disables provenance-based write-back "pending... policies." `06_hypothesis_tests.md`
records this as "some evidence that the combination carries a correctness or liability risk its
builders did not want to accept — not proof that it is hard, but a reason the absence may not be
mere neglect." The implication: if D-System's conceptual architecture treats automated,
provenance-weighted conflict resolution as a natural extension of having provenance data, the
literature suggests two careful engineering teams considered and rejected exactly that step. The
architecture should treat automated arbitration as its own explicit, separately-justified design
decision — with the risk named — rather than a default consequence of the provenance layer existing.

### 1.3 H4's frozen-register graph-topological phrasing and its review-instructions general phrasing
    imply two different architectural commitments, and the conceptual documents should not conflate
    them

`06_hypothesis_tests.md` treats H4 as genuinely splitting by phrasing, and this document carries that
split forward without blending it, per the same rule the hypothesis file itself applies. Under the
review-instructions' general phrasing (independent paths strengthen weight, derivative agreement is
discounted), the mechanism is established: Goldman (2001) is a peer-reviewed, 25-year-old, closed-form
proof of exactly this, extended by Mayo-Wilson (2014). The implication for that reading is
recommendation 7 of `09_reuse_recommendations.md` — inherit the arithmetic rather than deriving it.
Under the frozen register's sharper claim — computing the discount *from an explicit provenance-graph
topology*, at *mixed human-agent scope* — no source found combines both properties with maturity:
`epistemic-sybil-resistance-bara-2026` is graph-topological and closed-form but AI-agent-only, with
its own Sec.9 naming the practical protocol as an open problem; `barakat-corroboration-provenance-patterns-tapp2017`
is broader in scope but its discount term (Eq.8) is an unimplemented sketch that never reappears in
the paper. If the conceptual architecture commits specifically to graph-topological computation of
this discount at mixed human-agent scope — the frozen register's own wording — that specific
commitment has no established literature to inherit from; it would need original design and
validation, which is what `12_experiment_proposals.md`'s H4 experiment is built to test before
committing engineering effort to it.

**Carried caveat, binding wherever this document relies on H4's status.** Per the owner's ruling
closing `phase-lit-08`: the general/graph-topological split itself, and the finding that the general
reading clears the bar for `KNOWN_COMPONENT_NEW_INTEGRATION`, was pre-loaded by a coordinator
dispatch's framing rather than independently derived by the worker who ran the search. The worker
disclosed this unprompted, and the independent close review judged the risk real and contestable.
This document treats the split exactly as settled as `06_hypothesis_tests.md` itself treats it — no
more, no less — and any re-derivation of the split or the status is a decision for the owner, not
this dispatch.

### 1.4 H5's seven-dimension context-selection claim should be treated as an explicit hypothesis to
    validate, not an assumed consequence of using a mature retrieval architecture

Topology/lineage/recency-aware retrieval beyond plain semantic similarity is thoroughly established
(Zep/Graphiti's traversal-plus-recency pipeline, EM-LLM's peer-reviewed episodic retrieval,
solozobov's memory-tier context compiler) — but per `06_hypothesis_tests.md`, no single source found
combines more than three or four of the seven dimensions H5 specifies (state, lineage, evidence,
dissent, authority, convergence, unresolved uncertainty), and dissent/authority/convergence
specifically were not found as first-class retrieval inputs anywhere at this detail. The implication:
the mechanism *family* being mature does not make the specific seven-dimension combination
low-risk by association. The conceptual architecture should document H5's full enumeration as an
untested design choice on its own terms, not inherit confidence from the maturity of the narrower,
well-covered sub-mechanisms it is built from.

### 1.5 H6's distinctiveness claim, if any survives, rests on the two-system pairing itself — the
    architecture's documentation should locate the claim there, not in either system alone

H6 landed `KNOWN_COMPONENT_NEW_INTEGRATION`: OmniScientist is a full, empirically-evaluated instance
of integrated human-agent collective knowledge evolution in the scientific-research domain (0.22
Human-AI Collaboration accuracy vs. 0.10 Human Solo vs. 0.00 AI Solo, same case study), and its own
architecture is itself a recombination of nanopublication/PROV-O patterns and existing agent
protocols (MCP, A2A). No source found substantially subsumes D-System's specific two-system,
dual-domain pairing (Knowledge Construction & Management paired with Implementation & Experience
under one collective-evolution frame) — but each half independently has a demonstrated, evaluated
analog elsewhere: OmniScientist for the knowledge-construction side, AgenticAKM and the ADR lineage
for the development-lifecycle side. The implication for the conceptual architecture: whatever
distinctiveness case D-System makes should rest explicitly on the *pairing under one frame*, not on
either system's primitives, since the primitives are independently accounted for elsewhere in this
review (H2, H3, H7, H9 for the knowledge system; H7, H9's ADR/digital-thread evidence for the
development system).

### 1.6 H8's frozen-register consolidation half, H10's cross-lifecycle span, and H11's evidence-
    driven revision are the three points the architecture documents should flag as carrying the
    least literature support

H8's frozen-register phrasing, H10, and H11 share a shape `06_hypothesis_tests.md` names directly for
H10 and echoes for the other two: the underlying mechanism piece is separately proven (MemTX's
verified retraction-cascade for H10; LangGraph's/Durable Functions' replay-and-assembly machinery for
H8's assembly half), but the *specific scope* D-System's hypotheses claim — consolidation into
typed, ontological knowledge rather than opaque state (H8); propagation across the full
decision/requirement/plan/artifact/test lifecycle rather than one memory store's own derived records
(H10); revision of decision/rationale content from arbitrary runtime evidence rather than a
rule-triggered mutation over a closed vocabulary or a single derived metric (H11) — is not
demonstrated combined anywhere this campaign read. For H10 specifically, the field's own 134-study
systematic mapping (`assumptions-management-software-development-mapping-study-2018`) independently
names cross-lifecycle assumption tracing as the least-tooled of twelve identified activities despite
well-documented real-world damage from its absence — this is not just an absence in what this
campaign found, but a gap the field's own survey literature names. The implication for the conceptual
architecture: these three points are where the architecture is proposing something the literature
suggests nobody has built at the claimed scope, not routine engineering assembled from known parts.
Any conceptual-architecture document describing H8's consolidation half, H10, or H11 should flag them
at a different confidence level than H2/H3/H7/H9, and `12_experiment_proposals.md` ties H11 (and,
separately, H4's graph-topological reading and H1) to experiments aimed at resolving exactly this
uncertainty before further design investment.

### 1.7 H1's orthogonal state-model claim is the architecture's least-supported primitive, and the
    two closest real-world comparators point at two different possible resolutions

H1 found six candidates and none combined the right axis *content* with genuine independence and an
established comparator family: `mythologiq-agent-memory-oss` has two of the right axes (ontological
type, lifecycle stage) as independent JSON-Schema enums but distributes the third (epistemic
classification) across four separate fields rather than tracking it as one independently-varying
value; `subit-wiki-epistemic-hmm-oss` has three genuinely independent axes combined into a
64-state code with a working Viterbi decoder, but of the wrong content (discourse stance, not
ontological/epistemic/lifecycle). The implication for the conceptual architecture is concrete and
double-edged: the *closest* real precedent to D-System's H1 claim (MythologIQ) achieves two axes
cleanly and derives the third rather than tracking it independently — which is itself a design
option D-System's own architecture could adopt deliberately rather than by default, if genuine
three-way independence turns out to be difficult to sustain in practice. Whether independent tracking
of all three axes is worth the added complexity over MythologIQ's derived-third-axis approach is
exactly the kind of question `12_experiment_proposals.md`'s H1 experiment is built to answer with
evidence rather than architectural preference.

---

## 2. Implications for the implemented architecture

### 2.1 The shipped checkpoint mechanism is currently behind a production open-source library on the
    dimension the literature identifies as central to H8

The matrix row for `langgraph-checkpoint-library-oss` records, citing the adversarial codebase review
(`research/adversarial-codebase-review/04_state_transition_audit.md`, finding E42), that D-System's
own shipped checkpoint mechanism (`.claude/skills/checkpoint/SKILL.md`) currently rewrites/overwrites
summary sections in place, rather than retaining a parent-linked chain of past checkpoints the way
LangGraph's checkpointer does at production scale (41,574 GitHub stars, per-superstep persisted
checkpoints with parent-chain lineage enabling backward walk and "time travel" replay). This is not a
conceptual gap; it is a gap between what is implemented today and what an openly available,
widely-deployed library already does. The implication for the implemented architecture: on the
specific parent-chain-retention dimension, adopting or studying LangGraph's checkpoint model
(`09_reuse_recommendations.md`, recommendation 10) closes a gap the literature shows is already
solved elsewhere, without requiring new mechanism design.

### 2.2 The same gap the literature names in LangGraph — opaque state, not typed knowledge — means
    closing 2.1 alone would not satisfy H8's fuller, frozen-register claim

`burns-groth-agentic-ontological-notebook-memory-2026` characterizes LangGraph directly: it treats
"persisted state as opaque key-value pairs rather than typed ontological structures" (per
`06_hypothesis_tests.md`'s H8 block). This is the field naming, in its own words, exactly the
limitation that separates H8's review-instructions phrasing (assembly and consolidation over generic
execution state — already known, per §1.1) from its frozen-register phrasing (consolidation into
persistent, epistemic, *knowledge-bearing* memory specifically — not demonstrated anywhere this
campaign read, per §1.6). The implication for the implemented architecture: adopting LangGraph's
parent-chain mechanism (2.1) would close the assembly-half gap the adversarial codebase review found,
but would not, on its own, close the consolidation-into-knowledge gap the frozen register's fuller
claim requires — that remaining half is where H8 still carries the least literature support, per
§1.6 above.

### 2.3 Nothing in this campaign's matrix rows characterizes any part of D-System's actually-shipped
    code beyond the one checkpoint-mechanism comparison already on record

The adversarial codebase review is the authoritative source for what D-System's implementation
actually does (`CLAUDE.md` §1); this campaign's own search was aimed at literature, not at a fresh
audit of the codebase. Beyond the checkpoint-mechanism finding carried in §2.1-2.2 (already recorded
on the `langgraph-checkpoint-library-oss` matrix row, not independently re-derived here), this
document draws no further comparison between the literature and D-System's shipped code, and none
should be inferred from its absence — a further implementation-level comparison, if wanted, is a
separate research task this file does not perform.

---

## Summary

| Hypothesis | Conceptual-architecture implication | Implemented-architecture implication |
|---|---|---|
| H1 | Least-supported primitive; MythologIQ's derived-third-axis design is a real alternative to independent tracking, worth testing (§1.7) | None recorded |
| H2, H7, H9 | Document as vocabulary-mapped, established concepts (PROV-O/AGM/ADR/digital-thread), not inventions (§1.1) | None recorded |
| H3 | Conflict resolution should be an explicit, separately-gated decision, not an implicit consequence of provenance (§1.2) | None recorded |
| H4 | Two distinct commitments by phrasing; graph-topological/mixed-scope commitment has no established literature to inherit (§1.3, caveat carried) | None recorded |
| H5 | Seven-dimension combination is an untested design choice, not inherited maturity (§1.4) | None recorded |
| H6 | Distinctiveness claim, if any, belongs to the pairing, not either constituent system (§1.5) | None recorded |
| H8 | Frozen-register consolidation half is the least-supported reading (§1.6) | Assembly-half gap vs. LangGraph is closeable with an existing library (§2.1); consolidation-into-knowledge gap is not closed by that alone (§2.2) |
| H10 | Cross-lifecycle span is a field-recognized, least-tooled gap, not routine assembly (§1.6) | None recorded |
| H11 | Evidence-driven revision of decision/rationale content is the least-supported claim in the review (§1.6) | None recorded |

No implication above is a claim that D-System should be renamed, narrowed, or redesigned; each is a
recorded gap or a recorded point of support, for other, later-phase dispatches to act on under
`CLAUDE.md` §2's synthesis-only revision rule.
