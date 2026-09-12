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

- Sections are dispatched **verbatim, one at a time** (selective injection). Every `S`, `X`
  and `R` dispatch is the **common block below plus its own section** and nothing else — never
  the whole pack, never the whole domain matrix.
- **Models**: `K` and `G` run on **Haiku** (mechanical); `S`, `X`, `R` and `A` run on
  **Sonnet**. Opus is never pre-assigned; at most one documented escalation per campaign, and
  the session record names it. At most **two fix cycles** per work item; what survives them is
  reported, not looped on.
- **Every section is idempotent**: a re-dispatch is a resume. Output that already exists is
  verified against its contract and extended from the first missing item, never re-created.
- Where a section conflicts with the search-domain matrix (`PLAN-023.02`) or the evidence
  contract (`PLAN-023.03`) on data — domain lists, variants, schema fields — those documents
  win; the conflict is reported as a finding.

---

## Block C — common constraints (prepended verbatim to every S, X and R dispatch)

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
>   `research/literature-review/00_search_ledger.csv` in the evidence contract's format, with
>   the `domain_id` it served. A search that logged nothing did not happen.
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
>   confidential identifier into a tracked file. Commit your output before any review of it.

---

## LIT-01 — Pass 1a: knowledge representation, provenance and epistemics (phase-lit-01)

### LIT-01 K — kickoff (Haiku)

> Claim `phase-lit-01` per `AGENTS.md` (status `active`, your agent id, catalog `updated`
> bumped, validator green before the claim commit; work on branch `agent/phase-lit-01`). Then
> create, if they do not already exist:
> `research/literature-review/00_search_ledger.csv` and
> `research/literature-review/03_source_inventory.csv`, each with exactly the header row the
> evidence contract (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`)
> specifies, and `research/literature-review/01_terminology_map.md` containing only a title
> line and a "draft — Pass 1 in progress" marker. Commit. Item order for this phase:
> S1/X1 → S2/X2 → S3/X3 → S4/X4 → S5/X5 → S6/X6 → G. If any file already exists, verify its
> header against the contract and proceed without recreating it.

### LIT-01 S1 — search: graphs and provenance foundations (Sonnet; pair X1)

> Block C applies. Your domains, variants and starting collision queries (carried from
> `PLAN-023.02`, which wins on conflict):
>
> - **D01 Knowledge graphs**: knowledge graph, ontology, RDF graph, property graph, knowledge
>   base construction, entity-relation model. Collision: `"knowledge graph" epistemic status
>   lifecycle state classification`.
> - **D02 Semantic Web**: Semantic Web, RDF/OWL, linked data, SPARQL, named graphs,
>   reification. Collision: `"named graph" provenance belief statement-level metadata`.
> - **D03 W3C PROV / provenance**: W3C PROV, PROV-O, provenance ontology,
>   prov:Activity/Agent/Entity, derivation, attribution, delegation. Collision: `PROV-O
>   reasoning lineage conflict resolution authority`.
>
> For each domain run strategy Phase A (surveys, standards, canonical models, taxonomies,
> historically important papers — extend the variant list with what you find and log the
> extensions), Phase D (system search: arXiv, Semantic Scholar, OpenAlex, Crossref, GitHub,
> W3C), and the collision query above, at least two distinct variant queries per domain.
> Ledger row per search. Report the result identifiers you kept and why; do not fill the
> inventory — that is X1's job from your ledger rows.

### LIT-01 X1 — extraction (Sonnet)

> Block C applies. Read ledger rows `LIT-01-S*` for domains D01–D03. For every kept result,
> add a `03_source_inventory.csv` row per the evidence contract: identity, type, domain ids,
> `found_by`, component and architecture pre-scores (0–5 triage, rubric in the contract),
> `collision_candidate`, dedup and status fields. Apply the protocol's inclusion (§6) and
> exclusion (§7) criteria; excluded rows are marked with a reason, never deleted. Add draft
> terminology-map entries for D01–D03 to `01_terminology_map.md`: D-System term ↔ field term,
> with the source that establishes the field term. Commit.

### LIT-01 S2 — search: temporal and append-only substrates (Sonnet; pair X2)

> Block C applies. Domains: **D04 Temporal knowledge graphs** (temporal knowledge graph, TKG,
> time-aware embedding, temporal fact, quadruple (s,p,o,t); collision: `"temporal knowledge
> graph" belief revision provenance`); **D05 Bi-temporal systems** (bi-temporal, valid time,
> transaction time, temporal versioning, as-of query; collision: `bitemporal knowledge base
> belief validity transaction time`); **D06 Event sourcing** (event sourcing, append-only log,
> CQRS, event store, projection, immutable log; collision: `"event sourced" knowledge graph
> state transition provenance`); **D30 Temporal databases** (temporal database, valid-time
> table, Allen intervals, temporal query, history table; collision: `temporal database belief
> state supersession history`); **D31 Event calculus** (event calculus, fluent, situation
> calculus, narrative reasoning, action effects; collision: `event calculus knowledge state
> fluent provenance reasoning history`). Same procedure as S1.

