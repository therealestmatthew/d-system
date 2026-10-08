import { useContext, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { SlotFrameContext } from './slotFrameContext'
import { subSlotFor } from './slotMatcher'

/** The bar element types a panel may supply (`element_types.bar` in `slot-schemas.json`). */
export type BarElementType = 'help' | 'action' | 'choice' | 'toggle' | 'status'

/**
 * The typed wrapper a panel puts around each control it wants in its slot's top bar (ADR-031
 * decision 1, REQ-011 R13). A panel never draws a top bar. It declares its element types in
 * `_data/workbench/panel-elements.json` and renders each element inside a `BarElement`, which
 * places the children into the sub-slot of the hosting slot's frame that admits the type. The
 * children stay in the panel's React tree, so a refresh button still sees the viewer's active tab.
 *
 * - A type the hosting slot's frame has no place for throws while rendering, which the panel's own
 *   error boundary shows in the slot. It is never dropped silently.
 * - Render every `BarElement` a panel has all the time and put any condition inside it:
 *   `<BarElement type="choice">{ready ? <Picker /> : null}</BarElement>`. Elements land in a
 *   sub-slot in the order they first mount, so one that appears late would land after the rest.
 * - `places` is how many places of the bar the children take, when the children are a group such as
 *   three dropdowns. It must match the number of entries the panel declares for them in
 *   `panel-elements.json`; the `declared bar elements` test in `BarElement.test.tsx` holds the two
 *   together.
 * - Outside any slot (a panel rendered on its own) the children are drawn in place.
 */
export default function BarElement({
  type,
  places = 1,
  children,
}: {
  type: BarElementType
  places?: number
  children: ReactNode
}) {
  const binding = useContext(SlotFrameContext)
  const marked = (
    <span className="stage-bar-element" data-bar-element={type} data-bar-places={places}>
      {children}
    </span>
  )
  if (binding === null) return marked
  const subSlotId = subSlotFor(binding.frame, type)
  if (subSlotId === null) {
    throw new Error(`the ${binding.role} slot's top bar has no place for a ${type} element`)
  }
  const target = binding.subSlotElement(subSlotId)
  return target === null ? null : createPortal(marked, target)
}
