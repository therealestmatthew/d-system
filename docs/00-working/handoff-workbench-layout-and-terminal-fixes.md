# Hand-off: workbench terminal truncation fix and layout-assignment redesign

Ungoverned working document (ADR-010). Written 2026-09-11 by the workbench coordinator session,
from the owner's direction, to be given to a fresh session. That session's job is to produce, in
order and under the repository's normal flow (AGENTS.md; requirements and plan before code):

1. A delta section in the workbench requirements (`REQ-007`) covering both fixes below.
2. New phases appended to the workbench plan (`PLAN-022`) and the backlog
   (`docs/09-backlog/backlog.yaml`): `phase-wb-08` (terminal truncation fix, **first priority**)
   and `phase-wb-09` (layout-assignment redesign, second), each with scope, acceptance and
   verification in the backlog's existing shape.
3. A new delegation pack following `PROMPT-021`'s conventions (kickoff / creator / validator /
   adversary / browser-verification prompt sections per phase, named worktrees and ports,
   verbatim dispatch, GOV-003 completion gate).

The owner has already made the design decisions recorded below; do not re-litigate them. Where
this document marks something an **assumption** or an **open item**, confirm it with the owner
(AskUserQuestion) before writing it into a requirement.

---

## Fix 1 (first priority): terminal panel truncation — idea `000104`

**Symptom.** The terminal panel's xterm area collapses vertically while the shell inside stays
alive and interactive. Observed three independent ways on 2026-09-11:

- Linux, rehearsal pass 2 (`W07-R`): panel clipped to ~85px / 2 visible rows; `.xterm` container
  `getBoundingClientRect()` height **0** while its child `.xterm-screen` measured 372.99.
- Linux, `W07-W` and the layout-persistence check: reproduced height 0 / screen 390; content
  readable only from `.xterm-rows` innerText, not on screen.
- **Windows, owner's machine: the panel renders fully blank white.** Same bug, fully collapsed:
  the terminal body's dark background (`.stage-region__body--terminal`, `#0d1117`) has zero
  height, so the panel's base `.stage-region` background (`#fff`,
  `ts/src/stage/StagePage.css`) is what shows.

It affects all three shell panels (Terminal/bash, CMD, PowerShell) — they share one component
(`TerminalRegionCmd`/`TerminalRegionPowerShell` are parameterizations of `TerminalRegion`,
`ts/src/workbench/panelRegistry.tsx`).

**Suspected mechanism — verify, do not assume.** The height chain
(`.stage-workbench-slot` → `.stage-region` → `.stage-region__body--terminal` →
`.stage-terminal-sessions` (flex `1 1 auto`, `min-height: 0`) → absolutely-inset session divs →
`.stage-terminal-mount` (`height: 100%`) → `.xterm`) breaks somewhere when the terminal renders
inside the **multi-panel slot wrapper** (`ts/src/workbench/Slot.tsx` wraps the panel in an extra
`section.stage-region.stage-workbench-slot--multi` once a slot admits more than one implemented
panel — which the terminal slot has since `phase-wb-03` shipped the shell panels). The related
cosmetic double-header issue in the same wrapper is idea `000101`. Root-cause before fixing.

**Why first priority.** The owner cannot run the phase-wb-07 owner-driven dry-runs or the
Windows checks (REQ-006 R09, REQ-007 W12) while the terminal is invisible, and the live demo is
2026-09-15.

**Acceptance sketch** (the fresh session refines into REQ-007 delta language):

- The fix covers all three shell panels equally — Terminal (bash), CMD and PowerShell — not
  just the bash panel it was first observed on (owner-confirmed 2026-09-11).
- The active shell panel visibly fills its slot's body in both layouts at the demo window sizes,
  on Linux and Windows; typed input and output are visible without DOM inspection.
- The fix must hold in **any slot a shell panel can occupy**, not only the terminal slot's
  current geometry. Once Fix 2 lands, all three shells become assignable to the smaller main
  slot (owner-confirmed 2026-09-11): phase-wb-09's verification must re-run the visible-fill
  check with a shell assigned to the main slot in both layouts, so a fix that hard-codes the
  terminal slot's dimensions fails the later phase rather than slipping through.
- The zero-page-scroll rule (REQ-006 R02) still holds.
- Session persistence across layout switches does not regress. Regression guard (already proven
  green today, keep as a verification step): set `MARKER=persist$RANDOM` in Layout 1, switch to
  Layout 2 and back, `echo check-$MARKER` prints the same value both times, and no new terminal
  websocket opens during the switches.

---

## Fix 2 (second priority): layout configuration — assignment model, not a duplicate switcher

### What exists today (audited 2026-09-11)

- Eligibility lives on the **slot**: each layout file (`_data/workbench/layouts/layout-1.json`,
  `layout-2.json`) gives every slot an `admits` list and a `default_panel`. The admits sets are
  disjoint across slots, so a panel can never move to another slot: the terminal slot admits
  only the three shells, the main slot only `html-viewer` (plus `overview` in layout-2).
