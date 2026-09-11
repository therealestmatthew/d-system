import { useState } from 'react'
import Popover from './Popover'

/**
 * The terminal panel's `(...)` ellipsis menu (REQ-007 W02): the sole home for Collapse/Expand
 * terminal and Drop/Restore terminal now that the standalone header collapse button and the
 * page-level drop control are both removed. Collapse and drop keep their REQ-006 R10/R11
 * semantics unchanged — collapse only ever flips `TerminalRegion`'s `collapsed` CSS-hide flag (no
 * session terminates, every `TerminalSession` stays mounted underneath), and drop still runs
 * through an explicit confirmation before `onConfirmDrop` unmounts every session. Restore carries
 * no confirmation (R10/R11 impose none on it), matching the control it replaces.
 *
 * The confirmation step renders inside this same popover bubble (a local `confirmingDrop` flag)
 * rather than a second, nested `Popover` — `Popover` already portals one bubble per trigger, and
 * document-level Escape/outside-click handling only exists once. `onOpenChange` resets that flag
 * whenever the bubble closes without the confirm action having run, so reopening the menu never
 * resurfaces a stale prompt from an earlier, abandoned drop attempt.
 */
export default function TerminalMenu({
  collapsed,
  onToggleCollapse,
  dropped,
  onRestore,
  onConfirmDrop,
}: {
  collapsed: boolean
  onToggleCollapse: () => void
  dropped: boolean
  onRestore: () => void
  onConfirmDrop: () => void
}) {
  const [confirmingDrop, setConfirmingDrop] = useState(false)

  return (
    <Popover
      triggerLabel="..."
      triggerAriaLabel="Terminal options"
      title="Terminal options"
      onOpenChange={(open) => {
        if (!open) setConfirmingDrop(false)
      }}
    >
      {(close) => (
        <div className="stage-terminal-menu">
          {confirmingDrop ? (
            <div className="stage-terminal-confirm">
              <p className="stage-placeholder-text">
                Dropping the terminal region ends every open session's shell process and
                scrollback. This cannot be undone. Use "Collapse terminal" instead to hide it
                without ending anything.
              </p>
              <div className="stage-terminal-menu__confirm-actions">
                <button
                  type="button"
                  className="stage-terminal-confirm__action"
                  onClick={() => {
                    onConfirmDrop()
                    setConfirmingDrop(false)
                    close()
                  }}
                >
                  Confirm: drop terminal and end all sessions
                </button>
                <button
                  type="button"
                  className="stage-terminal-menu__cancel"
                  onClick={() => setConfirmingDrop(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="stage-terminal-menu__list">
              <button
                type="button"
                className="stage-terminal-menu__item"
                aria-pressed={collapsed}
                onClick={() => {
                  onToggleCollapse()
                  close()
                }}
              >
                {collapsed ? 'Expand terminal' : 'Collapse terminal'}
              </button>
              {dropped ? (
                <button
                  type="button"
                  className="stage-terminal-menu__item"
                  onClick={() => {
                    onRestore()
                    close()
                  }}
                >
                  Restore terminal
                </button>
              ) : (
                <button
                  type="button"
                  className="stage-terminal-menu__item"
                  onClick={() => setConfirmingDrop(true)}
                >
                  Drop terminal
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </Popover>
  )
}
