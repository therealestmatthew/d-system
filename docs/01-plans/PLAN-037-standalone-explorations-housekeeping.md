---
schema_version: 1
id: doc-standalone-explorations-housekeeping
code: PLAN-037
title: Standalone explorations and housekeeping (P12)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-governance]
depends_on: []
---

# Standalone explorations and housekeeping (P12)

## Summary

Programme `P12` of the twelve, and the one that is not a programme. Eleven ideas across seven fine
groups, and the partition is explicit about why they are together: **"Why together: nothing."** It is
a readability bucket — six singletons and two small chains that would otherwise inflate the programme
count without adding a programme.

This document therefore does what the phase's scope asks: it **rules on each of the seven groups
separately** and produces phases only where they are earned. There is no shared design here, because
there is nothing shared to design.

| Group | Ideas | Ruling |
|---|---|---|
| `G57` Observability and telemetry | `000054` | One scoping phase. Cannot be sized further until it lands |
| `G58` Content strategy | `000015`, `000016`, `000017` | One decision phase — and the decision is the owner's |
| `G59` Research scouting | `000068` | One capture phase |
| `G60` Repo tracker | `000086` | Two phases: the tracked list, then the agent |
| `G61` Platform evaluation | `000122` | One document phase. Explicitly not a rebuild |
| `G62` Websockets education | `000140` | One phase, producing study material rather than product code |
| `G63` Demo rehearsal placeholders | `000088`, `000090`, `000103` | **Already discarded. No phase.** |

Seven phases from eleven ideas. The partition declines to give the bucket a total — "the bucket's
total is not a meaningful number" — and that assessment is correct and worth preserving.

## Two decisions about this document itself

### 1. No requirement document, deliberately

Every other programme this batch finalized produced a paired requirement. **This one does not**, and
the phase's acceptance does not ask for one — unlike its nine siblings, whose acceptance names "a
requirement document exists for P*n*".

That asymmetry is correct. A requirement document states observable behaviour for a coherent body of
work. These seven groups share no system, no consumer and no file; a single requirement over them
would be a list of unrelated observables in one table, which is a document manufactured to match a
pattern rather than to serve a reader. `AGENTS.md` records the cost of that habit directly: four
documents were manufactured on 2026-09-06 for want of somewhere to put an idea.

Each phase still carries its own acceptance conditions in `backlog.yaml`, which is where the
checkable statements for unrelated work belong.

### 2. One prefix, and it is an index rather than a track

`phase-expl-*` carries all seven phases. That is a compromise and worth naming as one.

The alternative — a prefix per group — would add six or seven rows to the backlog index for one or two
phases each, making the index unreadable. That is precisely the cost the bucket exists to avoid, so
recreating it at the prefix level would defeat the purpose.

**But the prefix implies no shared design.** Phases under `phase-expl-*` have no relationship to each
other, no common system, and no sequencing between them beyond `G60`'s internal pair. A coordinator
should read the prefix as "unrelated small work", never as a track.

## The rulings

### `G63` — already discarded, confirmed rather than re-decided

The phase's acceptance requires `G63` ruled on rather than carried forward. **It was ruled on by the
owner on 2026-09-13, and the ruling has landed:**

```
000088 | discarded | Rehearsal idea from dry-run 1
000090 | discarded | Rehearsal idea from phase-demo-05 second dry-run
000103 | discarded | Rehearsal pass 2 test entry for the live terminal /idea command
```

The partition records the basis: *"Tier 1, the only tier all four analysts agreed on, control
included. Self-declared timing placeholders carrying no product content."* All four analysts
nominated them, which happened for no other group in the corpus.

**No phase is created.** The ruling is confirmed as executed, not re-made.

### `G57` — the scoping pass is the phase, and it has two boundaries the partition does not name

`000054` wants structured logging, metrics and tracing across the FastAPI backend, agent runs and
background tooling. The partition calls it "unscoped — needs a scoping pass", and notes that no
`sys-observability` exists — confirmed, `grep -c "sys-observability" docs/08-governance/systems.yaml`
returns `0` — while the work spans `sys-api`, `sys-projection` and `sys-html`.

The scoping pass is therefore the whole of `phase-expl-01`: what to instrument first, where telemetry
lives, and whether a new system id is warranted.

**Two overlaps this batch created, which the partition could not have known about:**

- **`P5`'s run ledger** (`phase-auto-04`) persists per-run duration, disposition, retry count and
  checkpoints. That is agent-run telemetry. If it ships first, `000054`'s agent-run half is partly
  built.
- **`P4`'s delegation retrospective** (`phase-agx-06`) measures dispatch counts, truncations, fix
  cycles and escalations. That is agent-run metrics with a different consumer.

The scoping pass must state its boundary against both rather than instrument the same thing twice.
Its `next_action` says so.

### `G58` — the decision is the owner's, and the phase exists to put it

`000015` → `000016` → `000017` is one expanding chain: one platform, then multi-platform, then
automation. The owner ruled them **kept as parked** on 2026-09-13: *"Dormancy is not deadness. Wholly
isolated in `G58`; a business-priority question, not a technical one."*

That ruling settles what the phase is. It is not a build and not a design — it is one session that
puts a business-priority question and records the answer, in the same shape as `P7`'s `phase-proj-01`.
An agent can frame the question and the options; it cannot decide whether the owner wants to build in
public.

The phase is created `queued` rather than `deferred`, because nothing blocks asking.

### `G59` — a capture pass, and the output is ideas

`000068` scouts `research/` — roughly 10,700 lines across about 90 files, including twelve adversarial
codebase-review reports whose findings were deliberately never executed, the last of which ends "Stop
here; do not start the…".

