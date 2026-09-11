import { useEffect, useRef, useState } from 'react'
import {
  isRawLayoutFile,
  type LayoutDefinition,
  type LayoutSlotDefinition,
  type RawLayoutFile,
} from './types'
import { loadStoredState, patchStoredState } from './storage'

// The two shipped layout files (REQ-007 W05, ADR-016 rule 1) — served at runtime by the Vite dev
// plugin `serveWorkbenchLayouts` (`ts/vite.config.ts`) from `_data/workbench/layouts/`, never
// bundled, so editing a layout file's geometry, panel eligibility or default assignment needs no
// frontend rebuild. Only the filenames are named here; every other detail (slot ids, geometry,
// per-panel eligibility, default assignment) is the JSON files' content, not this code's.
const LAYOUT_FILE_IDS = ['layout-1', 'layout-2'] as const

export type WorkbenchLoadState = 'loading' | 'loaded' | 'error'

async function fetchLayout(id: string): Promise<unknown> {
  const response = await fetch(`/workbench-layouts/${id}.json`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`status ${response.status}`)
  return response.json()
}

/** Resolves one raw layout file's default total assignment (panel_id -> slot_id) overridden by
 * any valid stored per-panel reassignment (REQ-007 W16). Invalid stored entries — an unknown
 * panel, an unknown slot, or a slot the panel is not eligible for — are dropped silently in
 * favor of the file's own default for that panel (ADR-016 rule 4), never an error. Returns both
 * the resolved assignment and the subset of the stored overrides that were actually valid, so the
 * persistence effect below only ever writes back entries `useWorkbenchLayouts` itself already
 * validated once. */
function resolveAssignment(
  layout: RawLayoutFile,
  storedForLayout: Record<string, string> | undefined,
): { assignment: Record<string, string>; validOverrides: Record<string, string> } {
  const eligibleSlotsByPanel = new Map(layout.panels.map((panel) => [panel.panel_id, panel.eligible_slots]))
  const assignment: Record<string, string> = { ...layout.default_assignment }
  const validOverrides: Record<string, string> = {}
  if (storedForLayout) {
    for (const [panelId, slotId] of Object.entries(storedForLayout)) {
      const eligibleSlots = eligibleSlotsByPanel.get(panelId)
      if (eligibleSlots && eligibleSlots.includes(slotId)) {
        assignment[panelId] = slotId
        validOverrides[panelId] = slotId
      }
    }
  }
  return { assignment, validOverrides }
}

/** Builds this layout's app-facing slot list (REQ-007 W16): each slot's `admits` is the panel
 * type ids the resolved `assignment` places there (order follows `layout.panels`' own
 * declaration order, for a stable dropdown/select order), and `default_panel` is the file's
 * `default_visible_panel` entry for that slot when it still names a panel assigned there, else
 * the first currently-assigned panel, else `null`. */
function buildSlots(
  layout: RawLayoutFile,
  assignment: Record<string, string>,
): LayoutSlotDefinition[] {
  const assignedPanelsBySlot = new Map<string, string[]>()
  for (const panel of layout.panels) {
    const slotId = assignment[panel.panel_id]
    if (!slotId) continue
    const existing = assignedPanelsBySlot.get(slotId)
    if (existing) existing.push(panel.panel_id)
    else assignedPanelsBySlot.set(slotId, [panel.panel_id])
  }
  return layout.slots.map((rawSlot) => {
    const admits = assignedPanelsBySlot.get(rawSlot.slot_id) ?? []
    const declaredDefault = layout.default_visible_panel[rawSlot.slot_id]
    const default_panel =
      declaredDefault && admits.includes(declaredDefault) ? declaredDefault : (admits[0] ?? null)
    return {
      slot_id: rawSlot.slot_id,
      display_name: rawSlot.display_name,
      admits,
      default_panel,
    }
  })
}

