# Terminal persistence and performance audit across three shells

Staging document for `phase-arch-16` (terminal persistence and performance audit across three
shells), governed by the idea-staging decision (`ADR-010`): ungoverned, no front matter, nothing here
is scheduled. It answers the workbench architecture requirements `REQ-011` R23 (a three-shell by
five-event persistence matrix) and R24 (five performance measurements, with the owner-machine checks
named). It builds on idea `000107` (terminal session lost on layout switch when the stored visible
panel differs between layouts) and is the work idea `000113` (audit terminal persistence and
performance across all three shells) asked for. It fixes nothing: every defect it meets is listed in
section 7 for the idea log.

## 1. What was audited and how to read the evidence

**Build audited.** The terminal panel as shipped at commit `21f890f` of branch
`agent/phase-arch-16`: `ts/src/stage/TerminalRegion.tsx` (the panel), `ts/src/stage/StagePage.tsx`
and `ts/src/workbench/` (layout engine, `schema_version` 3), `src/api/routes/demo_terminal.py` (the
websocket route and session registry). `ADR-016` (layouts are versioned repository JSON, which
stores the visible-panel choice per layout per slot) is superseded by the proposed `ADR-031` (slot
configuration-schema model, awaiting ratification); `phase-arch-08` (multi-instance panel identity) will change how panel
instances are identified. This matrix describes what runs today and should be re-run when that lands.

Every claim carries one label.

| Label | Meaning |
|---|---|
| **Measured (Linux)** | Observed on 2026-10-08 on the machine in section 2, with a command or script recorded here. Applies to bash only. |
| **Document** | What an ADR, requirement or code comment says the behavior should be. Platform independent. |
| **Code reading** | What the source does, read but not run on the shell in question. |
| **Owner-machine, not run** | Needs the owner's Windows machine. Not asserted. Section 8 says what to do and what to look for. |

CMD and PowerShell cells never carry a **Measured (Linux)** label. Where a Linux observation about
the CMD or PowerShell panel is reported (the panel shows an unavailability message), it is about the
panel on Linux, not about the Windows shell.

## 2. Environment and method

| Item | Value |
|---|---|
| Host | Linux 6.18 virtual machine, loopback only (client and server on one machine, so network latency is about zero and every latency below is a lower bound for any other setup) |
| Shell under test | GNU bash 5.2.21, root user, default rc files (prompt appears within about 17 ms) |
| Backend | `uvicorn src.main:app --port 8029` from the worktree `.venv` (Python 3.13.16), no `--reload`, `D_SYSTEM_DEMO_TERMINAL=1` and `D_SYSTEM_TERMINAL_API=1` |
| Frontend, development | Vite 6.4.3 dev server on 5199 with `D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://127.0.0.1:8029` (React 18.3.1 `StrictMode`, xterm.js 6.0.0, addon-fit 0.11.0). This is how the runbook launches the demo. |
| Frontend, production build | `npx vite build --outDir <scratch>/dist` then `vite preview --port 5199` with the same two variables. Used to separate development-mode effects from the product (sections 6.1 and 6.5). |
| Browser | Chromium headless from `/opt/pw-browsers`, Playwright driven from Node v22.22.0; a fresh browser context (empty `localStorage`) for each experiment unless the experiment says otherwise |
| Server-side truth | `GET /api/v1/demo/terminal/sessions` with the bearer token (`ADR-030`, built by `phase-wbf-08` as the flag-gated terminal inject and read API) lists live sessions; every "session survived" or "session ended" claim below is checked there as well as in the page |

Launch commands used (the development server was stopped and the preview server started on the same port when the production build was measured):

```bash
cd <worktree>
D_SYSTEM_DEMO_TERMINAL=1 D_SYSTEM_TERMINAL_API=1 setsid -f .venv/bin/python -m uvicorn src.main:app --port 8029 --host 127.0.0.1
cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://127.0.0.1:8029 npx vite --port 5199 --strictPort --host 127.0.0.1          # development
cd ts && D_SYSTEM_DEMO_TERMINAL=1 npx vite build --outDir <scratch>/dist --emptyOutDir                                              # production build
cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://127.0.0.1:8029 npx vite preview --outDir <scratch>/dist --port 5199 --strictPort
```

**Session identity check.** To tell "the same shell" from "a new shell" the script types
`export MARKER=<value>` once, then `echo "PID=$$ MK=${MARKER:-none}"` before and after the event. A
surviving shell prints the same pid and marker; a new one prints a new pid and `MK=none`. The server
session list is compared before and after as a second signal. Scrollback is checked by output
position (section 6.4).

**Launch artefact caught and corrected.** The first backend was started with `nohup`, which makes the
process ignore `SIGHUP`, and every shell it spawns inherits that. The first page-reload experiment
therefore showed a foreground `sleep` surviving the reload. That result was an artefact of the launch
and is discarded; the backend was restarted under `setsid -f` (checked in `/proc/<pid>/status`:
`SigIgn` no longer contains the `SIGHUP` bit) and the experiment was re-run. The same inheritance is
a finding in its own right (F9).

**Scripts.** The Playwright and raw-websocket scripts were kept in the session scratchpad and are not
committed (the deliverable of this phase is this document). The two measurement scripts whose numbers
anyone would want to reproduce are reproduced in appendix A and B. Every event experiment is
described as a step list in section 5, so it can be repeated by hand.

**Dev server effect on counts.** `ts/src/main.tsx` renders under `StrictMode`. In the development
server every terminal session mount runs its effect twice: the first websocket is opened, then closed
as soon as its handshake completes, and the second is the one used. Websocket and slot counts below
are given for both builds where they differ; behavior is otherwise identical on both (every event
experiment was run on both, except the state-survival table of 5.4, which is development build only, and the cases marked not repeated).

## 3. The matrix at a glance

Survival, intent and communication for each of the three shells and five events. Section 4 is the matrix of record. Detail, evidence
and exceptions are in section 4 (the cells) and section 5 (the Linux evidence behind the bash cells).
"Owner-machine" cells are not run; their intent and communication entries are judged from documents
and from the code the three panels share, and are marked as such.

| Event | bash (Linux, measured) | CMD (owner-machine, not run) | PowerShell (owner-machine, not run) |
|---|---|---|---|
| **Layout switch** | **Survives** when the destination layout shows the same shell. **Ends, silently** when the destination's stored visible panel for that slot is a different panel. | Survival: owner-machine, not run (O1). Intent and communication: as bash, by document and shared code. | Survival: owner-machine, not run (O1). Intent and communication: as bash, by document and shared code. |
| **Visible-panel switch** | **Ends, silently**: every tab of the panel that is hidden. | owner-machine, not run (O2). Intent and communication: as bash row 2, by document and shared code. | owner-machine, not run (O2). Intent and communication: as bash row 2, by document and shared code. |
| **Re-assignment** | **Survives** for the moved panel. **Ends, after a stated confirmation**, for the panel it displaces. | owner-machine, not run (O3). Intent and communication: as bash row 3, by document and shared code. | owner-machine, not run (O3). Intent and communication: as bash row 3, by document and shared code. |
| **Collapse, drop, restore** | Collapse **survives**. Drop **ends all** after a confirmation. Restore starts **fresh** sessions, one per previous tab. | owner-machine, not run (O4). Intent and communication: as bash row 4, by document and shared code. | owner-machine, not run (O4). Intent and communication: as bash row 4, by document and shared code. |
| **Page reload** | **Ends all**, no notice. Layout, assignment and visible-panel choices persist. | owner-machine, not run (O5). Intent and communication: as bash row 5, by document and shared code. | owner-machine, not run (O5). Intent and communication: as bash row 5, by document and shared code. |

