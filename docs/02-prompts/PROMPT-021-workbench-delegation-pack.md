---
schema_version: 1
id: doc-prompt-workbench-delegation-pack
code: PROMPT-021
title: Workbench build delegation pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench, doc-workbench-requirements, doc-prompt-demo-build-delegation-pack]
---

# Workbench build delegation pack

Every prompt the workbench build coordinator sends during
[PROMPT-022](PROMPT-022-workbench-build-orchestration.md), one delimited section per dispatch.
Produced by the workbench planning session (`PROMPT-020`'s output); nothing is authored
mid-build. The coordinator sends each fenced block **verbatim** to the named agent and sends
nothing that is not in this pack. The conventions are `PROMPT-018`'s, restated:

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
  `phase-wb-*` in that document), each phase's adversarial review (`demo-adversary`, WNN-A) and —
  for browser-facing phases — the Playwright browser checks (`demo-validator-web`, WNN-W) are
  dispatched by the **coordinator**, not the orchestrators. A phase is marked `status: complete`
  by the coordinator only after this gate is green and the branch is integrated with the owner's
  approval; the owner reviews retroactively.
- **Model policy** (`PROMPT-012`, binding): haiku for mechanical gates, sonnet as the default;
  opus never pre-assigned — at most one documented coordinator escalation of a single failed
  item after two sonnet attempts with validator findings attached.

The specifications every prompt cites: the workbench requirements
(`docs/06-requirements/REQ-007-workbench.md`, rows W01–W14), the terminal capability decision
(`docs/04-decisions/ADR-014-workbench-terminal-capability.md`), the API surface decision
(`docs/04-decisions/ADR-015-workbench-api-surface.md`) and the layout persistence decision
(`docs/04-decisions/ADR-016-workbench-layout-persistence.md`).

---

## W01 — phase-wb-01: workbench backend API (orchestrator: `demo-orch-stage`)

### W01-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-wb-01 (workbench backend API — enumeration, filesystem,
explorers, reveal, session registry; see docs/09-backlog/backlog.yaml and
docs/01-plans/PLAN-022-workbench.md). Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01, from dev. Ports: backend 8010, frontend 5180 (frontend not needed).

1. On an up-to-date dev in /code/d-system, claim phase-wb-01 per AGENTS.md (status: active,
   agent: agent-demo-stage, catalog updated date) in one small commit; the governance run must
   accept the claim. Before claiming, confirm the max_active budget has room (active count + 1
   <= 3); if it is full, report up and wait rather than claiming into a validator rejection.
2. Create the worktree and set it up: uv venv && uv sync --extra dev.
3. Dispatch, in order: W01-C1 then W01-V1; W01-C2 then W01-V2; W01-C3 then W01-V3 — each prompt
   verbatim from PROMPT-021 (docs/02-prompts/PROMPT-021-workbench-delegation-pack.md). At most
   two fix cycles per item, then report up. When a creator reports its item done, commit that
   item on the phase branch (narrow, one concern per commit) BEFORE dispatching its validator —
   the validator judges git diff dev...agent/phase-wb-01, which is empty until the work is
   committed.
4. Dispatch W01-G (demo-validator-check) as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
6. Checkpoint progress into the phase's session record. Do not mark the phase complete, do not
   integrate into dev, do not push without asking.

Phase deliverables (verbatim from the backlog): src/api/routes/workbench.py;
src/api/routes/demo_terminal.py; src/api/__init__.py; src/demo;
_data/workbench/injection-overrides.json; test/test_workbench_api.py; test/test_demo_terminal.py.

Stop when every deliverable exists in the worktree, W01-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W01-C1 — creator: enumeration, listing and search routes

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01. Ports: backend 8010.

Build the read half of the workbench route family at src/api/routes/workbench.py, registered in
src/api/__init__.py under /api/v1. Governing decision:
docs/04-decisions/ADR-015-workbench-api-surface.md — read it before writing code and do not
widen it. Routes (all GET-only), mounted ONLY when D_SYSTEM_DEMO_TERMINAL=1 (absent means 404,
exactly like the terminal route):

1. Injection-source enumeration: skills from .claude/skills/ (directory names), agents from
   .claude/agents/ (file stems), prompts from docs/02-prompts/ (governed PROMPT-* files). Each
   entry carries id, display label, and the injection text — defaults per REQ-007 W04: a skill
   injects "/<skill-name>"; a prompt injects a one-line run instruction naming its document
   ("Execute docs/02-prompts/<file>: read it in full and follow its prompt block"); an agent
   injects "Use the <name> agent to " with the cursor intended at the end. Merge the curated
   overrides file _data/workbench/injection-overrides.json (one section per category; each entry
   may relabel, replace the injection text, or hide) — create that file with a valid shape and
   no active overrides.
2. Directory listing and recursive file search, repo-bounded per ADR-015: resolve every
   requested path against the repository root and reject traversal, absolute escapes and
   symlink escapes on the RESOLVED path; never list _private/ or gitignored entries (use the
   repository's ignore rules, keeping _public/ visible); support an extension filter (the HTML
   Viewer requests .html/.svg) and a text filter on names.

Add tests in test/test_workbench_api.py: flag unset → every route 404; flag set → enumeration
matches the three directories minus hidden overrides, and an override relabel + text
replacement + hide each take effect; traversal (..), absolute-path and symlink-escape requests
rejected; a root listing contains no _private/ or gitignored entry; routes reject non-GET.

