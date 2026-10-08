import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  callOpenFiles,
  deliverBatch,
  isBatchAvailable,
  useBatchAvailable,
  terminalBridge,
  useViewerBridge,
  useViewerBridges,
  viewerBridge,
  type BatchCall,
  type BatchReceipt,
  type TerminalBridgeHandle,
  type ViewerBridgeHandle,
} from './panelBridge'

// ADR-029 section 6: the bridge holds several keyed handles and delivers an ordered list of paths
// to one or more targets. REQ-012 R07: N paths in, every one of N in delivered or declined.
// REQ-012 R08: no target registered means the action disables rather than raising, and registered
// targets still receive the list when others are absent. Stub handles stand in for the panels.

function viewerStub(openFiles?: (paths: string[]) => BatchReceipt): ViewerBridgeHandle {
  return { tabs: [], openInTab: () => undefined, openFiles }
}

function terminalStub(): TerminalBridgeHandle {
  return { enabled: true, dropped: false, injectPath: () => undefined }
}

const acceptAll = (paths: string[]): BatchReceipt => ({ delivered: [...paths], declined: [] })

// Not a handle's own batch method: the terminal has none yet, so its call returns the receipt of a
// stub kept here.
const terminalCall: BatchCall<TerminalBridgeHandle> = (_handle, paths) => acceptAll(paths)

const registered: Array<() => void> = []
function register(handle: ViewerBridgeHandle, key?: string): void {
  viewerBridge.register(handle, key)
  registered.push(() => viewerBridge.unregister(handle))
}

afterEach(() => {
  registered.splice(0).forEach((undo) => undo())
})

describe('keyed multi-handle channel', () => {
  it('keeps the single-handle behavior for callers that pass no key', () => {
    const first = viewerStub()
    const second = viewerStub()
    expect(viewerBridge.get()).toBeNull()
    register(first)
    register(second)
    // Same default key: the second replaces the first, as before.
    expect(viewerBridge.get()).toBe(second)
    expect(viewerBridge.getAll()).toEqual([second])
    viewerBridge.unregister(second)
    expect(viewerBridge.get()).toBeNull()
  })

  it('leaves a handle under another key alone and returns the most recent from get()', () => {
    const a = viewerStub()
    const b = viewerStub()
    register(a, 'a')
    register(b, 'b')
    expect(viewerBridge.get()).toBe(b)
    expect(viewerBridge.getAll()).toEqual([a, b])
  })

  it('replacing the handle under a key makes it the most recent', () => {
    const a = viewerStub()
    const b = viewerStub()
    const a2 = viewerStub()
    register(a, 'a')
    register(b, 'b')
    register(a2, 'a')
    expect(viewerBridge.getAll()).toEqual([b, a2])
    expect(viewerBridge.get()).toBe(a2)
  })

  it('falls back to the previous remaining handle when the most recent one unregisters', () => {
    const a = viewerStub()
    const b = viewerStub()
    register(a, 'a')
    register(b, 'b')
    viewerBridge.unregister(b)
    expect(viewerBridge.get()).toBe(a)
    viewerBridge.unregister(a)
    expect(viewerBridge.get()).toBeNull()
  })

  it('finds the entry to unregister by handle identity across keys', () => {
    const a = viewerStub()
    const b = viewerStub()
    register(a, 'a')
    register(b, 'b')
    viewerBridge.unregister(a)
    expect(viewerBridge.getAll()).toEqual([b])
  })

  it('ignores the belated cleanup of a superseded handle', () => {
    const old = viewerStub()
    const next = viewerStub()
    register(old, 'k')
    register(next, 'k')
    viewerBridge.unregister(old)
    expect(viewerBridge.get()).toBe(next)
  })

  it('returns the same getAll() array until a register or unregister replaces it', () => {
    const a = viewerStub()
    register(a, 'a')
    const snapshot = viewerBridge.getAll()
    expect(viewerBridge.getAll()).toBe(snapshot)
    viewerBridge.unregister(viewerStub())
    expect(viewerBridge.getAll()).toBe(snapshot)
    const b = viewerStub()
    register(b, 'b')
    expect(viewerBridge.getAll()).not.toBe(snapshot)
    expect(snapshot).toEqual([a])
  })

  it('notifies subscribers on register and unregister', () => {
    const listener = vi.fn()
    const unsubscribe = viewerBridge.subscribe(listener)
    const a = viewerStub()
    register(a)
    viewerBridge.unregister(a)
    unsubscribe()
    register(viewerStub())
    expect(listener).toHaveBeenCalledTimes(2)
  })
})