## 4. The matrix in full

Each table is one shell. Rows are events. Every cell has the three parts `REQ-011` R23 requires.

### 4.1 bash (Linux, measured)

| Event | Survival (Measured, Linux) | Intent (Document; Code reading where tagged) | Communication (Measured, Linux, except entries tagged Code reading) |
|---|---|---|---|
| **Layout switch** | **(a) Same shell shown in both layouts: survives.** Layout 1, 2, 1 from a cleared store: same pid and marker at each step, zero new terminal websockets in the production build, the same server session id (section 5.1). **(b) Shell in a different slot in each layout: survives.** bash assigned to Main in layout 1 and left in the Terminal slot in layout 2: same pid and marker across 1, 2, 1; the pty is resized from 10 by 62 (Main slot) to 17 by 156 (Terminal slot of layout 2). **(c) Destination layout's stored visible panel for that slot is another panel: ends.** Pid changed, marker lost, server session count 1 to 0 on arrival at layout 2, a fresh bash on return. This is the residual of `000107`. | (a) and (b): **intended.** `REQ-007` W15 names it as a regression guard: set a marker in layout 1, switch to layout 2 and back, "no new terminal websocket opens during the switches". `StagePage.tsx` explains the mechanism (stable per-panel host element). (c): **judged: the ending is a designed consequence, ending it silently is not documented as intended.** It follows from two rules that are intended separately: the visible-panel choice is stored per layout per slot (`ADR-016` decision 3) and a hidden panel is not mounted (`StagePage.tsx`: mounting hidden shells would consume the backend's six session slots, `ADR-014` decision 4). `REQ-007` W16's "never silently kills a shell session" is worded for re-assignment, not for layout switches, so no document says the silence is wanted or unwanted; by analogy with W16 it is a gap. Awaiting ratification (decision D1). | **None, in all three cases.** The layout choice applies immediately on selecting the radio button. In case (c) the only text on screen is the newly shown panel's own content. The confirmation that re-assignment has (section 4.1, row 3) is not reached by a layout switch. |
| **Visible-panel switch** | **Ends.** Three tabs open with markers `tab1` to `tab3`; choosing CMD in the slot header changed the server session count 3 to 0. Choosing Terminal (bash) again produced one tab, a new pid and no marker (section 5.2). | **Judged: the ending is deliberate, ending it silently is not documented as intended.** `StagePage.tsx`: "Only the visible panel of each slot is portaled. A hidden panel stays unmounted, which is deliberate", for the six-slot cap reason. `REQ-006` R10 says "switching tabs or collapsing the region never terminates a session", where "tabs" are the session tabs inside one panel, not this switcher. `REQ-007` W16 says the header dropdowns "switch among a slot's assigned panels and never re-assign" and says nothing about the session. By analogy with W16 the silence is a gap. Awaiting ratification (D1). | **None.** The switcher popover contains only the title "Terminal: choose a panel" and the other panel names (`CMD`, `PowerShell`); there is no warning and no confirmation, and nothing is shown afterwards. The terminal region's own tooltip says "Switching tabs or collapsing this region never ends a session" (Code reading, `TerminalRegion.tsx`), which a person can read as covering this switch. |
| **Re-assignment** | **Moved panel: survives.** bash moved from Terminal to Main with the configuration dialog: same pid and marker, zero new websockets, the pty follows the slot (34 by 88 to 10 by 62). **Displaced panel: ends, after confirmation.** HTML Viewer moved into the Terminal slot while bash was showing there: cancel left the session and its pid unchanged; confirm took the server session count 1 to 0. | **Intended.** `REQ-007` W16: "Re-assigning a panel between slots never silently kills a shell session: live sessions survive re-assignment where feasible; where a remount is unavoidable its behavior is explicit and stated, never a silent kill." The host-element mechanism that lets the moved panel survive is described in `ts/src/stage/StagePage.tsx` (Code reading); the proposed `ADR-031` also describes it; `REQ-007` W17 is a single row and states no such mechanism. | **Yes, before applying.** The dialog states which panel would close and the cost, quoted verbatim in section 5.3, offers `Confirm: move HTML Viewer and close Terminal (bash)` and `Cancel`, and states that the moved panel is not restarted (verified true). The slot left empty by moving a visible panel away shows "No panel is shown here. Use this slot's header menu to choose one of the panels assigned to it." |
| **Collapse, drop, restore** | **Collapse: survives.** Server session ids unchanged, same pid, same top scrollback line (1969) before and after; no resize frame is sent while hidden and the pty is refitted on expand (34 by 88 stays until expand, then 40 by 105 with `stty size` agreeing). **Drop: ends all.** Three live sessions stayed three while the confirmation was showing; zero after confirming. **Restore: fresh.** Three tabs before the drop gave three new sessions after restore (pid new, marker gone). **Tab close: ends that one**, three to two, after confirming. | **Intended.** `REQ-006` R10 (collapse never terminates), R11 (drop and tab close each need an explicit confirmation before any session terminates); `REQ-007` W02 (the `(...)` menu keeps those semantics) and W03 ("Restore returns a working terminal"). No document says restore should reopen as many sessions as there were tabs; that count is a side effect of tab state being kept while the sessions are unmounted (F7). | **Yes for drop and tab close, partial for restore.** Drop confirmation: "Dropping the terminal region ends every open session's shell process and scrollback. This cannot be undone. Use "Collapse terminal" instead to hide it without ending anything." Tab close: "Closing this tab ends its shell process and scrollback. This cannot be undone." After drop the panel says "Terminal dropped ... choose "Restore terminal" to start fresh sessions." It does not say how many sessions will start, and restore itself asks nothing (R10 and R11 do not require it). Collapse needs no message. |
| **Page reload** | **Ends all.** The new page starts one session whatever the previous tab count; the old session is gone from the server; foreground and plain background jobs received `SIGHUP` and ended; a `nohup` job and a `setsid` job outlived the session (section 5.5). Layout, assignment and visible-panel choices persist; collapsed state, dropped state and the tab count do not. | **Intended.** `ADR-014` decision 4: "One PTY per websocket stays; sessions still die with their websocket"; detach and reattach stay parked in idea `000087` (terminal interaction API for driving demo shell sessions from outside the stage page). `ADR-016` decision 3: the browser stores selections, not terminal state. | **No notice of any kind.** There is no `beforeunload` prompt (Code reading: searched `ts/src`) and the new page does not say a previous session ended. Separately, the connection-closed message "Terminal connection closed. Reload the page to reconnect." advises the action that ends every other live session in every panel (F4). |

### 4.2 CMD (owner-machine, not run)

