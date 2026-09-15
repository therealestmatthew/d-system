---
schema_version: 1
id: doc-workbench-architecture-quality-requirements
code: REQ-011
title: Workbench architecture and quality requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench-requirements, doc-workbench-layout-decision, doc-workbench-api-decision]
---

# Workbench architecture and quality requirements

## Observed problem and scope

The workbench shipped in one week. `REQ-007` specified it, `ADR-015` fixed the API posture and
`ADR-016` fixed layout persistence, and the `phase-wb-*` track built it against a 2026-09-15 demo.
The result works and is in daily use. What it does not have is a vocabulary, a stated structural
model, a content-fit contract, or a measurement of its own performance — because none of those were
what a one-week runway bought.

Thirteen ideas raised between 2026-09-11 and 2026-09-13 name the consequences. Four are observable
in the repository as it stands today:

1. **Names describe the first occupant, not the thing.** `_data/workbench/layouts/layout-1.json`
   and `layout-2.json` both declare `"slot_id": "terminal"`. Per-panel eligibility (`REQ-007` W16)
   lets any shell, or the HTML Viewer, occupy that slot, so the name misdescribes it. The owner
   raised this as `000124`, and went further in `000135`: the container/content sense of *slot* and
   *panel* may be backwards as used, and nothing terminology-related should be changed until it is
   settled. Two further ideas (`000141`, `000144`) say in their own text that they presuppose that
   settlement.

2. **The workbench has no entry in the glossary at all.** `brain/concepts/` holds eight concept
   memories and `docs/08-governance/GLOSSARY.md` renders them; none of them define *slot*, *panel*,
   *region*, *layout*, *assignment* or *visible panel*. The machinery for a governed vocabulary
   already exists and the workbench is simply absent from it.

3. **Structure is per-slot rather than general.** The wrapper/header/switcher machinery in
   `Slot.tsx` and its CSS chain was touched by `phase-wb-08`'s fix and again by the duplicate-header
   defect `000101`. `000141` observes that under a schema-owned sub-slot model the double header
   could not have arisen: the top bar would be populated once by the slot's schema rather than
   rendered independently by both the wrapper and the hosted panel.

4. **Fit bugs are found by the owner, not by a check.** The `phase-wb-08` height collapse
   (`000104`), the File Browser clip (W18), the rotator tooltip cutoff, the popup height floor
   (`000117`) and the ~98px chrome offset that defeats naive fill checks are five separate
   instances of the same missing contract.

