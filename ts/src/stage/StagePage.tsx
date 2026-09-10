import { useState } from 'react'
import './StagePage.css'
import TerminalRegion from './TerminalRegion'
import TalkingPointsRegion from './TalkingPointsRegion'
import OverviewRegion from './OverviewRegion'
import Popover from './Popover'

/**
 * The stage page: three regions (terminal, talking points, overview) laid out to fit the
 * viewport with zero page scrolling (REQ-006 R02), plus PLAN-021's descope ladder rungs 3 and
 * 4 as independently switchable layout states — each can be applied without the other, matching
 * "each rung is independent of the ones below it" — and, within rung 4's terminal region, a
 * separate collapse control (REQ-006 R10/R11): collapse hides the region via CSS and reflows
 * the grid but leaves every session's socket open, while the drop control (rung 4 itself) ends
 * every session and is guarded by an explicit confirm step.
 */
export default function StagePage() {
  // Rung 3: the overview panel becomes an open-in-tab link instead of an embed.
  const [overviewEmbedded, setOverviewEmbedded] = useState(true)
  // Rung 4: the stage drops the embedded terminal region entirely, terminating every session.
  // Dropping is guarded by a confirm popover below; restoring (mounting fresh sessions) is not
  // destructive and needs no confirm.
  const [terminalShown, setTerminalShown] = useState(true)
  // The terminal region's collapse state (R10/R11): CSS-hides the region and reflows the grid,
  // same as a drop, but every session stays mounted and its socket stays open. Lifted here
  // (rather than kept inside TerminalRegion) because the --no-terminal grid reflow is applied to
  // this page's grid container, not to the region itself.
  const [terminalCollapsed, setTerminalCollapsed] = useState(false)

  const terminalOccupiesGrid = terminalShown && !terminalCollapsed

  return (
    <div className="stage-page">
      <header className="stage-page__header">
        <h1>D-System Live Demo Stage</h1>
        <div className="stage-page__layout-controls">
          <button
            type="button"
            aria-pressed={!overviewEmbedded}
            onClick={() => setOverviewEmbedded((value) => !value)}
          >
            Overview: {overviewEmbedded ? 'Embedded' : 'Open-in-tab link (rung 3)'}
          </button>
          {terminalShown ? (
            <Popover triggerLabel="Terminal: Shown — drop (rung 4)" title="Drop the terminal region?">
              {(close) => (
                <div className="stage-terminal-confirm">
                  <p className="stage-placeholder-text">
                    Dropping the terminal region ends every open session's shell process and
                    scrollback. This cannot be undone. Use "Collapse terminal" in the region's
                    header instead to hide it without ending anything.
                  </p>
                  <button
                    type="button"
                    className="stage-terminal-confirm__action"
                    onClick={() => {
                      setTerminalShown(false)
                      close()
                    }}
                  >
                    Confirm: drop terminal and end all sessions
                  </button>
                </div>
              )}
            </Popover>
          ) : (
            <button type="button" aria-pressed={true} onClick={() => setTerminalShown(true)}>
              Terminal: Hidden (rung 4) — restore
            </button>
          )}
        </div>
      </header>
      <main
        className={
          'stage-page__grid' +
          (terminalOccupiesGrid ? '' : ' stage-page__grid--no-terminal')
        }
      >
        {terminalShown ? (
          <TerminalRegion
            collapsed={terminalCollapsed}
            onToggleCollapsed={() => setTerminalCollapsed((value) => !value)}
          />
        ) : null}
        <TalkingPointsRegion />
        <OverviewRegion embedded={overviewEmbedded} />
      </main>
    </div>
  )
}
