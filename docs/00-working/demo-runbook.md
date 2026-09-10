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

The two passes below are agent-driven fresh-eyes rehearsals against the current UI, run early to
catch runbook and tooling defects; complete owner-driven timing against the final UI moves to the
workbench track's rehearsal-refresh phase, per the owner's PROMPT-020 decision 7.

### Dry-Run 1 — 2026-09-10, fresh-eyes rehearsal (D05-R, pack PROMPT-018), agent demo-validator-code

| Step | Command / Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | Precondition: verify ports 8010 and 5180 are free — `ss -tlnp \| grep -E "8010\|5180"` should print nothing (both dry-runs collided with stray validator/dev servers left running in a checkout; confirm whose process it is before ever killing one). Then: `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010` (backend); `cd ts && npm run dev -- --port 5180` (frontend); open http://localhost:5180; review the interface state | 1m | 8s | Failed to bind: ports 8010/5180 occupied by a peer agent's servers in `/code/d-system` (not this worktree). See Rehearsal Findings. |
| /idea | `/idea <the idea in prose>` — a Claude Code slash command typed in the presenter's chat session (not a browser form or API call); wraps the sanctioned writer `tools/append_idea.py`. Skip to the already-seeded fallback idea if no audience idea is offered. | 2m | 0s | Recorded idea 000088, labelled a rehearsal entry. |
| /idea-triage | `/idea-triage` — a Claude Code slash command (not a browser page); scouts the recorded idea and records a finding, moving it to `triaged` | 2m | 1s (discovery only) | The discovery query ran; the subagent-dispatch half did not — a rehearsal agent forbidden from dispatching subagents cannot complete this step. See Rehearsal Findings. |
| plan beat | Owner narrates the planning stage (no live CLI execution) | 3m | skipped-by-marking | Owner-performed. |
| overview-skill rebuild | Invoke the `d-system-overview` skill live to rebuild the overview — this is the step's point: `demo_reset.py prepare` deliberately parked the pre-built skill so this rebuild is real, not a replay. Concrete fallback command if skill invocation is unavailable: `uv run python tools/generate_overview.py`. Full fallback: `uv run python tools/demo_reset.py restore`, then invoke the now-restored skill. Wait for page generation. | 4m | 1s | No `/overview-build` command exists; ran `tools/generate_overview.py` directly per the skill's own documented command. See Rehearsal Findings. |
| test | Click through the generated overview page, verify talking-points panel cycles, confirm terminal still interactive | 3m | skipped-by-marking | Browser-executable; covered by D05-W. |
| **Total (CLI-executable steps measured)** | | **15m** | **10s** | Partial: /idea-triage's subagent half unmeasured; total is not a complete R09 verification. |

### Dry-Run 2 — 2026-09-10, fresh-eyes rehearsal (D05-R, pack PROMPT-018), agent demo-validator-code, after `uv run python tools/demo_reset.py prepare`

**This pass is screen-recorded.** Screen recording path on presentation machine: `__RECORDING_PATH__`

| Step | Command / Action | Timebox | Actual | Notes |
|---|---|---|---|---|
| /orient | Precondition: verify ports 8010 and 5180 are free — `ss -tlnp \| grep -E "8010\|5180"` should print nothing (both dry-runs collided with stray validator/dev servers left running in a checkout; confirm whose process it is before ever killing one). Then: `D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010` (backend); `cd ts && npm run dev -- --port 5180` (frontend); open http://localhost:5180; review the interface state | 1m | 14s | Same port collision as dry-run 1, unchanged (peer servers still bound to 8010/5180). |
| /idea | `/idea <the idea in prose>` — a Claude Code slash command typed in the presenter's chat session (not a browser form or API call); wraps the sanctioned writer `tools/append_idea.py`. Skip to the already-seeded fallback idea if no audience idea is offered. | 2m | 0s | Recorded idea 000090, labelled a rehearsal entry. |
| /idea-triage | `/idea-triage` — a Claude Code slash command (not a browser page); scouts the recorded idea and records a finding, moving it to `triaged` | 2m | not run | Not executed this pass — same subagent-dispatch restriction as dry-run 1. |
| plan beat | Owner narrates the planning stage (no live CLI execution) | 3m | skipped-by-marking | Owner-performed. |
| overview-skill rebuild | Invoke the `d-system-overview` skill live to rebuild the overview — this is the step's point: `demo_reset.py prepare` deliberately parked the pre-built skill so this rebuild is real, not a replay. Concrete fallback command if skill invocation is unavailable: `uv run python tools/generate_overview.py`. Full fallback: `uv run python tools/demo_reset.py restore`, then invoke the now-restored skill. Wait for page generation. | 4m | 0s | `demo_reset.py prepare` had parked `.claude/skills/d-system-overview/`, so the skill is not at its active path when this step runs; ran `tools/generate_overview.py` directly. See Rehearsal Findings. |
| test | Click through the generated overview page, verify talking-points panel cycles, confirm terminal still interactive | 3m | skipped-by-marking | Browser-executable; covered by D05-W. |
| **Total (CLI-executable steps measured)** | | **15m** | **14s** | Partial: /idea-triage entirely unmeasured this pass; total is not a complete R09 verification. |

## Rehearsal Findings (both fresh-eyes passes, 2026-09-10)

These are moments a presenter would have to explain away, surfaced by two cold runs of this
runbook. Recorded, not silently fixed at the time — each is addressed below by a coordinator fix
cycle (2026-09-10) that changed the step definitions above, not the historical Actual/Notes
columns, which still reflect what each rehearsal pass actually observed.

