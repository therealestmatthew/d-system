---
id: mem-concept-terms-workbench-ui
title: Workbench UI
type: concept
tags: []
systems: [sys-wb-layout]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-14
updated: 2026-09-14
confidence: high
related: [mem-concept-terms-systems-vocabulary, mem-concept-terms-skills-and-agents-demo]
scope: global
---

The workbench's nouns, settled by `phase-arch-01` against `REQ-011` R01–R04. Each term is defined
against what the repository actually contains — `_data/workbench/layouts/*.json`,
`ts/src/workbench/`, `ts/src/stage/` and `REQ-007` — rather than generically, so a claim about the
workbench can be checked against a file.

**The container ruling, which the rest of this file is phrased against: a slot is the container and
a panel is its content — a slot is a named region of a layout's grid, and a panel is a unit of
content assigned into exactly one slot at a time.**

That ruling settles the question `000135` raised and deliberately left open, and which `000141` and
`000144` both say in their own text that they presuppose. `000135` asked whether the sense is
backwards — whether panels are the containers things get placed into. The answer is no at the
slot/panel boundary, and the reason the question felt open is that the containment it noticed is
real but one tier down: a panel does contain things, and what it contains are **elements**, not
slots. Naming that third tier is the fix, not inverting the first.

The shipped engine already implements the ruling and no code contradicts it: `default_assignment`
maps `panel_id` to `slot_id`, `eligible_slots` lists the containers a given content may occupy, and
`StagePage.tsx` sets `grid-area` from `slot_id`, so slots are what the grid is made of.

### Slot

The container. One named region of a layout's grid, declared in a layout file's `slots` list with a
`slot_id` and a `display_name`, and placed by `grid.areas` naming that same id. A slot holds the
panels assigned to it and shows one of them at a time. Not a panel, and not a fixed occupant — any
panel that lists the slot in its `eligible_slots` may be assigned there, which is precisely why a
slot id naming a panel type is a defect (see *Slot naming rule*).

### Panel

The content. One unit of workbench content assigned into exactly one slot at a time — a shell, the
HTML Viewer, the notes strip, a file or idea or backlog explorer. Declared in a layout file's
`panels` list by `panel_id`, rendered by the component the panel registry maps that id to. Not a
container of slots; a panel contains **elements**, which is the tier below it.

### Element

What a panel contains: the parts inside one panel's own body — the HTML Viewer's file tabs, an
explorer's table rows, a terminal's session tabs, a header's buttons and dropdowns. Not a layout
concept and not addressable by a layout file. Named here because it is the containment `000135`
observed, and because `000141`'s sub-slot model needs a word for the thing a sub-slot admits. Not
one of `R01`'s eleven terms; defined because leaving it unnamed is what made the container question
look unanswerable.

### Region (workbench)

A synonym for **panel**, surviving in code identifiers only: the panel components are named
`TerminalRegion`, `HtmlViewerRegion`, `FileBrowserRegion` and so on, and each renders a
`.stage-region` box. It predates the slot/panel vocabulary and means panel wherever it appears.
Prefer *panel* in prose, requirements and new identifiers. Distinct from the CSS grid sense of a
region, which is a **slot**.

### Layout

One arrangement of slots, loaded at runtime from `_data/workbench/layouts/<layout_id>.json` — the
slot list, the grid geometry, the panel eligibility, the default assignment and the default visible
panel. Layouts are repository data, never bundled and never edited from the UI (`ADR-016`). Two ship:
`layout-1` and `layout-2`. Not a theme and not a stylesheet; a layout decides what is where, not what
it looks like.

### Assignment

Which slot a panel currently occupies. The layout file carries a total `default_assignment` mapping
every declared panel to exactly one of its own eligible slots; the configuration dialog lets a
browser override it per panel, and the override is stored per browser, never written back to the
layout file. One panel has exactly one assignment at a time. Not the same as being visible — a slot
may hold several assigned panels and show one.

### Visible panel

Which of a slot's assigned panels is the one currently rendered. Stored per slot, defaulting to the
layout file's `default_visible_panel` for any slot whose assignment leaves it holding more than one.
A slot header's dropdown switches the visible panel and never re-assigns (`REQ-007` W16). The
distinction from *assignment* is the one most often lost: assigning moves a panel between
containers, switching the visible panel chooses among the panels already in one.

