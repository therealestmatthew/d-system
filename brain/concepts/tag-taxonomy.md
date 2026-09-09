---
id: mem-concept-tag-taxonomy
title: Tag Taxonomy
type: concept
tags: [frameworks, knowledge-base]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-05
confidence: high
related: [mem-concept-json-sot]
scope: global
---

## Summary

Tags are the primary cross-cutting classification axis. Projects have one `category` and one `type` (both fixed enums), but unlimited tags for nuanced multi-dimensional classification.

## Tag Categories (6)

| Category | Describes | Examples |
|---|---|---|
| `client` | A specific organization | `google` |
| `platform` | A named external service | `anaplan`, `aws`, `claude` |
| `tech` | A language or library | `python`, `react`, `selenium` |
| `domain` | A knowledge area | `data-science`, `security`, `wellness` |
| `methodology` | An approach or framework | `agentic-systems`, `code-gen`, `frameworks` |
| `context` | A situational qualifier | `hackathon`, `side-gig` |

## Key Rules

- **Tag IDs are permanent.** Renaming a tag ID silently breaks all project JSON that references it.
- **Deprecate, never delete.** Set `"deprecated": true` in `_data/tags.json`. The tag stays valid on existing data.
- **Minimum tags that fully describe the project.** Over-tagging dilutes signal.
- **Specific beats general.** Use `playwright` over just `automation` when the project actually uses Playwright.
- **All tags must exist in `_data/tags.json` before use.** Never add a tag ID to a project JSON without first defining it.

## Source of Truth

`_data/tags.json` — 28 tags as of 2026-09-05. Full documentation in `docs/07-architecture/ARCH-001-tagging-system.md`.

## DuckDB Queries

```sql
-- Projects with a tag
SELECT id, name FROM projects WHERE list_contains(tags, 'claude');

-- Tag co-occurrence (projects sharing two tags)
SELECT id, name FROM projects
WHERE list_contains(tags, 'python') AND list_contains(tags, 'automation');

-- Tags by category
SELECT id, label FROM tags WHERE category = 'methodology' AND deprecated = false;
```
