/**
 * The layout engine's data shapes (REQ-007 W05/W06, ADR-016). A `LayoutDefinition` is loaded at
 * runtime from `_data/workbench/layouts/<id>.json` (never bundled — see `useWorkbenchLayouts`)
 * and describes stable slot ids, fractional/grid geometry (no pixels), the panel types each slot
 * admits, and the slot's default panel. Geometry is data, not code: this file defines the shape
 * only, never a layout's actual numbers.
 */

export interface LayoutSlotDefinition {
  /** Stable within this layout file — persisted selections key off this id (ADR-016). */
  slot_id: string
  /** Shown in the slot's header — as plain text for a single-panel slot, or beside the dropdown
   * triangle for a multi-panel slot (REQ-007 W06). */
  display_name: string
  /** Panel type ids this slot may hold. May include ids with no implemented component yet — see
   * `panelRegistry.ts` — so a later phase can start shipping a real panel into an existing slot
   * with a data-file change only. */
  admits: string[]
  /** The panel type id assigned here absent any stored browser selection, or `null` when the
   * slot ships with nothing assigned (e.g. `explorer` before its panels exist). */
  default_panel: string | null
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

export interface LayoutDefinition {
  schema_version: number
  layout_id: string
  name: string
  slots: LayoutSlotDefinition[]
  grid: LayoutGridDefinition
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isLayoutSlotDefinition(value: unknown): value is LayoutSlotDefinition {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    typeof record.slot_id === 'string' &&
    typeof record.display_name === 'string' &&
    isStringArray(record.admits) &&
    (record.default_panel === null || typeof record.default_panel === 'string')
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
 * pattern for other runtime-loaded data (`TalkingPointsRegion`'s `isTalkingPointsFile`,
 * `CommandPanel`'s `isCommandsFile`): a malformed file is reported as absent, never a crash. The
 * repository-side JSON-schema assertion ADR-016 calls for is a separate, backend-side concern
 * outside this phase's `ts/src` deliverable. */
export function isLayoutDefinition(value: unknown): value is LayoutDefinition {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    typeof record.schema_version === 'number' &&
    typeof record.layout_id === 'string' &&
    typeof record.name === 'string' &&
    Array.isArray(record.slots) &&
    record.slots.every(isLayoutSlotDefinition) &&
    isLayoutGridDefinition(record.grid)
  )
}

/** The browser's stored selections (ADR-016 rule 3): active layout id and per-layout per-slot
 * panel choices, under one key namespaced by the layouts' `schema_version`. Never geometry, never
 * copy — selections only. */
export interface StoredWorkbenchState {
  schema_version: number
  active_layout: string
  slot_selections: Record<string, Record<string, string>>
}