1. **Port collision with a peer agent's dev servers.** Both passes found 8010 and 5180 occupied
   by processes rooted at `/code/d-system` (not this worktree), unrelated to phase-demo-05. The
   backend fails loudly (`address already in use`); the frontend does not — Vite silently falls
   back to the next free port (`5181`) and prints it, so a presenter who only reads the runbook's
   literal `http://localhost:5180` would land on a dead page. **Addressed:** the stray servers
   were leftovers from an earlier validator run and have been killed; the `/orient` step and its
   Step Markers entry now carry an explicit port-free precondition (`ss -tlnp | grep -E
   "8010|5180"`) before startup.
2. **`/idea-triage` is marked CLI-executable "via shell commands," but its second step dispatches
   a subagent** (`.claude/commands/idea-triage.md`). A rehearsal agent restricted from dispatching
   subagents can run the discovery half but not complete the step, so neither fresh-eyes pass
   produced a real timing for this step — the segment's second-largest timebox is unverified by
   CLI-only rehearsal. The real presenter's Claude Code session can dispatch the subagent; this is
   a rehearsal-tooling limitation, not proof the step is unusable. **Addressed:** the `/idea-triage`
   Step Markers entry now states the discovery half is CLI-measurable and the subagent-dispatch
   half runs only in the presenter's own Claude Code session; a rehearsal agent records it as
   partially measured, not failed. R09's full 15-minute total still needs a presenter-driven pass
   to verify the subagent half's timing.
3. **`/overview-build` does not exist** as a slash command; only `.claude/commands/idea.md`,
   `idea-triage.md`, `backlog.md`, `session-close.md` exist. **Addressed:** the overview-skill
   rebuild step no longer references `/overview-build`; it now describes what actually happens —
   the presenter's agents build/invoke the `d-system-overview` skill live, with
   `uv run python tools/generate_overview.py` as the concrete fallback command.
4. **Sequencing gap between `demo_reset.py prepare` and the overview-skill-rebuild step.**
   `prepare` parks `.claude/skills/d-system-overview/` to `.claude/skills/_parked/` by design
   (D05-C1). The runbook's overview-skill-rebuild step instructed invoking the skill, but after
   `prepare` has run the skill is not discoverable at its active path — only `restore` (documented
   as the failure fallback, not a required pre-step) puts it back. Both rehearsal passes worked
   around this by calling `tools/generate_overview.py` directly. **Addressed as narrative, not a
   tool change:** the overview-skill rebuild step's Step Markers entry now states the parked-skill
   design plainly — the parking is deliberate so the live rebuild is real, not a replay, and
   `restore` remains the named fallback if the live rebuild fails.

## Step Markers

Each step is marked for execution context:

- **CLI-executable**: Run by the D05-R rehearsal agent via shell commands.
- **Browser-executable**: Run by the D05-W Playwright browser validation pass; page scroll,
  popup behavior, terminal rendering verified programmatically.
- **Owner-performed**: Windows-machine-only item, executed by the owner during the Windows-setup
  gate (PROMPT-017, section "Windows-machine gate").

### /orient step

- CLI-executable: Verify ports 8010 and 5180 are free (`ss -tlnp | grep -E "8010|5180"`) before
  starting the backend and frontend. Both dry-run rehearsals collided with stray validator/dev
  servers left running from an earlier session's checkout, not this worktree — check first rather
  than assuming a clean port.
- Browser-executable: Open page, verify layout at 1280×720, 1920×1080, half-width viewport.
- Owner-performed (Windows gate): Run all steps on the presentation machine.

### /idea step

- CLI-executable only: run `/idea <the idea in prose>` in the presenter's chat session, or skip to
  the pre-seeded fallback idea. `/idea` is a Claude Code slash command (`.claude/commands/idea.md`)
  wrapping `tools/append_idea.py`, not a browser form or API endpoint — there is no idea-recording
  UI on the stage page. No browser-executable check exists for this step.

### /idea-triage step

- CLI-executable, partially measurable: run `/idea-triage` in the presenter's chat session.
  `/idea-triage` (`.claude/commands/idea-triage.md`) has two halves — a discovery query, which a
  rehearsal agent can run and time directly, and a subagent dispatch that annotates a finding and
  moves the idea to `triaged`, which runs only in the presenter's own Claude Code session. A
  rehearsal agent barred from dispatching subagents records this step as partially measured (the
  discovery half's time only), not as failed — there is no triage page or status selector on the
  stage page, and no browser-executable check exists for this step.

### plan beat

- Owner-performed: Narrated planning stage, no CLI execution on this step.

### overview-skill rebuild

- CLI-executable: Invoke the `d-system-overview` skill to rebuild the overview. Fallback command:
  `uv run python tools/generate_overview.py`.
- Browser-executable: Verify overview page regenerates and embeds the current outputs.
- **Sequencing note (parked-skill design):** `tools/demo_reset.py prepare` deliberately parks
  `.claude/skills/d-system-overview/` to `.claude/skills/_parked/d-system-overview/` before the
  segment starts, so this step's rebuild is a real, live invocation rather than a replay of
  something already built. `tools/demo_reset.py restore` is the named fallback if the live
  rebuild fails: it puts the pre-built skill back and regenerates the overview from current data,
  after which the presenter invokes the now-restored skill and continues.

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
