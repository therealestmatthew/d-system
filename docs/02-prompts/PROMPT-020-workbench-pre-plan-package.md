---
schema_version: 1
id: doc-prompt-workbench-pre-plan-package
code: PROMPT-020
title: Workbench pre-plan package — seed the planning session for the stage-to-product build
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-live-demo, doc-prompt-demo-agent-factory]
---

# Workbench pre-plan package — seed the planning session for the stage-to-product build

The owner reviewed the integrated demo stage on 2026-09-10 and decided it becomes the real
management UI the project charter names (`CLAUDE.md`, sys-ui): a configurable workbench of
panels, layouts and injection controls. This document is the pasteable seed for the **planning
session** that turns that decision into governed documents and an executable build — the same
two-session shape that built the demo (factory: [PROMPT-010](PROMPT-010-demo-agent-factory.md);
build: [PROMPT-014](PROMPT-014-demo-build-orchestration.md)). Nothing here is implementation;
everything here is the owner's ratified input to planning.

**Deadline context: the live demo is in one week (week of 2026-09-15), and the demo presents
the workbench itself.** The demo track (`phase-demo-01`..`06`, plus `phase-demo-05` pending
integration and `phase-demo-07` in flight) is the foundation this builds on, not a parallel
track.

## How to run this

Paste the prompt block at the end into a fresh session. The session produces planning artifacts
only — requirement, decisions, plan, backlog phases, agent-roster deltas, and a delegation pack —
and stops for the owner's review before any build session starts.

## Decisions the owner has already made (do not re-ask these)

1. **Timing.** Everything below lands before the demo. The 2026-09-10 session was topic review,
   not demo day.
2. **Product framing.** The workbench is the chartered management UI, not a demo prop. The
   demo-only posture of the terminal decision (`ADR-013`) is superseded by new decision records
   this planning session writes; the parked idea `000087` (terminal interaction API) folds into
   this work rather than waiting separately. Loopback-only remains the default posture until a
   decision record says otherwise.
3. **Injection data sources.** Live enumeration with curated overrides: a backend route lists
   skills (`.claude/skills/`), agents (`.claude/agents/`) and prompts (`docs/02-prompts/`) from
   the repository, and an optional data file can override labels and injected text or hide
   entries. Selecting an entry injects its invocation text into the active shell un-executed,
   exactly like the existing command injection (REQ-006 R12 semantics).
4. **Layout persistence.** Named layouts ship as versioned JSON data files in the repository;
   the browser stores the active layout and per-slot panel selections locally.
5. **Notes strip.** Display-only. It shows the active entry; all controls live in its dropdown.
6. **Demo-criticality.** All four workstreams below are demo-critical. The planning session
   still proposes a descope ladder ordering what degrades first if the week runs short — the
   owner chose everything, so the ladder is for emergencies, not intent.
7. **`phase-demo-05` disposition.** It finishes and integrates against the current UI; its reset
   tool, OPS document and Windows checklist survive unchanged. The workbench track ends with a
   fresh rehearsal phase that updates the runbook, re-times the live segment against the final
   UI, and re-runs the rehearsal gate (`PROMPT-017`) semantics.

## The feature inventory (owner's specification, 2026-09-10)

### A. Notes strip (replaces the talking-points panel)

- No title, and not called "talking points". A short, wide display-only strip at the top right.
- The `?` tooltip moves to the strip's far left.
- Every button and configuration moves into one dropdown menu behind a standard dropdown
  affordance (button with a downward-triangle glyph).
- The vertical space freed below the strip hosts new right-hand panels (section E).

### B. Terminal panel rework

- A `(...)` ellipsis menu at the panel's top right collects: **Collapse terminal** (moves out of
  the header; the standalone collapse control goes away) and **Drop/restore terminal** (moves
  from page-level chrome into this menu).
- Drop changes meaning: the panel no longer disappears. The terminal area is replaced in place
  by an info page stating the terminal is inactive and how to activate it.
- While dropped, the injection dropdowns remain visible but deactivated — grayed out,
  unclickable.
- New injection dropdowns next to **Commands**: **Skills**, **Prompts**, **Agents** — same
  injection and same deactivation behavior, fed per decision 3.

### C. Layout engine

- Multiple named page layouts; the current arrangement (terminal panel left) is layout 1.
- Panels arrange into a layout's position slots; new panel types can stack above the terminal
  or occupy other slots as the layout dictates.
- A layout-configuration button at the page's top right opens the configuration surface.
- More panels than slots: each panel is assigned to exactly one slot per layout; a slot holding
  several panels renders its header name as a dropdown (small downward triangle beside the
  name) listing the slot's panels — selecting one swaps it into view and returns the previous
  panel to the list.

### D. HTML Viewer panel (generalizes and replaces the Overview panel)

- Displays a selected HTML page; the generated overview becomes just one selectable page.
- Header controls to the right of the title: a refresh button; a searchable dropdown listing
  compatible files under a selected directory (recursive), filtered by the search input; a
  button opening a dialog to change the searched directory.
- Tabs exactly like the terminal's session tabs; the selected directory and search context are
  scoped to the active tab, the controls themselves are shared.

