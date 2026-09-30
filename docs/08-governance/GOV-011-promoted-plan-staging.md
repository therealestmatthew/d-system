---
schema_version: 1
id: doc-promoted-plan-staging-protocol
code: GOV-011
title: Promoted-plan staging protocol
kind: governance
status: active
owner: repository-owner
created: '2026-09-29'
updated: '2026-09-29'
systems: [sys-governance, sys-backlog]
depends_on: [doc-promoted-plan-staging, doc-idea-staging, doc-document-code-protocol]
---

# Promoted-plan staging protocol

The rationale is in [ADR-019](../04-decisions/ADR-019-promoted-plan-staging.md); this document
states the operational rules. It applies whenever an idea is promoted to a plan or requirement, per
[ADR-010](../04-decisions/ADR-010-idea-staging.md).

## Location

A promoted plan or requirement is drafted at:

```
docs/00-working/promoted/<code>-<slug>.md
```

using the code reserved for it, before that code has a document anywhere else. `docs/00-working/`
is tracked and ungoverned under ADR-010, so the draft is visible to every worktree but carries no
front-matter or catalog obligation while it is being written.

## Steps

1. **Reserve the code**, using GOV-005's existing mechanism — an entry under `reserved` in
   [codes.yaml](codes.yaml) naming the reason and the claiming phase. This is the same reservation
   GOV-005 already defines; no second reservation mechanism exists for this case.
2. **Draft at `docs/00-working/promoted/<code>-<slug>.md`.** The filename carries the reserved code
   from the start, so the eventual move does not rename the file.
3. **On completion, move the file** — unchanged filename — into its registered location
   (`docs/01-plans/` for `PLAN`, `docs/06-requirements/` for `REQ`), fill in the front matter the
   schema requires, and **remove the reservation entry from `codes.yaml` in the same change**. This
   is GOV-005's existing rule that using a reserved code requires removing the reservation in the
   change that adds the document; nothing new is added here.
4. **On abandonment**, delete the file from `docs/00-working/promoted/` and release the reservation:
   ```bash
   uv run python -m src.governance --release-code <code>
   ```
   Both steps happen together. A reservation left standing after its draft is deleted holds a code
   nothing will ever use; a deleted draft whose reservation survives leaves a phantom claim in
   `codes.yaml` that blocks the code from ever being reused for a genuine future document of that
   kind.

## What this does not change

- GOV-005's reservation mechanism, its expiry, and its manual-release command are unchanged. This
  protocol only names when a promoted-plan draft uses them.
- `docs/00-working/`'s exemption from the governance check (`EXEMPT_DIRS` in
  `src/governance/__main__.py`) already covers `docs/00-working/promoted/`; no code change was
  needed to introduce this location.
- The idea's own status in `_data/ideas.jsonl` is untouched by whether its resulting draft is
  finished or abandoned. `promoted` already records the owner's decision; this protocol governs only
  the document that decision produced.
