# Open workbench ideas and backlog coverage (Session 4 - Scout)

Read-only scan, 2026-10-08. Sources: `_data/ideas.jsonl` (folded with `scratchpad/fold.py`), `docs/09-backlog/backlog.yaml`,
PLAN-027, PLAN-028, REQ-011, REQ-012, `docs/00-working/ideas-priority.yaml`, `docs/00-working/ideas.md`,
`docs/00-working/idea-partition-2026-09-23.md`.

## Method and counts

| Item | Value |
|---|---|
| Ideas in log | 599 (fold: 567 triaged, 17 discarded, 13 promoted, 1 delivered, 1 open) |
| Terminal states (`src/db/ideas.py` TERMINAL_STATES) | discarded, delivered, resolved, absorbed. `promoted` is not terminal. |
| Excluded as terminal | 18 (17 discarded, 1 delivered) |
| Keyword hits among the remaining 581 | 219 (noisy: "stage", "shell", "slot" and "pty" inside "empty" match unrelated ideas) |
| Judged workbench-related after reading | 51 listed below (24 + 9 + 2 covered, 16 uncovered); adjacent ideas excluded are listed at the end |
| Status of every idea below | `triaged`, except 000104 and 000112 (`promoted` to PLAN-022) |
| How coverage was decided | Backlog phases rarely carry the idea id. Coverage comes from the PLAN-027/028 group tables, then the phase `ideas:` field, then the id appearing in the backlog. A phase that lists an idea only as a review follow-up it did not fix is NOT coverage (000516, 000555, 000573). |

## (a) Open workbench ideas already covered by a phase

### (a1) Covered by a queued phase (24)