### E. Explorer panels (right-hand side, in the space freed by A and D)

- **File Browser**: select a context folder; collapsible treeview of subdirectories and files;
  filter by text search and file type, hiding folders with no matches; right-click context menus
  varying by file type — initially "reveal in file explorer / open containing folder" for every
  entry, and "open in HTML Viewer" with a nested submenu choosing the target tab. A
  documentation-explorer mode (plans, decisions, requirements, …) is a File Browser
  configuration, not a separate panel.
- **Idea Explorer**: view, sort and filter ideas; toggle between the standard view and a
  priority-queue view. Reads idea state only through `fold()` (`src/db/ideas.py`) via a backend
  route — never the raw log.
- **Backlog Explorer**: the same configuration surface as the Idea Explorer, with the
  priority-queue option, over `docs/09-backlog/backlog.yaml`.

### F. Interchangeable shells

- Terminal (bash), **CMD** and **PowerShell** are three separate panel options in the slot
  dropdown, functionally identical — the existing PTY adapter's shell override and ConPTY
  backend are the mechanism. A shell unavailable on the host (CMD/PowerShell on Linux) must
  degrade to a clear in-panel message, not an error.

## What the planning session must produce (in order, before any code)

1. **Requirement document** (`--next-code requirement`): observable rows with verification
   methods for every item in the inventory, browser-verification methods in the established
   `demo-validator-web` style.
2. **Decision records** (`--next-code decision`): at minimum (a) the terminal/shell capability
   beyond the demo posture — gating, binding, session identity, and the fate of `ADR-013`
   (superseded or narrowed, stated explicitly); (b) the workbench read/action API surface
   (directory listing, file search, idea/backlog reads, reveal-in-explorer OS action) and its
   security posture; (c) layout persistence format and location.
3. **Plan** (`--next-code plan`) with backlog phases sized one session each, dependency-ordered,
   ending with the rehearsal-refresh phase (decision 7). Update `next_up`, `systems.yaml`
   maturity where responsibilities move, and the catalog.
4. **Agent-roster deltas**: which existing demo agents' charters extend (the `demo-orch-stage`
   extension commit `bf3e58e` is the precedent) and whether any new orchestrator or validator is
   needed. Fences in `.claude/settings.json` stay.
5. **Delegation pack**: pre-crafted, idempotent, verbatim-dispatchable prompts per phase in the
   `PROMPT-018` conventions (worktrees, ports, fix-cycle caps, completion gate per `GOV-003`'s
   demo-track decision — extend that decision's terms to the new track in the same document).
6. **Descope ladder** ordered for a one-week runway, and the open-questions list below resolved
   with the owner via AskUserQuestion — one batch at a time, at the point each matters.

## Open questions the planning session resolves with the owner (do not guess)

- Layout catalog: how many layouts to ship, their slot geometries, and which panels default
  where; what the layout-configuration surface edits (slot assignment only, or geometry too).
- Right-hand arrangement: which explorers are visible by default under the notes strip, and
  whether they share one slot with a header dropdown.
- HTML Viewer compatibility: which file types count as "compatible" (html only, or svg/md/pdf);
  whether the directory picker is browser-native or an in-app dialog fed by the file-browser API.
- Right-click menus: exact per-file-type options beyond the two initial ones; behavior on the
  Windows presentation machine vs the Linux dev machine for reveal-in-explorer.
- Idea/Backlog explorer columns, sort keys, and what "priority queue view" ranks by (backlog
  `next_up` + priority is the obvious candidate — confirm).
- Injection text per category: exact strings for a skill, an agent and a prompt entry (e.g.
  `/skill-name` vs a pasteable block), and whether curated overrides live in one file or one per
  category.
- Whether the notes strip's dropdown includes a file picker for switching the notes data file.

## Standing constraints

`AGENTS.md` governs; plan-before-code is mandatory; every governed document takes its code from
`--next-code`; the idea log is written only via the sanctioned writer; `AGENTS.md`/`CLAUDE.md`
are never edited without the owner's explicit approval; integration into `dev` is the owner's
call each time; a failing check is a result to record. The one-week runway is real — the
planning session should size phases so the build session can run them with the two-fix-cycle
cap and the completion gate without heroics.

---

## The prompt

> You are the planner for the D-System workbench build. Read `AGENTS.md`, then
> `docs/08-governance/GOV-006-conversation-guidelines.md`, then this document
> (`docs/02-prompts/PROMPT-020-workbench-pre-plan-package.md`) in full — it carries the owner's
> ratified decisions, the feature inventory, and the open questions. Produce the planning
> artifacts in the order its "What the planning session must produce" section lists, resolving
> the open questions with the owner via AskUserQuestion at the point each matters, one batch at
> a time. Do not write implementation code, do not re-ask decided questions, and do not start
> the build: stop when the requirement, decisions, plan, phases, roster deltas, delegation pack
> and descope ladder exist, governance exits 0, and the owner has the review summary — the
> build session (a `PROMPT-014`-style coordinator prompt you also draft) runs only after the
> owner approves the pack.
