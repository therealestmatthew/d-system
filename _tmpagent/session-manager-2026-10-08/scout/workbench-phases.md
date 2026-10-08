# Workbench phases scout report (Session 4 - Scout, GOV-017)

Date 2026-10-08. Repo HEAD 6951bb6. Read-only. Sources: docs/09-backlog/backlog.yaml, PLAN-027, PLAN-028, REQ-011, REQ-012, GOV-003, `uv run python -m src.governance --ready`, `src.governance.backlog.collisions()` (called read-only).

Backlog `max_active: 4`; 1 held (phase-idg-12, agent-batch-runner, locks sys-governance, path-locks `test/`, `src/governance/`, `.claude/agents/`; the active-claims table says "no evidence: no agent/<phase-id> branch found", so the claim may be stale). 3 slots free.

## 1. Inventory of open phases

All open phases have file `status: queued`; the Ready/Waiting column is the derived state from `--ready`/`--backlog`. No workbench phase is `deferred`. No `phase-wb-*` is open (all 10 complete). Complete and out of scope: phase-arch-00, phase-arch-01, phase-wbf-09, phase-wbf-10, phase-wbf-11, phase-wb-01..10.

Counts of open phases: arch 17 (7 ready: 02, 03, 05, 11, 14, 16, 18; 10 waiting: 04, 06, 07, 08, 09, 10, 12, 13, 15, 17); wbf 8 (5 ready: 01, 02, 03, 06, 07; 3 waiting: 04, 05, 08); wb 0. Total 25 = 12 ready + 13 waiting.

"Verif" = number of `verification` commands. All have session_budget 1.

