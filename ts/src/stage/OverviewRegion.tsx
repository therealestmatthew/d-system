import { useEffect, useState } from 'react'
import Tooltip from './Tooltip'

const OVERVIEW_LOCATION_URL = '/api/v1/demo/stage/overview-location'
// Mirrors `ts/vite.config.ts`'s `serveGeneratedOverview` dev-server plugin, which serves
// `_public/` under this prefix — the built-in `/@fs/` route was tried first and rejected: it
// falls through to Vite's SPA fallback for a missing file (200 + `index.html`, not 404), see
// `vite.config.ts`'s comment on `serveGeneratedOverview`.
const GENERATED_OVERVIEW_PREFIX = '/generated-overview/'
const PUBLIC_DIR_PREFIX = '_public/'

type LocationState = 'loading' | 'ready' | 'outside-public-dir' | 'error'

/**
 * The overview panel: embeds the generated D-System overview page (`_public/`, produced by the
 * `d-system-overview` skill, `phase-demo-04`) in an iframe. Its location is never hardcoded —
 * fetched at runtime from the backend's `overview-location` route
 * (`src/api/routes/demo_stage.py`, `phase-demo-01`), which reports the configured path whether
 * or not the file exists yet (it is genuinely absent until `phase-demo-04` runs).
 *
 * `embedded` is `StagePage`'s layout state (`D02-C1`): PLAN-021's descope rung 3 — the embed
 * becomes an open-in-tab link — as a switchable layout state independent of the other rungs.
 */
export default function OverviewRegion({ embedded }: { embedded: boolean }) {
  const [locationState, setLocationState] = useState<LocationState>('loading')
  const [relativePath, setRelativePath] = useState<string | null>(null)
  const [rawPath, setRawPath] = useState<string | null>(null)
  const [pageExists, setPageExists] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(OVERVIEW_LOCATION_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<{ path: string }>
      })
      .then(({ path }) => {
        if (cancelled) return
        setRawPath(path)
        if (!path.startsWith(PUBLIC_DIR_PREFIX)) {
          setLocationState('outside-public-dir')
          return
        }
        setRelativePath(path.slice(PUBLIC_DIR_PREFIX.length))
        setLocationState('ready')
      })
      .catch(() => {
        if (!cancelled) setLocationState('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Once the location is known, confirm the generated file actually exists (it may not, until
  // `phase-demo-04` runs) so the panel can show a clear in-page message rather than an empty or
  // recursive iframe.
  useEffect(() => {
    if (locationState !== 'ready' || !relativePath) return
    let cancelled = false
    fetch(`${GENERATED_OVERVIEW_PREFIX}${relativePath}`, { method: 'HEAD' })
      .then((response) => {
        if (!cancelled) setPageExists(response.ok)
      })
      .catch(() => {
        if (!cancelled) setPageExists(false)
      })
    return () => {
      cancelled = true
    }
  }, [locationState, relativePath])

  const embedSrc = relativePath ? `${GENERATED_OVERVIEW_PREFIX}${relativePath}` : null

  return (
    <section className="stage-region stage-region--overview" aria-label="Overview">
      <header className="stage-region__header">
        <h2>Overview</h2>
        <Tooltip label="About the overview panel">
          Embeds the generated D-System overview page from <code>_public/</code> (produced by
          the <code>d-system-overview</code> skill, <code>phase-demo-04</code>). Switch to the
          "open in tab" layout state to see the rung-3 descope fallback.
        </Tooltip>
      </header>
      <div
        className={
          'stage-region__body' +
          (embedded && locationState === 'ready' && pageExists
            ? ' stage-region__body--overview'
            : '')
        }
      >
        {locationState === 'loading' ? (
          <p className="stage-placeholder-text">Locating the generated overview page…</p>
        ) : locationState === 'error' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Could not reach the backend to locate the overview page.
          </p>
        ) : locationState === 'outside-public-dir' ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Configured overview page path (<code>{rawPath}</code>) is outside <code>_public/</code>
            and cannot be previewed by the dev server.
          </p>
        ) : pageExists === false ? (
          <p className="stage-placeholder-text stage-placeholder-text--absent">
            Overview page is absent — <code>{rawPath}</code> does not exist yet. It is generated
            by the <code>d-system-overview</code> skill (<code>phase-demo-04</code>).
          </p>
        ) : pageExists === null ? (
          <p className="stage-placeholder-text">Checking the generated overview page…</p>
        ) : embedded ? (
          <iframe
            className="stage-overview__iframe"
            src={embedSrc ?? undefined}
            title="D-System overview"
          />
        ) : (
          <a
            className="stage-overview__open-link"
            href={embedSrc ?? undefined}
            target="_blank"
            rel="noreferrer"
          >
            Open overview in a new tab ↗
          </a>
        )}
      </div>
    </section>
  )
}
