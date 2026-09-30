---
schema_version: 1
id: doc-promoted-plan-staging
code: ADR-019
title: Draft a promoted plan in staging under its reserved code
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-29'
updated: '2026-09-29'
systems: [sys-governance, sys-backlog]
depends_on: [doc-idea-staging, doc-document-code-protocol]
---

# Draft a promoted plan in staging under its reserved code

## Context

[ADR-010](ADR-010-idea-staging.md) defines `docs/00-working/` as ungoverned staging for an idea that
has not yet become work, and states that an idea ends in a status: `promoted` into a plan or
requirement, or `discarded`. It stops there. It does not say where the promoted document's draft
lives between the owner deciding an idea should become a plan and that document existing, with a
code, in `docs/01-plans/`.

Two existing mechanisms are adjacent but do not answer this:

- [GOV-005](../08-governance/GOV-005-document-codes.md) lets a code be reserved before its document
  is written, recorded under `reserved` in `codes.yaml` with a reason and a claiming phase. It says
  nothing about where the document sits while it is being drafted.
- [PLAN-015](../01-plans/PLAN-015-ephemeral-working-plans.md) defines `_working/` for task detail
  belonging to a phase that already exists, and states that nothing in it is deleted without the
  owner's approval. A promoted plan is not task detail for an existing phase; it is the phase's own
  governed document, still being written. `_working/`'s content is also gitignored, so a plan drafted
  there is invisible to a peer working in a sibling worktree, which a governed plan cannot be.

Without an answer, a draft plan has landed directly in `docs/01-plans/` before it carries a real code
or satisfies the front-matter schema, or has been written informally and lost track of which code it
was promised.

## Decision

**A promoted plan or requirement is drafted in `docs/00-working/promoted/`, under the filename its
reserved code will carry, from the moment the owner decides an idea should become one.**

The sequence:

1. The owner decides an idea should become a plan or requirement.
2. The code is reserved immediately, using GOV-005's existing reservation mechanism: an entry under
   `reserved` in `codes.yaml`, naming the reason and the claiming phase. No second reservation
   mechanism is introduced.
3. The draft is written at `docs/00-working/promoted/<code>-<slug>.md`, using the reserved code as
   its filename prefix from the start. `docs/00-working/` is already ungoverned staging under
   ADR-010, so the draft carries no obligation to satisfy front matter or the catalog while it is
   being written, and the governance check does not see it there.
4. When the draft is ready, it moves — by filename, unchanged — into its registered location
   (`docs/01-plans/` for a plan, `docs/06-requirements/` for a requirement). The reservation entry in
   `codes.yaml` is removed in the same change that adds the document, exactly as GOV-005 already
   requires for any reserved code coming into use.

**If the draft is abandoned**, the file at `docs/00-working/promoted/` is deleted and the
reservation entry is released with `--release-code`. Nothing about this is a new rule: ADR-010
already treats staged content as owning no obligation to act, and GOV-005 already defines expiry and
manual release for a reservation whose document is never written. Combining them answers the
abandoned-draft case without inventing a third mechanism — a draft that never leaves staging behaves
exactly like an idea that is discarded before promotion; the difference is that the code reservation
must also be released, since a promoted draft actually holds one.

The idea itself is unaffected either way: `promoted` already reflects the owner's decision, and
whether the resulting draft is finished or abandoned is a fact about the document, not about the
idea's own status in `_data/ideas.jsonl`.

## Why this and not something else

**Draft directly in `docs/01-plans/` before it is ready.** Rejected: the target directory's
front matter and catalog obligations apply the moment a file lands there, so an incomplete draft
would either fail the governance check or be excluded from it by a second exemption rule specific to
that directory — duplicating the exemption ADR-010 already grants `docs/00-working/`.

**Use `_working/`.** Rejected: `_working/` is defined for task detail scoped to a phase that already
exists, is gitignored, and is deleted only on the owner's request rather than moving anywhere. A
promoted plan is not task detail — it is the governed document itself, mid-draft — and its
destination is a specific, predictable path (`docs/01-plans/<code>-<slug>.md`), not deletion.

**Invent a second reservation ledger for promoted-document drafts.** Rejected by the acceptance
criterion this phase was given: GOV-005's reservation mechanism already solves early allocation
waste, so nothing here needs to avoid allocating a code before the draft exists, and a second ledger
would only create two places to check whether a code is spoken for.

## Consequences

- A promoted plan is visible to any peer, in any worktree, from the moment its code is reserved,
  because `docs/00-working/` is tracked, unlike `_working/`.
- Moving a finished draft into its registered location is a rename, not a rewrite: the filename does
  not change, only the directory.
- An abandoned draft leaves two things to clean up together — the file and the reservation — and the
  protocol document (`GOV-011`) states that as the operational rule.
- `docs/00-working/promoted/` inherits `EXEMPT_DIRS`'s existing exemption in
  `src/governance/__main__.py`; no code change to the governance check was needed for this decision.
