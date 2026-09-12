---
id: mem-concept-terms-documents-and-governance
title: Documents and Governance
type: concept
tags: []
systems: [sys-governance]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-08
confidence: high
related: [mem-concept-terms-plans-and-work]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).

### Governed document

A Markdown file under `docs/` carrying YAML front matter validated against
`schemas/document.schema.json` — a permanent code, kind, status, owner and dates. Not every Markdown
file in the repository: `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/00-working/` and `_working/` are
explicitly exempt from this contract. See `docs/08-governance/GOV-001-protocol.md`.

### Document kind

The `kind` front-matter field selecting which taxonomy row a document belongs to — `plan`, `adr`,
`architecture`, `requirement`, `prompt`, `session`, `walkthrough`, `operation`, or `governance`. Not a
free label — it fixes the document's code series, canonical directory and required body content. See
`docs/08-governance/GOV-001-protocol.md`.

### Code

The permanent identifier prefixing a governed document's filename — a counter (`PLAN-006`, with an
optional sub-code `PLAN-003.01`) or a dated sequence (`SESS-2026-09-05-01`). Not something chosen by
reading a directory — always allocated with `--next-code`, and never reused once it reaches `main`. See
`docs/08-governance/GOV-005-document-codes.md`.

### Series

The registered family of codes for one document kind — `PLAN`, `ADR`, `ARCH`, `REQ`, `PROMPT`, `OPS`,
`GOV`, `SESS`, `WALK` — each with its own numbering mode and canonical location. Not duplicated in
code; `docs/08-governance/codes.yaml` is the only source of truth for the table.

### Catalog

The generated index of every document, code and phase state at `docs/08-governance/catalog.md`. Not
hand-maintained — it is produced by `--catalog` and CI fails on any diff between the committed file
and a fresh regeneration, the same pattern the generated glossary follows.

### Reserved code

A code claimed for a document that does not exist yet, typically because a backlog phase names it as
a future deliverable, recorded under `reserved` in `codes.yaml`. Not a document — `--next-code` skips
it, and using the number fails until the reservation is removed in the same change that adds the
document.

### Retired code

A code whose document was deleted, recorded under `retired` in `codes.yaml` so the number is never
reissued. Not the same as a `deprecated` or `superseded` document, which keeps its code — retirement
applies only when the document itself is gone.

### Governance check

The single validator, `uv run python -m src.governance`, checking document and memory front matter,
ID and reference integrity, dependency cycles, backlog coverage and concurrency safety. Not a
code-quality, test or feature-correctness check — it does not run `pytest`, rebuild the database, or
verify that a plan's claims are actually true. See `docs/08-governance/GOV-001-protocol.md`.

### Document code allocation

Running `uv run python -m src.governance --next-code <kind>` (with `--parent <doc-id>` for a child
plan) to obtain the next free code before creating a document. Not a guess or a directory listing — a
pure function of committed state, so two agents on the same commit compute the same answer. See
`docs/08-governance/GOV-005-document-codes.md`.
