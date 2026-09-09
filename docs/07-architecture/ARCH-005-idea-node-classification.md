---
schema_version: 1
id: doc-idea-node-classification
code: ARCH-005
title: Idea node classification (ontological, epistemic, lifecycle)
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems: [sys-contracts, sys-portfolio]
depends_on: [doc-idea-record-system, doc-idea-plan-annotations-links, doc-tagging]
---

# Idea node classification (ontological, epistemic, lifecycle)

Recorded from the owner's proposal (2026-09-09) as a durable reference for the classifications
themselves, ahead of any decision about how — or whether — they are implemented. This document
is `status: draft`: it defines the taxonomy so it can be discussed and evaluated against the
existing idea corpus; it does not commit the system to a schema change. The originating idea is
`000061` in `_data/ideas.jsonl` (recorded verbatim per [ADR-010](../04-decisions/ADR-010-idea-staging.md));
this document is the properly-structured counterpart the owner asked for once the idea itself was
captured.

## Why a classification, not another tag

[ARCH-001](ARCH-001-tagging-system.md) already gives ideas a tagging axis — open-vocabulary,
additive, answers "what is this about." Idea `000018` (tagging and plan-mapping system for ideas)
and `000053` (idea-to-document links) both extend that same additive-metadata model: more tags,
richer link targets.

This taxonomy is a different kind of thing. It proposes a **small, closed set of node types**
along independent axes, so that graph traversal can partition on *kind of node* the way a
database partitions on a typed column — not by string-matching an open tag vocabulary. The
motivating query is structural, not topical: "every Strategic Directive resting on an Assumption
rather than an Axiom" is a join across two axes, not a keyword search. A tag vocabulary can grow
to describe this after the fact; a closed type system supports the query by construction.

Three axes are proposed, each orthogonal to the other two and to tags/links. An idea is expected
to carry at most one classification per axis (not one overall "type") — see Open Questions for
whether every axis applies to every idea.

## Axis 1 — Ontological (the nature of the idea)

What kind of thing the idea's subject *is*, independent of how true or how actionable it is.

| Type | Definition |
|---|---|
| **Concept / Mental Model** | A theoretical construct, principle, or paradigm (e.g. "Observability," "Systems Thinking"). Acts as a gravitational center other nodes cluster around. |
| **Artifact / Entity** | A concrete digital or physical output — a specific HTML report, a git commit, an existing system architecture. |
| **Process / Workflow** | A sequential operation or methodology — how something is done, not what it is. |
| **Event** | A distinct occurrence in time (a system failure, a deployed update, a meeting) that triggers new generative thoughts or retrospectives. |

## Axis 2 — Epistemic (the truth status of the idea)

How much the idea can currently be trusted or relied upon.

| Type | Definition |
|---|---|
| **Axiom / Ground Truth** | A verified, immutable fact within the domain. |
| **Hypothesis / Assumption** | An untested theory or premise that requires validation before it is safe to build code or infrastructure on top of it. |
| **Anti-Pattern / Falsified Concept** | A disproven theory, failed plan, or known dead-end. Retained deliberately — an explicit record of what doesn't work prevents cyclical mistakes and marks the boundary of the system, rather than being discarded once disproven. |

## Axis 3 — Execution / temporal (the lifecycle stage)

Where the idea sits in the arc from raw thought to executed and reviewed work.

| Type | Definition |
|---|---|
| **Generative Seed** | A raw, unstructured thought captured in the moment — pure potential, no plan formulated yet. |
| **Strategic Directive** | A high-level goal or plan that aggregates multiple seeds into a cohesive direction. |
| **Operational Task** | An executable, granular action derived from a strategic directive. |
| **Retrospective Insight** | A post-execution observation derived from a plan after the fact — a gap, technical debt, or newly realized context. |

## What this unlocks