### Panel type

The kind of panel, as against an instance of it. The `panel_id` in a layout file and the key in
`PANEL_REGISTRY` (`ts/src/workbench/panelRegistry.tsx`) both name a panel type: `terminal`,
`terminal-cmd`, `terminal-powershell`, `html-viewer`, `notes-strip`, `overview`, `file-browser`,
`idea-explorer`, `backlog-explorer`. Identity is currently singleton — one live panel per type per
workbench — which is the constraint `000135` asks to remove and `phase-arch-08` will remove; until
then, *panel type* and *panel* are the same thing in practice, and the two words are worth keeping
apart because they stop being the same thing then.

### Session (workbench)

One live PTY behind a websocket, owned by a shell panel and bounded to six concurrently across the
whole backend (`REQ-007` W17). A session outlives the panel's remount where feasible: switching
layouts or re-assigning a shell is required not to silently kill it. Distinct from the two other
senses of the word in this repository — a session record under `docs/03-sessions/`, and one
continuous conversation with an agent. See `### Session` under *Skills and agents*, which carries
the full overload.

### Template family

A set of HTML partials plus one stylesheet under a shared name prefix, filled by one generator with
`{{TOKEN}}` substitution. Two exist: the overview family (`templates/html/overview-*.html` with
`templates/styles/overview.css`, filled by `tools/generate_overview.py`) and the atlas family
(`templates/html/atlas-*.html` with `templates/styles/atlas.css`). A family is the unit a new
generated page is built from; adding a page to an existing family is not a new family.

### Generated page

An HTML file written into `_public/` by a generator from a template family — never hand-edited, and
regenerated from source data rather than patched. `_public/overview/index.html` is the one the
workbench serves in a panel. Distinct from a template, which is its input, and from a governed
document under `docs/`, which is authored rather than generated.

### Overview

Overloaded, and both senses are current. As a **generated page**, `_public/overview/index.html` —
the repository's own metrics and inventory, produced by `tools/generate_overview.py`. As a **panel
type**, the `overview` id in the panel registry, rendered by `OverviewRegion`, still admitted by
layout 2's main slot. The HTML Viewer generalized the panel sense: in layout 1 the overview page is
one entry in the viewer's file dropdown rather than a separately admitted panel type. Read *overview*
as the page unless a layout file or the registry is the subject.

## Slot naming rule

**A slot id names the slot's role in the layout. It never names a panel type, and no slot id may
equal any panel id.**

The second clause is not redundant. In both shipped layout files the string `terminal` is
simultaneously a `slot_id` and a `panel_id`, so `default_assignment` reads `"terminal": "terminal"`
(panel to slot) while `default_visible_panel` reads `"terminal": "terminal"` (slot to panel) — two
different namespaces, the same string, pointing opposite ways. `notes-strip` collides the same way.
A reader cannot tell the two apart without knowing which map they are in. The rule forbids the
collision rather than relying on the map to disambiguate it.

Role, not geometry, because the same slot is a different shape in each layout: `terminal` is the left
column in `layout-1` and the full-width bottom row in `layout-2`. A geometry-derived id would differ
per layout, and assignments are stored per `layout_id` per `panel_id`, so a panel could not keep a
recognisable home across a layout switch. Role names also survive `phase-arch-09`'s reconfigurable
geometry, which would invalidate a geometry-derived id the first time a slot moved.

## Migration ruling

`REQ-011` R04. Six identifier classes, each renamed or aliased, with the reason. **This phase
executes none of it** — `phase-arch-02` does, and gates nothing.

### 1. Layout `slot_id` values — RENAME

`terminal` becomes `secondary`, `main` becomes `primary`, `notes-strip` becomes `strip`, `explorer`
stays `explorer`. The `grid.areas` tokens rename with them, in the same file, because
`StagePage.tsx:250` sets `grid-area` from `slot_id` and the areas strings must keep naming real
slots.

Renamed rather than aliased because these are the identifiers `000124` was raised about and an alias
would leave the misdescription in the file that `R03` reads. `primary`/`secondary` is a role
distinction the shipped data already supports: shells and the HTML Viewer are eligible for both slots
in both layouts, so the only honest difference between them is which is the focal surface. The rename
also discharges the `slot_id`/`panel_id` collision above, since no panel type is called `primary`,
`secondary` or `strip`.

