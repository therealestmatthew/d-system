---
schema_version: 1
id: doc-workbench-architecture-quality
code: PLAN-028
title: Workbench architecture and quality (P10)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench-architecture-quality-requirements, doc-workbench-requirements, doc-workbench-layout-decision, doc-workbench-api-decision]
---

# Workbench architecture and quality (P10)

## Summary

Programme `P10` of the twelve, **second in the owner's delivery order**. Audits and architecture of
the workbench itself, as against `P11`'s discrete features — the same product, a different kind of
work.

It was moved ahead of `P11` on 2026-09-14, on the owner's ruling. `G40`'s container-versus-content
vocabulary is cited as a prerequisite by six ideas, so planning any work that renames things before
settling the names would have meant naming them twice.

**13 ideas across 8 fine groups**, from the accepted partition of 2026-09-13, **plus `000233`**
(panel maximize), raised on 2026-09-14 and ruled into `G43` below. This plan turns them into **17
phases** under the `phase-arch-*` prefix, plus `phase-arch-00`, which is owner-directed enabling work
rather than an idea of the partition's — **18 in total**, governed by
[REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md).

| Group | Ideas | What it covers | Phases |
|---|---|---|---|
| `G40` Vocabulary | `000124` | Settles container-vs-content naming before more work names things wrong | `phase-arch-01`, `phase-arch-02` |
| `G41` Duplication and structure audits | `000115`, `000116` | Two-way cross-reference: an abstraction extracted in one is often the refactor proposed in the other | `phase-arch-03`, `phase-arch-04` |
| `G42` Content-fit methodology | `000134` | Per-panel visibility contracts and mechanised checks | `phase-arch-05` |
| `G43` Slot/panel architecture | `000133`, `000135`, `000141`, `000233` | `000141` generalises `000135` structurally and would prevent the double-header defect by construction; `000133` revisits geometry on the same model, and `000233`'s maximize is that same geometry in a second state | `phase-arch-06` … `phase-arch-09`, `phase-arch-17` |
| `G44` Sub-app packaging | `000144` | How a sub-app plugs into a slot | `phase-arch-10`, `phase-arch-13` |
| `G45` Ports/process app | `000142`, `000143` | Explore the lifecycle, then build the tool — raised together against the same port-conflict incidents | `phase-arch-11`, `phase-arch-12` |
| `G46` Performance and cache invalidation | `000114`, `000121` | `000121` sharpens `000114`'s invalidation requirement with a dated failure: a stale overview page during demo prep | `phase-arch-14`, `phase-arch-15` |
| `G47` Terminal persistence audit | `000113` | Session survival and latency across all three shells | `phase-arch-16` |

### Correction: the six prerequisite ideas are all in P10

The placeholder that preceded this plan asserted that `G40` is cited as a prerequisite by six ideas,
"four of them in `P11`". **That is wrong, and this plan withdraws it.** The six are `000115`,
`000116`, `000133`, `000135`, `000141` and `000144`. By the partition's own `P10` table they sit in
`G41`, `G43` and `G44` — all `P10`. The `P11` table (`G48`–`G56`) contains none of them.

What `P11` actually carries is the partition's weaker statement that it "should follow `G40` where
naming is involved" — a general sequencing note across the programme, not four named ideas. The
ordering is unaffected: `P10` runs before `P11` because the owner ruled so on 2026-09-14, and
because `R01`'s vocabulary is a live input to `P11`'s renaming work either way. But the reason the
placeholder stated was not the reason its own evidence supported, and a plan that keeps asserting it
teaches the next reader something false.

## The chosen design

Five decisions shape the eighteen phases. Four were open in the placeholder; the fifth rules on an
idea raised after it.

`phase-arch-00` sits outside all five. It is not an idea from the partition and belongs to no group:
the owner directed on 2026-09-14 that `sys-ui` be decomposed before the rest of the track runs,
because `sys-ui` is declared by 14 of the 17 and the validator treats a shared system as a collision,
so the track would otherwise execute almost entirely serially. Measured rather than assumed — see
*Execution order* below. Recorded as `000234`.

### 1. The vocabulary ships as concept memories, not as a new document

`brain/concepts/` already holds the project's term definitions, `tools/generate_glossary.py` renders
them into `docs/08-governance/GLOSSARY.md`, and a test fails on any drift between the two. The
workbench is simply absent from that machinery: none of the eight existing concept memories define
*slot*, *panel*, *region*, *layout*, *assignment* or *visible panel*.

`G40` therefore adds `brain/concepts/terms-workbench-ui.md` and regenerates the glossary. It does
**not** create a governed glossary document of its own. A second glossary would be the
hand-maintained duplicate `GOV-001` forbids, and it would be unverified — the existing path is the
only one with a drift test behind it.

### 2. The vocabulary gate and the identifier migration are separate phases

