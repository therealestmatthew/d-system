import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import Tooltip from './Tooltip'
import Popover from './Popover'
import CommandPanel from './CommandPanel'
import InjectionDropdowns from './InjectionDropdowns'
import TerminalMenu from './TerminalMenu'

type TerminalEnabledState = 'checking' | 'enabled' | 'disabled' | 'unknown'
type ConnectionState = 'connecting' | 'open' | 'closed'

const TERMINAL_WEBSOCKET_PATH = '/api/v1/demo/terminal/ws'
// REQ-006 R10: "up to four terminal sessions as tabs."
const MAX_SESSIONS = 4
const FIRST_SESSION_ID = 1

// REQ-007 W12: the fixed shell allowlist mirrored from the backend's own
// (`src/api/routes/demo_terminal.py`, `SHELL_ALLOWLIST`, ADR-014 section 5) — bash is the POSIX
// panel, cmd/powershell the two Windows panels. Kept as a literal union (not imported — the two
// sides are independent, and a mismatch here only ever produces the same "unavailable_shell"
// in-panel message the backend already renders correctly) rather than a shared module, matching
// this repo's existing pattern of small runtime-checked literals per side (`isCommandsFile`,
// `isNotesFile`).
export type TerminalShell = 'bash' | 'cmd' | 'powershell'

const SHELL_LABELS: Record<TerminalShell, string> = {
  bash: 'bash',
  cmd: 'CMD',
  powershell: 'PowerShell',
}

// The structured refusal frame the backend sends (`SHELL_REFUSAL_MESSAGE_TYPE` /
// `_refuse_shell_request` in `src/api/routes/demo_terminal.py`) over an accepted-then-closed
// socket when the requested shell is unlisted or unavailable on this host (ADR-014 section 5).
// Recognized by shape, not trusted blindly — an unrecognized text frame falls through to the
// existing `term.write()` path unchanged, so this addition never intercepts real shell output.
interface ShellRefusal {
  shell: string
  reason: string
  message: string
}

function parseShellRefusal(raw: string): ShellRefusal | null {
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    return null
  }
  if (typeof parsed !== 'object' || parsed === null) return null
  const record = parsed as Record<string, unknown>
  if (
    record.type === 'shell_refusal' &&
    typeof record.shell === 'string' &&
    typeof record.reason === 'string' &&
    typeof record.message === 'string'
  ) {
    return { shell: record.shell, reason: record.reason, message: record.message }
  }
  return null
}

// REQ-007 W12: "a clear in-panel message naming the unavailable shell" — the backend's own
// `message` field already names the shell (e.g. "cmd is not available on this host") and is
// authored server-side, so this prefers it over inventing frontend copy; the fallback only
// covers a `message` that is present but empty, which the backend never actually sends.
function refusalDisplayMessage(refusal: ShellRefusal): string {
  if (refusal.message.trim().length > 0) return refusal.message
  const label = SHELL_LABELS[refusal.shell as TerminalShell] ?? refusal.shell
  return `${label} is not available on this host.`
}

// The imperative handle TerminalSession exposes to its parent (TerminalRegion) so the command
// panel (REQ-006 R12) — rendered in TerminalRegion's own header, not inside TerminalSession —
// can reach the *active* session's live socket without new shared state. This is the repo's
// existing prop-drilling style applied to a child's otherwise-private socket: the handle exposes
// only "send this text", never the socket itself or term.write(), so an injected command is
// always painted by the shell's own echo over the wire, exactly like a keystroke.
export interface TerminalSessionHandle {
  sendCommand: (text: string, appendNewline: boolean) => void
}

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
const TerminalSession = forwardRef<
  TerminalSessionHandle,
  { visible: boolean; shell: TerminalShell }
