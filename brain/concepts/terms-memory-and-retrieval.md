---
id: mem-concept-terms-memory-and-retrieval
title: Memory and Retrieval
type: concept
tags: []
systems: [sys-brain, sys-retrieval]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-07
confidence: high
related: [mem-concept-terms-data-and-storage]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).

### Brain

The shared, model-agnostic knowledge base under `brain/` — Markdown with YAML front matter, validated
against `schemas/memory.schema.json`, readable and writable by any model. Not a second copy of
`_data/` — it holds durable facts and procedures about the system, not business records.

### Memory type

The `type` field on a brain memory, one of five schema-fixed values: `concept`, `entity`,
`procedure`, `episode`, `decision`. Not a free label — each value carries a distinct job description
embedded directly in `schemas/memory.schema.json`.

### Concept (memory type)

A memory describing how something works — this document is one. Not a business record and not a
rationale for a choice; a rationale is a `decision` memory.

### Entity (memory sense)

A memory holding facts about a specific thing, e.g. `mem-entity-d-system`. Not a domain-data entity
(see Data and Storage) and not itself validated as a schema-governed record — it is a fact *about* the
system, not a row *in* it.

### Procedure (memory type)

A memory describing how to do something, step by step, e.g. `brain/procedures/add-brain-memory.md`.
Not a governed operation document (`kind: operation`, the `OPS` series) — an operation document
additionally states a trigger, expected result and failure/recovery steps for CI or ops use; a
procedure memory does not.

### Episode (memory type)

A memory describing what happened — a specific, dated event. Not a standing rule and not a fact
expected to generalize beyond the moment it records.

### Decision (memory type)

A memory describing why something was chosen. Not an ADR — an ADR is a governed document with a code
and a lifecycle; a decision memory is informal and needs neither to be recorded.

### Scope (memory field)

Whether a memory applies `global`ly, to one `project`, or is `session`-scoped pending review for
promotion to global. Not the same as a document's `status`, which tracks lifecycle rather than where
a memory applies.

### Confidence

How reliable a memory is: `high`, `medium`, `low`, or `uncertain`. Not a lifecycle state and not proof
that whatever the memory describes is implemented — mutable claims are verified against code
regardless of confidence.

### Source model

The `source_model` field recording which model or human authored or last substantively edited a
memory, as `provider/model-id` or `human`. Not a claim about correctness — provenance only.
