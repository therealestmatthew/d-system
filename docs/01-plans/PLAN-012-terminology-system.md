---
schema_version: 1
id: doc-terminology-system
code: PLAN-012
title: Terminology system — canonical definitions and generated glossaries
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-brain, sys-retrieval, sys-governance]
depends_on: [doc-governance-protocol]
---

# Terminology system — canonical definitions and generated glossaries

## Context and scope

The system has acquired vocabulary faster than definitions. Within a single day it gained governed
plans and ephemeral plans, phases and tracks, systems and subsystems, memories of five types, four
content folders with different rules, and document kinds, codes and series. Three consecutive
scope-creep corrections happened partly because no shared definition existed for what a plan *is*,
so each judgement was re-derived from scratch and got a different answer.

This plan establishes where terms are defined, how glossaries are produced from them, and how the
vocabulary is maintained as it grows.

It does **not** define the terms. That is content, and it belongs to
[PROMPT-004](../02-prompts/PROMPT-004-terminology-and-architecture.md). This plan builds the system
that content lives in — the distinction the owner drew when approving this work: no plan is needed to
*write* documentation, but a plan is needed for the *system that governs* it.

## Decisions

### Definitions are canonical in `brain/`, glossaries are generated

`brain/` is the model-agnostic knowledge base, already retrievable by any model through
`tools/load_context.py`. Terms live there as `concept` memories, one entry per domain group —
governance terms, backlog terms, data terms — rather than one file per term. Grouping keeps
retrieval useful without producing sixty single-paragraph files.

A governed glossary document is **generated** from those entries by a deterministic script, never
hand-written. This is the property that makes "both locations" safe: there is exactly one source of
truth, and the governed document is an artifact of it. A second hand-maintained copy would drift, and
`CLAUDE.md` already names that risk as the reason it holds pointers rather than copies.

The generator starts with one glossary. It must be written to emit several — filtered by tag or
domain — because targeted glossaries are wanted later and retrofitting a single-output script is
wasted work.

### Folder structure in `brain/` stays type-first — but only on one of the two reasons first given

An earlier draft rejected per-subsystem folders on two findings. **The first was wrong and is
withdrawn.**

1. ~~Governance enforces type-first, so subsystem folders would require rewriting the rule.~~
   **False.** `src/governance/__main__.py:226-228` is a `startswith` prefix test, and
   `markdown_paths` uses `os.walk`, which recurses. A file at
   `brain/concepts/sys-backlog/backlog-terms.md` passes today, unchanged — verified by creating one
   and running the check, which exited 0. Subsystem folders **nested under the type directory** need
   no rule change. Only a top-level `brain/sys-backlog/concepts/…` would.
2. **Folders contribute nothing to retrieval.** This holds. `tools/load_context.py:28-55` filters on
   query, project, type, tags and limit and never reads the path. Note it does *select* `file_path`
   at `:86`, so a path filter would be a small change — the honest argument is not that folders are
   impossible, but that a `systems` field answers the question directly while folders answer it by
   convention.

**The decision stands, on reason 2 alone.** Nesting is permitted; it is simply not the mechanism
that makes subsystem retrieval work.

### Subsystem-scoped retrieval needs a field, not a folder

The underlying want — *"ask for everything about one subsystem"* — is real and currently
unsupported. `project` is validated against project IDs, and `tags` against `_data/tags.json`, so
neither can hold a `sys-*` identifier.

The fix is a `systems` field on `schemas/memory.schema.json`, mirroring what governed documents
already carry, validated against `systems.yaml`, with a matching `--system` filter in
`load_context.py`. That is a small, surgical change that delivers what the folder restructure was
reaching for, without breaking the type-first rule or touching a single existing file's location.

## Governing the vocabulary over time

- **A term enters** when it appears in two governed documents with no definition, or when a
  correction turns out to have been caused by its absence.
- **A term is retired**, not deleted, when the thing it names is removed — the definition moves to a
  retired section so an old document remains readable.
- **Definitions are short.** One sentence of what it is, one of what it is not, and a pointer to the
  governing document. Anything longer is a concept memory, and the glossary should link to it.
- **The generated glossary is never edited by hand.** Like `catalog.md`, it carries a header saying
  so, and a test fails on any difference between the committed file and freshly generated output.
- **Review happens with the systems review**, not on a separate schedule. Vocabulary drifts when the
  system does.

## Deliverables

- `schemas/memory.schema.json` — a `systems` field.
- `tools/load_context.py` — a `--system` filter.
- `tools/generate_glossary.py` — deterministic, multi-output capable.
- A generated glossary document under `docs/`.
- A test asserting the committed glossary matches regenerated output.

## Sequencing

Scaffolding lands before content. Writing definitions into a structure that does not yet exist means
migrating them immediately afterwards, and the owner's condition on approving direct authorship was
that the system exist first.

## Open questions

- **Which document series the generated glossary belongs to.** `GOV` and `ARCH` both fit; the
  generator does not care, and this can be settled when it is written.
- **Whether definitions should carry examples.** Useful for teaching, expensive to maintain. Deferred
  until the first glossary exists and its weaknesses are visible.
