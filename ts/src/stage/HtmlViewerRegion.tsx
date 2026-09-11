import { useEffect, useRef, useState } from 'react'
import DirectoryPickerDialog from './DirectoryPickerDialog'
import Popover from './Popover'
import { useActiveSchemaVersion } from '../workbench/schemaVersionContext'
import { loadHtmlViewerTabs, saveHtmlViewerTabs } from '../workbench/storage'

const OVERVIEW_LOCATION_URL = '/api/v1/demo/stage/overview-location'
const SEARCH_URL = '/api/v1/workbench/search'
// Mirrors `ts/vite.config.ts`'s `serveRepositoryFiles` dev-server plugin, which serves any
// non-ignored repository file at this prefix — the workbench search/listing routes
// (`src/api/routes/workbench.py`, `phase-wb-01`) report paths only, never content (ADR-015), so
// this is what actually fetches the bytes an iframe can render.
const WORKBENCH_FILE_PREFIX = '/workbench-file/'
// REQ-007 W07: "the compatible files (.html and .svg)".
const COMPATIBLE_EXTENSIONS = ['.html', '.svg']

// REQ-007 W08: "tabs exactly like the terminal's session tabs" — mirrors `TerminalRegion`'s own
// `MAX_SESSIONS`/`FIRST_SESSION_ID` constants and cap, one tab bar per panel instance.
const MAX_TABS = 4
const FIRST_TAB_ID = 1

interface DirectoryEntry {
  name: string
  path: string
  is_dir: boolean
}

type FilesLoadState = 'loading' | 'loaded' | 'error'
type PageState = 'idle' | 'checking' | 'ready' | 'missing' | 'error'

/** One HTML Viewer tab's live (in-memory) context — the same three fields ADR-016 calls out as
 * per-tab ("directory, search, page"), plus this tab's stable id. Mirrors
 * `StoredHtmlViewerTab` (`ts/src/workbench/types.ts`) field-for-field, aside from naming
 * (`searchText`/`selectedFile` here vs. the storage shape's `search_text`/`selected_file`). */
interface ViewerTab {
  id: number
  directory: string | null
  searchText: string
  selectedFile: string | null
}

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

function makeEmptyTab(id: number): ViewerTab {
  return { id, directory: null, searchText: '', selectedFile: null }
}

/** Reads whatever is persisted under the ADR-016 key for this schema version and restores it, or
 * falls back to a single fresh tab (still to be seeded from the generated overview's location)
 * when nothing valid is stored — ADR-016 rule 4, "the repository defaults are the fallback
 * state." Read synchronously (localStorage is synchronous) inside each state's lazy initializer
 * below, the same pattern `NotesStripRegion` uses for its own single stored field — so the first
 * render already reflects any persisted tabs, with no async hydration pass that could otherwise
 * race the persistence effect and clobber a just-loaded browser's stored state with a placeholder
 * default tab. */
function loadInitialTabs(schemaVersion: number | null): { tabs: ViewerTab[]; activeTabId: number } {
  const stored = schemaVersion !== null ? loadHtmlViewerTabs(schemaVersion) : null
  if (stored && stored.tabs.length > 0) {
    const restoredTabs = stored.tabs.map((tab) => ({
      id: tab.id,
      directory: tab.directory,
      searchText: tab.search_text,
      selectedFile: tab.selected_file,
    }))
    const activeTabId = restoredTabs.some((tab) => tab.id === stored.active_tab_id)
      ? stored.active_tab_id
      : restoredTabs[0].id
    return { tabs: restoredTabs, activeTabId }
  }
  return { tabs: [makeEmptyTab(FIRST_TAB_ID)], activeTabId: FIRST_TAB_ID }
}

