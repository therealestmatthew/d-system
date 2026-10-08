# Owner-machine checklist (Windows)

This is one checklist of every check from the 2026-10-08 workbench run that can only be done on the
owner's Windows machine. The owner ruled on 2026-10-08 that these are collected in one place. The
document is ungoverned (`ADR-010`): no front matter, no code, no catalog entry. **Nothing in it was
run on Windows by an agent.** Every "Linux result" below is what an agent measured or read on Linux, given
for comparison. Where a check says "expected, not observed", the expectation comes from reading code
or documents, not from a run.

Fill the **Result** column of each table as you go, then copy the outcomes into the result sheet at
the end.

## Prerequisite: base setup

Complete [the Windows machine setup checklist](demo-windows-setup.md) first (repository, `uv`, Node,
`pywinpty`, frontend dependencies, ports free). This document does not repeat it.

Unless a check says otherwise, launch like this, in two PowerShell windows. Ports 8010 and 5180 are the
runbook's; the launch commands are in
[the demo runbook](demo-runbook.md) ("Launch Command Reference"). The `env ...` prefix used in the runbook is a Unix form; in PowerShell
set the variables with `$env:NAME='value'` before the command, as the setup checklist describes.

| Window | Command |
|---|---|
| Backend, repository root | `$env:D_SYSTEM_DEMO_TERMINAL='1'; uv run uvicorn src.main:app --port 8010` |
| Frontend, `ts\` | `$env:D_SYSTEM_DEMO_TERMINAL='1'; $env:VITE_API_TARGET='http://localhost:8010'; npm run dev -- --port 5180 --strictPort` |

Then open `http://localhost:5180`. Confirm the proxy with
`curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:5180/api/v1/workbench/injection-sources`: it must print `200`.

## 1. Workbench identifier migration (`phase-arch-02`)

Source: [the migration session record](../03-sessions/SESS-2026-10-08-02-execute-workbench-identifier-migration.md)
("Evidence", last paragraph before "Verification commands") and `ts/src/workbench/useWorkbenchLayouts.ts`.
The migration renamed the layout slot ids (`terminal` to `secondary`, `main` to `primary`) and bumped the
layout `schema_version` from 2 to 3. The browser storage key is `d-system:workbench-state:v{schema_version}`
(`ts/src/workbench/storage.ts`), so the old `…:v2` key is never read again.

| Id | What to do | What to look for | Result |
|---|---|---|---|
| M1 | Windows secondary-slot default (`REQ-007` W17; constant `SHELL_HOME_SLOT_ID = 'secondary'` in `ts/src/workbench/useWorkbenchLayouts.ts`). Open DevTools, Application, Local Storage, `http://localhost:5180`, and delete every key starting `d-system:workbench-state`. Reload. Read the header of the slot at the left of layout 1 (top left, small downward triangle). Also run `curl.exe -s http://127.0.0.1:8010/api/v1/workbench/platform`. | The header reads **PowerShell** and the PowerShell panel is visible by default; the platform route reports `windows`. Linux result: the same slot reads **Terminal (bash)** (scenario A, no stored state: secondary is Terminal (bash), strip is Notes, primary is HTML Viewer, explorer is File Browser). The failure this check guards against: the slot id literal in the hook stopped matching, so the Windows default silently stopped applying and the header reads Terminal (bash) with no error. | |
| M2 | A real pre-migration browser profile. Use the browser profile you used with the workbench before the migration; it should still hold a key `d-system:workbench-state:v2` (check in DevTools, Application, Local Storage). Do not delete the key. Load `http://localhost:5180` with the current code. Watch the DevTools Console and look for a `role=alert` message on the page. Afterwards check Local Storage again. | No page error in the Console and no alert. Layout 1 defaults are shown (the header again reads PowerShell on Windows). The `…:v2` key is still there, untouched, and a new `…:v3` key has been written. Notes file choice and open HTML Viewer tabs are reset to defaults: this is the stated side effect of the version bump, not a fault. Linux result: scenario B, a v2 state seeded by hand (old slot ids, `active_layout: layout-1`, an `active_notes_file`) gave no page error, no alert, slots identical to no stored state, v2 key untouched, v3 key written. The agent never saw a v2 state captured from a live session, which is why this check is yours. | |

