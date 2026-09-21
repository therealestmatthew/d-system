# Hypothesis tests — H1 through H11

> **Reconciled against the second reviews, 2026-09-14.** `phase-lit-06` ran nineteen independent
> second reviews of the `critical_collision: yes` rows in `04_evidence_matrix.csv` (6 confirmed, 13
> disputed; verdicts recorded in `05_critical_collisions.md`, one dated `### Review — 2026-09-14`
> subsection per row) but did not itself update this file. This pass folds those reviews' findings
> into the blocks below. Per the owner's ruling, the matrix's scores and `critical_collision` flags
> were left exactly as first assessed even where a review disputed them — a dispute is a recorded
> judgment call, not an applied correction — so this file's `strongest_challenger` overlap scores
> still cite those first-assessed values. What changed here is which sources are credited as
> challenging which hypothesis, and in two cases (H1, H11) the resulting status, based on what the
> reviews established the sources' own primary text actually says. A reader of this file alone
> should treat its verdicts as post-dating and superseding the pre-review reading of the same
> sources in `05`'s un-reviewed first-assessment prose.

> **Further reconciled against `phase-lit-08`'s dedicated collision searches, 2026-09-14
> (`LIT-08 X5`).** `phase-lit-08` ran the first search purpose-built for each of H1, H4 and H11 —
> the three hypotheses this file's own decision rule (below) had flagged as never having had one —
> and deep-read fifteen new sources across them, five newly flagged `critical_collision: yes` and
> all five independently second-reviewed as `confirmed`. This pass re-derives only the H1, H4 and
> H11 blocks and the decision rule itself against that new evidence; the other eight blocks are
> untouched. Per the same owner ruling that shaped the prior reconciliation,
> `04_evidence_matrix.csv` and `05_critical_collisions.md` are not edited here — this file's
> `strongest_challenger` entries cite the matrix's already-recorded scores directly.

> **Further reconciled against `phase-lit-09`'s H4 clean-room re-derivation, 2026-09-19 (`H4R`,
> commit `7141767`).** Two new evidence-matrix rows found by this phase's own collision searches —
> grading-narrators-isnad-rijal-claim-provenance-2026 and not-all-agreement-counts-as-corroboration-
> 2026 — were read after the `LIT-08 X5` reconciliation above had already run and closed, and
> neither was considered by it. `H4R` re-derived the H4 block from the evidence alone against that
> new material and found the split verdict `LIT-08 X5` gave H4 (`KNOWN_COMPONENT_NEW_INTEGRATION`
> for the review-instructions general phrasing, `INSUFFICIENT_EVIDENCE` for the frozen register's
> graph-topological phrasing) no longer holds: both phrasings now converge on
> `LIKELY_ALREADY_KNOWN`. Only the H4 block was re-derived. This pass (`phase-lit-09 X5`, fix cycle
> 1) reconciles the surrounding shared prose and the summary table to the new H4 block — the
> decision-rule paragraph below and the summary table's H4 row previously described the superseded
> split verdict as current; both are corrected here to describe it as historical and to state the
> current verdict from the H4 block itself. No block content is touched by this reconciliation pass;
> all eleven `## H<n>` blocks remain exactly as `H4R` committed them.

Verdicts follow `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md`.
Per that record, the review-instructions text (`research/literature-review/CLAUDE.md`, §4) is
primary; a frozen-register (`research/pre-literature-hypotheses.yaml`) nuance is noted wherever
it changes the assessment, never blended into a merged phrasing. `strongest_challenger` cites
`research/literature-review/04_evidence_matrix.csv` rows by `source_id`; every `evidence` line
carries a locator from that row's `evidence_locator`/`verbatim_notes` fields. Status vocabulary is
exactly `LIKELY_ALREADY_KNOWN`, `KNOWN_COMPONENT_NEW_INTEGRATION`, `POTENTIALLY_DISTINCT`,
`INSUFFICIENT_EVIDENCE` — `NOVEL` is not available to this review, and no verdict below asserts
"no prior work exists"; where a search found nothing it is recorded in
`00_search_ledger.csv`, not here.

Each `assessment` states the best case that D-System is not distinct on that hypothesis before
any counter-argument, per the campaign's method.

**Decision rule: `POTENTIALLY_DISTINCT` vs `INSUFFICIENT_EVIDENCE`.** Both statuses can describe
the same surface pattern — every candidate found for a hypothesis has been read closely and none
demonstrates the claimed mechanism at full scope — so the two are easy to conflate. The line
between them is not what the found candidates show; it is what the *search* supports concluding
about what has not been found. `POTENTIALLY_DISTINCT` requires the absence of a match to be
attributable to the mechanism genuinely not existing elsewhere, which in turn requires the search
that failed to find it to have plausibly covered the relevant ground — either of two routes:
approaching saturation (a falling duplicate-discovery rate across the campaign as a whole), or a
dedicated collision search for that specific hypothesis that still returned nothing better.
`INSUFFICIENT_EVIDENCE` is the status whenever neither route is satisfied, regardless of how well
or poorly the individual candidates read on inspection — because the open question in that case is
not "is the mechanism known" but "has this campaign looked hard enough to say."

*Route one — saturation — is closed to every hypothesis right now.* The owner has ruled that
saturation may not be claimed at this stage (pre-synthesis check-in, ruling 8). `LIT-06 G` measured
a campaign-wide duplicate rate of 20.0% (44/220 raw result identifiers; 36/208 = 17.3% on a
distinct-identifier basis). This phase's own three dedicated collision searches measure lower
still. Population: all 82 `LIT-08-*` rows in `00_search_ledger.csv` (24 tagged `domain_id: H1`, 32
`H4`, 26 `H11`), every semicolon-separated identifier in each row's `result_ids` field, checked for
membership in `03_source_inventory.csv` as it stood immediately before this phase started (commit
`83fb42b^`, the parent of the first `LIT-08` search, i.e. before any `LIT-08` row could itself add
an entry to the inventory it is being checked against) on either that snapshot's `source_id` or
`url_or_doi` column — the same either-column method `LIT-06 G` used and confirmed identical.
Result: 58/387 = 15.0% raw duplicates, 37/347 = 10.7% on a distinct-identifier basis (347 unique
identifiers across the 387 raw mentions) — a falling duplicate rate, i.e. a *rising* share of
genuinely new material, the opposite of the signal saturation would produce. That is a trend
against saturation, not toward it, and it holds even domain-by-domain, computed the same way but
restricted to each domain's own rows: H1's own searches ran the highest of the three at
39/156 = 25.0%, H4's the lowest at 4/66 = 6.1%, H11's at 15/165 = 9.1% — every one of them far
short of anything resembling "mostly yield duplicates," the methodology's own stop-condition
language (§18). Route one stays closed for all three hypotheses uniformly, regardless of these
differences between them.

*Route two — a dedicated collision search that still returns nothing better — is what this phase
exists to test, and it needs a sharper statement than this file previously gave it.* The prior text
held up "H4's Pass 3" as the worked example of a search that would satisfy the bar, while H4's own
block then called that same search "thinner, not thicker" and insufficient — an inconsistency
between the rule's stated example and the rule's applied bar, flagged and left open at
`SESS-2026-09-14-01`. Resolved here: a dedicated collision search satisfies route two only when it
clears two conditions together, not one —

1. **Search depth.** It runs multiple independent strategies against the hypothesis specifically —
   vocabulary/terminology-translation discovery, backward citation chaining to the mechanism's
   likely theoretical ancestors, and direct collision-style queries — and it deep-reads the primary
   text of the candidates it surfaces rather than resting on an abstract or a generated summary,
   verifying any claimed match against that primary text before crediting it (the exact failure
   this file's own H1 and H11 blocks below record catching, in `burns-groth`).
2. **Comparator quality.** The closest candidates the search turns up, taken together, constitute a
   genuinely mature, on-topic comparator family — established, multi-source, ideally multi-year —
   not a single very-recent, single-author, unreviewed item; *and* at least the closest member of
   that family instantiates the same mechanism the hypothesis claims, even if narrower in scope,
   rather than a structurally different mechanism that merely sits in the same neighborhood.

Condition 1 alone is not enough: a thorough, well-run search of a field that turns out to be thin
or immature has shown that corner of the field is thin, not that the mechanism is absent from the
wider literature — the search covered its own ground well without covering enough of the *right*
ground to license a conclusion either way. Condition 2's second half exists because a mature but
mechanism-mismatched comparator family is a false friend: finding that an adjacent, well-studied
tradition solves a related-but-different problem is not evidence about whether the claimed
mechanism exists elsewhere — it means the search struck the wrong neighborhood, however well-studied
that neighborhood is. Only when both conditions hold — a well-run search finds a mature family, and
the family's best member is a genuine (if partial) instance of the claimed mechanism rather than a
different one — does a negative or partial-only result license `POTENTIALLY_DISTINCT`; short of
that, a hypothesis stays at `INSUFFICIENT_EVIDENCE` regardless of how many queries were run, because
what is missing is not effort but *the right kind of finding*, a fact about the field, not about how
hard this campaign looked.

H1, H4, and H11 were assessed against this two-condition rule when `phase-lit-08` ran a dedicated
collision search against each for the first time, satisfying condition 1 for all three alike at that
point. Where they differed was condition 2, and each difference was argued explicitly in its own
block rather than merely asserted: H1's comparator family fails on maturity (four candidates, the
most-implemented eleven weeks old and single-author, one proving a formally different triple
entirely) — unchanged since. H11's comparator family is mature (a 2010–2023 peer-reviewed lineage,
plus two 2026 preprints) but its best-implemented member is a different mechanism shape — a
closed, hand-authored control-loop reaction, not a narrower instance of H11's evidence-revises-
knowledge claim — also unchanged since. H4, at that point, split by phrasing — its general
(review-instructions) reading had a genuine, mature, same-mechanism comparator (Goldman 2001,
backward-chained that phase from Mayo-Wilson 2014), moving that one reading's status to
`KNOWN_COMPONENT_NEW_INTEGRATION`, while its frozen-register graph-topological reading still failed
on maturity in the same shape as H1's and stayed `INSUFFICIENT_EVIDENCE`. That split verdict has
since been superseded: two further sources found by `phase-lit-09`'s own collision searches
(grading-narrators-isnad-rijal-claim-provenance-2026 and
not-all-agreement-counts-as-corroboration-2026) closed the maturity gap on the graph-topological
reading as well, and a clean-room re-derivation (`phase-lit-09 H4R`) converged both phrasings on a
single `LIKELY_ALREADY_KNOWN` verdict — see the H4 block below, which is the current source of
truth. H1 and H11 remain as `phase-lit-08` left them: neither clears both conditions for
`POTENTIALLY_DISTINCT`. `NOVEL` remains unavailable to all three.

---

## H1 — Multi-dimensional state model

