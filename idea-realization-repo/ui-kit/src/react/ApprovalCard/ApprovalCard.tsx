import { useId, useState, type ReactNode } from 'react'
import { Button } from '../Button/Button'
import { ConfirmDialog, Dialog } from '../Dialog/Dialog'
import { Pill, type PillStatus } from '../Pill/Pill'

export type ApprovalRisk = 'routine' | 'consequential'
export type ApprovalOutcome = 'approved' | 'edited' | 'rejected' | 'escalated'
export type ApprovalState = 'pending' | ApprovalOutcome

/** Who decided, when, and what. */
export interface DecisionRecord {
  /** A named person, e.g. "Examiner Avery". */
  by: string
  /** ISO 8601 date-time, e.g. "2026-10-14T10:05". Shown as "2026-10-14 10:05". */
  at: string
  outcome: ApprovalOutcome
  comment?: string
}

export interface ApprovalLabels {
  approve: string
  edit: string
  reject: string
  escalate: string
}

export const DEFAULT_APPROVAL_LABELS: ApprovalLabels = {
  approve: 'Approve',
  edit: 'Edit',
  reject: 'Reject',
  escalate: 'Escalate to supervisor',
}

export const OUTCOME_LABEL: Record<ApprovalState, string> = {
  pending: 'Awaiting decision',
  approved: 'Approved',
  edited: 'Edited and approved',
  rejected: 'Rejected',
  escalated: 'Escalated to supervisor',
}

const OUTCOME_STATUS: Record<ApprovalState, PillStatus> = {
  pending: 'warn',
  approved: 'ok',
  edited: 'ok',
  rejected: 'err',
  escalated: 'warn',
}

export interface ApprovalCardProps {
  /** What the agent proposes, e.g. "Allow benefits: misconduct not established". */
  proposal: ReactNode
  /** The object acted on, named for the confirm dialog, e.g. "the notice for SYN-0142". */
  object: ReactNode
  /** Agent and model, e.g. "Claude via Amazon Bedrock · Statutory Application (Opus 5.5)". */
  agent: ReactNode
  /** Why the agent proposes it. */
  summary: ReactNode
  /** The drafted artefact or diff. */
  preview?: ReactNode
  /** Names the scrolling preview, followed by the proposal, so two cards' previews differ (default "Preview"). */
  previewLabel?: string
  /** The consequence, e.g. "Sends the notice to the claimant." */
  impact: ReactNode
  /** Whether and how the action can be undone, e.g. "It cannot be recalled once sent." */
  undo?: ReactNode
  /** routine: Approve acts at once. consequential: Approve opens a confirm dialog first. */
  risk: ApprovalRisk
  onApprove: () => void
  onEdit: () => void
  /** Called with the reason the person typed; a reason is required. */
  onReject: (reason: string) => void
  /** When given, a secondary "Escalate to supervisor" action is shown. */
  onEscalate?: () => void
  /** The decision record; absent while pending. A decided card shows it and no actions. */
  decision?: DecisionRecord
  /** The fixed statement of who decides. */
  statement?: ReactNode
  labels?: Partial<ApprovalLabels>
  /** Extra sentence in the Reject dialog, e.g. that rejecting does not escalate on its own. */
  rejectNote?: ReactNode
  headingLevel?: 2 | 3 | 4
}

function formatAt(at: string): string {
  return at.replace('T', ' ').slice(0, 16)
}

/**
 * Approval card (ARCH-001 item 32): an agent's proposed side effect that stops for a person.
 * Approve is never the default Enter action and never takes focus; for consequential impact it
 * opens a ConfirmDialog naming the object and the consequence; Reject asks for a reason.
 */