Run in the worktree and paste real output: uv run pytest test/test_workbench_api.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when the routes, the overrides file and the tests exist and the commands' real output is
pasted — or report the blocking finding.
```

### W01-V1 — validator: enumeration, listing and search

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01.

Diff: git diff dev...agent/phase-wb-01 -- src/api _data/workbench test/test_workbench_api.py

Requirement text: REQ-007 W04 (backend half) and W14, and
docs/04-decisions/ADR-015-workbench-api-surface.md. Concretely: routes exist only when
D_SYSTEM_DEMO_TERMINAL=1 (absent = 404, not 403); GET-only; enumeration covers .claude/skills/,
.claude/agents/ and docs/02-prompts/ with the W04 default injection texts and the single
overrides file applied (relabel, replace, hide); path handling validates the RESOLVED path
against the repository root — traversal, absolute and symlink escapes rejected; listings exclude
_private/ and gitignored entries via the repository's ignore rules; extension and text filters
work. Tests prove each of these, not a subset.

Commands: uv run pytest test/test_workbench_api.py; uv run ruff check src/ test/;
uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W01-C2 — creator: idea route, backlog route, reveal action

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01. Ports: backend 8010.

Extend src/api/routes/workbench.py under the same gate:

1. Idea route (GET): reads idea state EXCLUSIVELY through load_events() and fold() from
   src/db/ideas.py — a direct parse of _data/ideas.jsonl is a defect. Emits per idea: id,
   title, status, created/updated (for age), annotation count, link count. Include a
   queue-ordered variant ranking by status precedence (open → triaged → planned) then age.
2. Backlog route (GET): reads docs/09-backlog/backlog.yaml. Emits per phase: id, title, status,
   priority, queue position (index in next_up or null), depends_on. Include a queue-ordered
   variant matching the governance --ready rendering: next_up order first, then ready phases by
   priority.
3. Reveal-in-explorer action (POST, the ONLY non-GET route): validates its path per ADR-015's
   repo-bounded rule, then spawns exactly one fixed opener via an argument list (never a shell
   string): explorer.exe /select,<path> on Windows; xdg-open <containing-dir> on Linux. Any
   other command, or any path outside the repository, is refused.

Extend test/test_workbench_api.py: idea rows match an independent fold() recomputation done in
the test; backlog queue ordering matches an independent read of next_up plus ready-by-priority;
the reveal route rejects escapes and non-POST, and the spawned argument list is asserted via
monkeypatching — no real opener process in tests.

Run in the worktree and paste real output: uv run pytest test/test_workbench_api.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when the routes and tests exist and the commands' real output is pasted — or report the
blocking finding.
```

### W01-V2 — validator: explorer routes and reveal

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01.

Diff: git diff dev...agent/phase-wb-01 -- src/api test/test_workbench_api.py

Requirement text: REQ-007 W10/W11 (backend halves), W09's reveal action, W14, and
docs/04-decisions/ADR-015-workbench-api-surface.md. Concretely: the idea route touches idea
state only through fold()/load_events() — grep the diff for any direct read of
_data/ideas.jsonl, which is a failing finding; the backlog queue ordering is next_up first then
ready phases by priority, proven against an independent recomputation, not the route's own
output; the reveal route is the sole non-GET route, validates the resolved path against the
repository root, and builds a fixed argument list (explorer.exe /select / xdg-open) with no
shell-string construction; tests assert the spawn via monkeypatching.

Commands: uv run pytest test/test_workbench_api.py; uv run ruff check src/ test/;
uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W01-C3 — creator: session registry and shell allowlist

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01. Ports: backend 8010.

Extend src/api/routes/demo_terminal.py per
docs/04-decisions/ADR-014-workbench-terminal-capability.md — read it before writing code and do
not widen it:

1. A session registry mapping session id → adapter for the route's live sessions. The
   four-session cap is enforced HERE, server-side: a fifth concurrent websocket is refused with
   a clear close reason. One PTY per websocket stays; a session still ends with its websocket.
2. Per-session shell selection: the client may request bash, cmd or powershell, validated
   against exactly that allowlist — an arbitrary path or unlisted name is rejected. On a host
   lacking the requested shell, return a structured unavailable-shell refusal the frontend can
   render as an in-panel message (REQ-007 W12) — never a pretend-connect, never a raw error.
3. Gating, loopback binding and the fail-fast behavior are UNCHANGED — do not touch them beyond
   what the registry requires.

Extend test/test_demo_terminal.py: a fifth session is refused while four are open; the refusal
is absent after one of the four closes; cmd and powershell requests on Linux produce the
structured unavailable refusal; a non-allowlisted shell is rejected; existing gating/binding
tests still pass unmodified.

Run in the worktree and paste real output: uv run pytest; uv run ruff check src/ test/;
uv run mypy src/.

