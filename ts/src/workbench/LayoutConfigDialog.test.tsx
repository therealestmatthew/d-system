import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import LayoutConfigDialog from './LayoutConfigDialog'
import layout1 from '../../../_data/workbench/layouts/layout-1.json'
import layout2 from '../../../_data/workbench/layouts/layout-2.json'
import type { LayoutDefinition } from './types'

// REQ-011 R12: a panel whose element configuration does not match a slot is not offered for it.
// The dialog's per-panel selector lists exactly the slots the matcher says the panel can occupy.

afterEach(cleanup)

type RawLayout = typeof layout1 | typeof layout2

function resolved(raw: RawLayout, assignment: Record<string, string>): LayoutDefinition {
  return {
    schema_version: raw.schema_version,
    layout_id: raw.layout_id,
    name: raw.name,
    slots: raw.slots.map((slot) => ({
      slot_id: slot.slot_id,
      display_name: slot.display_name,
      admits: raw.panels.map((p) => p.panel_id).filter((id) => assignment[id] === slot.slot_id),
      default_panel: null,
    })),
    panels: raw.panels,
    grid: raw.grid,
  }
}

function optionsFor(panelName: string): string[] {
  const label = screen.getByText(panelName, { selector: 'span' }).closest('label') as HTMLElement
  return within(label)
    .getAllByRole('option')
    .map((option) => option.textContent ?? '')
}

describe('LayoutConfigDialog eligibility', () => {
  it('offers each panel only the slots it is structurally eligible for', () => {
    const layout = resolved(layout2, layout2.default_assignment)
    render(
      <LayoutConfigDialog
        layouts={[layout]}
        activeLayout={layout}
        onSelectLayout={vi.fn()}
        onAssignPanelSlot={vi.fn()}
        visiblePanelInSlot={() => null}
      />,
    )
    fireEvent.click(screen.getByText('Configure layout ▾'))
    // Slot display names in layout 2: primary "Main", secondary "Terminal", explorer "Explorer",
    // strip "Notes".
    expect(optionsFor('Terminal (bash)').sort()).toEqual(['Main', 'Terminal'])
    expect(optionsFor('HTML Viewer').sort()).toEqual(['Main', 'Terminal'])
    // Overview is an embedded document like the HTML Viewer, so it may take either slot.
    expect(optionsFor('Overview').sort()).toEqual(['Main', 'Terminal'])
    expect(optionsFor('File Browser')).toEqual(['Explorer'])
    expect(optionsFor('Idea Explorer')).toEqual(['Explorer'])
    expect(optionsFor('Notes')).toEqual(['Notes'])
  })
})