| Phase | Title | Prio | State | depends_on (state) | systems | deliverables | Scope, one line | Verif |
|---|---|---|---|---|---|---|---|---|
| arch-02 | Execute the workbench identifier migration | 2 | ready | arch-01 (complete) | wb-layout, wb-styles, wb-shared, wb-terminal, wb-notes, wb-explorers, wb-viewer | `_data/workbench/layouts/`, `ts/src/workbench/`, `ts/src/stage/` | Apply arch-01's per-class rulings; slot ids to role names; old stored browser state read via alias or discarded | 3 (pytest, npm build, governance) |
| arch-03 | Duplication audit across workbench and API | 2 | ready | arch-01 | the 7 wb-* + sys-api | `docs/00-working/workbench-duplication-audit.md` | Audit ts/src and src for repeated logic; Slot.tsx wrapper/header/switcher machinery explicit | 1 (governance) |
| arch-04 | Code structure and file-size audit | 2 | waiting | arch-01, arch-03 (queued) | the 7 wb-* + sys-api | `docs/00-working/workbench-structure-audit.md` | LOC per file with regenerable command; target structure per flagged file; two-way cross-reference with arch-03 | 1 |
| arch-05 | Per-panel content-fit contracts and mechanised checks | 2 | ready (but Conflicts: idg-12) | arch-01 | 7 wb-* | `docs/06-requirements/`, `test/test_workbench_fit_contracts.py` | Contract per panel type; generalise Playwright fill/scroll checks; undeclared panel fails a check | 3 |
| arch-06 | Decide slot configuration-schema model, superseding ADR-016 | 2 | waiting | arch-01, arch-05 (queued) | wb-layout | `docs/04-decisions/` | New ADR, supersedes ADR-016, keeps repo-data layouts + browser selections-only; allocator for the ADR code | 2 |
| arch-07 | Schema-owned slots and sub-slots, structural eligibility | 2 | waiting | arch-06 | wb-layout, wb-styles | `ts/src/workbench/`, `ts/src/stage/StagePage.css`, `docs/06-requirements/` | Slot schema with sub-slots; replaces REQ-007 W16 allow-lists (amend row); slot owns the single top bar | 3 |
| arch-08 | Multi-instance panel identity | 2 | waiting | arch-07 | wb-layout, wb-terminal, sys-api | `ts/src/workbench/`, `ts/src/stage/TerminalRegion.tsx`, `_data/workbench/layouts/` | Instance identity in layout data, storage shape, registry, session ownership | 3 |
| arch-09 | Reconfigurable slot geometry with per-role constraints | 2 | waiting | arch-05, arch-07 | wb-layout, wb-styles | `ts/src/workbench/`, `ts/src/stage/StagePage.css`, `_data/workbench/layouts/` | Constraint table per slot role first; zero-scroll at 4 window sizes | 3 |
| arch-10 | Define the sub-app package contract | 2 | waiting | arch-06, arch-07 | wb-layout | `docs/06-requirements/` | Contract doc: boundary, API surface, registration as panel type, data receipt | 1 |
| arch-11 | Ports and system processes: lifecycle exploration | 2 | ready | none | sys-delivery | `docs/00-working/ports-and-processes-lifecycle.md` | Document grounded in port-8000 conflict, orphaned dev servers, PTY reaping (000099/000129) | 1 |
| arch-12 | Build the port and process management application | 2 | waiting | arch-11 | sys-api, sys-delivery | `docs/04-decisions/`, `src/api/routes/`, `test/test_ports_api.py` | Report listeners/processes; kill/free actions; own ADR resolving ADR-015 read-only tension | 4 (pytest, ruff, mypy, governance) |
| arch-13 | Package port/process app as a workbench sub-app | 2 | waiting | arch-10, arch-12 | wb-layout | `ts/src/workbench/panelRegistry.tsx`, `ts/src/stage/`, `docs/06-requirements/` | Integrate only via arch-10's documented registration path; fix the contract not the wiring | 3 |
| arch-14 | Measure workbench performance before any cache | 2 | ready | none | wb-layout, wb-explorers, wb-viewer, sys-api | `docs/00-working/workbench-performance-baseline.md` | Figure + method for six measurements; propose no cache | 2 |
| arch-15 | Design and ship mtime-keyed caching | 2 | waiting | arch-14 | sys-api, wb-viewer | `src/api/routes/`, `test/test_workbench_cache.py` | Caches keyed on mtime or writer-busted; no bare TTL; regenerated overview visible at once | 4 |
| arch-16 | Terminal persistence and performance audit, three shells | 2 | ready | none | wb-terminal, sys-demo-stage | `docs/00-working/terminal-persistence-audit.md` | 3-shell x 5-event matrix; latency measurements; CMD/PowerShell cells flagged as owner-machine | 2 |
| arch-17 | Panel maximize and collapse on the slot model | 2 | waiting | arch-07, arch-09 | wb-layout, wb-styles, wb-terminal | `ts/src/workbench/`, `ts/src/stage/StagePage.css`, `test/test_workbench_maximize.py` | Slot-level, transient, PTY session survives; zero-scroll in both states at 4 sizes | 3 |
| arch-18 | Retire sys-ui across document and phase corpus | 3 | ready (Conflicts: idg-12) | arch-00 (complete) | sys-governance | `docs/08-governance/systems.yaml`, `docs/09-backlog/backlog.yaml` | Replace sys-ui in 33 docs and 28 phases (2026-09-14 measure), retire the id; run only when no active claim declares sys-ui | 2 |
| wbf-01 | Open viewer tab's file in new browser tab on double-click | 2 | ready | none | sys-ui | `ts/src/stage/HtmlViewerRegion.tsx` | Double-click tab opens full page; confirm route-side markdown render already makes it right | 2 (npm build, governance) |
| wbf-02 | Last-modified badge on HTML Viewer header | 3 | ready | none | sys-ui, sys-api | `ts/src/stage/HtmlViewerRegion.tsx` | Header badge tracks displayed file's mtime; prefer existing workbench filesystem route | 3 |
| wbf-03 | Decide bookmark category storage, reference, batch-bridge model | 2 | ready | arch-01 (complete) | sys-ui, sys-contracts | `docs/04-decisions/` | One ADR covering 000111 and 000120; argue storage against its alternative | 1 |
| wbf-04 | Extend panel bridge to batch, multi-target actions | 2 | waiting | arch-01, wbf-03 (queued) | sys-ui | `ts/src/stage/panelBridge.ts` | Widen BridgeSlot to N files; keep never-throws-never-queues degradation | 2 |
| wbf-05 | Bookmark category surface and consumers | 2 | waiting | arch-01, wbf-03, wbf-04 | sys-ui, sys-api | `ts/src/stage/` | Create/rename/delete categories, add/remove/list files; open as set via batch; legible degradation | 3 |
| wbf-06 | Rotator variants: scrolling text and image entries | 3 | ready | arch-01 (complete) | sys-ui | `ts/src/stage/NotesStripRegion.tsx` | One union entry model; horizontal scroll with pause; image entries from a directory; mixing ruling | 2 |
| wbf-07 | Decide external terminal interaction API | 2 | ready | none | sys-contracts | `docs/04-decisions/` | ADR: gating, loopback, identity, auth, buffer depth, detach; scoped against ADR-014; build nothing | 1 |
| wbf-08 | Flag-gated terminal inject and read API | 2 | waiting | wbf-07 | sys-api, sys-demo-stage | `src/api/routes/`, `test/` | Inject/read endpoints via broadcast buffer; routes absent with flag unset | 3 |

