---
schema_version: 1
id: doc-idea-priority-queue
code: PLAN-019
title: Idea priority queue — an ordered next_up for open ideas
kind: plan
status: draft
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio, sys-governance]
depends_on: [doc-idea-record-system]
---

# Idea priority queue — an ordered next_up for open ideas

## Context and scope

[PLAN-016](PLAN-016-idea-record-system.md) gave ideas an append-only event log
(`_data/ideas.jsonl`, `schemas/idea.schema.json`) with a `status` field only:
`open` → `triaged` → `reviewing` → `promoted`/`discarded`. Status says how far an idea has moved,
not which open idea should be looked at next. `docs/09-backlog/backlog.yaml` solves the equivalent
problem for phases with a `next_up` list — "phases that jump the queue, in order; everything else
falls back to priority then ID" — but an idea cannot enter that backlog until a plan exists for it,
so nothing plays that role between "recorded" and "has a plan." Idea `000039` records this gap; this
plan is how it gets closed.

**Out of scope:** promotion criteria, triage judgement, and the idea triage agent's behavior
(`phase-idea-02`, from idea `000007`) — this plan only orders the queue an owner or that agent reads
from. It does not decide what belongs in it.

## Decisions

### The priority list lives beside the log, not inside it

`backlog.yaml`'s `next_up` is a plain ordered list sitting alongside each phase's own record, not a
field on the phase itself. The idea priority list follows the same shape: a new file,
`docs/00-working/ideas-priority.yaml`, holding an ordered list of six-digit idea IDs. This requires
no change to `schemas/idea.schema.json` and no new event type — the append-only log and its legal
status transitions (the thing PLAN-016 was careful to make replayable) are untouched.

```yaml
schema_version: 1
updated: '2026-09-08'
# Ideas that jump the queue, in order. Everything else falls back to status then ID
# (open before triaged before reviewing; lower ID first within a status).
next_up:
- '000039'
```

### The file is hand-edited, like backlog.yaml's next_up

`backlog.yaml`'s `next_up` is edited directly by whoever is reordering the queue; it is not
logged as an event. The idea list follows the same precedent for the same reason: reordering a
queue is an operational decision about attention, not a fact about the idea worth preserving in an
append-only history the way a status change is. `tools/append_idea.py` is unchanged — it still owns
every mutation to `_data/ideas.jsonl` and nothing else gains write access to that file.

### An idea in the list must be open or triaged

An idea already `reviewing`, `promoted`, or `discarded` has moved past the point this queue serves —
it's either being actively judged already or it's terminal. Listing one is a validation error, the
same way `backlog.yaml` rejects a `next_up` entry that is `complete` or `cancelled`
([GOV-002](../08-governance/GOV-002-backlog-protocol.md)).

## Work and dependencies

1. Add `schemas/idea-priority.schema.json` — `schema_version`, `updated` (date, not in the future),
   `next_up` (array of unique six-digit idea ID strings, each present in `_data/ideas.jsonl`).
2. Create `docs/00-working/ideas-priority.yaml` seeded with idea `000039` as its first (and
   currently only) entry.
3. Extend `src/governance` with a check: every `next_up` entry exists in the idea log and is
   `open` or `triaged`; `updated` is not in the future. Fold this into the existing governance run
   rather than a separate command, matching how backlog validation already runs inline.
4. Extend `tools/generate_ideas_md.py` to render the priority order — e.g. a "Priority" section at
   the top of `docs/00-working/ideas.md` listing the queued ideas in order, mirroring how the
   governance CLI's `--ready` report surfaces `next_up` ahead of the full phase table.
5. Update `docs/00-working/README.md` (or wherever the ideas workflow is documented) to name the
   new file and who may edit it.

No change to `tools/append_idea.py`, `schemas/idea.schema.json`, or any existing idea event.

## Acceptance and verification

- `schemas/idea-priority.schema.json` exists and `docs/00-working/ideas-priority.yaml` validates
  against it.
- `uv run python -m src.governance` fails if `ideas-priority.yaml` names an idea ID that does not
  exist in `_data/ideas.jsonl`, or one that is `reviewing`, `promoted`, or `discarded`.
- `uv run python tools/generate_ideas_md.py` renders the priority order at the top of
  `docs/00-working/ideas.md`, and running it twice with no source change produces an identical file
  (deterministic, matching the existing idempotence of that script).
- `uv run pytest` covers: a valid priority file passes governance; an entry for a non-existent ID
  fails it; an entry for a terminal-status idea fails it.

## Open questions

- Should reordering ever need a reason recorded (like a backlog phase's `next_action`), or is the
  file's own diff in git sufficient audit trail? Leaning toward git being sufficient, consistent
  with how `backlog.yaml`'s `next_up` carries no rationale field today.
- Once `phase-idea-02` (the idea triage agent) exists, should it be allowed to *propose* reordering
  this list, or only ever write `triaged` status and findings, leaving ordering to the owner
  entirely? Leaning toward the latter, consistent with that phase's own acceptance criteria ("owner
  judgement is not automated").
