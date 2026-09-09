# Knowledge Retrieval Architecture — Investigation Report

**Author:** Gemini (google/gemini-2.5-pro)
**Date:** 2026-09-08
**Scope:** Synthesis of ideas 000002, 000004, 000005, 000007, 000020, 000043, 000044, 000045 and
their relationship to PLAN-001 (agent memory system) and the `phase-mem-*` backlog line.
**Status:** Research deliverable. Nothing in this report is authorized for implementation on its own
authority. A human or agent in this repository decides afterward whether to promote any part of it
into a governed plan with backlog phases.

---

## 1. Summary

The recommended architecture is **DuckDB-only, local-first, and layered** — extending the project's
existing pattern (authoritative files → derived queryable store) rather than introducing new database
engines. Concretely:

1.  **A documentation metadata table in DuckDB**, projected from governed-document YAML front matter
    by an extension to `tools/rebuild_db.py`. This is the cheapest, most precedented piece and
    resolves the largest share of retrieval needs — including the "what does an agent consult first"
    problem from idea 000002 — by making `depends_on`, `systems`, `status`, `kind`, and
    cross-references queryable via SQL. This should be built first.

2.  **DuckDB VSS for semantic search**, using the existing VSS extension (HNSW indexes,
    `array_cosine_distance`) with embeddings generated locally by `nomic-embed-text-v2` via Ollama.
    This replaces PLAN-001's recommendation of `text-embedding-3-small` (an API-based provider that
    violates the local-only constraint) and adds a vector layer over documentation, memories, and
    session records — not just `brain/` entries. No separate vector database is needed.

3.  **DuckDB recursive CTEs (with `USING KEY`) for graph traversal in this repository**, replacing
    the proposed KuzuDB graph database. The document-relationship graph here (`depends_on` edges,
    `promoted_to` links, `systems` membership) is small, shallow, and fully representable in
    relational form. DuckDB's 2025–2026 recursive CTE optimizations make a separate graph engine
    unnecessary for this specific corpus. However, for larger repositories (1,000+ nodes), a
    dedicated embedded graph database is evaluated and recommended in §2.10.

4.  **A read-only MCP server for knowledge retrieval** (FastMCP, stdio transport), exposing the
    DuckDB-backed query layer to Claude Code, Gemini, and other MCP-capable assistants. This is the
    retrieval-over-MCP use case from idea 000020 — a contained, well-precedented pattern.

5.  **Coordination-over-MCP is not recommended.** The existing file-based locking system
    (`backlog.yaml` + `src/governance`) works, is tested, and is auditable. Replacing it with a live
    service is a materially larger change with no evidence that the current system is failing at a
    rate that justifies the risk.

6.  **A retrieval failure log** integrated into the MCP server and/or the governance CLI, so that
    `phase-mem-10`'s evidence gate can be satisfied and the deferred semantic-search phases
    (`phase-mem-15`–`19`) can be evaluated against real data.

**This report covers two distinct use cases and recommends treating them separately:**

-   **Knowledge retrieval for planning** (ideas 000002/000004/000020/000043/000044/000045): querying
    documentation, memories, decisions, and ideas to inform *what* to build and *why*. This is the
    primary scope, and the five phases above address it fully. A separate graph database is **not yet
    justified** for this use case at the current corpus scale (~200 nodes, ~300 edges); DuckDB
    recursive CTEs handle it. If the document graph grows past ~1,000 nodes with dense
    cross-referencing, or queries shift toward pattern matching, a graph DB should be re-evaluated.

-   **Code-structure analysis for agent development** (idea 000005 / GitNexus): querying call
    hierarchies, import graphs, and impact analysis to inform *how* agents write and modify code.
    This is a **separate concern** from knowledge retrieval — it is developer tooling, not planning
    infrastructure. GitNexus specifically cannot be adopted because its KuzuDB backend was acquired
    by Apple and archived in October 2025, but the category of tool is valuable and alternatives
    exist. §2.9 surveys the current landscape and recommends a path forward independent of this
    plan's phases.

---

## 2. Findings

### 2.1 Store topology

**Deep Dive Document:** [gemini-knowledge-retrieval-duckdb-architecture.md](./gemini-knowledge-retrieval-duckdb-architecture.md)

