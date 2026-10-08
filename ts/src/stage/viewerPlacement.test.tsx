import { describe, expect, it } from 'vitest'
import { isViewerCompatible } from './compatibleExtensions'
import { planOpenFiles, type PlacementTab } from './viewerPlacement'

// ADR-029 section 6 point 8 as a pure function: empty tabs first, then new tabs up to the cap,
// never replace a tab holding a page, decline the rest `capacity`, decline unsupported files
// `incompatible`. REQ-012 R07: every requested path is in exactly one list.

const MAX = 4
const page = (id: number, selectedFile: string | null = `held-${id}.html`): PlacementTab => ({
  id,
  selectedFile,
})
const plan = (tabs: PlacementTab[], paths: string[], nextTabId = 100) =>
  planOpenFiles(tabs, paths, { maxTabs: MAX, nextTabId, isCompatible: isViewerCompatible })

function expectAccountedFor(result: ReturnType<typeof plan>, paths: string[]) {
  const all = [...result.receipt.delivered, ...result.receipt.declined.map((item) => item.path)]
  expect([...all].sort()).toEqual([...paths].sort())
}

describe('planOpenFiles', () => {
  it('fills the empty tab first, then adds tabs for the rest', () => {
    const paths = ['a.html', 'b.html', 'c.html']
    const result = plan([page(1, null)], paths)
    expect(result.assignments).toEqual([
      { tabId: 1, path: 'a.html', newTab: false },
      { tabId: 100, path: 'b.html', newTab: true },
      { tabId: 101, path: 'c.html', newTab: true },
    ])
    expect(result.receipt).toEqual({ delivered: paths, declined: [] })
  })

  it('never replaces a tab that holds a page', () => {
    const result = plan([page(1), page(2, null), page(3)], ['a.html', 'b.html'])
    expect(result.assignments.map((assignment) => assignment.tabId)).toEqual([2, 100])
    expect(result.assignments.every((assignment) => assignment.tabId !== 1 && assignment.tabId !== 3)).toBe(true)
  })

  it('uses empty tabs in tab order', () => {
    const result = plan([page(1, null), page(2), page(3, null)], ['a.html', 'b.html', 'c.html'])
    expect(result.assignments.map((assignment) => [assignment.tabId, assignment.newTab])).toEqual([
      [1, false],
      [3, false],
      [100, true],
    ])
  })

  it('declines files beyond capacity and reports which', () => {
    const paths = ['a.html', 'b.html', 'c.html', 'd.html', 'e.html', 'f.html']
    const result = plan([page(1, null)], paths)
    expect(result.receipt.delivered).toEqual(['a.html', 'b.html', 'c.html', 'd.html'])
    expect(result.receipt.declined).toEqual([
      { path: 'e.html', reason: 'capacity' },
      { path: 'f.html', reason: 'capacity' },
    ])
    expectAccountedFor(result, paths)
  })

  it('declines everything for capacity when every tab holds a page and the cap is reached', () => {
    const tabs = [page(1), page(2), page(3), page(4)]
    const result = plan(tabs, ['a.html', 'b.html'])
    expect(result.assignments).toEqual([])
    expect(result.receipt.declined).toEqual([
      { path: 'a.html', reason: 'capacity' },
      { path: 'b.html', reason: 'capacity' },
    ])
  })

  it('declines an incompatible file without using a slot for it', () => {
    const paths = ['a.html', 'tool.py', 'b.md', 'data.json', 'c.svg']
    const result = plan([page(1), page(2), page(3)], paths)
    // One free slot: a.html takes it, the rest compatible files lose for capacity.
    expect(result.receipt.delivered).toEqual(['a.html'])
    expect(result.receipt.declined).toEqual([
      { path: 'tool.py', reason: 'incompatible' },
      { path: 'b.md', reason: 'capacity' },
      { path: 'data.json', reason: 'incompatible' },
      { path: 'c.svg', reason: 'capacity' },
    ])
    expectAccountedFor(result, paths)
  })

  it('opens three files when three slots are free (REQ-012 R10)', () => {
    const paths = ['one.html', 'two.md', 'three.svg']
    const result = plan([page(1, null)], paths)
    expect(result.receipt).toEqual({ delivered: paths, declined: [] })
    expect(result.assignments).toHaveLength(3)
  })

  it('makes the first delivered file the first assignment, skipping a declined first file', () => {
    const result = plan([page(1, null)], ['tool.py', 'b.html', 'c.html'])
    expect(result.assignments[0]).toEqual({ tabId: 1, path: 'b.html', newTab: false })
  })

  it('returns an empty plan for an empty request', () => {
    expect(plan([page(1, null)], [])).toEqual({ receipt: { delivered: [], declined: [] }, assignments: [] })
  })
})

describe('isViewerCompatible', () => {
  it.each([
    ['docs/a.html', true],
    ['A.HTML', true],
    ['x/y.md', true],
    ['logo.PNG', true],
    ['tool.py', false],
    ['data.json', false],
    ['Makefile', false],
    ['.gitignore', false],
    ['dir.html/readme', false],
  ])('%s -> %s', (path, expected) => {
    expect(isViewerCompatible(path)).toBe(expected)
  })
})
