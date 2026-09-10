---
schema_version: 1
id: doc-prompt-demo-build-delegation-pack
code: PROMPT-018
title: Demo build delegation pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview]
depends_on: [doc-prompt-demo-agent-factory, doc-live-demo]
---

# Demo build delegation pack

Every prompt the build coordinator sends during [PROMPT-014](PROMPT-014-demo-build-orchestration.md),
one delimited section per dispatch. Produced by the agent factory session
([PROMPT-010](PROMPT-010-demo-agent-factory.md)); nothing is authored mid-build. The coordinator
sends each fenced block **verbatim** to the named agent and sends nothing that is not in this pack.

Conventions used by every section:

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
- **Completion gate**: per the demo-track completion decision in `GOV-003`, each phase's D0N-A
  (adversarial review, `demo-adversary`) and — for browser-facing phases — D02-W/D04-W/D05-W
  (Playwright browser checks, `demo-validator-web`) are dispatched by the **coordinator** at
  PROMPT-015 step 8, not by the orchestrators. A phase is marked `status: complete` by the
  coordinator only after this gate is green and the branch is integrated with the owner's
  approval; the owner reviews retroactively.

---

## D01 — phase-demo-01: terminal backend (orchestrator: `demo-orch-stage`)

### D01-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-demo-01 (build the demo terminal backend and stage read
routes; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md).
Worktree: /code/d-system-worktrees/phase-demo-01. Branch: agent/phase-demo-01, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-01 per AGENTS.md (status: active,
   agent: agent-demo-stage, catalog updated date) in one small commit; the governance run must
   accept the claim. (Claim ids must match the schema's agent-* pattern; your claim id as this
   orchestrator is agent-demo-stage.)
2. Create the worktree at the path above and set it up: uv venv && uv sync --extra dev.
3. Dispatch, in order: D01-C1 then D01-V1; D01-C2 then D01-V2; D01-C3 then D01-V3 — each prompt
   verbatim from PROMPT-018 (docs/02-prompts/PROMPT-018-demo-build-delegation-pack.md). At most
   two fix cycles per item, then report up. When a creator reports its item done, commit that
   item on the phase branch (narrow, one concern per commit) BEFORE dispatching its validator —
   the validator judges git diff dev...agent/phase-demo-01, which is empty until the work is
   committed.
4. Dispatch D01-G (demo-validator-check) as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
6. Checkpoint progress into the phase's session record. Do not mark the phase complete, do not
   integrate into dev, do not push without asking.

Phase deliverables (verbatim from the backlog): src/demo; src/api/routes/demo_terminal.py;
src/api/routes/demo_stage.py; src/api/__init__.py; pyproject.toml; uv.lock;
test/test_demo_terminal.py.

Stop when every deliverable exists in the worktree, D01-G is green, and the verification output
is pasted in your report — or when a blocking finding is reported up.
```

### D01-C1 — creator: PTY adapter

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180 (not needed by this item).

Build the PTY adapter package at src/demo/: one adapter interface with two implementations —
POSIX pty + bash for Linux/macOS, and ConPTY via pywinpty + cmd or PowerShell for Windows.
Platform auto-detected; a config override (env var or explicit argument) selects the shell.
Import pywinpty only inside the Windows implementation so Linux runs never require it. The
governing decision is docs/04-decisions/ADR-013-demo-terminal-capability.md — read it before
writing code and do not widen it.

Add tests in test/test_demo_terminal.py for: platform detection choosing the POSIX adapter on
Linux; the shell override being honored; a POSIX adapter session echoing a real command's output;
and the module importing cleanly without pywinpty installed.

Run in the worktree and paste real output: uv run pytest test/test_demo_terminal.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when src/demo/ and the tests above exist and the commands' real output is pasted — or report
the blocking finding.
```

### D01-V1 — validator: PTY adapter

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-01 -- src/demo test/test_demo_terminal.py

Requirement text: One adapter interface, two implementations (POSIX pty + bash; ConPTY via
pywinpty + cmd or PowerShell). Platform auto-detected; a config override selects the shell.
pywinpty must be imported only in the Windows path, so the module imports and tests pass on Linux
without it. Tests must cover platform detection, the shell override, a real POSIX echo
round-trip, and import-without-pywinpty. Nothing outside src/demo and test/test_demo_terminal.py
may be touched by this item's diff. Boundaries per docs/04-decisions/ADR-013-demo-terminal-capability.md.

Commands: uv run pytest test/test_demo_terminal.py; uv run ruff check src/ test/;
uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D01-C2 — creator: websocket route, gating, optional dependency

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Build the terminal websocket route at src/api/routes/demo_terminal.py, registered in
src/api/__init__.py, bridging the websocket to a shell session through the src/demo adapter
(built by D01-C1). Per docs/04-decisions/ADR-013-demo-terminal-capability.md: the route is
registered only when D_SYSTEM_DEMO_TERMINAL=1 — when the flag is unset the route must not exist
(404), not exist-but-refuse. Enforce the loopback binding in code, not in a comment: when the
flag is set, app startup fails fast unless the configured bind host is loopback (127.0.0.1 or
::1), so a --host 0.0.0.0 launch with the terminal enabled refuses to start. Declare pywinpty as
a Windows-only optional dependency in pyproject.toml (sys_platform == 'win32') and update
uv.lock.

Extend test/test_demo_terminal.py: with the flag unset the route returns 404; with the flag set,
a websocket client sends a command and receives its output (FastAPI TestClient supports websocket
testing); and the non-loopback bind check refuses with the flag set.

Run in the worktree and paste real output: uv run pytest; uv run ruff check src/ test/;
uv run mypy src/.

Stop when the route, registration, dependency declaration and tests exist and the commands' real
output is pasted — or report the blocking finding.
```

### D01-V2 — validator: websocket route

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-01 -- src/api pyproject.toml uv.lock test/test_demo_terminal.py

Requirement text: REQ-006 rows R04 and R05 (docs/06-requirements/REQ-006-live-demo.md) and
docs/04-decisions/ADR-013-demo-terminal-capability.md. Concretely: the websocket route exists
only when D_SYSTEM_DEMO_TERMINAL=1 (absent means 404, not 403); it bridges to a real shell via
the src/demo adapter; the loopback binding is enforced in code — with the flag set, startup on a
non-loopback host must fail fast, and a mere docstring or comment is a failing finding; pywinpty
is optional and Windows-only in pyproject.toml; tests prove the absent-by-default state, a
command round-trip with the flag set, and the non-loopback refusal. The diff must not touch
files outside src/api, src/demo, pyproject.toml, uv.lock and test/test_demo_terminal.py.

Commands: uv run pytest; uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D01-C3 — creator: stage read routes

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Build the stage read routes at src/api/routes/demo_stage.py, registered in src/api/__init__.py:
GET the talking-points data (served from ts/public/talking-points.json's location or a
configurable path — return the file content unchanged, 404 with a clear message when missing)
and GET the generated overview page location under _public/ (path only; the frontend embeds it).
Read-only; no route writes anything. Add route tests to test/test_demo_terminal.py or a matching
test module within this phase's deliverables.

Run in the worktree and paste real output: uv run pytest; uv run ruff check src/ test/;
uv run mypy src/.

Stop when the routes and tests exist and the commands' real output is pasted — or report the
blocking finding.
```

