---
schema_version: 1
id: doc-session-standalone-explorations-plan
code: SESS-2026-09-15-11
title: Finalize or disperse the standalone explorations bucket (P12)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-governance]
depends_on: [doc-standalone-explorations-housekeeping]
---

# Finalize or disperse the standalone explorations bucket (P12)

## Phase

`phase-prog-12` — Finalize or disperse the standalone explorations bucket (P12).

Tenth and final phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 246 documents, 25 memories, 261 backlog phases
```

Exit 0. Documents 245 → 246 for this record — **no requirement document was written**, deliberately;
see `## Decisions`. Phases 254 → 261 for the seven `phase-expl-*` phases. An earlier run reported
`245 documents`, before this record existed.

`uv run python -m src.governance --ready`

```
| phase-expl-01 | Scope observability and telemetry, with its boundaries against P4 and P5 | — | 3 | ready | — | phase-prog-12 |
| phase-expl-02 | Put the content-strategy question to the owner and record the answer | — | 4 | ready | — | phase-prog-12 |
| phase-expl-03 | Scout research/ for uncaptured ideas | — | 4 | ready | — | phase-prog-12 |
| phase-expl-04 | Build the tracked repository list | — | 4 | ready | — | — |
| phase-expl-06 | Evaluate languages and platforms for a non-web rebuild | — | 4 | ready | — | phase-prog-12 |
| phase-expl-07 | Websockets deep dive grounded in this repository's terminal stack | — | 4 | ready | — | phase-prog-12 |
```

Six of seven are `ready`. Only `phase-expl-05` waits, on its own pair — which is the plan's claim that
this is the most parallelisable work in the backlog, confirmed by the tool rather than asserted.

`uv run pytest`

```
580 passed, 2 warnings
```

### `G63`, verified rather than re-ruled

```
000088 | discarded | Rehearsal idea from dry-run 1
000090 | discarded | Rehearsal idea from phase-demo-05 second dry-run
000103 | discarded | Rehearsal pass 2 test entry for the live terminal /idea command
```

All three carry `status: discarded`, read through `fold()`. The owner ruled them on 2026-09-13 on the
basis the partition records: Tier 1, the only tier all four analysts agreed on, control included.

### `G57`'s scoping precondition, verified

```
$ grep -c "sys-observability" docs/08-governance/systems.yaml
0
```

No such system exists, as the partition states.

## Acceptance

- **`PLAN-037` carries no placeholder banner and states what happened to each of the seven groups.**
  Met. Banner removed, `status` `draft` → `active`, and a ruling per group — stated twice, as a
  summary table and as seven prose rulings with reasons.
- **`G63` is ruled on rather than carried forward.** Met, by confirming the owner's existing ruling
  has landed rather than re-making it. All three ideas are `discarded`, shown above, and no phase is
  created for them.
- **Any member moved to another programme is recorded in that programme's plan too.** Met, vacuously
  and deliberately so: **no member was moved**, and `PLAN-037` says so under its own heading with the
  reasoning, rather than leaving a conditional acceptance silently unaddressed.
- **`phase-prog-12` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the index.

## Backlog

`phase-prog-12` is `status: active`, `agent: agent-night`, pending the independent review below.

Seven phases added under `phase-expl-*`, all `status: queued`, none claimed.

## Decisions

**No requirement document was written, and that is the phase's most consequential ruling.** Every
other programme in this batch produced one. This phase's acceptance is the only one of the ten that
does *not* name a requirement document — its siblings all say "a requirement document exists for
P*n*" — and the asymmetry is correct rather than an oversight in the phase definition.

A requirement states observable behaviour for a coherent body of work. These seven groups share no
system, no consumer and no file; the partition's own words are *"Why together: nothing."* A single
requirement over them would be unrelated observables in one table — a document manufactured to match a
pattern. `AGENTS.md` records what that habit costs: four documents were manufactured on 2026-09-06 for
want of somewhere to put an idea. Each phase carries its own acceptance conditions in `backlog.yaml`,
which is where checkable statements for unrelated work belong.

