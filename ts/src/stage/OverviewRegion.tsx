import Tooltip from './Tooltip'

const PLACEHOLDER_OVERVIEW_HREF = '/api/v1/demo/stage/overview-location'

/**
 * Placeholder for the generated D-System overview panel. The real embed (an iframe over the
 * page `phase-demo-04` generates under `_public/`) is a separate work item; this component
 * carries the layout slot and the rung-3 descope fallback from PLAN-021's descope ladder: an
 * open-in-tab link in place of the embed.
 */
export default function OverviewRegion({ embedded }: { embedded: boolean }) {
  return (
    <section className="stage-region stage-region--overview" aria-label="Overview">
      <header className="stage-region__header">
        <h2>Overview</h2>
        <Tooltip label="About the overview panel">
          Will embed the generated D-System overview page (a later work item). Switch to the
          "open in tab" layout state to see the rung-3 descope fallback.
        </Tooltip>
      </header>
      <div className="stage-region__body">
        {embedded ? (
          <p className="stage-placeholder-text">
            Overview embed placeholder — the generated overview page will render here.
          </p>
        ) : (
          <a
            className="stage-overview__open-link"
            href={PLACEHOLDER_OVERVIEW_HREF}
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