```yaml
hypothesis: >
  Orthogonal ontological + epistemic + lifecycle classifications for knowledge states may be
  uncommon in agent-memory systems. (Review-instructions text, primary.) The frozen register
  narrows the claim to classifications "not commonly integrated in existing agent-memory
  systems" and adds "idea/action" to the lifecycle dimension — a difference this verdict
  addresses explicitly below, per the scope record's flagged H1 divergence.
strongest_challenger: >
  eywa-provenance-grounded-memory-joshi-2026 (component_overlap=4, architecture_overlap=3,
  full_text) and burns-groth-agentic-ontological-notebook-memory-2026 (component_overlap=4,
  architecture_overlap=3, preprint_version) were the only two matrix rows listing H1 in
  `hypotheses_challenged` before this phase; independent review of both (`05_critical_collisions.md`,
  sources 18 and 16) found the specific claim each was credited with — a genuinely orthogonal
  three-axis classification — does not survive a full-text read of either. `phase-lit-08` ran H1's
  first dedicated collision search (`00_search_ledger.csv`, LIT-08-S001 through S024: vocabulary
  discovery, backward citation chaining, and direct collision queries) and deep-read four new
  candidates: mythologiq-agent-memory-oss (component_overlap=4, architecture_overlap=3, full_text,
  `critical_collision: yes`, second review: confirmed) and subit-wiki-epistemic-hmm-oss
  (component_overlap=4, architecture_overlap=2, full_text, `critical_collision: yes`, second
  review: confirmed) are now the closest partial matches found for H1 across the whole campaign;
  toki-bitemporal-operator-algebra-contradiction-2026 (component_overlap=3,
  architecture_overlap=2, full_text) and symbolic-memory-prolog-oss (component_overlap=2,
  architecture_overlap=1, full_text) are weaker but read in full below for completeness.
  `phase-lit-09` added two further H1-tagged rows via its general deep-extraction and reconciliation
  batches, not a dedicated H1 search: grading-narrators-isnad-rijal-claim-provenance-2026
  (component_overlap=5, architecture_overlap=3, full_text, `critical_collision: yes`, second review:
  disputed — component re-derived 5->4, flag unaffected, hypotheses_challenged H1;H3;H4 confirmed as
  appropriately hedged) and provenance-enhanced-statements-dec-2026 (component_overlap=4,
  architecture_overlap=3, full_text, `critical_collision: yes`, second review: disputed — component
  re-derived 4->3, reviewer concludes no trigger fires). Neither displaces mythologiq or subit-wiki as
  the closest match; both are read in full below.
evidence:
  - >
    (Unchanged from the prior reconciliation.) eywa, Table 2 / Sec.4.3, and burns-groth, Sec.3.2-3.3:
    both credited at first assessment with a genuinely orthogonal three-axis classification. Full-text
    review found eywa's five object types carry a deterministic one-to-one mapping to Mutability and
    epistemic tier — one axis restated, not three independent ones, and the word "orthogonal" appears
    nowhere in the paper — and Burns & Groth's ICE split is a type *hierarchy* (Artifact/Fragment/Note
    nested under Information Content Entities), not orthogonal axes applied uniformly. eywa also fails
    H1's own falsification bar on procedural grounds: a three-and-a-half-month-old, single-author,
    non-peer-reviewed preprint is not "a materially equivalent established framework."
  - >
    toki-bitemporal-operator-algebra-contradiction-2026 (full HTML text, arxiv.org/html/2606.06240v1,
    read across two extraction passes): a formally PROVEN three-orthogonal-axis system — four
    soundness theorems over a semiring-based provenance algebra — the strongest primary-source
    precedent found in this campaign for orthogonality *proven* rather than merely asserted. But the
    three axes it proves orthogonal are isolation/schema/provenance (Sec.2.2, 3.1, 3.3), write-time
    concurrency-control dimensions of a bitemporal fact store, not D-System's
    ontological/epistemic/lifecycle triple on a knowledge state — a different triple by content, with
    no ontological-type axis and no lifecycle axis anywhere in the paper, confirmed on full-text read.
  - >
    mythologiq-agent-memory-oss (README, five JSON Schemas, META_LEDGER.md, all read in full;
    github.com/MythologIQ-Labs-LLC/agent-memory): the closest structural match found in the whole
    campaign — `type` (an 18-value ontological content-category enum) and `state` (a 15-value
    lifecycle-stage enum) are two genuinely independent enum axes on one memory-unit record, confirmed
    by reading the JSON Schema directly rather than the README's prose. Second review re-derived the
    score independently and confirmed both the 4/3 overlap and the critical-collision flag. But the
    third axis — D-System's epistemic classification — is not a single field here: it is distributed
    across `evidence[]`, `signals[]`, `saturation`, and `certification.status`, which the matrix row's
    own `strongest_difference` records as "arguably more expressive... but not the same structure."
    Procedurally thin on the falsification bar: a single-author Apache-2.0 repository, 748 commits but
    12 stars, no published evaluation, ten weeks old as of this phase's search.
  - >
    subit-wiki-epistemic-hmm-oss (README, full schema, decoder source, all read in full;
    github.com/sciganec/subit-wiki): a real, working implementation of three independent 2-valued
    axes combined into a 64-state code, decoded via a genuine log-space Viterbi HMM — the same
    combinatorial-state-space-plus-probabilistic-transition shape as D-System's H1 and H2 claims
    combined. Second review confirmed the 4/2 score and flag. But the three axes (WHO/WHERE/WHEN)
    encode discourse/rhetorical stance — perspective, argumentative move, maturity phase — not
    D-System's type/epistemic-status/lifecycle content, confirmed by direct schema reading.
    Procedurally thinner still: the repository's LICENSE file is a 3-byte stub, not license text
    (GitHub's own API classifies it `license: other, NOASSERTION`), and the self-evolving ontology
    loop the source was nominated for fails 2 of its own 9 tests.
  - >
    symbolic-memory-prolog-oss (README, IMPLEMENTATION-STATUS.md, source, four open issues, all read
    in full; github.com/lost-rob0t/symbolic-memory): Kind and Lifecycle exist as separate fields on
    every memory record in the implemented code, but neither carries an enforced enum, and every
    H1/H2/H4-relevant primitive beyond those bare fields exists only as open-issue design prose,
    confirmed absent from the shipped code by a zero-hit search for the design issues' own named
    predicates.
  - >
    grading-narrators-isnad-rijal-claim-provenance-2026 (full HTML text, arxiv.org/html/2607.24117v1,
    Sec.4.1-4.2 actor/provenance-model fields, read as part of the `phase-lit-09` deep-extraction
    batch, not a dedicated H1 search): a genuine two-axis state — an ordinal, weakest-link chain grade
    plus a claim lifecycle/serve-review-quarantine status — attached to every claim, governed by a
    domain-conditioned, version-sensitive narrator-authority registry with an open-source, tested
    (157 passing tests) reference implementation. Second review confirmed this framing as
    appropriately hedged, not an overstatement, and re-derived the component score from 5 to 4 (flag
    unaffected). But the state carries only two axes — grade and lifecycle — not D-System's three;
    an ontological-type axis independent of both is absent entirely, the same content gap mythologiq
    and eywa already show, just with a different pair of fields present and a different one missing.
  - >
    provenance-enhanced-statements-dec-2026 (full HTML text, arxiv.org/html/2606.15246v1,
    Sec.3.2.2/4.2-4.3): a single epistemic-modality axis (doxastic/epistemic/conjectural/verbatim/
    delusional) with no ontological-type or lifecycle-stage axis anywhere in the paper — the weakest
    H1 state-model candidate found across the whole campaign, not merely a mismatched-content triple
    but one axis where D-System proposes three. Second review re-derived the component score from 4
    to 3 specifically because "state model has one epistemic-modality axis against D-System's
    orthogonal ontological×epistemic×lifecycle triple" and confirmed no trigger fires.
assessment: >
  The best case that D-System's orthogonal ontological+epistemic+lifecycle state model is already
  known now draws on eight sources rather than two, and the strongest of the six new candidates come
  closer than eywa or Burns & Groth ever did. mythologiq-agent-memory-oss genuinely has two of D-System's
  three axes as independent enums on one record, confirmed against its JSON Schema rather than its
  README; subit-wiki-epistemic-hmm-oss is a real, working three-axis-to-combinatorial-state
  implementation with a probabilistic typed-transition decoder, the same shape H1 and H2 propose
  together; toki proves three axes orthogonal with a rigor (four soundness theorems) nothing else in
  this review's H1 evidence approaches. If any one of these combined the right three axes with that
  level of rigor and maturity, H1's "uncommon" framing would be in real trouble.
  None of them does. toki's proven triple is the wrong one — isolation/schema/provenance, not
  ontological/epistemic/lifecycle — a different formalism entirely, not a looser version of
  D-System's. mythologiq has the right two axes (type, lifecycle stage) but distributes the third
  across four separate fields rather than tracking it as one independently-varying value. subit-wiki
  has three genuinely independent axes but of the wrong content (discourse stance, not D-System's
  ontological/epistemic/lifecycle triple). eywa and Burns & Groth, as already established, turn out
  on close reading not to be orthogonal at all. grading-narrators-isnad has the right shape for two
  axes (an ordinal grade, a lifecycle status) but no third; provenance-enhanced-statements has only
  one axis of any kind. Eight candidates, eight different ways of missing the specific claim, and not
  one candidate that gets the axis *content* and the *independence* and the *maturity* right together.
  Checked against this file's two-condition rule for route two of `POTENTIALLY_DISTINCT`: `phase-lit-08`'s
  search satisfies condition 1 in full — vocabulary discovery, backward chaining, and direct
  collision queries were all run specifically for H1, for the first time in this campaign, and every
  candidate was deep-read from primary text rather than credited from a summary (the same discipline
  that caught eywa and burns-groth's overclaims in the first place). `phase-lit-09` ran no dedicated
  H1 search of its own — its two additions arrived via general deep-extraction and reconciliation
  batches — so it neither strengthens nor needs to re-argue condition 1; it only supplies two more
  data points for condition 2, and neither moves it. Condition 2 is where the hypothesis fails.
  The six new candidates are not a mature, established comparator family: the most implemented
  (mythologiq) is ten weeks old, single-author, 12 stars, unreviewed; subit-wiki is a smaller hobby
  project with 2 of 9 tests failing; symbolic-memory implements almost none of what it was nominated
  for; only toki carries formal weight, and it proves an unrelated triple. grading-narrators-isnad is
  the most procedurally mature of the six (157 passing tests, Zenodo-archived, Apache-2.0) but is
  still a single-author, ~2-month-old preprint, and its own second review confirms it as two axes,
  hedged, not three; provenance-enhanced-statements is a similarly recent single-author preprint with
  a single axis. H1's own falsification bar asks for "a materially equivalent *established* framework"
  — a thorough search of this specific, thin, very-recent corner of GitHub and arXiv does not
  establish that no such framework exists elsewhere; it establishes that this corner doesn't have
  one. That is a genuine, re-examined finding, not a restatement of the prior assessment, and it
  leaves the verdict exactly where it was: this campaign has not searched enough of the *right*
  ground to say the claim is absent, only enough of this ground to say these eight candidates are not
  it. The frozen register's narrower "not commonly integrated" phrasing does not change this —
  mythologiq's distributed epistemic axis, subit-wiki's wrong-content triple, grading-narrators-isnad's
  missing third axis, and provenance-enhanced-statements' single axis all remain materially different
  mechanisms from an orthogonal (O,E,L) triple, not looser instances of the same one, under either
  phrasing. Status is unchanged from the prior reconciliation: this phase's two incidental additions
  are re-examined and found not to change it, not silently carried forward.
status: INSUFFICIENT_EVIDENCE
```

---

## H2 — Typed transition semantics as reasoning memory

```yaml
hypothesis: >
  Explicit typed transitions between append-only knowledge states preserve reasoning history
  separately from semantic relationships. (Review-instructions text; no material frozen-register
  divergence flagged for H2.)
strongest_challenger: >
  graph-native-cognitive-memory-belief-revision-semantics-2026 (component_overlap=5,
  architecture_overlap=4, preprint_version) and jansen-bosch-architecture-as-decisions-wicsa-2005
  (component_overlap=5, architecture_overlap=4, full_text) — the two highest component-overlap
  scores in the entire evidence matrix. Both scores are disputed on independent second review
  (`05_critical_collisions.md`): the reviewer re-derives Kumiho to component_overlap=4/
  architecture_overlap=3 (the flag surviving on the component trigger alone, not two independent
  triggers) and Jansen & Bosch to component_overlap=3/architecture_overlap=2 (the flag surviving
  only via the directly-falsifies trigger — idea-level anticipation of H2 — not mechanism-level
  equivalence, since no tool existed at publication). Per the owner's ruling that disputes are
  recorded, not applied, the matrix's original 5/4 scores stand undisputed-unapplied, and this
  file's citations continue to use them. `phase-lit-09` adds three more H2-tagged rows, none of
  which unseats Kumiho or Jansen & Bosch: provenance-enhanced-statements-dec-2026 (H1;H2;H3,
  component_overlap=4, architecture_overlap=3, full_text, `critical_collision: yes`, second review:
  disputed — component re-derived 4->3, no trigger fires), mitigating-provenance-role-collapse-typed-
  memory-2026 (H2;H3;H5, component_overlap=4, architecture_overlap=2, full_text, `critical_collision:
  yes`, second review: confirmed), and prov-agent-2025 (H2;H3;H9, component_overlap=4,
  architecture_overlap=3, full_text, `critical_collision: yes`, second review: disputed — the row's
  own `transition_model` cell is NOT_APPLICABLE and states H2's bar is not met; the reviewer flagged
  this as a self-contradiction, and it is not counted as H2 evidence here — see below). 16 rows
  challenge H2 in total.
evidence:
  - >
    graph-native-cognitive-memory (Kumiho), Sec.7 (per Abstract/Sec.1 summary): a formal
    correspondence proof between the AGM belief-revision postulates (Alchourron, Gardenfors,
    Makinson 1985) and a property-graph memory system's operational semantics — "every agent
    belief has a URI, a revision history, provenance edges to source evidence, and an immutable
    audit trail" — commercially deployed (kumiho.io / github.com/KumihoIO).
  - >
    jansen-bosch, Sec.4.5, p.86: "a software archictecture = dd1 + dd2 + ... + ddn" — architecture
    as an accumulated, non-overwritten set of decision objects, 2005.
  - >
    zimmermann-et-al-managing-architectural-decision-models-2009, p.16: a formally typed
    outcome-status lifecycle (open/implied/resolved) governed by 8 integrity constraints and
    production rules, extending Jansen & Bosch directly (p.5: "Our metamodel extends that from
    [1] and [5]").
  - >
    evidence-graphs-fair-computation-defeasible-reasoning-2021 (EVI): an OWL-formalized,
    PROV-O-extended ontology making support/challenge relations first-class, transitively
    propagating graph edges, deployed at 17,996-node scale on real data.
  - >
    zep-graphiti-temporal-kg-agent-memory-2025, Sec.2.2.1-2.2.3: a four-timestamp bi-temporal
    edge model with LLM-mediated contradiction detection, in a commercial, production-deployed
    system.
  - >
    Also present at component_overlap=3: w3c-prov-o-2013 (Entity/Activity/Agent plus
    generation/derivation as the raw vocabulary substrate); snodgrass-developing-time-oriented-
    database-applications-sql-1999, p.249-250 (the append-only transaction-time table, formalized
    1999); agm-partial-meet-contraction-revision-1985 (the axiomatic ancestor cited directly by
    both graph-native-cognitive-memory and decision-oriented-programming-aporia-2026).
  - >
    provenance-enhanced-statements-dec-2026 (full HTML text, arxiv.org/html/2606.15246v1,
    Sec.3.2.2): one explicit, formally defined transition operator (`settle`, `r' = r ∪ {(φ,T)}`)
    moving a statement from conjectural to factual status while retaining the superseded state — a
    real, if narrow, typed, provenance-linked knowledge-state transition. Second review found the
    paper itself attributes origination of this operator to a companion preprint (ref [45]) rather
    than to this paper, and re-derived the component score from 4 to 3 partly on that basis ("transition
    model has exactly one named operator... explicitly inherited... rather than originated here").
  - >
    mitigating-provenance-role-collapse-typed-memory-2026 (full 15-page PDF, arxiv.org/pdf/2605.25869,
    Sec.3.2-3.3): confirmed on independent review at component_overlap=4. Its contradiction handling
    is real and benchmarked (BEAM-100K CR category, 32.30 vs. next-best 20.60) but is, per the row's
    own field, "retrieval-time role assignment, not a persisted transition object" — a typed outcome
    computed at query time over an implicit history, not an append-only transition graph of the kind
    H2 proposes.
  - >
    prov-agent-2025 (full 7-page PDF, arxiv.org/pdf/2508.02866v3, Sec.III): listed by the row as
    challenging H2 alongside H3 and H9, but the row's own `transition_model` cell is NOT_APPLICABLE
    and states directly that the Agent_Decision chain "is a PROV-derivation chain, not a typed
    transition object with its own provenance record." Independent review confirmed this as a
    self-contradiction — H2's own falsification bar is explicitly not met by the row's own cells —
    and recorded it as disputed rather than corrected, per the binding rule against altering
    `hypotheses_challenged`. Not counted as H2 evidence here for that reason; the same source's real
    contribution is to H9, discussed in that block below.
assessment: >
  If any hypothesis in this review is dead on arrival, it is this one. The idea that reasoning/
  decision history should be preserved as explicit, typed, non-overwritten transitions distinct
  from ordinary semantic edges is one of the most densely prior-arted claims found across the
  whole campaign: it traces through classical belief-revision logic (AGM, 1985), classical
  temporal-database theory (Snodgrass, 1999), the architecture-decision-record tradition (Jansen
  & Bosch 2005, formally extended by Zimmermann et al. 2009), a W3C provenance standard (PROV-O,
  2013), and multiple production 2025-2026 agent-memory systems (Zep/Graphiti, Kumiho) — one of
  which (Kumiho) has a published, if partially unreproduced, formal correspondence proof to the
  AGM postulates specifically. Sixteen of the matrix's 67 rows challenge H2; two reach the
  matrix's ceiling component-overlap score of 5 (disputed on review to 4 and 3 respectively — see
  `strongest_challenger` above; the flags survive regardless). This is not a thin or contested
  finding, and `phase-lit-09`'s three additions do not change that: provenance-enhanced-statements'
  one named transition is real but is, by the paper's own text, inherited from a companion preprint
  rather than an original contribution — a further data point for prior art, not against it;
  mitigating-provenance-role-collapse's contradiction-resolution mechanism is confirmed and
  benchmarked but operates at retrieval time over an implicit history, not as a persisted,
  provenance-carrying transition object, so it corroborates the general finding without adding a
  materially stronger instance; and prov-agent-2025's H2 tag is a disputed self-contradiction — the
  row's own `transition_model` cell states plainly that no typed transition object exists in the
  system — and is excluded from this hypothesis's evidence rather than credited.
  Qualification: none of these sources combine transition-preservation with D-System's full
  proposed epistemic+ontological+lifecycle state model (H1) simultaneously, and Kumiho's own
  formal correspondence is explicitly scoped to "a deliberately simple propositional logic over
  ground triples," with its strongest reported benchmark carrying a self-disclosed independent-
  reproduction gap. But H2 as literally worded is about the transition-preservation mechanism
  itself, not that combination, and on that literal claim the field's coverage is thorough and
  multi-lineage, not a single narrow precedent. Status is unchanged from the prior reconciliation:
  the density of independent corroboration only grows this phase (13 -> 16 rows), and none of the
  three additions supplies a stronger instance than what was already established.
