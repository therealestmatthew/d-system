---
schema_version: 1
id: doc-session-system-boundary-prompt-rubric
code: SESS-2026-09-26-04
title: System boundary prompt classification rubric
kind: session
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-gov-docs]
depends_on: [doc-system-boundary-study-prompt-rubric, doc-system-boundary-study-requirements]
---

# System boundary prompt classification rubric

## Outcome

Completed the evidence deliverable for the prompt-rubric pilot (`phase-bnd-02`): a five-field
classification model and independently reasoned assignments for PROMPT-006, PROMPT-010,
PROMPT-020, and PROMPT-040. The work did not classify the remaining prompt corpus or alter any
prompt lifecycle status.

## Evidence

- [Prompt classification rubric and pilot](../00-working/boundary-study/prompt-classification-rubric.md)
  records the baseline revision `6be599416d1bfcf7af517cc0f58ab2c4cd3c1334` and a 40-prompt
  measurement.
- The field model keeps operational role, reuse disposition, precedent status, review disposition,
  and default entry point independent. The pilot includes prompt-local and governance citations for
  every assignment.
- `uv run python -m src.governance`: pass — 43 systems, 376 documents, 32 memories, 323 backlog
  phases.
- `git diff --check`: pass.

## Scope boundary and handoff

This phase did not read `_private/`, classify any prompt beyond the four required pilots, amend a
prompt, change a lifecycle status, or alter runtime behaviour. The backlog remains **active**
pending owner-controlled review and completion. The branch is ready for review once final
verification is recorded; `phase-bnd-05` remains blocked until this phase is completed.
