---
schema_version: 1
id: doc-adr-file-based-governance
code: ADR-001
title: 'ADR-001: File-based governance with separate memory metadata'
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-governance, sys-brain]
depends_on: []
---

# ADR-001: File-based governance with separate memory metadata

## Context

The repository already uses files as durable state and DuckDB as a disposable projection. Its memory front matter has a strict existing schema, while its plans and architecture documents have no common metadata. Narrative inventories mix implemented scaffolds with ambitious proposals. A useful governance system must work before a running API, database, or agent service exists.

## Decision

Store document lifecycle metadata in Markdown, keep component identity in one YAML registry, and derive plan inventories with a read-only Python command. Use Draft-07 JSON Schemas, matching the existing schema convention, plus semantic checks for references, dates and graphs. Add `jsonschema` only to development dependencies; the runtime application does not import governance.

Keep `schemas/memory.schema.json` unchanged. Validate memories separately and retain their existing IDs, provenance and repository-scope `project: d-system`. Do not force document fields into the brain loader. Governance metadata is development tooling, not a new business entity: it needs no DuckDB table, DDL migration, or API Pydantic model. This is the explicit exception to the otherwise applicable entity schema → DDL → model workflow.

Migrate existing substantive docs in place. Preserve historical paths, author content, and the user's execution prompt. Record existing unimplemented plans as drafts. Add navigation links rather than rewriting the user's modified README. Owner acceptance and historical lifecycle checks remain Git-review responsibilities; the command checks current-state integrity.

## Alternatives considered

| Alternative | Reason not selected |
|---|---|
| One universal schema for memories and documents | Breaks the existing strict memory contract and conflates confidence with approval |
| DuckDB-backed governance registry | Creates another projection to rebuild before basic repository checks can run |
| External catalog, wiki or agent orchestrator | Adds service dependencies and duplicate authority at this repository's present scale |
| Grandfather all existing docs indefinitely | Leaves the current plans invisible to the very checks intended to govern them |
| Parse every Markdown link and infer ownership from paths | Higher complexity; references inside design examples are often intentionally nonexistent |

## Consequences

The registry is small and manually curated; plan lists are generated. Schemas and Python semantics must evolve together with tests. Memory lifecycle enrichment and data-loader validation remain separate future changes. A passing check establishes structural consistency, not truth or user approval. The accepted status records this implementation choice under the requested governance task; it does not claim an additional review occurred.

## Revisit when

Reconsider the owner map when there are multiple maintainers, the schema boundary when the memory loader needs lifecycle fields, and catalog storage when measured repository checks or cross-repository discovery exceed a simple local scan. Scale based on observed friction, not project-count guesses.
