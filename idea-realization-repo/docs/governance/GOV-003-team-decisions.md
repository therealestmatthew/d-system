---
schema_version: 1
id: doc-team-decisions
code: GOV-003
title: Team decisions log
kind: governance
status: draft
owner: repository-owner
created: '2026-10-15'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Team decisions log

This is the backlog's decision record: `backlog/backlog.yaml` names it in `decision_record`. The
backlog protocol (`plugins/idea-realization/docs/backlog-protocol.md`, sections 12 and 13) says what
must be written here, and the repository check reads it.

## What goes here

- **A choice made to resolve a collision between phases**: which phase yields, whether a boundary
  moves, whether a phase splits or widens its declarations, which implementation is kept. The
  entry goes in the same change as the choice. A mechanical keep-both merge needs no entry.
- **A source-code conflict between phases declared disjoint**: always an entry, because it means
  the declarations the concurrency check relies on were wrong.
- **A phase that leaves `complete`**, or stays complete but loses `session`,
  `completion_evidence` or `result`. The entry names the phase id and is added in the same change;
  without it the repository check fails that change.

A commit message is not a record.

## Entry format

One entry per decision, newest last, under `## Entries`:

```markdown
### <date> <phase id(s)>: <what was decided>

Decided by <handle>. <Why, and what it rules out.>
```

## Entries

None yet.
