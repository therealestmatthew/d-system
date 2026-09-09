---
id: mem-proc-add-memory
title: Add a Brain Memory Entry
type: procedure
tags: [knowledge-base, frameworks]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-05
confidence: high
related: [mem-proc-add-project, mem-concept-json-sot]
scope: global
---

## Steps

**1. Choose the right directory and type**

| You want to capture... | Directory | Type |
|---|---|---|
| How something works | `brain/concepts/` | `concept` |
| Facts about a specific thing | `brain/entities/` | `entity` |
| How to do something | `brain/procedures/` | `procedure` |
| What happened in a session | `brain/episodes/` | `episode` |
| Why a choice was made | `brain/decisions/` | `decision` |

**2. Create the file**

```
brain/<type>/<descriptive-slug>.md
```

**3. Write the frontmatter**

```yaml
---
id: mem-<type>-<slug>         # e.g. mem-concept-duckdb-views
title: Human Readable Title
type: concept                  # concept|entity|procedure|episode|decision
tags: [python, frameworks]     # from _data/tags.json
source_model: anthropic/claude-sonnet-4-6   # or openai/gpt-4o, google/gemini-2.0-flash, human
project: project-id            # or null for global
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high               # high|medium|low|uncertain
related: [mem-other-id]
scope: global                  # global|project|session
---
```

**4. Write the body in Markdown**

Plain Markdown — no model-specific formatting. This body will be read by Claude, GPT-4o, Gemini, and humans.

**5. Add to `brain/index.md`**

Add a line under the correct type heading:
```markdown
- [Title](type/filename.md)
```

**6. Rebuild DuckDB**

```bash
uv run python tools/rebuild_db.py
```

**7. Verify retrieval**

```bash
uv run python tools/load_context.py --query "your topic"
```

## Confidence Guidelines

| Level | Use when |
|---|---|
| `high` | Verified, stable, well-understood |
| `medium` | Believed accurate, not fully validated |
| `low` | Uncertain, based on inference or partial information |
| `uncertain` | Needs verification before acting on it |
