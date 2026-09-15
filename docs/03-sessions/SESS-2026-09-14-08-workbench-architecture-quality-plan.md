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

Phase `phase-prog-03`, claimed by `agent-prog` on branch `agent/phase-prog-03`, worked in
`../d-system-worktrees/phase-prog-03`.

## Queue position

`phase-prog-03` was taken out of `next_up` order on the owner's explicit ruling of 2026-09-14,
jumping `phase-part-02`, `phase-prog-01`, `phase-port-02` and `phase-ses-01`. This was the owner's
instruction, not a read of the queue, and `next_up` was not reordered to make the jump look routine.

## What was produced

- **[REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md)** — 24 observable rows
  with verification methods, covering the vocabulary, the identifier migration, the two audits, the
  content-fit contracts, the slot configuration-schema model, sub-app packaging, the ports/process
  app, performance and cache invalidation, and the terminal persistence audit.
- **[PLAN-028](../01-plans/PLAN-028-workbench-architecture-quality.md)** — placeholder banner
  removed, four design decisions stated, 16 implementation phases, a requirement-coverage table and
  the stated `P11` dependency edge.
- **17 phases under `phase-arch-*`**, registered in [the backlog index](../09-backlog/README.md).
- **`phase-prog-03` removed from `next_up`** in the same change.

## The five design decisions

1. **The vocabulary ships as a `brain/concepts/` memory, not a new document.**
   `tools/generate_glossary.py` already renders `brain/concepts/` into
   `docs/08-governance/GLOSSARY.md`, with a drift test behind it. None of the eight existing concept
   memories define *slot*, *panel*, *region*, *layout*, *assignment* or *visible panel* — the
   workbench is simply absent from machinery that already exists. A second glossary document would
   be the hand-maintained duplicate `GOV-001` forbids, and nothing would check it.
2. **The vocabulary gate and the identifier migration are separate phases.** Six ideas wait on
   knowing what a slot is called; none wait on `_data/workbench/layouts/*.json` having been
   rewritten. `phase-arch-01` is the gate and `phase-arch-02` gates nothing.
3. **`G43` supersedes `ADR-016` rather than amending it** (the owner chose this at orientation).
   Three of `ADR-016`'s four decisions move; a superseding ADR keeps `ADR-016` readable as the
   demo-week record it is.
4. **`G44`'s two halves are sequenced apart, around `G45`.** The general contract needs `G40` and
   `G43`; the concrete packaging needs `G45`'s app to exist. `phase-arch-13` is the proof the
   contract works on something real.
5. **Panel maximize (`000233`) belongs to `P10`'s `G43`, not `P11`'s `G48`** — ruled mid-session
   after the owner raised the idea. See below.

## The 000233 ruling: P10 owns panel maximize

`000233` was raised on 2026-09-14, after this phase's brief was written, and read with the idea
system's `fold()`. The owner asked for maximize on the HTML Viewer, motivated by reading a generated
page from the back of a room on a projector.

**Ruled into `P10`'s `G43`, as `phase-arch-17`.** `P11` does not carry it and `PLAN-027` must not add
it. The reasoning is the boundary between the two programmes: `P11` is discrete features on one
panel, `P10` is the model all panels share, and maximize is geometry — the same geometry `000133`
revisits and `000141` restructures. Built inside `HtmlViewerRegion` it would be a second geometry
path outside the slot model, rebuilt the first time a shell or an explorer wanted it. `REQ-011` `R25`
makes that observable: a maximize implemented inside any single panel fails the row.

The three constraints recorded on the idea are carried into `R26`–`R28` rather than restated as
prose — zero scroll and the W15 fill assertions in both states at all four sizes, maximize as
transient state never written to the `ADR-016` store, and PTY survival across maximize and collapse.

**The cost is stated in the plan rather than hidden.** `phase-arch-17` depends on `07` and `09`, so
it sits at the end of the longest chain, `01` → `06` → `07` → `09` → `17`. The idea's motivation is
demoability and this is the slowest route to it. The faster route — a viewer-only maximize in one
`P11` phase — is rejected on purpose, because `G43` would throw it away. That trade-off is the
owner's to overrule with information; it is not a reason to file the work under whichever programme
would ship it sooner.

**`000232` is not affected.** Its sibling — the six already-served image formats in the HTML Viewer
— is `P11`/`G48` work, needs nothing from `P10`, and by its own text does not inherit `000118`'s
dependency on markdown rendering. `PLAN-028` names it only so the `000233` ruling is not read as
claiming its sibling too.

