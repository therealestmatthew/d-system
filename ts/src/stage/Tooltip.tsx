import {
  useCallback,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react'
import { createPortal } from 'react-dom'
import { choosePlacement } from './Popover'

// Kept clear between the bubble and the viewport edge, and between the bubble and its trigger.
const VIEWPORT_MARGIN = 8

/**
 * A hover-triggered popup. Opens on pointer enter (or keyboard focus, for accessibility
 * parity), and collapses the instant the pointer leaves the trigger+bubble region or focus
 * moves away — REQ-006 R03: "Hover-triggered popups collapse when the pointer leaves them."
 *
 * Rendered through a portal into document.body, for the reason `Popover` is: `.stage-region`
 * sets overflow: hidden (REQ-006 R02's reveal-in-place contract), and a bubble positioned inside
 * it was cut off by a region only a few lines high — the notes strip (idea 000130, REQ-012 R27).
 * `reposition()` anchors the bubble to the trigger's live bounding box and clamps it to the
 * viewport on open, resize and scroll, choosing the side with `Popover`'s `choosePlacement`.
 *
 * The portaled bubble stays inside the trigger's React tree, and React computes mouseenter and
 * mouseleave over that tree, so moving from the trigger onto the bubble does not collapse it.
 */
export default function Tooltip({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  const [open, setOpen] = useState(false)
  const [style, setStyle] = useState<CSSProperties>({})
  const triggerRef = useRef<HTMLButtonElement>(null)
  const bubbleRef = useRef<HTMLSpanElement>(null)

  const reposition = useCallback(() => {
    const trigger = triggerRef.current
    const bubble = bubbleRef.current
    if (!trigger || !bubble) return
    const rect = trigger.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    // The bubble's width comes from its CSS (15rem, at most 40vw); only the height is limited
    // here. Measured with maxHeight lifted so the natural height is what the placement sees.
    const { maxHeight: previousMaxHeight } = bubble.style
    bubble.style.maxHeight = 'none'
    const width = bubble.offsetWidth
    const naturalHeight = bubble.offsetHeight
    bubble.style.maxHeight = previousMaxHeight

    const left = Math.max(
      VIEWPORT_MARGIN,
      Math.min(rect.left, viewportWidth - VIEWPORT_MARGIN - width),
    )
    const { openUpward, maxHeight } = choosePlacement({
      // The bubble sits VIEWPORT_MARGIN from the trigger and keeps VIEWPORT_MARGIN from the
      // viewport edge, so each side loses the margin twice.
      spaceAbove: rect.top - 2 * VIEWPORT_MARGIN,
      spaceBelow: viewportHeight - rect.bottom - 2 * VIEWPORT_MARGIN,
      viewportHeight,
      naturalHeight,
    })
    const next: CSSProperties = { left, maxHeight }
    if (openUpward) {
      next.bottom = viewportHeight - rect.top + VIEWPORT_MARGIN
    } else {
      next.top = rect.bottom + VIEWPORT_MARGIN
    }
    setStyle(next)
  }, [])

  useLayoutEffect(() => {
    if (!open) return
    reposition()
    window.addEventListener('resize', reposition)
    // Capture phase, so it also sees scrolls of inner scrollers that move the trigger.
    window.addEventListener('scroll', reposition, true)
    return () => {
      window.removeEventListener('resize', reposition)
      window.removeEventListener('scroll', reposition, true)
    }
  }, [open, reposition])

  return (
    <span
      className="stage-tooltip"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <button
        type="button"
        ref={triggerRef}
        className="stage-tooltip__trigger"
        aria-label={label}
        aria-expanded={open}
      >
        ?
      </button>
      {open
        ? createPortal(
            <span role="tooltip" className="stage-tooltip__bubble" ref={bubbleRef} style={style}>
              {children}
            </span>,
            document.body,
          )
        : null}
    </span>
  )
}
