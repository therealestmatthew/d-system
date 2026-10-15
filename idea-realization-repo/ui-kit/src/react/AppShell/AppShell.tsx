import { useCallback, useId, useRef, type KeyboardEvent, type ReactNode } from 'react'

/** The standard shell regions (ARCH-001 "Layout grid"). */
export type RegionName = 'header' | 'nav' | 'main' | 'inspector' | 'dock' | 'strip'

/** One layout file from `ui-kit/layouts/<id>.json` (shape in the class contract). */
export interface ShellLayout {
  id: string
  label: string
  regions: readonly string[]
  grid: { columns: readonly string[]; rows: readonly string[]; areas: readonly string[] }
}

export interface AppShellProps {
  /** The layout object, imported from `layouts/*.json`. Selects the grid through `data-layout`. */
  layout: ShellLayout
  /** Content per region. Only regions the layout names are rendered. */
  regions: Partial<Record<RegionName, ReactNode>>
  /** Accessible names for the landmarks; defaults are the region's plain name. */
  regionLabels?: Partial<Record<RegionName, string>>
  /** Text of the skip link. */
  skipLinkLabel?: string
}

const KNOWN_REGIONS: readonly RegionName[] = ['header', 'nav', 'main', 'inspector', 'dock', 'strip']

const DEFAULT_LABELS: Record<RegionName, string> = {
  header: 'Application',
  nav: 'Navigation',
  main: 'Main',
  inspector: 'Inspector',
  dock: 'Dock',
  strip: 'Status',
}

function isRegionName(name: string): name is RegionName {
  return (KNOWN_REGIONS as readonly string[]).includes(name)
}

/**
 * The fixed-viewport frame. Each region is the landmark element for its role:
 * header -> header (banner), nav -> nav, main -> main, inspector and dock -> aside, strip -> footer.
 * The layout is fixed for the life of the page; F6 / Shift+F6 cycle focus between regions.
 */
export function AppShell({ layout, regions, regionLabels, skipLinkLabel = 'Skip to main content' }: AppShellProps) {
  const uid = useId()
  const mainId = `ui-main-${uid.replace(/:/g, '')}`
  const shellRef = useRef<HTMLDivElement>(null)

  const unknown = layout.regions.filter((name) => !isRegionName(name))
  if (unknown.length > 0) {
    throw new Error(`layout "${layout.id}" names unknown region(s): ${unknown.join(', ')}`)
  }
  const names = layout.regions as readonly RegionName[]

  const onKeyDown = useCallback((event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== 'F6' || !shellRef.current) return
    const regionEls = Array.from(
      shellRef.current.querySelectorAll<HTMLElement>(':scope > .ui-shell__region'),
    )
    if (regionEls.length === 0) return
    const current = regionEls.findIndex((el) => el.contains(document.activeElement))
    const step = event.shiftKey ? -1 : 1
    const next = current === -1 ? 0 : (current + step + regionEls.length) % regionEls.length
    regionEls[next]?.focus()
    event.preventDefault()
  }, [])

  return (
    <div ref={shellRef} className="ui-shell" data-layout={layout.id} onKeyDown={onKeyDown}>
      {names.includes('main') && (
        <a className="ui-skip-link" href={`#${mainId}`}>
          {skipLinkLabel}
        </a>
      )}
      {names.map((name) => {
        const label = regionLabels?.[name] ?? DEFAULT_LABELS[name]
        const common = {
          className: 'ui-shell__region',
          'data-region': name,
          tabIndex: -1,
        }
        const content = regions[name]
        switch (name) {
          case 'header':
            return <header key={name} {...common}>{content}</header>
          case 'nav':
            return (
              <nav key={name} {...common} aria-label={label}>
                {content}
              </nav>
            )
          case 'main':
            return (
              <main key={name} {...common} id={mainId}>
                {content}
              </main>
            )
          case 'inspector':
          case 'dock':
            return (
              <aside key={name} {...common} aria-label={label}>
                {content}
              </aside>
            )
          case 'strip':
            return (
              <footer key={name} {...common} aria-label={label}>
                {content}
              </footer>
            )
        }
      })}
    </div>
  )
}
