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
`000234`. The branch was merged fast-forward into `dev` on the owner's approval before this record
was closed, so the work described below is on `dev` and the worktree is removed.

## Verification

Both commands run in the primary checkout at close, against `dev` with this session's work merged.

`uv run python -m src.governance`

```
Governance OK: 27 systems, 225 documents, 24 memories, 181 backlog phases
```

`uv run pytest`

```
FAILED test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output
1 failed, 579 passed, 2 warnings
```

**That failure is real, is on `dev`, and is not this session's.** It passed throughout the session
— `580 passed` on the branch, before the rebase and after it — and appeared only at close, when a
peer committed ideas `000235` and `000237` to `_data/ideas.jsonl` without regenerating
`docs/00-working/ideas.md` from it:

```
E  AssertionError: docs/00-working/ideas.md is generated. Regenerate it with
   tools/generate_ideas_md.py; do not edit it by hand.
E  assert '# Parked ide... → `000129`\n' == '# Parked ide... → `000235`\n'
```

Neither file is in this session's diff, which touches exactly four files
(`git diff --name-only 43ed511..1b139b9`). Deselecting that one test gives `579 passed, 1
deselected`. It was left for the peer whose session owns it rather than regenerated here: they are
active in the primary checkout right now, and a generated file appearing in this session's commit
would land in the middle of their diff. The fix is one command,
`uv run python tools/generate_ideas_md.py`.

The phase's acceptance also names a measurement rather than a command. Run at close over
`docs/09-backlog/backlog.yaml` on `dev`, walking the dependency waves of the `phase-arch-*` set and
taking each wave's largest pairwise-disjoint subset under `src.governance.backlog.collisions()`:

```
Wave 1: ready=4 ceiling=3  e.g. phase-arch-01, phase-arch-11, phase-arch-16
Wave 2: ready=5 ceiling=2  e.g. phase-arch-02, phase-arch-12
Wave 3: ready=2 ceiling=1  e.g. phase-arch-04
Wave 4: ready=1 ceiling=1  e.g. phase-arch-07
Wave 5: ready=3 ceiling=1  e.g. phase-arch-08
Wave 6: ready=2 ceiling=1  e.g. phase-arch-13
Ceiling across the set: 3
```

That run excludes `phase-arch-00` and `phase-arch-18` — the seventeen idea-derived phases
`PLAN-028` measures. Counting all nineteen with `phase-arch-00` treated as complete, the ceiling is
**4**. Before this session's change the same two runs gave **2** and **3**.

Acceptance condition 4 was checked mechanically rather than by reading the diff, by parsing both
revisions of `backlog.yaml` and comparing item by item:

```
changed phases: phase-arch-01 … phase-arch-17
outside phase-arch-*: []
active or complete among them: []
top-level keys changed: []
```

## Acceptance

- **`REQ-011` R29's first half holds — the ceiling rises above 2.** Met. 2 → 3 among the seventeen,
  3 → 4 across all nineteen, from the `collisions()` runs in `## Verification`.
- **Every new system id names a surface that exists in the tree today.** Met. The governance check
  emits `missing path` for any registry path that does not resolve; it passed with 27 systems, and
  each of the seven ids lists only files and directories present under `ts/src` and `_data/`.
- **The governance check exits 0 with the new ids registered and the queued phases redeclared.**
  Met. `Governance OK: 27 systems, …` at close. The condition names the governance check, which
  passes; the one failing test in the suite is a peer's stale generated file, described in
  `## Verification`, and touches no file this session changed.
- **No phase outside `phase-arch-*` is modified, and no active or complete phase is modified.** Met.
  The item-by-item comparison above shows exactly seventeen changed phases, all `phase-arch-*`, none
  of them `active` or `complete`, and no top-level backlog key touched.

## Backlog

`phase-arch-00` is `status: complete`, `agent: agent-arch`, `session: doc-session-decompose-sys-ui-lock`.
Completion evidence is `docs/08-governance/systems.yaml` and `docs/09-backlog/backlog.yaml`. The
`result` records the measured 2 → 3 rise among the seventeen and the 3 → 4 rise across all nineteen,
and that waves 2 through 6 did not move. The phase was not in `next_up`, so nothing was pruned.

## Unresolved

- `phase-arch-01` and `phase-arch-14` still collide on `sys-wb-layout` although neither writes engine
  code. Fixing it would need `collisions()` to distinguish reading from writing, which is in no
  phase's scope today.
- `PLAN-028`'s concurrency table and `REQ-011` R29's verification text are both stale or
  self-contradictory against this change. Both are described under *Found wrong in the source
  material* below and neither was edited, by the owner's ruling.
