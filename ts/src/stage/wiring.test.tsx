import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  vi.doUnmock('./StagePage')
  vi.resetModules()
})

// These render the elements the stage actually ships, not a bare ErrorBoundary, so dropping a
// boundary from App.tsx or from StagePage's panel portal fails a test (idea 000569).
describe('error boundary wiring', () => {
  it('App catches a render error that escapes the stage', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.doMock('./StagePage', () => ({
      default: () => {
        throw new Error('layout engine failed')
      },
    }))
    const { default: App } = await import('../App')
    render(<App />)
    expect(screen.getByRole('alert').textContent).toContain(
      'The stage stopped working: layout engine failed.',
    )
  })

  it('each portaled panel is guarded and named by its display name', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const { guardedPanel } = await import('./StagePage')
    function Broken(): never {
      throw new Error('panel failed')
    }
    render(
      <>
        {guardedPanel('notes-strip', Broken)}
        {guardedPanel('file-browser', () => <p>still here</p>)}
      </>,
    )
    expect(screen.getByRole('alert').textContent).toContain(
      'Notes stopped working: panel failed.',
    )
    expect(screen.getByText('still here')).toBeTruthy()
  })
})
