import { useSyncExternalStore } from 'react'

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
 */
class BridgeSlot<T> {
  private current: T | null = null
  private readonly listeners = new Set<() => void>()

  /** Called by the owning panel whenever its live handle changes (mount, or any state change the
   * handle closes over) — replaces whatever was registered before, since only one instance is
   * ever expected. */
  register(handle: T): void {
    this.current = handle
    this.emit()
  }

  /** Called from the same effect's cleanup. Guarded by identity so a superseded registration's
   * belated cleanup (an old handle's effect cleanup running after a newer handle already
   * registered — see `TerminalRegion`'s own dependency-triggered re-registration) never clears a
   * registration it did not create. */
  unregister(handle: T): void {
    if (this.current === handle) {
      this.current = null
      this.emit()
    }
  }

  get(): T | null {
    return this.current
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private emit(): void {
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
}

export const terminalBridge = new BridgeSlot<TerminalBridgeHandle>()
export const viewerBridge = new BridgeSlot<ViewerBridgeHandle>()

/** `null` whenever no terminal-type panel is currently mounted anywhere in the active layout (or
 * before the first one has registered) — the File Browser's menu treats that exactly like
 * "absent", disabling "Inject path into terminal" the same way `InjectionDropdowns` disables its
 * own trigger when the terminal capability itself is absent. */
export function useTerminalBridge(): TerminalBridgeHandle | null {
  return useSyncExternalStore(terminalBridge.subscribe, () => terminalBridge.get())
}

/** `null` whenever no HTML Viewer panel is currently mounted (e.g. layout 2's main slot resolved
 * to `overview` instead) — the File Browser's menu hides/disables "Open in HTML Viewer"'s
 * submenu in that case rather than offering tabs that do not exist anywhere on screen. */
export function useViewerBridge(): ViewerBridgeHandle | null {
  return useSyncExternalStore(viewerBridge.subscribe, () => viewerBridge.get())
}
