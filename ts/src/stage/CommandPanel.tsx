import { useEffect, useRef, useState } from 'react'
import Popover from './Popover'

const DEMO_COMMANDS_URL = '/demo-commands.json'

interface CommandEntry {
  label: string
  command: string
  run: boolean
}

interface CommandsFile {
  commands: CommandEntry[]
}

// Control characters below 0x20 (plus DEL, 0x7f) — most importantly \n and \r — must never
// appear inside a loaded command string. `sendCommand` ships `run: false` entries byte-for-byte
// except for a trailing newline it withholds on purpose; an embedded \n in the middle of the
// string would execute everything before it the moment the shell's line editor sees it, defeating
// R12's "injects without executing" for any entry authored (or corrupted) with one. Rejecting the
// whole entry at load time is the first of the two defense layers — see TerminalRegion's
// `sendCommand` for the second.
const CONTROL_CHARACTER_PATTERN = /[\x00-\x1f\x7f]/

function isCommandEntry(value: unknown): value is CommandEntry {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as { label?: unknown }).label === 'string' &&
    typeof (value as { command?: unknown }).command === 'string' &&
    !CONTROL_CHARACTER_PATTERN.test((value as { command: string }).command) &&
    typeof (value as { run?: unknown }).run === 'boolean'
  )
}

function isCommandsFile(value: unknown): value is CommandsFile {
  return (
    typeof value === 'object' &&
    value !== null &&
    Array.isArray((value as { commands?: unknown }).commands) &&
    (value as { commands: unknown[] }).commands.every(isCommandEntry)
  )
}

type LoadState = 'loading' | 'loaded' | 'missing' | 'error'

/**
 * The command panel: a click-triggered, in-place reveal (`Popover`, so it is dismissible per
 * REQ-006 R03) living in the terminal region's header. Entries load at runtime from
 * `ts/public/demo-commands.json` — served as a static asset at `/demo-commands.json` (Vite's
 * `publicDir` convention, dev and build alike), never fetched once and cached in a bundle — so
 * editing the data file changes the list with no rebuild of page code (REQ-006 R12). The real
 * command list is authored in `phase-demo-05`; this file ships clearly-placeholder entries.
 *
 * Selecting an entry calls `onSelect(command, run)`, which `TerminalRegion` wires to the active
 * session's `sendCommand` imperative-handle method — never `term.write()` — so the shell's own
 * echo paints the text on the input line (R12: "injects its command into the active terminal's
 * input line without executing it"; `run: true` entries execute immediately).
 *
 * When the terminal route is absent (`disabled`), the trigger renders as a disabled button
 * instead of a `Popover` — visible alongside the existing absent-terminal message in the region
 * body, never erroring, and never attempting to fetch a selection target that doesn't exist.
 *
 * When the terminal is merely dropped rather than absent (`deactivated`, REQ-007 W03), the
 * `Popover` itself stays mounted — entries stay loaded, no refetch flicker on restore — but its
 * trigger carries a real `disabled` attribute (via `Popover`'s own `disabled` prop) so it is
 * visible, grayed out and genuinely unclickable rather than merely styled, and reactivates the
 * instant `deactivated` goes false again.
 */
export default function CommandPanel({
  disabled,
  deactivated = false,
  onSelect,
}: {
  disabled: boolean
  deactivated?: boolean
  onSelect: (command: string, run: boolean) => void
}) {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [entries, setEntries] = useState<CommandEntry[]>([])
  const fetchGeneration = useRef(0)

  const loadEntries = () => {
    const generation = ++fetchGeneration.current
    setLoadState('loading')
    fetch(DEMO_COMMANDS_URL, { cache: 'no-store' })
      .then((response) => {
        if (generation !== fetchGeneration.current) return
        if (response.status === 404) {
          setLoadState('missing')
          return
        }
        if (!response.ok) {
          setLoadState('error')
          return
        }
        return response.json().then((body: unknown) => {
          if (generation !== fetchGeneration.current) return
          if (!isCommandsFile(body)) {
            setLoadState('error')
            return
          }
          setEntries(body.commands)
          setLoadState('loaded')
        })
      })
      .catch(() => {
        if (generation === fetchGeneration.current) setLoadState('error')
      })
  }

  useEffect(() => {
    loadEntries()
    return () => {
      fetchGeneration.current += 1
    }
  }, [])

  if (disabled) {
    return (
      <button
        type="button"
        className="stage-command-panel__trigger stage-command-panel__trigger--disabled"
        disabled
      >
        Commands (terminal absent)
      </button>
    )
  }

  return (
    <Popover
      triggerLabel={`Commands (${entries.length})`}
      title="Command list"
      disabled={deactivated}
    >
      {(close) => (
        <div className="stage-command-panel">
          {loadState === 'loading' ? (
            <p className="stage-placeholder-text">Loading commands…</p>
          ) : loadState === 'missing' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Command list not found. Add <code>ts/public/demo-commands.json</code> (the real
              entries are authored in <code>phase-demo-05</code>).
            </p>
          ) : loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not load the command list.{' '}
              <button type="button" onClick={loadEntries}>
                Retry
              </button>
            </p>
          ) : entries.length === 0 ? (
            <p className="stage-placeholder-text">No commands configured.</p>
          ) : (
            <ul className="stage-command-panel__list">
              {entries.map((entry, index) => (
                <li key={`${entry.label}-${index}`}>
                  <button
                    type="button"
                    className="stage-command-panel__entry"
                    onClick={() => {
                      onSelect(entry.command, entry.run)
                      close()
                    }}
                  >
                    <span>{entry.label}</span>
                    {entry.run ? <span className="stage-command-panel__run-badge">run</span> : null}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Popover>
  )
}
