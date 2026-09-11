import { useEffect, useMemo, useState } from 'react'

const IDEAS_URL = '/api/v1/workbench/ideas'
const IDEAS_QUEUE_URL = '/api/v1/workbench/ideas/queue'

/** `IdeaRow`'s response shape (`src/api/routes/workbench.py`, `phase-wb-01`'s idea route) — id,
 * title, status, created/updated timestamps, and the two derived counts, exactly as `fold()`
 * (`src/db/ideas.py`) computes them server-side. Nothing here re-derives idea state; this panel
 * only renders what the route already folded. */
interface IdeaRow {
  id: string
  title: string
  status: string
  created: string
  updated: string
  annotation_count: number
  link_count: number
}

type LoadState = 'loading' | 'loaded' | 'error'

/** The two views REQ-007 W10 names. `standard` is `GET /ideas` (id order); `queue` is `GET
 * /ideas/queue` (status precedence then age, computed server-side by `_idea_queue_sort_key`) —
 * switching the toggle re-fetches the route for that view rather than re-ranking the already
 * loaded rows client-side, so the ranking is always the backend's own, not a second, potentially
 * drifting copy of its precedence rule. */
type ExplorerView = 'standard' | 'queue'

/** A sortable column: `age` sorts on `created` (oldest first ascending, same field the backend's
 * own queue tie-breaker uses), every other column sorts on its own value. */
type SortColumn = 'id' | 'title' | 'status' | 'age' | 'annotation_count' | 'link_count'
type SortDirection = 'asc' | 'desc'

interface ColumnDefinition {
  key: SortColumn
  label: string
}

const COLUMNS: ColumnDefinition[] = [
  { key: 'id', label: 'ID' },
  { key: 'title', label: 'Title' },
  { key: 'status', label: 'Status' },
  { key: 'age', label: 'Age' },
  { key: 'annotation_count', label: 'Annotations' },
  { key: 'link_count', label: 'Links' },
]

/** The idea schema's legal statuses (`schemas/idea.schema.json`'s `definitions.status` enum),
 * used only to populate the status filter dropdown — not idea copy, just the fixed vocabulary an
 * idea's `status` field is drawn from. */
const STATUSES = ['open', 'triaged', 'reviewing', 'promoted', 'discarded']

const NO_STATUS_FILTER = 'all'

const MS_PER_DAY = 24 * 60 * 60 * 1000

/** Whole days since `created`, floored at zero so a just-created idea (or a slightly-skewed
 * client clock) never reads negative. */
function ageInDays(created: string): number {
  const createdMs = Date.parse(created)
  if (Number.isNaN(createdMs)) return 0
  return Math.max(0, Math.floor((Date.now() - createdMs) / MS_PER_DAY))
}

function formatAge(created: string): string {
  const days = ageInDays(created)
  return days === 1 ? '1 day' : `${days} days`
}

function sortValue(row: IdeaRow, column: SortColumn): string | number {
  switch (column) {
    case 'age':
      return ageInDays(row.created)
    case 'annotation_count':
    case 'link_count':
      return row[column]
    default:
      return row[column].toLowerCase()
  }
}

function compareRows(a: IdeaRow, b: IdeaRow, column: SortColumn, direction: SortDirection): number {
  const left = sortValue(a, column)
  const right = sortValue(b, column)
  let result: number
  if (typeof left === 'number' && typeof right === 'number') {
    result = left - right
  } else {
    result = String(left).localeCompare(String(right))
  }
  return direction === 'asc' ? result : -result
}

function viewUrl(view: ExplorerView): string {
  return view === 'queue' ? IDEAS_QUEUE_URL : IDEAS_URL
}

/**
 * The Idea Explorer panel (REQ-007 W10), over `phase-wb-01`'s idea route only — never a direct
 * read of `_data/ideas.jsonl`. Columns: id, title, status, age (days since `created`), annotation
 * count, link count.
 *
 * Two independent controls:
 *
 * - The view toggle (`standard` / `queue`) selects which backend route feeds this panel — `GET
 *   /ideas` (id order) or `GET /ideas/queue` (status precedence — open, triaged, reviewing, then
 *   the terminal statuses — then age, per `_idea_queue_sort_key` in `src/api/routes/workbench.py`).
 *   Switching it re-fetches rather than re-ranking the already-loaded rows client-side, so the
 *   queue ranking shown is always the backend's own.
 * - Column-header sorting layers on top of whichever view is loaded: with no column selected, rows
 *   render in the fetched order (id order, or the queue's precedence-then-age order); clicking a
 *   header sorts the current rows by that column instead, ascending first, descending on a second
 *   click of the same header, cleared (back to the fetched order) on a third.
 *
 * Filtering (text against id/title, status via dropdown) is client-side over the already-fetched
 * rows — filtering never changes which route is called, only which of that route's rows are shown.
 */