### D01-V3 — validator: stage read routes

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-01 -- src/api/routes/demo_stage.py src/api/__init__.py test/

Requirement text: read-only routes returning the talking-points file content unchanged (404 with
a clear message when the file is missing) and the generated overview location; registered under
/api/v1; covered by tests; no route performs a write.

Commands: uv run pytest; uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D01-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: src/demo; src/api/routes/demo_terminal.py;
   src/api/routes/demo_stage.py; src/api/__init__.py registration; pyproject.toml pywinpty
   optional dependency; uv.lock; test/test_demo_terminal.py.
4. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
5. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D01-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-01. Branch:
agent/phase-demo-01. Ports: backend 8010, frontend 5180.

Adversarially review phase-demo-01 (the demo terminal backend). Assume it is broken; find where
it fails. Specifications: the phase's backlog entry; REQ-006 rows R04 and R05
(docs/06-requirements/REQ-006-live-demo.md); docs/04-decisions/ADR-013-demo-terminal-capability.md.
Attack at minimum: whether the route is truly absent (not merely refusing) with the flag unset;
whether the non-loopback fail-fast is enforced in code and actually exercised by a test, or a
--host 0.0.0.0 launch with the flag set still starts; whether the adapter's platform detection
and shell override do what the tests claim rather than what they mock; whether pywinpty could be
imported on Linux through any path; whether any test passes vacuously; whether the diff touches
anything outside the declared deliverables; whether anything here will break phase-demo-02's
wiring. Run commands to turn suspicion into evidence.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

---

## D02 — phase-demo-02: stage frontend (orchestrator: `demo-orch-stage`)

### D02-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-demo-02 (build the stage frontend with the zero-scroll
layout; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-01 being integrated into dev AND marked status: complete by the coordinator after its
adversarial-review + agentic-testing gate (the demo-track completion decision in GOV-003) —
confirm both before claiming; the governance validator rejects an active phase whose
prerequisite is not complete.
Worktree: /code/d-system-worktrees/phase-demo-02. Branch: agent/phase-demo-02, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-02 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-stage — your claim id as this orchestrator).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install (worktree-local
   node_modules, never a symlink).
3. Dispatch, in order: D02-C1 then D02-V1; D02-C2 then D02-V2; D02-C3 then D02-V3 — each verbatim
   from PROMPT-018. At most two fix cycles per item, then report up. When a creator reports its
   item done, commit that item on the phase branch (narrow, one concern per commit) BEFORE
   dispatching its validator — the validator judges git diff dev...agent/phase-demo-02, which is
   empty until the work is committed.
4. Dispatch D02-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run pytest; uv run python -m src.governance;
   uv run python tools/check_no_private_content.py with the changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src; ts/package.json; ts/package-lock.json;
ts/public/talking-points.json.

Stop when every deliverable exists in the worktree, D02-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### D02-C1 — creator: zero-scroll stage layout and fallbacks

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Build the stage page layout in ts/src: a page with three regions — terminal, talking-points
panel, overview panel — that fits the viewport with zero page scrolling at 1280x720, 1366x768,
1920x1080 and 1024x768; regions resize dynamically and never overlap; content that does not fit
is revealed in place via tabs, expanders or buttons. Hover-triggered popups collapse when the
pointer leaves; click-triggered popups are dismissible. Include two switchable layout states per
docs/01-plans/PLAN-021-live-demo.md's descope ladder: the overview panel replaced by an
open-in-tab link (rung 3), and the stage without the embedded terminal (rung 4). Use placeholder
content in the regions; later items fill them. The layout contract is REQ-006 rows R01–R03
(docs/06-requirements/REQ-006-live-demo.md).

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the layout, reveals, popup behaviors and both fallback states exist and the build
output is pasted — or report the blocking finding.
```

### D02-V1 — validator: layout

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-02 -- ts/

Requirement text: REQ-006 rows R01, R02, R03 (docs/06-requirements/REQ-006-live-demo.md). Check
the code implements: viewport-fitting layout with no page scroll at 1280x720, 1366x768, 1920x1080
and 1024x768 (fixed page height, internal panel scrolling only); dynamic resize without overlap;
in-place reveal controls for overflow; hover popups collapsing on pointer leave; click popups
with a dismiss control; the two descope fallback states switchable without a rebuild or with a
single documented switch.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### D02-C2 — creator: xterm.js terminal wiring

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Add xterm.js to ts/ (npm dependency, worktree install) and build the terminal component wired to
the phase-demo-01 websocket route through the Vite proxy. Do not repoint the default proxy
target: make it configurable (e.g. a VITE_API_TARGET env variable) defaulting to the existing
:8000, with the demo launch setting :8010 — ts/vite.config.ts is in this phase's deliverables
for exactly this change, and the /api path convention stays. When the terminal route is absent — the
default state per docs/04-decisions/ADR-013-demo-terminal-capability.md — the component shows a
clear in-page message, not a raw connection error. Resize the terminal with its region.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the component, wiring, absent-route message and resize behavior exist and the build
output is pasted — or report the blocking finding.
```

### D02-V2 — validator: terminal wiring

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-02 -- ts/

