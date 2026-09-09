---
schema_version: 1
id: doc-idea-plan-event-contract
code: PLAN-017.03
title: Event contract, identity and the validating amendment fold
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-08'
systems: [sys-portfolio, sys-projection]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Event contract, identity and the validating amendment fold

## What we know

`schemas/idea.schema.json` is the runtime source for the event grammar. It declares three event
types (`created`, `status`, `revisited`), five statuses, nine legal transitions, and
`additionalProperties: false`. The writer reads the transition table from that file rather than
restating it, which is why writer and projection have not drifted on transitions.

Three facts constrain every choice below.

**No event carries a position.** `seq` appears in `sql/001_schema.sql` as half of
`PRIMARY KEY (idea, seq)`, but it exists nowhere in `_data/ideas.jsonl`. It is assigned during the
rebuild from a line's ordinal within its idea. An amendment pointer written as `amends: <seq>` would
therefore reference a number that the log does not contain and that the rebuild recomputes on every
run — the pointer would be resolved against a value derived from the very ordering a concurrent
append is free to change.

**Replay is implemented three times** — `tools/append_idea.py:100`, `tools/rebuild_db.py:176` and a
fixture in `test_ideas.py:261` — and they already differ in two behaviours. None of them checks
`event["from"]` against the status the replay has actually reached.

**All 19 events are `created`.** Every status branch in all three implementations is unexercised.
A divergence test between them would compare three code paths that have never run.

## What we propose

### Event identity is explicit, not positional

Add an optional `eid` to the event grammar: a short, writer-generated, lexicographically sortable
identifier, unique across the whole log. Every newly written event carries one. No existing line is
touched.

The 19 historical events have no `eid`, and backfilling one would rewrite an append-only log. So
identity is resolved by a total function rather than a stored field:

> **`identity(event)`** is `event["eid"]` when present, and otherwise the digest of the event's
> canonical JSON encoding.

A legacy event's identity is thus a pure function of bytes that are already permanent. The fold
computes identities once, and **fails loudly if any two events resolve to the same identity** — for
legacy lines a digest collision, for new lines a writer bug. Neither is a condition to paper over.

This is what makes `amends` safe. An amendment names its target by identity, so the pointer survives
a rebase, a git merge that interleaves two branches' appended lines, and any reordering the rebuild
performs. Conflict `C07` stops being a process rule the writer must uphold and becomes a property of
the data. `seq` keeps its job as the display ordinal and loses its job as an address.

`PRIMARY KEY (idea, seq)` is replaced by a primary key on the resolved identity, with `seq` retained
as an ordinary sortable column. This removes the collision that `F2` demonstrated
(`ConstraintException: Duplicate key "idea: 000017, seq: 3"`) rather than routing around it.

### The amended event

```
{"idea": "000017", "event": "amended", "at": "<written>", "eid": "<new>",
 "amends": "<identity of the target>",
 "title": {"set": true,  "value": "the corrected title"},
 "body":  {"set": false}}
```

The per-field truth table is the owner's, unchanged:

| Field shape | Meaning |
|---|---|
| `{"set": true, "value": v}` | replace this field with `v` |
| `{"set": true, "value": null}` | clear this field |
| `{"set": false}` or absent | inherit whatever the chain already holds |

An amendment must target an event on the **same idea** that appears **earlier in the log**. Forward
and foreign targets are refused at the writer and rejected by the fold on import.

### Folding is a merge over a chain, never a selection

The defect in the original specification (`F1`) was that retaining the latest record per position
makes a second amendment silently revert a field the first one corrected. The fix is that
amendments compose:

1. Build `amendments: identity -> [amending events, in append order]` in one pass.
2. `effective(e)`: start from `e`'s own fields; for each amendment targeting `e` in append order,
   apply its `set: true` fields and leave the rest alone. Recurse into amendments of amendments, so
   an amendment is itself correctable.
3. Replay the base events once, using `effective(e)` in place of `e`.

