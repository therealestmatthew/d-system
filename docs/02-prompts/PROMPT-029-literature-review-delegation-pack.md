---
schema_version: 1
id: doc-prompt-literature-review-delegation-pack
code: PROMPT-029
title: Literature-review delegation pack — every prompt the campaign's execution sessions dispatch verbatim
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
depends_on:
- doc-lit-campaign
- doc-research-protocol
---

# Literature-review delegation pack

Every prompt the adversarial literature-review campaign dispatches, pre-crafted per
[GOV-009](../08-governance/GOV-009-research-protocol.md): **nothing is authored mid-campaign —
if this document does not contain it, the execution session does not send it.** A missing
prompt is a blocking finding for the owner, never something to improvise.

Dispatch rules:

- Sections are dispatched **verbatim, one at a time** (selective injection) — never the whole
  pack, never the whole domain matrix. Each dispatch is assembled from the shared blocks below
  plus the section's own payload:
  - **`S` search dispatch** = Block C + Block S + the section.
  - **`X` Pass 1 extraction dispatch** = Block C + Block X + the section.
  - **`X` deep-extraction dispatch (LIT-04, LIT-05)** = Block C + Block D + the section.
  - **`C` close-out and synthesis-writing dispatches (LIT-03 C, LIT-06 X1/X2, LIT-07
    X1/X2/X3)** = Block C + the section.
  - **`R` review dispatch** = Block C + the section.
  - **`G` gate dispatch** = Block G + the section.
  - **`K` kickoff dispatches** are self-contained.
- **Models**: `K` and `G` run on **Haiku** (mechanical); `S`, `X`, `R`, `C` and `A` run on
  **Sonnet**. Opus is never pre-assigned; at most one documented escalation per campaign, and
  the session record names it. At most **two fix cycles** per work item; what survives them is
  reported, not looped on.
- **Branch model (owner ruling, 2026-09-12)**: one long-lived campaign branch,
  **`agent/lit-campaign`**. Every phase commits to it, so the ledger, inventory, matrix and
  deliverables are always present for the next kickoff. The owner integrates it into `dev`
  twice: at the pre-synthesis check-in and at close-out. No per-phase branches.
- **Every section is idempotent**: a re-dispatch is a resume. Output that already exists is
  verified against its contract and extended from the first missing item, never re-created.
- Where a section conflicts with the search-domain matrix (`PLAN-023.02`) or the evidence
  contract (`PLAN-023.03`) on data — domain lists, variants, schema fields — those documents
  win; the conflict is reported as a finding.

---

## Block C — common constraints (in every S, X, R and C dispatch)

> You are one worker in the adversarial D-System literature-review campaign. The campaign
> works to support **H0: D-System is primarily a recombination of known ideas**. Rules that
> bind you:
>
> - **Providers**: web search and free/open endpoints only — arXiv, Semantic Scholar,
>   OpenAlex, Crossref, GitHub, W3C and the like. No paid database access exists. A paywalled
>   source (ACM, IEEE, Springer, Elsevier) is assessed from its abstract, preprint or
>   authoritative secondary coverage, and the evidence row's `access_limitation` field records
>   that; never present such an assessment as a full-text read.
> - **Ledger**: every search you run appends one row to
>   `research/literature-review/00_search_ledger.csv` in the evidence contract's format
>   (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`),
>   with the `domain_id` it served. A search that logged nothing did not happen.
> - **Evidence**: generated summaries (including your own) are leads, never evidence. Blogs
>   and product pages are leads. Every claim you record carries a locator into primary
>   material. Do not write "no prior work exists" — a failed search is a ledger row with its
>   queries.
> - **Thesis discipline**: record collisions; never rename a D-System concept, narrow a
>   hypothesis, or treat a terminology difference as a mechanism difference. Architecture is
>   revised only in the synthesis phase, by other dispatches.
> - **Frozen inputs**: never modify `research/pre-literature-baseline.md`,
>   `research/pre-literature-hypotheses.yaml`, `research/adversarial-codebase-review/`,
>   `research/evidence/`, `research/architecture/`, the glossaries, or anything under
>   `research/sources/`. Read the methodology at `research/literature-review/CLAUDE.md` (never
>   a root-level copy).
> - Never edit `AGENTS.md` or `CLAUDE.md`; never touch a peer's backlog claim; never write a
>   confidential identifier into a tracked file. Work on the campaign branch
>   `agent/lit-campaign` and commit your output there before any review of it.

## Block S — search procedure (in every S dispatch, after Block C)

> Your section lists domains, each with an id (`D01`–`D72` or a hypothesis id), mandated
> minimum terminology variants, and one or more pre-crafted collision queries. For **each**
> domain:
>
> 1. Run strategy **Phase A** — vocabulary discovery: surveys, standards, canonical models,
>    major taxonomies, historically important papers. Extend the variant list with the
>    field's own terminology as you find it, and log the extensions (they become part of the
>    domain's variant set for later passes).
> 2. Run strategy **Phase D** — system search across arXiv, Semantic Scholar, OpenAlex,
>    Crossref, GitHub, W3C and relevant lab/industrial pages.
> 3. Run **every pre-crafted collision query** listed for the domain, verbatim, plus any
>    sharper variant your Phase A vocabulary suggests.
> 4. Coverage floor: at least **two distinct-query searches per domain**, and **every
>    mandated minimum variant must appear in at least one logged query for its domain** —
>    the phase gate measures both from the ledger.
>
> One ledger row per search, at the time it runs. Report which result identifiers you kept
> and why. Do **not** fill the source inventory — that is the paired extraction dispatch's
> job, from your ledger rows.

## Block X — Pass 1 extraction procedure (in every Pass 1 X dispatch, after Block C)

> Your section names the domain ids whose ledger rows you process. Read the ledger rows for
> those domains; for every kept result, add a `03_source_inventory.csv` row per the evidence
> contract: identity, type, domain ids, `found_by`, component and architecture pre-scores
> (0–5 triage, rubric in the contract), `collision_candidate`, dedup and status fields.
> Apply the search protocol's inclusion (§6) and exclusion (§7) criteria; excluded rows are
> marked with a reason, never deleted. Add draft terminology-map entries for your domains to
> `research/literature-review/01_terminology_map.md`: D-System term ↔ field term, with the
> source that establishes the field term. Commit.

## Block D — deep-extraction procedure (in every LIT-04/LIT-05 X dispatch, after Block C)

> Your section names the exact source ids to deep-read, in rank order. For each source:
>
> 1. Obtain the fullest legal access (open version, preprint, abstract; record
>    `access_limitation` honestly).
> 2. Fill **every** evidence-matrix field per the contract
>    (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`)
>    — `NOT_APPLICABLE` / `NOT_DETERMINABLE_FROM_ACCESS` where true, blank never. Compare
>    against **both** the conceptual architecture (`research/two_system_architecture.md`,
>    the glossaries) and the implemented architecture (the frozen adversarial codebase
>    review) when scoring overlap.
> 3. Run backward citation chaining (strategy Phase B): identify the mechanism's theoretical
>    ancestors; log each chaining search as a ledger row with `strategy_phase: B` and
>    **`subject_source_id` set to the source you are chaining from**; fill
>    `derivative_ancestor` — five papers inheriting one mechanism are one lineage plus four
>    derivatives.
> 4. Score both overlap scales and set `critical_collision` strictly per the contract's flag
>    rules; a `yes` sets `second_review: pending`.
>
> Absence claims require reading the source's scope; from `abstract_only` access, absence
> claims cap `interpretation_confidence` at `medium`. Commit after each source, so a
> truncated run resumes at the first missing row.