| Event | Survival | Intent (Document) | Communication |
|---|---|---|---|
| **Layout switch** | **Owner-machine, not run.** Procedure O1. Expected by document, not asserted: same as bash (a) and (b). The `REQ-007` W15 regression guard is written with bash commands only (`MARKER=persist$RANDOM`, `echo check-$MARKER`), so no existing check covers CMD or PowerShell persistence. | As bash row 1: survival intended, stored-visible-panel case undecided (D1). Same component, so the same documents apply. | **Not observed for this shell.** By code reading the panels are one component (`TerminalRegion`) parameterized by shell name, so the same silence is expected in the stored-visible-panel case. **Code reading, not observed:** the panel labelled Terminal (bash) is not refused on Windows and is expected to start the host's default shell under that label (F13); O11 covers it. |
| **Visible-panel switch** | **Owner-machine, not run.** Procedure O2. | As bash row 2 (D1). | Not observed for this shell; code reading says no warning (one switcher for all shells). |
| **Re-assignment** | **Owner-machine, not run.** Procedure O3. | As bash row 3 (`REQ-007` W16). | Not observed for this shell; code reading says the same dialog text with the display name `CMD`. |
| **Collapse, drop, restore** | **Owner-machine, not run.** Procedure O4, including the Task Manager check that drop leaves no `cmd.exe` behind. | As bash row 4. `TerminalRegion.tsx` states that tabs, collapse, drop and the injection dropdowns "behave identically regardless of shell". | Not observed for this shell; code reading says the same texts. |
| **Page reload** | **Owner-machine, not run.** Procedure O5, including whether `ping -t` or a similar child outlives the reload. | As bash row 5. | Not observed for this shell; same remark as bash. |

### 4.3 PowerShell (owner-machine, not run)

| Event | Survival | Intent (Document) | Communication |
|---|---|---|---|
| **Layout switch** | **Owner-machine, not run.** Procedure O1. On a fresh store PowerShell is the default visible panel on Windows (`REQ-007` W17), in both layouts, so the round trip of case (a) is the default arrangement there. | As bash row 1. | Not observed for this shell; as CMD. |
| **Visible-panel switch** | **Owner-machine, not run.** Procedure O2. | As bash row 2 (D1). | Not observed for this shell; as CMD. |
| **Re-assignment** | **Owner-machine, not run.** Procedure O3. | As bash row 3. | Not observed for this shell; as CMD. |
| **Collapse, drop, restore** | **Owner-machine, not run.** Procedure O4, including whether `powershell.exe` or `conhost.exe`/`OpenConsole.exe` processes remain after a drop. | As bash row 4. | Not observed for this shell; as CMD. |
| **Page reload** | **Owner-machine, not run.** Procedure O5. | As bash row 5. | Not observed for this shell; as CMD. |

**What the Linux run does show about the other two panels.** Selecting the CMD or PowerShell panel on
Linux opens a websocket with `?shell=cmd` or `?shell=powershell`; the server accepts it, sends one
`shell_refusal` frame and closes with code 4002 (`ADR-014` decision 5). The panel shows "cmd is not
available on this host" or "powershell is not available on this host" and no session exists on the
server (count 0). That is the Linux behavior the Windows run must not be confused with. A refusal
does not hold a cap slot (section 6.5).

## 5. Evidence behind the bash cells (Measured, Linux)

Each experiment ran on the development server (counts of websockets are doubled by `StrictMode`,
section 2) and was repeated on the production build with the same outcome, except the state-survival table of 5.4 (development build only) and the cases marked not repeated. Pids are those printed by
`echo "PID=$$ MK=${MARKER:-none}"`.

### 5.1 Layout switch

Steps, from a cleared store, layout 1 active, bash showing in the Terminal slot:

1. `export MARKER=m$RANDOM`, then the identity check. Record the session ids from the sessions list.
2. Open **Configure layout**, choose **Layout 2 - Terminal Bottom**, close the dialog. Identity check.
3. Choose **Layout 1** again. Identity check; compare session ids.

| Run | Before | After layout 2 | After layout 1 | Terminal websockets opened by the switches |
|---|---|---|---|---|
| (a) development | pid 15950, `MK=m15784` | pid 15950, `MK=m15784` | pid 15950, `MK=m15784` | 0 (2 sockets existed from the one mount) |
| (a) production | pid 6743, `MK=m24373` | pid 6743, `MK=m24373` | pid 6743, `MK=m24373` | 0 (1 socket) |
| (b) bash assigned to Main in layout 1, default slot in layout 2 (development) | pid 23572, `MK=misc`, pty 10 by 62 | pid 23572, `MK=misc`, pty 17 by 156 | pid 23572, `MK=misc` | 0 |
| (c) layout 2's Terminal slot set to PowerShell first (development) | pid 16434, `MK=L1bash` | session ended: server sessions 1 to 0, page shows "powershell is not available on this host" (Linux) | pid 16482, `MK=none` | 2 per mount in development, 1 in production |

Case (c) steps: in layout 2 choose PowerShell in the Terminal slot header (bash is hidden and ends
there, which is the event of section 5.2), switch to layout 1 (bash mounts fresh), set
`MARKER=L1bash`, switch to layout 2, switch to layout 1. This is the corrected diagnosis of `000107`
reproduced: the layouts' own files agree (both set `default_visible_panel.secondary` to `terminal`),
and the failure needs a stored visible-panel choice that differs between the layouts. A browser that
has been used for that, and not cleared, will show it on every round trip.

### 5.2 Visible-panel switch

1. Open two more tabs (**+ New session** twice); in each of the three, `export MARKER=tabN`, identity
   check. Pids 17269, 17284, 17299.
2. Click the slot header **Terminal (bash) ▾**, choose **CMD**. Server sessions: 3, then 0.
3. Click the header **CMD ▾**, choose **Terminal (bash)**. One tab, pid 17320, `MK=none`; server
   sessions 1.

Popover text when open (read from the DOM): `Terminal: choose a panel × CMD PowerShell`.

### 5.3 Re-assignment

Steps use **Configure layout**, one selector per panel, from a cleared store.

1. `export MARKER=reassign`; identity check (pid 17941).
2. Terminal (bash) selector: **Main**. Dialog text (verbatim):
   "Main is showing HTML Viewer. A slot shows one panel at a time, so moving Terminal (bash) there
   closes HTML Viewer - any live session or unsaved state in it ends and it starts fresh when shown
   again. Terminal (bash) itself is not restarted by the move." Click **Confirm**. Result: pid 17941,
   `MK=reassign`, zero new websockets, server sessions 1. The vacated Terminal slot shows its header
   "Choose a panel ▾" and "No panel is shown here ...".
3. Reload. The assignment persists (bash is still in Main) and the session does not: pid 18363,
   `MK=none`, the old session id is gone from the server.
4. Move bash back to Terminal (the slot shows nothing, so no confirmation): zero new websockets, same pid.
5. HTML Viewer selector: **Terminal**. Dialog text: "Terminal is showing Terminal (bash). ... moving
   HTML Viewer there closes Terminal (bash) - any live session or unsaved state in it ends and it
   starts fresh when shown again. HTML Viewer itself is not restarted by the move." **Cancel**: server
   sessions 1, same pid. Repeat and **Confirm**: server sessions 1 to 0.

### 5.4 Collapse, drop, restore

1. Open two more tabs, `export MARKER=cN` in each (pids 19700, 19715, 19733). Record server session ids.
2. `...` menu, **Collapse terminal**: the slot box stays 711 by 600 px, the body is hidden
   (`display: none` on `.stage-region--terminal-collapsed .stage-region__body`), the session ids are
   unchanged. **Expand terminal**, Session 2: pid 19715 as before.
3. `...` menu, **Drop terminal**: the confirmation text is shown and server sessions are still 3.
   **Confirm**: server sessions 0, the panel (same 711 by 600 px box) shows the dropped message.
4. `...` menu, **Restore terminal**: 3 tabs, 3 server sessions, pid new, `MK=none`. Websockets
   opened: 6 in development, 3 in production.
5. Tab 3 **x**, confirmation text shown, server sessions 3; **Confirm: close session 3**: server sessions 2.

