import slotSchemasData from '../../../_data/workbench/slot-schemas.json'
import panelElementsData from '../../../_data/workbench/panel-elements.json'
import { frameForRole, isEligible, type PanelElements, type SlotSchemas } from './slotMatcher'

// The two data files structural eligibility is computed from (ADR-031 decisions 2 and 4). They are
// imported, not fetched: `PANEL_REGISTRY` refers to a panel type's entry synchronously
// (`elements: panelElements['html-viewer']`), and the matcher has to answer before the layouts
// have finished loading. Unlike the layout files they are therefore bundled, and editing one
// reaches the page through the dev server's module reload, not a plain refresh.

export const slotSchemas = slotSchemasData as unknown as SlotSchemas

/** Panel type -> its element configuration. Keyed by panel type, so the registry entry and the
 * data entry share one key. */
export const panelElements = panelElementsData.panels as Record<string, PanelElements>

/** The slot ids from `slotIds` (each one a role) that `panelId` may occupy, in the order given.
 * Computed on every call from the two data files; no list of eligible slots is kept anywhere. */
export function slotsEligibleFor(panelId: string, slotIds: string[]): string[] {
  const elements = panelElements[panelId]
  if (!elements) return []
  return slotIds.filter((slotId) => isEligible(elements, slotId, slotSchemas))
}

/** The frame the slot with this id (its role) is drawn with, or `null` for an unknown role. */
export function frameForSlot(slotId: string) {
  return frameForRole(slotId, slotSchemas)
}