## Block G — gate procedure (in every G dispatch)

> You are a mechanical gate. Read **only the files your section names**, take every
> measurement it lists, and report real output — numbers, lists, exit codes — never
> assertions. Name every gate that fails and every item that fails it. Do not fix anything:
> fixes go back to the responsible section as a fix cycle (at most two per work item; what
> survives them is reported, not looped on). Always finish with:
> `uv run python -m src.governance` (exit code) and
> `uv run python tools/check_no_private_content.py` with all changes staged.

---

## LIT-01 — Pass 1a: knowledge representation, provenance and epistemics (phase-lit-01)

### LIT-01 K — kickoff (Haiku)

> Claim `phase-lit-01` per `AGENTS.md` (status `active`, your agent id, catalog `updated`
> bumped, validator green before the claim commit). Create the campaign branch
> `agent/lit-campaign` from current `dev` if it does not exist; otherwise continue on it —
> every campaign phase commits to this one branch (owner ruling, 2026-09-12). Then create,
> if they do not already exist:
> `research/literature-review/00_search_ledger.csv` and
> `research/literature-review/03_source_inventory.csv`, each with exactly the header row the
> evidence contract (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`)
> specifies, and `research/literature-review/01_terminology_map.md` containing only a title
> line and a "draft — Pass 1 in progress" marker. Commit. Item order for this phase:
> S1/X1 → S2/X2 → S3/X3 → S4/X4 → S5/X5 → S6/X6 → G. If any file already exists, verify its
> header against the contract and proceed without recreating it.

### LIT-01 S1 — search payload: graphs and provenance foundations (Sonnet; pair X1)

> Your domains (carried from `PLAN-023.02`, which wins on conflict):
>
> - **D01 Knowledge graphs** — variants: knowledge graph, ontology, RDF graph, property
>   graph, knowledge base construction, entity-relation model. Collision: `"knowledge graph"
>   epistemic status lifecycle state classification`.
> - **D02 Semantic Web** — variants: Semantic Web, RDF/OWL, linked data, SPARQL, named
>   graphs, reification. Collision: `"named graph" provenance belief statement-level
>   metadata`.
> - **D03 W3C PROV / provenance** — variants: W3C PROV, PROV-O, provenance ontology,
>   prov:Activity/Agent/Entity, derivation, attribution, delegation, epistemic provenance.
>   Collisions: `PROV-O reasoning lineage conflict resolution authority`; `"epistemic
>   provenance" knowledge graph`.

### LIT-01 X1 — extraction payload (Sonnet)

> Domains: D01–D03.

### LIT-01 S2 — search payload: temporal and append-only substrates (Sonnet; pair X2)

> Your domains:
>
> - **D04 Temporal knowledge graphs** — variants: temporal knowledge graph, TKG, time-aware
>   embedding, temporal fact, quadruple (s,p,o,t). Collision: `"temporal knowledge graph"
>   belief revision provenance`.
> - **D05 Bi-temporal systems** — variants: bi-temporal, valid time, transaction time,
>   temporal versioning, as-of query. Collision: `bitemporal knowledge base belief validity
>   transaction time`.
> - **D06 Event sourcing** — variants: event sourcing, append-only log, CQRS, event store,
>   projection, immutable log. Collision: `"event sourced" knowledge graph state transition
>   provenance`.
> - **D30 Temporal databases** — variants: temporal database, valid-time table, Allen
>   intervals, temporal query, history table. Collision: `temporal database belief state
>   supersession history`.
> - **D31 Event calculus** — variants: event calculus, fluent, situation calculus, narrative
>   reasoning, action effects. Collision: `event calculus knowledge state fluent provenance
>   reasoning history`.

### LIT-01 X2 — extraction payload (Sonnet)

> Domains: D04–D06, D30–D31.

### LIT-01 S3 — search payload: belief dynamics and nonmonotonic reasoning (Sonnet; pair X3)

> Your domains:
>
> - **D07 Belief revision / AGM** — variants: belief revision, AGM theory, belief
>   contraction, belief update, epistemic entrenchment, iterated revision. Collisions: `AGM
>   belief revision provenance implementation agent memory`; `"belief revision" provenance
>   knowledge graph`.
> - **D08 Truth-maintenance systems** — variants: truth maintenance system, TMS, ATMS, JTMS,
>   reason maintenance, dependency-directed backtracking, justification network. Collision:
>   `truth maintenance justification network assumption retraction impact`.
> - **D09 Epistemic logic** — variants: epistemic logic, knowledge operator, S5, common
>   knowledge, dynamic epistemic logic. Collision: `dynamic epistemic logic multi-agent
>   knowledge base implementation`.
> - **D10 Doxastic logic** — variants: doxastic logic, belief operator, KD45, belief base,
>   graded belief. Collision: `doxastic logic belief base software agent architecture`.
> - **D11 Defeasible reasoning** — variants: defeasible reasoning, non-monotonic logic,
>   default logic, defeaters, prima facie justification. Collision: `defeasible reasoning
>   knowledge base conflicting evidence provenance`.

### LIT-01 X3 — extraction payload (Sonnet)

> Domains: D07–D11.

### LIT-01 S4 — search payload: argumentation, truth discovery and trust (Sonnet; pair X4)

> Your domains:
>
> - **D12 Computational argumentation** — variants: argumentation framework, Dung semantics,
>   abstract argumentation, structured argumentation, ASPIC+, argument attack/support.
>   Collision: `argumentation framework source reliability evidence graph`.
> - **D13 Truth discovery** — variants: truth discovery, source reliability estimation,
>   fact-finding algorithms, conflicting claims resolution. Collision: `"truth discovery"
>   "source dependence" copying detection graph`.
> - **D14 Data fusion** — variants: data fusion, conflict resolution, source accuracy, copy
>   detection, dependence-aware fusion. Collision: `data fusion source dependence independent
>   confirmation discount`.
> - **D15 Subjective logic** — variants: subjective logic, opinion triangle, uncertainty
>   mass, trust fusion operators, Jøsang. Collision: `subjective logic provenance trust
>   fusion knowledge graph`.
> - **D16 Trust and reputation systems** — variants: trust model, reputation system, trust
>   propagation, web of trust, domain authority. Collision: `trust propagation domain
>   authority claim arbitration multi-agent`.
> - **D17 Multi-agent belief systems** — variants: multi-agent beliefs, BDI, belief base
>   merging, judgment aggregation, epistemic multi-agent systems. Collision: `multi-agent
>   belief merging conflicting sources provenance human agent`.
>
> These domains carry H3/H4 collision weight — additionally run the protocol's H4 collision
> set, logging each row with **`domain_id: H4`** (cross-domain hypothesis queries log the
> hypothesis id, and the Pass 3 gate counts them toward H4's coverage): `"provenance"
> "independent sources" knowledge graph confidence`; `"corroboration" provenance paths`;
> `"independent evidence" epistemic graph`; `"convergence" multi-agent belief provenance`.

### LIT-01 X4 — extraction payload (Sonnet)

> Domains: D12–D17, plus any `domain_id: H4` ledger rows from S4.

### LIT-01 S5 — search payload: scientific discourse and claim networks (Sonnet; pair X5)

> Your domains:
>
> - **D18 Scientific discourse representation** — variants: scientific discourse ontology,
>   SWAN, SALT, discourse elements, claim-evidence networks, hypothesis ontology. Collision:
>   `scientific claim evidence network provenance corroboration ontology`.
> - **D19 Nanopublications** — variants: nanopublication, assertion graph, provenance graph,
>   publication info graph, trusty URI. Collision: `nanopublication assertion provenance
>   independent corroboration`.
> - **D20 Micropublications** — variants: micropublication, claim network, evidence chain,
>   statement-level citation. Collision: `micropublications evidence chain claim support
>   falsification`.

### LIT-01 X5 — extraction payload (Sonnet)

> Domains: D18–D20.

### LIT-01 S6 — search payload: lineage, evidence graphs and evolution (Sonnet; pair X6)

> Your domains:
>
> - **D28 Data lineage** — variants: data lineage, dataflow provenance, lineage tracing,
>   impact of upstream change. Collision: `data lineage upstream change downstream impact
>   knowledge`.
> - **D29 Evidence graphs** — variants: evidence graph, evidence network, Bayesian evidence
>   combination, evidential reasoning. Collision: `evidence graph independent sources
>   confidence propagation`.
> - **D32 Ontology evolution** — variants: ontology evolution, ontology versioning, change
>   management, concept drift, schema evolution. Collision: `ontology evolution change
>   propagation dependent artifacts`.

### LIT-01 X6 — extraction payload (Sonnet)

> Domains: D28–D29, D32.

### LIT-01 G — phase gate (Haiku)

> Files: `research/literature-review/00_search_ledger.csv`,
> `research/literature-review/03_source_inventory.csv`. Measurements:
>
> 1. Per domain in {D01–D20, D28–D32}: count of ledger rows, count of distinct `query`
>    values, and mandated-variant coverage — every minimum variant listed in this phase's S
>    payloads appears in at least one logged query for its domain. **Gates: ≥ 2 rows with
>    distinct queries per domain; no uncovered mandated variant.** Name every domain and
>    variant that fails.
> 2. Count of inventory rows for those domains, split kept/excluded; count of excluded rows
>    missing an `exclusion_reason` (**gate: 0**).
> 3. Count of ledger rows whose `kept` names a source absent from the inventory (**gate: 0**).

*No R section: Pass 1 pre-scores are triage, no `CRITICAL_COLLISION` flag is final before the
evidence matrix exists, so second reviews are dispatched in LIT-06. No A section: no synthesis
here.*

---

## LIT-02 — Pass 1b: agent memory, decision intelligence, requirements and rationale (phase-lit-02)

### LIT-02 K — kickoff (Haiku)

> Claim `phase-lit-02` per `AGENTS.md` (as LIT-01 K). Continue on the campaign branch
> `agent/lit-campaign` — do not create a new branch. Verify the ledger and inventory exist
> from phase-lit-01; do not recreate them. Item order: S1/X1 → S2/X2 → S3/X3 → S4/X4 →
> S5/X5 → G.

### LIT-02 S1 — search payload: agent memory and retrieval (Sonnet; pair X1)

> Your domains:
>
> - **D21 Agent memory** — variants: agent memory, memory architecture, working/long-term
>   memory, memory consolidation, cognitive architecture SOAR/ACT-R. Collisions: `"agent
>   memory" provenance temporal belief update contradiction`; `"agent memory" provenance
>   temporal knowledge graph`.
> - **D22 Long-term memory for LLM agents** — variants: LLM agent memory, persistent memory,
>   memory stream, reflection, MemGPT-style paging, vector memory. Collision: `LLM agent
>   long-term memory belief revision provenance retrieval`.
> - **D23 Episodic memory** — variants: episodic memory, autobiographical memory, episode
>   segmentation, event boundaries, experience replay. Collision: `episodic memory agent
>   session boundary consolidation retrieval`.
> - **D24 RAG / Graph-RAG** — variants: retrieval-augmented generation, RAG, GraphRAG,
>   hybrid retrieval, context assembly, chunking. Collision: `GraphRAG provenance-aware
>   retrieval reasoning lineage context selection`.
>
> These carry H5's collision weight.

### LIT-02 X1 — extraction payload (Sonnet)

> Domains: D21–D24.

### LIT-02 S2 — search payload: human-AI knowledge and decision provenance (Sonnet; pair X2)

> Your domains:
>
> - **D25 Human-AI collective intelligence** — variants: human-AI collaboration, collective
>   intelligence, hybrid intelligence, human-in-the-loop knowledge curation. Collision:
>   `human-AI shared knowledge base co-evolution provenance authority`.
> - **D26 Decision provenance** — variants: decision provenance, decision trace, accountable
>   decisions, PROV for decisions. Collisions: `"decision provenance" architecture knowledge
>   graph downstream impact`; `"decision provenance" ontology`.
> - **D27 Decision intelligence** — variants: decision intelligence, decision modeling,
>   decision records, DMN, decision automation. Collision: `decision intelligence lineage
>   requirements implementation feedback`.
>
> H6's end-to-end collision weight starts here.

### LIT-02 X2 — extraction payload (Sonnet)

> Domains: D25–D27.

### LIT-02 S3 — search payload: requirements engineering and evolution (Sonnet; pair X3)

> Your domains:
>
> - **D33 Requirements engineering** — variants: requirements engineering, RE lifecycle,
>   elicitation, specification, validation, goal-oriented RE KAOS/i*. Collision:
>   `goal-oriented requirements knowledge evolution assumption revision`.
> - **D34 Requirements traceability** — variants: requirements traceability, RTM,
>   forward/backward traceability, trace links, pre/post-RS traceability. Collision:
>   `requirements traceability matrix reasoning evidence bidirectional runtime`.
> - **D35 Requirements provenance** — variants: requirements provenance, requirement origin,
>   rationale capture, stakeholder attribution. Collision: `requirements provenance origin
>   evidence decision lineage`.
> - **D36 Requirements evolution** — variants: requirements evolution, requirements change
>   management, volatility, change propagation. Collision: `requirements change propagation
>   downstream artifacts impact assessment`.
>
> H7/H9 collision weight.

### LIT-02 X3 — extraction payload (Sonnet)

> Domains: D33–D36.

### LIT-02 S4 — search payload: rationale capture traditions (Sonnet; pair X4)

> Your domains:
>
> - **D37 Design rationale** — variants: design rationale, DR capture, argumentation-based
>   design, rationale management systems. Collision: `design rationale capture retrieval
>   impact assumption change`.
> - **D38 Architecture rationale** — variants: architecture rationale, architectural
>   decision rationale, rationale documentation. Collisions: `architecture rationale
>   traceability code requirements runtime`; `"architecture rationale" requirements code
>   traceability`.
> - **D39 Architecture knowledge management** — variants: architecture knowledge management,
>   AKM, architectural knowledge vaporization, knowledge codification. Collision:
>   `architecture knowledge management decision evidence lineage tool`.
> - **D40 Architecture Decision Records** — variants: ADR, architecture decision record,
>   MADR, decision log, superseded decisions. Collision: `ADR supersession lineage automated
>   impact analysis`.
> - **D41 IBIS** — variants: IBIS, issue-based information systems, gIBIS, Compendium,
>   issue-position-argument. Collision: `IBIS issue position argument software traceability
>   implementation`.
> - **D42 QOC** — variants: QOC, questions options criteria, design space analysis.
>   Collision: `QOC design space analysis decision traceability`.

### LIT-02 X4 — extraction payload (Sonnet)

> Domains: D37–D42.

### LIT-02 S5 — search payload: traceability mechanics and impact (Sonnet; pair X5)

> Your domains:
>
> - **D43 Software traceability** — variants: software traceability, trace link,
>   traceability information model, end-to-end traceability. Collision: `software
>   traceability reasoning decisions tests runtime end-to-end`.
> - **D44 Trace-link recovery** — variants: trace link recovery, traceability recovery,
>   IR-based tracing, LLM trace recovery. Collision: `automated trace recovery rationale
>   evidence links code`.
> - **D45 Change impact analysis** — variants: change impact analysis, ripple effect,
>   dependency analysis, impact propagation, program slicing. Collisions: `"impact analysis"
>   assumption requirements code test propagation`; `"assumption" impact analysis
>   requirements code`.
>
> H10's collision weight.

### LIT-02 X5 — extraction payload (Sonnet)

> Domains: D43–D45.

### LIT-02 G — phase gate (Haiku)

> Files: `research/literature-review/00_search_ledger.csv`,
> `research/literature-review/03_source_inventory.csv`. Measurements over domains {D21–D27,
> D33–D45}:
>
> 1. Per-domain ledger row counts, distinct-query counts, and mandated-variant coverage from
>    this phase's S payloads. **Gates: ≥ 2 distinct-query rows per domain; no uncovered
>    mandated variant.**
> 2. Inventory rows for those domains, kept/excluded split; excluded rows missing an
>    `exclusion_reason` (**gate: 0**).
> 3. Ledger `kept` entries absent from the inventory (**gate: 0**).

*No R, no A (as stated under LIT-01 G).*

---

## LIT-03 — Pass 1c: digital thread, specification, agentic SE and runtime feedback; close Pass 1 (phase-lit-03)

### LIT-03 K — kickoff (Haiku)

> Claim `phase-lit-03` per `AGENTS.md` (as LIT-01 K). Continue on the campaign branch
> `agent/lit-campaign`. Verify ledger and inventory exist; do not recreate. Item order:
> S1/X1 → … → S7/X7 → close-out C → G.

### LIT-03 S1 — search payload: systems-engineering threads (Sonnet; pair X1)

> Your domains:
>
> - **D46 Model-based systems engineering** — variants: MBSE, SysML, model-centric
>   engineering, system model integration. Collision: `MBSE requirement design verification
>   runtime thread provenance`.
> - **D47 Digital thread** — variants: digital thread, digital continuity, authoritative
>   source of truth, lifecycle data integration. Collision: `"digital thread" requirements
>   design code test runtime evidence`.
> - **D48 Digital engineering** — variants: digital engineering, digital engineering
>   ecosystem, model-based acquisition. Collision: `digital engineering knowledge provenance
>   decision lifecycle`.
>
> H7 collision weight.

### LIT-03 X1 — extraction payload (Sonnet)

> Domains: D46–D48.

### LIT-03 S2 — search payload: specification-first development (Sonnet; pair X2)

> Your domains:
>
> - **D49 Specification-driven development** — variants: specification-driven development,
>   spec-first, contract-first, spec-as-source-of-truth. Collision: `specification driven
>   agent development lineage verification`.
> - **D50 Executable specifications** — variants: executable specification, living
>   documentation, specification by example, acceptance-test driven. Collision: `executable
>   specification traceability implementation verification loop`.
> - **D51 Formal specification** — variants: formal specification, formal methods, Z, TLA+,
>   Alloy, refinement. Collision: `formal specification refinement traceability
>   implementation evidence`.
> - **D52 Behavior-driven development** — variants: BDD, Gherkin, given-when-then, feature
>   files, scenario-based testing. Collision: `BDD scenarios requirements traceability
>   runtime verification`.

### LIT-03 X2 — extraction payload (Sonnet)

> Domains: D49–D52.

### LIT-03 S3 — search payload: software and build provenance (Sonnet; pair X3)

> Your domains:
>
> - **D53 Software provenance** — variants: software provenance, code provenance, SBOM,
>   supply-chain provenance, SLSA. Collision: `software provenance decision reasoning
>   artifact lineage`.
> - **D54 Build provenance** — variants: build provenance, reproducible builds, in-toto,
>   attestation, artifact signing. Collision: `build attestation lineage requirements
>   decision traceability`.
> - **D55 Artifact lineage** — variants: artifact lineage, artifact graph, derivation chain,
>   pipeline lineage. Collision: `artifact lineage idea decision requirement code test
>   chain`.

### LIT-03 X3 — extraction payload (Sonnet)

> Domains: D53–D55.

### LIT-03 S4 — search payload: agentic software engineering (Sonnet; pair X4)

> Your domains:
>
> - **D56 Agentic software engineering** — variants: agentic software engineering, AI
>   software agents, autonomous coding, SWE agents, agent-driven development. Collision:
>   `agentic software engineering knowledge provenance phase context`.
> - **D57 Coding-agent memory** — variants: coding agent memory, repository memory, project
>   memory, codebase knowledge persistence. Collisions: `coding agent persistent memory
>   session knowledge provenance`; `"agent memory" coding "session" persistent`.
> - **D58 Cross-session coding agents** — variants: cross-session agent, session
>   persistence, context carryover, resumable agents. Collision: `"cross-session" coding
>   agent context carryover memory architecture`.
> - **D59 Agent handoff** — variants: agent handoff, task handoff, context transfer,
>   delegation protocol, baton passing. Collision: `agent handoff context package lineage
>   evidence transfer`.
> - **D60 Agent checkpointing** — variants: agent checkpointing, state snapshot, resumption,
>   recovery point, workflow checkpoint. Collision: `agent checkpoint resume context state
>   provenance`.
>
> H8's collision weight concentrates here.

### LIT-03 X4 — extraction payload (Sonnet)

> Domains: D56–D60.

### LIT-03 S5 — search payload: planning and execution monitoring (Sonnet; pair X5)

> Your domains:
>
> - **D61 Hierarchical task networks** — variants: HTN, hierarchical task network, task
>   decomposition, method decomposition. Collision: `HTN task decomposition context boundary
>   execution memory`.
> - **D62 AI planning** — variants: AI planning, PDDL, plan representation, plan execution,
>   replanning. Collision: `AI planning execution monitoring knowledge update replanning`.
> - **D63 Execution monitoring** — variants: execution monitoring, plan monitoring,
>   discrepancy detection, expectation monitoring. Collision: `plan execution monitoring
>   outcome knowledge revision`.

### LIT-03 X5 — extraction payload (Sonnet)

> Domains: D61–D63.

### LIT-03 S6 — search payload: verification and runtime evidence (Sonnet; pair X6)

> Your domains:
>
> - **D64 Verification and validation** — variants: V&V, verification and validation, test
>   evidence, assurance case, safety case. Collision: `assurance case evidence requirements
>   claims argumentation`.
> - **D65 Runtime verification** — variants: runtime verification, monitor synthesis,
>   temporal-logic monitoring, trace checking. Collision: `"runtime verification"
>   requirements feedback knowledge base update`.
> - **D66 Requirements monitoring** — variants: requirements monitoring, requirements at
>   runtime, awareness requirements, requirement reflection. Collision: `requirements
>   monitoring runtime evidence requirement revision loop`.
> - **D67 Observability-driven development** — variants: observability-driven development,
>   telemetry-informed development, production feedback. Collision: `observability telemetry
>   development decision feedback knowledge`.
>
> H11 collision weight.

### LIT-03 X6 — extraction payload (Sonnet)

> Domains: D64–D67.

### LIT-03 S7 — search payload: adaptive loops and DevOps traceability (Sonnet; pair X7)

> Your domains:
>
> - **D68 Self-adaptive systems** — variants: self-adaptive systems, adaptation logic,
>   managed/managing system, models@runtime. Collision: `self-adaptive system knowledge
>   model runtime evidence adaptation`.
> - **D69 MAPE-K** — variants: MAPE-K, monitor-analyze-plan-execute, knowledge base loop,
>   autonomic manager. Collision: `MAPE-K knowledge base development lifecycle integration`.
> - **D70 Autonomic computing** — variants: autonomic computing, self-management,
>   self-configuration, self-healing. Collision: `autonomic computing knowledge provenance
>   policy evolution`.
> - **D71 Continuous requirements engineering** — variants: continuous RE, just-in-time
>   requirements, agile RE, requirements in DevOps. Collision: `continuous requirements
>   engineering runtime feedback knowledge`.
> - **D72 DevOps traceability** — variants: DevOps traceability, CI/CD traceability,
>   deployment traceability, release evidence. Collision: `DevOps traceability commit
>   requirement deployment runtime evidence`.

### LIT-03 X7 — extraction payload (Sonnet)

> Domains: D68–D72.

### LIT-03 C — Pass 1 close-out (Sonnet)

> Using only the ledger, the inventory and the terminology-map draft:
>
> 1. Finalize `research/literature-review/01_terminology_map.md`: every D-System term from
>    the methodology's §6 table mapped to established terminology found in Pass 1, plus any
>    further D-System terms the sweeps surfaced field names for. Terminology novelty is not
>    mechanism novelty — say which field owns each term.
> 2. Write `research/literature-review/02_domain_map.md`: one entry per domain D01–D72 —
>    what the tradition is, its canonical sources from the inventory, and its relevance to
>    the hypotheses (which of H1–H11 it bears on). Include the **top-20 collision candidate
>    list**: the inventory's `collision_candidate: yes` rows ranked by pre-scores, with a
>    one-line reason each.
> 3. Mark the ranked top rows `deep_read` candidates in the inventory (status stays
>    `candidate` until LIT-04 actually reads them). Commit.

### LIT-03 G — phase gate (Haiku)

> Files: the ledger, the inventory, `01_terminology_map.md`, `02_domain_map.md`.
> Measurements over **all 72 domains**:
>
> 1. Per-domain ledger row counts, distinct-query counts, and mandated-variant coverage
>    (variants from all three Pass 1 phases' S payloads). **Gates: ≥ 2 distinct-query rows
>    for every one of D01–D72; no uncovered mandated variant.**
> 2. Total kept inventory rows (**gate: ≥ 75 across all domains**, the protocol's Pass 1
>    target).
> 3. `01_terminology_map.md` and `02_domain_map.md` exist; the domain map has all 72 entries
>    and a ranked top-20 list.
> 4. Inventory integrity gates as in LIT-01 G items 2–3.

*No R, no A.*

---

## LIT-04 — Pass 2a: deep-read the top collision candidates (phase-lit-04)

### LIT-04 K — kickoff (Haiku)

> Claim `phase-lit-04` per `AGENTS.md`. Continue on the campaign branch
> `agent/lit-campaign`. Create `research/literature-review/04_evidence_matrix.csv` with
> exactly the evidence contract's header (44 fields) if it does not exist. Item order:
> X1 → X2 → X3 → G. Split the top-20 list from `02_domain_map.md` into three consecutive
> batches in rank order (7/7/6) and write the exact source ids into each X dispatch's
> fill-in slot before dispatching it.

### LIT-04 X1 / X2 / X3 — deep-extraction payloads (Sonnet; dispatched separately)

> Deep-read each source in your batch per the procedure block, in the order given.
>
> *(Dispatcher: fill in — batch ids, in rank order: `____`.)*

### LIT-04 G — phase gate (Haiku)

> Files: the evidence matrix, the ledger. Measurements:
>
> 1. A matrix row exists for every batch id the K dispatch assigned (**gate: all present**).
> 2. Blank required fields across this phase's rows (**gate: 0**).
> 3. Rows with `critical_collision: yes` lacking `second_review: pending` (**gate: 0**).
> 4. Deep-read sources with no `strategy_phase: B` ledger row carrying their id in
>    `subject_source_id` (**gate: 0**).

*R deferred to LIT-06 (flags set here are reviewed there). No A.*

---

## LIT-05 — Pass 2b: foundational works, forward chaining, complete the matrix (phase-lit-05)

### LIT-05 K — kickoff (Haiku)

> Claim `phase-lit-05` per `AGENTS.md`. Continue on the campaign branch
> `agent/lit-campaign`. Verify the evidence matrix exists with LIT-04's rows. Item order:
> S1 → X1 → X2 → G. Name the exact source ids for X1 and X2 (from LIT-04's
> backward-chaining ancestors and S1's forward finds, in rank order) in each dispatch's
> fill-in slot before dispatching it.

### LIT-05 S1 — forward chaining on the strongest collisions (Sonnet)

> For each evidence-matrix row with either overlap score ≥ 3: run strategy Phase C (forward
> chaining) — extensions, critiques, replications, implementations, newer systems using the
> same mechanism — via citation indices (Semantic Scholar, OpenAlex). One ledger row per
> chaining search with `strategy_phase: C`, **`subject_source_id` set to the row's source
> id**, and the `chain_decision` recorded. Report new sources worth deep reading, with a
> one-line reason each; add them to the inventory. (Block S's per-domain coverage floors do
> not apply to this dispatch; it is chaining, not domain sweeping.)

### LIT-05 X1 / X2 — deep-extraction payloads (Sonnet; dispatched separately)

> Deep-read each source in your batch per the procedure block, in the order given, until the
> matrix holds **20–30 deeply compared sources overall**.
>
> *(Dispatcher: fill in — batch ids, in rank order: `____`.)*

### LIT-05 G — phase gate (Haiku)

> Files: the evidence matrix, the ledger. Measurements:
>
> 1. Total matrix rows (**gate: 20–30**, the methodology's stop condition).
> 2. Blank required fields (**gate: 0**).
> 3. Every row with either overlap score ≥ 3 has both a `strategy_phase: B` and a
>    `strategy_phase: C` ledger row with its id in `subject_source_id` (**gate: 0
>    missing**).
> 4. Distribution of `hypotheses_challenged` across H1–H11 — name every hypothesis with
>    **zero** challengers so LIT-06 knows where its collision searches must dig.
> 5. `derivative_ancestor` filled on every row (**gate: 0 blank**).

*R deferred to LIT-06. No A.*

---

## LIT-06 — Pass 3: adversarial hypothesis testing and collision second reviews (phase-lit-06)

### LIT-06 K — kickoff (Haiku)

> Claim `phase-lit-06` per `AGENTS.md`. Continue on the campaign branch
> `agent/lit-campaign`. Item order: S1 → X1 → R (one dispatch per critical collision, to
> agents that produced neither the collision's matrix row nor 05/06) → X2 → G.

### LIT-06 S1 — per-hypothesis collision search (Sonnet)

> For each hypothesis H1–H11 (register text and falsification criterion in the scope record,
> `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md`): run the
> search-domain matrix's pre-crafted collision queries for the domains bearing on it, plus
> gap-driven variants for any hypothesis LIT-05's gate reported with zero challengers.
> Construct queries specifically intended to find systems that already do what the
> hypothesis claims — you are trying to support H0, not defend the hypothesis. Ledger rows
> use the hypothesis id (`H1`–`H11`) as `domain_id`. Deep-extract any genuinely new strong
> candidate into the matrix (full contract row). (Block S's per-domain coverage floors apply
> per hypothesis here: at least two distinct-query rows per hypothesis id.)

### LIT-06 X1 — hypothesis tests (Sonnet)

> Write `research/literature-review/06_hypothesis_tests.md`: for each of H1–H11 the
> methodology's block —
>
> ```yaml
> hypothesis:
> strongest_challenger:
> evidence:
> assessment:
> status:
> ```
>
> — where `strongest_challenger` cites evidence-matrix rows, `evidence` carries locators,
> `assessment` articulates the **best argument that D-System is not distinct** before any
> counter-argument, and `status` uses only: `LIKELY_ALREADY_KNOWN`,
> `KNOWN_COMPONENT_NEW_INTEGRATION`, `POTENTIALLY_DISTINCT`, `INSUFFICIENT_EVIDENCE`
> (`NOVEL` is not available to this review). Where the frozen register's phrasing
> (`research/pre-literature-hypotheses.yaml`) differs materially (the scope record lists the
> differences — H1, H4, H8, H10), state which phrasing the verdict addresses. Also draft
> `research/literature-review/05_critical_collisions.md`: one section per
> `critical_collision: yes` row — the overlap analysis, what it would falsify, and
> `second_review: pending`. Commit.

### LIT-06 R — independent second review (Sonnet; one dispatch per critical collision; the owner-ratified staffing: pack-supplied prompt on a general-purpose agent, no committed charter)

> You are an independent reviewer in an adversarial literature review. You receive exactly
> two inputs and must not seek the first assessor's reasoning: (1) the source named below;
> (2) its evidence-matrix row (all fields, from
> `research/literature-review/04_evidence_matrix.csv`). **Do not open
> `research/literature-review/05_critical_collisions.md` or
> `research/literature-review/06_hypothesis_tests.md`** — they contain the first
> assessment's rationale, which must not reach you. The row's scores flag this source as a
> critical collision against the D-System hypothesis set (scope record:
> `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md`).
>
> Independently: inspect the source at the fullest legal access; verify the row's factual
> fields against it; re-derive both overlap scores from the evidence contract's rubric
> (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`);
> state whether the critical-collision flag stands, and whether the row overstates or
> understates the collision. **Your entire output is your report**: `confirmed` or
> `disputed: <what differs and the evidence locator for it>`, plus any factual corrections,
> returned to the dispatcher. You write no repository file — LIT-06 X2 alone folds review
> verdicts into the record. Disagreement is a result to record, not to negotiate away.
>
> *(Dispatcher: fill in — source citation and access path: `____`; matrix row: `____`.
> Dispatch one R per `critical_collision: yes` row, to an agent that produced neither the
> row nor 05/06; collect each R's report for X2.)*

### LIT-06 X2 — reconcile reviews (Sonnet; runs after all R reports are collected, and is the only writer of review outcomes)

> Inputs: the R reports the dispatcher collected. Serially, one collision at a time: write
> each verdict into the matrix row's `second_review` field and into a dated subsection of
> `05_critical_collisions.md`. A `disputed` outcome is recorded with both positions visible;
> apply at most two fix cycles against factual errors, then report what stands. If any
> collision **falsifies scope** — a source that materially subsumes a hypothesis such that
> continuing the campaign as scoped makes no sense — that is a critical issue: it gets
> `GOV-009`'s dual adversarial review, and pauses the campaign for the owner only if it
> survives unresolved. Commit.

### LIT-06 G — phase gate (Haiku)

> Files: `06_hypothesis_tests.md`, `05_critical_collisions.md`, the matrix, the ledger.
> Measurements:
>
> 1. Every H1–H11 has a challenger block with a permitted status (**gate: 11 of 11**; per
>    the methodology, each hypothesis needs at least one serious challenger before
>    stopping).
> 2. Every `critical_collision: yes` row has `second_review` set to `confirmed` or
>    `disputed` (**gate: 0 pending**).
> 3. Ledger rows with a hypothesis id as `domain_id`, per hypothesis — counting rows from
>    any phase (LIT-01 S4's `H4` rows count toward H4) (**gate: ≥ 2 each**).
> 4. Duplicate rate in this phase's searches (share of `result_ids` already in the
>    inventory) — report the number as the saturation signal.
>
> **After this gate: the campaign stops for the owner's one check-in (ratified decision 3),
> which is also the first owner integration of `agent/lit-campaign` into `dev`. LIT-07 is
> not dispatched until the kick-off record carries the dated check-in entry LIT-07 K
> requires.**

*No A: 05/06 are evidence documents; the synthesis review runs in LIT-07.*

---

## LIT-07 — Pass 4: synthesis, adversarial synthesis review, validated bibliography (phase-lit-07)

### LIT-07 K — kickoff (Haiku)

> Confirm the pre-synthesis owner check-in has been held: the kick-off record must contain a
> dated entry of the form **`pre-synthesis check-in held: <date>, ruling: proceed`** — an
> entry absent at campaign start by construction, appended only when the owner holds the
> check-in. If the entry is missing, stop and report; do not dispatch further items. Then
> claim `phase-lit-07` per `AGENTS.md` and continue on the campaign branch
> `agent/lit-campaign` (the owner will have integrated it into `dev` at the check-in; rebase
> onto `dev` if the branches have diverged). Item order: X1 → X2 → X3 → A → G.

### LIT-07 X1 — the anti-novelty case, then survivors (Sonnet)

> Write, in this order:
>
> 1. `research/literature-review/07_anti_novelty_case.md` — the strongest coherent argument
>    that D-System requires no new mechanism: the methodology's §14 decomposition (Knowledge
>    Graph + PROV-O + Event Sourcing + Belief Revision + Argumentation + Truth Discovery +
>    Agent Memory + Design Rationale + Requirements Traceability + ADRs + Digital Thread +
>    Software Provenance + Observability + MAPE-K), each component backed by evidence-matrix
>    rows with locators. Then identify exactly what remains after that decomposition. If
>    nothing remains, say so — that is a successful research result.
> 2. `research/literature-review/08_surviving_distinctions.md` — only after 07, and only
>    mechanisms/integrations that survive it, each tied to its hypothesis status from 06.
>    Keep the methodology's three categories separate: already known / new integration of
>    known parts / possibly requiring new mechanism design.
>
> Every claim traces to a matrix row or a ledger-logged source; a claim that cannot be
> traced is removed, not softened. Commit after each file.

### LIT-07 X2 — implications, questions, experiments (Sonnet)

> Write: `research/literature-review/09_reuse_recommendations.md` (standards, ontologies,
> models and implementations D-System should inherit rather than recreate — each with the
> matrix row that establishes it); `research/literature-review/10_architecture_implications.md`
> (what the literature implies for the conceptual architecture and the implemented one —
> recorded implications only, no code, no edits outside `research/literature-review/`);
> `research/literature-review/11_open_research_questions.md` (questions prior art does not
> resolve); `research/literature-review/12_experiment_proposals.md` (experiments capable of
> distinguishing D-System mechanisms from simpler baselines, tied to hypotheses that ended
> `POTENTIALLY_DISTINCT` or `INSUFFICIENT_EVIDENCE`). Commit after each file.

### LIT-07 X3 — validated bibliography (Sonnet)

> Write `research/literature-review/13_validated_bibliography.md`: every source a synthesis
> claim rests on, plus every seed source from `research/sources/` that was promoted — each
> seed through the evidence contract's five steps with the outcome recorded per step; a seed
> that fails a step is listed with the failing step named. The historical seed ledger is not
> edited. Commit.

### LIT-07 A — adversarial synthesis review (Sonnet; a different agent from X1–X3)

> You are an adversarial reviewer. Inputs: `07_anti_novelty_case.md`,
> `08_surviving_distinctions.md`, `06_hypothesis_tests.md` and
> `04_evidence_matrix.csv` — not the authors' reasoning. Audit, assuming the synthesis is
> broken:
>
> - every surviving distinction in 08 against the strongest matrix rows — does a row already
>   defeat it? Is a "new integration" actually present in one source end-to-end?
> - every synthesis claim's locator — does the cited row/source actually support it?
> - derivative ancestry — does any "independent confirmation" share an ancestor?
> - status vocabulary — any verdict outside the permitted set, any "no prior work exists",
>   any `NOVEL`?
> - the three synthesis categories — are they collapsed anywhere?
>
> Report findings as a numbered list with severity (blocking / should-fix / observation).
> You change nothing.

### LIT-07 G — final gate: the campaign's stop conditions, measured (Haiku)

> Files: the ledger, the inventory, the matrix, the thirteen deliverables. Measurements,
> each stop-condition measured never asserted:
>
> 1. All 72 domains searched with ≥ 2 distinct-query ledger rows and full mandated-variant
>    coverage (per-domain counts; variants from the Pass 1 S payloads).
> 2. Strongest collisions (either overlap score ≥ 3) have `strategy_phase: B` and
>    `strategy_phase: C` ledger rows carrying their id in `subject_source_id` (count
>    missing: gate 0).
> 3. Every H1–H11 has ≥ 1 serious challenger with a permitted status in 06 (list).
> 4. Matrix rows 20–30, no blank required fields.
> 5. Saturation: duplicate rate of phase-lit-06's searches, compared against phase-lit-05's,
>    measured against the inventory — report the trend (rising duplicates = saturation
>    demonstrated).
> 6. Every critical collision `second_review` is `confirmed` or `disputed` (count pending:
>    gate 0).
> 7. All thirteen deliverables exist in `research/literature-review/`.
> 8. A-review blocking findings: every one is either addressed or recorded for the owner's
>    report (**gate: 0 unaddressed-and-unrecorded**; at most two fix cycles were available —
>    survivors are reported, not looped on, and a recorded survivor passes this gate).
>
> This closes the first formal review: a research memo, not a final novelty claim.

---

## Spend and close-out

Each phase's session record reports spend posture per `GOV-009`: searches run (ledger row
count), sources deep-read, fix cycles used, any Opus escalation (at most one per campaign,
documented), wall-clock against the seven-session runway (owner-accepted range six to eight).
Close-out is the second owner integration of `agent/lit-campaign` into `dev`. A campaign that
stops early stops at a phase boundary with resume state in the session record. No
descope-ladder rung (campaign plan, `PLAN-023`) is taken without the owner's explicit
direction; each rung's gate re-parameterization is stated alongside it there.
