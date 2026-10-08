---
schema_version: 1
id: doc-session-viewer-last-modified-badge
code: SESS-2026-10-08-19
title: Show a last-modified badge on the HTML Viewer header (phase-wbf-02)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-viewer]
depends_on: [doc-workbench-features-defects-requirements]
---

# Show a last-modified badge on the HTML Viewer header (phase-wbf-02)

## Phase

`phase-wbf-02` (last-modified badge on the HTML Viewer header), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md), recorded as idea 000102 (restored
from `discarded` to `reviewing` for this run). Builder A (`agent-builder-a`) under the Session
Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-02`, cut from the run's
integration branch `ccr-b69b05b4-tdcrux`. The session code is 19 because 17 and 18 are taken on
sibling branches.

## What was found before designing

`GET /api/v1/workbench/list` and `/search` returned `name`, `path` and `is_dir` only, so the route
carried no mtime and the phase was not frontend-only. The `DirectoryEntry` model lives in
`src/api/routes/workbench.py`, not under `src/models/`, so `src/models/` needed no change.

## Outcome

- **Route.** `DirectoryEntry.modified_at: str | None = None`, filled by both routes through
  `_to_entry`. Format: ISO 8601 UTC with millisecond precision and a `Z` suffix, for example
  `2026-10-08T07:15:11.240Z`. `null` when `stat` fails (a dangling symlink, a delete between listing
  and stat). The field is optional with a default, so a client that predates it reads the same
  entries; the File Browser and the explorers were not edited and their tests pass.
- **How the viewer learns the mtime.** It does not take the time from the dropdown's cached search
  result, which goes stale. For the displayed file it requests
  `GET /workbench/list?path=<dirname>&q=<basename>` and picks the entry whose path equals the
  selection. The request is keyed exactly like the page-exists check (tab id, selected file,
  refresh token), so it is repeated on a tab switch, on a new selection and on Refresh: a re-fetch
  on select, as the Session Manager allowed.
- **Re-selecting the displayed file.** Choosing the file a tab already shows changed no state, so
  nothing refetched and the frame did not reload. That option now bumps the refresh token, which
  re-checks the page, reloads the frame and reads the mtime again. This is what makes R04's
  "regenerate the overview, re-select it, the badge advances" work.
- **Badge.** `<span data-testid="html-viewer-modified" role="status">` in the header after the title:
  `Modified YYYY-MM-DD HH:mm:ss` in the browser's local time, with the exact UTC ISO value in its
  `title`. While the read for the current key is pending it shows `Modified …` (never the previous
  file's time); when the backend has no time it shows `Modified time unavailable`; with no file
  selected it is not rendered.
- **Header wrap.** The header (`.stage-region__header`) now has `flex-wrap: wrap`, set as an inline
  style in `HtmlViewerRegion.tsx` because `StagePage.css` is outside the phase's deliverables. See
  the fit-contract numbers below.

## REQ-037 header measurement

`uv run python test/test_workbench_fit_contracts.py --live http://localhost:5203 --quick --panel html-viewer`
on this worktree's dev server (Vite 5203, API 8133; see the port note below).

| State | Rules pass / fail | Findings | HTML Viewer header |
|---|---|---|---|
| Before (no badge) | 39 / 2 | 4 | layout 2, primary, 1024x768: 377 px of content in a 307 px box (wrap + silent-clip); the other 2 findings are the notes-strip tooltip bubble |
| Badge added, header not wrapping | 36 / 8 | 10 | overflows in four primary cells: 529 px in 519 (layout 1, 1280x720), 413 (layout 1, 1024x768), 393 (layout 2, 1280x720) and 307 (layout 2, 1024x768) |
| Badge added, header wraps (committed) | 39 / 2 | 4 | only layout 2, primary, 1024x768 remains, now 324 px in 307 px (down from 377) |
| Badge added, header and controls both wrap (rejected) | 36 / 4 | 6 | layout 2 page area falls to 393x44 and 307x47, below the 60 px floor (fill and frame rules fail) |

So the badge adds no finding and does not make the idea 000637 overflow worse: the same two cells'
findings remain and that cell's overflow is 53 px smaller. It does not fix 000637; the controls group
alone is 324 px wide there and wrapping it costs the page area its 60 px floor.

## Acceptance

- REQ-012 R03: met. Live (headless Chromium, 1024x768, Vite 5203): default overview file badge
  `Modified 2026-10-08 07:15:11` against `stat` on disk `2026-10-08 07:15:11`; two probe files given
  `touch -d` times in March 2026 showed those times, not the load time. Unit tests assert the badge
  text equals the reported mtime and that the list request names the file's directory and name.
- REQ-012 R04: met. Live: Tab 1 (file a, `2026-03-01 10:00:00`) and Tab 2 (file b,
  `2026-03-02 11:30:45`) swapped the badge on each tab click. After `touch -d '2026-03-05 09:09:09'`
  on file b, the badge stayed `2026-03-02 11:30:45` until file b was selected again, then read
  `2026-03-05 09:09:09`. The regenerated overview page was not rebuilt (that would modify a tracked
  file); a touched probe file stands in for it. The mutation of removing the re-select bump makes
  the re-select unit test fail.

## Verification and gate checks

See the hand-off message for the command tails. In short: `pytest test/test_workbench_api.py` 50
passed (4 new); `cd ts && npm test` 152 passed (6 new); `npm run build` built; the five gates ran
after the last code commit. Full `pytest`: `2 failed, 2072 passed, 1 skipped in 399.17s`. The two
failures are the known ones, neither retried nor skipped: `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`
(idea 000604, uid 0 ignores `chmod 0o500`) and `test_demo_terminal_api.py::test_control_characters_reach_the_shell`
(load-sensitive flake; this phase touched no terminal code).

## Unresolved, assumptions, awaiting ratification

- **Port collision.** The dispatch assigned API port 8033. A uvicorn process whose working directory
  is `scratch-phase-arch-16` was already listening there (and a Vite for the same worktree on 5202),
  so this run used API port 8133 with Vite 5203 as assigned. That process was not touched.
- **Format of `modified_at`** (ISO 8601 UTC string rather than epoch seconds) and the **display in
  local time to the second** are this session's choices. Awaiting ratification (pre-approved run,
  2026-10-08).
- **Inline `flexWrap` on the header** instead of a rule in `StagePage.css`, to stay inside the
  declared deliverables. If the Session Manager prefers the stylesheet, it is a one-line move into
  `.stage-region__header` (which would also wrap every other panel's header, so it needs its own
  fit-contract run). Awaiting ratification.
- **The re-select bump** changes what choosing the displayed file does: it now reloads the frame.
  Awaiting ratification.
- **Not exercised:** browsers other than Chromium; Windows; dark mode (the badge colour is a fixed
  `#4a5568`, like the neighbouring controls' fixed colours); the badge in the "Open-in-tab link"
  mode (the header is the same in both modes, so it shows there too, not separately checked).
- **Commit trailers.** The builder contract names `Claude Fable 5.1`; this subagent runs as Sonnet
  5.5 and the session's attribution reminder names that, so the commits say `Claude Sonnet 5.5`. The
  session URL line is identical. Left for the Session Manager to rule on.
- `docs/06-requirements/REQ-037-workbench-content-fit-contracts.md` line 212 says phase-wbf-02 "will
  add" the badge; it was not edited (outside the deliverables).