### LIT-01 X2 — extraction (Sonnet)

> As X1, for ledger rows covering D04–D06, D30–D31.

### LIT-01 S3 — search: belief dynamics and nonmonotonic reasoning (Sonnet; pair X3)

> Block C applies. Domains: **D07 Belief revision / AGM** (belief revision, AGM theory, belief
> contraction, belief update, epistemic entrenchment, iterated revision; collision: `AGM
> belief revision provenance implementation agent memory`; also run the protocol's example
> `"belief revision" provenance knowledge graph`); **D08 Truth-maintenance systems** (truth
> maintenance system, TMS, ATMS, JTMS, reason maintenance, dependency-directed backtracking,
> justification network; collision: `truth maintenance justification network assumption
> retraction impact`); **D09 Epistemic logic** (epistemic logic, knowledge operator, S5,
> common knowledge, dynamic epistemic logic; collision: `dynamic epistemic logic multi-agent
> knowledge base implementation`); **D10 Doxastic logic** (doxastic logic, belief operator,
> KD45, belief base, graded belief; collision: `doxastic logic belief base software agent
> architecture`); **D11 Defeasible reasoning** (defeasible reasoning, non-monotonic logic,
> default logic, defeaters, prima facie justification; collision: `defeasible reasoning
> knowledge base conflicting evidence provenance`). Same procedure as S1.

### LIT-01 X3 — extraction (Sonnet)

> As X1, for ledger rows covering D07–D11.

### LIT-01 S4 — search: argumentation, truth discovery and trust (Sonnet; pair X4)

