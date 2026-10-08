import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import HtmlViewerRegion from './HtmlViewerRegion'
import { viewerBridge } from './panelBridge'

// REQ-012 R29: the viewer's page-exists check accepts only a response that came from the file
// route, which marks every file it serves with `Content-Security-Policy: sandbox`. With the route
// unregistered, the dev server's fallback answers 200 with the application shell and no such
// header; the viewer must report the page absent rather than frame the shell (idea 000555).

type FileResponse = () => Response

function stubBackend(fileResponse: FileResponse) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/demo/stage/terminal-enabled')) {
        return new Response(JSON.stringify({ terminal_enabled: true }), { status: 200 })
      }
      if (url.includes('/demo/stage/overview-location')) return new Response(null, { status: 500 })
      if (url.includes('/workbench/search')) return new Response('[]', { status: 200 })
      if (url.includes('/workbench-file/')) return fileResponse()
      return new Response(null, { status: 404 })
    }),
  )
}

const fromFileRoute: FileResponse = () =>
  new Response(null, { status: 200, headers: { 'Content-Security-Policy': 'sandbox' } })
const fromFallback: FileResponse = () =>
  new Response('<!doctype html><title>app shell</title>', {
    status: 200,
    headers: { 'Content-Type': 'text/html' },
  })

beforeEach(() => {
  window.localStorage.clear()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  window.localStorage.clear()
})

async function viewerHoldingSelection(path: string) {
  render(<HtmlViewerRegion />)
  await screen.findByText('Select a file from the dropdown above, or a directory to search.')
  act(() => {
    viewerBridge.get()?.openFiles?.([path])
  })
}

describe('HtmlViewerRegion page-exists check', () => {
  it('reports the page absent when an ok response lacks the file route header (R29)', async () => {
    stubBackend(fromFallback)
    await viewerHoldingSelection('_public/a.html')
    expect(await screen.findByText(/Selected page is absent/)).toBeTruthy()
    expect(screen.getByText('_public/a.html')).toBeTruthy()
    expect(document.querySelector('iframe')).toBeNull()
  })

  it('does not accept a different Content-Security-Policy as the file route marker (R29)', async () => {
    stubBackend(
      () => new Response(null, { status: 200, headers: { 'Content-Security-Policy': "default-src 'self'" } }),
    )
    await viewerHoldingSelection('_public/a.html')
    expect(await screen.findByText(/Selected page is absent/)).toBeTruthy()
    expect(document.querySelector('iframe')).toBeNull()
  })

  it('accepts a comma-merged multi-policy value that includes sandbox (R29)', async () => {
    stubBackend(
      () =>
        new Response(null, {
          status: 200,
          headers: { 'Content-Security-Policy': "default-src 'self', sandbox" },
        }),
    )
    await viewerHoldingSelection('_public/a.html')
    await waitFor(() =>
      expect(document.querySelector('iframe')?.getAttribute('src') ?? '').toContain(
        '/workbench-file/_public/a.html',
      ),
    )
  })

  it.each([
    ['.html', '_public/a.html'],
    ['.md', 'docs/b.md'],
    ['image', 'docs/c.png'],
  ])('still frames a %s file the file route served (R29)', async (_kind, path) => {
    stubBackend(fromFileRoute)
    await viewerHoldingSelection(path)
    await waitFor(() =>
      expect(document.querySelector('iframe')?.getAttribute('src') ?? '').toContain(`/workbench-file/${path}`),
    )
    expect(screen.queryByText(/Selected page is absent/)).toBeNull()
  })

  it('still reports a page the file route refused as absent', async () => {
    stubBackend(() => new Response('Not found', { status: 404 }))
    await viewerHoldingSelection('_public/gone.html')
    expect(await screen.findByText(/Selected page is absent/)).toBeTruthy()
  })
})

// REQ-012 R03/R04: the header badge shows the displayed file's mtime as the list route reports it
// (not page-load time), follows the active tab, and reads the time again when a file is selected
// again, so a file regenerated on disk shows its newer time.

function localStamp(iso: string): string {
  const moment = new Date(iso)
  const pad = (value: number) => String(value).padStart(2, '0')
  return (
    `${moment.getFullYear()}-${pad(moment.getMonth() + 1)}-${pad(moment.getDate())} ` +
    `${pad(moment.getHours())}:${pad(moment.getMinutes())}:${pad(moment.getSeconds())}`
  )
}

