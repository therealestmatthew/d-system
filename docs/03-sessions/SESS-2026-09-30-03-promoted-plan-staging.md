---
schema_version: 1
id: doc-session-promoted-plan-staging
code: SESS-2026-09-30-03
title: Where a promoted plan lives before it earns a code (phase-idg-11)
kind: session
status: active
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-gov-docs]
depends_on: [doc-idea-graph-lifecycle]
---

# Where a promoted plan lives before it earns a code (phase-idg-11)

## Phase

`phase-idg-11` — Define where a promoted plan lives before it earns a code. Run by PROMPT-036 as
batch-003's only phase, agent `agent-coord` (Session 5 - Batch Runner). Claimed at 24b9091 and
widened at e70d198.

## Verification

`uv run python -m src.governance`

```
Governance OK: 43 systems, 401 documents, 34 memories, 341 backlog phases
```

`uv run pytest`

```
FAILED test/test_codes.py::test_counter_allocation_skips_reserved_codes - Ass...
1 failed, 1156 passed, 1 warning
```

## Acceptance

- REQ-014 R18 holds (location defined, abandoned-draft case stated, ADR-010 points at it): Not met
  yet. ADR-019, GOV-011 and the ADR-010 pointer exist on the branch, but no validator or
  adversarial review has judged them, and `uv run pytest` above is red.
- Builds on GOV-005's reservation mechanism rather than a second one: Not met yet. Pending the same
  review.
- Consistent with GOV-005's rule that a code is permanent once on the trunk: Not met yet. Pending
  the same review.

## Backlog

`status: active`, `agent: agent-coord`. `next_action`: Decouple
test_counter_allocation_skips_reserved_codes in test/test_codes.py from the live register (owner
ruling 2026-09-29: give it its own reserved list, ADR-004, ADR-005 and ADR-019, so the allocator
arithmetic it checks is unchanged), re-run pytest green, then run PROMPT-036's validator and
adversary on ADR-019, GOV-011, the ADR-010 pointer and the codes.yaml change, then READY to the
Session Manager.

## Unresolved

- One failing test, cause known and fix ruled by the owner (see Backlog). It is not started,
  because the Session Manager called a wind-down.
- The validator and adversary have not run.
- Reconnaissance had reported that no test pins the reserved list; that was wrong, which is how the
  failing test was missed before the claim. Recorded in the coordinator's tracker,
  `_working/session-manager/build-batch-003/tracker.md`.
- The creator agent reserved ADR-026, ADR-027 and GOV-023 with `--next-code` and never used them.
  All three were released by owner approval on 2026-09-29.
