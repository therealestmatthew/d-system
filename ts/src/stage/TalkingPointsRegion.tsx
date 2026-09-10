import { useState } from 'react'
import Tooltip from './Tooltip'
import Popover from './Popover'

// Layout placeholders only — not the owner-authored copy. The rotator's real content loads
// from a data file in a separate work item; these strings exist purely to exercise the panel's
// sizing and in-place overflow reveal.
const PLACEHOLDER_POINTS = [
  'Placeholder talking point 1',
  'Placeholder talking point 2',
  'Placeholder talking point 3',
  'Placeholder talking point 4',
  'Placeholder talking point 5',
  'Placeholder talking point 6',
]

const VISIBLE_COUNT = 3

/**
 * Placeholder for the talking-points panel. The rotator behavior (cycling, transitions, and
 * loading owner-authored copy from a data file) is a separate work item; this component only
 * carries the layout slot and the in-place overflow reveal REQ-006 R02 requires: points beyond
 * what the panel's fixed slot can show are reached through a dismissible popup rather than a
 * page-level scrollbar.
 */
export default function TalkingPointsRegion() {
  const [current, setCurrent] = useState(0)
  const visible = PLACEHOLDER_POINTS.slice(0, VISIBLE_COUNT)
  const overflowCount = PLACEHOLDER_POINTS.length - VISIBLE_COUNT

  return (
    <section className="stage-region stage-region--talking-points" aria-label="Talking points">
      <header className="stage-region__header">
        <h2>Talking Points</h2>
        <Tooltip label="About the talking-points panel">
          Cycles owner-authored talking points loaded from a data file (a later work item). This
          is a layout placeholder with stand-in text.
        </Tooltip>
      </header>
      <div className="stage-region__body">
        <p className="stage-placeholder-text">
          Current point ({current + 1} of {PLACEHOLDER_POINTS.length}):{' '}
          {PLACEHOLDER_POINTS[current]}
        </p>
        <div className="stage-talking-points__controls">
          <button
            type="button"
            onClick={() => setCurrent((value) => (value + 1) % PLACEHOLDER_POINTS.length)}
          >
            Next point (placeholder)
          </button>
        </div>
        <ul className="stage-talking-points__list">
          {visible.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
        {overflowCount > 0 ? (
          <Popover triggerLabel={`Show all (${PLACEHOLDER_POINTS.length})`} title="All talking points">
            <ul className="stage-talking-points__list">
              {PLACEHOLDER_POINTS.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </Popover>
        ) : null}
      </div>
    </section>
  )
}