Stop when the registry, allowlist and tests exist and the commands' real output is pasted — or
report the blocking finding.
```

### W01-V3 — validator: registry and allowlist

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01.

Diff: git diff dev...agent/phase-wb-01 -- src/api/routes/demo_terminal.py src/demo test/test_demo_terminal.py

Requirement text: docs/04-decisions/ADR-014-workbench-terminal-capability.md decisions 4 and 5,
REQ-007 W12 (backend half) and W14. Concretely: the four-session cap lives in the websocket
route's registry, not only the UI; a fifth connection is refused with a clear close reason and
admitted again after a close; shell selection is allowlisted to bash/cmd/powershell with any
other value rejected; an unavailable shell yields a structured refusal, not an exception or a
half-open session; ADR-013's carried-forward gating, binding and fail-fast tests are untouched
and still pass. No test may pass vacuously (e.g. a cap test that never opens four sessions).

Commands: uv run pytest; uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W01-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-01. Branch:
agent/phase-wb-01.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: src/api/routes/workbench.py; src/api/routes/demo_terminal.py;
   src/api/__init__.py registration; src/demo; _data/workbench/injection-overrides.json;
   test/test_workbench_api.py; test/test_demo_terminal.py.
4. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
5. grep src/api/routes/workbench.py and the diff for any direct read of _data/ideas.jsonl —
   none present.
6. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W01-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-01. Branch: agent/phase-wb-01.

Adversarially review phase-wb-01 (the workbench backend API). Assume it is broken; find where it
fails. Specifications: the phase's backlog entry; REQ-007 rows W04, W09–W12, W14; ADR-014
decisions 4–5; ADR-015. Attack at minimum: whether any workbench route exists with the flag
unset, or answers non-GET where it must not; whether a crafted path (encoded traversal, symlink
created inside the worktree, absolute path, case tricks) escapes the repository root or lists
_private/ or gitignored content; whether the reveal route can be made to run anything other
than the fixed opener, or builds a shell string anywhere; whether the session cap holds under
concurrent connects or resets wrongly on abnormal disconnects; whether the shell allowlist can
be bypassed via the config override path the adapter already had; whether the idea route
reaches _data/ideas.jsonl anywhere; whether the backlog queue ordering actually matches the
--ready rendering on the real backlog; whether any test passes vacuously. Run commands to turn
suspicion into evidence.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

---

## W02 — phase-wb-02: layout engine and notes strip (orchestrator: `demo-orch-stage`)

### W02-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-wb-02 (layout engine and notes strip; see
docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-022-workbench.md). Depends on phase-wb-01
being integrated into dev and marked status: complete by the coordinator (the notes-file picker
consumes its listing route, and your claim id may hold only one active phase) — confirm before
claiming.
Worktree: /code/d-system-worktrees/phase-wb-02. Branch: agent/phase-wb-02, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-02 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-stage). Before claiming, confirm the max_active budget
   has room (active count + 1 <= 3); if it is full, report up and wait.
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install (worktree-local
   node_modules, never a symlink).
3. Dispatch, in order: W02-C1 then W02-V1; W02-C2 then W02-V2 — each verbatim from PROMPT-021.
   At most two fix cycles per item, then report up. Commit each item on the phase branch
   BEFORE dispatching its validator.
4. Dispatch W02-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src; _data/workbench/layouts.

Stop when every deliverable exists in the worktree, W02-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W02-C1 — creator: layout engine

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02. Ports: backend 8010, frontend 5180.

Build the workbench layout engine in ts/src per REQ-007 W05/W06 and
docs/04-decisions/ADR-016-workbench-layout-persistence.md — read both before writing code:

1. Layout definitions load from _data/workbench/layouts/, one JSON file per layout, each with
   schema_version, stable layout and slot ids, fractional/grid geometry (no pixels), the set of
   panel types each slot admits, and default assignments. Create the two shipped files:
   layout-1 (the current arrangement — terminal left; notes-strip area top right; a main right
   slot and an explorer slot below it) and layout-2 (terminal full-width bottom, panel slots
   across the top).
2. Every panel is assigned to exactly one slot per layout. A slot holding several panels
   renders its header name as a dropdown (small downward triangle beside the name) listing the
   slot's panels; selecting one swaps it into view and returns the previous panel to the list;
   a single-panel slot renders a plain header.
3. A layout-configuration button at the page's top right opens the configuration surface:
   select the active layout and assign panels to slots — NO geometry editing.
4. localStorage holds the active layout and per-layout per-slot selections under one namespaced
   key carrying the layouts' schema_version; unknown or version-mismatched stored state is
   silently discarded in favor of the layout file's defaults.
5. Existing regions (terminal, overview panel) become panels of this engine; zero page scroll
   and no overlapping regions must hold in BOTH layouts at 1280x720, 1366x768, 1920x1080 and
   1024x768 (REQ-006 R02 stays binding).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the engine, both layout files, the configuration surface and persistence exist and
the build output is pasted — or report the blocking finding.
```

### W02-V1 — validator: layout engine

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02.

Diff: git diff dev...agent/phase-wb-02 -- ts/ _data/workbench/layouts

Requirement text: REQ-007 W05 and W06, ADR-016. Check the code implements: layouts loaded from
_data/workbench/layouts/ data files (hardcoded geometry in components is a failing finding);
both shipped layouts present with schema_version, stable ids, fractional geometry and default
assignments; the slot-header dropdown on multi-panel slots and plain header on single-panel
slots; the configuration surface limited to layout choice and slot assignment — any geometry
editing control is a failing finding; the single namespaced versioned localStorage key with
silent fallback to defaults on mismatch; zero-scroll preserved structurally (fixed page height,
internal panel overflow) in both layouts.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W02-C2 — creator: notes strip

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02. Ports: backend 8010, frontend 5180.

Replace the talking-points panel with the notes strip per REQ-007 W01: a short, wide,
display-only strip at the top right with NO title and no "talking points" label, showing the
active entry; the ? tooltip moves to the strip's far left; every control — next/previous
cycling, the timed advance, and a picker listing compatible JSON files from the fixed notes
directory (ts/public/, where talking-points.json lives), enumerated through phase-wb-01's
workbench listing route with a .json extension filter — never a hardcoded file list and never a
client-side directory walk — moves into ONE dropdown behind a
standard downward-triangle affordance. The strip surface itself triggers nothing. The chosen
notes file persists in the browser under the ADR-016 selections key and survives reload;
content still loads from the chosen data file with no copy hardcoded in components. Remove the
stale placeholder comment the old panel carried (TalkingPointsRegion). The vertical space freed
below the strip belongs to the layout engine's right-hand slots (W02-C1).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the strip, its dropdown, the file picker and persistence exist and the build output
is pasted — or report the blocking finding.
```

### W02-V2 — validator: notes strip

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02.

Diff: git diff dev...agent/phase-wb-02 -- ts/

Requirement text: REQ-007 W01. The strip is display-only (no click handler on the strip surface
beyond the dropdown affordance), carries no title or "talking points" string, has the tooltip
at its far left, and holds every control inside one dropdown including the notes-file picker
scoped to the fixed notes directory and fed by the phase-wb-01 listing route (a hardcoded file
list or client-side directory walk is a failing finding); the chosen file and the entry content come from data, not
component code; the choice persists under the versioned selections key; the old panel's
standalone controls and stale placeholder comment are gone.

Commands: cd ts && npm run build; grep ts/src for "talking points" (case-insensitive) — a hit
in UI-visible strings is a failing finding.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W02-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: ts/src layout engine and notes strip;
   _data/workbench/layouts with layout-1 and layout-2 JSON files carrying schema_version.
4. cd ts && npm run build passes; uv run pytest passes.
5. The diff against dev touches nothing outside ts/ and _data/workbench/layouts.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W02-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-02. Branch: agent/phase-wb-02.

Adversarially review phase-wb-02 (layout engine and notes strip). Assume it is broken; find
where it fails. Specifications: the phase's backlog entry; REQ-007 W01, W05, W06; ADR-015 (the
notes-file picker is fed by the phase-wb-01 listing route); ADR-016; REQ-006 R02. Attack at
minimum: whether the notes-file picker's list really comes from the listing route rather than a
hardcoded list or client-side walk; whether zero-scroll is structural in BOTH layouts or only holds
in layout-1; whether a malformed or version-bumped layout file crashes the page instead of
falling back to defaults; whether stored selections referencing a removed panel or slot wedge
the UI; whether the configuration surface leaks geometry editing; whether any panel can end up
assigned to two slots or none; whether the strip is genuinely display-only or hides handlers;
whether the notes-file picker can select a non-JSON or out-of-directory file; whether
talking-points copy or layout geometry leaked into component code. Run the build and read the
code; W02-W measures rendered behavior — your job is what the code does outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W02-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-02. Branch:
agent/phase-wb-02. Ports: backend 8010, frontend 5180.

In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend
(cd ts && npm run dev -- --port 5180, proxy at :8010 via the configurable-target mechanism).
Verify mechanically:

1. In BOTH layouts at 1280x720, 1366x768, 1920x1080 and 1024x768: document scrollHeight <=
   viewport height (assert via evaluation) and no two region bounding boxes intersect.
   Screenshot each layout at each size.
2. Switching layouts via the configuration surface moves the terminal region per each layout's
   geometry (assert bounding-box change); reassigning a panel renders it in the chosen slot;
   reload restores the active layout and assignments; clearing the localStorage key restores
   layout-1 defaults.
3. A multi-panel slot's header dropdown lists its panels and swaps them (REQ-007 W06); a
   single-panel slot shows no dropdown.
4. The notes strip: shows the active entry, has no title, all controls inside its one dropdown;
   cycling works; the far-left ? tooltip appears on hover and collapses on pointer leave;
   selecting a different notes file changes the content and survives reload (REQ-007 W01).
5. browser_console_messages shows no uncaught errors across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or when the page cannot start, reported with the real startup output as a blocking
finding.
```

