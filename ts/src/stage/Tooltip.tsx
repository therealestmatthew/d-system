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
 * mouseleave over that tree. The bubble sits VIEWPORT_MARGIN from the trigger, and a pointer
 * crossing that gap would leave both, so the bubble is wrapped in a transparent bridge element that
 * touches the trigger and spans the gap (padding, in CSS). The pointer can therefore reach the
 * bubble, which matters when it is short of room and scrolls.
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
  const [bubbleStyle, setBubbleStyle] = useState<CSSProperties>({})
  const bridgeRef = useRef<HTMLSpanElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const bubbleRef = useRef<HTMLSpanElement>(null)
  // The side chosen at the last placement, for the bridge's padding.
  const [openUpward, setOpenUpward] = useState(false)

  const reposition = useCallback(() => {
    const trigger = triggerRef.current
    const bubble = bubbleRef.current
    if (!trigger || !bubble) return
    const rect = trigger.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    // The bubble's width comes from its CSS (15rem, at most 40vw); only the height is limited
    // here. Measured with maxHeight lifted so the natural height is what the placement sees.
    // Lifting maxHeight lets the browser clamp scrollTop to 0, so it is saved and put back.
    const { maxHeight: previousMaxHeight } = bubble.style
    const scrollTop = bubble.scrollTop
    bubble.style.maxHeight = 'none'
    const width = bubble.offsetWidth
    const naturalHeight = bubble.offsetHeight
    bubble.style.maxHeight = previousMaxHeight
    if (bubble.scrollTop !== scrollTop) bubble.scrollTop = scrollTop

    const left = Math.max(
      VIEWPORT_MARGIN,
      Math.min(rect.left, viewportWidth - VIEWPORT_MARGIN - width),
    )
    const { openUpward: upward, maxHeight } = choosePlacement({
      // The bubble sits VIEWPORT_MARGIN from the trigger and keeps VIEWPORT_MARGIN from the
      // viewport edge, so each side loses the margin twice.
      spaceAbove: rect.top - 2 * VIEWPORT_MARGIN,
      spaceBelow: viewportHeight - rect.bottom - 2 * VIEWPORT_MARGIN,
      viewportHeight,
      naturalHeight,
    })
    // The outer bridge element touches the trigger and carries the VIEWPORT_MARGIN gap as its own
    // padding, so the visible bubble sits where it would with a plain gap.
    const next: CSSProperties = { left }
    if (upward) {
      next.bottom = viewportHeight - rect.top
    } else {
      next.top = rect.bottom
    }
    setStyle(next)
    setBubbleStyle({ maxHeight })
    setOpenUpward(upward)
  }, [])

  useLayoutEffect(() => {
    if (!open) return
    reposition()
    // Capture phase, so it also sees scrolls of inner scrollers that move the trigger. The
    // bubble's own scroll moves nothing and is ignored: placing again would reset its scrollTop.
    const onScroll = (event: Event) => {
      if (bridgeRef.current?.contains(event.target as Node)) return
      reposition()
    }
    window.addEventListener('resize', reposition)
    window.addEventListener('scroll', onScroll, true)
    return () => {
      window.removeEventListener('resize', reposition)
      window.removeEventListener('scroll', onScroll, true)
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
            <span
              className={'stage-tooltip__bridge' + (openUpward ? ' stage-tooltip__bridge--above' : '')}
              ref={bridgeRef}
              style={style}
            >
              <span role="tooltip" className="stage-tooltip__bubble" ref={bubbleRef} style={bubbleStyle}>
                {children}
              </span>
            </span>,
            document.body,
          )
        : null}
    </span>
  )
}