`000124` raises two things: settling the names, and deciding where existing identifiers get renamed
versus aliased. Six ideas are waiting on the first. None are waiting on the second — what they need
is to know what a slot is called, not for `_data/workbench/layouts/*.json` to have been rewritten.

So `phase-arch-01` delivers the settled vocabulary plus the *ruling* on each identifier class, and
is the gate. `phase-arch-02` executes the migration and gates nothing. Fusing them would make one
rename phase — touching layout data, CSS class names, `REQ-007` row wording, localStorage keys, the
panel registry and test fixtures — the bottleneck for the entire programme.

### 3. `G43` supersedes `ADR-016` rather than amending it

`ADR-016` fixed layout persistence for demo week: repository-owned layout JSON, browser-stored
selections, no geometry editing in the UI. `G43` moves three of its four decisions — slots gain a
configuration schema with sub-slots (`000141`), panel identity stops being singleton by `panel_id`
(`000135`), and geometry becomes reconfigurable (`000133`).

That is a replacement, not an amendment. `phase-arch-06` writes a new ADR carrying
`supersedes: [doc-workbench-layout-decision]` and marks `ADR-016` `superseded` in the same change,
following `ADR-013`/`ADR-014`'s precedent. `ADR-016` stays readable as the record of what demo week
chose and why, which an in-place rewrite would destroy.

The new ADR keeps `ADR-016`'s two load-bearing choices — layouts are repository data, the browser
stores selections only — and states that it keeps them, so the superseding is legible as a change to
the structural model rather than to the persistence posture.

### 4. `G44`'s two halves are sequenced apart, around `G45`

`000144` is one idea with two halves: the general sub-app packaging contract, and packaging the
port/process app specifically. The general half needs `G40` and `G43`; the concrete half needs the
app `G45` builds to exist. They cannot be one phase without one half waiting on the other's inputs.

`phase-arch-10` writes the contract after `G43`'s model lands. `phase-arch-11` and `phase-arch-12`
run `G45` independently of both. `phase-arch-13` packages the app through the contract, and is the
proof the contract works on something real rather than only on paper.

### 5. Panel maximize (`000233`) belongs to `P10`'s `G43`, not `P11`'s `G48`

**The ruling: `P10` owns it.** `000233` joins `G43` and gets `phase-arch-17`. `P11` does not carry
it, and `PLAN-027` should not add it.

The owner asked for maximize on the HTML Viewer, for reading a generated page from the back of a
room. Read as a feature request that is `G48` work. Read as a mechanism it is not, and the mechanism
is what decides the boundary between these two programmes: `P11` is discrete features on one panel,
`P10` is the model all panels share.

Maximize is geometry. It changes which region of the viewport a panel occupies and then restores it
— the same thing `000133` revisits and the same model `000141` restructures. Built inside
`HtmlViewerRegion` it would be a second geometry path sitting outside the slot model, which is
precisely the divergence `G43` exists to remove, and it would be rebuilt the first time a shell or an
explorer wanted the same behavior. `REQ-011` `R25` makes that observable rather than merely intended:
a maximize implemented inside any single panel fails the row.

Three constraints ride with it, all already specified and verified elsewhere, and all carried into
`R25`–`R28`:

- **Zero scroll and the fill assertions hold in both states.** `REQ-006` R02 and `REQ-007` W15, at
  1280x720, 1366x768, 1920x1080 and 1024x768, in both layouts, maximized and collapsed.
- **Maximize is transient view state, not a `W16` re-assignment.** Collapsing restores the panel to
  its assigned slot, and maximize is never written into the `ADR-016` selections store — a browser
  left maximized would otherwise reopen wrong.
- **A maximized shell keeps its PTY session.** `W16` already obliges live sessions to survive
  re-assignment where feasible; a remount that kills the PTY is a regression, not a new gap.

**The cost of this ruling, stated plainly.** `phase-arch-17` depends on `phase-arch-07` and
`phase-arch-09`, so it sits at the end of the programme's longest chain —
`01` → `06` → `07` → `09` → `17`. The idea's stated motivation is demoability, and this ruling is the
slowest route to it. The faster route exists and is rejected here on purpose: a viewer-only maximize
would ship in one `P11` phase and be thrown away when `G43` lands. If the demo need is urgent enough
to buy a throwaway, that is the owner's call to make against this trade-off, not a reason to file the
work under the programme that would ship it sooner.

## Implementation phases

