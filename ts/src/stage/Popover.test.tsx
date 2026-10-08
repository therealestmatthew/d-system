import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Popover, { choosePlacement } from './Popover'

// The side a popover opens toward and the height it may take (idea 000108, REQ-012 R25). The
// pure decision is tested directly; the component tests then confirm the decision reaches the
// bubble's inline style and that the dismiss control stays inside the viewport.

const VH = 720

describe('choosePlacement side choice', () => {
  it('opens downward when the room above is under the old 120 px threshold and below is large', () => {
    const placement = choosePlacement({ spaceAbove: 101, spaceBelow: 562, viewportHeight: VH })
    expect(placement.openUpward).toBe(false)
  })

  it('opens downward when the room above is over 120 px but far smaller than below (idea 000117)', () => {
    // The reproduced defect: 149 px above, 529 px below, content needing 305 px.
    const placement = choosePlacement({
      spaceAbove: 149,
      spaceBelow: 529,
      viewportHeight: VH,
      naturalHeight: 305,
    })
    expect(placement.openUpward).toBe(false)
    expect(placement.maxHeight).toBeGreaterThanOrEqual(305)
  })

  it('keeps the upward side when the whole content fits above', () => {
    const placement = choosePlacement({
      spaceAbove: 300,
      spaceBelow: 380,
      viewportHeight: VH,
      naturalHeight: 200,
    })
    expect(placement.openUpward).toBe(true)
  })

  it('uses the downward side when the content fits there but not above', () => {
    const placement = choosePlacement({
      spaceAbove: 250,
      spaceBelow: 300,
      viewportHeight: VH,
      naturalHeight: 280,
    })
    expect(placement.openUpward).toBe(false)
  })

  it('picks the larger side when the content fits on neither', () => {
    expect(
      choosePlacement({ spaceAbove: 320, spaceBelow: 200, viewportHeight: VH, naturalHeight: 900 })
        .openUpward,
    ).toBe(true)
    expect(
      choosePlacement({ spaceAbove: 200, spaceBelow: 320, viewportHeight: VH, naturalHeight: 900 })
        .openUpward,
    ).toBe(false)
  })

  it('picks the larger side when the natural height is unknown', () => {
    expect(choosePlacement({ spaceAbove: 100, spaceBelow: 400, viewportHeight: VH }).openUpward).toBe(
      false,
    )
    expect(
      choosePlacement({ spaceAbove: 400, spaceBelow: 100, viewportHeight: VH, naturalHeight: 0 })
        .openUpward,
    ).toBe(true)
  })
})

describe('choosePlacement height clamp', () => {
  it('takes the room on the chosen side up to 60% of the viewport', () => {
    expect(
      choosePlacement({ spaceAbove: 0, spaceBelow: 677, viewportHeight: VH, naturalHeight: 1900 })
        .maxHeight,
    ).toBe(0.6 * VH)
    expect(choosePlacement({ spaceAbove: 0, spaceBelow: 260, viewportHeight: VH }).maxHeight).toBe(260)
  })

  it('never returns more than the room on the chosen side, even under the old 120 px floor', () => {
    const placement = choosePlacement({ spaceAbove: 60, spaceBelow: 80, viewportHeight: VH })
    expect(placement.openUpward).toBe(false)
    expect(placement.maxHeight).toBe(80)
  })

  it('treats a negative room as no room rather than a negative height', () => {
    const placement = choosePlacement({ spaceAbove: -8, spaceBelow: -3, viewportHeight: VH })
    expect(placement.maxHeight).toBe(0)
  })
})

describe('Popover placement in the DOM', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  function mockGeometry(triggerTop: number, triggerBottom: number, naturalHeight: number) {
    vi.spyOn(window, 'innerHeight', 'get').mockReturnValue(VH)
    vi.spyOn(window, 'innerWidth', 'get').mockReturnValue(1280)
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (
      this: HTMLElement,
    ) {
      const isTrigger = this.classList.contains('stage-popover__trigger')
      const top = isTrigger ? triggerTop : 0
      const bottom = isTrigger ? triggerBottom : 0
      return { top, bottom, left: 400, right: 480, width: 80, height: bottom - top, x: 400, y: top } as DOMRect
    })
    vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(naturalHeight)
  }

  async function open() {
    await act(async () => {
      render(
        <Popover triggerLabel="Choose a file" title="Choose a file">
          <p>entries</p>
        </Popover>,
      )
    })
    fireEvent.click(screen.getByRole('button', { name: 'Choose a file' }))
    return screen.getByRole('dialog')
  }

  it('opens below the trigger with a bubble tall enough for its content when below has the room', async () => {
    mockGeometry(157, 187, 305)
    const bubble = await open()
    expect(bubble.style.top).toBe('195px')
    expect(bubble.style.bottom).toBe('')
    expect(parseFloat(bubble.style.maxHeight)).toBeGreaterThanOrEqual(305)
    expect(screen.getByRole('button', { name: 'Dismiss Choose a file' })).toBeTruthy()
  })

  it('opens above the trigger when the content fits there', async () => {
    mockGeometry(500, 530, 200)
    const bubble = await open()
    expect(bubble.style.bottom).toBe(`${VH - 500 + 8}px`)
    expect(bubble.style.top).toBe('')
  })

  it('keeps the whole bubble inside the viewport when it opens downward', async () => {
    mockGeometry(157, 187, 2000)
    const bubble = await open()
    const top = parseFloat(bubble.style.top)
    expect(top + parseFloat(bubble.style.maxHeight)).toBeLessThanOrEqual(VH - 8)
  })
})
