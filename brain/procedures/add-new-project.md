---
id: mem-proc-add-project
title: Add a New Project
type: procedure
tags: [frameworks, python]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-08
confidence: high
related: [mem-concept-json-sot, mem-concept-tag-taxonomy]
scope: global
---

## Steps

**1. Create the project JSON file**

Per [ADR-009](../../docs/04-decisions/ADR-009-structure-content-boundary.md), where this file goes
depends on whether the project is real:

- **A real project** (the owner's actual work) goes under the resolved data root — on the owner's
  machine that's `_private/portfolio/projects/<kebab-id>.json`, since `D_SYSTEM_DATA_ROOT` is set to
  `_private/portfolio`. Never write real project content into the tracked `_data/`.
- **A fictional/example project** (extending the tracked worked-example set) goes in
  `_data/projects/<kebab-id>.json` directly — that tree must stay real-content-free.

```bash
# Real:       _private/portfolio/projects/<kebab-id>.json  (gitignored)
# Fictional:  _data/projects/<kebab-id>.json                (tracked)
```

Minimum required fields:
```json
{
  "id": "my-new-project",
  "name": "My New Project",
  "status": "active",
  "category": "work",
  "type": "project",
  "description": "One or two sentences.",
  "tags": ["python", "frameworks"],
  "stakeholders": [],
  "started": null,
  "target_date": null,
  "last_reviewed": "YYYY-MM-DD",
  "review_cadence": "weekly",
  "notes": ""
}
```

**2. Validate tags**

Every tag ID in `"tags"` must exist in `_data/tags.json`. If a tag is missing, add it first:
```json
{
  "id": "new-tag",
  "label": "New Tag",
  "category": "methodology",
  "description": "What this tag covers.",
  "related": [],
  "deprecated": false
}
```

**3. Rebuild DuckDB**

```bash
uv run python tools/rebuild_db.py                                    # fictional set
D_SYSTEM_DATA_ROOT=_private/portfolio uv run python tools/rebuild_db.py  # real records
```

Verify the project appears:
```bash
uv run python -c "
import duckdb
c = duckdb.connect('data/d_system.duckdb')
print(c.execute(\"SELECT id, name, status FROM projects WHERE id = 'my-new-project'\").fetchall())
"
```

**4. (Optional) Add a brain memory entry**

If this project has architectural decisions or unique context worth preserving across sessions, add `brain/entities/<slug>.md`.

## Rules

- `id` is permanent — use a stable slug, never rename
- `status` starts as `"active"` or `"planning"` for new projects
- `last_reviewed` should be today's date when creating
- Do not add the project to DuckDB directly — always edit the JSON file first
