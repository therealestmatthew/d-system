import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Button } from '../Button/Button'
import { ConfirmDialog, Dialog } from './Dialog'

describe('Dialog', () => {
  it('renders overlay, modal and dialog classes with the variant', async () => {
    const user = userEvent.setup()
    render(
      <Dialog trigger={<Button>Open</Button>} title="About" footer={(close) => <Button onPress={close}>Got it</Button>}>
        <p>Body text</p>
      </Dialog>,
    )
    await user.click(screen.getByRole('button', { name: 'Open' }))
    const dialog = screen.getByRole('dialog', { name: 'About' })
    expect(dialog).toHaveClass('ui-dialog')
    expect(dialog).toHaveAttribute('data-variant', 'info')
    expect(dialog.closest('.ui-modal')).not.toBeNull()
    expect(dialog.closest('.ui-overlay')).not.toBeNull()
    for (const part of ['header', 'title', 'body', 'footer']) {
      expect(dialog.querySelector(`.ui-dialog__${part}`)).not.toBeNull()
    }
  })

  it('Escape closes it and returns focus to the trigger', async () => {
    const user = userEvent.setup()
    render(
      <Dialog trigger={<Button>Open</Button>} title="About">
        <Button>Inside</Button>
      </Dialog>,
    )
    const trigger = screen.getByRole('button', { name: 'Open' })
    await user.click(trigger)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByRole('dialog').contains(document.activeElement)).toBe(true)
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).toBeNull()
    await waitFor(() => expect(trigger).toHaveFocus())
  })
})

describe('ConfirmDialog', () => {
  it('names object and consequence, focuses the safe button, danger rightmost', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <ConfirmDialog
        trigger={<Button variant="danger">Close session</Button>}
        object='session "build-42"'
        actionLabel="Close"
        consequence="This ends the shell."
        onConfirm={onConfirm}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Close session' }))
    const dialog = screen.getByRole('dialog', { name: 'Close session "build-42"?' })
    expect(dialog).toHaveAttribute('data-variant', 'confirm')
    expect(dialog).toHaveTextContent('This ends the shell.')
    const buttons = Array.from(dialog.querySelectorAll('.ui-dialog__footer button'))
    expect(buttons.map((b) => b.textContent)).toEqual(['Cancel', 'Close'])
    expect(buttons[1]).toHaveClass('ui-button--danger')
    expect(buttons[0]).toHaveFocus()
    await user.click(buttons[1]!)
    expect(onConfirm).toHaveBeenCalledOnce()
    expect(screen.queryByRole('dialog')).toBeNull()
  })
})
