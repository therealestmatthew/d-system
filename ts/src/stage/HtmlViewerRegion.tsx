import { useEffect, useRef, useState } from 'react'
import DirectoryPickerDialog from './DirectoryPickerDialog'
import Popover from './Popover'
import { useActiveSchemaVersion } from '../workbench/schemaVersionContext'
import { loadHtmlViewerTabs, saveHtmlViewerTabs } from '../workbench/storage'
import { viewerBridge, type BatchReceipt, type ViewerBridgeHandle } from './panelBridge'
import { fetchWorkbench } from './useTerminalEnabled'
import { COMPATIBLE_EXTENSIONS, isViewerCompatible } from './compatibleExtensions'
import { planOpenFiles } from './viewerPlacement'

const OVERVIEW_LOCATION_URL = '/api/v1/demo/stage/overview-location'
const SEARCH_URL = '/api/v1/workbench/search'
// Mirrors `ts/vite.config.ts`'s `serveRepositoryFiles` dev-server plugin, which serves any
// non-ignored repository file at this prefix — the workbench search/listing routes
// (`src/api/routes/workbench.py`, `phase-wb-01`) report paths only, never content (ADR-015), so
// this is what actually fetches the bytes an iframe can render.
const WORKBENCH_FILE_PREFIX = '/workbench-file/'

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

/** The file route (`serveRepositoryFiles` in `vite.config.ts`) sets `Content-Security-Policy:
 * sandbox` on every response that serves a file (the 403 and 404 refusals do not carry it, and
 * are not `ok` anyway). The dev server's single-page fallback answers any unregistered path (the route is registered only when
 * `D_SYSTEM_DEMO_TERMINAL=1` in the frontend process) with 200 and the application shell and
 * never sets that header, so a bare `response.ok` cannot tell a file from the shell (REQ-012 R29,
 * idea 000555). Requiring the header is the same-origin signal that the response came from the
 * file route; it is readable here because the request is same-origin. */
function isServedByFileRoute(response: Response): boolean {
  if (!response.ok) return false
  const policy = response.headers.get('Content-Security-Policy') ?? ''
  return policy.split(/[;,]/).some((directive) => directive.trim().toLowerCase().split(/\s+/)[0] === 'sandbox')
}

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

/** The URL a tab's file is opened at outside the workbench: the same `/workbench-file/` URL the
 * "Open page in a new tab" link uses, so the route renders markdown and wraps images there exactly
 * as it does for the panel's iframe (idea 000119's route-side ruling), with the route's
 * `Content-Security-Policy: sandbox` applying to the top-level navigation (REQ-012 R02). */
