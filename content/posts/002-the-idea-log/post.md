# 002 — The idea log can never be edited

- **Status:** draft
- **Arc stage:** 2 Capture
- **Pillar:** Mechanism
- **Image:** generated diagram ([image.md](image.md), `image.png`)
- **Drafted against:** dev `518642d` (2026-10-04)
- **Posted:** —

## Single post

> Every idea in D-System goes into an append-only log. Nothing in it is edited: a status change, a
> note or a correction is a new event. One script is the only writer, and it does not accept a
> timestamp. 2,717 events fold into the current state of 564 ideas.

## Thread

1. Every idea in D-System goes into one file: an append-only event log. Nothing in it is ever
   edited. A status change, a note, a link to another idea, a correction: each is a new line.
   2,717 lines so far, describing 564 ideas.

2. The log holds only events, never an idea's current state. That state is computed by folding
   the idea's events in order: its status, annotations and links all come from replaying the same
   history.

3. One script is the only writer. An agent supplies the prose; the script generates the id, the
   timestamp and the event shape, validates the result against a JSON Schema, and appends it. There
   is deliberately no way to supply a timestamp.

4. Why this strict: a malformed line is permanent. There is no correction path, only a longer
   history containing the mistake. An agent formatting its own entries will eventually format one
   wrongly, so no agent formats its own.

5. What it does not prevent: two sessions on different branches can both allocate the same next
   id, and git merges two appended lines without a conflict. That happened on two consecutive days.
   I'll cover it when the series reaches multi-session coordination.

## Sources

| Claim | Source |
|---|---|
| Append-only event log; nothing edited; only sanctioned writer | `tools/append_idea.py` docstring, lines 2-6 |
| Script generates id, timestamp, event shape; validates against the schema; appends | `tools/append_idea.py` lines 9-10; `schemas/idea.schema.json` |
| No way to supply a timestamp | `tools/append_idea.py` line 12 |
| "A malformed line is permanent… only a longer history containing the mistake" | `tools/append_idea.py` lines 4-5 |
| "An agent formatting its own entries will eventually format one wrongly" | `tools/append_idea.py` lines 6-7 |
| Current state computed by folding events | `src/db/ideas.py`, `fold()` |
| 2,717 events, 564 ideas | `load_events()` and `fold()` from `src/db/ideas.py` at `518642d` |
| Event kinds include status changes, annotations, links and amendments | event counts at `518642d`: linked 839, annotated 739, created 564, status 550, amended 15, revisited 10 |
| Same id allocated twice; no git conflict; consecutive days | `docs/08-governance/GOV-003-backlog-decisions.md`, "Concurrency collisions", rows 2026-09-12 and 2026-09-13 |