| Idea | Title | Phase(s) | Phase status |
|---|---|---|---|
| 000087 | Terminal interaction API for driving demo shell sessions from outside | phase-wbf-07 (ADR), phase-wbf-08 (build) | queued |
| 000109 | HTML Viewer: double-click a file tab opens a new browser tab | phase-wbf-01 (PLAN-027 G48; the phase's `ideas:` field lists 000119, not 000109) | queued |
| 000111 | File bookmark categories | phase-wbf-03 (ADR), -05 (build) | queued |
| 000120 | Batch, multi-target panel bridge for bookmark categories | phase-wbf-03, phase-wbf-04 | queued |
| 000131 | Rotator variant: horizontally scrolling text | phase-wbf-06 | queued |
| 000132 | Rotator variant: rotate images | phase-wbf-06 | queued |
| 000101 | Multi-panel slots render a double header after a dropdown swap | phase-arch-03 (audit), phase-arch-07 (fix by construction); REQ-011 R13 | queued |
| 000107 | Terminal session lost on layout switch | phase-arch-16 | queued |
| 000113 | Terminal persistence and performance audit, three shells | phase-arch-16 | queued |
| 000114 | General workbench performance audit, caching | phase-arch-14, phase-arch-15 | queued |
| 000121 | Cache invalidation vs regenerated overview page | phase-arch-14, phase-arch-15 (REQ-011 R22) | queued |
| 000115 | Duplication audit | phase-arch-03 (also listed on phase-wbf-04's `ideas:`) | queued |
| 000116 | Code structure and file-size audit | phase-arch-04 | queued |
| 000124 | Formalize workbench vocabulary | phase-arch-01 (complete), phase-arch-02 (identifier migration) | arch-01 complete, arch-02 queued |
| 000133 | Revisit slot geometries, custom layout reconfiguration | phase-arch-09 | queued |
| 000134 | Audit all slots and panels for content fit | phase-arch-05 | queued |
| 000135 | Multi-instance slots and panels | phase-arch-01 (complete), phase-arch-08 | arch-08 queued |
| 000141 | Slots as configuration schemas with sub-slots | phase-arch-01 (complete), phase-arch-06, phase-arch-07 | arch-06/07 queued |
| 000142 | Explore ports and system processes | phase-arch-11 (the phase's `ideas:` field lists 000099 and 000129, which are discarded; 000142 is only in PLAN-028 G45) | queued |
| 000143 | Small app for port usage and system processes | phase-arch-12 | queued |
| 000144 | Package the port/process app as a sub-app | phase-arch-10, phase-arch-13 | queued |
| 000233 | Panels maximize and collapse | phase-arch-17 | queued |
| 000122 | Evaluate non-web rebuild of the application | phase-expl-06 | queued |
| 000136 | Pack convention: browser smoke dispatch and runtime instruments (build-process, borderline workbench) | phase-agx-05 | queued |

### (a2) Phase is complete but the idea is still `triaged` (9)

| Idea | Title | Phase | Note |
|---|---|---|---|
| 000095 | Close the session-cap TOCTOU window | phase-wbf-09 | complete |
| 000096 | D_SYSTEM_DEMO_SHELL override vs per-session shell | phase-wbf-09 | complete |
| 000137 | Global-cap websocket refusal as structured close | phase-wbf-09 | complete |
| 000100 | Silence the flag-off 404 probes | phase-wbf-10 | complete |
| 000110 | HTML Viewer renders markdown | phase-wbf-11 (backfill) | complete |
| 000118 | Grow COMPATIBLE_EXTENSIONS | phase-wbf-11 | complete |
| 000119 | Markdown render location | phase-wbf-11 (and wbf-01 lists it) | complete |
| 000232 | HTML Viewer image formats | phase-wbf-11; phase-idg-16 (queued) backfills it to a terminal state | complete |
| 000234 | Decompose sys-ui | phase-arch-00 (complete), phase-arch-18 (retire, queued); phase-idg-16 (queued) backfills it | complete |

### (a3) Already promoted to PLAN-022, no phase needed (2)

| Idea | Title | Note |
|---|---|---|
| 000104 | Terminal panel clipped to ~85px | promoted to PLAN-022; phase-wb-08 (complete) fixed it |
| 000112 | File Explorer right-click opens file in HTML Viewer | promoted to PLAN-022; delivery not verified here |

## (b) Open workbench ideas with NO phase (16)

"Plan" is where it would fit. PLAN-027 = features and defects (P11), PLAN-028 = architecture and quality (P10).

| Idea | Title | Gist | Kind | Belongs to |
|---|---|---|---|---|
| 000246 | Terminal panel drops its connection and restarts unprovoked | Owner saw the terminal drop and restart with no trigger and ran the demo out of Claude Code instead. Diagnosis is the deliverable. Its own triage finding says "no phase claims investigation or fix". The 2026-09-23 partition (T8.1) ranks it first in the terminal group. | Defect (diagnose first) | PLAN-027 (terminal group G51; new phase, ahead of phase-wbf-07). It post-dates the plan (2026-09-15). |
| 000108 | HTML Viewer file-selector popup too short | Popup shows two entries; wants 8-10, scroll, open below, maybe resizable. | Defect | PLAN-027, one phase with 000117 and 000130 |
| 000117 | Popover height floor: fix in shared `Popover.tsx`, audit all consumers | `MIN_BUBBLE_HEIGHT_PX = 120` floor affects eight consumers. Extends 000108. REQ-011 cites it only as evidence for content-fit contracts; phase-arch-05 checks fit but does not fix it. | Defect plus audit | PLAN-027 (same phase as 000108/000130); phase-arch-05 later guards it |
| 000130 | Rotator help tooltip cut off at panel bottom; rethink font size | Probably another Popover consumer; adds rotator typography decisions. Owner note 2026-09-11: "live display bug worth demo-week attention". | Defect plus design | PLAN-027; could ride with phase-wbf-06 (same notes strip) once the Popover fix lands |
| 000238 | HTML Viewer steps through a directory's files | Step through diagrams one at a time instead of scrolling a long page. Owner put it on hold 2026-09-14. Partition T8.3 puts it in the Viewer group. | Feature | PLAN-027 G48 (new phase; shares HtmlViewerRegion.tsx with wbf-01/02) |
| 000594 | File Browser shows "Loading..." forever when a folder fetch fails | Render checks `entriesFolder !== contextFolder` before `loadState === 'error'`, so the error never shows. | Defect (small) | PLAN-027 (new small phase, `FileBrowserRegion.tsx`) |
| 000555 | HtmlViewerRegion page-exists check fooled by Vite SPA fallback | HEAD returns 200 from the SPA fallback when the flag is unset. Follow-up found in phase-wbf-10's review; listed on wbf-10's `ideas:` but not fixed there. | Defect | PLAN-027 (new phase; folds with wbf-01/02 on the same file) |
| 000573 | Close adapter and websocket when demo terminal startup fails | Leak after `accept()` if adapter creation fails; possible master pty fd leak. Found by phase-wbf-09's review, explicitly out of its scope. | Defect | PLAN-027 (terminal route, new phase beside wbf-07/08) |
| 000105 | Runbook does not document the HTML Viewer Embedded/Open-in-tab toggle | A demo-visible control missing from the runbook inventory. Note says reconcile with the layout-assignment redesign. | Defect (documentation) | PLAN-027, fold into wbf-01 or wbf-02 acceptance (same viewer header); no new plan |
| 000556 | Idea Explorer status filter omits delivered, resolved, absorbed, set_aside | `IdeaExplorerRegion.tsx:23` STATUSES list is stale. | Defect | PLAN-027 by file, PLAN-029 by subject (status vocabulary). Owner call. |
| 000516 | Teach workbench precedence map and Idea Explorer STATUSES the set-aside status | Same defect as 000556, backend half in `src/api/routes/workbench.py`. phase-idg-19 (complete) lists it under `ideas:` but its next_action says consumers still omit set_aside. | Defect | Same phase as 000556 and 000463 |
| 000463 | Idea consumers outside phase-idg-01's lock hard-code old statuses | `tools/overview_metrics.py`, `workbench.py` ranking, `src/orchestrator/state.py:67`. Workbench is one of three consumers. | Defect | Same phase as 000556/000516; PLAN-029 follow-up |
| 000569 | Error boundary and accessible loading/error status for the React stage | A render error blanks the whole app; PLAN-003 requirements retired without a replacement. | Feature / hardening | PLAN-028 (quality; new phase, REQ-011 would need a row) |
| 000123 | Audit pre-build HTML generation plans against what the workbench became | Document-by-document reconciliation. The partition groups it with 000115/000116 but PLAN-028 G41 omits it. The idea says phase-html-01 "still sits ready"; backlog now marks phase-html-01 cancelled. | Audit | PLAN-028 G41 (add), or the HTML-generation track. Owner call. |
| 000583 | Tests reading the live idea log should use a fixed fixture | A workbench test crashed on a status-table KeyError when 000554 became delivered. | Defect (test hygiene) | No fit in PLAN-027/028; PLAN-029 follow-up or a small standalone phase |
| 000360 | API routes and ts/ UI views for projects, people, commitments, tasks | Productivity-system gap 4.2; no route serves the four core entities. | Feature | New plan (not PLAN-027/028; they cover the existing workbench only) |

## Phase-side anomalies found while checking

| Finding | Detail |
|---|---|
| phase-wbf-02 is built on a discarded idea | Its source, 000102 (last-refreshed badge), was declined (`discarded`) by owner ruling at partition GATE 3, 2026-09-23. It was rehearsal-marked. PLAN-027 decision 1 records an owner affirmation on 2026-09-14, nine days earlier. The two rulings conflict and the phase is still queued. |
| phase-arch-11 `ideas:` lists discarded 000099 and 000129 | They are the PTY-test ideas (PLAN-027 G56, already fixed). 000142 is absent from the field. |
| phase-wbf-01 `ideas:` lists 000119 | PLAN-027 and the partition put 000109 there. |
| Review follow-ups recorded as phase `ideas:` | 000516 (idg-19), 000555 (wbf-10), 000573 (wbf-09 prose). Reading the field as coverage would hide three open defects. |
| 9 ideas in (a2) stay `triaged` after delivery | PLAN-027 says there was no honest status for them. `resolved` and `delivered` now exist in the writer. phase-idg-16 (queued) backfills only 000232 and 000234. 000095, 000096, 000137, 000100, 000110, 000118, 000119 are in no backfill phase. |

## Owner priority records (item 4)

| Source | Workbench ranking recorded |
|---|---|
| `docs/00-working/ideas-priority.yaml` `next_up` (updated 2026-09-24) | None. 17 ideas ranked (000452, 000240, 000157, 000158, 000150, 000303, 000241, 000284, 000283, 000214, 000219, 000066, 000041, 000038, 000037, 000040, 000091); not one is a workbench idea. |
| `docs/00-working/ideas.md` "Priority queue" | Generated from the YAML above; the same list. |
| Owner note on 000108 (2026-09-11, repository-owner) | 000133 yields to demo-specific fixes and is explicitly a future phase. 000130 is a live display bug "worth demo-week attention". |
| `idea-partition-2026-09-23.md` T8.1 | "246 first" within the terminal group. This is the analysts' sizing note, not an owner ruling. |
| PLAN-027 and PLAN-028 | Order set by owner ruling 2026-09-14: P10 runs before P11. `next_up` is the authority; backlog.yaml `next_up` currently holds 15 phases and none is a phase-wbf or phase-arch phase. |

## Adjacent ideas excluded (HTML-generation or other tracks, not workbench)

| Idea | Why excluded |
|---|---|
| 000042, 000300, 000301, 000302, 000299, 000424, 000425, 000491, 000492, 000497, 000507, 000511 | Generated HTML pages, explorers and reference artifacts; the HTML-generation and monitoring tracks, not the workbench. 000042 is on phase-idg-08. |
| 000083, 000084 | Template and component libraries (000084 is on phase-des-04, queued). |
| 000322 | `--ready` conflict-check defect that happened to involve phase-wbf-01/02; governance tooling. |
| 000374 | Glossary generator rendering workbench rulings as terms; glossary tooling. |
| 000170-000193 | Demo-kit entries; "terminal" and "workbench" occur only in their descriptions. |
| 000097, 000138, 000139, 000204, 000236, 000145 | Anti-pattern tracking and process ideas that cite the workbench build as an example. |
