/**
 * The layout engine's data shapes (REQ-007 W05/W06/W16, ADR-016). A layout is loaded at runtime
 * from `_data/workbench/layouts/<id>.json` (never bundled — see `useWorkbenchLayouts`) and
 * describes stable slot ids, fractional/grid geometry (no pixels), and — since the W16 delta —
 * per-*panel* eligibility (the set of slots each panel type may occupy) plus a default total
 * assignment of every panel to exactly one eligible slot. Geometry is data, not code: this file
 * defines the shape only, never a layout's actual numbers.
 *
 * Two shapes live here:
 * - `RawLayoutFile`/`RawLayoutSlot`/`RawLayoutPanel` mirror the JSON files on disk exactly
 *   (`isRawLayoutFile` validates a fetched file against this shape) and are consumed only by
 *   `useWorkbenchLayouts`, which resolves per-panel eligibility plus any valid stored assignment
 *   into a concrete "what does each slot currently hold" view.
 * - `LayoutDefinition`/`LayoutSlotDefinition` are that resolved, app-facing view: each slot's
 *   `admits` is now the panel type ids *currently assigned* to it (computed from the file's
 *   default assignment plus any valid stored per-panel override — ADR-016 rule 3), and
 *   `default_panel` is the slot's default-visible choice among those. This is deliberately the
 *   same shape `Slot.tsx`/`LayoutConfigDialog.tsx`/`StagePage.tsx` already consumed before the
 *   W16 delta moved eligibility from the slot to the panel: those three files render "the panels
 *   this slot currently holds" and "which one is visible" either way, so keeping their input
 *   shape stable confines this delta to the loading/validation layer (this file,
 *   `useWorkbenchLayouts.ts`, `storage.ts`) — the assignment-only configuration dialog (REQ-007
 *   W16's "one selector per panel over its eligible slots") is a separate, not-yet-built rework
 *   of `LayoutConfigDialog.tsx` itself, out of this data-model phase's scope.
 */

// --- the raw, on-disk layout file shape (schema_version 2, W16) ------------------------------

export interface RawLayoutSlot {
  /** Stable within this layout file — persisted assignments and visible-panel choices key off
   * this id (ADR-016). */
  slot_id: string
  /** Shown in the slot's header — as plain text for a single-panel slot, or beside the dropdown
   * triangle for a multi-panel slot (REQ-007 W06). */
  display_name: string
}

/** One panel type's eligibility within this layout (REQ-007 W16: "each panel declares the set of
 * slots it may occupy"). A panel type not listed here is not usable in this layout at all — the
 * pre-W16 per-slot `admits` list is superseded by this per-panel declaration. */
export interface RawLayoutPanel {
  panel_id: string
  /** Slot ids (must all name a slot in this layout's `slots` list) this panel may be assigned
   * to. Never empty — a panel with no eligible slot cannot ship (asserted by the layout-schema
   * test, idea `000098`). */
  eligible_slots: string[]
}

export interface LayoutGridDefinition {
  /** CSS grid-template-columns track sizes, fractional/grid units only (e.g. `"1.4fr"`) — never
   * pixels (ADR-016 rejected alternative: "pixel geometries"). */
  columns: string[]
  /** CSS grid-template-rows track sizes, same unit rule as `columns`. */
  rows: string[]
  /** One string per grid row, each a space-separated list of slot ids (or `.` for an empty
   * cell) — assembled into `grid-template-areas` at render time. Every non-`.` token must name a
   * slot in this layout's `slots` list. */
  areas: string[]
}

/** The layout file's on-disk shape: a total default assignment (`default_assignment`, every
 * declared panel mapped to exactly one of its own eligible slots) plus the default visible panel
 * for any slot a default assignment leaves holding more than one panel (`default_visible_panel`,
 * REQ-007 W16). */
export interface RawLayoutFile {
  schema_version: number
  layout_id: string
  name: string
  slots: RawLayoutSlot[]
  panels: RawLayoutPanel[]
  /** panel_id -> slot_id, one entry per panel in `panels`, each value one of that panel's own
   * `eligible_slots`. */
  default_assignment: Record<string, string>
  /** slot_id -> panel_id, for slots whose default assignment gives them more than one panel;
   * the named panel must itself be assigned to that slot in `default_assignment`. */
  default_visible_panel: Record<string, string>
  grid: LayoutGridDefinition
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isStringRecord(value: unknown): value is Record<string, string> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false
  return Object.values(value as Record<string, unknown>).every((item) => typeof item === 'string')
}

function isRawLayoutSlot(value: unknown): value is RawLayoutSlot {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return typeof record.slot_id === 'string' && typeof record.display_name === 'string'
}

function isRawLayoutPanel(value: unknown): value is RawLayoutPanel {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    typeof record.panel_id === 'string' &&
    isStringArray(record.eligible_slots) &&
    record.eligible_slots.length > 0
  )
}

function isLayoutGridDefinition(value: unknown): value is LayoutGridDefinition {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    isStringArray(record.columns) && isStringArray(record.rows) && isStringArray(record.areas)
  )
}

/** Defensive runtime validation of a fetched layout file — mirrors this codebase's existing
 * pattern for other runtime-loaded data (`NotesStripRegion`'s `isNotesFile`, `CommandPanel`'s
 * `isCommandsFile`): a malformed file is reported as absent, never a crash. Structural shape
 * only; the relational invariants (every panel's eligible slots real, the default assignment
 * total and eligible, every default-visible-panel entry actually assigned there, every grid-area
 * token a real slot) are asserted by the repository-side layout-schema test (idea `000098`) and,
 * defensively, by `useWorkbenchLayouts`'s own resolution, which drops anything that fails them
 * rather than trusting the file blindly. */
