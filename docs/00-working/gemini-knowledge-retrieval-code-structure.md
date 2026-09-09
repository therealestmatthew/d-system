# Deep Dive: Code-Structure Tooling

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

