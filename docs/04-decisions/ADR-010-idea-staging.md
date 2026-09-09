---
schema_version: 1
id: doc-idea-staging
code: ADR-010
title: Park unformed ideas in an ungoverned staging area
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-governance-protocol]
---

# Park unformed ideas in an ungoverned staging area

## Context

There was nowhere to record an idea that is not yet work. The options were all too heavy:

- **A backlog phase** requires `plan`, `sources`, `systems`, `verification` and `deliverables`. An
  idea has none of those, and inventing them is how four documents got manufactured on 2026-09-06 —
  a course production plan, a course extraction plan, the first draft of `PLAN-015`, and the first
  draft of `PLAN-014`, which admitted in its own text that it existed to satisfy a schema.
- **A governed plan** requires a code, front matter and a catalog entry, and commits to an approach
  before one has been chosen.
- **`_working/`** is defined by [PLAN-015](../01-plans/PLAN-015-ephemeral-working-plans.md) as
  ephemeral *task* plans belonging to a queued phase. An idea with no phase does not fit.
- **`status: deferred`** on a phase works — five `phase-mem-*` entries use it — but still demands the
  full schema. It defers *scheduling*, not *ceremony*.

`docs/00-working/` already existed and already held one file, `codex-answers.md`, exempted from the
audit **by exact filename** at `src/governance/__main__.py`. So the directory was a staging area for
precisely one file and nothing else.

## Decision

**`docs/00-working/` is an ungoverned staging area.** The exemption becomes directory-level rather
than per-filename, via `EXEMPT_DIRS`. Anything there carries no code, no front matter and no catalog
entry, and the governance check ignores it.

What it is for:

- Plan ideas that may become plans, and may not.
- Notes about work that will matter later but has no owner today.
- Questions to raise when a related phase comes up.

What it is not:

- **Not a plan.** It commits to nothing and schedules nothing.
- **Not the backlog.** Nothing here is queued, and nothing here is worked.
- **Not `_working/`.** That holds task detail for a phase that already exists; this holds ideas with
  no phase at all.
- **Not a commitment.** An entry carries no obligation to act. It ends in a status — `promoted` into
  a plan, requirement or phase, or `discarded` with a reason — never in silence and never in
  deletion.

## Ideas are recorded as given, not filtered at entry

An entry is never declined, merged or reworded because it overlaps something that already exists.
Overlap is noted **inside** the entry and left for triage.

The reason is that filtering at capture destroys the data the list exists to produce. An idea the
owner raised is a fact about what they were thinking and when, and it stays a fact even if the work
is already scoped elsewhere. Collapsing it at the door means the record no longer shows that the
thought recurred, which is precisely the signal worth measuring later.

This is the same routing principle [ADR-007](ADR-007-capture-routing.md) applies to captured notes:
ambiguity is flagged, not interrupted for. Detecting overlap is a **downstream pass** — see idea
`000007`, an agent whose purpose is triaging this list — not a gate an agent applies while the owner
is still talking.

## The idea list is append-only

> **Amended 2026-09-06 by [PLAN-016](../01-plans/PLAN-016-idea-record-system.md) (`phase-idea-01`).**
> The storage described below has moved. The source of truth is now `_data/ideas.jsonl`, an
> append-only event log, and `docs/00-working/ideas.md` is generated from it by
> `tools/generate_ideas_md.py`. Writes go through `tools/append_idea.py` and nowhere else.
>
> **The staging concept in this ADR stands unchanged** — ideas are recorded as given, never filtered
> or deduplicated at entry, and a discarded idea stays visible. What changed is only where they live.
> Within hours of this decision the list reached ten entries and outgrew markdown: it carried no
> timestamps, so nothing about it could be analysed over time.
>
> Two rules below are superseded by the log's structure rather than by a new rule:
>
> - **"The only permitted edit is the `Status` line"** is obsolete. Nothing is edited at all; a
>   status change appends an event. Immutability stopped being a rule to police and became a fact
>   about the bytes.
> - **The status vocabulary changed.** `investigating` became `reviewing`, and `triaged` was added
>   for the state where scouting has finished and the owner has not yet looked. Transitions move
>   forward only, and a discarded idea may be revisited once.
>
> The format-migration carve-out below did its second job on the way out: the migration into JSONL
> changed no content, and every timestamp was carried across unchanged. Those timestamps were
> observed against a clock as the ideas arrived, so preserving them exactly was preserving real data.
> Every event written since is stamped by the writer from the real clock, which offers no way to
> supply one.

