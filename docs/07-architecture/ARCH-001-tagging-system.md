---
schema_version: 1
id: doc-tagging
code: ARCH-001
title: Tagging System
kind: architecture
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems:
- sys-portfolio
- sys-contracts
depends_on: []
---

# Tagging System

Tags are the primary cross-cutting classification axis in d-system. A project can belong to only one `category` and one `type`, but it can carry any number of tags — which is where nuanced, multi-dimensional classification lives.

---

## Where Tags Live

| Artifact | Location | Purpose |
|---|---|---|
| Tag definitions | `_data/tags.json` | Source of truth — all valid tags defined here |
| Tag schema | `schemas/tag.schema.json` | Validation rules for entries in `_data/tags.json` |
| Tag references on projects | `_data/projects/<id>.json` → `tags: [...]` | Array of tag IDs |
| DuckDB (derived) | `tags` table + `project_tags` junction | Query and filter; rebuilt via `tools/rebuild_db.py` |

---

## Tag Structure

Each tag has five fields:

```json
{
  "id":          "agentic-systems",
  "label":       "Agentic Systems",
  "category":    "methodology",
  "description": "Multi-agent orchestration, agentic workflows, and autonomous AI system design.",
  "related":     ["ai-tools", "claude", "automation", "frameworks"],
  "deprecated":  false
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | Yes | Kebab-case, **never renamed** after first use — renaming silently breaks all project references |
| `label` | Yes | Human-readable display name |
| `category` | Yes | One of 6 fixed values (see below) |
| `description` | No | One sentence clarifying scope; distinguish from similar tags |
| `related` | No | Other tag IDs for discovery; not a hierarchy — just semantic neighbors |
| `deprecated` | No | If `true`: tag stays valid on existing projects but must not be added to new ones |

---

## Tag Categories

Six mutually exclusive categories organize tags by *what kind of thing they describe*:

### `client`
A specific organization you work with or for. Client tags never describe technology or methodology.

> Example: `client-a`

### `platform`
A named, external product or service. Distinguished from `tech` by being a *service you use*, not a *language/library you write*.

> Examples: `anaplan`, `aws`, `claude`, `cloud`

### `tech`
A programming language, library, or tool that produces artifacts. Code you write *in* or code you *call directly*.

> Examples: `python`, `typescript`, `react`, `selenium`, `playwright`, `html`

### `domain`
A knowledge area or professional discipline. Tags a project by *what it's about*, not how it's built.

> Examples: `data-science`, `security`, `finance`, `wellness`, `consulting`, `education`

### `methodology`
An approach, practice, or framework. How work gets done — spans tools and domains.

> Examples: `agentic-systems`, `automation`, `code-gen`, `frameworks`, `building-blocks`, `prompt-engineering`, `templates`, `ai-tools`

### `context`
Situational or circumstantial qualifiers that don't fit other categories — event types, work arrangements.

> Examples: `hackathon`, `side-gig`

---

## Full Tag Inventory (27 tags)

### Client
| ID | Label | Description |
|---|---|---|
| `client-a` | Client A | A named client engagement — real identity kept out of the tracked structure |

### Platform
| ID | Label | Description |
|---|---|---|
| `anaplan` | Anaplan | Anaplan connected planning platform |
| `aws` | AWS | Amazon Web Services cloud platform |
| `claude` | Claude / Anthropic | Anthropic Claude AI — models, APIs, Claude Code |
| `cloud` | Cloud | Cloud computing in general (use `aws` when platform is known) |

### Tech
| ID | Label | Description |
|---|---|---|
| `html` | HTML / Web | HTML generation, web page structure, templating |
| `playwright` | Playwright | Microsoft Playwright browser automation library |
| `python` | Python | Python language — backend, scripting, data, automation |
| `react` | React / TypeScript | React frontend framework, paired with TypeScript |
| `selenium` | Selenium | Selenium browser automation library |
| `typescript` | TypeScript | TypeScript language — primarily React frontend |

### Domain
| ID | Label | Description |
|---|---|---|
| `consulting` | Consulting | Client-facing consulting and professional services |
| `data-science` | Data Science | Data science, ML, statistical analysis, analytics |
| `education` | Education | Teaching, facilitation, curriculum design |
| `finance` | Finance | Financial management, budgeting, debt reduction |
| `security` | Security & Cyber | Security design principles, threat modeling |
| `wellness` | Wellness | Physical health, mental health, fitness, mindfulness |

### Methodology
| ID | Label | Description |
|---|---|---|
| `agentic-systems` | Agentic Systems | Multi-agent orchestration and autonomous AI system design |
| `ai-tools` | AI Tools | AI tooling and integrations — broader than any single platform |
| `automation` | Automation | Process automation, scripting, workflow orchestration |
| `building-blocks` | Building Blocks | Reusable components, snippets, patterns for cross-project leverage |
| `code-gen` | Code Generation | Artifact and code generation systems |
| `frameworks` | Frameworks | Framework and architecture design — reusable structural patterns |
| `prompt-engineering` | Prompt Engineering | Prompt design, optimization, versioning for LLMs |
| `templates` | Templates | Document, HTML, and code templates |

### Context
| ID | Label | Description |
|---|---|---|
| `hackathon` | Hackathon | Time-boxed competitive or collaborative build events |
| `side-gig` | Side Gig | Income-generating work outside primary employment |

---

## Tagging Rules

### When adding tags to a project
1. **Use the minimum number of tags that fully describe the project.** Over-tagging dilutes the signal.
2. **Never invent a tag inline in a project JSON** — add it to `_data/tags.json` first, then reference it.
3. **Prefer specific over general.** Use `playwright` instead of (or in addition to) `automation` when the project specifically uses Playwright.
4. **Do not tag the category.** If a project is `category: "work"`, don't add a `consulting` tag just because it's work — only add it if consulting delivery is a meaningful aspect of the project.

### When creating a new tag
1. Check that no existing tag covers the concept — use `related` fields to find near-misses.
2. Assign a `category` before adding — if you can't categorize it, the concept may not deserve its own tag.
3. Write a `description` that distinguishes it from similar tags.
4. Populate `related` with at least one existing tag.
5. Run `uv run python tools/rebuild_db.py` after updating `_data/tags.json`.

### When retiring a tag
Set `"deprecated": true` in `_data/tags.json`. Do **not** remove tag IDs or remove the tag from existing project JSONs — that would break historical queries. Deprecated tags are invisible in new-project UI but remain valid in data.

---

## Querying Tags in DuckDB

```sql
-- Projects with a specific tag (array column)
SELECT id, name, status
FROM projects
WHERE list_contains(tags, 'agentic-systems');

-- All projects grouped by their tags (junction table)
SELECT t.label, count(*) AS project_count
FROM project_tags pt
JOIN tags t ON pt.tag_id = t.id
GROUP BY t.label
ORDER BY project_count DESC;

-- Projects sharing two or more specific tags
SELECT p.id, p.name
FROM projects p
WHERE list_contains(p.tags, 'claude')
  AND list_contains(p.tags, 'python');

-- All tags in a category
SELECT id, label, description
FROM tags
WHERE category = 'methodology'
  AND deprecated = false
ORDER BY label;
```

---

## Design Rationale

Tags were chosen over a pure hierarchical taxonomy because this project portfolio is inherently multi-dimensional — a project like `example-web-platform` is simultaneously `client:client-a`, `tech:react`, and `tech:typescript`. A hierarchy forces a single spine; tags don't.

The `category` field on tags adds just enough structure to prevent the flat list from becoming a dumping ground, without imposing the rigidity of nested categories on projects themselves.

The `related` field is intentionally non-hierarchical — it's a graph edge, not a parent-child link. Two tags can be mutually related without either being the "parent."
