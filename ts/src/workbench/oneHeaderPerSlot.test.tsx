import { cleanup, render, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import StagePage from '../stage/StagePage'
import layout1 from '../../../_data/workbench/layouts/layout-1.json'
import layout2 from '../../../_data/workbench/layouts/layout-2.json'

// REQ-011 R13 (idea 000101): a slot's top bar is drawn once, by the slot, and a hosted panel cannot
// draw a second one. This is the standing check the requirement asks for: assign every panel type
// into every slot it can occupy, in both shipped layouts, and count the bars rendered in each slot.
// A bar is a `header` element or an element with `role="banner"`, never a class name, so a panel
// that draws its own bar under a different class is still counted (ADR-031 decision 1).

interface LayoutFile {
  schema_version: number
  layout_id: string
  slots: { slot_id: string }[]
  panels: { panel_id: string; eligible_slots: string[] }[]
}

const LAYOUTS: LayoutFile[] = [layout1 as LayoutFile, layout2 as LayoutFile]

function stubBackend() {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      const layout = LAYOUTS.find((candidate) => url.endsWith(`/workbench-layouts/${candidate.layout_id}.json`))
      if (layout) return new Response(JSON.stringify(layout), { status: 200 })
      if (url.includes('/demo/stage/terminal-enabled')) {
        return new Response(JSON.stringify({ terminal_enabled: false }), { status: 200 })
      }
      return new Response(null, { status: 404 })
    }),
  )
}

beforeEach(() => {
  window.localStorage.clear()
  stubBackend()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  window.localStorage.clear()
})

function seed(layout: LayoutFile, panelId: string, slotId: string) {
  window.localStorage.setItem(
    `d-system:workbench-state:v${layout.schema_version}`,
    JSON.stringify({
      schema_version: layout.schema_version,
      active_layout: layout.layout_id,
      panel_assignments: { [layout.layout_id]: { [panelId]: slotId } },
      slot_visible_panel: { [layout.layout_id]: { [slotId]: panelId } },
    }),
  )
}

function barsIn(element: Element): number {
  return element.querySelectorAll('header, [role="banner"]').length
}

const CASES = LAYOUTS.flatMap((layout) =>
  layout.panels.flatMap((panel) =>
    panel.eligible_slots.map((slotId) => ({ layout, panelId: panel.panel_id, slotId })),
  ),
)

describe('one top bar per slot (REQ-011 R13)', () => {
  it.each(CASES.map((c) => [c.layout.layout_id, c.panelId, c.slotId, c] as const))(
    '%s: %s in %s',
    async (_layoutId, panelId, slotId, { layout }) => {
      seed(layout, panelId, slotId)
      const { container } = render(<StagePage />)
      await waitFor(() => {
        const host = container.querySelector(`[data-panel-host="${panelId}"]`)
        expect(host).not.toBeNull()
        expect(host?.firstElementChild).not.toBeNull()
      })
      const slots = [...container.querySelectorAll('.stage-workbench-slot')]
      expect(slots.map((slot) => (slot as HTMLElement).style.gridArea).sort()).toEqual(
        layout.slots.map((slot) => slot.slot_id).sort(),
      )
      // The panel under test sits in the slot it was assigned to.
      const target = slots.find((slot) => (slot as HTMLElement).style.gridArea === slotId)
      expect(target?.querySelector(`[data-panel-host="${panelId}"]`)).not.toBeNull()
      for (const slot of slots) {
        const id = (slot as HTMLElement).style.gridArea
        expect(barsIn(slot), `${layout.layout_id}/${id} holding ${panelId}`).toBe(1)
      }
    },
  )
})