**Summary:** One DuckDB instance handles all knowledge-retrieval needs for this repository's scale. A separate graph database is not yet justified for the primary knowledge graph (~200 nodes), and DuckDB's capability ceiling (recursive CTEs with `USING KEY`) easily supports current requirements.

### 2.3 Documentation front matter as a first source

**Question:** Should the relational/structured half (projecting document front matter into DuckDB) be
built before any vector or graph layer?

**Finding:** Yes. This should be Phase 1 of any implementation, for three reasons:

1.  **It follows the existing precedent exactly.** `_data/` JSON → DuckDB via `rebuild_db.py` is the
    established pattern. Extending `rebuild_db.py` to also parse `docs/` front matter and populate
    a `documents` table is the same operation, using the same tooling, with the same rebuild/sync
    model. The marginal cost is a few dozen lines of Python and one new DDL table.

2.  **It resolves a meaningful fraction of retrieval needs on its own.** The questions agents most
    frequently need answered — "which documents touch this system?", "what plans depend on this
    requirement?", "what is the status of this phase's upstream dependencies?" — are all structured
    queries over front matter fields. Today these require grepping YAML by hand or reading
    `catalog.md` linearly. A `documents` table makes them one SQL query each.

3.  **It satisfies idea 000002's "what does an agent consult first" problem** by making the
    relationship between source types explicit and queryable. An agent can query for all documents
    with `kind: decision` touching `systems: [sys-retrieval]` rather than reading every ADR. The
    ordering/confidence problem becomes a SQL `ORDER BY` on `kind`, `status`, and `updated` —
    no embedding required.

**Proposed `documents` table:**

```sql
CREATE TABLE documents (
    code        VARCHAR PRIMARY KEY,    -- e.g., 'PLAN-001', 'ADR-003'
    id          VARCHAR NOT NULL,       -- e.g., 'doc-agent-memory'
    title       VARCHAR NOT NULL,
    kind        VARCHAR NOT NULL,       -- plan, decision, requirement, session, governance
    status      VARCHAR NOT NULL,       -- draft, approved, implemented, retired
    owner       VARCHAR,
    created     DATE NOT NULL,
    updated     DATE,
    systems     VARCHAR[],              -- from front matter
    depends_on  VARCHAR[],              -- from front matter
    file_path   VARCHAR NOT NULL        -- relative path to source .md file
);
```

**Companion junction tables for queryable graph traversal:**

```sql
CREATE TABLE document_systems (
    document_code   VARCHAR,
    system_id       VARCHAR,
    PRIMARY KEY (document_code, system_id)
);

CREATE TABLE document_dependencies (
    document_code       VARCHAR,
    depends_on_code     VARCHAR,
    PRIMARY KEY (document_code, depends_on_code)
);
```

**Conclusion:** Build this first. It is cheap, precedented, and resolves enough retrieval needs to
potentially defer or reduce the scope of the vector layer.

### 2.4 Embedding model

**Deep Dive Document:** [gemini-knowledge-retrieval-embeddings.md](./gemini-knowledge-retrieval-embeddings.md)

**Summary:** Recommends using `nomic-embed-text-v2` via Ollama for local-first embedding generation, replacing API-based recommendations from PLAN-001.

### 2.5 MCP server: what it's for and what it isn't

**Deep Dive Document:** [gemini-knowledge-retrieval-mcp-design.md](./gemini-knowledge-retrieval-mcp-design.md)

**Summary:** Recommends building a read-only retrieval MCP server (FastMCP, stdio transport) to expose the DuckDB query layer. Rejects "coordination-over-MCP" (replacing file-based locking with a live service) as unnecessary complexity.

### 2.6 Retrieval failure evidence gate

**Deep Dive Document:** [gemini-knowledge-retrieval-mcp-design.md](./gemini-knowledge-retrieval-mcp-design.md)

**Summary:** The evidence gate for semantic search is sound but needs a mechanism. Recommends logging every MCP query to `_data/retrieval_log.jsonl` so `phase-mem-10` can evaluate real retrieval failures before advancing to vector-based semantic search.

### 2.8 What NOT to build

Based on this investigation, the following should not be built **as part of the knowledge-retrieval
system:**