Eighteen phases under `phase-arch-*`, registered in
[the backlog index](../09-backlog/README.md). `phase-arch-01` is first and has no prerequisites.

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-arch-00` | Decompose `sys-ui` so frontend phases stop serializing on one lock | — | — |
| `phase-arch-01` | Settle the workbench vocabulary and rule on identifier migration | `G40` | — |
| `phase-arch-02` | Execute the workbench identifier migration | `G40` | `01` |
| `phase-arch-03` | Duplication audit across the workbench and API | `G41` | `01` |
| `phase-arch-04` | Code structure and file-size audit with target structures | `G41` | `01`, `03` |
| `phase-arch-05` | Per-panel content-fit contracts and their mechanised checks | `G42` | `01` |
| `phase-arch-06` | Decide the slot configuration-schema model, superseding ADR-016 | `G43` | `01`, `05` |
| `phase-arch-07` | Implement schema-owned slots and sub-slots with structural eligibility | `G43` | `06` |
| `phase-arch-08` | Multi-instance panel identity across layout, storage, registry and sessions | `G43` | `07` |
| `phase-arch-09` | Reconfigurable slot geometry with per-role content constraints | `G43` | `05`, `07` |
| `phase-arch-10` | Define the sub-app package contract | `G44` | `06`, `07` |
| `phase-arch-11` | Ports and system processes: lifecycle exploration | `G45` | — |
| `phase-arch-12` | Build the port and process management application | `G45` | `11` |
| `phase-arch-13` | Package the port/process app as a workbench sub-app | `G44` | `10`, `12` |
| `phase-arch-14` | Measure workbench performance before designing any cache | `G46` | — |
| `phase-arch-15` | Design and ship caching with mtime-keyed invalidation | `G46` | `14` |
| `phase-arch-16` | Terminal persistence and performance audit across three shells | `G47` | — |
| `phase-arch-17` | Panel maximize and collapse on the slot model | `G43` | `07`, `09` |

### Sizing against the partition

Partition-time sizing for `P10` was **12–15 phases**, against 13 ideas. This plan lands **17**
against 14, and the delta is three stated choices rather than scope growth:

- `000233` did not exist at partition time. It adds `phase-arch-17` under design decision 5.

- `G40` was sized at one phase because its deliverable is documentation. It is two here, because the
  migration is execution work and must not gate the six ideas waiting on the documentation (design
  decision 2).
- `G42` was sized at 1–2 and is one here: a content-fit contract with no mechanised assertion is a
  contract nothing checks, so `000134`'s two halves ship together.

`G41`, `G44`, `G45`, `G46` and `G47` each land inside their partition-time range. `G43` lands at five
against a 4–5 range, and the fifth is `000233`, which the range never covered.

## Execution order and real concurrency

Measured on 2026-09-14 by running `src.governance.backlog.collisions()` over the whole
`phase-arch-*` set, not read off the dependency graph. `depends_on` gives the waves; the lock table
decides how much of each wave can actually run at once.

| Wave | Ready together | Actually concurrent | What blocks the rest |
|---|---|---|---|
| 1 | `01`, `11`, `14`, `16` | **2** — `01`+`11`, or `01`+`16` | `01`/`14` share `sys-ui`; `11`, `14`, `16` all share the `docs/00-working/` deliverable |
| 2 | `02`, `03`, `05`, `12`, `15` | **2** — `02`+`12` only | `sys-ui` pairwise across `02`, `03`, `05`, `15`; `sys-api` across `03`, `12`, `15`; `test/` across `05`, `12`, `15` |
| 3 | `04`, `06` | **1** | share `sys-ui` |
| 4 | `07` | 1 | nothing ready beside it |
| 5 | `08`, `09`, `10` | **1** | all three share `sys-ui`; `08`/`09` also share `ts/src/stage/` and `_data/workbench/layouts/` |
| 6 | `13`, `17` | **1** | share `sys-ui` and `ts/src/stage/` |

**The ceiling is 2, not `max_active`'s 3, and it is 1 from wave 3 onward.** `sys-ui` is declared by
14 of the 17 idea-derived phases, and a shared system is a collision, so adding agents past two buys
nothing. The critical path is six deep: `01` → `05` → `06` → `07` → `09` → `17`.

This is what `phase-arch-00` exists to change, and why the owner directed it first. Until it lands,
a coordinator should claim the permitted pairs above and run everything else serially rather than
queue claims the validator will reject.

Two of the collisions are artifacts rather than real contention. `docs/00-working/` is a staging
directory, not a contended surface — three audit phases collide there only because each declares the
whole directory. `ts/src/stage/` is one path covering every panel. Both narrow naturally when
`phase-arch-00` splits the lock table.

## Requirement coverage

Every row of `REQ-011` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 Vocabulary in concept memories, rendered to the glossary | `phase-arch-01` |
| R02 Container-versus-content settled explicitly | `phase-arch-01` |
| R03 Slot ids name geometry or role, never an occupant | `phase-arch-01`, `phase-arch-02` |
| R04 Migration ruling per identifier class | `phase-arch-01` |
| R05 Migration leaves no broken stored state | `phase-arch-02` |
| R06 Duplication audit with references and a pay-for-itself judgment | `phase-arch-03` |
| R07 Structure audit with per-file measurement and target structures | `phase-arch-04` |
| R08 The two audits cross-reference each other | `phase-arch-03`, `phase-arch-04` |
| R09 Per-panel content-fit contracts, asserted mechanically | `phase-arch-05` |
| R10 A new panel inherits its contract by construction | `phase-arch-05` |
| R11 New ADR supersedes ADR-016 | `phase-arch-06` |
| R12 Structural panel eligibility replaces W16's lists | `phase-arch-07` |
| R13 A slot's top bar is rendered exactly once | `phase-arch-07` |
| R14 Multi-instance panel identity | `phase-arch-08` |
| R15 Reconfigurable geometry with per-role constraints | `phase-arch-09` |
| R16 Sub-app package contract | `phase-arch-10` |
| R17 Ports and processes exploration | `phase-arch-11` |
| R18 Port and process application | `phase-arch-12` |
| R19 The app integrates through the contract | `phase-arch-13` |
| R20 Performance measured before caching is designed | `phase-arch-14` |
| R21 Every cache carries an mtime-keyed invalidation story | `phase-arch-15` |
| R22 A regenerated overview is immediately visible | `phase-arch-15` |
| R23 Three-shell persistence matrix with intent judgments | `phase-arch-16` |
| R24 Latency measurements and named owner-machine checks | `phase-arch-16` |
| R25 Slot-level maximize and collapse, available to every panel | `phase-arch-17` |
| R26 Zero scroll and fill assertions hold maximized and collapsed | `phase-arch-17` |
| R27 Maximize is transient and never persisted | `phase-arch-17` |
| R28 A maximized shell keeps its PTY session | `phase-arch-17` |
| R29 The frontend lock table admits two independent phases | `phase-arch-00` |

## What P11 depends on

`P11` ([PLAN-027](PLAN-027-workbench-features-defects.md)) is the sibling programme on the same
product. One edge runs between them:

**Any `P11` phase that renames a slot, panel, region or layout identifier, or that writes new
requirement rows using those nouns, declares `depends_on: [phase-arch-01]`.** It is `phase-arch-01`
specifically — the settled vocabulary — not `phase-arch-02`, the migration. `P11` work that touches
no naming carries no edge and may run concurrently, subject to the usual system and deliverable
disjointness.

`P11`'s own finalize phase (`phase-prog-02`) sets those edges when it creates its phases. This plan
states the rule; it does not write into `PLAN-027`.

### Two ideas raised on 2026-09-14, split between the programmes

Both are anchored on `000119` and were raised after the partition was accepted. They are recorded
here together because they arrived together and look like one batch, and are not one batch.

- **`000233` (panel maximize) is `P10`'s.** Ruled into `G43` by design decision 5 above, and built
  as `phase-arch-17`. `PLAN-027` should not give it a phase. A `G48` phase that adds maximize to the
  HTML Viewer would duplicate `phase-arch-17` and create the second geometry path the ruling exists
  to prevent.
- **`000232` (the six already-served image formats) is `P11`'s**, and `P10` takes nothing from it.
  It is one `COMPATIBLE_EXTENSIONS` array in `ts/src/stage/HtmlViewerRegion.tsx`, needs no rendering
  step, and by the idea's own text does **not** inherit `000118`'s dependency on markdown rendering
  landing first. It is named here only so the `000233` ruling is not read as claiming its sibling
  too.

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P10`.
- **Requirements** — [REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md), this plan's governing requirement.
- **Workbench requirements** ([REQ-007](../06-requirements/REQ-007-workbench.md)) and the **workbench plan** ([PLAN-022](PLAN-022-workbench.md)) — what shipped.
- **Workbench layout persistence** ([ADR-016](../04-decisions/ADR-016-workbench-layout-persistence.md)) — the model `phase-arch-06` supersedes.
- **Workbench API surface** ([ADR-015](../04-decisions/ADR-015-workbench-api-surface.md)) — read-only, which `R18`'s management actions press against.
- **Glossary generation** ([OPS-004](../08-governance/OPS-004-generate-glossary.md)) — the mechanism `phase-arch-01` writes into.

## Known facts not to rediscover

- **`G40` gates `G43` and `G44`** by those ideas' own text, not by an inference drawn here.
- **`G46` measures before it changes anything** — `000114` is the measurement, `000121` the
  refinement, and they are not separable.
- **`G47` cannot be fully verified on Linux.** CMD and PowerShell checks need the owner's Windows
  machine, and `R24` requires the audit to name them rather than assert them.
- **`G45` is fully standalone** and was named a *candidate* first sub-app for `G44`, not a
  requirement of it. `phase-arch-13` uses it as the contract's first real consumer for that reason,
  not because `G44` depends on ports.
- **`G43` alone approaches a full architecture revision** — four phases here, and the only group
  whose phases were kept free of any other group's work.
