---
schema_version: 1
id: doc-session-workbench-architecture-quality-plan
code: SESS-2026-09-14-08
title: Finalize the workbench architecture and quality plan (P10)
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-demo-stage
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-architecture-quality-requirements
---

# Finalize the workbench architecture and quality plan (P10)

## Phase

`phase-prog-03` — Finalize the workbench architecture and quality plan (P10). Claimed by
`agent-prog`, worked on `agent/phase-prog-03` in `../d-system-worktrees/phase-prog-03`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 20 systems, 221 documents, 24 memories, 168 backlog phases
```

Exit status 0.

`uv run python -m src.governance --ready`

```
Queued to the front: phase-part-02, phase-prog-01, phase-port-02, phase-ses-01, phase-prog-02,
phase-prog-04, phase-prog-05, phase-prog-06, phase-prog-07, phase-prog-08, phase-prog-09,
phase-prog-10, phase-prog-11, phase-prog-12.

| phase-arch-00 | Decompose sys-ui so frontend phases stop serializing on one lock | — | 1 | ready | — | — |
| phase-arch-01 | Settle the workbench vocabulary and rule on identifier migration | — | 1 | ready | — | — |
| phase-arch-11 | Ports and system processes: lifecycle exploration | — | 2 | ready | — | — |
| phase-arch-14 | Measure workbench performance before designing any cache | — | 2 | ready | — | — |
| phase-arch-16 | Terminal persistence and performance audit across three shells | — | 2 | ready | — | phase-prog-03 |
```

The five dependency-free phases show `ready`; the other thirteen show `waiting` on their declared
prerequisites, which is the intended shape. `phase-prog-03` no longer appears in the queue line.

Additional check, beyond the phase's declared list, run because acceptance condition 2 asserts a
mapping rather than a command result:

```
REQ rows: 29
covered : 29
UNMAPPED: none
phases in plan: 18
phases with >=1 row: 18
PHASES WITH NO ROW: none
```

`uv run pytest`

```
580 passed, 2 warnings
```

## Acceptance

1. **PLAN-028 carries no placeholder banner and states a chosen design — Met.** Grepping the plan
   for the banner's text returns 0 matches. Five numbered design decisions are stated, each naming
   what was chosen and why the alternative was rejected.
2. **A requirement document exists for P10 and every row maps to at least one phase — Met.**
   `REQ-011` carries 29 rows; the coverage check above shows 29 covered and none unmapped. The
   converse also holds: all 18 phases carry at least one row.
3. **G40 is the first implementation phase, and P11's dependency on it is stated — Met, with a
   caveat recorded below.** `phase-arch-01` is `G40` and is the first phase that implements any P10
   idea. `PLAN-028`'s *What P11 depends on* section states the edge: any `P11` phase that renames a
   slot, panel, region or layout identifier declares `depends_on: [phase-arch-01]`, and it is
   `phase-arch-01` specifically rather than `phase-arch-02`. The caveat is that `phase-arch-00` now
   runs before it — see `## Unresolved`.
4. **phase-prog-03 is removed from next_up in the same change that completes it — Met.** The
   `--ready` output above shows the queue line without it, and the removal is in commit `435027c`,
   the same commit that replaced the placeholder.

## Backlog

`status: active`, `agent: agent-prog`.

`next_action`: All four acceptance conditions verified met at close. Awaiting the owner's
`/session-close` review; nothing remains to build.

Evidence recorded: `docs/01-plans/PLAN-028-workbench-architecture-quality.md`,
`docs/06-requirements/REQ-011-workbench-architecture-quality.md`, `docs/09-backlog/backlog.yaml`,
`docs/09-backlog/README.md`.

## Unresolved

**`phase-arch-00` precedes `G40` in the track, which acceptance condition 3 did not anticipate.**
The condition was written before the owner directed, on 2026-09-14, that `sys-ui` be decomposed
first. `phase-arch-00` implements no P10 idea — it is lock-table work recorded as `000234`, outside
the accepted partition — so `phase-arch-01` remains the first *implementation* phase on the reading
the condition intends. A stricter reading of "first phase" would not hold. Recorded rather than
resolved, because the wording is the owner's to settle.

**The `R18` / `ADR-015` tension is carried, not settled.** `R18`'s management actions — killing a
process, freeing a port — are writes, and `ADR-015` fixed a read-only workbench API posture.
`phase-arch-12` carries resolving it in its own ADR rather than widening `ADR-015` in passing.

**`000233` and `000232` live in an uncommitted file.** Both were appended to `_data/ideas.jsonl` in
the primary checkout and were uncommitted at close, which is why they resolve through `fold()` there
and not in this worktree. `000234` and `000235`, written this session, are in the same uncommitted
file. This phase references all four by id and writes nothing to the idea log.
