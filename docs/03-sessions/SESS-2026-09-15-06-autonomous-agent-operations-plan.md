---
schema_version: 1
id: doc-session-autonomous-agent-operations-plan
code: SESS-2026-09-15-06
title: Finalize the autonomous agent operations plan (P5)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-autonomous-agent-operations]
---

# Finalize the autonomous agent operations plan (P5)

## Phase

`phase-prog-07` — Finalize the autonomous agent operations plan (P5).

Fifth phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 236 documents, 25 memories, 228 backlog phases
```

Exit 0. Documents 235 → 236 for `REQ-017`; phases 222 → 228 for the six `phase-auto-*` phases.

`uv run python -m src.governance --ready`

```
| phase-auto-01 | Design the autonomous-operations architecture and rule what to build | — | 2 | ready | — | phase-prog-07 |
```

One of six is `ready`, which is correct and is the programme's shape: `phase-auto-01` blocks
everything except the `000020` revisit, and that revisit waits on `phase-agx-07` in `P4`.

`uv run pytest`

```
580 passed, 2 warnings
```

## Acceptance

- **`PLAN-032` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, four numbered design decisions plus an explicit section on the
  programme's evidence base.
- **A requirement document exists for P5 and every row maps to at least one phase.** Met. `REQ-017`
  carries sixteen rows; the mapping is total in both directions, checked against the backlog entries.
- **The `000031` gate is stated as a precondition for anything running unsupervised.** Met, and
  stated as an ordering rather than a note — see `## Decisions`. `R01` is the only row in `REQ-017`
  that describes a sequence rather than a component, and `phase-auto-02` is built ahead of the
  gateway, ledger and worker rather than beside them.
- **`phase-prog-07` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-07` is `status: active`, `agent: agent-night`, pending the independent review below.

Six phases added under `phase-auto-*`, all `status: queued`, none claimed.

## Decisions

**The broker is built first, inverting the partition's stated ordering.** The partition sequences
`000028` → `000029` → `000030` "with `031` required before anything runs unsupervised". Read as a
precedence note, that is satisfiable by building the other three and adding the broker before
switching anything on — and the window between "the worker drains queued runs" and "the broker denies
capabilities" is exactly when an unattended run happens with nothing authorising it. A gate built
after the things it gates has never gated anything.

This is the phase's third acceptance condition, and stating the gate in prose would have satisfied
its letter. `R01` makes the ordering itself the observable instead. The cost is accepted and written
down: the broker is the least immediately useful of the four, and will look like over-engineering
until the rest exists. That is the correct shape for a safety gate.

**`000020` was not re-decided, because the owner already ruled on it.** The scope asks for a ruling
and the control analyst nominated decline. The owner's ruling of 2026-09-13 is in the partition's own
owner-rulings table: *kept, sequenced behind `000128` — build the light `_tmpagent/` mechanism first,
revisit only if it proves insufficient.* So `phase-auto-06` is a revisit phase with a precondition
rather than a build phase, `R15` requires the revisit to name actual cases where the light mechanism
fell short, and concluding "still not needed" satisfies it fully.

**`R16` guards against `000020` arriving by drift rather than by decision.** Its MCP server would
become a second authority over documents, claims and worktrees, replacing `backlog.yaml` as the lock
table and the governance validator as the lock check. Both work today. Two authorities that can
disagree is the failure mode worth asserting against rather than trusting nobody to build.

**The design phase is allowed to recommend building less.** `phase-auto-01` may conclude that
`000028`, `000029` or `000030` should not be built yet. The partition decomposed these five
"deliberately… so each could be evaluated alone", and evaluating each alone is work nobody has done.
`000030`'s own body says it is "a scheduling daemon with nothing to schedule" until the other two
exist. A design phase that cannot act on that is a design phase in name.

**`000028` and `000029` were made siblings rather than a chain.** The partition sequences one behind
the other; neither actually depends on the other. The gateway normalises events, the ledger persists
runs, and each is testable alone. Only `000030` needs both, which its own body states. This is the
programme's only genuine concurrency.

## Corrections

None this phase.

## Unresolved

**Whether this programme should be planned at all yet.** Four of its five ideas came from a research
pass rather than from an incident, and the partition itself calls it the most speculative. Options:
finalize it as instructed, or recommend parking the plan until something actually needs it.
**Finalized it**, because the run prompt names it among the ten and a placeholder left in place blocks
nothing but also resolves nothing. The honesty was handled differently instead: `PLAN-032` carries an
explicit section, *The evidence problem, stated plainly*, rather than reading like the eleven plans
that do have incident evidence behind them.

**Whether tonight's own run is admissible evidence.** This unattended run executed programme-finalize
phases with no chat session driving each step and used none of this infrastructure — no gateway, no
ledger, no worker, no broker. What bounded it was written advance authority and an agent choosing to
comply, which is exactly the enforcement `000031` calls insufficient. Options: leave it out as
self-referential, or record it. **Recorded it**, in the plan and here, because it is the only real
data point the programme has and it points at which component matters most. A reader should weigh
that it was written by the agent that ran it.

**Whether `phase-auto-02` can be built without knowing what tool boundary it enforces at.** `R03`
requires enforcement at the tool boundary, and what that boundary is depends on the harness — the
same uncertainty `phase-agx-01` faces for truncation signals. **Proceeded by sizing the phase**, and
`phase-auto-01`'s design is where the boundary gets established. Flagged here because if the harness
exposes no enforcement point, `R03` is unbuildable and the programme's central safety claim is
unbuildable with it.

## Left undone

**All six phases.** This phase finalizes a plan and builds nothing.

**The `000031` gate is stated, not enforced.** Nothing tonight prevented an unattended run from
proceeding without a broker, including this one. The plan sequences the broker first so that the next
autonomous capability built here is gated; it does not retroactively gate what has already run.

**`phase-auto-06` waits on `phase-agx-07` in `P4`** — the third cross-programme dependency this batch
has produced, after `phase-dgov-02`'s and `phase-agx-10`'s ordering constraint. They are accumulating
faster than the partition anticipated, because finalizing programmes sequentially keeps discovering
that one programme's phase is another's prerequisite.