- `dev` is red on `test_ideas.py::test_the_committed_markdown_matches_regenerated_output` because a
  peer committed two ideas without regenerating `docs/00-working/ideas.md`. Not this session's, and
  left for the session that owns it.

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
| `sys-wb-shared` | Cross-panel primitives — popover, tooltip, the directory picker, the panel bridge | `Popover.tsx`, `Tooltip.tsx`, `DirectoryPickerDialog.tsx`, `panelBridge.ts` |
| `sys-wb-terminal` | The shell panel and the controls that drive it | `TerminalRegion.tsx`, `TerminalMenu.tsx`, `InjectionDropdowns.tsx`, `CommandPanel.tsx`, `_data/workbench/injection-overrides.json` |
| `sys-wb-notes` | The notes strip and its rotator | `NotesStripRegion.tsx` |
| `sys-wb-explorers` | The table-and-tree panels over repository state | `explorer/`, `IdeaExplorerRegion.tsx`, `BacklogExplorerRegion.tsx`, `FileBrowserRegion.tsx`, `FileTreeContextMenu.tsx` |
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
  where the engine is the target (`07`, `08`, `09`, `17`). Two phases keep the broad path.
  `phase-arch-02` keeps it because a repository-wide rename genuinely reaches all of it, and
  `phase-arch-13` keeps it alongside `ts/src/workbench/panelRegistry.tsx` because the sub-app it
  packages has no file in the tree yet, so there is no narrower path to name honestly.

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
  unchanged at nineteen. A further peer commit (`phase-wbf-11`, backfilled) landed during the
  session and was picked up by the rebase; the `phase-arch-*` set is still nineteen.

## Review

An independent sub-agent, given the phase's scope, acceptance and verification lists, the commit
range `43ed511..1b139b9` and nothing else, ran both verification commands and wrote its own
measurement script. Its findings, condition by condition:

- **Condition 1 — HOLDS.** "The record's claimed numbers — 2 → 3 among the seventeen, 3 → 4 across
  all nineteen — reproduce exactly under the wave-based definition, including the per-wave
  breakdown and the 'waves 2 through 6 did not move' claim."
  It added one caveat worth keeping: `collisions()` does **not** treat a dependency-chain
  relationship as a collision — that check lives separately in `concurrency_errors()`
  (`backlog.py:71-72`). Under a *global* definition of ceiling (the largest simultaneously
  achievable set anywhere in the programme, rather than within one wave) the pre-change figure
  among the seventeen was already 3, via `phase-arch-01` + `-12` + `-16`, so "rises above 2" was
  already true under that reading. It called this "a definitional nuance, not a defect", and noted
  the change is a real improvement under both definitions (global 3 → 4 among the seventeen, 4 → 5
  across all nineteen). The wave-based figure is the one this record reports, because it measures
  what is claimable at a single point in the queue.
- **Condition 2 — HOLDS.** All 22 declared paths resolve. On the harder half it read the import
  graph of every module under `ts/src/stage/` and `ts/src/workbench/` and found the seams real:
  the seven ids partition `ts/src/stage/` exactly, with no file in two ids and none omitted;
  `Popover` is imported by 7 modules across 4 other ids and `panelBridge` by 4 across 3;
  `StagePage.tsx` imports only `../workbench/*` and nothing in `ts/src/workbench/` imports a panel;
  `CommandPanel`, `InjectionDropdowns` and `TerminalMenu` are imported only by `TerminalRegion`.
- **Condition 3 — HOLDS.** `Governance OK: 27 systems, 225 documents, 24 memories, 181 backlog
  phases`, exit 0; `580 passed, 2 warnings`.
- **Condition 4 — HOLDS.** Its own item-by-item YAML comparison: exactly 17 changed phases, all
  `phase-arch-*`, none `active` or `complete` in either the before or the after state, no
  top-level key touched, and only the `systems` and `deliverables` fields changed. On
  `phase-arch-00` having been flipped to `active` in the earlier claim commit: "it does not
  matter… Reading the condition to forbid a phase from claiming itself would make any claimed
  phase unacceptable."

It raised three discrepancies against the record. Two were record errors and one was a real
imprecision in the split:

1. **The `## Backlog` section asserted a `complete` state that did not yet exist.** Correct, and it
   was written before the review by mistake. That section now describes the state written at close,
   after this review returned.
2. **`phase-arch-13` still declares the broad `ts/src/stage/` path**, which the "Deliverable paths
   narrowed" section did not say. Corrected in that section: two phases keep the broad path, not
   one, and `phase-arch-13` keeps it because the sub-app it packages has no file in the tree yet.
