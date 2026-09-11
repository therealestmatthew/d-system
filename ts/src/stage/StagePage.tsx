import './StagePage.css'
import Slot from '../workbench/Slot'
import LayoutConfigDialog from '../workbench/LayoutConfigDialog'
import { useWorkbenchLayouts } from '../workbench/useWorkbenchLayouts'
import { ActiveSchemaVersionProvider } from '../workbench/schemaVersionContext'
import type { LayoutDefinition } from '../workbench/types'

/**
 * The stage page: the workbench layout engine's root (REQ-007 W05/W06, ADR-016). Loads the
 * shipped layout files (`_data/workbench/layouts/`), renders the active layout's slots on a CSS
 * grid built from that layout's own fractional/grid geometry, and offers a top-right
 * layout-configuration surface to switch layouts and reassign panels to slots.
 *
 * Zero page scrolling and no overlapping regions (REQ-006 R02) hold for both shipped layouts at
 * every required window size because every grid track is wrapped in `minmax(0, ...)` and every
 * slot/panel keeps `min-height: 0`/`overflow: hidden` down its whole box chain, exactly as the
 * pre-engine static grid did — only the geometry's *source* changed (data file, not a CSS rule).
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
  } = useWorkbenchLayouts()

  const resolveSlotPanel = (layout: LayoutDefinition, slotId: string): string | null => {
    const slot = layout.slots.find((candidate) => candidate.slot_id === slotId)
    return slot ? getSlotPanel(layout, slot) : null
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
                getSlotPanel={resolveSlotPanel}
                onSelectSlotPanel={setSlotPanel}
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
                />
              </div>
            ))}
          </main>
        )}
      </div>
    </ActiveSchemaVersionProvider>
  )
}