---

## W03 — phase-wb-03: terminal panel rework, injection, shells (orchestrator: `demo-orch-stage`)

### W03-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-wb-03 (terminal panel rework, injection dropdowns and
shell panels; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-022-workbench.md).
Depends on phase-wb-01 AND phase-wb-02 being integrated into dev and marked status: complete by
the coordinator after their completion gates — confirm both before claiming.
Worktree: /code/d-system-worktrees/phase-wb-03. Branch: agent/phase-wb-03, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-03 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-stage).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: W03-C1 then W03-V1; W03-C2 then W03-V2; W03-C3 then W03-V3 — each
   verbatim from PROMPT-021. At most two fix cycles per item, then report up. Commit each item
   BEFORE dispatching its validator.
4. Dispatch W03-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run pytest; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src; ts/public/demo-commands.json.

Stop when every deliverable exists in the worktree, W03-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W03-C1 — creator: ellipsis menu and drop-in-place

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03. Ports: backend 8010, frontend 5180.

Rework the terminal panel per REQ-007 W02 and W03:

1. A (...) ellipsis menu at the panel's top right holding exactly: Collapse terminal (moved out
   of the header; the standalone collapse control is REMOVED) and Drop/restore terminal (moved
   from page-level chrome, which is REMOVED). Collapse and drop keep their REQ-006 R10/R11
   semantics unchanged — collapse never terminates sessions; drop and tab close keep their
   explicit confirmations.
2. Drop changes meaning: the panel no longer disappears. The terminal area is replaced IN PLACE
   by an info page stating the terminal is inactive and how to activate it; the panel's bounds
   and the page layout do not change.
3. While dropped, ALL injection dropdowns in the panel are visible but deactivated — grayed
   out, unclickable — and reactivate on restore. Restore returns a working terminal.
4. Fix the recorded websocket startup-race console warning in the terminal component (deferred
   from the demo track).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the menu, drop-in-place behavior, deactivation and the warning fix exist and the
build output is pasted — or report the blocking finding.
```

### W03-V1 — validator: ellipsis menu and drop

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03.

Diff: git diff dev...agent/phase-wb-03 -- ts/

Requirement text: REQ-007 W02 and W03; REQ-006 R10/R11 unchanged. No standalone collapse
control and no page-level drop control remain anywhere in ts/src; both actions live only in the
panel's ellipsis menu; drop renders the info page inside unchanged panel bounds rather than
unmounting the panel; the confirmation guards on drop and tab close are intact; sessions
survive collapse (components stay mounted); the injection dropdowns carry a real disabled state
while dropped (not merely styling); the startup-race warning path is actually fixed, not
suppressed by swallowing errors.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W03-C2 — creator: Skills, Prompts and Agents injection dropdowns

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03. Ports: backend 8010, frontend 5180.

Add three injection dropdowns next to the existing Commands dropdown — Skills, Prompts,
Agents — per REQ-007 W04, fed by phase-wb-01's enumeration route (labels, injection text and
hidden entries all come from the route; nothing hardcoded in components). Selecting an entry
injects its text into the active terminal's input line WITHOUT executing it — identical
mechanics to the existing command injection (REQ-006 R12): no trailing newline, active tab's
websocket. All three share the Commands dropdown's deactivation behavior while the terminal is
dropped or absent, and degrade cleanly when the route is absent (flag unset) — no errors.
Replace ts/public/demo-commands.json's placeholder entries with real demo commands (the
orient/idea/triage/overview command set the runbook uses; take the command strings from
docs/00-working/demo-runbook.md).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the three dropdowns, their wiring and the real command file exist and the build
output is pasted — or report the blocking finding.
```

### W03-V2 — validator: injection dropdowns

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03.

Diff: git diff dev...agent/phase-wb-03 -- ts/

Requirement text: REQ-007 W04; REQ-006 R12 semantics. The three dropdowns render only
route-served content — any skill, agent or prompt name hardcoded in a component is a failing
finding; injection reuses the R12 path (un-executed, no trailing newline, active tab); the
dropdowns disable with the drop state and degrade with the absent route;
ts/public/demo-commands.json no longer contains placeholder entries and its strings do not
appear inside ts/src.

Commands: cd ts && npm run build; grep ts/src for each demo-commands.json command string.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### W03-C3 — creator: shell panels

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03. Ports: backend 8010, frontend 5180.

