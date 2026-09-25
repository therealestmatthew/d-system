---
schema_version: 1
id: doc-session-idea-schema-bundle
code: SESS-2026-09-25-01
title: The idea schema bundle and the scope-fork decision
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-contracts, sys-portfolio, sys-governance]
depends_on: [doc-idea-graph-lifecycle]
---

# The idea schema bundle and the scope-fork decision

## Phase

`phase-idg-01` — Ship the idea schema bundle and record the scope-fork decision.

## Verification

Run in `/code/d-system-worktrees/phase-idg-01` on `agent/phase-idg-01`, rebased onto dev `c33dc3b`.

```
$ uv run pytest
1115 passed, 1 warning
```

```
$ uv run python -m src.governance
Governance OK: 43 systems, 361 documents, 32 memories, 318 backlog phases
```

Also run, as the Session Manager's merge gate requires: `uv run ruff check src/ test/` →
`All checks passed!`; `uv run mypy src/` → `Success: no issues found in 46 source files`.

## Acceptance

- REQ-014 R01, R04, R05 and R06 hold — **Met.** R01: `record_kind` and the four axis fields are
  separate closed enums on the schema, and a classification written as a tag or as a label outside
  the enum fails validation (`test_each_arch_005_type_is_one_enum_token_on_its_own_field`,
  `test_a_classification_written_as_a_tag_is_rejected`). R04: `target_code` is its own field; a link
  to `PLAN-029` through the writer folds with `target_code` set and `target` null, and `PLAN-999`
  is refused (`test_a_link_to_a_document_code_is_explicit_in_the_record`,
  `test_a_link_to_a_missing_document_code_is_refused`). R05: `component_of` and `lineage` are written
  and folded through the writer (`test_component_of_is_written_and_folded_with_a_derived_inverse`,
  `test_lineage_is_the_owners_voice`). R06: commit `8d00f7c` touches `schemas/idea.schema.json`,
  `src/db/ideas.py` and `tools/append_idea.py` together, and the full suite passes.
- REQ-014 R07 holds — **Met.** Every idea in the log at `0f142ce` (the last commit before the change)
  that nothing has touched since folds to a state equal to the old fold's, read with the old
  `ideas.py` and schema (`test_every_pre_change_idea_folds_to_identical_state`). The log at `0f142ce`
  is a byte-identical prefix of the current one (`test_the_log_before_the_change_is_a_byte_identical_prefix`),
  and the existing `test_no_committed_line_in_the_log_is_ever_altered` passes. This branch appends no
  line to `_data/ideas.jsonl`.
- An agent author attempting a lineage annotation is rejected by the writer's existing author rule —
  **Met.** `test_lineage_is_the_owners_voice`: the unchanged non-owner-may-only-write-finding rule
  refuses it, and the log is byte-identical afterwards.
- delivered, resolved and absorbed are legal statuses, each rejected by the writer when no pointer is
  given, and promoted accepts a later transition to delivered — **Met.**
  `test_each_close_is_legal_and_terminal`, `test_a_close_without_a_pointer_is_refused` (all three, in
  the writer and the schema), `test_promoted_accepts_a_later_move_to_delivered`.

## Backlog

`status: active`, `agent: agent-builder-a`, `session: doc-session-idea-schema-bundle`.
`next_action`: every acceptance condition is met on `agent/phase-idg-01`; awaiting the independent
review's findings and the owner's merge approval, after which the completion edit is made on dev.

## Unresolved

- Consumers outside this phase's lock still hard-code the five old statuses
  (`tools/overview_metrics.py`, `src/api/routes/workbench.py`, `src/orchestrator/state.py`), recorded
  as idea `000463`.
- The DuckDB projection stores the new events' common columns but has no columns for
  classification, `closes_with` or `target_code`, recorded as idea `000464`.
- `tools/generate_ideas_md.py` renders a link as `` `{target}` ``, so a document link would render as
  `None` in `docs/00-working/ideas.md` once one is written. None is written yet; the file is outside
  this phase's deliverables.
- OPS-005's hand-written prose predates annotate and link and does not mention the new commands;
  only its generated `--help` block was regenerated.
