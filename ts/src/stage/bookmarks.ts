import {
  callOpenFiles,
  deliverBatch,
  viewerBridge,
  type DeclineReason,
  type ViewerBridgeHandle,
  type BatchTarget,
} from './panelBridge'
import { fetchWorkbench } from './useTerminalEnabled'

/**
 * The client of the bookmark-category routes (`src/api/routes/workbench_bookmarks.py`, ADR-029)
 * and the one place that opens a category as a set.
 *
 * A category is held by its immutable `category_id`; nothing here copies a category's entries into
 * state that outlives a request. Opening a category re-reads it (`GET /bookmarks/{id}`), splits its
 * entries by the server's status, and hands only the `present` paths to `deliverBatch`
 * (`panelBridge.ts`), the single file-passing path. The category surface never calls `openInTab`.
 *
 * Private files are deliberately unsupported (ADR-029 section 3): the server refuses an entry under
 * `_private/` or any gitignored path on write, and reports one that became ignored later as
 * `excluded`. This module therefore has no way to bookmark such a file, and shows an `excluded`
 * entry by path like a `missing` one.
 */

const BOOKMARKS_URL = '/api/v1/workbench/bookmarks'

export type EntryStatus = 'present' | 'missing' | 'excluded'

export interface CategorySummary {
  category_id: string
  name: string
  entry_count: number
}

export interface ResolvedEntry {
  path: string
  status: EntryStatus
}

export interface CategoryDetail {
  category_id: string
  name: string
  entries: ResolvedEntry[]
}

/** The result of a bookmark request. `unavailable` means the workbench routes are not mounted (the
 * 404 `fetchWorkbench` reports when the demo-terminal flag is unset). */
export type BookmarkResult<T> =
  | { ok: true; value: T }
  | { ok: false; unavailable: boolean; message: string }

async function detailOf(response: Response): Promise<string> {
  const fallback = `request failed (status ${response.status})`
  try {
    const body: unknown = await response.json()
    if (typeof body === 'object' && body !== null) {
      const detail = (body as { detail?: unknown }).detail
      if (typeof detail === 'string') return detail
    }
  } catch {
    // Not a JSON body with a `detail` string: the status-only message stands.
  }
  return fallback
}

async function request<T>(url: string, init?: RequestInit): Promise<BookmarkResult<T>> {
  try {
    const response = await fetchWorkbench(url, init)
    if (response.ok) return { ok: true, value: (await response.json()) as T }
    // A 404 with no body is `fetchWorkbench` standing in for unmounted routes; a mounted route's
    // 404 carries a `detail`.
    const message = await detailOf(response)
    const unavailable = response.status === 404 && message === 'request failed (status 404)'
    return { ok: false, unavailable, message: unavailable ? 'Bookmarks are unavailable.' : message }
  } catch {
    return { ok: false, unavailable: false, message: 'Could not reach the backend.' }
  }
}