> Block C applies. Domains: **D12 Computational argumentation** (argumentation framework, Dung
> semantics, abstract argumentation, structured argumentation, ASPIC+, argument
> attack/support; collision: `argumentation framework source reliability evidence graph`);
> **D13 Truth discovery** (truth discovery, source reliability estimation, fact-finding
> algorithms, conflicting claims resolution; collision: `"truth discovery" "source
> dependence" copying detection graph`); **D14 Data fusion** (data fusion, conflict
> resolution, source accuracy, copy detection, dependence-aware fusion; collision: `data
> fusion source dependence independent confirmation discount`); **D15 Subjective logic**
> (subjective logic, opinion triangle, uncertainty mass, trust fusion operators, Jøsang;
> collision: `subjective logic provenance trust fusion knowledge graph`); **D16 Trust and
> reputation systems** (trust model, reputation system, trust propagation, web of trust,
> domain authority; collision: `trust propagation domain authority claim arbitration
> multi-agent`); **D17 Multi-agent belief systems** (multi-agent beliefs, BDI, belief base
> merging, judgment aggregation, epistemic multi-agent systems; collision: `multi-agent
> belief merging conflicting sources provenance human agent`). These domains carry H3/H4
> collision weight — also run the protocol's H4 examples: `"provenance" "independent sources"
> knowledge graph confidence`; `"corroboration" provenance paths`; `"independent evidence"
> epistemic graph`; `"convergence" multi-agent belief provenance`. Same procedure as S1.

### LIT-01 X4 — extraction (Sonnet)

> As X1, for ledger rows covering D12–D17.

### LIT-01 S5 — search: scientific discourse and claim networks (Sonnet; pair X5)

> Block C applies. Domains: **D18 Scientific discourse representation** (scientific discourse
> ontology, SWAN, SALT, discourse elements, claim-evidence networks, hypothesis ontology;
> collision: `scientific claim evidence network provenance corroboration ontology`); **D19
> Nanopublications** (nanopublication, assertion graph, provenance graph, publication info
> graph, trusty URI; collision: `nanopublication assertion provenance independent
> corroboration`); **D20 Micropublications** (micropublication, claim network, evidence
> chain, statement-level citation; collision: `micropublications evidence chain claim support
> falsification`). Same procedure as S1.

### LIT-01 X5 — extraction (Sonnet)

> As X1, for ledger rows covering D18–D20.

### LIT-01 S6 — search: lineage, evidence graphs and evolution (Sonnet; pair X6)

> Block C applies. Domains: **D28 Data lineage** (data lineage, dataflow provenance, lineage
> tracing, impact of upstream change; collision: `data lineage upstream change downstream
> impact knowledge`); **D29 Evidence graphs** (evidence graph, evidence network, Bayesian
> evidence combination, evidential reasoning; collision: `evidence graph independent sources
> confidence propagation`); **D32 Ontology evolution** (ontology evolution, ontology
> versioning, change management, concept drift, schema evolution; collision: `ontology
> evolution change propagation dependent artifacts`). Same procedure as S1.

### LIT-01 X6 — extraction (Sonnet)

> As X1, for ledger rows covering D28–D29, D32.

### LIT-01 G — phase gate (Haiku; measurements, never assertions)

> Read `research/literature-review/00_search_ledger.csv` and
> `research/literature-review/03_source_inventory.csv` — these two files, nothing else — and
> report with real output:
>
> 1. Per domain in {D01–D20, D28–D32}: count of ledger rows and count of distinct `query`
>    values. **Gate: ≥ 2 rows with distinct queries per domain.** Name any domain that fails.
> 2. Count of inventory rows for those domains, split kept/excluded; count of excluded rows
>    missing an `exclusion_reason` (**gate: 0**).
> 3. Count of ledger rows whose `kept` names a source absent from the inventory (**gate: 0**).
> 4. `uv run python -m src.governance` exit code, and
>    `uv run python tools/check_no_private_content.py` with all changes staged.
>
> Report failures as failures. Do not fix anything; fixes go back to the responsible S/X as a
> fix cycle (at most two).

*No R section: Pass 1 pre-scores are triage, no `CRITICAL_COLLISION` flag is final before the
evidence matrix exists, so second reviews are dispatched in LIT-06. No A section: no synthesis
here.*

---

## LIT-02 — Pass 1b: agent memory, decision intelligence, requirements and rationale (phase-lit-02)

### LIT-02 K — kickoff (Haiku)

> Claim `phase-lit-02` per `AGENTS.md` (as LIT-01 K, branch `agent/phase-lit-02`). Verify the
> ledger and inventory exist from phase-lit-01; do not recreate them. Item order:
> S1/X1 → S2/X2 → S3/X3 → S4/X4 → S5/X5 → G.

### LIT-02 S1 — search: agent memory and retrieval (Sonnet; pair X1)

> Block C applies. Domains: **D21 Agent memory** (agent memory, memory architecture,
> working/long-term memory, memory consolidation, cognitive architecture SOAR/ACT-R;
> collision: `"agent memory" provenance temporal belief update contradiction`; also the
> protocol's `"agent memory" provenance temporal knowledge graph`); **D22 Long-term memory
> for LLM agents** (LLM agent memory, persistent memory, memory stream, reflection,
> MemGPT-style paging, vector memory; collision: `LLM agent long-term memory belief revision
> provenance retrieval`); **D23 Episodic memory** (episodic memory, autobiographical memory,
> episode segmentation, event boundaries, experience replay; collision: `episodic memory
> agent session boundary consolidation retrieval`); **D24 RAG / Graph-RAG**
> (retrieval-augmented generation, RAG, GraphRAG, hybrid retrieval, context assembly,
> chunking; collision: `GraphRAG provenance-aware retrieval reasoning lineage context
> selection`). These carry H5's collision weight. Same procedure as LIT-01 S1.

### LIT-02 X1 — extraction (Sonnet)

> As LIT-01 X1, for ledger rows covering D21–D24; terminology-map entries for the same.

### LIT-02 S2 — search: human-AI knowledge and decision provenance (Sonnet; pair X2)

> Block C applies. Domains: **D25 Human-AI collective intelligence** (human-AI collaboration,
> collective intelligence, hybrid intelligence, human-in-the-loop knowledge curation;
> collision: `human-AI shared knowledge base co-evolution provenance authority`); **D26
> Decision provenance** (decision provenance, decision trace, accountable decisions, PROV for
> decisions; collision: `"decision provenance" architecture knowledge graph downstream
> impact`; also the protocol's `"decision provenance" ontology`); **D27 Decision
> intelligence** (decision intelligence, decision modeling, decision records, DMN, decision
> automation; collision: `decision intelligence lineage requirements implementation
> feedback`). H6's end-to-end collision weight starts here. Same procedure.

### LIT-02 X2 — extraction (Sonnet)

> As LIT-01 X1, for ledger rows covering D25–D27.

### LIT-02 S3 — search: requirements engineering and evolution (Sonnet; pair X3)

> Block C applies. Domains: **D33 Requirements engineering** (requirements engineering, RE
> lifecycle, elicitation, specification, validation, goal-oriented RE KAOS/i*; collision:
> `goal-oriented requirements knowledge evolution assumption revision`); **D34 Requirements
> traceability** (requirements traceability, RTM, forward/backward traceability, trace links,
> pre/post-RS traceability; collision: `requirements traceability matrix reasoning evidence
> bidirectional runtime`); **D35 Requirements provenance** (requirements provenance,
> requirement origin, rationale capture, stakeholder attribution; collision: `requirements
> provenance origin evidence decision lineage`); **D36 Requirements evolution** (requirements
> evolution, requirements change management, volatility, change propagation; collision:
> `requirements change propagation downstream artifacts impact assessment`). H7/H9 collision
> weight. Same procedure.

### LIT-02 X3 — extraction (Sonnet)

> As LIT-01 X1, for ledger rows covering D33–D36.

### LIT-02 S4 — search: rationale capture traditions (Sonnet; pair X4)

> Block C applies. Domains: **D37 Design rationale** (design rationale, DR capture,
> argumentation-based design, rationale management systems; collision: `design rationale
> capture retrieval impact assumption change`); **D38 Architecture rationale** (architecture
> rationale, architectural decision rationale, rationale documentation; collision:
> `architecture rationale traceability code requirements runtime`; also the methodology's
> `"architecture rationale" requirements code traceability`); **D39 Architecture knowledge
> management** (architecture knowledge management, AKM, architectural knowledge vaporization,
> knowledge codification; collision: `architecture knowledge management decision evidence
> lineage tool`); **D40 Architecture Decision Records** (ADR, architecture decision record,
> MADR, decision log, superseded decisions; collision: `ADR supersession lineage automated
> impact analysis`); **D41 IBIS** (IBIS, issue-based information systems, gIBIS, Compendium,
> issue-position-argument; collision: `IBIS issue position argument software traceability
> implementation`); **D42 QOC** (QOC, questions options criteria, design space analysis;
> collision: `QOC design space analysis decision traceability`). Same procedure.

### LIT-02 X4 — extraction (Sonnet)

> As LIT-01 X1, for ledger rows covering D37–D42.

### LIT-02 S5 — search: traceability mechanics and impact (Sonnet; pair X5)

> Block C applies. Domains: **D43 Software traceability** (software traceability, trace link,
> traceability information model, end-to-end traceability; collision: `software traceability
> reasoning decisions tests runtime end-to-end`); **D44 Trace-link recovery** (trace link
> recovery, traceability recovery, IR-based tracing, LLM trace recovery; collision:
> `automated trace recovery rationale evidence links code`); **D45 Change impact analysis**
> (change impact analysis, ripple effect, dependency analysis, impact propagation, program
> slicing; collision: `"impact analysis" assumption requirements code test propagation`; also
> the methodology's `"assumption" impact analysis requirements code`). H10's collision weight.
> Same procedure.

### LIT-02 X5 — extraction (Sonnet)

> As LIT-01 X1, for ledger rows covering D43–D45.

### LIT-02 G — phase gate (Haiku)

> As LIT-01 G, over domains {D21–D27, D33–D45}: per-domain ledger counts and distinct queries
> (**gate: ≥ 2 distinct-query rows per domain**), inventory integrity checks (gates: 0
> missing exclusion reasons, 0 kept-but-uninventoried), governance and staged private-content
> checks. Failures are results; fixes go back to the responsible S/X (at most two cycles).

*No R, no A (as LIT-01).*

---

## LIT-03 — Pass 1c: digital thread, specification, agentic SE and runtime feedback; close Pass 1 (phase-lit-03)

### LIT-03 K — kickoff (Haiku)

> Claim `phase-lit-03` per `AGENTS.md` (branch `agent/phase-lit-03`). Verify ledger and
> inventory exist; do not recreate. Item order: S1/X1 → … → S7/X7 → close-out C → G.

### LIT-03 S1 — search: systems-engineering threads (Sonnet; pair X1)

> Block C applies. Domains: **D46 Model-based systems engineering** (MBSE, SysML,
> model-centric engineering, system model integration; collision: `MBSE requirement design
> verification runtime thread provenance`); **D47 Digital thread** (digital thread, digital
> continuity, authoritative source of truth, lifecycle data integration; collision: `"digital
> thread" requirements design code test runtime evidence` — the methodology's own example);
> **D48 Digital engineering** (digital engineering, digital engineering ecosystem,
> model-based acquisition; collision: `digital engineering knowledge provenance decision
> lifecycle`). H7 collision weight. Same procedure as LIT-01 S1.

