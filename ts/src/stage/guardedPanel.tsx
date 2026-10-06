import type { ComponentType, ReactElement } from 'react'
import ErrorBoundary from './ErrorBoundary'
import { panelDisplayName } from '../workbench/panelRegistry'

/** A workbench panel inside its own error boundary, named for the reader (idea 000569). `StagePage`
 * portals exactly this into each panel's host. It lives in its own module so a test can render the
 * same element the stage does. */
export function guardedPanel(panelId: string, Component: ComponentType): ReactElement {
  return (
    <ErrorBoundary label={panelDisplayName(panelId)}>
      <Component />
    </ErrorBoundary>
  )
}
