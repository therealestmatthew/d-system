import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import BookmarkCategories from './BookmarkCategories'
import FileTreeContextMenu from './FileTreeContextMenu'
import {
  describeOpenSet,
  openCategoryInViewer,
  type CategoryDetail,
  type CategorySummary,
  type EntryStatus,
} from './bookmarks'
import { viewerBridge, type BatchReceipt, type ViewerBridgeHandle } from './panelBridge'
import type { BookmarksModel } from './useBookmarks'

// REQ-012 R10 (a category of three opens all three), R11 (a missing file is named, the rest open),
// R08 (no viewer registered disables the action) and the "opened X of Y; N declined: reason"
// receipt, with a stub viewer standing in for the HTML Viewer.

function category(entries: Array<[string, EntryStatus]>, name = 'Live demo'): CategoryDetail {
  return {
    category_id: 'live-demo',
    name,
    entries: entries.map(([path, status]) => ({ path, status })),
  }
}

const registrations: ViewerBridgeHandle[] = []
function registerViewer(openFiles: (paths: string[]) => BatchReceipt): {
  received: string[][]
  handle: ViewerBridgeHandle
} {
  const received: string[][] = []
  const handle: ViewerBridgeHandle = {
    tabs: [],
    openInTab: () => undefined,
    openFiles: (paths) => {
      received.push(paths)
      return openFiles(paths)
    },
  }
  viewerBridge.register(handle)
  registrations.push(handle)
  return { received, handle }
}
const acceptAll = (paths: string[]): BatchReceipt => ({ delivered: [...paths], declined: [] })

afterEach(() => {
  cleanup()
  registrations.splice(0).forEach((handle) => viewerBridge.unregister(handle))
})

describe('openCategoryInViewer', () => {
  it('delivers all three files of a three-file category, not the first only (R10)', () => {
    const { received } = registerViewer(acceptAll)
    const report = openCategoryInViewer(
      category([
        ['a.html', 'present'],
        ['b.md', 'present'],
        ['c.svg', 'present'],
      ]),
    )
    expect(received).toEqual([['a.html', 'b.md', 'c.svg']])
    expect(report.opened).toEqual(['a.html', 'b.md', 'c.svg'])
    expect(report.notOpened).toEqual([])
    expect(describeOpenSet('Live demo', report)).toEqual({
      summary: 'Opened 3 of 3 from "Live demo".',
      details: [],
    })
  })

  it('opens the remaining files and names the missing one by path (R11)', () => {
    const { received } = registerViewer(acceptAll)
    const report = openCategoryInViewer(
      category([
        ['a.html', 'present'],
        ['gone/b.html', 'missing'],
        ['c.html', 'present'],
      ]),
    )
    // The bridge is handed only the present paths; the missing one never reaches it.
    expect(received).toEqual([['a.html', 'c.html']])
    expect(report.opened).toEqual(['a.html', 'c.html'])
    expect(report.notOpened).toEqual([{ path: 'gone/b.html', reason: 'missing' }])
    expect(describeOpenSet('Live demo', report)).toEqual({
      summary: 'Opened 2 of 3 from "Live demo"; 1 declined: 1 file not found.',
      details: [{ path: 'gone/b.html', reason: 'file not found' }],
    })
  })

  it('reports viewer declines (capacity, incompatible) and excluded entries by path, in category order', () => {
    registerViewer((paths) => ({
      delivered: paths.filter((path) => path !== 'e.html' && path !== 'x.py'),
      declined: [
        ...(paths.includes('x.py') ? [{ path: 'x.py', reason: 'incompatible' as const }] : []),
        { path: 'e.html', reason: 'capacity' },
      ],
    }))
    const report = openCategoryInViewer(
      category([
        ['a.html', 'present'],
        ['x.py', 'present'],
        ['secret.md', 'excluded'],
        ['e.html', 'present'],
      ]),
    )
    expect(report.opened).toEqual(['a.html'])
    expect(report.notOpened).toEqual([
      { path: 'x.py', reason: 'incompatible' },
      { path: 'secret.md', reason: 'excluded' },
      { path: 'e.html', reason: 'capacity' },
    ])
    const message = describeOpenSet('Live demo', report)
    expect(message.summary).toBe(
      'Opened 1 of 4 from "Live demo"; 3 declined: 1 not a file type the viewer shows, 1 private or ignored, 1 no free viewer tab.',
    )
    expect(message.details.map((item) => item.path)).toEqual(['x.py', 'secret.md', 'e.html'])
  })

  it('opens nothing and throws nothing when no viewer is registered', () => {
    const report = openCategoryInViewer(
      category([
        ['a.html', 'present'],
        ['b.html', 'missing'],
      ]),
    )
    expect(report.viewerAbsent).toBe(true)
    expect(report.opened).toEqual([])
    expect(report.notOpened.map((item) => item.path)).toEqual(['a.html', 'b.html'])
    expect(describeOpenSet('Live demo', report).summary).toBe(
      'Opened 0 of 2: the HTML Viewer is not open.',
    )
  })

  it('does not call the viewer when no entry is present, and still names each', () => {
    const { received } = registerViewer(acceptAll)
    const report = openCategoryInViewer(category([['a.html', 'missing']]))
    expect(received).toEqual([])
    expect(report.viewerAbsent).toBe(false)
    expect(describeOpenSet('Live demo', report).summary).toBe(
      'Opened 0 of 1 from "Live demo"; 1 declined: 1 file not found.',
    )
  })

  it('treats a viewer that throws as declining every path', () => {
    registerViewer(() => {
      throw new Error('boom')
    })
    const report = openCategoryInViewer(category([['a.html', 'present']]))
    expect(report.opened).toEqual([])
    expect(report.notOpened).toEqual([{ path: 'a.html', reason: 'failed' }])
  })

  it('has a message for an empty category', () => {
    expect(describeOpenSet('Empty', openCategoryInViewer(category([], 'Empty'))).summary).toBe(
      '"Empty" has no files to open.',
    )
  })
})

