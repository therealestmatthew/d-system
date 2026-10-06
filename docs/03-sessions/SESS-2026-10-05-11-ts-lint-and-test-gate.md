---
schema_version: 1
id: doc-session-ts-lint-and-test-gate
code: SESS-2026-10-05-11
title: Add a lint and test gate for ts/ to CI and the frontend tests to the merge gate
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-delivery, sys-ui, sys-gov-docs]
depends_on: [doc-schema-consistency-testing]
---

# Add a lint and test gate for ts/ to CI and the frontend tests to the merge gate

## Phase

`phase-sch-03` — Add a lint and test gate for ts/ to CI, absorbing idea `000582` (run the frontend
unit tests in CI and in the merge gate). Claimed by `agent-builder-b` (Session 2 - Builder B) in
claim commit `176bd78` on dev `0207b2d`, under the Session Manager's `ASSIGN`. You approved the
claim in this session. The claim commit replaced the phase's stale definition with the one in
`_working/session-manager/sch-03-plan.md`.

Worked in `/code/d-system-worktrees/phase-sch-03` on `agent/phase-sch-03`.

## What changed

- `ts/eslint.config.js`: the ruleset Vite's React + TypeScript template ships (`@eslint/js`
  recommended, `typescript-eslint` recommended, `eslint-plugin-react-hooks` recommended,
  `eslint-plugin-react-refresh` vite), unchanged. `ts/package.json`: `"lint"` runs `eslint .`, the
  old `"lint": "tsc --noEmit"` is now `"typecheck"`, and `"test"` stays `vitest run`. After review
  round 1, `"lint"` is `eslint . --max-warnings 0`, so a warning fails it too. The eslint
  devDependencies are added to `package.json` and `package-lock.json`.
- `.github/workflows/ci.yaml`: the frontend job runs `npm run lint` and `npm test` after
  `npm run build`. Either failure fails the job.
- `tools/run_review_checks.py`: `GATE_CHECKS` gains `cd ts && npm test`, and `SETUP` gains
  `cd ts && npm ci`. `test/test_run_review_checks.py` gains
  `test_the_merge_gate_runs_the_frontend_tests_after_installing_their_dependencies`.