**One prefix, declared an index rather than a track.** A prefix per group would add six or seven rows
to the backlog index for one or two phases each, which is the unreadability the bucket exists to
prevent — recreating it one level down. So `phase-expl-*` holds all seven, and both the plan and the
README state that phases under it are unrelated by construction and that a coordinator should never
read it as a track.

**Nothing was dispersed into another programme.** The nearest candidate was `000054`, which could
plausibly join `P5` since a run ledger is telemetry. It stays: the partition's independence argument
is sound, and subordinating a system-wide observability question to unattended-operations
infrastructure that may never be built would gate the general on the speculative. The overlap is
handled as a stated boundary instead, which moves nothing.

**`G57`'s scoping pass gained two boundaries the partition could not have known about**, because this
batch created them tonight: `phase-auto-04`'s run ledger persists per-run duration, disposition,
retries and checkpoints, and `phase-agx-06`'s retrospective measures dispatch counts, truncations and
escalations. Both are agent-run telemetry. `phase-expl-01`'s scope and `next_action` name them so the
same thing is not instrumented twice.

**`G58`'s phase frames a question rather than answering it**, in the same shape as `P7`'s
`phase-proj-01`. The owner ruled the chain parked on 2026-09-13 as "a business-priority question, not
a technical one", and whether they want to build in public is not a fact in the repository.

**Two phases are bounded by what they may not do**, which is what keeps them one session each.
`phase-expl-03` reads `research/` and writes ideas, editing no research file. `phase-expl-06` produces
a comparison document and may not propose a migration — `000122` is recorded as future-only.

## Corrections

**Three phases were written with `priority: 5`, which the schema caps at 4.** Governance went red
immediately:

```
ERROR backlog:items.258.priority: 5 is greater than the maximum of 4
ERROR backlog:items.259.priority: 5 is greater than the maximum of 4
ERROR backlog:items.260.priority: 5 is greater than the maximum of 4
```

My own authoring bug, caught by the gate on the first run after the append. Fixed by capping the three
at 4, scoped to the `phase-expl-*` block so no pre-existing phase's priority was touched. Not
escalated to a triage agent: the gate named the items and the field, and dispatching an agent to
diagnose a bounds violation the error message already diagnosed is the cost `GOV-008` warns against.

## Unresolved

**Whether `phase-expl-02` should exist as a phase at all.** It produces no artifact except a recorded
answer, and the owner could answer the question in a sentence without a session being opened.
Options: create the phase, or leave the chain parked and let the owner raise it when it matters.
**Created it**, because the owner's ruling was "kept as parked", and a parked idea with no phase is
indistinguishable from a forgotten one six months later. The phase is the thing that makes the
parking visible.

**Whether `phase-expl-03` conflicts with this run's own constraint.** The run prompt forbids writing
to `_data/ideas.jsonl`, and that phase's whole output is ideas written through the sanctioned writer.
**Proceeded on the reading that the constraint binds this run, not the phases it plans** — tonight's
prohibition is about an unattended agent adding to the idea log without review, and `phase-expl-03`
will be claimed deliberately by someone. Recorded because a reader finding both statements could
reasonably wonder.

**Whether the single-prefix compromise is right.** It is a compromise, and the plan says so. A future
reader may reasonably prefer seven prefixes, or none at all with the phases dispersed by system.
**Chose readability of the index**, and stated the cost — that `phase-expl-*` implies a coherence
these phases do not have — rather than hiding it.

## Left undone

**All seven phases.** This phase finalizes a bucket and builds nothing.

**`G63` produced no work**, correctly. Three ideas were confirmed discarded; nothing else was done
with them.

**The bucket was not dispersed**, which the scope permitted as an outcome. The rulings kept every
surviving group where it was, and the reasoning is recorded rather than the outcome merely asserted.
