# Demo Runbook — Live Segment

Live-segment rehearsal and performance runbook for the skills-and-agents training demo, 2026-09-15.
This is an ungoverned working document (ADR-010); it is updated with rehearsal results and used as
the performance checklist on demo day. The runbook describes the final workbench UI (REQ-007 W13).

## Descope Ladder

Applied in order when time runs short; each rung is independent of the ones below it:

1. Priority-queue views drop from the Idea and Backlog explorers (standard view only).
2. The File Browser context menu reduces to reveal-in-explorer and open-in-HTML-Viewer.
3. The HTML Viewer loses tabs — one directory/search context.
4. The Idea and Backlog explorers drop; the explorer slot holds the File Browser only.
5. Layout 2 drops — one layout ships, the engine and configuration surface stand.
6. The notes-file picker drops — the strip reads the fixed current file.
7. Embedded HTML Viewer falls back to an open-in-tab link or a side-by-side external browser.
8. Embedded terminal falls back to a side-by-side real terminal.

## Dry-Run Rehearsals

Record timings for two timed passes of the live segment. Each step carries an explicit timebox;
per-step times sum to at most 15 minutes. Stopping the timer and re-running `uv run python
tools/demo_reset.py restore` is the fallback action named in the runbook for every step.

The two passes below are owner-driven timed rehearsals against the final workbench UI; the result
gates the live demo per PROMPT-017 and REQ-007 W13.

### Dry-Run 1 — Owner-driven timed pass against final workbench UI

Date/time: `__DATE_TIME_1__`

