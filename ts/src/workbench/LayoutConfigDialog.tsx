import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import type { LayoutDefinition } from './types'

const CONFIG_DIALOG_WIDTH_PX = 320

/**
 * The layout-configuration surface (REQ-007 W05): a button at the page's top right opening a
 * dismissible popup (reusing `Popover`, so it inherits REQ-006 R03's click-dismiss behavior) that
 * selects the active layout and assigns a panel to each of its slots. No geometry control is
 * offered here — ADR-016 rule 2: "the configuration surface selects the active layout and assigns
 * panels to slots; changing a slot's geometry ... is a reviewed commit of a JSON file."
 */
export default function LayoutConfigDialog({
  layouts,
  activeLayout,
  onSelectLayout,
  getSlotPanel,
  onSelectSlotPanel,
}: {
  layouts: LayoutDefinition[]
  activeLayout: LayoutDefinition | null
  onSelectLayout: (layoutId: string) => void
  getSlotPanel: (layout: LayoutDefinition, slotId: string) => string | null
  onSelectSlotPanel: (layoutId: string, slotId: string, panelId: string) => void
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
          <fieldset className="stage-workbench-config__slots">
            <legend>Panel assignment — {activeLayout.name}</legend>
            {activeLayout.slots.map((slot) => {
              const implementedAdmits = slot.admits.filter((id) => PANEL_REGISTRY[id]?.Component)
              const resolved = getSlotPanel(activeLayout, slot.slot_id)
              return (
                <label key={slot.slot_id} className="stage-workbench-config__slot-option">
                  <span>{slot.display_name}</span>
                  {implementedAdmits.length === 0 ? (
                    <span className="stage-placeholder-text stage-placeholder-text--absent">
                      No panels available
                    </span>
                  ) : (
                    <select
                      value={resolved && implementedAdmits.includes(resolved) ? resolved : implementedAdmits[0]}
                      onChange={(event) =>
                        onSelectSlotPanel(activeLayout.layout_id, slot.slot_id, event.target.value)
                      }
                    >
                      {implementedAdmits.map((panelId) => (
                        <option key={panelId} value={panelId}>
                          {panelDisplayName(panelId)}
                        </option>
                      ))}
                    </select>
                  )}
                </label>
              )
            })}
          </fieldset>
        ) : null}
      </div>
    </Popover>
  )
}
