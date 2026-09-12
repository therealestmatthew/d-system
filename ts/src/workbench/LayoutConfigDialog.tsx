import { useState } from 'react'
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
 * REQ-007 W16, "re-assigning a panel to another slot never silently kills a shell session":
 *
 * The panel *being moved* is never killed and needs no confirmation. `StagePage.tsx` portals every
 * panel into its own stable host element and moves that element between slot bodies, so a
 * reassignment does not re-render the panel, let alone remount it — a live shell keeps its
 * websocket, its process and its scrollback across the move (see `StagePage.tsx`'s file doc for
 * the mechanism, and for why the previous "the portal relocates itself" assumption was false).
 *
 * What a move *can* end is the panel already visible in the destination slot. A slot shows one
 * panel at a time, so moving a panel into an occupied slot hides the occupant, and a hidden panel
 * is unmounted (mounting hidden panels would open shell sessions nobody is watching, against the
 * backend's six-session global cap). That unmount is genuinely unavoidable, so this dialog takes
 * W16's other branch for it: the move is *not* applied on selection. The dialog states in place
 * which panel would be closed and what that costs, and applies only when the presenter confirms.
 * Moving a panel into a slot that currently shows nothing applies immediately — there is nothing
 * to close and so nothing to warn about.
 */
export default function LayoutConfigDialog({
  layouts,
  activeLayout,
  onSelectLayout,
  onAssignPanelSlot,
  visiblePanelInSlot,
}: {
  layouts: LayoutDefinition[]
  activeLayout: LayoutDefinition | null
  onSelectLayout: (layoutId: string) => void
  onAssignPanelSlot: (layoutId: string, panelId: string, slotId: string) => void
  /** The panel currently visible (and so currently mounted) in `slotId`, or `null` when that slot
   * shows nothing — `StagePage.tsx` passes the same resolved answer the slots themselves render
   * from. */
  visiblePanelInSlot: (slotId: string) => string | null
}) {
  // A move selected but not yet applied, because it would close the destination slot's current
  // occupant. Exactly one can be pending at a time: the selector that opened it is the only one
  // showing a value that is not yet real.
  const [pendingMove, setPendingMove] = useState<{
    panelId: string
    slotId: string
    displacedPanelId: string
  } | null>(null)

  const requestMove = (layoutId: string, panelId: string, slotId: string) => {
    const displacedPanelId = visiblePanelInSlot(slotId)
    if (displacedPanelId && displacedPanelId !== panelId) {
      setPendingMove({ panelId, slotId, displacedPanelId })
      return
    }
    setPendingMove(null)
    onAssignPanelSlot(layoutId, panelId, slotId)
  }

  const applyPendingMove = (layoutId: string) => {
    if (!pendingMove) return
    onAssignPanelSlot(layoutId, pendingMove.panelId, pendingMove.slotId)
    setPendingMove(null)
  }

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
                const pendingHere = pendingMove?.panelId === panel.panel_id ? pendingMove : null
                return (
                  <div key={panel.panel_id}>
                    <label className="stage-workbench-config__panel-option">
                      <span>{panelDisplayName(panel.panel_id)}</span>
                      <select
                        // While a move is pending confirmation the selector shows the slot the
                        // presenter picked, not the one still in force — otherwise the control
                        // would snap back under the notice asking them to confirm it.
                        value={pendingHere?.slotId ?? assignedSlotId ?? panel.eligible_slots[0]}
                        onChange={(event) =>
                          requestMove(activeLayout.layout_id, panel.panel_id, event.target.value)
                        }
                      >
                        {panel.eligible_slots.map((slotId) => (
                          <option key={slotId} value={slotId}>
                            {slotDisplayName(activeLayout, slotId)}
                          </option>
                        ))}
                      </select>
                    </label>
                    {pendingHere ? (
                      <div
                        className="stage-workbench-config__notice"
                        role="alert"
                        aria-live="polite"
                      >
                        <p className="stage-placeholder-text stage-placeholder-text--absent">
                          {slotDisplayName(activeLayout, pendingHere.slotId)} is showing{' '}
                          {panelDisplayName(pendingHere.displacedPanelId)}. A slot shows one panel
                          at a time, so moving {panelDisplayName(panel.panel_id)} there closes{' '}
                          {panelDisplayName(pendingHere.displacedPanelId)} — any live session or
                          unsaved state in it ends and it starts fresh when shown again.{' '}
                          {panelDisplayName(panel.panel_id)} itself is not restarted by the move.
                        </p>
                        <button
                          type="button"
                          // Reuses the workbench family's existing small-button style: adding a
                          // rule for a new class would mean editing `StagePage.css`, which is
                          // outside this work item's deliverable paths.
                          className="stage-workbench-config__notice-action stage-workbench-slot__panel-option"
                          onClick={() => applyPendingMove(activeLayout.layout_id)}
                        >
                          Confirm: move {panelDisplayName(panel.panel_id)} and close{' '}
                          {panelDisplayName(pendingHere.displacedPanelId)}
                        </button>
                        <button
                          type="button"
                          // Reuses the workbench family's existing small-button style: adding a
                          // rule for a new class would mean editing `StagePage.css`, which is
                          // outside this work item's deliverable paths.
                          className="stage-workbench-config__notice-action stage-workbench-slot__panel-option"
                          onClick={() => setPendingMove(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : null}
                  </div>
                )
              })}
          </fieldset>
        ) : null}
      </div>
    </Popover>
  )
}
