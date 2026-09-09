---
schema_version: 1
id: doc-idea-plan-annotations-links
code: PLAN-017.04
title: Annotations and relationship contributions
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection, sys-memory-agents]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Annotations and relationship contributions

## What we know

The triage agent (`phase-idea-02`) is queued and unbuilt. Its acceptance says it records what it
finds on the entry and never advances an idea past `triaged`. **It currently has nowhere to write
that finding.** The event grammar has three types and none of them carries prose after capture.
This is the concrete reason annotations exist, and it is why they precede tags.

Seven of nineteen ideas already reference other ideas in their prose — `000004` names `000002`,
`000009` names `000003` and `000007`, and five more. The references are real and unindexed. The
brief's claim of sixteen was wrong; so was the claim that nothing connects them.

`L2` — one typed `annotated` event — is confirmed in the transcript at lines 813-814, and the
accepted proposal at 559-562 includes an author and a kind. `L6` (supersession as a link plus a
`discarded` status) and `L10` (terminal states still accept annotations) are **brief-supplied and
not transcript-confirmed**; they are constraints of this task, not quoted decisions.

## What we propose

### The annotated event, kept small

```
{"idea": "000017", "event": "annotated", "at": "<written>", "eid": "<new>",
 "author": "repository-owner" | "<agent name>",
 "kind": "note" | "finding" | "assessment",
 "text": "..."}
```

Three kinds, chosen because each has a caller today: `note` is the owner thinking aloud, `finding`
is what the triage agent writes, `assessment` is a judgement that may later be superseded by another
assessment without either one being deleted. No elaborate vocabulary, no registry, no author table.
An unknown kind fails validation rather than being accepted as free text, so adding a fourth is a
deliberate schema change and not a typo.

Annotations **accumulate**. An amendment corrects one annotation's own `text`; it never rewrites the
collection. This is the distinction `C03` turns on: the accumulated set of contributions is not a
field, so no amendment can address it as one.

**Terminal statuses accept annotations.** `promoted` and `discarded` end the *state machine*; they
do not end the record. A note explaining a year later why a discarded idea was right to discard is
exactly the value an append-only log exists to hold. Annotations carry no `from`/`to` and so cannot
move a status — which is what makes permitting them on terminal ideas safe rather than a loophole
(`C05`).

### Relationships, three types only

```
{"idea": "000016", "event": "linked", "at": "<written>", "eid": "<new>",
 "type": "extends" | "supersedes" | "relates_to",
 "target": "000015"}
```

Three types, because three cover every prose reference now in the log. Each edge is stored once, on
the idea that asserts it; the inverse is derived at fold time and never stored, so the two halves
cannot disagree.

Cycles are **flagged at fold time, never rejected at write time**. A cycle in `extends` is a
modelling mistake worth surfacing, but refusing the append would put the owner in the position of
arguing with a graph checker while trying to record a thought — the failure `ADR-010` exists to
prevent. Capture always wins; the diagnostic goes in the report.

A link never mutates anything. `supersedes` does not discard its target: retiring an idea is a
separate, explicit status event. If a superseded idea is later legitimately revisited, the edge
remains historically true and the fold reports a diagnostic that a working idea is related as
superseded — it does not reject the revisit and does not silently drop the edge (`C06`).

Retraction is a `clear` on the link's own optional payload, per `PLAN-017.03`. Nothing is deleted.

### What we deliberately do not build

**Tags and classification are deferred**, with a stated gate: **60 captured ideas, or one recorded
instance of failing to find an idea that was known to exist.** At 19 ideas with zero transitions
there is no retrieval pressure, and the tags-versus-links boundary (`Q-F2`) is genuinely unresolved
— resolving it under time pressure is how a vocabulary becomes permanent by accident. The owner did
request retroactive tagging (transcript 114-116); this records the request and its resume condition
rather than discarding it.

**Prose references are not auto-promoted to edges.** An extractor over the seven known references
would produce edges nobody asserted. Extraction may *propose*; only a written `linked` event
asserts (`C17`).

## What is open

- Whether `assessment` needs a score field, or stays prose. Recommend prose until an actual scoring
  workflow exists; a number with no defined scale is worse than a sentence.
- Whether the fold reports link diagnostics per idea or once per graph. Cosmetic, but it decides
  whether the renderer can stay a pure function of one idea's events.
- Whether an agent may write a `note`, or only a `finding`. Recommend restricting agents to
  `finding`, so the owner's voice in the log stays unambiguous. Not settled.
- The six candidate edge types from transcript 582-598 were an assistant proposal, not a decision.
  Three is the recommendation; the other three are available if a real relationship cannot be
  expressed.

## What it touches

`schemas/idea.schema.json`, `sql/001_schema.sql` (annotation and link projections off
`idea_events`), the replay module, `tools/rebuild_db.py`, `tools/generate_ideas_md.py`,
`.claude/commands/idea.md`, and `phase-idea-02`'s scope — which must be updated to write findings
through the sanctioned writer before it is executed, not duplicated by a second triage phase
(`C13`).

## How it is verified

`R09`, `R10`, `R12`. Every author and kind combination round-trips. Notes on `promoted` and
`discarded` ideas leave status unchanged. Text replacement and clearing work; siblings survive.
A reciprocal `relates_to` is accepted; an `extends` cycle is flagged and still written. Duplicate
contributors and selective retraction behave. Inverse lookups match forward ones by construction.
A render with 100 findings stays readable and its collapse survives a reload in a different process.

## Conflicts with other categories

`C03` and `C05` are the load-bearing boundaries: contributions accumulate where fields replace, and
terminal governs transitions rather than the record. `C06` keeps graph interpretation out of the
state machine. `C12` is the live one — `PLAN-016` explicitly declined a `triaging` status, and `L7`
requires it; that wording changes only when the behaviour ships, not when this document is written.
`C14` limits what the annotation stream can be asked to measure while zero transitions exist.
