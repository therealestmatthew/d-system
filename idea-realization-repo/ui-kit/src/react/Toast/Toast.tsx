// The kit's Toast API. React Aria's toast components are exported as UNSTABLE_* in
// react-aria-components 1.22; they are imported in this one file only, so a change to them stays local.
import { createContext, useContext, useEffect, useMemo, useRef, type ReactNode } from 'react'
import {
  Button as RACButton,
  Text,
  UNSTABLE_Toast as RACToast,
  UNSTABLE_ToastContent as RACToastContent,
  UNSTABLE_ToastQueue as RACToastQueue,
  UNSTABLE_ToastRegion as RACToastRegion,
} from 'react-aria-components'
import { Button } from '../Button/Button'

export type ToastStatus = 'ok' | 'info' | 'err'

export interface ToastAction {
  label: string
  onAction: () => void
}

export interface ToastContent {
  status: ToastStatus
  title: string
  body?: string
  /** Required in spirit for `err` (Retry, View); allowed for any status. */
  action?: ToastAction
}

/** How long ok/info toasts stay, in ms. err toasts persist until dismissed. */
export const TOAST_TIMEOUT_MS = 5000
/** At most three toasts visible at once (ARCH-001 component 21). */
export const MAX_VISIBLE_TOASTS = 3

export interface ToastQueue {
  /** Show a toast; returns its key. */
  show(content: ToastContent): string
  close(key: string): void
  clear(): void
  /** @internal the React Aria queue behind this one. */
  readonly inner: RACToastQueue<ToastContent>
}

export function createToastQueue(): ToastQueue {
  const inner = new RACToastQueue<ToastContent>({ maxVisibleToasts: MAX_VISIBLE_TOASTS })
  return {
    inner,
    show(content) {
      return inner.add(content, content.status === 'err' ? {} : { timeout: TOAST_TIMEOUT_MS })
    },
    close(key) {
      inner.close(key)
    },
    clear() {
      inner.clear()
    },
  }
}

/** The app-wide queue used when no ToastProvider supplies another. */
export const defaultToastQueue: ToastQueue = createToastQueue()

const ToastQueueContext = createContext<ToastQueue | null>(null)

/** The queue to show toasts on: the nearest ToastProvider's, or the default queue. */
export function useToast(): ToastQueue {
  return useContext(ToastQueueContext) ?? defaultToastQueue
}

export interface ToastRegionProps {
  queue?: ToastQueue
  /** Accessible name of the region (default "Notifications"). */
  label?: string
}

/**
 * Renders the visible toasts as a bottom-right stack. Auto-dismiss pauses while the region is
 * hovered or focused (React Aria). The region never takes focus by itself; F8 moves focus into it.
 */
export function ToastRegion({ queue, label = 'Notifications' }: ToastRegionProps) {
  const contextQueue = useContext(ToastQueueContext)
  const active = queue ?? contextQueue ?? defaultToastQueue
  const regionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'F8' || !regionRef.current) return
      const first = regionRef.current.querySelector<HTMLElement>('[role="alertdialog"], button')
      if (first) {
        first.focus()
        event.preventDefault()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  return (
    <RACToastRegion ref={regionRef} queue={active.inner} className="ui-toast-region" aria-label={label}>
      {({ toast }) => (
        <RACToast toast={toast} className="ui-toast" data-status={toast.content.status}>
          <RACToastContent className="ui-toast__content">
            <Text slot="title" className="ui-toast__title">
              {toast.content.title}
            </Text>
            {toast.content.body !== undefined && (
              <Text slot="description" className="ui-toast__body">
                {toast.content.body}
              </Text>
            )}
          </RACToastContent>
          {toast.content.action !== undefined && (
            <div className="ui-toast__actions">
              <Button
                size="sm"
                variant="secondary"
                onPress={() => {
                  toast.content.action?.onAction()
                  active.close(toast.key)
                }}
              >
                {toast.content.action.label}
              </Button>
            </div>
          )}
          <RACButton slot="close" className="ui-toast__close ui-button ui-button--ghost ui-button--icon ui-button--sm" aria-label="Dismiss">
            <span aria-hidden="true">×</span>
          </RACButton>
        </RACToast>
      )}
    </RACToastRegion>
  )
}

export interface ToastProviderProps {
  /** A queue to use instead of a fresh one (tests, or sharing with non-React code). */
  queue?: ToastQueue
  children: ReactNode
}

/** Supplies a queue to `useToast()` below it and renders its ToastRegion. */
export function ToastProvider({ queue, children }: ToastProviderProps) {
  const value = useMemo(() => queue ?? createToastQueue(), [queue])
  return (
    <ToastQueueContext.Provider value={value}>
      {children}
      <ToastRegion queue={value} />
    </ToastQueueContext.Provider>
  )
}