Add Terminal (bash), CMD and PowerShell as three separate panel options in the slot dropdown
per REQ-007 W12, functionally identical, each requesting its shell through phase-wb-01's
per-session shell selection. When the backend returns the structured unavailable-shell refusal
(CMD/PowerShell on Linux), render a clear in-panel message naming the unavailable shell — never
a raw error, never a broken terminal, no uncaught console errors. The existing bash panel's
behavior (tabs, collapse, drop, injection) is shared, not duplicated.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the three panel options and the degradation message exist and the build output is
pasted — or report the blocking finding.
```

### W03-V3 — validator: shell panels

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03.

Diff: git diff dev...agent/phase-wb-03 -- ts/

Requirement text: REQ-007 W12 (frontend half). Three panel options sharing one implementation
parameterized by shell (a copy-pasted second terminal component is a failing finding); the
unavailable-shell refusal renders as an in-panel message naming the shell; no shell name is
used to build a command client-side — the backend allowlist is the authority.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W03-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: ts/src rework; ts/public/demo-commands.json with
   non-placeholder entries.
4. cd ts && npm run build passes; uv run pytest passes.
5. grep ts/src for standalone collapse/page-level drop control remnants and for any
   demo-commands.json command string — none present.
6. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W03-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-03. Branch: agent/phase-wb-03.

Adversarially review phase-wb-03 (terminal panel rework, injection dropdowns, shells). Assume
it is broken; find where it fails. Specifications: the phase's backlog entry; REQ-007 W02, W03,
W04, W12; REQ-006 R10–R12 unchanged. Attack at minimum: whether a session survives
collapse-from-the-menu as R10 requires, or the menu path unmounts what the old control kept
mounted; whether drop leaves any path that terminates without confirmation, or the info page
reflows the layout; whether "deactivated" dropdowns are truly unclickable (keyboard, focus,
programmatic) or only styled gray; whether injected text can execute on selection (embedded
newline through the enumeration route's text — the demo track's D06-A blocker pattern);
whether an overrides-file change really needs no rebuild; whether the shell panels duplicate
the terminal component; whether the startup-race fix hides real errors. W03-W measures rendered
behavior — your job is what the code does outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W03-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-03. Branch:
agent/phase-wb-03. Ports: backend 8010, frontend 5180.

Start backend (D_SYSTEM_DEMO_TERMINAL=1, port 8010) and frontend (port 5180) in the worktree.
Verify mechanically:

1. W02: no standalone collapse or page-level drop control exists; collapse via the ellipsis
   menu with a long-running command alive across collapse/re-expand; drop asks for
   confirmation, nothing terminates before it, sessions genuinely end after it.
2. W03: after drop, the info page renders inside the panel (bounding box unchanged before/
   after); each injection dropdown is visible, disabled, and does not open on click or
   keyboard; restore returns a working round-trip.
3. W04: each of Skills, Prompts, Agents lists the enumeration route's entries; selecting one
   per category puts the exact expected text on the active tab's input line un-executed, and
   Enter then executes it; edit _data/workbench/injection-overrides.json to relabel, replace
   and hide an entry and assert each takes effect on refresh with no rebuild.
4. W12: bash panel round-trips; CMD and PowerShell panels each show the in-panel
   unavailable-shell message naming the shell.
5. Restart the backend WITHOUT the flag: the dropdowns degrade alongside the absent-terminal
   message with no errors.
6. Zero-scroll and non-overlap hold at the four sizes; browser_console_messages shows no
   uncaught errors across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or a blocking finding with real output.
```

---

## W04 — phase-wb-04: HTML Viewer panel (orchestrator: `demo-orch-data`)

### W04-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-wb-04 (HTML Viewer panel with tabs; see
docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-022-workbench.md). Depends on phase-wb-03
being integrated into dev and marked status: complete by the coordinator (shared ts/src lock) —
confirm before claiming.
Worktree: /code/d-system-worktrees/phase-wb-04. Branch: agent/phase-wb-04, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-04 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-data).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: W04-C1 then W04-V1; W04-C2 then W04-V2 — each verbatim from PROMPT-021.
   At most two fix cycles per item, then report up. Commit each item BEFORE dispatching its
   validator.
4. Dispatch W04-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src.

Stop when the deliverable exists in the worktree, W04-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W04-C1 — creator: viewer panel and controls

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04. Ports: backend 8010, frontend 5180.

Build the HTML Viewer panel per REQ-007 W07, generalizing and replacing the overview panel: it
displays a selected page (iframe or equivalent), with the generated overview one selectable
entry. Header controls to the right of the title: a refresh button re-fetching the current
page; a searchable dropdown listing the compatible files (.html and .svg) found RECURSIVELY
under the selected directory via phase-wb-01's search route, filtered by the search input; a
button opening the in-app directory dialog fed by the listing route — repo-relative paths only,
no browser-native picker. Register the panel as a layout-engine panel type defaulting to
layout-1's main right slot; keep the open-in-tab fallback the overview panel had.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the panel, its three controls and the dialog exist and the build output is pasted —
or report the blocking finding.
```

### W04-V1 — validator: viewer panel

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04.

Diff: git diff dev...agent/phase-wb-04 -- ts/

Requirement text: REQ-007 W07; ADR-015 (client side). File lists come only from the
phase-wb-01 routes (a client-side directory walk or hardcoded file list is a failing finding);
the compatible set is exactly .html/.svg; the directory dialog is in-app over the listing
route — any use of a browser-native directory picker is a failing finding; refresh re-fetches
rather than re-mounting stale content; the overview page remains reachable as an ordinary
entry.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W04-C2 — creator: viewer tabs

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04. Ports: backend 8010, frontend 5180.

Add tabs to the HTML Viewer per REQ-007 W08, exactly like the terminal's session tabs in look
and interaction: the selected directory, search text and displayed page are scoped to the
active tab; the header controls themselves are shared. Tab state persists in the browser under
the ADR-016 selections key and survives reload. Tab open/close mirror the terminal's
affordances (close needs no confirmation here — nothing terminates).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the tabs and their per-tab scope and persistence exist and the build output is
pasted — or report the blocking finding.
```

### W04-V2 — validator: viewer tabs

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04.

Diff: git diff dev...agent/phase-wb-04 -- ts/

