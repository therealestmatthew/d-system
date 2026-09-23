---
schema_version: 1
id: doc-session-autonomous-operations-architecture
code: SESS-2026-09-22-08
title: Design the autonomous-operations architecture and rule what to build
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-broker-first-autonomous-operations, doc-autonomous-operations-architecture, doc-autonomous-agent-operations-requirements, doc-autonomous-agent-operations]
---

# Design the autonomous-operations architecture and rule what to build

## Phase

`phase-auto-01` — "Design the autonomous-operations architecture and rule what to build". Worked on
`agent/phase-auto-01` in `/code/d-system-worktrees/phase-auto-01`, base `b5cecfb`, per `PLAN-032`
(`doc-autonomous-agent-operations`) and `REQ-017` (`doc-autonomous-agent-operations-requirements`).
Deliverables were `docs/04-decisions/` and `docs/07-architecture/` only; `REQ-017`, `PLAN-032` and
`docs/09-backlog/backlog.yaml` were explicitly out of scope for edits.

## What was built

**`docs/04-decisions/ADR-022-broker-first-autonomous-operations.md`** (`ADR-022`) — records the
broker-first inversion as a decision with its reason, not a restated precedence note: the capability
and approval broker (`000031`) is built ahead of the trigger gateway (`000028`), the run ledger
(`000029`) and the supervised worker (`000030`), against the partition's stated `028 → 029 → 030`
ordering. Reasoning: a gate built after the things it gates has never gated anything, and the
2026-09-15 unattended run — the one real data point in this programme — shows a bounded, written
capability set was what actually made that run safe, not the gateway, ledger or worker, none of
which existed.

**`docs/07-architecture/ARCH-011-autonomous-operations-architecture.md`** (`ARCH-011`) — evaluates
each of the four components alone and rules build-now (broker) vs. defer (gateway, ledger, worker),
each deferral with reasoning attached rather than dropped silently. States the broker's shape and the
requirement-coverage consequence, and the R16 no-second-authority statement.

### Broker shape and build/defer ruling

**Broker shape: enforcement point with a permissive default, not full policy.** The design found it
was guessing at the capability taxonomy — the only real precedent for scoped enforcement in this
repository (the 2026-09-15 run) was situational, hand-written grants for that one run, not a set
drawn from multiple real requests, and with the gateway and ledger both deferred there is no second
source of requests to check a named taxonomy against. `phase-auto-02` is scoped to build the
tool-boundary enforcement mechanism, wire it into every agent action, default to denying nothing, and
audit every call — satisfying `REQ-017` `R01` (ordering) and `R03` (enforcement at the boundary).
`R02` (named, narrow capability sets) and `R04` (approval records) are recorded **open, not
claimed**, per `REQ-017`'s own qualification, in both ADR-022 and ARCH-011.

**Build/defer ruling:**

| Component | Ruling | Reason |
|---|---|---|
| `000031` broker | Build now, first | Only component with an unattended-safety argument independent of the other three; 2026-09-15 is real evidence it is load-bearing |
| `000028` gateway | Defer | Buildable and testable alone, but no current caller and no ledger to feed |
| `000029` ledger | Defer | Checkpoint/resume design is unanswerable against zero real interrupted, trigger-driven runs; primary consumer (gateway) also deferred |
| `000030` worker | Defer | Its own text already states it has no purpose without the gateway and ledger |

