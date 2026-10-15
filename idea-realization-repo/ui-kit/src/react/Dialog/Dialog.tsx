import type { ReactElement, ReactNode } from 'react'
import {
  Dialog as RACDialog,
  DialogTrigger,
  Heading,
  Modal,
  ModalOverlay,
} from 'react-aria-components'
import { Button } from '../Button/Button'

export type DialogVariant = 'info' | 'confirm' | 'form'

export interface DialogProps {
  /** The element that opens the dialog; must be a pressable (our Button). */
  trigger: ReactElement
  title: ReactNode
  variant?: DialogVariant
  /** Body content, or a function receiving `close`. */
  children: ReactNode | ((close: () => void) => ReactNode)
  /** Footer buttons, or a function receiving `close`. */
  footer?: ReactNode | ((close: () => void) => ReactNode)
  /** Controlled open state (optional). */
  isOpen?: boolean
  onOpenChange?: (isOpen: boolean) => void
  /** Close on a click outside (default false: a modal decision is made with the buttons or Escape). */
  isDismissable?: boolean
  /** Disable Escape, e.g. while a form holds unsaved work. */
  isKeyboardDismissDisabled?: boolean
}

/**
 * Modal dialog on React Aria `DialogTrigger` / `ModalOverlay` / `Modal` / `Dialog`. Focus is held
 * inside while open, Escape closes, and focus returns to the trigger on close.
 */
export function Dialog({
  trigger,
  title,
  variant = 'info',
  children,
  footer,
  isOpen,
  onOpenChange,
  isDismissable = false,
  isKeyboardDismissDisabled = false,
}: DialogProps) {
  return (
    <DialogTrigger isOpen={isOpen} onOpenChange={onOpenChange}>
      {trigger}
      <ModalOverlay
        className="ui-overlay"
        isDismissable={isDismissable}
        isKeyboardDismissDisabled={isKeyboardDismissDisabled}
      >
        <Modal className="ui-modal">
          <RACDialog className="ui-dialog" data-variant={variant}>
            {({ close }) => (
              <>
                <div className="ui-dialog__header">
                  <Heading slot="title" className="ui-dialog__title">
                    {title}
                  </Heading>
                </div>
                <div className="ui-dialog__body">{typeof children === 'function' ? children(close) : children}</div>
                {footer !== undefined && (
                  <div className="ui-dialog__footer">{typeof footer === 'function' ? footer(close) : footer}</div>
                )}
              </>
            )}
          </RACDialog>
        </Modal>
      </ModalOverlay>
    </DialogTrigger>
  )
}

export interface ConfirmDialogProps {
  trigger: ReactElement
  /** The object acted on, named, e.g. 'session "build-42"'. */
  object: ReactNode
  /** The verb of the destructive action, e.g. "Close" or "Delete". */
  actionLabel: string
  /** What happens, e.g. "This ends the shell and its running command." */
  consequence: ReactNode
  /** The safe choice (default "Cancel"); it takes focus when the dialog opens. */
  cancelLabel?: string
  onConfirm: () => void
  isOpen?: boolean
  onOpenChange?: (isOpen: boolean) => void
}

/**
 * Confirmation for a destructive or irreversible action (principle 7). Names the object and the
 * consequence; the danger button is rightmost and the safe button takes focus.
 */
export function ConfirmDialog({
  trigger,
  object,
  actionLabel,
  consequence,
  cancelLabel = 'Cancel',
  onConfirm,
  isOpen,
  onOpenChange,
}: ConfirmDialogProps) {
  return (
    <Dialog
      trigger={trigger}
      variant="confirm"
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      title={
        <>
          {actionLabel} {object}?
        </>
      }
      footer={(close) => (
        <>
          <Button variant="secondary" autoFocus onPress={close}>
            {cancelLabel}
          </Button>
          <Button
            variant="danger"
            onPress={() => {
              onConfirm()
              close()
            }}
          >
            {actionLabel}
          </Button>
        </>
      )}
    >
      <p>{consequence}</p>
    </Dialog>
  )
}
