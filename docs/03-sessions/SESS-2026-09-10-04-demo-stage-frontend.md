---
schema_version: 1
id: doc-session-demo-stage-frontend
code: SESS-2026-09-10-04
title: Demo stage orchestration — stage frontend with the zero-scroll layout (phase-demo-02)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage]
depends_on: [doc-live-demo, doc-prompt-demo-build-delegation-pack]
---

# Demo stage orchestration — stage frontend with the zero-scroll layout (phase-demo-02)

## Phase

`phase-demo-02` — Build the stage frontend with the zero-scroll layout.

## Verification

- `cd ts && npm run build` — `tsc -b && vite build` succeeds; `dist/index.html`,
  `dist/assets/index-CDZLIbzy.css` (10.32 kB), `dist/assets/index-CHL-p1qz.js` (489.20 kB); built
  in under 1s.
- `uv run pytest` — `2 failed, 456 passed, 2 warnings`. Both failures investigated and neither is
  a defect introduced by this phase's diff (`ts/` only); see `## Unresolved`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 132 documents, 15 memories, 110
  backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (413 tracked files, 0 identifiers checked)`.
- Adversarial review (D02-A) and Playwright browser verification (D02-W) — not yet dispatched. Per
  `PROMPT-018`'s completion-gate convention and `GOV-003`'s demo-track completion decision, both
  are dispatched by the build coordinator at `PROMPT-015` step 8, not by this orchestrator.

Item-level dispatch history (creator/validator pairs from `PROMPT-018`):

- D02-C1 (zero-scroll stage layout, `ts/src/stage/`) — built from scratch: `StagePage.tsx`/`.css`
  (three-region CSS grid, `minmax(0,...)` tracks, `overflow:hidden` on `html`/`body`), placeholder
  `TerminalRegion`/`TalkingPointsRegion`/`OverviewRegion`, reusable `Tooltip` (hover) and `Popover`
  (click-dismissible) components, and the two descope-ladder toggles (overview open-in-tab / rung
  3, terminal hidden / rung 4) as `useState` in `StagePage`. `npm run build` clean. D02-V1: PASS —
  build clean; layout mechanics for R01-R03 sound by inspection; flagged (not scored as a failure)
  that R01's actual content — live terminal, data-file rotator, real overview embed — is correctly
  deferred to D02-C2/C3 per the dispatch's own item split; flagged a risk (unconfirmed) that
  `.stage-region__body`'s `overflow:hidden` with no internal scroll fallback could clip a reveal
  control if content overflows its slot at a given size — left for D02-W's Playwright check.
- D02-C2 (xterm.js terminal wiring) — added `@xterm/xterm` and `@xterm/addon-fit`; rewired
  `TerminalRegion` to mount a real `Terminal` only when the backend reports `terminal_enabled`,
  piping I/O over a websocket at `/api/v1/demo/terminal/ws`, with a `ResizeObserver` calling
  `fitAddon.fit()` on every container resize. `ts/vite.config.ts` proxy target made configurable
  via `VITE_API_TARGET` (default unchanged at `:8000`, `ws: true` added for the upgrade). `npm run
  build` clean; `npm run lint` (`tsc --noEmit`) clean. Flagged a known gap: the backend route
  (`src/api/routes/demo_terminal.py`, outside this item's deliverable paths) has no resize message
  channel, so PTY rows/cols are never told about a resize — `fitAddon.fit()` is client-side/visual
  only. D02-V2: PASS — no findings; confirmed the proxy default is untouched and no `:8010`
  hardcode exists anywhere in the diff; build output pasted.
- D02-C3 (talking-points rotator and overview panel) — added `ts/public/talking-points.json`
  (five clearly-labeled placeholder entries — real copy is phase-demo-05's); rewrote
  `TalkingPointsRegion` to fetch `/api/v1/demo/stage/talking-points` at runtime (editing the JSON
  changes the panel with no rebuild), with manual next/previous, an off-by-default 6s
  auto-advance, and a rung-2 static-list degrade that drops the fade transition and the controls
  entirely. Rewrote `OverviewRegion` to fetch `/api/v1/demo/stage/overview-location` and embed via
  `<iframe>` (rung-3 fallback: open-in-tab link) wired to the existing `StagePage` toggle; added a
  `serveGeneratedOverview` Vite dev-server middleware to `vite.config.ts` serving `_public/` at
  `/generated-overview/*` with path-traversal rejection and a real 404 — stated explicitly why
  Vite's built-in `/@fs/` route was rejected (it falls through to `index.html` on a missing file,
  risking a silent iframe self-recursion instead of the required absent-page message). `npm run
  build` clean; runtime-verified against the real backend on 8010/frontend on 5180 (talking-points
  fetch, overview-location present/absent paths, 403 on traversal). D02-V3: PASS — no findings;
  confirmed no talking-points copy string appears anywhere in `ts/src` outside the data file.
- D02-G (phase gate) — dispatched once. FAIL on the pytest item only; all other items (governance,
  staged private-content check, deliverable existence, no-hardcoded-copy grep, diff-scope-to-`ts/`)
  passed. This orchestrator independently reproduced both pytest failures (see `## Unresolved`)
  and traced them to causes outside this item's own scope rather than re-dispatching a second gate
  attempt against an unrelated pre-existing/cross-phase condition.

## Acceptance

- No page scrollbar and no overlapping elements at 1280x720, 1366x768, 1920x1080 and 1024x768,
  hidden content reachable in place (REQ-006 R02) — Not yet confirmed. The CSS/JS mechanics exist
  (D02-C1/D02-V1) but no browser has rendered the page at any of the four sizes in this session;
  that measurement is D02-W's (Playwright), owned by the coordinator.
- A command typed in the embedded terminal against a flag-enabled backend returns real shell
  output end to end — Not yet confirmed for the same reason: the mechanism is built and
  code-reviewed (D02-C2/D02-V2) but not exercised in a live browser round-trip in this session.
- Editing the talking-points data file changes the rotator content without a change to page code —
  Met. `TalkingPointsRegion` reads only `/api/v1/demo/stage/talking-points`, which streams
  `ts/public/talking-points.json` unchanged; D02-V3 confirmed no hardcoded copy in `ts/src`, and
  this orchestrator's own runtime check (during D02-C3's dispatch) confirmed the route serves the
  file's live content.
- Adversarial review (D02-A) and Playwright browser verification (D02-W) — Not met / not yet run.
  Both are owned by the build coordinator per `GOV-003`'s demo-track completion gate, not this
  orchestrator.

## Backlog

- `phase-demo-02`: `status: active`, `agent: agent-demo-stage`.
- `next_action`: Resolve the two `uv run pytest` failures reported below (one pre-existing
  catalog-drift condition on `dev`, one a genuine cross-phase conflict between this phase's
  `ts/public/talking-points.json` deliverable and a phase-demo-01 test's absence assumption) with
  the coordinator, then dispatch D02-A and D02-W (coordinator-owned) before requesting the owner's
  approval to integrate `agent/phase-demo-02` into `dev`.

## Unresolved

- `uv run pytest` fails `test/test_codes.py::test_committed_catalog_matches_regenerated_output`.
  Reproduced identically on plain `dev` (stashed this phase's worktree changes and re-ran in the
  primary checkout at `/code/d-system`) — pre-existing catalog drift on `dev`, not introduced by
  this phase's diff (which touches only `ts/`). Reported up rather than fixed, since regenerating
  and committing `docs/08-governance/catalog.md` is outside this phase's declared deliverable
  paths and outside this orchestrator's authority to fix on `dev` unilaterally.
- `uv run pytest` fails `test/test_demo_terminal.py::test_get_talking_points_defaults_to_ts_public_location`,
  which asserts that with no path override, `GET /api/v1/demo/stage/talking-points` 404s because
  `ts/public/talking-points.json` is genuinely absent by default — a phase-demo-01 assumption
  written before phase-demo-02 existed. `phase-demo-02`'s own backlog deliverable list requires
  `ts/public/talking-points.json` to exist (D02-C3's dispatch: "create that file with
  clearly-placeholder entries"), which the test now contradicts by construction. This is a
  prompt/reality mismatch between the two phases' declared deliverables, not a defect in this
  phase's diff or an item this orchestrator can fix without authoring a change to
  `test/test_demo_terminal.py` — outside `phase-demo-02`'s deliverable paths (`ts/src`;
  `ts/package.json`; `ts/package-lock.json`; `ts/public/talking-points.json`) and outside the
  scope of any prompt in `PROMPT-018`. Reported up to the coordinator rather than improvised.
- D02-A (adversarial review) and D02-W (Playwright browser verification), and integration into
  `dev`, are all outstanding and require the coordinator/owner, not this orchestrator, to proceed.
