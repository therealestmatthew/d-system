import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from 'react'
import { createPortal } from 'react-dom'
import type { ViewerBridgeTab } from './panelBridge'

// Kept clear of the viewport edge when clamping the menu's position — same margin `Popover.tsx`
// uses for its own bubble, applied here to a cursor point instead of a trigger rect.
const VIEWPORT_MARGIN = 8

/**
 * The File Browser tree's right-click context menu (REQ-007 W09): five actions for whichever
 * entry was right-clicked, portaled to `document.body` (same reasoning as `Popover.tsx` — the
 * tree container is `overflow-y: auto` inside a `.stage-region__body` that clips anything
 * positioned inline) and positioned at the click point, clamped to the viewport once its own
 * measured size is known.
 *
 * Dismisses on Escape or a click outside the menu (REQ-006 R03's click-popup contract, applied
 * here since a context menu is itself a click-triggered popup even though nothing renders a
 * visible trigger button for it — the right-click *is* the trigger). Every leaf action closes the
 * menu immediately after running (`runAndClose`) — a context menu offering one action at a time,
 * not a panel that stays open across several.
 *
 * "Open in HTML Viewer" is the one item with a nested submenu (choosing the target tab): rendered
 * as an inline expand rather than a hover flyout, since a flyout positioned relative to a menu
 * item that is itself already viewport-clamped would need its own independent clamping pass for
 * comparatively little benefit here — REQ-007 W09 asks for "a nested submenu choosing the target
 * viewer tab", which an expand-in-place `role="menu"` nested under the parent `role="menuitem"`
 * satisfies structurally without that second clamping pass.
 *
 * Every item inapplicable to the right-clicked entry is hidden (not shown-disabled) —
 * `viewerCompatible=false` (a non-`.html`/`.svg` file, or a directory) drops the whole "Open in
 * HTML Viewer" item, matching this dispatch's own example ("open-in-viewer on a .py file"). The
 * two availability flags (`viewerAvailable`, `terminalAvailable`) instead *disable* their item
 * with a real `disabled` attribute — the target panel could still be applicable in principle
 * (compatible file, real path to inject), it is simply not reachable right now, exactly like
 * `InjectionDropdowns`' own disabled/deactivated split for the terminal being absent or dropped.
 */
export default function FileTreeContextMenu({
  x,
  y,
  entryName,
  viewerCompatible,
  viewerAvailable,
  viewerTabs,
  terminalAvailable,
  onReveal,
  onOpenInViewer,
  onCopyRelativePath,
  onCopyAbsolutePath,
  onInjectPath,
  onClose,
}: {
  x: number
  y: number
  entryName: string
  /** Whether the right-clicked entry is a compatible file for the HTML Viewer (REQ-007 W07:
   * `.html`/`.svg`, never true for a directory) — governs whether "Open in HTML Viewer" appears
   * at all. */
  viewerCompatible: boolean
  /** Whether an HTML Viewer panel is currently mounted anywhere in the active layout
   * (`useViewerBridge() !== null`) — governs whether the (shown) item is enabled. */
  viewerAvailable: boolean
  viewerTabs: ViewerBridgeTab[]
  /** Whether a terminal-type panel is mounted, enabled and not dropped
   * (`useTerminalBridge()`) — governs "Inject path into terminal"'s `disabled` attribute, exactly
   * like the injection dropdowns' own `disabled`/`deactivated` split collapsed to one flag here. */
  terminalAvailable: boolean
  onReveal: () => void
  onOpenInViewer: (tabId: number) => void
  onCopyRelativePath: () => void
  onCopyAbsolutePath: () => void
  onInjectPath: () => void
  onClose: () => void
}) {
  const menuRef = useRef<HTMLDivElement>(null)
  const [style, setStyle] = useState<CSSProperties>({ left: x, top: y })
  const [viewerSubmenuOpen, setViewerSubmenuOpen] = useState(false)

  // Clamp against the viewport once the menu's real size is known — re-run whenever the submenu
  // opens/closes too, since expanding it changes the menu's own height and could push its bottom
  // edge past the viewport where the collapsed menu fit fine.
  useLayoutEffect(() => {
    const menu = menuRef.current
    if (!menu) return
    const rect = menu.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    let left = x
    let top = y
    if (left + rect.width > viewportWidth - VIEWPORT_MARGIN) {
      left = viewportWidth - VIEWPORT_MARGIN - rect.width
    }
    if (top + rect.height > viewportHeight - VIEWPORT_MARGIN) {
      top = viewportHeight - VIEWPORT_MARGIN - rect.height
    }
    left = Math.max(VIEWPORT_MARGIN, left)
    top = Math.max(VIEWPORT_MARGIN, top)
    setStyle({ left, top })
  }, [x, y, viewerSubmenuOpen])

  useEffect(() => {
    function handlePointerDown(event: MouseEvent): void {
      if (menuRef.current?.contains(event.target as Node)) return
      onClose()
    }
    function handleKeyDown(event: KeyboardEvent): void {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [onClose])

  function runAndClose(action: () => void): void {
    action()
    onClose()
  }

  return createPortal(
    <div
      role="menu"
      aria-label={`Actions for ${entryName}`}
      ref={menuRef}
      className="stage-file-tree-menu"
      style={style}
    >
      <div className="stage-file-tree-menu__title">{entryName}</div>

      <button
        type="button"
        role="menuitem"
        className="stage-file-tree-menu__item"
        onClick={() => runAndClose(onReveal)}
      >
        Reveal in file explorer
      </button>

      {viewerCompatible ? (
        <div className="stage-file-tree-menu__submenu-wrap">
          <button
            type="button"
            role="menuitem"
            aria-haspopup="menu"
            aria-expanded={viewerSubmenuOpen}
            className="stage-file-tree-menu__item stage-file-tree-menu__item--parent"
            disabled={!viewerAvailable}
            onClick={() => setViewerSubmenuOpen((value) => !value)}
          >
            Open in HTML Viewer {viewerAvailable ? '▸' : '(viewer not open)'}
          </button>
          {viewerSubmenuOpen && viewerAvailable ? (
            <div role="menu" aria-label="Choose the target HTML Viewer tab" className="stage-file-tree-menu__submenu">
              {viewerTabs.length === 0 ? (
                <p className="stage-file-tree-menu__empty">No HTML Viewer tabs open.</p>
              ) : (
                viewerTabs.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    role="menuitem"
                    className="stage-file-tree-menu__item"
                    onClick={() => runAndClose(() => onOpenInViewer(tab.id))}
                  >
                    {tab.label}
                  </button>
                ))
              )}
            </div>
          ) : null}
        </div>
      ) : null}

      <button
        type="button"
        role="menuitem"
        className="stage-file-tree-menu__item"
        onClick={() => runAndClose(onCopyRelativePath)}
      >
        Copy relative path
      </button>

      <button
        type="button"
        role="menuitem"
        className="stage-file-tree-menu__item"
        onClick={() => runAndClose(onCopyAbsolutePath)}
      >
        Copy absolute path
      </button>

      <button
        type="button"
        role="menuitem"
        className="stage-file-tree-menu__item"
        disabled={!terminalAvailable}
        onClick={() => runAndClose(onInjectPath)}
      >
        Inject path into terminal
      </button>
    </div>,
    document.body,
  )
}
