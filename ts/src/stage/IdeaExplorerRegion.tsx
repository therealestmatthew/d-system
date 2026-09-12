import ExplorerRegion, { type ExplorerColumn } from './explorer/ExplorerRegion'

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

/** The idea schema's legal statuses (`schemas/idea.schema.json`'s `definitions.status` enum),
 * used only to populate the status filter dropdown — not idea copy, just the fixed vocabulary an
 * idea's `status` field is drawn from. */
const STATUSES = ['open', 'triaged', 'reviewing', 'promoted', 'discarded']

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

const COLUMNS: ExplorerColumn<IdeaRow>[] = [
  { key: 'id', label: 'ID', sortValue: (row) => row.id.toLowerCase(), render: (row) => row.id },
  { key: 'title', label: 'Title', sortValue: (row) => row.title.toLowerCase(), render: (row) => row.title },
  { key: 'status', label: 'Status', sortValue: (row) => row.status.toLowerCase(), render: (row) => row.status },
  { key: 'age', label: 'Age', sortValue: (row) => ageInDays(row.created), render: (row) => formatAge(row.created) },
  {
    key: 'annotation_count',
    label: 'Annotations',
    sortValue: (row) => row.annotation_count,
    render: (row) => row.annotation_count,
  },
  { key: 'link_count', label: 'Links', sortValue: (row) => row.link_count, render: (row) => row.link_count },
]

/**
 * The Idea Explorer panel (REQ-007 W10), over `phase-wb-01`'s idea route only — never a direct
 * read of `_data/ideas.jsonl`. Columns: id, title, status, age (days since `created`), annotation
 * count, link count. The standard/priority-queue toggle re-fetches `GET /ideas` or `GET
 * /ideas/queue` — the queue view's status-precedence-then-age ranking (`_idea_queue_sort_key`,
 * `src/api/routes/workbench.py`) is the backend's own, never re-derived here.
 *
 * All table/sort/filter/queue-toggle behavior lives in `ExplorerRegion` (`explorer/
 * ExplorerRegion.tsx`), the surface this panel shares with `BacklogExplorerRegion` per REQ-007
 * W11 — this file supplies only the idea-specific columns, urls, status vocabulary and search
 * predicate.
 */
export default function IdeaExplorerRegion() {
  return (
    <ExplorerRegion<IdeaRow>
      title="Idea Explorer"
      ariaLabel="Idea Explorer"
      regionClassSuffix="idea-explorer"
      standardUrl={IDEAS_URL}
      queueUrl={IDEAS_QUEUE_URL}
      columns={COLUMNS}
      rowKey={(row) => row.id}
      matchesSearch={(row, needle) =>
        row.id.toLowerCase().includes(needle) || row.title.toLowerCase().includes(needle)
      }
      statusOf={(row) => row.status}
      statusOptions={STATUSES}
      emptyMessage="No ideas yet."
      errorMessage="Could not load ideas."
    />
  )
}