### LIT-03 X1 — extraction (Sonnet)

> As LIT-01 X1, for D46–D48.

### LIT-03 S2 — search: specification-first development (Sonnet; pair X2)

> Block C applies. Domains: **D49 Specification-driven development** (specification-driven
> development, spec-first, contract-first, spec-as-source-of-truth; collision: `specification
> driven agent development lineage verification`); **D50 Executable specifications**
> (executable specification, living documentation, specification by example,
> acceptance-test driven; collision: `executable specification traceability implementation
> verification loop`); **D51 Formal specification** (formal specification, formal methods, Z,
> TLA+, Alloy, refinement; collision: `formal specification refinement traceability
> implementation evidence`); **D52 Behavior-driven development** (BDD, Gherkin,
> given-when-then, feature files, scenario-based testing; collision: `BDD scenarios
> requirements traceability runtime verification`). Same procedure.

### LIT-03 X2 — extraction (Sonnet)

> As LIT-01 X1, for D49–D52.

### LIT-03 S3 — search: software and build provenance (Sonnet; pair X3)

> Block C applies. Domains: **D53 Software provenance** (software provenance, code
> provenance, SBOM, supply-chain provenance, SLSA; collision: `software provenance decision
> reasoning artifact lineage`); **D54 Build provenance** (build provenance, reproducible
> builds, in-toto, attestation, artifact signing; collision: `build attestation lineage
> requirements decision traceability`); **D55 Artifact lineage** (artifact lineage, artifact
> graph, derivation chain, pipeline lineage; collision: `artifact lineage idea decision
> requirement code test chain`). Same procedure.

