import { useEffect, useMemo, useState, type MouseEvent as ReactMouseEvent } from 'react'
import DirectoryPickerDialog from './DirectoryPickerDialog'
import FileTreeContextMenu from './FileTreeContextMenu'
import { COMPATIBLE_EXTENSIONS } from './HtmlViewerRegion'
import { useTerminalBridge, useViewerBridge } from './panelBridge'

const SEARCH_URL = '/api/v1/workbench/search'
const REVEAL_URL = '/api/v1/workbench/reveal'
const ABSOLUTE_PATH_URL = '/api/v1/workbench/absolute-path'

interface DirectoryEntry {
  name: string
  path: string
  is_dir: boolean
}

/** `GET /absolute-path`'s response shape (`src/api/routes/workbench.py`'s `AbsolutePathResult`). */
interface AbsolutePathResult {
  absolute_path: string
}

type LoadState = 'loading' | 'loaded' | 'error'

/** The right-clicked tree entry the context menu is currently open for, and the pointer position
 * it should open at. `null` means no menu is open. */
interface ContextMenuState {
  x: number
  y: number
  node: FileTreeNode
}

/** The outcome of the most recent context-menu action, shown as a single in-place status line
 * (REQ-007 W09's "surface its refusal … as a visible message", generalized to every action's
 * outcome rather than just the reveal refusal it was written for). */
interface ActionStatus {
  kind: 'info' | 'error'
  message: string
}

/** One node of the client-built file tree (REQ-007 W09). `path` is always repository-relative,
 * matching what `phase-wb-01`'s routes take and return. Directories carry their descendants;
 * files never do. Built entirely from a flat file list (see `buildTree` below) — the backend has
 * no tree-shaped route, only one-level listing (`GET /list`, used by `DirectoryPickerDialog`) and
 * recursive-file search (`GET /search`, used here). */
interface FileTreeNode {
  name: string
  path: string
  isDir: boolean
  children: FileTreeNode[]
}

/** A File Browser preset (REQ-007 W09: "a documentation-explorer mode … is a File Browser
 * configuration, not a separate panel"): selecting one sets the context folder and the file-type
 * filter, nothing else — the panel underneath is identical either way. New presets are added
 * here, never as new panel types in `panelRegistry.tsx`. */
interface FileBrowserPreset {
  id: string
  label: string
  directory: string
  typeFilter: string
}

const PRESETS: FileBrowserPreset[] = [
  {
    id: 'documentation',
    label: 'Documentation (plans, decisions, requirements, …)',
    directory: 'docs',
    typeFilter: '.md',
  },
]

const NO_FILTER = 'all'

function buildSearchUrl(directory: string): string {
  const params = new URLSearchParams({ path: directory })
  return `${SEARCH_URL}?${params.toString()}`
}

/** The extension `_matches_filters` on the backend would compute for `name` (lowercased, leading
 * dot kept), or `null` for an extension-less name — including a dotfile like `.gitignore`, whose
 * single leading dot is not treated as an extension (`lastIndexOf('.') <= 0`). */
function extensionOf(name: string): string | null {
  const index = name.lastIndexOf('.')
  if (index <= 0) return null
  return name.slice(index).toLowerCase()
}

function rootLabel(directory: string): string {
  if (directory === '.' || directory === '') return 'repository root'
  const index = directory.lastIndexOf('/')
  return index === -1 ? directory : directory.slice(index + 1)
}

/** Turns a flat, already-filtered file list (every path repository-relative and rooted under
 * `directory`) into a nested tree. A directory appears in the result only if at least one file
 * under it survived filtering — REQ-007 W09's "hiding folders with no matches" falls out of this
 * for free, since a directory node is created only while inserting a file that passed through it,
 * never speculatively. */