This requirement covers the architecture and quality programme (`P10`) over the workbench: its
vocabulary, its code-shape audits, its content-fit methodology, the slot/panel structural model, the
sub-app packaging contract, the ports/processes exploration and app, the performance and cache-
invalidation work, the panel maximize capability, and the terminal persistence audit. It does
**not** cover the workbench's
discrete features and defects — that is `P11` ([PLAN-027](../01-plans/PLAN-027-workbench-features-defects.md)),
which consumes `R01`'s vocabulary and is sequenced behind it wherever it renames anything.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The workbench vocabulary exists as `concept` memories under `brain/concepts/` and is rendered into `docs/08-governance/GLOSSARY.md` by the existing generator. It defines at minimum: slot, panel, region, layout, assignment, visible panel, session, panel type, template family, generated page, overview. | Run `uv run python tools/generate_glossary.py` and confirm the committed glossary is unchanged (the drift test already asserts this). Grep the rendered glossary for each of the eleven terms; a missing term is a defect. Confirm no second, hand-maintained glossary document was created. |
| R02 | The vocabulary settles container-versus-content explicitly — which of *slot* and *panel* is the container — and says so in one sentence that `000135`, `000141` and `000144` can be read against. | Read the concept memory for an explicit statement naming the container. Confirm it states the answer rather than describing the ambiguity. |
| R03 | Every slot id in `_data/workbench/layouts/*.json` names the slot's geometry or role, never the panel that first occupied it. | Grep the layout files for `slot_id` values and check each against the vocabulary's naming rule. The value `terminal` in both shipped layouts is the known failing case and must be gone or explicitly ruled an alias. |
| R04 | The migration ruling states, per existing identifier class — layout `slot_id` values, CSS class names, `REQ-007` row wording, localStorage keys, panel registry ids, test fixtures — whether it is renamed or aliased, and why. | Read the ruling for a disposition on each of the six classes. A class with no disposition is a defect. |
| R05 | Executing the migration leaves no stored browser state in a broken intermediate: state written against the old identifiers is either read through an alias or discarded in favor of layout defaults, never surfaced as an error. | Write localStorage under the pre-migration key shape, load the workbench, and confirm it renders layout-1 defaults without an error. Confirm `ADR-016`'s decision 3 discard behavior still holds. |
| R06 | The duplication audit names each duplication with file references, judges whether generalizing pays for itself, and proposes the shared abstraction where it does. The multi-panel wrapper/header/switcher machinery is covered explicitly. | Read the audit for file:line references on every finding. Confirm each finding carries a pay-for-itself judgment rather than only a flag. Confirm `Slot.tsx` and its CSS chain appear. |
| R07 | The structure audit reports lines of code per file across `ts/src/` and `src/`, and for each file it judges to need refactoring it proposes the target structure — the split, the new module boundaries, what moves where. | Read the audit for a per-file measurement table produced by a command it names, and for a proposed structure on every flagged file. A flagged file with a size but no proposal is a defect. |
| R08 | The two audits cross-reference each other: where an abstraction extracted by the duplication audit is the refactor the structure audit proposes, both say so and name the other finding. | Read both documents for reciprocal references. A one-way reference is a defect; the ideas describe this relationship as two-way. |
| R09 | Every panel has a content-fit contract stating what overflows, what scrolls, what truncates and what reflows, and each contract is asserted mechanically rather than by inspection. | Read the contract document for one entry per panel type shipped. Run the assertion suite and confirm it fails when a panel is given content that violates its own contract. |
| R10 | A newly added panel inherits the content-fit contract by construction — adding a panel without declaring its fit behavior fails a check rather than shipping unchecked. | Add a throwaway panel type with no fit declaration and confirm the check fails and names it. |
| R11 | The slot/sub-slot configuration-schema model is recorded in an ADR that supersedes `ADR-016`, with `ADR-016` marked `superseded` in the same change. The ADR states what it keeps from `ADR-016` — repository-owned layout data, browser-stored selections — and what it changes. | Read both documents' front matter for `supersedes` and `status: superseded`. Confirm governance exits 0, which rejects a `supersedes` target that is not marked superseded. |
| R12 | Panel eligibility is decided by matching a panel's element configuration against the element types a slot's sub-slots admit, replacing `REQ-007` W16's per-panel eligibility lists. | Read the implementation for the matching rule. Confirm no per-panel allow-list remains as the eligibility authority. Confirm a panel whose configuration does not match is not offered for that slot. |
| R13 | A slot's top bar is rendered once, by the slot's schema, and a hosted panel cannot render a second one. | Assign every panel type into every slot in both layouts and count rendered headers per slot; any count other than one is a defect. This is `000101`'s defect asserted as a standing check. |
| R14 | The workbench supports multiple instances of the same panel type at once, across slots and within a slot where the schema admits it. Panel identity is no longer singleton by `panel_id`. | Assign two instances of the same panel type into two slots and confirm both mount with independent state. Confirm layout data, the storage shape, the panel registry and session ownership each carry an instance identity rather than a bare panel id. |
| R15 | Slot geometry is reconfigurable, and each slot role states its content constraints — a shell's rows/cols reflow, an iframe's scaling, an explorer tree's visible depth — stated per role rather than per current occupant. | Read the geometry specification for a constraint statement on every slot role. Resize each slot through its stated range and confirm the hosted content reflows within its declared constraint rather than clipping. |
| R16 | A sub-app package contract exists, stating a sub-app's boundary, its API surface toward the workbench, how it registers as a panel type, and how it receives its data. | Read the contract for all four. Confirm a future sub-app could be integrated against the document alone, without reading an existing sub-app's source. |
| R17 | The ports-and-processes exploration document explains lifecycle, when and how a process is killed, and how ports and processes should be managed, grounded in this repository's own incidents. | Read the document for the port-8000 conflict, the orphaned dev servers left by cut-off agents, and the PTY child reaping that `000099`/`000129` turned on. A treatment that cites none of them has not used the material available. |
| R18 | A port and process application reports what is listening on which port and which processes are running with their state, and offers management actions — killing a process, freeing a port. | Run it against a deliberately occupied port and confirm it names the listener. Use it to free that port and confirm the port is then bindable. |
| R19 | The port and process application is integrated as a workbench sub-app through `R16`'s contract, not hand-wired. | Read its integration for use of the documented registration path only. Confirm it is assignable into a slot whose sub-slots admit its element configuration, per `R12`. |
| R20 | Workbench performance is measured with numbers before any cache is designed: page load, panel mount and switch times, the enumeration, filesystem and explorer API round-trips, HTML Viewer file serving, and overview generation. | Read the measurement report for a figure and a method on each of the six. A caching proposal that precedes its own measurement is a defect. |
| R21 | Every cache that ships carries an invalidation story keyed on file mtime or explicitly busted by the writer, never a bare TTL. | Read each cache's invalidation rule. Grep for a TTL used as the only invalidation. |
| R22 | Regenerating the overview page makes the new page visible immediately to `GET /api/v1/workbench/search` and to `GET /api/v1/demo/stage/overview-location`. | Run `tools/generate_overview.py`, then call both routes and confirm each reflects the regenerated file without a restart or a wait. This is `000121`'s dated failure asserted as a check. |
| R23 | The terminal persistence audit covers bash, CMD and PowerShell equally, and for each of layout switch, visible-panel switch, re-assignment, collapse/drop/restore and page reload it states whether the session survives, whether that is intended, and whether it is communicated to the user. | Read the audit for a three-shell by five-event matrix with all three columns filled. A cell with a survival result but no intent judgment is a defect. |
| R24 | The audit reports connect latency, echo latency, resize behavior, scrollback handling and behavior at the six-session cap, and states plainly which measurements are owner-machine checks that agent evidence cannot supply. | Read the audit for the five measurements and for an explicit list of owner-machine checks. CMD and PowerShell coverage that claims Linux-gathered evidence is a defect. |
| R25 | Any panel can be maximized to fill the viewport and collapsed back to the slot it was assigned to. The capability belongs to the slot model and is available to every panel type; no panel implements its own. | Maximize and collapse each panel type in turn, in both layouts, and confirm each returns to its assigned slot. Grep the panel sources for a geometry path of their own; a maximize implemented inside `HtmlViewerRegion` or any single panel is a defect. |
| R26 | Maximizing breaks neither the zero-scroll obligation nor the fill assertions: the page does not scroll, and the maximized panel fills the viewport at 1280x720, 1366x768, 1920x1080 and 1024x768, in both layouts, maximized and collapsed. | Run the `REQ-006` R02 and `REQ-007` W15 checks at all four sizes in both layouts, in both states. Any scroll, or any unfilled region, is a defect. |
| R27 | Maximize is transient view state and is never written to the layout selections store. A browser closed while a panel is maximized reopens with that panel in its assigned slot. | Maximize a panel, read the `ADR-016` namespaced localStorage key, and confirm no maximize state appears in it. Reload and confirm the panel renders in its assigned slot, unmaximized. |
| R28 | A maximized shell panel keeps its PTY session. Maximizing and collapsing do not remount it or kill the session. | Start a shell, set a shell variable, maximize, collapse, and confirm the variable survives and the session id is unchanged. A remount that kills the PTY is a regression against `REQ-007` W16's survival obligation. |

