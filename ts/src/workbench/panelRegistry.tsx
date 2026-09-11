import type { ComponentType } from 'react'
import TerminalRegion from '../stage/TerminalRegion'
import NotesStripRegion from '../stage/NotesStripRegion'
import OverviewRegion from '../stage/OverviewRegion'

/**
 * The panel type registry (REQ-007 W05/W06): every panel type id a layout's slots may name, and
 * the component that renders it. `Component: null` marks a type id later phases will implement
 * (`html-viewer` — `phase-wb-04`; `file-browser` — `phase-wb-05`; `idea-explorer` and
 * `backlog-explorer` — `phase-wb-06`) — declaring the id now lets the shipped layout files admit
 * it into a slot today, so a future phase's only change is registering the component here and
 * (if needed) a layout-file edit, never new engine code (ADR-016 consequences).
 *
 * `terminal`, `notes-strip` and `overview` are this phase's three existing regions (REQ-007
 * dispatch item 5: "existing regions become panels of this engine") — each already renders its
 * own `.stage-region` section, which is what satisfies a single-panel slot's "plain header"
 * (REQ-007 W06) with no extra wrapper needed (the notes strip's own header carries no title,
 * per REQ-007 W01, but is still that same single `.stage-region` box). A slot resolving to more
 * than one *implemented* panel (none do in the two shipped layouts yet — see the layout JSON
 * files) is wrapped by `Slot.tsx` in an outer dropdown header instead; whichever future phase
 * first populates such a slot should note that the wrapped panel still renders its own inner
 * header too, and may want to drop it in that configuration — out of this phase's scope to
 * resolve for panels that do not exist yet.
 */
export interface PanelDefinition {
  displayName: string
  Component: ComponentType | null
}

export const PANEL_REGISTRY: Record<string, PanelDefinition> = {
  terminal: { displayName: 'Terminal', Component: TerminalRegion },
  'notes-strip': { displayName: 'Notes', Component: NotesStripRegion },
  overview: { displayName: 'Overview', Component: OverviewRegion },
  'html-viewer': { displayName: 'HTML Viewer', Component: null },
  'file-browser': { displayName: 'File Browser', Component: null },
  'idea-explorer': { displayName: 'Idea Explorer', Component: null },
  'backlog-explorer': { displayName: 'Backlog Explorer', Component: null },
}

export function panelDisplayName(panelId: string): string {
  return PANEL_REGISTRY[panelId]?.displayName ?? panelId
}

export function panelComponent(panelId: string | null): ComponentType | null {
  if (!panelId) return null
  return PANEL_REGISTRY[panelId]?.Component ?? null
}
