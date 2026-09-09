---
schema_version: 1
id: doc-agent-memory
code: PLAN-001
title: "Agent Memory System \u2014 Design Plan"
kind: plan
status: approved
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems:
- sys-memory-agents
depends_on: []
---

> Delivery is approved in phases. The [accepted user choices](../08-governance/GOV-003-backlog-decisions.md) resolve conflicting details below; the [session backlog](../09-backlog/README.md) tracks execution and completion. This document is a design source, not evidence of implementation.

# Agent Memory System — Design Plan

**Status:** Approved for phased delivery — not yet implemented
**Date:** 2026-09-05  
**Scope:** Three specialized agents + inter-agent contracts + memory retrieval architecture + tagging strategy for retrieval

---

## Overview

The brain/ shared memory system requires a dedicated agent layer to remain healthy, accurate, and useful over time. Three agents govern this:

| Agent | Role | Direction |
|---|---|---|
| **Vault Scribe** | Memory custodian — the only agent that writes to `brain/` | Write |
| **[AgentX — see naming]** | Session analyst — extracts candidate memories from transcripts | Read → Handoff |
| **The Librarian** | Retrieval router — all agents route memory queries through here | Read → Return |

These agents are model-agnostic — they can be implemented in Claude, GPT-4o, Gemini, or any future model. Their contracts define the interface, not the implementation.

---

## Agent 1: Vault Scribe

### Mandate

Vault Scribe is the sole writer to the shared brain. It owns memory integrity, recency, relevancy, and lifecycle. No other agent or human writes directly to `brain/` — everything routes through Vault Scribe.

### Capabilities

- Full read/write access to `brain/`
- Read access to `_data/`, `schemas/`, `sql/`
- Can invoke `tools/rebuild_db.py` after writes
- Can propose memory pruning (but cannot execute without human approval)
- Can merge duplicate memories
- Can update `confidence` fields as information ages or is confirmed

### Core Responsibilities

**Intake:** Receive candidate memory batches from AgentX (or from human via direct request). For each candidate:
1. Check for duplicates against existing memories (by id, title similarity, content overlap)
2. Validate against `schemas/memory.schema.json`
3. Assign or confirm `confidence` level
4. Assign or confirm `scope` (global / project / session)
5. Ensure tags reference valid entries in `_data/tags.json`
6. Set `source_model` field to the model that generated the content

**Write:** If a candidate passes intake, Vault Scribe creates or updates the `brain/` file, updates `brain/index.md`, and triggers `rebuild_db.py`.

**Review cycle:** Periodically review all memories for:
- **Recency decay** — mark `confidence: low` for memories that haven't been confirmed in 90+ days
- **Staleness** — flag memories with facts that may have changed (e.g., project statuses, tech versions)
- **Redundancy** — identify pairs of memories with high content overlap, propose merges
- **Orphans** — memories with no `related` links and no projects referencing them

**Pruning (human-gated):** Vault Scribe may propose deletion of specific memories. It must:
1. Produce a pruning proposal listing: memory ID, reason (stale / redundant / low-confidence / never-referenced), and any replacement memory ID
2. Present the proposal for human review
3. Only execute after explicit approval — never auto-delete
4. Log the deletion in `brain/episodes/` as a record

### Invariants (must always / never)

| Always | Never |
|---|---|
| Validate against schema before writing | Write to brain/ without validation |
| Set `source_model` on every entry | Delete without human approval |
| Update `brain/index.md` after any write | Modify `episode` type entries (immutable) |
| Run rebuild_db.py after any batch of writes | Create entries with `id` already in use |
| Preserve existing `id` values | Change an existing memory's `id` |

---

## Agent 2: [AgentX — Naming TBD]

### Name Candidates

| Name | Rationale |
|---|---|
| **Chronicle** | Captures the historian role — reads what happened and structures it |
| **Session Scout** | Active, directional — scouts sessions for value |
| **The Archivist** | Classical, authoritative — processes raw records into structured history |
| **Signal** | Concise — extracts signal from noise in session transcripts |
| **Distiller** | Functional — distills sessions into memory candidates |

