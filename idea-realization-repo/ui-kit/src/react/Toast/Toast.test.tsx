import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Button } from '../Button/Button'
import { TOAST_TIMEOUT_MS, ToastProvider, createToastQueue, useToast } from './Toast'

function Trigger() {
  const toast = useToast()
  return (
    <>
      <Button onPress={() => toast.show({ status: 'ok', title: 'Saved' })}>ok</Button>
      <Button
        onPress={() =>
          toast.show({ status: 'err', title: 'Upload failed', body: 'Connection closed.', action: { label: 'Retry', onAction: retry } })
        }
      >
        err
      </Button>
    </>
  )
}
const retry = vi.fn()

describe('Toast', () => {
  afterEach(() => vi.useRealTimers())

  it('renders region and toast classes with data-status', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <ToastProvider>
        <Trigger />
      </ToastProvider>,
    )
    await user.click(screen.getByRole('button', { name: 'err' }))
    const region = container.ownerDocument.querySelector('.ui-toast-region')!
    expect(region).not.toBeNull()
    const toast = region.querySelector('.ui-toast')!
    expect(toast).toHaveAttribute('data-status', 'err')
    expect(toast.querySelector('.ui-toast__title')).toHaveTextContent('Upload failed')
    expect(toast.querySelector('.ui-toast__body')).toHaveTextContent('Connection closed.')
    expect(toast.querySelector('.ui-toast__actions')).not.toBeNull()
    expect(toast.querySelector('.ui-toast__close')).toHaveAccessibleName('Dismiss')
    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect(retry).toHaveBeenCalledOnce()
    expect(container.ownerDocument.querySelector('.ui-toast')).toBeNull()
  })

  it('ok auto-dismisses after 5s; err persists', () => {
    vi.useFakeTimers()
    const queue = createToastQueue()
    render(<ToastProvider queue={queue}>{null}</ToastProvider>)
    act(() => {
      queue.show({ status: 'ok', title: 'Saved' })
      queue.show({ status: 'err', title: 'Failed', action: { label: 'Retry', onAction: () => undefined } })
    })
    expect(document.querySelectorAll('.ui-toast')).toHaveLength(2)
    act(() => {
      vi.advanceTimersByTime(TOAST_TIMEOUT_MS + 100)
    })
    const left = Array.from(document.querySelectorAll('.ui-toast'))
    expect(left.map((t) => t.getAttribute('data-status'))).toEqual(['err'])
    act(() => {
      vi.advanceTimersByTime(60_000)
    })
    expect(document.querySelectorAll('.ui-toast')).toHaveLength(1)
  })

  it('shows at most three at once', () => {
    const queue = createToastQueue()
    render(<ToastProvider queue={queue}>{null}</ToastProvider>)
    act(() => {
      for (let i = 0; i < 5; i++) queue.show({ status: 'err', title: `Failed ${i}` })
    })
    expect(document.querySelectorAll('.ui-toast')).toHaveLength(3)
  })
})