1.  **A separate graph database for the document/planning graph (not yet justified).** The document
    graph is currently too small (< 200 nodes, < 300 edges) and too shallow (max depth 4) to justify
    a separate engine for knowledge retrieval. DuckDB recursive CTEs with `USING KEY` handle this
    efficiently. Ideas 000044 (graph DB for documentation) is resolved by this finding for now —
    DuckDB is the graph engine for the planning/knowledge corpus. **Resumption trigger:** re-evaluate
    if the document graph exceeds ~1,000 nodes, or if queries requiring multi-hop pattern matching
    become common. LadybugDB (KuzuDB community fork) or ArcadeDB would be candidates at that point.

2.  **GitNexus for knowledge retrieval.** GitNexus is a *code-structure* tool, not a
    knowledge-retrieval tool; evaluating it on the knowledge-retrieval axis was a category error in
    the initial version of this report. Its KuzuDB dependency (archived October 2025) blocks
    adoption regardless of use case, but the *category* of code-structure MCP tool it represents is
    valuable for agent development and is evaluated separately in §2.9.

3.  **Coordination-over-MCP / the "Librarian as coordinator" from idea 000020.** The file-based
    coordination protocol works and has been tested under real concurrent-agent load. The pub/sub
    kill-switch and live backlog-claim mediation add complexity without demonstrated need.

4.  **Agentic RAG refinement (phase-mem-19) before evidence.** The existing gate is correct:
    agentic query decomposition and retries should not be built until semantic search exists and has
    been measured, and remaining failures justify a refinement loop. This is the most expensive piece
    of PLAN-001's pipeline and the one most likely to be unnecessary at this corpus scale.

5.  **An automated idea-triage agent (idea 000007) at this stage.** The investigation this report
    represents is exactly the kind of triage work 000007 describes, done by hand. At 45 ideas, the
    list is manageable. Automating triage is worth reconsidering when the idea count exceeds ~100
    and when the deterministic search layer exists (so the triage agent has something to query).
    The idea should remain open, not discarded — but it is not a prerequisite for the knowledge
    retrieval system.

6.  **Hosted vector databases or API-based embedding providers.** Per the local-only constraint:
    Pinecone, Weaviate, Qdrant Cloud, OpenAI embeddings, Google embeddings, and any other service
    that would send repository content off the local machine are ruled out. This is stated plainly
    rather than buried: these are often the faster path to production, but the confidentiality
    constraint makes them non-negotiable until `phase-priv-05` completes. See §3 for the full
    rejected-alternatives list.

### 2.9 Code-structure tooling for agent development (separate concern)

**Deep Dive Document:** [gemini-knowledge-retrieval-code-structure.md](./gemini-knowledge-retrieval-code-structure.md)

**Summary:** GitNexus cannot be adopted due to its deprecated KuzuDB backend. Code-structure MCP tools are a distinct, valuable category. Recommends trialing Codebase-Memory-MCP (Tree-sitter + SQLite) in a single agent session.

### 2.10 Graph database options for documentation knowledge graphs

**Deep Dive Document:** [gemini-knowledge-retrieval-graphdb-options.md](./gemini-knowledge-retrieval-graphdb-options.md)

**Summary:** Evaluates embedded graph DBs for larger multi-repo contexts (e.g. ~1,400+ nodes). Recommends LadybugDB as the closest successor to KuzuDB, or ArcadeDB for multi-model needs. FalkorDBLite and DuckPGQ are also compared.

## 3. Rejected alternatives

