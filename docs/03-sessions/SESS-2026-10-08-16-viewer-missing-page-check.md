---
schema_version: 1
id: doc-session-viewer-missing-page-check
code: SESS-2026-10-08-16
title: Report a missing HTML Viewer page when the file route is absent (phase-wbf-16)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-viewer]
depends_on: [doc-workbench-features-defects-requirements]
---

# Report a missing HTML Viewer page when the file route is absent (phase-wbf-16)

## Phase

`phase-wbf-16` (report a missing HTML Viewer page when the file route is absent), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md), recorded as idea 000555. Builder A
(`agent-builder-a`) under the Session Manager's pre-approved run of 2026-10-08. Branch
`agent/phase-wbf-16`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`.

## Reproduction (before the change, Linux)

Dev server on Vite port 5196 (API 8026) with `D_SYSTEM_DEMO_TERMINAL` unset in the frontend process,
and a viewer tab holding `README.md` stored under `d-system:workbench-state:v3`, loaded in headless
Chromium through Playwright.

- `HEAD /workbench-file/README.md` answered `200 OK`, `Content-Type: text/html`, no
  `Content-Security-Policy` header. `GET /workbench-file/README.md?v=0` returned the application
  shell (`<!doctype html>` with `/@react-refresh` and `/@vite/client` scripts).
- The viewer sent two HEADs, treated `200` as ready, and framed
  `/workbench-file/README.md?v=0` in the iframe. The panel showed no absent-page message.
- With the flag set to `1`: `HEAD /workbench-file/README.md` answered `200`,
  `Content-Type: text/html; charset=utf-8`, `Cache-Control: no-store`,
  `Content-Security-Policy: sandbox`. A HEAD for a file that does not exist answered `404 Not Found`
  with no such header.

## Outcome

Discriminator: the `Content-Security-Policy: sandbox` response header. Reason: `serveRepositoryFiles`
(`ts/vite.config.ts`) sets it unconditionally on every response that serves a file, for every file
type (`.html`, `.md`, images), before any branch on file type; the dev server's single-page fallback
never sets it; and the header is readable by script because the request is same-origin. It needed no
change to `ts/vite.config.ts`. The 403 and 404 refusals do not carry it and are not `ok` anyway.

`ts/src/stage/HtmlViewerRegion.tsx`: a new `isServedByFileRoute(response)` returns true only for an
`ok` response whose `Content-Security-Policy` header has a `sandbox` directive. The existence check
sets `ready` on that and `missing` otherwise, so the absent-page message shows and no iframe renders.
A network failure is still `error`. `OverviewRegion.tsx` was left alone, as the scope says.

`ts/src/stage/HtmlViewerRegion.test.tsx` (new, six tests): an ok response without the header gives
the absent-page message and no iframe; an ok response with a different Content-Security-Policy value
does the same; `.html`, `.md` and image selections served with the header still frame
`/workbench-file/<path>`; a 404 still shows the absent-page message. The first two fail against the
unmodified component (checked by stashing the change) and pass with it.

## Deliverable widening, for the Session Manager

`HtmlViewerRegion.doubleClick.test.tsx` and `HtmlViewerRegion.openFiles.test.tsx` stub the file route
as `200` with no headers, which is exactly the response the viewer must now treat as absent, so five
of their tests failed after the change. Each stub now returns `Content-Security-Policy: sandbox`, a
three-line edit in each file, no assertion changed. Both files are outside the phase's declared
deliverables; the phase's own acceptance ("the .html, .md and image cases are unchanged") and its
`npm test` verification cannot pass without them. Awaiting the Session Manager's ratification of the
widening (pre-approved run, 2026-10-08).

## Acceptance

- REQ-012 R29, flag unset: met. The viewer panel read "Selected page is absent - README.md does not
  exist.", zero iframes, and the only requests were two HEADs (no GET of the shell).
- REQ-012 R29, flag set: met. The same stored tab produced one iframe on
  `/workbench-file/README.md?v=0` whose document body begins with the README's rendered text, not the
  shell. `.html`, `.md` and image cases are covered by the new vitest cases and the two existing
  files (passing).

## Verification and gate checks

- `cd ts && npm test`: 9 files, 95 tests passed. `cd ts && npm run build`: built, no errors (the
  chunk-size warning predates this phase).
- `uv run python -m src.governance`: Governance OK before the session record.
- `uv run ruff check src/ test/ tools/`: All checks passed. `uv run mypy src/`: no issues in 52
  source files.
- `uv run pytest -q`: `1 failed, 2059 passed, 1 skipped in 367.52s`. The one failure is
  `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` (idea 000604): it
  relies on `chmod 0o500` blocking directory creation and this sandbox runs as uid 0. This phase
  touched no Python; the test was not retried or skipped.
- Owner-machine cells (Windows browsers, CMD, PowerShell): not run.

## Unresolved and assumptions

- Assumption: Linux Chromium only; no other browser exercised.
- Commit trailers follow the builder contract's text (`Claude Fable 5.1`), as the claim commit does;
  the session's attribution reminder names `Claude Sonnet 5.5`. The session URL line is identical.
  Left for the Session Manager to rule on.