/**
 * The HTML Viewer panel (REQ-007 W07/W08): generalizes the overview panel (`OverviewRegion`,
 * `phase-wb-02`) it replaces as the main slot's default in layout 1
 * (`_data/workbench/layouts/layout-1.json`) — it displays a selected page in an iframe, with the
 * generated D-System overview page (`_public/`, produced by the `d-system-overview` skill,
 * `phase-demo-04`) one selectable entry among every compatible file found recursively under
 * whatever directory is currently searched, rather than a fixed, hardcoded target.
 *
 * REQ-007 W08: tabs, styled and driven the same way as the terminal's session tabs
 * (`TerminalRegion`'s tab bar — select to switch, "×" to close, "+ New tab" capped at
 * `MAX_TABS`). Unlike a terminal session, closing a viewer tab ends nothing live — there is no
 * process or socket behind it — so close needs no confirmation step, unlike the terminal's
 * guarded tab close (REQ-006 R11). The selected directory, search text and displayed page are
 * scoped to whichever tab is active (`ViewerTab`); the three header controls below the title —
 * refresh, the searchable file dropdown, and the directory-change button — plus the kept
 * embed/open-in-tab toggle, stay shared: one instance in the header, acting on the active tab's
 * state, exactly as REQ-007 W08 specifies ("the header controls themselves are shared").
 *
 * Tab state (every open tab's directory/search/page, and which tab is active) persists under the
 * ADR-016 selections key (`ts/src/workbench/storage.ts`'s `saveHtmlViewerTabs`/
 * `loadHtmlViewerTabs`), namespaced by the schema version `StagePage` provides via
 * `useActiveSchemaVersion` — the same single version every other ADR-016 consumer
 * (`useWorkbenchLayouts`, `NotesStripRegion`) shares, via the same merge-on-write helper so this
 * component's writes never clobber theirs.
 *
 * A freshly created tab (the first tab on a browser with nothing stored, or any tab opened via
 * "+ New tab") has no directory yet; the seeding effect below fetches the generated overview
 * page's own location — never hardcoded — from the backend's `overview-location` route
 * (`src/api/routes/demo_stage.py`, `phase-demo-01`) and applies it to that tab only, once, so a
 * new tab opens exactly where the pre-tabs single-context viewer used to, before the user changes
 * anything. A tab restored from storage already has a directory (or `null` only if it was
 * persisted mid-seed) and is left alone.
 *
 * Three header controls sit right of the title, all fed by phase-wb-01's workbench read routes,
 * never a browser-native file/directory picker (ADR-015's rejected-alternative rule):
 * - Refresh: re-fetches the active tab's displayed page (a cache-busting query param on the
 *   iframe `src`, since a cached response would defeat the point of a manual refresh) and
 *   re-checks it still exists.
 * - The searchable file dropdown: every `.html`/`.svg` file found recursively under the active
 *   tab's searched directory (`GET /api/v1/workbench/search`), filtered client-side by the active
 *   tab's search text as the user types.
 * - The directory-change button: opens `DirectoryPickerDialog`, an in-app dialog fed by the
 *   one-level listing route (`GET /api/v1/workbench/list`) — repository-relative paths only —
 *   changing the active tab's directory.
 *
 * The embed/open-in-tab toggle (`D02-C1`, PLAN-021's descope rung 3) is `OverviewRegion`'s kept
 * fallback, carried over unchanged: local state here, not scoped per tab (REQ-007 W08 names only
 * directory/search/page as per-tab state) and not a prop from a parent, since the workbench
 * layout engine gives this panel's slot a fixed geometry regardless of which mode is active.
 */
