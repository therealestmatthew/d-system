# Open research questions

Questions this campaign's prior-art search did not resolve, per `CLAUDE.md` §15's deliverable
definition. Each question below is tied to a specific hypothesis, gap, or method-level uncertainty
recorded in `06_hypothesis_tests.md`, `07_anti_novelty_case.md`, or `08_surviving_distinctions.md`,
with the matrix rows or ledger evidence that leave it open. None of these is answered here; naming a
question is not a distinctiveness claim, and none of them is presented as evidence that D-System is
or is not novel.

**Coverage caveat, binding on this document.** This list is drawn from the 67 rows this campaign
deep-read, not the full candidate pool: 336 of 400 collision candidates have never been deep-read,
including 2 of the top prescore band's 32 candidates — `dhar-vaidhyanathan-varma-agenticakm-2026`
and `epistemic-sybil-resistance-multiplying-agents-2026`, each a documented near-duplicate of a
source this campaign did deep-read, under the partner ids
`dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` and `epistemic-sybil-resistance-bara-2026`
respectively. Several questions below are, in effect, questions about what that unread remainder
would show — those are named explicitly as such, not folded into claims about the literature at
large. On search completeness: the duplicate-discovery rate fell from 20.0% (44/220, `phase-lit-06`)
to 15.0% (58/387, `phase-lit-08`) when later searches targeted previously neglected ground — a
trend, stated without asserting saturation, which this document does not claim anywhere.

---

## Questions tied to H1 — the multi-dimensional state model

**Q1. Does an established (multi-year, multi-author, peer-reviewed, or widely adopted) system exist
anywhere that combines a genuinely independent ontological+epistemic+lifecycle triple?** This
campaign's dedicated H1 collision search (`00_search_ledger.csv`, LIT-08-S001 through S024) deep-read
six candidates; the two structurally closest (`mythologiq-agent-memory-oss`,
`subit-wiki-epistemic-hmm-oss`) are both ten-weeks-old-or-newer, single-author, unreviewed
repositories, and neither combines the right axis content with genuine independence. Per
`06_hypothesis_tests.md`'s own two-condition rule, this satisfies condition 1 (a dedicated,
multi-strategy, primary-text-verified search) but not condition 2 (a mature comparator family whose
best member instantiates the same mechanism) — the search establishes that this specific, thin,
very-recent corner of GitHub and arXiv does not have the answer, not that no established framework
exists elsewhere. Open.

**Q2. If genuine three-axis independence proves difficult to sustain in an implementation, is
MythologIQ's derived-third-axis pattern (two independent enums, the third distributed across
`evidence[]`/`signals[]`/`saturation`/`certification.status`) a viable, lower-risk alternative, or
does it lose something D-System's H1 specifically needs?** This campaign found the pattern but did
not evaluate its consequences against D-System's own requirements — that comparison is what
`12_experiment_proposals.md`'s H1 experiment is designed to run. Open.

---

## Questions tied to H4 — independence-aware convergence

**Q3. Withdrawn.** Previously asked: can a closed-form, graph-topological independence discount be
extended to mixed human-agent provenance scope, or does mixed-scope graph-topological corroboration
remain genuinely unbuilt? The question rested on a two-source evidentiary base —
`epistemic-sybil-resistance-bara-2026` (AI-agent-only, its own Sec.9 leaving the practical protocol
an explicit open problem) and `barakat-corroboration-provenance-patterns-tapp2017` (an unimplemented
Eq.8 sketch) — that this campaign's own subsequent collision searches have superseded.
`06_hypothesis_tests.md`'s H4 block, re-derived clean-room by `LIT-09 H4R` (2026-09-19), adds two
further 2026 sources: `grading-narrators-isnad-rijal-claim-provenance-2026` (ISNAD) and
`not-all-agreement-counts-as-corroboration-2026` (PACT). ISNAD specifically combines graph topology,
an explicit computed discount for shared lineage, and a confirmed mixed human-agent narrator scope in
one source — evidence that bears directly on what Q3 asked. Withdrawn rather than re-aimed at a
narrower target, per the owner's ruling that a reconciliation pass drops a question whose premise the
campaign has retired instead of inventing a replacement; see `06_hypothesis_tests.md`'s H4 block for
the current evidence.

**Judgment call, flagged for review.** No row combines full mixed-agent scope with a confirmed
component_overlap of 5 ("materially equivalent mechanism") — the one honest gap
`06_hypothesis_tests.md` itself names for H4. A narrower version of Q3 (does a *materially
equivalent*, not merely component_overlap=4, graph-topological, mixed-scope discount exist?) could be
argued to still be open on the current evidence. This dispatch does not write that narrower question
in, to avoid inventing a research question during a reconciliation pass; it is named here only so the
owner can decide whether it belongs in a future pass.