### LIT-03 X3 — extraction (Sonnet)

> As LIT-01 X1, for D53–D55.

### LIT-03 S4 — search: agentic software engineering (Sonnet; pair X4)

> Block C applies. Domains: **D56 Agentic software engineering** (agentic software
> engineering, AI software agents, autonomous coding, SWE agents, agent-driven development;
> collision: `agentic software engineering knowledge provenance phase context`); **D57
> Coding-agent memory** (coding agent memory, repository memory, project memory, codebase
> knowledge persistence; collision: `coding agent persistent memory session knowledge
> provenance`; also the methodology's `"agent memory" coding "session" persistent`); **D58
> Cross-session coding agents** (cross-session agent, session persistence, context carryover,
> resumable agents; collision: `"cross-session" coding agent context carryover memory
> architecture`); **D59 Agent handoff** (agent handoff, task handoff, context transfer,
> delegation protocol, baton passing; collision: `agent handoff context package lineage
> evidence transfer`); **D60 Agent checkpointing** (agent checkpointing, state snapshot,
> resumption, recovery point, workflow checkpoint; collision: `agent checkpoint resume
> context state provenance`). H8's collision weight concentrates here. Same procedure.

### LIT-03 X4 — extraction (Sonnet)

> As LIT-01 X1, for D56–D60.

### LIT-03 S5 — search: planning and execution monitoring (Sonnet; pair X5)

> Block C applies. Domains: **D61 Hierarchical task networks** (HTN, hierarchical task
> network, task decomposition, method decomposition; collision: `HTN task decomposition
> context boundary execution memory`); **D62 AI planning** (AI planning, PDDL, plan
> representation, plan execution, replanning; collision: `AI planning execution monitoring
> knowledge update replanning`); **D63 Execution monitoring** (execution monitoring, plan
> monitoring, discrepancy detection, expectation monitoring; collision: `plan execution
> monitoring outcome knowledge revision`). Same procedure.

### LIT-03 X5 — extraction (Sonnet)

> As LIT-01 X1, for D61–D63.

### LIT-03 S6 — search: verification and runtime evidence (Sonnet; pair X6)

> Block C applies. Domains: **D64 Verification and validation** (V&V, verification and
> validation, test evidence, assurance case, safety case; collision: `assurance case evidence
> requirements claims argumentation`); **D65 Runtime verification** (runtime verification,
> monitor synthesis, temporal-logic monitoring, trace checking; collision: `"runtime
> verification" requirements feedback knowledge base update` — the methodology's example);
> **D66 Requirements monitoring** (requirements monitoring, requirements at runtime,
> awareness requirements, requirement reflection; collision: `requirements monitoring runtime
> evidence requirement revision loop`); **D67 Observability-driven development**
> (observability-driven development, telemetry-informed development, production feedback;
> collision: `observability telemetry development decision feedback knowledge`). H11
> collision weight. Same procedure.

### LIT-03 X6 — extraction (Sonnet)

> As LIT-01 X1, for D64–D67.

### LIT-03 S7 — search: adaptive loops and DevOps traceability (Sonnet; pair X7)

> Block C applies. Domains: **D68 Self-adaptive systems** (self-adaptive systems, adaptation
> logic, managed/managing system, models@runtime; collision: `self-adaptive system knowledge
> model runtime evidence adaptation`); **D69 MAPE-K** (MAPE-K, monitor-analyze-plan-execute,
> knowledge base loop, autonomic manager; collision: `MAPE-K knowledge base development
> lifecycle integration`); **D70 Autonomic computing** (autonomic computing, self-management,
> self-configuration, self-healing; collision: `autonomic computing knowledge provenance
> policy evolution`); **D71 Continuous requirements engineering** (continuous RE, just-in-time
> requirements, agile RE, requirements in DevOps; collision: `continuous requirements
> engineering runtime feedback knowledge`); **D72 DevOps traceability** (DevOps traceability,
> CI/CD traceability, deployment traceability, release evidence; collision: `DevOps
> traceability commit requirement deployment runtime evidence`). Same procedure.

### LIT-03 X7 — extraction (Sonnet)

> As LIT-01 X1, for D68–D72.

### LIT-03 C — Pass 1 close-out (Sonnet)

> Block C applies. Using only the ledger, the inventory and the terminology-map draft:
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

> As LIT-01 G, but over **all 72 domains**: per-domain ledger row counts and distinct-query
> counts (**gate: ≥ 2 distinct-query rows for every one of D01–D72**); total inventory row
> count (**gate: ≥ 75 kept candidates across all domains** per the protocol's Pass 1 target);
> `01_terminology_map.md` and `02_domain_map.md` exist and the domain map has all 72 entries
> and a ranked top-20 list; inventory integrity gates as before; governance and staged
> private-content checks. Real output; failures named.

*No R, no A.*

---

## LIT-04 — Pass 2a: deep-read the top collision candidates (phase-lit-04)

### LIT-04 K — kickoff (Haiku)

> Claim `phase-lit-04` per `AGENTS.md` (branch `agent/phase-lit-04`). Create
> `research/literature-review/04_evidence_matrix.csv` with exactly the evidence contract's
> header (43 fields) if it does not exist. Item order: X1 → X2 → X3 → G, splitting the top-20
> list into three consecutive batches in rank order.

### LIT-04 X1 / X2 / X3 — deep extraction batches (Sonnet; dispatched separately, same text)

> Block C applies. Your batch: the next unprocessed ranked collision candidates from
> `02_domain_map.md`'s top-20 list (batch of 5–7; K names the exact ids in the dispatch).
> For each source:
>
> 1. Obtain the fullest legal access (open version, preprint, abstract; record
>    `access_limitation` honestly).
> 2. Fill **every** evidence-matrix field per the contract — `NOT_APPLICABLE` /
>    `NOT_DETERMINABLE_FROM_ACCESS` where true, blank never. Compare against **both** the
>    conceptual architecture (`research/two_system_architecture.md`, the glossaries) and the
>    implemented architecture (the frozen adversarial codebase review) when scoring overlap.
> 3. Run backward citation chaining (strategy Phase B): identify the mechanism's theoretical
>    ancestors, log chain decisions in the ledger, and fill `derivative_ancestor` — five
>    papers inheriting one mechanism are one lineage plus four derivatives.
> 4. Score both overlap scales and set `critical_collision` strictly per the contract's flag
>    rules; a `yes` sets `second_review: pending`.
>
> Absence claims require reading the source's scope; from `abstract_only` access, absence
> claims cap `interpretation_confidence` at `medium`. Commit after each source, so a
> truncated run resumes at the first missing row.

### LIT-04 G — phase gate (Haiku)

> Read the evidence matrix and ledger; report with real output: matrix row count for this
> phase's batches (**gate: every batch id has a row**); count of blank required fields
> (**gate: 0**); count of rows with `critical_collision: yes` lacking `second_review:
> pending` (**gate: 0**); count of deep-read sources with no strategy-B ledger row
> (**gate: 0**); governance and staged private-content checks.

*R deferred to LIT-06 (flags set here are reviewed there). No A.*

---

## LIT-05 — Pass 2b: foundational works, forward chaining, complete the matrix (phase-lit-05)

### LIT-05 K — kickoff (Haiku)

> Claim `phase-lit-05` per `AGENTS.md` (branch `agent/phase-lit-05`). Verify the evidence
> matrix exists with LIT-04's rows. Item order: S1 → X1 → X2 → G.

### LIT-05 S1 — forward chaining on the strongest collisions (Sonnet)

> Block C applies. For each evidence-matrix row with either overlap score ≥ 3: run strategy
> Phase C (forward chaining) — extensions, critiques, replications, implementations, newer
> systems using the same mechanism — via citation indices (Semantic Scholar, OpenAlex).
> Ledger row per search with `chain_decision`. Report new sources worth deep reading, with a
> one-line reason each; add them to the inventory.

### LIT-05 X1 / X2 — deep extraction batches (Sonnet; same text, dispatched separately)

> Block C applies. Your batch (K names the ids): the foundational ancestors LIT-04's backward
> chaining surfaced, plus S1's strongest forward finds, in rank order, until the matrix holds
> **20–30 deeply compared sources overall**. Fill rows exactly as LIT-04 X1 (all 43 fields,
> chaining, scores, flags). Commit after each source.

### LIT-05 G — phase gate (Haiku)

> Read the matrix and ledger; report with real output: total matrix rows (**gate: 20–30,
> per the methodology's stop condition**); blank required fields (**gate: 0**); every row
> with overlap ≥ 3 has both a strategy-B and strategy-C ledger row (**gate: 0 missing**);
> distribution of `hypotheses_challenged` across H1–H11 — name every hypothesis with **zero**
> challengers so LIT-06 knows where its collision searches must dig; `derivative_ancestor`
> filled on every row (**gate: 0 blank**); governance and staged private-content checks.

*R deferred to LIT-06. No A.*

---

## LIT-06 — Pass 3: adversarial hypothesis testing and collision second reviews (phase-lit-06)

### LIT-06 K — kickoff (Haiku)

> Claim `phase-lit-06` per `AGENTS.md` (branch `agent/phase-lit-06`). Item order:
> S1 → X1 → R (one dispatch per critical collision) → X2 → G.

### LIT-06 S1 — per-hypothesis collision search (Sonnet)

> Block C applies. For each hypothesis H1–H11 (register text and falsification criterion in
> the scope record, `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md`):
> run the matrix's pre-crafted collision queries for the domains bearing on it, plus
> gap-driven variants for any hypothesis LIT-05's gate reported with zero challengers.
> Construct queries specifically intended to find systems that already do what the
> hypothesis claims — you are trying to support H0, not defend the hypothesis. Ledger rows
> use the hypothesis id as `domain_id`. Deep-extract any genuinely new strong candidate into
> the matrix (full contract row).

### LIT-06 X1 — hypothesis tests (Sonnet)

> Block C applies. Write `research/literature-review/06_hypothesis_tests.md`: for each of
> H1–H11 the methodology's block —
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
> `research/literature-review/04_evidence_matrix.csv`). The row's scores flag this source as
> a critical collision against the D-System hypothesis set (scope record:
> `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md`).
>
> Independently: inspect the source at the fullest legal access; verify the row's factual
> fields against it; re-derive both overlap scores from the contract's rubric
> (`PLAN-023.03`); state whether the critical-collision flag stands, and whether the row
> overstates or understates the collision. Output: `confirmed` or `disputed: <what differs
> and the evidence locator for it>`, plus any factual corrections, into the row's
> `second_review` field and a dated subsection of `05_critical_collisions.md`. You never
> receive, and must not request, the first assessment's rationale. Disagreement is a result
> to record, not to negotiate away.
>
> *(Dispatcher: fill in — source citation and access path: `____`; matrix row: `____`.
> Dispatch one R per `critical_collision: yes` row, to an agent that produced neither the
> row nor 05/06.)*

### LIT-06 X2 — reconcile reviews (Sonnet)

> Block C applies. Fold the R outcomes into `05_critical_collisions.md` and the matrix's
> `second_review` fields. A `disputed` outcome is recorded with both positions visible;
> apply at most two fix cycles against factual errors, then report what stands. If any
> collision **falsifies scope** — a source that materially subsumes a hypothesis such that
> continuing the campaign as scoped makes no sense — that is a critical issue: it gets
> `GOV-009`'s dual adversarial review, and pauses the campaign for the owner only if it
> survives unresolved. Commit.

### LIT-06 G — phase gate (Haiku)

> Read `06_hypothesis_tests.md`, `05_critical_collisions.md`, the matrix and the ledger;
> report with real output: every H1–H11 has a challenger block with a permitted status
> (**gate: 11 of 11**; per the methodology, each hypothesis needs at least one serious
> challenger before stopping); every `critical_collision: yes` row has `second_review` set
> to `confirmed` or `disputed` (**gate: 0 pending**); every H1–H11 has ledger rows with the
> hypothesis id as `domain_id` (**gate: ≥ 2 each**); duplicate rate in this phase's searches
> (share of `result_ids` already in the inventory) — report the number as the saturation
> signal; governance and staged private-content checks.
>
> **After this gate: the campaign stops for the owner's one check-in (ratified decision 3).
> LIT-07 is not dispatched until the owner has held it.**

*No A: 05/06 are evidence documents; the synthesis review runs in LIT-07.*

---

## LIT-07 — Pass 4: synthesis, adversarial synthesis review, validated bibliography (phase-lit-07)

### LIT-07 K — kickoff (Haiku)

> Confirm the pre-synthesis owner check-in has been held (the kick-off record carries the
> ruling; without it, stop — do not dispatch further items). Claim `phase-lit-07` per
> `AGENTS.md` (branch `agent/phase-lit-07`). Item order: X1 → X2 → X3 → A → G.

### LIT-07 X1 — the anti-novelty case, then survivors (Sonnet)

> Block C applies. Write, in this order:
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

> Block C applies. Write: `09_reuse_recommendations.md` (standards, ontologies, models and
> implementations D-System should inherit rather than recreate — each with the matrix row
> that establishes it); `10_architecture_implications.md` (what the literature implies for
> the conceptual architecture and the implemented one — recorded implications only, no code,
> no edits outside `research/literature-review/`); `11_open_research_questions.md`
> (questions prior art does not resolve); `12_experiment_proposals.md` (experiments capable
> of distinguishing D-System mechanisms from simpler baselines, tied to hypotheses that
> ended `POTENTIALLY_DISTINCT` or `INSUFFICIENT_EVIDENCE`). Commit after each file.

### LIT-07 X3 — validated bibliography (Sonnet)

> Block C applies. Write `research/literature-review/13_validated_bibliography.md`: every
> source a synthesis claim rests on, plus every seed source from `research/sources/` that
> was promoted — each seed through the contract's five steps with the outcome recorded per
> step; a seed that fails a step is listed with the failing step named. The historical seed
> ledger is not edited. Commit.

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

> Read the ledger, inventory, matrix and deliverables; report with real output, each
> stop-condition measured never asserted:
>
> 1. All 72 domains searched with ≥ 2 distinct-query ledger rows (per-domain counts).
> 2. Strongest collisions have strategy-B and strategy-C chain rows (count missing: gate 0).
> 3. Every H1–H11 has ≥ 1 serious challenger with a permitted status in 06 (list).
> 4. Matrix rows 20–30, no blank required fields.
> 5. Saturation: duplicate rate of the last two phases' searches against the inventory —
>    report the trend (rising duplicates = saturation demonstrated).
> 6. Every critical collision `second_review` is `confirmed` or `disputed` (count pending:
>    gate 0).
> 7. All thirteen deliverables exist in `research/literature-review/`.
> 8. A-review blocking findings: count outstanding (gate 0; at most two fix cycles were
>    available — survivors are reported to the owner, not looped on).
> 9. `uv run python -m src.governance` exit code; staged private-content check.
>
> This closes the first formal review: a research memo, not a final novelty claim.

---

## Spend and close-out

Each phase's session record reports spend posture per `GOV-009`: searches run (ledger row
count), sources deep-read, fix cycles used, any Opus escalation (at most one per campaign,
documented), wall-clock against the seven-session runway (owner-accepted range six to eight).
A campaign that stops early stops at a phase boundary with resume state in the session record.
No descope-ladder rung (campaign plan, `PLAN-023`) is taken without the owner's explicit
direction.
