import { useCallback, useEffect, useRef, useState } from 'react'
import {
  isRawLayoutFile,
  type LayoutDefinition,
  type LayoutSlotDefinition,
  type RawLayoutFile,
} from './types'
import { loadStoredState, patchStoredState } from './storage'
import { PANEL_REGISTRY } from './panelRegistry'
import { frameForSlot, slotsEligibleFor } from './slotEligibility'
import { frameHasIdentity } from './slotMatcher'
import { fetchWorkbench } from '../stage/useTerminalEnabled'

// The two shipped layout files (REQ-007 W05, ADR-016 rule 1) — served at runtime by the Vite dev
// plugin `serveWorkbenchLayouts` (`ts/vite.config.ts`) from `_data/workbench/layouts/`, never
// bundled, so editing a layout file's geometry or default assignment needs no frontend rebuild.
// Only the filenames are named here; every other detail (slot ids, geometry, default assignment)
// is the JSON files' content, not this code's. Which slots a panel may occupy is not in them: it is
// computed from the element-configuration and slot-schema data files (`slotEligibility.ts`).
const LAYOUT_FILE_IDS = ['layout-1', 'layout-2'] as const

export type WorkbenchLoadState = 'loading' | 'loaded' | 'error'

async function fetchLayout(id: string): Promise<unknown> {
  const response = await fetch(`/workbench-layouts/${id}.json`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`status ${response.status}`)
  return response.json()
}

// --- REQ-007 W17: the secondary slot's fresh-store default becomes platform-conditional --------

// The one slot id this default applies to, across both shipped layout files — hardcoded the same
// way `TerminalRegion.tsx`'s own websocket path and shell allowlist are: a small, well-known
// piece of this repo's fixed vocabulary, not a value layout files vary per-install. It is the
// slot the shells are assigned to by default; its id names that role (`secondary`), not the
// shell panel type (terms-workbench-ui.md, "Slot naming rule").
const SHELL_HOME_SLOT_ID = 'secondary'
// The panel ids `panelRegistry.tsx` already registers for bash and PowerShell respectively.
const BASH_PANEL_ID = 'terminal'
const POWERSHELL_PANEL_ID = 'terminal-powershell'
const PLATFORM_ROUTE = '/api/v1/workbench/platform'

/**
 * The stored `slot_visible_panel` value meaning "this slot deliberately shows nothing right now"
 * — distinct from *no stored entry at all*, which still resolves to the layout file's own default
 * (and, for the secondary slot, the platform-conditional default above).
 *
 * It exists for exactly one situation (REQ-007 W16, W09 fix cycle 3): a reassignment that moves a
 * slot's *currently visible* panel out of it. Without this, `getSlotPanel` fell through to that
 * slot's "first still-assigned panel" default the instant the moved panel left `admits` — and for
 * the secondary slot, whose remaining assigned panels are CMD and PowerShell, that meant moving the
 * live bash panel to another slot spontaneously mounted a *CMD* panel, which opens a websocket and
 * spawns a shell nobody asked for, consuming one of the backend's six global session slots
 * (`MAX_CONCURRENT_SESSIONS`, ADR-014 section 4). A websocket-opening panel must never mount as a
 * side effect of moving a different panel, so the vacated slot resolves to "nothing visible"
 * instead and `Slot.tsx` offers its header dropdown to pick one of the panels still assigned there.
 *
 * The empty string is safe as the sentinel: it is not a legal panel id (every id in
 * `panelRegistry.tsx` and in the layout files is a non-empty string), and it survives
 * `storage.ts`'s structural `typeof entry === 'string'` check unchanged, so persisting it needs no
 * storage-layer change and an older build reading it simply finds no matching panel and falls back
 * to its own default (ADR-016 rule 4).
 */
const NO_VISIBLE_PANEL = ''

/** The secondary slot's platform-conditional fresh-store default panel id (REQ-007 W17): bash
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
    const response = await fetchWorkbench(PLATFORM_ROUTE, { cache: 'no-store' })
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

/** True when `slotId` may take `panelId` in addition to what `assignment` already places there.
 * A slot whose frame has no `identity` sub-slot has no panel switcher (ADR-031 decision 2), so it
 * holds at most one panel. */
function slotHasRoomFor(
  assignment: Record<string, string>,
  slotId: string,
  panelId: string,
): boolean {
  const frame = frameForSlot(slotId)
  if (!frame || frameHasIdentity(frame)) return true
  return !Object.entries(assignment).some(
    ([otherPanelId, otherSlotId]) => otherSlotId === slotId && otherPanelId !== panelId,
  )
}

/** Resolves one raw layout file's default total assignment (panel_id -> slot_id) overridden by
 * any valid stored per-panel reassignment (REQ-007 W16). Invalid stored entries — an unknown
 * panel, an unknown slot, a slot the panel is not structurally eligible for (ADR-031 decision 4),
 * or a slot with no panel switcher that is already taken — are dropped silently in favor of the
 * file's own default for that panel (ADR-016 rule 4), never an error. Returns both the resolved
 * assignment and the subset of the stored overrides that were actually valid, so the persistence
 * effect below only ever writes back entries `useWorkbenchLayouts` itself already validated
 * once. */