export default function HtmlViewerRegion() {
  // Resolved once, from the layout files, by `useWorkbenchLayouts` and provided by `StagePage` —
  // see `schemaVersionContext.ts`. `null` only before layouts have loaded, which this component
  // never observes in practice since `Slot.tsx` mounts panels only once `loadState === 'loaded'`.
  const schemaVersion = useActiveSchemaVersion()
  const [embedded, setEmbedded] = useState(true)
  // Read once, on this component instance's first render only (guarded below) — `useRef`'s own
  // initial-value argument is otherwise re-evaluated on every render, which would mean a
  // localStorage read (and JSON parse) on every render just to be discarded after the first.
  const initialStateRef = useRef<{ tabs: ViewerTab[]; activeTabId: number } | null>(null)
  if (initialStateRef.current === null) {
    initialStateRef.current = loadInitialTabs(schemaVersion)
  }
  const [tabs, setTabs] = useState<ViewerTab[]>(() => initialStateRef.current!.tabs)
  const [activeTabId, setActiveTabId] = useState<number>(() => initialStateRef.current!.activeTabId)
  const nextTabIdRef = useRef(Math.max(0, ...initialStateRef.current!.tabs.map((tab) => tab.id)) + 1)
  const [searchText, setSearchTextState] = useState(
    () => tabs.find((tab) => tab.id === activeTabId)?.searchText ?? '',
  )
  const [files, setFiles] = useState<DirectoryEntry[]>([])
  const [filesLoadState, setFilesLoadState] = useState<FilesLoadState>('loading')
  const [pageState, setPageState] = useState<PageState>('idle')
  const [refreshToken, setRefreshToken] = useState(0)

  const activeTab = tabs.find((tab) => tab.id === activeTabId) ?? null

  function updateTab(id: number, patch: Partial<Omit<ViewerTab, 'id'>>) {
    setTabs((previous) => previous.map((tab) => (tab.id === id ? { ...tab, ...patch } : tab)))
  }

  // Keep the search input's own state in sync with whichever tab is active — the input is a
  // shared header control (one `<input>`), but the text it shows and writes is per-tab (REQ-007
  // W08). Switching tabs swaps the displayed text; typing writes back to the active tab below.
  useEffect(() => {
    setSearchTextState(activeTab?.searchText ?? '')
  }, [activeTabId])

  // Seed any tab that has no directory yet — a freshly created tab, never one restored from
  // storage with a real value already — from the generated overview page's own location, once
  // per tab id (`seedingTabIdsRef` guards against re-seeding a tab already in flight or already
  // seeded, since this effect re-runs on every `tabs` change).
  const seedingTabIdsRef = useRef<Set<number>>(new Set())
  useEffect(() => {
    const pendingIds = tabs
      .filter((tab) => tab.directory === null)
      .map((tab) => tab.id)
      .filter((id) => !seedingTabIdsRef.current.has(id))
    if (pendingIds.length === 0) return
    pendingIds.forEach((id) => {
      seedingTabIdsRef.current.add(id)
      fetch(OVERVIEW_LOCATION_URL)
        .then((response) => {
          if (!response.ok) throw new Error(`status ${response.status}`)
          return response.json() as Promise<{ path: string }>
        })
        .then(({ path }) => {
          setTabs((previous) =>
            previous.map((tab) =>
              tab.id === id && tab.directory === null
                ? { ...tab, directory: dirname(path), selectedFile: path }
                : tab,
            ),
          )
        })
        .catch(() => {
          setTabs((previous) =>
            previous.map((tab) => (tab.id === id && tab.directory === null ? { ...tab, directory: '.' } : tab)),
          )
        })
    })
  }, [tabs])

  // The recursive compatible-file list for the active tab's currently searched directory
  // (REQ-007 W07). Text filtering happens client-side against this same fetched list, below — no
  // round trip per keystroke. Re-fetches whenever the active tab or its directory changes.
  useEffect(() => {
    if (activeTab === null || activeTab.directory === null) return
    let cancelled = false
    setFilesLoadState('loading')
    fetch(buildSearchUrl(activeTab.directory))
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab?.id, activeTab?.directory])

  // Confirm the active tab's selected page actually exists before rendering it — a selection can
  // point at a file that has since been removed, and `refreshToken` re-runs this same check for
  // the refresh control (REQ-007 W07: "a refresh button re-fetching the current page").
  useEffect(() => {
    if (activeTab === null || !activeTab.selectedFile) {
      setPageState('idle')
      return
    }
    let cancelled = false
    setPageState('checking')
    fetch(`${WORKBENCH_FILE_PREFIX}${activeTab.selectedFile}`, { method: 'HEAD', cache: 'no-store' })
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
  }, [activeTab?.id, activeTab?.selectedFile, refreshToken])

  // Persist every open tab's directory/search/page and which tab is active (REQ-007 W08 / ADR-016
  // rule 3) — best-effort, merged into the shared key so this write never clobbers the layout
  // engine's or the notes strip's own stored fields (`saveHtmlViewerTabs`).
  useEffect(() => {
    if (schemaVersion === null) return
    saveHtmlViewerTabs(
      schemaVersion,
      tabs.map((tab) => ({
        id: tab.id,
        directory: tab.directory,
        search_text: tab.searchText,
        selected_file: tab.selectedFile,
      })),
      activeTabId,
    )
  }, [schemaVersion, tabs, activeTabId])

  const addTab = () => {
    if (tabs.length >= MAX_TABS) return
    const id = nextTabIdRef.current
    nextTabIdRef.current += 1
    setTabs((previous) => [...previous, makeEmptyTab(id)])
    setActiveTabId(id)
  }

  // No confirmation step — unlike the terminal's guarded tab close (REQ-006 R11), a viewer tab
  // has no live process or socket behind it, so closing one ends nothing (this dispatch's own
  // instruction: "close needs no confirmation here — nothing terminates").
  const closeTab = (id: number) => {
    const index = tabs.findIndex((tab) => tab.id === id)
    const next = tabs.filter((tab) => tab.id !== id)
    setTabs(next)
    if (activeTabId === id && next.length > 0) {
      setActiveTabId(next[Math.max(0, Math.min(index, next.length - 1))].id)
    }
  }

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchText.trim().toLowerCase()),
  )

  const embedSrc = activeTab?.selectedFile
    ? `${WORKBENCH_FILE_PREFIX}${activeTab.selectedFile}?v=${refreshToken}`
    : null
  const openTabHref = activeTab?.selectedFile ? `${WORKBENCH_FILE_PREFIX}${activeTab.selectedFile}` : null

  return (
    <section className="stage-region stage-region--html-viewer" aria-label="HTML Viewer">
      <header className="stage-region__header">
        <h2>HTML Viewer</h2>
        <div className="stage-html-viewer__controls">
          <button
            type="button"
            className="stage-html-viewer__refresh"
            aria-label="Refresh the current page"
            disabled={!activeTab?.selectedFile}
            onClick={() => setRefreshToken((value) => value + 1)}
          >
            ⟳ Refresh
          </button>

          <Popover
            triggerLabel={activeTab?.selectedFile ? basename(activeTab.selectedFile) : 'Choose a file ▾'}
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
                  onChange={(event) => {
                    const value = event.target.value
                    setSearchTextState(value)
                    if (activeTab) updateTab(activeTab.id, { searchText: value })
                  }}
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
                            if (activeTab) updateTab(activeTab.id, { selectedFile: file.path })
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

          {activeTab && activeTab.directory !== null ? (
            <DirectoryPickerDialog
              initialDirectory={activeTab.directory}
              onSelectDirectory={(directory) => updateTab(activeTab.id, { directory })}
            />
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
      <div className="stage-region__body stage-region__body--html-viewer">
        <div className="stage-html-viewer__tabbar" role="tablist" aria-label="HTML Viewer tabs">
          {tabs.map((tab, index) => (
            <div
              key={tab.id}
              className={
                'stage-html-viewer__tab' + (tab.id === activeTabId ? ' stage-html-viewer__tab--active' : '')
              }
            >
              <button
                type="button"
                role="tab"
                aria-selected={tab.id === activeTabId}
                className="stage-html-viewer__tab-select"
                onClick={() => setActiveTabId(tab.id)}
              >
                Tab {index + 1}
              </button>
              <button
                type="button"
                className="stage-html-viewer__tab-close"
                aria-label={`Close tab ${index + 1}`}
                onClick={() => closeTab(tab.id)}
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            className="stage-html-viewer__tab-new"
            aria-label="New HTML Viewer tab"
            disabled={tabs.length >= MAX_TABS}
            onClick={addTab}
          >
            + New tab
          </button>
        </div>
        <div
          className={
            'stage-html-viewer__content' +
            (embedded && pageState === 'ready' ? ' stage-html-viewer__content--overview' : '')
          }
        >
          {tabs.length === 0 ? (
            <p className="stage-placeholder-text">No HTML Viewer tabs. Use "+ New tab" to open one.</p>
          ) : activeTab === null ? null : activeTab.directory === null ? (
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
              Selected page is absent — <code>{activeTab.selectedFile}</code> does not exist.
            </p>
          ) : embedded ? (
            // `sandbox=""` (no tokens, i.e. every restriction applied — no scripts, no
            // same-origin access, no top navigation, no forms/popups): unlike
            // `OverviewRegion`'s iframe, which always embeds one fixed repo-generated page, this
            // panel embeds whatever `.html`/`.svg` the workbench search/listing routes turn up
            // anywhere non-ignored in the repository (REQ-007 W07) — a script inside any of
            // those, served same-origin via `/workbench-file/...`, would otherwise run with the
            // app's own privileges: read/write its `localStorage` (the ADR-016 selections key),
            // reach `window.parent`, or make same-origin fetches to workbench routes including
            // `POST /api/v1/workbench/reveal` (which spawns the OS opener). The generated
            // overview page this panel also renders (W04-W) has no `<script>` tags, so it
            // renders unaffected by `sandbox` blocking script execution.
            <iframe
              className="stage-overview__iframe"
              src={embedSrc ?? undefined}
              title="HTML Viewer"
              sandbox=""
            />
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
      </div>
    </section>
  )
}
