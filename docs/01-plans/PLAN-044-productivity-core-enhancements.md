---
schema_version: 1
id: doc-productivity-core-enhancements
code: PLAN-044
title: Productivity core enhancements — the path to the weekly review and the specification route for new entity work
kind: plan
status: draft
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-portfolio, sys-projection, sys-capture, sys-signals, sys-synthesis, sys-api]
depends_on: [doc-mini-systems, doc-reliability-follow-up, doc-capture-build, doc-schema-decision-reconciliation, doc-backlog-decisions]
---

# Productivity core enhancements

The system exists to track people, projects, commitments and tasks. On 2026-09-23 the real data
root held projects and nothing else, and no phase that uses the data was in `next_up`
(`_working/session-manager/reports/productivity-system-inventory.md`, idea `000022`). This plan
does three things:

1. **Orders existing phases** so the first output the owner would use, the weekly review
   (`phase-syn-03`), is reachable next, with portfolio seeding (`phase-cap-08`) first.
2. **Adds two build phases** for defects in the data path: the dropped `repository` field
   (`000345`) and the private tag file the owner ruled on (`000343`).
3. **Adds specification phases** for the new entity work the owner asked for (`000360` to
   `000365`). Each follows the `phase-prog-*` pattern: it writes the requirement and the plan,
   settles the design questions with the owner, and adds session-sized build phases. None of them
   builds anything itself.

Every ordering and shape decision below is an owner ruling of 2026-09-23, relayed by the Session
Manager and recorded in [GOV-003](../08-governance/GOV-003-backlog-decisions.md).

## Waves

**Wave 1** is the path to the weekly review plus the work that makes its data trustworthy. It is
composed as `batch-007` and placed in `next_up` directly after `phase-cap-08`.

| Group | Phases | Why it is here |
|---|---|---|
| Seeding | `phase-cap-08` | Real commitments and tasks; `phase-sig-03` and `phase-sig-06` depend on it |
| Reliability | `phase-rel-03` to `phase-rel-07` | `phase-rel-06` gates `phase-sig-01`; `phase-rel-07` gates the API specification |
| Signals | `phase-sig-01` to `phase-sig-08` | Everything the weekly review reads |
| Synthesis | `phase-syn-01` to `phase-syn-03` | Context packs, the session briefing, the weekly review |
| Data defects | `phase-pc-01` (`000345`), `phase-pc-02` (`000343`) | A field the rebuild drops, and capture tags with nowhere to go |
| Backup | `phase-conc-07` | The real records are gitignored and have no backup (`000021`, `000058`) |
| Entity surface | `phase-pc-03` (`000360`) | Specification of API routes and UI views, after `phase-rel-07` |

`phase-sig-09`, `phase-syn-04`, `phase-syn-05` and `phase-rel-08` to `phase-rel-10` are not on the
path to the weekly review and keep their current place.

**Wave 2** is specification work that waits on wave-1 output. It is composed as `batch-008`.

| Phase | Idea | Waits on | Why |
|---|---|---|---|
| `phase-pc-04` | `000361` quick entry | `phase-cap-08` | Seeding shows whether capture friction is the real barrier |
| `phase-pc-05` | `000362` reminders | `phase-sig-03` | The Accountability Ledger is the data a reminder reads |
| `phase-pc-06` | `000363` external intake | `phase-cap-08` | Owner-written capture is proved on real material first |
| `phase-pc-07` to `phase-pc-09` | `000365` with `000364`, `000255` to `000267` | nothing | Closes `ARCH-010`'s open gates, then writes the requirement and plan |

## Design decisions

**Quick entry writes into staging (`000361`).** `ADR-007` makes staging the write boundary: agents
write to staging and the owner promotes. A quick-entry writer is a faster front end to that
boundary, not a bypass, so it needs no ADR. The option refused is a direct writer to the data root,
which would skip evidence scoring, routing and owner promotion, and which `ADR-008` relies on for
referenced identities.

**Capture tags live under the data root (`000343`).** A `tags.json` under `D_SYSTEM_DATA_ROOT`
holds tags promoted from a capture. `tools/rebuild_db.py` and source validation merge it with the
shared taxonomy in `_data/tags.json`, and promotion writes a new tag there instead of leaving it
held. When the data root is the tracked `_data/`, promotion keeps refusing, because writing there
would put a capture-derived tag into a tracked file. `src/capture/promote.py` already refuses to
write the tracked file; this phase adds the reader and the writer, not a leak fix.

**The organisational model starts with design, not build (`000365`).** `ARCH-010` records accepted
decisions and a table of open gates, and its own Delivery row puts requirements, a plan and phases
after those gates. The thirteen gates are split across three sessions by dependency: the identity
and party foundation first, the commercial and structural models second, and the registry,
projection integrity, vocabulary and the delivery documents last. The opportunity entity (`000364`)
is decided inside the second pass, with the commercial lifecycle and relationships gates.
`000255` (master data management) and `000256` (its stewardship agent) stay parked, as `ARCH-010`
marks them.

**Seeding writes to the primary checkout's private root (`phase-cap-08`).** A relative
`D_SYSTEM_DATA_ROOT` resolves inside the worktree, where `_private/` does not exist, and promotion
would create a new root there that worktree removal deletes. The phase uses the absolute path
`/code/d-system/_private/portfolio` per command and copies `_capture/` back before the worktree is
removed. No code change.

**The HTML track waits on its audit.** `phase-html-01` to `phase-html-10` depend on `phase-des-01`,
which may retire some of them as superseded by the workbench. They are outside both waves.

## Traceability

| Idea | Disposition | Phase |
|---|---|---|
| `000022` | Addressed by seeding real records | `phase-cap-08` |
| `000345` | Build | `phase-pc-01` |
| `000343` | Build, on the owner's ruling | `phase-pc-02` |
| `000021`, `000058` | Existing phase, now in wave 1 | `phase-conc-07` |
| `000360` | Specification | `phase-pc-03` |
| `000361` | Specification | `phase-pc-04` |
| `000362` | Specification | `phase-pc-05` |
| `000363` | Specification | `phase-pc-06` |
| `000365`, `000364`, `000257` to `000267` | Design, then specification | `phase-pc-07` to `phase-pc-09` |
| `000255`, `000256` | Parked by `ARCH-010` | none |
| `000366` | Idea-graph work, added to an existing phase's scope | `phase-idg-04` |
| `000367` | Idea-graph work, a decision added to an existing phase's scope | `phase-idg-01` |

Links proposed by the triage findings
(`_working/session-manager/reports/triage-findings-000357-000367.md`). These are proposals for the
owner only; none is written to the idea log by this plan.

| From | Relation | To |
|---|---|---|
| `000360` | relates_to | `000361` |
| `000361` | relates_to | `000179` |
| `000362` | relates_to | `000028`, `000030` |
| `000363` | relates_to | `000179` |
| `000364` | relates_to | `000262`, `000365` |
| `000365` | relates_to | `000255`, `000364` |
| `000366` | extends | `000018` |
| `000366` | relates_to | `000343` |
| `000367` | relates_to | `000053`, `000085` |

## Build batches

`batch-007` (wave 1) and `batch-008` (wave 2) are in `docs/09-backlog/batches/`. Wave 1 is also in
`next_up`, so the Builders take its phases by assignment while the Batch Runner works through
`batch-003` to `batch-006`. `PROMPT-036` skips a phase that is already complete or claimed, so the
two routes do not build the same phase twice. [PROMPT-039](../02-prompts/PROMPT-039-productivity-core-builder-prompts.md)
carries the prompts for the two kinds of phase in this plan that need more than `/session-start`:
seeding, and the specification phases.