function buildTree(directory: string, files: DirectoryEntry[]): FileTreeNode {
  const root: FileTreeNode = { name: rootLabel(directory), path: directory, isDir: true, children: [] }
  const prefix = directory === '.' || directory === '' ? '' : `${directory}/`

  for (const file of files) {
    const relative = file.path.startsWith(prefix) ? file.path.slice(prefix.length) : file.path
    const segments = relative.split('/').filter(Boolean)
    if (segments.length === 0) continue

    let current = root
    let currentPath = directory
    segments.forEach((segment, index) => {
      currentPath = currentPath === '.' || currentPath === '' ? segment : `${currentPath}/${segment}`
      const isLast = index === segments.length - 1
      if (isLast) {
        current.children.push({ name: segment, path: currentPath, isDir: false, children: [] })
        return
      }
      let child = current.children.find((candidate) => candidate.isDir && candidate.name === segment)
      if (!child) {
        child = { name: segment, path: currentPath, isDir: true, children: [] }
        current.children.push(child)
      }
      current = child
    })
  }

  sortTree(root)
  return root
}

/** Directories before files, both alphabetical (case-insensitive) — same ordering
 * `DirectoryPickerDialog` and `HtmlViewerRegion`'s file dropdown already use. */
function sortTree(node: FileTreeNode): void {
  node.children.sort((a, b) => {
    if (a.isDir !== b.isDir) return a.isDir ? -1 : 1
    return a.name.localeCompare(b.name)
  })
  node.children.forEach((child) => {
    if (child.isDir) sortTree(child)
  })
}

function collectDirPaths(node: FileTreeNode, into: Set<string>): void {
  node.children.forEach((child) => {
    if (child.isDir) {
      into.add(child.path)
      collectDirPaths(child, into)
    }
  })
}

/** One level of the tree, rendered as a nested `<ul>` so each recursive call indents one step
 * further via `.stage-file-browser__tree-list`'s own `padding-left` — no per-node depth math. */
function TreeLevel({
  nodes,
  expandedPaths,
  onToggle,
  onContextMenu,
  root = false,
}: {
  nodes: FileTreeNode[]
  expandedPaths: Set<string>
  onToggle: (path: string) => void
  /** REQ-007 W09: right-click opens the context menu for the node under the pointer — attached
   * to every entry, directory and file alike, at every depth. */
  onContextMenu: (event: ReactMouseEvent, node: FileTreeNode) => void
  /** The outermost call (the context folder's own children) skips the indent every deeper level
   * gets, so the top-level entries sit flush with the tree container instead of one step in. */
  root?: boolean
}) {
  return (
    <ul
      className={
        'stage-file-browser__tree-list' + (root ? ' stage-file-browser__tree-list--root' : '')
      }
      role="group"
    >
      {nodes.map((node) =>
        node.isDir ? (
          <li key={node.path} className="stage-file-browser__tree-item">
            <button
              type="button"
              className="stage-file-browser__tree-toggle"
              aria-expanded={expandedPaths.has(node.path)}
              onClick={() => onToggle(node.path)}
              onContextMenu={(event) => onContextMenu(event, node)}
            >
              <span aria-hidden="true">{expandedPaths.has(node.path) ? '▾' : '▸'}</span> {node.name}/
            </button>
            {expandedPaths.has(node.path) ? (
              <TreeLevel
                nodes={node.children}
                expandedPaths={expandedPaths}
                onToggle={onToggle}
                onContextMenu={onContextMenu}
              />
            ) : null}
          </li>
        ) : (
          <li key={node.path} className="stage-file-browser__tree-item">
            <span
              className="stage-file-browser__tree-file"
              title={node.path}
              onContextMenu={(event) => onContextMenu(event, node)}
            >
              {node.name}
            </span>
          </li>
        ),
      )}
    </ul>
  )
}