Separating node class from subject tag is what makes the traversal queries the taxonomy is for
possible at all: isolating a subgraph of every `Strategic Directive` whose supporting links land
on `Hypothesis`/`Assumption` nodes rather than `Axiom` nodes surfaces structural risk in a plan
before any code is written against it. That query is a filter on two closed enums; it is not
expressible as a tag search without first inventing tags that duplicate the taxonomy.

## Composition and abstraction (resolved 2026-09-09)

Discussing this taxonomy surfaced a related but separate question — how ideas compose into
larger ones — resolved with the owner and recorded here because it changes what "atomic" and
"compound" mean for this taxonomy's purposes:

- **Atomic and compound are not a fourth axis, and not node types at all.** They are structural
  *positions*, derivable from the graph rather than hand-classified: whether anything asserts
  `component_of` into a node. A node with nothing composed into it reads as atomic; one with
  edges composed into it reads as compound — at whatever level of the graph you're looking.
- **Composition runs bottom-up, never top-down.** A "compound idea" that started as a brainstorm
  dump of several unrelated thoughts is not decomposed by forking it apart — that dump was never
  one real node. A genuine compound (an emergent system where the whole does something none of
  its parts do alone) is *constructed*: specific atomic ideas are explicitly asserted to
  function together via a new link type, `component_of` (atomic idea → the compound it
  functions within), many-to-many by design — one atomic idea can be a real component of more
  than one distinct emergent system.
- **`extends` is unaffected and keeps doing real work one level up.** Once a compound exists as
  an emergent whole, it is itself a node with its own irreducible meaning and can `extends` a
  still-more-abstract idea — the same `component_of` → `extends` pattern repeats fractally
  rather than there being two fixed buckets.
- **Provenance of thought is not provenance of meaning.** An earlier version of this discussion
  proposed a `forked_from` link type recording which compound idea an atomic fragment was pulled
  out of. That was dropped: it records how the owner arrived at an idea, not how ideas currently
  relate, so it doesn't belong in the relationship graph at all. It is instead proposed as a new
  annotation kind (`000064`) — queryable, but structurally inert, same as `note`/`assessment`
  today.
- **Open tension, left unresolved**: an `Axiom`/`Ground Truth` is meant to be indivisible, yet it
  seems plausible for an axiom-level idea to itself be composed of several atomic ideas
  functioning together — the same fractal pattern as a `Concept`. Whether that contradicts the
  epistemic axis's intent, or epistemic status and compositional structure are simply
  independent and can co-occur, is unresolved pending real examples.

See `000063`'s `assessment` annotation for the full resolution, `000064` (lineage annotation
kind) and `000065` (a decomposition procedure for compound ideas that don't hold together as one
node) for the ideas this produced.

## Open questions

Deliberately unresolved here — this document defines the vocabulary, not the implementation:

- **Does every idea need a value on every axis?** An `Event` may not have a meaningful epistemic
  status the way a `Hypothesis` does. Forcing all three may produce meaningless values on some
  ideas; making them optional may produce a taxonomy with inconsistent coverage.
- **Where does this live?** Three new fields on `schemas/idea.schema.json`, a separate typed-node
  system that ideas participate in alongside a new memory/document graph (see `000060`, `000032`),
  or the seed of a distinct knowledge-graph layer that ideas are only one source feeding.
- **Who assigns it, and when?** The owner has proposed a dedicated classification agent whose
  only job is interpreting an idea's essence into these three axes — explicitly not tagging,
  not relationship-building. That agent does not exist yet; this document defines what it would
  classify against.
- **Backfill.** 61 ideas already exist unclassified as of this document's creation. A schema
  change here is not schema-forward-only unless the taxonomy is allowed to be silently absent on
  everything written before it, which weakens exactly the partition queries motivating this work.
- **Interaction with retrieval.** Whether node type becomes a first-class filter/facet once
  `000004`/`000005`/`000043`/`000044`/`000045`'s vector/graph retrieval work lands, or stays a
  property only the idea system itself reasons about.
