import { useId, type ReactNode } from 'react'
import {
  Button as RACButton,
  ToggleButton as RACToggleButton,
  type ButtonProps as RACButtonProps,
  type ToggleButtonProps as RACToggleButtonProps,
} from 'react-aria-components'
import { cx } from '../cx'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonBase extends Omit<RACButtonProps, 'children' | 'className' | 'style' | 'render' | 'isPending'> {
  variant?: ButtonVariant
  size?: ButtonSize
  /** Shows a spinner, sets aria-busy and blocks presses; the label stays for screen readers. */
  isLoading?: boolean
  /**
   * The reason the button is disabled, shown beside it in `.ui-reason` and linked by
   * aria-describedby (ARCH-001 principle 8). Rendered only while `isDisabled` is true.
   */
  disabledReason?: ReactNode
  /** Extra class names (block-level additions only; never state). */
  className?: string
}

/** A button with a visible text label, optionally with a leading icon. */
export interface LabelledButtonProps extends ButtonBase {
  children: ReactNode
  icon?: ReactNode
  iconOnly?: false
  /**
   * The label while `isLoading`, e.g. "Generating…". The idle and loading labels share one grid
   * cell, the inactive one invisible and aria-hidden, so the button keeps its width.
   */
  loadingLabel?: ReactNode
}

/** An icon-only button: `aria-label` is required by the type. */
export interface IconButtonProps extends ButtonBase {
  iconOnly: true
  icon: ReactNode
  'aria-label': string
  children?: never
  loadingLabel?: never
}

export type ButtonProps = LabelledButtonProps | IconButtonProps

export function buttonClassName(variant: ButtonVariant, size: ButtonSize, iconOnly: boolean, extra?: string) {
  return cx(
    'ui-button',
    `ui-button--${variant}`,
    iconOnly && 'ui-button--icon',
    size !== 'md' && `ui-button--${size}`,
    extra,
  )
}

function ButtonContent({ icon, label, isLoading }: { icon?: ReactNode; label?: ReactNode; isLoading?: boolean }) {
  return (
    <>
      {isLoading && <span className="ui-button__spinner ui-spinner" aria-hidden="true" />}
      {icon !== undefined && (
        <span className="ui-button__icon" aria-hidden="true">
          {icon}
        </span>
      )}
      {label !== undefined && <span className="ui-button__label">{label}</span>}
    </>
  )
}

/** Idle and loading labels stacked in one cell; only the active one is visible and announced. */
function LayeredContent({
  icon,
  label,
  loadingLabel,
  isLoading,
}: {
  icon?: ReactNode
  label: ReactNode
  loadingLabel: ReactNode
  isLoading: boolean
}) {
  return (
    <span className="ui-button__label">
      <span aria-hidden={isLoading || undefined}>
        {icon !== undefined && (
          <span className="ui-button__icon" aria-hidden="true">
            {icon}
          </span>
        )}
        {label}
      </span>
      <span aria-hidden={!isLoading || undefined}>
        <span className="ui-button__spinner ui-spinner" aria-hidden="true" />
        {loadingLabel}
      </span>
    </span>
  )
}

/** Button on React Aria `Button`. One `primary` per view; `danger` for destructive actions. */
export function Button(props: ButtonProps) {
  const {
    variant = 'secondary',
    size = 'md',
    isLoading = false,
    disabledReason,
    loadingLabel,
    className,
    icon,
    iconOnly,
    children,
    ...rest
  } = props
  const reasonId = useId()
  const showReason = disabledReason !== undefined && rest.isDisabled === true
  const describedBy = showReason ? [rest['aria-describedby'], reasonId].filter(Boolean).join(' ') : rest['aria-describedby']
  const button = (
    <RACButton
      {...rest}
      aria-describedby={describedBy}
      isPending={isLoading}
      className={buttonClassName(variant, size, iconOnly === true, className)}
      render={(domProps) => <button {...domProps} aria-busy={isLoading || undefined} />}
    >
      {loadingLabel !== undefined ? (
        <LayeredContent icon={icon} label={children} loadingLabel={loadingLabel} isLoading={isLoading} />
      ) : (
        <ButtonContent icon={icon} label={children} isLoading={isLoading} />
      )}
    </RACButton>
  )
  if (!showReason) return button
  return (
    <>
      {button}
      <span className="ui-reason" id={reasonId}>
        {disabledReason}
      </span>
    </>
  )
}

interface ToggleButtonBase extends Omit<RACToggleButtonProps, 'children' | 'className' | 'style' | 'render'> {
  variant?: ButtonVariant
  size?: ButtonSize
  className?: string
}

export interface LabelledToggleButtonProps extends ToggleButtonBase {
  children: ReactNode
  icon?: ReactNode
  iconOnly?: false
}

export interface IconToggleButtonProps extends ToggleButtonBase {
  iconOnly: true
  icon: ReactNode
  'aria-label': string
  children?: never
}

export type ToggleButtonProps = LabelledToggleButtonProps | IconToggleButtonProps

/** Toggle on React Aria `ToggleButton`: renders aria-pressed and data-selected. */
export function ToggleButton(props: ToggleButtonProps) {
  const { variant = 'ghost', size = 'md', className, icon, iconOnly, children, ...rest } = props
  return (
    <RACToggleButton {...rest} className={buttonClassName(variant, size, iconOnly === true, className)}>
      <ButtonContent icon={icon} label={children} />
    </RACToggleButton>
  )
}
