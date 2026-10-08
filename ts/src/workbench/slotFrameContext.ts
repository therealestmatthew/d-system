import { createContext } from 'react'
import type { Frame } from './slotMatcher'

/**
 * What a hosted panel can see of the slot that currently holds it (ADR-031 decision 1). `StagePage`
 * provides one around each panel it portals into a slot, and replaces it when the panel is
 * reassigned, so the panel's bar elements follow it to the new slot without the panel remounting.
 */
export interface SlotFrameBinding {
  /** The hosting slot's role (its slot id). */
  role: string
  frame: Frame
  /** The DOM element of one of the frame's panel-filled sub-slots, or `null` before the slot has
   * mounted it. */
  subSlotElement: (subSlotId: string) => HTMLElement | null
}

/** `null` outside a slot: a panel rendered on its own (in a test, say) draws its bar elements in
 * place. */
export const SlotFrameContext = createContext<SlotFrameBinding | null>(null)