## 2. Terminal interaction API (`ADR-030`)

Source: [`ADR-030`](../04-decisions/ADR-030-terminal-interaction-api.md) (the input route near line 364;
the token file near lines 170 to 230 and 477) and the launch commands in
[the demo runbook](demo-runbook.md) ("Launch Command Reference", optional API paragraph).

Launch the backend with both flags. The second flag is `D_SYSTEM_TERMINAL_API=1`; the first stays
`D_SYSTEM_DEMO_TERMINAL=1`. The API mounts only when both are set and the server is a single process
(no `--reload`, no `--workers`).

| Window | Command |
|---|---|
| Backend, repository root | `$env:D_SYSTEM_DEMO_TERMINAL='1'; $env:D_SYSTEM_TERMINAL_API='1'; uv run uvicorn src.main:app --port 8010` |

Read the token path from the backend log line at start-up. Set up a reader in a third PowerShell window:

```
$tok = (Get-Content -Raw "$env:USERPROFILE\.d-system\terminal-api\<key>.token")
$h = @{ Authorization = "Bearer $tok" }
$api = 'http://127.0.0.1:8010/api/v1/demo/terminal/sessions'
Invoke-RestMethod -Uri $api -Headers $h
```

Open a CMD session in the page first (choose **CMD** in the slot header), so the list is not empty. The list
gives each session's `session_id` and `shell`.