function stubBackendWithMtimes(mtimes: Record<string, string | null>) {
  const listCalls: string[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/demo/stage/terminal-enabled')) {
        return new Response(JSON.stringify({ terminal_enabled: true }), { status: 200 })
      }
      if (url.includes('/demo/stage/overview-location')) return new Response(null, { status: 500 })
      if (url.includes('/workbench/search')) {
        const entries = Object.keys(mtimes).map((path) => ({
          name: path.slice(path.lastIndexOf('/') + 1),
          path,
          is_dir: false,
          modified_at: mtimes[path],
        }))
        return new Response(JSON.stringify(entries), { status: 200 })
      }
      if (url.includes('/workbench/list')) {
        listCalls.push(url)
        const params = new URL(url, 'http://localhost').searchParams
        const directory = params.get('path') ?? '.'
        const entries = Object.keys(mtimes)
          .filter((path) => path.slice(0, path.lastIndexOf('/')) === directory)
          .map((path) => ({
            name: path.slice(path.lastIndexOf('/') + 1),
            path,
            is_dir: false,
            modified_at: mtimes[path],
          }))
        return new Response(JSON.stringify(entries), { status: 200 })
      }
      if (url.includes('/workbench-file/')) return fromFileRoute()
      return new Response(null, { status: 404 })
    }),
  )
  return listCalls
}

const badge = () => screen.getByTestId('html-viewer-modified')

describe('HtmlViewerRegion last-modified badge', () => {
  it('shows the file mtime the list route reports, not the load time (R03)', async () => {
    const mtimes = { '_public/a.html': '2026-03-01T10:00:00.000Z' }
    const listCalls = stubBackendWithMtimes(mtimes)
    await viewerHoldingSelection('_public/a.html')
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp(mtimes['_public/a.html'])}`))
    expect(badge().getAttribute('title')).toContain('2026-03-01T10:00:00.000Z')
    expect(listCalls[listCalls.length - 1]).toContain('path=_public')
    expect(listCalls[listCalls.length - 1]).toContain('q=a.html')
  })

  it('says so when the backend reports no time for the file (R03)', async () => {
    stubBackendWithMtimes({ '_public/a.html': null })
    await viewerHoldingSelection('_public/a.html')
    await waitFor(() => expect(badge().textContent).toBe('Modified time unavailable'))
  })

  it('is absent while no file is selected', async () => {
    stubBackendWithMtimes({})
    render(<HtmlViewerRegion />)
    await screen.findByText('Select a file from the dropdown above, or a directory to search.')
    expect(screen.queryByTestId('html-viewer-modified')).toBeNull()
  })

  it('follows the active tab when tabs hold files with different mtimes (R04)', async () => {
    const mtimes = {
      '_public/a.html': '2026-03-01T10:00:00.000Z',
      '_public/b.html': '2026-03-02T11:30:45.000Z',
    }
    stubBackendWithMtimes(mtimes)
    render(<HtmlViewerRegion />)
    await screen.findByText('Select a file from the dropdown above, or a directory to search.')
    act(() => {
      viewerBridge.get()?.openFiles?.(['_public/a.html', '_public/b.html'])
    })
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp(mtimes['_public/a.html'])}`))
    fireEvent.click(screen.getByRole('tab', { name: 'Tab 2' }))
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp(mtimes['_public/b.html'])}`))
    fireEvent.click(screen.getByRole('tab', { name: 'Tab 1' }))
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp(mtimes['_public/a.html'])}`))
  })

  it('shows the newer time after the file changes on disk and is selected again (R04)', async () => {
    const mtimes: Record<string, string | null> = { '_public/a.html': '2026-03-01T10:00:00.000Z' }
    stubBackendWithMtimes(mtimes)
    await viewerHoldingSelection('_public/a.html')
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp('2026-03-01T10:00:00.000Z')}`))

    mtimes['_public/a.html'] = '2026-03-05T09:09:09.000Z'
    fireEvent.click(screen.getByRole('button', { name: 'Choose a compatible file' }))
    fireEvent.click(await screen.findByRole('button', { name: '_public/a.html' }))
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp('2026-03-05T09:09:09.000Z')}`))
  })

  it('reads the time again on Refresh (R04)', async () => {
    const mtimes: Record<string, string | null> = { '_public/a.html': '2026-03-01T10:00:00.000Z' }
    stubBackendWithMtimes(mtimes)
    await viewerHoldingSelection('_public/a.html')
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp('2026-03-01T10:00:00.000Z')}`))
    mtimes['_public/a.html'] = '2026-03-06T00:00:01.000Z'
    fireEvent.click(screen.getByRole('button', { name: 'Refresh the current page' }))
    await waitFor(() => expect(badge().textContent).toBe(`Modified ${localStamp('2026-03-06T00:00:01.000Z')}`))
  })
})
