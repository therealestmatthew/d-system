# Hypothesis tests — H1 through H11

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
  full_text); secondary: burns-groth-agentic-ontological-notebook-memory-2026 (component_overlap=4,
  architecture_overlap=3, preprint_version)
evidence:
  - >
    eywa, Table 2 / Sec.4.3: a memory-object model (Evidence/Signal/Candidate/Belief/Link) that
    independently tracks ontological type, epistemic status/tier, and lifecycle state on the same
    object, in a real, implemented, evaluated agent-memory system (per-question artifacts
    published at eywa.to/research, Sec.1 Abstract).
  - >
    eywa, Sec.4.1, Eq.1: "a belief is valid only to the extent that it is supported by one or
    more evidence records" — the epistemic axis is load-bearing, not decorative.
  - >
    burns-groth, Sec.3.2-3.3: a domain-thing vs. Artifact/Fragment/Note (ICE) hierarchy, drawing
    on the W3C-adjacent Information Artifact Ontology (Ceusters 2013), with per-note actor
    attribution and full backward provenance to source — an independently-arrived-at ontological/
    epistemic/derivational split in a second, separately-authored 2026 system.
assessment: >
  Two independently authored 2026 agent-memory systems have already landed on a roughly
  three-axis classification for knowledge objects — eywa's ontological-type/epistemic-tier/
  lifecycle-state triple tracked on the same memory object, and Burns & Groth's ontological/
  epistemic/derivational (ICE) split drawn from an established upper ontology. That two teams,
  working independently in the same 2026 window, converged on the same general shape without
  citing each other or a common ancestor for the classification itself, is evidence that
  orthogonal state classification is an idea whose time has come as agent-memory systems mature,
  not a distinctively D-System insight. Against the review-instructions phrasing ("may be
  uncommon in agent-memory systems") eywa alone is close to sufficient to falsify "uncommon": it
  is exactly an agent-memory system, and it already does this.
  Qualification: neither system applies the classification uniformly across a full
  idea-to-runtime lifecycle. Eywa's three dimensions are described by its own authors as "a
  memory-object taxonomy and a two-tier capture/validation pipeline," confined to conversational
  memory, not a formally orthogonal (O,E,L) triple applied system-wide; Burns & Groth's
  classification is per-skill and domain-specific. Against the frozen register's added
  "idea/action" lifecycle-dimension nuance specifically, neither source's lifecycle field
  extends to idea or action states — that piece of the frozen claim is untested by this
  evidence, not falsified and not confirmed. The frozen register's narrower domain claim ("not
  commonly integrated in existing agent-memory systems") is, if anything, more directly
  undercut than the review-instructions text, since the strongest match is itself exactly such
  a system.
status: KNOWN_COMPONENT_NEW_INTEGRATION
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
  scores in the entire evidence matrix. 13 rows challenge H2 in total.
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
assessment: >
  If any hypothesis in this review is dead on arrival, it is this one. The idea that reasoning/
  decision history should be preserved as explicit, typed, non-overwritten transitions distinct
  from ordinary semantic edges is one of the most densely prior-arted claims found across the
  whole campaign: it traces through classical belief-revision logic (AGM, 1985), classical
  temporal-database theory (Snodgrass, 1999), the architecture-decision-record tradition (Jansen
  & Bosch 2005, formally extended by Zimmermann et al. 2009), a W3C provenance standard (PROV-O,
  2013), and multiple production 2025-2026 agent-memory systems (Zep/Graphiti, Kumiho) — one of
  which (Kumiho) has a published, if partially unreproduced, formal correspondence proof to the
  AGM postulates specifically. Thirteen of the matrix's 34 rows challenge H2; two reach the
  matrix's ceiling component-overlap score of 5. This is not a thin or contested finding.
  Qualification: none of these sources combine transition-preservation with D-System's full
  proposed epistemic+ontological+lifecycle state model (H1) simultaneously, and Kumiho's own
  formal correspondence is explicitly scoped to "a deliberately simple propositional logic over
  ground triples," with its strongest reported benchmark carrying a self-disclosed independent-
  reproduction gap. But H2 as literally worded is about the transition-preservation mechanism
  itself, not that combination, and on that literal claim the field's coverage is thorough and
  multi-lineage, not a single narrow precedent.
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
  architecture_overlap=4, full_text). 9 rows challenge H3 in total.
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
assessment: >
  The two halves of H3 are individually well established but no found source combines them.
  Rich, typed, multi-actor provenance representation is thoroughly known (PROV-O, EVI, log-is-
  the-agent, omniscientist, burns-groth all score component_overlap=3-4 on exactly this).
  Automated conflict resolution driven by a belief-revision rule is also thoroughly known (AGM,
  1985, and its 2026 descendants). Given both ingredients are independently mature, wiring
  provenance fields into an entrenchment-style automated arbitration rule is an unglamorous
  combination of two already-solved pieces, not a research gap — exactly the "known component,
  new integration" pattern the campaign's anti-novelty case is built to detect.
  Qualification: it is notable, and worth recording rather than explaining away, that the
  field's most rigorous, most deployed provenance systems repeatedly and explicitly decline to
  automate this step. EVI's authors state directly that challenge resolution "ultimately
  require[s] human judgment"; TGMS explicitly disables provenance-based write-back "pending
  policies." That two separate, careful, 2021-2026 engineering teams built the provenance
  machinery and then deliberately stopped short of automating arbitration on top of it is some
  evidence that the combination carries a correctness or liability risk its builders did not
  want to accept — not proof that it is hard, but a reason the absence may not be mere neglect.
  This tempers confidence without changing the verdict: the components needed are known: no
  source demonstrates a materially equivalent working arbitration mechanism, so this stops short
  of LIKELY_ALREADY_KNOWN, but the ingredients are too mature to call the combination distinct.
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
  review-instructions' general wording. Both phrasings are addressed together below since the
  same evidence bears on each; the frozen phrasing's topological language is, if anything, the
  closer match to what was found.
