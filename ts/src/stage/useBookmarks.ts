import { useCallback, useEffect, useRef, useState } from 'react'
import { bookmarksApi, type BookmarkResult, type CategoryDetail, type CategorySummary } from './bookmarks'

/** `unavailable`: the workbench routes are not mounted, so there is nothing to list or change. */
export type BookmarksLoadState = 'loading' | 'ready' | 'unavailable' | 'error'

export interface BookmarksModel {
  loadState: BookmarksLoadState
  categories: CategorySummary[]
  /** Increments after every successful change, so a view of one category's files knows to re-read
   * it. */
  revision: number
  refresh: () => Promise<void>
  create: (name: string) => Promise<BookmarkResult<CategoryDetail>>
  rename: (categoryId: string, name: string) => Promise<BookmarkResult<CategoryDetail>>
  remove: (categoryId: string) => Promise<BookmarkResult<{ deleted: string }>>
  addFile: (categoryId: string, path: string) => Promise<BookmarkResult<CategoryDetail>>
  removeFile: (categoryId: string, path: string) => Promise<BookmarkResult<CategoryDetail>>
  load: (categoryId: string) => Promise<BookmarkResult<CategoryDetail>>
}

/** The category list and the operations on it, shared by the File Browser's context menu and its
 * bookmarks section so a change made in one shows in the other. Holds only summaries (id, name,
 * count); a category's files are read on demand with `load`, never kept. */
export function useBookmarks(): BookmarksModel {
  const [loadState, setLoadState] = useState<BookmarksLoadState>('loading')
  const [categories, setCategories] = useState<CategorySummary[]>([])
  const [revision, setRevision] = useState(0)
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  const refresh = useCallback(async () => {
    const result = await bookmarksApi.list()
    if (!mounted.current) return
    if (result.ok) {
      setCategories(result.value)
      setLoadState('ready')
    } else {
      setLoadState(result.unavailable ? 'unavailable' : 'error')
    }
  }, [])

  useEffect(() => {
    // The first list is fetched on mount; `refresh` only sets state after the request settles.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh()
  }, [refresh])

  /** Runs a change and, when it succeeded, re-reads the list and bumps the revision. */
  const change = useCallback(
    async <T,>(run: () => Promise<BookmarkResult<T>>): Promise<BookmarkResult<T>> => {
      const result = await run()
      if (result.ok && mounted.current) {
        setRevision((value) => value + 1)
        await refresh()
      }
      return result
    },
    [refresh],
  )

  return {
    loadState,
    categories,
    revision,
    refresh,
    create: (name) => change(() => bookmarksApi.create(name)),
    rename: (categoryId, name) => change(() => bookmarksApi.rename(categoryId, name)),
    remove: (categoryId) => change(() => bookmarksApi.remove(categoryId)),
    addFile: (categoryId, path) => change(() => bookmarksApi.addFile(categoryId, path)),
    removeFile: (categoryId, path) => change(() => bookmarksApi.removeFile(categoryId, path)),
    load: (categoryId) => bookmarksApi.get(categoryId),
  }
}
