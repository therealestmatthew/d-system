---
schema_version: 1
id: doc-blocked-downstream-projections-requirements
code: REQ-019
title: Blocked downstream projections requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-projection, sys-portfolio]
depends_on: [doc-structure-content-boundary]
---

# Blocked downstream projections requirements

## Observed problem and scope

Four ideas, each needing infrastructure that does not exist, and one root fact behind most of them.

**The root fact is stale, and that is the first thing this requirement must say.** `000022` observes
that "`_data/people/` and `_data/commitments/` each contain only a `.gitkeep`" and that "33 populated
`_data/projects/*.json` files exist against zero commitments or people". That was true when written.
It is not true now, and not because the gap closed:

```
$ for d in projects people commitments tasks; do printf "%-14s %s\n" "$d" "$(ls _data/$d | wc -l)"; done
projects       5
people         1
commitments    1
tasks          3
```

`phase-priv-03` (complete) relocated the owner's real records to `_private/portfolio/` and seeded
`_data/` as a **fictional example set**, per [ADR-009](../04-decisions/ADR-009-structure-content-boundary.md).
So `_data/` now shows all four entities populated because it is a demo fixture, and the question
`000022` asks — whether the owner's actual portfolio has people and commitments — can no longer be
answered by looking there at all. It requires `D_SYSTEM_DATA_ROOT=_private/portfolio`, which is
gitignored, absent from any worktree, and which `AGENTS.md` forbids an agent to read unless the owner
directs it.

That is why this programme's first requirement is a question rather than a build.

The three remaining ideas are views over projections that do not exist yet: deterministic "as of"
snapshots and two-point diffs over ideas, plans and portfolio entities (`000033`); isolated what-if
scenarios over the derived portfolio projection, never writing to source (`000034`); and a record of
every recommendation with the owner's decision and the observed outcome, so calibration can be
measured (`000036`).

**All three were nominated for decline by the control analyst and kept by the owner.** The ruling of
2026-09-13: *"Kept, gate recorded — gated is not dead; R1's objection upheld against R4's
decline-until-evidence. Each now names what unblocks it."* This requirement carries that ruling and
names each gate.

This requirement covers the blocked downstream projections programme (`P7`). Its independence from
every other programme is total.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The portfolio data question is stated as a single question the owner can answer, with the exact command that produces the evidence. | Read the statement for one question and one runnable command. Confirm the command names `D_SYSTEM_DATA_ROOT=_private/portfolio`, because counting `_data/` answers a different question — that root is the fictional example set since `phase-priv-03`. |
| R02 | `000022`'s figures are corrected on the record, and the reason they went stale is stated. | Compare the idea's cited counts against `_data/` today and against what `ADR-009` moved. Confirm the correction says the relocation changed what the root means, not that the gap closed. |
| R03 | The answer, once given, routes to one of two stated outcomes: tooling friction, or no current need. | Read the statement for what follows from each answer. An answer with no consequence recorded leaves the question open in a new form. |
| R04 | Each of `000033`, `000034` and `000036` carries an explicit gate naming what unblocks it, rather than a decline. | Read each phase's `resume_when`. Confirm none is declined — the owner ruled all three kept on 2026-09-13, and a plan that declines them contradicts a recorded ruling. |
| R05 | `000033`'s gate is checked against the repository rather than assumed, and the phase's status reflects what is found. | Confirm whether `phase-idea-07` is complete and `fold()` exists. `000033` names that fold as its prerequisite; if it has shipped, the idea is no longer dormant and must not be filed as though it were. |
| R06 | Deterministic "as of" snapshots and two-point diffs are answerable over ideas and plans, showing which fact changed, when it became known, and which source event supports it. | Request a snapshot at a past date and a diff between two dates. Confirm each changed fact names its supporting event. Confirm two runs over unchanged history produce identical output. |
| R07 | Scenario simulation never writes to source JSON, the live database, or the idea log. | Run a scenario and confirm all three are byte-identical afterwards. This is `000034`'s own constraint and the property that makes what-if safe. |
| R08 | Every recommendation is persisted with its supporting evidence, the owner's actual decision, and the later observed outcome. | Read one record for all three. Confirm the decision field distinguishes accept, defer, dismiss and revise rather than collapsing them, since the calibration question is which advice created false urgency. |

## What each requirement is not

**R01 is not a build.** The partition sizes `G31` at "under one phase to resolve" and calls it "a
question for the owner more than a build". The deliverable is a question and a command, not a
mechanism.

**R02 is not a criticism of `000022`.** The idea was accurate when written. `ADR-009` moved the ground
under it. The correction exists so the next reader does not measure the example set and conclude the
gap closed.

**R04 does not reopen the decline debate.** The owner ruled. The requirement's job is to ensure each
gate is named, which is what the ruling asked for.

**R06, R07 and R08 describe work that is gated.** They are written now so the gates have something
specific to release, not because the work is ready to start.