>(function TerminalSession({ visible, shell }, ref) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting')
  // REQ-007 W12: set only when the backend refuses this session's requested shell (unlisted, or
  // unavailable on this host — e.g. CMD/PowerShell on Linux). Once set, it takes over this
  // session's body in place of the xterm mount, exactly like the existing `connectionState ===
  // 'closed'` overlay below — never a raw error, never an unmounted/broken terminal.
  const [shellRefusal, setShellRefusal] = useState<ShellRefusal | null>(null)
  // Holds the mount effect's `attemptFit` closure so the visibility-triggered effect below can
  // call the same guarded-fit-and-resize-frame logic without redefining it.
  const attemptFitRef = useRef<() => void>(() => {})
  // Holds the mount effect's live socket so the imperative handle below (and the command panel
  // that reaches it) always sends over the *current* socket, not a stale closure from mount.
  const socketRef = useRef<WebSocket | null>(null)

  useImperativeHandle(
    ref,
    () => ({
      sendCommand: (text: string, appendNewline: boolean) => {
        const socket = socketRef.current
        if (!socket || socket.readyState !== WebSocket.OPEN) return
        // Same path as term.onData below — raw bytes over the socket, never term.write() — so
        // the shell's own echo paints the text; no trailing newline leaves it un-executed on the
        // input line, a trailing "\n" (run: true entries) executes it immediately. Second defense
        // layer (CommandPanel's isCommandEntry is the first): this method does not trust its
        // caller either, so when it is not the one appending the newline, it strips any \r or \n
        // already inside `text` rather than shipping it byte-for-byte — an embedded newline
        // reaching the shell mid-string would execute everything before it, the same injection
        // the load-time check exists to block, just reached a different way (a caller that
        // bypasses CommandPanel entirely).
        const sanitized = appendNewline ? text : text.replace(/[\r\n]/g, '')
        const payload = appendNewline ? `${sanitized}\n` : sanitized
        socket.send(new TextEncoder().encode(payload))
      },
    }),
    [],
  )

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Guards every socket/terminal event handler below against firing after this effect's own
    // cleanup has already run — most importantly under React 18 StrictMode in dev, which mounts,
    // cleans up and remounts every effect once on purpose to surface exactly this class of bug.
    // Without it, the first (StrictMode-only) instance's `message` handler could still call
    // `term.write()` after `term.dispose()` had already run.
    let disposed = false

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
    // REQ-007 W12 / ADR-014 section 5: every session requests its shell explicitly, including
    // "bash" — the backend's own `_executable_for_shell` treats an explicit "bash" exactly like
    // the query param's absence (still `D_SYSTEM_DEMO_SHELL`-overridable), so this never changes
    // the existing bash panel's behavior; it only gives cmd/powershell sessions a name to ask for.
    const socketUrl = `${protocol}//${window.location.host}${TERMINAL_WEBSOCKET_PATH}?shell=${encodeURIComponent(shell)}`
    const socket = new WebSocket(socketUrl)
    socket.binaryType = 'arraybuffer'
    socketRef.current = socket

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
      if (disposed) return
      setConnectionState('open')
      attemptFit()
    })
    socket.addEventListener('close', () => {
      if (disposed) return
      setConnectionState('closed')
    })
    socket.addEventListener('error', () => {
      if (disposed) return
      setConnectionState('closed')
    })
    socket.addEventListener('message', (event) => {
      if (disposed) return
      if (event.data instanceof ArrayBuffer) {
        term.write(new Uint8Array(event.data))
      } else if (typeof event.data === 'string') {
        // A shell-refusal text frame (ADR-014 section 5) is recognized by shape and diverted to
        // in-panel state, never painted into the terminal and never thrown as an uncaught error;
        // any other text frame falls through to the pre-existing `term.write()` path unchanged.
        const refusal = parseShellRefusal(event.data)
        if (refusal) {
          setShellRefusal(refusal)
          return
        }
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
      disposed = true
      resizeObserver.disconnect()
      dataDisposable.dispose()
      socketRef.current = null
      // The startup-race console warning this fixes: calling `.close()` on a socket still in
      // `CONNECTING` state (readyState 0) makes the browser log "WebSocket is closed before the
      // connection is established" — harmless, but real, under React 18 StrictMode's
      // mount-cleanup-remount dance in dev, where the first instance's cleanup can run before its
      // handshake finishes. Closing a CONNECTING socket immediately is otherwise correct (the
      // session must end promptly), so instead of skipping the close, this defers it: let the
      // handshake finish, then close normally, once, the moment it does. `disposed` above already
      // stops every other handler from acting on this now-superseded socket in the meantime.
      if (socket.readyState === WebSocket.CONNECTING) {
        socket.addEventListener('open', () => socket.close(), { once: true })
      } else {
        socket.close()
      }
      term.dispose()
    }
    // Mount once per TerminalSession instance — a session's socket and shell live for the
    // instance's whole lifetime, ending only when the parent unmounts it (guarded drop/close).
    // `shell` is read once here (it names the panel instance's fixed shell, e.g. every "CMD"
    // panel session always requests "cmd") and never changes for an already-mounted session.
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
      {shellRefusal ? (
        // Takes priority over the plain "connection closed" message below: the backend accepts
        // the socket, sends this frame, then closes it (ADR-014 section 5), so `connectionState`
        // also reaches 'closed' shortly after — but the refusal's own named-shell message is the
        // one that belongs on screen, not the generic reconnect prompt.
        <p className="stage-placeholder-text stage-placeholder-text--absent stage-terminal-mount__overlay">
          {refusalDisplayMessage(shellRefusal)}
        </p>
      ) : connectionState === 'closed' ? (
        <p className="stage-placeholder-text stage-placeholder-text--absent stage-terminal-mount__overlay">
          Terminal connection closed. Reload the page to reconnect.
        </p>
      ) : null}
    </div>
  )
})

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
 * hides the region via CSS, and a guarded whole-region drop. REQ-007 W02 moves both controls into
 * a single `(...)` ellipsis menu (`TerminalMenu`) at the header's top right: the header's own
 * standalone "Collapse terminal" button and the page-level drop control (`StagePage`'s old rung-4
 * "Terminal: Shown/Hidden" toggle, already gone as of `phase-wb-02`) no longer exist anywhere.
 * Collapse still only flips CSS (no session terminates); drop still goes through `TerminalMenu`'s
 * in-bubble confirm step before anything terminates.
 *
 * REQ-007 W03: dropping no longer makes the region disappear or unmount. `dropped` swaps only the
 * body — the tab bar and session views are replaced in place by an inactive-terminal info page —
 * while the header, including the ellipsis menu and every injection dropdown (`CommandPanel` plus
 * the Skills/Prompts/Agents dropdowns, `InjectionDropdowns`, REQ-007 W04), stays mounted and
 * visible. Each dropdown receives `deactivated={dropped}` so it renders grayed out and genuinely
 * unclickable (a real `disabled` attribute via `Popover`'s own `disabled` prop, not styling
 * alone) and reactivates the instant `dropped` goes false again. The section's own box — and so
 * the workbench layout engine's (`ts/src/workbench/`, REQ-007 W05/ADR-016) fixed slot geometry
 * around it — never changes shape between the two states.
 *
 * Both `collapsed` and `dropped` are local state here (`phase-wb-02`), not lifted to a parent —
 * a panel's own drop/collapse only ever changes what renders *inside* its fixed slot box, never
 * the grid around it.
 *
 * REQ-007 W12: `shell` selects which of the three workbench panel dropdown options
 * (`ts/src/workbench/panelRegistry.tsx`: "Terminal (bash)", "CMD", "PowerShell") this instance
 * is — the three are functionally identical through this one component; nothing below forks on
 * it except the query param each session's socket opens with (`TerminalSession`, ADR-014
 * section 5's per-session shell selection) and the header's own label. Tabs, collapse, drop and
 * every injection dropdown behave identically regardless of shell, exactly once, here — never
 * copy-pasted per shell.
 */
