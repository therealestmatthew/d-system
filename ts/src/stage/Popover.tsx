import { useEffect, useRef, useState, type ReactNode } from 'react'

/**
 * A click-triggered popup. Opens on trigger click; dismissible three ways — REQ-006 R03:
 * "click-triggered popups are dismissible" — via its own close button, an Escape keypress, or
 * a click outside the popup.
 */
export default function Popover({
  triggerLabel,
  title,
  children,
}: {
  triggerLabel: string
  title: string
  children: ReactNode
}) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return

    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
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
        className="stage-popover__trigger"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {triggerLabel}
      </button>
      {open ? (
        <div role="dialog" aria-label={title} className="stage-popover__bubble">
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
          <div className="stage-popover__body">{children}</div>
        </div>
      ) : null}
    </div>
  )
}
