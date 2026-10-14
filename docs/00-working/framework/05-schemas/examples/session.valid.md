---
code: SESS-2026-10-12-01
title: "Requirement and plan document schemas"
kind: session
status: complete
created: 2026-10-12
phase: phase-fwt-03
agent: agent-builder-a
---

# Requirement and plan document schemas

## Summary

Wrote the requirement and plan schemas and rewrote both draft templates to match the governance
and protocol templates. Added a check that runs the schema, placeholder and retained-sample checks
on any one document, after the first review showed that a copied template could still validate.

## Acceptance

- REQ-024 R04 for the requirement schema — **Met.** The filled example validates; the copy without
  Acceptance criteria fails with "missing section: 'Acceptance criteria'".
- REQ-024 R04 for the plan schema — **Met.** The filled example validates; the copies without Scope
  or Phases fail, each naming the missing section.

## Decisions

- **Required sections** (owner): Overview, Requirements, Scope and Acceptance criteria for a
  requirement; Overview, Scope and Phases for a plan.
- **Reworded sample text is a known limit** (owner, review round 3): the check compares exact text
  after ignoring case and punctuation, and does not use fuzzy matching.

## New requirements

None.

## Deferred and out of scope

The rewording limit was recorded as idea 000695 for a later phase.

## Open investigations

One frontend test run failed once while two full test runs loaded the machine; the failing test was
not identified. Recorded as idea 000696.

## Outstanding actions

None.

## Verification

```text
$ uv run python docs/00-working/framework/05-schemas/check_schemas.py
0 failure(s)
$ uv run python -m src.governance
Governance OK: 46 systems, 484 documents, 38 memories, 364 backlog phases
```

## Completion evidence

- `docs/00-working/framework/05-schemas/requirement.schema.json`
- `docs/00-working/framework/05-schemas/plan.schema.json`
- `docs/00-working/framework/05-schemas/requirement.template.md`
- `docs/00-working/framework/05-schemas/plan.template.md`
- `docs/00-working/framework/05-schemas/check_schemas.py`
