# Demo Runbook — Live Segment

Live-segment rehearsal and performance runbook for the skills-and-agents training demo, 2026-09-10.
This is an ungoverned working document (ADR-010); it is updated with rehearsal results and used as
the performance checklist on demo day.

## Descope Ladder

Applied in order when time runs short; each rung is independent of the ones below it:

1. Overview charts become tables.
2. Talking-points rotator loses transitions.
3. Embedded overview panel becomes an open-in-tab link.
4. Embedded terminal falls back to a side-by-side real terminal.

## Dry-Run Rehearsals

Record timings for two timed passes of the live segment. Each step carries an explicit timebox;
per-step times sum to at most 15 minutes. Stopping the timer and re-running `uv run python
tools/demo_reset.py restore` is the fallback action named in the runbook for every step.

### Dry-Run 1 (Date and time)

| Step | Command / Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010` (backend); `cd ts && npm run dev -- --port 5180` (frontend); open http://localhost:5180; review the interface state | 1m | | |
| /idea | `/idea <the idea in prose>` — a Claude Code slash command typed in the presenter's chat session (not a browser form or API call); wraps the sanctioned writer `tools/append_idea.py`. Skip to the already-seeded fallback idea if no audience idea is offered. | 2m | | Fallback: `uv run python tools/demo_reset.py restore` + continue with fallback idea |
| /idea-triage | `/idea-triage` — a Claude Code slash command (not a browser page); scouts the recorded idea and records a finding, moving it to `triaged` | 2m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| plan beat | Owner narrates the planning stage (no live CLI execution) | 3m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| overview-skill rebuild | Run `/overview-build` or equivalent skill invocation; wait for page generation | 4m | | Fallback: `uv run python tools/demo_reset.py restore` + continue with pre-built overview |
| test | Click through the generated overview page, verify talking-points panel cycles, confirm terminal still interactive | 3m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| **Total** | | **15m** | | |

### Dry-Run 2 (Date and time)

**This pass is screen-recorded.** Screen recording path on presentation machine: `__RECORDING_PATH__`

| Step | Command / Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010` (backend); `cd ts && npm run dev -- --port 5180` (frontend); open http://localhost:5180; review the interface state | 1m | | |
| /idea | `/idea <the idea in prose>` — a Claude Code slash command typed in the presenter's chat session (not a browser form or API call); wraps the sanctioned writer `tools/append_idea.py`. Skip to the already-seeded fallback idea if no audience idea is offered. | 2m | | Fallback: `uv run python tools/demo_reset.py restore` + continue with fallback idea |
| /idea-triage | `/idea-triage` — a Claude Code slash command (not a browser page); scouts the recorded idea and records a finding, moving it to `triaged` | 2m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| plan beat | Owner narrates the planning stage (no live CLI execution) | 3m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| overview-skill rebuild | Run `/overview-build` or equivalent skill invocation; wait for page generation | 4m | | Fallback: `uv run python tools/demo_reset.py restore` + continue with pre-built overview |
| test | Click through the generated overview page, verify talking-points panel cycles, confirm terminal still interactive | 3m | | Fallback: `uv run python tools/demo_reset.py restore` + continue |
| **Total** | | **15m** | | |

## Step Markers

Each step is marked for execution context:

- **CLI-executable**: Run by the D05-R rehearsal agent via shell commands.
- **Browser-executable**: Run by the D05-W Playwright browser validation pass; page scroll,
  popup behavior, terminal rendering verified programmatically.
- **Owner-performed**: Windows-machine-only item, executed by the owner during the Windows-setup
  gate (PROMPT-017, section "Windows-machine gate").

### /orient step

- CLI-executable: Backend and frontend startup.
- Browser-executable: Open page, verify layout at 1280×720, 1920×1080, half-width viewport.
- Owner-performed (Windows gate): Run all steps on the presentation machine.

### /idea step

- CLI-executable only: run `/idea <the idea in prose>` in the presenter's chat session, or skip to
  the pre-seeded fallback idea. `/idea` is a Claude Code slash command (`.claude/commands/idea.md`)
  wrapping `tools/append_idea.py`, not a browser form or API endpoint — there is no idea-recording
  UI on the stage page. No browser-executable check exists for this step.

### /idea-triage step

- CLI-executable only: run `/idea-triage` in the presenter's chat session. `/idea-triage`
  (`.claude/commands/idea-triage.md`) drives the idea-triage subagent over open ideas and records a
  finding — there is no triage page or status selector on the stage page. No browser-executable
  check exists for this step.

### plan beat

- Owner-performed: Narrated planning stage, no CLI execution on this step.

### overview-skill rebuild

- CLI-executable: Invoke the skill to rebuild the overview.
- Browser-executable: Verify overview page regenerates and embeds the current outputs.

### test

- Browser-executable: Click through overview, cycle talking-points, verify terminal interactivity.

## Ideas Recorded During Rehearsal

Ideas appended to `_data/ideas.jsonl` during rehearsal are permanent (per PLAN-021's afterlife
decision). Each rehearsal idea **must be labeled as a rehearsal entry** in its body text. Example:

```
Title: Rehearsal idea from dry-run 2

Body: Recorded during the 2026-09-10 dry-run 2 rehearsal (from the screen recording). 
[Rehearsal entry: this idea is part of the demo record, not a real audience suggestion.]
```

Mark ideas in the idea log by hand after rehearsal if they need this label, using `uv run python
tools/append_idea.py amend <id> --body "..."`.

## Pre-Demo Preparation

Before the live session:

1. Run `uv run python tools/demo_reset.py prepare` on the presentation machine to park the
   pre-built skill and seed the fallback idea.
2. Create a pre-demo git tag: `git tag demo-day-2026-09-10` or similar, capturing the baseline
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
