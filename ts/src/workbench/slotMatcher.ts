/**
 * Structural eligibility: may a panel type occupy a slot role? (ADR-031 decision 4, REQ-011 R12).
 *
 * The authority is data: `_data/workbench/panel-elements.json` (each panel type's element
 * configuration) and `_data/workbench/slot-schemas.json` (each role's frame). Nothing here lists
 * which panels a slot admits. A panel type is eligible for a role when, and only when:
 *
 * 1. the role's body admits the panel's body kind; and
 * 2. every element in the panel's `bar` list can be routed to a panel-filled bar sub-slot of the
 *    role's frame that admits its type, taking sub-slots in declaration order and respecting each
 *    sub-slot's capacity; and
 * 3. every required sub-slot is satisfied (the body is required, and the panel always supplies it).
 *
 * The panel type's id, the slot id and the layout are not inputs. These functions take the schemas
 * as arguments so a test can pass synthetic ones; `slotEligibility.ts` binds them to the shipped
 * data files.
 *
 * This is one half of a documented pair. The other half is `src/workbench/slot_matcher.py`, which
 * the Python gate runs. They are written separately on purpose (ADR-031 decision 4);
 * `slotMatcher.test.tsx` and `test/test_workbench_slot_matcher.py` both read
 * `_data/workbench/matcher-cases.json` and fail if either side disagrees with it. Change the rule
 * in both files together.
 */

/** One sub-slot of a frame. Slot-filled sub-slots (`identity`, `frame_actions`) carry nothing a
 * panel supplies; a panel-filled bar sub-slot admits bar element types up to a capacity; the body
 * sub-slot holds the panel's content. */
export interface FrameLeaf {
  id: string
  filled_by: 'slot' | 'panel'
  holds?: 'bar' | 'body'
  admits?: string[]
  capacity?: number
  required?: boolean
}

/** A group of leaves (the top bar). A group contains leaves only: the tree is frame, group, leaf
 * (ADR-031 decision 3). */
export interface FrameGroup {
  id: string
  children: FrameLeaf[]
}

export interface Frame {
  arrangement: 'stacked' | 'inline'
  children: (FrameGroup | FrameLeaf)[]
}

export interface RoleSchema {
  frame: string
  body: string[]
}

export interface SlotSchemas {
  schema_version: number
  element_types: { bar: Record<string, string>; body: Record<string, string> }
  frames: Record<string, Frame>
  roles: Record<string, RoleSchema>
}

/** A panel type's element configuration: the body kind its content is, and the bar elements it
 * supplies, one entry per place each takes in the top bar. */
export interface PanelElements {
  body: string
  bar: string[]
}

/** A panel-filled bar sub-slot, in the shape routing needs. */
export interface BarLeaf {
  id: string
  admits: string[]
  capacity: number
}

function isGroup(node: FrameGroup | FrameLeaf): node is FrameGroup {
  return 'children' in node
}

/** Every sub-slot of a frame in declaration order, the group's leaves flattened in place. */
export function frameLeaves(frame: Frame): FrameLeaf[] {
  return frame.children.flatMap((node) => (isGroup(node) ? node.children : [node]))
}

/** The panel-filled bar sub-slots of a frame, in declaration order. */
export function barLeaves(frame: Frame): BarLeaf[] {
  return frameLeaves(frame).flatMap((leaf) =>
    leaf.filled_by === 'panel' && leaf.holds === 'bar'
      ? [{ id: leaf.id, admits: leaf.admits ?? [], capacity: leaf.capacity ?? 0 }]
      : [],
  )
}

/** The sub-slot id each bar element lands in, or `null` when some element has no place. Elements
 * are taken in order; each goes to the first sub-slot that admits its type and still has room. */
export function routeBar(bar: string[], leaves: BarLeaf[]): string[] | null {
  const used = new Map(leaves.map((leaf) => [leaf.id, 0]))
  const routes: string[] = []
  for (const elementType of bar) {
    const leaf = leaves.find(
      (candidate) =>
        candidate.admits.includes(elementType) && (used.get(candidate.id) ?? 0) < candidate.capacity,
    )
    if (!leaf) return null
    used.set(leaf.id, (used.get(leaf.id) ?? 0) + 1)
    routes.push(leaf.id)
  }
  return routes
}

/** The frame a role is drawn with, or `null` when the schema file has no such role. */
export function frameForRole(role: string, schemas: SlotSchemas): Frame | null {
  const roleSchema = schemas.roles[role]
  return roleSchema ? (schemas.frames[roleSchema.frame] ?? null) : null
}

/** True when a panel with this element configuration may occupy `role`. */
export function isEligible(elements: PanelElements, role: string, schemas: SlotSchemas): boolean {
  const roleSchema = schemas.roles[role]
  if (!roleSchema) return false
  if (!roleSchema.body.includes(elements.body)) return false
  const frame = schemas.frames[roleSchema.frame]
  if (!frame) return false
  return routeBar(elements.bar, barLeaves(frame)) !== null
}

/** The bar sub-slot an element of `type` is drawn into in this frame: the first panel-filled
 * sub-slot, in declaration order, that admits the type. `null` when the frame has no place for it
 * (rendering such an element is an error, ADR-031 decision 1). */
export function subSlotFor(frame: Frame, type: string): string | null {
  return barLeaves(frame).find((leaf) => leaf.admits.includes(type))?.id ?? null
}

/** True when the frame has an `identity` sub-slot, which carries the panel switcher. A role
 * without one can hold one panel. */
export function frameHasIdentity(frame: Frame): boolean {
  return frameLeaves(frame).some((leaf) => leaf.id === 'identity')
}