Requirement text: REQ-006 row R04's frontend half — xterm.js over a websocket to the backend
route; a clear in-page message when the route is absent (ADR-013 makes absent the default);
terminal resizes with its region; the proxy target is configurable with the default target
unchanged (:8000) and the demo configuration selecting :8010 — a hardcoded repoint of the
default is a failing finding. xterm.js appears in ts/package.json and ts/package-lock.json.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### D02-C3 — creator: rotator and overview panel

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Build the talking-points rotator: it loads its content from ts/public/talking-points.json (create
that file with clearly-placeholder entries — final copy is authored elsewhere; never write
audience-facing copy into page code), cycles entries with a manual next/previous control and an
optional timed advance, and degrades to a static list without transitions (descope rung 2,
docs/01-plans/PLAN-021-live-demo.md). Build the overview panel embedding the generated overview
page from _public/ (iframe or equivalent), with the rung-3 open-in-tab fallback wired to the
D02-C1 layout state.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the rotator, its data file, the panel and the fallback wiring exist and the build
output is pasted — or report the blocking finding.
```

### D02-V3 — validator: rotator and panel

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-02 -- ts/

Requirement text: REQ-006 row R01 parts (b) and (c). The rotator's content comes only from
ts/public/talking-points.json — no copy hardcoded in components; editing the JSON changes the
display without touching page code. The overview panel embeds a page from _public/ and the
open-in-tab fallback works. Transitions degrade per descope rung 2.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### D02-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: ts/src stage page; ts/package.json and ts/package-lock.json
   with xterm.js; ts/public/talking-points.json.
4. cd ts && npm run build passes; uv run pytest passes.
5. grep confirms no talking-points copy string from talking-points.json appears inside ts/src.
6. The diff against dev touches nothing outside ts/.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D02-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

Adversarially review phase-demo-02 (the stage frontend). Assume it is broken; find where it
fails. Specifications: the phase's backlog entry; REQ-006 rows R01–R04; PLAN-021's descope
ladder. Attack at minimum: whether the zero-scroll claim is structural (fixed page height,
internal panel overflow) or just happens to hold at the developer's window size; whether the
fallback layout states actually switch as documented; whether any talking-points copy leaked
into component code; whether the proxy default was repointed despite the configurable-target
requirement; whether the absent-route message actually renders when the backend flag is unset or
only when the backend is down entirely; whether npm run build hides type errors the components
carry. Run the build and read the code; the D02-W browser dispatch measures the rendered
behavior — your job is what the code will do outside the happy path.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### D02-W — browser verification (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-demo-02. Branch:
agent/phase-demo-02. Ports: backend 8010, frontend 5180.

In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend
(cd ts && npm run dev -- --port 5180, with the proxy configured for :8010 per the phase's
configurable-target mechanism). Then verify in the browser, mechanically:

1. At 1280x720, 1366x768, 1920x1080 and 1024x768: the page has no scrollable overflow
   (document scrollHeight <= viewport height, assert via evaluation) and no two of the three
   region bounding boxes intersect. Screenshot each size.
2. Overflowing content is reachable through its in-place control (tab/expander/button) at the
   smallest size.
3. A hover-triggered popup collapses when the pointer moves away; a click-triggered popup closes
   from its visible dismiss control.
4. Terminal round-trip: type a command (e.g. echo demo-web-check) into the embedded terminal and
   assert its output appears in the terminal region.
5. Rotator: the entries rendered match the content of ts/public/talking-points.json; the
   next/previous control changes the visible entry.
6. Restart the backend WITHOUT the flag and confirm the stage shows the clear absent-terminal
   message rather than a raw connection error.
7. browser_console_messages shows no uncaught errors across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence (assertion values, screenshot names, console output) — or when the stage cannot start,
reported with the real startup output as a blocking finding.
```

---

## D03 — phase-demo-03: deterministic overview tools (orchestrator: `demo-orch-data`)

### D03-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-demo-03 (build the deterministic overview tools; see
docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md).
Worktree: /code/d-system-worktrees/phase-demo-03. Branch: agent/phase-demo-03, from dev.
Ports: backend 8010, frontend 5180 (not needed by this phase).

1. On an up-to-date dev in /code/d-system, claim phase-demo-03 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-data — your claim id as this orchestrator; claim ids must
   match the schema's agent-* pattern). This phase may run in parallel with phase-demo-01; its
   systems are disjoint.
2. Create the worktree; uv venv && uv sync --extra dev.
3. Dispatch, in order: D03-C1 then D03-V1; D03-C2 then D03-V2; D03-C3 — each verbatim from
   PROMPT-018. At most two fix cycles per item, then report up. When a creator reports its item
   done, commit that item on the phase branch (narrow, one concern per commit) BEFORE dispatching
   its validator — the validator judges git diff dev...agent/phase-demo-03, which is empty until
   the work is committed.
4. Dispatch D03-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged. Also run each overview tool twice against the unchanged tree and diff the
   outputs — byte-identical is a completion condition.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): tools/overview_metrics.py;
tools/overview_inventory.py; docs/08-governance/OPS-011-overview-metrics.md;
docs/08-governance/OPS-012-overview-inventory.md; test/test_overview_tools.py.

Stop when every deliverable exists in the worktree, D03-G is green, and the verification output
(including the determinism diff) is pasted — or when a blocking finding is reported up.
```

### D03-C1 — creator: overview_metrics.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this item).

Build tools/overview_metrics.py: chart-ready JSON metrics over the idea log and the backlog.
Read the idea log via load_events() and fold() from src/db/ideas.py — never parse
_data/ideas.jsonl yourself. Read docs/09-backlog/backlog.yaml for phase counts by status. Emit,
per idea 000071's metric set: funnel counts and rates by status; cycle time between statuses;
annotation coverage; link-type distribution and orphan count; throughput by day; age of open
ideas. Zero counts appear as zero rows, never omitted. Output is deterministic — same inputs,
same bytes (sort every collection, no timestamps of the run, no randomness) — and goes to stdout
or a --out path as JSON shaped for charting (labeled series, not prose). No model or network
calls.

Add tests in test/test_overview_tools.py: two runs over the unchanged repository produce
byte-identical output, and at least the funnel counts match an independent recomputation via
fold() inside the test.

Run in the worktree and paste real output: uv run pytest test/test_overview_tools.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when the tool and tests exist and the commands' real output is pasted — or report the
blocking finding.
```

### D03-V1 — validator: overview_metrics.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-03 -- tools/overview_metrics.py test/test_overview_tools.py

Requirement text: REQ-006 row R07 (docs/06-requirements/REQ-006-live-demo.md), metrics half.
The tool reads idea state only through fold()/load_events() from src.db.ideas — a direct parse of
_data/ideas.jsonl is a failing finding. Covers funnel, cycle time, annotation coverage, link
distribution and orphans, throughput, age of open ideas. Zero counts present as zeros. Two runs
byte-identical; no model or network calls; chart-ready labeled JSON. Tests prove determinism and
recompute at least the funnel independently.

Commands: uv run pytest test/test_overview_tools.py; uv run ruff check src/ test/;
uv run mypy src/; run the tool twice and diff its outputs.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D03-C2 — creator: overview_inventory.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this item).

Build tools/overview_inventory.py: consolidated inventories as deterministic JSON — (a) concepts
and terminology from the brain/ glossary sources (reuse the reading conventions of
tools/generate_glossary.py rather than re-inventing them), and (b) systems from
docs/08-governance/systems.yaml (id, name, domain, status, dependency edges). Same determinism
contract as D03-C1: sorted output, no run timestamps, no model or network calls, stdout or --out.

Extend test/test_overview_tools.py: two runs byte-identical; the systems inventory count matches
the registry's entry count.

Run in the worktree and paste real output: uv run pytest test/test_overview_tools.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when the tool and tests exist and the commands' real output is pasted — or report the
blocking finding.
```

### D03-V2 — validator: overview_inventory.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-03 -- tools/overview_inventory.py test/test_overview_tools.py

Requirement text: REQ-006 row R07, inventory half. Concepts/terminology inventory sourced from
the brain/ glossary sources; systems inventory sourced from docs/08-governance/systems.yaml with
id, name, domain, status and dependencies. Deterministic (two runs byte-identical), no model or
network calls, chart-ready labeled JSON, zero counts as zeros. Tests prove determinism and the
systems count cross-check.

Commands: uv run pytest test/test_overview_tools.py; uv run ruff check src/ test/;
uv run mypy src/; run the tool twice and diff its outputs.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D03-C3 — creator: OPS-011 and OPS-012

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-docs. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this item).

Write docs/08-governance/OPS-011-overview-metrics.md (for tools/overview_metrics.py) and
docs/08-governance/OPS-012-overview-inventory.md (for tools/overview_inventory.py). Both codes
are already reserved in docs/08-governance/codes.yaml — use them exactly, and IN THE SAME CHANGE
remove both codes' reservation entries from docs/08-governance/codes.yaml: the governance check
rejects a document carrying a still-reserved code ("reserved; remove the reservation in this
change"). Then regenerate the catalog: uv run python -m src.governance --catalog >
docs/08-governance/catalog.md (the command prints; the redirect writes the file). Follow the
repository's existing OPS documents for front matter and shape: hand-written narrative (what the
tool reads, what it emits, its determinism contract), an empty
<!-- generated:tool-reference:start/end --> block, then run
uv run python tools/generate_tool_docs.py to fill it.

Run in the worktree and paste real output: uv run python tools/generate_tool_docs.py;
uv run python -m src.governance.

Stop when both documents exist with filled generated blocks and the commands' real output is
pasted — or report the blocking finding.
```

