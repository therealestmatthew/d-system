# Instructions for Gemini: knowledge retrieval architecture investigation

**Not a plan, not governed, not queued.** This file is a briefing for an external agent (Gemini),
staged per [ADR-010](../04-decisions/ADR-010-idea-staging.md). Its output is a report with a
proposed multi-phase plan inside it — a human or agent in this repository decides afterward whether
to promote that proposal into a real `docs/01-plans/PLAN-XXX.md` with backlog phases. Nothing in this
file or its output is authorized to be implemented on its own authority.

---

## 1. What you're investigating

This repository (`d-system`) accumulated eight related but un-synthesized ideas about how it stores
and retrieves knowledge about itself — its documentation, decisions, session history, and code. They
were captured separately, as this project's process requires ([ADR-010](../04-decisions/ADR-010-idea-staging.md):
ideas are recorded as given, never merged or filtered at the point of capture; synthesis is a
downstream pass). You are that downstream pass.

Your job: read the source material listed in section 2, then produce a single investigation report
(section 5) that synthesizes these ideas into a coherent, phased, implementable plan for moving this
project's knowledge into a queryable store — including, where you conclude it's warranted, an MCP
server that exposes that store to Claude Code and other assistants.

You are not building anything. You are not editing any file in this repository other than the one
output file specified in section 5. You are producing the design and the phased plan that a human
will decide whether to greenlight.

## 2. Required reading, in this order

Read every file below before forming conclusions. They are listed in the order that will build
context correctly — later documents assume the earlier ones.

1. **`AGENTS.md`** (repo root) — the working agreement. Pay particular attention to: the
   confidentiality section (no remote, `_data/` holds real client and personal data), the concurrent-agent
   protocol (file-based locking via `docs/09-backlog/backlog.yaml` and `uv run python -m
   src.governance`), and the "adding a domain entity" convention if present.
2. **`CLAUDE.md`** (repo root) — orientation: data architecture (`_data/` JSON as source of truth,
   DuckDB in `data/d_system.duckdb` as a *derived, rebuildable* query layer, never edited directly),
   backend/frontend layout, directory reference.
