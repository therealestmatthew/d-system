import { useEffect, useState } from 'react'
import Popover from './Popover'

const LIST_URL = '/api/v1/workbench/list'

interface DirectoryEntry {
  name: string
  path: string
  is_dir: boolean
}

type LoadState = 'loading' | 'loaded' | 'error'

interface Crumb {
  label: string
  path: string
}

/** `path` split into repo-root-first breadcrumb segments, each carrying the repo-relative path a
 * click on it should jump to. `"."` (the repository root) is always the first crumb. */
function crumbsFor(path: string): Crumb[] {
  const crumbs: Crumb[] = [{ label: 'repository root', path: '.' }]
  if (path === '.' || path === '') return crumbs
  let accumulated = ''
  for (const segment of path.split('/').filter(Boolean)) {
    accumulated = accumulated ? `${accumulated}/${segment}` : segment
    crumbs.push({ label: segment, path: accumulated })
  }
  return crumbs
}

/**
 * The in-app directory dialog (REQ-007 W07/ADR-015's rejected-alternative rule: "the in-app
 * dialog fed by the listing API keeps one path model everywhere" — never a browser-native
 * picker, which would yield an OS-absolute path the repo-bounded backend refuses). Fed
 * exclusively by the workbench's one-level listing route (`GET /api/v1/workbench/list`,
 * `phase-wb-01`), never the recursive search route — this dialog navigates the tree one
 * directory at a time, showing only subdirectories (a directory choice, not a file choice).
 *
 * Opens as a click-triggered, dismissible popup (`Popover`, REQ-006 R03). Every path shown or
 * emitted is repository-relative, exactly what the listing route both takes and returns — no
 * OS-absolute path is ever constructed here.
 */
export default function DirectoryPickerDialog({
  initialDirectory,
  onSelectDirectory,
}: {
  initialDirectory: string
  onSelectDirectory: (path: string) => void
}) {
  const [currentPath, setCurrentPath] = useState(initialDirectory)
  const [entries, setEntries] = useState<DirectoryEntry[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false
    setLoadState('loading')
    const params = new URLSearchParams({ path: currentPath })
    fetch(`${LIST_URL}?${params.toString()}`)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<DirectoryEntry[]>
      })
      .then((body) => {
        if (cancelled) return
        setEntries(
          body.filter((entry) => entry.is_dir).sort((a, b) => a.name.localeCompare(b.name)),
        )
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [currentPath])

  return (
    <Popover
      triggerLabel="Change directory…"
      title="Choose a directory"
      onOpenChange={(open) => {
        // Re-anchor to the viewer's current directory every time the dialog reopens, rather than
        // resuming wherever a previous browse session left off.
        if (open) setCurrentPath(initialDirectory)
      }}
    >
      {(close) => {
        const crumbs = crumbsFor(currentPath)
        return (
          <div className="stage-directory-dialog">
            <nav className="stage-directory-dialog__breadcrumbs" aria-label="Current directory">
              {crumbs.map((crumb, index) => (
                <span key={crumb.path}>
                  <button
                    type="button"
                    className="stage-directory-dialog__crumb"
                    onClick={() => setCurrentPath(crumb.path)}
                    disabled={index === crumbs.length - 1}
                  >
                    {crumb.label}
                  </button>
                  {index < crumbs.length - 1 ? <span aria-hidden="true"> / </span> : null}
                </span>
              ))}
            </nav>
            <div className="stage-directory-dialog__body">
              {loadState === 'loading' ? (
                <p className="stage-placeholder-text">Loading…</p>
              ) : loadState === 'error' ? (
                <p className="stage-placeholder-text stage-placeholder-text--absent">
                  Could not list this directory.
                </p>
              ) : entries.length === 0 ? (
                <p className="stage-placeholder-text">No subdirectories here.</p>
              ) : (
                <ul className="stage-directory-dialog__list">
                  {entries.map((entry) => (
                    <li key={entry.path}>
                      <button
                        type="button"
                        className="stage-directory-dialog__entry"
                        onClick={() => setCurrentPath(entry.path)}
                      >
                        {entry.name}/
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="stage-directory-dialog__footer">
              <button
                type="button"
                className="stage-directory-dialog__confirm"
                onClick={() => {
                  onSelectDirectory(currentPath)
                  close()
                }}
              >
                Search this directory
              </button>
            </div>
          </div>
        )
      }}
    </Popover>
  )
}
