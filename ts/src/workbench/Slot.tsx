import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import type { LayoutSlotDefinition } from './types'

/**
 * One layout slot's chrome (REQ-007 W05/W06/W16/W17).
 *
 * `visiblePanelId` arrives already fully resolved by `useWorkbenchLayouts`'s `getSlotPanel` — the
 * one resolver, which accounts for the stored choice, the deliberate "nothing visible" state, the
 * terminal slot's platform-conditional default, the layout file's default and whether a panel type
 * is implemented yet. This file never re-resolves it (the former exported `resolveImplementedPanel`
 * helper, which both this file and `StagePage.tsx` had to wrap every call in, is gone: see
 * `getSlotPanel`'s doc for why one function with one answer replaced it).
 *
 * The header has exactly two shapes:
 *
 * - **A plain header** naming the slot, when there is nothing to choose: the slot has no
 *   implemented panel assigned to it at all (e.g. a slot admitting only panel ids a later phase
 *   will implement), or it has exactly one and that one is showing. REQ-007 W16/W17: "a slot with
 *   one assigned panel renders a plain header."
 * - **A switcher dropdown** — the current panel's name beside a small downward triangle, opening a
 *   list of the slot's other assigned panels — when the slot holds more than one implemented panel,
 *   or when it currently shows nothing but still holds at least one. That second case is the way
 *   back from the "nothing visible" state a reassignment can leave behind (`NO_VISIBLE_PANEL` in
 *   `useWorkbenchLayouts.ts`): a slot showing nothing must offer a way to show something, even when
 *   only one panel remains assigned to it, or that panel would be reachable only through the
 *   configuration dialog.
 *
 * The dropdown is a *visibility switcher only*, never a reassignment (REQ-007 W16/W17): it lists
 * exactly the panels currently assigned here (`slot.admits`, whatever the configuration dialog's
 * per-panel assignment places in this slot) and only ever calls `onSelectPanel` (`setSlotPanel`).
 * Moving a panel to a *different* slot is the assignment-only configuration dialog's job
 * (`LayoutConfigDialog.tsx`, "one selector per panel over its eligible slots").
 *
 * REQ-007 W17 item 4: the resolved panel's component is not rendered in this file's own JSX tree.
 * This slot renders a stable body container `<div>` (registered with `StagePage.tsx` via
 * `registerBody`), and `StagePage.tsx` appends the visible panel's own persistent host element into
 * it. Every branch below returns the *same* root shape — `<section>`, then an unconditional
 * `<header>`, then that body `<div>` — regardless of how many panels are assigned or whether one is
 * showing, varying only their *contents*. That uniformity is load-bearing, not tidiness: React
 * cannot reuse a DOM node across a change of returned root element type, so a reassignment that
 * changed a slot's panel count across the 1 <-> (0 or >1) boundary used to tear this whole subtree
 * down and rebuild it — taking the registered body container, and any panel mounted inside it, with
 * it (verified live in W09 fix cycle 1: a reassignment closed the moved terminal's websocket and
 * opened a brand new one). An ordinary prop/children update reconciles in place instead, so the
 * body `<div>` is the same DOM node across every 0/1/>1 transition.
 */
export default function Slot({
  slot,
  visiblePanelId,
  onSelectPanel,
  registerBody,
}: {
  slot: LayoutSlotDefinition
  visiblePanelId: string | null
  onSelectPanel: (panelId: string) => void
  registerBody: (element: HTMLDivElement | null) => void
}) {
  const implementedAdmits = slot.admits.filter((id) => PANEL_REGISTRY[id]?.Component)
  const isEmpty = implementedAdmits.length === 0
  const isMulti = implementedAdmits.length > 1
  const showsNothing = !isEmpty && visiblePanelId === null
  const hasSwitcher = isMulti || showsNothing
  const otherPanelIds = implementedAdmits.filter((id) => id !== visiblePanelId)

  return (
    <section
      className={
        'stage-region' +
        (isEmpty ? ' stage-workbench-slot--empty' : '') +
        (isMulti ? ' stage-workbench-slot--multi' : '')
      }
      aria-label={slot.display_name}
    >
      <header className="stage-region__header stage-workbench-slot__header">
        {hasSwitcher ? (
          <Popover
            triggerLabel={`${visiblePanelId ? panelDisplayName(visiblePanelId) : 'Choose a panel'} ▾`}
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
        ) : (
          // Nothing to switch to — a slot with no implemented panel, or with exactly one and that
          // one already showing — so the header just names the slot.
          <h2>{slot.display_name}</h2>
        )}
      </header>
      <div
        className={
          isMulti
            ? 'stage-region__body stage-workbench-slot__body'
            : isEmpty
              ? 'stage-region__body stage-workbench-slot__portal-body'
              : 'stage-workbench-slot__portal-body'
        }
        ref={registerBody}
      >
        {/* Only ever React children *or* `StagePage.tsx`'s appended panel host, never both: the
            two placeholders below render exactly when no panel is visible here, which is exactly
            when no host is appended into this container. */}
        {isEmpty ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            No panels are available in this slot yet.
          </p>
        ) : showsNothing ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            No panel is shown here. Use this slot's header menu to choose one of the panels
            assigned to it.
          </p>
        ) : null}
      </div>
    </section>
  )
}
