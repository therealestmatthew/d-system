import { useEffect, useState, type FormEvent } from 'react'
import {
  VIEWER_BATCH_TARGET,
  describeOpenSet,
  openCategoryInViewer,
  type CategoryDetail,
  type OpenSetMessage,
} from './bookmarks'
import { useBatchAvailable } from './panelBridge'
import type { BookmarksModel } from './useBookmarks'

/** The outcome of the most recent action in this section: an error, a confirmation, or the receipt
 * of opening a category as a set (a summary line plus one line per entry that was not opened). */
interface SectionStatus {
  kind: 'info' | 'error'
  message: OpenSetMessage
}

type DetailState =
  | { id: string; state: 'loading' }
  | { id: string; state: 'error'; message: string }
  | { id: string; state: 'loaded'; category: CategoryDetail }

const STATUS_LABEL = {
  present: '',
  missing: 'missing',
  excluded: 'private or ignored',
} as const

function plain(message: string): OpenSetMessage {
  return { summary: message, details: [] }
}

/**
 * The File Browser's bookmark-category section (ADR-029, REQ-012 R09 and R10): lists categories,
 * creates, renames and deletes them, lists a category's files (a `missing` or `excluded` entry is
 * shown by its path and can still be removed), and opens a category as a set in the HTML Viewer
 * through `deliverBatch` (`bookmarks.ts`).
 *
 * "Open as set" is disabled while no HTML Viewer is registered (`useBatchAvailable`), never an
 * error (ADR-029 section 6 point 5). A category is identified by `category_id`; this component
 * holds names and counts from the shared list and re-reads a category's files each time it is
 * expanded or opened, so a stale status is never acted on.
 *
 * Adding a file is done from the tree's context menu (`FileTreeContextMenu`), not here.
 */
