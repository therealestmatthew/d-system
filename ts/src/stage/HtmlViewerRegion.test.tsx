import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
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
