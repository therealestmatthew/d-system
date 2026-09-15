---
schema_version: 1
id: doc-session-decompose-sys-ui-lock
code: SESS-2026-09-14-11
title: Decompose sys-ui so frontend phases stop serializing on one lock
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-governance
- sys-backlog
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-architecture-quality-requirements
---

# Decompose sys-ui so frontend phases stop serializing on one lock

## Phase

`phase-arch-00` — Decompose `sys-ui` so frontend phases stop serializing on one lock, from the
workbench architecture and quality plan (`PLAN-028`, programme `P10`). Claimed by `agent-arch`,
worked on `agent/phase-arch-00` in `../d-system-worktrees/phase-arch-00`. Recorded as idea
`000234`.

## The measurement, first and last

The phase's `next_action` requires the ceiling to be measured before a view is formed, and again
against the change. Both runs use `src.governance.backlog.collisions()` over the `phase-arch-*`
set, walking the dependency waves and taking the largest pairwise-disjoint subset of each wave —
the number of agents that could actually hold claims at once, not the number of phases that are
merely unblocked.

**Among the seventeen idea-derived phases** (`phase-arch-01` … `-17`, the set `PLAN-028` measures):

| Wave | Ready | Ceiling before | Ceiling after |
|---|---|---|---|
| 1 | `01`, `11`, `14`, `16` | 2 | **3** — `01`+`11`+`16` |
| 2 | `02`, `03`, `05`, `12`, `15` | 2 | 2 |
| 3 | `04`, `06` | 1 | 1 |
| 4 | `07` | 1 | 1 |
| 5 | `08`, `09`, `10` | 1 | 1 |
| 6 | `13`, `17` | 1 | 1 |
| **Across the set** | | **2** | **3** |

Counting all nineteen with `phase-arch-00` complete, `phase-arch-18` joins wave 1 and the ceiling
goes from 3 to **4** — above the backlog's own `max_active` of 3, so the lock table stops being the
binding constraint there and the policy cap becomes it.

The wave-1 gain is `phase-arch-16`, the terminal persistence audit: it declared `sys-demo-stage`
and the whole of `docs/00-working/`, which collided it with `phase-arch-11` and `-14` on the
staging directory alone. It now declares `sys-wb-terminal` alongside `sys-demo-stage` and a named
audit file, and collides with neither.

**Waves 2 through 6 did not move, and that is the honest result rather than a failure to try.**
What remains is not an artifact of the coarse id:

- `phase-arch-02`'s identifier migration rewrites class names, registry ids and layout data across
  every panel. It declares all seven new ids because it genuinely touches all seven.
- `phase-arch-03` and `-04` are audits of every file under `ts/src` and `src`. An audit is
  invalidated by a concurrent change to what it audits, so it declares what it reads — the owner's
  ruling this session. That is what keeps them apart from each other and from `phase-arch-02`.
- Waves 4, 5 and 6 are `G43`'s own chain. `phase-arch-07`, `-08`, `-09`, `-13` and `-17` all
  change the layout engine itself. One engine, one lock, correctly.

The one residual artifact worth naming: `phase-arch-01` (vocabulary) and `phase-arch-14`
(performance measurement) still collide, on `sys-wb-layout`. Neither writes engine code — one
writes a concept memory, the other writes numbers — but `collisions()` has no read-versus-write
distinction, so two readers of the same system serialize. Narrowing further would not fix it;
only a declaration that distinguishes reading from writing would.

## The seven new system ids

Every id names paths that exist in the tree today, which the governance check enforces directly:
`__main__.py` errors with `missing path` on any registry path that does not resolve.

| Id | Seam it names | Paths |
|---|---|---|
| `sys-wb-layout` | The layout and slot engine, and the geometry data it reads | `ts/src/workbench`, `ts/src/stage/StagePage.tsx`, `_data/workbench/layouts` |
| `sys-wb-styles` | The single stylesheet every slot and panel renders against | `ts/src/stage/StagePage.css` |
| `sys-wb-shared` | Cross-panel primitives — popover, tooltip, the panel bridge | `Popover.tsx`, `Tooltip.tsx`, `panelBridge.ts` |
| `sys-wb-terminal` | The shell panel and the controls that drive it | `TerminalRegion.tsx`, `TerminalMenu.tsx`, `InjectionDropdowns.tsx`, `CommandPanel.tsx`, `_data/workbench/injection-overrides.json` |
| `sys-wb-notes` | The notes strip and its rotator | `NotesStripRegion.tsx` |
| `sys-wb-explorers` | The table-and-tree panels over repository state | `explorer/`, `IdeaExplorerRegion.tsx`, `BacklogExplorerRegion.tsx`, `FileBrowserRegion.tsx`, `FileTreeContextMenu.tsx`, `DirectoryPickerDialog.tsx` |
| `sys-wb-viewer` | The panels that render generated HTML | `HtmlViewerRegion.tsx`, `OverviewRegion.tsx` |