/**
 * The File Browser panel (REQ-007 W09). Shows a collapsible treeview of subdirectories and files
 * under a context folder chosen through the same in-app directory dialog `HtmlViewerRegion`
 * already uses (`DirectoryPickerDialog`, the `phase-wb-04` pattern over `phase-wb-01`'s one-level
 * listing route), filterable by text search and by file type, hiding folders with no matches, and
 * right-clickable for a five-action context menu (`FileTreeContextMenu.tsx`, this comment's own
 * later section) on every entry.
 *
 * Fed by the recursive search route (`GET /api/v1/workbench/search`, `phase-wb-01`) fetched once
 * per context-folder change with no `q`/`ext` query params — every non-ignored file under the
 * folder, exactly `HtmlViewerRegion`'s own fetch-once-filter-client-side pattern — so typing in
 * the search box or switching the type dropdown never re-hits the backend. The client then (a)
 * filters that flat file list by name-substring and by extension and (b) builds a tree from
 * whatever survives (`buildTree`): a directory is only ever created while inserting a file that
 * passed both filters, so an unmatched folder is never even instantiated as a node, let alone
 * rendered — "hiding folders with no matches" falls out of the data structure rather than a
 * separate visibility pass.
 *
 * Expansion state (`expandedPaths`) is manual — a fresh browse starts with only the context
 * folder's immediate children visible, deeper levels collapsed until clicked — except while a
 * text or type filter is active, when every directory left in the (already-filtered) tree is
 * force-expanded too, so a match is never hidden behind a collapsed ancestor the filter itself
 * left in place.
 *
 * The documentation-explorer mode REQ-007 W09 names is not a separate panel: `PRESETS` above is
 * the whole of it — one entry that sets the context folder to `docs` and the type filter to
 * `.md`, applied through the same `directory`/`typeFilter` state this panel already carries for
 * manual browsing. Manually changing either one (via the directory dialog or the type dropdown)
 * simply leaves no preset's configuration matching current state, so the preset `<select>` shows
 * "Custom" — computed from current state (`currentPresetId`), never tracked as separate state
 * that could drift from it.
 *
 * The context menu (REQ-007 W09's second half): right-clicking any tree entry opens
 * `FileTreeContextMenu` at the pointer with five actions — reveal in file explorer, open in HTML
 * Viewer (compatible files only, nested submenu choosing the target tab), copy relative path,
 * copy absolute path, and inject path into terminal. Four of the five are wired here directly (a
 * `POST /reveal` call, `navigator.clipboard.writeText` for the relative path, a `GET
 * /absolute-path` call whose result is likewise handed to `navigator.clipboard.writeText`, and
 * the terminal bridge's `injectPath`); "open in HTML Viewer" and "inject path into terminal"
 * reach a *different*, independently-mounted panel, which this component has no other way to
 * reach — see `panelBridge.ts`'s doc comment for why a small cross-panel registry exists at all.
 * Every outcome (a reveal refusal's message, a copy confirmation, an injection confirmation) is
 * shown in `actionStatus`, a single-line status this panel owns, rather than a transient
 * `alert()` — consistent with this app's general posture of an in-place message over a native
 * dialog.
 */