3. **Two cross-imports cross the explorers/viewer boundary and were not flagged**:
   `FileBrowserRegion.tsx:4` imports `COMPATIBLE_EXTENSIONS` from `HtmlViewerRegion`, and
   `HtmlViewerRegion.tsx:2` imports `DirectoryPickerDialog`, which `FileBrowserRegion` also
   imports. Its judgment: `DirectoryPickerDialog` "by the project's own logic belongs under
   `sys-wb-shared`, not `sys-wb-explorers`. A phase declaring only `sys-wb-viewer` could
   legitimately need to edit it and would not lock it."

On scope it found `sys-ui` genuinely left valid (occurrences in `backlog.yaml` 44 → 30, the 14
removed all from `phase-arch-01..17`, 22 other phases untouched, the registry entry unchanged but
for the appended paragraph); the `docs/00-working/` three-way collision fully removed; the
`ts/src/stage/` path collisions removed while `08`/`09` and `13`/`17` still collide on the engine,
which it agreed is real rather than an artifact; the counter-consideration "an argument, not a
gesture"; and no file touched outside the declared deliverables plus the session record and the
regenerated catalog. It agreed that `REQ-011` R29's third verification clause is the negation of
this phase's scope, calling reporting it "the correct disposal".

## Decisions

**The declaration rule was the session's one real decision, and the owner made it.** When a phase
writes only documents — the four audit and measurement phases — it can declare the systems it
writes to, or the systems it reads. The first lifts the ceiling further; the second is honest about
a stale-findings risk, because an audit is invalidated by a concurrent change to what it audits.
The owner chose declaring what they read. That choice is why waves 2 and 3 did not move:
`phase-arch-03` and `-04` read every file under `ts/src` and `src`, so they declare all seven ids
and collide with almost everything. The alternative would have shown a better number and hidden a
real hazard.

**Seven ids rather than four or five**, also the owner's choice from three options. The two that
are not panels earn their place: `sys-wb-styles` is a single file that the identifier migration and
the content-fit contracts both act on from opposite directions, and `sys-wb-shared` is where
`panelBridge` lives, the one module that reaches across slots. Folding either into the engine would
have made every CSS-touching or primitive-touching phase collide with every engine phase.

**The counter-consideration lives in the registry descriptions and the commit message**, not in a
`GOV-003` entry — the owner's choice, and it kept the change inside the phase's two declared
deliverables.

**`PLAN-028` and `REQ-011` were left stale rather than corrected**, on the owner's ruling, because
both sit outside this phase's deliverables and `PLAN-028` was an active peer's document when the
session opened.

## Corrections

- **The `## Backlog` section was written as though the phase were already complete, before the
  review that decides completion had run.** The sub-agent caught it. Rewritten to describe the
  state actually written at close.
- **`DirectoryPickerDialog.tsx` was filed under `sys-wb-explorers` when both the File Browser and
  the HTML Viewer import it.** Moved to `sys-wb-shared` after the review, which is where the same
  reasoning already put `Popover`. The measurement was re-run after the move and is unchanged at 3
  and 4, as expected — `collisions()` reads phase declarations, not registry paths.
- **`sys-wb-explorers` did not declare its dependency on `sys-wb-viewer`.** It does now, and its
  description names the `COMPATIBLE_EXTENSIONS` import as the code-level leak that forces it.

## Left undone

- **`sys-ui` is not retired.** That is `phase-arch-18`, deliberately, and it cannot run until no
  peer holds a claim declaring the id. Twenty-two other phases still declare it.
- **`PLAN-028`'s concurrency table and `REQ-011` R29 are stale or self-contradictory** against this
  change. Natural companion work for `phase-arch-18`, which will touch both corpora anyway.
- **`phase-arch-01` and `phase-arch-14` still serialize on `sys-wb-layout`** although neither writes
  engine code. `collisions()` has no read-versus-write distinction; adding one is a change to
  `src/governance/backlog.py` and to the meaning of the `systems` field, and belongs to nobody's
  phase today. It is the single clearest remaining gain in the lock table.
- **The `COMPATIBLE_EXTENSIONS` import from `HtmlViewerRegion` into `FileBrowserRegion` is not
  fixed.** The registry now records it rather than hiding it. Moving the constant to a shared module
  is frontend work, outside this phase's deliverables, and is a natural item for
  `phase-arch-03`'s duplication audit.
- **The audit filenames and test module names used to narrow deliverable paths are predictions.**
  A phase that lands on a different name should correct its own declaration rather than treat the
  guess as binding.