strongest_challenger: >
  epistemic-sybil-resistance-bara-2026 (component_overlap=4, architecture_overlap=2, full_text)
  — the sole challenger. This is a thin-evidence hypothesis by count (1 challenger, after five
  prior phases at zero) and is assessed as such, per the coordinator's guidance: neither
  inflated into a falsification nor waved away as absent.
evidence:
  - >
    bara-2026, Sec.6: a provenance DAG G=(V,E_G) "whose nodes can represent primitive
    observations, datasets, documents, transformations, retrieval operations, models, agents,
    and reports, and whose edges u->v record that information from u was available in generating
    v" — a graph-topological structure, formally defined.
  - >
    bara-2026, Sec.5.2, Corollary 2: a closed-form discount kappa_m = 1/(1+rho(m-1)), "exactly
    m_eff/m" — corroborating reports sharing an evidentiary root are discounted rather than
    counted as independent confirmations, the precise mechanism H4 (and the frozen register's
    topological phrasing) describes.
  - >
    bara-2026, Sec.3.1: "common ancestry does not imply that one report is redundant conditional
    on the other, since different reports can extract different aspects" — a nuance beyond naive
    discounting.
  - >
    bara-2026, human_agent_scope field: AI-agent-only; no human witnesses or mixed human-agent
    evidence modeled or evaluated — explicitly outside H4's "mixed human-agent knowledge" scope.
  - >
    bara-2026, Sec.9: the paper's own stated open problems include practical provenance
    authentication and estimating I(Theta;Z|R) from raw reports — design guidance, not a
    runnable, deployed aggregator.
  - >
    Negative result, dong-berti-equille-srivastava-truth-discovery-copying-detection-2009
    (component_overlap=3, hypotheses_challenged=NOT_APPLICABLE): deep-read specifically as the
    closest named prior-art family for H4 (HMM-detected copier/independent classification
    feeding a Bayesian truth-decision model). Recorded verdict: "does not challenge H3 or H4 ...
    it neither models transition provenance with actor/authority/evidence/method/lineage/
    delegation (H3) nor a provenance/topology-aware graph over reasoning/evidence paths in mixed
    human-agent knowledge (H4)." The mechanism is correlation-based copier detection over a
    fixed, closed set of structured web sources, not a derivation-graph topology.