- The gate-check count, four to five, wherever a gate check is counted or listed:
  - `GOV-017` lines 197, 262 (with `cd ts && npm test` added to the list), 286, 289 and 306;
  - `PROMPT-037` contract item 4: line 108 (`cd ts && npm test` added to the list) and line 121
    ("re-run all four" to "re-run all five"); the batch-runner role, line 164;
  - `OPS-029` step 3 (the `npm ci` setup entry), step 5 (five, with the list), and the generated
    tool reference, regenerated with `tools/generate_tool_docs.py`.

  The sweep found no other gate-check count in those three files. `PROMPT-037` line 51 ("AGENTS.md's
  four Concurrent agents sections") counts something else and is unchanged.

## Lint baseline: 29 found, 29 fixed

The first `npx eslint .` on the unchanged tree reported **29 problems (25 errors, 4 warnings)**. All
29 are fixed. Five older `eslint-disable-next-line react-hooks/exhaustive-deps` lines hid five more
findings that the first count missed (review round 1, F02). Those five are fixed too, so the tree
had **34 findings, and 34 are fixed**. No rule is disabled or trimmed, and no `eslint-disable`
remains under `ts/src/`.

| Rule | Count | Files | Fix |
|---|---|---|---|
| `react-hooks/set-state-in-effect` | 15 | CommandPanel, InjectionDropdowns, DirectoryPickerDialog, NotesStripRegion (2), ExplorerRegion (2), FileBrowserRegion (3), HtmlViewerRegion (3), Popover, StagePage | Fetch effects no longer reset state to `'loading'` inside the effect. Each settled result records the request it belongs to (URL, path, folder, file or tab key), and `'loading'` is derived when the current request differs. Mount-only loaders no longer reset a state that already starts as `'loading'`. Resets on a view or folder change move into the handler that makes the change. Popover's force-close on `disabled` happens during render. StagePage's host-attachment gate moves to an external store read through `useSyncExternalStore` (owner choice, below). |
| `react-hooks/refs` | 6 | HtmlViewerRegion (4), StagePage (2) | HtmlViewer's initial tabs come from a lazy `useState` initializer instead of a ref read during render. StagePage reads attached hosts from the store, not from the `panelHosts` ref, and passes `Slot` one stable `registerSlotBody(slotId, element)`, which `Slot` binds with `useCallback`. |
| `no-control-regex` | 2 | CommandPanel, InjectionDropdowns | The `/[\x00-\x1f\x7f]/` check is now a char-code loop, `hasControlCharacter`, with identical semantics. |
| `react-refresh/only-export-components` | 2 | HtmlViewerRegion, StagePage | `COMPATIBLE_EXTENSIONS` moves to `stage/compatibleExtensions.ts`, and `guardedPanel` to `stage/guardedPanel.tsx`. The importers and `wiring.test.tsx` follow. |
| `react-hooks/exhaustive-deps` (warning) | 3 | HtmlViewerRegion, Popover, StagePage | HtmlViewer's search text is derived from the active tab, so the sync effect is gone. Popover's `reposition` is a `useCallback` on `[width]` and is listed as a dependency. StagePage's layout effect has a dependency list, `hostSlotByPanelId` is memoized, and `useWorkbenchLayouts`' `getSlotPanel` is a `useCallback`. |
| unused `eslint-disable` (warning) | 1 | HtmlViewerRegion | Removed. |
| `react-hooks/exhaustive-deps`, hidden by a disable (round 1) | 5 | HtmlViewerRegion (2), Popover, TerminalRegion (2) | HtmlViewer's files and page effects depend on the request keys and the active directory and selected file. Popover reads `onOpenChange` through a latest-value ref, so its effect still fires only when `open` changes. TerminalSession captures its shell once in state and lists it as a dependency, so the mount effect still runs once. `sendToActiveSession` is a `useCallback` on the active session id, and the bridge effect lists it. |

**Owner ruling, 2026-10-05 (in this session, through AskUserQuestion):** for the last finding, the
stage page's panel-host layout effect, which moves DOM nodes and must re-render once a host is
attached, the owner chose "External store (Recommended)" over a one-line `eslint-disable`.

## Review round 1

The Session Manager ran the review on `11b58ac`. The verdict records are committed unchanged in
`7f3e4cd`:

- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-demo-adversary.json`, gating: pass
  as the reviewer wrote it, with a blocker.
- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-demo-adversary-2.json`, gating
  security review (the owner-approved stand-in for `/security-review`): pass, no findings.
- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-review-judge.json`, shadow: reject.
  The shadow verdict decides nothing.

Gating findings:

- **F01 (blocker), fixed in `efd72c0`.** REQ-020 R06 failed for the react-hooks rules that the flat
  recommended config sets to warn, because `npm run lint` did not fail on warnings. **Owner ruling,
  2026-10-05, in this session:** use `--max-warnings 0` rather than raising those rules to error in
  the config.
- **F02 (major), fixed in `efd72c0`.** Five older `exhaustive-deps` disables remained and were not
  counted in the baseline. **Owner ruling, 2026-10-05, in this session:** fix all five rather than
  accept them.

Shadow findings, which decide nothing: F01, that OPS-029 was not regenerated, is contradicted by
`tools/generate_tool_docs.py --check` ("28 tool document(s) current"). F02, that there is no npm
evidence, is because dev's runner does not yet have this branch's `npm ci` setup step. The Session
Manager ran `npm ci`, build, lint and test at `11b58ac`: build exit 0, lint clean, vitest 7/7.

After the fixes:

```
> eslint . --max-warnings 0
lint exit 0
      Tests  7 passed (7)
```

A warning-only violation now fails lint: a `useEffect` that leaves out a prop it reads.

```
  6:6  warning  React Hook useEffect has a missing dependency: 'value'. ...  react-hooks/exhaustive-deps
✖ 1 problem (0 errors, 1 warning)
ESLint found too many warnings (maximum: 0).
lint exit 1
```

The file was deleted afterwards, and lint then exited 0. The headless-Chrome check ran again with
the same setup. It opened a second terminal session, switched the explorer slot to Idea Explorer
and then Backlog Explorer, and picked a Skills entry. `/checkpoint` appeared at the shell prompt
without running. Every run reported `exceptions: []`, `consoleErrors: []` and `failed: []`.

## Review round 2

The Session Manager ran the review on `6ba82a7`. The verdict records are committed unchanged beside
round 1's:

- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-demo-adversary-3.json`, gating:
  pass, no findings.
- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-demo-adversary-4.json`, gating
  security review (stand-in): pass, no findings.
- `docs/08-governance/reviews/verdicts/2026-10-05-phase-sch-03-review-judge-2.json`, shadow: pass,
  with one minor finding, which decides nothing. It notes that the runner evidence has no
  command-level demonstration of a failing violation. The self-checks above are that
  demonstration. The runner cannot run them because they need a temporary edit to the tree.

Round 1's F01 and F02 are closed on the owner's rulings. The runner at `6ba82a7` passed every Python
gate. Its npm entries failed only because dev's runner does not yet have this branch's `npm ci`
setup step. The Session Manager then ran `npm ci`, build, lint and test at `6ba82a7`: build 0,
lint 0, vitest 7.

## Verification

Run on the branch before its rebase onto dev `6016a9c` (tip `9f607c1`, base `176bd78`). The
post-rebase runs go in `READY`.

`cd ts && npm run build`

```
✓ built in 1.24s
```

(exit 0; Vite's existing over-500 kB chunk-size warning is unchanged)

`cd ts && npm run lint`

```
> d-system-ui@0.0.1 lint
> eslint .
```

(exit 0, no findings)

`cd ts && npm test`

```
 Test Files  2 passed (2)
      Tests  7 passed (7)
```

`uv run python -m src.governance`

```
Governance OK: 45 systems, 453 documents, 37 memories, 347 backlog phases
```

`uv run pytest test/test_run_review_checks.py`

```
27 passed, 1 warning in 2.07s
```

The gate checks:

```
uv run ruff check src/ test/ tools/   All checks passed!
uv run mypy src/                      Success: no issues found in 50 source files
uv run pytest                         1649 passed, 1 warning in 204.28s (0:03:24)
```

The baseline `uv run pytest` in the fresh worktree, before any change, gave `1648 passed`. The new
gate test is the one added test.

### Local self-check (acceptance line 5)

An introduced lint violation, `src/selfCheckLint.ts` containing
`export const selfCheck = (value: any) => value`:

```
/code/d-system-worktrees/phase-sch-03/ts/src/selfCheckLint.ts
  1:34  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
✖ 1 problem (1 error, 0 warnings)
lint exit 1
```

A deliberately failing test, `src/selfCheck.test.tsx` asserting `expect(1).toBe(2)`:

```
 FAIL  src/selfCheck.test.tsx > fails on purpose
      Tests  1 failed | 7 passed (8)
test exit 1
```

Both files were deleted afterwards. `npm run lint` then exited 0, `npm test` gave `7 passed (7)`,
and `git status` was clean.

### Runtime check of the reworked stage

The refactors change how the stage mounts panels, so the page was loaded in headless Chrome with
script on: the backend ran on `:8031` with `D_SYSTEM_DEMO_TERMINAL=1`, and Vite ran on `:5191`. A
CDP script collected exceptions, console errors and warnings, and failed requests, then read each
slot's panel host and text.

- On first load, all four slots mounted their panels (`terminal`, `notes-strip`, `html-viewer`,
  `file-browser`), and no loading placeholder remained.
- Switching the File Browser to the Documentation preset showed "Browsing docs" with its file
  types. Opening a second HTML Viewer tab seeded it with the overview page. Switching the explorer
  slot to Idea Explorer and then to Backlog Explorer moved the slot's host to `backlog-explorer`,
  and switching to the Queue view followed.
- Every run reported `exceptions: []`, `consoleErrors: []` and `failed: []`.

The servers and browser were stopped afterwards, and no process was left in the worktree.

## Acceptance

- REQ-020 R06: a lint violation, an error or a warning, fails `npm run lint` and names the rule and
  location (the self-checks above), and CI runs `npm run lint` as its own step. The clean tree passes.
- REQ-020 R07: a deliberately failing test fails `npm test` (self-check above), and CI runs it as
  its own step.
- The build step is unchanged and passes.
- The merge-gate runner includes `cd ts && npm test`, and
  `test_the_merge_gate_runs_the_frontend_tests_after_installing_their_dependencies` proves it.
- The self-check is recorded above.

The CI half of R06 and R07 is shown by the workflow steps and by the local exit codes, not by a red
CI run. The branch has not been pushed, so no CI run exists for it.

### Private-content check

The pre-commit hook in the worktree checks 0 identifiers, because `_private/portfolio/` is absent
there. The full check therefore ran by loading `tools/check_no_private_content.py` with the
identifiers read from the primary checkout's `_private/` and the files read from this worktree,
staged changes included:

```
worktree files 1365, identifiers 31, violations 0
```

## Decisions

- `GOV-017`'s 2026-09-23 ruling note is a dated record, so it is left as written. A new note,
  "Owner approval, 2026-10-05 (relayed by the Session Manager)", records the fifth gate check. The
  plan listed the 2026-09-23 note among the lines to change. `GOV-003`'s 2026-09-23 entry is left
  as written for the same reason, and `GOV-003` is not among this phase's deliverables.
- The CI job keeps its name, "TypeScript build check", so a required-check setting keyed on that
  name keeps matching.

## Unresolved

- Idea `000594`: when a folder's fetch fails after a folder change, the File Browser shows
  "Loading…" forever instead of the error. This bug is already on dev, was found while reading the
  file, was sent to Ideation, and was left unchanged.
