import { useEffect, useRef, useState } from 'react'
import Popover from './Popover'

const INJECTION_SOURCES_URL = '/api/v1/workbench/injection-sources'

interface InjectionSourceEntry {
  id: string
  label: string
  injection: string
}

interface InjectionSources {
  skills: InjectionSourceEntry[]
  agents: InjectionSourceEntry[]
  prompts: InjectionSourceEntry[]
}

const EMPTY_SOURCES: InjectionSources = { skills: [], agents: [], prompts: [] }

// Same reasoning as CommandPanel's CONTROL_CHARACTER_PATTERN (see that file) applied here to
// `injection` instead of `command`: an embedded \n/\r would execute everything before it the
// moment the shell's line editor sees it, defeating "injects without executing" for this entry.
// Rejecting the whole entry at load time is the first of two defense layers — TerminalRegion's
// `sendCommand` (via TerminalSession's imperative handle) is the second.
const CONTROL_CHARACTER_PATTERN = /[\x00-\x1f\x7f]/

function isInjectionSourceEntry(value: unknown): value is InjectionSourceEntry {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as { id?: unknown }).id === 'string' &&
    typeof (value as { label?: unknown }).label === 'string' &&
    typeof (value as { injection?: unknown }).injection === 'string' &&
    !CONTROL_CHARACTER_PATTERN.test((value as { injection: string }).injection)
  )
}

// Shape-only check: are the three category keys present and arrays? Deliberately does NOT
// validate individual entries — that is `isInjectionSourceEntry`'s job, applied per-entry via
// `.filter()` below so one malformed entry (e.g. an embedded newline from a supported operator's
// edit of `_data/workbench/injection-overrides.json`) drops only itself, not its whole category
// and not the other two categories' valid entries. Only a malformed top-level payload (not an
// object, or a category that isn't an array at all) is an `error` state here.
function isInjectionSourcesShape(
  value: unknown
): value is { skills: unknown[]; agents: unknown[]; prompts: unknown[] } {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as { skills?: unknown; agents?: unknown; prompts?: unknown }
  return (
    Array.isArray(candidate.skills) && Array.isArray(candidate.agents) && Array.isArray(candidate.prompts)
  )
}

type LoadState = 'loading' | 'loaded' | 'missing' | 'error'

/**
 * Fetches `GET /api/v1/workbench/injection-sources` (`phase-wb-01`) once and shares the result
 * across all three category dropdowns below — one fetch, not three, since the route returns
 * every category in a single payload.
 *
 * The route exists only when the backend is launched with `D_SYSTEM_DEMO_TERMINAL=1`
 * (`src/api/__init__.py` imports `src.api.routes.workbench` only under that flag); with the flag
 * unset the route 404s, which this hook reports as `missing` — never `error` — so the dropdowns
 * degrade to a clear in-place message instead of an error state, matching CommandPanel's own
 * `missing`/`error` split for its (differently-sourced) demo-commands.json.
 */
function useInjectionSources() {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [sources, setSources] = useState<InjectionSources>(EMPTY_SOURCES)
  const fetchGeneration = useRef(0)

  const load = () => {
    const generation = ++fetchGeneration.current
    setLoadState('loading')
    fetch(INJECTION_SOURCES_URL, { cache: 'no-store' })
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
          if (!isInjectionSourcesShape(body)) {
            setLoadState('error')
            return
          }
          setSources({
            skills: body.skills.filter(isInjectionSourceEntry),
            agents: body.agents.filter(isInjectionSourceEntry),
            prompts: body.prompts.filter(isInjectionSourceEntry),
          })
          setLoadState('loaded')
        })
      })
      .catch(() => {
        if (generation === fetchGeneration.current) setLoadState('error')
      })
  }

  useEffect(() => {
    load()
    return () => {
      fetchGeneration.current += 1
    }
  }, [])

  return { loadState, sources, reload: load }
}

