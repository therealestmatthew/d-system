import { useEffect, useRef, useState } from 'react'
import Tooltip from './Tooltip'
import Popover from './Popover'
import { WORKBENCH_SCHEMA_VERSION } from '../workbench/types'
import { loadActiveNotesFile, saveActiveNotesFile } from '../workbench/storage'

// The fixed notes directory (REQ-007 W01) — repository-relative, passed to the workbench
// listing route below. Never walked directly by this component.
const NOTES_DIRECTORY = 'ts/public'
const NOTES_FILE_EXTENSION = '.json'
const NOTES_FILE_LIST_URL = `/api/v1/workbench/list?path=${NOTES_DIRECTORY}&ext=${NOTES_FILE_EXTENSION}`

// The notes strip's own fallback file, used when nothing valid has ever been persisted or the
// persisted choice's content no longer loads — the same file the previous talking-points panel
// defaulted to, and the one the backend's `demo_stage.py` route still names as its own default.
const DEFAULT_NOTES_FILENAME = 'talking-points.json'

// Auto-advance interval for the optional timed advance. Not configurable from the data file —
// the data file carries content only (REQ-006 R01), never behavior.
const AUTO_ADVANCE_INTERVAL_MS = 6000

type ContentLoadState = 'loading' | 'loaded' | 'missing' | 'error'
type FileListState = 'loading' | 'loaded' | 'error'

interface NotesFile {
  points: string[]
}

interface NotesFileEntry {
  name: string
}

function isNotesFile(value: unknown): value is NotesFile {
  return (
    typeof value === 'object' &&
    value !== null &&
    Array.isArray((value as { points?: unknown }).points) &&
    (value as { points: unknown[] }).points.every((point) => typeof point === 'string')
  )
}

function isNotesFileEntryList(value: unknown): value is NotesFileEntry[] {
  return (
    Array.isArray(value) &&
    value.every(
      (entry) =>
        typeof entry === 'object' &&
        entry !== null &&
        typeof (entry as { name?: unknown }).name === 'string',
    )
  )
}

/**
 * The notes strip (REQ-007 W01), replacing the earlier talking-points panel: a short, wide,
 * display-only strip showing the active entry from an owner-authored notes file — content
 * loaded at runtime, never hardcoded in this component. The `?` tooltip sits at the strip's far
 * left; every control — next/previous cycling, the timed advance, and the notes-file picker —
 * lives behind the single dropdown at the right, opened by a standard downward-triangle
 * affordance. The strip surface itself triggers nothing.
 *
 * The picker's options come from the workbench listing route (`GET /api/v1/workbench/list`,
 * `src/api/routes/workbench.py`, `phase-wb-01`), filtered to `.json` under the fixed notes
 * directory (`ts/public/`) — never a hardcoded file list and never a client-side directory walk.
 * Once a file is chosen, its content is fetched directly from Vite's static serving of
 * `ts/public/` (the same runtime-fetch convention `CommandPanel` uses for `demo-commands.json`),
 * so both the dropdown's enumeration and the strip's content come from disk, not page code.
 *
 * The chosen file persists across reloads under the ADR-016 selections key
 * (`ts/src/workbench/storage.ts`'s `saveActiveNotesFile`/`loadActiveNotesFile`), sharing that key
 * with the layout engine's own persisted selections via a merge-on-write, so this component's
 * writes never clobber the layout engine's, and vice versa.
 */
