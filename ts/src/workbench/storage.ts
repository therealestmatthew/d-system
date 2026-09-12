import type { StoredHtmlViewerTab, StoredWorkbenchState } from './types'

// ADR-016 rule 3: "a single namespaced key carrying the schema_version of the layouts it was
// written against." The version lives in the key itself (not just the stored value) so a layout
// schema bump needs no migration code — the old key is simply never read again, and every reader
// falls straight through to the layout files' own defaults, matching rule 4 ("the repository
// defaults are the fallback state").
const STORAGE_KEY_PREFIX = 'd-system:workbench-state'

function storageKey(schemaVersion: number): string {
  return `${STORAGE_KEY_PREFIX}:v${schemaVersion}`
}

/** Every field beyond `schema_version` is optional (see `StoredWorkbenchState`'s doc comment) —
 * this validates only the fields actually present, so one owner's stored field (e.g. the notes
 * strip's `active_notes_file`) never fails validation just because another owner's field (e.g.
 * the layout engine's `panel_assignments`/`slot_visible_panel`) has not been written yet in a
 * fresh browser.
 */
/** Structural check only — every value is a `Record<string, Record<string, string>>` regardless
 * of which of `panel_assignments`/`slot_visible_panel` is being checked (REQ-007 W16: one maps
 * layout_id -> panel_id -> slot_id, the other layout_id -> slot_id -> panel_id, but both are the
 * same nested-string-record shape at this layer). Per-layout/per-panel/per-slot *validity*
 * against the loaded layouts is the caller's job (`useWorkbenchLayouts`), same as before the W16
 * delta. */
function isNestedStringRecord(value: unknown): boolean {
  if (typeof value !== 'object' || value === null) return false
  return Object.values(value as Record<string, unknown>).every(
    (perLayout) =>
      typeof perLayout === 'object' &&
      perLayout !== null &&
      Object.values(perLayout as Record<string, unknown>).every(
        (entry) => typeof entry === 'string',
      ),
  )
}

function isStoredWorkbenchState(
  value: unknown,
  schemaVersion: number,
): value is StoredWorkbenchState {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  if (record.schema_version !== schemaVersion) return false
  if (record.active_layout !== undefined && typeof record.active_layout !== 'string') {
    return false
  }
  if (record.panel_assignments !== undefined && !isNestedStringRecord(record.panel_assignments)) {
    return false
  }
  if (
    record.slot_visible_panel !== undefined &&
    !isNestedStringRecord(record.slot_visible_panel)
  ) {
    return false
  }
  if (
    record.active_notes_file !== undefined &&
    record.active_notes_file !== null &&
    typeof record.active_notes_file !== 'string'
  ) {
    return false
  }
  if (record.html_viewer_tabs !== undefined) {
    if (typeof record.html_viewer_tabs !== 'object' || record.html_viewer_tabs === null) {
      return false
    }
    const viewerTabs = record.html_viewer_tabs as Record<string, unknown>
    if (!Array.isArray(viewerTabs.tabs) || !viewerTabs.tabs.every(isStoredHtmlViewerTab)) {
      return false
    }
    if (typeof viewerTabs.active_tab_id !== 'number') return false
  }
  return true
}

function isStoredHtmlViewerTab(value: unknown): value is StoredHtmlViewerTab {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return (
    typeof record.id === 'number' &&
    (record.directory === null || typeof record.directory === 'string') &&
    typeof record.search_text === 'string' &&
    (record.selected_file === null || typeof record.selected_file === 'string')
  )
}

/**
 * Reads the stored workbench state written against `schemaVersion`, or `null` on anything short
 * of a well-formed match — a missing key, a parse failure, a shape mismatch, or (implicitly, via
 * the versioned key) a schema-version mismatch. ADR-016 rule 3: "discarded silently in favor of
 * the layout file's defaults — never an error, never a migration attempt." Per-layout/per-slot/
 * per-panel validity against the *loaded* layouts is the caller's job (`useWorkbenchLayouts`),
 * since this module has no layout data to check against.
 */
export function loadStoredState(schemaVersion: number): StoredWorkbenchState | null {
  let raw: string | null
  try {
    raw = window.localStorage.getItem(storageKey(schemaVersion))
  } catch {
    return null
  }
  if (!raw) return null
  try {
    const parsed: unknown = JSON.parse(raw)
    return isStoredWorkbenchState(parsed, schemaVersion) ? parsed : null
  } catch {
    return null
  }
}

/** Best-effort write — persistence is never a hard requirement for the page to keep working
 * (private browsing, a full quota, or a disabled store all fail silently). */
export function saveStoredState(state: StoredWorkbenchState): void {
  try {
    window.localStorage.setItem(storageKey(state.schema_version), JSON.stringify(state))
  } catch {
    // Best-effort, as above.
  }
}

/**
 * Merge-on-write: reads whatever is currently stored under `schemaVersion` (falling back to an
 * empty object, not the caller's own stale copy), overlays `patch`, and writes the result back.
 * This is how two independent owners of the one ADR-016-mandated key — the layout engine
 * (`useWorkbenchLayouts`, fields `active_layout`/`panel_assignments`/`slot_visible_panel`) and
 * the notes strip
 * (`NotesStripRegion`, field `active_notes_file`) — each persist their own field without
 * clobbering the other's, since every write re-reads from localStorage immediately beforehand
 * rather than reconstructing the whole object from one owner's in-memory state.
 */
export function patchStoredState(
  schemaVersion: number,
  patch: Partial<Omit<StoredWorkbenchState, 'schema_version'>>,
): void {
  const existing = loadStoredState(schemaVersion) ?? { schema_version: schemaVersion }
  saveStoredState({ ...existing, ...patch, schema_version: schemaVersion })
}

/** The notes strip's persisted file choice, or `null` when nothing valid is stored — the
 * strip falls back to its own default filename in that case (ADR-016 rule 4). */
export function loadActiveNotesFile(schemaVersion: number): string | null {
  return loadStoredState(schemaVersion)?.active_notes_file ?? null
}

/** Persists the notes strip's chosen file, merging into whatever else is stored under this key
 * (see `patchStoredState`) — never overwriting the layout engine's own stored fields. */
export function saveActiveNotesFile(schemaVersion: number, fileName: string | null): void {
  patchStoredState(schemaVersion, { active_notes_file: fileName })
}

/** The HTML Viewer's persisted tabs and active tab id (REQ-007 W08), or `null` when nothing
 * valid is stored — the viewer falls back to a single fresh tab in that case (ADR-016 rule 4). */
export function loadHtmlViewerTabs(
  schemaVersion: number,
): { tabs: StoredHtmlViewerTab[]; active_tab_id: number } | null {
  return loadStoredState(schemaVersion)?.html_viewer_tabs ?? null
}

/** Persists the HTML Viewer's open tabs and which one is active, merging into whatever else is
 * stored under this key (see `patchStoredState`) — never overwriting the layout engine's or the
 * notes strip's own stored fields. */
export function saveHtmlViewerTabs(
  schemaVersion: number,
  tabs: StoredHtmlViewerTab[],
  activeTabId: number,
): void {
  patchStoredState(schemaVersion, { html_viewer_tabs: { tabs, active_tab_id: activeTabId } })
}