Systems abbreviation: `wb-X` = `sys-wb-X`.

## 2. Plan orderings and rulings

PLAN-028 (P10, architecture) and PLAN-027 (P11, features), both dated 2026-09-14.

| Rule | Source | Content |
|---|---|---|
| P10 before P11 | PLAN-028 Summary; PLAN-027 Summary | Owner ruling 2026-09-14: P10 is second in delivery order, P11 third; `next_up` is the authority on order. |
| Stated reason was wrong | PLAN-028 "Correction" | The claim that G40 is a prerequisite of "four P11 ideas" is withdrawn. The six prerequisite ideas (000115, 000116, 000133, 000135, 000141, 000144) are all P10. The ordering stands on the owner's ruling plus R01 vocabulary being a live input to P11 renaming. |
| P11 edge to P10 | PLAN-028 "What P11 depends on"; PLAN-027 "Sequencing" | A P11 phase that renames a slot/panel/region/layout identifier, or writes REQ rows using those nouns, depends on **phase-arch-01** (vocabulary), not arch-02 (migration). Four carry it: wbf-03, 04, 05, 06. wbf-01, 02, 07, 08 carry none. |
| Do not add arch-02 edge to wbf-01/02 | PLAN-027 "Sequencing" | arch-02 may rename `HtmlViewerRegion.tsx`, which wbf-01/02 edit. A file-level conflict for the coordinator, not a dependency. |
| Vocabulary gate vs migration split | PLAN-028 decision 2 | arch-01 = vocabulary + per-class ruling (the gate); arch-02 = execution, gates nothing. |
| What arch-01 settled (complete) | backlog.yaml `result`, session SESS-2026-09-15-01 | A slot is the container (named region of a layout grid); a panel is content assigned into exactly one slot; "element" is the tier a panel contains. Eleven terms in `brain/concepts/terms-workbench-ui.md`, glossary regenerated. Six identifier classes ruled: layout `slot_id` values, localStorage field names, test fixtures renamed; CSS class names, REQ-007 row wording, panel registry ids aliased. Slot ids become `primary/secondary/strip/explorer`; a slot id names its role and may never equal a panel id (`terminal` and `notes-strip` are currently both). |
| What arch-00 settled (complete) | backlog.yaml `result` | 7 `sys-wb-*` ids registered; 17 queued arch phases redeclared; concurrency ceiling among idea-derived arch phases 2 to 3; waves 2-6 did not move. Left stale on owner's ruling: PLAN-028 concurrency table and REQ-011 R29's third verification clause. |
| wbf phases keep `sys-ui` | PLAN-027 decision 6 | Owner ruling 2026-09-14: wbf-01..06 declare `sys-ui` as it exists; no edge to arch-00; no revisit note. |
| Maximize belongs to P10 | PLAN-028 decision 5 | arch-17 only; no wbf phase may add maximize. Longest chain: 01 -> 05 -> 06 -> 07 -> 09 -> 17. A viewer-only throwaway is rejected unless the owner decides otherwise. |
| ADR-016 superseded not amended | PLAN-028 decision 3 | arch-06 writes a new ADR carrying `supersedes: [doc-workbench-layout-decision]`, marks ADR-016 superseded in same change. |
| ADR-first | PLAN-027 decision 3 | wbf-03 and wbf-07 are ADR phases separate from implementation (wbf-04/05, wbf-08). |
| wbf-06 not coupled to bookmarks | PLAN-027 decision 5 | Images come from a directory; no edge to wbf-03..05. |
| arch-11/12 independent of arch-10 | PLAN-028 decision 4 | arch-13 is the contract's proof; it integrates with arch-13's app source closed. |
| Owner-machine checks | PLAN-028 "Known facts"; REQ-011 R23-R24 | arch-16 cannot be fully verified on Linux; CMD/PowerShell cells must be named, not asserted. |
| ADR-015 read-only tension | REQ-011 final note | arch-12 resolves it in its own ADR; no widening of ADR-015. |
| arch-18 guard | arch-18 scope | Not runnable while any active claim declares sys-ui. |

