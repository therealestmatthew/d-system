import { useEffect, useRef, useState } from 'react'
import { isLayoutDefinition, type LayoutDefinition, type LayoutSlotDefinition } from './types'
import { loadStoredState, patchStoredState } from './storage'

// The two shipped layout files (REQ-007 W05, ADR-016 rule 1) — served at runtime by the Vite dev
// plugin `serveWorkbenchLayouts` (`ts/vite.config.ts`) from `_data/workbench/layouts/`, never
// bundled, so editing a layout file's geometry or slot admits needs no frontend rebuild. Only the
// filenames are named here; every other detail (slot ids, geometry, display names, admits,
// defaults) is the JSON files' content, not this code's.
const LAYOUT_FILE_IDS = ['layout-1', 'layout-2'] as const

export type WorkbenchLoadState = 'loading' | 'loaded' | 'error'

async function fetchLayout(id: string): Promise<unknown> {
  const response = await fetch(`/workbench-layouts/${id}.json`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`status ${response.status}`)
  return response.json()
}

/**
 * Loads the shipped layout files, hydrates the active layout and per-slot panel selections from
 * localStorage (ADR-016 rule 3), and persists changes back. Stored data referencing an unknown
 * layout, slot or panel — or written under a different schema-version key entirely — is dropped
 * silently in favor of each layout's own `default_panel` (ADR-016 rule 4), never surfaced as an
 * error and never migrated.
 */
export function useWorkbenchLayouts() {
  const [loadState, setLoadState] = useState<WorkbenchLoadState>('loading')
  const [layouts, setLayouts] = useState<LayoutDefinition[]>([])
  const [activeLayoutId, setActiveLayoutIdState] = useState<string | null>(null)
  // layout_id -> slot_id -> panel_id. Only entries that survived validation against the loaded
  // layouts are ever stored here — see the fetch effect below.
  const [selections, setSelections] = useState<Record<string, Record<string, string>>>({})
  // Guards the persistence effect against writing an empty/partial state back to localStorage
  // during the load race, before the stored state has actually been read once.
  const hydratedRef = useRef(false)

  useEffect(() => {
    let cancelled = false
    Promise.all(LAYOUT_FILE_IDS.map(fetchLayout))
      .then((bodies) => {
        if (cancelled) return
        const valid = bodies.filter(isLayoutDefinition)
        if (valid.length === 0) {
          setLoadState('error')
          return
        }
        const schemaVersion = valid[0].schema_version
        const stored = loadStoredState(schemaVersion)
        const knownLayoutIds = new Set(valid.map((layout) => layout.layout_id))

        const validatedSelections: Record<string, Record<string, string>> = {}
        if (stored) {
          for (const layout of valid) {
            const perLayoutStored = stored.slot_selections?.[layout.layout_id]
            if (!perLayoutStored) continue
            const slotsById = new Map(layout.slots.map((slot) => [slot.slot_id, slot]))
            const validPerLayout: Record<string, string> = {}
            for (const [slotId, panelId] of Object.entries(perLayoutStored)) {
              const slot = slotsById.get(slotId)
              if (slot && slot.admits.includes(panelId)) validPerLayout[slotId] = panelId
            }
            if (Object.keys(validPerLayout).length > 0) {
              validatedSelections[layout.layout_id] = validPerLayout
            }
          }
        }

        setLayouts(valid)
        setActiveLayoutIdState(
          stored?.active_layout && knownLayoutIds.has(stored.active_layout)
            ? stored.active_layout
            : valid[0].layout_id,
        )
        setSelections(validatedSelections)
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
    if (!hydratedRef.current || layouts.length === 0 || !activeLayoutId) return
    // Merge-on-write (`patchStoredState`), not a full overwrite: this hook owns
    // `active_layout`/`slot_selections` only, and must never clobber another owner's field
    // stored under the same ADR-016 key (e.g. the notes strip's `active_notes_file`).
    patchStoredState(layouts[0].schema_version, {
      active_layout: activeLayoutId,
      slot_selections: selections,
    })
  }, [layouts, activeLayoutId, selections])

  const activeLayout = layouts.find((layout) => layout.layout_id === activeLayoutId) ?? null

  /** The panel type id resolved for `slot` within `layout`: the stored selection when it is
   * still valid for that slot, else the slot's own default (which may be `null`). */
  const getSlotPanel = (layout: LayoutDefinition, slot: LayoutSlotDefinition): string | null => {
    const stored = selections[layout.layout_id]?.[slot.slot_id]
    if (stored && slot.admits.includes(stored)) return stored
    return slot.default_panel
  }

  const setSlotPanel = (layoutId: string, slotId: string, panelId: string) => {
    setSelections((previous) => ({
      ...previous,
      [layoutId]: { ...previous[layoutId], [slotId]: panelId },
    }))
  }

  return {
    loadState,
    layouts,
    activeLayout,
    activeLayoutId,
    setActiveLayoutId: setActiveLayoutIdState,
    getSlotPanel,
    setSlotPanel,
  }
}
