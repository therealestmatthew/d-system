import { useCallback, useId, useState, type KeyboardEvent, type ReactNode } from 'react'
import { Toolbar } from 'react-aria-components'
import { Button, ToggleButton } from '../Button/Button'
import { PanelErrorBoundary } from './PanelErrorBoundary'

export type PanelBodyKind = 'document' | 'tree' | 'table' | 'stream' | 'form' | 'terminal' | 'ticker' | 'chart'
export type PanelVariant = 'standard' | 'compact'

export interface PanelProps {
  /** The panel's name; labels the section. */
  title: string
  /** Help content, e.g. a toggletip trigger. */
  help?: ReactNode
  /** Panel controls, placed in a role=toolbar with arrow-key roving focus. */
  controls?: ReactNode
  variant?: PanelVariant
  body: PanelBodyKind
  /** Offer the maximize toggle (default true). */
  maximizable?: boolean
  /** Offer the collapse toggle (default true). */
  collapsible?: boolean
  children: ReactNode
}

const MAXIMIZE_ICON = '⤢'
const COLLAPSE_ICON = '▾'

/**
 * The container for any content in a region (ARCH-001 component 2). Maximized and collapsed are
 * transient React state, never persisted. Toggling them changes attributes only: the body element
 * stays in place, so its children are never remounted and keep their state.
 */
export function Panel({
  title,
  help,
  controls,
  variant = 'standard',
  body,
  maximizable = true,
  collapsible = true,
  children,
}: PanelProps) {
  const uid = useId()
  const titleId = `${uid}-title`
  const bodyId = `${uid}-body`
  const [maximized, setMaximized] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  const state = maximized ? 'maximized' : collapsed ? 'collapsed' : undefined

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLElement>) => {
      if (event.key === 'Escape' && maximized) {
        setMaximized(false)
        event.stopPropagation()
      }
    },
    [maximized],
  )

  return (
    <section
      className="ui-panel"
      aria-labelledby={titleId}
      data-variant={variant}
      data-state={state}
      onKeyDown={onKeyDown}
    >
      <div className="ui-panel__header">
        <div className="ui-panel__identity">
          <h2 className="ui-panel__title" id={titleId}>
            {title}
          </h2>
        </div>
        {help !== undefined && <div className="ui-panel__help">{help}</div>}
        {controls !== undefined && (
          <Toolbar className="ui-panel__controls" aria-label={`${title} controls`}>
            {controls}
          </Toolbar>
        )}
        {(maximizable || collapsible) && (
          <div className="ui-panel__frame-actions">
            {maximizable && (
              <ToggleButton
                iconOnly
                size="sm"
                icon={MAXIMIZE_ICON}
                aria-label={`Maximize ${title}`}
                isSelected={maximized}
                onChange={(next) => {
                  setMaximized(next)
                  if (next) setCollapsed(false)
                }}
              />
            )}
            {collapsible && (
              <Button
                iconOnly
                variant="ghost"
                size="sm"
                icon={COLLAPSE_ICON}
                aria-label={`Collapse ${title}`}
                aria-expanded={!collapsed}
                aria-controls={bodyId}
                isDisabled={maximized}
                onPress={() => setCollapsed((c) => !c)}
              />
            )}
          </div>
        )}
      </div>
      <div className="ui-panel__body" id={bodyId} data-body={body} hidden={collapsed && !maximized}>
        <PanelErrorBoundary label={title}>{children}</PanelErrorBoundary>
      </div>
    </section>
  )
}