export default function FileBrowserRegion() {
  const [contextFolder, setContextFolder] = useState('.')
  const [typeFilter, setTypeFilter] = useState(NO_FILTER)
  const [searchText, setSearchText] = useState('')
  const [entries, setEntries] = useState<DirectoryEntry[]>([])
  // The folder `entries` was actually fetched for. `contextFolder` changing is what triggers the
  // next fetch (the effect below), but React commits at least one render in between — new
  // `contextFolder`, still-old `entries` — before that effect's `setLoadState('loading')` takes
  // effect. `buildTree(contextFolder, entries)` during that one stale render mismatches directory
  // against file list: an old-folder entry whose path doesn't start with the new prefix falls
  // through `buildTree`'s unstripped-path branch and can compute a path that collides with a
  // genuine entry already inside the new folder (e.g. a stale top-level `README.md` under a new
  // `contextFolder` of `docs` computes to `docs/README.md`, colliding with the real
  // `docs/README.md`) — React's "two children with the same key" warning, logged at that commit
  // regardless of how quickly the following render replaces it with "Loading…". Comparing this
  // against `contextFolder` below lets the render treat that one stale commit as loading too,
  // instead of ever building a tree from a directory/file-list pair that don't match.
  const [entriesFolder, setEntriesFolder] = useState<string>('.')
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null)
  const [actionStatus, setActionStatus] = useState<ActionStatus | null>(null)

  // REQ-007 W09's remaining two actions reach a different, independently-mounted panel — see
  // `panelBridge.ts`'s doc comment. `null` here means "that panel is not currently on screen",
  // which `FileTreeContextMenu` renders as a disabled/hidden item rather than a broken action.
  const terminalHandle = useTerminalBridge()
  const viewerHandle = useViewerBridge()

  useEffect(() => {
    let cancelled = false
    setLoadState('loading')
    fetch(buildSearchUrl(contextFolder))
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<DirectoryEntry[]>
      })
      .then((body) => {
        if (cancelled) return
        setEntries(body)
        setEntriesFolder(contextFolder)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [contextFolder])

  // A freshly browsed folder starts fully collapsed below its own immediate children — a
  // previous folder's expanded paths otherwise carry over as harmless-but-stale entries that
  // never match anything in the new tree; clearing them is just tidiness.
  useEffect(() => {
    setExpandedPaths(new Set())
  }, [contextFolder])

  const availableExtensions = useMemo(() => {
    const extensions = new Set<string>()
    entries.forEach((entry) => {
      const ext = extensionOf(entry.name)
      if (ext) extensions.add(ext)
    })
    return Array.from(extensions).sort()
  }, [entries])

  const filtersActive = searchText.trim() !== '' || typeFilter !== NO_FILTER

  const filteredEntries = useMemo(() => {
    const needle = searchText.trim().toLowerCase()
    return entries.filter((entry) => {
      if (typeFilter !== NO_FILTER && extensionOf(entry.name) !== typeFilter) return false
      if (needle && !entry.name.toLowerCase().includes(needle)) return false
      return true
    })
  }, [entries, searchText, typeFilter])

  // `filteredEntries` was filtered from `entries`, which belongs to `entriesFolder`, not
  // necessarily `contextFolder` — see the field comment above `entriesFolder`'s declaration. Feed
  // `buildTree` an empty list rather than `filteredEntries` while they disagree, so a stale-folder
  // entry list is never turned into a tree keyed by the new folder's prefix; the render below
  // shows "Loading…" for that same window instead of this (empty, never displayed) tree.
  const tree = useMemo(
    () => buildTree(contextFolder, entriesFolder === contextFolder ? filteredEntries : []),
    [contextFolder, entriesFolder, filteredEntries],
  )

  const effectiveExpandedPaths = useMemo(() => {
    if (!filtersActive) return expandedPaths
    const forced = new Set(expandedPaths)
    collectDirPaths(tree, forced)
    return forced
  }, [expandedPaths, filtersActive, tree])

  const toggleExpanded = (path: string) => {
    setExpandedPaths((previous) => {
      const next = new Set(previous)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }

  const currentPresetId =
    PRESETS.find((preset) => preset.directory === contextFolder && preset.typeFilter === typeFilter)?.id ??
    'custom'

  // A stale menu anchored to an entry from the previous context folder would otherwise linger
  // over the newly loaded tree — close it (and any leftover status) the moment the browsed folder
  // changes, the same "fresh browse resets transient state" rule the expansion-clearing effect
  // above already applies.
  useEffect(() => {
    setContextMenu(null)
  }, [contextFolder])

  function openContextMenu(event: ReactMouseEvent, node: FileTreeNode): void {
    event.preventDefault()
    setContextMenu({ x: event.clientX, y: event.clientY, node })
  }

  // REQ-007 W09 action 1: POST the entry's repo-relative path to phase-wb-01's reveal route
  // (`src/api/routes/workbench.py`, `POST /reveal`) and surface its refusal — a repository-escape
  // or an excluded (`_private/`/gitignored) path, ADR-015 rule 5 — as a visible message rather
  // than a silent failure. A success spawns the OS file-manager opener as a side effect; this
  // reports that it was requested, not that the opener window has appeared (the route itself
  // does not wait for that either).
  async function handleReveal(node: FileTreeNode): Promise<void> {
    try {
      const response = await fetch(REVEAL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: node.path }),
      })
      if (response.ok) {
        setActionStatus({ kind: 'info', message: `Reveal requested for "${node.path}".` })
        return
      }
      let detail = `request failed (status ${response.status})`
      try {
        const body: unknown = await response.json()
        if (
          typeof body === 'object' &&
          body !== null &&
          typeof (body as { detail?: unknown }).detail === 'string'
        ) {
          detail = (body as { detail: string }).detail
        }
      } catch {
        // Falls through with the status-only message above — the body was not JSON with a
        // `detail` string, which the reveal route always sends on refusal, but this stays
        // defensive against anything else fronting the API in a dev proxy misconfiguration.
      }
      setActionStatus({ kind: 'error', message: `Reveal refused: ${detail}` })
    } catch {
      setActionStatus({ kind: 'error', message: 'Reveal failed: could not reach the backend.' })
    }
  }

  // REQ-007 W09 action 3: the exact repo-relative string the tree already carries (`node.path`
  // is `DirectoryEntry.path` verbatim, as served by `/search` — REQ-007 W09's "as served by the
  // API").
  function handleCopyRelativePath(node: FileTreeNode): void {
    navigator.clipboard.writeText(node.path).then(
      () => setActionStatus({ kind: 'info', message: `Copied relative path: ${node.path}` }),
      () =>
        setActionStatus({
          kind: 'error',
          message: 'Could not copy the relative path — the clipboard was not reachable.',
        }),
    )
  }

  // REQ-007 W09 action 4: GET the entry's repo-relative path against phase-wb-05's
  // `/absolute-path` route (`src/api/routes/workbench.py`, `AbsolutePathResult`) and copy the
  // server-resolved absolute path it returns — the same `navigator.clipboard.writeText`
  // mechanism `handleCopyRelativePath` above uses. A fetch failure (400 escape, 404 the entry no
  // longer exists, or the backend unreachable) is surfaced as a visible status message, the same
  // way `handleReveal` above surfaces its refusal.
  async function handleCopyAbsolutePath(node: FileTreeNode): Promise<void> {
    try {
      const response = await fetch(`${ABSOLUTE_PATH_URL}?path=${encodeURIComponent(node.path)}`)
      if (!response.ok) {
        let detail = `request failed (status ${response.status})`
        try {
          const body: unknown = await response.json()
          if (
            typeof body === 'object' &&
            body !== null &&
            typeof (body as { detail?: unknown }).detail === 'string'
          ) {
            detail = (body as { detail: string }).detail
          }
        } catch {
          // Falls through with the status-only message above, same defensive fallback
          // `handleReveal` applies for a non-JSON body.
        }
        setActionStatus({ kind: 'error', message: `Copy absolute path failed: ${detail}` })
        return
      }
      const body = (await response.json()) as AbsolutePathResult
      navigator.clipboard.writeText(body.absolute_path).then(
        () => setActionStatus({ kind: 'info', message: `Copied absolute path: ${body.absolute_path}` }),
        () =>
          setActionStatus({
            kind: 'error',
            message: 'Could not copy the absolute path — the clipboard was not reachable.',
          }),
      )
    } catch {
      setActionStatus({
        kind: 'error',
        message: 'Copy absolute path failed: could not reach the backend.',
      })
    }
  }

  // REQ-007 W09 action 2: hands the entry's path to whichever HTML Viewer tab the submenu chose,
  // through the bridge `HtmlViewerRegion` registers itself into (`panelBridge.ts`).
  function handleOpenInViewer(node: FileTreeNode, tabId: number): void {
    if (!viewerHandle) return
    viewerHandle.openInTab(tabId, node.path)
    setActionStatus({ kind: 'info', message: `Opened "${node.path}" in the HTML Viewer.` })
  }

  // REQ-007 W09 action 5: same un-executed injection `InjectionDropdowns`' own selections use
  // (R12 mechanics), reached through the terminal bridge.
  function handleInjectPath(node: FileTreeNode): void {
    if (!terminalHandle) return
    terminalHandle.injectPath(node.path)
    setActionStatus({
      kind: 'info',
      message: `Injected "${node.path}" into the active terminal tab's input line.`,
    })
  }

  const contextMenuNode = contextMenu?.node ?? null
  const contextMenuViewerCompatible =
    contextMenuNode !== null &&
    !contextMenuNode.isDir &&
    COMPATIBLE_EXTENSIONS.includes(extensionOf(contextMenuNode.name) ?? '')
  const contextMenuTerminalAvailable = terminalHandle !== null && terminalHandle.enabled && !terminalHandle.dropped

  return (
    <section className="stage-region stage-region--file-browser" aria-label="File Browser">
      <header className="stage-region__header">
        <h2>File Browser</h2>
        <div className="stage-file-browser__controls">
          <select
            className="stage-file-browser__preset"
            aria-label="File Browser preset"
            value={currentPresetId}
            onChange={(event) => {
              const preset = PRESETS.find((candidate) => candidate.id === event.target.value)
              if (!preset) return
              setContextFolder(preset.directory)
              setTypeFilter(preset.typeFilter)
            }}
          >
            <option value="custom">Custom</option>
            {PRESETS.map((preset) => (
              <option key={preset.id} value={preset.id}>
                {preset.label}
              </option>
            ))}
          </select>
          <DirectoryPickerDialog initialDirectory={contextFolder} onSelectDirectory={setContextFolder} />
        </div>
      </header>
      <div className="stage-region__body stage-region__body--file-browser">
        <p className="stage-file-browser__meta">
          Browsing <code>{contextFolder}</code>
        </p>
        {actionStatus ? (
          <p
            className={
              'stage-file-browser__status' +
              (actionStatus.kind === 'error' ? ' stage-file-browser__status--error' : '')
            }
          >
            {actionStatus.message}
            <button
              type="button"
              className="stage-file-browser__status-dismiss"
              aria-label="Dismiss status message"
              onClick={() => setActionStatus(null)}
            >
              ×
            </button>
          </p>
        ) : null}
        <div className="stage-file-browser__filters">
          <input
            type="text"
            className="stage-file-browser__search"
            placeholder="Filter by name…"
            aria-label="Filter files and folders by name"
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
          />
          <select
            className="stage-file-browser__type-filter"
            aria-label="Filter by file type"
            value={typeFilter}
            onChange={(event) => setTypeFilter(event.target.value)}
          >
            <option value={NO_FILTER}>All types</option>
            {availableExtensions.map((ext) => (
              <option key={ext} value={ext}>
                {ext}
              </option>
            ))}
          </select>
        </div>
        <div className="stage-file-browser__tree" role="tree" aria-label="File Browser tree">
          {loadState === 'loading' || entriesFolder !== contextFolder ? (
            <p className="stage-placeholder-text">Loading…</p>
          ) : loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not search <code>{contextFolder}</code>.
            </p>
          ) : tree.children.length === 0 ? (
            <p className="stage-placeholder-text">
              {filtersActive ? 'No matching files.' : 'No files here.'}
            </p>
          ) : (
            <TreeLevel
              nodes={tree.children}
              expandedPaths={effectiveExpandedPaths}
              onToggle={toggleExpanded}
              onContextMenu={openContextMenu}
              root
            />
          )}
        </div>
      </div>
      {contextMenu ? (
        <FileTreeContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          entryName={contextMenu.node.name}
          viewerCompatible={contextMenuViewerCompatible}
          viewerAvailable={viewerHandle !== null}
          viewerTabs={viewerHandle?.tabs ?? []}
          terminalAvailable={contextMenuTerminalAvailable}
          onReveal={() => {
            void handleReveal(contextMenu.node)
          }}
          onOpenInViewer={(tabId) => handleOpenInViewer(contextMenu.node, tabId)}
          onCopyRelativePath={() => handleCopyRelativePath(contextMenu.node)}
          onCopyAbsolutePath={() => {
            void handleCopyAbsolutePath(contextMenu.node)
          }}
          onInjectPath={() => handleInjectPath(contextMenu.node)}
          onClose={() => setContextMenu(null)}
        />
      ) : null}
    </section>
  )
}