function resolveAssignment(
  layout: RawLayoutFile,
  storedForLayout: Record<string, string> | undefined,
): { assignment: Record<string, string>; validOverrides: Record<string, string> } {
  const declaredPanelIds = new Set(layout.panels.map((panel) => panel.panel_id))
  const slotIds = layout.slots.map((slot) => slot.slot_id)
  const assignment: Record<string, string> = { ...layout.default_assignment }
  const validOverrides: Record<string, string> = {}
  if (storedForLayout) {
    for (const [panelId, slotId] of Object.entries(storedForLayout)) {
      if (!declaredPanelIds.has(panelId)) continue
      if (!slotsEligibleFor(panelId, slotIds).includes(slotId)) continue
      if (!slotHasRoomFor(assignment, slotId, panelId)) continue
      assignment[panelId] = slotId
      validOverrides[panelId] = slotId
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
 * a panel to a slot it is not structurally eligible for, or naming a visible panel not currently assigned to
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
  // REQ-007 W17: the secondary slot's platform-conditional fresh-store default panel id, resolved
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
              if (!slot) continue
              // `NO_VISIBLE_PANEL` is a valid stored value for any declared slot (see its doc
              // above) — it names no panel on purpose, so the `admits` check does not apply to it.
              if (panelId === NO_VISIBLE_PANEL || slot.admits.includes(panelId)) {
                validVisible[slotId] = panelId
              }
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
  // than a hardcoded constant of its own (both files ship `schema_version: 4` today, but only
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
      // REQ-007 W17: the panels the layout declares, unchanged by resolution — the assignment-only
      // configuration dialog reads this to build "one selector per panel over the slots it is
      // eligible for" (`LayoutConfigDialog.tsx`, `slotsEligibleFor`), independent of which slot
      // each panel is *currently* assigned to (that is `slots[].admits`, above).
      panels: layout.panels,
      grid: layout.grid,
    }
  })

  const activeLayout = layouts.find((layout) => layout.layout_id === activeLayoutId) ?? null

  /**
   * The panel type id `slot` actually shows within `layout` — `null` for "show no panel here".
   * This is the *single* resolver: it already accounts for the stored visible-panel choice, the
   * explicit `NO_VISIBLE_PANEL` sentinel, the secondary slot's platform-conditional fresh-store
   * default, the layout file's declared default, and whether the resolved panel type is actually
   * implemented yet (`PANEL_REGISTRY[id].Component` non-null — e.g. a slot admitting a panel id a
   * later phase will fill in). Both consumers — `Slot.tsx`'s header and `StagePage.tsx`'s portal
   * host — take this value verbatim.
   *
   * W09 fix cycle 3 folded the implemented-panel step in from `Slot.tsx`'s former exported
   * `resolveImplementedPanel` helper, which both consumers had to remember to wrap this call in.
   * That split made "nothing is visible here" unrepresentable: the helper turned every `null` back
   * into "the first implemented admitted panel", so the deliberate `NO_VISIBLE_PANEL` state above
   * could not survive the trip to either consumer. One function, one answer, no wrapper to forget.
   *
   * Resolution order:
   *  1. the stored choice, when it is the sentinel (-> `null`) or names an implemented panel
   *     currently assigned here;
   *  2. the secondary slot's platform-conditional default (REQ-007 W17), when that panel is
   *     currently assigned here — fresh store only, since a stored choice already returned above;
   *  3. the layout file's own default for this slot (`buildSlots`), when implemented;
   *  4. the first implemented panel assigned here — what a slot whose declared default names an
   *     unimplemented panel, or declares none at all (layout 1's explorer slot), has always shown;
   *  5. `null`, when no panel assigned here is implemented yet.
   */
  // Stable while the stored choices and the platform default are unchanged, so `StagePage` can
  // memoize the per-render panel placement it resolves through this.
  const getSlotPanel = useCallback((layout: LayoutDefinition, slot: LayoutSlotDefinition): string | null => {
    const implemented = (panelId: string | null | undefined): boolean =>
      !!panelId && slot.admits.includes(panelId) && !!PANEL_REGISTRY[panelId]?.Component

    const stored = slotVisiblePanel[layout.layout_id]?.[slot.slot_id]
    if (stored === NO_VISIBLE_PANEL) return null
    if (implemented(stored)) return stored as string
    // REQ-007 W17: only the secondary slot's *fresh-store* default (no stored choice survived
    // validation above) is platform-conditional, and only when the platform-preferred panel is
    // actually one of this slot's currently-assigned panels — a user who has reassigned
    // `terminal-powershell` away from the secondary slot, or a host the platform route reports as
    // not having PowerShell available, both fall straight through to the layout file's own
    // (platform-neutral) `default_panel` below, same as ADR-016 rule 4's "no valid override falls
    // back to the file's own default" posture elsewhere in this hook.
    if (slot.slot_id === SHELL_HOME_SLOT_ID && implemented(terminalPlatformDefaultPanelId)) {
      return terminalPlatformDefaultPanelId
    }
    if (implemented(slot.default_panel)) return slot.default_panel
    return slot.admits.find((panelId) => PANEL_REGISTRY[panelId]?.Component) ?? null
  }, [slotVisiblePanel, terminalPlatformDefaultPanelId])

  /** Changes which of a slot's currently-assigned panels is visible — never a reassignment (see
   * `setPanelSlot` for that). `Slot.tsx`'s header dropdown is its only caller (REQ-007 W16/W17:
   * the header dropdowns are switchers only, and the configuration dialog no longer duplicates
   * them). Also the way out of the `NO_VISIBLE_PANEL` state a reassignment can leave behind: any
   * pick here overwrites the sentinel with a real panel id. */
  const setSlotPanel = (layoutId: string, slotId: string, panelId: string) => {
    setSlotVisiblePanel((previous) => ({
      ...previous,
      [layoutId]: { ...previous[layoutId], [slotId]: panelId },
    }))
  }

  /** Moves `panelId` to `slotId` within `layoutId` — the REQ-007 W16 primitive the W17
   * assignment-only configuration dialog calls ("one selector per panel over the slots it is
   * eligible for"). Silently a no-op if `slotId` is not a slot the panel is structurally eligible
   * for in the loaded layout, matching this hook's existing "invalid input is dropped, never an
   * error" posture.
   *
   * It writes three things in one batched event-handler call, and each one is required:
   *
   *  1. `panelAssignments[layoutId][panelId] = slotId` — the move itself.
   *  2. `slotVisiblePanel[layoutId][slotId] = panelId` — the moved panel becomes the destination
   *     slot's visible panel. Without this (W09 fix cycle 1's state), a panel moved into a slot
   *     that already had a different visible occupant was the visible panel of *neither* slot, so
   *     `StagePage.tsx` rendered no portal for it at all and it was genuinely unmounted — a silent
   *     kill routed straight through the one primitive W16 exists to make safe. The panel this
   *     *displaces* from the destination slot's visibility does unmount (one visible panel per
   *     slot), which is why `LayoutConfigDialog.tsx` states that consequence and takes a confirm
   *     before ever calling this — REQ-007 W16's "where a remount is unavoidable, the dialog
   *     states it explicitly before applying".
   *  3. `slotVisiblePanel[layoutId][sourceSlotId] = NO_VISIBLE_PANEL`, when the panel being moved
   *     was the source slot's visible panel. See `NO_VISIBLE_PANEL`'s own doc: this is what stops
   *     the vacated slot from spontaneously promoting the next panel assigned to it, which for the
   *     secondary slot meant auto-mounting a CMD panel — a websocket, a shell process and one of
   *     the backend's six global session slots, all as a side effect of moving a different panel.
   *
   * What this function deliberately no longer relies on is React batching *rescuing* a doomed
   * portal: the moved panel's component instance now survives because `StagePage.tsx` portals each
   * panel into its own stable per-panel host element whose identity never changes, not because
   * these two state writes land in the same commit. See `StagePage.tsx`'s file doc for why the
   * previous "same key, new container" assumption could never have worked.
   */
  const setPanelSlot = (layoutId: string, panelId: string, slotId: string) => {
    const rawLayout = rawLayouts.find((candidate) => candidate.layout_id === layoutId)
    const panel = rawLayout?.panels.find((candidate) => candidate.panel_id === panelId)
    if (!rawLayout || !panel) return
    const slotIds = rawLayout.slots.map((slot) => slot.slot_id)
    if (!slotsEligibleFor(panelId, slotIds).includes(slotId)) return
    const layout = layouts.find((candidate) => candidate.layout_id === layoutId)
    if (!layout) return
    const currentAssignment = Object.fromEntries(
      layout.slots.flatMap((slot) => slot.admits.map((admitted) => [admitted, slot.slot_id])),
    )
    if (!slotHasRoomFor(currentAssignment, slotId, panelId)) return
    const sourceSlot = layout.slots.find((candidate) => candidate.admits.includes(panelId)) ?? null
    if (sourceSlot?.slot_id === slotId) return // already there — nothing to move, nothing to write.
    const sourceSlotLosesItsVisiblePanel =
      sourceSlot !== null && getSlotPanel(layout, sourceSlot) === panelId

    setPanelAssignments((previous) => ({
      ...previous,
      [layoutId]: { ...previous[layoutId], [panelId]: slotId },
    }))
    setSlotVisiblePanel((previous) => {
      const forLayout: Record<string, string> = { ...previous[layoutId], [slotId]: panelId }
      if (sourceSlot && sourceSlotLosesItsVisiblePanel) {
        forLayout[sourceSlot.slot_id] = NO_VISIBLE_PANEL
      }
      return { ...previous, [layoutId]: forLayout }
    })
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
