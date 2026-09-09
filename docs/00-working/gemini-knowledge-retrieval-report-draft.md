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

**Question:** Does code-structure retrieval (idea 000005, GitNexus/KuzuDB) and
documentation/knowledge retrieval (000043/000044/000045/000020/000004) need separate databases?

**Finding:** These are **two distinct use cases** that should be evaluated independently, not merged
into one store-topology question.

**Use case A: Knowledge retrieval for planning (this report's primary scope)**

One DuckDB instance can serve all knowledge-retrieval needs for this repository's scale:

-   **Documentation/knowledge retrieval** (000043/000044/000045): The document-relationship graph is
    entirely captured by structured YAML front matter fields that are already validated by
    `src/governance`. Projecting those into DuckDB tables and using recursive CTEs for traversal
    gives the same answers a graph database would, without a new engine. The semantic search layer
    (embeddings + VSS) lives naturally alongside that in the same DuckDB file.

-   **Memory retrieval** (PLAN-001 / `phase-mem-*`): Already targets DuckDB. The proposed
    `memory_embeddings` table from PLAN-001 fits directly into the existing `data/d_system.duckdb`.

A separate graph database is **not yet justified** for knowledge retrieval. The document graph is
small (~200 nodes, ~300 edges, max depth 4), and DuckDB recursive CTEs handle it trivially. This
is a "not now" finding, not a permanent exclusion — if the graph grows past ~1,000 nodes with dense
cross-referencing, or queries shift toward pattern matching (cycle detection, community analysis),
a graph DB should be re-evaluated. See §2.2 for the concrete capability ceiling analysis.

**Use case B: Code-structure analysis for agent development (separate concern)**

Code-structure tooling — call hierarchies, import graphs, impact analysis ("what breaks if I change
this function?") — serves a fundamentally different purpose from knowledge retrieval. It helps agents
*write and modify code*, not *plan what to build*. This use case:

-   Does not need to query documentation front matter, memories, or ideas
-   Does need a parser (tree-sitter) and a structural representation (AST → graph)
-   Is best served by a purpose-built MCP tool, not by extending the knowledge-retrieval DuckDB
-   Has a mature ecosystem of alternatives beyond GitNexus (see §2.9)

**Conclusion:** One DuckDB instance handles all knowledge-retrieval needs. Code-structure analysis
is a separate tool category evaluated in §2.9, independent of the knowledge-retrieval store.

### 2.2 DuckDB's own capability ceiling

**Question:** Before adding KuzuDB or any other engine, what can DuckDB *not* do here?

**Finding:** For this corpus, DuckDB can do everything required. The "where do recursive CTEs stop
being adequate" question has a concrete answer: they stop being adequate for graph workloads with
millions of edges, complex pattern matching (e.g., "find all triangles"), or workloads requiring
native Cypher/SPARQL. None of those apply here.

The document graph in this repository has:
-   ~20 governed documents with `depends_on` edges (max depth observed: 3)
-   ~45 ideas, some with `promoted_to` links
-   ~90 backlog phases with `depends_on` chains (max depth observed: 4)
-   ~15 systems in `systems.yaml` with `depends_on` edges (max depth: 2)

This is a graph with fewer than 200 nodes and fewer than 300 edges. DuckDB's recursive CTEs handle
this trivially, and the `USING KEY` optimization (available since DuckDB v1.x, 2025) means even
graph algorithms like shortest-path work efficiently at this scale.

**What DuckDB does not natively provide:**
-   **Cypher query syntax.** DuckPGQ (community extension implementing SQL/PGQ from SQL:2023) is
    available but is research-stage and has compatibility challenges with recent DuckDB versions.
    Since the queries needed here are straightforward recursive joins, SQL is adequate and DuckPGQ
    is not recommended.
-   **Named property graph declarations.** SQL/PGQ would allow `CREATE PROPERTY GRAPH`, but the
    same relationships are expressible as junction tables and foreign-key-style references.

**Conclusion:** For knowledge retrieval (the document/planning graph), DuckDB's ceiling is well
above what this corpus requires. The relational, graph-traversal, and vector layers all fit within
one engine. This conclusion applies to the *planning and knowledge* workload; code-structure
analysis (call graphs, import hierarchies, impact analysis) is a different workload with different
query patterns, evaluated separately in §2.9.

**Resumption trigger for graph DB re-evaluation:** If the document graph exceeds ~1,000 nodes, or if
queries requiring multi-hop pattern matching (not simple ancestor/descendant traversal) become
common, re-evaluate an embedded graph engine at that point. Community forks of KuzuDB (LadybugDB)
or multi-model options (ArcadeDB) would be the candidates to evaluate.

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

**Question:** Which locally-runnable embedding model fits this corpus?

**Finding:** **`nomic-embed-text-v2`** via Ollama is the clear recommendation.

| Criterion | nomic-embed-text-v2 | text-embedding-3-small (OpenAI) |
|---|---|---|
| **Local-only** | ✅ Runs fully local via Ollama | ❌ API call — violates constraint |
| **CPU performance** | ~580 chunks/sec on modern CPU | N/A (API) |
| **Model size** | ~274 MB download, ~0.3 GB RAM | N/A |
| **Dimensions** | 768 (truncatable to 256/512 via Matryoshka) | 1536 |
| **Python integration** | `ollama.embeddings()` — one function call | `openai.embeddings.create()` |
| **GPU required?** | No — MoE architecture optimized for CPU | N/A |
| **Cost** | Free | ~$0.02 per 1M tokens |

**Resource requirements for this corpus:**
-   ~13 brain memory files (averaging ~2 KB each)
-   ~20 governed documents (averaging ~5 KB each)
-   ~45 ideas (averaging ~2 KB each)
-   ~30 session records (averaging ~10 KB each)
-   Total: roughly 500 KB of text, or about 500 chunks at 1 KB per chunk.

At 580 chunks/sec on CPU, the full corpus embeds in under 1 second. Incremental re-embedding
(content-hash based invalidation, as PLAN-001's `memory_embeddings` table already specifies) would
touch only changed documents. This is not a performance-sensitive workload.

**Matryoshka dimension truncation** is worth using: 256 dimensions are likely sufficient for this
corpus size (hundreds, not millions, of documents) and reduce DuckDB VSS index size proportionally.
Start at 256; increase to 512 if retrieval quality measurement (phase-mem-10) shows it's needed.

**Runtime requirement:** Ollama must be installed and running as a local service. This is a separate
runtime from `uv`'s Python environment. The embedding adapter in Python calls Ollama's HTTP API
(`localhost:11434`). This is the same pattern used by any local LLM tool. No GPU is required.

**Conclusion:** Use `nomic-embed-text-v2` via Ollama. PLAN-001's recommendation of
`text-embedding-3-small` as primary with `nomic-embed-text` as fallback should be inverted and
simplified: Nomic is the only provider, run locally, no API dependency.

### 2.5 MCP server: what it's for and what it isn't

**Question:** Are retrieval-over-MCP and coordination-over-MCP separable? Which should be built?

**Finding:** They are entirely separable and have very different risk profiles. **Build
retrieval-over-MCP. Do not build coordination-over-MCP.**

**Retrieval-over-MCP (recommended):**
-   A FastMCP server (Python, stdio transport) that exposes 3–5 tools:
    -   `search_documents(query, kind, system, status)` — structured search over the `documents` table
    -   `search_memories(query, type, tags, system)` — the existing `load_context.py` functionality
    -   `search_semantic(query, top_k)` — vector similarity search (once embeddings exist)
    -   `get_document(code)` — exact lookup by document code
    -   `traverse_dependencies(code, direction, depth)` — recursive CTE over `document_dependencies`
-   Runs as a local subprocess launched by the AI assistant (Claude Code, Cursor, etc.)
-   Read-only — cannot write to any file or database
-   Well-precedented pattern; the MCP ecosystem has mature tooling (FastMCP) and conventions
-   Marginal complexity: ~200 lines of Python wrapping DuckDB queries

**Coordination-over-MCP (not recommended):**
-   Idea 000020 proposes replacing the file-based locking system (`backlog.yaml` + `src/governance`)
    with a live MCP service mediating backlog claims, worktree checkout, collision detection, and a
    pub/sub kill-switch.
-   The current system works. It has been tested by real concurrent-agent collisions (idea 000041
    documents one). Those collisions were resolved by the existing protocol, not by a missing service.
-   A live coordination service introduces: a new failure mode (service down = agents blocked), state
    that must be synchronized with `backlog.yaml` (or replaces it, breaking the file-based audit
    trail), and a startup/shutdown lifecycle that does not currently exist.
-   The kill-switch concept ("signal a running agent to stop") is interesting but is a monitoring
    problem, not a coordination-protocol problem. An MCP notification channel is one implementation;
    a simpler one is a sentinel file the agent checks between tool calls.
-   **If coordination-over-MCP is ever revisited,** it should be as a separate plan with its own
    evidence gate: "the file-based protocol failed in a way the MCP service would have prevented,
    and that failure was not addressable by a procedural fix."

**Conclusion:** Build a read-only retrieval MCP server. Leave coordination on `backlog.yaml` +
`src/governance`.

### 2.6 Retrieval failure evidence gate

**Question:** Does the plan respect the existing gate (phase-mem-10 must record retrieval failures
before semantic search is justified), or should the gate be revised?

**Finding:** The gate is sound but needs a mechanism. The plan should **build measurement alongside
the deterministic layer, not after it.**

The problem today: `phase-mem-15` through `phase-mem-19` are deferred with `resume_when: phase-mem-10
records concrete unmet retrieval needs`, but nothing in the current system records when a retrieval
fails. An agent that searches `load_context.py`, gets no results, and falls back to grepping `docs/`
by hand leaves no trace of the failure.

**Recommended approach:**
1.  The MCP server should log every query it receives and every result set it returns (including
    empty result sets) to a local JSONL file (`_data/retrieval_log.jsonl`).
2.  `phase-mem-10` (measure keyword and tag retrieval quality) should analyze this log, not only a
    synthetic evaluation set. Real queries from real sessions are stronger evidence than crafted test
    cases.
3.  The log schema should include: `timestamp`, `query_text`, `filters_applied`, `method_used`,
    `result_count`, `agent_id` (if available). It should *not* include the result content (to avoid
    duplicating sensitive data).
4.  This log is cheap to build (append a JSON line per query) and can be implemented in Phase 1,
    well before semantic search exists, so that the evidence base accumulates naturally.

**The gate itself should not be revised.** Building semantic search before demonstrating that
deterministic search is insufficient would violate the project's own evidence-based-gating principle.
The correct sequencing is: build the deterministic layer → measure it → use the measurements to
justify (or not justify) the semantic layer.

**Conclusion:** Respect the gate. Add a retrieval log to make it satisfiable.

### 2.7 Migration and sync

**Question:** How does each proposed store stay in sync with hand-edited source files?

**Finding:** Every store proposed follows the same precedent already established for `_data/`:
**full rebuild from source files, triggered by a command, never hand-edited.**

| Store | Source files | Rebuild command | Staleness check |
|---|---|---|---|
| `_data/` tables (existing) | `_data/*.json`, `_data/*.jsonl` | `tools/rebuild_db.py` | Source validation runs before rebuild |
| `brain/` memories (existing) | `brain/**/*.md` | `tools/rebuild_db.py` | YAML frontmatter validated by `src/governance` |
| `documents` table (proposed) | `docs/**/*.md` front matter | `tools/rebuild_db.py` (extended) | `src/governance` already validates front matter |
| `document_systems` (proposed) | Derived from `documents.systems` | Same rebuild | Same validation |
| `document_dependencies` (proposed) | Derived from `documents.depends_on` | Same rebuild | Same validation |
| Embedding vectors (proposed) | Derived from text content of above | `tools/refresh_embeddings.py` | Content-hash comparison (per PLAN-001's design) |

The key design constraint: **no additional sync mechanism is introduced.** The existing pattern is:

1.  Human or agent edits a markdown or JSON file.
2.  `src/governance` validates the file's structure (front matter, schema).
3.  `tools/rebuild_db.py` drops and recreates all DuckDB tables from source files.
4.  The MCP server reads from the rebuilt DuckDB file on each query.

The embedding refresh is the one new step, and it should follow the same trigger model: run
`tools/refresh_embeddings.py` after `tools/rebuild_db.py`, or integrate it as an optional step in
the rebuild. Content-hash comparison (already in PLAN-001's `memory_embeddings` DDL:
`content_hash VARCHAR NOT NULL`) means only changed documents get re-embedded.

**The MCP server does not cache independently.** It opens a read-only DuckDB connection per query.
There is no live state to drift.

**Conclusion:** All proposed stores follow the existing rebuild-from-source pattern. No new sync
mechanism is needed.

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

**Question:** Idea 000005 proposed GitNexus for code-structure analysis. GitNexus's backend (KuzuDB)
is deprecated. What alternatives exist, and should this be pursued?

**Finding:** Code-structure MCP tools are a **distinct, valuable category** that should be evaluated
independently of the knowledge-retrieval system. They serve a different purpose (helping agents write
and modify code via call-graph traversal, import analysis, and impact assessment) and use different
infrastructure (tree-sitter parsing, AST-to-graph projection) from the document/planning knowledge
base.

**Why this matters for this repository:** As agents work more of the codebase (`src/`, `tools/`,
`test/`), questions like "what calls `validate_sources()`?", "what is the blast radius of changing
`backlog.py`?", and "show me the import graph for `src/governance/`" become increasingly valuable
for *planning before execution of code* — impact analysis before making a change, not just
understanding what exists. The current codebase (~2,500 lines) is small enough that grep suffices
today, but the value of structural tooling scales with how frequently agents work the code, not
just with codebase size.

**GitNexus status:** Cannot be adopted. Its KuzuDB backend was acquired by Apple and archived in
October 2025. The project depends on deprecated, unmaintained software. No evidence of a backend
migration was found.

**Alternative landscape (as of September 2026):**

| Tool | Backend | Key strength | Concern for this repo |
|---|---|---|---|
| **Codebase-Memory-MCP** | Tree-sitter + SQLite | Speed (native Go binary), broad language support (35+), minimal overhead, single-binary distribution. No embedded LLM required. | Most mature and lightweight option. SQLite backend is maintained and stable. |
| **Treesitter-MCP** | Tree-sitter | Context compression — token-aware snippet extraction, structural filtering. Focused on keeping agent context windows lean. | Narrower scope (extraction, not full graph), but composable with other tools. |
| **CodeGraph (agntk)** | Tree-sitter + configurable | "Bitemporal" knowledge — tracks how code structure evolves over commits. Point-in-time queries. | More complex; the temporal dimension may be overkill initially but valuable for impact analysis on branches. |
| **Sonde** | Specialized | Historical/commit-level indexing optimized for breaking-change and PR analysis. | Best fit for impact analysis specifically, but narrower tool. |
| **Graphify** | NetworkX + Leiden | Indexes docs, PDFs, web URLs alongside code. Python-based. | Broader but heavier; the doc-indexing overlap with this report's knowledge-retrieval system would need careful scoping. |

**Recommendation:** **Codebase-Memory-MCP** is the strongest candidate for this repository:
-   SQLite backend (maintained, embedded, no KuzuDB risk)
-   Tree-sitter parsing (the industry-standard approach to structural code analysis)
-   MCP-native (stdio transport, same integration pattern as the knowledge-retrieval MCP server)
-   Read-only by design (agents query structure, never write)
-   Single-binary distribution (no Python dependency conflicts with the existing `uv` environment)

**This is a separate evaluation from the knowledge-retrieval plan.** Adopting a code-structure MCP
tool does not require any of the five phases proposed in §4. It is an independent tool installation
decision — closer to "install a useful MCP server" than "build a system." The recommendation is:

1.  **Trial Codebase-Memory-MCP** in a single agent session: install, index the repository, and
    test a handful of structural queries against `src/` and `tools/`.
2.  **If the trial succeeds**, register it alongside the knowledge-retrieval MCP server in the
    project's MCP configuration. The two servers serve different query types and do not conflict.
3.  **Record the evaluation** as an idea status change (000005 → triaged, with findings) and, if
    adopted, as a session record.

**Idea 000005 disposition:** The idea correctly identified that code-structure graph analysis is
valuable and complementary to semantic/vector search. Its specific tool recommendation (GitNexus)
is blocked by KuzuDB deprecation, but the underlying need is real and addressable by alternatives.
The idea should move to `triaged` with findings attached, not `discarded`.

### 2.10 Graph database options for documentation knowledge graphs

**Context:** The owner's primary working repository has ~1,400 documentation nodes — well past the
~1,000-node threshold where a dedicated graph engine becomes worth evaluating over DuckDB recursive
CTEs. This section provides a concrete evaluation of the current embedded graph DB landscape,
framed for multi-repo use, not just d-system.

#### When a graph DB earns its keep over DuckDB recursive CTEs

DuckDB recursive CTEs perform well for **tree/DAG traversals** (ancestor chains, dependency
resolution) up to tens of thousands of nodes. The cases where a graph DB adds meaningful value are:

| Query pattern | DuckDB CTE | Dedicated graph DB |
|---|---|---|
| "What does X depend on?" (single-root traversal) | ✅ Trivial, fast at any scale here | ✅ Also trivial |
| "What depends on X?" (reverse traversal) | ✅ Fine with indexed joins | ✅ Also fine |
| Multi-hop pattern: "find all docs that share 3+ systems with X and also depend on a common ancestor" | ⚠️ Expressible but awkward multi-join CTEs | ✅ Natural in Cypher: `MATCH (a)-[:DEPENDS_ON*..3]->(c)<-[:DEPENDS_ON*..3]-(b) WHERE ...` |
| Impact analysis: "if I change system Y, what is the full blast radius across documents, phases, and ideas?" | ⚠️ Multiple CTEs chained, one per relationship type | ✅ Single variable-length path query across edge types |
| Cross-referencing: "find clusters of documents connected by shared systems, tags, and dependencies" | ❌ Very awkward in SQL; requires self-joins and grouping | ✅ Community detection, centrality algorithms native |
| Shortest path between two documents through any relationship | ⚠️ Possible with `USING KEY` but verbose | ✅ `shortestPath()` built-in |

**At ~1,400 nodes with dense cross-referencing (systems, tags, depends_on, promoted_to edges), the
graph DB advantage is real — not for raw speed, but for query expressiveness.** Writing the
multi-hop pattern and impact-analysis queries in Cypher is 5–10 lines; the equivalent recursive CTE
chain is 30–50 lines and harder to compose dynamically at runtime (e.g., when an agent needs to
construct a traversal based on what it finds).

#### The current landscape (September 2026)

KuzuDB's archival left a gap, but three maintained options have filled it:

**1. LadybugDB** (KuzuDB community fork)

| Attribute | Detail |
|---|---|
| **Origin** | Direct fork of KuzuDB codebase, community-maintained since Oct 2025 |
| **Status** | Active — 1,000+ commits, 20+ releases, v0.19.1 (Aug 2026), 80+ contributors |
| **Architecture** | Embedded, in-process, columnar storage (same as KuzuDB) |
| **Query language** | Cypher |
| **Python install** | `pip install ladybug` |
| **Python API** | `import ladybug as lb` — familiar to KuzuDB users |
| **License** | MIT (same as original KuzuDB) |
| **Vector support** | HNSW indices (inherited from KuzuDB, enhanced) |
| **Ecosystem integration** | Arrow, Parquet, DuckDB interop (evolving "graph lakehouse" roadmap) |
| **Risk** | Community-driven; no corporate sponsor. Active but longevity uncertain. |

**Why consider it:** Most direct successor to KuzuDB. If you or your agents already know Cypher and
want an in-process, embedded, columnar graph DB, LadybugDB is the closest match. The DuckDB
interop roadmap is particularly interesting — it could eventually allow the knowledge-retrieval
DuckDB and the graph DB to share storage via Arrow, making the "one engine or two?" question less
binary.

**2. ArcadeDB** (multi-model)

| Attribute | Detail |
|---|---|
| **Origin** | Independent project, Apache 2.0 licensed |
| **Status** | Active, mature, commercially backed |
| **Architecture** | Multi-model: graph + document + key/value + vector + time-series |
| **Query languages** | SQL, OpenCypher 25 (97.8% TCK pass rate), Gremlin, GraphQL |
| **Python install** | `pip install arcadedb-embedded` (bundles Java 25 runtime, no setup) |
| **Python API** | In-process via JPype; `with arcadedb.create_database("./mydb") as db:` |
| **License** | Apache 2.0 |
| **Vector support** | Native JVector (HNSW + DiskANN + Product Quantization) |
| **MCP support** | Built-in MCP server (introduced early 2026) |
| **Risk** | Bundles a JVM — larger footprint (~200 MB). JPype bridge adds a layer. |

**Why consider it:** The multi-model aspect is compelling for a documentation knowledge graph: you
can store graph relationships (depends_on, systems membership), vector embeddings, and document
metadata in one engine instead of splitting across DuckDB + a graph DB. The built-in MCP server
means an agent could query it directly without writing a custom FastMCP wrapper. The OpenCypher
support is near-complete, so Cypher queries from KuzuDB/Neo4j tutorials work as-is.

**Trade-off:** The JVM runtime is a heavier dependency than a pure C++/Rust embedded DB. For a
Python project currently requiring only `uv` and `npm`, adding a bundled JVM is a meaningful
footprint increase. The JPype bridge works but adds a layer of abstraction that pure Python
bindings (LadybugDB, FalkorDBLite) don't have.

**3. FalkorDBLite** (embedded FalkorDB)

| Attribute | Detail |
|---|---|
| **Origin** | Embedded variant of FalkorDB (successor to RedisGraph) |
| **Status** | Active, commercially backed by FalkorDB Inc. |
| **Architecture** | Sub-process model (forks a lightweight process, communicates via Unix sockets) |
| **Query language** | Cypher (OpenCypher-based, RedisGraph lineage) |
| **Python install** | `pip install falkordblite` (Python 3.12+) |
| **Python API** | Standard FalkorDB client; `import falkordblite` |
| **License** | Server Source License (SSLv1) — more restrictive than Apache/MIT |
| **Vector support** | Native vector indexing for GraphRAG |
| **Performance** | GraphBLAS-based engine — optimized for sparse matrix operations on graphs |
| **Risk** | SSLv1 license is more restrictive. macOS requires `libomp` (Homebrew). Sub-process model means it's not truly in-process. |

**Why consider it:** Highest raw graph performance of the three for complex traversals (GraphBLAS
operations on sparse matrices are very efficient for multi-hop patterns). The sub-process isolation
model is actually a feature for stability — a bug in graph processing can't crash the Python host.
LangChain/LlamaIndex integrations are mature.

**Trade-off:** The SSLv1 license is more restrictive than Apache 2.0 or MIT — it prohibits offering
FalkorDB as a hosted service (not a problem for local use, but worth noting for the license audit
when `phase-priv-05` runs). The sub-process model means startup/shutdown lifecycle management,
which DuckDB and LadybugDB don't require.

**4. DuckPGQ** (SQL/PGQ extension for DuckDB)

| Attribute | Detail |
|---|---|
| **Origin** | CWI research project, community extension |
| **Status** | Active research, community extension, version-compatibility challenges |
| **Architecture** | Extension to DuckDB — no separate process or storage |
| **Query language** | SQL/PGQ (SQL:2023 standard graph pattern matching) |
| **Python install** | `INSTALL duckpgq FROM community; LOAD duckpgq;` in DuckDB |
| **License** | MIT |
| **Risk** | Research-stage; parser integration fragile across DuckDB major versions |

**Why consider it:** Zero additional infrastructure — it's DuckDB with graph syntax. If the main
concern is query expressiveness (writing Cypher-like patterns instead of recursive CTEs), DuckPGQ
provides that without a second engine. The SQL:2023 standard basis means it's not a proprietary
query language.

**Trade-off:** Compatibility with recent DuckDB versions is not guaranteed. As a research project,
the feature set may be incomplete. For a production system, this is the riskiest option.

#### Comparison matrix

| Criterion | LadybugDB | ArcadeDB | FalkorDBLite | DuckPGQ | DuckDB CTEs (baseline) |
|---|---|---|---|---|---|
| **In-process / embedded** | ✅ True in-process | ✅ Via JPype | ⚠️ Sub-process | ✅ Extension | ✅ Native |
| **Query expressiveness at 1,400 nodes** | ✅ Full Cypher | ✅ Cypher + SQL | ✅ Cypher | ⚠️ SQL/PGQ subset | ⚠️ Recursive CTEs |
| **Python integration** | ✅ `pip install ladybug` | ⚠️ `pip install arcadedb-embedded` (bundles JVM) | ✅ `pip install falkordblite` | ✅ DuckDB extension | ✅ Native |
| **Vector search** | ✅ HNSW | ✅ JVector | ✅ Native | ❌ Use DuckDB VSS separately | ✅ DuckDB VSS |
| **DuckDB interop** | ✅ Arrow roadmap | ⚠️ Via export/import | ❌ Separate store | ✅ Same engine | ✅ Native |
| **License** | MIT | Apache 2.0 | SSLv1 | MIT | MIT |
| **Maturity** | ⚠️ Community fork, < 1 year | ✅ Mature, backed | ✅ Mature, backed | ⚠️ Research-stage | ✅ Stable |
| **Additional runtime** | None | JVM (bundled) | Sub-process + libomp | None | None |
| **Source-of-truth pattern** | Rebuild from files → graph | Rebuild from files → graph | Rebuild from files → graph | Same DuckDB rebuild | Same DuckDB rebuild |
| **Built-in MCP** | ❌ | ✅ | ❌ | ❌ | ❌ (custom FastMCP) |

#### Recommendation tiers

**For d-system (this repo, ~200 nodes):** DuckDB recursive CTEs remain sufficient. No graph DB
needed now. This recommendation is unchanged.

**For the primary working repo (~1,400 nodes) and future repos at similar scale:**

1.  **Recommended: LadybugDB** — Best fit for the local-first, Python-centric, file-authority
    stack. Truly in-process (no sub-process, no JVM), MIT-licensed, and the DuckDB/Arrow interop
    roadmap means it may eventually share storage with the existing DuckDB projection. The
    community-fork risk is real but mitigated by active development (80+ contributors, monthly
    releases). If LadybugDB's development slows, the fallback is ArcadeDB.

2.  **Strong alternative: ArcadeDB** — Best fit if multi-model value (graph + vector + document in
    one engine) outweighs the JVM footprint concern. The built-in MCP server is a significant
    convenience — no custom FastMCP wrapper needed. The OpenCypher 25 support is near-complete.
    Choose this over LadybugDB if you want to consolidate the graph DB and vector DB into one engine
    and are comfortable with the JVM dependency.

3.  **Specialized alternative: FalkorDBLite** — Best raw graph performance (GraphBLAS), but the
    SSLv1 license and sub-process model are trade-offs. Choose this if graph traversal performance
    is the primary concern and the license is acceptable.

4.  **Not recommended for production: DuckPGQ** — Interesting for experimentation and may mature
    into the best option (zero infrastructure, SQL:2023 standard), but the research-stage stability
    is a concern for a production knowledge graph.

#### Integration architecture (for any graph DB choice)

Regardless of which graph DB is chosen, the integration pattern must follow the existing
source-of-truth principle: **files are authoritative, the graph DB is a derived projection.**

```
docs/**/*.md (YAML front matter)  ──┐
brain/**/*.md (YAML front matter) ──┤
_data/**/*.json                   ──┤
                                    ├──→ tools/rebuild_graph.py ──→ graph DB (derived, rebuildable)
                                    │
                                    └──→ tools/rebuild_db.py    ──→ DuckDB   (derived, rebuildable)
```

Key design constraints:
-   `tools/rebuild_graph.py` is the single command that drops and recreates the graph from source
    files, analogous to `tools/rebuild_db.py` for DuckDB.
-   The graph DB file/directory is gitignored (like `data/`).
-   No graph DB write occurs outside `rebuild_graph.py` — agents query the graph, never mutate it.
-   The MCP server (custom FastMCP or ArcadeDB's built-in) opens a read-only connection.
-   Both DuckDB and the graph DB can coexist: DuckDB handles relational queries, tabular projections,
    and VSS; the graph DB handles pattern matching, impact analysis, and multi-hop traversals.
    They are not mutually exclusive.

**The graph DB does not replace DuckDB.** It augments it with query patterns that recursive CTEs
handle poorly. Both are derived from the same source files and rebuilt by the same trigger.

---

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
