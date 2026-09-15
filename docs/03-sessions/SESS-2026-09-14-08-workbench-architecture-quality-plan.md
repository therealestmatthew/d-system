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
3. **G40 is the first implementation phase, and P11's dependency on it is stated — Met.**
   `phase-arch-01` is `G40`, and nothing precedes it: it declares `depends_on: []`, and
   `phase-arch-00` — the only lower-numbered phase — also declares `depends_on: []` and does not
   collide with it, so the two can be claimed simultaneously. The numbering orders them for reading,
   not for execution, and nothing gates `G40`. `PLAN-028`'s *What P11 depends on* section states the
   edge: any `P11` phase that renames a slot, panel, region or layout identifier declares
   `depends_on: [phase-arch-01]`, specifically rather than `phase-arch-02`.
4. **phase-prog-03 is removed from next_up in the same change that completes it — Met.** The
   `--ready` output above shows the queue line without it, and the removal is in commit `b1a2e8a`,
   the same commit that replaced the placeholder and added the phases.

## Backlog

`status: active`, `agent: agent-prog`.

`next_action`: All four acceptance conditions verified met at close. Awaiting the owner's
`/session-close` review; nothing remains to build.

Evidence recorded: `docs/01-plans/PLAN-028-workbench-architecture-quality.md`,
`docs/06-requirements/REQ-011-workbench-architecture-quality.md`, `docs/09-backlog/backlog.yaml`,
`docs/09-backlog/README.md`.

## Unresolved

**The `R18` / `ADR-015` tension is carried, not settled.** `R18`'s management actions — killing a
process, freeing a port — are writes, and `ADR-015` fixed a read-only workbench API posture.
`phase-arch-12` carries resolving it in its own ADR rather than widening `ADR-015` in passing.

**`000233` and `000232` live in an uncommitted file.** Both were appended to `_data/ideas.jsonl` in
the primary checkout and were uncommitted at close, which is why they resolve through `fold()` there
and not in this worktree. `000234` and `000235`, written this session, are in the same uncommitted
file. This phase references all four by id and writes nothing to the idea log.

## Review

Independent sub-agent review, run at close against `dev...agent/phase-prog-03` with no inherited
context. Its verdict and findings, as returned:

> All four acceptance conditions are **MET** in my independent judgement. Verification commands
> pass, the 29-row/18-phase coverage claim is exactly true, the partition correction is
> well-founded, the concurrency table reproduces cell for cell, and the backlog is schema-valid,
> acyclic and fully resolvable.

Condition by condition:

1. **MET.** "`grep -c "Placeholder. Not a finalized plan"` returns 0. The `dev` version carried the
   banner at lines 17–20; it is gone. … No discrepancy."
2. **MET.** "I parsed both files independently rather than trusting the record. … Every one of
   REQ-011's 29 rows appears in PLAN-028's coverage table, and all 18 `phase-arch-*` phases (00–17)
   carry at least one row. The record's claim is exactly right."
3. **MET, but not for the reason the session record gives.** "I do **not** accept the session
   record's argument as stated. … PLAN-028 files `phase-arch-00` under the heading
   `## Implementation phases` … and `phase-arch-00` carries a REQ-011 row (`R29`), so by the plan's
   own coverage table it implements a requirement. Calling it 'not an implementation phase' is
   therefore rationalising. But the condition still holds on a different and stronger ground the
   record did not use: **`phase-arch-00` does not precede `phase-arch-01` at all.** Both declare
   `depends_on: []`, and I confirmed they are collision-free."
4. **MET, with a bad citation in the record.** "Confirmed: `phase-prog-03` is absent from `next_up`,
   and the removal is in commit **`b1a2e8a`**. … The session record cites the wrong hash … That hash
   is not reachable from any branch."

Three findings it would not let pass silently, none overturning acceptance:

> 1. **`PLAN-028:198, 211, 216` — the concurrency measurement excludes `phase-arch-00` while
>    claiming to cover the "whole `phase-arch-*` set".** With `-00` included the wave-1 ceiling is
>    **3**, not 2, so the stated ceiling and the coordinator guidance are both wrong. … This is the
>    plan's own "measured rather than assumed" claim failing on the phase that was added to fix the
>    very problem.
> 2. **PLAN-028 contradicts itself on which phase is first** (`:157` vs `:161` vs `:215`).
> 3. **`SESS…:85` cites commit `435027c`** for the `next_up` removal; that object is unreachable
>    from any branch. The real commit is `b1a2e8a`.

