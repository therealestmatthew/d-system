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
| phase-ret-03 | State the prioritised search order and its conflict rule | — | 2 | ready | — | phase-prog-08 |
| phase-ret-05 | Revisit ADR-001 on a queryable document projection | — | 2 | ready | — | phase-prog-08 |
| phase-ret-08 | Evaluate a code-graph tool against this repository's code | — | 3 | ready | — | phase-prog-08 |
| phase-ret-09 | Detect memory staleness and contradiction, and track confidence | — | 3 | ready | — | phase-prog-08 |
```

Four of ten are `ready` — the four declaring `depends_on: []`. `phase-ret-01` is **not** among them,
which is the correction described below working: it now depends on `phase-mem-10`, the collector the
gate actually names. An earlier run in this session showed five, before that dependency was added.

`uv run pytest`

```
580 passed, 2 warnings
```

## Acceptance

- **`PLAN-033` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, six numbered rulings plus a section correcting the partition's account
  of the gate.
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

**The partition's premise about the gate is wrong, and checking it changed this plan.** The partition
says the programme "is gated on a recorded retrieval failure that nothing currently collects", and the
phase's own scope repeats it. Both are mistaken in the same way, and I drafted the whole plan on that
premise before verifying it.

The gate lives in `resume_when`, not `next_action`, and it names a collector:

```
phases gated on phase-mem-10: ['phase-mem-15', 'phase-mem-16', 'phase-mem-17', 'phase-mem-18']
phase-mem-10 status: ['queued']
```

Three corrections follow. **`phase-mem-10` exists and is `queued`** — ready, blocked by nothing,
dependent on nothing, simply never claimed; its deliverables `tools/evaluate_retrieval.py` and
`test/fixtures/retrieval_cases.json` are absent from disk. **`phase-mem-17` is gated too**, which the
partition's account omits. And **`phase-mem-10`'s acceptance already carries the both-outcomes ruling**
I had thought I was inventing: "identifies concrete unmet retrieval needs **or explicitly records that
current retrieval is sufficient**."

So the cheapest unblocking move in this programme is not to design anything. It is to claim a ready
phase. That is now `phase-ret-01`'s `next_action`.

**`phase-ret-01` was rewritten to complement `phase-mem-10` rather than replace it.** The distinction
that survives is the corpus: `phase-mem-10` builds a *synthetic* evaluation set, synthetic by its own
acceptance, which measures prepared queries; `phase-ret-01` records *actual* misses hit during real
work. `R14` is why both are wanted — a retrieval system evaluated only on queries its designer wrote
is evaluated on the wrong corpus. It now declares `depends_on: [phase-mem-10]`.

**`phase-ret-02` was narrowed from re-specifying the gate to correcting the record of it**, then adding
the one thing genuinely missing: a review date, so the waiting phases have a point at which they are
re-ruled rather than waiting longer.

**Collection is voluntary and seeded, not instrumented.** The obvious move is to instrument
`tools/load_context.py`; ruled against, because it reads only the `memories` table —
`load_context.py:94` is `FROM memories` — so instrumenting it measures the route that already works
and misses grep, which is how retrieval actually happens and which leaves no trace when it fails.
`R01` requires the record to say **whether the thing existed**, because without that a retrieval
failure is indistinguishable from a question with no answer. `R02` seeds the collection from existing
session records, which already describe such cases in prose.

**The gate gets a review date, which is the gap that survived the correction.** A condition that can
expire converts four waiting phases into phases scheduled for a decision. What it does *not* need is
the threshold I first drafted: `phase-mem-10`'s acceptance already rules both outcomes.

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

**The plan's central premise was wrong, and I wrote the whole first draft on it.** I inherited the
partition's claim that nothing collects the retrieval evidence and did not check it until the plan,
the requirement and ten phases were already drafted. `phase-mem-10` is the collector, it is `queued`,
and `phase-mem-17` is gated on it too. Corrected in `PLAN-033`, `REQ-018` R03/R04 and the two affected
phases before this phase was reviewed. The lesson is the ordinary one and I did not apply it: the
partition is a secondary source, and `backlog.yaml` was the authority available the whole time.

**`REQ-018`'s `depends_on` named a document id that does not exist.** I wrote `doc-agent-memory-system`
for `PLAN-001`; its actual id is `doc-agent-memory`. Caught by reading the file's front matter before
running governance rather than after. Corrected in both the requirement and the plan.

**A correction was almost made with a whole-file rewrite.** Applying the phase edits by re-dumping
`backlog.yaml` through the YAML writer reflowed every entry — 6,264 lines changed, 2,803 insertions
against 3,461 deletions — which is unreviewable and is exactly the silent-mutation risk every review
this run has checked for. Reverted and redone as a surgical replacement of the two blocks: 61 lines,
and a parsed-item diff against `HEAD` confirms only `phase-ret-01` and `phase-ret-02` changed.

## Unresolved

**What the review date should be.** `R03` requires one; `phase-ret-02` picks it. Options: fix it
here, or leave it to the phase. **Left it to the phase**, because the sensible date depends on whether
`phase-mem-10` gets claimed in the meantime, which is not knowable now.

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
