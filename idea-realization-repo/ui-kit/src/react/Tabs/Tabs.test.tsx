import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { Tabs } from './Tabs'

const ITEMS = [
  { id: 'a', label: 'Alpha', content: <p>alpha body</p> },
  { id: 'b', label: 'Beta', content: <p>beta body</p> },
  { id: 'c', label: 'Gamma', content: <p>gamma body</p> },
]

describe('Tabs', () => {
  it('renders the contract classes', () => {
    const { container } = render(<Tabs label="Views" items={ITEMS} />)
    expect(container.querySelector('.ui-tabs')).not.toBeNull()
    expect(screen.getByRole('tablist', { name: 'Views' })).toHaveClass('ui-tabs__list')
    for (const tab of screen.getAllByRole('tab')) expect(tab).toHaveClass('ui-tabs__tab')
    expect(screen.getByRole('tabpanel')).toHaveClass('ui-tabs__panel')
    expect(screen.getByRole('tab', { name: 'Alpha' })).toHaveAttribute('aria-selected', 'true')
  })

  it('arrow keys, Home and End move the selection', async () => {
    const user = userEvent.setup()
    render(<Tabs label="Views" items={ITEMS} />)
    await user.tab()
    expect(screen.getByRole('tab', { name: 'Alpha' })).toHaveFocus()
    await user.keyboard('{ArrowRight}')
    expect(screen.getByRole('tab', { name: 'Beta' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('tabpanel')).toHaveTextContent('beta body')
    await user.keyboard('{End}')
    expect(screen.getByRole('tab', { name: 'Gamma' })).toHaveAttribute('aria-selected', 'true')
    await user.keyboard('{Home}')
    expect(screen.getByRole('tab', { name: 'Alpha' })).toHaveAttribute('aria-selected', 'true')
    await user.keyboard('{ArrowLeft}')
    expect(screen.getByRole('tab', { name: 'Gamma' })).toHaveAttribute('aria-selected', 'true')
  })

  it('manual activation moves focus without selecting until Enter', async () => {
    const user = userEvent.setup()
    render(<Tabs label="Views" items={ITEMS} keyboardActivation="manual" />)
    await user.tab()
    await user.keyboard('{ArrowRight}')
    expect(screen.getByRole('tab', { name: 'Beta' })).toHaveFocus()
    expect(screen.getByRole('tab', { name: 'Alpha' })).toHaveAttribute('aria-selected', 'true')
    await user.keyboard('{Enter}')
    expect(screen.getByRole('tab', { name: 'Beta' })).toHaveAttribute('aria-selected', 'true')
  })
})