### D03-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this phase).

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: tools/overview_metrics.py; tools/overview_inventory.py;
   docs/08-governance/OPS-011-overview-metrics.md; docs/08-governance/OPS-012-overview-inventory.md;
   test/test_overview_tools.py.
4. Both OPS documents carry governed front matter, their allocated codes, and non-empty generated
   tool-reference blocks; the OPS-011 and OPS-012 reservation entries are removed from
   docs/08-governance/codes.yaml in this branch, and the regenerated catalog is committed.
5. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
6. Each tool run twice produces byte-identical output (paste the diff commands and their empty
   results).
7. grep both tools for network or model-API imports (requests, httpx, anthropic, openai) — none
   present.
8. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D03-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-03. Branch:
agent/phase-demo-03. Ports: backend 8010, frontend 5180 (not needed by this phase).

Adversarially review phase-demo-03 (the deterministic overview tools). Assume it is broken; find
where it fails. Specifications: the phase's backlog entry; REQ-006 row R07; idea 000071's metric
set (read via fold(), never the raw log). Attack at minimum: whether any code path reads
_data/ideas.jsonl without going through fold()/load_events(); whether determinism survives a
dict-ordering or locale change rather than merely two same-process runs; whether the
"independent recomputation" in the tests actually recomputes or just calls the same function
twice; whether zero-count categories are really emitted; whether a metric's number is simply
wrong against a hand count you perform on the real log; whether the OPS documents describe the
tools as built or as specified.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

---

## D04 — phase-demo-04: overview skill, templates, generation (orchestrator: `demo-orch-data`)

### D04-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-demo-04 (build the overview skill, templates and page
generation; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-03 being integrated into dev AND marked status: complete by the coordinator after its
adversarial-review + agentic-testing gate (the demo-track completion decision in GOV-003) —
confirm both before claiming; the governance validator rejects an active phase whose
prerequisite is not complete.
Worktree: /code/d-system-worktrees/phase-demo-04. Branch: agent/phase-demo-04, from dev.
Ports: backend 8010, frontend 5180 (not needed by this phase).

1. On an up-to-date dev in /code/d-system, claim phase-demo-04 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-data — your claim id as this orchestrator).
2. Create the worktree; uv venv && uv sync --extra dev.
3. Dispatch, in order: D04-C1 then D04-V1; D04-C2 then D04-V2; D04-C3 then D04-V3; D04-C4 — each
   verbatim from PROMPT-018. At most two fix cycles per item, then report up. When a creator
   reports its item done, commit that item on the phase branch (narrow, one concern per commit)
   BEFORE dispatching its validator — the validator judges git diff dev...agent/phase-demo-04,
   which is empty until the work is committed.
4. Dispatch D04-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged. Also generate the overview page twice against the unchanged tree and diff —
   identical is a completion condition.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): tools/generate_overview.py;
docs/08-governance/OPS-014-generate-overview.md; .claude/skills/d-system-overview/SKILL.md;
templates/html; templates/styles; _public/overview; test/test_generate_overview.py.

Stop when every deliverable exists in the worktree, D04-G is green, and the verification output
(including the regeneration diff) is pasted — or when a blocking finding is reported up.
```

### D04-C1 — creator: overview templates

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Build the overview template family: page and component templates under templates/html/ and a
matching stylesheet under templates/styles/, for a single self-contained overview page showing
the idea metrics (chart blocks fed by chart-ready JSON, each with a plain HTML table fallback per
docs/01-plans/PLAN-021-live-demo.md descope rung 1), the concepts/terminology inventory, and the
systems inventory. The page must be embeddable in the stage panel (no external network
dependencies; assets inline or repository-relative). Use sample outputs from the phase-demo-03
tools (already on dev) as the reference data shape.

Run in the worktree and paste real output: none required beyond rendering evidence — state which
template files exist and show a rendered sample via tools or a static open if the generator
(D04-C2) is not yet built.

Stop when the template family exists and its files are listed with the data shape they consume —
or report the blocking finding.
```

### D04-V1 — validator: templates

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-04 -- templates/

Requirement text: a self-contained overview page template family under templates/html/ and
templates/styles/ covering metrics charts with table fallbacks (descope rung 1), the
concepts/terminology inventory and the systems inventory; no external network dependency (no CDN
script or font URLs); consumes the phase-demo-03 tools' JSON shapes as-is.

Commands: grep the templates for http:// and https:// asset references; list the template files.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D04-C2 — creator: generate_overview.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Build tools/generate_overview.py: runs tools/overview_metrics.py and tools/overview_inventory.py
(as subprocesses or importable mains — do not reimplement their computation), renders the
templates/html/ + templates/styles/ overview family with their outputs, and writes the generated
page under _public/overview/. Deterministic end to end: generating twice against an unchanged
tree produces identical files (no generation timestamps). Add
test/test_generate_overview.py proving the double-generation identity and that a figure in the
page matches the metrics tool's output.

Run in the worktree and paste real output: uv run pytest test/test_generate_overview.py;
uv run ruff check src/ test/; uv run mypy src/.

Stop when the generator, generated page and tests exist and the commands' real output is
pasted — or report the blocking finding.
```

### D04-V2 — validator: generator

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-04 -- tools/generate_overview.py _public/overview test/test_generate_overview.py

Requirement text: REQ-006 row R08's mechanics — the generator calls the two phase-demo-03 tools
rather than recomputing their numbers (a reimplementation of any metric is a failing finding);
output lands under _public/overview/; double generation is byte-identical; a page figure equals
the tool output in the test.

Commands: uv run pytest test/test_generate_overview.py; uv run ruff check src/ test/;
uv run mypy src/; run the generator twice and diff _public/overview between runs.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D04-C3 — creator: the d-system-overview skill

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Write .claude/skills/d-system-overview/SKILL.md, following the shape of the repository's existing
skills (see .claude/skills/checkpoint/SKILL.md). The skill's procedure: run
tools/generate_overview.py, report the generated page location and the headline numbers the tools
emitted, and stop. It must instruct the agent running it to never recompute or adjust a number
the tools produced and never edit the generated page by hand (REQ-006 row R08); if generation
fails, the failure output is the result to report.

Run in the worktree and paste real output: uv run python -m src.governance.

Stop when the skill file exists and the command's real output is pasted — or report the blocking
finding.
```

