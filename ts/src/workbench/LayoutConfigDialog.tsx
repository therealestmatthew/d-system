import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import type { LayoutDefinition } from './types'

const CONFIG_DIALOG_WIDTH_PX = 320

/** The slot id `layout` currently assigns `panelId` to, or `null` if (unexpectedly) nothing
 * assigns it — every declared panel is assigned to exactly one of its own eligible slots by
 * construction (`useWorkbenchLayouts`'s total-mapping resolution), so this is a lookup, not a
 * search for an edge case the data model allows. */
function findAssignedSlotId(layout: LayoutDefinition, panelId: string): string | null {
  const slot = layout.slots.find((candidate) => candidate.admits.includes(panelId))
  return slot ? slot.slot_id : null
}

function slotDisplayName(layout: LayoutDefinition, slotId: string): string {
  return layout.slots.find((candidate) => candidate.slot_id === slotId)?.display_name ?? slotId
}

/**
 * The layout-configuration surface (REQ-007 W05, reworked by W16/W17): a button at the page's top
 * right opening a dismissible popup (reusing `Popover`, so it inherits REQ-006 R03's click-
 * dismiss behavior) that selects the active layout and, per panel, assigns it to one of its own
 * eligible slots — a total mapping, one `<select>` per panel. No geometry control is offered here
 * — ADR-016 rule 2: "the configuration surface selects the active layout and assigns panels to
 * slots; changing a slot's geometry ... is a reviewed commit of a JSON file."
 *
 * This is deliberately *not* the pre-W16 shape, which offered one `<select>` per *slot* choosing
 * that slot's *visible* panel — a second, dialog-level copy of exactly what each multi-panel
 * slot's own header dropdown already does (`Slot.tsx`), never an actual reassignment. REQ-007
 * W16/W17 retire that duplication: this dialog now only ever calls `onAssignPanelSlot`
 * (`useWorkbenchLayouts`'s `setPanelSlot`), which moves a panel between slots, and never touches
 * a slot's visible-panel choice at all — that stays the header dropdown's job alone (`Slot.tsx`,
 * "switchers only... they never re-assign").
 *
 * REQ-007 W17 item 4: picking a different slot here applies immediately, with no confirmation
 * step, because it does not kill anything to confirm against — `StagePage.tsx` portals a panel's
 * component into whichever slot's container is currently assigned to it, keyed by panel id, so
 * moving a panel to a new (already-mounted) slot container relocates its live component instance
 * rather than remounting it. There is no case reachable from this dialog today where that portal
 * target is unavailable (every slot named in a panel's `eligible_slots` is a slot the active
 * layout actually declares, by the layout-schema test idea `000098` already enforces), so no
 * "remount is unavoidable" fallback notice applies here; if a future layout ever named an
 * eligible slot the active layout does not have, `StagePage.tsx`'s portal simply does not render
 * until that slot exists, same as any other panel with no registered container yet — never a
 * crash, and never a silent loss of an already-mounted instance, since nothing already mounted
 * would need moving in that case.
 */
export default function LayoutConfigDialog({
  layouts,
  activeLayout,
  onSelectLayout,
  onAssignPanelSlot,
}: {
  layouts: LayoutDefinition[]
  activeLayout: LayoutDefinition | null
  onSelectLayout: (layoutId: string) => void
  onAssignPanelSlot: (layoutId: string, panelId: string, slotId: string) => void
}) {
  return (
    <Popover
      triggerLabel="Configure layout ▾"
      title="Layout configuration"
      width={CONFIG_DIALOG_WIDTH_PX}
    >
      <div className="stage-workbench-config">
        <fieldset className="stage-workbench-config__layouts">
          <legend>Active layout</legend>
          {layouts.map((layout) => (
            <label key={layout.layout_id} className="stage-workbench-config__layout-option">
              <input
                type="radio"
                name="workbench-active-layout"
                value={layout.layout_id}
                checked={activeLayout?.layout_id === layout.layout_id}
                onChange={() => onSelectLayout(layout.layout_id)}
              />
              {layout.name}
            </label>
          ))}
        </fieldset>

        {activeLayout ? (
          <fieldset className="stage-workbench-config__panels">
            <legend>Panel assignment — {activeLayout.name}</legend>
            {activeLayout.panels
              .filter((panel) => PANEL_REGISTRY[panel.panel_id]?.Component)
              .map((panel) => {
                const assignedSlotId = findAssignedSlotId(activeLayout, panel.panel_id)
                return (
                  <label key={panel.panel_id} className="stage-workbench-config__panel-option">
                    <span>{panelDisplayName(panel.panel_id)}</span>
                    <select
                      value={assignedSlotId ?? panel.eligible_slots[0]}
                      onChange={(event) =>
                        onAssignPanelSlot(activeLayout.layout_id, panel.panel_id, event.target.value)
                      }
                    >
                      {panel.eligible_slots.map((slotId) => (
                        <option key={slotId} value={slotId}>
                          {slotDisplayName(activeLayout, slotId)}
                        </option>
                      ))}
                    </select>
                  </label>
                )
              })}
          </fieldset>
        ) : null}
      </div>
    </Popover>
  )
}
