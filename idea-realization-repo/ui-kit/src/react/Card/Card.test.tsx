import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Card, CardGrid, StatCard } from './Card'

describe('Card', () => {
  it('renders the contract parts and variants', () => {
    const { container } = render(
      <CardGrid>
        <Card kicker="Run" title="Summary" meta="Source: runs" actions={<button>Open</button>} variant="ai">
          Body
        </Card>
        <Card title="Plain">Body</Card>
      </CardGrid>,
    )
    expect(container.querySelector('.ui-card-grid')).not.toBeNull()
    const [ai, plain] = Array.from(container.querySelectorAll('.ui-card'))
    expect(ai).toHaveClass('ui-card', 'ui-card--ai')
    for (const part of ['kicker', 'title', 'body', 'meta', 'actions']) {
      expect(ai!.querySelector(`.ui-card__${part}`)).not.toBeNull()
    }
    expect(plain!.className).toBe('ui-card')
    expect(plain!.querySelector('h3.ui-card__title')).toHaveTextContent('Plain')
  })

  it('StatCard shows value and delta, and "Not recorded" instead of a made-up zero', () => {
    const { container } = render(
      <>
        <StatCard label="Open" value={12} delta="+3" />
        <StatCard label="Cost" value={null} />
      </>,
    )
    const [open, cost] = Array.from(container.querySelectorAll('.ui-card--stat'))
    expect(open!.querySelector('.ui-card__value')).toHaveTextContent('12')
    expect(open!.querySelector('.ui-card__delta')).toHaveTextContent('+3')
    expect(cost!.querySelector('.ui-card__value')).toHaveTextContent('Not recorded')
    expect(cost!.querySelector('.ui-card__value')).toHaveAttribute('data-state', 'not-recorded')
  })
})