| Id | What to do | What to look for | Result |
|---|---|---|---|
| T1 | ConPTY, **cmd**. Take the `session_id` of the CMD session. Inject a line with submit: `$sid='<id>'; $before=(Invoke-RestMethod -Uri "$api/$sid/output" -Headers $h).next; Invoke-RestMethod -Method Post -Uri "$api/$sid/input" -Headers $h -ContentType 'application/json' -Body '{"input":"echo api-cmd","submit":true}'`. Then read: `(Invoke-RestMethod -Uri "$api/$sid/output?after=$before&wait=5" -Headers $h).text`. Watch the CMD panel in the page at the same time. | The line `echo api-cmd` is executed (the shell prints `api-cmd`), which shows the carriage return that `submit: true` appends is accepted as end of line by ConPTY. Linux result: the POSIX pty accepts `\r` as end of line (`ICRNL`), confirmed in `phase-wbf-08`. Record if the command only appears typed at the prompt and does not run. | |
| T2 | ConPTY, **PowerShell**. Same as T1 with the PowerShell session id and `{"input":"Write-Output api-ps","submit":true}`. | `api-ps` is printed and the command ran, as in T1. Also note whether the read `text` contains extra escape sequences from PSReadLine around the echo (expected, not observed: the exact `data_base64` bytes are always returned, `text` may drop up to three leading bytes of a split character). | |
| T3 | Token file location. Run `Get-ChildItem "$env:USERPROFILE\.d-system\terminal-api"` and compare with the path printed in the backend log. | One `<key>.token` file under `%USERPROFILE%\.d-system\terminal-api\`, `<key>` being 16 hex characters. It is a plain file with no trailing newline. The file's contents are replaced on each backend restart. The token itself never appears in the log. Linux result: `~/.d-system/terminal-api/<key>.token`. | |
| T4 | Token file Windows protection. Run `icacls "$env:USERPROFILE\.d-system\terminal-api"` and `icacls "$env:USERPROFILE\.d-system\terminal-api\<key>.token"`. Also run `Invoke-RestMethod -Uri $api` with no `Authorization` header. | The permission lists name only your account, `SYSTEM` and `Administrators` (no `Everyone`, `Users` or `Authenticated Users`). The `0700` and `0600` modes the code sets have no effect on Windows, so the protection rests on the profile directory's default permissions; the ADR says this is unverified. The unauthenticated request returns `401` with error code `unauthorized`. Linux result: the directory is `0700`, the file `0600`, asserted by tests; the mode assertions do not run on Windows. | |

## 3. Bookmark categories with Windows paths (`ADR-029`, `phase-wbf-05`)

Source: [the bookmark session record](../03-sessions/SESS-2026-10-08-08-bookmark-category-surface.md)
("Outcome" and the adversarial review fixes) and [`ADR-029`](../04-decisions/ADR-029-bookmark-categories-and-batch-bridge.md)
(decision 2, the reference model). The page sends forward-slash paths, so the backslash and case checks
go straight to the routes. A category is one file under `<data root>\workbench\bookmarks\` (data root
`_data` unless `D_SYSTEM_DATA_ROOT` is set). Use the launch from the prerequisite section.

```
$b = 'http://127.0.0.1:8010/api/v1/workbench/bookmarks'
$ct = 'application/json'
Invoke-RestMethod -Method Post -Uri $b -ContentType $ct -Body (@{name='Win check'} | ConvertTo-Json)
```

That creates the category `win-check`. Delete the test categories at the end (B3 and B4 list the
commands) so no test files stay under `_data\workbench\bookmarks\`.

| Id | What to do | What to look for | Result |
|---|---|---|---|
| B1 | Add a file by a backslash path: `Invoke-RestMethod -Method Post -Uri "$b/win-check/entries" -ContentType $ct -Body (@{path='docs\04-decisions\ADR-029-bookmark-categories-and-batch-bridge.md'} \| ConvertTo-Json)` | Status `201`. The returned entry is stored with forward slashes (`docs/04-decisions/ADR-029-...`) and has status `present`. Linux result: a unit test pins that backslashes become forward slashes on write; Windows was not run. | |
| B2 | A path that differs only in case: `Invoke-RestMethod -Method Post -Uri "$b/win-check/entries" -ContentType $ct -Body (@{path='DOCS/04-Decisions/adr-029-bookmark-categories-and-batch-bridge.md'} \| ConvertTo-Json)`. Then `Invoke-RestMethod -Uri "$b/win-check"`. Also try `docs/.GIT/config` and `docs/_PRIVATE/x.md` with the same call. | The case-different path is accepted (Windows paths are case-insensitive, and the symlink check compares with `os.path.normcase`), is stored with the case you typed (case is preserved), and reads `present`. The code compares the stored text for duplicates exactly, so whether it is a second entry next to the B1 entry or a `409` is not stated anywhere: record which. The `.GIT` and `_PRIVATE` paths are refused with `400` (the private and internal segment check runs before the existence check, so a missing file still gives `400`): record the codes. Linux result: the wrongly-cased file is `404` (no such file), because Linux paths are case-sensitive. The segment checks are casefolded and unit-tested on Linux. | |
| B3 | A category named `con`: `Invoke-RestMethod -Method Post -Uri $b -ContentType $ct -Body (@{name='con'} \| ConvertTo-Json)`. Then `Get-ChildItem _data\workbench\bookmarks` (or the data root in use). Clean up: `Invoke-RestMethod -Method Delete -Uri "$b/con-category"`. Repeat with `nul`, then `com1` and delete each (`nul-category`, `com1-category`). | Status `201`; `category_id` is `con-category` and the display `name` is still `con`. The file on disk is `con-category.json`; no `con.json` exists. Linux result: the id rule appends `-category`; unit tests pin `is_valid_category_id` for `con` and `com1`. A failure here would be an error creating the file, or a hang. | |
| B4 | Files resolve present and missing on Windows. After B1, run `Invoke-RestMethod -Uri "$b/win-check"` and read each entry's `status`. Then rename the B1 file temporarily (`Rename-Item docs\04-decisions\ADR-029-bookmark-categories-and-batch-bridge.md x.md`), read the category again, and rename it back. Finally delete the category: `Invoke-RestMethod -Method Delete -Uri "$b/win-check"`. | `present` for the existing file, `missing` while it is renamed, `present` again after the rename back; nothing is pruned from the entries. No entry reads `excluded` (it would mean the normalised-path comparison rejected a normal Windows path). Linux result: tests cover `present`, `missing` and `excluded` resolution with nothing pruned; Windows was not run. Also check in the page: in the File Browser, open the **Bookmarks** section, open the category and the files list shows the same entries. | |

## 4. Content-fit contracts (`REQ-037`)

Source: [`REQ-037`](../06-requirements/REQ-037-workbench-content-fit-contracts.md), row `C10` (the CMD and
PowerShell fit is an owner check, and Linux evidence does not close it), the panel contract table
(`terminal-cmd` and `terminal-powershell` rows) and the finding "Terminal header does not wrap" in
"Measured state, 2026-10-08".

The check runs the live script against the running workbench. It needs Node, Playwright for Node (in
`ts\node_modules`, in the global `npm root`, or at the path in `FIT_PLAYWRIGHT_MODULE`) and a Chromium
that Playwright can launch. The tracked directory `_public\engine\trace` must hold more than twenty
`.html` or `.svg` files. Use the prerequisite launch (backend 8010, frontend 5180), then in a third window at the
repository root:

```
uv run python test/test_workbench_fit_contracts.py --live http://localhost:5180 --self-test --dump fit-windows.json
```

The full matrix takes about eight minutes. `--quick` keeps 1280x720 and 1024x768 only; `--panel
terminal-cmd` or `--panel terminal-powershell` restricts the run to one panel type.

| Id | What to do | What to look for | Result |
|---|---|---|---|
| F1 | Row `C10`: run the command above and keep the full output (the run exits non-zero while the known defects stand). Record the exit code, the totals line (rules passed and failed) and the number of panel cells. | Linux result for comparison: 100 panel cells (2 layouts, 9 panel types, every eligible slot, 4 sizes), 132 floating-surface measurements, 489 rules passed, 35 failed, exit 1. On Windows the totals will differ because the CMD and PowerShell terminals exist. Any finding not in the table under F3 is new. | |
| F2 | The `terminal-cmd` and `terminal-powershell` rows. In the output, find every line naming `terminal-cmd` or `terminal-powershell`. The rows are panel box (`fill`), header controls (`wrap`), session tabs (`scroll-x optional`), terminal screen `.xterm` (`fill(min-h=68) optional`) and scrollback `.xterm .scrollbar.vertical` (`scrollbar optional`). | The `.xterm` screen and the scrollback exist and pass (they are `optional`, present only where the shell is available). Linux result: both panels showed "is not available on this host", so the scrollback was reported as not exercised, by name, for both. Passing here closes that gap; a failure on `.xterm` or the scrollbar is new. | |
| F3 | Finding "Terminal header does not wrap". Look for findings on region `.stage-region__header` for `terminal`, `terminal-cmd` and `terminal-powershell`. Compare with the Linux list below. Also look at the page at 1280x720 and 1024x768 with the PowerShell panel in the primary slot: are the injection dropdowns cut off at the panel's right edge? | Linux result (the known defect): the header's injection controls are 410 px wide (437 px for PowerShell) in a box 393 px down to 307 px, and are cut off. Seen for `terminal` in the primary slot (layout 1 at 1280x720 and 1024x768, layout 2 at 1280x720 and 1024x768), `terminal-cmd` the same, `terminal-powershell` also at 1366x768. Each `wrap` finding comes with a `silent-clip` finding on the panel root. Record whether Windows shows the same list, a longer one or none. | |

## 5. HTML Viewer toggle label (`phase-wbf-18`, `REQ-012` R31)

Source: [`REQ-012`](../06-requirements/REQ-012-workbench-features-defects.md) row `R31` ("click the toggle
in the running viewer; confirm each statement matches what appears") and the HTML Viewer entry in
[the demo runbook](demo-runbook.md) ("Workbench UI Reference", HTML Viewer panel, Embedded / Open-in-tab
toggle). The owner has ruled that the label's "rung 3" will be renumbered to rung 7 in a later phase, so
the label text you see may read differently from the one quoted here.

| Id | What to do | What to look for | Result |
|---|---|---|---|
| V1 | In the running workbench select a page in the HTML Viewer (the overview is fine). The toggle button is at the far right of the viewer header. Click it, read the label and the panel, click it again. Reload the page. | Initial label **Embedded**: the page is shown inline in an iframe. After one click the label reads **Open-in-tab link (rung 3)** (or the renumbered rung), the iframe is replaced by a link "Open page in a new tab ↗" that opens the page in a new browser tab, and the button is pressed (`aria-pressed`). A second click returns to Embedded. The setting is one for the whole panel, not per tab, and a reload returns to Embedded. With no page selected the placeholder message shows in either mode and there is no link. Every sentence of the runbook entry must match what you see; note any that does not, including the ladder-number mismatch the runbook itself records (idea `000105`). Linux result: none; the click check was not run by an agent. | |

## 6. Terminal persistence audit (`phase-arch-16`)

Source: [the terminal persistence audit](terminal-persistence-audit.md), section 8 (owner-machine
checks), copied here with the wording tightened and no step or figure dropped. `REQ-011` R24 requires
these checks to be named. The audit's section 4.2 and 4.3 matrices have Survival cells that these checks
fill. The measurement script is appendix A of that audit (`node measure-terminal.js`).

### 6.1 Setup for every check

1. Launch the backend and the frontend with the prerequisite commands, both with
   `D_SYSTEM_DEMO_TERMINAL=1`. For the optional server-side session list also set
   `D_SYSTEM_TERMINAL_API=1` on the backend (`ADR-030`; the token path is printed in the backend log;
   Windows permissions on the token file are themselves unverified, see T4).
2. Start from a cleared browser store (delete the workbench key from Local Storage in DevTools, or use a
   fresh browser profile). A stale stored visible-panel choice is how the original `000107` measurement
   went wrong.
3. On Windows a fresh store shows **PowerShell** in the Terminal slot (`REQ-007` W17). The panel labelled
   **Terminal (bash)** is still offered in the slot header. Code reading, not observed: it is not refused
   on Windows; it is expected to start `cmd` (or the `D_SYSTEM_DEMO_SHELL` override) under the bash label
   (audit finding F13, check O11). Pick the shell under test in the slot header (**Terminal: choose a
   panel**), and use the **CMD** and **PowerShell** panels, not the bash panel, for the CMD and
   PowerShell columns.
4. Identity check, the equivalent of the bash `PID`/`MARKER` line. Type once, then repeat after the event:

   | Shell | Set once | Check after the event |
   |---|---|---|
   | CMD | `set MK=<new value>` | `echo %MK%` (a new shell prints `%MK%` literally) |
   | PowerShell | `$env:MK='<new value>'; $PID` | `"PID=$PID MK=$env:MK"` (a new shell prints a different `PID` and an empty `MK`) |

   Scrollback sentinel, to look for after the event by scrolling up: CMD
   `for /l %i in (1,1,300) do @echo line %i`; PowerShell `1..300 \| ForEach-Object { "line $_" }`.
5. In DevTools, Network, filter **WS**: every terminal socket is a row; a row that has ended shows as
   closed. Count the rows before and after each event. A new row during an event that should be
   survivable is a restart.
6. Process leaks: before opening any session, note the count of `cmd.exe`, `powershell.exe`,
   `conhost.exe` and `OpenConsole.exe` in Task Manager (Details tab, with the Command line column).
   Compare after each ending event.

### 6.2 Persistence events (O1 to O5 and O11)

For each of CMD and PowerShell, record the result. The "Look for" column gives what Linux bash did.

| Id | Event | Do | Look for (and what Linux bash did) | Result |
|---|---|---|---|---|
| O1 | Layout switch | Set the identity marker. (a) Switch layout 1, 2, 1 with the shell in the Terminal slot. (b) Assign the shell to **Main** in layout 1 and leave it in the Terminal slot in layout 2, and switch 1, 2, 1. (c) In layout 2 choose a different shell in the Terminal slot, return to layout 1, set the marker, switch to layout 2 and back. | Same marker and no new WS row in (a) and (b) (bash: survived both). In (c) a new shell and a lost marker (bash: ended, no message). Also whether anything on screen says so. | |
| O2 | Visible-panel switch | Open three tabs with distinct markers. In the slot header choose another shell, then choose the first one again. | Number of WS rows that closed (bash: all three), tabs after returning (bash: one), markers (bash: lost), any warning text before or after (bash: none). Task Manager: shells left behind. | |
| O3 | Re-assignment | Set the marker. Move the shell to **Main** with **Configure layout**; read the dialog; confirm. Then move **HTML Viewer** into the Terminal slot while the shell shows there: read the text, **Cancel**, check the marker, repeat and **Confirm**. | Moved shell keeps the marker with no new WS row (bash: kept); cancel leaves the session (bash: kept); confirm closes it (bash: closed). The dialog text should name the displaced panel and say the moved panel is not restarted. | |
| O4 | Collapse, drop, restore | Three tabs with markers and the sentinel lines, plus a long-running child (`ping -t 127.0.0.1` in CMD or PowerShell). `...` menu: Collapse, wait, Expand. Then Drop: read the confirmation, check nothing ended before **Confirm**, confirm. Restore. Close one tab by its **x** and confirm. | Collapse keeps markers, scrollback and the child (bash: kept). After Drop zero live WS rows, and no `ping.exe` or shell processes left in Task Manager (bash: foreground child ended). Restore: how many sessions start (bash: as many as there were tabs). | |
| O5 | Page reload | Marker, sentinel lines, `ping -t 127.0.0.1` running. Reload. Then also close the browser tab and reopen the URL. | All sessions new, one tab (bash: yes). The reload leaves no `ping.exe` or orphaned shell in Task Manager (bash: foreground and background jobs ended; `nohup` and `setsid` jobs, which have no direct equivalent, outlived it). Whether `Start-Process`-started programs outlive the shell, as the Windows analogue. | |
| O11 | Terminal (bash) panel on Windows | With the Terminal slot showing **Terminal (bash)** on Windows, type the identity check for each candidate (`echo %MK%` after `set MK=1`, then `$PSVersionTable` or `ver`) to learn which shell started. Repeat with `D_SYSTEM_DEMO_SHELL=powershell` set on the backend. Also open the panel's tabs and the CMD panel and compare. | Which shell the bash-labelled panel starts (expected from code: `cmd`, or the override) and whether any message says it is not bash. A refusal message "bash is not available on this host" would contradict the code reading in audit finding F13. | |

The audit also names two things in the Windows adapter (`src/demo/windows.py`) to watch in O4 and O5:
`read()` has no timeout and blocks until data or end of file, so a pump thread ends only when the shell does;
and `close()` ends the shell process with `terminate(force=True)`, which does not obviously end its children.

### 6.3 Performance measurements (O6 to O10)

| Id | Measurement | Do | Look for | Result |
|---|---|---|---|---|
| O6 | Connect latency | `node measure-terminal.js ws://127.0.0.1:<backend port> cmd`, then `powershell` (appendix A of the audit; needs Node 22 or later for the global `WebSocket`; the setup checklist asks only for Node 18, so check `node --version`). Also, in the page, time 10 clicks of **+ New session** to a visible prompt with a stopwatch or a screen recording. | `connect_ms.open`, `first_byte` and `last_byte_of_startup_output` for each shell. The script discards one warm-up connection, so its first sample is not the client's slow first connection. Expected, not observed: on Windows the first byte may be terminal setup sequences before the prompt, in which case `last_byte_of_startup_output` is the closer figure for "prompt ready"; a PowerShell profile may add to start-up. Like-for-like Linux bash baseline (this script, two runs, after its warm-up): open about 5 ms, first byte about 21 to 23 ms. The audit's section 6.1 tables came from a different run, warmed by an earlier HTTP request, and their medians are lower (3.2 ms open, 17.5 ms first byte, direct). | |
| O7 | Echo latency | The same script prints `echo_ms` (300 keystrokes). In the page, type into the shell under screen recording at 60 frames per second and count frames from key to character. | `median` and `p95`. Caveat (expected, not observed): the script counts the first byte after each key, which in PowerShell (PSReadLine) and ConPTY may be a redraw sequence rather than the character, so also report the page-level figure. Like-for-like Linux bash baseline (this script, two runs): echo median about 2.1 ms (the audit's 6.2 table, from a different run, has 1.8 ms); page-level 28 ms. | |
| O8 | Resize | With the shell showing, set the window to 1280 by 720, 1366 by 768, 1920 by 1080 and 1024 by 768. At each, CMD: `mode con`; PowerShell: `$Host.UI.RawUI.WindowSize`. Compare rows and columns with what the page shows. Then drag the window edge continuously for five seconds and release. | Reported size equal to the visible grid at each size (bash: equal at all eight layout and size combinations). After the drag, the final size is correct within a second (bash: 33 to 40 ms) and the screen has no duplicated or torn lines (expected, not observed: ConPTY may repaint on resize). | |
| O9 | Scrollback | Print 3000 numbered lines (CMD `for /l %i in (1,1,3000) do @echo %i`; PowerShell `1..3000`). Scroll to the top and read the first retained line number. Resize the window once and look again for repeated lines. Then flood: create a file with `1..200000 \| Out-File $env:TEMP\f.txt` and print it (`type %TEMP%\f.txt` in CMD, `Get-Content $env:TEMP\f.txt` in PowerShell) while timing to the last line, and note whether the page stays responsive (DevTools Performance, long tasks). | First retained line (bash: 1969 of 3002, a 1000-line scrollback), duplicated lines after resize, time to finish (bash: 254 to 526 ms for 200,000 lines), any page freeze. | |
| O10 | Six-session cap | Put PowerShell in the Terminal slot and CMD in **Main** (assign with the dialog). Open three tabs in each: six live. Click **+ New session** in either panel. Then free one tab and try again. Separately, with five live, click **+ New session** four times (closing the new tab each time) on the development server. | The seventh is refused with "Maximum of 6 concurrent terminal sessions reached" and the refused tab stays refused (bash: both). With five live, whether a free slot is ever refused (bash on the development server: 2 of 4 and 4 of 8). On the Linux development server a refusal is consistent with the doubled mount's first websocket still holding a slot when the second arrives (audit section 6.5); PowerShell is expected (not measured) to be slower to start and to end than bash, so this probe is the most likely to differ. | |

## Result sheet

Copy each outcome here when the tables above are filled. Write PASS, FAIL or NOT RUN, and put the
number, error text or one-line observation in Notes. For O1 to O10 and O11 write CMD and PowerShell
separately (and say whether each matches the bash column).

| Id | Source | Check | Result | Notes |
|---|---|---|---|---|
| M1 | `phase-arch-02` | Windows default: PowerShell in the secondary slot on a fresh store | | |
| M2 | `phase-arch-02` | Real pre-migration profile loads defaults with no page error | | |
| T1 | `ADR-030` | ConPTY inject with submit on cmd | | |
| T2 | `ADR-030` | ConPTY inject with submit on PowerShell | | |
| T3 | `ADR-030` | Token file location under the profile directory | | |
| T4 | `ADR-030` | Token file and directory permissions on Windows | | |
| B1 | `ADR-029`, `phase-wbf-05` | Backslash path stored with forward slashes | | |
| B2 | `ADR-029`, `phase-wbf-05` | Path differing only in case, and `.GIT` or `_PRIVATE` segments | | |
| B3 | `ADR-029`, `phase-wbf-05` | Category named `con` gives `con-category` | | |
| B4 | `ADR-029`, `phase-wbf-05` | Files resolve present and missing | | |
| F1 | `REQ-037` C10 | `--live` run on the owner machine | | |
| F2 | `REQ-037` | `terminal-cmd` and `terminal-powershell` rows | | |
| F3 | `REQ-037` | Terminal header does not wrap | | |
| V1 | `phase-wbf-18`, `REQ-012` R31 | HTML Viewer toggle matches the runbook entry | | |
| O1 | `phase-arch-16` | Layout switch (CMD / PowerShell) | | |
| O2 | `phase-arch-16` | Visible-panel switch (CMD / PowerShell) | | |
| O3 | `phase-arch-16` | Re-assignment (CMD / PowerShell) | | |
| O4 | `phase-arch-16` | Collapse, drop, restore (CMD / PowerShell) | | |
| O5 | `phase-arch-16` | Page reload (CMD / PowerShell) | | |
| O11 | `phase-arch-16` | Terminal (bash) panel on Windows | | |
| O6 | `phase-arch-16` | Connect latency (CMD / PowerShell) | | |
| O7 | `phase-arch-16` | Echo latency (CMD / PowerShell) | | |
| O8 | `phase-arch-16` | Resize (CMD / PowerShell) | | |
| O9 | `phase-arch-16` | Scrollback (CMD / PowerShell) | | |
| O10 | `phase-arch-16` | Six-session cap (CMD / PowerShell) | | |
