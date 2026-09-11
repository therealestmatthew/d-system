import { useState } from 'react'
import { createPortal } from 'react-dom'
import './StagePage.css'
import Slot, { resolveImplementedPanel } from '../workbench/Slot'
import LayoutConfigDialog from '../workbench/LayoutConfigDialog'
import { useWorkbenchLayouts } from '../workbench/useWorkbenchLayouts'
import { ActiveSchemaVersionProvider } from '../workbench/schemaVersionContext'
import { PANEL_REGISTRY } from '../workbench/panelRegistry'
import type { LayoutDefinition, LayoutSlotDefinition } from '../workbench/types'

/**
 * The stage page: the workbench layout engine's root (REQ-007 W05/W06/W16/W17, ADR-016). Loads
 * the shipped layout files (`_data/workbench/layouts/`), renders the active layout's slots on a
 * CSS grid built from that layout's own fractional/grid geometry, and offers a top-right
 * layout-configuration surface to switch layouts and reassign panels to slots.
 *
 * Zero page scrolling and no overlapping regions (REQ-006 R02) hold for both shipped layouts at
 * every required window size because every grid track is wrapped in `minmax(0, ...)` and every
 * slot/panel keeps `min-height: 0`/`overflow: hidden` down its whole box chain, exactly as the
 * pre-engine static grid did — only the geometry's *source* changed (data file, not a CSS rule).
 *
 * REQ-007 W17 item 4: this is also the portal host that keeps a panel's component instance alive
 * across a reassignment to a different slot (never just a layout switch). `slotBodies` is a
 * slot_id -> body-container map, populated by each `Slot`'s `registerBody` callback once its
 * container div mounts; the portal list below renders every slot's currently-resolved,
 * implemented panel into its slot's registered container, *keyed by panel id*. Because the React
 * element at that keyed position is the same `createPortal(<Component />, container, panelId)`
 * call across renders — only `container` changes when `LayoutConfigDialog`'s `setPanelSlot` moves
 * the panel to a different slot's already-registered container — React relocates the mounted DOM
 * subtree rather than unmounting and remounting it, so a live terminal session (or any other
 * panel's in-progress state) survives the move. This extends, rather than replaces, the
 * pre-existing "one grid keyed by slot_id" mechanism below: the outer per-slot `<div
 * key={slot.slot_id}>` grid cells (and so each slot's registered body container) never remount
 * across a layout switch either, since both shipped layout files declare the identical four slot
 * ids — that stability is exactly what let idea `000107`'s layout 1->2->1 round-trip defect close
 * once the layout files' own `default_visible_panel.terminal` entries agreed (both now name the
 * bash panel), with no engine change required for that case.
 *
 * Also the sole provider of the ADR-016 schema version (`ActiveSchemaVersionProvider`, fed by
 * `useWorkbenchLayouts`'s own resolution of it): every panel that persists a selection under the
 * ADR-016 storage key — the notes strip included — reads it from here rather than a hardcoded
 * constant of its own, so a data-only `schema_version` bump moves every consumer together.
 */
export default function StagePage() {
  const {
    loadState,
    layouts,
    schemaVersion,
    activeLayout,
    setActiveLayoutId,
    getSlotPanel,
    setSlotPanel,
    setPanelSlot,
  } = useWorkbenchLayouts()

  // slot_id -> that slot's registered body container (REQ-007 W17 item 4, see file doc above).
  // Never cleared on a layout switch: both shipped layouts share the same four slot ids, so every
  // `Slot` instance — and so every entry here — lives for the whole session once first mounted.
  const [slotBodies, setSlotBodies] = useState<Record<string, HTMLDivElement | null>>({})

  const registerSlotBody = (slotId: string) => (element: HTMLDivElement | null) => {
    setSlotBodies((previous) =>
      previous[slotId] === element ? previous : { ...previous, [slotId]: element },
    )
  }

  const renderPanelPortal = (layout: LayoutDefinition, slot: LayoutSlotDefinition) => {
    const panelId = resolveImplementedPanel(slot.admits, getSlotPanel(layout, slot))
    const container = slotBodies[slot.slot_id]
    if (!panelId || !container) return null
    const Component = PANEL_REGISTRY[panelId]?.Component
    if (!Component) return null
    return createPortal(<Component />, container, panelId)
  }

  return (
    <ActiveSchemaVersionProvider value={schemaVersion}>
      <div className="stage-page">
        <header className="stage-page__header">
          <h1>D-System Live Demo Stage</h1>
          <div className="stage-page__layout-controls">
            {loadState === 'loaded' && layouts.length > 0 ? (
              <LayoutConfigDialog
                layouts={layouts}
                activeLayout={activeLayout}
                onSelectLayout={setActiveLayoutId}
                onAssignPanelSlot={setPanelSlot}
              />
            ) : null}
          </div>
        </header>
        {loadState === 'loading' ? (
          <main className="stage-page__grid">
            <p className="stage-placeholder-text">Loading workbench layouts…</p>
          </main>
        ) : loadState === 'error' || !activeLayout ? (
          <main className="stage-page__grid">
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not load the workbench layout files from{' '}
              <code>_data/workbench/layouts/</code>.
            </p>
          </main>
        ) : (
          <>
            <main
              className="stage-page__grid"
              style={{
                gridTemplateColumns: activeLayout.grid.columns
                  .map((track) => `minmax(0, ${track})`)
                  .join(' '),
                gridTemplateRows: activeLayout.grid.rows
                  .map((track) => `minmax(0, ${track})`)
                  .join(' '),
                gridTemplateAreas: activeLayout.grid.areas.map((row) => `"${row}"`).join(' '),
              }}
            >
              {activeLayout.slots.map((slot) => (
                <div
                  key={slot.slot_id}
                  className="stage-workbench-slot"
                  style={{ gridArea: slot.slot_id }}
                >
                  <Slot
                    slot={slot}
                    resolvedPanelId={getSlotPanel(activeLayout, slot)}
                    onSelectPanel={(panelId) =>
                      setSlotPanel(activeLayout.layout_id, slot.slot_id, panelId)
                    }
                    registerBody={registerSlotBody(slot.slot_id)}
                  />
                </div>
              ))}
            </main>
            {activeLayout.slots.map((slot) => renderPanelPortal(activeLayout, slot))}
          </>
        )}
      </div>
    </ActiveSchemaVersionProvider>
  )
}
