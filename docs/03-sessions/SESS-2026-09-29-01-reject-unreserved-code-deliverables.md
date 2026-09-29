---
schema_version: 1
id: doc-session-reject-unreserved-code-deliverables
code: SESS-2026-09-29-01
title: Reject backlog deliverables claiming an unreserved code
kind: session
status: active
owner: repository-owner
created: '2026-09-29'
updated: '2026-09-29'
systems: [sys-governance, sys-backlog]
depends_on: [doc-code-reservation-enforcement]
---

# Reject backlog deliverables claiming an unreserved code

## Phase

`phase-gov-01` — Reject backlog deliverables claiming an unreserved code.

## Verification

```text
$ uv run pytest test/test_backlog.py
50 passed, 1 warning
```

```text
$ uv run python -m src.governance
Governance OK: 43 systems, 398 documents, 34 memories, 341 backlog phases
```

## Acceptance

- A fixture phase naming an unreserved code fails with the phase and code named — Met:
  `test_deliverable_claiming_unreserved_code_fails` asserts the exact message naming
  `phase-demo-01`, the file and `ADR-007`, and tells the reader to reserve it in `codes.yaml`.
- A fixture phase naming a retired code fails with the retired-code message — Met:
  `test_deliverable_naming_retired_code_fails_with_retired_message` asserts the separate message
  for `PLAN-011`, which points to `--next-code`.
- A deliverable naming an existing document passes, including a sub-code and a dated session code —
  Met: `test_deliverables_naming_existing_or_reserved_codes_pass` covers `PLAN-039`, `PLAN-039.01`
  and `SESS-2026-09-06-04`, and `test_unknown_dated_code_is_not_misread_as_counter_code` confirms a
  dated code is read whole.
- A deliverable carrying no code, such as AGENTS.md, passes — Met: the same passing test includes
  `AGENTS.md` and `docs/09-backlog/backlog.yaml`.
- The current repository passes unchanged, including every deliverable that passes only by a
  register reservation — Met: governance is OK on the live backlog.
  `test_repository_reservation_only_deliverables_pass` asserts that every reservation-only code is
  reserved. A direct count found 111 coded deliverables, of which five pass only by reservation:
  GOV-012 (`phase-idg-08`), ADR-019 and GOV-011 (`phase-idg-11`), ADR-004 (`phase-rel-04`) and
  ADR-005 (`phase-rel-05`).

## Backlog

`status: active`, `agent: agent-standby-3`, `session: doc-session-reject-unreserved-code-deliverables`.
`next_action`: All acceptance met on agent/phase-gov-01; awaiting owner-approved merge, after which
the completion edit is made on dev.

## Unresolved

The completion edit (`status: complete`, `completion_evidence`, `result`) is not written. The
session-close conditions require the branch to be merged onto `dev` with the owner's approval first,
and the Session Manager's contract places that edit on `dev` inside the merge turn.
