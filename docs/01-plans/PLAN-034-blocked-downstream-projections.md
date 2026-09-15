---
schema_version: 1
id: doc-blocked-downstream-projections
code: PLAN-034
title: Blocked downstream projections (P7)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-projection, sys-portfolio]
depends_on: [doc-blocked-downstream-projections-requirements, doc-structure-content-boundary]
---

# Blocked downstream projections (P7)

## Summary

Programme `P7` of the twelve, and the smallest. Four ideas across two fine groups, each needing
infrastructure that does not exist, with one root fact behind most of it. Its independence from every
other programme is total.

| Group | Ideas | What it covers |
|---|---|---|
| `G31` Portfolio data gap | `000022` | Do two of four core entities hold zero records because of tooling friction, or because there is no current need? |
| `G32` Temporal, scenario and calibration | `000033`, `000034`, `000036` | Three views over projections that do not yet exist |

The partition sizes `G31` at under one phase and `G32` as **dormant**, noting the programme is "not
yet sizeable". This plan lands **four phases**, two of which are created `deferred` — which is the
backlog's own mechanism for dormant work with a named gate, and is what the owner's ruling asked for.

## `G31` cannot be resolved by an agent, and the acceptance anticipates that

The phase's scope says to resolve `G31` *with the owner*, "measured against the correct data root".
Its acceptance offers two branches: `G31` is resolved, **or the plan states exactly what the owner
must answer**. The second branch applies, and the reason is structural rather than a shortfall of
effort.

**`000022`'s figures are stale, and the staleness is the interesting part.** The idea observes that
`_data/people/` and `_data/commitments/` "each contain only a `.gitkeep`", against "33 populated
`_data/projects/*.json` files". Today:

```
$ for d in projects people commitments tasks; do printf "%-14s %s\n" "$d" "$(ls _data/$d | wc -l)"; done
projects       5
people         1
commitments    1
tasks          3
```

All four are populated and the project count fell from 33 to 5. Neither movement means the gap closed.
`phase-priv-03` (`status: complete`) relocated the owner's real records to `_private/portfolio/` and
seeded `_data/` as a **fictional example set**, per `ADR-009`. So `_data/` now shows four populated
entities because it is a demo fixture, and `000022`'s question has become unanswerable at the location
it was asked about.

**The correct root is `_private/portfolio/`, and this run cannot read it.** It is gitignored, so it is
absent from every worktree — confirmed here — and `AGENTS.md` states plainly: "Never read or write
there unless the owner directs you to." The run prompt does not direct it. Counting files there would
be a read of the owner's real client engagements, personal finances and health records, which is not a
boundary to cross for a phase-sizing question.

So `phase-proj-01`'s deliverable is the question and the command that answers it, stated exactly:

```bash
D_SYSTEM_DATA_ROOT=_private/portfolio uv run python tools/rebuild_db.py
# then, per entity:
for d in projects people commitments tasks; do printf "%-14s %s\n" "$d" "$(ls _private/portfolio/$d 2>/dev/null | wc -l)"; done
```

**The question for the owner:** *do `people` and `commitments` hold records in your real portfolio?*
And if not — is that tooling friction (capture is too slow, the schema does not fit how you think
about people, entry has no surface) or no current need (projects are what you actually track, and the
other two entities were built ahead of demand)?

`R03` requires the answer to route to a stated consequence, because an answer with no consequence
recorded leaves the question open in a new form. If it is friction, the work is capture ergonomics and
belongs with `P1`'s session-less capture thinking. If it is no current need, `CLAUDE.md`'s statement
of purpose — "tracking people, projects, commitments, and tasks" — describes an aspiration rather than
a use, and that is worth knowing before anything downstream is built on the assumption.

## The chosen design

### 1. `G32`'s decline nomination was already ruled on, and the ruling is kept

The phase's scope asks for a ruling on the control analyst's nomination to decline all three of
`G32`. **The owner ruled on 2026-09-13**, and the partition records it:

> **Kept, gate recorded** | `000030`, `000033`, `000034`, `000036` | Gated is not dead — R1's objection
> upheld against R4's decline-until-evidence. Each now names what unblocks it.

The partition also records that R1 declined to nominate these three at all, calling them "genuinely
gated on prerequisites, not dead."

So this plan does not re-run the decision. It does the thing the ruling asked for: **each of the three
carries an explicit gate naming what unblocks it**, expressed as a `resume_when` on a `deferred`
phase rather than as prose. `R04` makes that checkable, and makes a plan that declines them a
contradiction of a recorded ruling rather than a judgement call.

### 2. `000033` is not dormant — its gate is already met

The partition lists `000033` as needing `phase-idea-07`'s fold, and files the whole of `G32` as
dormant. **Checked, and the gate has been met for some time:**

