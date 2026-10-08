import { cleanup, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import layout1 from '../../../_data/workbench/layouts/layout-1.json'
import layout2 from '../../../_data/workbench/layouts/layout-2.json'
import { useWorkbenchLayouts } from './useWorkbenchLayouts'

// REQ-011 R12: a stored panel assignment is honored only when the panel is structurally eligible
// for the slot (ADR-031 decision 4); anything else is discarded to the layout's defaults, silently
// (ADR-016 rule 3, kept). The key carries the layouts' schema version, so version-3 state is simply
// never read.

const LAYOUTS = [layout1, layout2]
const KEY = `d-system:workbench-state:v${layout1.schema_version}`

beforeEach(() => {
  window.localStorage.clear()
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      const layout = LAYOUTS.find((candidate) => url.endsWith(`/workbench-layouts/${candidate.layout_id}.json`))
      return layout ? new Response(JSON.stringify(layout), { status: 200 }) : new Response(null, { status: 404 })
    }),
  )
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  window.localStorage.clear()
})

function seed(state: Record<string, unknown>) {
  window.localStorage.setItem(KEY, JSON.stringify({ schema_version: layout1.schema_version, ...state }))
}

async function loaded() {
  const hook = renderHook(() => useWorkbenchLayouts())
  await waitFor(() => expect(hook.result.current.loadState).toBe('loaded'))
  return hook
}

function admits(hook: Awaited<ReturnType<typeof loaded>>, layoutId: string, slotId: string) {
  const layout = hook.result.current.layouts.find((candidate) => candidate.layout_id === layoutId)
  return layout?.slots.find((slot) => slot.slot_id === slotId)?.admits
}

describe('useWorkbenchLayouts stored assignments', () => {
  it('reads the layouts at schema version 4', async () => {
    const hook = await loaded()
    expect(hook.result.current.schemaVersion).toBe(4)
  })

  it('honors a stored assignment into a slot the panel is structurally eligible for', async () => {
    // Overview is an embedded document like the HTML Viewer, so the secondary slot admits it.
    seed({ panel_assignments: { 'layout-2': { overview: 'secondary' } } })
    const hook = await loaded()
    expect(admits(hook, 'layout-2', 'secondary')).toContain('overview')
    expect(admits(hook, 'layout-2', 'primary')).not.toContain('overview')
  })

  it('discards a stored assignment into a slot whose body the panel does not fit', async () => {
    seed({
      panel_assignments: {
        'layout-1': { terminal: 'explorer', 'file-browser': 'primary', 'notes-strip': 'primary' },
      },
    })
    const hook = await loaded()
    expect(admits(hook, 'layout-1', 'secondary')).toContain('terminal')
    expect(admits(hook, 'layout-1', 'explorer')).not.toContain('terminal')
    expect(admits(hook, 'layout-1', 'explorer')).toContain('file-browser')
    expect(admits(hook, 'layout-1', 'strip')).toEqual(['notes-strip'])
  })

  it('never reads state written under the previous schema version', async () => {
    window.localStorage.setItem(
      'd-system:workbench-state:v3',
      JSON.stringify({
        schema_version: 3,
        active_layout: 'layout-2',
        panel_assignments: { 'layout-2': { 'html-viewer': 'secondary' } },
      }),
    )
    const hook = await loaded()
    expect(hook.result.current.activeLayoutId).toBe('layout-1')
    expect(admits(hook, 'layout-2', 'secondary')).not.toContain('html-viewer')
  })

  it('ignores a move the matcher refuses', async () => {
    const hook = await loaded()
    hook.result.current.setPanelSlot('layout-1', 'file-browser', 'strip')
    await waitFor(() => expect(hook.result.current.loadState).toBe('loaded'))
    expect(admits(hook, 'layout-1', 'strip')).toEqual(['notes-strip'])
    expect(admits(hook, 'layout-1', 'explorer')).toContain('file-browser')
  })
})
