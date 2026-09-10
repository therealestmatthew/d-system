import { useState, type ReactNode } from 'react'

/**
 * A hover-triggered popup. Opens on pointer enter (or keyboard focus, for accessibility
 * parity), and collapses the instant the pointer leaves the trigger+bubble region or focus
 * moves away — REQ-006 R03: "Hover-triggered popups collapse when the pointer leaves them."
 */
export default function Tooltip({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  const [open, setOpen] = useState(false)

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
        className="stage-tooltip__trigger"
        aria-label={label}
        aria-expanded={open}
      >
        ?
      </button>
      {open ? (
        <span role="tooltip" className="stage-tooltip__bubble">
          {children}
        </span>
      ) : null}
    </span>
  )
}