/**
 * One category's dropdown — identical mechanics to `CommandPanel` (REQ-006 R12): a click-
 * triggered, in-place `Popover` (dismissible per REQ-006 R03) whose entries come entirely from
 * the enumeration route (labels and injection text alike — nothing hardcoded here), and whose
 * selection calls `onSelect(injection)` with no "run" concept at all, since injection-source
 * entries are never executed on selection (REQ-007 W04).
 *
 * `disabled`/`deactivated` mirror CommandPanel's own contract exactly: `disabled` (terminal
 * route absent) renders a disabled trigger button instead of a `Popover`; `deactivated` (terminal
 * dropped, REQ-007 W03) keeps the `Popover` mounted with entries already loaded, but its trigger
 * carries a real `disabled` attribute via `Popover`'s own `disabled` prop.
 */
function InjectionCategoryDropdown({
  categoryLabel,
  entries,
  loadState,
  disabled,
  deactivated,
  onSelect,
  onRetry,
}: {
  categoryLabel: string
  entries: InjectionSourceEntry[]
  loadState: LoadState
  disabled: boolean
  deactivated: boolean
  onSelect: (injection: string) => void
  onRetry: () => void
}) {
  if (disabled) {
    return (
      <button
        type="button"
        className="stage-command-panel__trigger stage-command-panel__trigger--disabled"
        disabled
      >
        {categoryLabel} (terminal absent)
      </button>
    )
  }

  return (
    <Popover
      triggerLabel={`${categoryLabel} (${entries.length})`}
      title={`${categoryLabel} list`}
      disabled={deactivated}
    >
      {(close) => (
        <div className="stage-command-panel">
          {loadState === 'loading' ? (
            <p className="stage-placeholder-text">Loading {categoryLabel.toLowerCase()}…</p>
          ) : loadState === 'missing' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              {categoryLabel} list not found. Start the backend with{' '}
              <code>D_SYSTEM_DEMO_TERMINAL=1</code> to enable the workbench enumeration route
              (`phase-wb-01`).
            </p>
          ) : loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not load the {categoryLabel.toLowerCase()} list.{' '}
              <button type="button" onClick={onRetry}>
                Retry
              </button>
            </p>
          ) : entries.length === 0 ? (
            <p className="stage-placeholder-text">No {categoryLabel.toLowerCase()} available.</p>
          ) : (
            <ul className="stage-command-panel__list">
              {entries.map((entry) => (
                <li key={entry.id}>
                  <button
                    type="button"
                    className="stage-command-panel__entry"
                    onClick={() => {
                      onSelect(entry.injection)
                      close()
                    }}
                  >
                    <span>{entry.label}</span>
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

/**
 * The three injection dropdowns REQ-007 W04 adds next to `CommandPanel` — Skills, Prompts,
 * Agents — all fed by the single `/injection-sources` fetch above. Rendered unconditionally by
 * `TerminalRegion` (like `CommandPanel`), with `disabled`/`deactivated` passed straight through to
 * every category so all four dropdowns (Commands plus these three) share one deactivation
 * contract.
 */
export default function InjectionDropdowns({
  disabled,
  deactivated = false,
  onSelect,
}: {
  disabled: boolean
  deactivated?: boolean
  onSelect: (injection: string) => void
}) {
  const { loadState, sources, reload } = useInjectionSources()

  return (
    <>
      <InjectionCategoryDropdown
        categoryLabel="Skills"
        entries={sources.skills}
        loadState={loadState}
        disabled={disabled}
        deactivated={deactivated}
        onSelect={onSelect}
        onRetry={reload}
      />
      <InjectionCategoryDropdown
        categoryLabel="Prompts"
        entries={sources.prompts}
        loadState={loadState}
        disabled={disabled}
        deactivated={deactivated}
        onSelect={onSelect}
        onRetry={reload}
      />
      <InjectionCategoryDropdown
        categoryLabel="Agents"
        entries={sources.agents}
        loadState={loadState}
        disabled={disabled}
        deactivated={deactivated}
        onSelect={onSelect}
        onRetry={reload}
      />
    </>
  )
}
