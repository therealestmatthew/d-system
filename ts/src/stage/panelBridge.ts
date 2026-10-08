import { useCallback, useSyncExternalStore } from 'react'

/**
 * Cross-panel reach for the File Browser's right-click context menu (REQ-007 W09, items 2 and
 * 5): "open in HTML Viewer" and "inject path into terminal" both act on a *different* panel than
 * the one the click happened in. The workbench layout engine (`ts/src/workbench/Slot.tsx`,
 * ADR-016) mounts every panel independently — a slot's panel has no reference to any sibling
 * slot's panel, by design (a panel only ever changes what renders inside its own fixed slot box).
 * That independence is right for layout, but the File Browser's menu genuinely needs to reach the
 * live HTML Viewer / Terminal instance, not just persisted-to-storage state (REQ-007 W08's ADR-
 * 016 persistence is snapshotted on write, not live, and would race an in-flight tab open).
 *
 * `BridgeSlot<T>` is the smallest thing that closes that gap without lifting state into a shared
 * parent: a module-level singleton (one page, one app instance, no SSR — a plain module variable
 * is exactly the ref-based prop-drilling style this repo already uses for the terminal's own
 * imperative handle, `TerminalRegion.tsx`'s `sessionHandlesRef`, generalized to reach across
 * slots instead of down through props). Whichever panel is currently mounted registers its live
 * handle on mount and unregisters on unmount; `Slot.tsx` guarantees at most one instance of a
 * given panel type renders at a time, so "the current registration" is unambiguous. A menu action
 * with nothing registered (no HTML Viewer panel in the active layout right now, or the terminal
 * panel absent/dropped) reads `null` and disables or messages accordingly — never throws, never
 * queues.
 *
 * ADR-029 section 6 widens this without changing it for single-handle callers. A channel may hold
 * several handles keyed by panel-instance key (the key defaults to the channel id, so a caller that
 * passes none behaves as before), and `deliverBatch` is the one entry point that hands an ordered
 * list of paths to one or more targets and returns a receipt of what each accepted or declined.
 * Opening a set of files by calling `openInTab` once per file from other code is a second
 * file-passing path and a defect (REQ-012 R07); route it through `deliverBatch`.
 */
class BridgeSlot<T> {
  /** Live registrations in registration order; the last entry is the "current" one. At most one
   * entry per key. */
  private entries: Array<{ key: string; handle: T }> = []
  /** Referentially stable snapshot for `useSyncExternalStore`: replaced only on register and
   * unregister, never rebuilt on read. */
  private snapshot: T[] = []
  private readonly listeners = new Set<() => void>()

  /** `id` names the channel in a batch outcome and is the default registration key: panels are
   * singletons today, so one key per panel type id reproduces the old single-handle behavior. */
  constructor(readonly id: string) {}

  /** Called by the owning panel whenever its live handle changes (mount, or any state change the
   * handle closes over). A handle registered under a key already in use replaces that entry and
   * becomes the most recent one; entries under other keys are left alone. `key` defaults to the
   * channel id, so callers that pass no key keep the single-handle behavior. */
  register(handle: T, key: string = this.id): void {
    this.entries = [...this.entries.filter((entry) => entry.key !== key), { key, handle }]
    this.publish()
  }

  /** Called from the same effect's cleanup. Finds the entry by handle identity across all keys and
   * removes it only if that exact handle is still registered, so a superseded registration's
   * belated cleanup (an old handle's effect cleanup running after a newer handle already
   * registered — see `TerminalRegion`'s own dependency-triggered re-registration) never clears a
   * registration it did not create. */
  unregister(handle: T): void {
    if (!this.entries.some((entry) => entry.handle === handle)) return
    this.entries = this.entries.filter((entry) => entry.handle !== handle)
    this.publish()
  }

  /** The most recently registered remaining handle; when it unregisters, the previous remaining
   * one. `null` when nothing is registered. */
  get(): T | null {
    return this.entries.length > 0 ? this.entries[this.entries.length - 1].handle : null
  }

  /** Every live handle, oldest registration first. The same array instance is returned until the
   * next register or unregister. */
  getAll(): T[] {
    return this.snapshot
  }