export function ApprovalCard({
  proposal,
  object,
  agent,
  summary,
  preview,
  previewLabel = 'Preview',
  impact,
  undo,
  risk,
  onApprove,
  onEdit,
  onReject,
  onEscalate,
  decision,
  statement = 'Claude recommends; the examiner decides.',
  labels: labelOverrides,
  rejectNote,
  headingLevel = 3,
}: ApprovalCardProps) {
  const labels = { ...DEFAULT_APPROVAL_LABELS, ...labelOverrides }
  const titleId = useId()
  const previewId = useId()
  const state: ApprovalState = decision?.outcome ?? 'pending'
  const Heading = `h${headingLevel}` as const

  const approve =
    risk === 'consequential' ? (
      <ConfirmDialog
        trigger={<Button variant="primary">{labels.approve}</Button>}
        object={object}
        actionLabel={labels.approve}
        consequence={
          <>
            {impact} {undo}
          </>
        }
        onConfirm={onApprove}
      />
    ) : (
      <Button variant="primary" onPress={onApprove}>
        {labels.approve}
      </Button>
    )

  return (
    <section className="ui-approval" data-state={state} data-risk={risk} aria-labelledby={titleId}>
      <div className="ui-approval__header">
        <Heading className="ui-approval__title" id={titleId}>
          {proposal}
        </Heading>
        <Pill status={OUTCOME_STATUS[state]}>{OUTCOME_LABEL[state]}</Pill>
        <p className="ui-approval__agent">Proposed by {agent}</p>
      </div>
      <p className="ui-approval__statement">{statement}</p>
      <div className="ui-approval__summary">{summary}</div>
      {preview !== undefined && (
        <div className="ui-approval__preview" tabIndex={0} role="region" aria-labelledby={`${previewId} ${titleId}`}>
          <span className="ui-visually-hidden" id={previewId}>
            {previewLabel}:
          </span>
          {preview}
        </div>
      )}
      <p className="ui-approval__impact">
        <strong>{risk === 'consequential' ? 'Consequential: ' : 'Impact: '}</strong>
        {impact}
        {undo !== undefined && <> {undo}</>}
      </p>
      {decision === undefined && (
        <div className="ui-approval__actions">
          {approve}
          <Button onPress={onEdit}>{labels.edit}</Button>
          <RejectDialog label={labels.reject} object={object} note={rejectNote} onReject={onReject} />
          {onEscalate !== undefined && (
            <Button variant="ghost" className="ui-approval__escalate" onPress={onEscalate}>
              {labels.escalate}
            </Button>
          )}
        </div>
      )}
      <DecisionRecordView decision={decision} />
    </section>
  )
}

function DecisionRecordView({ decision }: { decision: DecisionRecord | undefined }) {
  if (decision === undefined) {
    return (
      <div className="ui-approval__record">
        <span className="ui-state" data-state="not-recorded">
          <span className="ui-state__title">Decision: not recorded</span>
        </span>
      </div>
    )
  }
  return (
    <dl className="ui-approval__record" aria-label="Decision record">
      <dt>Decided by</dt>
      <dd>{decision.by}</dd>
      <dt>When</dt>
      <dd>
        <time dateTime={decision.at}>{formatAt(decision.at)}</time>
      </dd>
      <dt>Outcome</dt>
      <dd>{OUTCOME_LABEL[decision.outcome]}</dd>
      {decision.comment !== undefined && (
        <>
          <dt>Comment</dt>
          <dd>{decision.comment}</dd>
        </>
      )}
    </dl>
  )
}

function RejectDialog({
  label,
  object,
  note,
  onReject,
}: {
  label: string
  object: ReactNode
  note: ReactNode
  onReject: (reason: string) => void
}) {
  const [isOpen, setOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [showError, setShowError] = useState(false)
  const fieldId = useId()
  const errorId = useId()
  const open = (next: boolean) => {
    setOpen(next)
    if (!next) {
      setReason('')
      setShowError(false)
    }
  }
  const submit = () => {
    const trimmed = reason.trim()
    if (trimmed === '') {
      setShowError(true)
      document.getElementById(fieldId)?.focus()
      return
    }
    onReject(trimmed)
    open(false)
  }
  return (
    <Dialog
      trigger={<Button>{label}</Button>}
      title={
        <>
          {label} {object}?
        </>
      }
      variant="form"
      isOpen={isOpen}
      onOpenChange={open}
      footer={(close) => (
        <>
          <Button variant="secondary" onPress={close}>
            Cancel
          </Button>
          <Button variant="danger" onPress={submit}>
            {label}
          </Button>
        </>
      )}
    >
      <p>
        Your reason is kept in the decision record.{note !== undefined && <> {note}</>}
      </p>
      <label className="ui-approval__field" htmlFor={fieldId}>
        Reason (required)
        <textarea
          id={fieldId}
          className="ui-approval__input"
          rows={3}
          required
          autoFocus
          value={reason}
          aria-invalid={showError || undefined}
          aria-describedby={showError ? errorId : undefined}
          onChange={(e) => {
            setReason(e.target.value)
            if (showError && e.target.value.trim() !== '') setShowError(false)
          }}
        />
      </label>
      {showError && (
        <p id={errorId} className="ui-approval__error" role="alert">
          Enter a reason before rejecting.
        </p>
      )}
    </Dialog>
  )
}
