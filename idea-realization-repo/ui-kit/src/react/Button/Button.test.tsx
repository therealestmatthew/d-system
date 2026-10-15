import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Button, ToggleButton } from './Button'

describe('Button', () => {
  it('renders the contract classes for variant and size', () => {
    render(
      <>
        <Button variant="primary">Go</Button>
        <Button variant="danger" size="sm">
          Delete
        </Button>
        <Button iconOnly icon="⟳" aria-label="Refresh" size="lg" variant="ghost" />
      </>,
    )
    expect(screen.getByRole('button', { name: 'Go' })).toHaveClass('ui-button', 'ui-button--primary')
    expect(screen.getByRole('button', { name: 'Go' }).className).not.toMatch(/--md/)
    expect(screen.getByRole('button', { name: 'Delete' })).toHaveClass('ui-button--danger', 'ui-button--sm')
    const icon = screen.getByRole('button', { name: 'Refresh' })
    expect(icon).toHaveClass('ui-button--icon', 'ui-button--ghost', 'ui-button--lg')
    expect(icon.querySelector('.ui-button__icon')).toHaveAttribute('aria-hidden', 'true')
    expect(screen.getByRole('button', { name: 'Go' }).querySelector('.ui-button__label')).toHaveTextContent('Go')
  })

  it('presses with keyboard and pointer', async () => {
    const user = userEvent.setup()
    const onPress = vi.fn()
    render(<Button onPress={onPress}>Run</Button>)
    await user.click(screen.getByRole('button', { name: 'Run' }))
    expect(onPress).toHaveBeenCalledTimes(1)
    await user.keyboard('{Enter}')
    await user.keyboard(' ')
    expect(onPress).toHaveBeenCalledTimes(3)
  })

  it('isLoading sets aria-busy, shows a spinner, keeps the label and blocks presses', async () => {
    const user = userEvent.setup()
    const onPress = vi.fn()
    render(
      <Button isLoading onPress={onPress}>
        Generating…
      </Button>,
    )
    const button = screen.getByRole('button', { name: /Generating…/ })
    expect(button).toHaveAttribute('aria-busy', 'true')
    expect(button.querySelector('.ui-button__spinner')).not.toBeNull()
    expect(button.querySelector('.ui-button__label')).toHaveTextContent('Generating…')
    await user.click(button)
    expect(onPress).not.toHaveBeenCalled()
  })

  it('requires aria-label on an icon-only button at the type level', () => {
    // @ts-expect-error an icon-only button without aria-label must not compile
    const missingLabel = <Button iconOnly icon="⟳" />
    // @ts-expect-error an icon-only button takes no text children
    const withChildren = <Button iconOnly icon="⟳" aria-label="Refresh">Refresh</Button>
    expect(missingLabel).toBeTruthy()
    expect(withChildren).toBeTruthy()
  })
})

describe('ToggleButton', () => {
  it('toggles aria-pressed and data-selected', async () => {
    const user = userEvent.setup()
    render(<ToggleButton>Pin</ToggleButton>)
    const toggle = screen.getByRole('button', { name: 'Pin' })
    expect(toggle).toHaveClass('ui-button', 'ui-button--ghost')
    expect(toggle).toHaveAttribute('aria-pressed', 'false')
    await user.click(toggle)
    expect(toggle).toHaveAttribute('aria-pressed', 'true')
    expect(toggle).toHaveAttribute('data-selected', 'true')
  })
})