GOV-003 (grep `arch-|wbf-|workbench`) rulings that affect these phases. None names `phase-arch-*` or `phase-wbf-*` directly.

| Date | GOV-003 section | Effect |
|---|---|---|
| 2026-09-10 | "The demo-track completion gate extends to the workbench track" (line 274) | Coordinator-marked completion for `phase-wb-*` only. Does not cover arch/wbf. |
| 2026-09-11 | "The workbench completion gate extends to the fix phases" (line 299) | Extends to wb-08/09 only. Not arch/wbf. |
| 2026-09-16 | "Coordinator completion replaces owner-invoked /session-close, repository-wide" (line 456) | Applies to arch/wbf: complete needs verification green, independent adversarial review, and integration onto dev with the owner's explicit approval. |
| 2026-09-22 | "The idea lifecycle gains three terminal states" (line 558) | 000233 (maximize) is `absorbed` into PLAN-028 decision 5; 000232 `delivered`; 000099/000129 move to `resolved`. Confirms arch-17 owns maximize. |
| 2026-09-22 | "Parallel sessions run under a Session Manager, with six departures" (line 651) | Builders take the phase the Session Manager assigns; "System overlap, not the claim limit, is what bounds parallel work: one active claim blocked 46 of 74 ready phases". Preflight pytest runs in the worktree. |
| 2026-09-23 | "Remote branch deletion is owner-only", "Every worktree removal needs the owner's approval" (lines 803, 814) | Constrains cleanup after workbench builds. |

Requirement docs: REQ-011 (R01-R29) governs arch; REQ-012 (R01-R23) governs wbf. Every phase carries at least one row. REQ-012 R20 notes a code reading, not a storm, is the verification for the cap race (phase wbf-09, already complete).

## 3. Dependency graph and runnable set

Chains (arrows = "unblocks"):

```
arch-01(done) -> arch-02 (leaf; gates nothing)
              -> arch-03 -> arch-04 (leaf)
              -> arch-05 -> arch-06 -> arch-07 -> arch-08 (leaf)
                                               -> arch-09 -> arch-17 (leaf)
                                       arch-06+07 -> arch-10 -> arch-13
              -> wbf-03 -> wbf-04 -> wbf-05
              -> wbf-06 (leaf)
arch-05 + arch-07 -> arch-09
arch-11 -> arch-12 -> arch-13
arch-14 -> arch-15
arch-16 (leaf)
arch-00(done) -> arch-18 (leaf, last)
wbf-01, wbf-02 (leaves, no prereq)
wbf-07 -> wbf-08
```

Blockers of the rest: arch-05 (blocks 06 and 09, hence the whole G43 chain: 06, 07, 08, 09, 10, 13, 17), arch-03 (blocks 04), wbf-03 (blocks 04, 05), wbf-04 (blocks 05), arch-11 (blocks 12, 13), arch-14 (blocks 15), wbf-07 (blocks 08).

