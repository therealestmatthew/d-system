import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import HtmlViewerRegion from './HtmlViewerRegion'
import { viewerBridge, type ViewerBridgeHandle } from './panelBridge'

// REQ-012 R01: double-clicking a viewer tab opens that tab's file in a new browser tab through
// the same URL the "Open page in a new tab" link uses. The backend is stubbed, the panel and the
// bridge are real, and `window.open` is a spy.

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

let openSpy: ReturnType<typeof vi.fn>

beforeEach(() => {
  window.localStorage.clear()
  stubBackend()
  openSpy = vi.fn(() => null)
  vi.stubGlobal('open', openSpy)
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

const tab = (name: string) => screen.getByRole('tab', { name })

async function viewerWithThreeFiles() {
  render(<HtmlViewerRegion />)
  await screen.findByText('Select a file from the dropdown above, or a directory to search.')
  act(() => {
    handle().openFiles?.(['_public/a.html', 'docs/b.md', 'docs/c.png'])
  })
}

describe('HtmlViewerRegion double-click to open in a browser tab', () => {
  it('opens each tab at its own file URL, whichever tab is active (R01)', async () => {
    await viewerWithThreeFiles()
    expect(tab('Tab 1').getAttribute('aria-selected')).toBe('true')
    for (const [name, path] of [
      ['Tab 2', 'docs/b.md'],
      ['Tab 3', 'docs/c.png'],
      ['Tab 1', '_public/a.html'],
    ]) {
      fireEvent.doubleClick(tab(name))
      expect(openSpy).toHaveBeenLastCalledWith(
        `/workbench-file/${path}`,
        '_blank',
        'noopener,noreferrer',
      )
    }
    expect(openSpy).toHaveBeenCalledTimes(3)
  })

  it('uses the same URL as the Open-in-tab link', async () => {
    await viewerWithThreeFiles()
    fireEvent.click(screen.getByRole('button', { name: 'Embedded' }))
    const link = screen.getByRole('link', { name: /Open page in a new tab/ })
    fireEvent.doubleClick(tab('Tab 1'))
    expect(openSpy.mock.calls[0][0]).toBe(link.getAttribute('href'))
  })

  it('does nothing for a tab with no file selected', async () => {
    render(<HtmlViewerRegion />)
    await screen.findByText('Select a file from the dropdown above, or a directory to search.')
    fireEvent.doubleClick(tab('Tab 1'))
    expect(openSpy).not.toHaveBeenCalled()
  })

  it('leaves single-click selection and tab closing unchanged', async () => {
    await viewerWithThreeFiles()
    fireEvent.click(tab('Tab 2'))
    expect(tab('Tab 2').getAttribute('aria-selected')).toBe('true')
    fireEvent.click(screen.getByRole('button', { name: 'Close tab 3' }))
    expect(screen.getAllByRole('tab').map((t) => t.textContent)).toEqual(['Tab 1', 'Tab 2'])
    expect(openSpy).not.toHaveBeenCalled()
  })

  it('opens on Shift+Enter and Shift+Space, but not on plain Enter or Space', async () => {
    await viewerWithThreeFiles()
    fireEvent.keyDown(tab('Tab 2'), { key: 'Enter' })
    fireEvent.keyDown(tab('Tab 2'), { key: ' ' })
    expect(openSpy).not.toHaveBeenCalled()
    fireEvent.keyDown(tab('Tab 2'), { key: 'Enter', shiftKey: true })
    expect(openSpy).toHaveBeenLastCalledWith('/workbench-file/docs/b.md', '_blank', 'noopener,noreferrer')
    fireEvent.keyDown(tab('Tab 3'), { key: ' ', shiftKey: true })
    // The keyup that follows must not also activate the button (Firefox activates on keyup).
    expect(fireEvent.keyUp(tab('Tab 3'), { key: ' ', shiftKey: true })).toBe(false)
    expect(fireEvent.keyUp(tab('Tab 3'), { key: ' ' })).toBe(true)
    expect(tab('Tab 1').getAttribute('aria-selected')).toBe('true')
    expect(tab('Tab 3').getAttribute('aria-selected')).toBe('false')
    expect(openSpy).toHaveBeenLastCalledWith('/workbench-file/docs/c.png', '_blank', 'noopener,noreferrer')
    expect(openSpy).toHaveBeenCalledTimes(2)
  })
})
