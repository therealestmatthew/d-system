# IDEA lines raised by builders, not yet recorded (Session Manager relay)

## RECORDED 000614-000630 at trunk b9aae45 (all items below)
## From Session 1 - Builder A (phase-wbf-07, ADR-030)
- The demo terminal websocket route has no authentication or Origin check (read from demo_terminal.py, not reproduced): any local process or any web page the owner has open can start a shell; decide whether to require a token or an Origin check there (ADR-014 owns the route; ADR-030 open item 7).
- src/api/__init__.py gates the terminal routes by an inline os.environ check with no shared helper for flag reads; a second flag would be the second copy of that pattern.
- The injection dropdowns and the terminal bridge could show when input came from the HTTP API rather than the keyboard; the panel currently marks nothing as externally injected.

## From Session 2 - Builder B (phase-wbf-04)
- FileBrowserRegion's single-file "Open in HTML Viewer" could route through deliverBatch with one path, so single and batch share one accounting path (wbf-05 or later).
- (duplicate of 000604) test_run_review_checks::test_an_unwritable_worktree_parent_is_refused fails whenever the suite runs as root.

## Recorded already (trunk 71f01b9): 000600-000613; mapping
000600-000604 from phase-arch-02 (Batch Runner); 000605-000608 from phase-arch-11 (Builder A); 000609-000612 from phase-wbf-03 (Builder B); 000613 from the Prompt Planner.