| Alternative | Reason for rejection |
|---|---|
| **KuzuDB** (embedded graph DB) | Acquired by Apple October 2025; project archived and deprecated. **LadybugDB** (community fork) is the recommended successor — see §2.10. KuzuDB itself should not be adopted in any repo due to the lack of security patches and updates. |
| **Neo4j** (server graph DB) | Server process, not embedded. Violates the local-only, no-server-dependency stack preference. Overkill for < 200 nodes. |
| **DuckPGQ** (SQL/PGQ extension) | Research-stage community extension with compatibility challenges against recent DuckDB versions. Standard recursive CTEs are adequate and stable. |
| **LanceDB** (vector DB) | Arrow-native and DuckDB-compatible, but adds a second storage engine when DuckDB VSS provides equivalent functionality for this scale. Worth revisiting only if DuckDB VSS proves inadequate at scale. |
| **ChromaDB** (vector DB) | Adds a separate process and storage layer. Good for prototyping but unnecessary when DuckDB VSS is available in-process. |
| **Qdrant** (vector DB) | Production-grade but overkill for hundreds of documents. PLAN-001 correctly notes: "Migrate to Qdrant if memory count exceeds 2,000." Currently at ~100. |
| **text-embedding-3-small** (OpenAI) | API-based — sends content off-machine. Violates the local-only constraint. Was PLAN-001's primary recommendation; that recommendation is revised. |
| **text-embedding-004** (Google) | Same: API-based, violates local-only constraint. |
| **GitNexus** (code-structure MCP) | Depends on deprecated KuzuDB backend (archived October 2025). The *concept* of code-structure MCP tooling is validated and valuable — GitNexus correctly identified the pattern. The tool itself cannot be adopted; alternatives (notably Codebase-Memory-MCP) are evaluated in §2.9. |
| **Coordination-over-MCP** | Replaces a working, tested, auditable file-based system with a live service. No evidence the current system is failing in ways the service would prevent. |

---

## 4. Proposed multi-phase plan

### Phase 1: Documentation metadata projection into DuckDB

**Delivers:** A `documents` table (plus `document_systems` and `document_dependencies` junction
tables) in DuckDB, populated by extending `tools/rebuild_db.py` to parse governed-document YAML
front matter. A retrieval query log (`_data/retrieval_log.jsonl`).

**Dependency:** None — can begin immediately.

**Ideas addressed:** 000043 (documentation front matter review and database) — directly implements.
000002 (prioritized search order) — makes source types, recency, and system membership queryable,
which is the prerequisite for defining an ordering.

**Existing backlog:** Extends `sys-projection` (adds new tables to the existing rebuild). Does not
supersede any `phase-mem-*` phase — those target `brain/` memories; this targets governed documents.

**Done when:**
-   `tools/rebuild_db.py` successfully parses all governed documents and populates the three new
    tables.
-   `SELECT * FROM documents WHERE 'sys-retrieval' = ANY(systems)` returns the expected documents.
-   A recursive CTE over `document_dependencies` returns the full dependency chain for a document
    with known depth-3 dependencies.
-   The retrieval log is being written by the existing `load_context.py` (even before the MCP server
    exists).

### Phase 2: Read-only MCP server for knowledge retrieval

**Delivers:** A FastMCP server (`tools/mcp_knowledge_server.py`) exposing structured and keyword
search over the `documents` and `memories` tables, plus dependency traversal. Stdio transport.
Configuration for Claude Code (`.mcp.json` or equivalent).

**Dependency:** Phase 1 (needs the `documents` table to query).

**Ideas addressed:** 000020 (MCP-mediated retrieval — the retrieval half only, not coordination).
000002 (retrieval ordering — the MCP server implements the prioritized search pipeline).
000040 (deterministic search algorithms — the MCP tools are the interface to those algorithms).

**Existing backlog:** Partially supersedes `phase-mem-07` (Librarian retrieval contract) by
providing the same capability (structured retrieval with method-used metadata) via MCP rather than
as a Python library. The contract defined in PLAN-001's Contract A (Caller ↔ Librarian) maps
directly to MCP tool definitions. The Librarian's "five-layer pipeline" from PLAN-001 is preserved
as a design principle but the first two layers (exact-ID + tag filter + keyword) are what this
phase implements; semantic and agentic layers come later.

**Done when:**
-   Claude Code (or another MCP client) can call `search_documents`, `search_memories`,
    `get_document`, and `traverse_dependencies` and receive formatted results.
-   The MCP server is read-only: no write tools exposed.
-   Every query is logged to the retrieval log.

### Phase 3: Embedding generation and semantic search

**Delivers:** `nomic-embed-text-v2` embeddings stored in DuckDB (VSS extension, HNSW index) for all
governed documents, brain memories, and ideas. A `search_semantic` tool added to the MCP server.
A `tools/refresh_embeddings.py` command for incremental re-embedding.