| Step | Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | Precondition: verify ports 8010 and 5180 are free — `ss -tlnp \| grep -E "8010\|5180"` should print nothing. Then: start the backend with `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010`; start the frontend with `cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort`; open http://localhost:5180. **Check the terminal slot's header** (top left, small downward triangle): on a fresh store it defaults to the host platform's working shell — "PowerShell ▾" on the presentation machine (Windows), "Terminal (bash) ▾" elsewhere. A persisted browser choice can override that, so confirm rather than assume; to change, click the header and pick the wanted shell from the switcher list it opens ("Terminal: choose a panel"). Start a Claude Code session in the terminal by running `claude`. Review the workbench interface: notes strip at top right with `?` tooltip at far left and dropdown menu; terminal panel on the left with ellipsis menu in top right (Collapse and Drop/restore) and its own header dropdown — a switcher over the shells assigned to the slot (Terminal (bash), CMD, PowerShell by default); injection dropdowns (Commands, Skills, Prompts, Agents) below the terminal header; layout-configuration button ("Configure layout") at top right; HTML Viewer panel and explorer slot (File Browser visible first, with Idea Explorer and Backlog Explorer in the header dropdown) on the right. | 1m | __ACTUAL_1__ | "This is the d-system workbench — where this project actually gets worked on. Terminal on the left runs a live Claude Code session. Top right is a notes strip, out of the way until I need it — it's what's cueing me right now. On the right, a viewer for generated pages and a browser over the repository itself. The dropdowns next to the terminal hand an agent an exact command or prompt without me typing it out." |
| /idea | Type `/idea <the idea in prose>` in the Claude Code session (not a browser form or API call); wraps `tools/append_idea.py`. If no audience idea, skip to pre-seeded fallback. | 2m | __ACTUAL_2__ | "Let's capture something live. Give me an idea — anything you'd want this system to do." [take an audience suggestion, or use the pre-seeded fallback] "I type `/idea` and the idea in plain language, right here in the terminal. That's it — no form, no dialog. It's written straight into the project's permanent idea log." |
| /idea-triage | Type `/idea-triage` in Claude Code to scout and triage the recorded idea. **`/idea-triage` triages the entire open backlog, not just this one idea** — after the captured idea's subagent reports back, the session announces it will continue to the next open idea, and continue through the rest. **Fallback (always follow this):** as soon as the captured idea's subagent reports back and the finding is recorded, interrupt with `Ctrl-C` (not `Escape` — it does not stop the queued continuation) before the session moves to the next backlog idea. | 2m | __ACTUAL_3__ | "Now I hand that idea to an agent to scout — `/idea-triage`. It reads the idea, searches the repository for related plans and prior decisions, and records what it finds directly on the idea. Every idea gets this same pass before anyone acts on it." [as soon as this one idea's finding is recorded, hit Ctrl-C before it moves to the next backlog idea] |
| plan beat | Narrate the planning stage (no live CLI execution). | 3m | __ACTUAL_4__ | "From here the normal path is: requirements, then an implementation plan, then a backlog phase an agent can claim and build against — I won't run that live, it's a longer loop, but that's the chain a triaged idea travels." |
| overview-skill rebuild | Invoke the `d-system-overview` skill live to rebuild the overview — this is the step's point: `demo_reset.py prepare` deliberately parks the pre-built skill so this rebuild is real, not a replay. Fallback command if skill invocation unavailable: `uv run python tools/generate_overview.py`. Full fallback: `uv run python tools/demo_reset.py restore` then invoke the now-restored skill. Wait for page generation. Verify the HTML Viewer displays the generated overview (will already be open in the visible tab). | 4m | __ACTUAL_5__ | "Now let's generate a live report. I'm invoking the `d-system-overview` skill from the Skills dropdown — it rebuilds this project's status page from what's on disk right now, not a cached copy." [select the skill, Enter, wait] "While that runs — the panel on the right is already pointed at where it lands." |
| test | In the HTML Viewer, click refresh to reload the page and verify the generated overview displays current data. Verify the terminal panel remains interactive (type a quick command or test the session tabs). Close the demo by returning the interface to its pre-demo state. | 3m | __ACTUAL_6__ | "Refresh — there's today's data, generated during this session." [click refresh] "And the terminal underneath is still live." [type a quick command] "One idea, captured and triaged, fed into a report regenerated live — same terminal driving all of it." |
| **Total (all steps)** | | **15m** | __TOTAL_1__ | |

### Dry-Run 2 — Owner-driven timed pass (screen-recorded)

**This pass is screen-recorded.** Screen recording path on presentation machine: `__RECORDING_PATH__`

Date/time: `__DATE_TIME_2__`

| Step | Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | Precondition: verify ports 8010 and 5180 are free. Then: start the backend with `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010`; start the frontend with `cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort`; open http://localhost:5180. Check the terminal slot's header (top left): the fresh-store default is "PowerShell ▾" on Windows and "Terminal (bash) ▾" elsewhere; if a persisted browser choice has a different panel showing, switch via the header's switcher list ("Terminal: choose a panel"). Start a Claude Code session in the terminal by running `claude`. Review the workbench interface. | 1m | __ACTUAL_1__ | "This is the d-system workbench — where this project actually gets worked on. Terminal on the left runs a live Claude Code session. Top right is a notes strip, out of the way until I need it — it's what's cueing me right now. On the right, a viewer for generated pages and a browser over the repository itself." |
| /idea | Type `/idea <the idea in prose>` in Claude Code. | 2m | __ACTUAL_2__ | "Let's capture something live. Give me an idea." [take an audience suggestion, or use the pre-seeded fallback] "I type `/idea` and the idea in plain language — written straight into the project's permanent idea log." |
| /idea-triage | Type `/idea-triage` in Claude Code. Interrupt with `Ctrl-C` as soon as the one captured idea's finding is recorded — the command otherwise continues into the rest of the open backlog. | 2m | __ACTUAL_3__ | "Now I hand it to an agent to scout — `/idea-triage`. It searches the repository for related plans and prior decisions and records what it finds directly on the idea." [Ctrl-C as soon as this idea's finding is recorded] |
| plan beat | Narrate the planning stage. | 3m | __ACTUAL_4__ | "From here the normal path is requirements, then a plan, then a backlog phase an agent can claim — I won't run that live, but that's the chain a triaged idea travels." |
| overview-skill rebuild | Invoke the skill live; fallback is `uv run python tools/generate_overview.py` or full fallback `uv run python tools/demo_reset.py restore` + skill invoke. Verify the HTML Viewer displays the overview. | 4m | __ACTUAL_5__ | "Now let's generate a live report. I'm invoking the `d-system-overview` skill from the Skills dropdown — it rebuilds this project's status page from what's on disk right now, not a cached copy." [select the skill, Enter, wait] |
| test | Refresh HTML Viewer; verify terminal interactivity; return interface to pre-demo state. | 3m | __ACTUAL_6__ | "Refresh — there's today's data, generated during this session." [click refresh] "And the terminal underneath is still live." [type a quick command] "One idea, captured and triaged, fed into a report regenerated live." |
| **Total (all steps)** | | **15m** | __TOTAL_2__ | |

