import { useEffect, useRef, useState } from 'react'
import Tooltip from './Tooltip'
import Popover from './Popover'

const TALKING_POINTS_URL = '/api/v1/demo/stage/talking-points'

// Auto-advance interval for the optional timed advance. Not configurable from the data file —
// the data file carries content only (REQ-006 R01), never behavior.
const AUTO_ADVANCE_INTERVAL_MS = 6000

type LoadState = 'loading' | 'loaded' | 'missing' | 'error'

interface TalkingPointsFile {
  points: string[]
}

function isTalkingPointsFile(value: unknown): value is TalkingPointsFile {
  return (
    typeof value === 'object' &&
    value !== null &&
    Array.isArray((value as { points?: unknown }).points) &&
    (value as { points: unknown[] }).points.every((point) => typeof point === 'string')
  )
}

/**
 * The talking-points panel: cycles owner-authored talking points loaded at runtime from
 * `ts/public/talking-points.json` (served by the backend's `talking-points` route,
 * `src/api/routes/demo_stage.py`, `phase-demo-01`) — never hardcoded, and re-fetched on demand
 * so editing the data file changes what the panel shows with no page-code rebuild (REQ-006 R01).
 * The real copy is authored in `phase-demo-05`; this file ships clearly-placeholder entries.
 *
 * Two independent controls:
 * - Manual next/previous, plus an optional timed auto-advance (both only meaningful in rotator
 *   mode).
 * - A rotator/static-list toggle — PLAN-021's descope rung 2 ("talking-points rotator loses
 *   transitions") as a switchable layout state: static mode renders every point as a plain list,
 *   with no current-point transition and no cycling.
 */
export default function TalkingPointsRegion() {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [points, setPoints] = useState<string[]>([])
  const [current, setCurrent] = useState(0)
  const [staticMode, setStaticMode] = useState(false)
  const [autoAdvance, setAutoAdvance] = useState(false)
  const fetchGeneration = useRef(0)

  const loadPoints = () => {
    const generation = ++fetchGeneration.current
    setLoadState('loading')
    fetch(TALKING_POINTS_URL)
      .then((response) => {
        if (generation !== fetchGeneration.current) return
        if (response.status === 404) {
          setLoadState('missing')
          return
        }
        if (!response.ok) {
          setLoadState('error')
          return
        }
        return response.json().then((body: unknown) => {
          if (generation !== fetchGeneration.current) return
          if (!isTalkingPointsFile(body) || body.points.length === 0) {
            setLoadState('error')
            return
          }
          setPoints(body.points)
          setCurrent(0)
          setLoadState('loaded')
        })
      })
      .catch(() => {
        if (generation === fetchGeneration.current) setLoadState('error')
      })
  }

  useEffect(() => {
    loadPoints()
    return () => {
      fetchGeneration.current += 1
    }
  }, [])

  // Optional timed advance: only runs in rotator mode, with more than one point, while enabled.
  useEffect(() => {
    if (staticMode || !autoAdvance || points.length < 2) return
    const timer = window.setInterval(() => {
      setCurrent((value) => (value + 1) % points.length)
    }, AUTO_ADVANCE_INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [staticMode, autoAdvance, points.length])

  return (
    <section className="stage-region stage-region--talking-points" aria-label="Talking points">
      <header className="stage-region__header">
        <h2>Talking Points</h2>
        <Tooltip label="About the talking-points panel">
          Cycles owner-authored talking points loaded from{' '}
          <code>ts/public/talking-points.json</code>. Toggle "Static list" for the
          no-transitions descope fallback (PLAN-021 rung 2).
        </Tooltip>
        <button
          type="button"
          className="stage-region__header-toggle"
          aria-pressed={staticMode}
          onClick={() => setStaticMode((value) => !value)}
        >
          {staticMode ? 'Static list (rung 2)' : 'Rotator'}
        </button>
      </header>
      <div className="stage-region__body">
        {loadState === 'loading' ? (
          <p className="stage-placeholder-text">Loading talking points…</p>
        ) : loadState === 'missing' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Talking-points data file not found. Add <code>ts/public/talking-points.json</code> (the
            copy is authored in <code>phase-demo-05</code>).
          </p>
        ) : loadState === 'error' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Could not load talking points.{' '}
            <button type="button" onClick={loadPoints}>
              Retry
            </button>
          </p>
        ) : staticMode ? (
          <ul className="stage-talking-points__list stage-talking-points__list--static">
            {points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        ) : (
          <>
            <p
              key={current}
              className="stage-placeholder-text stage-talking-points__current"
            >
              ({current + 1} of {points.length}) {points[current]}
            </p>
            <div className="stage-talking-points__controls">
              <button
                type="button"
                onClick={() =>
                  setCurrent((value) => (value - 1 + points.length) % points.length)
                }
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setCurrent((value) => (value + 1) % points.length)}
              >
                Next
              </button>
              <button
                type="button"
                aria-pressed={autoAdvance}
                onClick={() => setAutoAdvance((value) => !value)}
              >
                Auto-advance: {autoAdvance ? 'On' : 'Off'}
              </button>
            </div>
            <Popover triggerLabel={`Show all (${points.length})`} title="All talking points">
              <ul className="stage-talking-points__list">
                {points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </Popover>
          </>
        )}
      </div>
    </section>
  )
}
