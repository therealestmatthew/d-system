import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { axeViolations } from '../test-utils/axe'
import { ApprovalCard, type ApprovalCardProps } from './ApprovalCard'

function props(overrides: Partial<ApprovalCardProps> = {}): ApprovalCardProps {
  return {
    proposal: 'Send the notice: allow benefits',
    object: 'the notice for SYN-0142',
    agent: 'Claude via Amazon Bedrock · Notice Drafting (Sonnet 5)',
    summary: <p>Misconduct is not established on this record.</p>,
    preview: <p>We have decided you can receive unemployment benefits.</p>,
    previewLabel: 'Drafted notice',
    impact: 'Sends the notice to the claimant.',
    undo: 'It cannot be recalled once sent.',
    risk: 'consequential',
    onApprove: vi.fn(),
    onEdit: vi.fn(),
    onReject: vi.fn(),
    onEscalate: vi.fn(),
    ...overrides,
  }
}

describe('ApprovalCard', () => {
  it('is a region named by its heading, with every part, the statement and "not recorded"', () => {
    render(<ApprovalCard {...props()} />)
    const region = screen.getByRole('region', { name: 'Send the notice: allow benefits' })
    expect(region).toHaveClass('ui-approval')
    expect(region).toHaveAttribute('data-state', 'pending')
    expect(region).toHaveAttribute('data-risk', 'consequential')
    for (const part of ['header', 'title', 'agent', 'statement', 'summary', 'preview', 'impact', 'actions', 'record']) {
      expect(region.querySelector(`.ui-approval__${part}`)).not.toBeNull()
    }
    expect(region).toHaveTextContent('Claude recommends; the examiner decides.')
    expect(region.querySelector('.ui-approval__agent')).toHaveTextContent('Proposed by Claude via Amazon Bedrock')
    expect(within(region).getByRole('region', { name: 'Drafted notice: Send the notice: allow benefits' })).toHaveAttribute('tabindex', '0')
    expect(region.querySelector('.ui-approval__record .ui-state[data-state="not-recorded"]')).toHaveTextContent(
      'Decision: not recorded',
    )
    expect(within(region).getByRole('button', { name: 'Escalate to supervisor' })).toHaveClass(
      'ui-button--ghost',
      'ui-approval__escalate',
    )
  })

  it('never makes Approve the default action: no autofocus, not a submit button, focus stays put', () => {
    render(<ApprovalCard {...props({ risk: 'routine' })} />)
    const approve = screen.getByRole('button', { name: 'Approve' })
    expect(approve).not.toHaveAttribute('autofocus')
    expect(approve).toHaveAttribute('type', 'button')
    expect(approve).not.toHaveFocus()
    expect(document.activeElement).toBe(document.body)
  })

  it('routine: Approve acts at once', async () => {
    const user = userEvent.setup()
    const p = props({ risk: 'routine' })
    render(<ApprovalCard {...p} />)
    await user.click(screen.getByRole('button', { name: 'Approve' }))
    expect(p.onApprove).toHaveBeenCalledOnce()
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('consequential: Approve opens a confirm naming the object and consequence, focused on Cancel', async () => {
    const user = userEvent.setup()
    const p = props()
    render(<ApprovalCard {...p} />)
    await user.click(screen.getByRole('button', { name: 'Approve' }))
    expect(p.onApprove).not.toHaveBeenCalled()
    const dialog = screen.getByRole('dialog', { name: 'Approve the notice for SYN-0142?' })
    expect(dialog).toHaveTextContent('Sends the notice to the claimant.')
    expect(dialog).toHaveTextContent('It cannot be recalled once sent.')
    expect(within(dialog).getByRole('button', { name: 'Cancel' })).toHaveFocus()
    await user.keyboard('{Enter}')
    expect(p.onApprove).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: 'Approve' }))
    await user.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Approve' }))
    expect(p.onApprove).toHaveBeenCalledOnce()
  })

  it('Reject requires a reason and passes it on', async () => {
    const user = userEvent.setup()
    const p = props({ rejectNote: 'Rejecting does not, on its own, send the case to a supervisor.' })
    render(<ApprovalCard {...p} />)
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    const dialog = screen.getByRole('dialog', { name: 'Reject the notice for SYN-0142?' })
    expect(dialog).toHaveAttribute('data-variant', 'form')
    expect(dialog).toHaveTextContent('Rejecting does not, on its own, send the case to a supervisor.')
    const reason = within(dialog).getByRole('textbox', { name: 'Reason (required)' })
    await user.click(within(dialog).getByRole('button', { name: 'Reject' }))
    expect(p.onReject).not.toHaveBeenCalled()
    expect(within(dialog).getByRole('alert')).toHaveTextContent('Enter a reason before rejecting.')
    expect(reason).toHaveAttribute('aria-invalid', 'true')
    await user.type(reason, '  The warning was delivered by hand.  ')
    await user.click(within(dialog).getByRole('button', { name: 'Reject' }))
    expect(p.onReject).toHaveBeenCalledWith('The warning was delivered by hand.')
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('Edit and Escalate call their handlers; labels can be overridden', async () => {
    const user = userEvent.setup()
    const p = props({ labels: { approve: 'Accept' } })
    render(<ApprovalCard {...p} />)
    expect(screen.getByRole('button', { name: 'Accept' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Edit' }))
    await user.click(screen.getByRole('button', { name: 'Escalate to supervisor' }))
    expect(p.onEdit).toHaveBeenCalledOnce()
    expect(p.onEscalate).toHaveBeenCalledOnce()
  })

  it('a decided card renders who, when, outcome and comment, and no actions', () => {
    render(
      <ApprovalCard
        {...props({
          decision: { by: 'Examiner Avery', at: '2026-10-14T10:05:00', outcome: 'edited', comment: 'Plainer second sentence.' },
        })}
      />,
    )
    const region = screen.getByRole('region', { name: 'Send the notice: allow benefits' })
    expect(region).toHaveAttribute('data-state', 'edited')
    expect(region.querySelector('.ui-approval__actions')).toBeNull()
    expect(within(region).queryByRole('button')).toBeNull()
    const record = region.querySelector('dl.ui-approval__record')!
    const terms = Array.from(record.querySelectorAll('dt')).map((d) => d.textContent)
    const values = Array.from(record.querySelectorAll('dd')).map((d) => d.textContent)
    expect(terms).toEqual(['Decided by', 'When', 'Outcome', 'Comment'])
    expect(values).toEqual(['Examiner Avery', '2026-10-14 10:05', 'Edited and approved', 'Plainer second sentence.'])
    expect(record.querySelector('time')).toHaveAttribute('dateTime', '2026-10-14T10:05:00')
  })

  it('has no axe violations pending, decided, and with the reject dialog open', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <div>
        <ApprovalCard {...props()} />
        <ApprovalCard {...props({ proposal: 'Second', decision: { by: 'Examiner Blake', at: '2026-10-14T11:00', outcome: 'rejected' } })} />
      </div>,
    )
    expect(await axeViolations(container)).toEqual([])
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    expect(await axeViolations(document.body)).toEqual([])
  })
})