Requirement text: REQ-007 W08. Directory, search and page are per-tab state; the controls are
shared components reading the active tab's state (per-tab duplicated control rendering is a
failing finding); tab state persists under the versioned selections key and survives reload;
the tab strip reuses the terminal tabs' interaction pattern rather than inventing a new one.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W04-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. The deliverable exists: ts/src HTML Viewer panel with tabs, registered as a panel type.
4. cd ts && npm run build passes; uv run pytest passes.
5. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W04-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-04. Branch: agent/phase-wb-04.

Adversarially review phase-wb-04 (HTML Viewer panel). Assume it is broken; find where it fails.
Specifications: the phase's backlog entry; REQ-007 W07, W08; ADR-015; ADR-016. Attack at
minimum: whether the viewer can be pointed outside the repository through any client-crafted
path the backend then serves; whether an .svg with script content executes in the panel's
origin (iframe sandboxing); whether refresh actually re-fetches a changed file or serves cache;
whether two tabs share mutable state through the "shared controls"; whether reload restores
per-tab state or only the last tab; whether the overview panel's replacement broke the stage's
zero-scroll or the open-in-tab fallback. W04-W measures rendered behavior — your job is the
code outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W04-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-04. Branch:
agent/phase-wb-04. Ports: backend 8010, frontend 5180.

Start backend (D_SYSTEM_DEMO_TERMINAL=1, port 8010) and frontend (port 5180) in the worktree.
Verify mechanically:

1. W07: point the viewer at docs/07-architecture/diagrams/demo and assert the dropdown lists
   exactly its recursive .html/.svg files; type in the search input and assert the list
   filters; select the generated overview page and assert a known figure renders; select an
   .svg and assert it renders; change a displayed file on disk, click refresh, and assert the
   change appears; change the directory through the dialog and assert the list re-scopes.
2. W08: open two tabs with different directories and search text; switch between them and
   assert each restores its own directory, filter and page; reload and assert both tabs'
   state persisted.
3. Zero-scroll and non-overlap hold at the four sizes with the viewer populated;
   browser_console_messages shows no uncaught errors.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or a blocking finding with real output.
```

---

## W05 — phase-wb-05: File Browser panel (orchestrator: `demo-orch-data`)

### W05-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-wb-05 (File Browser panel; see docs/09-backlog/backlog.yaml
and docs/01-plans/PLAN-022-workbench.md). Depends on phase-wb-04 being integrated into dev and
marked status: complete by the coordinator (shared ts/src lock; the open-in-viewer submenu
needs the viewer tabs) — confirm before claiming.
Worktree: /code/d-system-worktrees/phase-wb-05. Branch: agent/phase-wb-05, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-05 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-data).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: W05-C1 then W05-V1; W05-C2 then W05-V2 — each verbatim from PROMPT-021.
   At most two fix cycles per item, then report up. Commit each item BEFORE dispatching its
   validator.
4. Dispatch W05-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src.

Stop when the deliverable exists in the worktree, W05-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W05-C1 — creator: tree, filters, configuration

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05. Ports: backend 8010, frontend 5180.

Build the File Browser panel per REQ-007 W09 (tree half): a context folder chosen through the
in-app directory dialog (the phase-wb-04 pattern over phase-wb-01's listing route); a
collapsible treeview of subdirectories and files; filter by text search and by file type,
hiding folders with no matches. Ship the documentation-explorer mode (plans, decisions,
requirements, ...) as a configuration preset of this panel — a preset selects the context
folder and type filter; it is NOT a separate panel type. Register the panel as a layout-engine
panel type, default-visible in layout-1's explorer slot.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the tree, filters and preset exist and the build output is pasted — or report the
blocking finding.
```

### W05-V1 — validator: tree and filters

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05.

Diff: git diff dev...agent/phase-wb-05 -- ts/

Requirement text: REQ-007 W09 (tree, filters, preset). Tree content comes only from the
phase-wb-01 listing route; text and type filters hide non-matching files AND folders left
empty by the filter; the documentation-explorer is a configuration preset of the same panel
(a second panel type is a failing finding); the panel registers in the explorer slot as
layout-1's default-visible panel.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W05-C2 — creator: context menus

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05. Ports: backend 8010, frontend 5180.

Add the right-click context menu per REQ-007 W09 for every tree entry, five actions:

1. Reveal in file explorer / open containing folder — POST to phase-wb-01's reveal action
   route; surface its refusal (path outside the repository) as a visible message.
2. Open in HTML Viewer — compatible files only (.html/.svg), with a nested submenu choosing
   the target viewer tab; the file opens in that tab.
3. Copy relative path (repo-relative, as served by the API).
4. Copy absolute path (the repository root joined server-side; the route provides it).
5. Inject path into terminal — the repo-relative path appears on the active terminal tab's
   input line un-executed, reusing the R12 injection mechanics; disabled while the terminal is
   dropped or absent, like the injection dropdowns.

