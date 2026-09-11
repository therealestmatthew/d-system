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

// --- REQ-007 W17: the terminal slot's fresh-store default becomes platform-conditional --------

// The one slot id this default applies to, across both shipped layout files — hardcoded the same
// way `TerminalRegion.tsx`'s own websocket path and shell allowlist are: a small, well-known
// piece of this repo's fixed vocabulary, not a value layout files vary per-install.
const TERMINAL_SLOT_ID = 'terminal'
// The panel ids `panelRegistry.tsx` already registers for bash and PowerShell respectively.
const BASH_PANEL_ID = 'terminal'
const POWERSHELL_PANEL_ID = 'terminal-powershell'
const PLATFORM_ROUTE = '/api/v1/workbench/platform'

/** The terminal slot's platform-conditional fresh-store default panel id (REQ-007 W17): bash
 * unless the backend's `/platform` route (`src/api/routes/workbench.py`, W09-C1) reports
 * `windows`, in which case PowerShell. The route is gated behind `D_SYSTEM_DEMO_TERMINAL=1`
 * (ADR-015 rule 1) exactly like the terminal websocket itself, so a non-ok response — 404 when
 * the flag is unset, same as every other route that import gate hides — resolves to bash here
 * too, never an error and never a guess at a platform this route did not report. Awaited as part
 * of this hook's one load effect (below), never as a separate, later-resolving fetch: resolving
 * it before `loadState` ever reaches `'loaded'` is what stops a fresh session's default terminal
 * panel from changing *after* a session may have already started against the file's own
 * platform-neutral default — the exact race a later-arriving platform answer would otherwise
 * open, one this route's own absence-by-default posture (ADR-013) makes easy to trip over. */
async function fetchTerminalPlatformDefaultPanel(): Promise<string> {
  try {
    const response = await fetch(PLATFORM_ROUTE, { cache: 'no-store' })
    if (!response.ok) return BASH_PANEL_ID
    const body: unknown = await response.json()
    const platform =
      typeof body === 'object' && body !== null
        ? (body as Record<string, unknown>).platform
        : undefined
    return platform === 'windows' ? POWERSHELL_PANEL_ID : BASH_PANEL_ID
  } catch {
    return BASH_PANEL_ID
  }
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
 * admits list); `Slot.tsx`'s header dropdown is the only caller of `setSlotPanel` as of the W17
 * delta — `LayoutConfigDialog.tsx` no longer duplicates it (REQ-007 W16/W17: that was never
 * intended). `setPanelSlot`, exposed alongside them, is the REQ-007 W16 primitive — moving a
 * panel to a different one of its eligible slots — that the W17 assignment-only configuration
 * dialog now calls.
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
  // REQ-007 W17: the terminal slot's platform-conditional fresh-store default panel id, resolved
  // once by the load effect below (see `fetchTerminalPlatformDefaultPanel`'s own doc for why it
  // is awaited alongside the layout files rather than fetched separately). The initial value here
  // is never actually observed by a consumer — `getSlotPanel` is only ever called once
  // `loadState` reaches `'loaded'`, by which point this has already resolved.
  const [terminalPlatformDefaultPanelId, setTerminalPlatformDefaultPanelId] =
    useState<string>(BASH_PANEL_ID)
  // Guards the persistence effect against writing an empty/partial state back to localStorage
  // during the load race, before the stored state has actually been read once.
  const hydratedRef = useRef(false)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      Promise.all(LAYOUT_FILE_IDS.map(fetchLayout)),
      fetchTerminalPlatformDefaultPanel(),
    ])
      .then(([bodies, platformDefaultPanelId]) => {
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
        setTerminalPlatformDefaultPanelId(platformDefaultPanelId)
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
  // this layout's resolved panel assignment, so a reassignment (via the configuration dialog's
  // `setPanelSlot` call, REQ-007 W17) is reflected here without any other change to this hook's
  // shape.
  const layouts: LayoutDefinition[] = rawLayouts.map((layout) => {
    const { assignment } = resolveAssignment(layout, panelAssignments[layout.layout_id])
    return {
      schema_version: layout.schema_version,
      layout_id: layout.layout_id,
      name: layout.name,
      slots: buildSlots(layout, assignment),
      // REQ-007 W17: the raw file's own per-panel eligibility, unchanged by resolution — the
      // assignment-only configuration dialog reads this to build "one selector per panel over
      // its eligible slots" (`LayoutConfigDialog.tsx`), independent of which slot each panel is
      // *currently* assigned to (that is `slots[].admits`, above).
      panels: layout.panels,
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
    // REQ-007 W17: only the terminal slot's *fresh-store* default (no stored choice survived
    // validation above) is platform-conditional, and only when the platform-preferred panel is
    // actually one of this slot's currently-assigned panels — a user who has reassigned
    // `terminal-powershell` away from the terminal slot, or a host the platform route reports as
    // not having PowerShell available, both fall straight through to the layout file's own
    // (platform-neutral) `default_panel` below, same as ADR-016 rule 4's "no valid override falls
    // back to the file's own default" posture elsewhere in this hook.
    if (
      slot.slot_id === TERMINAL_SLOT_ID &&
      slot.admits.includes(terminalPlatformDefaultPanelId)
    ) {
      return terminalPlatformDefaultPanelId
    }
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

  /** Moves `panelId` to `slotId` within `layoutId` — the REQ-007 W16 primitive the W17
   * assignment-only configuration dialog calls ("one selector per panel over its eligible
   * slots"). Silently a no-op if `slotId` is not one of the panel's eligible slots in the loaded
   * layout, matching this hook's existing "invalid input is dropped, never an error" posture. */
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