assessment: >
  A closed-form, formally derived discount for corroboration sharing an evidentiary root,
  published on a provenance DAG whose node/edge semantics are essentially the same shape as
  D-System's own reasoning-lineage graph, already exists (bara-2026) — not as loose analogy but
  as matching mathematics: a topology-aware discount factor for shared-ancestry agreement is
  exactly what H4, and especially the frozen register's "graph-topological ... discounted based
  on shared lineage" phrasing, describes. Treated uncharitably, H4 is simply an unformalized
  restatement of a result that already has a closed-form proof.
  Qualification: this is one preprint, found late (Pass 3 of this phase, after five prior phases
  found nothing), scoped to AI-agent report multiplicity with no human actor and no deployed
  aggregator — its own author leaves the practical protocol as an open problem. That the field's
  most likely candidate ancestor family (truth discovery / copying detection, dong 2009) was
  searched specifically for this hypothesis and came back a deliberate non-match, rather than a
  weak match, is itself informative: it suggests the graph-topological formalization is recent
  and narrow rather than an established, decades-deep tradition like H2's. One close but
  narrowly-scoped, unimplemented formal result is not "an established framework" in the sense
  the falsification criterion asks for, but it is also too close, too formal, and too directly
  on-point to say the hypothesis stands untested. Per the coordinator's framing: thin evidence
  cuts both ways, and INSUFFICIENT_EVIDENCE is the honest status for exactly this shape of
  result, not a discomfort to be resolved by picking a side.
status: INSUFFICIENT_EVIDENCE
```

---

## H5 — Topology-aware context transfer

```yaml
hypothesis: >
  Context selection includes current state, reasoning lineage, supporting evidence, dissent,
  authority, convergence, and unresolved uncertainty. (Review-instructions text; no material
  frozen-register divergence flagged for H5.)
strongest_challenger: >
  log-is-the-agent-event-sourced-reactive-graphs-2026 (component_overlap=4, architecture_overlap=4,
  full_text) and solozobov-verify-gated-completion-admission-control-2026 (component_overlap=4,
  architecture_overlap=4, full_text). 8 rows challenge H5 in total.
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
    None of these sources implement the full enumerated set: dissent, authority, and convergence
    as explicit, first-class selection dimensions are absent from every source read at this
    detail (recorded per-row in each strongest_difference field above).
