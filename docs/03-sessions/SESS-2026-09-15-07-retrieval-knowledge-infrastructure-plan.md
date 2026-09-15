---
schema_version: 1
id: doc-session-retrieval-knowledge-infrastructure-plan
code: SESS-2026-09-15-07
title: Finalize the retrieval and knowledge infrastructure plan (P6)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-retrieval, sys-brain, sys-governance]
depends_on: [doc-retrieval-knowledge-infrastructure]
---

# Finalize the retrieval and knowledge infrastructure plan (P6)

## Phase

`phase-prog-08` — Finalize the retrieval and knowledge infrastructure plan (P6).

Sixth phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 239 documents, 25 memories, 238 backlog phases
```

Exit 0. Documents 237 → 239: `REQ-018`, and this record. Phases 228 → 238 for the ten `phase-ret-*`
phases. An earlier run during the session reported `238 documents`, correctly — this record did not
exist yet.

`uv run python -m src.governance --ready`

```
| phase-ret-01 | Build retrieval-failure collection and seed it from the session corpus | — | 1 | ready | — | phase-prog-08 |
| phase-ret-03 | State the prioritised search order and its conflict rule | — | 2 | ready | — | phase-prog-08 |
| phase-ret-05 | Revisit ADR-001 on a queryable document projection | — | 2 | ready | — | phase-prog-08 |
| phase-ret-08 | Evaluate a code-graph tool against this repository's code | — | 3 | ready | — | phase-prog-08 |
| phase-ret-09 | Detect memory staleness and contradiction, and track confidence | — | 3 | ready | — | phase-prog-08 |
```

Five of ten are `ready` — exactly the five declaring `depends_on: []`.

`uv run pytest`

```
580 passed, 2 warnings
```

## Acceptance

- **`PLAN-033` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, six numbered rulings plus a section on the gate deadlock.
- **A requirement document exists for P6 and every row maps to at least one phase.** Met. `REQ-018`
  carries fourteen rows; the mapping is total in both directions, checked against the backlog.
- **`G28` is kept whole, with the reason audit 2 gave for restoring it recorded.** Met. `PLAN-033`
  design ruling 3 quotes audit 2's finding and its fix verbatim, records the checkable fact
  underneath it — `000045`'s own body naming the other two as companion ideas — and quotes audit 2's
  own summary of the pattern. `R10` makes wholeness a checkable requirement rather than a note: the
  decision must cite all three surveys.
- **`phase-prog-08` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-08` is `status: active`, `agent: agent-night`, pending the independent review below.

Ten phases added under `phase-ret-*`, all `status: queued`, none claimed.

## Decisions

**The gate is a deadlock, and re-specifying it is the programme's first job.** `phase-mem-15`, `-16`,
`-18` and `-19` are all `deferred`, each citing "the recorded retrieval failures", and nothing records
one. The evidence that would release the work can only come from using a retrieval system nobody may
build until the evidence exists. Four phases have sat behind a condition with no threshold — no
number, no date, nothing that could be satisfied or expire.

**Collection is voluntary and seeded, not instrumented.** The obvious move is to instrument
`tools/load_context.py`; ruled against, because it reads only the `memories` table —
`load_context.py:94` is `FROM memories` — so instrumenting it measures the route that already works
and misses grep, which is how retrieval actually happens and which leaves no trace when it fails.
`R01` requires the record to say **whether the thing existed**, because without that a retrieval
failure is indistinguishable from a question with no answer. `R02` seeds the collection from existing
session records, which already describe such cases in prose.

**The gate gets a threshold and an expiry, and both outcomes are ruled.** This is the half that
matters. A condition that can expire converts four indefinitely parked phases into phases scheduled
for a decision. If the failures never materialise, that is itself an answer — retrieval was not the
problem it was assumed to be. The threshold is a guess made before the data exists; the expiry is
what stops a wrong guess parking the work a second time.

**`G26` gets no phase at all.** `000004` enumerates `phase-mem-15`, `-16`, `-18` and `-19` by id in
its own body. Creating phases beside them would duplicate an existing line, so `phase-ret-02` acts on
the group by re-ruling their gate. This is why the programme lands at ten with one group at zero.

**`ADR-001` is revisited before any documentation database is designed.** `000043` proposes exactly
what that decision ruled out — governance metadata "needs no DuckDB table, DDL migration, or API
Pydantic model… the explicit exception to the otherwise applicable entity schema → DDL → model
workflow." Surveying tooling while the governing decision forbids the projection surveys something
that cannot be built. Reaffirming `ADR-001` is a complete outcome.

**`000040`'s deterministic boundary is made checkable.** It says in its own text that it is not
semantic search. That boundary erodes easily — a deterministic design that reaches for embeddings
when exact matching gets hard has become `G26`'s work under `G25`'s name — so `R07` requires the
absence of any vector mechanism.

## Corrections

**`REQ-018`'s `depends_on` named a document id that does not exist.** I wrote `doc-agent-memory-system`
for `PLAN-001`; its actual id is `doc-agent-memory`. Caught by reading the file's front matter before
running governance rather than after. Corrected in both the requirement and the plan.

## Unresolved

**What the threshold and review date should actually be.** `R03` requires a number and a date;
`phase-ret-02` picks them. Options: fix them here, or leave them to the phase with the collection in
hand. **Left them to the phase**, because choosing a threshold before `phase-ret-01`'s seeding sweep
reports how many cases the corpus already contains would be guessing at a number that will be
knowable in one session's time.

**Whether the seeding sweep can distinguish a retrieval failure from an ordinary correction.** Session
records carry "Found wrong in the source material" and "Unresolved" sections, and not every entry
there is a retrieval failure — some are defects found, not things sought and missed. **Proceeded on
the assumption that the sweep will need a judgement pass**, and wrote `R01`'s third field (whether the
thing existed) partly so the sweep has a criterion to apply. If the distinction proves unworkable,
the seed count will be small and the threshold should account for that.

**Whether `phase-ret-08`'s successor tool exists.** `000005` names GitNexus, and the owner's ruling of
2026-09-13 records the tool as dead — KuzuDB archived — with the question alive and any evaluation
starting from a successor. **Sized the phase anyway**, with `next_action` telling whoever claims it to
confirm a maintained successor exists before planning around it. If none does, the phase is a short
survey concluding so.

## Left undone

**All ten phases.** This phase finalizes a plan and builds nothing.

**The four deferred `phase-mem-*` phases are still deferred.** This plan designs the mechanism that
would release them; it does not release them. That is `phase-ret-02`'s, and it belongs to another
plan's phases, which is why the re-specification needs an ADR rather than a quiet edit.

**`P6` should run after `P1`**, which is the fourth cross-programme ordering constraint this batch has
produced. `phase-ret-03`'s search order must rank the ideas log among its sources, and `P1` gives that
log the classification to rank by. Ordering an unstructured corpus produces an order that changes the
moment `P1` lands.
