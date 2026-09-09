# Brain — Shared Memory Index

Model-agnostic knowledge base. Entries are readable and writable by any AI model (Claude, GPT-4o, Gemini, or others) and by humans. Source of truth for cross-session, cross-model context continuity.

Each entry is a Markdown file with YAML frontmatter. Loaded into DuckDB by `tools/rebuild_db.py`. Retrieved via `tools/load_context.py`.

---

## Entry Types

| Type | Meaning | Example |
|---|---|---|
| `concept` | How something works or why it was designed a certain way | Architecture patterns, design decisions |
| `entity` | Facts about a specific thing (project, tool, person, org) | Project overviews, tool capabilities |
| `procedure` | Step-by-step: how to do something | Runbooks, workflows, onboarding |
| `episode` | What happened in a session or event | Decisions made, context from a meeting |
| `decision` | Why a specific choice was made (ADR-style) | Why DuckDB over Postgres, why JSON-first |

---

## Directory Structure

```
brain/
  concepts/     ← how things work
  entities/     ← facts about specific things
  procedures/   ← how to do things
  episodes/     ← what happened
  decisions/    ← why things were chosen
```

---

## Memory Inventory

### Concepts
- [JSON Source-of-Truth Pattern](concepts/json-source-of-truth-pattern.md)
- [Tag Taxonomy](concepts/tag-taxonomy.md)
- [Mini Systems Architecture](concepts/mini-systems-architecture.md)

### Entities
- [d-system Overview](entities/d-system-overview.md)

### Procedures
- [Add a New Project](procedures/add-new-project.md)
- [Add a Brain Memory Entry](procedures/add-brain-memory.md)
- [Verify Before Claiming Ignorance](procedures/verify-before-claiming-ignorance.md)
- [Handling /session-close When No Phase Is Active](procedures/session-close-with-no-active-phase.md)
- [Resolving Staged Idea-Triage Follow-ups via AskUserQuestion](procedures/resolve-idea-triage-followups.md)

### Episodes
*(none yet — add session summaries here)*

### Decisions
- [Why JSON-First with DuckDB as Derived Layer](decisions/json-first-duckdb-derived.md)

---

## How to Add an Entry

1. Create `brain/<type>/<slug>.md`
2. Add YAML frontmatter (see `schemas/memory.schema.json` for all fields)
3. Write the content body in Markdown
4. Add to this index under the right type heading
5. Run `uv run python tools/rebuild_db.py` to sync to DuckDB

## How to Load Context into Any Model

```bash
# By keyword
uv run python tools/load_context.py --query "DuckDB"

# By project
uv run python tools/load_context.py --project example-project

# By type
uv run python tools/load_context.py --type procedure

# By tag
uv run python tools/load_context.py --tags python,frameworks

# Combine
uv run python tools/load_context.py --query "memory" --type concept --limit 5
```

Output is plain Markdown — paste into any model's context window.