**Recommendation: Chronicle** — it implies both faithful capture (reading what happened) and structured output (turning it into lasting record), without implying it has write authority.

### Mandate

Chronicle reads session transcripts and other unstructured artifacts (chat logs, session notes, decision threads) and extracts candidate memories for Vault Scribe to audit and integrate. It is strictly read-only on `brain/`. It packages candidates but never writes them.

### Capabilities

- Read access to `docs/03-sessions/`, `_working/`, and any designated transcript locations
- Read access to `brain/` (to avoid proposing duplicates)
- Read access to `data/d_system.duckdb` (to query existing memories via The Librarian)
- Write access to a staging area: `_working/memory-candidates/` (temporary, not brain/)
- Can invoke The Librarian to check if a candidate already exists

### Core Responsibilities

**Trigger:** Invoked at the end of a session (manually or automatically), or pointed at a specific transcript file.

**Extraction pass:** Read the full transcript. Identify:
- **Decisions made** — why was X chosen over Y? (→ `decision` type)
- **Patterns discovered** — a technique or approach that worked (→ `concept` type)
- **Facts established** — about a project, tool, person, or system (→ `entity` type)
- **Procedures followed** — step-by-step actions taken (→ `procedure` type)
- **Significant events** — what happened in this session (→ `episode` type)

**Novelty check:** For each candidate, query The Librarian: "Does a memory covering this already exist?" If yes and the existing memory is accurate and current, discard the candidate or flag it as a potential update rather than a new entry.

**Candidate packaging:** For each novel or update-worthy candidate, produce a structured candidate object:

```json
{
  "candidate_action": "create | update",
  "target_id": null,
  "proposed_entry": {
    "id": "mem-<type>-<slug>",
    "title": "...",
    "type": "concept | entity | procedure | episode | decision",
    "tags": ["..."],
    "confidence": "high | medium | low",
    "scope": "global | project | session",
    "project": "project-id or null",
    "content": "...",
    "source_model": "provider/model-id"
  },
  "rationale": "Why this memory is worth keeping",
  "source_transcript": "path/to/transcript.md",
  "source_excerpt": "The relevant passage that generated this candidate"
}
```

**Handoff:** Pass the batch of candidates to Vault Scribe for audit. Chronicle's job ends here — it does not follow up on what Vault Scribe accepts or rejects, but Vault Scribe should log its decisions.

### Invariants

| Always | Never |
|---|---|
| Check for duplicates before proposing | Write to brain/ directly |
| Include `source_transcript` in every candidate | Create candidates without rationale |
| Package candidates as structured objects | Propose merges (that's Vault Scribe's job) |
| Invoke The Librarian for novelty checks | Auto-trigger without a session to read |

---

## Agent 3: The Librarian

### Mandate

The Librarian is the retrieval router. All other agents — and humans — route memory and context queries through The Librarian. It bears the cost of glob, grep, vector search, and DuckDB queries so callers don't need to. It returns ranked, formatted context blocks in a consistent output format regardless of which retrieval method was used internally.

### Capabilities

- Read-only access to `brain/`, `_data/`, `data/d_system.duckdb`
- Can run `tools/load_context.py` (current keyword retrieval)
- Can invoke DuckDB SQL queries
- Can invoke vector similarity search (once implemented)
- Can run grep/glob over `brain/` for exact-match lookups
- **No write access anywhere**

### Retrieval Pipeline (ordered by cost, lowest first)

```
Query arrives
    │
    ▼
Layer 1: Exact ID lookup       (O(1) — if caller knows the mem-* id)
    │ miss
    ▼
Layer 2: Tag filter            (DuckDB — fast, high precision when tags are good)
    │ insufficient results
    ▼
Layer 3: Keyword / FTS         (DuckDB ILIKE or FTS extension — moderate cost)
    │ insufficient results
    ▼
Layer 4: Semantic / vector     (embedding similarity — higher cost, higher recall)
    │ still insufficient
    ▼
Layer 5: Agentic refinement    (The Librarian rephrases query and retries layers 2-4)
    │
    ▼
Return ranked results
```