describe('hooks over the channel', () => {
  it('useViewerBridge keeps reading the current handle, or null', () => {
    const { result } = renderHook(() => useViewerBridge())
    expect(result.current).toBeNull()
    const a = viewerStub()
    act(() => register(a, 'a'))
    expect(result.current).toBe(a)
  })

  it('useViewerBridges reads null when empty and a stable array otherwise', () => {
    const { result, rerender } = renderHook(() => useViewerBridges())
    expect(result.current).toBeNull()
    const a = viewerStub()
    act(() => register(a, 'a'))
    expect(result.current).toEqual([a])
    const before = result.current
    rerender()
    expect(result.current).toBe(before)
    act(() => viewerBridge.unregister(a))
    expect(result.current).toBeNull()
  })
})

describe('deliverBatch: every requested path is accounted for (R07)', () => {
  const paths = ['a.html', 'b.md', 'c.txt', 'd.html', 'e.html', 'f.html']

  it('delivers all N to one registered target', () => {
    const openFiles = vi.fn(acceptAll)
    register(viewerStub(openFiles))
    const outcome = deliverBatch(paths, [{ channel: viewerBridge, call: callOpenFiles }])
    expect(openFiles).toHaveBeenCalledTimes(1)
    expect(openFiles).toHaveBeenCalledWith(paths)
    expect(outcome.requested).toEqual(paths)
    expect(outcome.targets).toHaveLength(1)
    expect(outcome.targets[0]).toMatchObject({ channel: 'html-viewer', key: 'html-viewer', absent: false })
    expect(outcome.targets[0].receipt).toEqual({ delivered: paths, declined: [] })
  })

  it('accounts for every path when the target declines some, with the reason it gave', () => {
    register(
      viewerStub((requested) => ({
        delivered: requested.slice(0, 3),
        declined: [
          { path: 'd.html', reason: 'capacity' },
          { path: 'e.html', reason: 'capacity' },
          { path: 'f.html', reason: 'incompatible' },
        ],
      })),
    )
    const { targets } = deliverBatch(paths, [{ channel: viewerBridge, call: callOpenFiles }])
    const receipt = targets[0].receipt!
    expect(receipt.delivered).toEqual(['a.html', 'b.md', 'c.txt'])
    expect(receipt.declined).toEqual([
      { path: 'd.html', reason: 'capacity' },
      { path: 'e.html', reason: 'capacity' },
      { path: 'f.html', reason: 'incompatible' },
    ])
    expect(receipt.delivered.length + receipt.declined.length).toBe(paths.length)
  })

  it('declines as failed a path the target left out of its receipt', () => {
    register(viewerStub(() => ({ delivered: ['a.html'], declined: [] })))
    const { targets } = deliverBatch(['a.html', 'b.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(targets[0].receipt).toEqual({
      delivered: ['a.html'],
      declined: [{ path: 'b.html', reason: 'failed' }],
    })
  })

  it('puts a path the target reported as both delivered and declined in declined, once', () => {
    register(
      viewerStub(() => ({
        delivered: ['a.html', 'b.html'],
        declined: [{ path: 'a.html', reason: 'capacity' }],
      })),
    )
    const { targets } = deliverBatch(['a.html', 'b.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(targets[0].receipt).toEqual({
      delivered: ['b.html'],
      declined: [{ path: 'a.html', reason: 'failed' }],
    })
  })

  it('drops paths the target reports that were never requested', () => {
    register(viewerStub(() => ({ delivered: ['a.html', 'stray.html'], declined: [] })))
    const { targets } = deliverBatch(['a.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(targets[0].receipt).toEqual({ delivered: ['a.html'], declined: [] })
  })

  it('declines every path as failed when the receipt is malformed', () => {
    register(viewerStub())
    const call: BatchCall<ViewerBridgeHandle> = () => ({ delivered: 'nope' }) as unknown as BatchReceipt
    const { targets } = deliverBatch(['a.html', 'b.html'], [{ channel: viewerBridge, call }])
    expect(targets[0].receipt).toEqual({
      delivered: [],
      declined: [
        { path: 'a.html', reason: 'failed' },
        { path: 'b.html', reason: 'failed' },
      ],
    })
  })

  it('handles an empty list', () => {
    register(viewerStub(acceptAll))
    const { requested, targets } = deliverBatch([], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(requested).toEqual([])
    expect(targets[0].receipt).toEqual({ delivered: [], declined: [] })
  })

  it('declines every path as failed when the handle has no batch method, without throwing', () => {
    register(viewerStub())
    const { targets } = deliverBatch(['a.html', 'b.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(targets[0].absent).toBe(false)
    expect(targets[0].error).toMatch(/no batch method/)
    expect(targets[0].receipt?.delivered).toEqual([])
    expect(targets[0].receipt?.declined.map((d) => d.reason)).toEqual(['failed', 'failed'])
  })

  it('collapses a duplicated path so requested, the call and the receipt agree', () => {
    const openFiles = vi.fn(acceptAll)
    register(viewerStub(openFiles))
    const outcome = deliverBatch(['a', 'a', 'b'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(openFiles).toHaveBeenCalledWith(['a', 'b'])
    expect(outcome.requested).toEqual(['a', 'b'])
    expect(outcome.targets[0].receipt).toEqual({ delivered: ['a', 'b'], declined: [] })
  })

  it('records a thrown value with no string form instead of throwing', () => {
    const throwers: unknown[] = [
      Object.create(null),
      {
        toString() {
          throw new Error('no string for you')
        },
      },
    ]
    for (const thrown of throwers) {
      register(
        viewerStub(() => {
          throw thrown
        }),
      )
      const terminal = terminalStub()
      terminalBridge.register(terminal)
      registered.push(() => terminalBridge.unregister(terminal))
      let outcome: ReturnType<typeof deliverBatch> | undefined
      expect(() => {
        outcome = deliverBatch(['a.html'], [
          { channel: viewerBridge, call: callOpenFiles },
          { channel: terminalBridge, call: terminalCall },
        ])
      }).not.toThrow()
      expect(outcome!.targets[0].error).toBe('target threw a non-printable value')
      expect(outcome!.targets[0].receipt).toEqual({
        delivered: [],
        declined: [{ path: 'a.html', reason: 'failed' }],
      })
      // The other target still received the list.
      expect(outcome!.targets[1].receipt).toEqual({ delivered: ['a.html'], declined: [] })
      registered.splice(0).forEach((undo) => undo())
    }
  })

  it('declines every path as failed and records the error when the target throws', () => {
    register(
      viewerStub(() => {
        throw new Error('viewer exploded')
      }),
    )
    const outcome = deliverBatch(['a.html', 'b.html'], [{ channel: viewerBridge, call: callOpenFiles }])
    expect(outcome.targets[0].error).toBe('viewer exploded')
    expect(outcome.targets[0].receipt).toEqual({
      delivered: [],
      declined: [
        { path: 'a.html', reason: 'failed' },
        { path: 'b.html', reason: 'failed' },
      ],
    })
  })

  it('addresses a handle by key and gives each listed target the full ordered list', () => {
    const first = vi.fn(acceptAll)
    const second = vi.fn(acceptAll)
    register(viewerStub(first), 'one')
    register(viewerStub(second), 'two')
    const outcome = deliverBatch(paths, [
      { channel: viewerBridge, call: callOpenFiles, key: 'one' },
      { channel: viewerBridge, call: callOpenFiles, key: 'two' },
    ])
    expect(first).toHaveBeenCalledWith(paths)
    expect(second).toHaveBeenCalledWith(paths)
    expect(outcome.targets.map((t) => t.key)).toEqual(['one', 'two'])
  })

  it('does not fan out: an unkeyed target reaches only the current handle', () => {
    const older = vi.fn(acceptAll)
    const newer = vi.fn(acceptAll)
    register(viewerStub(older), 'one')
    register(viewerStub(newer), 'two')
    const outcome = deliverBatch(paths, [{ channel: viewerBridge, call: callOpenFiles }])
    expect(older).not.toHaveBeenCalled()
    expect(newer).toHaveBeenCalledTimes(1)
    expect(outcome.targets[0].key).toBe('two')
  })
})

describe('deliverBatch: absent and partial targets (R08)', () => {
  const paths = ['a.html', 'b.html', 'c.html']

  it('reports every target absent, delivers nothing and does not throw when none is registered', () => {
    let outcome: ReturnType<typeof deliverBatch> | undefined
    expect(() => {
      outcome = deliverBatch(paths, [
        { channel: viewerBridge, call: callOpenFiles },
        { channel: terminalBridge, call: terminalCall },
      ])
    }).not.toThrow()
    expect(outcome!.requested).toEqual(paths)
    expect(outcome!.targets).toEqual([
      { channel: 'html-viewer', key: 'html-viewer', absent: true },
      { channel: 'terminal', key: 'terminal', absent: true },
    ])
  })

  it('reports an absent key even when the channel has another handle', () => {
    const openFiles = vi.fn(acceptAll)
    register(viewerStub(openFiles), 'one')
    const outcome = deliverBatch(paths, [{ channel: viewerBridge, call: callOpenFiles, key: 'two' }])
    expect(outcome.targets).toEqual([{ channel: 'html-viewer', key: 'two', absent: true }])
    expect(openFiles).not.toHaveBeenCalled()
  })

  it('returns an empty target list for an empty target list', () => {
    expect(deliverBatch(paths, [])).toEqual({ requested: paths, targets: [] })
  })

  it('delivers to the registered target and names the absent one (best effort per target)', () => {
    const openFiles = vi.fn(acceptAll)
    register(viewerStub(openFiles))
    const outcome = deliverBatch(paths, [
      { channel: viewerBridge, call: callOpenFiles },
      { channel: terminalBridge, call: terminalCall },
    ])
    expect(openFiles).toHaveBeenCalledWith(paths)
    expect(outcome.targets[0].receipt).toEqual({ delivered: paths, declined: [] })
    expect(outcome.targets[1]).toEqual({ channel: 'terminal', key: 'terminal', absent: true })
  })

  it('a throwing target does not stop the other targets', () => {
    const terminal = terminalStub()
    terminalBridge.register(terminal)
    registered.push(() => terminalBridge.unregister(terminal))
    register(
      viewerStub(() => {
        throw new Error('boom')
      }),
    )
    const outcome = deliverBatch(paths, [
      { channel: viewerBridge, call: callOpenFiles },
      { channel: terminalBridge, call: terminalCall },
    ])
    expect(outcome.targets[0].error).toBe('boom')
    expect(outcome.targets[1].receipt).toEqual({ delivered: paths, declined: [] })
  })

  it('queues nothing: a target that registers after a batch receives nothing', () => {
    deliverBatch(paths, [{ channel: viewerBridge, call: callOpenFiles }])
    const openFiles = vi.fn(acceptAll)
    register(viewerStub(openFiles))
    expect(openFiles).not.toHaveBeenCalled()
  })

  it('the action is available when at least one listed target is registered, and not otherwise', () => {
    const targets = [
      { channel: viewerBridge, call: callOpenFiles },
      { channel: terminalBridge, call: terminalCall },
    ] as const
    expect(isBatchAvailable([...targets])).toBe(false)
    register(viewerStub(acceptAll))
    expect(isBatchAvailable([...targets])).toBe(true)
    expect(isBatchAvailable([{ channel: terminalBridge, call: terminalCall }])).toBe(false)
  })
})

describe('useBatchAvailable', () => {
  it('flips when a listed panel registers and unregisters', () => {
    const { result } = renderHook(() =>
      useBatchAvailable([
        { channel: viewerBridge, call: callOpenFiles },
        { channel: terminalBridge, call: terminalCall },
      ]),
    )
    expect(result.current).toBe(false)
    const viewer = viewerStub(acceptAll)
    act(() => register(viewer))
    expect(result.current).toBe(true)
    const terminal = terminalStub()
    act(() => terminalBridge.register(terminal))
    expect(result.current).toBe(true)
    act(() => viewerBridge.unregister(viewer))
    expect(result.current).toBe(true)
    act(() => terminalBridge.unregister(terminal))
    expect(result.current).toBe(false)
  })

  it('follows a keyed target only while that key is registered', () => {
    const { result } = renderHook(() =>
      useBatchAvailable([{ channel: viewerBridge, call: callOpenFiles, key: 'two' }]),
    )
    const one = viewerStub(acceptAll)
    act(() => register(one, 'one'))
    expect(result.current).toBe(false)
    act(() => register(viewerStub(acceptAll), 'two'))
    expect(result.current).toBe(true)
  })
})