- The stored browser state (ADR-016) is per-layout, per-slot: which admitted panel the slot
  currently shows.
- The "Configure layout ▾" dialog (`ts/src/workbench/LayoutConfigDialog.tsx`) renders one
  `<select>` per slot over the same admits list — operationally identical to each slot's header
  dropdown. The owner confirms this duplication was never the intent: **the layout config was
  never meant to control which panel is visible in a slot, only which panels are assigned to
  which slot.**

### The intended model (owner's specification, 2026-09-11 — decided, not open)

There is a set of layout slots **L** and a set of panels **P**. Each panel `p` carries a set of
eligible slots (eligibility moves from the slot to the panel). In the layout configuration, each
`p` is assigned to **exactly one** eligible slot `l` — a total mapping P → L. Decisions:

1. **Multi-occupancy presents as a dropdown switcher.** A slot holding several assigned panels
   shows one at a time, with the header dropdown switching among them — exactly the current
   terminal-slot behavior, applied uniformly to any multi-panel slot.
2. **Header dropdowns stay, as switchers only.** They list the panels currently assigned to
   that slot and control which is visible. They never re-assign.
3. **The config dialog becomes the assignment surface.** Per panel, a selector over that
   panel's eligible slots. It no longer offers per-slot visible-panel selects.
4. **Two live shells at once is allowed.** Terminal in one slot and CMD/PowerShell in another
   may render simultaneously.
5. **Raise the backend's global concurrent-PTY cap from 4 to 6** (the session registry of
   ADR-014, `src/api/routes/demo_terminal.py`, currently "bounds concurrent sessions to four").

### Concrete eligibility the owner specified

- The current terminal slot (layout-1 left / layout-2 bottom) and the current HTML Viewer slot
  (main) must **each admit all four**: Terminal (bash), CMD, PowerShell, HTML Viewer. So all
  four panels have eligibility {terminal slot, main slot}, and e.g. HTML Viewer in the large
  slot with Terminal in the smaller one is a legal assignment.
- Notes strip and the explorer slot/panels (File Browser, Idea Explorer, Backlog Explorer) are
  unchanged — the owner named only the two slots and four panels above.

### Assumptions and open items — confirm with the owner before writing requirements

- **Overview panel:** today `overview` is layout-2's main-slot default. Assumption: it stays
  eligible for (only) the main slot and joins the assignment model there. Confirm.
- **Per-panel session-tab cap vs the new global cap:** REQ-006 R10 says "up to four terminal
  sessions as tabs" per terminal panel, and `MAX_SESSIONS = 4` in
  `ts/src/stage/TerminalRegion.tsx`. With the global cap moving to 6 and two shell panels
  visible at once, decide how R10's per-panel text reconciles with the 6-session registry
  (e.g. per-panel cap stays 4, global 6 enforced server-side as today). Confirm the intended
  numbers with the owner and update R10's language accordingly.
- **Storage shape and migration:** the persisted state changes from per-slot selection to
  per-panel assignment plus per-slot visible choice. ADR-016 rule 4's existing pattern (invalid
  or old-schema stored state dropped silently in favor of defaults) is probably sufficient —
  propose whether a schema-version bump suffices or an ADR-016 amendment is needed.
- **Defaults:** each layout file needs a default assignment (suggestion: today's effective
  arrangement — shells + HTML Viewer default to their current homes — so a cleared browser
  looks unchanged). Confirm.

### Interaction with Fix 1

Fix 1 lands first and must not be broken by Fix 2: re-assigning a panel between slots will
re-parent the terminal in the DOM. Where feasible keep component instances alive across
re-assignment (the layout-switch persistence works because `StagePage.tsx` keys slots by
`slot_id` in one grid); where a re-assignment must remount a shell panel, the behavior must be
explicit and stated, never a silent session kill. The Fix 1 regression guard above applies to
Fix 2's verification too, and so does Fix 1's slot-independence obligation: after Fix 2, each
of the three shell panels must render unclipped and fully interactive when assigned to the
smaller (main) slot, exactly as in the terminal slot.

---

## Standing constraints for the fresh session

- AGENTS.md governs; requirements and plan before code; ask before integrating a feature branch
  into `dev`; never write a confidential identifier into a tracked file; never edit `CLAUDE.md`
  or `AGENTS.md` without explicit approval.
- `tools/demo_reset.py`, `OPS-013` and the phase-wb-07 runbook/checklist deliverables are not
  touched by these fixes (the runbook will need a follow-up update after Fix 2 changes the
  config dialog — note that in the plan, do not fold it into these phases without asking).
- Evidence sources: idea `000104` (truncation), idea `000101` (double header in the multi-panel
  wrapper), `docs/03-sessions/SESS-2026-09-11-05-rehearsal-refresh.md` (rehearsal findings),
  the W07-W report and layout-persistence check recorded in that session's conversation.
- The live demo is **2026-09-15**; the owner's dry-runs are blocked on Fix 1.
