# Deep Dive: MCP Server & Evidence Gate

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

