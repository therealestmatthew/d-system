import { useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import './StagePage.css'
import Slot from '../workbench/Slot'
import LayoutConfigDialog from '../workbench/LayoutConfigDialog'
import { useWorkbenchLayouts } from '../workbench/useWorkbenchLayouts'
import { ActiveSchemaVersionProvider } from '../workbench/schemaVersionContext'
import { PANEL_REGISTRY } from '../workbench/panelRegistry'

/**
 * The stage page: the workbench layout engine's root (REQ-007 W05/W06/W16/W17, ADR-016). Loads
 * the shipped layout files (`_data/workbench/layouts/`), renders the active layout's slots on a
 * CSS grid built from that layout's own fractional/grid geometry, and offers a top-right
 * layout-configuration surface to switch layouts and reassign panels to slots.
 *
 * Zero page scrolling and no overlapping regions (REQ-006 R02) hold for both shipped layouts at
 * every required window size because every grid track is wrapped in `minmax(0, ...)` and every
 * slot/panel keeps `min-height: 0`/`overflow: hidden` down its whole box chain, exactly as the
 * pre-engine static grid did — only the geometry's *source* changed (data file, not a CSS rule).
 *
 * REQ-007 W17 item 4: this is also the host that keeps a panel's component instance — and so a
 * live shell session — alive across a reassignment to a different slot (never just a layout
 * switch). Two element maps do that work together:
 *
 *  - `slotBodies`: slot_id -> that slot's body container, populated by each `Slot`'s
 *    `registerBody` callback once its container div mounts. Never cleared on a layout switch: both
 *    shipped layouts share the same four slot ids, so every `Slot` instance — and so every entry
 *    here — lives for the whole session once first mounted. That is also what let idea `000107`'s
 *    layout 1->2->1 round-trip defect close once the two layout files' own
 *    `default_visible_panel.terminal` entries agreed, with no engine change.
 *  - `panelHosts`: panel_id -> a plain `<div>` created once for that panel type and *never
 *    replaced*. Each visible panel's component is portaled into its own host, and the host is what
 *    moves between slot bodies (a DOM `appendChild`, in the layout effect below) when the panel is
 *    reassigned.
 *
 * That second map is the whole fix, and it is worth stating why the obvious alternative cannot
 * work. This file previously portaled each panel straight into its *slot's* container, keyed by
 * panel id, on the assumption that "same key, new container" makes React relocate the mounted
 * subtree. React does the opposite, unconditionally, by design: `updatePortal` in the reconciler
 * (`react-dom`, `ReactChildFiber`) treats a portal whose `containerInfo` differs from the current
 * fiber's as an *insert* — a brand-new fiber, with the old one deleted — never an update. So every
 * reassignment tore the panel down and rebuilt it, which ran `TerminalRegion`'s effect cleanup and
 * closed its websocket: the silent kill REQ-007 W16 forbids, wired directly into the mechanism
 * meant to prevent it. No amount of state batching in `setPanelSlot` could have changed that,
 * because the unmount is a property of the portal's container changing at all.
 *
 * With a stable per-panel host, a reassignment changes no React element: the portal's container is
 * the same object before and after, so the component is not re-rendered, let alone remounted, and
 * the browser reparents the already-mounted DOM subtree when the layout effect appends the host to
 * its new slot body. Moving a DOM node preserves it and everything inside it — the xterm.js
 * instance, its scrollback and its open websocket all survive, because none of them is recreated.
 * Each host carries `display: contents`, so it generates no box of its own and the panel's
 * `.stage-region` remains, for layout purposes, the direct flex child of the slot body it would
 * have been without the wrapper (no CSS rule needed for the host itself).
 *
 * Ordering matters and is handled by `attachedHosts`: a panel's portal renders only once its host
 * is actually attached inside a slot body in the document, so a panel never mounts into a detached
 * container (xterm.js measures its container on `open()`). The cost is one extra render the first
 * time a given panel becomes visible; the benefit is that on a *reassignment* nothing about the
 * portal changes at all, since the host is already attached — the gate is on attachment, not on
 * which slot the host is attached to.
 *
 * Only the visible panel of each slot is portaled. A hidden panel stays unmounted, which is
 * deliberate: mounting hidden shell panels would open websockets and consume the backend's six
 * global session slots (ADR-014 section 4) for panels nobody is looking at.
 *
 * Also the sole provider of the ADR-016 schema version (`ActiveSchemaVersionProvider`, fed by
 * `useWorkbenchLayouts`'s own resolution of it): every panel that persists a selection under the
 * ADR-016 storage key — the notes strip included — reads it from here rather than a hardcoded
 * constant of its own, so a data-only `schema_version` bump moves every consumer together.
 */
export default function StagePage() {
  const {
    loadState,
    layouts,
    schemaVersion,
    activeLayout,
    setActiveLayoutId,
    getSlotPanel,
    setSlotPanel,
    setPanelSlot,
  } = useWorkbenchLayouts()

  // slot_id -> that slot's registered body container (REQ-007 W17 item 4, see file doc above).
  // Never cleared on a layout switch: both shipped layouts share the same four slot ids, so every
  // `Slot` instance — and so every entry here — lives for the whole session once first mounted.
  const [slotBodies, setSlotBodies] = useState<Record<string, HTMLDivElement | null>>({})

  // Fix for the review-blocker "Maximum update depth exceeded" crash: `registerSlotBody` used to
  // be a factory called inline in the JSX below (`registerBody={registerSlotBody(slot.slot_id)}`),
  // which allocates a brand-new closure every render. A ref prop whose identity changes every
  // commit makes React detach the old ref (call it with `null`) and attach the new one (call it
  // with the mounted element) on every single render — and since the detach call always saw
  // `previous[slotId]` go from a real element to `null`, the old `previous[slotId] === element`
  // guard never caught it, so every render produced a state update, which produced another
  // render: a self-sustaining loop the instant the four slots' body containers first mounted.
  //
  // The fix has two parts, both required:
  //  1. One stable callback per slot id, held in a ref-backed map rather than recreated inline, so
  //     the ref prop React sees for a given slot never changes identity across renders — no more
  //     spurious detach/attach pairs from *this* cause.
  //  2. That stable callback ignores `null` (detach) calls entirely rather than writing them into
  //     state, so a slot's entry here only ever moves from one real element to another. `Slot.tsx`
  //     now returns one uniform root shape for all of its 0/1/>1 cases, so a slot body should
  //     never be torn down and rebuilt in the first place; this guard is the belt to that braces,
  //     and it costs nothing, because a slot that genuinely unmounted would be a slot no longer on
  //     screen to portal into anyway. What it does *not* have to protect anymore is the moved
  //     panel: with a stable per-panel host (see the file doc), a slot body briefly going missing
  //     no longer removes any panel's portal from the tree — the portal's container is the panel's
  //     own host, not the slot's.
  const slotBodyCallbacks = useRef<Record<string, (element: HTMLDivElement | null) => void>>({})

  function getRegisterSlotBody(slotId: string): (element: HTMLDivElement | null) => void {
    const existing = slotBodyCallbacks.current[slotId]
    if (existing) return existing
    const callback = (element: HTMLDivElement | null) => {
      if (!element) return // transient detach during a structural remount — ignore, see above.
      setSlotBodies((previous) =>
        previous[slotId] === element ? previous : { ...previous, [slotId]: element },
      )
    }
    slotBodyCallbacks.current[slotId] = callback
    return callback
  }

  // panel_id -> that panel's own host element (see the file doc): created once, never replaced,
  // moved between slot bodies by the layout effect below. A ref, not state — its identity is
  // exactly the thing that must never change across a render.
  const panelHosts = useRef<Map<string, HTMLDivElement>>(new Map())
  // panel_id -> true once that panel's host is attached inside a slot body in the document. The
  // gate that stops a panel mounting into a detached host; see the file doc.
  const [attachedHosts, setAttachedHosts] = useState<Record<string, boolean>>({})

  // This render's visible panel per slot, resolved once by `useWorkbenchLayouts`'s single resolver
  // and reused by both consumers below (the `Slot` chrome and the panel portals) so the header and
  // the mounted panel can never disagree about what this slot is showing.
  const visiblePanelBySlotId: Record<string, string | null> = {}
  // panel_id -> the slot whose body its host belongs in this render. Only visible, implemented
  // panels appear here; a slot showing nothing contributes no entry.
  const hostSlotByPanelId: Record<string, string> = {}
  if (activeLayout) {
    for (const slot of activeLayout.slots) {
      const panelId = getSlotPanel(activeLayout, slot)
      visiblePanelBySlotId[slot.slot_id] = panelId
      if (panelId && PANEL_REGISTRY[panelId]?.Component) hostSlotByPanelId[panelId] = slot.slot_id
    }
  }

  // Attaches each visible panel's host to its slot's body, moving it there if it is currently
  // somewhere else, and detaches the hosts of panels that are no longer visible anywhere. A
  // *layout* effect, so the DOM move happens before the browser paints — a reassignment never
  // shows the panel in its old slot for a frame. Runs on every commit (no dependency array): its
  // inputs are two plain objects rebuilt each render, and it only ever writes state when something
  // genuinely changed, so it cannot loop.
  useLayoutEffect(() => {
    let changed = false
    const nextAttached = { ...attachedHosts }

    for (const [panelId, slotId] of Object.entries(hostSlotByPanelId)) {
      const body = slotBodies[slotId]
      if (!body) continue // that slot's container has not registered yet — next commit will.
      let host = panelHosts.current.get(panelId)
      if (!host) {
        host = document.createElement('div')
        host.dataset.panelHost = panelId
        // No box of its own: the panel's own `.stage-region` stays the slot body's flex child.
        host.style.display = 'contents'
        panelHosts.current.set(panelId, host)
      }
      // The reassignment itself: a DOM move, invisible to React, so nothing unmounts.
      if (host.parentElement !== body) body.appendChild(host)
      if (!nextAttached[panelId]) {
        nextAttached[panelId] = true
        changed = true
      }
    }

    for (const panelId of Object.keys(nextAttached)) {
      if (hostSlotByPanelId[panelId]) continue
      // No longer visible anywhere: React has already unmounted its portal children this commit,
      // so the host is empty — take the empty div back out of the slot body.
      panelHosts.current.get(panelId)?.remove()
      delete nextAttached[panelId]
      changed = true
    }

    if (changed) setAttachedHosts(nextAttached)
  })

  // One portal per visible panel, into that panel's own host. `panelId` is both the React key and
  // the host's identity, and neither changes when the panel moves slots — that is what makes a
  // reassignment a no-op for React and a plain DOM reparent for the browser.
  const panelPortals = Object.keys(hostSlotByPanelId).flatMap((panelId) => {
    if (!attachedHosts[panelId]) return []
    const host = panelHosts.current.get(panelId)
    const Component = PANEL_REGISTRY[panelId]?.Component
    if (!host || !Component) return []
    return [createPortal(<Component />, host, panelId)]
  })

  return (
    <ActiveSchemaVersionProvider value={schemaVersion}>
      <div className="stage-page">
        <header className="stage-page__header">
          <h1>D-System Live Demo Stage</h1>
          <div className="stage-page__layout-controls">
            {loadState === 'loaded' && layouts.length > 0 ? (
              <LayoutConfigDialog
                layouts={layouts}
                activeLayout={activeLayout}
                onSelectLayout={setActiveLayoutId}
                onAssignPanelSlot={setPanelSlot}
                // REQ-007 W16: what the dialog needs to tell the presenter, before applying a
                // move, which panel that move would close — the same resolved answer the slot
                // chrome and the portals use, never a second guess at it.
                visiblePanelInSlot={(slotId) => visiblePanelBySlotId[slotId] ?? null}
              />
            ) : null}
          </div>
        </header>
        {loadState === 'loading' ? (
          <main className="stage-page__grid">
            <p className="stage-placeholder-text">Loading workbench layouts…</p>
          </main>
        ) : loadState === 'error' || !activeLayout ? (
          <main className="stage-page__grid">
            <p className="stage-placeholder-text stage-placeholder-text--absent">
              Could not load the workbench layout files from{' '}
              <code>_data/workbench/layouts/</code>.
            </p>
          </main>
        ) : (
          <>
            <main
              className="stage-page__grid"
              style={{
                gridTemplateColumns: activeLayout.grid.columns
                  .map((track) => `minmax(0, ${track})`)
                  .join(' '),
                gridTemplateRows: activeLayout.grid.rows
                  .map((track) => `minmax(0, ${track})`)
                  .join(' '),
                gridTemplateAreas: activeLayout.grid.areas.map((row) => `"${row}"`).join(' '),
              }}
            >
              {activeLayout.slots.map((slot) => (
                <div
                  key={slot.slot_id}
                  className="stage-workbench-slot"
                  style={{ gridArea: slot.slot_id }}
                >
                  <Slot
                    slot={slot}
                    visiblePanelId={visiblePanelBySlotId[slot.slot_id] ?? null}
                    onSelectPanel={(panelId) =>
                      setSlotPanel(activeLayout.layout_id, slot.slot_id, panelId)
                    }
                    registerBody={getRegisterSlotBody(slot.slot_id)}
                  />
                </div>
              ))}
            </main>
            {panelPortals}
          </>
        )}
      </div>
    </ActiveSchemaVersionProvider>
  )
}
