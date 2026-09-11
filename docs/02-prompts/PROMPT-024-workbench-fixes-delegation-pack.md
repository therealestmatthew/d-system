---
schema_version: 1
id: doc-prompt-workbench-fixes-delegation-pack
code: PROMPT-024
title: Workbench fixes delegation pack — terminal truncation and layout assignment
kind: prompt
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench, doc-workbench-requirements, doc-prompt-workbench-delegation-pack]
---

# Workbench fixes delegation pack — terminal truncation and layout assignment

Every prompt the build coordinator sends to execute `phase-wb-08` (panel rendering fixes —
terminal fill, HTML Viewer, File Browser scroll; first priority) and `phase-wb-09`
(layout-assignment redesign), one delimited section per dispatch. Produced by the 2026-09-11
hand-off session from the owner's confirmed decisions (REQ-007 delta rows W15–W18); nothing
is authored mid-build. The coordinator sends each fenced
block **verbatim** to the named agent and sends nothing that is not in this pack. The
conventions are [PROMPT-021](PROMPT-021-workbench-delegation-pack.md)'s, restated:

- **Idempotency**: every prompt opens with the clause *"Assess the current state of the worktree
  and repository against the deliverables below; do only what is missing; report what already
  existed."* A dispatch may be re-sent in a later session without harm.
- **Worktrees**: the primary checkout is `/code/d-system`; each phase's worktree is
  `/code/d-system-worktrees/<phase-id>` on branch `agent/<phase-id>`, created from `dev`.
- **Ports**: backend `8010`, frontend `5180` — never `8000` or `5173`.
- **Truncation**: if a dispatched agent's output is cut off by its turn limit, resume that same
  agent; never re-run it from scratch (idea `000077`).
- Validator dispatches carry only the diff reference, the requirement text and the commands —
  never a creator's rationale.
- **Completion gate**: per the completion-gate decision in `GOV-003` (demo track, extended to
  `phase-wb-*` in that document), each phase's adversarial review (`demo-adversary`, WNN-A) and
  the Playwright browser checks (`demo-validator-web`, WNN-W) are dispatched by the
  **coordinator**, not the orchestrator. A phase is marked `status: complete` by the coordinator
  only after this gate is green and the branch is integrated with the owner's approval; the
  owner reviews retroactively.
- **Model policy** (`PROMPT-012`, binding): haiku for mechanical gates, sonnet as the default;
  opus never pre-assigned — at most one documented coordinator escalation of a single failed
  item after two sonnet attempts with validator findings attached.

The specifications every prompt cites: the workbench requirements delta
(`docs/06-requirements/REQ-007-workbench.md`, rows W15–W18 and the three amendments above
them), the terminal capability decision
(`docs/04-decisions/ADR-014-workbench-terminal-capability.md`), the layout persistence decision
(`docs/04-decisions/ADR-016-workbench-layout-persistence.md`), and the evidence trail: idea
`000104` (terminal truncation), idea `000101` (multi-panel wrapper double header), and the
rehearsal session record `docs/03-sessions/SESS-2026-09-11-05-rehearsal-refresh.md`.

