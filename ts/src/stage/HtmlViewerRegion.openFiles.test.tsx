import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import HtmlViewerRegion from './HtmlViewerRegion'
import { callOpenFiles, deliverBatch, viewerBridge, type ViewerBridgeHandle } from './panelBridge'

// The real HTML Viewer panel as the target of a batch (ADR-029 section 6 point 8, REQ-012 R10):
// the backend is stubbed, the panel and the bridge are real. The overview-location route fails, so
// the one starting tab is empty (no page selected), which is the state "fill empty tabs first"
// acts on.

function stubBackend() {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/demo/stage/terminal-enabled')) {
        return new Response(JSON.stringify({ terminal_enabled: true }), { status: 200 })
      }
      if (url.includes('/demo/stage/overview-location')) return new Response(null, { status: 500 })
      if (url.includes('/workbench/search')) return new Response('[]', { status: 200 })
      // The file route marks every file response with this header, which the viewer's existence
      // check requires (REQ-012 R29).
      if (url.includes('/workbench-file/')) {
        return new Response(null, { status: 200, headers: { 'Content-Security-Policy': 'sandbox' } })
      }
      return new Response(null, { status: 404 })
    }),
  )
}

beforeEach(() => {
  window.localStorage.clear()
  stubBackend()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  window.localStorage.clear()
})

function handle(): ViewerBridgeHandle {
  const registered = viewerBridge.get()
  if (!registered) throw new Error('the viewer did not register')
  return registered
}

const tabLabels = () => screen.getAllByRole('tab').map((tab) => tab.textContent)
const selectedTab = () => screen.getByRole('tab', { selected: true }).textContent
const iframeSrc = () => (screen.getByTitle('HTML Viewer') as HTMLIFrameElement).getAttribute('src')

async function mountedViewer() {
  render(<HtmlViewerRegion />)
  // Wait for the failed seed to settle: the tab then has a directory but no page.
  await screen.findByText('Select a file from the dropdown above, or a directory to search.')
}

describe('HtmlViewerRegion openFiles', () => {
  it('publishes openFiles on the bridge handle', async () => {
    await mountedViewer()
    expect(typeof handle().openFiles).toBe('function')
  })

  it('opens three files in three tabs and makes the first one active (R10)', async () => {
    await mountedViewer()
    expect(tabLabels()).toEqual(['Tab 1'])
    let receipt: ReturnType<NonNullable<ViewerBridgeHandle['openFiles']>> | undefined
    act(() => {
      receipt = handle().openFiles?.(['_public/a.html', 'docs/b.md', 'docs/c.svg'])
    })
    expect(receipt).toEqual({
      delivered: ['_public/a.html', 'docs/b.md', 'docs/c.svg'],
      declined: [],
    })
    expect(tabLabels()).toEqual(['Tab 1', 'Tab 2', 'Tab 3'])
    expect(selectedTab()).toBe('Tab 1')
    await waitFor(() => expect(iframeSrc()).toContain('/workbench-file/_public/a.html'))
    // The other two tabs hold the other two files.
    act(() => screen.getByRole('tab', { name: 'Tab 2' }).click())
    await waitFor(() => expect(iframeSrc()).toContain('/workbench-file/docs/b.md'))
    act(() => screen.getByRole('tab', { name: 'Tab 3' }).click())
    await waitFor(() => expect(iframeSrc()).toContain('/workbench-file/docs/c.svg'))
  })

  it('never replaces a tab holding a page and declines overflow with capacity', async () => {
    await mountedViewer()
    act(() => {
      handle().openFiles?.(['one.html', 'two.html', 'three.html'])
    })
    let receipt: ReturnType<NonNullable<ViewerBridgeHandle['openFiles']>> | undefined
    act(() => {
      receipt = handle().openFiles?.(['four.html', 'five.html', 'six.html'])
    })
    // Three tabs hold pages; one slot remained.
    expect(receipt).toEqual({
      delivered: ['four.html'],
      declined: [
        { path: 'five.html', reason: 'capacity' },
        { path: 'six.html', reason: 'capacity' },
      ],
    })
    expect(tabLabels()).toEqual(['Tab 1', 'Tab 2', 'Tab 3', 'Tab 4'])
    // The earlier pages are still where they were.
    act(() => screen.getByRole('tab', { name: 'Tab 1' }).click())
    await waitFor(() => expect(iframeSrc()).toContain('one.html'))
    act(() => screen.getByRole('tab', { name: 'Tab 3' }).click())
    await waitFor(() => expect(iframeSrc()).toContain('three.html'))

    let full: ReturnType<NonNullable<ViewerBridgeHandle['openFiles']>> | undefined
    act(() => {
      full = handle().openFiles?.(['seven.html'])
    })
    expect(full).toEqual({ delivered: [], declined: [{ path: 'seven.html', reason: 'capacity' }] })
    expect(tabLabels()).toHaveLength(4)
  })

  it('declines a file the viewer cannot show with incompatible and keeps the rest in order', async () => {
    await mountedViewer()
    let receipt: ReturnType<NonNullable<ViewerBridgeHandle['openFiles']>> | undefined
    act(() => {
      receipt = handle().openFiles?.(['tool.py', 'second.html', 'data.json'])
    })
    expect(receipt).toEqual({
      delivered: ['second.html'],
      declined: [
        { path: 'tool.py', reason: 'incompatible' },
        { path: 'data.json', reason: 'incompatible' },
      ],
    })
    // The empty first tab took the first delivered file; no extra tab was made.
    expect(tabLabels()).toEqual(['Tab 1'])
    await waitFor(() => expect(iframeSrc()).toContain('second.html'))
  })

  it('answers two calls made before a re-render from the combined state', async () => {
    await mountedViewer()
    const open = handle().openFiles!
    let first: ReturnType<typeof open> | undefined
    let second: ReturnType<typeof open> | undefined
    act(() => {
      first = open(['a.html', 'b.html'])
      second = open(['c.html', 'd.html', 'e.html'])
    })
    expect(first?.delivered).toEqual(['a.html', 'b.html'])
    expect(second?.delivered).toEqual(['c.html', 'd.html'])
    expect(second?.declined).toEqual([{ path: 'e.html', reason: 'capacity' }])
    expect(tabLabels()).toEqual(['Tab 1', 'Tab 2', 'Tab 3', 'Tab 4'])
  })

  it('makes the first delivered file of the second call the active tab, not the first tab', async () => {
    await mountedViewer()
    act(() => {
      handle().openFiles?.(['first.html'])
    })
    // The empty tab took the first file, so Tab 1 is active and the next set lands in new tabs.
    expect(selectedTab()).toBe('Tab 1')
    act(() => {
      handle().openFiles?.(['a.html', 'b.html', 'c.html'])
    })
    expect(tabLabels()).toEqual(['Tab 1', 'Tab 2', 'Tab 3', 'Tab 4'])
    expect(selectedTab()).toBe('Tab 2')
    await waitFor(() => expect(iframeSrc()).toContain('/workbench-file/a.html'))
  })

  it('is reachable through deliverBatch, the one file-passing path', async () => {
    await mountedViewer()
    let outcome: ReturnType<typeof deliverBatch> | undefined
    act(() => {
      outcome = deliverBatch(['x.html', 'y.html', 'z.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    })
    expect(outcome?.targets[0].absent).toBe(false)
    expect(outcome?.targets[0].receipt?.delivered).toEqual(['x.html', 'y.html', 'z.html'])
    expect(tabLabels()).toEqual(['Tab 1', 'Tab 2', 'Tab 3'])
  })
})