The menu dismisses on click-away and Escape; actions inapplicable to an entry (open-in-viewer
on a .py file) are hidden or disabled consistently.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the menu and all five actions exist and the build output is pasted — or report the
blocking finding.
```

### W05-V2 — validator: context menus

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05.

Diff: git diff dev...agent/phase-wb-05 -- ts/

Requirement text: REQ-007 W09 (menu half); ADR-015. All five actions present; reveal goes
through the backend action route only (any client-side process spawn is a failing finding);
open-in-viewer offers the tab submenu and respects the .html/.svg compatibility set;
inject-path reuses the R12 injection path un-executed and disables with the terminal state;
copy actions place the documented strings; the menu dismisses on click-away and Escape.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W05-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. The deliverable exists: ts/src File Browser panel with tree, filters, preset and the
   five-action context menu.
4. cd ts && npm run build passes; uv run pytest passes.
5. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W05-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-05. Branch: agent/phase-wb-05.

Adversarially review phase-wb-05 (File Browser panel). Assume it is broken; find where it
fails. Specifications: the phase's backlog entry; REQ-007 W09; ADR-015. Attack at minimum:
whether the tree can render content the listing route would refuse (client-side caching or
path joining that skips the API); whether the filter's hide-empty-folders logic drops folders
that DO contain matches deeper down; whether inject-path can execute (newline in a filename);
whether reveal can be pointed at a path outside the repository through the client; whether the
context menu leaks between entries (acting on the previously right-clicked file); whether the
documentation-explorer preset is a hidden second panel; whether large trees (docs/) block the
UI. W05-W measures rendered behavior — your job is the code outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W05-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-05. Branch:
agent/phase-wb-05. Ports: backend 8010, frontend 5180.

Start backend (D_SYSTEM_DEMO_TERMINAL=1, port 8010) and frontend (port 5180) in the worktree.
Verify mechanically:

1. Point the browser panel at docs/04-decisions and assert the tree matches an ls of that
   directory; apply a text filter and a type filter and assert non-matching files and
   emptied folders disappear; switch to the documentation-explorer preset and assert the tree
   re-scopes.
2. Right-click a file: all five actions present; open-in-viewer into tab 2 renders the file in
   that tab; inject-path puts the repo-relative path un-executed on the active terminal line;
   for both copy actions, stub navigator.clipboard.writeText via script injection BEFORE
   clicking and assert the exact string each action passed to it (do not attempt to read the
   OS clipboard — headless contexts do not grant clipboard-read); reveal returns success
   from the action route (assert the network response; do not require a desktop window).
3. The menu dismisses on click-away and on Escape.
4. Zero-scroll and non-overlap hold at the four sizes with the tree populated;
   browser_console_messages shows no uncaught errors.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or a blocking finding with real output.
```

---

## W06 — phase-wb-06: Idea and Backlog explorers (orchestrator: `demo-orch-data`)

### W06-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-wb-06 (Idea and Backlog explorer panels; see
docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-022-workbench.md). Depends on phase-wb-05
being integrated into dev and marked status: complete by the coordinator (shared ts/src lock) —
confirm before claiming.
Worktree: /code/d-system-worktrees/phase-wb-06. Branch: agent/phase-wb-06, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-06 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-data).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: W06-C1 then W06-V1; W06-C2 then W06-V2 — each verbatim from PROMPT-021.
   At most two fix cycles per item, then report up. Commit each item BEFORE dispatching its
   validator.
4. Dispatch W06-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src.

Stop when the deliverable exists in the worktree, W06-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### W06-C1 — creator: Idea Explorer

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06. Ports: backend 8010, frontend 5180.

Build the Idea Explorer panel per REQ-007 W10, over phase-wb-01's idea route ONLY — no other
data path. Columns: id, title, status, age, annotation count, link count. Sortable by column,
filterable by text and status. A toggle switches between the standard view and a
priority-queue view ranking by status precedence (open → triaged → planned) then age — use the
route's queue-ordered variant rather than re-ranking client-side. Register the panel in
layout-1's explorer slot (behind the slot-header dropdown; File Browser stays default-visible).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the panel, both views and the registration exist and the build output is pasted — or
report the blocking finding.
```

### W06-V1 — validator: Idea Explorer

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06.

Diff: git diff dev...agent/phase-wb-06 -- ts/

Requirement text: REQ-007 W10. Data comes only from the phase-wb-01 idea route (any other read
of idea state is a failing finding — the fold()-only rule reaches the frontend through that
route); the six columns render; sort and filters work on route data; the queue view uses the
route's ordering rather than a client-side re-rank that could drift from it.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W06-C2 — creator: Backlog Explorer

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06. Ports: backend 8010, frontend 5180.

Build the Backlog Explorer panel per REQ-007 W11 as the SAME configuration surface as the Idea
Explorer (shared table/sort/filter/queue-toggle components parameterized by data source — a
copy-pasted sibling is a defect), over phase-wb-01's backlog route. Columns: id, title, status,
priority, queue position, depends_on. Its priority-queue view uses the route's queue-ordered
variant (next_up first, then ready phases by priority — the --ready rendering). Register the
panel in layout-1's explorer slot behind the slot-header dropdown.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the panel, both views and the registration exist and the build output is pasted — or
report the blocking finding.
```

### W06-V2 — validator: Backlog Explorer

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06.

Diff: git diff dev...agent/phase-wb-06 -- ts/

Requirement text: REQ-007 W11 and W06. The explorer shares the Idea Explorer's components
parameterized by source (duplicated table code is a failing finding); the six columns render;
the queue view is the route's ordering; layout-1's explorer slot now lists all three explorers
in its header dropdown with File Browser default-visible.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### W06-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. The deliverable exists: ts/src Idea and Backlog explorer panels registered in the explorer
   slot.