A1 correcting `title` and A2 correcting `body` therefore both survive. The two passes of the
original design collapse into one prepared map plus one replay, so this is smaller than what it
replaces as well as correct.

**Required fields cannot be cleared.** `title` and `body` carry `minLength: 1` in the schema and
`NOT NULL` in `ideas`; clearing either would break the schema, the table and the rendered view at
once (`F6`). The writer refuses it and the fold rejects it on import. Optional contributions —
a note's text, a link — may be cleared, which is how retraction works without deletion.

### The fold validates history, not lines

Every replay implementation becomes one importable function in `src/`, consumed by the writer, the
rebuild, the renderer and the tests. It checks, against the *effective* history:

- a `created` event exists and is unique per idea, and precedes every other event;
- `event["from"]` equals the status replay has actually reached — the single highest-value check in
  the redesign (`F5`), because without it an amendment can retroactively legalise a chain that never
  held;
- the `from -> to` pair is in the schema's transition table;
- `revisited` fires only from `discarded`, and at most once.

It runs **before** any append and **before** the rebuild drops a table. `rebuild_db.py:88-90` drops
every table before inserting, so an invalid log currently empties the whole database — projects
included — rather than failing the ideas projection alone.

## What was decided

- **Nested precedence (`C02`) — confirmed as append order (2026-09-08).** When A1 amends the base
  and A2 amends A1, and a later A3 amends the base directly, A3 applies last simply because it was
  appended last, independent of which event it names as `amends`. `phase-idea-07` implements this as
  one merge over the flat append order, never resolving chains to separate slots first — see
  `src/db/ideas.py`'s `_effective_fields`.
- **Amendment reason (`Q-A3`) — confirmed optional (2026-09-08).** No reason field was added. The
  `amends` pointer and the field-shape delta are already auditable on their own, matching the
  owner's stated preference against ceremony.
- **Identity encoding — settled by implementation.** `src.db.ideas.new_eid()` uses nanosecond epoch
  time as fixed-width lowercase hex (`f"e{time.time_ns():016x}"`), which sorts lexicographically in
  write order without parsing. `identity()` falls back to a SHA-256 digest of the event's canonical
  JSON encoding (sorted keys, no extra whitespace), truncated to 16 hex characters, for the events
  written before `eid` existed.

## What remains open

- Correcting several events in one logical repair still means several appended amendments. The
  minimal writer supports one append at a time; a multi-record repair is out of scope.

## What it touches

`schemas/idea.schema.json` (new `amended` event, optional `eid`, the field-shape definition),
`sql/001_schema.sql` (primary key, `eid` column), `tools/append_idea.py`, `tools/rebuild_db.py`,
`test/test_ideas.py`, and the new single-source replay module in `src/`. It does not touch a single
existing byte of `_data/ideas.jsonl`.

## How it is verified

`R03`, `R05`–`R08`. Sibling amendments to `title` and `body` both survive. A nested chain resolves.
Absent, forward and foreign targets are refused. Two events resolving to one identity fail the fold.
Required-field clears fail; optional clears succeed. An early transition amended into one that
contradicts a later `from` is refused before append and rejects an imported log before the rebuild
writes anything. A synthetic branch-merge fixture interleaves two worktrees' appends and proves every
`amends` pointer still resolves. Raw row count equals log line count, including retracted
contributions.

## Conflicts with other categories

`C01` is resolved here rather than deferred. `C03` fixes the boundary between clearable optional
contributions and unclearable required fields, which `PLAN-017.04` relies on for retraction.
`C07` is resolved by identity rather than by the serialisation contract the parent plan previously
carried. `C04` (final-state-only display) is a rendering decision owned by `PLAN-017.05`; this
document guarantees only that raw history stays separately queryable. `C18` recorded that the
mandatory-reason recommendation was never approved; it is now settled as optional (2026-09-08, see
What was decided) rather than mandatory.