/**
 * Loads the shipped layout files, hydrates the active layout, per-panel slot assignment and
 * per-slot visible-panel choice from localStorage (ADR-016 rule 3, reshaped by REQ-007 W16), and
 * persists changes back. Stored data referencing an unknown layout, panel or slot — or assigning
 * a panel to a slot it is not eligible for, or naming a visible panel not currently assigned to
 * that slot — or written under a different schema-version key entirely — is dropped silently in
 * favor of each layout's own defaults (ADR-016 rule 4), never surfaced as an error and never
 * migrated.
 *
 * Also resolves the one ADR-016 `schema_version` the storage key is namespaced by (returned as
 * `schemaVersion`) — the single source of truth `StagePage` provides to every panel via
 * `ActiveSchemaVersionProvider`, so no other consumer derives or hardcodes its own copy.
 *
 * The returned `layouts`/`getSlotPanel`/`setSlotPanel` shape is deliberately unchanged from
 * before the W16 delta (see `types.ts`'s file doc) — `getSlotPanel` resolves a slot's *visible*
 * panel and `setSlotPanel` changes it, both scoped to the panels the slot currently holds
 * (`slot.admits`, now computed from panel eligibility + assignment rather than a raw per-slot
 * admits list). `setPanelSlot`, exposed alongside them, is the new REQ-007 W16 primitive — moving
 * a panel to a different one of its eligible slots — for the assignment-only configuration-dialog
 * rework to call; nothing in this data-model phase's scope calls it yet.
 */