## Agent-Driven Rehearsal Passes (fresh-eyes mechanics checks)

These are NOT the owner-driven timed dry-runs above and do not close REQ-006 R09's deferred
conditions — R09 closes only on the owner's own recorded passes in the Dry-Run tables above.
These two agent-driven passes (`demo-validator-web`, pack W07-R) are mechanics checks run early
to catch runbook and tooling defects against the final workbench UI, dispatched by
demo-orch-content and separated by `uv run python tools/demo_reset.py prepare`.

### Agent-Driven Pass 1 — 2026-09-11, fresh-eyes rehearsal (W07-R), agent demo-validator-web

Ran before the runbook's `/orient`-step `claude`-session fix below; the /idea and /idea-triage
CLI halves were exercised directly via `tools/append_idea.py` and an open-idea listing rather
than through the embedded terminal, because the terminal opened to plain bash at the time (see
Rehearsal Findings).

| Step | Timebox | Actual (AGENT-DRIVEN) | Pass/Fail | Notes |
|---|---|---|---|---|
| /orient | 1m | ~85s | Fail against timebox | Mostly cold-start latency (uvicorn + vite boot) plus mechanical verification of every control; a presenter starting the stack before the audience arrives would not experience this as one live minute. Both launch commands worked verbatim. |
| /idea | 2m | CLI half: 3.97s (`append_idea.py add`, idea 000102) | Pass (CLI half only) | Live-Claude-Code-REPL half not independently measurable by an agent barred from a nested interactive session — see Rehearsal Findings item 1. |
| /idea-triage | 2m | CLI half (open-idea listing): ~0.06s | Pass (CLI half only) | The `/idea-triage` subagent-dispatch half is not independently measurable by this agent, same restriction as phase-demo-05's rehearsal. |
| plan beat | 3m | N/A — narration only | N/A | Nothing to mechanically verify. |
| overview-skill rebuild | 4m | Fallback command: 0.62s (`generate_overview.py`) | Pass (fallback path only) | Skills dropdown correctly omitted `d-system-overview` while `demo_reset.py prepare` had it parked, confirming the parked-skill design. Live skill-dispatch-via-terminal half blocked by the same terminal finding. |
| test | 3m | ~16s | Pass | Refresh confirmed via iframe idea-count change (101→102); terminal interactivity confirmed via echoed command; `demo_reset.py restore` completed in 0.69s. |
| **Total (CLI-executable/mechanical steps measured)** | **15m** | **well under 15m** | Partial | Not comparable to the owner's 15m budget — the live-REPL portions of /idea and /idea-triage, which consume most of their timeboxes in a real demo, were not exercised. |

### Agent-Driven Pass 2 — 2026-09-11, fresh-eyes rehearsal (W07-R), agent demo-validator-web

Run against the runbook as fixed by the pass-1 findings (the `/orient` step's `claude`-in-terminal
instruction). `uv run python tools/demo_reset.py prepare` ran cleanly (0.43s) before the pass; both
launch commands worked verbatim.