assessment: >
  Retrieval that goes beyond plain semantic similarity — incorporating graph topology, temporal
  recency, reasoning lineage, and evidence provenance — is thoroughly established across
  2024-2026 agent-memory and agentic-runtime systems: Zep/Graphiti's traversal-plus-recency
  pipeline, EM-LLM's peer-reviewed episodic-segmentation retrieval, solozobov's explicit
  memory-tier context compiler, and log-is-the-agent's total provenance-chain lineage are all
  real, working instances of "select context using more than semantic similarity." If H5 were
  read as "context selection beyond naive similarity is uncommon," the evidence flatly falsifies
  that reading.
  Qualification: H5 as worded lists seven specific dimensions (state, lineage, evidence, dissent,
  authority, convergence, unresolved uncertainty), and no single source combines more than three
  or four of them. Dissent, authority, and convergence specifically as first-class retrieval
  inputs were not found in any source at this detail. The mechanism family (topology/lineage/
  recency-aware retrieval) is known; the specific seven-dimension enumeration D-System proposes
  is an untested combination, not a demonstrated one.
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
  (component_overlap=5, architecture_overlap=4) — the matrix's ceiling scores, tied. 10 rows
  challenge H7 in total.
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
assessment: >
  This is one of the most densely prior-arted hypotheses in the entire review. The claim that
  development artifacts are the downstream, traceable result of a persistent decision/
  requirement lineage is the organizing idea of at least five independent traditions found in
  this campaign: architecture-decision-record research (Jansen & Bosch 2005, formally extended
  by Zimmermann et al. 2009), model-based systems engineering's "digital thread" (2022), a
  granted US patent commercially operated as a digital-engineering platform (priority 2023,
  granted 2025), and a 2026 agentic-coding tool (Aporia) explicitly self-described as an
  application of 1991-era design-rationale notation. Ten of 34 matrix rows challenge H7, two at
  the matrix's ceiling overlap score.
  Qualification: most of these chains start at Decision or Requirement, not at Idea/Reasoning/
  Evidence as D-System's fuller lifecycle proposes, and none combines the chain with an
  append-only, typed-transition data model carrying the epistemic apparatus H1-H4 describe. But
  H7's literal claim is about the existence and traceability of the provenance chain itself, and
  on that claim the field's coverage — spanning three decades, multiple standards bodies, and a
  granted patent — is thorough.
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
  (component_overlap=5, architecture_overlap=4). 18 of the matrix's 34 rows challenge H9 — the
  single most heavily challenged hypothesis in the review.
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
assessment: >
  Bidirectional traceability — forward from intent to artifact, backward from artifact to
  rationale — is essentially the organizing promise of the requirements-traceability, design-
  rationale, digital-thread, and provenance-ontology literatures combined, and this campaign
  found it independently demonstrated across three decades and at least seven distinct
  technical traditions, several at production scale (Zep/Graphiti, LangGraph, Kumiho, the
  granted Istari patent). Eighteen of 34 matrix rows — over half — challenge this hypothesis,
  more than any other. By raw density of independent corroboration, this is the review's
  clearest case.
  Qualification: no single source combines all of D-System's proposed traceability directions
  (idea -> decision -> requirement -> specification -> plan -> phase -> implementation ->
  verification -> deployment -> runtime -> revised knowledge) into one continuous chain across
  that many stages simultaneously — most sources cover a contiguous subset. But the mechanism
  class itself, and multiple examples spanning most individual stage-to-stage links, are
  established beyond reasonable dispute.
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
  memtx-transactional-belief-commit-2026 (component_overlap=4, architecture_overlap=2,
  abstract_only). 4 rows challenge H10 in total; H10 has exactly one source with
  component_overlap above 2.
evidence:
  - >
    memtx, arXiv abstract: "retracting a belief triggers typed cascading repair of its derived
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
  burns-groth-agentic-ontological-notebook-memory-2026 (component_overlap=4,
  architecture_overlap=3, preprint_version). 2 rows challenge H11 in total — treated as a
  near-gap, not as covered, per the same thin-evidence caution applied to H4.
