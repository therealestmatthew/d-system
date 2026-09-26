---
schema_version: 1
id: doc-session-system-boundary-study-plan
code: SESS-2026-09-26-01
title: System boundary study plan
kind: session
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-portfolio, sys-realization, sys-plugin, sys-wb-layout, sys-governance]
depends_on: [doc-system-boundary-study-requirements, doc-system-boundary-study]
---

# System boundary study plan

## Outcome

Created the system-boundary study package requested by the owner: `REQ-033`, `PLAN-050`, and
three queued backlog phases (`phase-bnd-01` through `phase-bnd-03`). The package stops at an
owner-decision report and authorises no repository extraction, private-data access, or behaviour
change.

## Evidence

- `uv run python -m src.governance --ready` on 2026-09-26 reported 318 phases: 3 active, 113
  complete, 8 deferred, 84 ready, and 110 waiting. The new study phases were deliberately not added
  to `next_up`.
- The governed corpus scan reported 39 `kind: prompt` documents. The requirements distinguish that
  lifecycle count from reuse classification.
- The first governance run rejected two unquoted YAML list values containing colons in
  `backlog.yaml`. They were quoted, then catalog generation and governance completed successfully.
- Final commands: `uv run python -m src.governance --catalog`,
  `uv run python -m src.governance`, and `git diff --check`.

## Scope boundary

This was owner-directed documentation work with no pre-existing backlog phase, completed on the
unclaimed `agent/boundary-study` worktree branch. It creates the plan and its future phase records;
it does not claim or perform any `phase-bnd-*` study work.

## Next action

The owner may review the branch diff. If the plan is accepted and integrated, claim
`phase-bnd-01` or `phase-bnd-02` according to the normal backlog protocol; they may run in parallel
only if their then-current conflict checks permit it.
