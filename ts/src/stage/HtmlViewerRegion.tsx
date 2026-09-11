import { useEffect, useState } from 'react'
import DirectoryPickerDialog from './DirectoryPickerDialog'
import Popover from './Popover'

const OVERVIEW_LOCATION_URL = '/api/v1/demo/stage/overview-location'
const SEARCH_URL = '/api/v1/workbench/search'
// Mirrors `ts/vite.config.ts`'s `serveRepositoryFiles` dev-server plugin, which serves any
// non-ignored repository file at this prefix — the workbench search/listing routes
// (`src/api/routes/workbench.py`, `phase-wb-01`) report paths only, never content (ADR-015), so
// this is what actually fetches the bytes an iframe can render.
const WORKBENCH_FILE_PREFIX = '/workbench-file/'
// REQ-007 W07: "the compatible files (.html and .svg)".
const COMPATIBLE_EXTENSIONS = ['.html', '.svg']

interface DirectoryEntry {
  name: string
  path: string
  is_dir: boolean
}

type FilesLoadState = 'loading' | 'loaded' | 'error'
type PageState = 'idle' | 'checking' | 'ready' | 'missing' | 'error'

function dirname(path: string): string {
  const index = path.lastIndexOf('/')
  return index === -1 ? '.' : path.slice(0, index)
}

function basename(path: string): string {
  const index = path.lastIndexOf('/')
  return index === -1 ? path : path.slice(index + 1)
}

function buildSearchUrl(directory: string): string {
  const params = new URLSearchParams({ path: directory })
  COMPATIBLE_EXTENSIONS.forEach((ext) => params.append('ext', ext))
  return `${SEARCH_URL}?${params.toString()}`
}

/**
 * The HTML Viewer panel (REQ-007 W07): generalizes the overview panel (`OverviewRegion`,
 * `phase-wb-02`) it replaces as the main slot's default in layout 1
 * (`_data/workbench/layouts/layout-1.json`) — it displays a selected page in an iframe, with the
 * generated D-System overview page (`_public/`, produced by the `d-system-overview` skill,
 * `phase-demo-04`) one selectable entry among every compatible file found recursively under
 * whatever directory is currently searched, rather than a fixed, hardcoded target.
 *
 * On mount, the searched directory and displayed page default to the generated overview page's
 * own location and containing directory — fetched at runtime from the backend's
 * `overview-location` route (`src/api/routes/demo_stage.py`, `phase-demo-01`), never hardcoded —
 * so the panel opens exactly where `OverviewRegion` used to, before the user changes anything.
 *
 * Three header controls sit right of the title, all fed by phase-wb-01's workbench read routes,
 * never a browser-native file/directory picker (ADR-015's rejected-alternative rule):
 * - Refresh: re-fetches the currently displayed page (a cache-busting query param on the iframe
 *   `src`, since a cached response would defeat the point of a manual refresh) and re-checks it
 *   still exists.
 * - The searchable file dropdown: every `.html`/`.svg` file found recursively under the searched
 *   directory (`GET /api/v1/workbench/search`), filtered client-side by the search input as the
 *   user types.
 * - The directory-change button: opens `DirectoryPickerDialog`, an in-app dialog fed by the
 *   one-level listing route (`GET /api/v1/workbench/list`) — repository-relative paths only.
 *
 * The embed/open-in-tab toggle (`D02-C1`, PLAN-021's descope rung 3) is `OverviewRegion`'s
 * kept fallback, carried over unchanged: local state here, not a prop from a parent, since the
 * workbench layout engine gives this panel's slot a fixed geometry regardless of which mode is
 * active.
 */
