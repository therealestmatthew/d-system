import type { ReactNode } from 'react'

export type SourceKind = 'statute' | 'policy' | 'precedent' | 'claim-document'

/** One cited source. `id` is stable; the list item's anchor is `<idPrefix><id>`. */
export interface Source {
  id: string
  kind: SourceKind
  /** e.g. "SS UI Act § 4-210(b)". */
  title: string
  /** Where in the source, e.g. "Synthetic State corpus, section 4" or "p. 2". */
  location: string
  /** The source itself (S3 object, knowledge-base chunk, URL). When given, the chip links here. */
  href?: string
}

export const SOURCE_KIND_LABEL: Record<SourceKind, string> = {
  statute: 'Statute',
  policy: 'Policy',
  precedent: 'Precedent',
  'claim-document': 'Claim document',
}

const SCHEME = /^([a-z][a-z0-9+.-]*):/i

/**
 * The href if it is safe to put in a link: http(s), or relative (path, `?query`, `#anchor`).
 * Any other scheme (javascript:, data:, vbscript:, file: ...) returns undefined. Whitespace and
 * control characters are removed before the scheme is read, as browsers do when they parse a URL.
 */
export function safeHref(href: string | undefined): string | undefined {
  if (href === undefined) return undefined
  const normalized = href.replace(/[\u0000-\u0020\u007f]/g, '')
  if (normalized === '') return undefined
  const scheme = SCHEME.exec(normalized)
  if (scheme === null) return href
  const name = scheme[1]!.toLowerCase()
  return name === 'http' || name === 'https' ? href : undefined
}

/** Default anchor prefix shared by Citation and SourceList, so a chip reaches its list item. */
export const SOURCE_ID_PREFIX = 'source-'

/** The accessible name of a citation: "Source 1: Statute, SS UI Act § 4-210(b)". */
export function citationName(index: number, source: Source): string {
  return `Source ${index}: ${SOURCE_KIND_LABEL[source.kind]}, ${source.title}`
}

export interface CitationProps {
  /** The visible number; matches the source's position in the SourceList. */
  index: number
  source: Source
  /** Optional short label shown after the index, e.g. "§ 4-210(b)". */
  label?: ReactNode
  /** Anchor prefix of the SourceList on the page (default "source-"). */
  idPrefix?: string
}

/**
 * Inline numbered citation chip (ARCH-001 item 30, static form). A real link: to the source's
 * href when given and safe (see safeHref), otherwise to its item in the page's SourceList. No popover in Kit v0.
 */
export function Citation({ index, source, label, idPrefix = SOURCE_ID_PREFIX }: CitationProps) {
  return (
    <a className="ui-citation" href={safeHref(source.href) ?? `#${idPrefix}${source.id}`} aria-label={citationName(index, source)}>
      <span className="ui-citation__index">{index}</span>
      {label !== undefined && <span className="ui-citation__label">{label}</span>}
    </a>
  )
}

export interface SourceListProps {
  sources: Source[]
  /** Accessible name of the list (default "Sources"). */
  label?: string
  /** Anchor prefix (default "source-"); must match the Citations on the page. */
  idPrefix?: string
  /** Source id to highlight (sets data-highlighted), besides the CSS :target highlight. */
  highlightedId?: string
}

/** The page- or panel-level sources list the citation chips point at. Item n is citation [n]. */
export function SourceList({ sources, label = 'Sources', idPrefix = SOURCE_ID_PREFIX, highlightedId }: SourceListProps) {
  return (
    <ol className="ui-sources" aria-label={label}>
      {sources.map((s) => (
        <li
          key={s.id}
          id={`${idPrefix}${s.id}`}
          className="ui-sources__item"
          tabIndex={-1}
          data-highlighted={s.id === highlightedId || undefined}
        >
          <span className="ui-sources__kind">{SOURCE_KIND_LABEL[s.kind]}</span>
          {safeHref(s.href) !== undefined ? (
            <a className="ui-sources__title" href={safeHref(s.href)}>
              {s.title}
            </a>
          ) : (
            <span className="ui-sources__title">{s.title}</span>
          )}
          <span className="ui-sources__location">{s.location}</span>
        </li>
      ))}
    </ol>
  )
}
