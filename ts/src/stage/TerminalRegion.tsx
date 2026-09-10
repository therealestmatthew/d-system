import { useEffect, useRef, useState } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import Tooltip from './Tooltip'
import Popover from './Popover'

type TerminalEnabledState = 'checking' | 'enabled' | 'disabled' | 'unknown'
type ConnectionState = 'connecting' | 'open' | 'closed'

const TERMINAL_WEBSOCKET_PATH = '/api/v1/demo/terminal/ws'
// REQ-006 R10: "up to four terminal sessions as tabs."
const MAX_SESSIONS = 4
const FIRST_SESSION_ID = 1

/**
 * One terminal session's xterm.js instance and its own websocket — the unit R10 says must be
 * independent per tab ("each tab is an independent shell over its own websocket").
 *
 * `visible` is true only while this session is both the active tab and the region is not
 * collapsed; it never controls mounting. TerminalRegion always keeps every session's
 * TerminalSession mounted regardless of tab/collapse state (R10: "switching tabs or collapsing
 * the region never terminates a session"), and only CSS visibility responds to `visible` — the
 * socket and shell process live for as long as this component instance is mounted, which ends
 * only when TerminalRegion removes this session's id from its list (the guarded-drop / guarded
 * tab-close path in the parent).
 */
function TerminalSession({ visible }: { visible: boolean }) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting')
  // Holds the mount effect's `attemptFit` closure so the visibility-triggered effect below can
  // call the same guarded-fit-and-resize-frame logic without redefining it.
  const attemptFitRef = useRef<() => void>(() => {})

  useEffect(() => {
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

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(`${protocol}//${window.location.host}${TERMINAL_WEBSOCKET_PATH}`)
    socket.binaryType = 'arraybuffer'

    // Guards fitAddon.fit() against a zero-size container — an inactive tab or a collapsed
    // region has a container with no box (CSS-hidden per R10/R11's "never terminate, just
    // hide"), and xterm.js's fit math (and its underlying term.resize()) throws on a
    // non-positive column/row count rather than silently no-op-ing. On a successful fit, sends
    // the D06-C1 resize control frame so the PTY on the backend tracks the same grid the
    // frontend just fit to.
    const attemptFit = () => {
      if (container.clientWidth === 0 || container.clientHeight === 0) return
      try {
        fitAddon.fit()
      } catch {
        return
      }
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }))
      }
    }
    attemptFitRef.current = attemptFit
    attemptFit()

    socket.addEventListener('open', () => {
      setConnectionState('open')
      attemptFit()
    })
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
      attemptFit()
    })
    resizeObserver.observe(container)

    return () => {
      resizeObserver.disconnect()
      dataDisposable.dispose()
      socket.close()
      term.dispose()
    }
    // Mount once per TerminalSession instance — a session's socket and shell live for the
    // instance's whole lifetime, ending only when the parent unmounts it (guarded drop/close).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Refit when this session becomes visible again — a CSS display:none -> block transition
  // (tab activation, or the region re-expanding from collapsed) doesn't reliably produce a
  // ResizeObserver callback in the same tick in every browser, so this is an explicit refit on
  // top of the ResizeObserver path above.
  useEffect(() => {
    if (!visible) return
    attemptFitRef.current()
  }, [visible])

  return (
    <div className={'stage-terminal-session' + (visible ? ' stage-terminal-session--active' : '')}>
      <div ref={containerRef} className="stage-terminal-mount" />
      {connectionState === 'closed' ? (
        <p className="stage-placeholder-text stage-placeholder-text--absent stage-terminal-mount__overlay">
          Terminal connection closed. Reload the page to reconnect.
        </p>
      ) : null}
    </div>
  )
}

/**
 * The embedded terminal region: xterm.js in the browser, bridged over a websocket to the real
 * shell `phase-demo-01`'s route (`src/api/routes/demo_terminal.py`) exposes at
 * `/api/v1/demo/terminal/ws`, reached through the Vite dev proxy's `/api` entry
 * (`ts/vite.config.ts`, `VITE_API_TARGET`-configurable, `ws: true` so the same proxy entry
 * carries the websocket upgrade).
 *
 * It asks the backend's read-only `terminal-enabled` route
 * (`src/api/routes/demo_stage.py`) before ever attempting a websocket connection, because a
 * failed websocket upgrade gives JavaScript no HTTP status to distinguish "route never
 * registered" (the default state, ADR-013) from any other failure. Only when that check reports
 * `terminal_enabled: true` does this component ever mount a TerminalSession — so the in-page
 * "terminal absent" message (ADR-013) is never a race against a connection attempt that was
 * always going to fail.
 *
 * REQ-006 R10/R11: hosts up to four independent sessions as tabs (every session's
 * TerminalSession stays mounted; inactive tabs are CSS-hidden only), a collapse control that
 * hides the region via CSS while leaving every socket open (`collapsed`/`onToggleCollapsed`,
 * lifted to StagePage because the --no-terminal grid reflow lives on StagePage's grid
 * container), and a guarded drop for both the whole-region descope (rung 4, in StagePage) and
 * closing an individual tab (here) — both go through the portaled Popover's confirm action
 * before anything terminates.
 */