4. cd ts && npm run build passes; uv run pytest passes.
5. grep ts/src for ideas.jsonl — no direct reference.
6. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W06-A — adversarial review (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-wb-06. Branch: agent/phase-wb-06.

Adversarially review phase-wb-06 (Idea and Backlog explorers). Assume it is broken; find where
it fails. Specifications: the phase's backlog entry; REQ-007 W10, W11, W06. Attack at minimum:
whether either panel's numbers are simply wrong against a hand recomputation on the real data
(run fold() and read backlog.yaml yourself and compare rendered counts and orderings); whether
the queue views re-rank client-side and diverge from the routes; whether the "same
configuration surface" is actually shared code; whether sorting or filtering mutates the
underlying data or breaks the queue toggle; whether the explorer slot's dropdown still shows
File Browser as default after registration. W06-W measures rendered behavior — your job is the
code outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### W06-W — browser verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-06. Branch:
agent/phase-wb-06. Ports: backend 8010, frontend 5180.

Start backend (D_SYSTEM_DEMO_TERMINAL=1, port 8010) and frontend (port 5180) in the worktree.
Verify mechanically:

1. W10: the Idea Explorer's row count and one spot-checked row match an independent fold() run
   you perform in the worktree; sort by a column and assert the order; filter and assert the
   subset; toggle the queue view and assert status-precedence-then-age ordering.
2. W11: the Backlog Explorer's rows match backlog.yaml (count and one spot-checked phase);
   toggle the queue view and assert the top rows equal next_up in order followed by ready
   phases by priority, cross-checked against uv run python -m src.governance --ready run in
   the worktree.
3. W06: the explorer slot's header dropdown lists File Browser, Idea Explorer and Backlog
   Explorer; File Browser is the default-visible panel on a fresh state; selecting each swaps
   it into view.
4. Zero-scroll and non-overlap hold at the four sizes with either explorer visible;
   browser_console_messages shows no uncaught errors.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or a blocking finding with real output.
```

---

## W07 — phase-wb-07: rehearsal refresh (orchestrator: `demo-orch-content`)

### W07-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-content. Phase: phase-wb-07 (rehearsal refresh — runbook, Windows checks,
owner-driven timing; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-022-workbench.md).
Depends on phase-wb-01 through phase-wb-06 being integrated into dev and marked status:
complete by the coordinator — confirm all six before claiming.
Worktree: /code/d-system-worktrees/phase-wb-07. Branch: agent/phase-wb-07, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-wb-07 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-content).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch W07-C1 then W07-V1 — verbatim from PROMPT-021. At most two fix cycles, then report
   up. Commit before validating.
4. Yourself (audience-facing prose is yours): finalize the runbook's presenter-facing step
   copy over the creator's skeleton, in PROMPT-017's step shape — each step with its commands,
   fallback action and timebox, timeboxes summing inside 15 minutes.
5. Dispatch W07-R (fresh-eyes rehearsal) twice, separated by
   uv run python tools/demo_reset.py prepare; record both runs' per-step times in the runbook,
   marked clearly as AGENT-DRIVEN mechanics checks.
6. Report plainly as outstanding owner-machine, owner-driven work — never as done: the REQ-006
   R06 Windows smoke check, the CMD and PowerShell round-trips (REQ-007 W12 Windows half), and
   both owner-driven timed dry-runs (REQ-006 R09's deferred conditions). These close only on
   the owner's recorded results.
7. Dispatch W07-G as the phase gate.
8. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
9. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): docs/00-working/demo-runbook.md;
docs/00-working/demo-windows-setup.md.

Stop when the deliverables exist, W07-G is green, the agent-driven rehearsal times are
recorded, and the owner-driven items are listed as outstanding — or when a blocking finding is
reported up.
```

### W07-C1 — creator: runbook skeleton and Windows checklist update

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-docs. Worktree: /code/d-system-worktrees/phase-wb-07. Branch:
agent/phase-wb-07.

Update docs/00-working/demo-runbook.md and docs/00-working/demo-windows-setup.md against the
final workbench UI (REQ-007 W13). The runbook keeps PROMPT-017's step shape (orient → record an
idea → triage it → plan beat → overview-skill rebuild → test) but every UI reference now names
the workbench's controls: the notes strip and its dropdown, the terminal panel's ellipsis menu,
the injection dropdowns (Commands, Skills, Prompts, Agents), the layout switch, the HTML Viewer
and explorer panels where the flow touches them. Leave the presenter-facing step copy as
clearly-marked skeleton for demo-orch-content to finalize — structure and commands are yours,
prose is not. The Windows checklist adds: the workbench launch (same flag, ports 8010/5180),
the CMD and PowerShell panel round-trip checks, and keeps the pre-demo git tag, pywinpty, zoom
and screen-hygiene steps and the demo_reset.py prepare/restore verification. Do not modify
tools/demo_reset.py or OPS-013 — they survive unchanged per PROMPT-020 decision 7.

Run in the worktree and paste real output: uv run python -m src.governance.

Stop when both documents are updated and the command's real output is pasted — or report the
blocking finding.
```

### W07-V1 — validator: runbook and checklist

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-wb-07. Branch:
agent/phase-wb-07.

Diff: git diff dev...agent/phase-wb-07 -- docs/00-working/demo-runbook.md docs/00-working/demo-windows-setup.md

Requirement text: REQ-007 W13; PROMPT-017's step shape. The runbook's steps each carry
commands, a fallback action and a timebox, the timeboxes summing inside 15 minutes; every UI
reference describes the workbench (a surviving reference to the removed standalone collapse
control, page-level drop control, or "talking points" panel is a failing finding); the Windows
checklist covers the workbench launch, both shell round-trips, the R06 smoke check, the
pre-demo tag and the reset verification; tools/demo_reset.py and OPS-013 are untouched by the
diff.

Commands: none beyond reading; quote the lines that satisfy or violate each obligation.

Stop when your verdict, findings and the quoted evidence are reported.
```

### W07-R — fresh-eyes rehearsal (dispatched twice by the orchestrator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-07. Branch:
agent/phase-wb-07. Ports: backend 8010, frontend 5180.

Fresh-eyes rehearsal of the live segment: start the stack as the runbook's launch section says
(and only as it says — if the runbook's commands do not work verbatim, that is a blocking
finding), then execute the runbook's steps in order, timing each. Follow only what the runbook
says; where a step is ambiguous or a named control does not exist under that name, record it as
a finding rather than improvising. For browser-marked steps, verify in the browser
mechanically. Record per-step wall-clock times and whether each fits its timebox.

Stop each server you started. Stop when every step has a recorded time and pass/fail/finding —
or the segment cannot start, reported with real output as a blocking finding.
```

### W07-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-wb-07. Branch:
agent/phase-wb-07.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Both deliverables exist and are updated: docs/00-working/demo-runbook.md (workbench UI,
   per-step commands/fallbacks/timeboxes, both agent-driven rehearsal runs' times recorded and
   marked agent-driven) and docs/00-working/demo-windows-setup.md (workbench launch, shell
   round-trip checks, R06, tag, reset verification).
4. The runbook's timeboxes sum to 15 minutes or less (add them; paste the sum).
5. tools/demo_reset.py and docs/08-governance/OPS-013-demo-reset.md are untouched by the diff.
6. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### W07-W — rehearsal verification (dispatched by the coordinator)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-wb-07. Branch:
agent/phase-wb-07. Ports: backend 8010, frontend 5180.

Playwright pass over the runbook's browser-marked steps against the integrated workbench: start
the stack per the runbook's launch section, then execute exactly the browser-marked steps,
asserting each step's named control exists under the runbook's name for it and behaves as the
step describes. This is the gate's independent check that the runbook describes the real UI —
a control the runbook names that does not exist, or exists under another name, is a blocking
finding.

Stop each server you started. Stop when every browser-marked step has a recorded pass/fail
with evidence — or a blocking finding with real output.
```