Rows copied from `--ready` (live, Queue column "—" for all, none are in `next_up`):

| Phase | Outcome | Prio | State | Prerequisites | Conflicts |
|---|---|---|---|---|---|
| phase-arch-02 | Execute the workbench identifier migration | 2 | ready | phase-arch-01 | — |
| phase-arch-03 | Duplication audit across the workbench and API | 2 | ready | phase-arch-01 | — |
| phase-arch-05 | Per-panel content-fit contracts and their mechanised checks | 2 | ready | phase-arch-01 | phase-idg-12 |
| phase-arch-11 | Ports and system processes: lifecycle exploration | 2 | ready | — | — |
| phase-arch-14 | Measure workbench performance before designing any cache | 2 | ready | — | — |
| phase-arch-16 | Terminal persistence and performance audit across three shells | 2 | ready | — | — |
| phase-wbf-01 | Open a viewer tab's file in a new browser tab on double-click | 2 | ready | — | — |
| phase-wbf-03 | Decide the bookmark category storage, reference and batch-bridge model | 2 | ready | phase-arch-01 | — |
| phase-wbf-07 | Decide the external terminal interaction API | 2 | ready | — | — |
| phase-arch-18 | Retire sys-ui across the document and phase corpus | 3 | ready | phase-arch-00 | phase-idg-12 |
| phase-wbf-02 | Show a last-modified badge on the HTML Viewer header | 3 | ready | — | — |
| phase-wbf-06 | Rotator variants: horizontally scrolling text and image entries | 3 | ready | phase-arch-01 | — |