3. **`docs/00-working/ideas.md`** — read the full file, but the entries that define your scope are:
   - `000002` — prioritised search order for agentic knowledge retrieval (the ordering/confidence
     problem across sources: code, plans, ADRs, sessions, ideas, `brain/` memories)
   - `000004` — vector databases, agentic RAG, semantic+deterministic search (references the
     `phase-mem-*` backlog line, all currently `deferred`)
   - `000005` — graph databases and GitNexus (client-side repo-to-knowledge-graph tool using KuzuDB
     + Cypher + MCP, argued as complementary to vector search: graph for structure, vector for
     semantic recall — treat that framing as a hypothesis to test, not a given)
   - `000007` — an agent for triaging parked ideas (relevant because your own investigation is
     doing this triage by hand; note whether your findings suggest this should be automated)
   - `000020` — MCP-mediated multi-agent coordination with a "Librarian" context service (an MCP
     server as the coordination substrate for this repo's own multi-agent backlog/claims protocol,
     with a vector DB behind it and a pub/sub kill-switch — the most architecturally ambitious of
     the eight ideas)
   - `000043` — documentation front-matter review and a documentation database (the
     structured/relational half of knowledge retrieval: querying front matter — `depends_on`,
     `systems`, `status` — the way `_data/` is already queried via DuckDB)
   - `000044` — graph database tooling for documentation/knowledge, distinct from GitNexus's
     code-structure graph (KuzuDB vs. Neo4j vs. lighter options, for the document-cross-reference
     graph: `depends_on` edges, `promoted_to` links, `systems` membership)
   - `000045` — vector database tooling for a knowledge retrieval system (embedded options —
     including DuckDB's own VSS extension — vs. hosted, for semantic search over docs/sessions/decisions)
4. **`docs/01-plans/PLAN-001-agent-memory-system.md`** — an existing approved-but-unbuilt design for
   a three-agent memory system (Vault Scribe / Chronicle / The Librarian) with a five-layer retrieval
   pipeline and a phased path to DuckDB VSS-based semantic search. **Treat this as one input among
   several, not a preset conclusion.** It predates the MCP and graph-database ideas above and was
   scoped narrower (the `brain/` memory system only, not documentation or code structure). Your
   investigation should independently evaluate whether its retrieval pipeline, its agent-contract
   model, and its DuckDB VSS recommendation still hold once MCP, graph retrieval, and the
   documentation/knowledge-base scope are considered together — revise, extend, or replace pieces of
   it as your evidence indicates, and say explicitly which you did and why.
5. **`docs/09-backlog/backlog.yaml`** — search for `phase-mem-` to see the current backlog line
   (phases 01–19; 15–19 are `deferred` pending recorded retrieval failures that nothing currently
   collects — this gap is itself a finding worth addressing). Also search for `phase-idea-` and
   `phase-priv-` to understand the idea lifecycle and the confidentiality-sweep gating this touches.
6. **`brain/`** (directory) — the current, unaugmented memory store this would extend or replace:
   `brain/README.md`, `brain/index.md`, and a sample of `brain/concepts/`, `brain/decisions/`,
   `brain/entities/`, `brain/procedures/`. Note its current retrieval mechanism:
   `tools/load_context.py` (keyword search only, no semantic or graph layer yet).
7. **`schemas/memory.schema.json`** — the current memory entry shape (id, type, tags, confidence,
   scope, content, source_model, etc.), for continuity if you propose extending rather than replacing it.
8. **`docs/08-governance/systems.yaml`** — search for `sys-retrieval` and `sys-memory-agents` to see
   how retrieval and memory-agent concerns are currently scoped as system components; your plan should
   say which existing systems it extends and whether it needs a new one.
9. **`sql/001_schema.sql` and `tools/rebuild_db.py`** — how `_data/` JSON is currently projected into
   DuckDB, as the existing precedent for "source of truth in files, queryable layer derived from it."
   Any documentation/knowledge database you propose should be judged against whether it follows or
   breaks this precedent.

## 3. Hard constraints — non-negotiable regardless of what you find

- **Local-only tooling.** `_data/` in this repository holds real client engagement data and personal
  financial/health information, and `AGENTS.md` forbids adding a remote or pushing until the
  confidentiality sweep (`phase-priv-05`) completes. **Do not recommend any hosted vector database,
  hosted graph database, or API-based embedding provider that would send repository content off the
  local machine.** Every tool your plan proposes must run embedded or fully local (e.g., DuckDB's VSS
  extension, KuzuDB, a locally-run embedding model such as `nomic-embed-text` via Ollama). If a
  hosted option is clearly superior on some axis, you may name it as a rejected alternative with the
  reason, but it may not appear as a recommendation.
- **JSON/Markdown-in-files stays the source of truth.** This project's whole architecture (`_data/`
  → DuckDB, documents → `catalog.md`) is: authoritative content lives in git-tracked files a human can
  read and diff; databases are derived, rebuildable, and never hand-edited. Any knowledge/vector/graph
  store you propose must be a *projection* of file content, not a second source of truth. State
  explicitly, for every store you propose, what file(s) it is derived from and what rebuilds it.
