import { useEffect, useMemo, useState, type ReactNode } from 'react'

export type SortDirection = 'asc' | 'desc'

/** One sortable/renderable column, generic over the row shape a particular explorer fetches.
 * `sortValue` is required even for a column whose render is the raw field, because string columns
 * need an explicit lowercased compare key and derived columns (idea age, backlog queue position)
 * have no single field to sort on directly. */
export interface ExplorerColumn<T> {
  key: string
  label: string
  sortValue: (row: T) => string | number
  render: (row: T) => ReactNode
}

export type ExplorerView = 'standard' | 'queue'

type LoadState = 'loading' | 'loaded' | 'error'

export interface ExplorerViewLabels {
  standard: string
  queue: string
}

export interface ExplorerRegionProps<T> {
  /** Panel title, shown in the header and used to build the search field's aria-label. */
  title: string
  ariaLabel: string
  /** Suffix for the outer `.stage-region--*` modifier class — cosmetic hook only, no behavior
   * depends on it. */
  regionClassSuffix: string
  standardUrl: string
  queueUrl: string
  columns: ExplorerColumn<T>[]
  rowKey: (row: T) => string
  /** Free-text filter predicate; the caller decides which fields the search box matches (id/title
   * in both current explorers). */
  matchesSearch: (row: T, needle: string) => boolean
  /** Status dropdown filter — optional in the shared surface, since not every future explorer
   * this component parameterizes need carry a status field, but both current ones do. */
  statusOf?: (row: T) => string
  statusOptions?: string[]
  emptyMessage: string
  errorMessage: string
  viewLabels?: ExplorerViewLabels
}

const NO_STATUS_FILTER = 'all'

function compareRows<T>(a: T, b: T, column: ExplorerColumn<T>, direction: SortDirection): number {
  const left = column.sortValue(a)
  const right = column.sortValue(b)
  let result: number
  if (typeof left === 'number' && typeof right === 'number') {
    result = left - right
  } else {
    result = String(left).localeCompare(String(right))
  }
  return direction === 'asc' ? result : -result
}

/**
 * The shared table/sort/filter/queue-toggle configuration surface REQ-007 W10 and W11 require the
 * Idea Explorer and Backlog Explorer to present identically, parameterized here by data source (a
 * pair of backend routes) and by column set — never copy-pasted per panel. Both
 * `IdeaExplorerRegion.tsx` and `BacklogExplorerRegion.tsx` render this component and own no table,
 * sort, filter, or view-toggle logic of their own; they only supply columns, urls and predicates.
 *
 * Two independent controls, identical across both panels:
 *
 * - The view toggle (`standard` / `queue`) selects which backend route feeds this panel
 *   (`standardUrl` / `queueUrl`). Switching it re-fetches rather than re-ranking the already-loaded
 *   rows client-side, so the ranking shown is always the backend's own precedence — the idea
 *   route's status-then-age order (`_idea_queue_sort_key`) or the backlog route's `next_up`-then-
 *   priority order (`queue_order()`/`readiness()`), never a second, potentially drifting copy of
 *   either rule.
 * - Column-header sorting layers on top of whichever view is loaded: with no column selected, rows
 *   render in the fetched order; clicking a header sorts ascending, a second click of the same
 *   header sorts descending, a third click clears the sort back to the fetched order.
 *
 * Filtering (free text against caller-chosen fields, plus an optional status dropdown) is
 * client-side over the already-fetched rows — filtering never changes which route is called.
 */