**Dependency:** Phase 1 + Phase 2 (needs the document and memory tables, and the MCP server to
expose the semantic tool). Additionally gated by the existing `phase-mem-10` evidence requirement:
**this phase should only proceed if the retrieval log from Phases 1–2 demonstrates concrete cases
where deterministic search failed to return relevant results.** If deterministic search proves
sufficient, this phase is deferred — not cancelled, but genuinely contingent on evidence.

**Ideas addressed:** 000004 (vector databases, semantic + deterministic search). 000045 (vector
database tooling evaluation — this phase implements the conclusion: DuckDB VSS + Nomic).

**Existing backlog:** Supersedes `phase-mem-15` (choose embedding provider — decided: Nomic local),
`phase-mem-16` (embedding cache/invalidation — the content-hash design from PLAN-001 is preserved),
and `phase-mem-17` (build embeddings — implemented here). Extends `phase-mem-18` (semantic search
as retrieval fallback).

**PLAN-001 revisions:** PLAN-001's embedding model recommendation table is revised: the API-based
options (`text-embedding-3-small`, `text-embedding-004`) are moved to rejected alternatives.
`nomic-embed-text-v2` (local via Ollama) becomes the sole recommendation. The vector store
recommendation (DuckDB VSS) is confirmed and unchanged. The proposed `memory_embeddings` DDL from
PLAN-001 is extended to cover documents and ideas, not just memories:

```sql
CREATE TABLE embeddings (
    source_type     VARCHAR NOT NULL,       -- 'memory', 'document', 'idea'
    source_id       VARCHAR NOT NULL,       -- mem-xxx, PLAN-001, 000043
    model           VARCHAR NOT NULL,       -- nomic-embed-text-v2
    vector          FLOAT[256],             -- Matryoshka-truncated from 768
    content_hash    VARCHAR NOT NULL,       -- SHA-256 of embedded text
    embedded_at     TIMESTAMP NOT NULL,
    PRIMARY KEY (source_type, source_id)
);
```

**Done when:**
-   All governed documents, brain memories, and ideas have embeddings in the `embeddings` table.
-   `search_semantic("how does the project handle concurrent agents")` returns relevant documents
    (AGENTS.md sections, ADR-003, GOV-003) with cosine similarity scores.
-   `tools/refresh_embeddings.py` skips unchanged documents (content-hash match) and re-embeds only
    changed ones.
-   The retrieval evaluation from `phase-mem-10` shows measurable improvement on the cases that
    deterministic search missed.

### Phase 4: Retrieval quality measurement and evidence report

**Delivers:** A retrieval evaluation tool (`tools/evaluate_retrieval.py`) and a baseline report.
Uses both the synthetic evaluation set (per `phase-mem-10`) and the real retrieval log accumulated
during Phases 1–3.

**Dependency:** Phase 2 (needs the MCP server and retrieval log). Can run in parallel with or
before Phase 3 — in fact, running it *before* Phase 3 is what produces the evidence that justifies
Phase 3.

**Ideas addressed:** 000004 (evidence for semantic search). 000002 (measuring whether the ordering
works).

**Existing backlog:** Directly implements `phase-mem-10` (measure keyword and tag retrieval quality).

**Done when:**
-   The evaluation report identifies specific queries where deterministic retrieval returned no
    results or missed relevant documents, OR explicitly records that current retrieval is sufficient.
-   The report is a session record with governed front matter (`kind: session`).

### Phase 5: PLAN-001 reconciliation and agent-contract update

**Delivers:** A revised PLAN-001 (or a successor plan) that reconciles the original memory-agent
design with the broader knowledge-retrieval scope and the findings of this investigation. Updates
the Librarian's retrieval pipeline to reflect the actual implementation (MCP server, DuckDB-only
stack, Nomic embeddings). Confirms or revises the Chronicle and Vault Scribe contracts.

**Dependency:** Phases 1–4 (needs the implementation to exist before revising the plan that
describes it).

**Ideas addressed:** All eight ideas reach a terminal state (promoted to the reconciled plan,
implemented by earlier phases, or explicitly deferred/discarded with reasoning).

