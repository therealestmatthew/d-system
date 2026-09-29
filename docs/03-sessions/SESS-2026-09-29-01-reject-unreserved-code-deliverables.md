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
51 passed, 1 warning
```

```text
$ uv run python -m src.governance
Governance OK: 43 systems, 399 documents, 34 memories, 341 backlog phases
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
  dated code is read whole. `test_code_shape_outside_its_series_numbering_is_not_a_code` confirms a
  code shape is only a code when it matches its series' registered numbering.
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

## Review

Independent review by a fresh `demo-adversary` sub-agent over `dev...HEAD` at 17ef0dc, run before
the fix below. It re-ran the verification commands, `ruff check` and `mypy` in the worktree and
reported, condition by condition:

1. A fixture phase naming an unreserved code fails with the phase and code named — **Met.** Also
   reproduced with a standalone call to `code_claim_errors` against the real `codes.yaml`.
2. A fixture phase naming a retired code fails with the retired-code message — **Met.** The retired
   branch fires before the generic unreserved message.
3. A deliverable naming an existing document passes, including a sub-code and a dated session code
   — **Met.** Width-5-then-width-2 ordering keeps `SESS-2026-09-06-04` whole.
4. A deliverable carrying no code, such as AGENTS.md, passes — **Met.**
5. The current repository passes unchanged, including every reservation-only deliverable — **Met.**
   Independently recomputed: 111 coded deliverables, exactly five reservation-only (ADR-004,
   ADR-005, GOV-012, ADR-019, GOV-011).

Findings:

1. **(should-fix / major)** `deliverable_code()` ignored each series' registered `numbering`, so a
   counter-only series (GOV, ADR, ARCH, REQ, PROMPT, OPS) could be misparsed as a dated code.
   Reproduced: `docs/08-governance/GOV-2026-09-29-01-freeze-notice.md` failed as "claims unreserved
   code GOV-2026-09-29-01". Not triggered by any live deliverable. Suggested fix: accept a match
   only when its grammar matches the series' registered numbering. **Fixed** — see Corrections.
2. **(note)** A deliverable's code is matched by code value only, not by path, so an existing code
   under a different filename passes. Consistent with the stated scope. **Accepted** as out of
   scope.

No other discrepancies found. The diff touches only the declared deliverables plus the session
record, the phase's own backlog lines and the regenerated catalog.

## Decisions

- The claim was pre-approved by the owner for the 2026-09-29 overnight run ("owner pre-approved
  (overnight-2026-09-29)"), relayed by the Session Manager. The claim commit on `dev` was then
  refused by this session's permission classifier. The owner approved it in this session, and said
  commits are approved as needed for this overnight session.
- Codes are read from the start of the filename's stem, trying the five-part dated form before the
  two-part counter form, using `parse_code()` alone. No new regular expression was written, per the
  scope.
- Only series listed in `codes.yaml` count, and only in their registered numbering mode. A
  code-shaped name outside the register, such as `RFC-123-x.md`, is not a claim.
- A code matches an existing document by code value, not path (review finding 2, accepted).
- Directory deliverables that carry no code stay unchecked, per the owner's 2026-09-23 ruling that
  was recorded in the phase's previous `next_action`.
- The completion edit is left for the merge turn on `dev`, as the Session Manager's contract
  requires. `/session-close`'s third completion condition (an owner-approved merge) is not yet met.

## Corrections

- The first version of `deliverable_code()` checked only that the series was registered, not its
  numbering mode (review finding 1). It now takes a series-to-numbering map and accepts a match only
  when the grammar matches the mode. `test_code_shape_outside_its_series_numbering_is_not_a_code`
  covers both directions (a dated shape in the ADR counter series, a counter shape in the SESS dated
  series).
- A new fixture first added an open sub-plan document with no phase, which tripped the unrelated
  open-plan coverage check. The fixture now marks it complete.

## Left undone

- The completion edit on `dev` (`status: complete`, `completion_evidence`, `result`) after the
  owner-approved merge.
- PLAN-010's open question on codes claimed in plan prose, and the directory-deliverable gap. Both
  are out of scope by the plan and by the owner's ruling.
