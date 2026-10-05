---
schema_version: 1
id: doc-session-source-references
code: SESS-2026-10-05-02
title: Enforce source references and global identities
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-contracts, sys-projection, sys-delivery]
depends_on: [doc-reliability-follow-up]
---

# Enforce source references and global identities

## Phase

`phase-rel-03`: Enforce source references and global identities. PLAN-004 step 2, the
cross-record half: the schema preflight from `phase-rel-02` now also checks that references
resolve and that IDs are unique. Run overnight on 2026-10-04/05 as Session 5 (Batch Runner,
`agent-batch-runner`). The Session Manager assigned it, and the owner pre-approved the assignment (O1).

## Verification

The phase's verification entry is prose ("Run source-integrity tests for missing references,
duplicate IDs and valid repository-scope memory"). These are the tests added to
`test/test_source_validation.py` that it refers to:

- Missing references: `test_unknown_entity_reference_names_record_field_and_id` (13 cases:
  project tags and stakeholders, person projects, commitment project, task commitment, project
  and tags, interaction participants, decision decided_by, interaction_id and supersedes,
  waiting-on project, development-event tags), `test_unknown_tag_relation_is_reported`,
  `test_unknown_memory_reference_is_reported` (project, tags, related),
  `test_repository_scope_is_not_a_project_for_entities`.
- Duplicate IDs: `test_duplicate_task_across_commitments_names_both_files`,
  `test_duplicate_entity_ids_name_both_files` (projects, people, commitments),
  `test_duplicate_tag_ids_name_both_entries`, `test_duplicate_memory_ids_name_both_files`,
  `test_same_id_in_different_kinds_is_not_a_duplicate`.
- Valid repository-scope memory: `test_repository_scope_memory_is_valid_without_a_project_record`
  (scope global and scope project).
- Other cases: `test_fully_cross_referenced_tree_passes`, `test_null_references_are_not_errors`,
  `test_unconfirmed_names_in_promised_to_are_not_references`,
  `test_schema_invalid_record_is_not_reported_again_as_a_reference`,
  `test_reference_failure_leaves_an_existing_projection_unchanged`.

Removing `validate_identities(records)` from `validate_sources` makes 23 of the 30 tests added in
the first commit fail. The 7 that still pass are the positive cases, which should pass without
the check.

Run after rebasing onto `dev` at `b53a1cd`, in the worktree:

`uv run pytest -q test/test_source_validation.py test/test_rebuild.py`

```text
83 passed, 1 warning
```

`uv run pytest -q`

```text
1545 passed, 1 skipped, 1 warning
```

`uv run python tools/check_test_baseline.py base.xml branch.xml` (base: `pytest --junitxml` on
`b53a1cd` in a temporary `git clone --shared`, deleted after)

```text
Test baseline OK: 1513 tests passed in the base; none is missing or skipped in the branch (1546 tests in the branch, 1514 in the base).
```

`uv run python tools/check_diff_patterns.py dev..HEAD`

```text
Diff patterns OK: no added type-ignore, cast(Any, or broad except/pass in dev..HEAD.
```

`uv run ruff check src/ test/` and `uv run mypy src/`

```text
All checks passed!
Success: no issues found in 48 source files
```

`uv run python -m src.governance`

```text
Governance OK: 45 systems, 442 documents, 37 memories, 347 backlog phases
```

`uv run python -m src.governance --containment phase-rel-03` (report only)

```text
phase-rel-03: (dev...agent/phase-rel-03)
  test/test_rebuild.py - outside declared systems; owned by sys-delivery
```

The owner's real records were also validated, with
`D_SYSTEM_DATA_ROOT=/code/d-system/_private/portfolio` and only the count printed:
`real portfolio errors: 0`. The new checks therefore do not block the owner's own rebuild.

## Acceptance

- Unknown references and duplicate tasks across commitments identify both source records: Met. A
  duplicate is reported on the later file and names the earlier one
  (`test_duplicate_task_across_commitments_names_both_files`). An unknown reference names the
  record holding it, the field and the missing ID; there is no second record to name.
