---
id: mem-proc-send-the-queue-entry-before-you-name-it
title: Send the Queue Entry Before You Name It
type: procedure
tags: [agentic-systems, ai-tools]
source_model: anthropic/claude-opus-5-5
project: d-system
created: 2026-10-03
updated: 2026-10-03
confidence: high
related: []
scope: global
---

## The rule

Name a command entry to the owner (`C9`, `C10`, ...) only after its `QUEUE` message has been sent
to the session that keeps the queue. An id that exists only in your own report is a plan, not an
entry. Say "I will queue" until the send has happened, and then say it was sent.

## What happened (2026-10-03, Session Manager run)

The Session Manager told the owner several times that the run's commits would go out in "one C9
push from the Owner Terminal". It never sent `QUEUE C9`. The owner went to the Owner Terminal,
which reported that it knew of no C9. The owner had to ask for it to be queued.

The Owner Terminal records only entries it receives, and Remote Control does not confirm delivery,
so nothing on either side would have shown the gap until the owner looked.

## The procedure

- **When an owner-only command comes up,** send the `QUEUE <id>` message first, in the same turn
  that first mentions the id to the owner.
- **Before naming an id in a report,** check that the send happened in this session. If it has
  not, either send it now or describe the command without an id.
- **Over Remote Control,** ask the owner to confirm the entry appears in the Owner Terminal's queue,
  since the send itself is not confirmed.
