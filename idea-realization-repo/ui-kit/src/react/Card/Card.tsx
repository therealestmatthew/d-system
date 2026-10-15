import type { ReactNode } from 'react'
import { cx } from '../cx'

export type CardVariant = 'neutral' | 'accent' | 'ai'
type HeadingLevel = 2 | 3 | 4

export interface CardProps {
  title?: ReactNode
  kicker?: ReactNode
  meta?: ReactNode
  actions?: ReactNode
  children?: ReactNode
  variant?: CardVariant
  /** Heading level of the title (default 3). */
  headingLevel?: HeadingLevel
}

export function Card({ title, kicker, meta, actions, children, variant = 'neutral', headingLevel = 3 }: CardProps) {
  const Heading = `h${headingLevel}` as const
  return (
    <article className={cx('ui-card', variant !== 'neutral' && `ui-card--${variant}`)}>
      {kicker !== undefined && <p className="ui-card__kicker">{kicker}</p>}
      {title !== undefined && <Heading className="ui-card__title">{title}</Heading>}
      {children !== undefined && <div className="ui-card__body">{children}</div>}
      {meta !== undefined && <p className="ui-card__meta">{meta}</p>}
      {actions !== undefined && <div className="ui-card__actions">{actions}</div>}
    </article>
  )
}

export interface StatCardProps {
  /** What the number is. */
  label: ReactNode
  /** The computed value; `null` or `undefined` renders "Not recorded", never a made-up zero. */
  value: ReactNode | null | undefined
  delta?: ReactNode
  /** Source and time of the number (principle 14). */
  meta?: ReactNode
  headingLevel?: HeadingLevel
}

export function StatCard({ label, value, delta, meta, headingLevel = 3 }: StatCardProps) {
  const Heading = `h${headingLevel}` as const
  const recorded = value !== null && value !== undefined
  return (
    <article className="ui-card ui-card--stat">
      <Heading className="ui-card__title">{label}</Heading>
      <p className="ui-card__value" data-state={recorded ? undefined : 'not-recorded'}>
        {recorded ? value : 'Not recorded'}
      </p>
      {delta !== undefined && <p className="ui-card__delta">{delta}</p>}
      {meta !== undefined && <p className="ui-card__meta">{meta}</p>}
    </article>
  )
}

export function CardGrid({ children }: { children: ReactNode }) {
  return <div className="ui-card-grid">{children}</div>
}
