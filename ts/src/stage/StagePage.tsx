import { useState } from 'react'
import './StagePage.css'
import TerminalRegion from './TerminalRegion'
import TalkingPointsRegion from './TalkingPointsRegion'
import OverviewRegion from './OverviewRegion'

/**
 * The stage page: three regions (terminal, talking points, overview) laid out to fit the
 * viewport with zero page scrolling (REQ-006 R02), plus PLAN-021's descope ladder rungs 3 and
 * 4 as independently switchable layout states — each can be applied without the other, matching
 * "each rung is independent of the ones below it".
 */
export default function StagePage() {
  // Rung 3: the overview panel becomes an open-in-tab link instead of an embed.
  const [overviewEmbedded, setOverviewEmbedded] = useState(true)
  // Rung 4: the stage drops the embedded terminal region entirely.
  const [terminalShown, setTerminalShown] = useState(true)

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
          <button
            type="button"
            aria-pressed={!terminalShown}
            onClick={() => setTerminalShown((value) => !value)}
          >
            Terminal: {terminalShown ? 'Shown' : 'Hidden (rung 4)'}
          </button>
        </div>
      </header>
      <main
        className={
          'stage-page__grid' +
          (terminalShown ? '' : ' stage-page__grid--no-terminal')
        }
      >
        {terminalShown ? <TerminalRegion /> : null}
        <TalkingPointsRegion />
        <OverviewRegion embedded={overviewEmbedded} />
      </main>
    </div>
  )
}
