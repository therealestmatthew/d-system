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
| /orient | Precondition: verify ports 8010 and 5180 are free — `ss -tlnp \| grep -E "8010\|5180"` should print nothing. Then: start the backend with `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010`; start the frontend with `cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort`; open http://localhost:5180. Start a Claude Code session in the terminal by running `claude`. Review the workbench interface: notes strip at top right with `?` tooltip at far left and dropdown menu; terminal panel on the left with ellipsis menu in top right (Collapse and Drop/restore); injection dropdowns (Commands, Skills, Prompts, Agents) below the terminal header; layout-configuration button at top right; HTML Viewer panel and explorer slot (File Browser visible first, with Idea Explorer and Backlog Explorer in the header dropdown) on the right. | 1m | __ACTUAL_1__ | "This is the d-system workbench — where this project actually gets worked on. Terminal on the left runs a live Claude Code session. Top right is a notes strip carrying my talking points, out of the way until I need it. On the right, a viewer for generated pages and a browser over the repository itself. The dropdowns next to the terminal hand an agent an exact command or prompt without me typing it out." |
| /idea | Type `/idea <the idea in prose>` in the Claude Code session (not a browser form or API call); wraps `tools/append_idea.py`. If no audience idea, skip to pre-seeded fallback. | 2m | __ACTUAL_2__ | "Let's capture something live. Give me an idea — anything you'd want this system to do." [take an audience suggestion, or use the pre-seeded fallback] "I type `/idea` and the idea in plain language, right here in the terminal. That's it — no form, no dialog. It's written straight into the project's permanent idea log." |
| /idea-triage | Type `/idea-triage` in Claude Code to scout and triage the recorded idea. | 2m | __ACTUAL_3__ | "Now I hand that idea to an agent to scout — `/idea-triage`. It reads the idea, searches the repository for related plans and prior decisions, and records what it finds directly on the idea. Every idea gets this same pass before anyone acts on it." |
| plan beat | Narrate the planning stage (no live CLI execution). | 3m | __ACTUAL_4__ | "From here the normal path is: requirements, then an implementation plan, then a backlog phase an agent can claim and build against — I won't run that live, it's a longer loop, but that's the chain a triaged idea travels." |
| overview-skill rebuild | Invoke the `d-system-overview` skill live to rebuild the overview — this is the step's point: `demo_reset.py prepare` deliberately parks the pre-built skill so this rebuild is real, not a replay. Fallback command if skill invocation unavailable: `uv run python tools/generate_overview.py`. Full fallback: `uv run python tools/demo_reset.py restore` then invoke the now-restored skill. Wait for page generation. Verify the HTML Viewer displays the generated overview (will already be open in the visible tab). | 4m | __ACTUAL_5__ | "Now let's generate a live report. I'm invoking the `d-system-overview` skill from the Skills dropdown — it rebuilds this project's status page from what's on disk right now, not a cached copy." [select the skill, Enter, wait] "While that runs — the panel on the right is already pointed at where it lands." |
| test | In the HTML Viewer, click refresh to reload the page and verify the generated overview displays current data. Verify the terminal panel remains interactive (type a quick command or test the session tabs). Close the demo by returning the interface to its pre-demo state. | 3m | __ACTUAL_6__ | "Refresh — there's today's data, generated during this session." [click refresh] "And the terminal underneath is still live." [type a quick command] "One idea, captured and triaged, fed into a report regenerated live — same terminal driving all of it." |
| **Total (all steps)** | | **15m** | __TOTAL_1__ | |

### Dry-Run 2 — Owner-driven timed pass (screen-recorded)

**This pass is screen-recorded.** Screen recording path on presentation machine: `__RECORDING_PATH__`

Date/time: `__DATE_TIME_2__`

| Step | Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | Precondition: verify ports 8010 and 5180 are free. Then: start the backend with `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010`; start the frontend with `cd ts && D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort`; open http://localhost:5180. Start a Claude Code session in the terminal by running `claude`. Review the workbench interface. | 1m | __ACTUAL_1__ | "This is the d-system workbench — where this project actually gets worked on. Terminal on the left runs a live Claude Code session. Top right is a notes strip carrying my talking points, out of the way until I need it. On the right, a viewer for generated pages and a browser over the repository itself." |
| /idea | Type `/idea <the idea in prose>` in Claude Code. | 2m | __ACTUAL_2__ | "Let's capture something live. Give me an idea." [take an audience suggestion, or use the pre-seeded fallback] "I type `/idea` and the idea in plain language — written straight into the project's permanent idea log." |
| /idea-triage | Type `/idea-triage` in Claude Code. | 2m | __ACTUAL_3__ | "Now I hand it to an agent to scout — `/idea-triage`. It searches the repository for related plans and prior decisions and records what it finds directly on the idea." |
| plan beat | Narrate the planning stage. | 3m | __ACTUAL_4__ | "From here the normal path is requirements, then a plan, then a backlog phase an agent can claim — I won't run that live, but that's the chain a triaged idea travels." |
| overview-skill rebuild | Invoke the skill live; fallback is `uv run python tools/generate_overview.py` or full fallback `uv run python tools/demo_reset.py restore` + skill invoke. Verify the HTML Viewer displays the overview. | 4m | __ACTUAL_5__ | "Now let's generate a live report. I'm invoking the `d-system-overview` skill from the Skills dropdown — it rebuilds this project's status page from what's on disk right now, not a cached copy." [select the skill, Enter, wait] |
| test | Refresh HTML Viewer; verify terminal interactivity; return interface to pre-demo state. | 3m | __ACTUAL_6__ | "Refresh — there's today's data, generated during this session." [click refresh] "And the terminal underneath is still live." [type a quick command] "One idea, captured and triaged, fed into a report regenerated live." |
| **Total (all steps)** | | **15m** | __TOTAL_2__ | |