The Librarian should attempt the cheapest sufficient layer first and only escalate when the result set is below a minimum relevance threshold.

### Standard Output Format

Every response from The Librarian is a Markdown block with a consistent header:

```markdown
## Librarian Context Block
*query: [original query] | method: [tag|keyword|semantic|agentic] | retrieved: N | timestamp: ISO*

### [TYPE] Memory Title
*id:mem-xxx | confidence:high | scope:global | project:project-id*

[content]

---
*[next memory...]*
---
*End of Librarian context block*
```

This format is identical regardless of which retrieval method was used. Downstream agents do not need to know how the retrieval happened.

### Invariants

| Always | Never |
|---|---|
| Return results in the standard output format | Write to any file or database |
| Indicate which retrieval method was used | Make judgments about what to do with retrieved context |
| Return confidence level per memory | Suppress low-confidence results without flagging them |
| Escalate through layers before giving up | Return results the caller didn't ask for without flagging them |

---

## Agent Contracts

A contract defines the interface between two agents. Both sides must honor it. Contracts are versioned — changes require updating both sides.

### Contract A: Caller ↔ The Librarian

**Version:** 1.0  
**Caller:** Any agent or human  
**Provider:** The Librarian

```
REQUEST (Caller → Librarian):
{
  "query": "text description of what's needed",
  "filter_tags": ["tag-id", ...],      // optional
  "filter_type": "concept|entity|...", // optional
  "filter_project": "project-id",      // optional
  "limit": 10,                         // default 10
  "min_confidence": "low",             // default "low" (returns everything)
  "preferred_method": "auto|tag|keyword|semantic"  // default "auto"
}

RESPONSE (Librarian → Caller):
  Standard Librarian Context Block (Markdown)
  plus metadata header with method used, result count, and query echo

GUARANTEES:
  - Response always in standard format
  - Never returns zero results without an explanation
  - Always indicates retrieval method used
  - Results ranked by: confidence desc, recency desc

LIMITATIONS:
  - Does not interpret results
  - Does not filter based on caller identity
  - Cannot guarantee completeness (memory may not exist yet)
```

---

### Contract B: Chronicle ↔ Vault Scribe

**Version:** 1.0  
**Caller:** Chronicle  
**Provider:** Vault Scribe

```
REQUEST (Chronicle → Vault Scribe):
{
  "session_source": "path/to/transcript.md",
  "candidates": [
    {
      "candidate_action": "create | update",
      "target_id": "mem-xxx or null",
      "proposed_entry": { ...memory schema fields... },
      "rationale": "Why this memory is worth keeping",
      "source_excerpt": "Relevant passage from transcript"
    }
  ]
}

RESPONSE (Vault Scribe → Chronicle):
{
  "accepted": ["mem-id-1", "mem-id-2"],
  "rejected": [
    { "candidate_index": 2, "reason": "duplicate of mem-concept-json-sot" }
  ],
  "deferred": [
    { "candidate_index": 3, "reason": "requires human review before integration" }
  ]
}

GUARANTEES:
  - Every candidate receives a disposition (accepted / rejected / deferred)
  - Accepted memories are written and rebuild triggered before response
  - Rejections include a reason

LIMITATIONS:
  - Vault Scribe may rephrase or restructure accepted candidates
  - Vault Scribe may split one candidate into multiple entries
  - Vault Scribe does not guarantee same-session turnaround for deferred items
```

---

### Contract C: Vault Scribe ↔ Human (Pruning Gate)

**Version:** 1.0  
**Caller:** Vault Scribe  
**Approver:** Human

