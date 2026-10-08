---
schema_version: 1
id: doc-adr-slot-configuration-schema-model
code: ADR-031
title: Slots are schema-owned frames with sub-slots, and panel instances are matched to slots by structure
kind: adr
status: draft
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-layout, sys-wb-styles, sys-wb-terminal]
depends_on: [doc-workbench-architecture-quality-requirements, doc-workbench-architecture-quality, doc-workbench-requirements, doc-workbench-content-fit-contracts-requirements, doc-workbench-terminal-decision, doc-workbench-api-decision]
supersedes: [doc-workbench-layout-decision]
---

# Slots are schema-owned frames with sub-slots, and panel instances are matched to slots by structure

## Status

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** Written by
`phase-arch-06` (decide the slot configuration-schema model, superseding `ADR-016`) under the
Session Manager's pre-approved run. The owner has not reviewed it. It gates five phases, each of
which builds against the recommendation below, so a different ruling changes that phase's scope:
`phase-arch-07` (schema-owned slots and sub-slots with structural eligibility), `phase-arch-08`
(multi-instance panel identity), `phase-arch-09` (reconfigurable slot geometry with per-role content
constraints), `phase-arch-10` (the sub-app package contract) and `phase-arch-17` (panel maximize and
collapse). The ratification points are collected in "Open items for the owner" at the end. Nothing
is built by this record.

`ADR-016` is marked `superseded` in the same change, because the governance validator rejects a
`supersedes` target that is not (`GOV-001`). That has a side effect the owner should see: until this
record is ratified, `ADR-016` still describes what the shipped workbench does, and its status says
otherwise. If the owner rejects this record, revert both front matters in one commit.

Field names and file names below are indicative; the properties are binding. The phases that build
them may rename a field if they keep the property.

## Context

`REQ-011` (`R11`) requires the slot and sub-slot model to be recorded in an ADR that supersedes
`ADR-016`, stating what it keeps and what it changes. Four owner ideas converge on one model, and
`PLAN-028` group `G43` and its design decision 3 rule that the model replaces `ADR-016` rather than
amending it:

- `000141` (slots as configuration schemas with nested sub-slots): each slot has a fixed structure,
  such as a top bar with places for buttons and dropdowns; a slot is either a single place for one
  kind of panel, or a nest of sub-slots that each admit certain element types; a panel is eligible
  when its element configuration matches what the sub-slots support.
- `000101` (the double-header defect): a swapped-in panel renders its own header under the slot's
  header.
- `000135` (multiple copies of a panel type): panel identity is singleton by `panel_id` in the layout
  data, the storage shape and the panel registry, and touches session ownership too.
- `000133` (slot geometry and customization): revisit the geometry editing `ADR-016` excluded,
  stating constraints per slot role rather than per current occupant.
- `000233` (maximize a panel and collapse it back): `PLAN-028` design decision 5 rules it slot-level.

Facts from the repository that bind the decision. These were read from source on 2026-10-08; none
was rendered in a browser by this phase.

1. **Every slot has a header, and eight of the nine panel types draw a second one.** `Slot.tsx`
   always renders a `<header>` (a plain title, or a panel switcher). `TerminalRegion.tsx` (which
   serves `terminal`, `terminal-cmd` and `terminal-powershell`), `HtmlViewerRegion.tsx`,
   `OverviewRegion.tsx`, `FileBrowserRegion.tsx` and `explorer/ExplorerRegion.tsx` (which serves
   `idea-explorer` and `backlog-explorer`) each render their own `<header className="stage-region__header">`
   holding a title plus real controls: refresh, file pickers, view toggles, injection dropdowns, a
   help tooltip. Only `notes-strip` has none. So the defect `000101` describes is not confined to a
   multi-panel slot's dropdown swap; any slot hosting those eight types has two bars.
2. **The panel's header carries controls that cannot simply be deleted.** A model that removes the
   second bar must give those controls a place in the first.
3. **Eligibility is a list on each panel.** Layout files carry `panels[].eligible_slots`
   (`REQ-007` W16). It is read by `useWorkbenchLayouts.ts`, `LayoutConfigDialog.tsx`, `types.ts`,
   `test/test_workbench_layout_schema.py` and `test/test_workbench_fit_contracts.py` (which builds
   its live matrix from it).
