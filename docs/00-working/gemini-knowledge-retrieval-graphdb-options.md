# Deep Dive: Multi-Repo Graph Database Options

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