## Step Markers

Each step is marked for execution context:

- **Owner-performed**: Run by the owner on the presentation machine during the live demo.

### /orient step

- Owner-performed: verify ports are free, start backend with `D_SYSTEM_DEMO_TERMINAL=1`, start frontend with `D_SYSTEM_DEMO_TERMINAL=1` and `VITE_API_TARGET=http://localhost:8010`, open browser to `http://localhost:5180`. Start a Claude Code session in the terminal by running `claude`. Scan the workbench interface: notes strip (top right, `?` tooltip at far left, dropdown menu); terminal panel (left side, ellipsis menu in top right); injection dropdowns (Commands, Skills, Prompts, Agents); layout-configuration button (top right); HTML Viewer (right side, with refresh button, searchable file dropdown, directory dialog); explorer slot (File Browser default, Idea Explorer and Backlog Explorer in header dropdown). Verify zero page scroll at all viewport sizes.

### /idea step

- Owner-performed: narrate and type `/idea <the idea in prose>` in Claude Code session. If no audience idea, use pre-seeded fallback.

### /idea-triage step

- Owner-performed: type `/idea-triage` in Claude Code to scout and triage the idea.

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

- **Terminal panel** (left side): A `(...)` ellipsis menu in the top right corner contains "Collapse terminal" and "Drop/restore terminal" (moves from page-level chrome into this menu). Collapse does not terminate sessions. Drop replaces the terminal area in place with an info page saying the terminal is inactive; the panel does not disappear and the page layout does not reflow. While dropped, the injection dropdowns remain visible but deactivated. Restore returns a working terminal.

- **Injection dropdowns** (below terminal header): **Commands**, **Skills**, **Prompts**, **Agents** — four dropdowns, same behavior for each. Selecting an entry injects its invocation text into the active shell un-executed (e.g., `/skill-name` for a skill, one-line run instruction for a prompt, dispatch phrase for an agent). Fed by live enumeration with optional curated overrides. Deactivated while terminal is dropped.

- **Layout-configuration button** (top right): Opens a surface to select the active layout and assign panels to slots (slot geometry is not editable). Active layout and per-slot panel selections persist in browser. Two layouts ship: layout 1 (terminal left, notes strip top right, right column below) and layout 2 (terminal full-width bottom, panels across top).

- **HTML Viewer panel** (right side, main slot): Displays a selected HTML page. The generated overview is one selectable file among others found in a chosen directory. Header controls (right of title): refresh button (re-fetch current page); searchable dropdown (filter file list by search input); directory button (in-app dialog to change search directory). Has tabs like the terminal (directory, search text, and displayed page scoped per tab; controls shared).

- **Explorer slot** (right side, below HTML Viewer): File Browser, Idea Explorer, Backlog Explorer stack behind the slot header. Header renders a dropdown (small downward triangle) listing the panels; selecting one swaps it into view and returns the previous to the list. File Browser default on fresh state. All three explorers read state read-only: File Browser shows collapsible tree of subdirectories and files, filterable by text and file type, with right-click context menu (reveal in file explorer, open in HTML Viewer, copy path, inject path into terminal); Idea Explorer reads idea state via `fold()` and displays columns (id, title, status, age, annotation count, link count) with sort/filter and priority-queue toggle; Backlog Explorer presents same over `docs/09-backlog/backlog.yaml` with columns (id, title, status, priority, queue position, depends_on) and queue-view toggle.

## Launch Command Reference

**CRITICAL:** Both backend and frontend require `D_SYSTEM_DEMO_TERMINAL=1`.

Backend launch:
```
D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010
```

Frontend launch (in `ts/` directory):
```
D_SYSTEM_DEMO_TERMINAL=1 VITE_API_TARGET=http://localhost:8010 npm run dev -- --port 5180 --strictPort
```

Without the frontend flag `VITE_API_TARGET`, the dev proxy silently targets `http://localhost:8000` instead, and every route 404s if anything holds that port. The `--strictPort` flag ensures the frontend fails rather than silently falling back to another port.