evidence:
  - >
    burns-groth, Sec.2: "Agent-generated notes and extraction failures serve as loss signals ...
    the agent records the deficit/error as a note in its memory, and subsequently treats it as a
    github issue to be addressed under normal coding agent practices. This closes the loop
    between curation experience and ontological design" — a named, working, demonstrated closed
    loop, with a public benchmark repo (github.com/sciknow-io/alhazen-skill-dismech).
  - >
    burns-groth, strongest_difference field: the feedback loop closes onto ONTOLOGY/SCHEMA
    refinement specifically, not onto the broader idea -> decision -> requirement -> code ->
    runtime lineage H7/H9/H10 target — a narrower loop than D-System's proposed "same knowledge
    structure that generated implementation intent."
  - >
    ibm-architectural-blueprint-autonomic-computing-whitepaper-2006 (component_overlap=1,
    secondary_coverage via Muller, O'Brien, Klein & Wood, CMU/SEI-2006-TN-006): the MAPE-K
    control loop — Monitor-Analyze-Plan-Execute over shared Knowledge — is the foundational,
    extremely widely cited ancestor of "close the loop from runtime observation back into a
    knowledge structure that also drives action," and is itself already named in D-System's own
    CLAUDE.md (§5, domain #69-70) as a search domain and vocabulary-translation target
    ("Runtime-to-knowledge loop -> runtime verification, feedback control, requirements
    monitoring, MAPE-K").
  - >
    ibm-autonomic-computing, strongest_difference field: MAPE-K's "Knowledge" is short-lived,
    single-control-loop operational state, not an append-only, provenance-bearing, cross-session
    history, and the architecture is explicitly oriented toward reducing human involvement,
    unlike D-System's collaborative human-agent framing.
assessment: >
  The general pattern H11 describes — runtime observation closing a loop back into the knowledge
  that drove the observed behavior — is one of the most foundational, most widely cited patterns
  in all of systems engineering: MAPE-K, named directly by D-System's own architecture notes as
  an ancestor to search for. A concrete, running, agentic instance of the loop closing onto
  memory specifically already exists (Burns & Groth, 2026): curation failures during runtime
  become notes, which become GitHub issues, which drive schema changes — evidence flowing back
  from operation into structure, demonstrated and benchmarked. Taken together, closing this loop
  at all is neither underexplored nor unprecedented.
  Qualification: neither found source demonstrates the specific loop H11 proposes. MAPE-K's
  knowledge is deliberately narrow, short-lived, and not human-legible or decision-relevant
  across sessions; Burns & Groth's loop closes specifically onto ontology/schema refinement, not
  onto the decisions and requirements that produced the observed code in the first place — the
  "same knowledge structure that generated implementation intent" is not what either source
  updates. With only two challengers, one purely conceptual/foundational and one real but
  narrowly scoped, and no deep search in this campaign having targeted H11 specifically the way
  H4's Pass 3 collision search did, this is thin evidence in both directions: too little to
  claim prior art defeats it, too little to claim it survives.
status: INSUFFICIENT_EVIDENCE
```

---

## Summary table

| Hyp. | Status | Strongest challenger (source_id) | Challenger count |
|---|---|---|---|
| H1 | KNOWN_COMPONENT_NEW_INTEGRATION | eywa-provenance-grounded-memory-joshi-2026 | 2 |
| H2 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied) | 13 |
| H3 | KNOWN_COMPONENT_NEW_INTEGRATION | log-is-the-agent-event-sourced-reactive-graphs-2026 / omniscientist-coevolving-ecosystem-human-ai-scientists-2026 (tied) | 9 |
| H4 | INSUFFICIENT_EVIDENCE | epistemic-sybil-resistance-bara-2026 | 1 |
| H5 | KNOWN_COMPONENT_NEW_INTEGRATION | log-is-the-agent-event-sourced-reactive-graphs-2026 / solozobov-verify-gated-completion-admission-control-2026 (tied) | 8 |
| H6 | KNOWN_COMPONENT_NEW_INTEGRATION | omniscientist-coevolving-ecosystem-human-ai-scientists-2026 | 3 |
| H7 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied) | 10 |
| H8 | LIKELY_ALREADY_KNOWN (review-instructions phrasing); KNOWN_COMPONENT_NEW_INTEGRATION (frozen-register phrasing) | langgraph-checkpoint-library-oss (review-instructions) / solozobov-verify-gated-completion-admission-control-2026 (frozen-register, assembly half only) | 4 |
| H9 | LIKELY_ALREADY_KNOWN | graph-native-cognitive-memory-belief-revision-semantics-2026 / jansen-bosch-architecture-as-decisions-wicsa-2005 (tied) | 18 |
| H10 | KNOWN_COMPONENT_NEW_INTEGRATION | memtx-transactional-belief-commit-2026 | 4 |
| H11 | INSUFFICIENT_EVIDENCE | burns-groth-agentic-ontological-notebook-memory-2026 | 2 |

No hypothesis reaches `POTENTIALLY_DISTINCT` on this pass. Per the methodology
(`research/literature-review/CLAUDE.md`, §14 and §19): "If nothing remains, say so. That is a
successful research result." Every gap identified above is a gap in what any single found
system's *scope* combines (mixed human-agent + graph topology for H4; ontology-refinement scope
vs. full development lineage for H11; cross-lifecycle span for H6/H10; knowledge-bearing
consolidation for H8's frozen phrasing) — not a gap in whether the field knows how to build the
underlying mechanisms. That distinction is exactly what separates `KNOWN_COMPONENT_NEW_
INTEGRATION` and `INSUFFICIENT_EVIDENCE` from `POTENTIALLY_DISTINCT` in this review's vocabulary.