Which of these states survives other events (development build; measured by the experiments of section 5.4 steps 6 and 7 below and by the collapse and drop checks in the page-reload and layout-switch runs):

| State | Layout switch | Page reload | Panel switched away and back |
|---|---|---|---|
| Collapsed | kept | lost (panel returns expanded) | lost |
| Dropped | kept | lost: the panel returns as a live terminal with one new session | lost |
| Tab count | kept | lost (one tab) | lost (one tab) |

Steps for the table, development build, cleared store:

6. Collapse, switch to layout 2 and back, check the collapsed class; Expand, collapse again, reload, check
   it. Drop, switch layouts and back, check the dropped message; reload, check it. Collapse, switch the
   slot to CMD and back, check it.
7. Open two more tabs (3), switch to layout 2: 3 tabs and 3 server sessions. Back to layout 1, reload:
   1 tab. Open two more tabs (3 again), switch the slot to CMD and back: 1 tab. Drop, switch the slot to
   CMD and back: the dropped message is gone and the panel is live. The same run also produced the
   eight five-live trials of 6.5.

### 5.5 Page reload

1. Start in the shell: `sleep 7771 &`, `nohup sleep 7772 >/dev/null 2>&1 &`,
   `setsid sleep 7773 >/dev/null 2>&1 &`, `(disown; sleep 7774) &`, and a foreground `sleep 7775`.
2. Reload the page. Compare which `sleep` processes remain (`ps -eo pid,args`, matched exactly, never
   by pattern kill).

| Process | After reload |
|---|---|
| `sleep 7771 &` (background job) | ended |
| `sleep 7774` in a subshell | ended |
| `sleep 7775` (foreground job) | ended |
| `nohup sleep 7772 &` | **still running**, parent is init |
| `setsid sleep 7773 &` | **still running**, parent is init |