## Boundaries and unresolved compatibility

**Architecture and quality, not features.** Every discrete user-facing feature and defect in the
shipped workbench belongs to `P11`. The line is the kind of work, not the surface: `R13` is here
because the double header is being prevented structurally, while fixing one rendered header is a
`P11` defect.

**`R01` is a gate, `R03`–`R05` are not.** Six ideas — `000115`, `000116`, `000133`, `000135`,
`000141`, `000144` — cite the vocabulary as a prerequisite by their own text. What they need is the
settled vocabulary, not the executed rename. Landing the glossary before the migration is what lets
the other seven groups start; coupling them would make one rename phase the bottleneck for the
whole programme.

**`R23`–`R24` cannot be fully verified on Linux.** CMD and PowerShell coverage needs the owner's
Windows machine. The audit is required to name those checks rather than assert them, which is why
`R24` makes the naming itself the observable.

**`R12` changes a shipped contract.** `REQ-007` W16 specifies per-panel eligibility lists, and W16
is implemented. `R12` replaces the eligibility authority, so the phase delivering it amends W16's
row rather than leaving two contradictory specifications in force.

**`R25`–`R28` were asked for on one panel and are specified for all of them.** The owner raised
maximize on the HTML Viewer (`000233`), for a projector at the back of a room. The rows here are
slot-level deliberately: the mechanism is geometry, the geometry belongs to the slot, and a maximize
built inside `HtmlViewerRegion` would be a second geometry path outside the model `R12` and `R15`
establish. `R25`'s grep for a panel-owned geometry path is what makes that observable rather than
merely intended.

**`R18`'s management actions are destructive.** Killing a process is not a read-only operation, and
`ADR-015` fixed a read-only posture for the workbench API. The phase delivering `R18` resolves that
tension in its own ADR rather than widening `ADR-015` in passing.