Cost, stated plainly: the layout files are repository data, so this is a data edit plus the stored
browser state handled in class 4. No engine code reads a slot id literal.

### 2. CSS class names — ALIAS, meaning leave them alone

`.stage-region`, `.stage-workbench-slot`, `.stage-region--terminal` and the rest keep their current
names. They are internal to the frontend, invisible in every governed document, and carry no
cross-file contract that a wrong name can corrupt. Renaming them would touch every panel component
and the 1,289-line `StagePage.css` for a vocabulary gain no reader outside `ts/src/` ever sees, and
it would collide directly with `phase-arch-03` and `phase-arch-04`, whose audits are about to propose
a different structure for those same files.

`.stage-region--terminal` is the one that misdescribes under the new vocabulary, since it is a
modifier named for a panel type on a class named with the panel synonym. It is ruled an alias here
and left to whichever of `phase-arch-03`/`-04` restructures that CSS, rather than renamed twice.

### 3. `REQ-007` row wording — ALIAS, with one amendment already owed

The W-rows say "the terminal slot", "the main slot" and "the explorer slot" as prose. Those readings
stay correct under the new vocabulary — they name a slot by the role it plays, and *the terminal
slot* remains an unambiguous reference to the slot the shells default into.

Not renamed, because `REQ-007` is the specification of what shipped, and rewriting a shipped
requirement's prose to match later vocabulary makes the record of what was built less accurate rather
than more. The one row that must change is W16, and not for naming: `R12` replaces its per-panel
eligibility lists with structural matching, and `PLAN-028` already assigns that amendment to
`phase-arch-07`. Class 1's rename lands new slot ids in the layout files while W16's prose still says
*terminal slot*; that is acceptable precisely because the prose names the role, not the id.

### 4. localStorage keys — RENAME, executed by a version bump, with no alias and no migration code

The key itself is `d-system:workbench-state:v{schema_version}` and is not renamed. The identifiers at
risk are the fields inside it — `panel_assignments` and `slot_visible_panel` — and the `slot_id`
values used as keys within them, which class 1 changes.

`ADR-016` rule 3 already makes this free: the schema version is in the key, so bumping
`schema_version` in the layout files means the old key is never read again and every reader falls
through to the layout files' defaults. No alias, no migration code, and no broken intermediate — which
is exactly what `R05` requires `phase-arch-02` to demonstrate. `phase-arch-02` bumps
`schema_version` from 2 to 3 in the same change as the slot ids, or the rename strands live browsers
on stored assignments naming slots that no longer exist.

### 5. Panel registry ids — ALIAS, meaning leave them alone

`terminal`, `terminal-cmd`, `terminal-powershell`, `html-viewer`, `notes-strip`, `overview`,
`file-browser`, `idea-explorer`, `backlog-explorer` all keep their ids. Every one of them already
names a panel type rather than a container or a location, which is what the vocabulary asks of a
panel id. `terminal` as a *panel* id is correct and always was; it was only ever wrong as a *slot*
id, and class 1 removes that use.

`overview` is the one to watch, because it is a panel type whose page the HTML Viewer now also serves.
It is left alone here: retiring it is a question about whether `OverviewRegion` still earns its place,
which belongs to `phase-arch-03`'s duplication audit, not to a naming ruling.

### 6. Test fixtures — RENAME, in the same commit as class 1

`test/test_workbench_layout_schema.py` hard-codes the slot id literals — `assignment[shell_id] ==
"terminal"`, `layout["default_visible_panel"]["terminal"] == "terminal"`, the W16 eligibility
assertion comparing against `{"terminal", "main"}`, and the mutation fixtures at
`test_default_visible_panel_naming_an_unassigned_panel_fails_invariant` and
`test_grid_area_naming_an_unknown_slot_fails_invariant`.

Renamed, not aliased, and necessarily in the same commit as class 1: these tests assert the shipped
layout files' actual contents, so a rename that leaves them behind turns a green suite red on the
same commit. A compatibility shim mapping old literals to new would be a second source of truth for
slot ids inside the only test that checks them, which is the one place it cannot be allowed.

There are no Playwright spec files in the repository to update; browser assertions are driven by the
`demo-validator-web` agent against a live page, and they address slots through the rendered header
text and `display_name`, neither of which class 1 changes.