Two of these are not panels and were added deliberately. `sys-wb-styles` is one file, and it is
registered alone because two different kinds of work act on it — the identifier migration renames
its classes, the content-fit contracts assert against them — and folding it into the engine would
have made every CSS-touching phase collide with every engine phase for nothing but an import.
`sys-wb-shared` exists because `panelBridge` is the one place panels reach across slots, which is
exactly where a finer lock table would otherwise stop seeing a real conflict.

`sys-ui` is untouched as an id and stays declared everywhere it already is, including on documents
and on the thirteen complete phases. Retiring it is `phase-arch-18`.

## Deliverable paths narrowed

- `docs/00-working/` — one named file per audit: `workbench-duplication-audit.md` (`03`),
  `workbench-structure-audit.md` (`04`), `ports-and-processes-lifecycle.md` (`11`),
  `workbench-performance-baseline.md` (`14`), `terminal-persistence-audit.md` (`16`).
- `test/` — one named module per phase: `test_workbench_fit_contracts.py` (`05`),
  `test_ports_api.py` (`12`), `test_workbench_cache.py` (`15`),
  `test_workbench_maximize.py` (`17`).
- `ts/src/stage/` — the specific panel or stylesheet each phase edits, plus `ts/src/workbench/`
  where the engine is the target (`07`, `08`, `09`, `13`, `17`). `phase-arch-02` keeps the broad
  path, because a repository-wide rename genuinely reaches all of it.

Both the audit filenames and the test module names are predictions of files that do not exist yet.
They narrow the lock, and a phase that lands on a different name should correct its own
declaration rather than treat the guess as binding.

## The counter-consideration

A finer lock table admits conflicts the coarse one was accidentally preventing. Two phases that
both touch the workbench but declare different narrow ids may now run at once and genuinely
interfere — through `StagePage.css` class names, through `panelBridge`'s module-level
registrations, or through a panel whose behavior a second phase is asserting against.
`sys-wb-styles` and `sys-wb-shared` exist to make the two most likely of those declarable rather
than invisible. They do not close the gap: the validator still cannot see an edit that strays
outside a phase's declarations, as `sys-backlog`'s own description says. That boundary is enforced
by diff review, and this change moves more weight onto it.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 224 documents, 24 memories, 180 backlog phases
```

`uv run pytest`

```
580 passed, 2 warnings in 53.95s
```

Acceptance condition 4 was checked mechanically rather than by reading the diff — parsing both
revisions of `backlog.yaml` and comparing item by item:

```
changed phases: phase-arch-01 … phase-arch-17
outside phase-arch-*: []
active or complete among them: []
top-level keys changed: []
```

## Found wrong in the source material

- **`PLAN-028`'s *Execution order and real concurrency* table and its `R29` coverage row are now
  stale.** They state the pre-split numbers — ceiling 2, and `phase-arch-00` raising wave 1 to 3
  "and nothing further". After this change wave 1 is 3 among the seventeen and 4 across all
  nineteen. The plan was not corrected here: it sits under `docs/01-plans/`, outside this phase's
  declared deliverables, and the owner ruled on 2026-09-14 to leave it and report it. It is
  `phase-arch-18`'s natural companion work.
- **`REQ-011` `R29`'s verification asks for three confirmations, and one of them cannot hold in
  this phase**: "confirm the coarse `sys-ui` id is retired rather than left as a third alias."
  `phase-arch-00` is explicitly scoped not to retire it. The row's two halves are split across
  `phase-arch-00` and `phase-arch-18` by `PLAN-028`'s coverage table, but `R29`'s own verification
  text does not say so, so the row read alone fails against this phase. `REQ-011` was not edited —
  it sits under `docs/06-requirements/`, outside this phase's deliverables.
- **A peer merged `phase-prog-02` into `dev` between this session's preflight and its claim**,
  taking the backlog from 170 to 180 phases and releasing `sys-ui`. The claim was re-validated
  against the merged state. The ten new phases are `phase-wbf-*`; the `phase-arch-*` set is
  unchanged at nineteen.