export default function TerminalRegion({ shell = 'bash' }: { shell?: TerminalShell }) {
  const [enabledState, setEnabledState] = useState<TerminalEnabledState>('checking')
  const [collapsed, setCollapsed] = useState(false)
  const [dropped, setDropped] = useState(false)
  const [sessionIds, setSessionIds] = useState<number[]>([FIRST_SESSION_ID])
  const [activeSessionId, setActiveSessionId] = useState<number>(FIRST_SESSION_ID)
  const nextSessionIdRef = useRef(FIRST_SESSION_ID + 1)
  // Every mounted session's imperative handle, keyed by session id — reached into (not lifted to
  // state) so the command panel (R12) can send to whichever session is active without a new
  // shared-state mechanism, matching the repo's existing ref-based prop-drilling style.
  const sessionHandlesRef = useRef<Map<number, TerminalSessionHandle>>(new Map())

  const sendToActiveSession = (text: string, appendNewline: boolean) => {
    sessionHandlesRef.current.get(activeSessionId)?.sendCommand(text, appendNewline)
  }

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

  // REQ-007 W12: bash keeps the pre-existing bare "Terminal" title (nothing about the bash
  // panel's own label changes), cmd/powershell name themselves so the presenter can tell the
  // three dropdown-selected panel instances apart once one is placed in a slot.
  const regionTitle = shell === 'bash' ? 'Terminal' : `Terminal (${SHELL_LABELS[shell]})`

  return (
    <section
      className={'stage-region stage-region--terminal' + (collapsed ? ' stage-region--terminal-collapsed' : '')}
      aria-label={regionTitle}
    >
      <header className="stage-region__header">
        <h2>{regionTitle}</h2>
        <Tooltip label="About the terminal region">
          Up to four independent xterm.js terminals, each over its own websocket to a real
          shell, when the backend's terminal capability is enabled (ADR-013). Absent by default.
          Switching tabs or collapsing this region never ends a session; closing a tab or
          dropping the whole region does, after confirming. While dropped, the terminal area
          shows an inactive-terminal info page in place and the injection dropdowns are
          deactivated until restored.
        </Tooltip>
        <CommandPanel
          disabled={enabledState !== 'enabled'}
          deactivated={dropped}
          onSelect={sendToActiveSession}
        />
        <InjectionDropdowns
          disabled={enabledState !== 'enabled'}
          deactivated={dropped}
          onSelect={(injection) => sendToActiveSession(injection, false)}
        />
        {enabledState === 'enabled' ? (
          <TerminalMenu
            collapsed={collapsed}
            onToggleCollapse={() => setCollapsed((value) => !value)}
            dropped={dropped}
            onRestore={() => setDropped(false)}
            onConfirmDrop={() => setDropped(true)}
          />
        ) : null}
      </header>
      {dropped ? (
        <div className="stage-region__body stage-region__body--terminal-placeholder">
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Terminal dropped — every open session's shell process and scrollback ended. Open the
            "..." menu and choose "Restore terminal" to start fresh sessions.
          </p>
        </div>
      ) : enabledState === 'enabled' ? (
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
                <TerminalSession
                  key={id}
                  visible={!collapsed && id === activeSessionId}
                  shell={shell}
                  ref={(handle) => {
                    if (handle) sessionHandlesRef.current.set(id, handle)
                    else sessionHandlesRef.current.delete(id)
                  }}
                />
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

// REQ-007 W12: the two additional panel-registry entries (`ts/src/workbench/panelRegistry.tsx`)
// for the CMD and PowerShell slot-dropdown options. Each is a parameter fixed to a prop value —
// not a fork of `TerminalRegion` — so the shared tabs/collapse/drop/injection behavior stays in
// exactly one place, per this phase's dispatch ("shared, not duplicated"). The bash panel option
// uses the default export directly with its default `shell="bash"`.
export function TerminalRegionCmd() {
  return <TerminalRegion shell="cmd" />
}

export function TerminalRegionPowerShell() {
  return <TerminalRegion shell="powershell" />
}