export default function NotesStripRegion() {
  const [activeFile, setActiveFile] = useState<string>(
    () => loadActiveNotesFile(WORKBENCH_SCHEMA_VERSION) ?? DEFAULT_NOTES_FILENAME,
  )
  const [contentState, setContentState] = useState<ContentLoadState>('loading')
  const [points, setPoints] = useState<string[]>([])
  const [current, setCurrent] = useState(0)
  const [autoAdvance, setAutoAdvance] = useState(false)
  const [fileListState, setFileListState] = useState<FileListState>('loading')
  const [fileList, setFileList] = useState<NotesFileEntry[]>([])
  const contentFetchGeneration = useRef(0)

  // The compatible-file list for the dropdown's picker — enumerated once via the workbench
  // listing route, independent of which file is currently active or whether its content loads.
  useEffect(() => {
    let cancelled = false
    setFileListState('loading')
    fetch(NOTES_FILE_LIST_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json()
      })
      .then((body: unknown) => {
        if (cancelled) return
        if (!isNotesFileEntryList(body)) {
          setFileListState('error')
          return
        }
        setFileList(body)
        setFileListState('loaded')
      })
      .catch(() => {
        if (!cancelled) setFileListState('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  // The active file's content — served as a static asset at the site root (Vite's default
  // `ts/public/` handling), refetched whenever the chosen file changes.
  useEffect(() => {
    const generation = ++contentFetchGeneration.current
    setContentState('loading')
    fetch(`/${activeFile}`, { cache: 'no-store' })
      .then((response) => {
        if (generation !== contentFetchGeneration.current) return
        if (response.status === 404) {
          setContentState('missing')
          return
        }
        if (!response.ok) {
          setContentState('error')
          return
        }
        return response.json().then((body: unknown) => {
          if (generation !== contentFetchGeneration.current) return
          if (!isNotesFile(body) || body.points.length === 0) {
            setContentState('error')
            return
          }
          setPoints(body.points)
          setCurrent(0)
          setContentState('loaded')
        })
      })
      .catch(() => {
        if (generation === contentFetchGeneration.current) setContentState('error')
      })
  }, [activeFile])

  // Optional timed advance: only runs with more than one point, while enabled.
  useEffect(() => {
    if (!autoAdvance || points.length < 2) return
    const timer = window.setInterval(() => {
      setCurrent((value) => (value + 1) % points.length)
    }, AUTO_ADVANCE_INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [autoAdvance, points.length])

  const selectFile = (fileName: string) => {
    setActiveFile(fileName)
    saveActiveNotesFile(WORKBENCH_SCHEMA_VERSION, fileName)
  }

  const currentEntryText =
    contentState === 'loading'
      ? 'Loading notes…'
      : contentState === 'missing'
        ? `Notes file not found: ${activeFile}.`
        : contentState === 'error'
          ? `Could not load "${activeFile}" as a notes file.`
          : points[current]

  const cyclingDisabled = contentState !== 'loaded' || points.length < 2

  return (
    <section className="stage-region stage-notes-strip" aria-label="Notes">
      <div className="stage-notes-strip__row">
        <Tooltip label="About the notes strip">
          Cycles owner-authored notes loaded at runtime from a chosen JSON file under{' '}
          <code>ts/public/</code>. Every control — cycling, the timed advance, and the file
          picker — lives in the dropdown at the right.
        </Tooltip>
        <p key={contentState === 'loaded' ? current : contentState} className="stage-notes-strip__current">
          {currentEntryText}
        </p>
        <Popover triggerLabel="▾" title="Notes controls">
          {() => (
            <div className="stage-notes-strip__menu">
              <div className="stage-notes-strip__menu-nav">
                <button
                  type="button"
                  disabled={cyclingDisabled}
                  onClick={() =>
                    setCurrent((value) => (value - 1 + points.length) % points.length)
                  }
                >
                  Previous
                </button>
                <span className="stage-notes-strip__menu-index">
                  {contentState === 'loaded' ? `${current + 1} / ${points.length}` : '—'}
                </span>
                <button
                  type="button"
                  disabled={cyclingDisabled}
                  onClick={() => setCurrent((value) => (value + 1) % points.length)}
                >
                  Next
                </button>
              </div>
              <button
                type="button"
                className="stage-notes-strip__menu-auto-advance"
                aria-pressed={autoAdvance}
                disabled={cyclingDisabled}
                onClick={() => setAutoAdvance((value) => !value)}
              >
                Auto-advance: {autoAdvance ? 'On' : 'Off'}
              </button>
              <label className="stage-notes-strip__menu-picker">
                Notes file
                <select value={activeFile} onChange={(event) => selectFile(event.target.value)}>
                  {!fileList.some((entry) => entry.name === activeFile) ? (
                    <option value={activeFile}>{activeFile}</option>
                  ) : null}
                  {fileList.map((entry) => (
                    <option key={entry.name} value={entry.name}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              {fileListState === 'error' ? (
                <p className="stage-notes-strip__menu-list-error">
                  Could not list notes files from <code>ts/public/</code>.
                </p>
              ) : null}
            </div>
          )}
        </Popover>
      </div>
    </section>
  )
}
