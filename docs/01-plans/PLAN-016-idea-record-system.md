---
schema_version: 1
id: doc-idea-record-system
code: PLAN-016
title: Idea record system — append-only event log, schema and write tooling
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection, sys-governance]
depends_on: [doc-idea-staging]
---

# Idea record system — append-only event log, schema and write tooling

## Context and scope

`docs/00-working/ideas.md` was created on 2026-09-06 as an ungoverned markdown list
([ADR-010](../04-decisions/ADR-010-idea-staging.md)). Within hours it accumulated ten entries and
outgrew its format: it had no timestamps, so nothing about it could be analysed over time.

**This is time-sensitive and therefore first in the queue.** Every idea captured before this system
exists is captured without reliable structure, and a timestamp reconstructed later is a guess.

**The existing timestamps are real observations.** The owner recorded each entry against a clock as
it arrived, which is why they run at roughly two-minute intervals from `2026-09-06T14:45:00-04:00`.
Note the offset: 6 September is daylight time in US Eastern, so a literal "EST" of `-05:00` would
place every entry an hour off in any time series.

The migration must therefore **preserve** them exactly. They are observations, and restamping them
with the migration's own clock would destroy real data rather than tidy up an estimate.

The owner's stated purpose is analysis: idea density over time, actualisation rate, fizzle rate,
duplication rate, promoted-to-investigated ratios. That purpose dictates the design — the record has
to be queryable and every transition has to carry its own time.

## Decisions

### Ideas are an append-only event log

`_data/ideas.jsonl` — one JSON object per line, each an **event**, not an entity:

```jsonl
{"idea":"000001","event":"created","at":"...","title":"...","body":"..."}
{"idea":"000001","event":"status","from":"open","to":"triaged","at":"..."}
{"idea":"000001","event":"revisited","at":"..."}
```

This was chosen over one file per idea and over a single JSON array, and the reason is the owner's
own constraint: *some fields must change while the entry stays immutable.* An event log dissolves
that tension rather than managing it. **Nothing is ever edited**, so "immutable except status" stops
being a rule to police and becomes structurally true — a status change appends a line.

The rejected options, with their actual costs:

- **One JSON per idea in `_data/ideas/`** — matches the existing `_data/<type>/` convention and needs
  no new reader. File count is *not* the objection: ext4 with `dir_index` degrades in the hundreds of
  thousands, git handles ~80k files in the kernel tree, and at three ideas a day it would take a
  century to reach 100k. The real cost is that a status change rewrites a file, so immutability
  becomes a claim about content rather than a fact about bytes.
- **A single JSON array in `_data/ideas.json`** — every append parses and re-serialises the whole
  file. Worst fit for an immutability guarantee, and concurrent writers conflict badly.

Single-file precedent already exists in `_data/tags.json`, so JSONL does not break the source-of-truth
pattern; it only declines the directory convention.

### Point-in-time reconstruction is a requirement, not a side effect

Because every transition is an event with its own timestamp, the state of **every** idea at **any**
past moment is reconstructible by replaying events up to that instant. This answers a class of
question the folded state cannot: how many ideas were `open` on a given date, what was under review
during a quarter, how the backlog's shape moved over months.

**`idea_events` is therefore retained in full, permanently.** The folded `ideas` table is a
convenience derived from it, never a replacement for it. Any later change that discards events in
favour of current state — as a size optimisation, or because folded state looks sufficient —
destroys this capability silently, and the loss is unrecoverable because the events are the only
record that the intermediate states ever existed.

State this in the projection so the constraint travels with the code rather than living only here.

### The status machine is forward-only, with one revisit

| State | Meaning |
|---|---|
| `open` | Captured; nothing has looked at it |
| `triaged` | The idea agent finished scouting and attached findings; awaiting the owner |
| `reviewing` | The owner is actively considering it |
| `promoted` | Became a plan, requirement or phase — terminal, names which |
| `discarded` | Rejected — terminal unless revisited |

Transitions move forward only. `discarded` is reachable from any working state.

**`revisited` is an attribute, not a status**, at the owner's direction. A revisit appends a
`revisited` event with its own timestamp and returns status to `reviewing`. An idea may be revisited
**once**; a second `discarded` is permanent. The reasoning is the owner's: something worth revisiting
twice needs a profoundly new but related idea recorded separately, and forcing that keeps the second
thought legible as its own entry rather than buried in the first one's history.

