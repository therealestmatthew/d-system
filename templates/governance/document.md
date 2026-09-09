---
schema_version: 1
id: doc-replace-me
code: SERIES-NNN
title: Replace with a concrete outcome
kind: plan
status: draft
owner: repository-owner
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
systems: []
depends_on: []
---

# Concrete outcome

Replace `code` with the output of `uv run python -m src.governance --next-code <kind>`, and name this file `<code>-<slug>.md`.

## Context and scope

What problem exists, where is the evidence, and what is included?

## Work and dependencies

List the smallest useful steps and prerequisites. Use `parent` for multi-file plans.

## Acceptance and verification

State observable outcomes and commands. When complete, add existing implementation/test
paths to `completion_evidence`, record actual results here, and update status/date.

## Open questions

Record decisions still needed. Adapt these sections to the document kind; ADRs need
context, decision, alternatives, consequences and a revisit trigger.
