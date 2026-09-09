---
schema_version: 1
id: doc-session-close-contracts-preflight
code: SESS-2026-09-06-06
title: Session close after the contracts and preflight phases
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-contracts, sys-projection]
depends_on: [doc-backlog-decisions, doc-session-entity-contracts, doc-session-source-preflight]
---

# Session close after the contracts and preflight phases

Two phases were executed this session, each with its own record:
[SESS-2026-09-06-04](SESS-2026-09-06-04-entity-contracts.md) for `phase-cap-02` and
[SESS-2026-09-06-05](SESS-2026-09-06-05-source-preflight.md) for `phase-rel-02`. Both ran as
`agent-architect` in worktrees, both integrated to `dev` fast-forward, and both worktrees were
removed. This record covers what belongs to no phase: the owner's decisions at close, and the state
the next session starts from.

## Where the repository stands

`dev` is clean. 264 tests pass; `ruff check src/ test/`, `mypy src/` and the governance check are
green; `tools/rebuild_db.py` projects 33 projects, 28 tags and 7 memories. There is still no remote
and none was added.

The entity model is nine shapes with a settled evidence contract, and no source file can reach the
database without passing it first. Nothing in the capture pipeline is built — intake, structuring,
routing, review and promotion are all still contracts and plans.

## Decisions taken at close

All four were the owner's; the reasoning for the first three is recorded in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md) rather than only here.

**`waiting_on.owed_by` stays unprotected.** I raised it because it is the structural mirror of
`commitment.promised_to`, which ADR-007 protects. The owner declined to widen ADR-007's set of four.
The stakes are not symmetric, and `waiting_on` is a medium-stakes type that already routes to
flagged review regardless of evidence level, so the rule would add a second flag on a record the
owner reads anyway.

**`tools/` joins the documented lint gate.** No new phase was filed: `phase-rel-09` already owned
resolving the script lint issues and pulling this tooling into CI, so its scope, acceptance and
deliverables were widened to include the documented command in `AGENTS.md` and `OPS-001`. That phase
is not ready — it waits on `phase-rel-06`, `-07` and `-08`.

**The contract tests and the preflight must agree about dates.** Filed as `phase-rel-11` under
PLAN-004, whose step 2 already covers invalid-date behaviour. It gets a phase rather than a fix in
passing because it changes `test/test_schemas.py`, a completed phase's deliverable.

**Queue order.** The owner set `phase-cap-03` as the front and asked me to order the rest.

## The queue the next session starts from

`next_up` was empty at the end of the two phases and is now:

| # | Phase | Why here |
|---|---|---|
| 1 | `phase-cap-03` | Owner's choice, and PLAN-009's stated next step: raw capture and staged record shapes, where they live, and the ignore rules keeping them untracked |
| 2 | `phase-rel-11` | Small, and ahead of the schema phases on purpose — every date field added while the two suites disagree widens the gap, and `phase-cap-03` adds a capture timestamp |
| 3 | `phase-cap-07` | Closes a divergence opened this session, and unblocks fourteen `phase-sig-*` and `phase-syn-*` phases that were written against data that did not exist |
| 4 | `phase-priv-02` | Gates the confidentiality sweep, which gates ever adding a remote; real client identifiers are in every commit today |
| 5 | `phase-ses-01` | OPS-001's closing procedure is marked interim until the session taxonomy exists |

## Carried into the next session

- **The DuckDB column is still `commitment_cadence` while the source field is `review_cadence`.**
  The insert is positional so the values land correctly, and it is verified — 33 rows carry a
  cadence, none null. `phase-cap-07` renames the column. Until then the mismatch is real and
  deliberate, not a bug to re-discover.
- **Corrections have no field on any entity schema.** REQ-002 R15 requires promoted records to carry
  dated correction entries. Excluded from `phase-cap-02` on purpose, since its scope limits a
  promoted record to a capture reference and the assumed-field list. `phase-cap-06` will need to add
  the field to all nine schemas.
- **`capture_id` is constrained only to a non-empty string.** `phase-cap-03` owns the raw capture
  identifier and pre-empting its format would have settled that decision by accident.
- **The preflight is wired into `rebuild_db.py` and nothing else.** A capture pipeline writing to
  `_data/` should call `validate_sources` before it writes; `phase-cap-06` is where that lands.
- **`_data/commitments/` and `_data/people/` are empty, and `_data/tasks/` does not exist.** The
  preflight treats a missing entity directory as normal, because capture creates them. Nothing
  downstream has real rows to verify against until `phase-cap-08`.

## Deviations from AGENTS.md

Both phases used worktrees, so the GOV-003 primary-checkout exemption was not relied on. This
closing record was written in the primary checkout on `dev` under that exemption: no peer holds a
claim and nothing here touches `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`.

`phase-cap-02`'s declarations were widened twice mid-phase, each time committed to `dev` before the
work so the wider lock was visible first, and both are reasoned in GOV-003. One change was made
outside a phase's stated scope — the loader's cadence read in `phase-rel-02` — and is stated plainly
in that phase's record rather than folded into its result.