export default function BookmarkCategories({ model }: { model: BookmarksModel }) {
  const viewerAvailable = useBatchAvailable([VIEWER_BATCH_TARGET])
  const [open, setOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<DetailState | null>(null)
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameText, setRenameText] = useState('')
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const [status, setStatus] = useState<SectionStatus | null>(null)

  const { load, revision } = model

  // Read the expanded category's files whenever it is expanded or any change was made, so the list
  // shows the server's current present / missing / excluded status.
  useEffect(() => {
    if (expandedId === null) return
    let cancelled = false
    void load(expandedId).then((result) => {
      if (cancelled) return
      setDetail(
        result.ok
          ? { id: expandedId, state: 'loaded', category: result.value }
          : { id: expandedId, state: 'error', message: result.message },
      )
    })
    return () => {
      cancelled = true
    }
  }, [expandedId, revision, load])

  if (model.loadState === 'unavailable') {
    return (
      <p className="stage-placeholder-text stage-bookmarks__unavailable">
        Bookmarks are unavailable: the workbench routes are not mounted.
      </p>
    )
  }

  const fail = (message: string) => setStatus({ kind: 'error', message: plain(message) })
  const note = (message: string) => setStatus({ kind: 'info', message: plain(message) })

  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    const result = await model.create(newName)
    if (!result.ok) return fail(`Could not create the category: ${result.message}`)
    note(`Created category "${result.value.name}".`)
    setNewName('')
    setCreating(false)
  }

  async function handleRename(event: FormEvent, categoryId: string) {
    event.preventDefault()
    const result = await model.rename(categoryId, renameText)
    if (!result.ok) return fail(`Could not rename the category: ${result.message}`)
    note(`Renamed to "${result.value.name}".`)
    setRenamingId(null)
  }

  async function handleDelete(category: { category_id: string; name: string }) {
    const result = await model.remove(category.category_id)
    setConfirmDeleteId(null)
    if (!result.ok) return fail(`Could not delete the category: ${result.message}`)
    if (expandedId === category.category_id) setExpandedId(null)
    note(`Deleted category "${category.name}".`)
  }

  async function handleRemoveFile(categoryId: string, path: string) {
    const result = await model.removeFile(categoryId, path)
    if (!result.ok) return fail(`Could not remove the file: ${result.message}`)
    note(`Removed "${path}" from the category.`)
  }

  async function handleOpenSet(categoryId: string) {
    const result = await model.load(categoryId)
    if (!result.ok) return fail(`Could not open the category: ${result.message}`)
    const report = openCategoryInViewer(result.value)
    const message = describeOpenSet(result.value.name, report)
    setStatus({ kind: report.opened.length > 0 ? 'info' : 'error', message })
    if (expandedId === categoryId) {
      setDetail({ id: categoryId, state: 'loaded', category: result.value })
    }
  }

  return (
    <section className="stage-bookmarks" aria-label="Bookmark categories">
      <div className="stage-bookmarks__header">
        <button
          type="button"
          className="stage-bookmarks__toggle"
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          <span aria-hidden="true">{open ? '▾' : '▸'}</span> Bookmarks ({model.categories.length})
        </button>
        {open ? (
          <button
            type="button"
            className="stage-bookmarks__button"
            aria-label="New bookmark category"
            onClick={() => setCreating((value) => !value)}
          >
            + New category
          </button>
        ) : null}
      </div>

      {open ? (
        <div className="stage-bookmarks__body">
          {creating ? (
            <form className="stage-bookmarks__form" onSubmit={(event) => void handleCreate(event)}>
              <input
                type="text"
                aria-label="New category name"
                placeholder="Category name…"
                value={newName}
                autoFocus
                onChange={(event) => setNewName(event.target.value)}
              />
              <button type="submit" className="stage-bookmarks__button" disabled={newName.trim() === ''}>
                Create
              </button>
            </form>
          ) : null}

          {status ? (
            <div
              className={
                'stage-bookmarks__status' +
                (status.kind === 'error' ? ' stage-bookmarks__status--error' : '')
              }
              role="status"
            >
              <span>{status.message.summary}</span>
              {status.message.details.length > 0 ? (
                <ul className="stage-bookmarks__declined" aria-label="Files not opened">
                  {status.message.details.map((item) => (
                    <li key={item.path}>
                      <code>{item.path}</code>: {item.reason}
                    </li>
                  ))}
                </ul>
              ) : null}
              <button
                type="button"
                className="stage-file-browser__status-dismiss"
                aria-label="Dismiss bookmarks message"
                onClick={() => setStatus(null)}
              >
                ×
              </button>
            </div>
          ) : null}

          {model.loadState === 'loading' ? (
            <p className="stage-placeholder-text" role="status">Loading…</p>
          ) : model.loadState === 'error' ? (
            <p className="stage-placeholder-text stage-placeholder-text--absent" role="alert">
              Could not load the bookmark categories.
            </p>
          ) : model.categories.length === 0 ? (
            <p className="stage-placeholder-text">
              No categories yet. Create one, then right-click a file to add it.
            </p>
          ) : (
            <ul className="stage-bookmarks__list">
              {model.categories.map((category) => {
                const expanded = expandedId === category.category_id
                return (
                  <li key={category.category_id} className="stage-bookmarks__item">
                    <div className="stage-bookmarks__row">
                      {renamingId === category.category_id ? (
                        <form
                          className="stage-bookmarks__form"
                          onSubmit={(event) => void handleRename(event, category.category_id)}
                        >
                          <input
                            type="text"
                            aria-label={`New name for ${category.name}`}
                            value={renameText}
                            autoFocus
                            onChange={(event) => setRenameText(event.target.value)}
                          />
                          <button
                            type="submit"
                            className="stage-bookmarks__button"
                            disabled={renameText.trim() === ''}
                          >
                            Save
                          </button>
                          <button
                            type="button"
                            className="stage-bookmarks__button"
                            onClick={() => setRenamingId(null)}
                          >
                            Cancel
                          </button>
                        </form>
                      ) : (
                        <>
                          <button
                            type="button"
                            className="stage-bookmarks__name"
                            aria-expanded={expanded}
                            aria-label={`Files in ${category.name}`}
                            onClick={() => {
                              setExpandedId(expanded ? null : category.category_id)
                              setDetail(null)
                            }}
                          >
                            <span aria-hidden="true">{expanded ? '▾' : '▸'}</span> {category.name}{' '}
                            <span className="stage-bookmarks__count">({category.entry_count})</span>
                          </button>
                          <button
                            type="button"
                            className="stage-bookmarks__button"
                            aria-label={`Open ${category.name} as a set in the HTML Viewer`}
                            disabled={!viewerAvailable || category.entry_count === 0}
                            title={
                              !viewerAvailable
                                ? 'The HTML Viewer is not open.'
                                : category.entry_count === 0
                                  ? 'This category has no files.'
                                  : 'Open every file in the HTML Viewer'
                            }
                            onClick={() => void handleOpenSet(category.category_id)}
                          >
                            Open as set
                          </button>
                          <button
                            type="button"
                            className="stage-bookmarks__button"
                            aria-label={`Rename ${category.name}`}
                            onClick={() => {
                              setRenamingId(category.category_id)
                              setRenameText(category.name)
                              setConfirmDeleteId(null)
                            }}
                          >
                            Rename
                          </button>
                          {confirmDeleteId === category.category_id ? (
                            <>
                              <button
                                type="button"
                                className="stage-bookmarks__button stage-bookmarks__button--danger"
                                aria-label={`Confirm deleting ${category.name}`}
                                onClick={() => void handleDelete(category)}
                              >
                                Confirm delete
                              </button>
                              <button
                                type="button"
                                className="stage-bookmarks__button"
                                onClick={() => setConfirmDeleteId(null)}
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <button
                              type="button"
                              className="stage-bookmarks__button"
                              aria-label={`Delete ${category.name}`}
                              onClick={() => setConfirmDeleteId(category.category_id)}
                            >
                              Delete
                            </button>
                          )}
                        </>
                      )}
                    </div>
                    {expanded ? (
                      <div className="stage-bookmarks__files">
                        {detail === null || detail.id !== category.category_id || detail.state === 'loading' ? (
                          <p className="stage-placeholder-text" role="status">Loading…</p>
                        ) : detail.state === 'error' ? (
                          <p className="stage-placeholder-text stage-placeholder-text--absent" role="alert">
                            Could not load this category: {detail.message}
                          </p>
                        ) : detail.category.entries.length === 0 ? (
                          <p className="stage-placeholder-text">
                            No files. Right-click a file in the tree to add it.
                          </p>
                        ) : (
                          <ul className="stage-bookmarks__entries">
                            {detail.category.entries.map((entry) => (
                              <li key={entry.path} className="stage-bookmarks__entry">
                                <code
                                  className={
                                    entry.status === 'present'
                                      ? undefined
                                      : 'stage-bookmarks__entry-path--absent'
                                  }
                                >
                                  {entry.path}
                                </code>
                                {entry.status !== 'present' ? (
                                  <span className="stage-bookmarks__badge">
                                    {STATUS_LABEL[entry.status]}
                                  </span>
                                ) : null}
                                <button
                                  type="button"
                                  className="stage-bookmarks__button"
                                  aria-label={`Remove ${entry.path} from ${category.name}`}
                                  onClick={() => void handleRemoveFile(category.category_id, entry.path)}
                                >
                                  Remove
                                </button>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ) : null}
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      ) : null}
    </section>
  )
}
