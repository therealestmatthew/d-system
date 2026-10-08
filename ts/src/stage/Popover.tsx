import {
  useCallback,
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
// The smallest bubble worth opening when the room allows it. It is a lower bound on the bubble's
// height only up to the room the chosen side actually has: a floor larger than that room pushed the
// bubble off the viewport edge (idea 000117), so `choosePlacement` never returns more than the room.
const MIN_BUBBLE_HEIGHT_PX = 120
// The largest share of the viewport height a bubble may take.
const MAX_BUBBLE_VIEWPORT_FRACTION = 0.6

export interface PlacementInput {
  // Free viewport height above the trigger and below it, each already net of the viewport margin.
  spaceAbove: number
  spaceBelow: number
  viewportHeight: number
  // The bubble's height with no limit applied (header plus the body's full scroll height), or
  // undefined/0 when it could not be measured.
  naturalHeight?: number
  // When set, the side is kept and only the height is worked out. Used while the bubble stays open
  // and its content changes, so typing a filter does not move the bubble across the trigger.
  keepSide?: 'above' | 'below'
}

export interface Placement {
  openUpward: boolean
  maxHeight: number
}

/**
 * Chooses the side a bubble opens toward and the height it may take (idea 000108, REQ-012 R25).
 *
 * The side is chosen from the room each side has for the bubble, not from a fixed threshold: the
 * upward side is kept when the whole content fits there (the trigger's usual position is near the
 * bottom of its region), then the downward side when the content fits there, and otherwise the side
 * with more room. The height is the room on the chosen side, capped at 60% of the viewport, and is
 * never more than that room, so the bubble and its dismiss control stay inside the viewport.
 */
// Exported for Popover.test.tsx. A separate module would keep the component file components-only, but
// the phase's deliverables name no such file.
// eslint-disable-next-line react-refresh/only-export-components
export function choosePlacement({
  spaceAbove,
  spaceBelow,
  viewportHeight,
  naturalHeight,
  keepSide,
}: PlacementInput): Placement {
  const above = Math.max(0, spaceAbove)
  const below = Math.max(0, spaceBelow)
  const cap = viewportHeight * MAX_BUBBLE_VIEWPORT_FRACTION
  let openUpward: boolean
  if (keepSide) {
    openUpward = keepSide === 'above'
  } else if (naturalHeight !== undefined && naturalHeight > 0) {
    const fitsAbove = naturalHeight <= Math.min(above, cap)
    const fitsBelow = naturalHeight <= Math.min(below, cap)
    openUpward = fitsAbove || (!fitsBelow && above >= below)
  } else {
    openUpward = above >= below
  }
  const room = openUpward ? above : below
  const limit = Math.min(room, cap)
  return { openUpward, maxHeight: Math.max(Math.min(MIN_BUBBLE_HEIGHT_PX, room), limit) }
}

// The bubble's height with no maxHeight applied, at the width it will have. Measured on the live
// element (its inline size is restored straight after, because React skips a style property whose
// value it believes unchanged). Lifting maxHeight lets the browser clamp the body's scrollTop, so
// that is saved and put back too. Returns undefined before the bubble has rendered. It forces a
// layout, so it runs on open, resize and content change only, never on a scroll.
function measureNaturalHeight(bubble: HTMLDivElement | null, width: number): number | undefined {
  if (!bubble) return undefined
  const body = bubble.querySelector<HTMLElement>('.stage-popover__body')
  const scrollTop = body?.scrollTop ?? 0
  const { maxHeight, width: previousWidth } = bubble.style
  bubble.style.maxHeight = 'none'
  bubble.style.width = `${width}px`
  const natural = bubble.offsetHeight
  bubble.style.maxHeight = maxHeight
  bubble.style.width = previousWidth
  if (body && body.scrollTop !== scrollTop) body.scrollTop = scrollTop
  return natural
}

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
  triggerAriaLabel,
  title,
  children,
  width = BUBBLE_WIDTH_PX,
  disabled = false,
  onOpenChange,
}: {
  triggerLabel: string
  // Accessible name for the trigger when `triggerLabel`'s visible text is not descriptive on its
  // own (e.g. the terminal panel's "..." ellipsis menu, REQ-007 W02) — falls back to the trigger's
  // own text content (`triggerLabel`) when omitted, matching every existing caller's behavior.
  triggerAriaLabel?: string
  title: string
  // Most callers (e.g. NotesStripRegion's controls menu) pass static content. Callers that
  // need a confirm action inside the bubble (R11's guarded drop / guarded tab close) pass a
  // function instead, so they can close the popover themselves once the confirmed action has
  // run, without Popover exposing its internal `open` state as a wider API.
  children: ReactNode | ((close: () => void) => ReactNode)
  // Overrides the bubble's default width in px — the layout-configuration surface
  // (`LayoutConfigDialog`, `phase-wb-02`) needs more room than the default list/confirm bubbles.
  width?: number
  // REQ-007 W03: while true, the trigger renders with a real `disabled` attribute — grayed out
  // and genuinely unclickable, not just styled — and any already-open bubble is force-closed.
  // Reactivates the instant the caller flips this back to false (e.g. terminal restore).
  disabled?: boolean
  // Fires whenever `open` changes, including the force-close triggered by `disabled` flipping to
  // true. Lets a caller that keeps its own state inside the bubble (the terminal menu's
  // in-progress drop confirmation) reset that state whenever the bubble closes without it having
  // run — so reopening the menu never resurfaces a stale confirmation from an abandoned attempt.
  onOpenChange?: (open: boolean) => void
}) {
  const [open, setOpen] = useState(false)
  const [style, setStyle] = useState<CSSProperties>({})
  const containerRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const bubbleRef = useRef<HTMLDivElement>(null)

  // The content height measured at the last open, resize or content change; a scroll reuses it.
  const naturalRef = useRef<number | undefined>(undefined)

  // The side chosen at open or resize, kept while the content changes.
  const sideRef = useRef<'above' | 'below' | undefined>(undefined)

  // 'open' (open and resize): measure the content and choose the side. 'content' (the body's
  // content changed): measure again but keep the side. 'move' (the trigger moved on a page scroll):
  // reuse the last measurement and choose the side again.
  const reposition = useCallback((mode: 'open' | 'content' | 'move') => {
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

    if (mode !== 'move') naturalRef.current = measureNaturalHeight(bubbleRef.current, clampedWidth)
    const { openUpward, maxHeight } = choosePlacement({
      // The bubble sits VIEWPORT_MARGIN from the trigger and keeps VIEWPORT_MARGIN from the
      // viewport edge, so each side loses the margin twice.
      spaceAbove: rect.top - 2 * VIEWPORT_MARGIN,
      spaceBelow: viewportHeight - rect.bottom - 2 * VIEWPORT_MARGIN,
      viewportHeight,
      naturalHeight: naturalRef.current,
      keepSide: mode === 'content' ? sideRef.current : undefined,
    })
    sideRef.current = openUpward ? 'above' : 'below'

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
  }, [width])

  // The latest `onOpenChange`, so the effect below fires only when `open` changes, never because a
  // caller passed a new inline callback on its own re-render.
  const onOpenChangeRef = useRef(onOpenChange)
  useEffect(() => {
    onOpenChangeRef.current = onOpenChange
  })

  useEffect(() => {
    onOpenChangeRef.current?.(open)
  }, [open])

  // Force-close whenever the caller disables the trigger — a bubble left open while its trigger
  // goes disabled (e.g. mid-drop) would be reachable only via Escape/outside-click, not via the
  // now-disabled trigger button, and REQ-007 W03 wants deactivation to be immediate and total.
  // Adjusted during render rather than in an effect, so the bubble never commits open while
  // disabled.
  if (disabled && open) setOpen(false)

  useLayoutEffect(() => {
    if (!open) return
    naturalRef.current = undefined
    sideRef.current = undefined
    reposition('open')
    const onResize = () => reposition('open')
    // Capture phase, so it also sees scrolls of the page's inner scrollers that move the trigger.
    // A scroll inside the bubble (the body's own list) moves nothing and must not touch layout:
    // remeasuring there reset the body's scrollTop to 0.
    const onScroll = (event: Event) => {
      if (bubbleRef.current?.contains(event.target as Node)) return
      reposition('move')
    }
    window.addEventListener('resize', onResize)
    window.addEventListener('scroll', onScroll, true)
    // The content can change after open (a list that finishes loading, a filter typed): size the
    // bubble for what it holds now, not for what it held when it opened.
    const body = bubbleRef.current?.querySelector('.stage-popover__body')
    const observer = body ? new MutationObserver(() => reposition('content')) : null
    if (body) observer?.observe(body, { childList: true, subtree: true, characterData: true })
    return () => {
      window.removeEventListener('resize', onResize)
      window.removeEventListener('scroll', onScroll, true)
      observer?.disconnect()
    }
  }, [open, reposition])

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
        className={'stage-popover__trigger' + (disabled ? ' stage-popover__trigger--disabled' : '')}
        aria-expanded={open}
        aria-label={triggerAriaLabel}
        disabled={disabled}
        onClick={() => {
          if (disabled) return
          setOpen((value) => !value)
        }}
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