Sequencing constraint the coordinator enforces: `phase-wb-08` completes and integrates before
`phase-wb-09` is claimed, and `phase-wb-10` (the runbook refresh — dispatched outside this
pack, completes via `/session-close`) follows `phase-wb-09`; `depends_on` encodes the chain.
The post-fix Windows confirmations are owner checks belonging to `phase-wb-07`, blocked
behind `phase-wb-10` (see the kick-off record's delta 4). The live demo is 2026-09-15.

One convention addition over `PROMPT-021`: a **diagnosis dispatch** (`W08-M`,
`demo-validator-web`). The creator agents carry no browser tool, so live measurements a
creator prompt depends on are captured by `demo-validator-web` first and handed to the creator
as recorded evidence — measurements are observed by the agent that can observe them, never
asserted by one that cannot. `W08-M` may be re-dispatched after a fix is committed to confirm
the measurements changed, without spending a fix cycle.

---

## W08 — phase-wb-08: panel rendering fixes (orchestrator: `demo-orch-stage`)

### W08-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-wb-08 (panel rendering fixes — terminal fill, HTML
Viewer, File Browser scroll; see docs/09-backlog/backlog.yaml and
docs/01-plans/PLAN-022-workbench.md, delta section). Worktree:
/code/d-system-worktrees/phase-wb-08. Branch: agent/phase-wb-08, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-08 per AGENTS.md (status: active,
   agent: agent-demo-stage, catalog updated date) in one small commit; the governance run must
   accept the claim. Before claiming, run uv run python -m src.governance --ready and confirm
   BOTH that phase-wb-08's Conflicts column is empty (no active peer locks a shared system or
   path — the validator rejects a systems overlap regardless of the budget) AND that the
   max_active budget has room (active count + 1 <= 3); if either fails, report up and wait
   rather than claiming into a validator rejection.
2. Create the worktree and set it up: uv venv && uv sync --extra dev; cd ts && npm install
   (worktree-local node_modules, never a symlink).
3. Dispatch W08-M (pre-fix diagnosis) first, then W08-C1 with W08-M's recorded measurements
   attached as evidence, then W08-V1 — each prompt verbatim from PROMPT-024
   (docs/02-prompts/PROMPT-024-workbench-fixes-delegation-pack.md). At most two fix cycles,
   then report up. When the creator reports its item done, commit it on the phase branch
   (narrow, one concern per commit) BEFORE dispatching the validator — the validator judges
   git diff dev...agent/phase-wb-08, which is empty until the work is committed. You may
   re-dispatch W08-M after a committed fix to confirm the measurements changed; that does not
   spend a fix cycle.
4. Dispatch W08-G (demo-validator-check) as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress into the phase's session record. Do not mark the phase complete, do not
   integrate into dev, do not push without asking.

Phase deliverables (verbatim from the backlog): ts/src.

Stop when the deliverable exists in the worktree, W08-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W08-M — diagnosis: live measurements before the fix (demo-validator-web)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-08. Branch:
agent/phase-wb-08. Ports: backend 8010, frontend 5180.

This is a DIAGNOSIS dispatch, not a verification: the state of dev is expected to be broken,
and your job is to measure exactly how, so the creator (which has no browser tool) can
root-cause from your recorded evidence. Change no repository file. On a re-dispatch after a
committed fix, take the same measurements and report what changed.