export function isRawLayoutFile(value: unknown): value is RawLayoutFile {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    typeof record.schema_version === 'number' &&
    typeof record.layout_id === 'string' &&
    typeof record.name === 'string' &&
    Array.isArray(record.slots) &&
    record.slots.every(isRawLayoutSlot) &&
    Array.isArray(record.panels) &&
    record.panels.every(isRawLayoutPanel) &&
    isStringRecord(record.default_assignment) &&
    isStringRecord(record.default_visible_panel) &&
    isLayoutGridDefinition(record.grid)
  )
}

// The layout files' `schema_version` (ADR-016 rule 1: each layout file "carries a
// `schema_version` integer"; both shipped files declare `2` since the W16 delta moved
// eligibility from the slot to the panel) is not duplicated as a constant here. It is resolved
// once, at runtime, from the fetched layout files by `useWorkbenchLayouts` (its `schemaVersion`
// return value) and shared with every other consumer of the single namespaced storage key
// ADR-016 rule 3 describes — the notes strip included — via `schemaVersionContext.ts`'s
// `ActiveSchemaVersionProvider`/`useActiveSchemaVersion`. A hardcoded copy of the version number
// is exactly what let the two consumers drift apart independently; see `schemaVersionContext.ts`
// for the shared source of truth.

// --- the resolved, app-facing layout shape (unchanged from pre-W16, by design — see file doc) -

export interface LayoutSlotDefinition {
  /** Stable within this layout file — persisted selections key off this id (ADR-016). */
  slot_id: string
  /** Shown in the slot's header — as plain text for a single-panel slot, or beside the dropdown
   * triangle for a multi-panel slot (REQ-007 W06). */
  display_name: string
  /** Panel type ids *currently assigned* to this slot — the file's default assignment for this
   * slot, overridden by any valid stored per-panel reassignment (REQ-007 W16). Computed by
   * `useWorkbenchLayouts`, not a raw file field: eligibility now lives on the panel
   * (`RawLayoutPanel.eligible_slots`), not the slot. */
  admits: string[]
  /** The panel type id resolved as this slot's default-visible choice among `admits` — the
   * file's `default_visible_panel` entry when it names a panel actually assigned here, else the
   * first currently-assigned panel, else `null` when nothing is assigned (e.g. `explorer` before
   * its panels existed). */
  default_panel: string | null
}

export interface LayoutDefinition {
  schema_version: number
  layout_id: string
  name: string
  slots: LayoutSlotDefinition[]
  grid: LayoutGridDefinition
}

/** One HTML Viewer tab's persisted context (REQ-007 W08 / ADR-016: "per-tab HTML Viewer state
 * (directory, search, page)"). `id` is stable within the browser's stored state only — it has no
 * relationship to a layout slot id or a terminal session id. `directory`/`selected_file` are
 * `null` while a freshly created tab is still being seeded from the generated overview's own
 * location (mirrors `HtmlViewerRegion`'s pre-tabs mount-time fetch, now per tab). */
export interface StoredHtmlViewerTab {
  id: number
  directory: string | null
  search_text: string
  selected_file: string | null
}

/** The browser's stored selections (ADR-016 rule 3, reshaped by REQ-007 W16): active layout id,
 * per-layout per-*panel* slot assignment, per-layout per-slot visible-panel choice, and the
 * notes strip's chosen file, under one key namespaced by the layouts' `schema_version`. Never
 * geometry, never copy — selections only. Every field beyond `schema_version` is optional:
 * different owners (the layout engine, the notes strip) write only the field they own, via
 * `storage.ts`'s merge-on-write helper, so one owner's write never clobbers another's already-
 * stored field.
 *
 * `panel_assignments` (layout_id -> panel_id -> slot_id) is new in schema_version 2 — it
 * supersedes the pre-W16 `slot_selections` (layout_id -> slot_id -> panel_id), which conflated
 * "which slot is this panel assigned to" with "which panel is currently visible in this slot".
 * `slot_visible_panel` (layout_id -> slot_id -> panel_id) is the latter, kept distinct: a slot
 * holding several assigned panels still needs a visible choice independent of assignment. Stored
 * state under the old `schema_version` is never read here at all — the version lives in the
 * storage key itself (`storage.ts`) — so no migration code exists for the renamed fields; a
 * cleared or old-schema store falls straight through to the layout files' own defaults (ADR-016
 * rule 4).
 */
export interface StoredWorkbenchState {
  schema_version: number
  active_layout?: string
  /** layout_id -> panel_id -> slot_id. Only entries where the slot is one of that panel's own
   * eligible slots in the loaded layout survive validation (`useWorkbenchLayouts`). */
  panel_assignments?: Record<string, Record<string, string>>
  /** layout_id -> slot_id -> panel_id. Only entries naming a panel currently assigned to that
   * slot survive validation (`useWorkbenchLayouts`). */
  slot_visible_panel?: Record<string, Record<string, string>>
  /** The notes strip's chosen file, by filename under `ts/public/` (e.g. `talking-points.json`).
   * `null`/absent means no choice has ever been persisted — the strip falls back to its own
   * default file (ADR-016 rule 4: repository defaults are the fallback state). */
  active_notes_file?: string | null
  /** The HTML Viewer's open tabs and which one was active (REQ-007 W08). Absent, or invalid,
   * falls back to a single fresh tab seeded from the generated overview page's own location
   * (ADR-016 rule 4). */
  html_viewer_tabs?: {
    tabs: StoredHtmlViewerTab[]
    active_tab_id: number
  }
}
