---
schema_version: 1
id: doc-session-phase-wb-09-layout-assignment
code: SESS-2026-09-11-08
title: phase-wb-09 layout assignment model — checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-api]
depends_on: [doc-workbench]
---

# phase-wb-09 layout assignment model — checkpoint

## Phase

`phase-wb-09` — Layout assignment model — per-panel eligibility, assignment-only dialog,
concurrent shells.

## Verification

State at close: the phase is integrated into `dev` (fast-forward to the rebased branch at
`08305cc`, four phase commits `8d7c4ea`/`711464c`/`2a9afce`/`08305cc`); the worktree and
`agent/phase-wb-09` branch are removed; the phase is `status: complete` (commit `81e8404`).
Commands re-run in the primary checkout at close:

- `cd ts && npm run build`: `✓ 55 modules transformed … ✓ built` (pre-existing 500 kB
  chunk-size warning only).
- `uv run ruff check src/ test/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 24 source files`
- `uv run python -m src.governance`: `Governance OK: 18 systems, 168 documents, 18 memories,
  122 backlog phases`
- `uv run python tools/check_no_private_content.py` with changes staged:
  `check_no_private_content: OK (507 tracked files, 31 identifiers checked)`
- `uv run pytest` (post-rebase, pre-integration, in the worktree): `575 passed, 3 failed` —
  the known environmental PTY failures (ideas `000097`/`000099`; a real fix is idea `000129`),
  unchanged in kind and count.

Creator/validator loop (orchestrator-run):

- W09-C1/V1 (backend: six-session cap, `/platform` route, ADR-014 wording) — `8d7c4ea`; V1
  PASS, no findings.
- W09-C2/V2 (layout data: per-panel eligibility, schema v2, storage rework, new
  `schemas/workbench-layout.schema.json` + `test/test_workbench_layout_schema.py` per the
  idea-`000098` mandate in the pack) — `711464c`; V2 PASS, no findings.
- W09-C3/V3 (assignment dialog, switcher-only headers, concurrent shells) — `2a9afce`, then
  the fix-cycle commit `08305cc` (see the gate account below); V3 re-run PASS with one
  cosmetic note (unstyled displacement-notice classes), no blocking findings.
- W09-G (mechanical gate): FAIL once on worktree staleness against `dev` (unrelated idea-log
  commits), resolved by a clean forward-merge; re-run ALL GREEN.

Completion gate (`GOV-003`, coordinator-dispatched):

- `W09-A` adversarial review, first run: **BLOCKER** — the stage page crashed on load
  (Maximum update depth exceeded; root `innerHTML` empty) in dev AND production builds on a
  clean profile: `StagePage.tsx`'s `registerSlotBody(slot.slot_id)` allocated a new closure
  per render, so React detached/reattached the ref and ran `setSlotBodies` every commit.
  Invisible to build/pytest/W09-G by construction; caught by the gate's first live browser
  launch. Fix cycle 1 repaired the loop (stable per-slot callbacks; verified live) but left
  re-assignment killing a live shell session after two creator attempts — the orchestrator's
  websocket-lifecycle trace showed the live bash socket closing, a CMD panel thrash-mounting,
  and a fresh bash replacing the original.
- Documented opus escalation (`PROMPT-012`'s single permitted escalation, coordinator-
  dispatched): found the true mechanism — React treats a portal whose `containerInfo` changes
  as insert+delete, never an update (verified in react-dom source), so no batching fix could
  work. Rework (commit `851e5c5`, rebased to `08305cc`): permanent per-panel host divs moved
  between slot bodies via `appendChild` in a layout effect; a `NO_VISIBLE_PANEL` sentinel so a
  vacated slot shows a placeholder instead of auto-promoting CMD (which had been burning
  global cap slots as a transition artifact); an explicit confirm notice before displacing an
  occupied slot's live panel (REQ-007 W16's announced-remount path); a distinct in-panel
  message for a socket closed before ever opening (the pre-accept global-cap refusal whose
  structured reason cannot reach the browser — recorded as idea `000137`, backend scope).
  Orchestrator re-verified live pre-commit: a reassignment produces ZERO websocket events;
  Cancel produces none and reverts; page loads clean in dev and `vite preview`.
- `W09-A` re-run: both prior findings **CLOSED** (independently reproduced — live marker
  survived reassignment with zero websocket events); no blocker or major survived a hostile
  pass including a true-concurrency cap attack (12 simultaneous connects: exactly 6 admitted,
  6 refused, slots freed after abrupt TCP disconnects), seeded old-schema/malformed storage
  (silent fallback, zero errors), synchronous double-click on the confirm (idempotent), rapid
  reassign-during-layout-switch host-div stress (no leaks or duplicates), main-slot height
  chain (exact match), and header-dropdown re-assignment impossibility (code-proven).