**Existing backlog:** Directly implements `phase-mem-01` (reconcile memory-agent contracts with
accepted choices). The reconciliation should cover:
-   PLAN-001's embedding model table → revised per §2.4
-   PLAN-001's vector store table → confirmed (DuckDB VSS)
-   PLAN-001's Librarian pipeline → extended from brain-only to documents + memories + ideas
-   PLAN-001's `text-embedding-3-small` recommendation → replaced by `nomic-embed-text-v2`
-   PLAN-001's "Migrate to Qdrant if memory count exceeds 2,000" → retained as a future option
    but not expected to be needed given corpus size projections

**Done when:**
-   PLAN-001 (or its successor) accurately describes the implemented system.
-   All eight ideas (000002, 000004, 000005, 000007, 000020, 000043, 000044, 000045) have explicit
    statuses in the ideas log (promoted, discarded, or deferred with reasoning).

---

## 5. Open questions for the owner

These cannot be resolved from the source material and need a human decision before implementation:

1.  **Ollama as a runtime dependency.** The embedding model (`nomic-embed-text-v2`) requires Ollama
    to be installed and running. This is a new external dependency — the project currently requires
    only `uv` (Python) and `npm` (Node). Is this acceptable? If not, the alternative is
    `sentence-transformers` running directly in the `uv` Python environment (heavier Python
    dependency, ~2x slower on CPU, but no separate service). The Ollama approach is recommended
    because it keeps the embedding runtime cleanly separated from the Python application.

2.  **MCP server registration.** The MCP server needs to be registered with the AI assistant (Claude
    Code, Cursor, etc.) via a configuration file. For Claude Code this is typically
    `.mcp.json` in the project root. This file would be tracked in git. Is that acceptable, or should
    it be gitignored like `.claude/settings.local.json`? The recommendation is to track it (it
    describes a project capability, not a personal preference), but this is an owner call.

3.  **Retrieval log confidentiality.** The proposed retrieval log (`_data/retrieval_log.jsonl`)
    records query text but not result content. However, query text itself may reveal what an agent
    was working on. Should this log be gitignored (like `data/`), tracked (like `_data/`), or placed
    in `_private/`? The recommendation is gitignored — it's derived operational data, not a source
    of truth — but it touches the confidentiality boundary and the owner should decide.

4.  **Phase 3 evidence gate: how strict?** The plan proposes that Phase 3 (semantic search) only
    proceeds if the retrieval log shows concrete failures of deterministic search. How many failures
    constitute "concrete"? One reproducible miss? Five? A pattern across multiple sessions? The
    recommendation is to define this before Phase 1 ships, so the gate is objective rather than
    subjective.

5.  **Embedding scope.** Should session transcripts (`docs/03-sessions/`) be embedded? They are
    large (some are 10+ KB), contain contemporaneous narrative that may be valuable for semantic
    search, but also contain corrections and superseded information. The recommendation is to embed
    them with lower retrieval weight (the `kind`-based ordering from §2.3 handles this), but the
    owner may prefer to exclude them.

6.  **Idea 000007 (triage agent) timing.** This investigation recommends deferring automated triage
    until the idea count exceeds ~100 and the deterministic search layer exists. The owner may have
    a different threshold or a different reason to build it sooner. The finding is that it is not a
    prerequisite for the knowledge retrieval system, not that it lacks value.

7.  **Code-structure tooling: priority and timing.** §2.9 recommends trialing Codebase-Memory-MCP
    for agent-assisted code development. This is independent of the knowledge-retrieval phases
    (§4) — it can be done before, during, or after them. Should this trial happen now (it's a
    low-cost installation exercise, not a build), or should it wait until the knowledge-retrieval
    MCP server exists so both can be configured together?

8.  **Code-structure tooling: scope.** Should the code-structure MCP tool index only `src/` and
    `tools/`, or also `test/` and `schemas/`? Indexing more gives agents better impact-analysis
    coverage, but also means structural queries may return test fixtures or schema definitions
    alongside production code. The recommendation is to index everything and let agents filter by
    path prefix in their queries, but the owner may prefer a narrower scope initially.

9.  **Multi-repo Graph DB piloting.** For the primary working repo (~1,400 documentation nodes) where
    a graph database is justified (§2.10), should we immediately trial LadybugDB or ArcadeDB there,
    or wait until the DuckDB baseline implementation (Phases 1-3) is proven out in this repository first?
    If we pilot LadybugDB now, we can validate the embedded Python workflow before committing to it.
