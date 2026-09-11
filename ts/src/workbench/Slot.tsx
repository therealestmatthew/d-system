import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import type { LayoutSlotDefinition } from './types'

/**
 * One layout slot (REQ-007 W05/W06): renders whichever panel is currently resolved for it.
 *
 * - Zero implemented panels admitted (e.g. `explorer` before phase-wb-05/06 land): a plain header
 *   naming the slot and a clear in-page placeholder — the same "say so in place" posture ADR-013
 *   applies to the absent terminal route, generalized to an absent panel.
 * - Exactly one implemented panel admitted: rendered directly, no extra chrome. Every panel this
 *   phase ships (`TerminalRegion`, `NotesStripRegion`, `OverviewRegion`) already renders its own
 *   `.stage-region` section, which is what satisfies "a single-panel slot renders a plain
 *   header" here (the notes strip's own header carries no title, per REQ-007 W01).
 * - More than one implemented panel admitted (the terminal slot, since `phase-wb-03`'s CMD and
 *   PowerShell shell options landed, and layout 1's explorer slot, since `phase-wb-06`'s
 *   `idea-explorer` joined `phase-wb-05`'s `file-browser`): a slot-level header shows the current
 *   panel's name
 *   beside a small downward-triangle dropdown listing the others; selecting one swaps it into
 *   view. The swapped-in panel still renders its own inner header too — a double-header cosmetic
 *   case left as-is, noted in `panelRegistry.tsx`.
 */
export default function Slot({
  slot,
  resolvedPanelId,
  onSelectPanel,
}: {
  slot: LayoutSlotDefinition
  resolvedPanelId: string | null
  onSelectPanel: (panelId: string) => void
}) {
  const implementedAdmits = slot.admits.filter((id) => PANEL_REGISTRY[id]?.Component)

  if (implementedAdmits.length === 0) {
    return (
      <section className="stage-region stage-workbench-slot--empty" aria-label={slot.display_name}>
        <header className="stage-region__header">
          <h2>{slot.display_name}</h2>
        </header>
        <div className="stage-region__body">
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            No panels are available in this slot yet.
          </p>
        </div>
      </section>
    )
  }

  const currentPanelId =
    resolvedPanelId && implementedAdmits.includes(resolvedPanelId)
      ? resolvedPanelId
      : implementedAdmits[0]
  const Component = PANEL_REGISTRY[currentPanelId]?.Component

  if (implementedAdmits.length === 1 || !Component) {
    return Component ? <Component /> : null
  }

  const otherPanelIds = implementedAdmits.filter((id) => id !== currentPanelId)

  return (
    <section className="stage-region stage-workbench-slot--multi" aria-label={slot.display_name}>
      <header className="stage-region__header stage-workbench-slot__header">
        <Popover
          triggerLabel={`${panelDisplayName(currentPanelId)} ▾`}
          title={`${slot.display_name}: choose a panel`}
        >
          {(close) => (
            <ul className="stage-workbench-slot__panel-list">
              {otherPanelIds.map((panelId) => (
                <li key={panelId}>
                  <button
                    type="button"
                    className="stage-workbench-slot__panel-option"
                    onClick={() => {
                      onSelectPanel(panelId)
                      close()
                    }}
                  >
                    {panelDisplayName(panelId)}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Popover>
      </header>
      <div className="stage-region__body stage-workbench-slot__body">
        <Component />
      </div>
    </section>
  )
}