- `W09-W` browser verification: **all seven items PASS** with measured evidence — dialog shape
  (one eligible-slot selector per panel, no geometry or per-slot visible controls); assignment
  round-trip with the displacement notice, persistence across reload, and cleared-store
  defaults; old-schema and ineligible-state fallbacks with zero console errors; W15 fill
  re-run with bash in the MAIN slot at all four sizes in both layouts (all eight
  measurements 36.64px from the panel body — tabbar only); the persistence guard (zero new
  websockets across layout switches, MARKER preserved in scrollback); concurrent shells with
  independent session tabs; switcher-only headers (localStorage assignments provably
  unchanged by swaps); zero page scroll and zero region overlaps in every combination.

Operational notes, resolved: the owner's own `src/demo/factory.py` edit (separate session,
landed as `3e4b5cd`) was confirmed not this phase's; orphaned dev servers from a truncated
gate dispatch were killed; browser-heavy dispatches truncated repeatedly and were resumed by
the coordinator (post-mortems: `brain/procedures/runtime-behavior-needs-runtime-evidence.md`
and `brain/procedures/scope-dispatches-to-the-turn-budget.md`; pack conventions idea `000136`).

## Acceptance

- Dialog offers exactly one eligible-slot selector per panel and nothing else; assigning HTML
  Viewer to the terminal slot and a shell to the main slot renders both there and survives
  reload; a cleared or old-schema store yields the pre-delta default arrangement (REQ-007
  W16): Met — `W09-W` items 1–3 measured all of it live (including the ineligible-assignment
  seed falling back silently with zero console errors), on top of V2/V3's code confirmation.
- Two shell panels visible at once each complete an independent command round-trip; a seventh
  concurrent session is refused while six are open and admitted after one closes; the platform
  route reports host platform and shell availability (REQ-007 W17): Met — the cap tests
  genuinely open six live sessions (V1, re-attacked by `W09-A` with 12 true-concurrent
  connects), the platform route was curl-verified live, and `W09-W` item 5 measured bash
  round-tripping while a second shell panel rendered its unavailable-shell message unclipped
  with independent session tabs (Linux half; the live two-shell round-trip is the Windows
  owner check).
- Each shell panel renders unclipped and fully interactive assigned to the main slot in both
  layouts (REQ-007 W15 re-run), and the persistence guard passes: Met — `W09-W` item 4: all
  eight size×layout combinations measured (non-zero xterm height, 36.64px from the panel
  body, echo round-trip visible at every combination), and the persistence guard passed
  (zero new websockets across the layout round-trip, MARKER preserved).
- On Linux a fresh store defaults the terminal slot to bash; the Windows default (PowerShell)
  and a Windows two-shell round-trip are owner checks belonging to `phase-wb-07`'s checklist,
  not closed here: Met for the Linux half — `W09-W` item 2's cleared-store check rendered
  bash visible in the terminal slot; the Windows half is explicitly deferred to the owner's
  checklist, and the coordinator reminded the owner at integration per delta 4.

## Backlog

- `status: complete`, `agent: agent-demo-stage` (kept as the record of who did the work).
- `next_action`: None — phase complete and integrated into `dev` (fast-forward to `08305cc`)
  under the kick-off record's delta-4 pre-approval; the post-fix Windows confirmations remain
  owner checks in `phase-wb-07`'s checklist.
- `completion_evidence`: `src/api/routes/demo_terminal.py`, `src/api/routes/workbench.py`,
  `_data/workbench/layouts/layout-1.json`, `ts/src/workbench/useWorkbenchLayouts.ts` (plus the
  full 17-file diff on `dev` at `08305cc`).
- `result`: the full gate account as written to `backlog.yaml` in commit `81e8404`.
- Removed from `next_up` in the completing change.

## Unresolved

- The Windows confirmations for this phase (fresh-store PowerShell default; a two-shell
  round-trip) are owner checks in `phase-wb-07`'s checklist — outstanding by design.
- The displacement notice's wrapper/action classes have no dedicated CSS rule (V3's cosmetic
  note) — usable but unstyled; a small follow-up for any later UI pass.
- The global-cap refusal's structured close reason cannot reach the browser (pre-accept close
  → uvicorn 403 → bare 1006); the frontend infers it structurally. Backend fix recorded as
  idea `000137`.
- The three environmental PTY test failures persist host-wide (ideas `000097`/`000099`); the
  owner directed a real fix, recorded as idea `000129`.
- `phase-wb-10` (runbook refresh) is unblocked and ready for a documentation session;
  `phase-wb-07` (owner-machine checks) follows it. Neither is dispatched from this pack.

## Review

Independent sub-agent review at close (fresh non-fork agent; code range `2ed5314..08305cc`; it
ran the verification commands, read the mechanisms, and drove the live app itself on ports
8012/5182 with a fresh browser profile). Findings verbatim:

- Diff scope: "touches exactly the declared deliverables ... plus `schemas/workbench-layout.schema.json`
  and `test/test_workbench_layout_schema.py`. Those two extra files are legitimately covered:
  idea `000098` ... explicitly asks for the schema + test to fulfill ADR-016's promise, and
  PROMPT-024 item 5 mandates them. Not a scope violation."
