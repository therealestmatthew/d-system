import type { StoredWorkbenchState } from './types'

// ADR-016 rule 3: "a single namespaced key carrying the schema_version of the layouts it was
// written against." The version lives in the key itself (not just the stored value) so a layout
// schema bump needs no migration code — the old key is simply never read again, and every reader
// falls straight through to the layout files' own defaults, matching rule 4 ("the repository
// defaults are the fallback state").
const STORAGE_KEY_PREFIX = 'd-system:workbench-state'

function storageKey(schemaVersion: number): string {
  return `${STORAGE_KEY_PREFIX}:v${schemaVersion}`
}

function isStoredWorkbenchState(
  value: unknown,
  schemaVersion: number,
): value is StoredWorkbenchState {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  if (record.schema_version !== schemaVersion) return false
  if (typeof record.active_layout !== 'string') return false
  if (typeof record.slot_selections !== 'object' || record.slot_selections === null) return false
  return Object.values(record.slot_selections as Record<string, unknown>).every(
    (perLayout) =>
      typeof perLayout === 'object' &&
      perLayout !== null &&
      Object.values(perLayout as Record<string, unknown>).every(
        (panelId) => typeof panelId === 'string',
      ),
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
