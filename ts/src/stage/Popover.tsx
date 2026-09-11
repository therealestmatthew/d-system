import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react'
import { createPortal } from 'react-dom'

// Kept clear between the bubble and the viewport edge when clamping its position/size.
const VIEWPORT_MARGIN = 8
// Mirrors the 16rem width the bubble used to carry in CSS, converted to px for the clamp math
// below (the trigger's layout is unaffected by the page's root font size in this app).
const BUBBLE_WIDTH_PX = 256
const MIN_BUBBLE_HEIGHT_PX = 120

/**
 * A click-triggered popup. Opens on trigger click; dismissible three ways — REQ-006 R03:
 * "click-triggered popups are dismissible" — via its own close button, an Escape keypress, or
 * a click outside the popup.
 *
 * Rendered through a portal into document.body rather than inline: .stage-region and
 * .stage-region__body both set overflow: hidden (REQ-006 R02's reveal-in-place contract for the
 * rest of the stage), and an inline-positioned bubble grown upward from the trigger was clipped
 * by those ancestors — including its own dismiss control, which rendered outside the viewport
 * entirely. Portaling escapes that clipping; `reposition()` then anchors the bubble to the
 * trigger's live getBoundingClientRect() and clamps it to the viewport on every open, resize and
 * scroll, so the whole bubble — dismiss control included — always lands on-screen.
 */
export default function Popover({
  triggerLabel,
  title,
  children,
  width = BUBBLE_WIDTH_PX,
}: {
  triggerLabel: string
  title: string
  // Most callers (e.g. NotesStripRegion's controls menu) pass static content. Callers that
  // need a confirm action inside the bubble (R11's guarded drop / guarded tab close) pass a
  // function instead, so they can close the popover themselves once the confirmed action has
  // run, without Popover exposing its internal `open` state as a wider API.
  children: ReactNode | ((close: () => void) => ReactNode)
  // Overrides the bubble's default width in px — the layout-configuration surface
  // (`LayoutConfigDialog`, `phase-wb-02`) needs more room than the default list/confirm bubbles.
  width?: number
}) {
  const [open, setOpen] = useState(false)
  const [style, setStyle] = useState<CSSProperties>({})
  const containerRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const bubbleRef = useRef<HTMLDivElement>(null)

  const reposition = () => {
    const trigger = triggerRef.current
    if (!trigger) return
    const rect = trigger.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    const clampedWidth = Math.min(width, viewportWidth - VIEWPORT_MARGIN * 2)
    let left = rect.left
    if (left + clampedWidth > viewportWidth - VIEWPORT_MARGIN) {
      left = viewportWidth - VIEWPORT_MARGIN - clampedWidth
    }
    left = Math.max(VIEWPORT_MARGIN, left)

    const spaceAbove = rect.top - VIEWPORT_MARGIN
    const spaceBelow = viewportHeight - rect.bottom - VIEWPORT_MARGIN
    // Prefer opening upward (matches the trigger's usual position near the bottom of its
    // region) unless there isn't even the minimum usable height above and downward has more
    // room to offer.
    const openUpward = spaceAbove >= MIN_BUBBLE_HEIGHT_PX || spaceAbove >= spaceBelow

    const available = openUpward ? spaceAbove : spaceBelow
    const maxHeight = Math.max(MIN_BUBBLE_HEIGHT_PX, Math.min(available, viewportHeight * 0.6))

    const next: CSSProperties = {
      left,
      width: clampedWidth,
      maxHeight,
    }
    if (openUpward) {
      next.bottom = viewportHeight - rect.top + VIEWPORT_MARGIN
    } else {
      next.top = rect.bottom + VIEWPORT_MARGIN
    }
    setStyle(next)
  }

  useLayoutEffect(() => {
    if (!open) return
    reposition()
    window.addEventListener('resize', reposition)
    window.addEventListener('scroll', reposition, true)
    return () => {
      window.removeEventListener('resize', reposition)
      window.removeEventListener('scroll', reposition, true)
    }
  }, [open])

  useEffect(() => {
    if (!open) return

    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node
      // The bubble is portaled to document.body, so it sits outside containerRef's DOM subtree
      // and needs its own containment check to avoid being treated as an "outside" click.
      if (containerRef.current?.contains(target)) return
      if (bubbleRef.current?.contains(target)) return
      setOpen(false)
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open])

  return (
    <div className="stage-popover" ref={containerRef}>
      <button
        type="button"
        ref={triggerRef}
        className="stage-popover__trigger"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {triggerLabel}
      </button>
      {open
        ? createPortal(
            <div
              role="dialog"
              aria-label={title}
              className="stage-popover__bubble"
              ref={bubbleRef}
              style={style}
            >
              <div className="stage-popover__header">
                <span className="stage-popover__title">{title}</span>
                <button
                  type="button"
                  className="stage-popover__dismiss"
                  aria-label={`Dismiss ${title}`}
                  onClick={() => setOpen(false)}
                >
                  ×
                </button>
              </div>
              <div className="stage-popover__body">
                {typeof children === 'function' ? children(() => setOpen(false)) : children}
              </div>
            </div>,
            document.body,
          )
        : null}
    </div>
  )
}
