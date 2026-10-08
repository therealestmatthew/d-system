---
schema_version: 1
id: doc-session-viewer-tab-double-click
code: SESS-2026-10-08-10
title: Open a viewer tab's file in a new browser tab on double-click (phase-wbf-01)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui]
depends_on: [doc-workbench-features-defects-requirements]
---

# Open a viewer tab's file in a new browser tab on double-click (phase-wbf-01)

## Phase

`phase-wbf-01` (open a viewer tab's file in a new browser tab on double-click), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Standby builder
(`agent-standby`) under the Session Manager's pre-approved run of 2026-10-08. Branch
`agent/phase-wbf-01`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`.

## Confirmation first: markdown already renders at the new-tab URL

The phase's `next_action` asked whether route-side markdown rendering already makes a new-tab open
correct. It does, so no rendering code was added. `ts/vite.config.ts`'s `serveRepositoryFiles`
renders `.md` with `marked` at `/workbench-file/` (idea 000119's ruling, delivered 2026-09-14) and
wraps raster images in a small HTML page; it sets `Content-Security-Policy: sandbox` on every
response. The new build only calls that URL.

## Outcome

`ts/src/stage/HtmlViewerRegion.tsx`:

- Double-clicking a viewer tab calls `window.open(url, '_blank', 'noopener,noreferrer')` with
  `/workbench-file/<that tab's file>`, the same URL as the "Open page in a new tab" link (one
  `fileHref` helper builds both). It opens the double-clicked tab's own file, whether or not that
  tab was active. A tab with no file selected does nothing.
- Keyboard equivalent (my choice, stated): Shift+Enter or Shift+Space on a focused tab. Plain
  Enter and Space still select the tab. The tab carries `aria-keyshortcuts` and a `title` naming
  both paths.
- Single-click selection, the close button and the Embedded / Open-in-tab toggle are unchanged. No
  slot, panel, region or layout identifier was renamed. Nothing outside `serveRepositoryFiles`
  reads the file (R02): the new code only builds a URL.

`ts/src/stage/HtmlViewerRegion.doubleClick.test.tsx` (new): five tests with `window.open` as a spy.
Each tab opens its own URL whichever tab is active; the URL equals the Open-in-tab link's `href`; an
empty tab does nothing; single click and close are unchanged and open nothing; Shift+Enter and
Shift+Space open but plain Enter and Space do not.

## Deliverable widening, for the Session Manager

The phase lists `ts/src/stage/HtmlViewerRegion.tsx` only. The vitest file above is outside it, as
the dispatch anticipated. The deliverable needs widening by
`ts/src/stage/HtmlViewerRegion.doubleClick.test.tsx`, which the Session Manager applies on the
trunk at completion.

## Acceptance

- REQ-012 R01: met. Playwright (below) opened `.html`, `.md` and `.png` tabs in new browser tabs;
  the contents are the rendered page, not raw source.
- REQ-012 R02: met. The response of each new-tab document carries `Content-Security-Policy: sandbox`
  with no tokens, and the new tab's origin is opaque (`localStorage` throws). No new code path reads
  a file.

## Playwright pass

Run on API port 8017 and Vite port 5187 with `D_SYSTEM_DEMO_TERMINAL=1`, Chromium headless,
1280x720. Three viewer tabs were seeded through the ADR-016 storage key:
`_public/d-system-architecture.html`, `docs/README.md`, `content/posts/002-the-idea-log/image.png`.
Exercised, per tab: select it, double-click it, read the new browser tab.

| Tab file | New tab URL | Content | Response header |
|---|---|---|---|
| `.html` | `/workbench-file/_public/d-system-architecture.html` | title "D-System - Proposed Knowledge Architecture", 14 headings | `Content-Security-Policy: sandbox`, `text/html` |
| `.md` | `/workbench-file/docs/README.md` | title "README.md", 2 headings, text does not start with `# ` | `Content-Security-Policy: sandbox`, `text/html` |
| `.png` | `/workbench-file/content/posts/002-the-idea-log/image.png` | wrapper page with one `<img>` | `Content-Security-Policy: sandbox`, `text/html` |

Also: Shift+Enter on the focused Tab 2 opened `/workbench-file/docs/README.md`; a single click on
Tab 3 selected it and opened no new browser tab. Not exercised: comparing the new tab's pixels with
the panel's (the panel iframe and the new tab load the identical URL); the owner-machine browsers.

Finding from the first Playwright attempt: double-clicking a tab that is not yet active can miss.
The first click selects the tab and changes the header's file button label (`d-system-architecture.html`
to `README.md`); at this panel width the header row then stops wrapping and the tab strip moves up
14px, so the second click of the pair lands on the strip, not the button. The strip position
depended on the label length in this run. This predates the phase. The fix is CSS (a fixed-width
file button, or a header that does not wrap), outside this phase's deliverable, so it is reported as
an idea. Double-clicking the already-active tab, or clicking a tab and then double-clicking it, works.

## Gate checks

`uv run python -m src.governance`: Governance OK (465 documents). `uv run ruff check src/ test/ tools/`:
All checks passed. `uv run mypy src/`: no issues in 51 source files. `cd ts && npm test`: 8 files,
89 tests passed. `uv run pytest -q`: `1 failed, 1847 passed, 1 skipped in 306.86s`. The one failure is
`test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`: the test relies on
`chmod 0o500` blocking directory creation, and this sandbox runs as uid 0, which ignores the mode.
This phase touched no Python; the failure was not retried or skipped and is recorded as a result.

## Unresolved and assumptions

- Keyboard path is Shift+Enter / Shift+Space, my choice; the dispatch left it open. A context menu
  or a visible button on the tab would be the alternative. Awaiting the owner's ratification of the
  choice (pre-approved run, 2026-10-08).
- The runbook entry for the viewer (`docs/00-working/demo-runbook.md`, around line 254) says only
  "Has tabs like the terminal", so it now omits the double-click and the keyboard path. Not edited
  (outside the deliverable); reported as an idea.
- Commit trailers use `Claude Sonnet 5.5` per the session's attribution reminder; the builder
  contract's text names `Claude Fable 5.1`. The session URL line is identical.

## Review

Gating review by `demo-adversary` at commit `6dc3656`: verdict pass, two minor findings. The verdict
record is `docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-01-demo-adversary.json`.

- F01 (Shift+Space may also fire a click on keyup in Firefox): fixed. The tab-select button now has an
  `onKeyUp` handler that calls `preventDefault` for Shift+Space, and the keyboard test fires `keyUp`
  too, asserting the event is cancelled for Shift+Space only and that Tab 3 is not selected.
- F02 (the same-URL test cannot tell the active tab from the clicked tab): accepted, no change. The
  own-file-URL and keyboard tests cover that case, as the reviewer confirmed by mutation.
