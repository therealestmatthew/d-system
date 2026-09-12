import ExplorerRegion, { type ExplorerColumn } from './explorer/ExplorerRegion'

const BACKLOG_URL = '/api/v1/workbench/backlog'
const BACKLOG_QUEUE_URL = '/api/v1/workbench/backlog/queue'

/** `BacklogPhaseRow`'s response shape (`src/api/routes/workbench.py`, `phase-wb-01`'s backlog
 * route) — id, title, status, priority, queue position and the phase's `depends_on` list, exactly
 * as that route computes them from `docs/09-backlog/backlog.yaml`. Nothing here re-parses the
 * backlog file directly. */
interface BacklogRow {
  id: string
  title: string
  status: string
  priority: number
  queue_position: number | null
  depends_on: string[]
}

/** The backlog item schema's legal statuses (`schemas/backlog.schema.json`'s
 * `items[].properties.status` enum), used only to populate the status filter dropdown — not
 * backlog copy, just the fixed vocabulary a phase's `status` field is drawn from. */
const STATUSES = ['queued', 'active', 'blocked', 'deferred', 'complete', 'cancelled']

const NO_QUEUE_POSITION = Number.POSITIVE_INFINITY

function formatQueuePosition(row: BacklogRow): string {
  return row.queue_position === null ? '—' : String(row.queue_position)
}

function formatDependsOn(row: BacklogRow): string {
  return row.depends_on.length === 0 ? '—' : row.depends_on.join(', ')
}

const COLUMNS: ExplorerColumn<BacklogRow>[] = [
  { key: 'id', label: 'ID', sortValue: (row) => row.id.toLowerCase(), render: (row) => row.id },
  { key: 'title', label: 'Title', sortValue: (row) => row.title.toLowerCase(), render: (row) => row.title },
  { key: 'status', label: 'Status', sortValue: (row) => row.status.toLowerCase(), render: (row) => row.status },
  { key: 'priority', label: 'Priority', sortValue: (row) => row.priority, render: (row) => row.priority },
  {
    key: 'queue_position',
    label: 'Queue position',
    // Unranked phases (not in next_up) sort to the end ascending, matching their absence from the
    // ready queue rather than tying them all to zero.
    sortValue: (row) => row.queue_position ?? NO_QUEUE_POSITION,
    render: formatQueuePosition,
  },
  {
    key: 'depends_on',
    label: 'Depends on',
    sortValue: (row) => row.depends_on.join(', ').toLowerCase(),
    render: formatDependsOn,
  },
]

/**
 * The Backlog Explorer panel (REQ-007 W11), over `phase-wb-01`'s backlog route only — never a
 * direct read of `docs/09-backlog/backlog.yaml`. Columns: id, title, status, priority, queue
 * position, depends_on. The standard/priority-queue toggle re-fetches `GET /backlog` or `GET
 * /backlog/queue`; the queue view's `next_up`-first-then-ready-by-priority ranking
 * (`queue_order()`/`readiness()`, `src/governance/backlog.py`, matching `uv run python -m
 * src.governance --ready`) is the backend's own, never re-derived here.
 *
 * Presents the same configuration surface as `IdeaExplorerRegion` (REQ-007 W11) by rendering the
 * same `ExplorerRegion` (`explorer/ExplorerRegion.tsx`) that panel does — this file supplies only
 * the backlog-specific columns, urls, status vocabulary and search predicate, never a second copy
 * of the table/sort/filter/queue-toggle logic.
 */
export default function BacklogExplorerRegion() {
  return (
    <ExplorerRegion<BacklogRow>
      title="Backlog Explorer"
      ariaLabel="Backlog Explorer"
      regionClassSuffix="backlog-explorer"
      standardUrl={BACKLOG_URL}
      queueUrl={BACKLOG_QUEUE_URL}
      columns={COLUMNS}
      rowKey={(row) => row.id}
      matchesSearch={(row, needle) =>
        row.id.toLowerCase().includes(needle) || row.title.toLowerCase().includes(needle)
      }
      statusOf={(row) => row.status}
      statusOptions={STATUSES}
      emptyMessage="No backlog phases yet."
      errorMessage="Could not load the backlog."
    />
  )
}