  /** The registration a batch target addresses: the one under `key`, or the current one when no
   * key is given. `null` when there is none. Internal to `deliverBatch`. */
  resolve(key?: string): { key: string; handle: T } | null {
    if (key === undefined) {
      return this.entries.length > 0 ? this.entries[this.entries.length - 1] : null
    }
    return this.entries.find((entry) => entry.key === key) ?? null
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private publish(): void {
    this.snapshot = this.entries.map((entry) => entry.handle)
    this.listeners.forEach((listener) => listener())
  }
}

/** What `TerminalRegion` publishes about whichever terminal-type panel (bash/CMD/PowerShell — one
 * component, REQ-007 W12) is currently mounted. `enabled`/`dropped` mirror the same two flags the
 * in-panel injection dropdowns (`InjectionDropdowns`, `CommandPanel`) already key their own
 * disabled/deactivated state on, so the context menu's "Inject path into terminal" item disables
 * under exactly the same conditions those dropdowns do (this dispatch's own instruction). */
export interface TerminalBridgeHandle {
  enabled: boolean
  dropped: boolean
  /** Sends `relativePath` to the active session's input line un-executed — the same
   * `sendCommand(text, appendNewline: false)` path `InjectionDropdowns`' `onSelect` already uses
   * (R12 injection mechanics), reused rather than re-implemented here. */
  injectPath: (relativePath: string) => void
}

export interface ViewerBridgeTab {
  id: number
  label: string
}

/** What `HtmlViewerRegion` publishes about its currently open tabs (REQ-007 W08). `tabs` is
 * whatever the panel currently has open, in order, so the context menu's submenu always lists
 * live tabs — including one just opened via "+ New tab" a moment ago — never a stale snapshot. */
export interface ViewerBridgeHandle {
  tabs: ViewerBridgeTab[]
  /** Sets `tabId`'s displayed page to `relativePath` and makes it the active tab, so the opened
   * file is immediately visible rather than opened silently in a background tab. */
  openInTab: (tabId: number, relativePath: string) => void
  /** Opens the whole ordered list and reports, for every path, whether it was delivered or
   * declined and why (`BatchReceipt`). Optional so a handle without batch support still
   * type-checks; `callOpenFiles` treats a handle that lacks it as having failed every path.
   * Implemented by `HtmlViewerRegion` (`phase-wbf-05`). */
  openFiles?: (paths: string[]) => BatchReceipt
}

export const terminalBridge = new BridgeSlot<TerminalBridgeHandle>('terminal')
export const viewerBridge = new BridgeSlot<ViewerBridgeHandle>('html-viewer')

/** `null` whenever no terminal-type panel is currently mounted anywhere in the active layout (or
 * before the first one has registered) — the File Browser's menu treats that exactly like
 * "absent", disabling "Inject path into terminal" the same way `InjectionDropdowns` disables its
 * own trigger when the terminal capability itself is absent. */
export function useTerminalBridge(): TerminalBridgeHandle | null {
  return useSyncExternalStore(terminalBridge.subscribe, () => terminalBridge.get())
}

/** `null` whenever no HTML Viewer panel is currently mounted (e.g. layout 2's primary slot resolved
 * to `overview` instead) — the File Browser's menu hides/disables "Open in HTML Viewer"'s
 * submenu in that case rather than offering tabs that do not exist anywhere on screen. */
export function useViewerBridge(): ViewerBridgeHandle | null {
  return useSyncExternalStore(viewerBridge.subscribe, () => viewerBridge.get())
}

/** Every live terminal handle, or `null` when none is registered. The array is stable between
 * register and unregister calls, as `useSyncExternalStore` requires. */
export function useTerminalBridges(): TerminalBridgeHandle[] | null {
  const all = useSyncExternalStore(terminalBridge.subscribe, () => terminalBridge.getAll())
  return all.length > 0 ? all : null
}

/** Every live HTML Viewer handle, or `null` when none is registered. */
export function useViewerBridges(): ViewerBridgeHandle[] | null {
  const all = useSyncExternalStore(viewerBridge.subscribe, () => viewerBridge.getAll())
  return all.length > 0 ? all : null
}

// ---------------------------------------------------------------------------------------------
// Batch delivery (ADR-029 section 6, REQ-012 R07 and R08)
// ---------------------------------------------------------------------------------------------

export type DeclineReason = 'incompatible' | 'capacity' | 'failed'

/** What a target reports for one batch. Every requested path is in exactly one list. */
export interface BatchReceipt {
  delivered: string[]
  declined: Array<{ path: string; reason: DeclineReason }>
}

/** Invokes a handle's batch method. Returns `undefined` when the handle has no such method. */
export type BatchCall<H> = (handle: H, paths: string[]) => BatchReceipt | undefined

/** One place to deliver a batch. An omitted `key` addresses the channel's current handle. */
export interface BatchTarget<H> {
  channel: BridgeSlot<H>
  call: BatchCall<H>
  key?: string
}

export interface BatchTargetOutcome {
  channel: string
  key: string
  /** No handle was registered for this target; nothing was delivered to it. */
  absent: boolean
  receipt?: BatchReceipt
  /** The message of what the target's method threw; its paths are then all declined `failed`. */
  error?: string
}

export interface BatchOutcome {
  requested: string[]
  targets: BatchTargetOutcome[]
}

/** The viewer's batch method as a `BatchCall`. */
export const callOpenFiles: BatchCall<ViewerBridgeHandle> = (handle, paths) =>
  handle.openFiles?.(paths)

function declineAll(paths: string[], reason: DeclineReason): BatchReceipt {
  return { delivered: [], declined: paths.map((path) => ({ path, reason })) }
}

/** Forces a target's reply into the invariant: each requested path in exactly one list, in request
 * order, nothing else. A path the target omitted, listed twice, or listed as both delivered and
 * declined is declined `failed`, because the bridge cannot tell what happened to it. */
function normalizeReceipt(paths: string[], raw: unknown): BatchReceipt {
  const receipt = raw as Partial<BatchReceipt> | null | undefined
  if (!receipt || !Array.isArray(receipt.delivered) || !Array.isArray(receipt.declined)) {
    return declineAll(paths, 'failed')
  }
  const delivered = new Map<string, number>()
  for (const path of receipt.delivered) delivered.set(path, (delivered.get(path) ?? 0) + 1)
  const declined = new Map<string, { reason: DeclineReason; count: number }>()
  for (const item of receipt.declined) {
    const reason: DeclineReason =
      item?.reason === 'incompatible' || item?.reason === 'capacity' ? item.reason : 'failed'
    const seen = declined.get(item?.path)
    declined.set(item?.path, { reason: seen?.reason ?? reason, count: (seen?.count ?? 0) + 1 })
  }
  const result: BatchReceipt = { delivered: [], declined: [] }
  for (const path of paths) {
    const deliveredCount = delivered.get(path) ?? 0
    const declinedEntry = declined.get(path)
    if (deliveredCount === 1 && !declinedEntry) result.delivered.push(path)
    else if (deliveredCount === 0 && declinedEntry?.count === 1) {
      result.declined.push({ path, reason: declinedEntry.reason })
    } else result.declined.push({ path, reason: 'failed' })
  }
  return result
}

/** The message for a thrown value. Never throws itself: a value with no usable string form (a null
 * prototype object, or a `toString` that throws) gets a fixed message. */
function describeThrown(error: unknown): string {
  try {
    return error instanceof Error ? error.message : String(error)
  } catch {
    return 'target threw a non-printable value'
  }
}

/** The one entry point that delivers an ordered list of paths to one or more targets. Each listed
 * target receives the full list; the caller chooses the fan-out, and the bridge never adds
 * targets. Returns an outcome value synchronously: it never throws and never queues. A target with
 * no registered handle is reported `absent` and the rest still receive the list (best effort per
 * target). A target whose method throws is recorded in `error` with all its paths declined
 * `failed`. The bridge does no I/O and no path validation; callers pass resolved paths. A path
 * repeated in `paths` is collapsed to its first occurrence: `requested`, every target's call and
 * every receipt are over the same distinct, ordered paths. */
export function deliverBatch<Hs extends unknown[]>(
  paths: string[],
  targets: { [I in keyof Hs]: BatchTarget<Hs[I]> },
): BatchOutcome {
  const distinct = [...new Set(paths)]
  const requested = [...distinct]
  const outcomes: BatchTargetOutcome[] = []
  for (const target of targets as Array<BatchTarget<unknown>>) {
    const channel = target.channel.id
    const entry = target.channel.resolve(target.key)
    if (!entry) {
      outcomes.push({ channel, key: target.key ?? channel, absent: true })
      continue
    }
    try {
      const raw = target.call(entry.handle, [...distinct])
      outcomes.push({
        channel,
        key: entry.key,
        absent: false,
        receipt: raw === undefined ? declineAll(distinct, 'failed') : normalizeReceipt(distinct, raw),
        ...(raw === undefined ? { error: 'target has no batch method' } : {}),
      })
    } catch (error) {
      outcomes.push({
        channel,
        key: entry.key,
        absent: false,
        receipt: declineAll(distinct, 'failed'),
        error: describeThrown(error),
      })
    }
  }
  return { requested, targets: outcomes }
}

/** Whether a batch action should be enabled: at least one listed target has a registered handle
 * (ADR-029 section 6 point 6). A point-in-time read with no subscription: use it in event handlers
 * and tests, and use `useBatchAvailable` where a rendered control must follow registrations. */
export function isBatchAvailable<Hs extends unknown[]>(targets: {
  [I in keyof Hs]: BatchTarget<Hs[I]>
}): boolean {
  return (targets as Array<BatchTarget<unknown>>).some(
    (target) => target.channel.resolve(target.key) !== null,
  )
}

/** Reactive form of `isBatchAvailable`: re-renders when any listed channel registers or
 * unregisters a handle, so a batch action disables when no listed target is on screen and enables
 * when one mounts (REQ-012 R08). Subscribes to every listed channel. */
export function useBatchAvailable<Hs extends unknown[]>(targets: {
  [I in keyof Hs]: BatchTarget<Hs[I]>
}): boolean {
  const list = targets as Array<BatchTarget<unknown>>
  // The caller usually builds `targets` inline, so resubscribe only when the set of channels
  // changes, not on every render. The snapshot is a boolean, which is stable by value.
  const channels = [...new Set(list.map((target) => target.channel))]
  const channelsKey = channels.map((channel) => channel.id).join('|')
  const subscribe = useCallback(
    (listener: () => void) => {
      const unsubscribers = channels.map((channel) => channel.subscribe(listener))
      return () => unsubscribers.forEach((unsubscribe) => unsubscribe())
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [channelsKey],
  )
  return useSyncExternalStore(subscribe, () => isBatchAvailable(targets))
}
