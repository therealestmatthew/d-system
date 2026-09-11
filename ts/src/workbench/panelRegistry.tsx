import type { ComponentType } from 'react'
import TerminalRegion, { TerminalRegionCmd, TerminalRegionPowerShell } from '../stage/TerminalRegion'
import NotesStripRegion from '../stage/NotesStripRegion'
import OverviewRegion from '../stage/OverviewRegion'
import HtmlViewerRegion from '../stage/HtmlViewerRegion'
import FileBrowserRegion from '../stage/FileBrowserRegion'

/**
 * The panel type registry (REQ-007 W05/W06): every panel type id a layout's slots may name, and
 * the component that renders it. `Component: null` marks a type id later phases will implement
 * (`idea-explorer` and `backlog-explorer` — `phase-wb-06`) — declaring the id now lets the
 * shipped layout files admit it into a slot today, so a future phase's only change is registering
 * the component here and (if needed) a layout-file edit, never new engine code (ADR-016
 * consequences).
 *
 * `file-browser` (`phase-wb-05`, `FileBrowserRegion`) is this comment's other formerly-`null`
 * entry now filled in — REQ-007 W09's tree, filters and documentation-explorer preset, plus the
 * five-action right-click context menu (reveal, open-in-viewer with tab submenu, copy relative
 * path, copy absolute path, inject path) that same requirement row describes, wired via
 * `FileTreeContextMenu.tsx`. Layout 1's explorer slot (`_data/workbench/layouts/layout-1.json`) admits `file-browser`,
 * `idea-explorer` and `backlog-explorer` with `default_panel: null`; `Slot.tsx` resolves a slot
 * with exactly one *implemented* admitted panel to that panel regardless of `default_panel`, so
 * `file-browser` renders there today with no layout-file edit needed — it stops being the only
 * implemented one the moment `phase-wb-06` fills in the other two, at which point that slot
 * reaches `Slot.tsx`'s multi-panel dropdown branch and `default_panel` would need to be set
 * explicitly for `file-browser` to stay the one shown first.
 *
 * `terminal`, `notes-strip` and `overview` are this phase's three existing regions (REQ-007
 * dispatch item 5: "existing regions become panels of this engine") — each already renders its
 * own `.stage-region` section, which is what satisfies a single-panel slot's "plain header"
 * (REQ-007 W06) with no extra wrapper needed (the notes strip's own header carries no title,
 * per REQ-007 W01, but is still that same single `.stage-region` box).
 *
 * `html-viewer` (`phase-wb-04`, `HtmlViewerRegion`) generalizes and replaces `overview` as
 * layout 1's main slot default (`_data/workbench/layouts/layout-1.json`): the generated overview
 * page is now one selectable entry inside the HTML Viewer's file dropdown rather than a
 * separately-admitted panel type, so layout 1's main slot admits `html-viewer` only. `overview`
 * stays registered here — `OverviewRegion` is untouched and layout 2's main slot still admits it
 * — this phase's dispatched deliverable paths did not include layout 2 or removing the older
 * component.
 *
 * `terminal-cmd` and `terminal-powershell` (REQ-007 W12) are the CMD and PowerShell panel
 * options — the terminal slot's `admits` list (`_data/workbench/layouts/*.json`) now names all
 * three terminal ids, so the terminal slot is this repo's first slot to actually reach `Slot.tsx`'s
 * "more than one implemented panel" branch below: a slot-level header showing the current panel's
 * name beside a dropdown listing the other two, wrapping whichever terminal panel is selected in
 * an outer box. The wrapped panel still renders its own inner header too (the double-header
 * cosmetic case flagged below) — left as-is, per the note this comment already carried before
 * this slot became the one to exercise it. All three ids share the one `TerminalRegion`
 * component, parameterized by its `shell` prop — never three copies of the terminal panel's
 * logic.
 *
 * A slot resolving to more than one *implemented* panel is wrapped by `Slot.tsx` in an outer
 * dropdown header instead; whichever future phase first populates such a slot should note that
 * the wrapped panel still renders its own inner header too, and may want to drop it in that
 * configuration — out of this phase's scope to resolve for panels that do not exist yet.
 */
export interface PanelDefinition {
  displayName: string
  Component: ComponentType | null
}

export const PANEL_REGISTRY: Record<string, PanelDefinition> = {
  terminal: { displayName: 'Terminal (bash)', Component: TerminalRegion },
  'terminal-cmd': { displayName: 'CMD', Component: TerminalRegionCmd },
  'terminal-powershell': { displayName: 'PowerShell', Component: TerminalRegionPowerShell },
  'notes-strip': { displayName: 'Notes', Component: NotesStripRegion },
  overview: { displayName: 'Overview', Component: OverviewRegion },
  'html-viewer': { displayName: 'HTML Viewer', Component: HtmlViewerRegion },
  'file-browser': { displayName: 'File Browser', Component: FileBrowserRegion },
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