- Condition 1 (assignment dialog): "SUPPORTED. `LayoutConfigDialog.tsx` offers exactly one
  `<select>` per panel over `panel.eligible_slots`, no per-slot visible-panel controls, no
  geometry editing. Live check: displacement notice appeared verbatim ..., confirm applied the
  move, cancel reverts. Cleared-store reload restored bash-in-terminal / HTML-Viewer-in-main
  defaults with zero console errors."
- Condition 2 (concurrent shells, cap, platform route): "SUPPORTED WITH CAVEAT. Code confirms
  `MAX_CONCURRENT_SESSIONS = 6` and the gated `/platform` route; `curl` against the live route
  returned `{"platform":"linux","shells":[...]}`. I did not personally drive a live
  7th-session-refused/6th-admitted-after-close test (the session record attributes that to
  `W09-A`'s 12-connection attack, which I did not rerun) — code inspection and the cap
  constant support it, but I did not independently reproduce the concurrency edge case live."
- Condition 3 (unclipped shells in main, persistence guard): "SUPPORTED. Live reassignment of
  bash from terminal to main slot produced zero new websockets (instrumented via a `WebSocket`
  constructor proxy) and the pre-existing scrollback marker (`REASSIGN-MARKER-42`) survived
  intact in the Main slot after the move — this is the strongest possible confirmation of the
  record's central claim ... I did not re-run the full W15 four-size×two-layout
  pixel-measurement matrix myself; that rests on the record's own reported measurements."
- Condition 4 (Linux fresh-store bash default): "SUPPORTED. Verified live: cleared
  localStorage → reload → terminal slot header reads 'Terminal (bash) ▾'. Windows
  default/round-trip correctly left as an owner check."
- Mechanism review: "the file-doc reasoning (React's `updatePortal` treats a portal whose
  `containerInfo` changes as insert+delete, never update) matches the actual code ... I
  reproduced the exact failure mode it describes never occurring (zero websockets, surviving
  scrollback) live."
- Overall verdict: "No discrepancies found between the session record's claims and what the
  diff, code, and a live rerun support. `status: complete` for `phase-wb-09` is corroborated
  by independent review. The one caveat is condition 2's cap-refusal/admission edge case,
  which I did not personally re-attack live ... everything else was independently reproduced."

## Decisions

- The owner ratified the fix build via the kick-off record's delta 4: dispatches verbatim from
  the fixes pack, integration pre-approved behind a green gate, no descoping, the bounded
  enhancement lane open. All held; the lane implemented nothing beyond the pack.
- When the first adversarial run found the load-crash blocker, findings were routed through
  the phase's orchestrator for a fix cycle per the gate protocol rather than paused to the
  owner — correct under delta 4, and the fix landed inside the cycle cap for the crash itself.
- When the re-assignment session-kill survived two creator attempts, the coordinator spent the
  model policy's single documented opus escalation rather than authorizing a third quiet retry
  or descoping. The escalation found a root cause both prior attempts had misdiagnosed.
- The persistence-guard hygiene lesson from `phase-wb-08`'s close (run from a clean store;
  idea `000107`'s amendment) was applied to every browser dispatch in this phase's gate, and
  the guard passed cleanly everywhere it ran.
- Mid-session, the owner directed several process-level improvements captured for the next
  planning session rather than acted on in-flight: the batch triage reframe (`000125`), the
  anti-pattern tracking system (`000138`), and the delegation-scoping methodology (`000139`).

## Corrections

- The coordinator initially suspected the owner's uncommitted `src/demo/factory.py` edit in
  the primary checkout was a wb-09 agent writing to the wrong directory, and alerted the
  orchestrator accordingly. The owner confirmed it was their own separate-session work; the
  alert was stood down and the investigation closed without touching the file.
- Attempt 2's re-assignment fix (visible-panel write relying on React 18 batching) was
  presented as complete by the creator but disproven by the orchestrator's websocket-lifecycle
  trace before any validator ran — the two-attempt cap was then honored rather than retried.
  The durable lessons are recorded in `brain/procedures/runtime-behavior-needs-runtime-evidence.md`
  and `brain/procedures/scope-dispatches-to-the-turn-budget.md`.

## Left undone

- The Windows owner checks for this phase (fresh-store PowerShell default; a two-shell
  round-trip), plus `phase-wb-08`'s (terminal and viewer filling their slots) — all belong to
  `phase-wb-07`'s checklist, blocked behind `phase-wb-10`. The owner has already informally
  confirmed the viewer half on Windows (blank until the frontend flag was set, then working).
- `phase-wb-10` (runbook refresh: post-fix dialog description, platform-conditional default,
  the frontend-flag launch line) is unblocked, first in `next_up`, ready for a documentation
  session outside this pack; `phase-wb-07` follows it.
- The displacement notice's dedicated CSS rule (cosmetic, V3's note), the backend cap-refusal
  close-reason fix (idea `000137`), and the environmental PTY test repair (idea `000129`) are
  recorded, not built.
- The planning-triage batch (`000108`–`000140`, minus standalone `000122`) awaits the
  categorize/prioritize/group-into-plans session the owner directed (`000125`).