status: LIKELY_ALREADY_KNOWN
```

---

## H3 — Provenance as conflict-resolution input

```yaml
hypothesis: >
  Transition provenance includes actor identity, domain authority, evidence, method, lineage,
  and delegation and influences conflict resolution. (Review-instructions text; no material
  frozen-register divergence flagged for H3.)
strongest_challenger: >
  log-is-the-agent-event-sourced-reactive-graphs-2026 (component_overlap=4, architecture_overlap=4,
  full_text) and omniscientist-coevolving-ecosystem-human-ai-scientists-2026 (component_overlap=4,
  architecture_overlap=4, full_text) remain the matrix's highest-scoring H3 rows. `phase-lit-09`'s
  strongest addition by mechanism fit, not raw score, is grading-narrators-isnad-rijal-claim-
  provenance-2026 (component_overlap=5, architecture_overlap=3, full_text, `critical_collision: yes`,
  second review: disputed — component re-derived 5->4, flag unaffected, hypotheses_challenged
  H1;H3;H4 confirmed as appropriately hedged, not an overstatement): its domain-conditioned
  narrator-authority registry actually drives an automated serve/review/quarantine decision, the
  closest single system found in this campaign to computing an outcome from graded authority rather
  than merely recording it. 16 rows challenge H3 in total, including two added by `phase-lit-08`'s
  H4-targeted search that this file had not previously discussed:
  extending-nanopublications-knowledge-provenance (component_overlap=3, architecture_overlap=2,
  full_text) and provenance-based-interpretation-multi-agent-information-analysis-2020 (DIVE,
  component_overlap=4, architecture_overlap=3, full_text, `critical_collision: yes`, second
  review: confirmed), and five added by `phase-lit-09`: grading-narrators-isnad (above),
  provenance-enhanced-statements-dec-2026 (H1;H2;H3, component_overlap=4, architecture_overlap=3,
  full_text, `critical_collision: yes`, second review: disputed — component re-derived 4->3, no
  trigger fires), inter-agent-trust-models-comparative-study-2025 (H3 only, component_overlap=3,
  architecture_overlap=2, no collision), mitigating-provenance-role-collapse-typed-memory-2026
  (H2;H3;H5, component_overlap=4, architecture_overlap=2, full_text, `critical_collision: yes`,
  second review: confirmed), and prov-agent-2025 (H2;H3;H9, component_overlap=4,
  architecture_overlap=3, full_text, `critical_collision: yes`, second review: disputed — component
  re-derived 4->3, no trigger fires, and the row's own cells rule out H3; discussed below and not
  counted toward H3).