**Q4. Withdrawn — resolved.** Previously asked: given the risk that H4's general/graph-topological
split was pre-loaded by a coordinator dispatch's framing rather than independently derived, would an
independently-framed re-derivation reach the same condition-2 boundary, or does the coordinator's
original framing itself determine where the line falls? This was a question about the campaign's own
method rather than about the literature, and it has since been answered by the campaign's own
subsequent work: `LIT-09 H4R` (2026-09-19) performed exactly that re-derivation, clean-room, from the
evidence alone and without being told what to conclude, and found that the split does not hold —
`06_hypothesis_tests.md`'s H4 block, `07_anti_novelty_case.md` §6, and
`08_surviving_distinctions.md`'s H4 entry all record this. Withdrawn as resolved by that
re-derivation, not merely as a premise that went stale.

---

## Questions tied to H3 — provenance as conflict-resolution input

**Q5. Why do mature, independently-built provenance systems consistently stop short of automating
conflict arbitration?** EVI's authors state resolution "ultimately require[s] human judgment"; TGMS
explicitly disables provenance-based write-back "pending... policies." `06_hypothesis_tests.md` reads
this as "some evidence that authority-weighted automated arbitration carries a correctness or
liability risk its builders did not want to accept — not proof that it is hard, but a reason the
absence may not be mere neglect." This campaign found the *pattern* of declining to automate, in two independent 2021-2026 systems, but
not the underlying reason — whether it is a demonstrated correctness risk, an unaddressed technical
difficulty, a liability concern specific to each system's domain, or simply unaddressed demand. Open.

---

## Questions tied to H5 — topology-aware context transfer

**Q6. Does any system combine all seven of H5's context-selection dimensions (state, lineage,
evidence, dissent, authority, convergence, unresolved uncertainty), and if none does, is the absence
because the combination is technically hard, because production systems have not needed it, or
because this campaign has not searched the right corner for it?** No source read at this level of
detail combines more than three or four of the seven; dissent, authority, and convergence
specifically were not found anywhere as first-class retrieval inputs. This campaign cannot
distinguish "hard," "unneeded," and "unsearched" from what it found. Open.

---

## Questions tied to H6 — integrated human-agent collective knowledge evolution

**Q7. Is there a system, in any domain, that pairs a knowledge-construction system with a
software-development-lifecycle system under one collective-evolution frame the way D-System's
two-system architecture proposes?** OmniScientist is a full, evaluated instance of integrated
human-agent knowledge evolution in scientific-research production; AgenticAKM and the ADR lineage
cover the development-lifecycle side. This campaign found no source pairing both under one frame. Q7
asks whether such a pairing exists outside the 67 rows read, not whether it is impossible — the
campaign's search was not aimed specifically at cross-domain pairings as a search target in its own
right. Open.

---

## Questions tied to H8 — phase-bounded context construction (frozen-register phrasing)

**Q8. Does any system consolidate execution results back into typed, ontologically-structured
knowledge, rather than opaque key-value state?** `burns-groth-agentic-ontological-notebook-memory-2026`
characterizes LangGraph directly — "persisted state as opaque key-value pairs rather than typed
ontological structures" — which implies the field recognizes this as a real distinction, but this
campaign found no system on either side of that distinction that also closes the loop back into
knowledge specifically (as opposed to merely recognizing the gap). Open.

---

## Questions tied to H10 — epistemic blast-radius analysis

**Q9. Does a system exist, anywhere, that propagates an epistemic retraction across the full
decision/requirement/plan/artifact/test lifecycle, at any scale — not merely within one memory
store's own derived records and tool side effects?** MemTX proves the underlying retraction-cascade
mechanism, machine-verified over 5.5 million enumerated protocol states, but scoped to one memory
store. Separately, `assumptions-management-software-development-mapping-study-2018`'s 134-study
systematic mapping independently names "Assumptions Tracing and Monitoring" as the least-studied
(14.2%) and least-tooled (2.2%-13.4%) of twelve assumption-management activities, despite the same
study's RQ8 documenting extensive real-world damage — including explicitly named hindered
change-impact analysis — from not tracing assumptions well. This is the one question in this
document where a field's own peer-reviewed survey, not just this campaign's search, independently
names the gap as real and under-addressed. Whether that reflects a genuinely hard engineering problem
or simply low investment relative to documented need is not answered by either source. Open.

---

## Questions tied to H11 — runtime-to-knowledge closure