| Step | Timebox | Actual (AGENT-DRIVEN) | Pass/Fail | Notes |
|---|---|---|---|---|
| /orient | 1m | ~232s (≈3m52s), ~10s of which is server cold start | Fail against timebox | Blocking finding inside this step — see Rehearsal Findings item 4. Layout, control inventory and zero-page-scroll otherwise matched the runbook exactly (terminal left, notes strip top right, HTML Viewer + File Browser default on the right, Idea/Backlog Explorer behind the header dropdown). |
| /idea | 2m | N/A — no audience idea; skipped straight to the pre-seeded fallback per the step's own instruction | N/A | Pass (fallback path exercised as designed). |
| /idea-triage | 2m | ~115s to complete triage of one idea (000087), after the agent intervened to stop broader scope | Fits, for a single idea | Pass with a major finding — see Rehearsal Findings item 5. Left uninterrupted, this step does not do what the runbook narrates. |
| plan beat | 3m | N/A — narration only | N/A | Nothing to mechanically verify. |
| overview-skill rebuild | 4m | Skills dropdown check: instant. Fallback command `generate_overview.py`: 0.38s | Pass | Skills dropdown correctly listed only `_parked`, `checkpoint`, `orient` — `d-system-overview` absent while parked, confirming the parked-skill design (same as Pass 1). |
| test | 3m | Refresh: instant, confirmed via event-count change (395→397 events). `demo_reset.py restore`: 0.42s | Pass | |
| **Total (CLI-executable/mechanical steps measured)** | **15m** | **not comparable — /orient alone exceeded budget** | Fail | The /orient blocking finding (item 4) makes this pass's total not meaningful against the owner's 15m budget; see findings 4 and 5 for what must change before the owner's timed dry-runs. |

Side effects on the worktree from this pass are real, intended idea-log activity, not test pollution:
the `/idea-triage` step triaged idea `000087` via the sanctioned `append_idea.py status` call
(`_data/ideas.jsonl`, `docs/00-working/ideas.md`, `_public/overview/index.html` all regenerated
accordingly). Both servers were stopped and ports 8010/5180 confirmed free at the end of the pass.

## Rehearsal Findings (agent-driven passes, 2026-09-11)

1. **Terminal opens to plain bash, not a live Claude Code session.** Pass 1 found the embedded
   terminal shows a bare `user@host:path$` prompt on load; the runbook's `/idea` and
   `/idea-triage` steps assume typing `/idea ...` directly into a Claude Code REPL, but nothing
   in the runbook said to start one first. **Addressed:** the `/orient` step's action text (both
   Dry-Run tables) and its step marker now instruct starting a Claude Code session in the
   terminal (`claude`) before proceeding to `/idea`.
