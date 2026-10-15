import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Badge, Chip, Pill } from './Pill'

describe('Pill, Badge, Chip', () => {
  it('pill carries status as data-status and in words', () => {
    const { container } = render(<Pill status="warn">Needs review</Pill>)
    const pill = container.querySelector('.ui-pill')!
    expect(pill).toHaveAttribute('data-status', 'warn')
    expect(pill).toHaveTextContent('Needs review')
    expect(pill.querySelector('.ui-pill__dot')).toHaveAttribute('aria-hidden', 'true')
  })

  it('badge shows the count', () => {
    const { container } = render(<Badge count={3} label="3 unread" />)
    expect(container.querySelector('.ui-badge')).toHaveTextContent('3')
  })

  it('chip remove button is labelled "Remove filter: X"', async () => {
    const user = userEvent.setup()
    const onRemove = vi.fn()
    const { container } = render(<Chip label="status: open" onRemove={onRemove} />)
    expect(container.querySelector('.ui-chip')).not.toBeNull()
    const remove = screen.getByRole('button', { name: 'Remove filter: status: open' })
    expect(remove).toHaveClass('ui-chip__remove')
    await user.click(remove)
    expect(onRemove).toHaveBeenCalledOnce()
  })
})