**Where the ideas live.** `000233` and `000232` were appended to `_data/ideas.jsonl` in the primary
checkout and were uncommitted at the time of this session, which is why they resolve through
`fold()` there and not in this worktree. This phase references them by id and writes nothing to the
idea log.

## The defect in PLAN-028, resolved

PLAN-028's Summary asserted that `G40` is cited as a prerequisite by six ideas, "four of them in
`P11`". Its own "Known facts" section enumerated those six as `000115`, `000116`, `000133`,
`000135`, `000141` and `000144`.

Checked against `docs/00-working/idea-batching-partition.md`: the `P10` table places all six in
`G41`, `G43` and `G44`. The `P11` table (`G48`–`G56`) contains **none** of them. The enumeration is
correct and the Summary's "four of them in `P11`" is wrong; the finalized plan says so and withdraws
it.

This mattered beyond bookkeeping, because that claim was the stated justification for running `P10`
ahead of `P11`. The ordering stands — it is the owner's 2026-09-14 ruling, and `R01`'s vocabulary is
a live input to `P11`'s renaming work regardless — but the plan no longer asserts a reason its own
evidence contradicts.

## Ground truth confirmed against the repository

- `_data/workbench/layouts/layout-1.json` and `layout-2.json` both declare
  `"slot_id": "terminal"` — the owner's example in `000124`, confirmed in the data rather than
  taken on report.
- `brain/concepts/` holds eight memories, none of them workbench terms; `docs/08-governance/
  GLOSSARY.md` is generated from them and asserted by a drift test.
- `ADR-015` is `ADR-015-workbench-api-surface.md` (`doc-workbench-api-decision`), and its read-only
  posture is what `R18`'s kill-a-process actions press against — recorded as a boundary rather than
  resolved here.

## Sizing

Partition-time sizing for `P10` was 12–15 phases; this plan lands 16. The delta is two stated
choices, not scope growth: `G40` splits into a gating glossary and a non-gating migration, and
`G42`'s contract ships together with its mechanised assertion because a contract nothing checks is
not a contract. Every other group lands inside its partition-time range.

## Verification

```
$ uv run python -m src.governance
Governance OK: 20 systems, 220 documents, 24 memories, 166 backlog phases
EXIT=0
```

```
$ uv run python -m src.governance --ready
...
| phase-arch-01 | Settle the workbench vocabulary and rule on identifier migration | — | 1 | ready | — | — |
| phase-arch-11 | Ports and system processes: lifecycle exploration | — | 2 | ready | — | — |
| phase-arch-14 | Measure workbench performance before designing any cache | — | 2 | ready | — | — |
| phase-arch-16 | Terminal persistence and performance audit across three shells | — | 2 | ready | — | phase-prog-03 |
```

The four dependency-free phases show `ready`; the other twelve show `waiting` on their declared
prerequisites, which is the intended shape.

```
$ uv run pytest
580 passed, 2 warnings in 40.58s
```

Two governance failures occurred during the work and were fixed rather than retried:

- `ERROR documents depends_on: dependency cycle at doc-workbench-architecture-quality` — REQ-011 had
  declared the plan as a dependency while the plan declared REQ-011. The requirement now depends on
  `doc-workbench-api-decision` instead.
- `ERROR backlog:items.160.acceptance: [...] is too short` — `phase-arch-11` carried one acceptance
  condition where the schema requires two.

## Observations for the owner

**`phase-prog-02` is correctly blocked.** `--ready` now shows its Conflicts column as
`phase-prog-03`, because both declare `docs/06-requirements/` as a deliverable. That is the
validator doing its job; `P11` is claimed only after this phase completes and integrates.

**`phase-prog-03`'s `deliverables` list does not name `docs/09-backlog/backlog.yaml` or
`docs/09-backlog/README.md`, and should not.** Its scope requires editing both, so the declaration
looks incomplete. It was left alone deliberately: `deliverables` feeds only
`collisions()` in `src/governance/backlog.py`, so declaring `backlog.yaml` would make this phase
conflict with every future claim — every claim edits that file. The gap is a naming artifact of what
the field is for, not a missing lock.

**One unresolved tension is recorded, not settled.** `R18`'s management actions — killing a process,
freeing a port — are writes, and `ADR-015` fixed a read-only workbench API. `phase-arch-12` carries
resolving that in its own ADR rather than widening `ADR-015` in passing.

## Not done here

Marking `phase-prog-03` complete. That is `/session-close`'s, and only the owner invokes it.