export function useWorkbenchLayouts() {
  const [loadState, setLoadState] = useState<WorkbenchLoadState>('loading')
  const [rawLayouts, setRawLayouts] = useState<RawLayoutFile[]>([])
  const [activeLayoutId, setActiveLayoutIdState] = useState<string | null>(null)
  // layout_id -> panel_id -> slot_id. Only entries that survived validation against the loaded
  // layouts' panel eligibility are ever stored here (REQ-007 W16) — see the fetch effect below.
  const [panelAssignments, setPanelAssignments] = useState<Record<string, Record<string, string>>>(
    {},
  )
  // layout_id -> slot_id -> panel_id. Only entries naming a panel actually assigned to that slot
  // at hydration time are ever stored here — see the fetch effect below.
  const [slotVisiblePanel, setSlotVisiblePanel] = useState<Record<string, Record<string, string>>>(
    {},
  )
  // Guards the persistence effect against writing an empty/partial state back to localStorage
  // during the load race, before the stored state has actually been read once.
  const hydratedRef = useRef(false)

  useEffect(() => {
    let cancelled = false
    Promise.all(LAYOUT_FILE_IDS.map(fetchLayout))
      .then((bodies) => {
        if (cancelled) return
        const valid = bodies.filter(isRawLayoutFile)
        if (valid.length === 0) {
          setLoadState('error')
          return
        }
        const schemaVersion = valid[0].schema_version
        const stored = loadStoredState(schemaVersion)
        const knownLayoutIds = new Set(valid.map((layout) => layout.layout_id))

        const validatedAssignments: Record<string, Record<string, string>> = {}
        const validatedVisiblePanels: Record<string, Record<string, string>> = {}
        for (const layout of valid) {
          const { assignment, validOverrides } = resolveAssignment(
            layout,
            stored?.panel_assignments?.[layout.layout_id],
          )
          if (Object.keys(validOverrides).length > 0) {
            validatedAssignments[layout.layout_id] = validOverrides
          }

          const slots = buildSlots(layout, assignment)
          const slotsById = new Map(slots.map((slot) => [slot.slot_id, slot]))
          const storedVisible = stored?.slot_visible_panel?.[layout.layout_id]
          if (storedVisible) {
            const validVisible: Record<string, string> = {}
            for (const [slotId, panelId] of Object.entries(storedVisible)) {
              const slot = slotsById.get(slotId)
              if (slot && slot.admits.includes(panelId)) validVisible[slotId] = panelId
            }
            if (Object.keys(validVisible).length > 0) {
              validatedVisiblePanels[layout.layout_id] = validVisible
            }
          }
        }

        setRawLayouts(valid)
        setActiveLayoutIdState(
          stored?.active_layout && knownLayoutIds.has(stored.active_layout)
            ? stored.active_layout
            : valid[0].layout_id,
        )
        setPanelAssignments(validatedAssignments)
        setSlotVisiblePanel(validatedVisiblePanels)
        setLoadState('loaded')
        hydratedRef.current = true
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!hydratedRef.current || rawLayouts.length === 0 || !activeLayoutId) return
    // Merge-on-write (`patchStoredState`), not a full overwrite: this hook owns
    // `active_layout`/`panel_assignments`/`slot_visible_panel` only, and must never clobber
    // another owner's field stored under the same ADR-016 key (e.g. the notes strip's
    // `active_notes_file`).
    patchStoredState(rawLayouts[0].schema_version, {
      active_layout: activeLayoutId,
      panel_assignments: panelAssignments,
      slot_visible_panel: slotVisiblePanel,
    })
  }, [rawLayouts, activeLayoutId, panelAssignments, slotVisiblePanel])

  // The single ADR-016 schema version, resolved from the loaded layout files — the one source of
  // truth `NotesStripRegion` also reads, via `StagePage`'s `ActiveSchemaVersionProvider`, rather
  // than a hardcoded constant of its own (both files ship `schema_version: 2` today, but only
  // this derivation is authoritative once a later data-only bump lands).
  const schemaVersion = rawLayouts[0]?.schema_version ?? null

  // The app-facing layouts (REQ-007 W16): each slot's `admits`/`default_panel` recomputed from
  // this layout's resolved panel assignment, so a reassignment (once the configuration-dialog
  // rework calls `setPanelSlot`) is reflected here without any other change to this hook's shape.
  const layouts: LayoutDefinition[] = rawLayouts.map((layout) => {
    const { assignment } = resolveAssignment(layout, panelAssignments[layout.layout_id])
    return {
      schema_version: layout.schema_version,
      layout_id: layout.layout_id,
      name: layout.name,
      slots: buildSlots(layout, assignment),
      grid: layout.grid,
    }
  })

  const activeLayout = layouts.find((layout) => layout.layout_id === activeLayoutId) ?? null

  /** The panel type id resolved as visible for `slot` within `layout`: the stored visible-panel
   * choice when it still names a panel currently assigned to that slot, else the slot's own
   * computed default (which may be `null`). */
  const getSlotPanel = (layout: LayoutDefinition, slot: LayoutSlotDefinition): string | null => {
    const stored = slotVisiblePanel[layout.layout_id]?.[slot.slot_id]
    if (stored && slot.admits.includes(stored)) return stored
    return slot.default_panel
  }

  /** Changes which of a slot's currently-assigned panels is visible — never a reassignment (see
   * `setPanelSlot` for that). This is what `Slot.tsx`'s header dropdown and
   * `LayoutConfigDialog.tsx`'s per-slot select both call today. */
  const setSlotPanel = (layoutId: string, slotId: string, panelId: string) => {
    setSlotVisiblePanel((previous) => ({
      ...previous,
      [layoutId]: { ...previous[layoutId], [slotId]: panelId },
    }))
  }

  /** Moves `panelId` to `slotId` within `layoutId` — the REQ-007 W16 primitive an
   * assignment-only configuration dialog needs ("one selector per panel over its eligible
   * slots"). Silently a no-op if `slotId` is not one of the panel's eligible slots in the loaded
   * layout, matching this hook's existing "invalid input is dropped, never an error" posture. Not
   * called anywhere yet — this data-model phase does not rework `LayoutConfigDialog.tsx`. */
  const setPanelSlot = (layoutId: string, panelId: string, slotId: string) => {
    const layout = rawLayouts.find((candidate) => candidate.layout_id === layoutId)
    const panel = layout?.panels.find((candidate) => candidate.panel_id === panelId)
    if (!panel || !panel.eligible_slots.includes(slotId)) return
    setPanelAssignments((previous) => ({
      ...previous,
      [layoutId]: { ...previous[layoutId], [panelId]: slotId },
    }))
  }

  return {
    loadState,
    layouts,
    schemaVersion,
    activeLayout,
    activeLayoutId,
    setActiveLayoutId: setActiveLayoutIdState,
    getSlotPanel,
    setSlotPanel,
    setPanelSlot,
  }
}
