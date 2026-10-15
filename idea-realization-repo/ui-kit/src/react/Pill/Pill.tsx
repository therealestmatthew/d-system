import type { ReactNode } from 'react'

export type PillStatus = 'ok' | 'warn' | 'info' | 'err' | 'neutral' | 'ai'

export interface PillProps {
  status: PillStatus
  /** The status in words. Colour is never the only carrier. */
  children: ReactNode
  /** Show the leading dot (default true). */
  dot?: boolean
}

export function Pill({ status, children, dot = true }: PillProps) {
  return (
    <span className="ui-pill" data-status={status}>
      {dot && <span className="ui-pill__dot" aria-hidden="true" />}
      {children}
    </span>
  )
}

export interface BadgeProps {
  count: number
  /** Accessible wording for the count, e.g. "3 unread". Defaults to the number. */
  label?: string
}

export function Badge({ count, label }: BadgeProps) {
  return (
    <span className="ui-badge" aria-label={label}>
      {count}
    </span>
  )
}

export interface ChipProps {
  /** The filter text, e.g. "status: open". */
  label: string
  /** When given, the chip is removable through a button labelled "Remove filter: <label>". */
  onRemove?: () => void
}

export function Chip({ label, onRemove }: ChipProps) {
  return (
    <span className="ui-chip">
      <span className="ui-chip__label">{label}</span>
      {onRemove && (
        <button type="button" className="ui-chip__remove" aria-label={`Remove filter: ${label}`} onClick={onRemove}>
          <span aria-hidden="true">×</span>
        </button>
      )}
    </span>
  )
}
