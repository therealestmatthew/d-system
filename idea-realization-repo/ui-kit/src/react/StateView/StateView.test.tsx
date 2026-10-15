import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { StateView, type ViewState } from './StateView'

describe('StateView', () => {
  it.each<[ViewState, string | null]>([
    ['empty', null],
    ['error', 'alert'],
    ['missing', null],
    ['not-recorded', null],
  ])('%s renders data-state and role %s', (state, role) => {
    const { container } = render(<StateView state={state} title="T" body="B" action={<button>Act</button>} />)
    const el = container.querySelector('.ui-state')!
    expect(el).toHaveAttribute('data-state', state)
    expect(el.getAttribute('role')).toBe(role)
    expect(el.querySelector('.ui-state__title')).toHaveTextContent('T')
    expect(el.querySelector('.ui-state__body')).toHaveTextContent('B')
    expect(el.querySelector('.ui-state__action')).not.toBeNull()
  })

  describe('loading', () => {
    beforeEach(() => vi.useFakeTimers())
    afterEach(() => vi.useRealTimers())

    it('is a status region whose spinner and text appear after the delay', () => {
      const { container } = render(<StateView state="loading" title="Searching…" />)
      const el = screen.getByRole('status')
      expect(el).toHaveClass('ui-state')
      expect(el).toHaveAttribute('data-state', 'loading')
      expect(container.querySelector('.ui-spinner')).toBeNull()
      act(() => {
        vi.advanceTimersByTime(150)
      })
      expect(container.querySelector('.ui-spinner')).not.toBeNull()
      expect(el).toHaveTextContent('Searching…')
    })
  })
})
