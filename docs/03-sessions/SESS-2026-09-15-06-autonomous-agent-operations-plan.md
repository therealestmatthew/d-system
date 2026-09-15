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
Governance OK: 27 systems, 237 documents, 25 memories, 228 backlog phases
```

Exit 0. Documents 235 → 237: `REQ-017`, and this record. Phases 222 → 228 for the six
`phase-auto-*` phases. An earlier run during the session reported `236 documents`, correctly — this
record did not exist yet. The final figure is the one recorded here.

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

`phase-prog-07` is `status: complete`, `agent: agent-night`,
`session: doc-session-autonomous-agent-operations-plan`. Completion evidence is `PLAN-032`,
`REQ-017`, `docs/09-backlog/README.md` and this record. Written under the owner's advance authority
for this batch, after the read-only independent review below confirmed all four conditions.

Six phases added under `phase-auto-*`, all `status: queued`, none claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-07`. Its own runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 237 documents, 25 memories, 228 backlog phases
EXIT=0

$ uv run pytest -q
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** "`status: draft` → `active`;
four numbered design decisions plus an 'evidence problem' section replace the old banner."

**Condition 2 — requirement exists, every row maps to a phase — Met.** "Checked coverage directly
against `backlog.yaml`, not PLAN-032's own table: all 16 IDs appear in the `phase-auto-01..06`
acceptance text, and every phase's acceptance cites at least one row."

**Condition 3 — the `000031` gate is a precondition for anything unsupervised — Met, and verified two
ways, not just in prose.** The reviewer went further than the data shape and found the enforcement:

> "Mechanical enforcement, not just data shape: `src/governance/backlog.py:134-136` — `if
> item["status"] == "active"/"complete" and items[dependency]["status"] != "complete":
> errors.append("prerequisite ... is not complete")`. … The ordering is a real, checked gate, not a
> note that a later builder could satisfy by prose alone."

That is a stronger result than this phase claimed. The plan argued the ordering makes the gate real;
the reviewer established that the governance check actively refuses to let `phase-auto-03`, `-04` or
`-05` reach `active` or `complete` while the broker is not complete.

**Condition 4 — removed from `next_up` in the same change — Met**, verified by `git show`.

**The `000020` ruling was checked against the source, not the claim.** "Confirmed real, not
re-decided… `docs/00-working/idea-batching-partition.md` line 458, 'Owner rulings, 2026-09-13,' row:
`Kept, sequenced behind 000128 | 000020 | Build the light _tmpagent/ mechanism first; revisit only if
it proves insufficient.` PLAN-032 and REQ-017 restate this without contradiction." It also confirmed
`phase-agx-07` exists and the dependency is real rather than fabricated.

**The self-citation was corroborated independently**, which this phase could not do for itself. The
reviewer checked whether citing this run as evidence was self-serving and found the owner's own
authority grant committed before the batch ran:

> "`docs/00-working/overnight-run-prompt-2026-09-15.md` (committed on `dev` at `c4e0e759`, **authored
> by the owner**, before the batch ran, not part of this diff) records the exact authority grant and
> guardrails PLAN-032 cites… This is real, independently-dated corroboration — not the same agent
> inventing its own evidence after the fact. … I judge this legitimate, appropriately caveated
> evidence, not a self-serving overclaim."

**`backlog.yaml` integrity.** "Exactly 6 new items, **zero** pre-existing items changed, no YAML
anchors/aliases introduced. `next_up` differs only by the removal of `phase-prog-07`."

**Two minor findings, both already addressed.**

- *R08's "eleven fields" overstates fidelity to `000029`'s text* — the idea names ten
  comma-separated items, and eleven is reachable only by splitting "the model/tool versions used" in
  two. The reviewer is right, and this was **already corrected in commit `c74360b`**, which landed
  after the snapshot it reviewed: both documents now cite the idea's list without imposing a count.
  Independently reaching the same conclusion from the idea body is corroboration of the fix.
- *The session record's pasted governance output was stale* — `236 documents` against 237, because
  this record was not yet in the catalog when the command ran. **Fixed**, with the reason stated.

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