export default function TerminalRegion({
  collapsed,
  onToggleCollapsed,
}: {
  collapsed: boolean
  onToggleCollapsed: () => void
}) {
  const [enabledState, setEnabledState] = useState<TerminalEnabledState>('checking')
  const [sessionIds, setSessionIds] = useState<number[]>([FIRST_SESSION_ID])
  const [activeSessionId, setActiveSessionId] = useState<number>(FIRST_SESSION_ID)
  const nextSessionIdRef = useRef(FIRST_SESSION_ID + 1)

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

  const addSession = () => {
    if (sessionIds.length >= MAX_SESSIONS) return
    const id = nextSessionIdRef.current
    nextSessionIdRef.current += 1
    setSessionIds((previous) => [...previous, id])
    setActiveSessionId(id)
  }

  // Guarded: called only from the tab-close Popover's confirm action, never from the close
  // button's click handler directly (R11 — "nothing terminates before the confirm").
  const confirmCloseSession = (id: number) => {
    const index = sessionIds.indexOf(id)
    const next = sessionIds.filter((sessionId) => sessionId !== id)
    setSessionIds(next)
    if (activeSessionId === id && next.length > 0) {
      setActiveSessionId(next[Math.max(0, Math.min(index, next.length - 1))])
    }
  }

  return (
    <section
      className={'stage-region stage-region--terminal' + (collapsed ? ' stage-region--terminal-collapsed' : '')}
      aria-label="Terminal"
    >
      <header className="stage-region__header">
        <h2>Terminal</h2>
        <Tooltip label="About the terminal region">
          Up to four independent xterm.js terminals, each over its own websocket to a real
          shell, when the backend's terminal capability is enabled (ADR-013). Absent by default.
          Switching tabs or collapsing this region never ends a session; closing a tab or
          dropping the whole region does, after confirming.
        </Tooltip>
        {enabledState === 'enabled' ? (
          <button
            type="button"
            className="stage-terminal-collapse-toggle"
            aria-pressed={collapsed}
            onClick={onToggleCollapsed}
          >
            {collapsed ? 'Expand terminal' : 'Collapse terminal'}
          </button>
        ) : null}
      </header>
      {enabledState === 'enabled' ? (
        <div className="stage-region__body stage-region__body--terminal">
          <div className="stage-terminal-tabbar" role="tablist" aria-label="Terminal sessions">
            {sessionIds.map((id, index) => (
              <div
                key={id}
                className={
                  'stage-terminal-tab' + (id === activeSessionId ? ' stage-terminal-tab--active' : '')
                }
              >
                <button
                  type="button"
                  role="tab"
                  aria-selected={id === activeSessionId}
                  className="stage-terminal-tab__select"
                  onClick={() => setActiveSessionId(id)}
                >
                  Session {index + 1}
                </button>
                <Popover triggerLabel="×" title={`Close session ${index + 1}?`}>
                  {(close) => (
                    <div className="stage-terminal-confirm">
                      <p className="stage-placeholder-text">
                        Closing this tab ends its shell process and scrollback. This cannot be
                        undone.
                      </p>
                      <button
                        type="button"
                        className="stage-terminal-confirm__action"
                        onClick={() => {
                          confirmCloseSession(id)
                          close()
                        }}
                      >
                        Confirm: close session {index + 1}
                      </button>
                    </div>
                  )}
                </Popover>
              </div>
            ))}
            <button
              type="button"
              className="stage-terminal-tab__new"
              aria-label="New terminal session"
              disabled={sessionIds.length >= MAX_SESSIONS}
              onClick={addSession}
            >
              + New session
            </button>
          </div>
          <div className="stage-terminal-sessions">
            {sessionIds.length === 0 ? (
              <p className="stage-placeholder-text">
                No terminal sessions. Use "+ New session" to start one.
              </p>
            ) : (
              sessionIds.map((id) => (
                <TerminalSession key={id} visible={!collapsed && id === activeSessionId} />
              ))
            )}
          </div>
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