function jsonInit(method: string, body: unknown): RequestInit {
  return { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
}

const categoryUrl = (categoryId: string) => `${BOOKMARKS_URL}/${encodeURIComponent(categoryId)}`

export const bookmarksApi = {
  list: () => request<CategorySummary[]>(BOOKMARKS_URL),
  get: (categoryId: string) => request<CategoryDetail>(categoryUrl(categoryId)),
  create: (name: string) => request<CategoryDetail>(BOOKMARKS_URL, jsonInit('POST', { name })),
  rename: (categoryId: string, name: string) =>
    request<CategoryDetail>(categoryUrl(categoryId), jsonInit('PATCH', { name })),
  remove: (categoryId: string) =>
    request<{ deleted: string }>(categoryUrl(categoryId), { method: 'DELETE' }),
  addFile: (categoryId: string, path: string) =>
    request<CategoryDetail>(`${categoryUrl(categoryId)}/entries`, jsonInit('POST', { path })),
  removeFile: (categoryId: string, path: string) =>
    request<CategoryDetail>(`${categoryUrl(categoryId)}/entries`, jsonInit('DELETE', { path })),
}

// ---------------------------------------------------------------------------------------------
// Opening a category as a set in the HTML Viewer
// ---------------------------------------------------------------------------------------------

/** The one place the HTML Viewer is named as a batch target. */
export const VIEWER_BATCH_TARGET: BatchTarget<ViewerBridgeHandle> = {
  channel: viewerBridge,
  call: callOpenFiles,
}

/** Why an entry was not opened: the viewer's decline reasons, plus the two non-present statuses
 * the surface itself reports (the bridge never sees those paths). */
export type NotOpenedReason = DeclineReason | 'missing' | 'excluded'

export interface OpenSetReport {
  /** Entries in the category, whatever their status. */
  total: number
  /** Paths the viewer opened, in category order. */
  opened: string[]
  /** Every other entry, by path, with why it was not opened. */
  notOpened: Array<{ path: string; reason: NotOpenedReason }>
  /** No HTML Viewer was registered when the set was delivered: nothing was opened. */
  viewerAbsent: boolean
}

/** Splits a resolved category by status, delivers the `present` paths through `deliverBatch`, and
 * merges what the viewer declined with what the surface withheld. Never throws. */
export function openCategoryInViewer(category: CategoryDetail): OpenSetReport {
  const present = category.entries.filter((entry) => entry.status === 'present')
  const withheld = category.entries
    .filter((entry) => entry.status !== 'present')
    .map((entry) => ({ path: entry.path, reason: entry.status as NotOpenedReason }))

  if (present.length === 0) {
    return { total: category.entries.length, opened: [], notOpened: withheld, viewerAbsent: false }
  }
  const outcome = deliverBatch(
    present.map((entry) => entry.path),
    [VIEWER_BATCH_TARGET],
  )
  const target = outcome.targets[0]
  if (!target || target.absent || !target.receipt) {
    return {
      total: category.entries.length,
      opened: [],
      notOpened: category.entries.map((entry) => ({
        path: entry.path,
        reason: entry.status === 'present' ? 'failed' : (entry.status as NotOpenedReason),
      })),
      viewerAbsent: true,
    }
  }
  const declined = new Map(target.receipt.declined.map((item) => [item.path, item.reason]))
  const opened = new Set(target.receipt.delivered)
  // Category order throughout, so the report reads in the order the set was stored.
  const notOpened: OpenSetReport['notOpened'] = []
  for (const entry of category.entries) {
    if (opened.has(entry.path)) continue
    const reason = entry.status === 'present' ? (declined.get(entry.path) ?? 'failed') : entry.status
    notOpened.push({ path: entry.path, reason })
  }
  return {
    total: category.entries.length,
    opened: category.entries.filter((entry) => opened.has(entry.path)).map((entry) => entry.path),
    notOpened,
    viewerAbsent: false,
  }
}

const REASON_TEXT: Record<NotOpenedReason, string> = {
  missing: 'file not found',
  excluded: 'private or ignored',
  incompatible: 'not a file type the viewer shows',
  capacity: 'no free viewer tab',
  failed: 'the viewer could not open it',
}

export interface OpenSetMessage {
  /** "Opened X of Y" plus, when anything was not opened, "; N declined: reason". */
  summary: string
  /** One line per entry that was not opened: its path and why. */
  details: Array<{ path: string; reason: string }>
}

/** The legible receipt for an open-as-set action. Reasons are summarised by kind in the summary
 * line and named per path in `details`. */
export function describeOpenSet(categoryName: string, report: OpenSetReport): OpenSetMessage {
  const details = report.notOpened.map((item) => ({
    path: item.path,
    reason: REASON_TEXT[item.reason],
  }))
  if (report.total === 0) {
    return { summary: `"${categoryName}" has no files to open.`, details }
  }
  if (report.viewerAbsent) {
    return {
      summary: `Opened 0 of ${report.total}: the HTML Viewer is not open.`,
      details,
    }
  }
  let summary = `Opened ${report.opened.length} of ${report.total} from "${categoryName}"`
  if (report.notOpened.length > 0) {
    const counts = new Map<NotOpenedReason, number>()
    for (const item of report.notOpened) counts.set(item.reason, (counts.get(item.reason) ?? 0) + 1)
    const reasons = [...counts].map(([reason, count]) => `${count} ${REASON_TEXT[reason]}`)
    summary += `; ${report.notOpened.length} declined: ${reasons.join(', ')}`
  }
  return { summary: `${summary}.`, details }
}
