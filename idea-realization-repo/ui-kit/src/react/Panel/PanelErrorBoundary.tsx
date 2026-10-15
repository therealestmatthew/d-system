import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '../Button/Button'
import { StateView } from '../StateView/StateView'

interface Props {
  /** What stopped working, as the reader knows it (the panel title). */
  label: string
  children: ReactNode
}

interface State {
  error: Error | null
}

/**
 * Contains a render error to one panel body (principle 6). The fallback is `.ui-state[data-state=error]`
 * with role=alert and a Retry that clears the error and mounts the children afresh. Error boundaries
 * are class components in React, which is why this one is a class.
 */
export class PanelErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: unknown): State {
    return { error: error instanceof Error ? error : new Error(String(error)) }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`${this.props.label} stopped working:`, error, info.componentStack)
  }

  private retry = () => this.setState({ error: null })

  render() {
    const { error } = this.state
    if (error) {
      return (
        <StateView
          state="error"
          title={`${this.props.label} stopped working`}
          body={error.message || 'An unknown error.'}
          action={
            <Button variant="secondary" onPress={this.retry}>
              Retry
            </Button>
          }
        />
      )
    }
    return this.props.children
  }
}
