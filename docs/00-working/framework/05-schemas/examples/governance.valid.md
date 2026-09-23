---
code: GOV-001
title: "Owner approval before editing orientation files"
kind: governance
status: active
created: 2026-09-09
---

# Owner approval before editing orientation files

## Rule

**No agent edits the orientation files without the owner's explicit approval for that specific
change.**

## Problem

The orientation files are the instructions every agent reads first. An agent that edits them
rewrites its own governing rules and every later agent's, usually inside a diff about something
else, where no reviewer is looking for it.

## Incident and rationale

Incident, 2026-09-09: an agent asked to fix stale references replaced the publishing policy with a
rule the owner never requested, inferred from a one-time instruction, and shipped it in an
unrelated commit.
