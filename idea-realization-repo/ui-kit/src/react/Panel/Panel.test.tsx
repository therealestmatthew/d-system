import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { Button } from '../Button/Button'
import { Panel } from './Panel'

function Counter() {
  const [n, setN] = useState(0)
  return <button onClick={() => setN((v) => v + 1)}>count {n}</button>
}

function Thrower({ fail }: { fail: { current: boolean } }) {
  if (fail.current) throw new Error('data could not be read')
  return <p>healthy</p>
}

describe('Panel', () => {
  it('renders the contract anatomy', () => {
    const { container } = render(
      <Panel title="Runs" body="table" help={<span>help</span>} controls={<Button>Refresh</Button>}>
        content
      </Panel>,
    )
    const section = container.querySelector('section.ui-panel')!
    expect(section).toHaveAttribute('data-variant', 'standard')
    expect(section).not.toHaveAttribute('data-state')
    const title = section.querySelector('h2.ui-panel__title')!
    expect(section.getAttribute('aria-labelledby')).toBe(title.id)
    expect(screen.getByRole('region', { name: 'Runs' })).toBe(section)
    expect(section.querySelectorAll('.ui-panel__header')).toHaveLength(1)
    expect(section.querySelector('.ui-panel__identity h2.ui-panel__title')).not.toBeNull()
    expect(section.querySelector('.ui-panel__help')).toHaveTextContent('help')
    expect(screen.getByRole('toolbar', { name: 'Runs controls' })).toHaveClass('ui-panel__controls')
    expect(section.querySelector('.ui-panel__frame-actions')).not.toBeNull()
    expect(section.querySelector('.ui-panel__body')).toHaveAttribute('data-body', 'table')
  })

  it('maximize is an aria-pressed toggle, Escape exits, and child state survives', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <Panel title="Logs" body="stream">
        <Counter />
      </Panel>,
    )
    const section = container.querySelector('section.ui-panel')!
    const counterBefore = screen.getByRole('button', { name: 'count 0' })
    await user.click(counterBefore)
    await user.click(counterBefore)
    expect(screen.getByRole('button', { name: 'count 2' })).toBe(counterBefore)

    const maximize = screen.getByRole('button', { name: 'Maximize Logs' })
    expect(maximize).toHaveAttribute('aria-pressed', 'false')
    await user.click(maximize)
    expect(maximize).toHaveAttribute('aria-pressed', 'true')
    expect(section).toHaveAttribute('data-state', 'maximized')
    // Same DOM node and same state: the child was not remounted.
    expect(screen.getByRole('button', { name: 'count 2' })).toBe(counterBefore)

    await user.keyboard('{Escape}')
    expect(section).not.toHaveAttribute('data-state')
    expect(maximize).toHaveAttribute('aria-pressed', 'false')
    expect(screen.getByRole('button', { name: 'count 2' })).toBe(counterBefore)
  })

  it('collapse hides the body without unmounting it', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <Panel title="Inspector" body="form">
        <Counter />
      </Panel>,
    )
    const counter = screen.getByRole('button', { name: 'count 0' })
    await user.click(counter)
    const collapse = screen.getByRole('button', { name: 'Collapse Inspector' })
    expect(collapse).toHaveAttribute('aria-expanded', 'true')
    await user.click(collapse)
    expect(container.querySelector('section.ui-panel')).toHaveAttribute('data-state', 'collapsed')
    expect(collapse).toHaveAttribute('aria-expanded', 'false')
    expect(container.querySelector('.ui-panel__body')).toHaveAttribute('hidden')
    await user.click(collapse)
    expect(screen.getByRole('button', { name: 'count 1' })).toBe(counter)
  })

  it('contains a throwing child in an error state with Retry', async () => {
    const user = userEvent.setup()
    const spy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const fail = { current: true }
    const { container } = render(
      <div>
        <Panel title="Broken" body="document">
          <Thrower fail={fail} />
        </Panel>
        <Panel title="Healthy" body="document">
          <p>still here</p>
        </Panel>
      </div>,
    )
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('ui-state')
    expect(alert).toHaveAttribute('data-state', 'error')
    expect(alert).toHaveTextContent('Broken stopped working')
    expect(alert).toHaveTextContent('data could not be read')
    expect(screen.getByText('still here')).toBeInTheDocument()
    expect(container.querySelectorAll('.ui-panel__header')).toHaveLength(2)

    fail.current = false
    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect(screen.getByText('healthy')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).toBeNull()
    spy.mockRestore()
  })
})
