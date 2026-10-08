import { describe, expect, it } from 'vitest'
import cases from '../../../_data/workbench/matcher-cases.json'
import { panelElements, slotSchemas, slotsEligibleFor } from './slotEligibility'
import {
  barLeaves,
  frameForRole,
  frameHasIdentity,
  isEligible,
  routeBar,
  subSlotFor,
  type PanelElements,
} from './slotMatcher'

// The TypeScript half of the structural-eligibility pair (ADR-031 decision 4, REQ-011 R12). The
// Python half is `test/test_workbench_slot_matcher.py`; both are held to the hand-written expected
// answers in `_data/workbench/matcher-cases.json`, so neither can drift from the other unnoticed.

const syntheticPanels = cases.synthetic_panels as Record<string, PanelElements>

function elementsFor(panel: string): PanelElements {
  const elements = syntheticPanels[panel] ?? panelElements[panel]
  if (!elements) throw new Error(`matcher-cases.json names an unknown panel ${panel}`)
  return elements
}

describe('structural eligibility (TypeScript matcher)', () => {
  it.each(cases.cases.map((c) => [`${c.panel} in ${c.role}`, c] as const))(
    'agrees with the shared cases: %s',
    (_name, c) => {
      expect(isEligible(elementsFor(c.panel), c.role, slotSchemas)).toBe(c.eligible)
    },
  )

  it('has a shared case for every shipped panel type in every role', () => {
    const covered = new Set(cases.cases.map((c) => `${c.panel}|${c.role}`))
    for (const panel of Object.keys(panelElements)) {
      for (const role of Object.keys(slotSchemas.roles)) {
        expect(covered.has(`${panel}|${role}`), `${panel} in ${role}`).toBe(true)
      }
    }
  })

  it('refuses a panel with more controls than the strip has room for (bar capacity)', () => {
    // The body kind fits and the only reason for the refusal is the bar: two controls against a
    // compact frame with room for one.
    const tooMany: PanelElements = { body: 'ticker', bar: ['help', 'choice', 'choice'] }
    const fits: PanelElements = { body: 'ticker', bar: ['help', 'choice'] }
    expect(isEligible(tooMany, 'strip', slotSchemas)).toBe(false)
    expect(isEligible(fits, 'strip', slotSchemas)).toBe(true)
    expect(isEligible({ body: 'table', bar: ['help', 'choice', 'choice'] }, 'explorer', slotSchemas)).toBe(
      true,
    )
  })

  it('takes sub-slots in declaration order and respects capacity', () => {
    const leaves = barLeaves(slotSchemas.frames.standard)
    expect(leaves.map((leaf) => leaf.id)).toEqual(['help', 'controls'])
    expect(routeBar(['help', 'choice', 'toggle'], leaves)).toEqual(['help', 'controls', 'controls'])
    expect(routeBar(['help', 'help'], leaves)).toBeNull()
    expect(routeBar(Array(5).fill('choice'), leaves)).toEqual(Array(5).fill('controls'))
    expect(routeBar(Array(6).fill('choice'), leaves)).toBeNull()
  })

  it('spills an element to the next sub-slot when the first admitting one is full', () => {
    const leaves = [
      { id: 'a', admits: ['choice'], capacity: 1 },
      { id: 'b', admits: ['choice', 'action'], capacity: 2 },
    ]
    expect(routeBar(['choice', 'choice', 'action'], leaves)).toEqual(['a', 'b', 'b'])
    expect(routeBar(['choice', 'choice', 'choice', 'action'], leaves)).toBeNull()
  })

  it('computes the shipped eligibility per slot from the data alone', () => {
    const slots = ['primary', 'secondary', 'explorer', 'strip']
    expect(slotsEligibleFor('terminal', slots)).toEqual(['primary', 'secondary'])
    expect(slotsEligibleFor('overview', slots)).toEqual(['primary', 'secondary'])
    expect(slotsEligibleFor('html-viewer', slots)).toEqual(['primary', 'secondary'])
    expect(slotsEligibleFor('file-browser', slots)).toEqual(['explorer'])
    expect(slotsEligibleFor('notes-strip', slots)).toEqual(['strip'])
    expect(slotsEligibleFor('no-such-panel', slots)).toEqual([])
    expect(isEligible(panelElements['html-viewer'], 'no-such-role', slotSchemas)).toBe(false)
  })

  it('finds the sub-slot a bar element type is drawn into, and none for an unadmitted type', () => {
    const standard = slotSchemas.frames.standard
    expect(subSlotFor(standard, 'help')).toBe('help')
    expect(subSlotFor(standard, 'toggle')).toBe('controls')
    expect(subSlotFor(standard, 'slider')).toBeNull()
  })

  it('knows which frames carry a panel switcher', () => {
    expect(frameHasIdentity(frameForRole('primary', slotSchemas)!)).toBe(true)
    expect(frameHasIdentity(frameForRole('strip', slotSchemas)!)).toBe(false)
    expect(frameForRole('no-such-role', slotSchemas)).toBeNull()
  })
})