export default function ExplorerRegion<T>({
  title,
  ariaLabel,
  regionClassSuffix,
  standardUrl,
  queueUrl,
  columns,
  rowKey,
  matchesSearch,
  statusOf,
  statusOptions,
  emptyMessage,
  errorMessage,
  viewLabels,
}: ExplorerRegionProps<T>) {
  const [view, setView] = useState<ExplorerView>('standard')
  const [rows, setRows] = useState<T[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [textFilter, setTextFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState(NO_STATUS_FILTER)
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  useEffect(() => {
    let cancelled = false
    setLoadState('loading')
    fetch(view === 'queue' ? queueUrl : standardUrl)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<T[]>
      })
      .then((body) => {
        if (cancelled) return
        setRows(body)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [view, standardUrl, queueUrl])

  // A fresh view load starts with no column sort applied, so the just-fetched order (the view's
  // own order) is what renders until the user asks for a column sort — never a stale sort column
  // silently reapplied to the new view's rows.
  useEffect(() => {
    setSortColumn(null)
  }, [view])

  const filteredRows = useMemo(() => {
    const needle = textFilter.trim().toLowerCase()
    return rows.filter((row) => {
      if (statusOf && statusFilter !== NO_STATUS_FILTER && statusOf(row) !== statusFilter) return false
      if (needle && !matchesSearch(row, needle)) return false
      return true
    })
  }, [rows, textFilter, statusFilter, statusOf, matchesSearch])

  const activeColumn = sortColumn ? columns.find((column) => column.key === sortColumn) ?? null : null

  const displayRows = useMemo(() => {
    if (!activeColumn) return filteredRows
    return [...filteredRows].sort((a, b) => compareRows(a, b, activeColumn, sortDirection))
  }, [filteredRows, activeColumn, sortDirection])

  function handleHeaderClick(key: string): void {
    if (sortColumn !== key) {
      setSortColumn(key)
      setSortDirection('asc')
      return
    }
    if (sortDirection === 'asc') {
      setSortDirection('desc')
      return
    }
    // Third click on the same header clears the sort, returning to the fetched (view) order.
    setSortColumn(null)
  }

  function headerSortIndicator(key: string): string {
    if (sortColumn !== key) return ''
    return sortDirection === 'asc' ? ' ▲' : ' ▼'
  }

  const standardLabel = viewLabels?.standard ?? 'Standard'
  const queueLabel = viewLabels?.queue ?? 'Priority queue'

  return (
    <section className={`stage-region stage-region--${regionClassSuffix}`} aria-label={ariaLabel}>
      <header className="stage-region__header">
        <h2>{title}</h2>
        <div className="stage-explorer__controls">
          <div className="stage-explorer__view-toggle" role="group" aria-label="Explorer view">
            <button
              type="button"
              className="stage-explorer__view-button"
              aria-pressed={view === 'standard'}
              onClick={() => setView('standard')}
            >
              {standardLabel}
            </button>
            <button
              type="button"
              className="stage-explorer__view-button"
              aria-pressed={view === 'queue'}
              onClick={() => setView('queue')}
            >
              {queueLabel}
            </button>
          </div>
        </div>
      </header>
      <div className="stage-region__body stage-region__body--explorer">
        <div className="stage-explorer__filters">
          <input
            type="text"
            className="stage-explorer__search"
            placeholder="Filter by id or title…"
            aria-label={`Filter ${title.toLowerCase()} by id or title`}
            value={textFilter}
            onChange={(event) => setTextFilter(event.target.value)}
          />
          {statusOf && statusOptions ? (
            <select
              className="stage-explorer__status-filter"
              aria-label="Filter by status"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value={NO_STATUS_FILTER}>All statuses</option>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          ) : null}
        </div>
        <div className="stage-explorer__table-wrap">
          {loadState === 'loading' ? (
            <p className="stage-placeholder-text">Loading…</p>
          ) : loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">{errorMessage}</p>
          ) : displayRows.length === 0 ? (
            <p className="stage-placeholder-text">
              {rows.length === 0 ? emptyMessage : 'No rows match the current filters.'}
            </p>
          ) : (
            <table className="stage-explorer__table">
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column.key}>
                      <button
                        type="button"
                        className="stage-explorer__sort-button"
                        aria-sort={
                          sortColumn === column.key
                            ? sortDirection === 'asc'
                              ? 'ascending'
                              : 'descending'
                            : 'none'
                        }
                        onClick={() => handleHeaderClick(column.key)}
                      >
                        {column.label}
                        {headerSortIndicator(column.key)}
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {displayRows.map((row) => (
                  <tr key={rowKey(row)}>
                    {columns.map((column) => (
                      <td key={column.key}>{column.render(row)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </section>
  )
}
