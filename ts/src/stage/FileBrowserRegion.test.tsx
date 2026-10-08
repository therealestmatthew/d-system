import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import FileBrowserRegion from './FileBrowserRegion'

// REQ-012 R28: the File Browser's listing state after the user browses from one folder to another.
// The backend is stubbed, the panel is real. The directory picker dialog is replaced by two
// buttons so a test can browse to any folder without driving the dialog's own requests.

vi.mock('./DirectoryPickerDialog', () => ({
  default: ({ onSelectDirectory }: { onSelectDirectory: (path: string) => void }) => (
    <div>
      <button type="button" onClick={() => onSelectDirectory('docs')}>
        browse docs
      </button>
      <button type="button" onClick={() => onSelectDirectory('src')}>
        browse src
      </button>
    </div>
  ),
}))

type SearchAnswer = () => Promise<Response>

/** Stubs `fetch`: the workbench routes are mounted, bookmarks are empty, and each `/search`
 * request is answered by the function registered for its `path` query. */
function stubBackend(searchAnswers: Record<string, SearchAnswer>) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input), 'http://localhost')
      if (url.pathname.endsWith('/demo/stage/terminal-enabled')) {
        return new Response(JSON.stringify({ terminal_enabled: true }), { status: 200 })
      }
      if (url.pathname.endsWith('/workbench/bookmarks')) return new Response('[]', { status: 200 })
      if (url.pathname.endsWith('/workbench/search')) {
        const answer = searchAnswers[url.searchParams.get('path') ?? '']
        return answer ? answer() : new Response(null, { status: 404 })
      }
      return new Response(null, { status: 404 })
    }),
  )
}

const listing = (...names: string[]) =>
  new Response(JSON.stringify(names.map((name) => ({ name, path: name, is_dir: false }))), {
    status: 200,
  })

beforeEach(() => {
  window.localStorage.clear()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  window.localStorage.clear()
})

describe('FileBrowserRegion listing state after a folder change (R28)', () => {
  it('shows the could-not-search alert, not Loading, when the new folder fails', async () => {
    stubBackend({
      '.': async () => listing('root-file.txt'),
      docs: async () => new Response(null, { status: 500 }),
    })
    render(<FileBrowserRegion />)
    await screen.findByText('root-file.txt')

    act(() => screen.getByRole('button', { name: 'browse docs' }).click())

    const alert = await screen.findByRole('alert')
    expect(alert.textContent).toBe('Could not search docs.')
    expect(screen.queryByText('Loading…')).toBeNull()
    expect(screen.queryByText('root-file.txt')).toBeNull()
  })

  it('replaces the alert when a later browse succeeds', async () => {
    stubBackend({
      '.': async () => listing('root-file.txt'),
      docs: async () => new Response(null, { status: 500 }),
      src: async () => listing('main.py'),
    })
    render(<FileBrowserRegion />)
    await screen.findByText('root-file.txt')

    act(() => screen.getByRole('button', { name: 'browse docs' }).click())
    await screen.findByRole('alert')

    act(() => screen.getByRole('button', { name: 'browse src' }).click())
    await screen.findByText('main.py')
    expect(screen.queryByRole('alert')).toBeNull()
    expect(screen.queryByText('Loading…')).toBeNull()
  })

  it('shows Loading and builds no tree from the previous folder while the new listing is pending', async () => {
    // The root and docs listings both hold a README.md. If the stale root entries were fed to
    // buildTree under the docs prefix, `README.md` would compute to `docs/README.md` and collide
    // with the real entry: React logs a duplicate-key error at that commit.
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    let resolveDocs: (response: Response) => void = () => {}
    const pendingDocs = new Promise<Response>((resolve) => {
      resolveDocs = resolve
    })
    stubBackend({
      '.': async () => listing('README.md', 'root-file.txt'),
      docs: () => pendingDocs,
    })
    render(<FileBrowserRegion />)
    await screen.findByText('root-file.txt')

    act(() => screen.getByRole('button', { name: 'browse docs' }).click())

    await screen.findByText('Loading…')
    expect(screen.queryByRole('alert')).toBeNull()
    expect(screen.queryByText('root-file.txt')).toBeNull()
    expect(screen.queryByText('README.md')).toBeNull()
    expect(consoleError).not.toHaveBeenCalled()

    // The pending listing then settles normally.
    await act(async () => {
      resolveDocs(listing('README.md', 'guide.md'))
    })
    await waitFor(() => expect(screen.getByText('guide.md')).toBeTruthy())
    expect(screen.queryByText('Loading…')).toBeNull()
    expect(consoleError).not.toHaveBeenCalled()
    consoleError.mockRestore()
  })

  it('shows Loading, not the old alert, when browsing back to a failed folder', async () => {
    let docsCalls = 0
    let resolveSecondDocs: (response: Response) => void = () => {}
    const secondDocs = new Promise<Response>((resolve) => {
      resolveSecondDocs = resolve
    })
    let resolveSrc: (response: Response) => void = () => {}
    const pendingSrc = new Promise<Response>((resolve) => {
      resolveSrc = resolve
    })
    stubBackend({
      '.': async () => listing('root-file.txt'),
      docs: () => {
        docsCalls += 1
        return docsCalls === 1 ? Promise.resolve(new Response(null, { status: 500 })) : secondDocs
      },
      src: () => pendingSrc,
    })
    render(<FileBrowserRegion />)
    await screen.findByText('root-file.txt')

    act(() => screen.getByRole('button', { name: 'browse docs' }).click())
    await screen.findByRole('alert')

    // src is pending, then the user returns to docs, whose refetch is also pending.
    act(() => screen.getByRole('button', { name: 'browse src' }).click())
    await screen.findByText('Loading…')
    act(() => screen.getByRole('button', { name: 'browse docs' }).click())
    await screen.findByText('Loading…')
    expect(screen.queryByRole('alert')).toBeNull()

    await act(async () => {
      resolveSecondDocs(listing('guide.md'))
    })
    await screen.findByText('guide.md')
    expect(screen.queryByRole('alert')).toBeNull()
    resolveSrc(listing('main.py'))
  })
})