function fileHref(path: string | null): string | null {
  return path ? `${WORKBENCH_FILE_PREFIX}${path}` : null
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
 * `phase-wb-02`) it replaces as the primary slot's default in layout 1
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
 * - The searchable file dropdown: every compatible file (`COMPATIBLE_EXTENSIONS` above — `.html`,
 *   `.svg`, and the six served image formats) found recursively under the active tab's searched
 *   directory (`GET /api/v1/workbench/search`), filtered client-side by the active tab's search
 *   text as the user types.
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
  // Read once, on this component instance's first render only — a lazy `useState` initializer,
  // so the localStorage read (and JSON parse) is not repeated on every render just to be
  // discarded after the first.
  const [initialState] = useState(() => loadInitialTabs(schemaVersion))
  const [tabs, setTabs] = useState<ViewerTab[]>(initialState.tabs)
  const [activeTabId, setActiveTabId] = useState<number>(initialState.activeTabId)
  const nextTabIdRef = useRef(Math.max(0, ...initialState.tabs.map((tab) => tab.id)) + 1)
  const [files, setFiles] = useState<DirectoryEntry[]>([])
  // Each settled result names the request it belongs to, so a tab, directory, page or refresh
  // change reads as 'loading'/'checking' until its own fetch settles, without resetting state
  // inside the effects below.
  const [settledFiles, setSettledFiles] = useState<{ key: string; state: 'loaded' | 'error' } | null>(null)
  const [settledPage, setSettledPage] = useState<{
    key: string
    state: Exclude<PageState, 'idle' | 'checking'>
  } | null>(null)
  const [refreshToken, setRefreshToken] = useState(0)

  const activeTab = tabs.find((tab) => tab.id === activeTabId) ?? null
  // The search input is a shared header control (one `<input>`), but the text it shows and writes
  // is the active tab's own (REQ-007 W08), so switching tabs swaps the displayed text.
  const searchText = activeTab?.searchText ?? ''
  const activeDirectory = activeTab?.directory ?? null
  const activeSelectedFile = activeTab?.selectedFile ?? null
  const filesKey = activeTab === null ? null : `${activeTab.id}|${activeTab.directory}`
  const filesLoadState: FilesLoadState =
    settledFiles !== null && settledFiles.key === filesKey ? settledFiles.state : 'loading'
  const pageKey =
    activeTab === null || !activeTab.selectedFile
      ? null
      : `${activeTab.id}|${activeTab.selectedFile}|${refreshToken}`
  const pageState: PageState =
    pageKey === null
      ? 'idle'
      : settledPage !== null && settledPage.key === pageKey
        ? settledPage.state
        : 'checking'

  // The tabs as of the latest committed render, plus any `openFiles` call since. `openFiles` must
  // answer synchronously with a receipt (ADR-029 section 6 point 2) and two calls can land before
  // React re-renders, so the placement plan is computed from this ref, not from the render's
  // `tabs` closure, and the ref is advanced by the same change that is queued on the state.
  const tabsRef = useRef<ViewerTab[]>(tabs)
  useEffect(() => {
    tabsRef.current = tabs
  }, [tabs])

  /** ADR-029 section 6 point 8: opens an ordered set of files. Fills empty tabs first, then adds
   * tabs up to `MAX_TABS`, never replaces a tab that holds a page, and declines the rest. The first
   * delivered file's tab becomes active. */
  function openFiles(paths: string[]): BatchReceipt {
    const plan = planOpenFiles(tabsRef.current, paths, {
      maxTabs: MAX_TABS,
      nextTabId: nextTabIdRef.current,
      isCompatible: isViewerCompatible,
    })
    if (plan.assignments.length === 0) return plan.receipt
    nextTabIdRef.current += plan.assignments.filter((assignment) => assignment.newTab).length
    const apply = (previous: ViewerTab[]): ViewerTab[] => {
      const next = [...previous]
      for (const { tabId, path, newTab } of plan.assignments) {
        if (newTab) {
          next.push({ id: tabId, directory: dirname(path), searchText: '', selectedFile: path })
          continue
        }
        const index = next.findIndex((tab) => tab.id === tabId)
        if (index === -1) continue
        // A tab still waiting for the overview-location seed has no directory; give it one so the
        // seed (which only fills a tab whose directory is null) does not replace this file.
        next[index] = {
          ...next[index],
          selectedFile: path,
          directory: next[index].directory ?? dirname(path),
        }
      }
      return next
    }
    tabsRef.current = apply(tabsRef.current)
    setTabs(apply)
    setActiveTabId(plan.assignments[0].tabId)
    return plan.receipt
  }

  function updateTab(id: number, patch: Partial<Omit<ViewerTab, 'id'>>) {
    setTabs((previous) => previous.map((tab) => (tab.id === id ? { ...tab, ...patch } : tab)))
  }

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
    if (activeDirectory === null || filesKey === null) return
    let cancelled = false
    fetchWorkbench(buildSearchUrl(activeDirectory))
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<DirectoryEntry[]>
      })
      .then((body) => {
        if (cancelled) return
        setFiles(body)
        setSettledFiles({ key: filesKey, state: 'loaded' })
      })
      .catch(() => {
        if (!cancelled) setSettledFiles({ key: filesKey, state: 'error' })
      })
    return () => {
      cancelled = true
    }
  }, [filesKey, activeDirectory])

  // Confirm the active tab's selected page actually exists before rendering it — a selection can
  // point at a file that has since been removed, and `refreshToken` re-runs this same check for
  // the refresh control (REQ-007 W07: "a refresh button re-fetching the current page").
  useEffect(() => {
    if (!activeSelectedFile || pageKey === null) return
    let cancelled = false
    fetch(`${WORKBENCH_FILE_PREFIX}${activeSelectedFile}`, { method: 'HEAD', cache: 'no-store' })
      .then((response) => {
        if (!cancelled) {
          setSettledPage({ key: pageKey, state: isServedByFileRoute(response) ? 'ready' : 'missing' })
        }
      })
      .catch(() => {
        if (!cancelled) setSettledPage({ key: pageKey, state: 'error' })
      })
    return () => {
      cancelled = true
    }
  }, [pageKey, activeSelectedFile])

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

  // REQ-007 W09: publishes this instance's live tabs — and a way to open a path into one of them
  // — to the File Browser's right-click context menu, which is a sibling panel with no other
  // route to reach this one (`panelBridge.ts`'s own doc comment explains why a bridge is needed
  // at all). Re-registers on every `tabs` change so the bridge's tab list (and each tab's label,
  // which is derived from array position) never lags the panel actually on screen; unregisters on
  // unmount, e.g. the layout's primary slot swapping away from `html-viewer` (layout 2 also admits
  // `overview`), so a stale registration never outlives the panel it describes.
  useEffect(() => {
    const handle: ViewerBridgeHandle = {
      tabs: tabs.map((tab, index) => ({ id: tab.id, label: `Tab ${index + 1}` })),
      openInTab: (tabId, path) => {
        updateTab(tabId, { selectedFile: path })
        setActiveTabId(tabId)
      },
      openFiles: (paths) => openFiles(paths),
    }
    viewerBridge.register(handle)
    return () => viewerBridge.unregister(handle)
  }, [tabs])

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
  const openTabHref = fileHref(activeTab?.selectedFile ?? null)

  // REQ-012 R01: opens the given tab's own file (not necessarily the active tab's) in a new
  // browser tab. A tab with no file selected has nothing to open and does nothing.
  const openTabInBrowser = (tab: ViewerTab) => {
    const href = fileHref(tab.selectedFile)
    if (href !== null) window.open(href, '_blank', 'noopener,noreferrer')
  }

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
                    if (activeTab) updateTab(activeTab.id, { searchText: event.target.value })
                  }}
                />
                {filesLoadState === 'loading' ? (
                  <p className="stage-placeholder-text" role="status">Searching…</p>
                ) : filesLoadState === 'error' ? (
                  <p className="stage-placeholder-text stage-placeholder-text--absent" role="alert">
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
                // Double-click opens this tab's file in a new browser tab (REQ-012 R01). The two
                // clicks still select the tab first, which is harmless. Keyboard equivalent:
                // Shift+Enter or Shift+Space on the focused tab. Plain Enter/Space keep selecting.
                onDoubleClick={() => openTabInBrowser(tab)}
                onKeyDown={(event) => {
                  if (event.shiftKey && (event.key === 'Enter' || event.key === ' ')) {
                    event.preventDefault()
                    openTabInBrowser(tab)
                  }
                }}
                // A native button activates on Space at keyup, which Firefox does not cancel from
                // the keydown's preventDefault; cancel it here so Shift+Space only opens the file.
                onKeyUp={(event) => {
                  if (event.shiftKey && event.key === ' ') event.preventDefault()
                }}
                aria-keyshortcuts="Shift+Enter Shift+Space"
                title="Double-click, or press Shift+Enter, to open this tab's file in a new browser tab"
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
            <p className="stage-placeholder-text" role="status">Locating the generated overview page…</p>
          ) : pageState === 'idle' ? (
            <p className="stage-placeholder-text">
              Select a file from the dropdown above, or a directory to search.
            </p>
          ) : pageState === 'checking' ? (
            <p className="stage-placeholder-text" role="status">Checking the selected page…</p>
          ) : pageState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent" role="alert">
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
            // panel embeds whatever compatible file (`COMPATIBLE_EXTENSIONS` above) the workbench
            // search/listing routes turn up anywhere non-ignored in the repository — a script
            // inside an `.html` or `.svg` among those, served same-origin via
            // `/workbench-file/...`, would otherwise run with the app's own privileges: read/write
            // its `localStorage` (the ADR-016 selections key), reach `window.parent`, or make
            // same-origin fetches to workbench routes including `POST /api/v1/workbench/reveal`
            // (which spawns the OS opener). The generated overview page this panel also renders
            // (W04-W) has no `<script>` tags, so it renders unaffected by `sandbox` blocking
            // script execution — and the six image formats in the list carry no script capability
            // at all, so `sandbox` has nothing to neutralize there; it stays applied uniformly
            // regardless of which compatible type is on screen.
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
