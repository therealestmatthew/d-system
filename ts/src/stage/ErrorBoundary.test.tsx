import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { useEffect } from 'react'
import ErrorBoundary from './ErrorBoundary'
import IdeaExplorerRegion from './IdeaExplorerRegion'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

function Boom({ message }: { message: string }): never {
  throw new Error(message)
}

describe('ErrorBoundary (idea 000569)', () => {
  it('renders its children when nothing throws', () => {
    render(
      <ErrorBoundary label="Notes">
        <p>fine</p>
      </ErrorBoundary>,
    )
    expect(screen.getByText('fine')).toBeTruthy()
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('replaces only the panel that threw, with an alert naming it', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    render(
      <>
        <ErrorBoundary label="File Browser">
          <Boom message="tree exploded" />
        </ErrorBoundary>
        <ErrorBoundary label="Notes">
          <p>other panel still running</p>
        </ErrorBoundary>
      </>,
    )
    const alert = screen.getByRole('alert')
    expect(alert.textContent).toContain('File Browser stopped working: tree exploded.')
    expect(screen.getByText('other panel still running')).toBeTruthy()
  })

  it('Retry remounts the children, re-running their effects', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    let failing = true
    let mounts = 0
    function Flaky() {
      useEffect(() => {
        mounts += 1
      }, [])
      if (failing) throw new Error('backend not ready')
      return <p>recovered</p>
    }
    render(
      <ErrorBoundary label="Overview">
        <Flaky />
      </ErrorBoundary>,
    )
    expect(screen.getByRole('alert').textContent).toContain('Overview stopped working: backend not ready.')
    expect(mounts).toBe(0)
    failing = false
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    expect(screen.getByText('recovered')).toBeTruthy()
    expect(screen.queryByRole('alert')).toBeNull()
    expect(mounts).toBe(1)
  })
})

describe('loading and error status (idea 000569)', () => {
  it('announces loading as a status', () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => new Promise(() => {}))
    render(<IdeaExplorerRegion />)
    expect(screen.getByRole('status').textContent).toBe('Loading…')
  })

  it('announces a failed load as an alert', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('offline'))
    render(<IdeaExplorerRegion />)
    expect((await screen.findByRole('alert')).textContent).toBe('Could not load ideas.')
  })
})