`phase-auto-02` through `phase-auto-05` were already `status: queued` in `docs/09-backlog/backlog.yaml`
before this phase ran, gated by `depends_on` on `phase-auto-01`; this phase makes no edit to that
file. They remain `queued`, not returned to it, and ARCH-011 is the reasoning a reader of the backlog
should be pointed to for why the three deferred components stay that way, though nothing in
`backlog.yaml` currently cites it.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 317 documents, 30 memories, 293 backlog phases
```

Exit code 0, run after every commit including this session record and the fix-cycle-2 correction.

## Acceptance

- **`REQ-017` `R01` holds on its design half** — Met. ADR-022's Context and Decision sections give
  the 2026-09-15 evidence and the "gate built after the things it gates" reasoning; it is a decision
  with its reason, not a precedence note.
- **`REQ-017` `R16` holds** — Met. Both ADR-022 ("Nothing here becomes a second authority over phase
  claims") and ARCH-011 ("Nothing here becomes a second authority over phase claims") name
  `docs/09-backlog/backlog.yaml` as the lock table and `uv run python -m src.governance` as the lock
  check, and state that no component proposed here replaces either.
- **Any deferred component is returned with reasoning attached** — Met. ARCH-011 gives each of
  `000028`, `000029` and `000030` its own non-circular reasoning, not a bare "deferred" label.
- **The ADR states explicitly which broker shape ships, and records `R02`/`R04` open if
  permissive-default** — Met, in ADR-022 directly (added in fix cycle 1; see below) as well as in
  ARCH-011.

## Fix cycles

**Fix cycle 1** (coordinator finding): the broker-shape ruling and the `R02`/`R04`-open statement
existed only in ARCH-011; acceptance condition 4 requires the ADR itself to state them. Fixed by
adding "The broker ships as an enforcement point with a permissive default" and "Nothing here becomes
a second authority over phase claims" subsections directly to `ADR-022`, stating the shape, the
reasoning, the `R02`/`R04`-open ruling and the `R16` statement in the ADR's own text.
`grep -n -e R02 -e R04 docs/04-decisions/ADR-022-broker-first-autonomous-operations.md` went from 0
matches to 3. Committed as `be65ef6`.

**Fix cycle 2** (adversarial review finding F2, confirmed): ARCH-011 stated `phase-auto-03` through
`phase-auto-05` "return to `queued` in `docs/09-backlog/backlog.yaml` with this document as their
reasoning" — false, since this phase never edited `backlog.yaml` and those phases were already
`queued` before it ran; none of their fields cite this document. Fixed by rewording to state plainly
that they were already `queued`, gated by `depends_on`, that this phase made no edit to that file,
and that this document is the reasoning a reader should be pointed to even though nothing currently
cites it. Fixed in this session's commit.

Adversarial review (`docs/… /_working/build-batch-002/phase-auto-01-adversary.md`, not a repository
deliverable) raised two findings against the range `b5cecfb..be65ef6`:

- **F2 — LOW — CONFIRMED.** The false backlog-return claim above. Fixed in this fix cycle.
- **F1 — MEDIUM — CONFIRMED, not fixed here.** `PLAN-032`'s requirement-coverage table
  (`docs/01-plans/PLAN-032-autonomous-agent-operations.md:199-202`) still maps `R02` and `R04` to
  `phase-auto-02` unconditionally, which now contradicts ADR-022/ARCH-011's open-not-claimed ruling.
  `PLAN-032` is not a deliverable of this phase and was explicitly out of scope for this fix cycle
  (the coordinator directed it go to the owner, not to this session). Left unfixed; see Unresolved.

## Unresolved

Two documents outside this phase's declared deliverables now read as stale against ADR-022/ARCH-011's
ruling, and neither was edited here:

- **`REQ-017`** still reads as if `R02` and `R04` are to be met unconditionally; it does not yet
  record them as open. `docs/06-requirements/REQ-017-autonomous-agent-operations.md` is not a
  deliverable of this phase.
- **`PLAN-032`'s requirement-coverage table** (lines ~199-202) still maps `R02` and `R04` to
  `phase-auto-02` unconditionally (adversarial finding F1). `PLAN-032` is not a deliverable of this
  phase either.

Both await the owner's decision on whether and how to update them; this phase states the fact rather
than making either edit, per its declared deliverables (`docs/04-decisions/` and
`docs/07-architecture/` only).

## Backlog

This session makes no edit to `docs/09-backlog/backlog.yaml`. The completion decision and any
downstream backlog changes (to `phase-auto-02` through `phase-auto-06`, or elsewhere) are the
coordinator's or owner's to make.
