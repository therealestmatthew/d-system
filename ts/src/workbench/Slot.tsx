import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import type { LayoutSlotDefinition } from './types'

/** The panel type id this slot should actually show: `resolvedPanelId` (from
 * `useWorkbenchLayouts`'s `getSlotPanel`) when it is both still admitted here and implemented
 * (`PANEL_REGISTRY[id].Component` non-null), else the first implemented panel `admits` lists,
 * else `null` when none of this slot's admitted panels are implemented yet (e.g. `explorer`
 * before `phase-wb-05`/`phase-wb-06` landed). Exported so `StagePage.tsx`'s portal-host
 * computation (REQ-007 W17 item 4, below) resolves the *same* panel id this file's own header
 * resolves, from the same inputs — one rule, not two copies that could drift apart. */
export function resolveImplementedPanel(
  admits: string[],
  resolvedPanelId: string | null,
): string | null {
  const implementedAdmits = admits.filter((id) => PANEL_REGISTRY[id]?.Component)
  if (implementedAdmits.length === 0) return null
  return resolvedPanelId && implementedAdmits.includes(resolvedPanelId)
    ? resolvedPanelId
    : implementedAdmits[0]
}

/**
 * One layout slot's chrome (REQ-007 W05/W06/W16/W17):
 *
 * - Zero implemented panels admitted (e.g. `explorer` before phase-wb-05/06 land): a plain header
 *   naming the slot and a clear in-page placeholder — the same "say so in place" posture ADR-013
 *   applies to the absent terminal route, generalized to an absent panel.
 * - Exactly one implemented panel admitted: a plain header, satisfied entirely by that panel's
 *   own `.stage-region` (every panel this engine hosts already renders one) — this component
 *   renders no header markup of its own in that case, only the portal body container below.
 * - More than one implemented panel admitted (the terminal slot, since `phase-wb-03`'s CMD and
 *   PowerShell shell options landed, and layout 1's explorer slot, since `phase-wb-06`'s
 *   `idea-explorer` joined `phase-wb-05`'s `file-browser`): a slot-level header shows the current
 *   panel's name beside a small downward-triangle dropdown listing the *other panels currently
 *   assigned to this slot* — REQ-007 W16/W17: this dropdown is a visibility switcher only, never
 *   a reassignment; it lists exactly `slot.admits` (whatever the configuration dialog's per-panel
 *   assignment currently places here) and only ever calls `onSelectPanel` (`setSlotPanel`), which
 *   changes which of those is shown, never which slot a panel belongs to. Moving a panel to a
 *   *different* slot is the assignment-only configuration dialog's job now
 *   (`LayoutConfigDialog.tsx`, "one selector per panel over its eligible slots"). The swapped-in
 *   panel still renders its own inner header too — a double-header cosmetic case left as-is,
 *   noted in `panelRegistry.tsx`.
 *
 * REQ-007 W17 item 4: the resolved panel's component is no longer rendered inline in this file's
 * own JSX tree. Instead, this slot renders a stable body container `<div>` (registered with
 * `StagePage.tsx` via `registerBody`) that `StagePage.tsx` portals the resolved panel's component
 * into, keyed by *panel id* rather than by this slot. That is what lets a panel reassigned to a
 * different slot (via the configuration dialog) keep its component instance — and so a live
 * terminal session — mounted instead of unmounting here and remounting fresh over there: the
 * portal's target container changes, but the React element at that keyed position does not, so
 * the underlying component is never torn down. This `Slot` instance itself (and so this container
 * div) never remounts across a layout switch either, for the same reason `StagePage.tsx` already
 * relied on before this delta: both shipped layout files declare the identical four slot ids, so
 * `StagePage.tsx`'s one grid keeps rendering the same slot-keyed `<div>` regardless of which
 * layout is active.
 */
export default function Slot({
  slot,
  resolvedPanelId,
  onSelectPanel,
  registerBody,
}: {
  slot: LayoutSlotDefinition
  resolvedPanelId: string | null
  onSelectPanel: (panelId: string) => void
  registerBody: (element: HTMLDivElement | null) => void
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

  const currentPanelId = resolveImplementedPanel(slot.admits, resolvedPanelId) ?? implementedAdmits[0]

  if (implementedAdmits.length === 1) {
    // No extra chrome here — the portaled panel's own `.stage-region` is what renders the "plain
    // header" REQ-007 W06 calls for. This container is a transparent flex pass-through (see
    // `.stage-workbench-slot__portal-body` in `StagePage.css`), sized identically to the plain
    // `<Component />` this branch rendered directly before the W17 portal delta.
    return <div className="stage-workbench-slot__portal-body" ref={registerBody} />
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
      <div className="stage-region__body stage-workbench-slot__body" ref={registerBody} />
    </section>
  )
}