2. **`_parked` renders as its own selectable entry in the Skills dropdown** rather than being
   hidden, which could read as a real skill to a presenter unfamiliar with the parking mechanism.
   Not addressed in this pass — cosmetic, not a runbook defect (the dropdown's own content is a
   workbench UI matter, not the runbook's).
3. **`/orient`'s measured ~85s exceeds its 1m timebox** almost entirely due to backend/frontend
   cold-start latency plus this agent's own mechanical verification of every listed control. A
   presenter starting the stack before the audience is seated would not experience this the same
   way; flagged for the owner's attention during the real timed dry-runs rather than changed
   here, since the timebox reflects the live-segment's on-stage time, not setup time.
4. **The terminal slot can default to a non-functional panel on a non-Windows machine, and the
   runbook never mentioned the picker.** Pass 2 found the terminal loaded with header "CMD ▾"
   and body text `cmd is not available on this host` — no shell, no prompt — on this (Linux)
   rehearsal host. Clicking the header opened an undocumented dialog, "Terminal: choose a
   panel," listing "Terminal (bash)" and "PowerShell." Nothing in the runbook mentioned this
   control, that CMD can be the default, or that a presenter might need to switch panels before
   typing `claude`. **Addressed:** the `/orient` step and the Workbench UI Reference now document
   the terminal slot's panel picker and instruct checking/selecting a working shell before
   starting the Claude Code session — this matters most because rehearsals run on Linux while
   the live machine is Windows, where CMD is expected to work; on a rehearsal host it may not.
   **[Superseded by phase-wb-09, 2026-09-11: a fresh store now defaults the visible shell to the
   host platform's working shell — PowerShell on Windows, bash elsewhere — so CMD is never a
   fresh-store default. The header dropdown remains, as a pure switcher; a persisted browser
   choice can still override the default, so the runbook keeps the confirm-the-header step.]**
5. **`/idea-triage`, typed once as the runbook instructs, does not triage only the just-captured
   idea.** Pass 2 found that typing `/idea-triage` dispatches a subagent for the captured idea,
   then the session announces it will continue through the rest of the open backlog ("I'll
   verify its finding and advance it when the subagent reports back, then continue through the
   remaining 15 ideas one at a time") — 16 ideas were open at rehearsal start. `Escape` did not
   stop the queued continuation; it took two rounds of `Ctrl-C` to fully halt it, after it had
   already begun a second idea. The single idea it did complete triaged correctly (mechanics are
   sound); the command's actual scope (all open ideas, self-directed, hard to interrupt) is the
   problem, not its correctness. This is a real mismatch with the runbook's single-idea narrative
   ("Now I hand *that idea* to an agent to scout") and its 2-minute timebox — left unattended for
   2 minutes, a presenter would be well into unrelated backlog housekeeping live on stage. **Not
   a runbook-authoring choice to leave as-is:** the underlying `/idea-triage` command's behavior
   is not this phase's deliverable to change (its deliverables are the runbook and Windows
   checklist only). **Addressed within the runbook's own scope:** the `/idea-triage` step now
   states the command's real scope-past-one-idea behavior and gives the presenter an explicit,
   named fallback — interrupt with `Ctrl-C` (not `Escape`) as soon as the one captured idea's
   subagent reports back, before the session continues to the next backlog idea — so the
   timebox is honest about what "done" looks like on stage.
6. **Terminal panel renders severely clipped (~85px, about two visible text rows), hiding almost
   all of a live Claude Code session's output.** Pass 2 found `.xterm` container height 0 against
   a child `.xterm-screen` height of 372.99 via `getBoundingClientRect()` — a real CSS/layout
   sizing bug, not a small window; content was present and interactive but not visible without
   scripted inspection. **This is a code defect outside this phase's deliverables (application
   code, not the runbook or Windows checklist) and is not fixed here.** It is recorded for the
   owner as idea `000104` (terminal panel clipped-height layout bug) rather than built against.
   Flagging prominently: **this would wreck the live demo if unaddressed** — the terminal panel
   is the primary visual surface for the entire live segment, and this pass found it functionally
   invisible even once a working shell was selected.
   **[Resolved by phase-wb-08, 2026-09-11 (idea 000104): the height chain through the multi-panel
   slot wrapper was fixed for all three shell panels in any slot; the fill assertions passed in
   both layouts at all four checked window sizes, and phase-wb-09 re-ran them with each shell
   assigned to the main slot. The Windows visual confirmation remains phase-wb-07's owner check.]**
7. **Repeat of Pass 1 finding 2**: `_parked` still renders as its own selectable entry in the
   Skills dropdown, alongside `checkpoint` and `orient`. Still cosmetic, not a runbook defect.

## Step Markers

Each step is marked for execution context:

- **Owner-performed**: Run by the owner on the presentation machine during the live demo.

### /orient step

- Owner-performed: verify ports are free, start backend with `D_SYSTEM_DEMO_TERMINAL=1`, start frontend with `D_SYSTEM_DEMO_TERMINAL=1` and `VITE_API_TARGET=http://localhost:8010`, open browser to `http://localhost:5180`. Check the terminal slot's header (top left, small downward triangle): it should read the platform default — "PowerShell ▾" on the presentation machine (Windows), "Terminal (bash) ▾" on a non-Windows rehearsal host. A persisted browser choice can override the default, so confirm rather than assume; to change, use the header's switcher list ("Terminal: choose a panel"), which switches among the shells assigned to the slot and never moves a panel between slots. Start a Claude Code session in the terminal by running `claude`. Scan the workbench interface: notes strip (top right, `?` tooltip at far left, dropdown menu); terminal panel (left side, ellipsis menu in top right, plus its own switcher-only header dropdown); injection dropdowns (Commands, Skills, Prompts, Agents); layout-configuration button ("Configure layout", top right, opening the assignment-only dialog); HTML Viewer (right side, with refresh button, searchable file dropdown, directory dialog); explorer slot (File Browser default, Idea Explorer and Backlog Explorer in header dropdown). Verify zero page scroll at all viewport sizes.

### /idea step

- Owner-performed: narrate and type `/idea <the idea in prose>` in Claude Code session. If no audience idea, use pre-seeded fallback.

### /idea-triage step

- Owner-performed: type `/idea-triage` in Claude Code to scout and triage the idea. **The command triages the whole open backlog, not just this one idea, once dispatched** — as soon as the captured idea's subagent reports back and its finding is recorded, interrupt with `Ctrl-C` (not `Escape`) before the session continues to the next open idea.

### plan beat

- Owner-performed: narrate the planning stage (no CLI execution).

### overview-skill rebuild

- Owner-performed: invoke the `d-system-overview` skill live (this is the step's point: the parked pre-built skill makes the rebuild real, not a replay). The skill injects its invocation text `/d-system-overview` into the active terminal; the presenter hits Enter to execute. Concrete fallback if skill dispatch unavailable: `uv run python tools/generate_overview.py`. Full fallback: `uv run python tools/demo_reset.py restore` (un-parks the pre-built skill), then invoke it.
  - **Sequencing note (parked-skill design):** `tools/demo_reset.py prepare` deliberately parks `.claude/skills/d-system-overview/` to `.claude/skills/_parked/d-system-overview/` before the demo, so this rebuild is a real live invocation, not a replay. `restore` is the named fallback if the live rebuild fails.
  - Wait for page generation. The HTML Viewer will display the generated overview on its current tab (already open in `/orient`).

### test

- Owner-performed: click the refresh button in the HTML Viewer to reload and verify the current data displays. Type a quick command in the terminal to verify it remains interactive (or check session tabs if available). Return the interface to its pre-demo state when done.

## Ideas Recorded During Rehearsal

Ideas appended to `_data/ideas.jsonl` during rehearsal are permanent (per the idea lifecycle). Each rehearsal idea **must be labeled as a rehearsal entry** in its body text. Example:

```
Title: Rehearsal idea from dry-run 2

Body: Recorded during the 2026-09-15 dry-run 2 rehearsal (from the screen recording). 
[Rehearsal entry: this idea is part of the demo record, not a real audience suggestion.]
```

Mark ideas in the idea log by hand after rehearsal if they need this label, using `uv run python
tools/append_idea.py amend <id> --body "..."`.

## Pre-Demo Preparation

Before the live session:

1. Run `uv run python tools/demo_reset.py prepare` on the presentation machine to park the
   pre-built skill and seed the fallback idea.
2. Create a pre-demo git tag: `git tag demo-day-2026-09-15` (or similar), capturing the baseline
   state before any live-segment ideas are recorded.
3. Verify the tag is in place and the pre-built skill is parked.

## Live Session Fallback Actions

Every step's fallback is the same action: `uv run python tools/demo_reset.py restore`.

If any step fails (API error, network timeout, terminal hang), run the restore command and continue
the narrative with the pre-built overview skill. The fallback idea is already seeded, so the
triage step always has content to work with.

## Permission Allowlist

A pre-approved allowlist for the live-demo session is built from rehearsal transcripts and loaded
before the session starts (the `fewer-permission-prompts` skill does this). The allowlist is
scoped to the specific commands and paths the live segment uses, so the segment runs without
permission pauses while the write fences stay in place.

## Workbench UI Reference

The final workbench UI (REQ-007 W13) presents these controls:

- **Notes strip** (top right): Display-only entry from the active notes file; no title label. The `?` tooltip sits at the strip's far left. All controls (cycling, file picker, timed advance) live in one dropdown menu behind a downward-triangle affordance; the strip surface itself triggers nothing. Selected notes file persists in browser.

- **Terminal panel** (left side): A `(...)` ellipsis menu in the top right corner contains "Collapse terminal" and "Drop/restore terminal" (moves from page-level chrome into this menu). Collapse does not terminate sessions. Drop replaces the terminal area in place with an info page saying the terminal is inactive; the panel does not disappear and the page layout does not reflow. While dropped, the injection dropdowns remain visible but deactivated. Restore returns a working terminal. Separately, when the slot holds more than one assigned panel — Terminal (bash), CMD and PowerShell in the default arrangement — its own header (top left, small downward triangle) opens a "Terminal: choose a panel" list. That list is a visibility switcher only: it changes which of the slot's assigned panels is showing and never moves a panel between slots (reassignment is the configuration dialog's job). On a fresh store the visible shell defaults to the host platform's working shell — PowerShell on Windows, Terminal (bash) elsewhere — resolved through the flag-gated `GET /api/v1/workbench/platform` route (with `D_SYSTEM_DEMO_TERMINAL` unset the route is absent and the default falls back to bash). A persisted browser choice overrides the platform default, so confirm the header reads a working shell before proceeding.

- **Injection dropdowns** (below terminal header): **Commands**, **Skills**, **Prompts**, **Agents** — four dropdowns, same behavior for each. Selecting an entry injects its invocation text into the active shell un-executed (e.g., `/skill-name` for a skill, one-line run instruction for a prompt, dispatch phrase for an agent). Fed by live enumeration with optional curated overrides. Deactivated while terminal is dropped.

- **Layout-configuration button** ("Configure layout ▾", top right): Opens the assignment-only "Layout configuration" dialog — a radio group selecting the active layout, then exactly one selector per panel ("Panel assignment") choosing which of that panel's eligible slots holds it. There are no per-slot visible-panel selects (which assigned panel a slot currently shows is the slot header dropdown's job alone) and slot geometry is not editable. Moving a panel into a slot already showing another panel is not applied on selection: a confirm notice appears in place, naming the displaced panel and warning that any live session or unsaved state in it ends (the moved panel itself is not restarted — a live shell keeps its session across the move), with Confirm and Cancel buttons. Moving into a slot showing nothing applies immediately. Shipped eligibility: the three shells and the HTML Viewer are each eligible for the terminal and main slots in both layouts; Overview is main-slot-only; the notes strip and the three explorers stay in their own slots. Active layout, per-panel assignments and per-slot visible choices persist in browser; an old-schema stored state is silently discarded in favor of the default arrangement. Two layouts ship: layout 1 (terminal left, notes strip top right, right column below) and layout 2 (terminal full-width bottom, panels across top).

