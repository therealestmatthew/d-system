import { useEffect, useRef, useState } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import Tooltip from './Tooltip'

type TerminalEnabledState = 'checking' | 'enabled' | 'disabled' | 'unknown'
type ConnectionState = 'connecting' | 'open' | 'closed'

const TERMINAL_WEBSOCKET_PATH = '/api/v1/demo/terminal/ws'

/**
 * The embedded terminal region: xterm.js in the browser, bridged over a websocket to the real
 * shell `phase-demo-01`'s route (`src/api/routes/demo_terminal.py`) exposes at
 * `/api/v1/demo/terminal/ws`, reached through the Vite dev proxy's `/api` entry
 * (`ts/vite.config.ts`, `VITE_API_TARGET`-configurable, `ws: true` so the same proxy entry
 * carries the websocket upgrade).
 *
 * It asks the backend's read-only `terminal-enabled` route
 * (`src/api/routes/demo_stage.py`) before ever attempting the websocket connection, because a
 * failed websocket upgrade gives JavaScript no HTTP status to distinguish "route never
 * registered" (the default state, ADR-013) from any other failure. Only when that check reports
 * `terminal_enabled: true` does this component open the websocket at all — so the in-page
 * "terminal absent" message (ADR-013) is never a race against a connection attempt that was
 * always going to fail.
 */
export default function TerminalRegion() {
  const [enabledState, setEnabledState] = useState<TerminalEnabledState>('checking')
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting')
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch('/api/v1/demo/stage/terminal-enabled')
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<{ terminal_enabled: boolean }>
      })
      .then((body) => {
        if (!cancelled) setEnabledState(body.terminal_enabled ? 'enabled' : 'disabled')
      })
      .catch(() => {
        if (!cancelled) setEnabledState('unknown')
      })
    return () => {
      cancelled = true
    }
  }, [])

  // The terminal itself, its websocket, and the resize wiring only exist while the backend has
  // confirmed the route is present — mounting xterm.js against a route ADR-013 says is absent
  // by default would just trade the in-page message for a raw connection error.
  useEffect(() => {
    if (enabledState !== 'enabled') return
    const container = containerRef.current
    if (!container) return

    setConnectionState('connecting')

    const term = new Terminal({
      cursorBlink: true,
      convertEol: true,
      fontFamily: 'ui-monospace, "SFMono-Regular", Consolas, monospace',
      fontSize: 13,
      theme: { background: '#0d1117', foreground: '#c9d1d9' },
    })
    const fitAddon = new FitAddon()
    term.loadAddon(fitAddon)
    term.open(container)
    fitAddon.fit()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(`${protocol}//${window.location.host}${TERMINAL_WEBSOCKET_PATH}`)
    socket.binaryType = 'arraybuffer'

    socket.addEventListener('open', () => setConnectionState('open'))
    socket.addEventListener('close', () => setConnectionState('closed'))
    socket.addEventListener('error', () => setConnectionState('closed'))
    socket.addEventListener('message', (event) => {
      if (event.data instanceof ArrayBuffer) {
        term.write(new Uint8Array(event.data))
      } else if (typeof event.data === 'string') {
        term.write(event.data)
      }
    })

    const dataDisposable = term.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(new TextEncoder().encode(data))
      }
    })

    // Resize the terminal with its region: refit xterm.js's cell grid to the container's
    // current size on every layout change (window resize, a layout-control toggle in
    // StagePage reflowing the grid, or the browser's own reflow), not just on mount.
    const resizeObserver = new ResizeObserver(() => {
      fitAddon.fit()
    })
    resizeObserver.observe(container)

    return () => {
      resizeObserver.disconnect()
      dataDisposable.dispose()
      socket.close()
      term.dispose()
    }
  }, [enabledState])

  return (
    <section className="stage-region stage-region--terminal" aria-label="Terminal">
      <header className="stage-region__header">
        <h2>Terminal</h2>
        <Tooltip label="About the terminal region">
          An xterm.js terminal connected over a websocket to a real shell, when the backend's
          terminal capability is enabled (ADR-013). Absent by default.
        </Tooltip>
      </header>
      {enabledState === 'enabled' ? (
        <div className="stage-region__body stage-region__body--terminal">
          <div ref={containerRef} className="stage-terminal-mount" />
          {connectionState === 'closed' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent stage-terminal-mount__overlay">
              Terminal connection closed. Reload the page to reconnect.
            </p>
          ) : null}
        </div>
      ) : (
        <div className="stage-region__body stage-region__body--terminal-placeholder">
          {enabledState === 'checking' ? (
            <p className="stage-placeholder-text">Checking terminal availability…</p>
          ) : enabledState === 'disabled' ? (
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
      )}
    </section>
  )
}
