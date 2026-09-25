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

Run in `/code/d-system-worktrees/phase-idg-01` on `agent/phase-idg-01`, rebased onto dev `6903db8`.

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

`status: complete`, `agent: agent-builder-a`, `session: doc-session-idea-schema-bundle`, set on dev
after the owner-approved fast-forward of `agent/phase-idg-01` (`0008788`). `completion_evidence`
names this record, ADR-024, the three bundle files and the new test file.

## Unresolved

- Consumers outside this phase's lock still hard-code the five old statuses
  (`tools/overview_metrics.py`, `src/api/routes/workbench.py`, `src/orchestrator/state.py`), recorded
  as idea `000463`.
- The DuckDB projection stores the new events' common columns but has no columns for
  classification, `closes_with` or `target_code`, recorded as idea `000464`.
- `tools/generate_ideas_md.py` renders a link as `` `{target}` ``, so a document link would render as
  `None` in `docs/00-working/ideas.md` once one is written, and renders neither classification nor
  `closes_with`. None is written yet; the file is outside this phase's deliverables. Recorded as idea
  `000465`.
- OPS-005's hand-written prose predates annotate and link and does not mention the new commands;
  only its generated `--help` block was regenerated.

## Review

Independent adversarial review by a `demo-adversary` sub-agent (the owner chose the type, since no
reviewer type is scoped to this track), over `dev...HEAD` at `d5e03f6`. It re-ran pytest (1115
passed), governance, ruff and mypy, all matching the record, and probed the schema and the real log
directly. Its verdicts and findings, as reported:

- **R01 — Met.** `record_kind` and four separate enum fields; tag rejection reproduced directly.
- **R04 — Met, with a schema-level gap (Finding 2).** `target_code` is distinct and checked against
  `document_codes()`, reused rather than re-scanned.
- **R05 — Met.** `component_of` with inverse `has_component`; `lineage` covered by the unchanged
  author check at `tools/append_idea.py:408`.
- **R06 — Met.** `8d00f7c` touches the three files together.
- **R07 — Met.** The branch touches no line of `_data/ideas.jsonl`; the fold-identity and prefix
  tests pass against the real corpus.
- **Agent lineage rejected — Met.**
- **Closes legal, pointer-required, promoted → delivered — Met**, confirmed by direct schema probes.

1. **[Major] The 000099/000129 reversal was not written to the real log.** Both fold to `reviewing`.
   The mechanism is shipped and tested against the exact case, but no status event was appended,
   and the record's Unresolved section did not mention it. The reviewer asked for an explicit ruling
   on whether that write is this phase's job.
2. **[Should-fix] The `linked` branch's `oneOf` let a `supersedes` or `component_of` link carrying
   both `target` and `target_code` validate**, contradicting the owner's ruling that only `extends`
   and `relates_to` may point at a document. Not reachable through the writer, which checks
   `DOCUMENT_LINK_TYPES` first, but `fold()` and the rebuild preflight would accept a hand-written line.
3. **[Note] `generate_ideas_md.py` renders a document link as `None`.** Already disclosed; confirmed.
4. **[Note] The hard-coded old statuses and the projection gap degrade gracefully.** `workbench.py`
   sorts an unknown status last via `.get`, and `rebuild_db.py` omits the new columns; tracked as
   `000463` and `000464`.
5. **[Note] The `link_diagnostics()` filter change is necessary and correct.**

No defect was found in ADR-024's claims, the pointer patterns (361/361 real codes and 318/318 real
phase ids match), or the pointer resolvers.

**Disposition.** Finding 2 is fixed: the type restriction now applies whenever `target_code` is
present (`if`/`then` in the `linked` branch), and `test_only_extends_and_relates_to_may_point_at_a_document`
covers both targets together on `supersedes` and `component_of`; full gates re-run green after the
rebase onto `6903db8`. Finding 1 is accepted as outside this phase, and the owner confirmed that
acceptance when approving the merge on 2026-09-25; the move stays with `phase-idg-13`. The reasoning: the scope bullet says what remains "is a status move from reviewing to resolved, which the
transition table must allow". This phase makes the table allow it (`reviewing → resolved`, tested by
`test_a_revisited_idea_moves_from_reviewing_to_resolved`). `phase-idg-13`'s scope names the move itself
("Move 000099 and 000129 to resolved"), its deliverables are `_data/ideas.jsonl`, and its acceptance
requires every close it writes to carry `proposed_by` through `phase-idg-14`, a field this phase must
not add. This phase's deliverables exclude the log. Findings 3–5 need no action.

## Decisions

- **Classification is a `classified` event, not fields on `created`.** A `created` line is
  permanent, and the backfill and the classification agent both have to append. Recorded in ADR-024.
- **The owner ruled four shapes** when asked: pointers are a typed `closes_with` list resolved at
  write time; the new closes are reachable from every working state, and from `promoted` only to
  `delivered`; confidence is a 0 to 1 number per axis; document links use a separate `target_code`
  field, only on `extends` and `relates_to`. Each was the recommended option.
- **New fold keys appear only where the data does** (`closes_with`, `classification`, a link's
  `target_code`). REQ-014 R07 asks for identical derived state, and always-present `None` keys
  changed every legacy link and idea. Consumers read them with `.get()`.
- **`document_codes()` lives in `src/governance/__main__.py`**, built on `audit`'s own walker and
  front-matter parser, as the `next_action` required.
- **OPS-005 was added to the deliverables on dev** (`c33dc3b`, through a Session Manager turn),
  because the writer's new flags made its generated `--help` block stale.
- **The reviewer type was `demo-adversary`**, chosen by the owner.

## Corrections

- The first fold change added `target_code: None` to every link, which broke an existing test and
  R07's identical-state reading. Replaced with conditional keys.
- The pointer rule first sat in its own `allOf` clause keyed on `event: status`, which the
  transition-table test mistook for the status branch. It moved inside the status branch.
- Review finding 2 was a real schema hole, fixed as above.

## Left undone

- **The 000099/000129 status move** belongs to `phase-idg-13`, per the review disposition above.
- **The three knock-ons outside the lock** (`000463` status consumers, `000464` DuckDB projection,
  `000465` renderer) are recorded as ideas for later phases, since each file is outside this phase's
  deliverables.
- **OPS-005's hand-written prose** still describes only `add`, `status`, `revisit` and `amend`; it
  was already behind before this phase and only its generated block was in scope.

