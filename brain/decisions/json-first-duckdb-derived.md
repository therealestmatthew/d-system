---
id: mem-decision-json-first
title: Why JSON-First with DuckDB as Derived Layer
type: decision
tags: [frameworks, knowledge-base, python]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-05
confidence: high
related: [mem-concept-json-sot]
scope: global
---

## Decision

Use human-readable JSON files in `_data/` as the source of truth. DuckDB is rebuilt from those files on demand and is gitignored. Memories in `brain/` use Markdown with YAML frontmatter.

## Context

This is a personal system operated by one person, frequently in collaboration with AI models (Claude, GPT-4o, Gemini). The system needed to:
- Survive database corruption without data loss
- Be readable and editable by any AI model without tool access to a running database
- Be version-controlled with meaningful diffs
- Support cross-model collaboration on shared repos

## Alternatives Considered

| Alternative | Problem |
|---|---|
| DuckDB as primary store | Binary file — not diffable, not human-readable, AI can't safely edit without SQL tools |
| SQLite | Same binary/non-diffable problem |
| Plain Markdown only | Hard to query or aggregate across many entries |
| Postgres | Requires a running server, overkill for a personal tool |

## Consequences

**Positive:**
- Any AI model can read and write `_data/` JSON files directly
- Git history shows meaningful diffs per entity
- Database corruption loses nothing — just rebuild
- No server to manage

**Negative:**
- Multi-step write: edit JSON, then run rebuild
- No real-time queries against in-flight writes
- YAML/JSON discipline required — malformed files break the rebuild

## When to Revisit

If the system grows to multiple concurrent users or requires real-time write consistency, migrate to a proper database with the JSON files as the migration source.
