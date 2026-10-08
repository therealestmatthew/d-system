---
schema_version: 1
id: doc-workbench-features-defects-requirements
code: REQ-012
title: Workbench features and defects requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-10-08'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench-requirements, doc-workbench-terminal-decision, doc-workbench-api-decision]
---

# Workbench features and defects requirements

## Observed problem and scope

The workbench shipped in one week against a 2026-09-15 demo. `REQ-007` specified it, `ADR-014` and
`ADR-015` fixed its terminal capability and API posture, and the `phase-wb-*` track built it. Sixteen
ideas raised between 2026-09-10 and 2026-09-14 name what it does not yet do and what it does wrong —
discrete, mostly small, user-facing features and bugs, each on a different panel or route.

This is the sibling of [`REQ-011`](REQ-011-workbench-architecture-quality.md) and covers the other
kind of work on the same product. `REQ-011` covers the workbench's vocabulary, structural model,
audits and performance. This one covers features and defects: the HTML Viewer's remaining
interactions, file bookmark categories and the panel-bridge contract they need, the notes-strip
rotator's two variants, an external terminal interaction API, and four defects on the terminal route
and its frontend.

It does **not** cover panel maximize. `000233` was raised on the HTML Viewer but ruled into `P10`'s
`G43` as `phase-arch-17` by [`PLAN-028`](../01-plans/PLAN-028-workbench-architecture-quality.md)
design decision 5, because the mechanism is slot geometry rather than a viewer feature. No row below
covers it, and no `phase-wbf-*` phase implements it.

### Already delivered — no rows, no phases

Six of the sixteen ideas were resolved before this requirement was written. They carry **no rows in
the table below**, deliberately: a row that maps to no phase would break this document's own coverage
property. They are recorded here so the next reader does not re-specify them.