```
PROPOSAL (Vault Scribe → Human):
  A structured pruning proposal document written to:
  _working/pruning-proposals/YYYY-MM-DD-proposal.md

  Contents per candidate:
    - Memory ID and title
    - Reason: stale | redundant | low-confidence | never-referenced
    - Replacement memory ID (if redundant)
    - Last referenced date
    - Confidence level at time of proposal

APPROVAL:
  Human edits the proposal, marking each item: APPROVE | REJECT | DEFER
  Human runs: uv run python tools/apply_pruning.py _working/pruning-proposals/<file>

GUARANTEES (Vault Scribe):
  - Will not delete any memory without an APPROVE marking on the proposal
  - Will log all deletions to brain/episodes/pruning-log.md
  - Will never prune episode-type memories (permanent historical record)

LIMITATIONS:
  - Vault Scribe cannot force pruning — human is always in the loop
  - Proposals expire after 30 days if not actioned
```

---

### Contract D: Any Agent ↔ Any Agent (General Principle)

Agents do not call each other directly by implementation — they pass structured messages through a defined interface. No agent inspects another agent's internal state. No agent writes to another agent's owned resources.

**Ownership:**
| Resource | Owner | Others may |
|---|---|---|
| `brain/` | Vault Scribe | Read only |
| `_working/memory-candidates/` | Chronicle | Read only |
| `_working/pruning-proposals/` | Vault Scribe | Read only |
| DuckDB read queries | The Librarian | Also read directly if needed |
| `_data/` JSON files | Human / tools | Read |

---

## Memory Retrieval Architecture

### Current State (Phase 1)

`tools/load_context.py` implements Layer 3 (ILIKE keyword search) only. Sufficient to start. Every query hits the full memories table with a text scan.

### Target Architecture (Phase 2+)

#### Embedding Layer

Each memory entry gets an embedding vector representing: `title + " " + tags.join(" ") + " " + content[:500]`

**Embedding model options (in preference order for this stack):**

| Option | Pros | Cons |
|---|---|---|
| `text-embedding-3-small` (OpenAI) | Fast, cheap, high quality | API dependency, cost at scale |
| `text-embedding-004` (Google) | Strong multilingual, matches Gemini usage | API dependency |
| `nomic-embed-text` (local/Ollama) | No API cost, private, runs offline | Requires local GPU or CPU inference |
| Anthropic embeddings | Same provider as Claude | Not yet publicly available as standalone |

**Recommendation:** Start with `text-embedding-3-small` for speed; add `nomic-embed-text` as a local fallback for offline/private operation.

#### Vector Store Options

| Option | Fit | Notes |
|---|---|---|
| **DuckDB VSS extension** | Best fit — no new infra, same query layer | Available in DuckDB ≥0.10; 1M vectors before performance degrades |
| **LanceDB** | Arrow-native, DuckDB-compatible | Good Python integration, reasonable scale |
| **ChromaDB** | Simple Python-native | Good for prototyping, weaker at scale |
| **Qdrant** | Production-grade | Overkill until memory count is in the thousands |

**Recommendation:** DuckDB VSS for Phase 2. Store embedding vectors in an `embeddings` table alongside the `memories` table. Migrate to Qdrant if memory count exceeds 2,000 entries or retrieval latency becomes noticeable.

#### Embeddings Table (proposed DDL)

```sql
CREATE TABLE memory_embeddings (
    memory_id       VARCHAR PRIMARY KEY,  -- references memories.id
    model           VARCHAR NOT NULL,     -- embedding model used
    vector          FLOAT[1536],          -- dimension matches the model
    content_hash    VARCHAR NOT NULL,     -- SHA-256 of embedded text; detect staleness
    embedded_at     TIMESTAMP NOT NULL
);
```

#### Agentic RAG (Phase 3)

When layers 1–4 fail to return sufficient results, The Librarian enters an agentic retrieval loop:

```
1. Analyze the original query
2. Decompose into 2-3 sub-queries covering different aspects
3. Run each sub-query through layers 2-4 independently
4. Merge and deduplicate results
5. Score merged results against original query intent
6. Return top N
```

This is implemented as a small agentic loop inside The Librarian — no external orchestration needed.

---

## Tagging Strategy for Retrieval

### Problem

Tags serve two distinct purposes that can conflict:
1. **Classification** — organizing what a memory *is about*
2. **Retrieval routing** — enabling The Librarian to pre-filter before expensive search