### D04-V3 — validator: the skill

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-04 -- .claude/skills/d-system-overview/

Requirement text: REQ-006 row R08 — the skill orchestrates the deterministic scripts via
tools/generate_overview.py and contains no instruction to recompute, restate from memory, or
hand-edit any tool-owned number or the generated page; failing generation is reported, not
patched around.

Commands: none beyond reading the skill; quote the lines that satisfy or violate each obligation.

Stop when your verdict, findings and the quoted evidence are reported.
```

### D04-C4 — creator: OPS-014

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-docs. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this item).

Write docs/08-governance/OPS-014-generate-overview.md for tools/generate_overview.py. The code is
reserved in docs/08-governance/codes.yaml — use it exactly, and IN THE SAME CHANGE remove its
reservation entry from docs/08-governance/codes.yaml (the governance check rejects a document
carrying a still-reserved code), then regenerate the catalog:
uv run python -m src.governance --catalog > docs/08-governance/catalog.md. Follow the existing
OPS documents: governed front matter, hand-written narrative (what it runs, where output lands,
the determinism contract), empty generated block, then
uv run python tools/generate_tool_docs.py to fill it.

Run in the worktree and paste real output: uv run python tools/generate_tool_docs.py;
uv run python -m src.governance.

Stop when the document exists with a filled generated block and the commands' real output is
pasted — or report the blocking finding.
```

### D04-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this phase).

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: tools/generate_overview.py;
   docs/08-governance/OPS-014-generate-overview.md; .claude/skills/d-system-overview/SKILL.md;
   templates/html and templates/styles overview files; _public/overview generated page;
   test/test_generate_overview.py.
4. OPS-014 carries governed front matter, its allocated code, and a non-empty generated block;
   the OPS-014 reservation entry is removed from docs/08-governance/codes.yaml in this branch,
   and the regenerated catalog is committed.
5. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
6. Generating twice produces an identical _public/overview (paste the diff command and its empty
   result).
7. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D04-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed by this phase).