export default function HtmlViewerRegion() {
  const [embedded, setEmbedded] = useState(true)
  const [directory, setDirectory] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [searchText, setSearchText] = useState('')
  const [files, setFiles] = useState<DirectoryEntry[]>([])
  const [filesLoadState, setFilesLoadState] = useState<FilesLoadState>('loading')
  const [pageState, setPageState] = useState<PageState>('idle')
  const [refreshToken, setRefreshToken] = useState(0)

  // Seed the initial directory/page from the generated overview's own location, once, on mount —
  // never a hardcoded default (mirrors OverviewRegion's own runtime fetch of this same route).
  useEffect(() => {
    let cancelled = false
    fetch(OVERVIEW_LOCATION_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<{ path: string }>
      })
      .then(({ path }) => {
        if (cancelled) return
        setDirectory(dirname(path))
        setSelectedFile(path)
      })
      .catch(() => {
        if (cancelled) return
        setDirectory('.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  // The recursive compatible-file list for the currently searched directory (REQ-007 W07). Text
  // filtering happens client-side against this same fetched list, below — no round trip per
  // keystroke.
  useEffect(() => {
    if (directory === null) return
    let cancelled = false
    setFilesLoadState('loading')
    fetch(buildSearchUrl(directory))
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<DirectoryEntry[]>
      })
      .then((body) => {
        if (cancelled) return
        setFiles(body)
        setFilesLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setFilesLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [directory])

  // Confirm the selected page actually exists before rendering it — a selection can point at a
  // file that has since been removed, and `refreshToken` re-runs this same check for the refresh
  // control (REQ-007 W07: "a refresh button re-fetching the current page").
  useEffect(() => {
    if (!selectedFile) {
      setPageState('idle')
      return
    }
    let cancelled = false
    setPageState('checking')
    fetch(`${WORKBENCH_FILE_PREFIX}${selectedFile}`, { method: 'HEAD', cache: 'no-store' })
      .then((response) => {
        if (!cancelled) setPageState(response.ok ? 'ready' : 'missing')
      })
      .catch(() => {
        if (!cancelled) setPageState('error')
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFile, refreshToken])

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchText.trim().toLowerCase()),
  )

  const embedSrc = selectedFile
    ? `${WORKBENCH_FILE_PREFIX}${selectedFile}?v=${refreshToken}`
    : null
  const openTabHref = selectedFile ? `${WORKBENCH_FILE_PREFIX}${selectedFile}` : null

  return (
    <section className="stage-region stage-region--html-viewer" aria-label="HTML Viewer">
      <header className="stage-region__header">
        <h2>HTML Viewer</h2>
        <div className="stage-html-viewer__controls">
          <button
            type="button"
            className="stage-html-viewer__refresh"
            aria-label="Refresh the current page"
            disabled={!selectedFile}
            onClick={() => setRefreshToken((value) => value + 1)}
          >
            ⟳ Refresh
          </button>

          <Popover
            triggerLabel={selectedFile ? basename(selectedFile) : 'Choose a file ▾'}
            triggerAriaLabel="Choose a compatible file"
            title="Choose a file"
          >
            {(close) => (
              <div className="stage-html-viewer__file-picker">
                <input
                  type="text"
                  className="stage-html-viewer__search"
                  placeholder="Filter files…"
                  aria-label="Filter compatible files"
                  value={searchText}
                  onChange={(event) => setSearchText(event.target.value)}
                />
                {filesLoadState === 'loading' ? (
                  <p className="stage-placeholder-text">Searching…</p>
                ) : filesLoadState === 'error' ? (
                  <p className="stage-placeholder-text stage-placeholder-text--absent">
                    Could not search this directory.
                  </p>
                ) : filteredFiles.length === 0 ? (
                  <p className="stage-placeholder-text">No matching files.</p>
                ) : (
                  <ul className="stage-html-viewer__file-list">
                    {filteredFiles.map((file) => (
                      <li key={file.path}>
                        <button
                          type="button"
                          className="stage-html-viewer__file-option"
                          onClick={() => {
                            setSelectedFile(file.path)
                            close()
                          }}
                        >
                          {file.path}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </Popover>

          {directory !== null ? (
            <DirectoryPickerDialog initialDirectory={directory} onSelectDirectory={setDirectory} />
          ) : null}

          <button
            type="button"
            className="stage-region__header-toggle"
            aria-pressed={!embedded}
            onClick={() => setEmbedded((value) => !value)}
          >
            {embedded ? 'Embedded' : 'Open-in-tab link (rung 3)'}
          </button>
        </div>
      </header>
      <div
        className={
          'stage-region__body' +
          (embedded && pageState === 'ready' ? ' stage-region__body--overview' : '')
        }
      >
        {directory === null ? (
          <p className="stage-placeholder-text">Locating the generated overview page…</p>
        ) : pageState === 'idle' ? (
          <p className="stage-placeholder-text">
            Select a file from the dropdown above, or a directory to search.
          </p>
        ) : pageState === 'checking' ? (
          <p className="stage-placeholder-text">Checking the selected page…</p>
        ) : pageState === 'error' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Could not reach the backend to check the selected page.
          </p>
        ) : pageState === 'missing' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Selected page is absent — <code>{selectedFile}</code> does not exist.
          </p>
        ) : embedded ? (
          <iframe className="stage-overview__iframe" src={embedSrc ?? undefined} title="HTML Viewer" />
        ) : (
          <a
            className="stage-overview__open-link"
            href={openTabHref ?? undefined}
            target="_blank"
            rel="noreferrer"
          >
            Open page in a new tab ↗
          </a>
        )}
      </div>
    </section>
  )
}
