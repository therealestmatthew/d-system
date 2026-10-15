import { useEffect, useState, type ReactNode } from 'react'

export type ViewState = 'empty' | 'loading' | 'error' | 'missing' | 'not-recorded'

export interface StateViewProps {
  state: ViewState
  /** Says what goes here / what failed / what is unavailable, in plain words. */
  title: ReactNode
  body?: ReactNode
  /** One next step, usually a Button (Retry for error, the primary action for empty). */
  action?: ReactNode
  /** Loading only: milliseconds before the spinner and text appear (default 150) to avoid a flash. */
  loadingDelayMs?: number
}

const ROLE: Partial<Record<ViewState, 'alert' | 'status'>> = { error: 'alert', loading: 'status' }

/** The named states of an asynchronous surface (ARCH-001 component 22). */
export function StateView({ state, title, body, action, loadingDelayMs = 150 }: StateViewProps) {
  const isLoading = state === 'loading'
  const [visible, setVisible] = useState(!isLoading || loadingDelayMs <= 0)

  useEffect(() => {
    if (!isLoading || loadingDelayMs <= 0) {
      setVisible(true)
      return
    }
    setVisible(false)
    const timer = setTimeout(() => setVisible(true), loadingDelayMs)
    return () => clearTimeout(timer)
  }, [isLoading, loadingDelayMs])

  return (
    <div className="ui-state" data-state={state} role={ROLE[state]}>
      {visible && (
        <>
          {isLoading && <span className="ui-spinner" aria-hidden="true" />}
          <p className="ui-state__title">{title}</p>
          {body !== undefined && <div className="ui-state__body">{body}</div>}
          {action !== undefined && <div className="ui-state__action">{action}</div>}
        </>
      )}
    </div>
  )
}