- **HTML Viewer panel** (right side, main slot): Displays a selected HTML page. The generated overview is one selectable file among others found in a chosen directory. Header controls (right of title): refresh button (re-fetch current page); searchable dropdown (filter file list by search input); directory button (in-app dialog to change search directory). Has tabs like the terminal (directory, search text, and displayed page scoped per tab; controls shared).

- **Explorer slot** (right side, below HTML Viewer): File Browser, Idea Explorer, Backlog Explorer stack behind the slot header. Header renders a dropdown (small downward triangle) listing the panels; selecting one swaps it into view and returns the previous to the list. File Browser default on fresh state. All three explorers read state read-only: File Browser shows collapsible tree of subdirectories and files, filterable by text and file type, with right-click context menu (reveal in file explorer, open in HTML Viewer, copy path, inject path into terminal); Idea Explorer reads idea state via `fold()` and displays columns (id, title, status, age, annotation count, link count) with sort/filter and priority-queue toggle; Backlog Explorer presents same over `docs/09-backlog/backlog.yaml` with columns (id, title, status, priority, queue position, depends_on) and queue-view toggle.

## Launch Command Reference

**CRITICAL:** Both backend and frontend require `D_SYSTEM_DEMO_TERMINAL=1`. On the backend the flag gates every workbench route. On the frontend process it gates the dev server's repository file-serving route (`/workbench-file/*`), which the HTML Viewer loads every page through: with the flag unset on the frontend, the route is simply absent, the dev server's history fallback answers those requests with the app shell at HTTP 200, and the HTML Viewer goes silently blank — no error appears anywhere (owner-confirmed on Windows, 2026-09-11).

Backend launch:
```
D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010
```

Frontend launch (in `ts/` directory):
```
D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort
```

Without the frontend flag `VITE_API_TARGET`, the dev proxy silently targets `http://localhost:8000` instead, and every route 404s if anything holds that port. The `--strictPort` flag ensures the frontend fails rather than silently falling back to another port.