evidence:
  - >
    log-is-the-agent, Sec.6/Sec.8: a total, worked-example-verified provenance/lineage chain
    from goal to individual model call, using D-System's own vocabulary (claim, evidence,
    question) linked by typed relations (supports, addresses, derived_from) — but its own
    strongest_difference field records that authority-weighting and evidence-as-arbitration-input
    are absent: "actor+lineage present, authority+evidence-as-provenance-input absent."
  - >
    omniscientist, Sec.4.1.3: an immutable ContributionLedger recording actor identity, action
    type and timestamp per contribution — but disagreement is resolved by an explicit
    REQUEST_DECISION escalation to human fiat, not by computing evidential weight from the
    ledger (Sec.4.4).
  - >
    evidence-graphs-fair-computation-defeasible-reasoning-2021 (EVI): typed support/challenge
    edges transitively propagate through a reasoned graph — but the paper states directly:
    "Challenges do not invalidate, they present an opposing view. They ultimately require human
    judgment as to their validity and strength." Deliberately not automated.
  - >
    tgms-agent-native-bitemporal-graph-2026, Sec.8: actor/authority provenance fields are
    reserved in the schema but explicitly unused; write-back is "disabled pending provenance and
    authorization policies."
  - >
    agm-partial-meet-contraction-revision-1985: a genuine, automated, axiomatically-constrained
    conflict-resolution rule (epistemic entrenchment) exists — but it is source-agnostic; AGM's
    only recorded property of a belief is a scalar entrenchment rank, with no actor, evidence,
    method, or delegation dimension at all.
  - >
    extending-nanopublications-knowledge-provenance (full 15-page paper, retrieved via curl): a
    real, automated conflict-resolution rule deployed at scale (197,511 published facts, CoreKB) —
    a two-stage sufficiency/consistency threshold test (Sec.4) classifying each Proposition as
    ReliableFact or UnreliableFact (InsufficientEvidence/ContrastingEvidence) from its
    supporting-vs-conflicting evidence counts, with no human arbitration in the deployed pipeline.
    But on full-text read the ontology's own actor-trust classes (InfoCreatorTrust,
    PropositionTrust) play no role in the threshold test itself: the classification runs entirely
    on evidence-probability counts, the same source-agnostic shape AGM's entrenchment rule already
    exhibits, not an authority- or delegation-weighted arbitration. A second, independent instance
    of "automated resolution exists, but not wired to the rich provenance dimensions," not a
    counter-example to it.
  - >
    provenance-based-interpretation-multi-agent-information-analysis-2020 (DIVE; full 6-page
    paper, retrieved via curl): a real, implemented, demonstrated conflict/sensitivity mechanism —
    TMS-environment refutation (Sec.3.2) that propagates disabling a source or operation class
    through every dependent element, letting an operator counter-factually inspect the analysis
    without a given contribution. But this is explicitly manual and user-triggered, not automated
    arbitration; DIVE's three confidence-propagation policies (minimum/maximum/average) compute
    over evidence diversity without weighting by actor identity or authority.
  - >
    grading-narrators-isnad-rijal-claim-provenance-2026 (full HTML text, arxiv.org/html/2607.24117v1,
    Sec.4.1-4.4): two decoupled, automated mechanisms — weakest-link bounding (a chain's grade is the
    minimum grade over its narrators, itself a function of a domain-conditioned actor-authority
    registry) and matn contradiction detection — combine via an explicit serve/review/quarantine
    decision matrix. This is the closest match found in the whole campaign to authority actually
    driving an automated outcome rather than sitting beside one. But the paper's own
    `human_agent_scope` field records that final content adjudication on a flagged contradiction is
    human by explicit design ("LLM auto-resolution deliberately disabled 'due to known
    unreliability'") — the automated step is triage (serve/review/quarantine), not the resolution of
    which claim is correct. Second review confirmed the H1;H3;H4 tag as appropriately hedged, not an
    overstatement, and re-derived the component score from 5 to 4 (flag unaffected).
  - >
    provenance-enhanced-statements-dec-2026 (full HTML text, arxiv.org/html/2606.15246v1, Sec.4):
    provenance gates a statement's epistemic-modality type (doxastic/epistemic/conjectural) but the
    paper states directly it provides "no explicit trust score or source-reliability ranking between
    worlds" — categorical typing substitutes for graded authority, the same shape as extending-
    nanopublications' evidence-count-only classification already discussed above, just gating type
    rather than a reliability tier. Second review confirmed no trigger fires and that H3 is, in the
    row's own words, "only partially engaged."
  - >
    inter-agent-trust-models-comparative-study-2025 (arXiv HTML render, arxiv.org/html/2511.03434):
    a taxonomy of six agent-trust mechanisms (Brief/Claim/Proof/Stake/Reputation/Constraint)
    explicitly acknowledging that Reputation is vulnerable to "Sybil attacks, ballot stuffing,
    collusion... mitigated only partially." But every mechanism gates whether to trust an *acting*
    agent for its *next action*, not whether to credit a *knowledge claim* — a genuinely different
    mechanism family (agent-to-agent authorization, not claim-provenance arbitration) under a
    partially overlapping vocabulary (trust, evidence, attestation, lineage), confirmed by the row's
    own actor-model field.
  - >
    mitigating-provenance-role-collapse-typed-memory-2026 (full 15-page PDF, arxiv.org/pdf/2605.25869,
    Sec.3.2/4.7): a real, benchmarked, automated contradiction-resolution mechanism (BEAM-100K CR
    category, 32.30 vs. next-best 20.60) — but resolution is via recency plus evidential grounding,
    explicitly not authority/trust-scoring arbitration, and the row's own `actor_model` field is
    NOT_APPLICABLE (no distinct actor identity is modeled at all). A second, independently confirmed
    instance of "automated resolution exists, but not wired to actor-authority," alongside
    extending-nanopublications.
  - >
    prov-agent-2025 (full 7-page PDF, arxiv.org/pdf/2508.02866v3): listed by the row as an H3
    challenger, but its own `conflict_trust_mechanism` cell is NOT_APPLICABLE and states directly
    "no arbitration, trust scoring, or authority-weighted conflict resolution" exists — the provenance
    graph supports post-hoc human traceability, not automated conflict resolution. Independent review
    confirmed this as a self-contradiction (the row's own cells rule out H3) and recorded it as
    disputed rather than corrected. Not counted as H3 evidence here.
assessment: >
  The two halves of H3 are individually well established but no found source combines them.
  Rich, typed, multi-actor provenance representation is thoroughly known (PROV-O, EVI, log-is-
  the-agent, omniscientist, burns-groth, extending-nanopublications, DIVE all score
  component_overlap=3-4 on exactly this). Automated conflict resolution driven by a
  belief-revision-style rule is also known: AGM's axiomatically-constrained entrenchment rule
  (1985), and, deployed at real scale, extending-nanopublications' sufficiency/consistency
  threshold test (197,511 facts) — but both are source-agnostic, resolving disagreement from
  evidence quantity alone, never drawing on the actor-identity/domain-authority/delegation
  dimensions that make provenance "rich" in the first place. Given both ingredients are
  independently mature, wiring rich, multi-actor provenance into an authority-weighted automated
  arbitration rule is an unglamorous combination of two already-solved pieces, not a research
  gap — exactly the "known component, new integration" pattern the campaign's anti-novelty case
  is built to detect.
  Qualification: it is notable, and worth recording rather than explaining away, that of the
  provenance systems in this matrix rich enough to plausibly support authority-weighted
  arbitration, most explicitly decline to automate the step at all. EVI's authors state directly
  that challenge resolution "ultimately require[s] human judgment"; TGMS explicitly disables
  provenance-based write-back "pending policies"; DIVE's refutation mechanism is manual and
  user-triggered. The one exception, extending-nanopublications, does automate arbitration — but
  only over evidence-sufficiency counts, never over the actor-trust relationships its own
  ontology defines. That three separate, careful, 2020-2026 engineering teams built rich
  provenance machinery and either declined to automate arbitration on top of it or automated it
  without drawing on that same rich machinery is some evidence that authority-weighted automated
  arbitration carries a correctness or liability risk its builders did not want to accept — not
  proof that it is hard, but a reason the absence may not be mere neglect. This tempers confidence
  without changing the verdict: the components needed are known: no source demonstrates a
  materially equivalent working arbitration mechanism that draws on the rich provenance dimensions,
  so this stops short of LIKELY_ALREADY_KNOWN, but the ingredients are too mature to call the
  combination distinct.
  `phase-lit-09` sharpens this qualification rather than reversing it. grading-narrators-isnad is
  the closest thing found in the whole campaign to a fifth, contrary data point: its serve/review/
  quarantine decision is genuinely automated and genuinely a function of the narrator-authority
  registry — the first source in this review where authority actually computes an outcome rather
  than merely being recorded beside one. But by the paper's own explicit design, that automated step
  is triage, not adjudication: when the matn check flags a contradiction, a human muhaddith decides,
  with LLM auto-resolution deliberately disabled. That is a fourth instance of the same pattern, not
  a break from it — one step closer to the claimed mechanism than EVI, TGMS, or DIVE, but still
  stopping short of it at the same point they do: the content decision itself. mitigating-provenance-
  role-collapse adds a second confirmed instance of "automated resolution exists, but not wired to
  actor-authority" (recency-plus-grounding, no actor model at all), reinforcing rather than
  displacing extending-nanopublications as the sole automated-but-source-agnostic exception.
  provenance-enhanced-statements substitutes categorical typing for a trust score, another instance
  of "provenance gates something, but not gradedly, and not by authority." inter-agent-trust-models
  is the clearest false friend among the five: it names the correlated-agreement problem directly,
  in language that echoes H4, but its trust mechanisms gate agent *authorization* for a next action,
  not knowledge-claim arbitration — a different mechanism family under partially shared vocabulary,
  exactly the caution this campaign's own thesis-discipline rule exists to enforce. prov-agent-2025's
  H3 tag does not survive scrutiny at all: the row's own `conflict_trust_mechanism` cell rules it out,
  and it is excluded from this hypothesis's evidence rather than credited, per the disputed-not-
  applied resolution recorded in `05`. None of these five additions, individually or together, closes
  the specific gap this block has identified twice now: an automated rule that resolves a disagreement
  by weighing the actors' authority, not merely alongside recording it. Status is unchanged from the
  prior reconciliation: sixteen rows now challenge H3 (up from eleven), and the closest addition
  narrows the gap without closing it.
status: KNOWN_COMPONENT_NEW_INTEGRATION
```

---

## H4 — Independence-aware convergence

```yaml
hypothesis: >
  Independent reasoning/evidence paths arriving at equivalent states strengthen epistemic
  weight while derivative agreement is discounted. (Review-instructions text.) The frozen
  register makes the topological character explicit: "graph-topological epistemic signal ...
  discounted based on shared lineage" — a sharper, more specific claim than the
  review-instructions' general wording. Both phrasings are addressed together below because the
  evidence now closes the gap between them: sources found since the prior reconciliation satisfy
  the frozen register's sharper topological reading directly, not merely the general one.
strongest_challenger: >
  grading-narrators-isnad-rijal-claim-provenance-2026 (ISNAD; component_overlap=4,
  architecture_overlap=3, full_text, `critical_collision: yes`, second review 2026-09-19:
  disputed on component score only — re-derived 5->4, flag and hypotheses_challenged
  unaffected) is the strongest challenger found against either phrasing, because it is the only
  source in this file's H4 evidence that combines all three elements the frozen register's
  falsification clause names in one place: a derivation-chain topology (the isnad, a directed
  narrator-to-narrator transmission chain), an explicit computed discount for shared lineage
  (Sec.4.3's muta ba'at cross-chain corroboration check, which withholds a tier upgrade when two
  converging chains share a narrator identity, an upstream source, or a model family), and an
  explicitly mixed human-agent narrator scope (`narrator_type` spans source|scraper|model|human,
  with contradictions arbitrated by a human by default). This row was added by this campaign's own
  `LIT-09-S034/S035` and was not evaluated in the prior reconciliation (`LIT-08 X5`, 2026-09-14),
  which read only bara-2026, barakat-2017, extending-nanopublications, DIVE-2020,
  Mayo-Wilson-2014, and Goldman-2001 — none of which combine all three elements in one source.
  not-all-agreement-counts-as-corroboration-2026 (PACT; component_overlap=4,
  architecture_overlap=2, full_text, `critical_collision: yes`, second review 2026-09-19:
  disputed on two factual corrections applied, scores confirmed unchanged) is the second new
  addition: a formally proved (Proposition 1, an identifiability result), empirically validated
  discount for repeated/derivative agreement, computed over a supplied provenance partition — but
  scoped to machine sensor/VLM sources only, with zero evidence-contributing human agents, which
  the second review confirmed directly by an exhaustive grep of the primary text. Both new rows
  were found by this phase's own collision searches (`LIT-09-S034` through `LIT-09-S053` and
  onward), after the prior reconciliation's search had already run and closed.
evidence:
  - >
    grading-narrators-isnad-rijal-claim-provenance-2026 (arxiv:2607.24117, full HTML text read):
    Sec.4.1 defines the isnad as "the ordered, gap-free sequence of narrators from origin to the
    point of serving"; Sec.4.3's muta ba'at mechanism upgrades a claim's tier when it "reaches the
    system via disjoint narrator sets and independent sources," explicitly checking for and
    discounting correlation from a shared model family, upstream source, or narrator identity
    before granting the upgrade — an operational, chain-topology-based instance of exactly H4's
    claim. The second review's one contested point does not touch this: it re-derives
    component_overlap from 5 to 4 because the paper's own Sec.2.3 concedes "subjective logic
    supplies chain-discounting arithmetic but no operational registry lifecycle" — i.e. the
    discount math is imported from josang-subjective-logic-book-2016, and ISNAD's own contribution
    is the narrator-registry lifecycle built around it. That concession bears on whether ISNAD
    itself invented the mechanism; it does not bear on whether the mechanism, as literature
    predating this campaign, already exists and already covers a mixed human-agent narrator scope
    — which the row's own confirmed fields establish that it does.
  - >
    not-all-agreement-counts-as-corroboration-2026 (PACT; arxiv:2609.01662, full HTML text read):
    Proposition 1 proves source-local numerical attributes alone cannot distinguish a repeated
    derivation from a separately countable acquisition; the coordinatewise meet within a supplied
    provenance partition is then the unique rule satisfying singleton fidelity and
    insertion-non-amplification (Propositions 2-3), empirically reducing ncsAURC by 0.0557 and
    leaving 720 typed responses unchanged under 1x-8x within-camera duplication. A graph/partition-
    topology-based discount mechanism, formally guaranteed rather than merely proposed. Sec.2.2's
    own "substantive precedents" citation (Denoeux 2008, Josang et al. 2010) situates this as a
    further derivative refinement of a sensor-fusion/belief-function lineage running back to Julier
    & Uhlmann's 1997 covariance intersection, sixteen to eighteen years earlier — confirmed by the
    second review's correction to the row's `derivative_ancestor` field. Scope is fully
    machine-source (camera/VLM outputs); humans appear only as handover recipients, confirmed by
    the second review's exhaustive text grep — so this row alone does not reach H4's mixed-agent
    requirement, but it independently corroborates that the discount mechanism itself is thoroughly
    established, arriving at essentially the same shape as bara-2026's kappa_m from an unrelated
    sensor-fusion lineage rather than from AI-Sybil-resistance framing.
  - >
    (Unchanged from the prior reconciliation.) epistemic-sybil-resistance-bara-2026
    (component_overlap=4, architecture_overlap=2, full_text): Sec.6's provenance DAG
    G=(V,E_G) with the closed-form discount kappa_m = 1/(1+rho(m-1)) (Sec.5.2, Corollary 2) for
    reports sharing an evidentiary root remains the most rigorous single graph-topological
    formalization found. Still AI-agent-only in scope (human_agent_scope field), with practical
    provenance authentication left as an open problem (Sec.9). Presented as this paper's own
    original contribution, not attributed to a prior mechanism — a second, apparently independent
    origin of the same discount shape alongside the sensor-fusion lineage below.
  - >
    (Unchanged.) barakat-corroboration-provenance-patterns-tapp2017 (component_overlap=4,
    architecture_overlap=3, full_text, `critical_collision: yes`, second review: confirmed): a
    PROV-graph corroboration methodology explicitly scoped to "computational or human" sources
    (Abstract), computing a graph-derived reliability score (Eq.1) — but Sec.5 states plainly the
    built methodology "assumed independence among witnesses," and the paper's only treatment of
    shared-dependency discounting is Eq.8, a sketched, never-implemented rewrite citing an external
    analogy (Townend et al. 2005's channel weighting, itself traced back to Eckhardt & Lee 1985's
    N-version-programming reliability theory), with no worked example and no reappearance anywhere
    else in the paper. A third, independent lineage (distributed fault tolerance) converging on the
    same discount-for-shared-dependency idea, not yet delivered as a built mechanism here.
  - >
    (Unchanged.) provenance-based-interpretation-multi-agent-information-analysis-2020 (DIVE,
    component_overlap=4, architecture_overlap=3, full_text, `critical_collision: yes`, second
    review: confirmed): a real, implemented, live system with a demonstrated mixed human-machine
    appraisal scope (Sec.2.1's Appraisal class is "a human or machine agent's judgment," with a
    named human user co-participating with machine agents in one worked provenance graph). Its
    three implemented confidence-propagation policies (minimum/maximum/average) are not
    topology-aware and do not discount for shared lineage; the specific H4 mechanism is named only
    as future work (Sec.3.3), citing Kuter & Golbeck 2007, confirmed by this file's own prior
    backward chain (LIT-08-S054) not to supply it either.
  - >
    (Unchanged.) goldman-experts-which-ones-should-you-trust-2001 (component_overlap=4,
    architecture_overlap=1, full_text, `critical_collision: yes`, second review: confirmed with one
    locator correction): a fourth, independent lineage (Bayesian testimony epistemology): a
    closed-form proof (Sec.4, Eqs.1-6') that a "blind follower" or "non-discriminating reflector"
    of another witness adds zero extra evidential weight, materially the same discount shape as
    bara-2026's kappa_m, twenty-five years earlier, at wider (agent-model-agnostic) scope but
    characterized narratively rather than via an explicit graph structure — no traversal, no
    worked graph example. Extended by reliability-testimonial-norms-scientific-communities-synthese
    (Mayo-Wilson 2014, component_overlap=3, architecture_overlap=2, preprint_version) with
    network-topology-sensitive convergence results, though that paper's own formal machinery
    evaluates whole belief-update strategies rather than a per-claim discount function.
  - >
    (Unchanged.) extending-nanopublications-knowledge-provenance (component_overlap=3,
    architecture_overlap=2, full_text): a real, deployed (197K+ facts) provenance/trust ontology
    searched specifically for an independence/shared-lineage discount and confirmed to have none —
    reliability rests on naive sufficiency/consistency counting over supporting-vs-conflicting
    sentences, with no treatment of shared dependent origin.
  - >
    (Unchanged.) uspto-10445654-feedforward-evidence-graph-confidence-patent (component_overlap=3,
    architecture_overlap=2, full_text): the patent's noisy-OR combining function is gated on a
    named independence assumption ("the noisy-OR combination can be utilized when the sources of
    evidence are independent," col.6) — a real but binary independence gate on which formula to
    apply, not a graded discount for correlated/derivative agreement. Confirms "evidence graph" is
    independently coined vocabulary (this campaign's phase-lit-01 finding) rather than a shared
    mechanism with D-System's own use of the term.
  - >
    (Unchanged.) Negative result, dong-berti-equille-srivastava-truth-discovery-copying-detection-2009:
    the closest named prior-art family for H4 by mechanism shape (HMM-detected copier/independent
    classification feeding a Bayesian truth-decision model), deep-read specifically for this
    hypothesis and recorded as not challenging it — correlation-based copier detection over a
    fixed, closed set of structured web sources, not a derivation-graph topology.
assessment: >
  The best case that D-System is not distinct here, stated before any counter-argument: H4's
  claim, read at the narrow scope the frozen register itself states — a graph-topological discount
  of corroboration that shares lineage, applied to knowledge from a mix of human and agent sources
  — is not a new idea. It is a specific instance of the general, decades-old statistical and
  epistemological principle that non-independent evidence must not be double-counted, and that
  principle has now been found independently re-derived and re-applied, in closed or operational
  form, across at least four unconnected lineages: Bayesian testimony epistemology (Goldman 2001,
  extended by Mayo-Wilson 2014), distributed multi-version fault tolerance (Eckhardt & Lee 1985 ->
  Townend et al. 2005, cited into barakat-2017), sensor fusion and belief-function combination
  (Julier & Uhlmann 1997, Denoeux 2008, Josang 2010/2016, applied into PACT-2026 and, for its
  discounting arithmetic, into ISNAD-2026), and at least one apparently self-originated 2026
  AI-agent formalization (bara-2026's kappa_m). Per this campaign's own methodology (`CLAUDE.md`
  Sec.12, "this same rule applies when evaluating D-System's convergence hypothesis"), these are
  not independent confirmations of novelty but four traceable ancestor lineages, each already
  wired to a graph or chain-topology representation by at least one 2026 paper (bara-2026's
  provenance DAG, ISNAD-2026's isnad chains, PACT-2026's provenance partition) — meaning the "new
  integration" step the prior reconciliation treated as the open gap (marrying a known discount
  formula to a known graph representation) has already been done, more than once, in settings
  structurally analogous to D-System's own knowledge-state graph: reports, claims, or observations
  reaching a system via distinct derivation paths that must be checked for shared ancestry before
  being counted as independent corroboration. ISNAD-2026 closes the remaining gap by name: its
  narrator_type field spans source, scraper, model, and human, and its muta ba'at check discounts
  cross-chain agreement for shared narrator identity, upstream source, or model family — confirmed
  by an independent second review on 2026-09-19 as an accurately described, non-overstated
  mechanism (the review's only correction lowers the component score from 5 to 4, on the separate
  point that ISNAD's own discount arithmetic is imported from subjective logic rather than
  original to the paper, not on whether the described mechanism exists or covers a mixed
  human-agent scope). No single row reaches a confirmed component_overlap of 5 ("materially
  equivalent mechanism") — the honest caveat against reading this as flatly settled — but this is
  no longer, as the prior reconciliation found, "one narrow 2026 preprint and one unimplemented
  citation-sketch." It is three independent 2026 graph/topology-based instantiations of the same
  discount idea (two of them confirmed by independent review not to overstate their own claims),
  layered on top of a forty-year cross-domain derivation history, with the specific combination of
  graph topology, computed shared-lineage discount, and mixed human-agent narrator scope that the
  frozen register's falsification clause names already present, together, in one deep-read primary
  source. This is not an unformalized restatement of a single narrow paper; it is an established,
  independently-recurring pattern that D-System's own knowledge-state graph would be one further
  domain application of.
  This changes the verdict from the prior reconciliation (`LIT-08 X5`, 2026-09-14), which had not
  yet read grading-narrators-isnad-rijal-claim-provenance-2026 or
  not-all-agreement-counts-as-corroboration-2026 — both added to `04_evidence_matrix.csv` by this
  phase's own collision searches (`LIT-09-S034/S035`, `LIT-09-S052/S053`) after the prior
  reconciliation had already run and closed. That prior reconciliation split H4's status by
  phrasing — `KNOWN_COMPONENT_NEW_INTEGRATION` for the review-instructions' general wording,
  `INSUFFICIENT_EVIDENCE` for the frozen register's sharper graph-topological wording — reasoning
  that the graph-topological family it had found (bara-2026 alone, plus barakat's unimplemented
  Eq.8 sketch) was "one narrow 2026 preprint... not an established tradition." With ISNAD-2026 and
  PACT-2026 added, that specific reasoning no longer holds: the graph-topological family is now
  three independent 2026 instantiations resting on a forty-year cross-domain ancestor base, and one
  of the three (ISNAD-2026) is confirmed, not merely claimed, to cover a mixed human-agent scope.
  The gap between the two phrasings that motivated the prior split verdict is accordingly closed;
  both phrasings are assessed here as the same status.
  Checked against this file's two-condition rule (search effort and field maturity): condition 1 is
  satisfied by the prior reconciliation's own 32-query dedicated collision search plus this
  phase's further collision searches that produced the two new rows above (`00_search_ledger.csv`,
  `LIT-09-S034` through `LIT-09-S053` and surrounding rows). Condition 2, which failed for the
  frozen-register phrasing in the prior reconciliation on field-maturity grounds, is now satisfied
  for both phrasings: three independent 2026 graph-topology-based instantiations plus a forty-year
  ancestor lineage across four unconnected research traditions is a mature, established field
  finding, not a thin one — the same standard this file already applies elsewhere (e.g. H3, H9) to
  call a field "thoroughly known." No row combines full mixed-agent scope with a confirmed
  materially-equivalent (component_overlap=5) score, so `LIKELY_ALREADY_KNOWN` is not stretched to
  claim total, unqualified prior anticipation of D-System's own knowledge-state-graph
  instantiation — but the underlying mechanism H4 actually names, independent of which specific
  knowledge domain it is wired into, is established well past the threshold this file uses
  elsewhere to move off `INSUFFICIENT_EVIDENCE` or a split verdict.
status: LIKELY_ALREADY_KNOWN
```

---

## H5 — Topology-aware context transfer

```yaml
hypothesis: >
  Context selection includes current state, reasoning lineage, supporting evidence, dissent,
  authority, convergence, and unresolved uncertainty. (Review-instructions text; no material
  frozen-register divergence flagged for H5.)
strongest_challenger: >
  solozobov-verify-gated-completion-admission-control-2026 (component_overlap=4,
  architecture_overlap=4, full_text) and zep-graphiti-temporal-kg-agent-memory-2025
  (component_overlap=4, architecture_overlap=3, full_text). `04_evidence_matrix.csv` lists 9 rows
  as challenging H5, including log-is-the-agent-event-sourced-reactive-graphs-2026 (the first
  assessment's other strongest_challenger) — but independent review (`05_critical_collisions.md`,
  source 7) found log-is-the-agent's own Sec.8 explicitly positions the paper as *rejecting* the
  memory/retrieval category rather than instantiating it: a shared word ("topology") over a
  different mechanism (a replayable event log, not context selection). It is dropped as a
  challenger here; solozobov and zep-graphiti carry the hypothesis instead. One of the 9 rows,
  provenance-based-interpretation-multi-agent-information-analysis-2020 (DIVE), is also tagged H5
  but not separately discussed below: its three confidence-propagation policies (minimum/maximum/
  average, per H4's evidence above) select over evidence diversity, not the dissent/authority/
  convergence dimensions H5 lists, so it does not change the qualification's conclusion.
  `phase-lit-09` adds one more H5-tagged row, confirmed on independent second review:
  mitigating-provenance-role-collapse-typed-memory-2026 (component_overlap=4, architecture_overlap=2,
  full_text, `critical_collision: yes`, second review: confirmed). It does not unseat solozobov or
  zep-graphiti and does not change the qualification below.
evidence:
  - >
    solozobov, Sec.6, Table 9, Sec.6.1-6.2: an explicit context compiler distinguishing canonical/
    archive-only/prompt-injectable memory tiers and shaping role-specific context envelopes —
    "Canonical memory includes common-ground snapshots, packets, after-action reviews, trust
    state, and governance labels ... Prompt-injectable memory includes active governance hints,
    route corrections, verify hints, and procedure packs that have already been summarized and
    filtered."
  - >
    zep-graphiti-temporal-kg-agent-memory-2025, Sec.3-3.2: a formally specified three-stage
    Search-Rerank-Constructor retrieval pipeline including breadth-first graph traversal to
    incorporate "recently mentioned entities and relationships" — a direct match on
    topology-plus-recency context assembly, in a commercial, deployed system.
  - >
    em-llm-human-inspired-episodic-memory-infinite-context-2024, Sec.3.1: episodic segmentation
    plus combined similarity/temporal-contiguity retrieval, peer-reviewed at ICLR 2025,
    demonstrated at 10M-token scale, publicly released.
  - >
    lineagerag-2026, Table 5: a controlled ablation showing that scrambling correct provenance
    (while preserving its volume) is measurably worse than having no provenance at all
    (-8.11 vs -2.95 R@5 points) — quantified evidence that provenance-correctness, not just
    provenance-presence, materially changes what a retrieval system trusts.
  - >
    mitigating-provenance-role-collapse-typed-memory-2026 (full 15-page PDF, arxiv.org/pdf/2605.25869,
    Sec.3.2): every fact exposed to the answer model carries a "provenance closure" back to its raw
    grounding evidence spans — a real, confirmed, benchmarked provenance-aware context-construction
    mechanism. But the row's own fields record no actor/authority dimension (`actor_model`:
    NOT_APPLICABLE) and no independence/convergence weighting (`convergence_independence_mechanism`:
    NOT_APPLICABLE) — evidential grounding and recency drive selection, not the dissent/authority/
    convergence dimensions H5 lists.
  - >
    None of these sources implement the full enumerated set: dissent, authority, and convergence
    as explicit, first-class selection dimensions are absent from every source read at this
    detail (recorded per-row in each strongest_difference field above).
assessment: >
  Retrieval that goes beyond plain semantic similarity — incorporating graph topology, temporal
  recency, reasoning lineage, and evidence provenance — is thoroughly established across
  2024-2026 agent-memory and agentic-runtime systems: Zep/Graphiti's traversal-plus-recency
  pipeline, EM-LLM's peer-reviewed episodic-segmentation retrieval, and solozobov's explicit
  memory-tier context compiler are all real, working instances of "select context using more
  than semantic similarity." If H5 were
  read as "context selection beyond naive similarity is uncommon," the evidence flatly falsifies
  that reading.
  Qualification: H5 as worded lists seven specific dimensions (state, lineage, evidence, dissent,
  authority, convergence, unresolved uncertainty), and no single source combines more than three
  or four of them. Dissent, authority, and convergence specifically as first-class retrieval
  inputs were not found in any source at this detail. The mechanism family (topology/lineage/
  recency-aware retrieval) is known; the specific seven-dimension enumeration D-System proposes
  is an untested combination, not a demonstrated one. mitigating-provenance-role-collapse adds a
  further confirmed instance of provenance-aware context construction (evidential grounding, not
  dissent/authority/convergence), reinforcing rather than changing this qualification. Status is
  unchanged from the prior reconciliation.
status: KNOWN_COMPONENT_NEW_INTEGRATION
```

---

## H6 — Integrated human-agent collective knowledge evolution

```yaml
hypothesis: >
  The full synthesis may be distinct even if primitives are known. (Review-instructions text;
  no material frozen-register divergence flagged for H6.)
strongest_challenger: >
  omniscientist-coevolving-ecosystem-human-ai-scientists-2026 (component_overlap=4,
  architecture_overlap=4, full_text) and dhar-vaidhyanathan-varma-agenticakm-2026-arxiv
  (component_overlap=4, architecture_overlap=3, preprint_version). 3 rows challenge H6.
evidence:
  - >
    omniscientist, Sec.4.4-4.5, Fig.14: Human-AI Collaboration Mode reaches 0.22 accuracy vs.
    0.10 Human Solo and 0.00 AI Solo on the same 10-question, 10-participant HLE case study —
    an empirically evaluated, quantified demonstration of integrated human-AI knowledge
    evolution outperforming either party alone.
  - >
    omniscientist, Sec.4.1.3: "the final scientific result ... can always be transparently
    traced back to all contributors" via the ContributionLedger, explicitly framed by the paper
    as moving "from Data Provenance to Contribution Provenance."
  - >
    dhar-agenticakm, Sec.6: a multi-agent Extraction/Retrieval/Generation/Validation pipeline
    generating and validating architecture decision records against source code and prior ADRs,
    with "architect in the loop" named as the paper's own future-work direction for deeper
    human-agent collaboration (not yet implemented).
  - >
    keim-kaplan-scattered-to-structured-akm-vision-2026, Sec.4 (component_overlap=2): a 2026
    ICSE-C vision paper naming, near-verbatim, one of D-System's own unresolved design questions
    ("whether to discard outdated information ... or maintain a temporal knowledge base with
    versioning and time-aware query capabilities") as an acknowledged open challenge — confirming
    the problem is recognized in contemporary literature, with neither paper having a working
    answer.
assessment: >
  A full, working, empirically-evaluated instance of "integrated human-agent collective
  knowledge evolution" already exists and is published: OmniScientist ships a Unified
  Participant Model with an immutable, actor-attributed contribution ledger, applied to real
  scientific production, and quantitatively shown to outperform either human-only or AI-only
  operation. Per this campaign's own derivative-ancestor analysis, its ledger mechanism is a
  scientific-credit specialization of already-known nanopublication/PROV-O provenance patterns,
  and its communication layer sits atop existing agent-to-agent protocols (MCP, A2A) rather than
  inventing new ones — by its own architecture, a recombination. If H6 asks whether the full
  synthesis can be distinct even when every primitive is known, OmniScientist is direct evidence
  that the synthesis itself is already achievable by assembling known primitives, in a domain
  structurally parallel to D-System's own Knowledge-Construction system.
  Qualification: OmniScientist's domain is scientific-paper production; it has no analog of
  D-System's Implementation & Experience system (requirements, plans, execution, artifacts,
  tests, deployment, runtime observation), its participant model is explicitly symmetric with no
  domain-authority weighting, and disagreement is escalated to human fiat rather than computed
  (the same H3 gap noted above). AgenticAKM's parallel synthesis argument is scoped to a single
  artifact type (ADRs) with no requirement or plan lifecycle, and its human-in-the-loop
  collaboration is stated future work, not an evaluated mechanism. No single system found
  substantially subsumes D-System's specific two-system, dual-domain pairing (knowledge
  construction and software development lifecycle under one collective-evolution framing) —
  but each half of that pairing has an independently demonstrated, evaluated analog in a
  different domain. That is a recombination of two already-demonstrated domain-specific
  integrations, which is what H6 anticipates when it concedes "even if primitives are known."
status: KNOWN_COMPONENT_NEW_INTEGRATION
```

---

## H7 — Development provenance

```yaml
hypothesis: >
  Software functionality can be represented as downstream result of an append-only lineage
  connecting ideas, evidence, decisions, requirements, specifications, plans, execution phases,
  artifacts, verification, and runtime outcomes. (Review-instructions text.) The frozen register
  phrases the same claim with materially equivalent scope for H7 itself; the scope record flags
  H7 only for its `prior_art_families_to_search` annotation (Requirements Traceability Matrix,
  bidirectional traceability, software traceability), which the search-domain matrix already
  subsumes — no separate phrasing-divergence note is required for H7's verdict.
strongest_challenger: >
  graph-native-cognitive-memory-belief-revision-semantics-2026 (component_overlap=5,
  architecture_overlap=4) and jansen-bosch-architecture-as-decisions-wicsa-2005
  (component_overlap=5, architecture_overlap=4) — the matrix's ceiling scores, tied. Both are
  disputed on independent second review (`05_critical_collisions.md`): Kumiho re-derived to 4/3,
  Jansen & Bosch to 3/2 (the latter's flag surviving only via idea-level anticipation, not
  mechanism-level equivalence — no tool existed at publication). Per the owner's ruling, disputes
  are recorded, not applied; the matrix's original 5/4 scores stand and are cited as-is.
  `phase-lit-09` adds the standards-body citation the prior assessment's "multiple standards bodies"
  language anticipated but had not yet evidenced: iso-42010-conceptual-model-working-group-page
  (H7;H9, component_overlap=3, architecture_overlap=2, full_text, no collision) and
  iso-42010-2022-architecture-description-standard (H7 only, component_overlap=3,
  architecture_overlap=2, secondary_coverage, no collision). 12 rows challenge H7 in total.
evidence:
  - >
    jansen-bosch, Sec.4.2-4.3, p.81-83: "A design decision may result in additional requirements
    to be satisfied by the architecture. These new requirements need to be addressed by
    additional design decisions" — decisions generating requirements, and "Clear, bilateral
    relationship between architecture and realization ... Changes in the architecture will have
    an effect on the realization of the system and vice versa," 2005.
  - >
    zimmermann-et-al-managing-architectural-decision-models-2009, Sec.3-4: a formal extension of
    Jansen & Bosch adding typed dependency relations, 8 integrity constraints, and per-outcome
    actor provenance (changedBy) — a direct, formal successor, not an independent invention
    ("Our metamodel extends that from [1] and [5]," p.5).
  - >
    us20250165226a1-ai-digital-thread-patent, Claims 1-2: an intent-to-code-generation loop with
    feedback-based model retraining, granted as US12461717B2, commercially operated by Istari
    Digital as the "Interconnected Digital Engineering Platform."
  - >
    model-based-digital-threads-sociotechnical-systems-2022, Fig.2.18: a typed, directional
    (trace/refine/realize) graph spanning Requirement -> Specification -> Implementation ->
    Test Case -> Field Performance, "to compare expected behavior (requirements) and actual
    system performance."
  - >
    decision-oriented-programming-aporia-2026, p.3: "Aporia elicits decisions with questions as
    an application of QOC" — a 2026 agentic-coding instantiation of the 1991 QOC design-rationale
    notation, with decisions formally connected to implementation via generated test suites.
  - >
    de-boer-architectural-knowledge-management-dissertation-2009 and
    procko-provtracer-erau-dissertation-2025 (both component_overlap=3): independently
    converging, 15+ years apart, on decision-rationale-as-first-class-object and automated
    provenance-graph capture, respectively, as solutions to the same "knowledge vaporization"
    problem.
  - >
    iso-42010-conceptual-model-working-group-page (full page, iso-architecture.org/42010/cm/,
    read in full): Architecture Rationale is defined as "the explanation, justification or
    reasoning about Architecture Decisions that have been made and architectural alternatives not
    chosen" — a standardized decision-plus-rationale pairing predating D-System by roughly a decade
    (ISO 42010:2011) to over two decades (IEEE 1471-2000). The general-purpose Correspondence/
    Correspondence Rule mechanism names "traceability, dependency, constraint and obligation" as
    relation types between architecture-description elements.
  - >
    iso-42010-2022-architecture-description-standard (free iTeh preview, 15 pages of the paywalled
    standard, read in full through Clause 5.2.3; the standard's own rationale-defining clauses,
    5.2.12 and 6.10, sit past the preview and are corroborated only via the working-group page above
    — recorded as `access_limitation: secondary_coverage` for that reason): confirms the same
    Decision/Rationale/Correspondence vocabulary from the normative standard's own Terms and
    Definitions (Clause 3), independent of the companion working-group page.
assessment: >
  This is one of the most densely prior-arted hypotheses in the entire review. The claim that
  development artifacts are the downstream, traceable result of a persistent decision/
  requirement lineage is the organizing idea of at least five independent traditions found in
  this campaign: architecture-decision-record research (Jansen & Bosch 2005, formally extended
  by Zimmermann et al. 2009), model-based systems engineering's "digital thread" (2022), a
  granted US patent commercially operated as a digital-engineering platform (priority 2023,
  granted 2025), and a 2026 agentic-coding tool (Aporia) explicitly self-described as an
  application of 1991-era design-rationale notation. Twelve of the matrix's 67 rows challenge H7,
  two at the matrix's ceiling overlap score (disputed on review to 4 and 3 respectively — see
  `strongest_challenger` above). The "multiple standards bodies" claim made in this paragraph before
  this phase is now directly evidenced rather than merely implied: ISO/IEC/IEEE 42010 (2011, 2022,
  and its IEEE 1471-2000 predecessor) standardizes exactly the Decision+Rationale pairing this
  hypothesis proposes, independent of the ADR research tradition already cited above.
  Qualification: most of these chains start at Decision or Requirement, not at Idea/Reasoning/
  Evidence as D-System's fuller lifecycle proposes, and none combines the chain with an
  append-only, typed-transition data model carrying the epistemic apparatus H1-H4 describe. ISO
  42010 is no exception — a documentation-structure standard, not an executable or queryable
  system, per its own row's `strongest_difference` field: it prescribes what an architecture
  description must record, not any state, transition, actor-authority, or runtime-feedback
  mechanism. But H7's literal claim is about the existence and traceability of the provenance chain
  itself, and on that claim the field's coverage — spanning three decades, multiple standards
  bodies, and a granted patent — is thorough. Status is unchanged from the prior reconciliation.
status: LIKELY_ALREADY_KNOWN
```

---

## H8 — Phase-bounded context construction

```yaml
hypothesis: >
  A planned development phase can serve as an explicit context boundary for agentic software
  engineering. (Review-instructions text, primary — falsify by finding "equivalent task/
  session/context lifecycle in agentic development systems.") The frozen register adds a
  consolidation half the review-instructions one-liner omits: context assembled from persistent
  reasoning/development lineage AND execution results consolidated back into persistent memory.
  Per the scope record: "A challenger that defeats only the assembly half has not defeated the
  frozen register's full claim." Both phrasings are addressed separately below, per that
  instruction, and not blended.
strongest_challenger: >
  Against the review-instructions phrasing: langgraph-checkpoint-library-oss
  (component_overlap=4, architecture_overlap=2, full_text). Against the frozen-register
  phrasing: solozobov-verify-gated-completion-admission-control-2026 (component_overlap=4,
  architecture_overlap=4, full_text) for the assembly half, with no source found that combines
  assembly and knowledge-consolidation together. 4 rows challenge H8 in total.
evidence:
  - >
    langgraph-checkpoint, base/__init__.py (861 lines, read in full): per-superstep persisted
    checkpoints with parent-chain lineage enabling backward walk and "time travel" replay, and
    an explicit `source={"input","loop","update","fork"}` classification of how each snapshot was
    produced — production-grade (41,574 GitHub stars on the parent repo, MIT-licensed, PyPI
    v4.2.0), with first-party Postgres/SQLite/Redis backends.
  - >
    langgraph-checkpoint, persistence docs: "Checkpointers ... save the graph state at every
    superstep ... enable human-in-the-loop, memory between interactions, durable execution, and
    more" — assembly (loading a checkpoint = a context boundary) and consolidation (put_writes
    records step results back into the checkpoint store) both present, at the level of raw
    execution state.
  - >
    Coordinator-noted comparison to the implemented system: D-System's own checkpoint mechanism
    (`.claude/skills/checkpoint/SKILL.md`) currently rewrites/overwrites summary sections in
    place rather than retaining a parent-linked chain of past checkpoints (adversarial codebase
    review, `04_state_transition_audit.md`, E42) — on this specific dimension, LangGraph's
    shipped behavior exceeds D-System's current implementation, not only its conceptual
    architecture.
  - >
    solozobov, Sec.6, Table 9: risk-tiered (Light/Standard/Deep) execution-unit boundaries with
    an explicit context compiler assembling role-specific envelopes from canonical/archive-only/
    prompt-injectable memory tiers — a developed, explicitly-named assembly mechanism.
  - >
    decision-oriented-programming-aporia-2026: a goal-scoped elicit/decide/implement/validate
    loop functioning as an implicit context boundary, with decisions persisted to a Decision Bank
    across the loop — partial consolidation (decisions, not general execution results).
  - >
    burckhardt-et-al-durable-functions-stateful-serverless-2021, Sec.3.2.3, Thm 6.4: a formally
    proven-correct append-only history log reconstructing one execution unit's state via full
    replay — a proven durability/reconstruction mechanism, but carrying zero epistemic content.
assessment: >
  Against the review-instructions phrasing, the claim is thoroughly known: LangGraph's
  checkpointer is a production, widely-deployed instance of exactly "task/session/context
  lifecycle in agentic development systems" — bounded execution units with parent-linked,
  forkable, resumable snapshots, assembled from and written back to persistent state at every
  step — and Durable Functions independently proves the same replay-as-reconstruction pattern
  correct in a different (serverless) tradition. D-System's own shipped checkpoint mechanism
  currently does less than the LangGraph library on the parent-chain dimension specifically.
  Against the frozen register's fuller claim, the picture splits. The assembly half — context
  built from a bounded unit's persistent lineage — is well covered (solozobov's context
  compiler, Aporia's Decision Bank, LangGraph's parent-chain loading). But no source
  demonstrates the consolidation half operating over persistent reasoning/development
  *knowledge* specifically, as opposed to opaque execution state: LangGraph's channel_values are
  "opaque key-value pairs" over generic application state (an absence the field's own literature
  names — burns-groth-agentic-ontological-notebook-memory-2026, Sec.5, characterizing LangGraph:
  "treat persisted state as opaque key-value pairs rather than typed ontological structures").
  Consolidation into a genuinely epistemic, knowledge-bearing memory, combined with assembly
  from the same, is the frozen register's distinguishing addition, and it is not demonstrated
  combined in any one system found.
status: LIKELY_ALREADY_KNOWN
```

---

## H9 — Bidirectional epistemic traceability

```yaml
hypothesis: >
  The system supports idea/knowledge -> realized functionality/outcome, and functionality/
  artifact -> reasoning/evidence/assumptions/decisions. (Review-instructions text.) The frozen
  register phrases the same forward/backward pairing with materially equivalent scope for H9
  itself; the scope record's H9 note is only that its `prior_art_families_to_search` annotation
  (Requirements Traceability Matrix, bidirectional traceability, design rationale systems) is
  subsumed by the search-domain matrix — no separate phrasing-divergence note is required for
  H9's verdict.
strongest_challenger: >
  graph-native-cognitive-memory-belief-revision-semantics-2026 (component_overlap=5,
  architecture_overlap=4) and jansen-bosch-architecture-as-decisions-wicsa-2005
  (component_overlap=5, architecture_overlap=4). Both are disputed on independent second review
  (`05_critical_collisions.md`): Kumiho re-derived to 4/3, Jansen & Bosch to 3/2 (the latter's
  flag surviving only via idea-level anticipation, not mechanism-level equivalence — no tool
  existed at publication). Per the owner's ruling, disputes are recorded, not applied; the
  matrix's original 5/4 scores stand and are cited as-is. `phase-lit-09` adds five more H9-tagged
  rows: iso-42010-conceptual-model-working-group-page (H7;H9, component_overlap=3,
  architecture_overlap=2, full_text, no collision), antoniol-recovering-traceability-links-tse-2002
  (H9 only, component_overlap=3, architecture_overlap=2, full_text, no collision), prov-agent-2025
  (H2;H3;H9, component_overlap=4, architecture_overlap=3, full_text, `critical_collision: yes`,
  second review: disputed — component re-derived 4->3, no trigger fires, but H9 specifically is
  confirmed as the one hypothesis of the three the row's own cells actually support),
  arnold-bohner-software-change-impact-analysis-book-1996 (H9;H10, component_overlap=3,
  architecture_overlap=1, secondary_coverage, no collision), and
  chianti-cia-tool-java-icse-2005 (H9;H10, component_overlap=4, architecture_overlap=2,
  secondary_coverage, `critical_collision: yes`, second review: disputed — component re-derived
  4->3, no trigger fires, and the reviewer argues the H9 tag is backwards against the frozen
  register; discussed below and not counted as H9 evidence). 23 of the matrix's 67 rows challenge
  H9 — still the single most heavily challenged hypothesis in the review.
evidence:
  - >
    graph-native-cognitive-memory (Kumiho): agent outputs "automatically versioned, addressable,
    and linked to the reasoning that produced them" — direct forward-and-backward linkage,
    commercially deployed.
  - >
    jansen-bosch, Sec.4.3, p.83: "Improved traceability of the design decisions and their
    relationship to features, design aspects, concerns, and among themselves" named as an
    explicit design requirement in 2005.
  - >
    log-is-the-agent, Sec.6, p.9: "Lineage is the deliverable ... every statement in the memo is
    traceable ... this recoverable chain from goal to output, reconstructable from the log
    alone, is the actual product" — a real, running, open-source (Apache-2.0) demonstration.
  - >
    evidence-graphs-fair-computation-defeasible-reasoning-2021: SPARQL-based backward-lineage
    queries over a 17,996-node evidence graph on real biomedical data.
  - >
    zep-graphiti-temporal-kg-agent-memory-2025, Sec.2.1: "bidirectional indices that track the
    relationships between edges and their source episodes ... enabling both forward and backward
    traversal," commercially deployed.
  - >
    omniscientist, us20250165226a1-ai-digital-thread-patent, model-based-digital-threads-
    sociotechnical-systems-2022, dhar-vaidhyanathan-varma-agenticakm-2026-arxiv,
    decision-oriented-programming-aporia-2026, solozobov-verify-gated-completion-admission-
    control-2026, tgms-agent-native-bitemporal-graph-2026, langgraph-checkpoint-library-oss:
    all independently score component_overlap=4 for a bidirectional traceability mechanism
    within their own domain (see per-row `strongest_dsystem_overlap` fields in the evidence
    matrix).
  - >
    Two items in that list are weaker H9 evidence than the lumped bullet above implies, per
    independent review. zep-graphiti's own text states its bidirectional episode<->entity
    indices were "not directly examined in this paper's experiments" (Sec.2.1) — the mechanism is
    specified but not run in the reported evaluation (`05`, source 14). langgraph-checkpoint's
    parent-chain lineage ties checkpoint-to-checkpoint mechanically; the reviewer found it never
    ties to a decision, requirement, or evidence object, since none of those types exist in the
    interface (`channel_values` is opaque application state) — of the two hypotheses the row
    lists, the reviewer called H9 "the more overstated" (`05`, source 9). Neither point changes
    the verdict below, given the remaining six-plus independently-scored traditions, but both are
    recorded so the density claim is not overstated by two of its weaker members.
  - >
    iso-42010-conceptual-model-working-group-page (full page, read in full) and
    antoniol-recovering-traceability-links-tse-2002 (full 14-page PDF, sdml.cs.kent.edu mirror,
    matching TSE pagination 970-983): two further, independently mature traditions — a standardized
    Correspondence/Correspondence Rule mechanism naming "traceability" explicitly as one of several
    bidirectional relation types between architecture elements, and a canonical, widely cited
    (WCRE1999->ICSM2000->TSE2002 lineage) automated code-to-document IR-based link-recovery method
    with a symmetric forward/backward query. Both are real, on-point additions to the density claim;
    neither combines with an epistemic-claim, decision, or evidence model (both rows'
    `conflict_trust_mechanism`/`provenance_model` fields are NOT_APPLICABLE beyond artifact linkage).
  - >
    prov-agent-2025 (full 7-page PDF, arxiv.org/pdf/2508.02866v3, Sec.IV-B): the one hypothesis of
    the row's three-hypothesis tag (H2;H3;H9) that survives independent review intact — Q1-Q3
    demonstrate genuine multi-hop backward traceability from an agent decision through its prompts
    and model invocations to originating sensor data, and Q4-Q5 demonstrate forward traceability to
    downstream results, all in a real, running, cross-facility-deployed system. (H2 and H3 are ruled
    out by the row's own cells and are not counted toward those hypotheses; see those blocks above.)
  - >
    arnold-bohner-software-change-impact-analysis-book-1996 (known only via Li et al. 2012's
    open-access survey, since the book itself could not be obtained through any exhausted access
    route): the traceability-based CIA class this book is credited with founding traces forward from
    a changed element across abstraction levels (requirements/design/code/tests) — foundational
    background for H9's cross-artifact traceability claim, though known only through secondary
    characterization and access-limited accordingly.
  - >
    chianti-cia-tool-java-icse-2005: listed by the row as challenging H9 alongside H10, but
    independent review argues this is backwards against the frozen register
    (`research/pre-literature-hypotheses.yaml`, lines 89-98), which requires bidirectional tracing to
    reach reasoning, evidence, assumptions, and decisions — Chianti's backward isolation terminates
    at atomic code changes and never reaches any of those endpoints, confirmed by the row's own
    NOT_APPLICABLE calls on every epistemic-apparatus field. Not counted as H9 evidence here; see the
    H10 block below for the parallel finding on that hypothesis.
assessment: >
  Bidirectional traceability — forward from intent to artifact, backward from artifact to
  rationale — is essentially the organizing promise of the requirements-traceability, design-
  rationale, digital-thread, and provenance-ontology literatures combined, and this campaign
  found it independently demonstrated across three decades and at least seven distinct
  technical traditions, several at production scale (Zep/Graphiti, LangGraph, Kumiho, the
  granted Istari patent). Twenty-three of the matrix's 67 rows challenge this hypothesis — more
  than any other, and the density only grows this phase: two further mature traditions (the ISO
  42010 standards lineage, the classical requirements-traceability-recovery literature via Antoniol
  2002) and a real, deployed system (prov-agent-2025, whose H9 contribution survives review even
  where its H2/H3 tags do not) are added. By raw density of independent corroboration, this remains
  the review's clearest case.
  One addition is explicitly excluded rather than credited: chianti-cia-tool-java-icse-2005's H9 tag
  is disputed as backwards against the frozen register by its own second review — H9 requires
  backward tracing to reach reasoning, evidence, assumptions, and decisions, and Chianti's
  backward-isolation mechanism, however precise and empirically validated, terminates at atomic code
  changes and never reaches any of those endpoints. This is exactly the shared-name-not-shared-
  mechanism risk this campaign's own thesis-discipline rule warns against: Chianti's "impact
  analysis" and D-System's "epistemic traceability" share a propagate/isolate shape but not an
  object domain, and crediting it as H9 support would be the error, not the omission. It is not
  counted here.
  Qualification: no single source combines all of D-System's proposed traceability directions
  (idea -> decision -> requirement -> specification -> plan -> phase -> implementation ->
  verification -> deployment -> runtime -> revised knowledge) into one continuous chain across
  that many stages simultaneously — most sources cover a contiguous subset. But the mechanism
  class itself, and multiple examples spanning most individual stage-to-stage links, are
  established more thoroughly than any other hypothesis in this review — bounded, like every
  claim in this file, by the coverage caveat that 336 of 400 collision candidates surfaced by
  this campaign were never deep-read (`07_anti_novelty_case.md`'s coverage caveat), not a claim
  that no unread source could sharpen or contest the picture. Status is unchanged from the prior
  reconciliation.
status: LIKELY_ALREADY_KNOWN
```

---

## H10 — Epistemic blast-radius analysis

```yaml
hypothesis: >
  Changing/falsifying an assumption, evidence source, or claim identifies downstream decisions,
  requirements, plans, artifacts, tests, and functionality that require reassessment.
  (Review-instructions text.) The frozen register carries the sharper bar: propagation "from
  epistemic change rather than only artifact/requirement change." This verdict is assessed
  against the frozen register's sharper bar specifically, since it is the more demanding
  reading and the evidence bears on it directly; the review-instructions phrasing is satisfied
  by the same evidence a fortiori.
strongest_challenger: >
  memtx-transactional-belief-commit-2026 (component_overlap=4, architecture_overlap=2, full_text)
  remains the only H10 source with component_overlap above 3 and the only one unchanged by this
  phase. `phase-lit-09` adds three more H10-tagged rows, none of which displaces it:
  ferrante-ottenstein-warren-program-dependence-graph-1987 (H10 only, component_overlap=2,
  architecture_overlap=1, full_text, no collision), arnold-bohner-software-change-impact-analysis-
  book-1996 (H9;H10, component_overlap=3, architecture_overlap=1, secondary_coverage, no collision),
  and chianti-cia-tool-java-icse-2005 (H9;H10, component_overlap=4, architecture_overlap=2,
  secondary_coverage, `critical_collision: yes`, second review: disputed — component re-derived
  4->3, no trigger fires, and the reviewer argues the H10 tag is backwards against the frozen
  register's own falsification criterion; discussed below and not counted toward H10). 7 rows
  challenge H10 in total; H10 still has exactly one source with component_overlap above 3.
evidence:
  - >
    memtx, Sec.3.4/3.5 (full HTML text, arxiv.org/html/2607.23929v2, read twice): "retracting a belief triggers typed cascading repair of its derived
    records and tool side effects. Two invariants, action-safety gating and cascade-repair
    completeness, are machine-checked by property-based testing and bounded exhaustive
    enumeration of 5.5 million protocol states, with zero violations." Retraction of a belief —
    an epistemic change, not an artifact or requirement edit — triggers verified, cascading
    downstream reassessment. This is the frozen register's sharper bar, met on the propagation-
    trigger dimension specifically.
  - >
    memtx, strongest_difference field: scoped to a single shared memory store's internal derived
    records and tool-call side effects, not D-System's cross-lifecycle propagation into
    requirements, plans, specifications, artifacts, and tests; multi-AI-agent only, no human
    actor.
  - >
    assumptions-management-software-development-mapping-study-2018 (component_overlap=2,
    peer-reviewed, 134-study systematic mapping): "Assumptions Tracing and Monitoring" is
    documented as the least-studied and least-tooled of twelve identified assumption-management
    activities (14.2% and 2.2%-13.4% of surveyed studies respectively) despite the same study's
    RQ8 consequence taxonomy documenting extensive real-world damage, including explicitly named
    hindered change-impact analysis, from not tracing assumptions well.
  - >
    keim-kaplan-scattered-to-structured-akm-vision-2026, Sec.4 (component_overlap=2): names
    change-impact analysis over an architectural knowledge base as an explicit, currently unmet
    target capability, in a 2026 ICSE-C vision paper.
  - >
    perry-wolf-foundations-software-architecture-1992, Sec.5.1: names forward/backward
    architecture<->requirements<->design dependency analysis as a desired, unmet capability,
    three decades before this campaign.
  - >
    ferrante-ottenstein-warren-program-dependence-graph-1987 (full 31-page PDF,
    csa.iisc.ac.in mirror): the foundational data-dependence-plus-control-dependence structure
    underlying nearly all subsequent program-slicing and change-impact tooling, including an
    incremental-update algorithm (Sec.5) that re-triggers analysis only on the edges a change
    actually affects — the mechanistic ancestor of "compute what a change affects," decades before
    this campaign, but confined entirely to compiler-internal program representations with no
    knowledge-state, provenance, actor, or epistemic-claim model of any kind (H1-H4 all
    NOT_APPLICABLE per the row). Sharpens H10's ancestry; does not challenge its actual claim.
  - >
    arnold-bohner-software-change-impact-analysis-book-1996 (known only via Li et al. 2012's
    open-access survey, the book itself unobtainable through any exhausted access route): the
    named, foundational origin of "change impact analysis" and its most-cited definition — the
    literal ancestor vocabulary this campaign's own methodology maps H10's "epistemic blast radius"
    onto (`research/literature-review/CLAUDE.md` Sec.6's translation table). Everything reported
    about it, via secondary coverage only, concerns code/artifact-level structural dependency, not
    epistemic claims or evidence-triggered propagation.
  - >
    chianti-cia-tool-java-icse-2005: listed by the row as challenging H10 alongside H9, but
    independent review argues this is backwards against the frozen register's own falsification
    criterion (`research/pre-literature-hypotheses.yaml`, lines 100-109), which requires propagation
    "from epistemic change rather than only artifact/requirement change" to falsify H10 — Chianti's
    forward-propagate/backward-isolate pipeline, however precise and empirically validated (52% of
    tests affected per edit on average, isolated to 3.95% of atomic changes), propagates only from
    artifact (code) change, the exact category the criterion excludes. The reviewer's own words:
    Chianti is "the generic shape of essentially any change-impact or build-dependency tool," not a
    mechanism mirroring D-System's heterogeneous, epistemic-claim-bearing propagation. Not counted
    as H10 evidence here.
assessment: >
  A real, machine-verified system already performs the core mechanism H10 (and especially the
  frozen register's sharper bar) describes: an epistemic retraction cascades, correctness-
  verified, to every downstream derived record and side effect (memtx). Structurally, this is
  not a proposal or a vision-paper aspiration — it is a proven property over 5.5 million
  enumerated protocol states. If the question is "does epistemic-change-triggered cascading
  reassessment already exist as a working mechanism," the answer is yes.
  Qualification: memtx's proof applies to one memory store's own derived records and tool
  effects, not to a cross-lifecycle span into decisions, requirements, plans, artifacts, and
  tests the way D-System's H10 specifically claims — and the field's own systematic literature
  survey (Yang, Liang & Avgeriou 2018, 134 studies) independently confirms that the broader,
  cross-lifecycle version of exactly this capability is the least mature, least tooled activity
  in the software-assumptions field despite well-documented need. Read together, these two
  sources point the same direction: the underlying mechanism (retraction triggers verified
  cascading repair) is proven and known; the specific scope D-System proposes (spanning
  decisions/requirements/plans/artifacts/tests, triggered by epistemic rather than only artifact
  change) is a recombination that the field's own survey confirms nobody has built yet, not a
  mechanism nobody knows how to build.
  `phase-lit-09`'s three additions reinforce this reading rather than change it. Chianti is the
  most mature, most empirically validated artifact-level change-impact tool found across this
  entire campaign — more so even than memtx, which is confined to a multi-AI-agent-only memory
  store — and its own second review still finds it falls on the wrong side of H10's own
  falsification criterion: propagation "from epistemic change," not from artifact/code change alone.
  That a mature, 20-year-old, real-world-validated exemplar of exactly this category still does not
  cross the bar is itself informative — it shows the artifact-level CIA tradition genuinely stops at
  the boundary the frozen register draws, rather than the boundary being an artifact of thin
  search — but it is evidence for the qualification above, not against it, and it must not be
  counted as a positive H10 challenger merely because it shares "change impact" vocabulary with the
  hypothesis's own name; doing so would be exactly the shared-name-not-shared-mechanism error this
  campaign's thesis discipline exists to catch. arnold-bohner and ferrante-ottenstein-warren are
  ancestry, not challengers: they establish how old and well-studied artifact-level change-impact
  analysis is, which is precisely what makes its failure to cross into epistemic-change propagation
  notable rather than a search gap. Status is unchanged from the prior reconciliation: memtx remains
  the only source that meets H10's core mechanism, and the specific cross-lifecycle,
  epistemic-triggered scope D-System proposes remains, per the field's own survey and now a second,
  independent confirmation from its most mature artifact-level exemplar, an unbuilt recombination
  rather than an unknown mechanism.
status: KNOWN_COMPONENT_NEW_INTEGRATION
```

---

## H11 — Runtime-to-knowledge closure

```yaml
hypothesis: >
  Runtime telemetry, tests, incidents, and outcomes become provenance-bearing evidence updating
  the same knowledge structure that generated implementation intent. (Review-instructions text;
  no material frozen-register divergence flagged for H11.)
strongest_challenger: >
  ibm-architectural-blueprint-autonomic-computing-whitepaper-2006 (component_overlap=1,
  architecture_overlap=1, secondary_coverage) and burns-groth-agentic-ontological-notebook-memory-2026
  (component_overlap=4, architecture_overlap=3, preprint_version, matrix values unchanged, found not
  to demonstrate the loop it was credited with — see below) were the only two matrix rows listing
  H11 before this phase. `phase-lit-08` ran H11's first dedicated collision search
  (`00_search_ledger.csv`, LIT-08-S057 through S082: vocabulary discovery, backward citation
  chaining through the awareness-requirements lineage, and direct collision queries) and deep-read
  six new candidates. requirement-evolution-requirements-adaptive-systems-seams-2012 (EvoReqs;
  component_overlap=3, architecture_overlap=2, full_text) is now the closest *implemented* candidate
  found for H11 in the whole campaign; souza-lapouchnian-robinson-mylopoulos-awareness-requirements-
  seams-2011 (component_overlap=3, architecture_overlap=2, full_text) and
  runtime-verification-self-adaptive-changing-requirements-2023 (component_overlap=3,
  architecture_overlap=2, full_text) are the family's other implemented members;
  sawyer-bencomo-whittle-letier-requirements-reflection-icse-2010 (component_overlap=2,
  architecture_overlap=1, full_text) is the family's founding, unimplemented vision paper;
  krentsel-agarwal-cemri-reality-final-verifier-two-gaps-agentic-se-2026 (component_overlap=2,
  architecture_overlap=1, full_text) and bajaj-ai-augmented-closed-loop-quality-engineering-2026
  (component_overlap=2, architecture_overlap=1, full_text) are two brand-new 2026 papers outside that
  lineage, read in full below.
evidence:
  - >
    (Unchanged.) Independent review (`05`, source 16) found burns-groth's claimed closed loop —
    "curation failure to note to GitHub issue to schema change" — is the paper's own stated future
    work ("We are developing a feedback loop for iterative refinement"), not a demonstrated result;
    nothing in its Demonstration section or Conclusion shows it closing.
  - >
    (Unchanged.) ibm-architectural-blueprint-autonomic-computing-whitepaper-2006: MAPE-K, the
    foundational Monitor-Analyze-Plan-Execute-over-Knowledge control loop, is the widely cited
    ancestor of "close the loop from runtime observation back into a knowledge structure that also
    drives action," but its "Knowledge" is short-lived, single-control-loop operational state, not
    an append-only, provenance-bearing, cross-session history, and the architecture is explicitly
    oriented toward reducing human involvement, unlike D-System's collaborative framing.
  - >
    sawyer-bencomo-whittle-letier-requirements-reflection-icse-2010 (complete 4-page paper, author
    copy): the family's founding statement — requirements as introspectable, runtime-mutable
    objects, synchronized bidirectionally with architecture — is the closest verbal match in the
    ranked H11 sources to a knowledge structure being revised at runtime, and also the least
    realized: "We know of no approach that fully supports requirements reflection" (Abstract); every
    mechanism is stated as a named "Challenge" (Sec.3), zero implementation of any kind.
  - >
    souza-lapouchnian-robinson-mylopoulos-awareness-requirements-seams-2011 (complete paper): AwReqs
    are first-class, runtime-monitorable requirement objects with an explicit satisfaction lifecycle
    (Undecided->Succeeded/Failed/Canceled) and an append-only PropertyEvent evaluation repository —
    the closest of the family to D-System's state-plus-evidence-at-runtime idea. But the authors name
    the loop closing runtime evidence back into requirement revision as explicitly future work ("is
    at the core of our future work," Sec.7); AwReqs themselves are elicited manually at design time,
    not derived from evidence, and carry no provenance model (actor, authority, evidence, method,
    lineage, delegation).
  - >
    requirement-evolution-requirements-adaptive-systems-seams-2012 (EvoReqs; complete paper): the
    strongest *built* analog in this dispatch's payload — ECA-triggered, code-executing mutation of
    the live requirements/goal model in direct response to a runtime AwReq failure, implemented
    (OSGi, open-source, github.com/vitorsouza/Zanshin) and evaluated on a case study grounded in a
    real historical incident. But the set of possible mutations is closed and hand-authored in
    advance by an analyst — the system selects among anticipated responses, it does not derive a
    novel requirement change from arbitrary runtime evidence — and no provenance model records why or
    by what authority a mutation fired. This is a rule-triggered control-loop reaction over a
    pre-specified vocabulary, the same MAPE-K-family shape this block already distinguishes from
    D-System's claim above, not a narrower instance of "runtime evidence becomes provenance-bearing
    evidence updating a knowledge structure."
  - >
    runtime-verification-self-adaptive-changing-requirements-2023 (complete paper, arXiv HTML):
    persistent observer state functioning as knowledge preserved across change, explicitly framed as
    "co-evolution of runtime verification and requirements" (Sec.I) — but requirement changes are
    externally/human-supplied by design: "we believe that fully automating the requirements
    manager...is challenging and also possibly not desired" (Sec.III-B). No provenance model; the
    mechanism never reaches Decision, Specification, Plan, Artifact, or Deployment stages.
  - >
    krentsel-agarwal-cemri-reality-final-verifier-two-gaps-agentic-se-2026 (complete paper, arXiv
    HTML): the single closest terminological match to H11 found anywhere in this campaign — an
    "outer assurance-revision loop that uses deployment evidence to revise the requirements, model,
    or evaluator" (Abstract), with a proposed "versioned assurance argument" linking claims to
    evidence, assumptions, scope, and owners, the closest any ranked source comes to gesturing at a
    provenance model for this exact loop. But Sec.1 itself frames the loop as part of "a research
    agenda," motivated by third-party incident reports, never built or evaluated by the authors — a
    direct instance of the same failure mode already caught in burns-groth, here correctly not scored
    as a critical collision.
  - >
    bajaj-ai-augmented-closed-loop-quality-engineering-2026 (complete paper, arXiv HTML): the only
    ranked H11 source that both implements a runtime-evidence-to-upstream-artifact feedback formula
    and reports quantitative results — production defect-severity and incident-impact signals
    measurably change a requirement-linked risk score used in later release decisions (Sec.3.5-3.6).
    But the "knowledge structure" being revised is a single derived numeric feature attached to a
    requirement for test-prioritization, not the requirement's content, its specification, or any
    decision/rationale artifact — materially narrower than H11's claim — and the evaluation dataset
    is semi-synthetic, not collected from a deployed system.
assessment: >
  The best case that runtime-to-knowledge closure is already known now draws on a genuine academic
  tradition rather than one disputed source. The "awareness requirements" family spans 2010-2023,
  peer-reviewed at ICSE and SEAMS, and its most-implemented member (EvoReqs, 2012) is a real, working,
  evaluated system where a runtime evidence event — an AwReq failure — automatically triggers a
  mutation of the live requirements model. Two brand-new 2026 papers extend the picture: krentsel
  states H11's own mechanism in language that maps almost one-to-one onto it, and bajaj reports actual
  quantitative before/after results from a deployed feedback formula. If either the family's most
  mature member or either of the 2026 papers held up as a working instance of the specific claim, H11
  would be in real trouble: a fourteen-year academic tradition converging on this exact idea,
  reinforced by working 2026 tooling, would be a strong falsification case.
  None of them holds up as that instance, but not for a uniform reason, and the reason matters for
  what this finding is worth. Three of the six — sawyer-bencomo (2010), souza-lapouchnian (2011), and
  krentsel (2026) — name the loop and explicitly state it as future work, a challenge, or a research
  agenda, never built. runtime-verification-self-adaptive-changing-requirements-2023 keeps a human
  deciding what changed and how, by explicit design choice, not merely as an unfilled gap. bajaj builds and evaluates a real feedback
  loop, but onto a single derived risk number, not the decision/rationale content H11 actually asks
  about. EvoReqs is the one member that is both implemented and closes a loop from runtime evidence
  back into an actual requirements-model mutation — but on inspection that loop is a rule-triggered
  control-loop reaction over a closed, analyst-authored vocabulary of anticipated responses, the same
  MAPE-K-family shape this block already treats as distinct from D-System's provenance-bearing,
  evidence-driven claim, not a scoped-down version of it.
  Checked against this file's two-condition rule: this phase's search satisfies condition 1 in
  full — 26 queries across vocabulary discovery, a genuine multi-paper backward citation chain
  through the awareness-requirements lineage (each paper's own reference list read in full), and
  direct collision queries, with every candidate deep-read from primary text and verified against it
  before being credited (catching krentsel's "we propose" framing exactly the way burns-groth's was
  caught previously). Condition 2 is where H11 differs from H1 rather than resembling it: the
  comparator family found here is genuinely mature — a fourteen-year, multi-venue, peer-reviewed
  lineage, not a scattering of unreviewed hobby repositories — so the first half of condition 2 is
  satisfied where H1's was not. But the second half fails: the family's best-implemented member
  (EvoReqs) is a structurally different mechanism — closed-vocabulary rule triggering, not evidence
  weighed into a provenance-bearing knowledge revision — not a narrower instance of the same one, and
  every member that *is* aimed at the same mechanism (sawyer-bencomo, souza-lapouchnian, krentsel)
  states it as unbuilt. A mature field that keeps naming the same gap across sixteen years without
  building the thing itself is suggestive, but under this file's rule it is not the same as a mature
  field producing even a narrow positive instance of the actual claimed mechanism the way Goldman does
  for H4's general reading — it is closer to a mature field solving an adjacent problem well
  (rule-triggered adaptive control) while repeatedly declining to solve this one, which the rule
  treats as a false-friend match, not a same-mechanism one. That keeps H11 short of
  `POTENTIALLY_DISTINCT` for the same structural reason H1 falls short, even though the two fail
  different halves of the same test — and it is a genuinely closer call than H1's, worth recording as
  such rather than flattening into an identical verdict for an identical reason. The status is
  unchanged from the prior reconciliation, re-examined rather than reasserted: this campaign has
  found, for the first time, a mature field that has spent over a decade naming this exact gap, and
  still has not searched up a working instance of it — which is evidence worth weighing in synthesis,
  but is not, by this file's own rule, sufficient on its own to call the mechanism absent from the
  wider field.
status: INSUFFICIENT_EVIDENCE
```

---

## Summary table

| Hyp. | Status | Strongest challenger (source_id) | Challenger count |
|---|---|---|---|
| H1 | INSUFFICIENT_EVIDENCE | mythologiq-agent-memory-oss / subit-wiki-epistemic-hmm-oss (closest new candidates, both mechanism-mismatched — see block) | 8 |
| H2 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied) | 16 |
| H3 | KNOWN_COMPONENT_NEW_INTEGRATION | log-is-the-agent-event-sourced-reactive-graphs-2026 / omniscientist-coevolving-ecosystem-human-ai-scientists-2026 (tied on score); grading-narrators-isnad-rijal-claim-provenance-2026 (closest by mechanism fit at a lower score — see block) | 16 |
| H4 | LIKELY_ALREADY_KNOWN (both phrasings converge — see block) | grading-narrators-isnad-rijal-claim-provenance-2026 (ISNAD) / not-all-agreement-counts-as-corroboration-2026 (PACT) | 9 |
| H5 | KNOWN_COMPONENT_NEW_INTEGRATION | solozobov-verify-gated-completion-admission-control-2026 / zep-graphiti-temporal-kg-agent-memory-2025 (tied; log-is-the-agent dropped on review) | 10 |
| H6 | KNOWN_COMPONENT_NEW_INTEGRATION | omniscientist-coevolving-ecosystem-human-ai-scientists-2026 | 3 |
| H7 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied) | 12 |
| H8 | LIKELY_ALREADY_KNOWN (review-instructions phrasing); KNOWN_COMPONENT_NEW_INTEGRATION (frozen-register phrasing) | langgraph-checkpoint-library-oss (review-instructions) / solozobov-verify-gated-completion-admission-control-2026 (frozen-register, assembly half only) | 4 |
| H9 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied; zep-graphiti/langgraph's contribution to this row is weaker than the raw count implies — see block) | 23 |
| H10 | KNOWN_COMPONENT_NEW_INTEGRATION | memtx-transactional-belief-commit-2026 | 7 |
| H11 | INSUFFICIENT_EVIDENCE | requirement-evolution-requirements-adaptive-systems-seams-2012 (closest built candidate, different mechanism shape — see block) | 8 |

`phase-lit-08` ran the first dedicated collision search this campaign has aimed at H1, H4, and H11
specifically, and the result was not uniform at that time, though it was checked for uniformity
deliberately — the same mistake `phase-lit-06`'s first pass made (moving H1 and H11 toward
`POTENTIALLY_DISTINCT` while leaving H4 behind, for hypotheses in materially the same evidential
position) is exactly what that reconciliation set out not to repeat. Applying the two-condition rule
stated at the top of this file uniformly: all three hypotheses satisfied condition 1 (a genuinely
dedicated, multi-strategy, primary-text-verified search ran for each, for the first time). Condition
2 — a mature, on-topic comparator family whose closest member instantiates the *same* mechanism,
even narrowly — is where they separated at that point. H1's comparator family
(mythologiq-agent-memory-oss, subit-wiki-epistemic-hmm-oss, toki, symbolic-memory) fails on
maturity: the closest candidates are weeks-old, single-author, unreviewed repositories, or (toki) a
rigorous proof of an unrelated triple. H11's comparator family (the 2010-2023
awareness-requirements lineage, plus krentsel and bajaj) is genuinely mature but fails on mechanism
match: its best-implemented member, EvoReqs, closes a loop over a closed, hand-authored rule
vocabulary — a control-loop reaction, not a narrower instance of
evidence-becomes-provenance-bearing-knowledge. Both stay `INSUFFICIENT_EVIDENCE`, re-examined and
confirmed unchanged, for related but distinct reasons that are argued in full in their own blocks
rather than asserted here.
H4 was, at that same point, the one hypothesis where condition 2 was satisfied only for its
review-instructions general phrasing — Goldman (2001), backward-chained from Mayo-Wilson (2014), a
mature, peer-reviewed, closed-form demonstration of the general discount mechanism H4 describes —
while its frozen-register graph-topological phrasing still failed condition 2 on maturity in the
same shape H1's does, producing the split verdict this table showed at the time
(`KNOWN_COMPONENT_NEW_INTEGRATION` on the general phrasing, `INSUFFICIENT_EVIDENCE` on the
graph-topological one). That split has since been superseded within this same phase: two further
sources found by this phase's own collision searches after this reconciliation had already run and
closed (grading-narrators-isnad-rijal-claim-provenance-2026 and
not-all-agreement-counts-as-corroboration-2026) closed the maturity gap on the graph-topological
reading as well, and a clean-room re-derivation (`phase-lit-09 H4R`) converged both phrasings on
`LIKELY_ALREADY_KNOWN`. See the H4 block above for the full argument; it is the current source of
truth and is not restated here.
This phase's own duplicate-discovery rate (58/387 = 15.0% raw, 37/347 = 10.7% distinct, computed
against the pre-phase inventory snapshot) is lower than `LIT-06 G`'s campaign-wide 20.0%/17.3% — a
falling duplicate rate, i.e. more new material found, not less, which argues against approaching
saturation rather than for it. Per the owner's ruling, saturation is not claimed for any hypothesis
on that basis; route one of the decision rule stays closed for all three uniformly, and every
status change or non-change above rests on route two — search depth and comparator quality — argued
explicitly, hypothesis by hypothesis, rather than on the duplicate-rate trend. `NOVEL` remains
unavailable to all three; none met the bar this file states for `POTENTIALLY_DISTINCT` at that
point. H1 and H11 remain open to revision by a further, more targeted search this reconciliation did
not perform; H4 has since received exactly that further evidence and moved off its split verdict
entirely, as argued in its own block. Every other remaining gap in the table above is a gap in what
any single found system's *scope* combines (cross-lifecycle span for H6/H10; knowledge-bearing
consolidation for H8's frozen phrasing) — not a gap in whether the field knows how to build the
underlying mechanisms, and not a search-quality question the way H1/H11 still are. That distinction
is what separates `KNOWN_COMPONENT_NEW_INTEGRATION` from `INSUFFICIENT_EVIDENCE` in this review's
vocabulary.
