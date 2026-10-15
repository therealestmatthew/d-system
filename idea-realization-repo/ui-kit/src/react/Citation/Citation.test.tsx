import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { axeViolations } from '../test-utils/axe'
import { Citation, SourceList, safeHref, type Source } from './Citation'

const SOURCES: Source[] = [
  { id: 's1', kind: 'statute', title: 'SS UI Act § 4-210(b)', location: 'Synthetic State corpus' },
  { id: 's2', kind: 'policy', title: 'Benefit Policy Manual 7.3', location: 'Attendance and warnings' },
  { id: 's3', kind: 'precedent', title: 'Appeal Board P-B-17', location: 'Notice of a warning' },
  { id: 's4', kind: 'claim-document', title: 'Employer exhibit 3', location: 'p. 1', href: 'https://example.invalid/exhibit-3' },
]

describe('Citation', () => {
  it('is a link whose accessible name names the source and contains the visible index', () => {
    render(<Citation index={1} source={SOURCES[0]!} />)
    const link = screen.getByRole('link', { name: 'Source 1: Statute, SS UI Act § 4-210(b)' })
    expect(link).toHaveClass('ui-citation')
    expect(link.querySelector('.ui-citation__index')).toHaveTextContent('1')
    expect(link.querySelector('.ui-citation__label')).toBeNull()
  })

  it('links to the list item by default, or to the source href when given', () => {
    render(
      <>
        <Citation index={1} source={SOURCES[0]!} />
        <Citation index={4} source={SOURCES[3]!} label="exhibit 3" />
        <Citation index={2} source={SOURCES[1]!} idPrefix="case-src-" />
      </>,
    )
    expect(screen.getByRole('link', { name: /^Source 1:/ })).toHaveAttribute('href', '#source-s1')
    const external = screen.getByRole('link', { name: /^Source 4:/ })
    expect(external).toHaveAttribute('href', 'https://example.invalid/exhibit-3')
    expect(external.querySelector('.ui-citation__label')).toHaveTextContent('exhibit 3')
    expect(screen.getByRole('link', { name: /^Source 2:/ })).toHaveAttribute('href', '#case-src-s2')
  })
})

describe('SourceList', () => {
  it('renders an ordered list whose items are the citation targets and name kind, title and location', () => {
    const { container } = render(<SourceList sources={SOURCES} highlightedId="s2" />)
    const list = screen.getByRole('list', { name: 'Sources' })
    expect(list.tagName).toBe('OL')
    expect(list).toHaveClass('ui-sources')
    const items = Array.from(container.querySelectorAll('li.ui-sources__item'))
    expect(items.map((li) => li.id)).toEqual(['source-s1', 'source-s2', 'source-s3', 'source-s4'])
    expect(items.map((li) => li.querySelector('.ui-sources__kind')?.textContent)).toEqual([
      'Statute',
      'Policy',
      'Precedent',
      'Claim document',
    ])
    expect(items[0]!.querySelector('.ui-sources__title')).toHaveTextContent('SS UI Act § 4-210(b)')
    expect(items[0]!.querySelector('.ui-sources__location')).toHaveTextContent('Synthetic State corpus')
    expect(items[1]).toHaveAttribute('data-highlighted', 'true')
    expect(items[0]).not.toHaveAttribute('data-highlighted')
    expect(items[3]!.querySelector('a.ui-sources__title')).toHaveAttribute('href', 'https://example.invalid/exhibit-3')
  })

  it('chips and list together have no axe violations', async () => {
    const { container } = render(
      <div>
        <p>
          Misconduct needs a knowing breach.
          <Citation index={1} source={SOURCES[0]!} />
          <Citation index={2} source={SOURCES[1]!} label="7.3" />
        </p>
        <SourceList sources={SOURCES} />
      </div>,
    )
    expect(await axeViolations(container)).toEqual([])
  })

  it('never links to an unsafe scheme: the chip falls back to the list and the title is plain text', () => {
    const unsafe = ['javascript:alert(1)', ' JavaScript:alert(1)', 'java\tscript:alert(1)', 'data:text/html,x', 'vbscript:x']
    for (const href of unsafe) {
      const source: Source = { id: 'bad', kind: 'policy', title: 'Bad source', location: 'x', href }
      const { container, unmount } = render(
        <>
          <Citation index={1} source={source} />
          <SourceList sources={[source]} />
        </>,
      )
      expect(screen.getByRole('link', { name: /^Source 1:/ })).toHaveAttribute('href', '#source-bad')
      expect(container.querySelector('.ui-sources__title')!.tagName).toBe('SPAN')
      unmount()
    }
  })

  it('keeps http(s) and relative hrefs', () => {
    expect(safeHref('https://example.invalid/a')).toBe('https://example.invalid/a')
    expect(safeHref('HTTP://example.invalid/a')).toBe('HTTP://example.invalid/a')
    expect(safeHref('/docs/a.pdf')).toBe('/docs/a.pdf')
    expect(safeHref('#source-s1')).toBe('#source-s1')
    expect(safeHref('mailto:x@example.invalid')).toBeUndefined()
    expect(safeHref('')).toBeUndefined()
    expect(safeHref(undefined)).toBeUndefined()
  })
})