Start the backend (D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the
frontend WITH the flag (D_SYSTEM_DEMO_TERMINAL=1 cd ts && npm run dev -- --port 5180). Record,
with real numbers:

1. Terminal collapse (idea 000104): in both layouts at 1366x768, for the bash panel, the
   getBoundingClientRect() height of every element in the chain .stage-workbench-slot →
   .stage-region → .stage-region__body--terminal → .stage-terminal-sessions → the session div
   → .stage-terminal-mount → .xterm → .xterm-screen, plus each element's computed display,
   flex, min-height, height and overflow. Name the first element whose height diverges from
   its parent's available space.
2. The same chain measured in a slot WITHOUT the multi-panel wrapper if one renders a panel
   (compare single-panel vs stage-workbench-slot--multi wrapping — the wrapper is the suspect;
   the related double-header issue is idea 000101).
3. HTML Viewer (owner-reported blank on Windows): in both layouts (layout 2's main slot is
   multi-panel), record whether the viewer renders a known overview figure, the same
   height-chain measurements for the viewer's slot, and whether the file-serving route
   responds (GET a known .html through it). Then restart the frontend WITHOUT the flag and
   record what the viewer shows — this distinguishes the launch-flag gap (the phase-wb-04
   follow-on) from a height collapse.
4. File Browser (REQ-007 W18): point it at docs/, expand folders until content exceeds the
   panel, and record the panel body's scrollHeight, clientHeight and computed overflow-y —
   the evidence that no internal scroll exists today.

Stop each server you started. Stop when every measurement above is recorded with real numbers
and element identifications — this report is the creator's input, so precision beats brevity.
```

### W08-C1 — creator: root-cause and fix the xterm height collapse

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-08. Branch:
agent/phase-wb-08. Ports: backend 8010, frontend 5180.

Fix the terminal panel truncation defect per REQ-007 W15 (idea 000104). Observed 2026-09-11:
the shell panel's .xterm container measures height 0 while its child .xterm-screen measures
~373–390px; on Linux the panel clips to ~2 visible rows, on Windows it renders fully blank
white (the terminal body's dark background has zero height, so .stage-region's white base in
ts/src/stage/StagePage.css shows). The shell inside stays alive — content is readable from
.xterm-rows innerText but not on screen.

ROOT-CAUSE FIRST — verify, do not assume. Your evidence is the W08-M diagnosis report the
orchestrator attaches to this dispatch: live measurements taken by demo-validator-web. You
have no browser tool — never report a measurement you did not receive from W08-M; if the
report is missing or does not settle the mechanism, report that as blocking rather than
guessing. The suspected mechanism is the height chain breaking
inside the multi-panel slot wrapper: ts/src/workbench/Slot.tsx wraps the panel in an extra
section.stage-region.stage-workbench-slot--multi once a slot admits more than one implemented
panel, and the chain .stage-workbench-slot → .stage-region → .stage-region__body--terminal →
.stage-terminal-sessions (flex 1 1 auto, min-height: 0) → absolutely-inset session divs →
.stage-terminal-mount (height: 100%) → .xterm loses its height somewhere in that wrapper.
Reconcile W08-M's measurements with the code, identify the actual break, and state it in your
report before fixing. The related double-header cosmetic issue in the same wrapper is idea
000101 — fix it only if the same root cause covers it; do not widen scope otherwise.

Two further items belong to this same work item (REQ-007 W15 viewer half and W18):

A. HTML Viewer blank rendering: W08-M's item 3 distinguishes the launch-flag gap (the
   phase-wb-04 follow-on — with the frontend flag unset the file-serving route is absent by
   design; that is a runbook matter for phase-wb-10, NOT a code fix here) from a height
   collapse in the viewer's slot (layout 2's main slot carries the multi-panel wrapper). Fix
   only what the diagnosis confirms is code; state plainly which cause was confirmed.
B. File Browser internal scroll: make the panel body scroll vertically within its own bounds
   when the tree exceeds it (with or without filters), in any slot and layout, without
   introducing page scroll — consistent with the same height chain you are repairing, not a
   hard-coded height.

Constraints on the fix:
1. It covers all three shell panels equally — Terminal (bash), CMD, PowerShell are
   parameterizations of one TerminalRegion component (ts/src/workbench/panelRegistry.tsx).
2. It must hold in ANY slot a shell panel can occupy, not only the terminal slot's current
   geometry — phase-wb-09 makes shells assignable to the main slot and re-runs the fill checks
   there; a fix hard-coding the terminal slot's dimensions fails that phase.
3. Zero page scroll (REQ-006 R02) still holds in both layouts at 1280x720, 1366x768,
   1920x1080 and 1024x768.
4. Session persistence across layout switches must not regress (StagePage.tsx keys slots by
   slot_id in one grid — do not break that mechanism).

You cannot verify the fix in a browser yourself. Instead, state the exact post-fix
measurements you expect (which chain elements' heights change and to what relation), and ask
the orchestrator to re-dispatch W08-M to confirm them — never report the fix as live-verified
on your own authority.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the root cause is stated, the fixes (terminal chain, viewer where code-confirmed,
File Browser scroll) exist, the expected post-fix measurements are stated and the build output
is pasted — or report the blocking finding.
```

### W08-V1 — validator: truncation fix

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-08. Branch:
agent/phase-wb-08.

Diff: git diff dev...agent/phase-wb-08 -- ts/

Requirement text: REQ-007 W15 and W18; REQ-006 R02 and R10 unchanged. Check the code: the fix
applies to the shared TerminalRegion component or the slot wrapper's generic height chain, not
to one shell panel; no hard-coded pixel height or terminal-slot-specific dimension is
introduced (a fix keyed to the terminal slot's geometry is a failing finding — W15 requires it
to hold in any slot a shell can occupy); the zero-scroll structure (fixed page height,
internal panel overflow) is intact in both layouts; the slot-keying that preserves sessions
across layout switches is untouched; no xterm content is made visible by suppressing or
restyling symptoms (e.g. forcing .xterm-screen visible while the container stays 0-height)
rather than repairing the height chain; the HTML Viewer change (if any) matches the cause the
W08-M diagnosis confirmed — a code change compensating for the launch-flag gap (which is
runbook scope, phase-wb-10) is a failing finding; the File Browser body scrolls via its own
overflow within the repaired chain, not a hard-coded height.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W08-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-08. Branch:
agent/phase-wb-08.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. The phase deliverable exists: the ts/src fix.
4. cd ts && npm run build passes; uv run pytest passes (the known environmental PTY failures
   in test_demo_terminal.py, ideas 000097/000099, are recorded as environmental, not new).
5. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W08-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-08. Branch: agent/phase-wb-08.

Adversarially review phase-wb-08 (terminal panel truncation fix). Assume it is broken; find
where it fails. Specifications: the phase's backlog entry; REQ-007 W15 and W18; REQ-006 R02,
R10, R11; ideas 000104 and 000101; the W08-M diagnosis report. Attack at minimum: whether the fix is a symptom patch (styling the
collapsed state visible) rather than a repair of the height chain; whether it survives the
multi-panel wrapper AND the single-panel path — both slot states Slot.tsx can render; whether
it holds when the panel is CMD or PowerShell showing the unavailable-shell message rather than
a live xterm; whether it depends on the terminal slot's geometry in either layout file, which
phase-wb-09's main-slot assignment will break; whether collapse, drop-in-place and restore
(REQ-007 W02/W03) still render correctly inside the fixed chain; whether any hard-coded pixel
height sneaks in via CSS; whether layout switching still preserves sessions or the fix
re-keys/remounts the terminal; whether the HTML Viewer change (if any) matches the W08-M
diagnosis or papers over the launch-flag gap in code; whether the File Browser scroll holds
with filters active and in layout 2, or reintroduces page scroll at any of the four sizes.
Run the build, read the code, and run the page if needed to turn suspicion into evidence. W08-W measures rendered behavior — your job is what the code
does outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W08-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-08. Branch:
agent/phase-wb-08. Ports: backend 8010, frontend 5180.

In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend with the
same flag in its environment (D_SYSTEM_DEMO_TERMINAL=1 cd ts && npm run dev -- --port 5180).
Verify mechanically:

1. W15 fill assertions: for each shell panel selectable in the terminal slot (Terminal/bash,
   CMD, PowerShell), in BOTH layouts at 1280x720, 1366x768, 1920x1080 and 1024x768, assert via
   evaluation that the .xterm container's (or, for CMD/PowerShell on Linux, the in-panel
   unavailability message's) bounding-box height is non-zero and within 60px of its slot
   body's height. Screenshot each layout at each size.
2. On the bash panel: run echo fill-check-$RANDOM and assert the echoed line is present in the
   visible rendered area (element visible, not merely present in .xterm-rows innerText with a
   0-height container).
3. Persistence guard: set MARKER=persist$RANDOM in layout 1, switch to layout 2 and back via
   the configuration surface, run echo check-$MARKER and assert it prints the same value both
   times; assert no new terminal websocket opened during the switches (count websocket
   connections before and after).
4. Collapse and re-expand via the ellipsis menu, drop and restore: after each restore or
   re-expand, re-assert the fill check from item 1 at 1366x768 in layout 1.
5. HTML Viewer (W15 viewer half): with the flag-set frontend, assert the viewer renders a
   known overview figure in BOTH layouts — including layout 2's multi-panel main slot — and
   that its panel body's bounding-box height is non-zero and within 60px of its slot body's.
6. File Browser scroll (W18): point it at docs/, expand folders until content exceeds the
   panel; assert the body's scrollHeight exceeds its clientHeight, scrolling the body reaches
   the last entry, document scrollHeight stays within the viewport, and the same holds with a
   text filter active and in layout 2.
7. Zero-scroll: document scrollHeight <= viewport height and no two region bounding boxes
   intersect, both layouts, all four sizes. browser_console_messages shows no uncaught errors
   across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or when the page cannot start, reported with the real startup output as a blocking
finding.
```

---

## W09 — phase-wb-09: layout assignment model (orchestrator: `demo-orch-stage`)

### W09-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-wb-09 (layout assignment model — per-panel eligibility,
assignment-only dialog, concurrent shells; see docs/09-backlog/backlog.yaml and
docs/01-plans/PLAN-022-workbench.md, delta section). Depends on phase-wb-08 being integrated
into dev and marked status: complete by the coordinator — confirm before claiming.
Worktree: /code/d-system-worktrees/phase-wb-09. Branch: agent/phase-wb-09, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-09 per AGENTS.md (status: active,
   agent: agent-demo-stage, catalog updated date) in one small commit. Before claiming, run
   uv run python -m src.governance --ready and confirm BOTH that phase-wb-09's Conflicts
   column is empty (no active peer locks a shared system or path) AND that the max_active
   budget has room (active count + 1 <= 3); if either fails, report up and wait.
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: W09-C1 then W09-V1; W09-C2 then W09-V2; W09-C3 then W09-V3 — each
   prompt verbatim from PROMPT-024. At most two fix cycles per item, then report up. Commit
   each item on the phase branch BEFORE dispatching its validator.
4. Dispatch W09-G (demo-validator-check) as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
6. Checkpoint progress into the phase's session record. Do not mark the phase complete, do not
   integrate into dev, do not push without asking.

Phase deliverables (verbatim from the backlog): ts/src; _data/workbench/layouts;
src/api/routes/workbench.py; src/api/routes/demo_terminal.py; test/test_workbench_api.py;
test/test_demo_terminal.py; docs/04-decisions/ADR-014-workbench-terminal-capability.md.

Stop when every deliverable exists in the worktree, W09-G is green, and the verification
output is pasted — or when a blocking finding is reported up.
```

### W09-C1 — creator: backend — six-session cap, platform route, ADR-014 wording

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09. Ports: backend 8010.

Backend half of REQ-007 W17. Governing decision:
docs/04-decisions/ADR-014-workbench-terminal-capability.md — read it before writing code and
do not widen it beyond the two changes below:

1. Raise the session registry's global concurrent-PTY cap in
   src/api/routes/demo_terminal.py from four to six (owner decision 2026-09-11; REQ-007 W17).
   The refusal semantics are unchanged: a session past the cap is refused with the same clear
   close reason, and admitted again after a close. Everything else — gating, loopback binding,
   fail-fast, one PTY per websocket, the shell allowlist, the unavailable-shell refusal —
   stays untouched.
2. Add one GET route to src/api/routes/workbench.py under the existing
   D_SYSTEM_DEMO_TERMINAL=1 gate: it reports the host platform (windows/linux/other) and, per
   allowlisted shell (bash, cmd, powershell), whether it is available on this host — reusing
   the availability logic the unavailable-shell refusal already has, not duplicating it. Read
   docs/04-decisions/ADR-015-workbench-api-surface.md first: the route is read-only, GET-only,
   absent (404) when the flag is unset, and takes no path input.
3. Update ADR-014's cap wording (its "four-session cap" statements) to six, citing the
   2026-09-11 owner decision recorded in REQ-007's delta — a wording correction to
   match the decided behavior, nothing else in the ADR changes.

Update tests: in test/test_demo_terminal.py, the cap tests move to six — a seventh concurrent
session is refused while six are open and admitted after one closes (do not leave a
four-session cap test passing vacuously); in test/test_workbench_api.py, the platform route is
404 with the flag unset, GET-only with it set, and reports bash available with cmd/powershell
unavailable on Linux.

Run in the worktree and paste real output: uv run pytest test/test_demo_terminal.py
test/test_workbench_api.py; uv run ruff check src/ test/; uv run mypy src/.

Stop when the cap, the route, the ADR wording and the tests exist and the commands' real
output is pasted — or report the blocking finding.
```

### W09-V1 — validator: backend changes

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09.

Diff: git diff dev...agent/phase-wb-09 -- src/api test/test_demo_terminal.py test/test_workbench_api.py docs/04-decisions/ADR-014-workbench-terminal-capability.md

Requirement text: REQ-007 W17 (backend half) and W14 unchanged; ADR-014; ADR-015. Concretely:
the global cap is six, enforced server-side in the websocket route's registry, with the
refusal/re-admission semantics intact and proven by a test that really opens six sessions;
gating, loopback binding, fail-fast, the shell allowlist and the unavailable-shell refusal are
untouched; the platform route is GET-only, absent without the flag, takes no path input, and
reuses the existing shell-availability logic rather than duplicating it; ADR-014's wording
change is confined to the cap statements; no other ADR text, and nothing in REQ documents, is
edited in this diff.

Commands: uv run pytest test/test_demo_terminal.py test/test_workbench_api.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W09-C2 — creator: layout data — per-panel eligibility and defaults

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09. Ports: backend 8010, frontend 5180.

Move eligibility from the slot to the panel per REQ-007 W16 and
docs/04-decisions/ADR-016-workbench-layout-persistence.md — read both before writing code:

1. In _data/workbench/layouts/layout-1.json and layout-2.json, bump schema_version and replace
   the per-slot admits lists with per-panel eligibility: each panel type declares the set of
   slots it may occupy, and the file carries a default total assignment — every panel assigned
   to exactly one eligible slot — plus the default visible panel for each multi-panel slot.
2. Shipped eligibility (owner-specified, 2026-09-11): terminal (bash), cmd, powershell and
   html-viewer are each eligible for BOTH the terminal slot and the main slot, in both
   layouts; overview is eligible for the main slot only; the notes strip and the explorer slot
   and its panels (file-browser, idea-explorer, backlog-explorer) keep their current homes
   unchanged.
3. Defaults reproduce the pre-delta arrangement: shells assigned to the terminal slot (bash
   visible), html-viewer to the main slot (overview behind it in layout-2), so a cleared
   browser looks unchanged.
4. Update the loading/validation code (ts/src/workbench/types.ts, useWorkbenchLayouts.ts,
   storage.ts, schemaVersionContext.ts) to the new shape. The localStorage state becomes
   per-layout per-panel assignment plus per-slot visible choice, under the same single
   namespaced key now carrying the bumped schema_version; stored state from the old schema, or
   referencing an unknown layout, slot or panel, or assigning a panel to a slot it is not
   eligible for, is silently discarded in favor of the file defaults (ADR-016 rule 3) — never
   an error, never a migration.
5. Extend the layout-schema test (if none exists on dev yet — idea 000098 — add one) so a
   malformed layout file, a panel with no eligible slot, or a default assignment to an
   ineligible slot fails before it ships.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when both layout files, the loading code, the storage shape and the test exist and the
build output is pasted — or report the blocking finding.
```

### W09-V2 — validator: layout data and storage

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09.

Diff: git diff dev...agent/phase-wb-09 -- ts/ _data/workbench/layouts

Requirement text: REQ-007 W16 (data and storage half); ADR-016. Concretely: both layout files
carry a bumped schema_version, per-panel eligibility exactly as specified (four panels
eligible for terminal+main slots, overview main-only, notes strip and explorers unchanged) and
a default total assignment reproducing the pre-delta arrangement; eligibility lives in the
data files, not hardcoded in components; the stored state is per-panel assignment plus
per-slot visible choice under the single versioned key; old-schema, unknown-reference and
ineligible-assignment stored state all fall back silently to defaults (an error path or a
migration attempt is a failing finding); a test rejects malformed layout files and ineligible
default assignments.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W09-C3 — creator: assignment dialog, switchers, concurrent shells

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09. Ports: backend 8010, frontend 5180.

Rework the configuration and slot surfaces per REQ-007 W16/W17 over W09-C2's data model:

1. The configuration dialog (ts/src/workbench/LayoutConfigDialog.tsx) becomes the assignment
   surface: per panel, one selector over that panel's eligible slots — a total mapping. It no
   longer offers per-slot visible-panel selects (that duplication of the header dropdowns was
   never intended) and still offers no geometry editing.
2. Slot-header dropdowns stay, as switchers ONLY: they list the panels currently assigned to
   the slot and control which is visible; they never re-assign. A slot with one assigned panel
   renders a plain header. Multi-occupancy presents exactly like the current terminal slot's
   dropdown, uniformly for any multi-panel slot.
3. Two live shells at once are allowed and correct: e.g. Terminal in the terminal slot and
   PowerShell in the main slot render simultaneously, each fully interactive over its own
   sessions, within the backend's six-session global cap (W09-C1). The per-panel tab cap
   stays four (MAX_SESSIONS in ts/src/stage/TerminalRegion.tsx); when the backend refuses a
   session over the global cap, the panel shows a clear message, not a broken terminal.
4. Re-assigning a panel to another slot never silently kills a shell session: keep component
   instances alive across re-assignment where feasible (the layout-switch persistence works
   because StagePage.tsx keys slots by slot_id in one grid — extend that mechanism, do not
   discard it); where a remount is unavoidable, the dialog states it explicitly before
   applying (a visible notice, not a silent kill).
5. The terminal slot's default visible shell becomes platform-conditional on a fresh store:
   query W09-C1's platform route and default to powershell when it reports windows, bash
   otherwise; when the route is absent (flag unset) default to bash. The layout files stay
   platform-neutral — this touches only the fresh-store default, never a stored choice.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the dialog, the switcher semantics, concurrent shells, the re-assignment behavior
and the platform default exist and the build output is pasted — or report the blocking
finding.
```

### W09-V3 — validator: dialog and concurrent shells

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09.

Diff: git diff dev...agent/phase-wb-09 -- ts/

Requirement text: REQ-007 W16 (surface half), W17 (frontend half), W15's slot-independence
obligation. Concretely: the dialog renders one eligible-slot selector per panel and no
per-slot visible-panel select and no geometry control; header dropdowns only switch
visibility — any re-assignment path through them is a failing finding; two shell panels can
mount simultaneously without sharing or clobbering each other's sessions; the per-panel tab
cap stays four and a global-cap refusal renders as a message; re-assignment either preserves
the live component instance or is preceded by an explicit stated remount notice — a silent
session kill on re-assignment is a failing finding; the platform default reads the backend
route with a bash fallback and never overrides a stored choice; no platform sniffing of
navigator.userAgent replaces the route.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W09-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: the ts/src rework; both _data/workbench/layouts files with
   the bumped schema_version and per-panel eligibility; the src/api/routes/workbench.py
   platform route; the src/api/routes/demo_terminal.py six-session cap; the updated
   test/test_workbench_api.py and test/test_demo_terminal.py; ADR-014's corrected cap wording.
4. cd ts && npm run build passes; uv run pytest passes (the known environmental PTY failures,
   ideas 000097/000099, recorded as environmental, not new); uv run ruff check src/ test/
   passes; uv run mypy src/ passes.
5. grep the diff for any remaining per-slot admits list in the layout files and for
   navigator.userAgent platform sniffing in ts/src — none present.
6. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W09-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-09. Branch: agent/phase-wb-09.

Adversarially review phase-wb-09 (layout assignment model). Assume it is broken; find where it
fails. Specifications: the phase's backlog entry; REQ-007 W15–W17 and the delta's amendments;
ADR-014; ADR-015; ADR-016; REQ-006 R02, R10–R12. Attack at minimum: whether any panel can end
up assigned to two slots or none (partial mapping) through the dialog, stored state, or a
layout file edit; whether stored old-schema or ineligible state really falls back silently or
wedges/crashes the page; whether re-assigning a live shell kills its session silently despite
the stated behavior; whether two simultaneous shells share websockets, session ids or storage
keys; whether the six-session cap holds under concurrent connects from two panels and resets
correctly on abnormal disconnects; whether the platform route leaks anything beyond
platform/shell availability or exists with the flag unset; whether the fresh-store PowerShell
default can override a user's stored bash choice or fire when the route is absent; whether a
shell panel in the main slot is truly unclipped (W15's slot-independence — the phase-wb-08 fix
must hold here) including collapse/drop/restore in that slot; whether the header dropdown
gained any re-assignment side effect; whether any test passes vacuously (a cap test that never
opens six, an eligibility test that never asserts the ineligible case). Run commands to turn
suspicion into evidence. W09-W measures rendered behavior — your job is what the code does
outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W09-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-09. Branch:
agent/phase-wb-09. Ports: backend 8010, frontend 5180.

In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend with the
same flag in its environment (D_SYSTEM_DEMO_TERMINAL=1 cd ts && npm run dev -- --port 5180).
Verify mechanically:

1. W16 dialog: the configuration surface lists one slot selector per panel, scoped to that
   panel's eligible slots (assert the html-viewer selector offers the terminal and main slots;
   the overview selector offers only the main slot); no per-slot visible-panel select and no
   geometry control renders.
2. W16 assignment round-trip: assign html-viewer to the terminal slot and the PowerShell panel
   to the main slot; assert both render in their new slots; reload and assert the assignment
   persisted; clear the localStorage key and assert the pre-delta default arrangement returns
   (shells in the terminal slot with bash visible, html-viewer in the main slot).
3. W16 fallback: seed localStorage with an old-schema value and with an assignment of overview
   to the terminal slot (ineligible); assert each loads the defaults with no error rendered
   and no uncaught console error.
4. W15 re-run: with the bash panel assigned to the MAIN slot, in both layouts at 1280x720,
   1366x768, 1920x1080 and 1024x768, assert the .xterm container's bounding-box height is
   non-zero and within 60px of the slot body's height, and a command round-trip's output is
   visible on screen; repeat the layout-switch persistence guard (MARKER echo, no new
   websocket).
5. W17 concurrent shells: with bash in one slot and a second shell panel in another, assert
   bash round-trips while the second panel is live (on Linux the second panel shows its
   unavailable-shell message; assert it renders unclipped); assert the two panels' session
   tabs are independent (opening a tab in one adds none to the other).
6. W17 switchers: a slot with several assigned panels shows the header dropdown listing
   exactly its assigned panels and swaps them; a single-panel slot shows a plain header;
   assert swapping never changes the dialog's assignments.
7. Zero-scroll and non-overlap at the four sizes in both layouts with the reassigned
   arrangement active; browser_console_messages shows no uncaught errors across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or a blocking finding with real output.
```
