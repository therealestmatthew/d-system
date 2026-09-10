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
   agent: demo-orch-stage, catalog updated date) in one small commit; the governance run must
   accept the claim.
2. Create the worktree at the path above and set it up: uv venv && uv sync --extra dev.
3. Dispatch, in order: D01-C1 then D01-V1; D01-C2 then D01-V2; D01-C3 then D01-V3 — each prompt
   verbatim from PROMPT-018 (docs/02-prompts/PROMPT-018-demo-build-delegation-pack.md). At most
   two fix cycles per item, then report up.
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
(404), not exist-but-refuse. Document in the route module that the demo server is started bound
to 127.0.0.1. Declare pywinpty as a Windows-only optional dependency in pyproject.toml
(sys_platform == 'win32') and update uv.lock.

Extend test/test_demo_terminal.py: with the flag unset the route returns 404; with the flag set,
a websocket client sends a command and receives its output (FastAPI TestClient supports websocket
testing).

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
the src/demo adapter; pywinpty is optional and Windows-only in pyproject.toml; tests prove both
the absent-by-default state and a command round-trip with the flag set. The diff must not touch
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

---

## D02 — phase-demo-02: stage frontend (orchestrator: `demo-orch-stage`)

### D02-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-stage. Phase: phase-demo-02 (build the stage frontend with the zero-scroll
layout; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-01 being integrated into dev — confirm that before claiming.
Worktree: /code/d-system-worktrees/phase-demo-02. Branch: agent/phase-demo-02, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-02 per AGENTS.md in one small commit.
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install (worktree-local
   node_modules, never a symlink).
3. Dispatch, in order: D02-C1 then D02-V1; D02-C2 then D02-V2; D02-C3 then D02-V3 — each verbatim
   from PROMPT-018. At most two fix cycles per item, then report up.
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
the phase-demo-01 websocket route through the Vite proxy (backend on 8010; adjust the dev proxy
target accordingly, keeping the /api path convention). When the terminal route is absent — the
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
terminal resizes with its region; proxy targets port 8010, never 8000. xterm.js appears in
ts/package.json and ts/package-lock.json.

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

1. On an up-to-date dev in /code/d-system, claim phase-demo-03 per AGENTS.md in one small commit.
   This phase may run in parallel with phase-demo-01; its systems are disjoint.
2. Create the worktree; uv venv && uv sync --extra dev.
3. Dispatch, in order: D03-C1 then D03-V1; D03-C2 then D03-V2; D03-C3 — each verbatim from
   PROMPT-018. At most two fix cycles per item, then report up.
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
are already reserved in docs/08-governance/codes.yaml — use them exactly. Follow the repository's
existing OPS documents for front matter and shape: hand-written narrative (what the tool reads,
what it emits, its determinism contract), an empty <!-- generated:tool-reference:start/end -->
block, then run uv run python tools/generate_tool_docs.py to fill it.

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
4. Both OPS documents carry governed front matter, their reserved codes, and non-empty generated
   tool-reference blocks.
5. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
6. Each tool run twice produces byte-identical output (paste the diff commands and their empty
   results).
7. grep both tools for network or model-API imports (requests, httpx, anthropic, openai) — none
   present.
8. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

---

## D04 — phase-demo-04: overview skill, templates, generation (orchestrator: `demo-orch-data`)

### D04-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-data. Phase: phase-demo-04 (build the overview skill, templates and page
generation; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-03 being integrated into dev — confirm that before claiming.
Worktree: /code/d-system-worktrees/phase-demo-04. Branch: agent/phase-demo-04, from dev.
Ports: backend 8010, frontend 5180 (not needed by this phase).

1. On an up-to-date dev in /code/d-system, claim phase-demo-04 per AGENTS.md in one small commit.
2. Create the worktree; uv venv && uv sync --extra dev.
3. Dispatch, in order: D04-C1 then D04-V1; D04-C2 then D04-V2; D04-C3 then D04-V3; D04-C4 — each
   verbatim from PROMPT-018. At most two fix cycles per item, then report up.
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
reserved in docs/08-governance/codes.yaml — use it exactly. Follow the existing OPS documents:
governed front matter, hand-written narrative (what it runs, where output lands, the determinism
contract), empty generated block, then uv run python tools/generate_tool_docs.py to fill it.

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
4. OPS-014 carries governed front matter, its reserved code, and a non-empty generated block.
5. uv run pytest passes; uv run ruff check src/ test/ passes; uv run mypy src/ passes.
6. Generating twice produces an identical _public/overview (paste the diff command and its empty
   result).
7. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```

---

## D05 — phase-demo-05: content, runbook, reset, rehearsals (orchestrator: `demo-orch-content`)

### D05-K — kickoff

```
Assess the current state of the worktree and repository against the deliverables below; do only
what is missing; report what already existed.

Agent: demo-orch-content. Phase: phase-demo-05 (demo content, runbook, reset tool and
rehearsals; see docs/09-backlog/backlog.yaml and docs/01-plans/PLAN-021-live-demo.md). Depends on
phase-demo-01 through phase-demo-04 being integrated into dev — confirm that before claiming.
Worktree: /code/d-system-worktrees/phase-demo-05. Branch: agent/phase-demo-05, from dev.
Ports: backend 8010, frontend 5180.

1. On an up-to-date dev in /code/d-system, claim phase-demo-05 per AGENTS.md in one small commit.
2. Create the worktree; uv venv && uv sync --extra dev; cd ts && npm install.
3. Dispatch, in order: D05-C1 then D05-V1; D05-C2 — each verbatim from PROMPT-018. At most two
   fix cycles per item, then report up.
4. Yourself (this is the one authoring task that is yours): write the final talking-points copy
   into ts/public/talking-points.json per D05-O, replacing the placeholders.
5. Dispatch D05-R (fresh-eyes rehearsal) twice, separated by a demo reset; record both runs'
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

Build tools/demo_reset.py: returns demo-visible state to the rehearsed baseline — regenerates the
overview outputs via tools/generate_overview.py and clears demo scratch state (list explicitly in
the tool what it clears). Hard limits, enforced in code with an explicit path allowlist: it never
deletes or rewrites _data/ideas.jsonl or any file under docs/ except regenerated outputs it owns;
it never touches _private/, .agents/, .codex/, AGENTS.md or CLAUDE.md; running it twice in a row
is safe and the second run reports nothing to do. Add tests in the phase's test scope proving the
allowlist refuses an out-of-scope path and the double-run is idempotent.

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

Requirement text: the reset restores the rehearsed baseline (regenerated overview outputs,
cleared scratch state) and can never touch idea-log history, governed documents, _private/,
.agents/, .codex/, AGENTS.md or CLAUDE.md — the protection must be an explicit allowlist in
code, not a comment. Double-run idempotent. Tests prove the refusal and the idempotence.

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
   docs/08-governance/codes.yaml; existing OPS shape; empty generated block filled by
   uv run python tools/generate_tool_docs.py.
2. docs/00-working/demo-runbook.md — ungoverned (no front matter, no code, per ADR-010's staging
   rules): the live-segment runbook skeleton with the five steps from idea 000070
   (orient, record an idea, triage it, metrics, idea-to-plan) as sections, a per-step timebox
   column summing to at most 15 minutes, the descope ladder copied verbatim from
   docs/01-plans/PLAN-021-live-demo.md, and empty dry-run recording tables for two rehearsals.
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
point. Follow the runbook exactly as written, cold: run each step's commands, time each step
(date +%s before and after), and record what a presenter would have to explain away — a
confusing output, a step whose instructions do not match reality, a missing precondition. Do not
fix anything.

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
4. OPS-013 carries governed front matter, its reserved code, and a non-empty generated block; the
   two docs/00-working/ documents carry no front matter and no code (they are ungoverned by
   design).
5. The runbook's timeboxes sum to at most 15 minutes and both dry-run tables carry recorded
   times.
6. The runbook contains the descope ladder verbatim from docs/01-plans/PLAN-021-live-demo.md
   (diff the four rungs' text).
7. The Windows checklist contains the REQ-006 R06 smoke-check step with its result line, the
   pre-demo git tag step, and the screen hygiene items.
8. uv run pytest passes.
9. The diff against dev touches nothing outside the phase's deliverable paths.

Stop when every item has a recorded real result and the overall verdict is stated.
```