Every transition stamps its own time. That is what makes time-in-state, time-to-resolution and
fizzle rate computable rather than estimated.

**`triaging` is deliberately omitted.** An in-progress state would separate "the agent has not
started" from "the agent is working", which are different problems with different fixes — but it
only pays if triage is slow enough to be observed in. Adding it later costs nothing, because a new
event type does not invalidate existing events. This is a decision the event log makes reversible, so
it is not made now.

### The markdown list becomes generated

`docs/00-working/ideas.md` stops being the source of truth and becomes an artifact, like
`catalog.md` and the glossary specified in [PLAN-012](PLAN-012-terminology-system.md). Same rule: a
header saying so, and a test failing on any difference from regenerated output.

This partly supersedes [ADR-010](../04-decisions/ADR-010-idea-staging.md), which made the list
ungoverned markdown. The staging *concept* stands — capture as given, never filtered at entry — but
the storage moves. **The migration must amend ADR-010 rather than leave it contradicting reality.**

### The write path is a tool, not a convention

A deterministic script owns all writes. The agent supplies **prose only** — title and body — and the
script generates the identifier, the timestamp, the event shape and the append. A custom tool wraps
the script so an agent can call it directly.

The separation matters: an agent that formats its own entries will eventually format one wrongly, and
in an append-only log a malformed line is permanent.

## Deliverables

- `schemas/idea.schema.json` — the event shape, with legal transitions expressed.
- `_data/ideas.jsonl` — the log, migrated from every markdown entry predating the writer.
- `tools/append_idea.py` — deterministic writer; takes prose, emits the event, stamps its own time.
- `tools/backfill_ideas.py` — one-time migrator, deleted once the migration is committed.
- A custom tool wrapping the writer for agent use.
- `tools/generate_ideas_md.py` — renders the markdown view.
- `sql/` and `tools/rebuild_db.py` — `ideas` (folded current state) and `idea_events` (full history).
- A test asserting no committed line in `_data/ideas.jsonl` ever changes.
- An amendment to `ADR-010`.

## Sequencing

**`phase-idea-01`** delivers the schema, the writer, the migration, the projection and the
enforcement test. **`phase-idea-02`** builds the idea agent, which the owner has explicitly called
secondary — the tool is usable by hand or by any agent the moment it exists, so the agent is not on
the critical path.

### Migration uses a separate writer that is then deleted

`tools/append_idea.py` generates the timestamp itself — that is the point of it, and an agent or
owner supplying one is how the log stops being trustworthy. But the migration has to **preserve** the
existing timestamps rather than restamp every entry with the migration's own clock, which would
collapse the whole list into one instant and destroy real recorded times.

This plan originally specified an `--at` override on the writer, gated behind an explicit migration
flag and covered by a test asserting ordinary invocation could not reach it. **That is superseded.**
A guard proves the lock holds; it leaves the door. The argument stays in the parser permanently, one
flag away from anyone reading `--help`, and the test can only ever assert a behaviour rather than an
absence.

Instead, `tools/backfill_ideas.py` is a **one-time migrator, deleted when the migration is
committed**. `append_idea.py` never gains a timestamp argument at all, so the assertion becomes
structural — the interface offers no way to supply a time — rather than behavioural. Two conditions
make this a closed door rather than a moved one:

- **The backfill imports its event construction from `append_idea.py`** and overrides only the
  timestamp. Otherwise the event shape exists twice, and the second copy is the one writing permanent
  unfixable lines.
- **Deletion is an acceptance condition, not an intention.** A migrator that survives its phase is
  the escape hatch under another name.

This is the same distinction [PLAN-015](PLAN-015-ephemeral-working-plans.md) draws for plans: a thing
that should be *deleted* rather than *maintained* when its task finishes was never permanent tooling.
The script is gone rather than archived. `phase-priv-05` squashes this repository to a single commit
before any remote exists, so git history is not a place anything can be kept — a decision to preserve
something has to be a decision to keep it in the tree. Nothing here needed keeping: the migration it
performed is fully described above, and `_data/ideas.jsonl` is the result.

