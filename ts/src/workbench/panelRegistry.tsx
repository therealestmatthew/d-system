import type { ComponentType } from 'react'
import TerminalRegion, { TerminalRegionCmd, TerminalRegionPowerShell } from '../stage/TerminalRegion'
import NotesStripRegion from '../stage/NotesStripRegion'
import OverviewRegion from '../stage/OverviewRegion'
import HtmlViewerRegion from '../stage/HtmlViewerRegion'
import FileBrowserRegion from '../stage/FileBrowserRegion'
import IdeaExplorerRegion from '../stage/IdeaExplorerRegion'
import BacklogExplorerRegion from '../stage/BacklogExplorerRegion'
import { panelElements } from './slotEligibility'
import type { PanelElements } from './slotMatcher'

/**
 * The panel type registry (REQ-007 W05/W06): every panel type id a layout's slots may name, and
 * the component that renders it. `Component: null` marks a type id a later phase will implement
 * — declaring the id now lets the shipped layout files admit it into a slot today, so that
 * phase's only change is registering the component here and (if needed) a layout-file edit, never
 * new engine code (ADR-016 consequences).
 *
 * `file-browser` (`phase-wb-05`, `FileBrowserRegion`), `idea-explorer` and `backlog-explorer`
 * (both `phase-wb-06`, `IdeaExplorerRegion` and `BacklogExplorerRegion`) are this comment's three
 * formerly-`null` entries now filled in. `file-browser` is REQ-007 W09's tree, filters and
 * documentation-explorer preset, plus the five-action right-click context menu (reveal,
 * open-in-viewer with tab submenu, copy relative path, copy absolute path, inject path) that same
 * requirement row describes, wired via `FileTreeContextMenu.tsx`. `idea-explorer` is REQ-007
 * W10's columns (id, title, status, age, annotation count, link count) and `backlog-explorer` is
 * REQ-007 W11's columns (id, title, status, priority, queue position, depends_on) — both
 * sortable and text/status-filterable, with a standard/priority-queue view toggle that re-fetches
 * `phase-wb-01`'s `GET /ideas`/`GET /ideas/queue` or `GET /backlog`/`GET /backlog/queue` rather
 * than re-ranking client-side. The two panels are the same configuration surface, parameterized
 * by data source: both render the shared `ExplorerRegion` (`stage/explorer/ExplorerRegion.tsx`),
 * which owns all table/sort/filter/queue-toggle behavior; `IdeaExplorerRegion.tsx` and
 * `BacklogExplorerRegion.tsx` supply only their columns, urls, status vocabulary and search
 * predicate. Layout 1's explorer slot (`_data/workbench/layouts/layout-1.json`) admits
 * `file-browser`, `idea-explorer` and `backlog-explorer`, in that order, with
 * `default_panel: null`; `Slot.tsx` resolves a slot with exactly one *implemented* admitted panel
 * to that panel, and falls through to its "first of `implementedAdmits`" default when no panel
 * has been explicitly selected, which is `file-browser` given the admits order above: it stays
 * the slot's default-visible panel, with `idea-explorer` and `backlog-explorer` both reachable
 * via the slot-header dropdown `Slot.tsx` renders for this slot now that all three are
 * implemented.
 *
 * `terminal`, `notes-strip` and `overview` are this phase's three existing regions (REQ-007
 * dispatch item 5: "existing regions become panels of this engine").
 *
 * `html-viewer` (`phase-wb-04`, `HtmlViewerRegion`) generalizes and replaces `overview` as
 * layout 1's primary slot default (`_data/workbench/layouts/layout-1.json`): the generated overview
 * page is now one selectable entry inside the HTML Viewer's file dropdown rather than a
 * separately-admitted panel type, so layout 1's primary slot admits `html-viewer` only. `overview`
 * stays registered here — `OverviewRegion` is untouched and layout 2's primary slot still admits it
 * — this phase's dispatched deliverable paths did not include layout 2 or removing the older
 * component.
 *
 * `terminal-cmd` and `terminal-powershell` (REQ-007 W12) are the CMD and PowerShell panel
 * options — the secondary slot's `admits` list (`_data/workbench/layouts/*.json`) now names all
 * three terminal ids, so the secondary slot is this repo's first slot to actually reach `Slot.tsx`'s
 * "more than one implemented panel" branch below: a slot-level header showing the current panel's
 * name beside a dropdown listing the other two, wrapping whichever terminal panel is selected in
 * an outer box. All three ids share the one `TerminalRegion` component, parameterized by its
 * `shell` prop — never three copies of the terminal panel's logic.
 *
 * A slot resolving to more than one *implemented* panel is wrapped by `Slot.tsx` in an outer
 * dropdown header instead; the secondary slot (above) was the first to reach that branch, and the
 * explorer slot is now the second, once `phase-wb-06` filled in `idea-explorer` and
 * `backlog-explorer` alongside `phase-wb-05`'s `file-browser` — the explorer slot's dropdown now
 * lists all three, per REQ-007 W06.
 *
 * `elements` is the panel type's element configuration (ADR-031 decision 4): the body kind its
 * content is and the bar elements it supplies. It is read from `_data/workbench/panel-elements.json`
 * under the same key, never restated here, and it is what decides which slot roles the type may
 * occupy (`slotMatcher.ts`). A panel never draws a top bar of its own: it renders each bar element
 * inside a `BarElement`, and the slot that holds it draws the one bar (REQ-011 R13).
 */
export interface PanelDefinition {
  displayName: string
  Component: ComponentType | null
  elements: PanelElements
}

export const PANEL_REGISTRY: Record<string, PanelDefinition> = {
  terminal: {
    displayName: 'Terminal (bash)',
    Component: TerminalRegion,
    elements: panelElements['terminal'],
  },
  'terminal-cmd': {
    displayName: 'CMD',
    Component: TerminalRegionCmd,
    elements: panelElements['terminal-cmd'],
  },
  'terminal-powershell': {
    displayName: 'PowerShell',
    Component: TerminalRegionPowerShell,
    elements: panelElements['terminal-powershell'],
  },
  'notes-strip': {
    displayName: 'Notes',
    Component: NotesStripRegion,
    elements: panelElements['notes-strip'],
  },
  overview: {
    displayName: 'Overview',
    Component: OverviewRegion,
    elements: panelElements['overview'],
  },
  'html-viewer': {
    displayName: 'HTML Viewer',
    Component: HtmlViewerRegion,
    elements: panelElements['html-viewer'],
  },
  'file-browser': {
    displayName: 'File Browser',
    Component: FileBrowserRegion,
    elements: panelElements['file-browser'],
  },
  'idea-explorer': {
    displayName: 'Idea Explorer',
    Component: IdeaExplorerRegion,
    elements: panelElements['idea-explorer'],
  },
  'backlog-explorer': {
    displayName: 'Backlog Explorer',
    Component: BacklogExplorerRegion,
    elements: panelElements['backlog-explorer'],
  },
}

export function panelDisplayName(panelId: string): string {
  return PANEL_REGISTRY[panelId]?.displayName ?? panelId
}

export function panelComponent(panelId: string | null): ComponentType | null {
  if (!panelId) return null
  return PANEL_REGISTRY[panelId]?.Component ?? null
}
