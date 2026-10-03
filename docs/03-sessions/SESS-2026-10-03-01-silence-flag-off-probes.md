---
schema_version: 1
id: doc-session-silence-flag-off-probes
code: SESS-2026-10-03-01
title: Silence the flag-off workbench probes
kind: session
status: active
owner: repository-owner
created: '2026-10-03'
updated: '2026-10-03'
systems: [sys-ui]
depends_on: [doc-workbench-features-defects]
---

# Silence the flag-off workbench probes

## Phase

`phase-wbf-10` — Silence the flag-off workbench probes.

## Verification

`cd ts && npm run build`

```text
✓ built in <time>
```

(Plus Vite's standing chunk-size advice, unchanged by this phase.)

`uv run python -m src.governance`

```text
Governance OK: 43 systems, 424 documents, 35 memories, 347 backlog phases
```

`load the stage with D_SYSTEM_DEMO_TERMINAL unset and count console 404 entries: 0 (REQ-012 R23)`:
done with a script that drives headless Chrome (JavaScript enabled) through the Chrome DevTools
Protocol. It records `Log.entryAdded`, `Runtime.consoleAPICalled`, `Network.responseReceived` with
status 400 or above, and `Runtime.exceptionThrown`, waits 8 s after navigation, then reads the
disabled buttons and the page text. Backend `uv run uvicorn src.main:app --port 8011` with the flag
unset, `npx vite --port 5181` with `VITE_API_TARGET` pointing at it (dev mode, so React StrictMode
mounts each effect twice).

| | Before (c2c48b5) | After (5d13727) |
|---|---|---|
| Console 404 entries | 14 | 0 |
| Responses 400 or above | 14 | 0 |
| Uncaught exceptions | 0 | 0 |
| Disabled dropdowns | Commands, Skills, Prompts, Agents "(terminal absent)" | the same four |
| Absent-terminal message | shown | shown |
| File browser | "Could not search .." | "Could not search .." |

The 14 before: `/workbench/platform` x2, `/workbench/injection-sources` x2,
`/workbench/list?path=ts/public&ext=.json` x2, `/workbench/search?path=.` x2,
`/workbench/list?path=.` x2, `/workbench/list?path=_public/overview` x2,
`/workbench/search?path=_public/overview&ext=…` x1, `/favicon.ico` x1.

Flag set (`D_SYSTEM_DEMO_TERMINAL=1`, backend :8012, vite :5182), after the change: 0 console 404
entries, 0 responses 400 or above, 0 uncaught exceptions, no disabled dropdown, no absent-terminal
message. The backend log shows the workbench requests still sent: `injection-sources` 2,
`list` 6, `platform` 2, `search` 3.

## Acceptance

- REQ-012 R23 count, zero 404 console entries on load with the flag unset: **Met** — 14 before, 0
  after (Verification table).
- REQ-012 R23 degradation, disabled dropdowns, absent-terminal message, no uncaught exceptions:
  **Met** — all three unchanged in the after column, and the flag-set run still issues every
  workbench request.

## Backlog

`status: active`, `agent: agent-builder-a`, `session: doc-session-silence-flag-off-probes`.
`next_action`: Acceptance met on agent/phase-wbf-10 (14 console 404s before, 0 after, degradation
unchanged; SESS-2026-10-03-01). Awaiting the owner-approved merge, then the completion edit on dev.

## Unresolved

None.

## Review

(Pending: independent review.)

## Decisions

- The phase was written against four measured 404s and one deliverable. Orientation found the
  `/list` fetch the scope names in `NotesStripRegion.tsx`, so the claim was held back; the owner
  widened the deliverables in the claim turn. The first measurement then found 14 entries from
  six source files and the missing favicon, and the owner widened again (option (a)) with one
  shared probe helper rather than a probe per panel.
- The helper (`fetchWorkbench` in `ts/src/stage/useTerminalEnabled.ts`) returns a synthetic 404
  `Response` when the terminal is not enabled, instead of throwing. Every caller already handled
  the real 404, each in its own way (`missing` for the dropdowns, `error` for the panels, bash for
  the platform default), so this keeps each one's flag-off state identical and changes only what
  reaches the network.
- The favicon is an empty `data:` icon link in `ts/index.html`, so no binary file is added.
- `TerminalRegion.tsx` keeps its own `terminal-enabled` probe: it is not a deliverable and its
  probe returns 200. The page therefore asks `terminal-enabled` twice, once from the panel and once
  from the shared helper.

## Corrections

None.

## Left undone

- `TerminalRegion.tsx` could use the shared helper so the page probes once; that is outside this
  phase's deliverables.
- The user-triggered workbench calls in `FileBrowserRegion.tsx` (reveal, absolute path) still use
  plain `fetch`. They run only on a user action, not on load, so R23 does not cover them; with
  the flag unset such an action still logs one 404.