**Q10. Is there a working system, anywhere, that closes the loop from arbitrary runtime evidence
into a revision of decision- or rationale-bearing knowledge content — not a single derived numeric
feature (Bajaj et al.'s risk-score formula, Sec.3.5-3.6), and not a mutation over a closed,
analyst-authored rule vocabulary (EvoReqs)?** The awareness-requirements lineage spans 2010-2023,
peer-reviewed at ICSE and SEAMS — a genuinely mature academic tradition — and repeatedly names this
exact loop: sawyer-bencomo (2010) states "We know of no approach that fully supports requirements
reflection"; souza-lapouchnian (2011) names the loop "at the core of our future work"; krentsel et
al. (2026) frames it as "a research agenda." Fourteen-plus years of a mature, multi-venue tradition
naming the same gap without building it is, per `06_hypothesis_tests.md`, "evidence worth weighing in
synthesis," but the file's own two-condition rule holds this short of `POTENTIALLY_DISTINCT` because
the field's best-*implemented* member (EvoReqs) solves a structurally different, rule-triggered
problem rather than a narrower instance of the same one. Q10 asks directly what that repeated naming
without building represents: a genuinely unsolved engineering problem, a problem solved outside the
requirements-engineering literature this campaign searched (a different field entirely), or a problem
this campaign's search — bounded to the corners it covered — has not yet found the answer to. Open.

---

## Questions about the campaign's own coverage

**Q11. What would the 336 never-deep-read candidates show if read — particularly for H1 and H11,
where condition 2 (comparator maturity or mechanism match) is exactly what each is missing?** This
campaign's own stop condition was met by count of sources compared (67), not by coverage of the top
prescore band (2 of its 32 candidates remain unread — see the coverage caveat above for which two).
This is not answerable by this dispatch; it is the natural next search target for a future phase, and
the question this campaign's own coverage caveat exists to keep visible rather than let the existing
67-row matrix quietly stand in for "the literature." H4's graph-topological phrasing is no longer
listed here: `06_hypothesis_tests.md`'s H4 block now finds condition 2 satisfied for that reading, so
it is not a case where the unread remainder is doing the work of an open condition-2 gap. Open.

**Q12. Is the falling duplicate-discovery rate (20.0% at `phase-lit-06`, 15.0% at `phase-lit-08`) a
real signal about the richness of the fields being searched, or an artifact of `phase-lit-08`'s
searches being deliberately aimed at previously neglected hypotheses (H1, H4, H11) rather than a
representative resampling of the whole search space?** The trend is real as measured — computed
identically both times, same either-column dedup method — but two data points aimed at different
targets do not establish a generalizable rate. A third dedicated collision pass on the same three
hypotheses, run independently, would test whether the rate keeps falling (suggesting genuinely richer
neglected ground) or rises back toward the campaign-wide baseline (suggesting `phase-lit-08`'s result
was itself a one-time effect of where it looked). Per the owner's ruling, no claim of saturation is
made either way; this question is posed, not answered, by that ruling. Open.

---

## Summary

| # | Question | Hypothesis / source | What would close it |
|---|---|---|---|
| Q1 | Does a mature comparator exist for H1's specific orthogonal triple? | H1 | A search finding a multi-year, multi-author, or peer-reviewed system combining the right axis content and independence |
| Q2 | Is MythologIQ's derived-third-axis pattern a viable alternative to full independence? | H1 | The experiment in `12_experiment_proposals.md` |
| Q3 | Withdrawn — see "Q3. Withdrawn" above | H4 (graph-topological) | N/A — superseded by `06_hypothesis_tests.md`'s unified H4 verdict |
| Q4 | Withdrawn — resolved, see "Q4. Withdrawn — resolved" above | H4, method | N/A — resolved by `LIT-09 H4R`'s clean-room re-derivation |
| Q5 | Why do mature provenance systems decline to automate arbitration? | H3 | A search aimed specifically at engineering/liability rationale in EVI's, TGMS's, or comparable systems' own design documentation |
| Q6 | Does any system combine H5's seven context-selection dimensions? | H5 | A dedicated collision search for dissent/authority/convergence as first-class retrieval inputs |
| Q7 | Does any system pair knowledge-construction and dev-lifecycle systems under one frame? | H6 | A dedicated cross-domain-pairing search, not yet run by this campaign |
| Q8 | Does any system consolidate execution results into typed knowledge, not opaque state? | H8 (frozen-register) | A dedicated search for "ontological" or "typed" state consolidation in agent-runtime literature |
| Q9 | Does cross-lifecycle epistemic-retraction propagation exist anywhere at scale? | H10 | Extending MemTX-style verification to a cross-lifecycle scope, or finding a system that already has |
| Q10 | Does a working system close the evidence-to-knowledge-revision loop H11 claims? | H11 | A search outside requirements engineering specifically, or a scoped experiment (`12_experiment_proposals.md`) |
| Q11 | What would the 336 unread candidates show? | Coverage | Deep-reading the top prescore band's remaining 2 candidates |
| Q12 | Is the falling duplicate rate a real trend or a one-time targeting effect? | Method | A third, independently-aimed dedicated collision pass |