A tag set optimized for classification may be too broad for retrieval. A tag set optimized for retrieval may be too granular to maintain.

### Design Principles

**1. Every memory must have at least one `domain` or `methodology` category tag.**
This enables The Librarian to use Layer 2 (tag filter) as a meaningful pre-filter on every query.

**2. Memories should have 2–5 tags. More than 5 is a signal the memory is trying to cover too much.**
Broad memories with 6+ tags should be split into narrower entries.

**3. Tag specificity ladder.** When tagging, prefer the most specific applicable tag:
```
automation > python > playwright   (most specific wins)
```
Only use `automation` if the memory is about automation in general, not Playwright specifically.

**4. Retrieval hint tags.** Beyond the standard taxonomy, memories can carry retrieval-hint tags that are query-pattern oriented rather than classification-oriented:

```
[how-to]        → procedure memories that answer "how do I..."
[why]           → decision memories that answer "why was this chosen"
[reference]     → entity memories that are factual lookups
[pattern]       → concept memories describing a reusable pattern
[warning]       → memories flagging a common mistake or gotcha
[deprecated]    → memories about things that no longer apply
```

These retrieval hints are separate from the domain/methodology/tech/etc. classification tags. They allow The Librarian to answer "show me warnings about python" or "show me how-to memories for automation."

**5. Required tag sets by memory type:**

| Type | Required tag category | Recommended hint tag |
|---|---|---|
| `concept` | At least one: `tech`, `methodology`, or `domain` | `[pattern]` or `[reference]` |
| `entity` | At least one: `client`, `platform`, or `project-scoped` | `[reference]` |
| `procedure` | Domain or tech tag for what the procedure applies to | `[how-to]` |
| `episode` | Project tag or `scope: project` | *(none required)* |
| `decision` | The system or domain affected | `[why]` |

**6. Tag the retrieval trigger, not just the content.**
Ask: "What query would make someone want this memory?" and ensure that query's key terms appear in the tags.
- A memory about "why DuckDB was chosen over Postgres" should have tags `[why]`, `frameworks`, and ideally a note mentioning the alternative considered — because someone searching "Postgres" should still find it.

---

## Proposed Implementation Sequence

| Phase | Deliverable | Dependency |
|---|---|---|
| **Phase 1** | Chronicle and Vault Scribe as prompt-based agents (no code) | Current brain/ + load_context.py |
| **Phase 2** | The Librarian as a tool-calling agent with DuckDB + keyword retrieval | Phase 1 operating |
| **Phase 3** | Embedding layer: memory_embeddings table + DuckDB VSS | Stable memory corpus (50+ entries) |
| **Phase 4** | Semantic search in The Librarian (Layer 4 of pipeline) | Phase 3 |
| **Phase 5** | Agentic RAG loop in The Librarian (Layer 5) | Phase 4 + sufficient memory density |
| **Phase 6** | `tools/apply_pruning.py` + automated Vault Scribe review cycle | Phase 4 |

Phase 1 can begin immediately — Chronicle and Vault Scribe are initially roles to be played by a human-directed AI session, not autonomous code. The contracts define their behavior; the code comes later.

---

## Open Questions (to resolve before Phase 3)

1. **Embedding model commitment** — which provider is primary? Cost, privacy, and offline-capability trade-offs to evaluate.
2. **Retrieval hint tags** — are these maintained in `_data/tags.json` alongside domain tags, or in a separate hints registry? Mixing them risks polluting the classification taxonomy.
3. **Chronicle trigger** — is Chronicle invoked manually at end of session, or is there an automatic hook when a session file is written to `docs/03-sessions/`?
4. **Memory promotion** — how does a `scope: session` memory get promoted to `scope: global`? Who initiates, and on what cadence?
5. **Multi-model provenance** — when GPT-4o and Claude write conflicting memories on the same topic, how does Vault Scribe resolve? Priority rules? Human escalation always?
6. **AgentX final name** — Chronicle is the recommendation; confirm or choose alternative before any implementation begins.
