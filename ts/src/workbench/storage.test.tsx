import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { loadStoredState, patchStoredState } from './storage'

// REQ-011 R05 and ADR-016 rule 3: the layout `schema_version` is part of the storage key, so state
// written before the slot ids were renamed (version 2) is never read by version 3.
const V2_KEY = 'd-system:workbench-state:v2'
const V3_KEY = 'd-system:workbench-state:v3'

beforeEach(() => window.localStorage.clear())
afterEach(() => window.localStorage.clear())

describe('stored workbench state across the slot id rename', () => {
  it('ignores a version-2 key naming the old slot ids, leaving layout defaults to apply', () => {
    window.localStorage.setItem(
      V2_KEY,
      JSON.stringify({
        schema_version: 2,
        active_layout: 'layout-2',
        panel_assignments: { 'layout-1': { 'html-viewer': 'terminal', 'notes-strip': 'notes-strip' } },
        slot_visible_panel: { 'layout-1': { terminal: 'html-viewer', main: 'terminal-cmd' } },
        active_notes_file: 'talking-points.json',
      }),
    )
    expect(loadStoredState(3)).toBeNull()
    // Nothing is written back under the old key or migrated into the new one by reading.
    expect(window.localStorage.getItem(V3_KEY)).toBeNull()
    expect(window.localStorage.getItem(V2_KEY)).not.toBeNull()
  })

  it('does not carry version-2 fields into a version-3 write', () => {
    window.localStorage.setItem(V2_KEY, JSON.stringify({ schema_version: 2, active_layout: 'layout-2' }))
    patchStoredState(3, { active_layout: 'layout-1' })
    expect(loadStoredState(3)).toEqual({ schema_version: 3, active_layout: 'layout-1' })
  })

  it('discards a version-3 key whose recorded version is not 3', () => {
    window.localStorage.setItem(V3_KEY, JSON.stringify({ schema_version: 2, active_layout: 'layout-1' }))
    expect(loadStoredState(3)).toBeNull()
  })
})

// ADR-031 decision 10: version 4 removed `eligible_slots` from the layout files. Selections written
// under version 3 are never read by version 4, and nothing migrates them.
const V4_KEY = 'd-system:workbench-state:v4'

describe('stored workbench state across the removal of the eligibility list', () => {
  it('ignores a version-3 key, leaving layout defaults to apply, and leaves it unread in place', () => {
    window.localStorage.setItem(
      V3_KEY,
      JSON.stringify({
        schema_version: 3,
        active_layout: 'layout-2',
        panel_assignments: { 'layout-2': { overview: 'primary' } },
        slot_visible_panel: { 'layout-2': { primary: 'overview' } },
      }),
    )
    expect(loadStoredState(4)).toBeNull()
    expect(window.localStorage.getItem(V4_KEY)).toBeNull()
    expect(window.localStorage.getItem(V3_KEY)).not.toBeNull()
  })

  it('does not carry version-3 fields into a version-4 write', () => {
    window.localStorage.setItem(V3_KEY, JSON.stringify({ schema_version: 3, active_layout: 'layout-2' }))
    patchStoredState(4, { active_layout: 'layout-1' })
    expect(loadStoredState(4)).toEqual({ schema_version: 4, active_layout: 'layout-1' })
  })
})
