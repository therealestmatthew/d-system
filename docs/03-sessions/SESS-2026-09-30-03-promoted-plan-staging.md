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

Run in the worktree after rebasing onto dev at 51e0924, with the test fix committed at e804461.

`uv run python -m src.governance`

```
Governance OK: 43 systems, 404 documents, 34 memories, 341 backlog phases
```

`uv run pytest`

```
1157 passed, 1 warning in 115.66s (0:01:55)
```

`uv run ruff check src/ test/`: `All checks passed!`. `uv run mypy src/`: `Success: no issues found
in 46 source files`.

The checkpoint run before the fix had 1 failed, 1156 passed; the failure was
`test_counter_allocation_skips_reserved_codes`, which read the live register and assumed ADR-019
was still reserved. Per the owner's ruling of 2026-09-29 it now builds on `bare_register` with its
own reserved list (ADR-004, ADR-005, ADR-019), so the allocator arithmetic it checks is unchanged.

## Acceptance

Judged by a validator (`demo-validator-code`, verdict PASS) and an adversary (`demo-adversary`,
verdict HOLDS), each with no findings. Evidence in
`_working/session-manager/build-batch-003/idg-11-validator.md` and `idg-11-adversary.md`.

- REQ-014 R18 holds (location defined, abandoned-draft case stated, ADR-010 points at it): Met.
  ADR-019 and GOV-011 define `docs/00-working/promoted/<code>-<slug>.md` and the abandoned-draft
  case (delete the draft, release the reservation); ADR-010 points at them.
- Builds on GOV-005's reservation mechanism rather than a second one: Met. The draft uses the
  existing `reserved:` list and `--release-code`; no second ledger.
- Consistent with GOV-005's rule that a code is permanent once on the trunk: Met. ADR-019 and GOV-011
  were reservations until their documents landed; no code is renumbered or reissued.

## Backlog

`status: active`, `agent: agent-coord`. `next_action`: built, verified and reviewed; awaiting the
owner-approved merge.

## Unresolved

- The merge onto dev needs the owner's approval in the Batch Runner session, then the Session
  Manager's GRANTED merge.
- Reconnaissance had reported that no test pins the reserved list; that was wrong, which is how the
  failing test was missed before the claim. Recorded in the coordinator's tracker,
  `_working/session-manager/build-batch-003/tracker.md`.
- The creator agent reserved ADR-026, ADR-027 and GOV-023 with `--next-code` and never used them.
  All three were released by owner approval on 2026-09-29.
