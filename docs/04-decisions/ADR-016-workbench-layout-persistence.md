---
schema_version: 1
id: doc-workbench-layout-decision
code: ADR-016
title: Layouts are versioned repository JSON; the browser stores only selections
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui]
depends_on: [doc-workbench-requirements]
---

# Layouts are versioned repository JSON; the browser stores only selections

## Context

The workbench layout engine (REQ-007 W05/W06) needs named layouts with fixed slot geometries,
panel-to-slot assignment, and state that survives reload. The owner decided the split in
`PROMPT-020` (decision 4) and its open-question resolution (2026-09-10): named layouts ship as
versioned JSON data files in the repository; the browser stores the active layout and per-slot
panel selections locally; the configuration surface edits slot assignment only, never geometry.

## Decision

1. **Layout definitions live at `_data/workbench/layouts/`, one JSON file per layout.** Each file
   carries a `schema_version` integer, a stable layout id, a display name, its slot list — each
   slot with a stable slot id, its fixed geometry (grid-template areas/fractions, not pixels),
   and its default panel assignment — and the set of panel types it admits. Two ship: `layout-1`
   (terminal left, notes strip top right, HTML Viewer and the explorer slot below it) and
   `layout-2` (terminal full-width bottom, panel slots across the top).
2. **Geometry changes are data-file edits.** The configuration surface selects the active layout
   and assigns panels to slots; changing a slot's geometry or adding a layout is a reviewed
   commit of a JSON file. This keeps the demo-week UI small and every geometry change diffable.
3. **The browser stores selections only, keyed and versioned.** localStorage holds the active
   layout id, per-layout per-slot panel selections, the active notes file, and per-tab HTML
   Viewer state (directory, search, page) — under a single namespaced key carrying the
   `schema_version` of the layouts it was written against. Stored selections referencing an
   unknown layout, slot, panel or version are discarded silently in favor of the layout file's
   defaults — never an error, never a migration attempt in demo week.
4. **The repository defaults are the fallback state.** A fresh browser, a cleared store, or a
   version mismatch always yields layout-1 with its default assignments, so the demo machine's
   state is reproducible by clearing one key.

## Rejected alternatives

- **Persisting layouts server-side.** A write route contradicts the read-only API posture
  (ADR-015) for no demo-week gain; the owner's layouts are repository data.
- **Geometry editing in the UI.** Materially more frontend work and testing in a one-week
  runway, and it turns reproducible layout files into unreviewable browser state (owner
  decision, 2026-09-10).
- **Pixel geometries.** Fractional/grid definitions keep the zero-scroll obligation (REQ-006
  R02) satisfiable at all four required window sizes from one definition.

## Consequences

- REQ-007 W05/W06 verify switching, assignment, persistence and the absence of geometry editing;
  the layout JSON schema is asserted by a test so a malformed layout file fails before it ships.
- Panels added by later phases declare a panel type id once and become assignable wherever a
  layout's slots admit them; new layouts are new files, no code change.
- The notes strip's file choice and the viewer's tab state follow the same repository-defaults /
  browser-selections split (W01, W08).