```
phase-idea-07 | complete | Add event identity and the amendment fold
src/db/ideas.py:230:def fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
```

`phase-idea-07` is `status: complete` and `fold()` ships — this plan's own reading of the idea corpus
went through it. So `000033` is sizeable now, and `phase-proj-02` is created `queued` rather than
`deferred`.

This is the second programme tonight where a gate turned out to be met or reachable while the phases
behind it waited. `R05` exists so the next reader checks rather than inherits.

### 3. `000034` and `000036` stay deferred, with gates that name real prerequisites

`000034` needs the portfolio projection and signals to exist, and needs `G31` answered — a what-if
simulator over a portfolio with no people or commitments would simulate the example set. Its
`resume_when` names both.

`000036` needs recommendations and outcomes to accumulate before calibration has anything to measure.
Even R4's decline nomination described it as "the most downstream idea in the corpus", and that is
accurate; it is the gate, not a reason to discard it.

Neither is given a speculative size. `R07` and `R08` are written now so the gates have something
specific to release rather than a topic.

### Which of these need a decision record

**None.** `G32`'s disposition is the owner's existing ruling, already recorded in the partition;
duplicating it into an ADR would create a second place for it to drift. `G31`'s outcome may deserve
one once the owner answers — if the answer is "no current need", that reshapes what the system claims
to be for — and `phase-proj-01`'s scope says so conditionally.

## Implementation phases

Four phases under `phase-proj-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Status at creation | Gate |
|---|---|---|---|---|
| `phase-proj-01` | Answer the portfolio data question against the real root | `G31` | `queued` | — |
| `phase-proj-02` | Deterministic as-of snapshots and two-point diffs | `G32` | `queued` | gate already met |
| `phase-proj-03` | Portfolio scenario simulation that never writes to source | `G32` | `deferred` | `G31` answered, and portfolio signals exist |
| `phase-proj-04` | Recommendation calibration against observed outcomes | `G32` | `deferred` | recommendations and outcomes accumulate |

### Sizing against the partition

`G31` was sized at "<1 phase to resolve" and lands at one, which is the smallest unit available.
`G32` was filed **dormant** and lands at three — one claimable now and two `deferred`. The departure
is decision 2: the partition's dormancy assessment was correct for two of the three and stale for
`000033`.

## Execution order and real concurrency

`phase-proj-01` and `phase-proj-02` are independent of each other and of everything else in the
repository — this programme's total independence is the partition's assessment and it holds. Both can
run beside any peer in any other programme.

`phase-proj-03` depends on `phase-proj-01`'s answer, and on portfolio signals that belong to
`PLAN-002`'s `phase-sig-*` line rather than to this programme.

There is no critical path worth naming: the deepest chain is two.

## Requirement coverage

Every row of `REQ-019` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 The question and the exact command | `phase-proj-01` |
| R02 `000022`'s figures corrected, with the reason | `phase-proj-01` |
| R03 The answer routes to a stated consequence | `phase-proj-01` |
| R04 Each `G32` idea carries a gate, not a decline | `phase-proj-02`, `phase-proj-03`, `phase-proj-04` |
| R05 `000033`'s gate checked against the repository | `phase-proj-02` |
| R06 As-of snapshots and diffs with supporting events | `phase-proj-02` |
| R07 Scenario simulation never writes to source | `phase-proj-03` |
| R08 Recommendations persisted with decision and outcome | `phase-proj-04` |

## Key references

- **The requirement** — [REQ-019](../06-requirements/REQ-019-blocked-downstream-projections.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P7`, its decline tiers, and the owner-rulings table carrying the `G32` decision.
- **The structure/content boundary** ([ADR-009](../04-decisions/ADR-009-structure-content-boundary.md)) — why `_data/` no longer answers `000022`'s question.
- **`AGENTS.md`** — the standing rule that `_private/` is never read without the owner's direction, which is why `G31` takes the acceptance's second branch.

## Known facts not to rediscover

- **`000022`'s counts are stale and the gap may not have closed.** `_data/` is the fictional example
  set since `phase-priv-03`; its populated entities prove nothing about the real portfolio.
- **The correct root is `_private/portfolio/`**, reached with `D_SYSTEM_DATA_ROOT`. It is gitignored,
  absent from every worktree, and off-limits to an agent without the owner's direction.
- **`G32` was ruled kept on 2026-09-13**, against a decline nomination, with gates to be recorded. Do
  not re-open it.
- **`000033`'s gate is met.** `phase-idea-07` is complete and `fold()` ships. The partition's dormancy
  filing is stale for this one idea.
- **R1 declined to nominate all three of `G32`** — "genuinely gated on prerequisites, not dead" — which
  is the objection the owner upheld.
- **`phase-proj-03` depends on work outside this programme**, in `PLAN-002`'s signals line. Its gate
  names it so nobody claims the phase expecting it to be self-contained.