- Validation failure leaves an existing temporary projection unchanged: Met.
  `test_reference_failure_leaves_an_existing_projection_unchanged` builds a database in a temporary
  tree, adds a task naming a missing project and re-runs `rebuild()`. `rebuild()` exits, and the
  database file is byte-identical afterwards.

## Backlog

`status: active`, `agent: agent-batch-runner`. `next_action`: All acceptance met and reviewed;
awaiting the owner's merge approval via the Session Manager, then completion on dev.
`completion_evidence`: `src/db/source_validation.py`, `test/test_source_validation.py`,
`test/test_rebuild.py`, this record.

## Unresolved

- `test/test_rebuild.py` belongs to `sys-delivery`, outside the phase's declared systems
  (containment report above). See Decisions.

## Review

The reviewer was a fresh `demo-adversary` sub-agent. It reviewed `dev...HEAD` at the first build
commit and was given the phase's scope, acceptance, verification and deliverables, and no session
record. Its findings, verbatim in substance:

- Scope, references and duplicate IDs: Met. It ran the mutation (checks stripped) itself, and 23
  new tests failed.
- Scope, repository memory scope `d-system`: Met. The exemption is limited to a memory's `project`
  field. A task with `project_id: d-system` is still rejected.
- Acceptance, unknown references and duplicate tasks identify both records: Met. An unknown
  reference can only name the one real record and the missing ID.
- Acceptance, projection unchanged: Met. `rebuild()` validates before `mkdir` and `connect`. It
  re-ran the byte-identity test.
- Verification: 152 passed on focused files; full suite 1543 passed, 1 skipped; ruff, mypy and
  governance clean.
- Finding 1 (should-fix): `decision.interaction_id` and `decision.supersedes` are confirmed-ID
  references left unchecked, with no comment or test, and no SQL foreign key catches them
  downstream. It judged this outside the literal scope list and not a blocker.
- Finding 2 (note): a file that is both schema-invalid and a duplicate ID reports only its schema
  error. The rebuild still halts. This is the documented trade-off.
- Findings 3 and 4: no discrepancy in `D_SYSTEM_DATA_ROOT` handling, in the rule that the same ID
  in different kinds is not a duplicate, or in duplicate ordering.

Finding 1 was fixed in `964eab8`: both fields were added to `REFERENCES["decision"]`, with two
test cases. Finding 2 is accepted as documented behaviour.

## Decisions

- OVERNIGHT ASSUMPTION: the new checks leave out `promised_to` and `owed_by`. Their schemas allow
  the name as written until an identity is confirmed (ADR-008), so an unresolved value there is
  not an error. A comment in `REFERENCES` says so, and a test pins it.
- OVERNIGHT ASSUMPTION: `decision.interaction_id` and `supersedes` were first left out as outside
  the scope list. After review finding 1 they were added. This is the safer option, the change is
  inside `sys-contracts`, and the owner's real records still validate with 0 errors.
- OVERNIGHT ASSUMPTION: `d-system` is exempt only as a memory's `project`, per ADR-001. It is not
  accepted as a `project_id` on any entity. A constant names it in `source_validation.py`. The
  governance check's own copy of the same exemption in `src/governance/__main__.py` was left
  alone, because it belongs to `sys-governance`.
- References are checked only across records that passed their own schema, so a malformed file
  is reported once and not again as a series of broken references.
- `test/test_rebuild.py`'s "task loads with any combination of parents" fixture referenced
  commitment `c-1` without writing it, and the new check rejected it (2 failures). The fixture now
  writes the commitment. The file is the rebuild loader's test, but the containment report assigns
  it to `sys-delivery`, outside this phase's systems. No active phase holds `sys-delivery`. Under
  the overnight contract this was sent to the Session Manager as BLOCKED, with the change attached
  for an accept-or-park decision.

## Corrections

None.

## Left undone

Completion on `dev` waits for the owner's merge approval, relayed by the Session Manager.
`--next-code session` reserved `SESS-2026-10-05-01` on its first call this session, before this
record was written. This record uses `-02`, from the second call.
