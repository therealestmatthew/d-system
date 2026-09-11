import { useEffect, useMemo, useState } from 'react'
import DirectoryPickerDialog from './DirectoryPickerDialog'

const SEARCH_URL = '/api/v1/workbench/search'

interface DirectoryEntry {
  name: string
  path: string
  is_dir: boolean
}

type LoadState = 'loading' | 'loaded' | 'error'

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
  root = false,
}: {
  nodes: FileTreeNode[]
  expandedPaths: Set<string>
  onToggle: (path: string) => void
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
            >
              <span aria-hidden="true">{expandedPaths.has(node.path) ? '▾' : '▸'}</span> {node.name}/
            </button>
            {expandedPaths.has(node.path) ? (
              <TreeLevel nodes={node.children} expandedPaths={expandedPaths} onToggle={onToggle} />
            ) : null}
          </li>
        ) : (
          <li key={node.path} className="stage-file-browser__tree-item">
            <span className="stage-file-browser__tree-file" title={node.path}>
              {node.name}
            </span>
          </li>
        ),
      )}
    </ul>
  )
}

/**
 * The File Browser panel (REQ-007 W09, tree half only — the right-click context menu described
 * alongside it in W09 is a separate, not-yet-dispatched slice of that same requirement row and is
 * not built here). Shows a collapsible treeview of subdirectories and files under a context
 * folder chosen through the same in-app directory dialog `HtmlViewerRegion` already uses
 * (`DirectoryPickerDialog`, the `phase-wb-04` pattern over `phase-wb-01`'s one-level listing
 * route), filterable by text search and by file type, hiding folders with no matches.
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
 */
export default function FileBrowserRegion() {
  const [contextFolder, setContextFolder] = useState('.')
  const [typeFilter, setTypeFilter] = useState(NO_FILTER)
  const [searchText, setSearchText] = useState('')
  const [entries, setEntries] = useState<DirectoryEntry[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())

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

  const tree = useMemo(() => buildTree(contextFolder, filteredEntries), [contextFolder, filteredEntries])

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
          {loadState === 'loading' ? (
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
              root
            />
          )}
        </div>
      </div>
    </section>
  )
}
