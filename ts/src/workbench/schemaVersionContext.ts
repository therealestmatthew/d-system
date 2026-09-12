import { createContext, useContext } from 'react'

/**
 * The active layout `schema_version` (ADR-016 rule 3's "single namespaced key"), shared by every
 * consumer that reads or writes it. ADR-016 tracks exactly one version number, resolved once from
 * the fetched layout files by `useWorkbenchLayouts` — never a hardcoded constant duplicated per
 * consumer. `StagePage` provides the resolved value here; any panel that persists a selection
 * under the ADR-016 key (today: `NotesStripRegion`'s chosen file) reads it via
 * `useActiveSchemaVersion` instead of importing its own copy, so a data-only `schema_version`
 * bump in `_data/workbench/layouts/*.json` moves every consumer to the new storage key together.
 */
const ActiveSchemaVersionContext = createContext<number | null>(null)

export const ActiveSchemaVersionProvider = ActiveSchemaVersionContext.Provider

/**
 * The active schema version, or `null` before the layout files have loaded. Every panel that
 * needs it renders only once `StagePage` has reached `loadState === 'loaded'` (see `Slot.tsx`),
 * so in practice a mounted panel always sees a number here — `null` is handled defensively only.
 */
export function useActiveSchemaVersion(): number | null {
  return useContext(ActiveSchemaVersionContext)
}