- **No agent automates final judgment calls.** Per this repo's existing pattern (idea status can only
  reach `triaged` by automation; `reviewing`/`promoted`/`discarded` require the owner), any agent your
  plan introduces (a Librarian, a triage agent, an MCP server acting on the owner's behalf) must have
  its write authority and its autonomy boundary stated explicitly per component. Default to "proposes,
  does not apply" unless you have a specific, argued reason a component should write directly.
- **This is a personal, single-owner repository**, not a team's, and the "multi-agent coordination"
  angle in idea `000020` refers to *multiple AI agent sessions* working this repo concurrently (see
  `AGENTS.md`'s concurrent-agent protocol), not multiple human users. Design accordingly — this is not
  a multi-tenant access-control problem.

## 4. Questions your report must answer

Structure your investigation around these; do not treat them as a checklist to tick past — each needs
a reasoned answer, not just an acknowledgment.

1. **Store topology.** Does code-structure retrieval (idea `000005`, GitNexus/KuzuDB) and
   documentation/knowledge retrieval (`000043`/`000044`/`000045`/`000020`/`000004`) need separate
   databases, or can one embedded store (or one store per retrieval *kind* — relational, graph,
   vector — shared across both use cases) serve both? Test the "graph for structure, vector for
   semantics" framing from `000005` against the concrete tools rather than assuming it.
2. **DuckDB's own capability ceiling.** DuckDB already holds this project's relational data and has a
   VSS extension. Before adding KuzuDB or any other engine, establish concretely what DuckDB cannot
   do here (graph traversal? recursive CTEs get you partway — where do they stop being adequate for
   `depends_on`/`promoted_to`/`systems` traversal?) rather than assuming a graph database is needed
   because graphs are the natural shape of the data.
3. **Documentation front matter as a first source.** Idea `000043` observes that governed-document
   front matter (`depends_on`, `systems`, `status`, etc.) is validated but never projected into a
   queryable form, unlike `_data/`. Evaluate whether this relational/structured half should be built
   *before* any vector or graph layer — it's the cheapest, most precedented piece (same pattern as
   `sql/001_schema.sql` + `rebuild_db.py`) and may resolve a meaningful fraction of retrieval needs
   (e.g., idea `000002`'s "what does an agent consult first" problem) on its own.
4. **Embedding model.** Which locally-runnable embedding model fits this corpus (markdown documents,
   JSONL event logs, session transcripts) — evaluate at least one option and state its resource
   requirements (does it need a GPU, how slow is CPU inference for this corpus size, does it run
   inside `uv`'s existing Python environment or require a separate runtime like Ollama).
5. **MCP server: what it's for and what it isn't.** Idea `000020` bundles several things under "MCP
   server" — (a) exposing the knowledge store to Claude Code / other assistants for querying, and
   (b) mediating this repo's own multi-agent coordination (backlog claims, worktree checkout,
   collision detection, a kill-switch). **Evaluate these as separable proposals.** Retrieval-over-MCP
   is a comparatively contained, well-precedented pattern (GitNexus already does it per idea `000005`).
   Coordination-over-MCP replaces a working file-based locking system (`backlog.yaml` +
   `src/governance`) with a live service, which is a materially larger and riskier change. Your plan
   may recommend building the former without the latter, or propose both as separate phases/tracks —
   but do not treat "build an MCP server" as one undifferentiated deliverable when the two use cases
   have very different risk profiles.
6. **Retrieval failure evidence gate.** `phase-mem-15` through `phase-mem-19` are currently `deferred`
   in this repo's own backlog because they require *recorded retrieval failures* before a semantic
   layer is justified, and idea `000004` notes nothing currently collects that evidence. Does your
   plan's sequencing respect this gate (build measurement before or alongside the semantic layer,
   per the existing `phase-mem-10` "measure keyword and tag retrieval quality" phase), or does your
   evidence suggest the gate should be revised? Either answer is acceptable — state which and why.
7. **Migration and sync.** Every proposed store must state how it stays in sync with hand-edited
   source (markdown front matter edited by a person, `_data/ideas.jsonl` appended to) without becoming
   a second thing that drifts, matching the staleness-check precedent already in place for
   `catalog.md`.
8. **What NOT to build.** At least one of the eight ideas, or some scope within them, may not be worth
   building given what you find (e.g., a graph database that duplicates what recursive SQL already
   handles, or an agentic RAG refinement loop with no evidence base yet). Say so if you find it — a
   report that recommends building everything proposed has not actually evaluated the tradeoffs.

## 5. Deliverable

Write **one file**: `docs/00-working/gemini-knowledge-retrieval-report.md`.

Structure it as:

1. **Summary** — the recommended architecture in a few paragraphs: what store(s), what they hold,
   what's derived from what, whether code-graph and knowledge-base share tooling, whether and what
   kind of MCP server is recommended.
2. **Findings**, one subsection per question in section 4, each ending in a stated conclusion (not
   just a survey of options).
3. **Rejected alternatives** — what you considered and ruled out, and why, including any hosted
   option ruled out solely on the local-only constraint (state that plainly, don't bury it).
4. **Proposed multi-phase plan** — an ordered sequence of phases, each with:
   - a short title and what it delivers
   - its dependency on earlier phases in your sequence
   - which existing idea(s) (`000002`/`000004`/`000005`/`000007`/`000020`/`000043`/`000044`/`000045`)
     and which existing plan/backlog item (`PLAN-001`, `phase-mem-*`) it supersedes, extends, or
     leaves untouched — be explicit, since whoever promotes this into a governed plan will need to
     reconcile it against what already exists
   - what would demonstrate the phase is done (you don't need this repo's exact verification-command
     format, but state a concrete, checkable condition)
5. **Open questions for the owner** — anything you could not resolve from the source material and
   that needs a human decision before implementation (this repo's own convention, per `AGENTS.md`'s
   GOV-006 import, is to flag rather than guess on anything that changes what gets built).

Do not create, modify, or delete any other file in this repository. Do not write code. This is a
research and design deliverable only.
