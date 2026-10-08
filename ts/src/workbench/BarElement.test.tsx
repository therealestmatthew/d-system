import { useRef, useState, type ReactNode } from 'react'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import BarElement, { type BarElementType } from './BarElement'
import { SlotFrameContext, type SlotFrameBinding } from './slotFrameContext'
import { PANEL_REGISTRY } from './panelRegistry'
import { panelElements, slotSchemas, slotsEligibleFor } from './slotEligibility'
import { guardedPanel } from '../stage/guardedPanel'

// ADR-031 decision 1: a panel never draws a top bar. It wraps each control in a `BarElement`, which
// places the children into the matching sub-slot of whichever slot currently holds the panel.

function makeTargets(ids: string[]) {
  const targets: Record<string, HTMLElement> = {}
  for (const id of ids) {
    const element = document.createElement('div')
    element.dataset.subSlot = id
    document.body.appendChild(element)
    targets[id] = element
  }
  return targets
}

function bindingFor(role: string, targets: Record<string, HTMLElement>): SlotFrameBinding {
  return {
    role,
    frame: slotSchemas.frames[slotSchemas.roles[role].frame],
    subSlotElement: (id) => targets[id] ?? null,
  }
}

let created: HTMLElement[] = []
function track(targets: Record<string, HTMLElement>) {
  created.push(...Object.values(targets))
  return targets
}

beforeEach(() => {
  created = []
})
afterEach(() => {
  cleanup()
  for (const element of created) element.remove()
  vi.unstubAllGlobals()
})

describe('BarElement', () => {
  it('draws its children in place when no slot hosts the panel', () => {
    render(
      <BarElement type="action">
        <button type="button">Refresh</button>
      </BarElement>,
    )
    const marker = screen.getByRole('button', { name: 'Refresh' }).parentElement
    expect(marker?.getAttribute('data-bar-element')).toBe('action')
  })

  it('places each element in the sub-slot of the hosting frame that admits its type', () => {
    const targets = track(makeTargets(['help', 'controls']))
    render(
      <SlotFrameContext.Provider value={bindingFor('primary', targets)}>
        <BarElement type="help">
          <span>about</span>
        </BarElement>
        <BarElement type="toggle">
          <button type="button">mode</button>
        </BarElement>
      </SlotFrameContext.Provider>,
    )
    expect(targets.help.textContent).toBe('about')
    expect(targets.controls.querySelector('button')?.textContent).toBe('mode')
  })

  it('renders nothing until the slot has mounted the sub-slot, then draws there', () => {
    const targets = track(makeTargets(['help', 'controls']))
    const late: Record<string, HTMLElement> = {}
    const binding: SlotFrameBinding = {
      ...bindingFor('primary', targets),
      subSlotElement: (id) => late[id] ?? null,
    }
    const { rerender } = render(
      <SlotFrameContext.Provider value={binding}>
        <BarElement type="action">
          <button type="button">go</button>
        </BarElement>
      </SlotFrameContext.Provider>,
    )
    expect(screen.queryByRole('button', { name: 'go' })).toBeNull()
    late.controls = targets.controls
    rerender(
      <SlotFrameContext.Provider value={{ ...binding }}>
        <BarElement type="action">
          <button type="button">go</button>
        </BarElement>
      </SlotFrameContext.Provider>,
    )
    expect(targets.controls.querySelector('button')?.textContent).toBe('go')
  })

  it('throws, caught by the panel error boundary, for a type the slot has no place for', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    // A frame whose bar offers only `controls`: a `help` element has nowhere to go.
    const targets = track(makeTargets(['controls']))
    const binding = bindingFor('primary', targets)
    const controlsOnly: SlotFrameBinding = {
      ...binding,
      frame: {
        arrangement: 'stacked',
        children: [
          {
            id: 'top_bar',
            children: [
              {
                id: 'controls',
                filled_by: 'panel',
                holds: 'bar',
                admits: ['action'],
                capacity: 1,
              },
            ],
          },
        ],
      },
    }
    function PanelWithHelp() {
      return (
        <BarElement type="help">
          <span>about</span>
        </BarElement>
      )
    }
    render(
      <SlotFrameContext.Provider value={controlsOnly}>
        {guardedPanel('notes-strip', PanelWithHelp)}
      </SlotFrameContext.Provider>,
    )
    const alert = screen.getByRole('alert')
    expect(alert.textContent).toContain('Notes stopped working')
    expect(alert.textContent).toContain('no place for a help element')
    expect(targets.controls.textContent).toBe('')
  })

  it('follows the panel to another slot without remounting the panel or losing its state', async () => {
    const first = track(makeTargets(['help', 'controls']))
    const second = track(makeTargets(['help', 'controls']))
    let mounts = 0
    function Counter() {
      const [count, setCount] = useState(0)
      const mounted = useRef(false)
      if (!mounted.current) {
        mounted.current = true
        mounts += 1
      }
      return (
        <BarElement type="action">
          <button type="button" onClick={() => setCount((value) => value + 1)}>
            count {count}
          </button>
        </BarElement>
      )
    }
    function Harness({ children }: { children: (binding: SlotFrameBinding) => ReactNode }) {
      const [slot, setSlot] = useState<'first' | 'second'>('first')
      const binding = bindingFor('primary', slot === 'first' ? first : second)
      return (
        <>
          <button type="button" onClick={() => setSlot('second')}>
            move
          </button>
          {children(binding)}
        </>
      )
    }
    render(
      <Harness>
        {(binding) => (
          <SlotFrameContext.Provider value={binding}>
            <Counter />
          </SlotFrameContext.Provider>
        )}
      </Harness>,
    )
    const press = () =>
      act(() => {
        const button = first.controls.querySelector('button') ?? second.controls.querySelector('button')
        button?.click()
      })
    press()
    expect(first.controls.textContent).toBe('count 1')
    act(() => screen.getByRole('button', { name: 'move' }).click())
    await waitFor(() => expect(second.controls.textContent).toBe('count 1'))
    expect(first.controls.textContent).toBe('')
    expect(mounts).toBe(1)
  })
})