4. **Panel identity is one string with three jobs.** `panel_id` is the registry key
   (`PANEL_REGISTRY` in `panelRegistry.tsx`), the layout key (`panels`, `default_assignment`,
   `default_visible_panel`) and the storage key (`panel_assignments`, `slot_visible_panel`). It also
   keys `StagePage.tsx`'s per-panel host element, which is what lets a live panel survive a
   reassignment or a layout switch (`REQ-007` W15, W16). Two layouts that both name `terminal` share
   one live terminal. So identity is workbench-wide, not layout-scoped.
5. **Some per-panel state is stored once, not per panel.** `html_viewer_tabs` and
   `active_notes_file` are single fields in the stored state (`storage.ts`). A second HTML Viewer
   would read and overwrite the first's tabs.
6. **Terminal session ownership is local to the panel component, with a bare registration key.**
   `TerminalRegion` holds its tab list and per-tab websocket in component state (cap four tabs per
   panel); the backend registry (`SESSIONS` in `src/api/routes/demo_terminal.py`) keys sessions by a
   server-generated id the browser never sees and caps them at six globally (`ADR-014`). The panel
   registers with the cross-panel bridge as `terminalBridge.register(handle)`, with no key, so a
   second terminal would replace the first's registration. The bridge already accepts a key
   (`ADR-029` section 6 point 1).
7. **The terminal panel carries a geometry path of its own.** `TerminalRegion` has a `collapsed`
   flag that hides the screen and a `stage-region--terminal-collapsed` class. `REQ-011` `R25` forbids
   any panel from implementing its own geometry.
8. **Three constraints are already specified and must stay true.** `REQ-006` `R02` (zero page
   scroll) at 1280x720, 1366x768, 1920x1080 and 1024x768; `REQ-007` W15 and W16 (fill, and a shell
   session survives reassignment); and `REQ-037` (the per-panel content-fit contracts that
   `test/test_workbench_fit_contracts.py` reads and asserts).

Vocabulary follows `brain/concepts/terms-workbench-ui.md`: a slot is the container, a panel is its
content, an element is a part inside a panel, and a slot id names the slot's role (`primary`,
`secondary`, `strip`, `explorer`), never a panel type. This record adds one term, **panel
instance**, defined in decision 5.

## What is kept from ADR-016, and what is replaced

`PLAN-028` asks that the supersede read as a change to the structural model and not to the
persistence posture. The four decisions of the layout decision (`ADR-016`), one by one:

| `ADR-016` decision | Verdict | Reason |
|---|---|---|
| 1. Layouts are versioned JSON at `_data/workbench/layouts/`, one file per layout, with a stable id, a display name, slots with stable ids, fractional grid geometry and default assignment, and "the set of panel types it admits" | **Keep**, except the last clause, which is **replaced** | The location, the one-file-per-layout rule, the `schema_version` integer, stable slot ids and fractional geometry are not in question, and the shipped layouts and their tests rely on them. "The set of panel types it admits" is the per-panel allow-list that `R12` removes. It is replaced by structural eligibility (decision 4). |
| 2. Geometry changes are data-file edits; the configuration surface never edits geometry | **Replace** | Its reason was a one-week runway and the risk of unreviewable browser state (`ADR-016`, 2026-09-10). The runway has ended, and `000133` asks to revisit exactly this. Decision 8 admits bounded track-size selections in the browser while topology, ranges and floors stay in data, which answers the second reason. |
| 3. The browser stores selections only, under one namespaced key carrying the layouts' `schema_version`; unknown layout, slot, panel or version is discarded silently in favor of the layout file's defaults, never an error, never a migration | **Keep**, with the stored shape widened | "Selections only" and the silent-discard rule are the load-bearing choices and `R05`, `phase-arch-08` and `R27` all rely on them. What changes is what a selection refers to (an instance, not a bare panel id) and the list of things that are explicitly not stored (maximize, collapse). The words "in demo week" are dropped as a qualifier: no migration code is written for any version bump, now or later, unless a later record says otherwise. |
| 4. The repository defaults are the fallback state; a fresh browser, a cleared store or a version mismatch yields layout-1 with its default assignments | **Keep unchanged** | Nothing in the new model touches it, and clearing one key as the way to reset a machine is still what the demo needs. |

Of `ADR-016`'s three rejected alternatives: server-side layout persistence stays rejected
(`ADR-015` rule 4 is unchanged); pixel geometries stay rejected for layout definitions (decision 8
introduces content floors, but the layout files stay fractional, and a standing check keeps the
floors satisfiable at the smallest required window); geometry editing in the UI is reversed in part,
for the reason in the table.

## Decision

### 1. A slot is a schema-owned frame: one top bar and one body, and panels fill the sub-slots

