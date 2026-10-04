---
schema_version: 1
id: doc-session-react-error-boundary
code: SESS-2026-10-04-15
title: Error boundaries and accessible loading and error status for the stage
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-ui]
depends_on: []
---

# Error boundaries and accessible loading and error status for the stage

## Phase

Unclaimed: owner-directed work, no backlog phase. `fix-react-error-boundary`. Idea 000569 asked
for an error boundary and an accessible loading and error status for the React stage and
workbench, because a render error blanked the whole app. The Session Manager assigned it with the
owner's approval, and the idea's status is left for Ideation.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 44 systems, 437 documents, 36 memories, 347 backlog phases
```

`uv run pytest`

```text
1457 passed, 1 skipped, 1 warning
```

`uv run ruff check src/ test/` and `uv run mypy src/`

```text
All checks passed!
Success: no issues found in 47 source files
```

`cd ts && npm test` (new in this session)

```text
Test Files  2 passed (2)
     Tests  7 passed (7)
```

`cd ts && npm run build` and `npm run lint`

```text
✓ built
> tsc --noEmit        (no errors)
```

The built stage was also checked live. `npx vite preview` served it with no backend running, and
headless Chrome rendered it with JavaScript enabled. Every panel rendered; none went blank. The
File Browser's failed search appeared in the dumped DOM as `role="alert"` with the text "Could not
search .".

`npm audit` reports `found 0 vulnerabilities` with the new dev dependencies.

## Acceptance

Self-declared from the owner's instruction and the two choices the owner made in this session; no
backlog acceptance list exists for this session.

- A render error in one workbench panel replaces only that panel, with an error naming it and a
  Retry button, and the other panels keep running: Met. `ErrorBoundary` wraps each panel at the
  portal in `StagePage.tsx`, through `guardedPanel()`. The test "each portaled panel is guarded
  and named by its display name" renders the element `StagePage` ships, a throwing panel beside a
  healthy one, and asserts both.
- A render error outside every panel no longer blanks the stage: Met. `App.tsx` wraps `StagePage`
  in a boundary labelled "The stage". The test "App catches a render error that escapes the
  stage" renders `App` with a throwing `StagePage`.
- Retry brings the panel back, mounted afresh: Met. The test "Retry remounts the children,
  re-running their effects" asserts no mount while the child throws and exactly one mount after
  Retry.
- Loading and error states are announced to assistive technology: Met.
  - Loading texts carry `role="status"`, and "Could not …" errors carry `role="alert"`. This covers
    the layout loader and nine panel files, including the terminal's three session overlays
    (shell refused, session cap reached, connection closed).
  - The boundary's fallback is `role="alert"`.
  - Two tests assert the roles on the Idea Explorer's loading and failed states.
- The behaviour is tested at runtime with vitest and Testing Library, as the owner chose: Met.
  `npm test` runs seven tests. Two deliberate breaks each failed one: removing the boundary from
  `App.tsx`, and removing it from `guardedPanel()`.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

- Nothing in CI or the Session Manager's gate runs `npm test` yet. A broken stage test would not
  stop a merge. Sent to Ideation as an idea.
- The notes strip's current text has no live region. It changes on a timer, and announcing every
  change would interrupt a screen reader. Its loading and error states share that element, so they
  are not announced either.
- Retry on a crashed terminal panel opens a new terminal session. The old one ended when the panel
  crashed.
- In the File Browser, the loading and error paragraphs sit inside its `role="tree"` container.
  Whether every screen reader announces a live region there is unconfirmed.

## Decisions

- **Boundary placement: around the root and around each panel.** This was the owner's choice. A
  boundary only at the root would replace the whole workbench when any one panel crashed.
- **Tests: vitest and Testing Library.** This was the owner's choice, over a one-off headless
  browser check or a pytest that reads the source. The boundary's value is runtime behaviour, and
  only a runtime test exercises it.
- **vitest 5, not 3.** vitest 3 carries a moderate advisory (GHSA-82fw-gwwq-j7x9). Version 5
  fixes it and supports the installed Vite 6.4.3.
- **No key-based remount.** The first version remounted the children under a new key on Retry.
  React has already unmounted a subtree that threw, so clearing the error mounts it afresh anyway.
  The key wrapper was removed, and the Retry test still asserts a single fresh mount.
- **Tests live beside the component** in `ts/src/`, configured in `ts/vitest.config.ts` and kept
  separate from `vite.config.ts`. That file's dev-server plugins read the repository at startup.

## Corrections

- The first Retry test failed the run on a render count. React retries a throwing render once by
  itself, so the count did not settle. The test now uses an explicit flag that it flips before
  clicking Retry.
- The first pass of status roles missed the terminal panel's "Checking terminal availability…" and
  "the stage backend is not reachable" messages. The live check exposed them, and both now carry
  roles.

## Review

A `demo-adversary` agent reviewed `1d2e6ab..542eddb`. Verdict: PASS WITH FINDINGS. Its report,
condition by condition:

- The boundary is a correct class component, and Retry remounts. `npm test` passed 5 tests, the
  production bundle contains no test code, `tsc` passed, vite 6.4.3 and vitest 5.0.3 resolve
  without a peer conflict, `npm audit` was clean, and governance passed.
- Condition 1 (one panel replaced, others keep running): Met.
- Condition 2 (an error outside the panels no longer blanks the stage): met in code, but untested.
- Condition 3 (Retry remounts): Met.
- Condition 4 (announcements): partially met.
- Condition 5 (runtime tests): Met, for the scope the record states.

Its findings:

1. **Major.** `TerminalRegion.tsx`'s three session overlays had no role: shell refused, session
   cap reached, connection closed. Fixed: each now has `role="alert"`.
2. **Major.** The tests rendered a bare `ErrorBoundary`, not the wiring that ships, so dropping a
   boundary from `App.tsx` or `StagePage.tsx` would have gone unnoticed. Fixed. `StagePage` now
   portals `guardedPanel()`, and `wiring.test.tsx` renders `App` and `guardedPanel()`. Removing
   either boundary made a test fail.
3. **Minor, not confirmed.** In `FileBrowserRegion.tsx`, the loading and error paragraphs sit
   inside a `role="tree"` container. Some assistive technology may not announce a live region
   inside a widget role. Accepted and left open. The paragraph's place inside the tree predates
   this work, and confirming it needs a screen reader.
4. **Minor.** `ExplorerRegion`'s roles are tested only through `IdeaExplorerRegion`. Accepted,
   because the Backlog Explorer renders the same component.