- **Query surface.** Whether a graph-processing library (NetworkX was named as an example) is the
  intended way to run these traversal queries, or whether the existing DuckDB derived layer
  (`tools/rebuild_db.py`) can express the same joins over relational tables adequately at this
  corpus size.

## Recommended build order (2026-09-09)

The owner's assessment of sequencing across every idea this document touches, given as of a
65-idea corpus. Not a commitment — no REQ or PLAN exists yet (see item 2) — but the order this
work would go in once one does.

1. **Resolve the scope fork first.** Is this a handful of new fields/enum values on the existing
   `schemas/idea.schema.json`, or the seed of a separate graph layer that ideas, memories
   (`brain/`, `docs/05-memories/`), and documents all become nodes within (see `000060`,
   `000032`)? Still open. Everything below is scoped differently depending on the answer.
2. **Write the governing REQ/PLAN**, turning this document plus `000061`–`000065`, `000053` and
   `000018` into an accepted requirement and implementation plan, per this repo's
   plan-before-code rule. The gate before any schema change lands.
3. **Ship the schema additions as one bundled phase**: the `component_of` link type, the
   `lineage` annotation kind, the classification fields themselves, and `000053`'s
   document-code link targets. All touch `schemas/idea.schema.json`, `src/db/ideas.py`'s
   `fold()`, and `tools/append_idea.py` together — bundling avoids re-touching the same files
   across four separate phases.
4. **Backfill the existing corpus.** The taxonomy's value is entirely coverage-dependent — the
   partition queries it exists for (e.g. every `Strategic Directive` resting on an `Assumption`)
   can't run on an unclassified majority. Shipping the schema without backfilling defers the
   payoff indefinitely.
5. **Build the classification agent (`000062`)** — the mechanism for #4, and for every idea
   captured after it.
6. **Build the connection-builder agent (`000055`)**, extended to own `component_of`
   maintenance and tagging as already scoped in its own body. Depends on #3; works alongside #5.
7. **Tagging system (`000018`)** — PLAN-017 deferred this pending "60 captured ideas or a
   recorded failed retrieval." The corpus crossed 60 during this same design conversation; the
   deferral condition is no longer speculative. Can run in parallel with #5/#6 — additive
   metadata, not structural.
8. **`000053`'s document-code link targets** — bundled into #3 for convenience, but genuinely
   independent: a different axis (link *target* shape) from node classification or link *type*,
   so it isn't blocked by the rest of #3 if sequencing needs to split.
9. **Decomposition procedure (`000065`)** — write once `component_of` exists and there's a real
   backlog worth decomposing. `000004` ("three related ideas recorded together... the overlap is
   the useful information") already reads like a live candidate compound idea to test the
   procedure against.
10. **The unrelated umbrella ideas from the prior triage session** (`000054` observability,
    `000056` documentation governance, `000057` testing strategy, `000058`/`000059` version
    control and git, `000060` memory and context management) — real, already-triaged gaps, but
    orthogonal to this design thread. Lowest priority only in sequencing, not in importance.

## Related

- `000061` — the idea this document was written from (ontological/epistemic/lifecycle taxonomy)
- `000018` — tagging and plan-mapping system for ideas (the additive-metadata sibling this
  taxonomy is deliberately not another instance of)
- `000053` — idea-to-document links (the other pending schema extension to the idea system)
- `000055` — a connection-builder agent for the full idea corpus (relationship/tag maintenance;
  contrast with the pure-classification agent proposed above, which does neither)
- `000062` — a pure classification agent (contrast with `000055`, which does neither
  classification nor tagging)
- `000063` — the composition/abstraction relationship model resolved above (`component_of`
  added, `forked_from` dropped as a link type)
- `000064` — a lineage annotation kind, replacing `forked_from`
- `000065` — a decomposition procedure for compound ideas that don't hold together as one node
- `000032`, `000060` — provenance and memory-lifecycle ideas that already gesture at a graph
  layer broader than the idea log alone