It also flagged, on files changed outside declared `deliverables`: "The substance is fine — every
one of these is mandated by the phase's own scope or acceptance. The process point is that
`AGENTS.md:261–263` says to *update the phase's declarations on `dev`* when work needs a file
outside them … the wider lock was never visible to peers."

All three numbered findings were fixed before this phase was marked complete; the deliverables
finding is answered under `## Decisions`.

## Decisions

**The vocabulary ships as a `brain/concepts/` memory, not a new governed document.** The generator
and its drift test already exist and the workbench was simply absent from them. A second glossary
would have been the hand-maintained duplicate `GOV-001` forbids, and nothing would have checked it.

**`G40`'s gate and its migration were split.** Six ideas wait on knowing what a slot is called; none
wait on the layout JSON having been rewritten. Fusing them would have made one rename phase the
bottleneck for the whole programme.

**`G43` supersedes `ADR-016` rather than amending it** — the owner's choice at orientation, offered
against amending in place or deferring. Three of `ADR-016`'s four decisions move, and a superseding
record keeps the demo-week reasoning readable.

**Panel maximize (`000233`) was ruled into `P10`'s `G43`, against the owner's framing of it as an
HTML Viewer feature.** The mechanism is slot geometry, not a viewer capability; built inside
`HtmlViewerRegion` it would be a second geometry path outside the model `G43` exists to unify. The
cost is stated rather than hidden: `phase-arch-17` sits at the end of the longest chain, which is
the slowest route to the demoability the idea asks for. The owner may overrule it with information;
`PLAN-028` says so explicitly.

**`phase-arch-00` was added on the owner's direction, overriding the recommendation offered.** Asked
how to handle a concurrency ceiling of 2, the recommendation was to respect the locks and run two;
the owner chose to decompose `sys-ui` first instead. That is the better call and the measurement
now shows why: it lifts wave 1 to three concurrent phases, which is `max_active`.

**`backlog.yaml` was deliberately not added to `deliverables`, and the reviewer's process finding is
answered rather than accepted.** `deliverables` feeds only `collisions()`, so declaring
`backlog.yaml` would make this phase conflict with every future claim — every claim edits that file.
`docs/09-backlog/README.md` was added, because it is a real surface with no such property.

## Corrections

**The concurrency measurement was wrong in the document that boasted of being measured.** The table
claimed to cover the "whole `phase-arch-*` set" while omitting `phase-arch-00`, which was added in
the same commit. The true wave-1 ceiling is 3, not 2, and `max_active` is reachable. Found by the
independent review, not by the session that wrote it. Fixed in `PLAN-028`, and the Track B
coordinator prompt built on the wrong number needed a successor.

**Acceptance condition 3 was first argued on bad ground.** The record claimed `phase-arch-00` "is
not an implementation phase", which the plan's own `## Implementation phases` heading and `R29`
coverage row both contradict. The condition holds for a better reason — `-00` and `-01` are
concurrent and unordered — and the record now says that instead.

**A commit hash cited in the record was unreachable.** `435027c` was a pre-rebase object; the real
commit is `b1a2e8a`.

**Two governance failures mid-session, fixed rather than retried**: a `depends_on` cycle between
`REQ-011` and `PLAN-028`, and `phase-arch-11` carrying one acceptance condition where the schema
requires two.

**`REQ-011` rows were twice inserted out of numeric order** and moved into place before commit.

## Left undone

**Nothing in this phase's scope.** All four acceptance conditions hold on independent review.

**The `R18` / `ADR-015` tension is carried deliberately.** Killing a process is a write, and
`ADR-015` fixed a read-only workbench API posture. `phase-arch-12` resolves it in its own ADR rather
than this plan widening `ADR-015` in passing.

**`P11`'s finalize phase (`phase-prog-02`) was not started.** It was blocked throughout by this
phase — both declare `docs/06-requirements/`, and `--ready` showed the conflict as predicted. It is
claimable once this integrates. Its input is ready: `_tmpagent/viewer-render-location-ruling.md` is
`activated`.

**Four ideas sit in an uncommitted `_data/ideas.jsonl`** in the primary checkout — `000232`,
`000233` (the owner's) and `000234`, `000235` (written this session). The owner directed that the
file be held. Committing it releases all four together.
