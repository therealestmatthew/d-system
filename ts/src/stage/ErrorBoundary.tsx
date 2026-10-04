import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  /** What stopped working, as the reader knows it: a panel's display name, or "The stage". */
  label: string
  children: ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

/**
 * Catches a render error below it and shows what failed in place of the broken subtree (idea
 * 000569). Without one, React unmounts the whole tree on an uncaught render error and the stage
 * goes blank.
 *
 * `App.tsx` puts one around the whole stage, and `StagePage.tsx` puts one around each workbench
 * panel where it portals the panel into its slot. A crash in one panel then replaces only that
 * panel; the other panels, and any terminal session in them, keep running.
 *
 * The fallback has `role="alert"`, so a screen reader announces it when it appears. Retry clears
 * the error and renders the children again. React unmounted them when they threw, so they mount
 * afresh and their effects run again: a panel re-fetches its data, a terminal opens a new session.
 * React offers error boundaries only as class components, which is why this one is a class.
 */
export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: unknown): ErrorBoundaryState {
    return { error: error instanceof Error ? error : new Error(String(error)) }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`${this.props.label} stopped working:`, error, info.componentStack)
  }

  private retry = () => {
    this.setState({ error: null })
  }

  render() {
    const { error } = this.state
    if (error) {
      return (
        <div className="stage-error-boundary" role="alert">
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            {this.props.label} stopped working: {error.message || 'an unknown error'}.{' '}
            <button type="button" onClick={this.retry}>
              Retry
            </button>
          </p>
        </div>
      )
    }
    return this.props.children
  }
}