Every slot renders exactly one **frame**, drawn by the slot and never by a panel. A frame has a **top
bar** and a **body**. The top bar is a fixed set of named **sub-slots**, in order:

| Sub-slot | Filled by | Admits | Purpose |
|---|---|---|---|
| `identity` | the slot | (none) | The hosted instance's label, as plain text, or as the panel switcher when the slot holds more than one instance |
| `help` | the panel | `help` | The help tooltip a panel has today |
| `controls` | the panel | `action`, `choice`, `toggle` | The buttons, dropdowns and toggles a panel has today in its header |
| `frame_actions` | the slot | (none) | Maximize and collapse (decision 9); nothing a panel supplies |

The body is one sub-slot that admits a **body kind** (decision 4) and hosts the panel's content.

**A panel never draws a top bar.** It declares element types and renders its elements into the
sub-slots the slot gives it. The panel module has no import path to a header renderer and its markup
contains no `.stage-region__header`. Two bars in one slot therefore cannot be produced by a panel
that follows the contract, and `R13` is asserted as a standing check anyway: assign every panel type
into every slot it is eligible for, in both layouts, and count the rendered top bars per slot; any
count other than one fails.

The mechanism is `phase-arch-07`'s to choose. The properties it must hold: (1) a panel has no way to
render a top bar; (2) a panel's bar elements keep its state, so a viewer's refresh button still sees
the viewer's active tab; the recommended form is a typed wrapper a panel renders in its own tree,
which places its children into the matching sub-slot of whichever slot currently hosts the
instance; (3) the elements follow the instance across a reassignment without remounting the panel,
which is the existing per-instance host element's job; (4) an element whose type the hosting slot
does not admit is a render-time error caught by the existing per-panel error boundary, not a silent
omission.

### 2. Slot schemas are repository data, one per role, shared by every layout

Slot structure lives in one tracked file, `_data/workbench/slot-schemas.json`, validated by a JSON
Schema under `schemas/`. It holds three things:

- an **element-type vocabulary**: the bar element types (`help`, `action`, `choice`, `toggle`) and
  the body kinds (`terminal-screen`, `document-frame`, `tree`, `table`, `ticker`), each body kind
  carrying its content floor (decision 8);
