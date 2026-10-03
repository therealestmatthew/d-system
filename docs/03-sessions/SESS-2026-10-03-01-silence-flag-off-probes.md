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
message. The backend log shows every workbench route still requested (`injection-sources`,
`list`, `platform`, `search`). The per-route totals vary between runs under StrictMode (13 on this
session's run, 14 and 15 on the reviewer's), so they are not a reproducible figure.

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

Independent review by a `demo-adversary` sub-agent of `dev...agent/phase-wbf-10` (5d13727,
afa903c). Its report, verbatim except for formatting:

**Verdict: PASS WITH FINDINGS** (informational/minor only — no blocker or major findings; both
acceptance halves hold under independent rerun).

What it verified independently:

- Flag unset (backend :8021, vite :5281, same CDP capture): `404 console entries: 0`,
  `responses >=400: 0`, `uncaught exceptions: 0`. Disabled buttons: Commands, Skills, Prompts,
  Agents "(terminal absent)"; page text includes "Terminal is absent..." and "Could not search ..".
  Backend access log shows only `terminal-enabled` (x3: 2 from `TerminalRegion.tsx`'s own
  StrictMode-doubled probe + 1 from the shared helper) and `overview-location` (x1, ungated) —
  zero real calls reached any `/api/v1/workbench/*` route, so `fetchWorkbench` short-circuits
  before the network.
- Flag set (backend :8022, vite :5282): 0 console 404s, 0 responses >=400, 0 exceptions; all four
  dropdowns populated (Commands 4, Skills 11, Prompts 43, Agents 16); terminal session live; file
  browser populated; every workbench route (`injection-sources`, `platform`, `list`, `search`)
  still fires.
- `cd ts && npm run build` clean. `uv run python -m src.governance` → `Governance OK: 43 systems,
  424 documents, 35 memories, 347 backlog phases`.
- Diff scope: only the eight deliverables plus `backlog.yaml`, `catalog.md` and this record.

Findings:

1. **Minor — pre-existing gap in the same route class, not a regression.**
   `ts/src/stage/HtmlViewerRegion.tsx:268` still sends a plain `fetch` `HEAD` to
   `/workbench-file/<selected file>`, which Vite serves only under the flag
   (`ts/vite.config.ts:472`). With the flag off it returns **200**: Vite's SPA fallback serves
   the app shell. So it does not violate R23, but the viewer's "page exists" check reports
   `ready` with the flag off for a file that is not served at that URL, and would iframe the
   SPA shell instead of surfacing `missing`. Unchanged from `dev`.
2. **Minor — the record's flag-on request count is not reproducible.** The record gave 13
   workbench requests; two reruns gave 14 and 15, with `injection-sources` firing 3 times on
   one and 2 on the other. StrictMode mount-unmount-remount issues the real fetch more than
   once per load (pre-existing, not introduced by the diff). Does not affect the verdict.
3. **No finding, documented.** `TerminalRegion.tsx` keeps its own `terminal-enabled` probe
   (line 405) instead of the shared helper, contrary to the phase's original `next_action`;
   the record discloses it and gives the reason (not a deliverable).
4. **Checked and held.** Every on-load caller of a flag-gated workbench route now goes through
   `fetchWorkbench`, and none reads headers or a body on its non-ok path, so the synthetic 404
   leaves each caller's handling unchanged. The favicon request is gone in both reruns.

Disposition by this session: finding 2 fixed (Verification now says the totals vary between
runs). Findings 1 and 3 accepted as out of scope: finding 1 returns 200, not a console 404, and
is unchanged from `dev`, so it was sent to Ideation as a new idea; finding 3 follows the owner's
ruling to widen with one shared helper, and `TerminalRegion.tsx` is not a deliverable.

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

- The record first gave the flag-on request counts as a fixed figure (13). The review's reruns
  gave 14 and 15, because StrictMode double-mounting makes the count vary between runs. The
  Verification section now says the routes are still requested and that the totals vary.

## Left undone

- `TerminalRegion.tsx` could use the shared helper so the page probes once; that is outside this
  phase's deliverables.
- The HTML viewer's page-exists `HEAD` check gets 200 from Vite's SPA fallback with the flag
  unset (review finding 1). It is not a 404 and is unchanged from `dev`; sent to Ideation.
- The user-triggered workbench calls in `FileBrowserRegion.tsx` (reveal, absolute path) still use
  plain `fetch`. They run only on a user action, not on load, so R23 does not cover them; with
  the flag unset such an action still logs one 404.