export default function IdeaExplorerRegion() {
  const [view, setView] = useState<ExplorerView>('standard')
  const [rows, setRows] = useState<IdeaRow[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [textFilter, setTextFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState(NO_STATUS_FILTER)
  const [sortColumn, setSortColumn] = useState<SortColumn | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  useEffect(() => {
    let cancelled = false
    setLoadState('loading')
    fetch(viewUrl(view))
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<IdeaRow[]>
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
  }, [view])

  // A fresh view load starts with no column sort applied, so the just-fetched order (id order, or
  // the queue's own precedence-then-age order) is what renders until the user asks for a column
  // sort — never a stale sort column silently reapplied to the new view's rows.
  useEffect(() => {
    setSortColumn(null)
  }, [view])

  const filteredRows = useMemo(() => {
    const needle = textFilter.trim().toLowerCase()
    return rows.filter((row) => {
      if (statusFilter !== NO_STATUS_FILTER && row.status !== statusFilter) return false
      if (needle && !row.id.toLowerCase().includes(needle) && !row.title.toLowerCase().includes(needle)) {
        return false
      }
      return true
    })
  }, [rows, textFilter, statusFilter])

  const displayRows = useMemo(() => {
    if (!sortColumn) return filteredRows
    return [...filteredRows].sort((a, b) => compareRows(a, b, sortColumn, sortDirection))
  }, [filteredRows, sortColumn, sortDirection])

  function handleHeaderClick(column: SortColumn): void {
    if (sortColumn !== column) {
      setSortColumn(column)
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

  function headerSortIndicator(column: SortColumn): string {
    if (sortColumn !== column) return ''
    return sortDirection === 'asc' ? ' ▲' : ' ▼'
  }

  return (
    <section className="stage-region stage-region--idea-explorer" aria-label="Idea Explorer">
      <header className="stage-region__header">
        <h2>Idea Explorer</h2>
        <div className="stage-idea-explorer__controls">
          <div className="stage-idea-explorer__view-toggle" role="group" aria-label="Explorer view">
            <button
              type="button"
              className="stage-idea-explorer__view-button"
              aria-pressed={view === 'standard'}
              onClick={() => setView('standard')}
            >
              Standard
            </button>
            <button
              type="button"
              className="stage-idea-explorer__view-button"
              aria-pressed={view === 'queue'}
              onClick={() => setView('queue')}
            >
              Priority queue
            </button>
          </div>
        </div>
      </header>
      <div className="stage-region__body stage-region__body--idea-explorer">
        <div className="stage-idea-explorer__filters">
          <input
            type="text"
            className="stage-idea-explorer__search"
            placeholder="Filter by id or title…"
            aria-label="Filter ideas by id or title"
            value={textFilter}
            onChange={(event) => setTextFilter(event.target.value)}
          />
          <select
            className="stage-idea-explorer__status-filter"
            aria-label="Filter by status"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value={NO_STATUS_FILTER}>All statuses</option>
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
        <div className="stage-idea-explorer__table-wrap">
          {loadState === 'loading' ? (
            <p className="stage-placeholder-text">Loading…</p>
          ) : loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not load ideas.
            </p>
          ) : displayRows.length === 0 ? (
            <p className="stage-placeholder-text">
              {rows.length === 0 ? 'No ideas yet.' : 'No ideas match the current filters.'}
            </p>
          ) : (
            <table className="stage-idea-explorer__table">
              <thead>
                <tr>
                  {COLUMNS.map((column) => (
                    <th key={column.key}>
                      <button
                        type="button"
                        className="stage-idea-explorer__sort-button"
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
                  <tr key={row.id}>
                    <td>{row.id}</td>
                    <td>{row.title}</td>
                    <td>{row.status}</td>
                    <td>{formatAge(row.created)}</td>
                    <td>{row.annotation_count}</td>
                    <td>{row.link_count}</td>
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
