import { useEffect, useState } from 'react'
import Tooltip from './Tooltip'

type TerminalEnabledState = 'checking' | 'enabled' | 'disabled' | 'unknown'

/**
 * Placeholder for the terminal region. The real xterm.js component and its websocket wiring
 * are a separate work item; this component only carries the layout slot and the in-page
 * "terminal absent" message ADR-013 requires, since absent is the system's default state.
 *
 * It asks the backend's read-only `terminal-enabled` route (`src/api/routes/demo_stage.py`)
 * rather than probing the terminal websocket itself, because a failed websocket upgrade gives
 * JavaScript no HTTP status to distinguish "route never registered" from any other failure.
 */
export default function TerminalRegion() {
  const [state, setState] = useState<TerminalEnabledState>('checking')

  useEffect(() => {
    let cancelled = false
    fetch('/api/v1/demo/stage/terminal-enabled')
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<{ terminal_enabled: boolean }>
      })
      .then((body) => {
        if (!cancelled) setState(body.terminal_enabled ? 'enabled' : 'disabled')
      })
      .catch(() => {
        if (!cancelled) setState('unknown')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="stage-region stage-region--terminal" aria-label="Terminal">
      <header className="stage-region__header">
        <h2>Terminal</h2>
        <Tooltip label="About the terminal region">
          Will hold an xterm.js terminal connected over a websocket to a real shell (a later
          work item). This is a layout placeholder.
        </Tooltip>
      </header>
      <div className="stage-region__body stage-region__body--terminal-placeholder">
        {state === 'checking' ? (
          <p className="stage-placeholder-text">Checking terminal availability…</p>
        ) : state === 'enabled' ? (
          <p className="stage-placeholder-text">
            Terminal placeholder — backend reports the terminal flag is enabled. The xterm.js
            component lands in a later work item.
          </p>
        ) : state === 'disabled' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Terminal is absent. Start the backend with <code>D_SYSTEM_DEMO_TERMINAL=1</code> to
            enable the embedded terminal (ADR-013).
          </p>
        ) : (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Terminal availability is unknown — the stage backend is not reachable.
          </p>
        )}
      </div>
    </section>
  )
}