## PENDING (waves 4-6): not yet recorded. Dedupe: the root-only pytest failure is 000604 (annotate, do not add).
## RECORDED 000631-000643 at trunk 0507a37
### Session 3 - Standby Builder (phase-wbf-01)
- Double-clicking a non-active viewer tab can miss: the first click selects the tab and changes the header file button's label, the header row stops wrapping, and the tab strip moves up 14px at this panel width, so the second click lands on the strip. Observed in Playwright; predates the phase; the fix is CSS (a fixed-width file button or a non-wrapping header).
- The demo runbook entry for the HTML Viewer (docs/00-working/demo-runbook.md, around line 254) says only "Has tabs like the terminal". It should gain the double-click and Shift+Enter open-in-browser-tab behaviour.
### Session 1 - Builder A (phase-wbf-08)
- The terminal websocket route still has no authentication (ADR-030 open item 7); a per-session or token check there would close the gap that the new token does not. (Possible duplicate of the wave-3 websocket idea; annotate that one if it already exists.)
- The stage page could show the session id, or a visible "driven externally" cue, so a person watching a demo can tell an injected command from typed input.
### Session 3 - Standby Builder (phase-wbf-06)
- Remove or reword REQ-037's "unbounded entry is the defect phase-wbf-06 addresses" sentences and the C-row defect table entry now that the notes-strip active-entry row passes; and name the moving element (data-notes-part=track) in the notes-strip row per REQ-037's own boundaries text.
- The notes strip's silent-clip finding is entirely the dropdown trigger (000628); fixing the trigger's height clears both the visible and silent-clip rows. (Annotate 000628 rather than add.)
- A notes-strip fixture directory of images under ts/public (or a tracked test image directory) would let the Playwright rotator check be committed and gated instead of relying on _public/images.
- Gate the scratch Playwright rotator check (scroll, pause, rotation rule, image entry) as a repeatable test once the fit contract's live run has a gate (REQ-037 follow-up; link to 000629).
### Session 2 - Builder B (phase-wbf-13)
- Layout 2 at 1024x768: the HTML Viewer region header is 377 px of content in a 307 px box (live-check wrap and silent-clip findings), so header controls are clipped.
- Layout 2 "Skills (11)" popover needs 395 px but only 360 to 379 px of room exists on the larger side at 1280x720, so its last entries scroll; the Skills/Prompts/Agents dropdowns could be made more compact.
- Count-at-rest Playwright checks (including the fit contract's file-selector measurement) cannot catch a popover that fails to scroll; the live check could scroll the popover body with a real wheel and assert scrollTop moves.
### Session 5 - Batch Runner (phase-arch-06)
- REQ-037's live runner seeds panel_assignments by bare panel id and builds its matrix from eligible_slots, so arch-07 and arch-08 both break it; worth a note on those phases' deliverables.
- useWorkbenchLayouts.ts hardcodes the shell home slot (secondary) and the bash and PowerShell panel ids; these are type ids standing where instance ids will be, and are the likeliest place for an arch-08 regression.
- Per-instance terminal tab caps (4 each) against the global server cap (6): two terminal instances can reach the cap with fewer than 8 tabs; arch-08 should add a test for the refusal message with two instances.
### Session 5 - Batch Runner (phase-wbf-15)
- File Browser could show the API's error detail (or status) in the could-not-search alert; the listing fetch discards the response body today.

## PENDING (wave 6+)
## RECORDED 000644-000662 at trunk 91f33b3
### Session Manager (observed in the wbf-16 runner gate)
- test/test_demo_terminal_api.py::test_control_characters_reach_the_shell failed once under machine load ("'after-ctrl-c-4' never appeared"; it sleeps 0.3 s before sending Ctrl-C and reads with an 8 s timeout) and passed in every other run of the day; make it wait for evidence that `sleep 30` started instead of a fixed delay.
### Session 1 - Builder A (phase-wbf-16)
- The viewer's absent-page check cannot tell "route absent" from "file missing"; both print "does not exist". When the route is absent, a message such as "the file route is not enabled; start the frontend with D_SYSTEM_DEMO_TERMINAL=1" would be more accurate.
### Session 2 - Builder B (phase-arch-07, blocked attempt)
- REQ-037 rows that name .stage-region__header, and the "Header controls" rows that measure bar controls against the panel box, need amending in arch-07's requirements work; test/test_workbench_fit_contracts.py references stage-region__header.
### Session 3 - Standby Builder (phase-wbf-06 fix round)
- Record the notes-strip mixing ruling (one rotation is all text or all images) in REQ-012 or GOV-003 once the owner ratifies it.
- Move the entry-box overflow rules out of the inline style into StagePage.css in a later CSS pass (inline overflow: hidden overrides the stylesheet's overflow-y: auto).
### Session 5 - Batch Runner (phase-wbf-14)
- The fit check only measures tooltips present in each layout's default panels, so the overview panel's tooltip (layout 2 main slot) is never measured; assign the overview panel to a slot in the fit check's cells.
- A tooltip bubble has a roughly 8 px gap from its trigger, so a fast pointer move across the gap collapses it before it reaches the bubble; a transparent bridge or a short close delay would let the user reach and scroll a tall bubble.
### Session 2 - Builder B (phase-arch-16 terminal persistence audit) — 12 lines; see docs/00-working/terminal-persistence-audit.md on agent/phase-arch-16 for evidence
- The slot-header panel switcher silently ends every session of the panel it hides (3 tabs to 0 observed); no warning, and the region tooltip's "switching ... never ends a session" reads as covering it.
- A layout switch can end a shell silently when the stored visible panel differs between layouts (000107 residual); it also bypasses the re-assignment dialog's confirmation. (Annotate 000107.)
- The server closes any session with no client frame for 300 s whatever it is running (close code 1006, empty reason, no page keepalive); a long build is killed like an abandoned prompt (candidate cause for 000246; annotate 000246).
- The "Terminal connection closed. Reload the page to reconnect." message advises an action that ends every other live session in every panel; there is no per-tab reconnect.
- Under the dev server, StrictMode opens two websockets and spawns two shells per terminal mount; at 5 live sessions a new tab was falsely refused with "Maximum of 6 ..." in 2 of 4 trials (production build 0 of 4); the runbook demos on the dev server.
- A tab refused at the session cap stays dead after slots free; "+ New session" stays enabled at the cap; the tab shows only the server's reason, never the "close a session" instruction.
- Restore after drop reopens one session per previous tab (3 to 3; 4 to 4, which is 8 websockets on the dev server); no document says so and the dropped message gives no count.
- Collapsed state, dropped state and tab count are component-local: lost on reload and on a visible-panel round trip, and a reload of a dropped terminal returns a live terminal; no document says which is intended.
- PosixPtyAdapter.close() sends SIGTERM to bash only and never waits; shells inherit the backend's signal dispositions, so a backend started under nohup leaves foreground jobs running after the session ends; a defunct bash stayed a child of the backend.
- Client scrollback is xterm's unconfigured default of 1000 lines and is stated nowhere; long build logs cannot be scrolled back through.
- The only persistence regression guard (REQ-007 W15) is written with bash commands; no check covers CMD or PowerShell persistence.
- Turn the audit's Playwright event matrix and connect/echo/resize/cap measurements into a committed regression test; re-run the matrix after phase-arch-08 changes panel identity.
### Session 5 - Batch Runner (phase-wbf-14 fix round)
- At 1280x260 in layout 1 the notes strip ? trigger is covered by the slot header (Playwright hover intercepted by section[aria-label=Notes] and h2), so the help tooltip is unreachable at very short viewport heights.

## PENDING (wave 7)
### Session 2 - Builder B (phase-arch-16 fix round)
- On Windows the panel labelled Terminal (bash) is expected, from code reading, to start cmd (or the D_SYSTEM_DEMO_SHELL override) with no message, because the bash session sends no ?shell= and the platform route's per-shell availability is not used to hide it (audit finding F13, owner check O11).
### Session 1 - Builder A (phase-wbf-02)
- Re-selecting the file already shown in the HTML Viewer used to do nothing (no reload, no re-check); worth stating as a requirement row (now behaviour, covered only by a unit test).
- The HTML Viewer file dropdown list is fetched once per tab and directory, so a file regenerated or newly created after load never appears until the directory changes; it needs a refresh path.
- HTML Viewer header at layout 2, 1024x768 still needs 324 px in a 307 px box (000637; annotate): wrapping the controls group breaks the 60 px page-area floor, so the real fix is a shorter or collapsing control set.
- Dev-server ports are not exclusive across worktrees: another worktree's uvicorn already held the API port assigned to this phase (8033); dispatches should check ports are free or allocate them from a ledger.
### Session 1 - Builder A (phase-wbf-02 fix round)
- The fit-contract script seeds selected_file null, so no REQ-037 live check measures any panel with a file shown; seed a selected file for the HTML Viewer cells so features that add header content (like the badge) are measured.
### Owner rulings at the wind-down (2026-10-08) — record as ideas (owner asks), one each
- Add a defect phase to the workbench features plan: the demo terminal websocket reuses the ADR-030 bearer token (or an Origin check) on connect, closing ADR-030 open item 7 / idea 000614 (annotate 000614 and link).
- Renumber the HTML Viewer toggle's ladder label to match the runbook ladder (rung 7); keep the toggle visible (phase-wbf-18 follow-up).
- Preserve terminal sessions across visible-panel and layout switches (detach/reattach) instead of warning before ending them; reopens ADR-014 decision 4 and ADR-030 item 3; needs a decision phase (ADR) before a fix phase (link 000651, 000652, 000087).
- Write one owner-machine checklist document under docs/00-working/ collecting every Windows/owner check raised by the run (arch-02 browser profile, ADR-030 ConPTY and token file mode, bookmark route paths, REQ-037 CMD/PowerShell fit, wbf-18 R31 click, arch-16 O1..O11).