| Idea | What it asked | Where it landed | Verified |
|---|---|---|---|
| `000119` | Decide where markdown-to-HTML rendering happens | Route-side, in `serveRepositoryFiles` (`ts/vite.config.ts`), commit `593597e`. The ruling in `_tmpagent/viewer-render-location-ruling.md` is consumed | `marked` imported at `ts/vite.config.ts:6`; rendering at the `/workbench-file/` route, so panel and new-tab open resolve to the same output |
| `000110` | Render markdown with formatting, not raw source | Same commit; `.md` added to the viewer's compatible list. The `marked` dependency's `npm install` prerequisite is recorded in the runbook (`bdd1aa0`) | `.md` present at `ts/src/stage/HtmlViewerRegion.tsx:29` |
| `000232` | Support the six already-served image formats | Commit `6896efc`, plus a fitted centred wrapper document (`2e35ae7`) and a `?raw=1` discriminator serving image bytes to sub-resource requests (`71cc841`) | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.ico` at `HtmlViewerRegion.tsx:30-35` |
| `000118` | Grow `COMPATIBLE_EXTENSIONS` once rendering lands | Same batch, in the order the idea sequenced. The single-list property held: the File Browser's context action followed for free | `FileBrowserRegion.tsx:4` imports the constant and reads it at line 500 |
| `000099`, `000129` | Fix the three red PTY tests | Fixed before this programme was planned; 46 demo-terminal tests pass and the full suite is green | `uv run pytest` |

`000232`'s one open question — whether bare-image iframe presentation was acceptable or an image
needed wrapping — was **answered in the build, not deferred to planning**: images are wrapped, and
the answer is the same for all six, as the idea required. Nothing remains for this requirement to
settle.

`GET /api/v1/workbench/search` was already extension-agnostic — it takes `ext` from the caller
(`src/api/routes/workbench.py:439`) — and needed no change for any of the above.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | Double-clicking a file tab in the HTML Viewer opens that file in a new browser tab, as a full page outside the workbench iframe, showing the **same rendered output** the panel shows — rendered markdown for `.md`, the wrapper document for an image, not raw source. | Double-click a tab holding each of `.html`, `.md` and one image format; confirm a new browser tab opens and its content matches the panel's. Raw markdown source in the new tab is the defect `000119` existed to prevent and is a failure. |
| R02 | A file opened this way carries the same sandbox posture as the panel: the response sets `Content-Security-Policy: sandbox`, so a top-level navigation inherits the iframe's restrictions. | Read the response headers on the new-tab URL. Confirm the header is present with no tokens. Confirm no code path bypasses `serveRepositoryFiles` to reach the file. |
| R03 | The HTML Viewer's header shows when the displayed file was last modified, readable without opening dev tools. | Load a file into the viewer, read the badge, and compare it against the file's `mtime` on disk. A badge showing page-load time rather than file time is a defect. |
| R04 | The badge tracks what is displayed: switching tabs updates it to the newly displayed file, and re-selecting a file that changed on disk shows the newer time. | Switch between two tabs holding files with different `mtime`s and confirm the badge changes. Regenerate the overview page, re-select it, and confirm the badge advances. |
| R05 | An accepted ADR records the bookmark-category model: the storage shape (a tracked `_data/` entity versus browser storage, with the choice argued rather than asserted), the reference model by which a category is named elsewhere, and how file paths stay valid as the repository moves. | Read the ADR for all three. A storage choice with no argument against the alternative is a defect — `000111` names both candidates and states only a leaning. Confirm governance exits 0. |
| R06 | The ADR states how a category is consumed as a set by more than one surface, naming the surfaces, and states the consequence for the panel bridge that `R07` then implements. | Read the ADR for named consuming surfaces and an explicit statement of the batch requirement. A model that describes only the grouping half leaves `000111`'s second half undesigned. |
| R07 | The panel bridge supports a batch, multi-target action: one invocation delivers N files to one or more registered targets. No second, parallel bridging mechanism is introduced. | Invoke a batch action with N files and confirm all N arrive. Grep `ts/src/stage/` for a file-passing path that does not go through `panelBridge.ts`; one is a defect, and is the duplication `000115`'s audit exists to catch. |
| R08 | Extending the bridge preserves its existing degradation contract: an action with nothing registered reads null and disables — it never throws and never queues. | Invoke a batch action with no target registered and confirm the action is disabled rather than raising. Invoke with a partial set of targets registered and confirm the stated behavior, whatever the ADR chose, is what happens. |
| R09 | The owner can create, rename and delete named bookmark categories, and add and remove files within one, and list a category's files. | Exercise each of the six operations through the UI and confirm the stored representation changes as `R05` specifies. |
| R10 | Referencing a category pulls up its files as a set, through `R07`'s batch action — not by opening the first file only. | Reference a category holding at least three files and confirm all three open. Opening one is the silent degradation `000120` predicted and is a failure. |
| R11 | A category naming a file that has moved or been deleted degrades legibly: the category still opens, the missing entry is identified by path, and nothing raises. | Delete a file named by a category, reference the category, and confirm the remaining files open and the missing one is named in the UI. |
| R12 | A notes-strip entry too long for the panel scrolls horizontally right to left rather than truncating or overflowing, and pausing is possible so a reader can finish it. | Place an entry longer than the panel width and confirm it scrolls rather than clipping. Confirm the stated pause interaction works. Confirm `REQ-006` R02's zero-scroll obligation still holds on the page. |
| R13 | The interaction between rotating *between* entries and scrolling *within* one is stated and implemented — an entry is not rotated away mid-scroll unless that is the stated choice. | Read the implementation for an explicit rule. Observe a long entry through a full rotation cycle and confirm the observed behavior matches the stated rule. |
| R14 | The rotator can rotate image entries as well as text, with a stated sizing rule inside the small panel, and a stated ruling on whether text and image entries may mix in one rotation. | Configure an image rotation and confirm images are sized per the stated rule rather than overflowing the panel. Read the ruling on mixing; an unstated answer is a defect, whichever way it is ruled. |
| R15 | An accepted ADR covers the external terminal interaction API before it is built: its gating (its own flag or the existing one), loopback binding, session identity, authentication if any, output buffering depth, and whether sessions outlive their websocket. | Read the ADR for a decision on each of the six. `ADR-013` set the precedent that a shell capability beyond the demo stage starts from its own decision record; an implementation preceding this ADR is a defect. |
| R16 | The ADR states its relationship to `ADR-014`, which already absorbed `000087`'s session-registry half, and scopes itself to the remaining inject/read surface rather than re-deciding what `ADR-014` settled. | Read the ADR for an explicit statement of what `ADR-014` already owns. A duplicate session registry is the failure this row exists to prevent. |
| R17 | A flag-gated HTTP endpoint injects input into a named live shell session, and the injected text reaches that session's shell. | Open a session, inject a command over HTTP, and confirm the shell executes it. Confirm injection into an unknown session id is refused with a structured error rather than creating one. |
| R18 | A flag-gated HTTP endpoint reads buffered output from a named session **without stealing bytes from the websocket pump** — the browser attached to the same session loses nothing. | Attach a browser, read over HTTP, and confirm the browser's own output is complete. Adapter reads are destructive (`src/demo/adapter.py`), so a naive read is the defect; confirm a broadcast buffer sits between them. |
| R19 | With the API's flag unset, its routes are absent — no partial exposure, no route that authenticates but does nothing. | Start with the flag unset and confirm each route returns 404. Confirm no session-registry side effect occurs on a flag-off request. |
| R20 | Two connections racing the session cap cannot both pass it: the registry slot is reserved before `await websocket.accept()` and released on failure. | Read `src/api/routes/demo_terminal.py` and confirm the reservation precedes the accept — the check at line 287 and the accept at line 313 are today separated by an await. Drive concurrent connect storms at the boundary. The race was never reproduced under the asyncio scheduler, so **the code reading is the verification**, not the storm. |
| R21 | A global-cap refusal reaches the browser as a structured close frame carrying a quotable reason, not as `CloseEvent` code 1006 with an empty reason, and the panel displays that reason. | Fill the cap, attempt one more connection, and read the `CloseEvent` in the browser. Confirm the code and reason are the structured ones and that the panel quotes the reason rather than a generic message. The current code closes before `accept()` (line 288), which uvicorn converts to an HTTP 403 handshake rejection. |
| R22 | The interaction between the `D_SYSTEM_DEMO_SHELL` operator override and a client's per-session shell selection is no longer silent: it is either documented in the demo terminal OPS document, or changed so the override applies only when no explicit shell is requested. The choice is stated with its reason. | Set the override, request `shell=bash`, and confirm the observed behavior matches what the document says happens. A behavior the document does not describe is the defect, whichever behavior was chosen. |
| R23 | With `D_SYSTEM_DEMO_TERMINAL` unset, loading the workbench produces no 404 console entries, and the existing correct degradation is unchanged — disabled dropdowns, the absent-terminal message, no uncaught exceptions. | Load with the flag unset and count 404 entries in the browser console; four were measured in `phase-wb-03`, and the target is zero. Confirm the three degradation behaviors still hold, so silencing the probes did not silence the feature. |
| R24 | An unprovoked drop of a terminal session has a stated cause found by reproduction. A diagnosis note says, for each candidate cause, which side closed the socket, with what close code and reason, after how long, whether the shell process survived, and whether the panel opened a second session or only showed its closed message. A cause that could not be reproduced is stated as such, with each candidate ruled out and the measurement that ruled it out. A test in the suite exercises the closing path found. | Read the note for the five facts per candidate. Run `uv run pytest test/test_demo_terminal.py` and confirm the new test fails against the behaviour the note blames (or, where the diagnosis found no fault, that it pins the ruled-out behaviour). A cause asserted without a reproduction is the guess `000246` says the diagnosis exists to avoid. |
| R25 | The HTML Viewer's file selector shows at least eight entries at once, in a popup that opens on the side with more room and scrolls inside for a longer list. The shared popover no longer applies a fixed 120 px height floor that exceeds the room on its chosen side, and its dismiss control stays inside the viewport. | In a directory with more than twenty compatible files, open the selector at 1280x720 and 1024x768 in both layouts and count the fully visible entries: eight or more. Scroll the list to its end. Confirm the dismiss control is on screen (`REQ-006` R03). Two entries visible is the defect `000108` reported. |
| R26 | Every consumer of the shared popover is accounted for in an audit note that gives its measured bubble height at 1280x720 in both layouts and an outcome: content fully shown, fixed by the shared change, or a recorded reason it cannot be. | Run `grep -rl "from '.*Popover'" ts/src` (nine hits on 2026-10-08) and compare the consumers with the note's rows. The audit measures only consumers reachable in the stock layouts. A consumer missing from the note is a failure, which is the sibling bug `000117` warned would otherwise resurface as a fresh report. |
| R27 | Hovering the `?` tooltip in the notes strip shows the whole tooltip text inside the viewport rather than cut off at the strip's bottom edge, and the tooltip still collapses when the pointer leaves it (`REQ-006` R03). The same holds for every other tooltip consumer (the terminal panel and the overview panel). | At 1280x720 and 1024x768 in both layouts, hover each tooltip trigger and compare the bubble's bounding box with the viewport and its text height with its scroll height. Move the pointer away and confirm the bubble is gone. Confirm `REQ-006` R02 zero page scroll still holds. |
| R28 | When a folder's listing fails to load after the user has browsed to it from another folder, the File Browser shows its could-not-search message, not "Loading…", and a later successful browse replaces the message. While a listing is pending, the panel still shows "Loading…" and builds no tree from another folder's entries. | In a vitest test, answer the first folder's request with a list and the second's with a server error, browse to the second, and expect the alert message. Run a second case where the second request is still pending and expect "Loading…" and no entries from the first folder. |
| R29 | With `D_SYSTEM_DEMO_TERMINAL` unset in the frontend process, an HTML Viewer tab holding a persisted file selection shows the absent-page message and does not frame the application shell. With the flag set, the same selection renders as before for `.html`, `.md` and image files. | Run the dev server on a free port with the flag unset, store a viewer tab naming an existing file, load the page, and read the panel: absent-page text and no iframe loading the app's `index.html`. Repeat with the flag set and confirm the file renders. A panel reading "ready" over the app shell is the defect `000555` records. |
| R30 | A terminal session that fails to start (the backend accepts, then closes with the startup-failure code and its reason) shows that reason in the panel. A session that ran and was closed by the idle bound or by the shell exiting still shows the generic closed message. | In a vitest test, use a stub socket that opens and closes with the startup-failure code and reason, and expect the reason on screen; repeat with an ordinary close and expect the generic message. Run `uv run pytest test/test_demo_terminal.py` to confirm the backend half of `000573` still holds. |
| R31 | The demo runbook's HTML Viewer entry names the header toggle by both of its labels ("Embedded" and "Open-in-tab link (rung 3)"), says what each state shows, says how to switch back, and states which descope-ladder rung the control is. No wording contradicts the control's behaviour in `HtmlViewerRegion.tsx`. | Read the entry beside `ts/src/stage/HtmlViewerRegion.tsx` and click the toggle in the running viewer; confirm each statement matches what appears. A presenter who clicks the control mid-demo must be able to explain and reverse it from the script (`000105`). |
| R32 | A websocket connection to the demo terminal route whose `Origin` header is present and is not an `http` or `https` origin on `localhost`, `127.0.0.1` or `[::1]` (including the literal `null`) is closed with a structured refusal (close code 4004 and a fixed reason that quotes no header value) before any shell is started or any cap slot is reserved. A connection with no `Origin` header, or a loopback one, behaves as before: same cap, same shell selection, same session semantics. With `D_SYSTEM_DEMO_TERMINAL` unset the route and the check do not exist. | A pytest opens the websocket with each of these. Refused with 4004 and the fixed reason (which names `D_SYSTEM_WORKBENCH_ORIGIN` as the remedy), adapter factory uncalled, `SESSIONS` and `RESERVED` unchanged: `http://evil.example`, `http://evil.example:80`, `http://localhost.evil.example`, `http://127.0.0.1.evil.example`, `http://localhost@evil.example`, `null` and an empty-string `Origin`. Connects with a working shell: no `Origin`, `http://localhost:5180`, `http://127.0.0.1:5180`, `http://[::1]:5180` and an upper-case scheme or host (the parser uses `urlsplit` and compares the host, not a prefix). With `D_SYSTEM_WORKBENCH_ORIGIN=http://localhost:5180` set, another loopback origin gets 4004, the exact origin connects and an absent `Origin` connects. Fill the cap and confirm a non-loopback `Origin` gets 4004, not the cap refusal. Confirm the success, cap-refusal, shell-refusal and Origin-refusal paths each accept the connection once. In vitest, expect the panel to quote the reason on a 4004 close. A refusal that arrives after the shell has started is the defect idea `000669` and `ADR-030` open item 7 describe. |
| R33 | The HTML Viewer and overview panel toggles read "Embedded" in the embedded state and "Open-in-tab link (rung 7)" in the open-in-tab state, matching the descope ladder in the demo runbook, which lists that fallback as rung 7. The toggle stays visible, and the runbook entry, the owner-machine checklist and this document quote the new label as the current one. | In vitest, click each toggle and expect the new label and the "Open page in a new tab" link. Run `grep -rn "Open-in-tab link (rung" ts/src docs/00-working/demo-runbook.md docs/00-working/owner-machine-checklist.md docs/06-requirements` and confirm every hit reads rung 7. Compare the label with the runbook ladder. A label whose number disagrees with the ladder a presenter reads from is the defect idea `000670` records. |
| R34 | A decision record states how terminal sessions are preserved across a visible-panel switch and a layout switch, and answers six questions with a decision each: the server-side session lifetime independent of a websocket, the identity a returning page presents, the output kept while no page is attached, the interaction with the six-session cap, what the panel switcher and the layout switch do in the browser, and what changes for CMD and PowerShell. It names one recommended option, argues the alternatives against, states its effect on `ADR-014` decision 4, `ADR-030` open item 3 and `ADR-031` decision 7, and has frontmatter status draft with a Status section saying proposed, awaiting the owner's ratification. Warn-and-confirm is not offered as an option. No fix is built by this record. | Read the record for six decisions, one recommendation and a rejected-alternatives section. Search it for the three named decisions and confirm each is addressed. Confirm the Status section says proposed and awaiting ratification, and that `git diff` for the phase touches no file under `src/` or `ts/`. A record that leaves a question open without saying so, or that recommends warning before ending a session, is the defect. |

