import type { BatchReceipt } from './panelBridge'

/**
 * The HTML Viewer's placement policy for opening a set of files (ADR-029 section 6 point 8, REQ-012
 * R10). Pure, so the policy is testable without rendering the panel:
 *
 * - A file the viewer cannot show (`isCompatible` false) is declined `incompatible`.
 * - The remaining files fill the viewer's empty tabs first (a tab with no page selected), in tab
 *   order, then new tabs while the tab count is below `maxTabs`.
 * - A tab that holds a page is never replaced. A file with no free tab left is declined `capacity`.
 * - The first delivered file's tab becomes the active one.
 *
 * Every requested path appears in exactly one of `receipt.delivered` and `receipt.declined`.
 */
export interface PlacementTab {
  id: number
  selectedFile: string | null
}

/** Where one delivered file goes: an existing empty tab (`newTab` false) or a new tab with the
 * pre-allocated `tabId` (`newTab` true). */
export interface PlacementAssignment {
  tabId: number
  path: string
  newTab: boolean
}

export interface PlacementPlan {
  receipt: BatchReceipt
  assignments: PlacementAssignment[]
}

export function planOpenFiles(
  tabs: PlacementTab[],
  paths: string[],
  options: { maxTabs: number; nextTabId: number; isCompatible: (path: string) => boolean },
): PlacementPlan {
  const emptyTabIds = tabs.filter((tab) => tab.selectedFile === null).map((tab) => tab.id)
  const newTabRoom = Math.max(0, options.maxTabs - tabs.length)
  let freeSlots = emptyTabIds.length + newTabRoom
  let nextEmpty = 0
  let nextTabId = options.nextTabId

  const receipt: BatchReceipt = { delivered: [], declined: [] }
  const assignments: PlacementAssignment[] = []
  for (const path of paths) {
    if (!options.isCompatible(path)) {
      receipt.declined.push({ path, reason: 'incompatible' })
      continue
    }
    if (freeSlots === 0) {
      receipt.declined.push({ path, reason: 'capacity' })
      continue
    }
    freeSlots -= 1
    if (nextEmpty < emptyTabIds.length) {
      assignments.push({ tabId: emptyTabIds[nextEmpty], path, newTab: false })
      nextEmpty += 1
    } else {
      assignments.push({ tabId: nextTabId, path, newTab: true })
      nextTabId += 1
    }
    receipt.delivered.push(path)
  }
  return { receipt, assignments }
}