The phase produces **ideas, not features**, through `tools/append_idea.py`, and edits no research
file. That boundary is what keeps it one or two sessions rather than open-ended: the scout records
what it finds and stops.

### `G60` — two phases, and it may split further on contact

`000086` pairs a tracked list of the owner's repositories with a cross-repo awareness agent. The
partition sizes it 2–3 and notes it "may split into two ideas on contact".

Split at the natural seam: `phase-expl-04` builds the tracked list, `phase-expl-05` the agent that
reads it. The agent is worthless without the list, and the list is useful alone — so the first phase
delivers value even if the second never runs.

The owner names `autoclaude-api`, a repo that scouts repositories for Claude skills, as something
this should tie into. That is a real external dependency and the first phase's `next_action` flags it.

### `G61` — a document, and explicitly not a rebuild

`000122` evaluates Rust, Go and C# for a desktop-class rebuild, and is recorded as "deliberately
standalone and future-only". One phase, producing a comparison document.

The phase's acceptance forbids it proposing a migration. The idea's own framing is that the
application "is becoming something like an integrated development environment" and that this "does
not have to live in a web app" — a thought worth writing down, and a long way from a decision to act
on it.

### `G62` — owner education, producing study material

`000140` is a websockets deep dive using this repository's terminal stack as the worked example, and
is explicitly "not a build item". One phase.

It has unusually good material to work from: the lifecycle traces from the 2026-09-11 gate work,
`000137`'s 403-versus-close-frame distinction, and the PTY reaping incidents. The phase's value
depends on using those rather than writing a generic tutorial, and its acceptance says so.

## Nothing was moved to another programme

The phase's third acceptance condition is conditional — *"Any member moved to another programme is
recorded in that programme's plan too"* — and the ruling is that **no member is moved**. Stated
explicitly rather than left silent, because a condition with no visible outcome is indistinguishable
from one that was overlooked.

The nearest candidate was `000054`, which could plausibly join `P5` on the grounds that a run ledger
is telemetry. It stays here for two reasons. The partition's independence argument is sound — it spans
three systems and is not a child of `000080` — and subordinating a system-wide observability question
to unattended-operations infrastructure that may never be built would gate the general on the
speculative. The overlap is handled as a stated boundary in `phase-expl-01`'s scope instead, which
costs nothing and moves nothing.

## Implementation phases

Seven phases under `phase-expl-*`, registered in [the backlog index](../09-backlog/README.md) as an
index rather than a track.

| Phase | Title | Group |
|---|---|---|
| `phase-expl-01` | Scope observability and telemetry, with its boundaries against `P4` and `P5` | `G57` |
| `phase-expl-02` | Put the content-strategy question to the owner and record the answer | `G58` |
| `phase-expl-03` | Scout `research/` for uncaptured ideas | `G59` |
| `phase-expl-04` | Build the tracked repository list | `G60` |
| `phase-expl-05` | Build the cross-repo awareness agent | `G60` |
| `phase-expl-06` | Evaluate languages and platforms for a non-web rebuild | `G61` |
| `phase-expl-07` | Websockets deep dive grounded in this repository's terminal stack | `G62` |

### Sizing against the partition

The partition sizes each member alone and declines a total. Per group: `G57` unscoped → 1 scoping
phase; `G58` "1 session to decide" → 1; `G59` "1–2 sessions" → 1; `G60` "2–3 phases" → 2; `G61` "1
session" → 1; `G62` "1 session" → 1; `G63` "0" → 0.

Every group lands at or inside its stated size. `G59` and `G60` land at the bottom of their ranges,
both because the phases are bounded by what they may not do — the scout edits no research file, and
the tracker's first phase ships a list rather than a system.

## Execution order and real concurrency

**Six of the seven phases depend on nothing and collide with nothing.** Only `phase-expl-05` has a
prerequisite, and only on its own pair.

This is the most parallelisable work in the entire backlog, and it is so precisely because the bucket
has no design: the phases touch `docs/00-working/`, `brain/`, `tools/`, `_data/` and the agent roster
in different combinations, with no shared system beyond `sys-governance` on the two that write
governed documents.

A coordinator with spare capacity and a blocked main track should reach for these.

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P12`, its decline tiers, and the owner-rulings table carrying both the `G63` discard and the `G58` parked ruling.
- **Autonomous agent operations** ([PLAN-032](PLAN-032-autonomous-agent-operations.md)) — `phase-auto-04`'s run ledger, one of the two boundaries `phase-expl-01` must state.
- **Agent engineering and delegation** ([PLAN-031](PLAN-031-agent-engineering-delegation.md)) — `phase-agx-06`'s retrospective, the other.
- **`tools/append_idea.py`** and its operations document `OPS-005` — the sanctioned writer `phase-expl-03` records through.

## Known facts not to rediscover

- **`G63` is already discarded.** All three ideas carry `status: discarded`. Do not re-rule, and do
  not create a phase.
- **`G58` is parked by owner ruling**, not by oversight. "Dormancy is not deadness… a business-priority
  question, not a technical one."
- **No `sys-observability` exists.** `grep -c` returns `0`. Whether to create one is `phase-expl-01`'s
  question, not a prerequisite it can assume.
- **`000054` now overlaps two phases this batch created** — `phase-auto-04`'s run ledger and
  `phase-agx-06`'s retrospective. The partition predates both.
- **`000068` produces ideas, not features**, and edits no file under `research/`. That boundary is what
  bounds the phase.
- **`000122` is future-only.** It evaluates; it does not propose migrating.
- **`000140` is owner education.** It ships no product code, and its worth depends on using this
  repository's real incidents rather than generic material.
- **This prefix is an index, not a track.** Phases under it are unrelated by construction.
