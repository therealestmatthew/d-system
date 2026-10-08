---
schema_version: 1
id: doc-session-file-browser-folder-error
code: SESS-2026-10-08-15
title: Show the File Browser error when a folder listing fails after a folder change (phase-wbf-15)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-explorers]
depends_on: [doc-workbench-features-defects-requirements]
---

# Show the File Browser error when a folder listing fails after a folder change (phase-wbf-15)

## Phase

`phase-wbf-15` (show the File Browser error when a folder listing fails after a folder change),
group of [`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Batch runner
(`agent-batch-runner`) under the Session Manager's pre-approved run of 2026-10-08. Branch
`agent/phase-wbf-15`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`. Idea `000594`
(File Browser shows "Loading…" forever when a folder's fetch fails after a folder change).

## Outcome

`ts/src/stage/FileBrowserRegion.tsx`: the tree area now tests `loadState === 'error'` before
`loadState === 'loading' || entriesFolder !== contextFolder`. `loadState` is derived from the
settled result and names the folder it belongs to, so it is `'error'` only when the failed fetch is
for the current `contextFolder`. A failed fetch never advances `entriesFolder`, which is why the
old order hid the error. The message is unchanged ("Could not search <folder>." with `role="alert"`).
The stale-render protection is untouched: `buildTree` still receives an empty list while
`entriesFolder !== contextFolder`, and a pending fetch still shows "Loading…". The bookmark section
from `phase-wbf-05` was not touched.

`ts/src/stage/FileBrowserRegion.test.tsx` (new, in the deliverables): three vitest tests with
`fetch` stubbed and the real panel mounted. The directory picker dialog is replaced by two buttons
(`vi.mock`) so a test browses to a folder without driving the dialog's requests.

1. First folder (`.`) succeeds, second (`docs`) returns 500: the alert "Could not search docs."
   appears, "Loading…" does not, and the first folder's entry is not shown.
2. After that failure, a browse to `src` succeeds: the entry shows and the alert is gone.
3. Second folder pending: "Loading…" shows, no alert, no entry from the first folder; resolving it
   then shows the new listing.

Written first and run on the old order: tests 1 and 2 failed (the tree area held "Loading…"), test
3 passed. On the new order all three pass.

## Acceptance

- REQ-012 R28, error case: met (tests 1 and 2).
- REQ-012 R28, stale-render case: met (test 3: "Loading…", no tree from the previous folder).

## Not done

- No Playwright pass. The change is one reordered conditional with a vitest covering both cases
  against the real panel, so a browser run was judged not worth the cost; it was not run.
- The message does not include the text the API returned. The phase asked for the could-not-search
  message, which is the existing text; the fetch path discards the response body.

## Gate checks

`cd ts && npm test`: 9 files, 92 tests passed. `cd ts && npm run build`: built. `uv run python -m
src.governance`: Governance OK. `uv run ruff check src/ test/ tools/`: All checks passed. `uv run
mypy src/`: no issues in 51 source files. `uv run pytest -q`: `1 failed, 1903 passed, 1 skipped`.
The failure is `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`,
which relies on `chmod 0o500` blocking directory creation; this sandbox runs as uid 0, which
ignores the mode. It fails identically with this phase's changes stashed. This phase touched no
Python. Recorded as a result, not retried or skipped.

## Awaiting ratification

None. No decision or assumption beyond the above.
