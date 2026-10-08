import { useCallback, useMemo } from 'react'
import Popover from '../stage/Popover'
import { PANEL_REGISTRY, panelDisplayName } from './panelRegistry'
import { frameForSlot } from './slotEligibility'
import { frameLeaves } from './slotMatcher'
import type { LayoutSlotDefinition } from './types'

// The class each frame sub-slot is drawn with. `identity` and `frame_actions` are filled by the
// slot, `help` and `controls` by the hosted panel through `BarElement`. Written out as literals so
// the REQ-037 selector check (C08) finds them.
const SUB_SLOT_CLASS: Record<string, string> = {
  identity: 'stage-slot__identity',
  help: 'stage-slot__help',
  controls: 'stage-slot__controls',
  frame_actions: 'stage-slot__frame-actions',
}
const ARRANGEMENT_CLASS: Record<string, string> = {
  stacked: 'stage-slot--stacked',
  inline: 'stage-slot--inline',
}

/**
 * One layout slot, drawn from its role's frame schema (ADR-031 decisions 1 and 2, REQ-011 R13):
 * exactly one top bar and one body. The bar is built from the frame in `slot-schemas.json`, so
 * the slot draws it and a hosted panel cannot draw a second one. A panel supplies only the
 * elements the frame has places for (`BarElement`), which `StagePage.tsx` portals into the
 * sub-slots registered here with `registerSubSlot`.
 *
 * `visiblePanelId` arrives already fully resolved by `useWorkbenchLayouts`'s `getSlotPanel` — the
 * one resolver, which accounts for the stored choice, the deliberate "nothing visible" state, the
 * secondary slot's platform-conditional default, the layout file's default and whether a panel type
 * is implemented yet. This file never re-resolves it.
 *
 * The `identity` sub-slot has exactly two shapes (a frame without one, such as the strip's, has
 * neither):
 *
 * - **Plain text** naming the hosted panel (or, when no panel is implemented here, the slot):
 *   there is nothing to choose, because the slot has no implemented panel assigned to it at all or
 *   has exactly one and that one is showing. REQ-007 W16/W17: "a slot with one assigned panel
 *   renders a plain header."
 * - **A switcher dropdown** — the current panel's name beside a small downward triangle, opening a
 *   list of the slot's other assigned panels — when the slot holds more than one implemented panel,
 *   or when it currently shows nothing but still holds at least one. That second case is the way
 *   back from the "nothing visible" state a reassignment can leave behind (`NO_VISIBLE_PANEL` in
 *   `useWorkbenchLayouts.ts`): a slot showing nothing must offer a way to show something, even
 *   when only one panel remains assigned to it, or that panel would be reachable only through the
 *   configuration dialog.
 *
 * The dropdown is a *visibility switcher only*, never a reassignment (REQ-007 W16/W17): it lists
 * exactly the panels currently assigned here (`slot.admits`, whatever the configuration dialog's
 * per-panel assignment places in this slot) and only ever calls `onSelectPanel` (`setSlotPanel`).
 * Moving a panel to a *different* slot is the assignment-only configuration dialog's job
 * (`LayoutConfigDialog.tsx`, "one selector per panel over the slots it is eligible for").
 *
 * REQ-007 W17 item 4: the resolved panel's component is not rendered in this file's own JSX tree.
 * This slot renders a stable body container `<div>` (registered with `StagePage.tsx` via
 * `registerBody`), and `StagePage.tsx` appends the visible panel's own persistent host element into
 * it. Every branch below returns the *same* root shape — `<section>`, then the one `<header>`,
 * then that body `<div>` — regardless of how many panels are assigned or whether one is showing,
 * varying only their *contents*. That uniformity is load-bearing, not tidiness: React cannot reuse
 * a DOM node across a change of returned root element type, so a reassignment that changed a slot's
 * panel count across the 1 <-> (0 or >1) boundary used to tear this whole subtree down and rebuild
 * it — taking the registered body container, and any panel mounted inside it, with it (verified
 * live in W09 fix cycle 1: a reassignment closed the moved terminal's websocket and opened a brand
 * new one). An ordinary prop/children update reconciles in place instead, so the body `<div>` is
 * the same DOM node across every 0/1/>1 transition.
 */
export default function Slot({
  slot,
  visiblePanelId,
  onSelectPanel,
  registerBody,
  registerSubSlot,
}: {
  slot: LayoutSlotDefinition
  visiblePanelId: string | null
  onSelectPanel: (panelId: string) => void
  registerBody: (slotId: string, element: HTMLDivElement | null) => void
  registerSubSlot: (slotId: string, subSlotId: string, element: HTMLElement | null) => void
}) {
  // Stable per slot id, so React never sees this body's ref change identity across renders (see
  // StagePage's comment above `registerSlotBody`).
  const slotId = slot.slot_id
  const bodyRef = useCallback(
    (element: HTMLDivElement | null) => registerBody(slotId, element),
    [registerBody, slotId],
  )

  const frame = frameForSlot(slotId)
  // The top bar's sub-slots in declaration order. The body is not one of them: it is drawn below.
  const barSubSlots = useMemo(
    () => (frame ? frameLeaves(frame).filter((leaf) => leaf.holds !== 'body') : []),
    [frame],
  )
  // One stable ref callback per panel-filled sub-slot, for the same reason as `bodyRef`.
  const subSlotRefs = useMemo(
    () =>
      Object.fromEntries(
        barSubSlots
          .filter((leaf) => leaf.filled_by === 'panel')
          .map((leaf) => [
            leaf.id,
            (element: HTMLElement | null) => registerSubSlot(slotId, leaf.id, element),
          ]),
      ),
    [barSubSlots, registerSubSlot, slotId],
  )

  const implementedAdmits = slot.admits.filter((id) => PANEL_REGISTRY[id]?.Component)
  const isEmpty = implementedAdmits.length === 0
  const isMulti = implementedAdmits.length > 1
  const showsNothing = !isEmpty && visiblePanelId === null
  const hasSwitcher = isMulti || showsNothing
  const otherPanelIds = implementedAdmits.filter((id) => id !== visiblePanelId)
  const identityLabel = visiblePanelId ? panelDisplayName(visiblePanelId) : slot.display_name

  const identity = hasSwitcher ? (
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
    // Nothing to switch to — a slot with no implemented panel, or with exactly one and that one
    // already showing — so the identity just names it.
    <h2>{identityLabel}</h2>
  )

  return (
    <section
      className={
        'stage-region stage-slot ' +
        (ARRANGEMENT_CLASS[frame?.arrangement ?? 'stacked'] ?? ARRANGEMENT_CLASS.stacked) +
        (isEmpty ? ' stage-workbench-slot--empty' : '')
      }
      aria-label={slot.display_name}
      data-slot-role={slotId}
    >
      <header className="stage-region__header stage-slot__bar">
        {frame === null ? (
          <div className={SUB_SLOT_CLASS.identity}>{identity}</div>
        ) : (
          barSubSlots.map((leaf) => (
            <div
              key={leaf.id}
              className={SUB_SLOT_CLASS[leaf.id] ?? 'stage-slot__sub-slot'}
              data-sub-slot={leaf.id}
              ref={subSlotRefs[leaf.id]}
            >
              {leaf.id === 'identity' ? identity : null}
            </div>
          ))
        )}
      </header>
      <div
        className={
          isEmpty || showsNothing
            ? 'stage-region__body stage-workbench-slot__portal-body'
            : 'stage-workbench-slot__portal-body'
        }
        ref={bodyRef}
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
