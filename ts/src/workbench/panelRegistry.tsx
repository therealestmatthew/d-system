import type { ComponentType } from 'react'
import TerminalRegion, { TerminalRegionCmd, TerminalRegionPowerShell } from '../stage/TerminalRegion'
import NotesStripRegion from '../stage/NotesStripRegion'
import OverviewRegion from '../stage/OverviewRegion'
import HtmlViewerRegion from '../stage/HtmlViewerRegion'
import FileBrowserRegion from '../stage/FileBrowserRegion'
import IdeaExplorerRegion from '../stage/IdeaExplorerRegion'

/**
 * The panel type registry (REQ-007 W05/W06): every panel type id a layout's slots may name, and
 * the component that renders it. `Component: null` marks a type id a later phase will implement
 * (`backlog-explorer`, still pending) — declaring the id now lets the shipped layout files admit
 * it into a slot today, so that phase's only change is registering the component here and (if
 * needed) a layout-file edit, never new engine code (ADR-016 consequences).
 *
 * `file-browser` (`phase-wb-05`, `FileBrowserRegion`) and `idea-explorer` (`phase-wb-06`,
 * `IdeaExplorerRegion`) are this comment's other two formerly-`null` entries now filled in.
 * `file-browser` is REQ-007 W09's tree, filters and documentation-explorer preset, plus the
 * five-action right-click context menu (reveal, open-in-viewer with tab submenu, copy relative
 * path, copy absolute path, inject path) that same requirement row describes, wired via
 * `FileTreeContextMenu.tsx`. `idea-explorer` is REQ-007 W10's columns (id, title, status, age,
 * annotation count, link count), sortable and text/status-filterable, with a standard/
 * priority-queue view toggle that re-fetches `phase-wb-01`'s `GET /ideas` or `GET /ideas/queue`
 * rather than re-ranking client-side. Layout 1's explorer slot
 * (`_data/workbench/layouts/layout-1.json`) admits `file-browser`, `idea-explorer` and
 * `backlog-explorer`, in that order, with `default_panel: null`; `Slot.tsx` resolves a slot with
 * exactly one *implemented* admitted panel to that panel, and — now that two are implemented —
 * falls through to its "first of `implementedAdmits`" default when no panel has been explicitly
 * selected, which is `file-browser` given the admits order above: it stays the slot's
 * default-visible panel, with `idea-explorer` reachable via the slot-header dropdown
 * `Slot.tsx` now renders for this slot. `backlog-explorer` will join that same dropdown once
 * implemented, with no further layout-file edit needed.
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
 * dropdown header instead; the terminal slot (above) was the first to reach that branch, and the
 * explorer slot is now the second, once `phase-wb-06` filled in `idea-explorer` alongside
 * `phase-wb-05`'s `file-browser`. The wrapped panel still renders its own inner header too (the
 * same double-header cosmetic case the terminal slot already carries) — left as-is here too, out
 * of this phase's declared scope (`ts/src`, this file and `IdeaExplorerRegion.tsx`), not because
 * it is otherwise desirable.
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
  'idea-explorer': { displayName: 'Idea Explorer', Component: IdeaExplorerRegion },
  'backlog-explorer': { displayName: 'Backlog Explorer', Component: null },
}

export function panelDisplayName(panelId: string): string {
  return PANEL_REGISTRY[panelId]?.displayName ?? panelId
}

export function panelComponent(panelId: string | null): ComponentType | null {
  if (!panelId) return null
  return PANEL_REGISTRY[panelId]?.Component ?? null
}