> **Pre-live correction, 2026-09-06.** Entry `000014` was deleted and re-created through the writer
> while the system was still being tested. It had been stamped `15:56:08-05:00` because the machine's
> timezone was set to Central while the owner was in Eastern, so the instant was right but the local
> time of day it recorded was an hour early — and the local offset is kept precisely to show what time
> of day an idea was had. The identifier was reused, and the title and body were carried across
> verbatim; only the stamp differs, now `17:39:22-04:00`.
>
> **This is the same carve-out as the one-time backfill tool**, and it closes the same way. The log
> was hours old, nothing depended on it, and the writer was still being shaken out. The owner's
> condition is explicit: **once the tooling is live, immutability holds without exception.** A
> deletion after that point is not available, and the append-only test exists to make it visible.
>
> The rejected alternative was a `corrected` event type superseding the bad stamp — which honours
> append-only exactly, since it edits nothing. It was declined because it would add permanent
> machinery to the schema, the writer and the projection to fix one row: every future reader of
> `idea_events` would have to know that a stamp might be superseded. That cost is real and outlives
> the mistake; the deletion does not.

`ideas.md` is append-only. New entries are added at the bottom with a **six-digit** identifier; the
only permitted edit to an existing entry is its `Status` line — `open`, `investigating`, `promoted`,
`discarded`.

**One carve-out:** a format migration that changes no content is permitted and must be recorded here.
Entries `001` and `002` were renumbered to `000001` and `000002` on 2026-09-06, while the list was two
entries old. The rule protects the record of what was judged and why; an identifier width carries no
judgement, so nothing it protects was lost. Doing this at entry 400 would have cost far more, and
three digits was chosen without a horizon — see idea `000006`, which audits every other index in the
system for the same defect.

The reason is that a deletable list cannot be trusted for the decision it exists to inform. If an
idea can be quietly removed, the absence of an entry means nothing: it may never have been raised, or
it may have been raised and rejected for good reason. Someone then re-proposes it, and the work of
having judged it once is lost. Keeping discarded entries visible with their reasons makes the list
answer *"has this been considered?"* — which is the question it is actually for.

This is the same principle `GOV-005` applies to document codes, and for the same reason: a record
that can be rewritten stops being evidence.

## Consequences

- The pressure that manufactures governed documents has an escape valve. An agent or the owner can
  record a thought without deciding what kind of document it is — which is the decision that has
  repeatedly been made wrongly and early.
- The list only grows. That is deliberate: pruning means marking `discarded` with a reason, never
  deleting. Length is the accepted cost of the list staying trustworthy, and status makes it
  skimmable without shortening it.
- The audit gains a directory it deliberately does not check. A test
  (`test_idea_staging_directory_is_ungoverned`) asserts that property so a future refactor cannot
  quietly re-govern it.

## Alternatives rejected

**Use `status: deferred` phases.** Rejected: it defers scheduling but not the schema. An idea would
still need a plan behind it, which is the exact pressure this relieves.

**Put ideas in `brain/`.** Rejected: `brain/` is knowledge that is true, retrieved by agents as
context. A speculative to-do is neither, and mixing them degrades retrieval.

**Create a new top-level folder.** Rejected: `docs/00-working/` already existed with an exemption
precedent. Adding a folder to hold things that prevent unnecessary structure would have been its own
joke.
