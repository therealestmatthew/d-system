---
schema_version: 1
id: doc-session-schema-architecture-review
code: SESS-2026-09-17-02
title: Adversarial schema architecture review recorded
kind: session
status: active
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
systems: [sys-contracts, sys-portfolio, sys-capture, sys-projection, sys-governance]
depends_on: [doc-schema-architecture-review, doc-schema-catalog, doc-organizational-and-wbs-data-model, doc-architecture-overview]
---

# Adversarial schema architecture review recorded

This owner-directed, unclaimed review inspected the public schema files, tracked example source
paths, source validation, capture/governance validators, DuckDB DDL and rebuild loader, and the
organizational/WBS architecture documents. `_private/` was not read.

## Outcome

Delivered [ARCH-009](../07-architecture/ARCH-009-schema-architecture-review.md), allocated from
the architecture series. The artifact inventories all 20 schema files with their source,
validation, loader/consumer and projection status; records contradictions between the current
legacy model and ARCH-007/ARCH-008; proposes eight missing contracts beyond ARCH-008; and contains a
machine-readable JSON link map with 40 proposed shared-dimensionality links.

The review did not alter ARCH-007 or ARCH-008, add schemas, change DDL/loaders, or update the
glossary. It recommends those as separately governed follow-up work.

## Findings carried forward

- `person.projects` and `project.stakeholders` are competing relationship inputs; the loader only
  projects the former.
- Party-bearing fields remain person-shaped strings or unresolved names, so a shared PartyRef and
  an explicit unresolved-party lifecycle are prerequisites for the planned organization model.
- `opportunity-party`, `engagement-party`, `wbs-baseline`, and `work-dependency` are missing from
  the catalog even though the architecture requires their relationship dimensions.
- Source preflight and DuckDB loading do not yet resolve optional IDs or enforce foreign keys.
- ARCH-001, ARCH-002 and ARCH-004 contain dated counts/descriptions that should be refreshed only
  by an owner-reviewed documentation change.

## Verification

- Embedded link map parsed as JSON: 40 links, schema map version 1.
- `uv run python -m src.governance`: passed — `Governance OK: 31 systems, 279 documents, 26 memories, 278 backlog phases`.
- `uv run python -m src.governance --catalog`: passed after the dedicated worktree received the
  required filesystem approval; `docs/08-governance/catalog.md` now includes ARCH-009 and this
  session record.
- The initial unprivileged catalog attempt failed because the sandbox could not create the
  repository's temporary catalog file in the sibling worktree; no repository content was changed
  by that failed attempt.
- `uv run pytest -q`: 628 passed, 1 failed. The failure is the pre-existing generated-output drift
  check `test_the_committed_markdown_matches_regenerated_output`: uncommitted `_data/ideas.jsonl`
  contains new idea events while `docs/00-working/ideas.md` has not been regenerated. That
  unrelated generated file was intentionally not changed or staged.