Server sessions after the reload: 1 (the new page's), pid new, `MK=none`. These last two are ordinary
shell semantics and are not a defect of the panel; they matter to the ports and processes work
(`phase-arch-11`, the lifecycle exploration, and `phase-arch-12`, the port and process management application) because the panel cannot be relied on to end work a person
detached. The test's own sleeps were removed by pid afterwards.

### 5.6 A session closed by the server at 300 seconds

Not one of the five events, but it decides whether a session survives, so it is reported. The route
ends any session that sends no websocket frame for `DEFAULT_IDLE_TIMEOUT_SECONDS` = 300
(`demo_terminal.py`). The page sends frames only for keystrokes and resize; there is no keepalive
(Code reading: searched `ts/src`). Output from the shell does not count.

| Client | Command running | Result |
|---|---|---|
| Raw websocket to the backend | foreground `sleep 905` | closed by the server **300.088 s** after connecting, close code **1006**, empty reason |
| The real page | foreground `sleep 906` | websocket closed **300.002 s** after the command; the page showed "Terminal connection closed. Reload the page to reconnect." at 300.241 s |

The process did not survive: no `sleep 905` or `sleep 906` remained afterwards. `000246` (terminal
panel drops its connection and restarts unprovoked) is owned by `REQ-012` R24; this measurement is
one candidate cause for that note, not its diagnosis.

## 6. The five measurements (`REQ-011` R24)

All figures are bash on Linux over loopback (**Measured, Linux**). The CMD and PowerShell figures are
owner-machine checks (section 8, O6 to O10); no number here stands in for them. Conventions: `n` is
the sample count, "median" and "p95" are over those samples, times are milliseconds unless stated.

### 6.1 Connect latency

Raw protocol, no browser: 30 sequential connections each, the client waits for the first output byte,
then closes. Script: appendix A (the measurement script there is the standalone form of the one used;
the one used also polled the sessions list). "Prompt" and "first byte" coincide because bash writes
its prompt as the first output.

| Path | Socket open (median / p95 / max) | First byte = prompt (median / p95 / max) |
|---|---|---|
| Direct to the backend, port 8029 | 3.2 / 6.1 / 15.0 | 17.5 / 20.6 / 25.4 |
| Through the Vite dev proxy, port 5199 | 4.3 / 5.6 / 6.5 | 18.7 / 23.8 / 30.4 |

The first connection a client process makes can be slower than the rest. The appendix script as written in this document, run once with its warm-up line removed, gave open max 87.7 ms (median 5.0) and first-byte max 102.0 ms (median 22.0) over 30 connections; with the warm-up line, two runs gave open max 10.6 and 7.8 ms and first-byte max 32.7 and 28.5 ms. Per-sample values were not recorded, so that the outlier is the first sample is inferred from the removal of the warm-up, not read from a sample. It is consistent with client-side initialisation (the headline figures above were taken after an HTTP request had already warmed the client, so they do not contain it), not with the backend's start-up.

In the page (Playwright, in-page timers):

| Measure | Development (median, range, n) | Production build (median, range, n) |
|---|---|---|
| Click **+ New session** to a prompt in the new tab | 60.8 (58.2 to 65.8, n=3) | 35.2 (35.0 to 36.9, n=3) |
| Navigation start of a cold page to the first prompt in the terminal | 1864.9 (1574.3 to 2005.1, n=8) | 810.1 (748.8 to 850.0, n=8) |
| With CMD showing, click **Terminal (bash)** in the slot switcher, to a new bash prompt | not measured | 67.3 (58.9 to 70.3, n=6) |
| Click on a layout radio to the new grid being applied | not measured | 23.2 (19.8 to 28.0, n=6) |

The page-load figure is dominated by what the page does before the first socket opens (loading the
bundle, fetching the two layout files, the platform route and the `terminal-enabled` check); the
socket itself accounts for under 25 ms of it. Server-side release after a client closes: the slot was
free again about 2 ms later (median of 30, polled).

### 6.2 Echo latency

One session at the prompt, 300 single-character writes 30 ms apart, time from `send` to the echoed
byte arriving.

| Path | Median / p95 / max |
|---|---|
| Direct to the backend | 1.8 / 3.3 / 24.1 |
| Through the Vite dev proxy | 2.1 / 4.5 / 11.7 |

In the page: 120 keypresses 60 ms apart, from the `keydown` event timestamp to the rendered text
changing in the xterm DOM (a `MutationObserver`; appendix B). Development: 27.9 median, 36.4 p95, 50.3
max. Production build: 27.8 median, 35.5 p95, 38.2 max. The transport accounts for about 2 ms of it (above); the rest is xterm's write and render path and the browser's frame timing, which were not separated further.

### 6.3 Resize behavior

Fit: the xterm container tracks its slot, and the pty tracks the xterm grid. For each layout and
viewport the page was resized, then `echo "SZ=$(stty size)"` was typed and compared with the last
resize frame the page had sent and with the number of xterm rows in the DOM.

| Layout | Viewport | xterm height / slot body height (px) | Rows by columns: DOM = last frame sent = `stty size` |
|---|---|---|---|
| 1 | 1280 by 720 | 522 / 558 | 34 by 88, equal |
| 1 | 1366 by 768 | 570 / 606 | 38 by 95, equal |
| 1 | 1920 by 1080 | 874 / 910 | 58 by 135, equal |
| 1 | 1024 by 768 | 570 / 606 | 38 by 69, equal |
| 2 | 1280 by 720 | 263 / 299 | 17 by 156, equal |
| 2 | 1366 by 768 | 293 / 329 | 19 by 167, equal |
| 2 | 1920 by 1080 | 477 / 513 | 31 by 237, equal |
| 2 | 1024 by 768 | 293 / 329 | 19 by 123, equal |

The 36 px difference at every size is the session tab bar. Layout 2 at 1280 by 720 gives the shell
17 rows.

Other resize behavior:

- **Resize bursts are not coalesced.** A sweep of 41 viewport widths 10 ms apart (about 0.8 s)
  produced 40 resize frames. The final frame matched the pty (below).
- **Latency to the shell.** With `trap 'echo WINCH $(stty size)' WINCH` set, the shell printed the new
  size 33 ms and 40 ms (two runs) after the viewport change, and it equalled the last frame (33 rows
  by 75 columns).
- **Hidden sessions are not resized until shown.** With the region collapsed, a viewport change sent
  no frame (the pty stayed 34 by 88); after **Expand terminal** the page sent 40 by 105 and `stty
  size` agreed. A tab that was not active during a viewport change had `stty size` equal to the xterm
  grid once activated (30 by 67). Until it is shown again a hidden session's pty has the old size.
- **Re-assignment resizes the pty** to the new slot (34 by 88 to 10 by 62, section 4.1).

### 6.4 Scrollback handling

- **Client scrollback is 1000 lines.** `TerminalRegion.tsx` does not pass `scrollback` to `new
  Terminal(...)`, so xterm.js's default of 1000 lines applies. Measured: after `seq 1 3000`, scrolling
  to the top (Shift+PageUp, 120 presses) showed 1969 as the first line of 1034 retained (1000 lines
  plus the 34 visible rows; lines 1969 to 3002 including the sentinel and the prompt). After `seq 1
  200000` the first retained line was 198969. Anything older is gone, and a build log longer than
  about a thousand lines cannot be scrolled back through.
- **Scrollback survives collapse and expand** (first retained line 1969 before and after) and
  re-assignment and layout switches that keep the shell (same xterm instance). It does not survive
  anything in section 4.1 that ends the session.
- **Server-side ring.** With `D_SYSTEM_TERMINAL_API=1`, the backend keeps the last 262,144 bytes of a
  session's output for the interaction API (`OUTPUT_RING_BYTES`). After 6,685,316 bytes had been
  emitted, the ring held offsets 6,423,172 to 6,685,316 and a read from offset 0 returned
  `truncated: true`. The ring is for `GET .../output` only; it is not replayed to a new websocket, so a
  reload cannot recover earlier output.
- **Throughput and responsiveness**, time from the Enter keydown to the sentinel appearing in the
  rendered rows, three runs: `seq 1 20000` 67 to 83 ms; `seq 1 200000` 254 to 526 ms; a 5,000,000-byte
  burst folded to 200 columns 655 to 782 ms. The browser's `longtask` observer (tasks over 50 ms) saw
  none in any run, so the page stayed responsive during the floods.

### 6.5 Behavior at the six-session cap

Backend cap: `MAX_CONCURRENT_SESSIONS` = 6, counting live and reserved sessions across all pages and
panels (`demo_terminal.py`; `ADR-014` decision 4). The per-panel tab cap is 4 in the page.

Raw websockets, directly to the backend:

| Step | Result |
|---|---|
| Open 6 | all admitted (61 bytes of startup output each); server count 6 |
| Open a 7th | accepted, then closed by the server after **6.6 ms** with code **4001** and reason "Maximum of 6 concurrent terminal sessions reached"; 0 bytes; server count stays 6 |
| Request `?shell=powershell` at the cap | the same 4001: the cap is checked before the shell request |
| Close one, connect again 150 ms later | admitted |
| `?shell=powershell`, `?shell=cmd` below the cap | accepted, one `shell_refusal` text frame (`unavailable_shell`), closed with 4002; server count unchanged (4 before, 4 after) |
| `?shell=zsh` below the cap | `shell_refusal` with `invalid_shell` and the message "'zsh' is not a supported terminal shell (allowed: bash, cmd, powershell)", 4002; no slot used |

In the page, with other sessions held open by raw websockets:

| Scenario | Development | Production build |
|---|---|---|
| 6 live (5 raw + 1 page tab), click **+ New session** | the new tab shows "Maximum of 6 concurrent terminal sessions reached" (the server's reason); server count 6; the button stays enabled | the same |
| 5 live (4 raw + 1 page tab), click **+ New session**, 4 trials | **2 of 4 refused (first run), 4 of 8 (second run), with the same message although a sixth slot was free** (live count stayed 5 after the click) | 0 of 4 refused; 6 live each time |
| Two pages open (page 1 four tabs, page 2 adds tabs) | page 2's second and third attempts refused at 5 live (2 of 2) | page 2's first and second tabs admitted (6 live), the third refused |
| Two slots freed after a refusal | the refused tab stays refused (server count 4 and the overlay unchanged) | not repeated |
| Reload with 6 live (5 raw + 1 page tab), 1 trial each | the new session was admitted | the new session was admitted |
| Restore after drop with 4 tabs | 4 sessions live, none refused, 8 websockets opened | 4 live, 4 websockets |

The false refusals are consistent with the development server's doubled mount (section 2): the first
websocket of a mount can still hold the sixth slot when the second arrives, so the second is
refused. This is inferred from the contrast with the production build, which does not double the
mount; the order of slot release and arrival was not traced. The refusal rate varies from run to
run: 2 of 4 in the first run and 4 of 8 in a second run (section 5.4's added experiment). The refused tab shows the server's reason only; the longer instruction in
`connectionRefusalMessage` (Code reading) ("Close a session tab here or in another terminal panel, then open a new
session.") is shown only when the browser reports a handshake failure, which this server does not
produce.

## 7. Findings

Each is a distinct defect or gap met while auditing. None is fixed here. Evidence labels as in
section 1; the matrix cell or measurement it comes from is named.

| Id | Finding | Evidence |
|---|---|---|
| F1 | **Switching the visible panel in a slot ends every session of the panel it hides, with no warning.** Three tabs went to zero server sessions; coming back gives one fresh tab. The only text in the switcher is the panel names. `REQ-006` R10's "switching tabs ... never terminates a session" refers to session tabs, and the terminal region's tooltip uses the same word "switching". | Measured (Linux), section 5.2; Code reading, `Slot.tsx`, `StagePage.tsx` |
| F2 | **A layout switch can end a shell silently**, and it bypasses the confirmation the re-assignment dialog gives. The cause is the stored visible-panel choice differing between layouts (`000107`'s corrected diagnosis). It needs only one earlier visible-panel switch in the other layout to be left in browser storage. | Measured (Linux), section 5.1 case (c) |
| F3 | **A session with no keystrokes for 300 seconds is closed by the server, whatever it is running, and the page has no keepalive.** The socket closes with code 1006 and an empty reason; the page shows "Terminal connection closed. Reload the page to reconnect." A long build or a `tail -f` that only produces output is closed at the same moment as an abandoned prompt. `000246` is the unprovoked-drop idea; this is one measured cause. | Measured (Linux), section 5.6 |
| F4 | **The advice in the connection-closed message ends every other live session.** Reload is the only route the message offers; it ends all sessions in all panels (section 4.1, page reload). A closed tab can also be replaced by closing it and opening a new one, which the message does not say. | Measured (Linux) for the effect; Code reading for the message |
| F5 | **In the development server each terminal mount opens two websockets**, the first closed as soon as its handshake completes (`StrictMode`; whether the first also starts a shell was not traced). At five live sessions a new tab was refused with "Maximum of 6 concurrent terminal sessions reached" in 2 of 4 trials and 4 of 8 trials although a sixth slot was free; the production build refused 0 of 4. The runbook launches the development server for the demo. | Measured (Linux): the two websockets per mount, the refusal counts and the production-build contrast, sections 2 and 6.5. Inferred, not traced: that the first websocket holds the slot the second needs. |
| F6 | **A tab refused at the cap stays refused after slots free**, and **+ New session** is enabled while the cap is reached (its own limit is 4 per panel). The tab shows only the server's reason; the instruction to close a session is shown only on a handshake failure, which the server does not produce. | Measured (Linux), section 6.5; Code reading, `connectionRefusalMessage` |
| F7 | **Restore after drop reopens one session per previous tab** (three to three; four to four, which is eight websockets in the development server). No document says this, and the dropped message does not give the count. | Measured (Linux), sections 5.4 and 6.5 |
| F8 | **Collapse, drop and tab count are component-local and are lost on reload and on a visible-panel round trip.** A reload of a dropped terminal returns a live terminal with a new session. No document says whether that is intended. | Measured (Linux), section 5.4 |
| F9 | **Shells inherit the backend's signal handling, and `close()` sends `SIGTERM` to bash only.** A backend started under `nohup` left a foreground `sleep` running after its page reloaded (the artefact described in section 2). `PosixPtyAdapter.close()` does not wait for the child: a `[bash] <defunct>` process stayed a child of the backend after its session ended (observed twice; the earlier one was gone after the next session started). | Measured (Linux), section 2 and 5.5; Code reading, `src/demo/posix.py` |
| F10 | **Client scrollback is 1000 lines and is stated nowhere.** It comes from xterm.js's default. | Measured (Linux), section 6.4 |
| F11 | **The only persistence regression guard (`REQ-007` W15) is written with bash commands**, so no check covers CMD or PowerShell. | Document |
| F12 | **A hidden session's pty keeps its old size until it is shown.** Output produced while hidden is laid out for the old size. By design (`attemptFit` skips zero-size containers); recorded because `REQ-006` R10 promises running processes survive hidden. | Measured (Linux), section 6.3 |
| F13 | **On Windows the panel labelled Terminal (bash) is expected to start a Windows shell, not refuse.** `TerminalRegion.tsx` lines 210-211 send no `?shell=` for a bash session (`sessionShell === 'bash' ? '' : ...`). `_run_session` in `demo_terminal.py` checks availability only `if requested_shell is not None:` (line 465). `create_adapter(shell=None)` reaches `resolve_shell(None)` (`src/demo/factory.py` lines 36-48 (`resolve_shell`)), which returns the `D_SYSTEM_DEMO_SHELL` override if set and otherwise `DEFAULT_WINDOWS_SHELL`, which is `cmd`: the name is `DEFAULT_SHELL` at `src/demo/windows.py` line 16, imported as `DEFAULT_WINDOWS_SHELL` at `src/demo/factory.py` line 21. No UI code hides the bash panel by platform: the only reader of `GET /api/v1/workbench/platform` is `useWorkbenchLayouts.ts`, and it reads `platform` for the fresh-store default only, not the per-shell availability the route also reports. The panel's label and its shell can therefore disagree, with no message. The explicit `?shell=bash` request is what is refused on Windows (`_shell_is_available_on_host`), and the panel never sends it. | Code reading; not observed (owner-machine, O11) |

## 8. Owner-machine checks (the part agent evidence on Linux cannot supply)

`REQ-011` R24 requires these to be named. Everything below is **owner-machine, not run**. No result
for CMD or PowerShell appears anywhere in this document. The results go into the table at the end of
this section when the owner has them.

### 8.1 Setup for every check

1. Launch the backend and the frontend with the commands in `docs/00-working/demo-runbook.md` ("Launch
   Command Reference"), both with `D_SYSTEM_DEMO_TERMINAL=1`. For the optional server-side session
   list also set `D_SYSTEM_TERMINAL_API=1` on the backend (`ADR-030`; the token path is printed in the
   backend log; Windows permissions on the token file are themselves unverified).
2. Start from a cleared browser store (delete the workbench key from Local Storage in DevTools, or use
   a fresh browser profile). A stale stored visible-panel choice is exactly how the original `000107`
   measurement went wrong.
3. On Windows a fresh store shows **PowerShell** in the Terminal slot (`REQ-007` W17). The panel
   labelled **Terminal (bash)** is still offered in the slot header. **Code reading, not observed:** it
   is not refused on Windows; it is expected to start `cmd` (or the `D_SYSTEM_DEMO_SHELL` override)
   under the bash label (F13, O11). Pick the shell under test in the slot header (**Terminal: choose
   a panel**), and use the **CMD** and **PowerShell** panels, not the bash panel, for the CMD and
   PowerShell columns.
4. Identity check, the equivalent of the bash `PID`/`MARKER` line. Type once, then repeat after the event:

   | Shell | Set once | Check after the event |
   |---|---|---|
   | CMD | `set MK=<new value>` | `echo %MK%` (a new shell prints `%MK%` literally) |
   | PowerShell | `$env:MK='<new value>'; $PID` | `"PID=$PID MK=$env:MK"` (a new shell prints a different `PID` and an empty `MK`) |

   Scrollback sentinel, to look for after the event by scrolling up: CMD `for /l %i in (1,1,300)
   do @echo line %i`; PowerShell `1..300 | ForEach-Object { "line $_" }`.
5. In DevTools, Network, filter **WS**: every terminal socket is a row; a row that has ended shows
   as closed. Count the rows before and after each event. A new row during an event that should be
   survivable is a restart.
6. Process leaks: before opening any session, note the count of `cmd.exe`, `powershell.exe`,
   `conhost.exe` and `OpenConsole.exe` in Task Manager (Details tab, with the Command line column).
   Compare after each ending event.

### 8.2 Persistence events (the matrix cells)

For each of CMD and PowerShell, fill the **Survival** cells of sections 4.2 and 4.3 from these.

| Id | Event | Do | Look for (and what Linux bash did) |
|---|---|---|---|
| **O1** | Layout switch | Set the identity marker. (a) Switch layout 1, 2, 1 with the shell in the Terminal slot. (b) Assign the shell to **Main** in layout 1 and leave it in the Terminal slot in layout 2, and switch 1, 2, 1. (c) In layout 2 choose a different shell in the Terminal slot, return to layout 1, set the marker, switch to layout 2 and back. | Same marker and no new WS row in (a) and (b) (bash: survived both). In (c) a new shell and a lost marker (bash: ended, no message). Also whether anything on screen says so. |
| **O2** | Visible-panel switch | Open three tabs with distinct markers. In the slot header choose another shell, then choose the first one again. | Number of WS rows that closed (bash: all three), tabs after returning (bash: one), markers (bash: lost), any warning text before or after (bash: none). Task Manager: shells left behind. |
| **O3** | Re-assignment | Set the marker. Move the shell to **Main** with **Configure layout**; read the dialog; confirm. Then move **HTML Viewer** into the Terminal slot while the shell shows there: read the text, **Cancel**, check the marker, repeat and **Confirm**. | Moved shell keeps the marker with no new WS row (bash: kept); cancel leaves the session (bash: kept); confirm closes it (bash: closed). The dialog text should name the displaced panel and say the moved panel is not restarted. |
| **O4** | Collapse, drop, restore | Three tabs with markers and the sentinel lines, plus a long-running child (CMD or PowerShell: `ping -t 127.0.0.1`). `...` menu: Collapse, wait, Expand. Then Drop: read the confirmation, check nothing ended before **Confirm**, confirm. Restore. Close one tab by its **x** and confirm. | Collapse keeps markers, scrollback and the child (bash: kept). After Drop zero live WS rows, and **no `ping.exe` or shell processes left** in Task Manager (bash: foreground child ended). Restore: how many sessions start (bash: as many as there were tabs). |
| **O5** | Page reload | Marker, sentinel lines, `ping -t 127.0.0.1` running. Reload. Then also: close the browser tab and reopen the URL. | All sessions new, one tab (bash: yes). The reload leaves no `ping.exe` or orphaned shell in Task Manager (bash: foreground and background jobs ended; `nohup` and `setsid` jobs, which have no direct equivalent, outlived it). Whether `Start-Process`-started programs outlive the shell, as the Windows analogue. |
| **O11** | Terminal (bash) panel on Windows | With the Terminal slot showing **Terminal (bash)** on Windows, type the identity check for each candidate (`echo %MK%` after `set MK=1`, then `$PSVersionTable` or `ver`) to learn which shell started. Repeat with `D_SYSTEM_DEMO_SHELL=powershell` set on the backend. Also open the panel's tabs and the CMD panel and compare. | Which shell the bash-labelled panel starts (expected from code: `cmd`, or the override) and whether any message says it is not bash. A refusal message "bash is not available on this host" would contradict the code reading in F13. |

### 8.3 Performance measurements

| Id | Measurement | Do | Look for |
|---|---|---|---|
| **O6** | Connect latency | `node measure-terminal.js ws://127.0.0.1:<backend port> cmd`, then `powershell` (appendix A; needs Node 22 or later for the global `WebSocket`; the checklist asks only for Node 18, so check `node --version`). Also, in the page, time 10 clicks of **+ New session** to a visible prompt with a stopwatch or a screen recording. | `connect_ms.open`, `first_byte` and `last_byte_of_startup_output` for each shell. The script discards one warm-up connection, so its first sample is not the client's slow first connection. Expected, not observed: on Windows the first byte may be terminal setup sequences before the prompt, in which case `last_byte_of_startup_output` is the closer figure for "prompt ready"; a PowerShell profile may add to start-up. Like-for-like Linux bash baseline (this script, two runs, after its warm-up): open about 5 ms, first byte about 21 to 23 ms. The 6.1 tables were taken from a different run, warmed by an earlier HTTP request, and their medians are lower (3.2 ms open, 17.5 ms first byte, direct). |
| **O7** | Echo latency | The same script prints `echo_ms` (300 keystrokes). In the page, type into the shell under screen recording at 60 frames per second and count frames from key to character. | `median` and `p95`. Caveat (expected, not observed): the script counts the first byte after each key, which in PowerShell (PSReadLine) and ConPTY may be a redraw sequence rather than the character, so also report the page-level figure. Like-for-like Linux bash baseline (this script, two runs): echo median about 2.1 ms (the 6.2 table, from a different run, has 1.8 ms); page-level 28 ms. |
| **O8** | Resize | With the shell showing, set the window to 1280 by 720, 1366 by 768, 1920 by 1080 and 1024 by 768. At each, CMD: `mode con`; PowerShell: `$Host.UI.RawUI.WindowSize`. Compare rows and columns with what the page shows. Then drag the window edge continuously for five seconds and release. | Reported size equal to the visible grid at each size (bash: equal at all eight layout and size combinations). After the drag, the final size is correct within a second (bash: 33 to 40 ms) and the screen has no duplicated or torn lines (expected, not observed: ConPTY may repaint on resize). |
| **O9** | Scrollback | Print 3000 numbered lines (CMD `for /l %i in (1,1,3000) do @echo %i`; PowerShell `1..3000`). Scroll to the top and read the first retained line number. Resize the window once and look again for repeated lines. Then flood: create a file with `1..200000 | Out-File $env:TEMP\f.txt` and print it (`type %TEMP%\f.txt` in CMD, `Get-Content $env:TEMP\f.txt` in PowerShell) while timing to the last line, and note whether the page stays responsive (DevTools Performance, long tasks). | First retained line (bash: 1969 of 3002, a 1000-line scrollback), duplicated lines after resize, time to finish (bash: 254 to 526 ms for 200,000 lines), any page freeze. |
| **O10** | Six-session cap | Put PowerShell in the Terminal slot and CMD in **Main** (assign with the dialog). Open three tabs in each: six live. Click **+ New session** in either panel. Then free one tab and try again. Separately, with five live, click **+ New session** four times (closing the new tab each time) on the development server. | The seventh is refused with "Maximum of 6 concurrent terminal sessions reached" and the refused tab stays refused (bash: both). With five live, whether a free slot is ever refused (bash on the development server: 2 of 4 and 4 of 8). On the Linux development server a refusal is consistent with the doubled mount's first websocket still holding a slot when the second arrives (6.5); PowerShell is expected (not measured) to be slower to start and to end than bash, so this probe is the most likely to differ. |

### 8.4 Result sheet (to be filled by the owner)

| Id | CMD result | PowerShell result | Matches the bash column? |
|---|---|---|---|
| O1 to O5 | | | |
| O11 bash-labelled panel | | | |
| O6 connect | | | |
| O7 echo | | | |
| O8 resize | | | |
| O9 scrollback | | | |
| O10 cap | | | |

## 9. What this audit did not cover

- CMD and PowerShell on Windows: every survival, connect, echo, resize, scrollback and cap result.
  The Windows adapter (`src/demo/windows.py`, ConPTY through `pywinpty`) was read, not run. Two
  things in it are worth the owner's attention in O4 and O5: `read()` has no timeout and blocks until
  data or end of file, so a pump thread ends only when the shell does; and `close()` ends the shell
  process with `terminate(force=True)`, which does not obviously end its children.
- macOS.
- Unprovoked drops other than the 300-second idle close (`000246`, `REQ-012` R24).
- A machine other than a loopback client and server: no network, no second user, no slow disk.
- The file browser's "Inject path into terminal" and the injection dropdowns against a dropped or
  hidden terminal (`REQ-007` W04, W09 own them).
- A session surviving a backend restart. Sessions die with the backend by `ADR-014`; not tested.
- Several panels of the same shell at once: the registry supports it, the shipped layouts do not offer it
  (`phase-arch-08` changes that).

## 10. Assumptions and decisions awaiting the owner

Written under the pre-approved run of 2026-10-08; the owner has not reviewed these.

- **D1. Is a shell ending on a visible-panel switch (F1) or on a layout switch with a differing stored
  panel (F2) an intended outcome?** The documents are silent on the outcome. This audit judges the ending a designed consequence and the missing warning a gap, by analogy with `REQ-007` W16; the owner has not ruled. The options
  for a later phase are: keep the behavior and warn before it (as the re-assignment dialog does);
  keep hidden shells mounted and count them against the cap (`ADR-014` decision 4 is the reason they
  are not); or record the behavior as accepted. Not chosen here.
- **D2. "Re-assignment" in R23 is taken to mean moving a panel with the configuration dialog**, as
  `REQ-007` W16 uses the word, and the slot-header switcher is classed as a visible-panel switch.
- **D3. Intent and communication for CMD and PowerShell are judged from documents and from the code
  the three panels share.** They are not observations of those shells and are labelled so.
- **D4. Both builds were measured** because the runbook uses the development server and the
  development server changes websocket counts and cap behavior. The production-build figures are
  given where they differ.
- **D5. The 300-second idle close is reported inside this audit** although it is not one of the five
  events, because it decides survival; its diagnosis stays with `REQ-012` R24.

## Appendix A. Standalone connect and echo measurement script

Run on Linux against the backend on port 8029 for the figures in 6.1 and 6.2
(`node measure-terminal.js ws://127.0.0.1:8029 bash`, extracted from this appendix with `awk` and run twice. The first run printed, with 30 connections after one discarded warm-up and 300 echoes 30 ms apart, open 5.6 ms median (p95 9.9, max 10.6), first byte 23.2 ms (p95 32.4, max 32.7) and echo 2.1 ms median (p95 3.2, max 29.6); the second run printed open 4.8 (7.7, 7.8), first byte 21.0 (27.8, 28.5) and echo 2.1 (3.8, 9.7)).

The script uses the headline parameters of 6.1 and 6.2 (30 connections, 300 echoes, 30 ms apart) after one
discarded warm-up connection. It differs from the run behind the headline tables in that it also reports the time of the last
byte of start-up output, does not poll the sessions list for slot release (so those tables'
slot-release row is not reproduced by it), and discards a warm-up connection, where the headline run
was instead warmed by an earlier HTTP request; its medians are therefore a little higher than the
headline tables'. It is also the script for
owner checks O6 and O7 with `cmd` or `powershell` as the second argument. It talks to the backend
directly (the second path measured in 6.1 went through the Vite proxy), needs Node 22 or later, and
has no other dependency. Save it as `measure-terminal.js`.

```js
// Usage: node measure-terminal.js <ws-base> [shell]
//   node measure-terminal.js ws://127.0.0.1:8010 powershell
// Needs Node 22 or later (global WebSocket). No other dependency. Opens sessions one at a time.
// The first connection a Node process makes is slower than the rest, so one warm-up connection is
// made and discarded first (see section 6.1).
const base = process.argv[2] || 'ws://127.0.0.1:8029'
const shell = process.argv[3] // bash | cmd | powershell; omit for the host default
const url = `${base}/api/v1/demo/terminal/ws` + (shell ? `?shell=${shell}` : '')
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const stats = (a) => { const s = [...a].sort((x, y) => x - y); const q = (p) => s[Math.min(s.length - 1, Math.floor(p * s.length))]; return { n: s.length, min: +s[0].toFixed(1), median: +q(0.5).toFixed(1), p95: +q(0.95).toFixed(1), max: +s[s.length - 1].toFixed(1) } }

function connect() {
  return new Promise((resolve, reject) => {
    const t0 = performance.now()
    const ws = new WebSocket(url); ws.binaryType = 'arraybuffer'
    const r = { ws, tOpen: null, tFirst: null, tQuiet: null, buf: '', lastData: 0, listeners: [] }
    ws.onopen = () => { r.tOpen = performance.now() - t0 }
    ws.onmessage = (e) => {
      const now = performance.now()
      if (typeof e.data === 'string') { reject(new Error('refused or text frame: ' + e.data)); return }
      if (r.tFirst === null) r.tFirst = now - t0
      r.buf += new TextDecoder().decode(e.data); r.lastData = now
      r.listeners.forEach((f) => f(now))
    }
    ws.onclose = (e) => reject(new Error(`closed before ready: code ${e.code} ${e.reason}`))
    // "ready" = no new output for 300 ms after the first byte; tQuiet is then the time of the last byte seen
    const iv = setInterval(() => {
      if (r.tFirst !== null && performance.now() - r.lastData > 300) { clearInterval(iv); r.tQuiet = r.lastData - t0; ws.onclose = null; resolve(r) }
    }, 20)
    setTimeout(() => { clearInterval(iv); reject(new Error('no output within 20 s')) }, 20000)
  })
}

;(async () => {
  const out = { url }
  const open = [], first = [], ready = []
  { const w = await connect(); w.ws.close(); await sleep(300) } // warm-up, discarded
  for (let i = 0; i < 30; i++) {
    const r = await connect()
    open.push(r.tOpen); first.push(r.tFirst); ready.push(r.tQuiet)
    r.ws.close(); await sleep(300)
  }
  out.connect_ms = { open: stats(open), first_byte: stats(first), last_byte_of_startup_output: stats(ready) }
  const r = await connect()
  const lat = []
  for (let i = 0; i < 300; i++) {
    const before = r.buf.length, t = performance.now()
    const got = new Promise((res) => { const f = (now) => { if (r.buf.length > before) { r.listeners = r.listeners.filter((g) => g !== f); res(now) } }; r.listeners.push(f) })
    r.ws.send(new TextEncoder().encode(String.fromCharCode(97 + (i % 26))))
    const now = await Promise.race([got, sleep(2000).then(() => null)])
    if (now) lat.push(now - t)
    await sleep(30)
  }
  r.ws.send(new TextEncoder().encode('\x15')); r.ws.close()
  out.echo_ms = stats(lat)
  console.log(JSON.stringify(out, null, 1))
  process.exit(0)
})().catch((e) => { console.error(String(e)); process.exit(1) })
```

## Appendix B. The in-page echo recorder and the other measurement fragments

Echo in the page (6.2): installed with `page.evaluate` after focusing the terminal, then 120 keys
pressed with `page.keyboard.press` 60 ms apart; `window.__echo` holds the milliseconds from each
`keydown` event timestamp to the first change in the rendered text. Both timestamps come from the same
page clock, so no cross-process offset enters.

```js
window.__sig = () => [...document.querySelectorAll('.stage-terminal-session--active .xterm-rows')]
  .map(el => [...el.children].map(r => r.textContent.replace(/ /g, ' ').trimEnd()).join('\n'))
  .join('\n\f')
window.__echo = []; window.__pending = null
document.addEventListener('keydown', (e) => {
  if (e.key.length === 1) window.__pending = { t: e.timeStamp, len: window.__sig().length }
}, true)
new MutationObserver(() => {
  const p = window.__pending
  if (p && window.__sig().length > p.len) { window.__echo.push(performance.now() - p.t); window.__pending = null }
}).observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true })
```

Other fragments, so each number above can be reproduced by hand or in a script:

- Server-side session list (the second signal for survival):
  `curl -s -H "Authorization: Bearer $(cat ~/.d-system/terminal-api/<key>.token)" http://127.0.0.1:8029/api/v1/demo/terminal/sessions`
  (the file name is printed in the backend log at start-up).
- Identity check typed into the shell: `echo "PID=$$ MK=${MARKER:-none}"` after `export MARKER=<value>`.
- Size agreement (6.3): `echo "SZ=$(stty size)"`, compared with the last `{"type":"resize","cols":N,"rows":N}`
  text frame the page sent (Playwright `websocket.on('framesent')`) and the number of children of
  `.stage-terminal-session--active .xterm-rows`.
- SIGWINCH latency (6.3): `trap 'echo WINCH $(stty size)' WINCH`, then `page.setViewportSize`.
- Throughput (6.4): `seq 1 200000; echo F2$((1+1))END`, timed from the Enter `keydown` timestamp to
  `F22END` appearing in `.xterm-rows` (the sentinel is built by arithmetic so the typed command line
  cannot match it).
- Scrollback top (6.4): focus `.xterm-helper-textarea`, press `Shift+PageUp` 120 times, read the first
  child of `.xterm-rows`.
- Cap (6.5): six `new WebSocket('ws://127.0.0.1:8029/api/v1/demo/terminal/ws')` held open from a Node
  process, then a seventh; `close` event code and reason recorded.
- Idle (5.6): one raw websocket, `sleep 905` as its only input, nothing else sent; `close` event code
  and elapsed time recorded.
