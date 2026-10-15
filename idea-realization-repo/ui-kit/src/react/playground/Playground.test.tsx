import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { ToastProvider, createToastQueue } from '../index'
import { axeViolations } from '../test-utils/axe'
import { Playground } from './Playground'

describe('playground composite', () => {
  it('has no axe violations', async () => {
    const queue = createToastQueue()
    const { container } = render(
      <ToastProvider queue={queue}>
        <Playground />
      </ToastProvider>,
    )
    expect(await axeViolations(container)).toEqual([])
  })

  it('has no axe violations with a dialog and a toast open', async () => {
    const user = userEvent.setup()
    const queue = createToastQueue()
    render(
      <ToastProvider queue={queue}>
        <Playground />
      </ToastProvider>,
    )
    await user.click(screen.getByRole('button', { name: 'Show error toast' }))
    await user.click(screen.getByRole('button', { name: 'Close session' }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(await axeViolations(document.body)).toEqual([])
  })
})

describe('axe helper', () => {
  it('does report a real violation (guards against a silently passing check)', async () => {
    const { container } = render(
      <div>
        <img src="x.png" />
        <button />
      </div>,
    )
    const ids = (await axeViolations(container)).map((v) => v.id)
    expect(ids).toEqual(expect.arrayContaining(['image-alt', 'button-name']))
  })
})