// A panel's declared element configuration is what the matcher reads, so the bar elements the
// component really renders must be drawn from it (ADR-031 decision 4: "an element configuration can
// drift from what its component renders"). Elements that depend on state (the terminal menu only
// renders once the terminal is enabled) may be absent here, so the check is that a component never
// renders MORE of a type than it declares. Fewer is harmless; more would overrun a frame's capacity
// that the matcher believed was free.
describe('declared bar elements', () => {
  function stubBackend() {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes('/demo/stage/terminal-enabled')) {
          return new Response(JSON.stringify({ terminal_enabled: false }), { status: 200 })
        }
        return new Response(null, { status: 404 })
      }),
    )
  }

  it.each(Object.keys(PANEL_REGISTRY))('%s renders no more bar elements than it declares', async (panelId) => {
    stubBackend()
    window.localStorage.clear()
    const role = slotsEligibleFor(panelId, Object.keys(slotSchemas.roles))[0]
    const targets = track(makeTargets(['help', 'controls']))
    const Component = PANEL_REGISTRY[panelId].Component!
    render(
      <SlotFrameContext.Provider value={bindingFor(role, targets)}>
        <Component />
      </SlotFrameContext.Provider>,
    )
    // Let the panel's mount-time fetches settle so conditional elements have appeared.
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })
    const rendered: Record<string, number> = {}
    for (const element of Object.values(targets).flatMap((target) => [
      ...target.querySelectorAll('[data-bar-element]'),
    ])) {
      const type = element.getAttribute('data-bar-element') as BarElementType
      rendered[type] = (rendered[type] ?? 0) + Number(element.getAttribute('data-bar-places'))
    }
    const declared: Record<string, number> = {}
    for (const type of panelElements[panelId].bar) declared[type] = (declared[type] ?? 0) + 1
    for (const [type, count] of Object.entries(rendered)) {
      expect(count, `${panelId} renders ${count} ${type} element(s)`).toBeLessThanOrEqual(
        declared[type] ?? 0,
      )
    }
    expect(Object.keys(rendered).length, `${panelId} rendered no bar elements`).toBeGreaterThan(0)
  })
})