- named **frames**: a top-bar structure (the table in decision 1) with a capacity per panel-filled
  sub-slot, and an arrangement (`stacked`, or `inline` for a body that shares the bar's row);
- one entry per **role**, naming a frame and the body kinds its body admits.

A layout file lists slots by `slot_id` (the role) and does not restate or override a role's
schema. So the same role has the same structure in every layout, which is what lets constraints be
stated per role (decision 8). Because `slot_id` is the role, no separate role field is added.

Proposed starting content, which `phase-arch-07` confirms by measuring the nine panels:

| Role | Frame | Body admits |
|---|---|---|
| `primary` | `standard` (stacked) | `terminal-screen`, `document-frame` |
| `secondary` | `standard` (stacked) | `terminal-screen`, `document-frame` |
| `explorer` | `standard` (stacked) | `tree`, `table` |
| `strip` | `compact` (inline) | `ticker` |

`primary` and `secondary` have the same schema because the shipped data already makes them
interchangeable and the terms file says the only honest difference is which surface is focal. They
remain two roles. The strip uses an inline frame so its body shares the bar's row and it keeps
the single thin row it has today; this is still one bar. Capacity numbers (`controls` and `help`
per frame) are for `phase-arch-07` to set from the real element counts of the nine panels; they must
not exclude any assignment that `REQ-007` W16 ships.

### 3. Nesting: a slot is a tree of depth two, and a single slot is the degenerate case

A schema is a tree. The root is the frame. Its children are either **leaf sub-slots** (they admit
element types and have a capacity) or one **group** (the top bar, whose children are leaves). A
group contains leaves only. So the deepest path is frame, group, leaf.

`000141` distinguishes a "truly single slot for a single element-type panel" from "a nested structure
of sub-slots". Both fit: a single slot is a frame whose top bar has no panel-filled sub-slot and
whose body admits one body kind (the `strip` role is near this). A composite slot is a frame with
panel-filled bar sub-slots. No separate "kind" flag is needed; the shape of the tree is the
distinction.

Depth two is a bound, not a measured need. No shipped panel has a control group nested inside
another, and a recursive grammar would need a renderer and a matcher for a shape nobody has. A
deeper tree is a later schema version.

### 4. Eligibility is a structural match, and nothing else decides it

Each panel type declares an **element configuration** next to its component, in `PANEL_REGISTRY`
(the one registration point `REQ-037` discovers by parsing that literal):

```ts
'html-viewer': {
  displayName: 'HTML Viewer',
  Component: HtmlViewerRegion,
  elements: { body: 'document-frame', bar: ['action', 'choice', 'toggle'] },
},
```

A panel type is **eligible** for a role when, and only when:

1. the role's body admits the panel's `body` kind; and
2. every element in the panel's `bar` list can be routed to a panel-filled sub-slot of the role's
   frame that admits its type, taking sub-slots in declaration order and respecting each sub-slot's
   capacity; and
3. every required sub-slot is satisfied (the body is required).

The inputs are the panel's element configuration and the role's schema. The panel type's id, the
slot id and the layout are not inputs. An element configuration is a property of the component's
code, so it lives with the component and cannot drift from what it renders; a data file listing it
would be a second copy.

**Applied to the shipped panels, the rule reproduces `REQ-007` W16's eligibility in all but one
cell.** Checked on 2026-10-08 against both shipped layout files, with `terminal`, `terminal-cmd` and
`terminal-powershell` as `terminal-screen`, `html-viewer` and `overview` as `document-frame`,
`file-browser` as `tree`, `idea-explorer` and `backlog-explorer` as `table`, and `notes-strip` as
`ticker`: 16 of the 17 panel-in-layout rows match W16, and in the 17th `overview` in layout 2 becomes
eligible for `secondary` as well as `primary`. That is correct by the rule (`overview` embeds an iframe exactly
as the HTML Viewer does) and is a visible change, so it is open item 3. `overview` is the panel type
`phase-arch-03`'s duplication audit may retire.

There is no per-panel or per-slot allow-list anywhere, including as a generated cache. `R12`'s
verification includes a layout carrying an `eligible_slots` key failing the layout JSON Schema.

### 5. A panel instance is declared in layout data and carries its own identity

A **panel type** is a kind of panel (a `PANEL_REGISTRY` key). A **panel instance** is one occurrence
of a type in the workbench, with its own live state. This record adds the second term; the terms file
should gain it when `phase-arch-08` lands.

Layout files declare instances, not types:

```json
"panels": [
  { "instance_id": "html-viewer",   "panel_type": "html-viewer" },
  { "instance_id": "html-viewer-2", "panel_type": "html-viewer", "label": "HTML Viewer 2" }
],
"default_assignment": { "html-viewer": "primary", "html-viewer-2": "explorer" }
```

- `instance_id` is a lowercase kebab string, unique across the **workbench**, not only within a
  layout. Two layouts that declare the same `instance_id` refer to the same live instance, which is
  how a shell survives a layout switch today (fact 4). A standing check asserts that every layout
  declaring an id gives it the same `panel_type`.
- The first instance of a type keeps the type id as its instance id (`terminal` is the
  `terminal` instance of type `terminal`); further instances are `<type>-<n>` from 2. This keeps the
  shipped defaults, tests and prose readable, and makes a bare type id used where an instance id is
  meant an obvious bug rather than a silent one.
- `label` is optional and shown in the `identity` sub-slot; it defaults to the type's display name,
  with an ordinal appended when a layout declares more than one instance of the type.
- `panel_id` stops existing as a name in layout data, storage and the TypeScript types, so a type and
  an instance cannot be confused. The code distinguishes the two by distinct types
  (`PanelTypeId`, `PanelInstanceId`), and a panel component receives its identity from a hook
  (`usePanelInstance()`), not from props, because `Component` is a zero-prop component type today.
- `eligible_slots` is removed from `panels` (decision 4). Eligibility is computed per instance from
  its type.
- The three terminal types stay three types. Collapsing them into one type with a shell setting is a
  separate refactor with no requirement behind it, and `REQ-037`, `REQ-007` W12 and the platform
  default are keyed by type.
- **Instances are declared by the repository, not created in the browser.** Multiplicity in
  `000135` ("technically able to create multiple copies") is satisfied by the model: a layout can
  declare any number of instances of a type. A browser-created instance would be a stored
  definition, which `ADR-016` rule 3 (kept) forbids, and it would give selections that refer to
  ids no layout declares. Open item 2.
- **Within a slot, multiplicity means "assigned", not "visible together".** A role's body has a
  visible capacity of one. Two instances of a type assigned to the same slot are switched with the
  `identity` dropdown, as any two panels are. A schema whose body admits two visible instances is
  expressible (a body capacity above one) but none ships, because no layout needs a split slot.
  `phase-arch-08` implements across-slot multiplicity and within-slot assignment.

### 6. What the browser stores, and what it does not

The single namespaced key and the silent-discard rule are kept. The stored state after
`phase-arch-08`:

| Field | Shape | Notes |
|---|---|---|
| `active_layout` | layout id | unchanged |
| `panel_assignments` | layout id, then instance id, then slot id | validated against the layout's declared instances and structural eligibility |
| `slot_visible_panel` | layout id, then slot id, then instance id | unchanged in form; values are instance ids |
| `instance_state` | instance id, then that instance's own state | replaces the single `html_viewer_tabs` and `active_notes_file` fields; each panel validates its own entry, as the viewer validates its tabs today; an entry for an undeclared instance is dropped |
| `grid_tracks` | layout id, then column and row track sizes | added by `phase-arch-09` (decision 8); optional |

**Not stored, by rule:** maximize and collapse state (decision 9), open popovers, scroll positions,
terminal output, session ids and anything that names a websocket. A reload returns to the layout
file's arrangement plus the stored selections above.

The repository holds everything that defines the workbench's structure: slot schemas, layout
topology, the declared instances, default assignment and visibility, default track sizes and
content floors. The panel registry (code) holds each type's element configuration.

### 7. Session ownership: per instance in the browser, no change on the server

A terminal instance owns its tab list and the websockets behind it, as `TerminalRegion` does now,
keyed by `instance_id` wherever a key is needed. Concretely: the bridge registration key is the
instance id (`terminalBridge.register(handle, instanceId)`), so a second terminal registers beside
the first instead of replacing it; per-instance state is stored under `instance_state`; and the
instance's tabs end when the instance unmounts, as now.

**The server is unchanged.** The backend session registry keeps its server-generated id, the cap of
six, and its structured refusal (`ADR-014`, `REQ-012` `R20` and `R21`). The per-panel cap of four
tabs stays. With several terminal instances the product of four tabs and N instances can exceed six,
and the existing refusal already reports that clearly; `phase-arch-08` proves it with two instances
and does not raise either number. The server is not told which instance owns a session, because (a)
a session's life is its websocket's, so the browser-side owner is enough to end it, and (b) a
client-asserted label on an unauthenticated route is a second identity scheme with nothing
enforcing it (`ADR-030` fact 4). If the external terminal API (`ADR-030`) later needs to address a
session by instance, that record decides it.

Cross-panel actions need a rule for which instance they reach. The bridge's batch contract
(`ADR-029` section 6) leaves fan-out to the caller and defaults an omitted key to the most recently
registered handle. With two instances of a type that default is arbitrary from the user's point of
view. `phase-arch-08` states and tests the rule; the recommendation is that a caller without an
explicit key reaches the visible instance the user last interacted with.

### 8. Geometry: constraints come from the schema, and the browser may choose track sizes inside them

Three parts.

1. **Constraints are stated per body kind and apply to every role that admits the kind.** A role's
   floor is derived from every kind its body admits, never from the instance currently assigned. So
   the `secondary` role's floor is the larger of the `terminal-screen` and `document-frame` floors,
   and an instance moved there cannot find the slot smaller than its kind needs. This is `000133`'s
   "per slot role rather than per current occupant". A floor is stated in content units (a terminal
   screen's minimum rows and columns, a document frame's minimum scaled width, a tree's or table's
   minimum visible rows) and converted to pixels by the renderer. A floor must be at least the
   smallest box the matching `REQ-037` panel contract needs, plus the frame's own chrome; a
   standing check asserts that inequality, so the slot side and the panel side cannot disagree.
2. **Topology, ranges and floors stay repository data.** Which slots a layout has, where they sit in
   the grid, the default track sizes, and every floor are reviewed commits. Adding a layout is a
   file.
3. **Track sizes are a browser selection, clamped by the floors.** The grid's column and row sizes
   (fractions) may be adjusted in the browser and stored as `grid_tracks` per layout. The renderer
   enforces each track's floor with `minmax(<floor>, <size>fr)`, so a stored value can never make a
   slot smaller than its role allows, and the zero-scroll obligation does not depend on what is
   stored. A stored value of the wrong shape or unit is discarded to the layout's default sizes
   under the kept discard rule. Resetting is clearing the key, or a reset control.

The pixel concern that rejected "pixel geometries" in `ADR-016` is met by a standing check: the sum
of the floors along each axis, plus gaps and page chrome, must fit the smallest required window
(1024x768) for every shipped layout. A layout whose floors cannot all be satisfied at once fails
that check at commit time rather than scrolling at the owner's window size.

The drag or keyboard interaction that changes a track size is `phase-arch-09`'s. This record fixes
only that the stored value is track fractions and that floors win.

### 9. Maximize and collapse are slot frame actions on transient state

Maximize and collapse live in the `frame_actions` sub-slot, which only the slot fills, so every
panel type has them and none implements them (`R25`).

- **Transient.** The state (which slot is maximized, which are collapsed) lives in the workbench's
  in-memory state, keyed by slot id. It is never written to the stored state, so a reload renders
  every panel in its assigned slot (`R27`).
- **No remount, no reparent.** Maximizing changes the geometry of the slot element that already
  holds the instance's host; it does not move the host or unmount the panel. A shell therefore keeps
  its session across maximize and collapse (`R28`), which is the one property that cannot be added
  afterwards. Other slots stay mounted underneath.
- **Collapse is a slot action.** The terminal's own collapse toggle (fact 7) is a panel-owned
  geometry path and is what `R25`'s grep will flag. The recommendation is that it becomes the slot's
  `collapse` frame action (body hidden, panel still mounted, bar still visible), so the terminal
  keeps the behavior and loses the code. If `phase-arch-17` retires it instead, it amends the
  `REQ-007` row that specifies it.
- The zero-scroll and fill checks (`REQ-006` `R02`, `REQ-007` W15) hold in both states at all four
  sizes in both layouts (`R26`).

### 10. Migration from schema_version 3

The kept discard rule is the migration: a version bump means the old key is never read again and
every reader falls through to the layout files' defaults. No migration code is written. The shape
changes land in three phases, and each bumps `schema_version` in the same commit as the shape change
(the `phase-arch-02` precedent for the slot-id rename, version 2 to 3).

| Phase | Layout file change | `schema_version` | Stored state effect |
|---|---|---|---|
| `phase-arch-07` | `eligible_slots` removed from `panels`; slot schemas added as a new file | 3 to 4 | Selections written under version 3 are not read |
| `phase-arch-08` | `panel_id` becomes `instance_id` plus `panel_type`; `instance_state` replaces the two single fields | 4 to 5 | Selections written against singleton ids are discarded to defaults, no error (`phase-arch-08` acceptance) |
| `phase-arch-09` | none required (`grid_tracks` is an additive optional stored field; floors live in the schema file) | none unless the layout file changes | Existing selections stay valid |

Each bump discards the browser's stored selections once. That is the stated cost of the kept rule
and it is small: three clearings of a machine whose defaults are the reproducible state. The old
`d-system:workbench-state:v3` entry remains in `localStorage` unread; nothing deletes it.

The `schema_version` that namespaces the storage key stays the layout files' version. The slot
schema file carries its own `schema_version`, independent of the key, because changing a floor does
not change what a stored selection means.

## What each downstream phase builds

| Phase | Builds | Deliverables that need widening |
|---|---|---|
| `phase-arch-07` (schema-owned slots and sub-slots with structural eligibility) | `slot-schemas.json` and its JSON Schema; `elements` on each registry entry; the matcher as a pure function; the frame renderer with the four sub-slots and the typed wrapper panels use; the eight panels' headers moved into bar elements; `eligible_slots` removed and version 4; the configuration dialog fed by the matcher; the header-count test written first (`R13`) and the no-allow-list check (`R12`); the `REQ-007` W16 row and the `REQ-037` rows that name `.stage-region__header` or that measure bar controls against the panel box (notes strip trigger and tooltip rows, every "Header controls" row) amended, since those controls now sit outside the panel box | `ts/src/stage/` panel sources (`TerminalRegion.tsx`, `HtmlViewerRegion.tsx`, `OverviewRegion.tsx`, `FileBrowserRegion.tsx`, `explorer/ExplorerRegion.tsx`, `NotesStripRegion.tsx`) and `StagePage.tsx`; `_data/workbench/` (the new file and both layouts); `schemas/workbench-layout.schema.json` and the new slot-schema schema; `test/test_workbench_layout_schema.py`; `test/test_workbench_fit_contracts.py` (builds its live matrix from `eligible_slots` and must use the matcher); `ts/vite.config.ts` (serves only `_data/workbench/layouts/`, so the new file needs a route). `REQ-037`'s `C03` parse of `PANEL_REGISTRY` must stay green when entries gain `elements`. |
| `phase-arch-08` (multi-instance panel identity) | `instance_id` and `panel_type` in layout data and the schema (version 5); instance-keyed hosts, assignment, visibility and `instance_state`; `usePanelInstance()`; bridge keys; terminal session ownership per instance; the dialog and the hard-coded ids in `useWorkbenchLayouts.ts` (the shell home slot, the bash and PowerShell panel ids) converted so no type id stands where an instance id is meant; one extra instance in a shipped layout so `R14` is observable (recommended: a second HTML Viewer assigned to `explorer` in layout 2, hidden by default, so the cleared-browser arrangement is unchanged). No `src/` change; `sys-api` is listed on the phase but is not exercised under decision 7 | `ts/src/stage/StagePage.tsx`, `guardedPanel.tsx`, `panelBridge.ts`, `HtmlViewerRegion.tsx`, `NotesStripRegion.tsx` and the File Browser's bridge callers; `schemas/workbench-layout.schema.json`; `test/test_workbench_layout_schema.py`; `test/test_workbench_fit_contracts.py` (its live runner seeds `panel_assignments` by panel id). Terms file gains **panel instance**. |
| `phase-arch-09` (reconfigurable slot geometry) | The per-kind floor table in the slot-schema data (the table `next_action` asks for first); floors as `minmax` in the grid; `grid_tracks` selections with a way to change and reset them; the two standing checks (floors at least the `REQ-037` minimum; floors fit 1024x768); the zero-scroll checks at four sizes in both layouts. If the owner rejects open item 1, it builds the two checks and no stored geometry | `_data/workbench/slot-schemas.json`; `docs/06-requirements/` and `test/` (`R15` asks for a readable constraint statement per role, which the data alone is not) |
| `phase-arch-10` (sub-app package contract) | A document only. It must state registration as one `PANEL_REGISTRY` entry with an element configuration (decision 4); that a package never renders a top bar; how it obtains its instance identity (`usePanelInstance()`) and stores its own state (`instance_state`); that session ownership is the package's own, per instance. How it receives data is its own decision | none: `docs/06-requirements/` suffices |
| `phase-arch-17` (panel maximize and collapse) | The `maximize` and `collapse` frame actions; transient state keyed by slot id; no reparent of the instance host; the terminal's collapse flag and class moved to the slot or retired; the `R28` test first | `ts/src/stage/TerminalRegion.tsx`, `TerminalMenu.tsx` and `StagePage.tsx`; the `REQ-007` row for the terminal collapse toggle if retired |

## Alternatives considered

### Where the slot structure lives

- **Inline in each layout file.** Rejected: the same role could differ between layouts, so
  "constraints per role" would have no single statement, and four slots across two layouts would
  repeat one top-bar structure eight times.
- **As TypeScript constants.** Rejected: structure would be invisible to `pytest`, to the JSON
  Schema and to a reviewer reading a diff, and `ADR-016`'s posture that the workbench's shape is
  reviewable data would stop holding exactly where it matters most.
- **Only a top-bar schema, keeping the allow-lists.** Rejected: it would fix `000101` and leave two
  eligibility authorities, which `R12` forbids.
- **Status quo with a header-count test only.** Rejected: it detects the defect after a panel
  introduces it. `000141` asks that it be impossible, and the cost of the model is incurred once.

### How eligibility is decided

- **Derive allow-lists from the schema and keep them in the layout files.** Rejected: a generated
  list that a test regenerates is still a second copy that can be edited by hand and then disagree.
- **Free-form capability tags on panels and slots.** Rejected: matching tags is an allow-list under
  another name. It checks that two names agree and checks nothing about capacity or whether the
  slot has a place for the panel's controls. Structure does.
- **Decide by the panel's body kind alone.** Rejected: it would admit a panel whose controls the slot
  has no room for, and it gives the strip no way to refuse a panel with five controls.

### Instance identity

- **Runtime-generated ids in the browser** (`terminal#2` created by a button). Rejected: the browser
  would store a definition, which the kept rule 3 forbids; ids would not be reproducible; and a
  stored selection could name an id no layout declares.
- **A suffix convention parsed from the string** (`html-viewer:2`). Rejected: it makes the type
  recoverable only by string parsing, and the next code that forgets to parse treats the whole
  string as a type. Two fields cannot be confused that way.
- **Server-assigned ids.** Rejected: layout data could not reference them, and the session registry
  needs no instance knowledge (decision 7).
- **Layout-scoped ids.** Rejected: the live shell that survives a layout switch is identified by the
  same id in both layouts (fact 4). Scoping ids per layout would remount it on every switch and
  break `REQ-007` W15.
- **Keep singleton `panel_id` and add a counter field.** Rejected: it leaves one name meaning both a
  type and an instance, which is the confusion that made `000135` call the terminology backwards.

### Session ownership

- **Tag server sessions with the owning instance id.** Rejected for now: the benefit is only for
  external addressing, which `ADR-030` owns, and it adds a client-asserted label to an
  unauthenticated route.
- **Raise or remove the six-session cap for several instances.** Rejected: `ADR-014` set the number
  for the host's capacity, and the refusal path already tells the user. Nothing here changes the
  capacity.

### Geometry

- **Keep `ADR-016` decision 2 as it is** (data-file edits only, no UI), adding only the floors.
  A defensible fallback and the one `phase-arch-09` builds if open item 1 goes the other way. Not
  recommended because `000133` asks to revisit the exclusion, and because with the floors in place
  the original risk (unreviewable, unbounded browser state) no longer applies to what would be
  stored.
- **Unbounded resizing stored as selections.** Rejected: nothing would stop a stored size from
  starving a terminal or scrolling the page.
- **Writing resized geometry back to the layout files.** Rejected: it needs a write route, and
  `ADR-015` allows reads and the single reveal action.
- **Pixel track definitions.** Rejected for the reason `ADR-016` gave; floors are in content units
  and tracks stay fractional.

### Maximize

- **Per-panel maximize.** Rejected: it is the second geometry path `PLAN-028` design decision 5
  and `R25` exist to prevent, and it is rebuilt for each panel type.
- **Reparent the instance into a full-screen overlay.** Rejected: a DOM move of a mounted terminal is
  survivable (the reassignment mechanism proves it) but it is not needed; changing the slot
  element's own geometry avoids any move and so has strictly fewer ways to lose a session.
- **Store maximize in the selections.** Rejected: `R27`, and a browser left maximized would reopen
  wrong.

## Consequences

- The workbench's structure becomes data plus one registration literal. A sub-app that declares an
  element configuration is assignable into exactly the slots whose schema has places for it, which
  is what `phase-arch-10` documents and `phase-arch-13` tests by trying it.
- The eight panels lose their headers and gain bar elements. That is the largest change in
  `phase-arch-07`, it touches panel sources outside that phase's declared deliverables, and the
  widening is listed above rather than done silently.
- One shipped eligibility cell changes (`overview` in `secondary`, layout 2).
- Three clearings of stored selections across `phase-arch-07` and `phase-arch-08`, and none for
  `phase-arch-09` unless the layout file changes.
- `REQ-007` W16 and parts of `REQ-037` are amended by `phase-arch-07` so there is one specification
  of eligibility and of the bar controls in force. `ADR-029` (draft) and other documents that list
  `ADR-016` in `depends_on` keep a pointer to a superseded record; their owners may retarget them
  when this record is ratified. This record does not edit them.
- The geometry decision is the largest departure from what the owner decided on 2026-09-10 and
  carries the most ratification weight.

## Open items for the owner

These are the points the owner is asked to ratify or change.

1. **Geometry (decision 8).** Admit bounded track-size selections in the browser, with floors
   derived from the schema (recommended), or keep `ADR-016` decision 2 as it stands with the
   floors validated at commit time and no stored geometry. Changes what `phase-arch-09` builds.
2. **Instances are declared in layout data, never created in the browser (decision 5).** The
   alternative is a stored instance list, which breaks the kept "selections only" rule.
3. **`overview` becomes eligible for `secondary` in layout 2 (decision 4).** The one change to
   `REQ-007` W16's shipped eligibility. It can be prevented by giving `overview` a distinct body
   kind, at the cost of a vocabulary entry for a panel type that may be retired.
4. **The terminal's collapse toggle moves to the slot (decision 9)** and its panel-local code is
   removed. The alternative is retiring the feature.
5. **`ADR-016` reads `superseded` before this record is accepted.** Required by the validator; if
   the owner rejects this record, both front matters are reverted together.
6. **The three terminal types stay three types (decision 5).**
7. **The server is not told instance ids (decision 7).** Revisit if `ADR-030`'s API needs it.
8. **The `strip` role uses an inline frame (decision 2)** so it stays one thin row. If that proves
   unworkable, the strip takes a stacked frame and its fit contract is restated.
9. **The default target for a cross-panel action with several instances (decision 7):** the visible
   instance last interacted with.

## Revisit trigger

Revisit decision 3 (nesting depth) when a panel needs a control group nested inside another bar
group, or a body that holds two visible instances. Revisit decision 5 if the owner wants panels
created from the page. Revisit decision 7 when `ADR-030`'s API is built and a caller needs to
address a session by instance. Revisit the vocabulary of body kinds when a sub-app's body does not
fit any of the five; adding a kind is a schema edit and a floor, and no code change.