Claimable now (ready and Conflicts empty): arch-02, arch-03, arch-11, arch-14, arch-16, wbf-01, wbf-02, wbf-03, wbf-06, wbf-07 (10). Not claimable while idg-12 is active: arch-05 (idg-12's `test/` covers `test/test_workbench_fit_contracts.py`), arch-18 (shares `sys-governance`).

Also of note in the same listing: none of arch/wbf waiting phases appear in `--ready`; their prerequisites are as in section 1.

## 4. Disjointness analysis

Pair test = `collisions()` (shared system, or deliverable path prefix overlap). Pairs among the 10 claimable phases that are CLEAR:

| Phase | CLEAR with |
|---|---|
| arch-02 | arch-11, wbf-03, wbf-07 (and arch-18, not claimable) |
| arch-03 | arch-11, wbf-01, wbf-03, wbf-06, wbf-07 |
| arch-11 | all other 9 |
| arch-14 | arch-11, arch-16, wbf-01, wbf-03, wbf-06, wbf-07 |
| arch-16 | arch-11, arch-14, wbf-01, wbf-02, wbf-03, wbf-06, wbf-07 |
| wbf-01 | arch-03, arch-11, arch-14, arch-16, wbf-07 |
| wbf-02 | arch-11, arch-16, wbf-07 |
| wbf-03 | arch-02, arch-03, arch-11, arch-14, arch-16 (collides with wbf-07 on `docs/04-decisions/` and with wbf-01/02/06 on `sys-ui`) |
| wbf-06 | arch-03, arch-11, arch-14, arch-16, wbf-07 |
| wbf-07 | arch-02, arch-03, arch-11, arch-14, arch-16, wbf-01, wbf-02, wbf-06 |

Maximal pairwise-disjoint sets (cliques):

| Set | Size | Note |
|---|---|---|
| {arch-11, arch-14, arch-16, wbf-01, wbf-07} | 5 | Largest. Exceeds the 3 free slots. All documentation or small-edit work; see hazard H5 and H6 on contention. |
| {arch-02, arch-11, wbf-03} | 3 | Contains the largest rename. |
| {arch-02, arch-11, wbf-07} | 3 | Variant (ADR is wbf-07 not wbf-03). |
| {arch-03, arch-11, wbf-01, wbf-07} (also with wbf-06 instead of wbf-01) | 4 | Audit plus small viewer or notes edit. |
| {arch-03, wbf-03, arch-11} | 3 | |
| {arch-14, arch-16, wbf-06, wbf-07, arch-11} | 5 | |

Anything with arch-02 is capped at size 3 (arch-02 collides with arch-03, 05, 14, 16, wbf-01, wbf-02, wbf-06). Anything with arch-03 or arch-05 excludes arch-02, 14, 16.

### Hazards: pairs the validator calls CLEAR, but whose real files overlap

| ID | Pair(s) | Why it is a hazard |
|---|---|---|
| H1 | wbf-01/02/04/06 x arch-05, arch-14 (arch-05 x wbf-01, 02, 04, 06 are CLEAR; arch-14 x wbf-01, 06 CLEAR) | wbf phases declare `sys-ui`, but the files they edit belong to `sys-wb-viewer` (HtmlViewerRegion.tsx), `sys-wb-shared` (panelBridge.ts), `sys-wb-notes` (NotesStripRegion.tsx) per `docs/08-governance/systems.yaml`. arch-05/arch-14 declare those systems. Collision is invisible to the validator because the wbf phases never declared the narrower ids (PLAN-027 decision 6 ruled this on purpose). |
| H2 | wbf-06 x arch-05 | arch-05 writes the notes-strip fit contract and mechanised check; wbf-06 changes how long entries overflow (horizontal scroll). The contract must be written first or wbf-06 invalidates it. Order arch-05 before wbf-06. |
| H3 | wbf-04 / wbf-05 x arch-03 (wbf-04 CLEAR, wbf-05 collides on sys-api) | arch-03 audits for a second file-passing mechanism beside `panelBridge.ts` (REQ-012 R07 cites 000115's audit). If wbf-04 lands first the audit sees the extended bridge; if concurrent the audit is stale. arch-03 should precede or at least not race wbf-04. |
| H4 | arch-02 x wbf-03 / wbf-07 (CLEAR) | The ADRs name slots/panels. arch-02 renames slot ids to `primary/secondary/strip/explorer`. The ADR author must use arch-01's glossary terms and the new ids; write after reading arch-02's diff or state the ids by role. Low severity. |
| H5 | arch-14 x anything concurrent (CLEAR with most) | arch-14 measures page load, panel mount, API round trips. Concurrent pytest, `npm run build`, or Playwright in sibling worktrees on the same machine distorts the figures. Run alone or beside documentation-only phases. |
| H6 | Port 8000 / dev servers | arch-05 (Playwright), arch-14, arch-16, wbf-01 (browser check), wbf-06, arch-17 all need a running API and Vite. Separate worktrees share the host's ports. This is arch-11's own subject (port-8000 conflict). The validator knows nothing of it. Give each concurrent session a distinct port or serialize browser phases. |
| H7 | `docs/04-decisions/`: wbf-03, wbf-07, arch-06, arch-12 (wbf-03 x wbf-07 flagged; arch-06 x arch-12 CLEAR and vs wbf-03 CLEAR in places) | ADR codes come from the governance allocator (`--next-code adr`); concurrent ADR authors race the counter and the directory. External ready phases also hold the whole directory: conc-05, conc-07, proj-01, ret-05 (all collide with wbf-03 and wbf-07). |
| H8 | `docs/06-requirements/` | arch-05 (dir), arch-07, arch-10, arch-13 all edit it; REQ-011 rows may be edited by two sessions. Serial by dependency in practice (05 < 07 < 10 < 13), arch-05 x arch-10 never overlaps in time. Also phase-irs-02 collides with arch-05 on the same dir. |
| H9 | arch-18 x every wbf-01..06 claim | arch-18 rewrites `systems` of 28 phases in backlog.yaml and says it cannot run while any claim declares `sys-ui`. wbf-01/02/03/04/05/06 are the live `sys-ui` declarers (plus cancelled html-05..10). The validator shows arch-18 CLEAR against all of them. Run arch-18 last, after wbf-01..06 complete. Also, every claim commit edits backlog.yaml, so arch-18 is one big merge-conflict magnet. |
| H10 | arch-02 x external phases | arch-02 collides with phase-irs-13 (declares `ts/`; currently not in the ready list), phase-idg-04 and phase-expl-04 (both declare `_data/workbench/layouts/`, both ready). Check before claiming arch-02. |
| H11 | wbf-08 declares `test/` whole | Collides with idg-12 now and with any phase writing a test module (arch-12, 15, 17). Narrow to a named module or serialize. |
| H12 | wbf-02 sys-api | The wbf-02 next_action hopes the work is frontend-only. `grep -n "mtime\|modified" src/api/routes/workbench.py` returns nothing, so the route does not carry mtime today; the backend change is needed and sys-api stays. wbf-02 then collides with arch-03, arch-14 (sys-api), and wbf-05, wbf-08. |
| H13 | arch-02 x wbf-01/02/06 | Flagged by the validator (shared paths), repeated for ordering: PLAN-027 warns that arch-02 may rename HtmlViewerRegion.tsx. Run arch-02 first, then these three, to avoid rebasing small phases onto a large rename. |
| H14 | arch-16 x arch-17 / wbf-09 history | arch-16 builds on 000107's corrected diagnosis (stored visible-panel choice differing between layouts kills the hidden shell's session). If arch-02 changes localStorage field names first, re-read the storage keys. |

## 5. Proposed build order

Constraints used: 3 free slots (4 if idg-12 releases; extra slot rarely usable because of collisions); the sys-wb-layout chain (02, 03, 04, 05, 06, 07, 08, 09, 10, 13, 14, 17) is strictly serial because they share systems; all wbf-01..06 serialize on `sys-ui`; arch-05 is blocked until idg-12 releases `test/`.

| Wave | Phases (concurrent) | Why this set |
|---|---|---|
| 1 (now) | arch-02, arch-11, wbf-03 | arch-02 lands the rename before the viewer/notes/bridge edits (H13) and while the layout chain is idle; arch-11 unblocks arch-12; wbf-03 unblocks wbf-04/05. All three pairwise CLEAR. Alternative third: wbf-07 (not both, they share docs/04-decisions/). |
| 2 | arch-05, arch-12, wbf-04 | arch-05 is the critical-path gate (06, 09) and uses post-rename slot ids. All CLEAR. If idg-12 still holds `test/`, substitute {arch-03, wbf-04, wbf-07} (all CLEAR; arch-03 is a documentation audit that races wbf-04 only mildly, H3). |
| 3 | arch-03, wbf-06, wbf-07 | Audit before G43 rewrites Slot.tsx; wbf-06 after arch-05's notes-strip contract (H2). All CLEAR. If arch-03 already ran in wave 2, put arch-06 here instead of arch-03 (arch-06 x wbf-06 CLEAR, x wbf-07 CLEAR). |
| 4 | arch-04, wbf-01 | arch-04 with wbf-01 (CLEAR). Add nothing else: arch-04 collides with every other ready phase except wbf-03/04/06/07. |
| 5 | arch-06, wbf-05, arch-16 | arch-06 needs arch-05 (done by wave 2). arch-06 x wbf-05 CLEAR, x arch-16 CLEAR, wbf-05 x arch-16 CLEAR. wbf-05 needs wbf-04. |
| 6 | arch-07, wbf-08 | arch-07 x wbf-08 CLEAR. wbf-08 needs wbf-07. Add wbf-02 only if sys-api conflict with wbf-08 is cleared (it is not, H12). |
| 7 | arch-09, wbf-02 | arch-09 x wbf-02 CLEAR. |
| tail, serial | arch-08, arch-10, arch-14 -> arch-15, arch-12 done, arch-13, arch-17, arch-18 | arch-08/09/10/13/14/17 all share sys-wb-layout (serial). arch-10 before arch-13 and after arch-07. arch-17 after 09. arch-14 should run on a quiet machine (H5). arch-15 after 14 (sys-api; with idg-12 gone no test/ conflict). arch-18 last (H9). |

If the coordinator wants the audits to follow the G43 chain, delay arch-03/04 until after arch-07; the cost is that audit file:line references describe the new structure and arch-07's own work gets no audit input.

Risk per phase (what would make a careful claimant decline):

| Phase | Risk |
|---|---|
| arch-02 | Largest blast radius (all 7 systems, ts/src/stage/ and ts/src/workbench/ whole dirs); needs the Playwright/browser pass for R05 stored-state check; only `npm run build` and pytest as automated verification; possible collisions with idg-04, expl-04, irs-13 (H10). |
| arch-03 | Judgment-heavy ("pays for itself"); acceptance is document reading; next_action wants Slot.tsx first. Low blocking risk. |
| arch-04 | Needs arch-03 first; acceptance is two lines. Stale if run after G43 rewrites. |
| arch-05 | Blocked by idg-12 `test/` claim (a claim that may be stale); needs a browser (Playwright) and a dev server; creates REQ rows in `docs/06-requirements/` (shared with irs-02). |
| arch-06 | Needs owner-reviewed ADR decisions (four ADR-016 decisions, keep/replace); acceptance short; must use allocator for ADR code. Blocked until arch-05. |
| arch-07 | Biggest architectural change; must amend REQ-007 W16 row and assert single-header count first; needs browser checks in both layouts; depends on an accepted arch-06 ADR. |
| arch-08 | Touches layout data, storage, registry and session ownership, including TerminalRegion; second terminal instance needs a real PTY. |
| arch-09 | Needs arch-05 and arch-07; zero-scroll at four sizes requires browser; constraint table must precede code. |
| arch-10 | Doc-only but cannot be validated until arch-13 tries it; depends on arch-06 and 07 being real, not just ADR. |
| arch-11 | Needs session records for the port-8000 incident (reconstruction); acceptance vague ("grounded in incidents"); low code risk. |
| arch-12 | A kill action contradicts ADR-015's read-only posture, so needs an owner decision recorded in its own ADR; runs pytest, ruff, mypy; destructive local actions in tests. |
| arch-13 | Requires working with arch-10's contract and arch-12's app source closed; end of two chains. |
| arch-14 | Needs a running stack and quiet machine; measurements are machine-specific; vague unless a method is named for each of six figures. |
| arch-15 | Needs arch-14 numbers; touches caching in API routes, risk of stale-overview regression (000121); four verification commands. |
| arch-16 | Cannot finish on Linux: CMD and PowerShell cells are owner-machine checks (R24). A careful agent declines to claim "complete"; it should deliver the bash column and mark the owner cells. Needs a browser and live PTYs. |
| arch-17 | End of longest chain (01-05-06-07-09-17); needs browser plus PTY survival test (set a variable, maximize, collapse). |
| arch-18 | Not runnable while idg-12 holds sys-governance or any sys-ui claim exists; edits 28 phases; the 33 documents measured on 2026-09-14 are stale and need recounting. |
| wbf-01 | Needs a browser to verify double-click (acceptance), but verification list is only `npm run build` and governance; must first confirm 000119's route-side rendering already works (maybe nothing to build). Overlaps the arch-02 rename. |
| wbf-02 | Backend change is probably required (H12); more than the declared frontend-only hope; pytest test_workbench.py plus browser check of the badge. |
| wbf-03 | ADR needs owner review before wbf-04/05 build against it; storage decision (tracked `_data/` vs browser storage) is an owner decision; acceptance lists browser and owner mentions. |
| wbf-04 | Depends on an accepted wbf-03 ADR; browser check for partial-target behavior; `panelBridge.ts` is owned by sys-wb-shared while the phase declares sys-ui (H1). |
| wbf-05 | Needs wbf-03 and 04; ts/src/stage/ whole-dir deliverable collides with arch-02, 07, 09, 13, 17 on paths; browser check. |
| wbf-06 | Needs mixing-text-and-image ruling (owner decision either way); browser needed for scroll/pause; contracts from arch-05 should come first (H2). |
| wbf-07 | ADR with six decisions, several security-relevant (auth, binding); needs owner review; must read idea 000087 via fold() and ADR-014 first. |
| wbf-08 | Depends on an accepted wbf-07 ADR; touches `test/` whole dir (H11); broadcast buffer design; route-absent-when-flag-unset check. |
