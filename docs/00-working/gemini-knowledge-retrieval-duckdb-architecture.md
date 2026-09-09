# Deep Dive: DuckDB Architecture & Limits

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