**`R14`'s mixing ruling (owner, 2026-10-08).** A rotation is all text or all images; mixing is not
allowed. A notes file that lists `points` and names an `imageDirectory` is rejected with a message
before the directory is read. `phase-wbf-06` built the rotator on that ruling, idea `000647` asked
for it to be recorded here, and the owner ratified it on 2026-10-08 (`GOV-003`).

## Amendment, 2026-10-08: seven phases for uncovered defects

The owner decided on 2026-10-08 to amend the features plan with phases for the workbench defect
ideas that no phase covered, so they can be built in the same run. Rows `R24` to `R31` cover them;
each maps to one new phase in [`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md)'s
*Amendment* section. The sixteen ideas this document was written for are unchanged.

The scan found eleven candidate ideas. Four were checked against the code on this branch and
dropped or narrowed, because the defect no longer reproduces:

| Idea | Finding | Where verified |
|---|---|---|
| `000556` | Fixed. The Idea Explorer's status list holds all nine schema statuses, and a test compares it with the schema enum | `ts/src/stage/IdeaExplorerRegion.tsx:23-33`; `test/test_workbench_api.py:555` |
| `000516` | Fixed. The queue precedence map holds all nine statuses, including `set_aside`, and a test compares it with the schema enum | `src/api/routes/workbench.py:507-517`; `test/test_workbench_api.py:550` |
| `000463` | Fixed. The workbench ranking is the `000516` row above, and the two consumers outside the workbench now read the status list from the schema | `tools/overview_metrics.py:47`; `src/orchestrator/state.py:72` |
| `000573` | Narrowed. The backend half is fixed. The panel's missing reason is `R30` | `src/api/routes/demo_terminal.py:354-366`; `ts/src/stage/TerminalRegion.tsx:243-250` |

No row covers the three fixed ideas. They remain `triaged` in the log; closing them is the idea
lifecycle's work, not this document's.

## Amendment, 2026-10-08 (second): three owner-ruled follow-ups

The owner ruled on 2026-10-08, after the first amendment, on three further items. Rows `R32` to
`R34` cover them; each maps to one new phase in
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md)'s second *Amendment* section.

| Row | Idea | What the owner ruled |
|---|---|---|
| `R32` | `000669`, `000614` | The demo terminal websocket checks a token or an `Origin` on connect, closing `ADR-030` open item 7; the plan builds the `Origin` branch |
| `R33` | `000670` | The HTML Viewer toggle label's "rung 3" becomes "rung 7" to match the runbook's ladder; the toggle stays visible |
| `R34` | `000671`, `000651`, `000652`, `000107`, `000087` | Sessions are preserved across panel and layout switches instead of the user being warned; a decision record comes before any fix |

`R31` quotes the old label. Its text is updated by `phase-wbf-20` when the label changes, not by
this amendment, because until then the label still reads rung 3.

## Out of scope

- **Panel maximize (`000233`)** — `P10`'s `phase-arch-17`, per `PLAN-028` design decision 5.
- **The workbench's vocabulary, structural model, audits, caching and performance** — `REQ-011`.
- **A terminal session registry** — `ADR-014` owns it; `R16` exists to keep this programme from
  building a second one.

## Traceability

Every row maps to at least one phase, and every `phase-wbf-*` phase carries at least one row. The
mapping table lives in
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md)'s *Requirement coverage* section
rather than here, so the phase list and its coverage stay in one document.