Adversarially review phase-demo-04 (overview skill, templates, generation). Assume it is broken;
find where it fails. Specifications: the phase's backlog entry; REQ-006 row R08; PLAN-021
descope rung 1. Attack at minimum: whether the generator recomputes any number the phase-demo-03
tools own (compare a rendered figure against the tool's own output on the real repository);
whether the double-generation identity holds because it is deterministic or because the test
compares too little; whether the skill instructs anything that edits the generated page or
restates numbers from model memory; whether the page truly has no external network dependency;
whether the table fallback exists and renders, or only the charts do; whether OPS-014 and the
skill describe what was built.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### D04-W — browser verification of the generated page (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-demo-04. Branch:
agent/phase-demo-04. Ports: backend 8010, frontend 5180 (not needed — this page is static).

Open the generated overview page under _public/overview/ in the worktree directly in the browser
(file:// is fine). Verify mechanically:

1. The page renders with no uncaught console errors and no failed network request to any
   non-local URL (browser_network_requests must show no external host).
2. Every metrics block renders either its chart or its table fallback — none renders empty.
3. Spot-check one figure: read the corresponding value from the phase-demo-03 tool's JSON output
   in the worktree and assert the page displays the same number.
4. The concepts/terminology and systems inventories are present and non-empty, and the systems
   count matches docs/08-governance/systems.yaml's entry count.
5. Screenshot the full page once at 1366x768.

Stop when every item has a recorded pass/fail with the measured evidence — or when the page does
not exist at the stated path, reported as a blocking finding.
```

---

## D05 — phase-demo-05: content, runbook, reset, rehearsals (orchestrator: `demo-orch-content`)

### D05-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-content. Phase: phase-demo-05 (demo content, runbook, reset tool and
rehearsals; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-01 through phase-demo-04 being integrated into dev AND marked status: complete by the
coordinator after each phase's adversarial-review + agentic-testing gate (the demo-track
completion decision in GOV-003) — confirm all four before claiming; the governance validator
rejects an active phase whose prerequisite is not complete.
Worktree: /code/d-system-worktrees/phase-demo-05. Branch: agent/phase-demo-05, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-05 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-content — your claim id as this orchestrator).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: D05-C1 then D05-V1; D05-C2 — each verbatim from PROMPT-018. At most two
   fix cycles per item, then report up. When a creator reports its item done, commit that item
   on the phase branch (narrow, one concern per commit) BEFORE dispatching its validator — the
   validator judges git diff dev...agent/phase-demo-05, which is empty until the work is
   committed.
4. Yourself (this is the one authoring task that is yours): write the final talking-points copy
   into ts/public/talking-points.json per D05-O, replacing the placeholders.
5. Dispatch D05-R (fresh-eyes rehearsal) twice, separated by uv run python tools/demo_reset.py
   prepare; record both runs'
   per-step times in the runbook.
6. Dispatch D05-G as the phase gate.
7. Run the phase's verification commands yourself in the worktree and paste real output:
   uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
8. Checkpoint progress. Report the Windows smoke check (REQ-006 R06) plainly as outstanding
   owner-machine work — it cannot run here. Do not mark the phase complete, do not integrate, do
   not push without asking.

Phase deliverables (verbatim from the backlog): ts/public/talking-points.json;
tools/demo_reset.py; docs/08-governance/OPS-013-demo-reset.md; docs/00-working/demo-runbook.md;
docs/00-working/demo-windows-setup.md.

Stop when every deliverable exists in the worktree, both rehearsal runs are recorded, D05-G is
green, and the verification output is pasted — or when a blocking finding is reported up.
```

### D05-C1 — creator: demo_reset.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180 (not needed by this item).

Build tools/demo_reset.py with two explicit subcommands, per the rehearsal gate
(docs/02-prompts/PROMPT-017-demo-rehearsal-gate.md):

- `prepare` — sets the stage for a rehearsal or the live run: regenerates the overview outputs
  via tools/generate_overview.py; clears demo scratch state (list explicitly in the tool what it
  clears); PARKS the pre-built overview skill (moves .claude/skills/d-system-overview/ aside to
  a parked location the tool owns); and SEEDS the fallback audience idea by running
  tools/append_idea.py IF an idea labelled as the fallback seed is not already present in the
  folded state (the sanctioned writer; appending is permitted — deleting or rewriting the log
  never is).
- `restore` — the fallback and post-segment action the runbook invokes by name: puts the parked
  pre-built skill back in place and regenerates the overview outputs from current data.

Contract to state in the tool's own help text: "pre-built state" means the pre-built SKILL is
back in place; the overview page is always regenerated from current data, which grows as ideas
are appended — the log is append-only, so byte-identical pre-rehearsal page output is
deliberately NOT the contract (PLAN-021's afterlife decision keeps demo-recorded ideas as real
work, and the page reflecting them is intended behavior).

Hard limits, enforced in code with an explicit path allowlist: it never deletes or rewrites
_data/ideas.jsonl or any file under docs/ except regenerated outputs it owns; its only idea-log
access is appending through tools/append_idea.py; it never touches _private/, .agents/, .codex/,
AGENTS.md or CLAUDE.md. Running either subcommand twice in a row is safe: a second `prepare`
reports nothing to do and seeds no duplicate idea; a second `restore` reports the skill already
in place. Add tests in the phase's test scope proving the allowlist refuses an out-of-scope
path, the prepare→restore round-trip returns the skill to its original content, the
no-duplicate-seed check, and both subcommands' double-run idempotence.

Run in the worktree and paste real output: uv run pytest; uv run ruff check src/ test/;
uv run mypy src/.

Stop when the tool and tests exist and the commands' real output is pasted — or report the
blocking finding.
```

### D05-V1 — validator: demo_reset.py

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-05 -- tools/demo_reset.py test/

Requirement text: the tool exposes two subcommands. `prepare` regenerates overview outputs,
clears scratch state, parks the pre-built overview skill, and seeds the fallback audience idea
only through tools/append_idea.py without duplicating it on a re-run. `restore` — a real,
separately invokable operation, not an internal test helper — puts the parked pre-built skill
back byte-identical and regenerates the outputs from current data. The tool's contract must
state that page content regenerates forward from the append-only log (byte-identical
pre-rehearsal page output is explicitly not claimed); a tool or test claiming to restore
pre-rehearsal page bytes is a failing finding, and so is a runbook-named restore capability that
does not exist. It can never delete or rewrite idea-log content, governed documents, _private/,
.agents/, .codex/, AGENTS.md or CLAUDE.md — the protection must be an explicit allowlist in
code, not a comment. Both subcommands double-run idempotent. Tests prove the refusal, the
prepare→restore skill round-trip, the no-duplicate seed, and both idempotences.

Commands: uv run pytest; uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D05-C2 — creator: OPS-013, runbook skeleton, Windows checklist

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-docs. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180 (not needed by this item).

Three documents:
1. docs/08-governance/OPS-013-demo-reset.md for tools/demo_reset.py — code reserved in
   docs/08-governance/codes.yaml; use it exactly, and IN THE SAME CHANGE remove the OPS-013
   reservation entry from docs/08-governance/codes.yaml (the governance check rejects a document
   carrying a still-reserved code), then regenerate the catalog:
   uv run python -m src.governance --catalog > docs/08-governance/catalog.md. Existing OPS
   shape; empty generated block filled by uv run python tools/generate_tool_docs.py.
2. docs/00-working/demo-runbook.md — ungoverned (no front matter, no code, per ADR-010's staging
   rules): the live-segment runbook skeleton with the step shape the rehearsal gate defines
   (docs/02-prompts/PROMPT-017-demo-rehearsal-gate.md): /orient → record an idea (/idea) →
   triage it (/idea-triage) → plan beat → overview-skill rebuild → test, one section per step.
   Each step carries: the exact commands it runs, its timebox (the column sums to at most 15
   minutes), and its fallback action — for every step, the same literal command: run
   `uv run python tools/demo_reset.py restore` and continue the narrative with the pre-built
   skill. The skeleton also carries: the
   descope ladder copied verbatim from docs/01-plans/PLAN-021-live-demo.md; empty dry-run
   recording tables for two rehearsals; a named line for the second dry-run's screen-recording
   path on the presentation machine (the recording is a rehearsal-gate deliverable); a marker on
   each step as CLI-executable (run by the D05-R rehearsal), browser-executable (run by the
   D05-W Playwright pass — page scroll, popup behavior, terminal rendering), or owner-performed
   (Windows-machine-only items); and a note that ideas
   recorded during rehearsal are permanent in the append-only log and must be labelled as
   rehearsal entries in their body text.
3. docs/00-working/demo-windows-setup.md — ungoverned: the Windows machine checklist from
   PLAN-021's demo-day operational requirements (clone location, uv and Node versions, pywinpty
   install, D_SYSTEM_DEMO_TERMINAL=1, ports 8010/5180, browser and zoom, the REQ-006 R06 smoke
   check with a result line to fill in, the pre-demo git tag step, screen hygiene).

Run in the worktree and paste real output: uv run python tools/generate_tool_docs.py;
uv run python -m src.governance.

Stop when the three documents exist (OPS-013 with a filled generated block) and the commands'
real output is pasted — or report the blocking finding.
```

### D05-O — orchestrator's own task: talking-points copy

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-content (you; do not delegate this item). Worktree:
/code/d-system-worktrees/phase-demo-05. Branch: agent/phase-demo-05. Ports: backend 8010,
frontend 5180.

Write the final talking-points copy into ts/public/talking-points.json, replacing every
placeholder. Source material: idea 000070's demo shape (read via fold(), never the raw log), the
live demo plan docs/01-plans/PLAN-021-live-demo.md, and the point the demo exists to land — the
separation between a skill, a command, a subagent and a tool, and why the owner-only decision
(/session-close) sits behind a command a person types. One entry per live-segment step plus an
opening and a closing entry; each entry short enough to read from a projector at a glance
(headline plus at most three supporting lines). Keep the data file's existing schema so the
rotator needs no code change. Plain, direct prose — no metaphor decoration; flag the copy for
owner review in your report.

Stop when the file carries final copy, the frontend build still passes (cd ts && npm run build),
and the copy is flagged for owner review — or report the blocking finding.
```

### D05-R — fresh-eyes rehearsal

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180.

Diff: none — this is a rehearsal, not a review.

Requirement text: docs/00-working/demo-runbook.md is the script; REQ-006 row R09
(docs/06-requirements/REQ-006-live-demo.md) is the contract: every step completes inside its
timebox and the whole segment inside 15 minutes. You have not seen this demo built; that is the
point. Follow the runbook exactly as written, cold: run each CLI-executable step's commands,
time each step (date +%s before and after), skip steps the runbook marks browser-executable
(covered by the D05-W Playwright pass) or owner-performed (record both kinds as
skipped-by-marking, with no time), and record what a presenter would have to explain
away — a confusing output, a step whose instructions do not match reality, a missing
precondition. Do not fix anything. Executing a runbook step whose command is the sanctioned idea
writer (tools/append_idea.py) or a generation tool is execution, not editing — run it as
written, labelling any idea you record as a rehearsal entry per the runbook; you still change no
file by hand.

Second-run note, overriding a literal reading of this prompt's opening clause for this dispatch
only: a rehearsal is a run, not a deliverable. When the dry-run tables already hold one run's
times, you are the second run — execute the runbook in full again rather than reporting nothing
missing.

Commands: exactly those the runbook states, in order, plus the timing wrappers.

Stop when you report per-step wall-clock times, the total, and the list of would-need-explaining
moments — an empty list is a complete result.
```

### D05-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: ts/public/talking-points.json (no placeholder markers remain —
   grep for TODO/PLACEHOLDER/lorem); tools/demo_reset.py;
   docs/08-governance/OPS-013-demo-reset.md; docs/00-working/demo-runbook.md;
   docs/00-working/demo-windows-setup.md.
4. OPS-013 carries governed front matter, its allocated code, and a non-empty generated block;
   the OPS-013 reservation entry is removed from docs/08-governance/codes.yaml in this branch,
   and the regenerated catalog is committed; the two docs/00-working/ documents carry no front
   matter and no code (they are ungoverned by design).
5. The runbook's timeboxes sum to at most 15 minutes; both dry-run tables carry recorded times;
   every step names its commands and its fallback action; the second dry-run's screen-recording
   path line exists; and each step is marked agent-executable or owner-performed.
6. The runbook contains the descope ladder verbatim from docs/01-plans/PLAN-021-live-demo.md
   (diff the four rungs' text).
7. The Windows checklist contains the REQ-006 R06 smoke-check step with its result line, the
   pre-demo git tag step, and the screen hygiene items.
8. uv run pytest passes.
9. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D05-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180.

Adversarially review phase-demo-05 (content, runbook, reset, rehearsals). Assume it is broken;
find where it fails. Specifications: the phase's backlog entry; REQ-006 row R09;
docs/02-prompts/PROMPT-017-demo-rehearsal-gate.md; PLAN-021's demo-day operational requirements.
Attack at minimum: whether demo_reset's allowlist is actually enforced in code (feed it an
out-of-scope path); whether park/restore of the overview skill round-trips and a double run
really seeds no duplicate idea; whether the runbook's steps would survive a presenter who knows
nothing (run one cold yourself); whether the recorded dry-run times are real measurements or
placeholders; whether the timeboxes sum as claimed; whether the talking-points copy contains
anything unfit for a projector (length, jargon, placeholder residue); whether the Windows
checklist verifies what PROMPT-017's gate expects rather than re-installing a completed setup.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### D05-W — rehearsal browser pass (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-demo-05. Branch:
agent/phase-demo-05. Ports: backend 8010, frontend 5180.

Companion to the D05-R command-line rehearsal: execute the runbook's browser-marked checks
against the full running stage. In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend
(cd ts && npm run dev -- --port 5180), then walk every runbook step marked browser-executable
in docs/00-working/demo-runbook.md, in order, timing each (assert timebox compliance), with the
mechanical assertions of D02-W (no page scroll, no overlap, popup behavior, terminal echo) plus
whatever the runbook step itself specifies. Record any moment a presenter would have to explain
away. Steps the runbook marks owner-performed (Windows-machine-only items) are recorded as
skipped-by-marking.

Stop each server you started. Stop when every browser-marked step has a recorded pass/fail with
timing and evidence — or when the stage cannot start, reported with the real startup output as a
blocking finding.
```

---

## D06 — phase-demo-06: stage terminal interaction (orchestrator: `demo-orch-stage`)

Added 2026-09-10 with the owner's approval of the phase-demo-06 insertion (GOV-003); REQ-006
rows R10–R12 govern.

### D06-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-demo-06 (stage terminal interaction — session tabs, guarded
drop, command injection; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md).
Depends on phase-demo-01 through phase-demo-04 being integrated into dev AND marked status:
complete — confirm before claiming.
Worktree: /code/d-system-worktrees/phase-demo-06. Branch: agent/phase-demo-06, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-06 per AGENTS.md in one small commit
   (status: active, agent: agent-demo-stage — your claim id as this orchestrator).
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install (worktree-local
   node_modules, never a symlink).
3. Dispatch, in order: D06-C1 then D06-V1; D06-C2 then D06-V2; D06-C3 then D06-V3 — each verbatim
   from PROMPT-018. At most two fix cycles per item, then report up. When a creator reports its
   item done, commit that item on the phase branch (narrow, one concern per commit) BEFORE
   dispatching its validator — the validator judges git diff dev...agent/phase-demo-06, which is
   empty until the work is committed.
4. Dispatch D06-G as the phase gate.
5. Run the phase's verification commands yourself in the worktree and paste real output:
   cd ts && npm run build; uv run pytest; uv run ruff check src/ test/; uv run mypy src/;
   uv run python -m src.governance; uv run python tools/check_no_private_content.py with the
   changes staged.
6. Checkpoint progress. Do not mark the phase complete, do not integrate, do not push without
   asking.

Phase deliverables (verbatim from the backlog): ts/src; ts/public/demo-commands.json;
src/api/routes/demo_terminal.py; test/test_demo_terminal.py.

Stop when every deliverable exists in the worktree, D06-G is green, and the verification output
is pasted — or when a blocking finding is reported up.
```

### D06-C1 — creator: websocket control frames (resize)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-py. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180 (not needed by this item).

Extend the terminal websocket route (src/api/routes/demo_terminal.py) to accept JSON text frames
as control messages alongside the existing binary input frames: replace the receive_bytes() loop
with receive() handling both frame kinds — binary bytes go to adapter.write() unchanged; a text
frame parsing as {"type": "resize", "cols": N, "rows": N} with positive integers calls
adapter.resize(cols, rows) (implemented but unused today, src/demo/posix.py TIOCSWINSZ); any
other or malformed text frame is ignored safely and never reaches the shell as input. No new
endpoints, one PTY per websocket, ADR-013's gating and loopback binding unchanged — do not touch
registration or enforce code.

Extend test/test_demo_terminal.py: a resize frame reaches the adapter (assert cols/rows applied
or the adapter method called); a malformed text frame neither crashes the session nor appears in
the shell's input; binary round-trip still works after a text frame; two concurrent websocket
sessions are independent shells.

Run in the worktree and paste real output: uv run pytest; uv run ruff check src/ test/;
uv run mypy src/.

Stop when the route change and tests exist and the commands' real output is pasted — or report
the blocking finding.
```

### D06-V1 — validator: control frames

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180 (not needed by this item).

Diff: git diff dev...agent/phase-demo-06 -- src/api/routes/demo_terminal.py test/test_demo_terminal.py

Requirement text: the websocket route accepts binary frames as raw shell input (unchanged) and
JSON text frames as control messages; {"type":"resize","cols":N,"rows":N} calls the adapter's
resize; malformed or unknown text frames are ignored and never written to the shell — a text
frame reaching adapter.write() is a failing finding. No new endpoints; registration gating and
the loopback fail-fast are untouched; one PTY per websocket. Tests cover resize reaching the
adapter, malformed-frame safety, binary round-trip after a text frame, and two independent
concurrent sessions.

Commands: uv run pytest; uv run ruff check src/ test/; uv run mypy src/.

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D06-C2 — creator: session tabs, collapse, guarded drop

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Rework the terminal region in ts/src/stage/ per REQ-006 rows R10 and R11:

- Session tabs: the region hosts up to four terminal sessions as tabs (tab bar in the region
  header: one control per session plus a new-tab control, disabled at the cap). Each session is
  its own TerminalRegion instance over its own websocket. Every session's component stays
  mounted; inactive tabs are CSS-hidden — switching tabs must never close a socket. Guard the
  ResizeObserver/fitAddon.fit() path against zero-size containers and refit on tab activation
  (TerminalRegion.tsx currently fits unconditionally). On fit, send the D06-C1 resize control
  frame ({"type":"resize","cols":N,"rows":N}) over the socket.
- Collapse: a control that hides the whole terminal region via CSS and the existing
  --no-terminal grid reflow, leaving every socket open; re-expanding refits and shows the same
  sessions.
- Guarded drop: the existing descope toggle (rung 4) keeps its unmount-and-terminate behavior
  but only after an explicit confirmation step (reuse the portaled Popover with a clearly
  labelled confirm action). Closing an individual tab gets the same confirm. Nothing terminates
  before the confirm; everything the confirm names terminates after it.

Zero-scroll (REQ-006 R02) must hold at 1280x720, 1366x768, 1920x1080 and 1024x768 with 1-4 tabs,
collapsed and expanded.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when tabs, collapse, the guarded drop and the resize frame sending exist and the build
output is pasted — or report the blocking finding.
```

### D06-V2 — validator: tabs and guards

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-06 -- ts/

Requirement text: REQ-006 rows R10 and R11. Check the code implements: up to four session tabs,
each an independent websocket; every session component stays mounted with inactive tabs
CSS-hidden — a conditional render that unmounts on tab switch is a failing finding; the fit path
guarded against zero-size containers, refit on activation, resize control frame sent on fit;
collapse hides the region without closing any socket; the drop control and per-tab close each
require an explicit confirm before termination — a code path that terminates a session without
passing through the confirm is a failing finding; a fifth tab cannot be created.

Commands: cd ts && npm run build.

Stop when your verdict, findings and the command's verbatim output are reported.
```

### D06-C3 — creator: command panel and injection

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-creator-web. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Build the command panel per REQ-006 row R12: an in-place reveal within the terminal region
header (the three-region layout contract R01/R02 is untouched). Entries load from
ts/public/demo-commands.json — create it with clearly-placeholder entries of shape
{"label": ..., "command": ..., "run": false} (final content is authored in phase-demo-05; never
write real demo commands into page code — editing the JSON must change the list with no
rebuild). Selecting an entry sends its command text into the ACTIVE tab's websocket — through
the socket (the shell's echo paints it), never term.write() — without a trailing newline, so it
lands on the input line un-executed; entries with run true append a newline. Expose the active
terminal's send via a ref-based imperative handle from TerminalRegion (the repo's prop-drilling
style; no new state library). When the terminal route is absent, the panel renders disabled
alongside the existing absent-terminal message and nothing errors.

Run in the worktree and paste real output: cd ts && npm run build.

Stop when the panel, its data file, the injection path and the absent-state degrade exist and
the build output is pasted — or report the blocking finding.
```

### D06-V3 — validator: command panel

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-code. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Diff: git diff dev...agent/phase-demo-06 -- ts/

Requirement text: REQ-006 row R12. The panel's entries come only from
ts/public/demo-commands.json — command text hardcoded in a component is a failing finding;
injection goes through the active tab's websocket send, not term.write() — a term.write()
injection is a failing finding; no trailing newline unless the entry sets run true; the panel is
an in-place reveal inside the terminal region (no fourth page region); it degrades without
errors when the terminal route is absent.

Commands: cd ts && npm run build; grep ts/src for each placeholder command string from
demo-commands.json (none may appear in components).

Stop when your verdict, findings and the commands' verbatim output are reported.
```

### D06-G — phase gate

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-check. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Checklist:
1. uv run python -m src.governance exits 0 (paste the summary line).
2. git add -A, then uv run python tools/check_no_private_content.py passes with changes staged.
3. Every phase deliverable exists: the ts/src tab/collapse/drop/panel changes;
   ts/public/demo-commands.json; the src/api/routes/demo_terminal.py control-frame handling;
   test/test_demo_terminal.py extensions.
4. cd ts && npm run build passes; uv run pytest passes; uv run ruff check src/ test/ passes;
   uv run mypy src/ passes.
5. grep confirms no demo-commands.json command string appears inside ts/src.
6. The diff against dev touches nothing outside the phase's deliverable paths plus the standard
   checkpoint files (session record, backlog entry, catalog).

Stop when every item has a recorded real result and the overall verdict is stated.
```

### D06-A — adversarial review (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-adversary. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

Adversarially review phase-demo-06 (stage terminal interaction). Assume it is broken; find where
it fails. Specifications: the phase's backlog entry; REQ-006 rows R10-R12; ADR-013. Attack at
minimum: whether a hidden tab's socket actually stays open or the CSS hide still unmounts;
whether dropped or closed sessions genuinely terminate their shell processes — hunt for orphaned
PTYs after a confirmed drop, a page reload, and a websocket error; whether any termination path
bypasses the confirm; whether the fifth-tab cap can be defeated; whether injection can target
the wrong tab or a dropped session; whether a crafted demo-commands.json entry (quotes,
backticks, control characters) breaks injection or executes despite run false; whether a resize
control frame can be forged as shell input or shell output can forge a control frame; whether
ADR-013's gating and loopback enforcement survived the route change unmodified; whether
zero-scroll still holds structurally with four tabs and the panel open. Run commands to turn
suspicion into evidence.

Stop when your ranked findings (blocker/major/minor, each with file:line and a concrete failure
scenario) or the explicit statement that none survived, plus supporting output, are reported.
```

### D06-W — browser verification (dispatched by the coordinator, PROMPT-015 step 8)

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-validator-web. Worktree: /code/d-system-worktrees/phase-demo-06. Branch:
agent/phase-demo-06. Ports: backend 8010, frontend 5180.

In the worktree, start the backend with the terminal enabled
(D_SYSTEM_DEMO_TERMINAL=1 uv run uvicorn src.main:app --port 8010) and the frontend
(cd ts && npm run dev -- --port 5180, proxy configured for :8010). Then verify mechanically:

1. Session persistence (R10): open a second tab; in tab 1 run a long-lived command (e.g.
   sleep 300 &, then echo marker-1); switch to tab 2, run echo marker-2; switch back and assert
   tab 1's scrollback still shows marker-1; collapse and re-expand the region and assert both
   tabs' content survives; assert the new-tab control refuses a fifth tab.
2. Guards (R11): activate the drop control and assert nothing terminates before its confirm;
   confirm and assert the sessions genuinely end; reopen, close one tab through its confirm and
   assert only that tab's session ended.
3. Injection (R12): open the command panel, select an entry and assert its text appears on the
   active tab's input line un-executed; press Enter and assert it executes; select a run true
   entry and assert it executes on selection; edit ts/public/demo-commands.json, reload, and
   assert the list changed.
4. Zero-scroll (R02): at 1280x720, 1366x768, 1920x1080 and 1024x768, with four tabs open and
   the command panel open and closed: document scrollHeight <= viewport height and no two
   region bounding boxes intersect. Screenshot each size once.
5. Restart the backend WITHOUT the flag and assert the absent-terminal message renders and the
   command panel is disabled with no console errors.
6. browser_console_messages shows no uncaught errors across the above.

Stop each server you started. Stop when every item has a recorded pass/fail with the measured
evidence — or when the stage cannot start, reported with the real startup output as a blocking
finding.
```
