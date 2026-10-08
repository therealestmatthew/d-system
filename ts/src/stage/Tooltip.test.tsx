import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Tooltip from './Tooltip'

// Placement and collapse of the hover tooltip (idea 000130, REQ-012 R27, REQ-006 R03). jsdom has
// no layout, so the trigger's box and the bubble's size are mocked; the decision under test is
// where the component puts the bubble given them.

const VW = 1280
const VH = 720

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

function mockGeometry(trigger: { top: number; bottom: number; left: number }, bubble = { w: 240, h: 113 }) {
  vi.spyOn(window, 'innerWidth', 'get').mockReturnValue(VW)
  vi.spyOn(window, 'innerHeight', 'get').mockReturnValue(VH)
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (
    this: HTMLElement,
  ) {
    const isTrigger = this.classList.contains('stage-tooltip__trigger')
    const top = isTrigger ? trigger.top : 0
    const bottom = isTrigger ? trigger.bottom : 0
    const left = isTrigger ? trigger.left : 0
    return {
      top,
      bottom,
      left,
      right: left + 18,
      width: 18,
      height: bottom - top,
      x: left,
      y: top,
    } as DOMRect
  })
  vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(bubble.h)
  vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockReturnValue(bubble.w)
}

function renderTooltip() {
  render(
    <section className="stage-region" style={{ overflow: 'hidden' }}>
      <Tooltip label="About the strip">Help text</Tooltip>
    </section>,
  )
  return screen.getByRole('button', { name: 'About the strip' })
}

describe('Tooltip placement', () => {
  it('renders the bubble in document.body, outside the clipping region', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    const trigger = renderTooltip()
    fireEvent.mouseEnter(trigger)
    const bubble = screen.getByRole('tooltip')
    expect(bubble.parentElement).toBe(document.body)
    expect(bubble.closest('.stage-region')).toBeNull()
  })

  it('opens below a trigger near the top of the viewport (the notes strip, idea 000130)', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    fireEvent.mouseEnter(renderTooltip())
    const bubble = screen.getByRole('tooltip')
    expect(bubble.style.top).toBe('111px')
    expect(bubble.style.bottom).toBe('')
    expect(bubble.style.left).toBe('754px')
    expect(parseFloat(bubble.style.maxHeight)).toBeGreaterThanOrEqual(113)
  })

  it('opens above a trigger near the bottom of the viewport when the text fits there', () => {
    mockGeometry({ top: 640, bottom: 658, left: 400 })
    fireEvent.mouseEnter(renderTooltip())
    const bubble = screen.getByRole('tooltip')
    expect(bubble.style.bottom).toBe(`${VH - 640 + 8}px`)
    expect(bubble.style.top).toBe('')
  })

  it('shifts the bubble left so its right edge stays inside the viewport', () => {
    mockGeometry({ top: 85, bottom: 103, left: 1250 })
    fireEvent.mouseEnter(renderTooltip())
    expect(screen.getByRole('tooltip').style.left).toBe(`${VW - 8 - 240}px`)
  })

  it('keeps the bubble off the left edge', () => {
    mockGeometry({ top: 85, bottom: 103, left: 2 })
    fireEvent.mouseEnter(renderTooltip())
    expect(screen.getByRole('tooltip').style.left).toBe('8px')
  })

  it('limits the height to the room on the chosen side when the text is taller than the room', () => {
    mockGeometry({ top: 300, bottom: 318, left: 400 }, { w: 240, h: 900 })
    fireEvent.mouseEnter(renderTooltip())
    const bubble = screen.getByRole('tooltip')
    const room = bubble.style.top ? VH - 318 - 16 : 300 - 16
    expect(parseFloat(bubble.style.maxHeight)).toBeLessThanOrEqual(room)
    expect(parseFloat(bubble.style.maxHeight)).toBeLessThanOrEqual(0.6 * VH)
  })

  it('places the bubble again when the window resizes while it is open', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    fireEvent.mouseEnter(renderTooltip())
    vi.spyOn(window, 'innerWidth', 'get').mockReturnValue(600)
    fireEvent(window, new Event('resize'))
    expect(screen.getByRole('tooltip').style.left).toBe(`${600 - 8 - 240}px`)
  })
})

describe('Tooltip hover collapse (REQ-006 R03)', () => {
  it('is closed until the pointer enters the trigger', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    renderTooltip()
    expect(screen.queryByRole('tooltip')).toBeNull()
  })

  it('opens on pointer enter and collapses on pointer leave', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    const trigger = renderTooltip()
    fireEvent.mouseEnter(trigger)
    expect(screen.getByRole('tooltip').textContent).toBe('Help text')
    expect(trigger.getAttribute('aria-expanded')).toBe('true')
    fireEvent.mouseLeave(trigger.parentElement as HTMLElement)
    expect(screen.queryByRole('tooltip')).toBeNull()
    expect(trigger.getAttribute('aria-expanded')).toBe('false')
  })

  it('stays open while the pointer is over the portaled bubble, then collapses on leaving it', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    const trigger = renderTooltip()
    const wrapper = trigger.parentElement as HTMLElement
    fireEvent.mouseEnter(wrapper)
    const bubble = screen.getByRole('tooltip')
    // React sees the bubble as inside the wrapper, so moving onto it is not a leave.
    fireEvent.mouseOut(trigger, { relatedTarget: bubble })
    fireEvent.mouseOver(bubble, { relatedTarget: trigger })
    expect(screen.getByRole('tooltip')).toBeTruthy()
    fireEvent.mouseOut(bubble, { relatedTarget: document.body })
    expect(screen.queryByRole('tooltip')).toBeNull()
  })

  it('opens on keyboard focus and collapses on blur', () => {
    mockGeometry({ top: 85, bottom: 103, left: 754 })
    const trigger = renderTooltip()
    fireEvent.focus(trigger)
    expect(screen.getByRole('tooltip')).toBeTruthy()
    fireEvent.blur(trigger)
    expect(screen.queryByRole('tooltip')).toBeNull()
  })
})
