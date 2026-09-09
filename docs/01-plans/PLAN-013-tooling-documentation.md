---
schema_version: 1
id: doc-tooling-documentation
code: PLAN-013
title: Tooling documentation — one operations document per tool, with a generated reference
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-delivery, sys-projection, sys-retrieval]
depends_on: [doc-governance-protocol]
---

# Tooling documentation — one operations document per tool, with a generated reference

## Context and scope

Nothing documents what the tools do. `tools/rebuild_db.py` and `tools/load_context.py` are named in
passing across a dozen documents and described in none. `OPS-001` is *governance* operations — a
runbook for the check, codes and session protocol — not a reference for the data tooling.

This matters more than three files would suggest, because the tool count is about to multiply. The
owner has several governance tools designed and not yet integrated: front-matter validation, drift
detection, and a family of file generators — the catalog generator that exists, the glossary
generator specified in [PLAN-012](PLAN-012-terminology-system.md), and more to come.

## Decision: one operations document per tool

Considered and rejected: a single operations document covering all tooling. At three tools that is
obviously lighter. At the eight-to-ten this repository is heading toward, a shared document becomes a
file everyone edits and nobody owns, where a tool cannot be deprecated or rewritten without touching
prose belonging to five others.

Per-tool documents give each tool a code, a lifecycle and a `status` that can move to `deprecated`
independently. The catalog growing alongside the toolchain is the correct behaviour, not bloat — each
entry corresponds to a real executable thing.

**The threshold was the deciding fact.** The single-document recommendation was made without knowing
about the planned tools and does not survive that information.

## Decision: generate the reference, hand-write the narrative

Each tool document has two parts:

- **Generated** — the mechanical reference: module docstring, arguments, exit codes. The code is the
  source of truth, exactly as `catalog.md` derives from the documents it lists. This part cannot
  drift, because drifting would require the generator to disagree with the file it reads.
- **Hand-written** — what the tool is *for*, its contract, its failure modes, and what to do when it
  fails. This is the part with judgement in it and the part a generator cannot produce.

## Decision: no drift enforcement yet

A check failing when a tool changes without its document updating was considered and **deliberately
deferred**. Generation already removes drift from the mechanical half, and the remaining risk is
narrative lag, which is real but not urgent.

Recorded for later: the shape most likely to work is a **recorded hash of each tool's public
signature**, failing only when that signature changes without the narrative being touched. A hash
over the whole file was rejected in advance — every rename and typo fix would trip it, training
people to re-record the hash without reading anything, and a check that always fires is not a signal.

Revisit once the toolchain stabilises.

## Deliverables

- `tools/generate_tool_docs.py` — emits the generated section for each tool from its docstring.
- One `OPS-*` document per tool in `docs/08-governance/`, starting with `rebuild_db.py`,
  `load_context.py` and the glossary generator.
- A test asserting each committed generated section matches regenerated output, in the same shape as
  the existing catalog test.
- A convention, recorded in `AGENTS.md`, that a new tool ships with its operations document.

## Sequencing

After [PLAN-012](PLAN-012-terminology-system.md). The glossary generator is written first and this
follows its pattern rather than inventing a second one — two generators with different shapes would
be exactly the unnecessary complexity
[PROMPT-003](../02-prompts/PROMPT-003-systems-review.md) exists to catch.

## Open questions

- **Whether planned-but-unbuilt tools get documents before they exist.** Probably not — a document
  describing an unwritten tool is the aspirational-map problem PROMPT-003 already raises about
  `systems.yaml`.
- **Whether `OPS` is the right series**, or tools want their own. Deferred to
  [PROMPT-005](../02-prompts/PROMPT-005-governance-model-review.md), which is already asking why
  `governance` and `operation` are separate kinds.
