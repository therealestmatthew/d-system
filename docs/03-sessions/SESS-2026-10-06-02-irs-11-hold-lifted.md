---
schema_version: 1
id: doc-session-irs-11-hold-lifted
code: SESS-2026-10-06-02
title: Record the owner's ruling lifting the phase-irs-11 hold (build fail closed)
kind: session
status: active
owner: repository-owner
created: '2026-10-06'
updated: '2026-10-06'
systems: [sys-gov-docs]
depends_on: []
---

# Record the owner's ruling lifting the phase-irs-11 hold (build fail closed)

## Phase

Unclaimed: owner-directed work assigned by the Session Manager, with no backlog phase. Peers held no
lock against it. The branch is `agent/fix-irs-11-hold`, in
`/code/d-system-worktrees/fix-irs-11-hold`, cut from dev `d217a1c5`.

The work records the owner's ruling of 2026-10-06, "Build it, fail closed", which the Session
Manager relayed in its `ASSIGN`. The ruling lifts the hold on `phase-irs-11` (run budgets, hard caps
and the kill switch). The phase builds the mechanism with no cap values, and nothing dispatches
until a cap is configured.

## What changed

- `GOV-003`: a new entry, "The phase-irs-11 hold is lifted: build the run caps fail closed —
  2026-10-06". It records the ruling, the deadlock it resolves (`phase-irs-12`'s baselines depend on
  `phase-irs-14`, which depends on `phase-irs-11`), and that cap values remain the owner's, set from
  measured baselines.
- `backlog.yaml`, `phase-irs-11`'s own lines only:
  - status `blocked` to `queued`, with `blocked_reason` and `resume_when` removed along with the
    hold;
  - scope rewritten to the fail-closed mechanism;
  - acceptance gains the no-cap refusal and "no cap value shipped";
  - verification gains the placeholder test `no_cap_refuses_dispatch`;
  - next_action names the lift.

  Systems (`sys-realization`) and deliverables (`src/`, `test/`) are unchanged: the rewrite did not
  need different ones. The `updated` dates of `backlog.yaml` and `GOV-003` are now 2026-10-06.
- Catalog regenerated.

Not changed, as the assignment directed:

- `batch-007`'s table, in the first commit; its hold sentences were changed after review, as
  described under Review. Its prose states the hold, at lines 12–13, line 23 and lines 57–62
  ("…phase-irs-11 returns to queued and this table opens normally."). That table's composition and
  prose are the owner's, so the Session Manager is taking those lines to the owner.
  `batch-003`'s notes, lines 14–18, also describe the hold, as history.
- The Standby Builder's review of `phase-irs-11` (two fixes and three questions) goes to the owner
  separately and is not applied here.

## Review

The Session Manager's gate at `07396f3d` passed. As unclaimed work, the review produced no verdict
records; the raw replies are kept under
`_working/session-manager/verdict-evidence/fix-irs-11-hold/`.

- The gating `demo-adversary` passed with two minor findings. Batch-007's notes and
  `verified.method` still said `phase-irs-11` is on owner hold (minor 1), and batch-003's lines
  14–18 said the same (minor 2).
- The shadow `review-judge` passed, with no findings.

**Owner ruling, 2026-10-06 (in the Session Manager's session):** fix that prose in this branch
before merging. Edit only the sentences about the `phase-irs-11` hold, so they say the hold was
lifted on 2026-10-06, with `batch-003`'s kept as history.

What was done:

- `batch-007`: the provenance sentence, the `verified.method` clause and the notes now say the hold
  was lifted on 2026-10-06 (`GOV-003`).
- `batch-003`: the provenance sentence keeps the hold as history and adds the lift.
- Each table's `updated` date is now 2026-10-06.
- No composition, stage, phase, status or exclusion changed.
- Both tables validate against `schemas/batch.schema.json`.

## Verification

In the worktree, after the first commit:

```
uv run python -m src.governance --check-ideas   Idea field check: 102 phases name 170 ideas; 0 phases differ (0 missing, 0 extra)
uv run python -m src.governance                 Governance OK: 45 systems, 454 documents, 37 memories, 347 backlog phases
uv run pytest                                   1655 passed, 1 warning in 206.25s (0:03:26)
```

After the batch-table change: governance OK (455 documents); pytest 1655 passed.