// --- the section ------------------------------------------------------------------------------

function model(overrides: Partial<BookmarksModel> = {}, detail?: CategoryDetail): BookmarksModel {
  const summaries: CategorySummary[] = [
    { category_id: 'live-demo', name: 'Live demo', entry_count: detail?.entries.length ?? 0 },
  ]
  const ok = <T,>(value: T) => Promise.resolve({ ok: true as const, value })
  return {
    loadState: 'ready',
    categories: summaries,
    revision: 0,
    refresh: () => Promise.resolve(),
    create: () => ok(category([])),
    rename: () => ok(category([])),
    remove: () => ok({ deleted: 'live-demo' }),
    addFile: () => ok(category([])),
    removeFile: () => ok(category([])),
    load: () => ok(detail ?? category([])),
    ...overrides,
  }
}

async function openSection() {
  fireEvent.click(screen.getByRole('button', { name: /Bookmarks \(/ }))
}

describe('BookmarkCategories', () => {
  const three = category([
    ['a.html', 'present'],
    ['b.md', 'present'],
    ['c.svg', 'present'],
  ])

  it('disables Open as set while no viewer is registered, then enables it when one mounts (R08)', async () => {
    render(<BookmarkCategories model={model({}, three)} />)
    await openSection()
    const button = screen.getByRole('button', { name: 'Open Live demo as a set in the HTML Viewer' })
    expect((button as HTMLButtonElement).disabled).toBe(true)
    let handle: ViewerBridgeHandle | undefined
    act(() => {
      handle = registerViewer(acceptAll).handle
    })
    await waitFor(() => expect((button as HTMLButtonElement).disabled).toBe(false))
    act(() => viewerBridge.unregister(handle!))
    await waitFor(() => expect((button as HTMLButtonElement).disabled).toBe(true))
  })

  it('shows the receipt with declined paths after opening a category', async () => {
    registerViewer((paths) => ({
      delivered: paths.slice(0, 2),
      declined: paths.slice(2).map((path) => ({ path, reason: 'capacity' as const })),
    }))
    const withMissing = category([
      ['a.html', 'present'],
      ['gone.html', 'missing'],
      ['b.md', 'present'],
      ['c.svg', 'present'],
    ])
    render(<BookmarkCategories model={model({}, withMissing)} />)
    await openSection()
    fireEvent.click(screen.getByRole('button', { name: 'Open Live demo as a set in the HTML Viewer' }))
    const status = await screen.findByText(/Opened 2 of 4 from "Live demo"/)
    expect(status.textContent).toBe(
      'Opened 2 of 4 from "Live demo"; 2 declined: 1 file not found, 1 no free viewer tab.',
    )
    const list = screen.getByRole('list', { name: 'Files not opened' })
    expect(within(list).getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      'gone.html: file not found',
      'c.svg: no free viewer tab',
    ])
  })

  it('lists a category\'s files with missing and excluded entries marked by path', async () => {
    const mixed = category([
      ['a.html', 'present'],
      ['gone.html', 'missing'],
      ['_p/x.md', 'excluded'],
    ])
    render(<BookmarkCategories model={model({}, mixed)} />)
    await openSection()
    fireEvent.click(screen.getByRole('button', { name: 'Files in Live demo' }))
    await screen.findByText('gone.html')
    expect(screen.getByText('missing')).toBeTruthy()
    expect(screen.getByText('private or ignored')).toBeTruthy()
    expect(screen.getByText('_p/x.md')).toBeTruthy()
    // A missing entry can still be removed.
    expect(screen.getByRole('button', { name: 'Remove gone.html from Live demo' })).toBeTruthy()
  })

  it('creates, renames and deletes through the model', async () => {
    const create = vi.fn(() => Promise.resolve({ ok: true as const, value: category([], 'Fresh') }))
    const rename = vi.fn(() => Promise.resolve({ ok: true as const, value: category([], 'Renamed') }))
    const remove = vi.fn(() => Promise.resolve({ ok: true as const, value: { deleted: 'live-demo' } }))
    render(<BookmarkCategories model={model({ create, rename, remove })} />)
    await openSection()

    fireEvent.click(screen.getByRole('button', { name: 'New bookmark category' }))
    fireEvent.change(screen.getByLabelText('New category name'), { target: { value: 'Fresh' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create' }))
    await waitFor(() => expect(create).toHaveBeenCalledWith('Fresh'))

    fireEvent.click(screen.getByRole('button', { name: 'Rename Live demo' }))
    fireEvent.change(screen.getByLabelText('New name for Live demo'), { target: { value: 'Renamed' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))
    await waitFor(() => expect(rename).toHaveBeenCalledWith('live-demo', 'Renamed'))

    fireEvent.click(screen.getByRole('button', { name: 'Delete Live demo' }))
    expect(remove).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Confirm deleting Live demo' }))
    await waitFor(() => expect(remove).toHaveBeenCalledWith('live-demo'))
  })

  it('shows a refusal from the server as an error message', async () => {
    const create = vi.fn(() =>
      Promise.resolve({ ok: false as const, unavailable: false, message: "A category named 'x' already exists." }),
    )
    render(<BookmarkCategories model={model({ create })} />)
    await openSection()
    fireEvent.click(screen.getByRole('button', { name: 'New bookmark category' }))
    fireEvent.change(screen.getByLabelText('New category name'), { target: { value: 'x' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create' }))
    await screen.findByText("Could not create the category: A category named 'x' already exists.")
  })

  it('says bookmarks are unavailable when the routes are not mounted', () => {
    render(<BookmarkCategories model={model({ loadState: 'unavailable', categories: [] })} />)
    expect(screen.getByText(/Bookmarks are unavailable/)).toBeTruthy()
  })
})

// --- the context menu -------------------------------------------------------------------------

function menu(props: Partial<React.ComponentProps<typeof FileTreeContextMenu>> = {}) {
  const handlers = {
    onReveal: vi.fn(),
    onOpenInViewer: vi.fn(),
    onCopyRelativePath: vi.fn(),
    onCopyAbsolutePath: vi.fn(),
    onInjectPath: vi.fn(),
    onAddToCategory: vi.fn(),
    onAddToNewCategory: vi.fn(),
    onClose: vi.fn(),
  }
  render(
    <FileTreeContextMenu
      x={10}
      y={10}
      entryName="a.html"
      viewerCompatible
      viewerAvailable={false}
      viewerTabs={[]}
      terminalAvailable={false}
      isFile
      bookmarkCategories={[{ category_id: 'live-demo', name: 'Live demo', entry_count: 1 }]}
      {...handlers}
      {...props}
    />,
  )
  return handlers
}

describe('context menu: add to bookmark category', () => {
  it('adds the file to an existing category by id', () => {
    const handlers = menu()
    fireEvent.click(screen.getByRole('menuitem', { name: /Add to bookmark category/ }))
    fireEvent.click(screen.getByRole('menuitem', { name: 'Live demo' }))
    expect(handlers.onAddToCategory).toHaveBeenCalledWith('live-demo')
    expect(handlers.onClose).toHaveBeenCalled()
  })

  it('creates a new category and adds the file in one step', () => {
    const handlers = menu()
    fireEvent.click(screen.getByRole('menuitem', { name: /Add to bookmark category/ }))
    fireEvent.click(screen.getByRole('menuitem', { name: 'New category…' }))
    const submit = screen.getByRole('button', { name: 'Create and add' }) as HTMLButtonElement
    expect(submit.disabled).toBe(true)
    fireEvent.change(screen.getByLabelText('New category name'), { target: { value: 'Favorites' } })
    fireEvent.click(submit)
    expect(handlers.onAddToNewCategory).toHaveBeenCalledWith('Favorites')
  })

  it('is disabled when the bookmark routes are unavailable', () => {
    menu({ bookmarkCategories: null })
    const item = screen.getByRole('menuitem', { name: /Add to bookmark category/ }) as HTMLButtonElement
    expect(item.disabled).toBe(true)
  })

  it('is absent for a directory', () => {
    menu({ isFile: false, viewerCompatible: false })
    expect(screen.queryByRole('menuitem', { name: /Add to bookmark category/ })).toBeNull()
  })
})
