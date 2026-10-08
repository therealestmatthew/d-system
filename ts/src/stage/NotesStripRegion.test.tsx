import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import NotesStripRegion from './NotesStripRegion'

// REQ-012 R12 (a long entry scrolls and pauses), R13 (rotation never interrupts a scroll) and R14
// (image entries, the sizing rule, and the mixing ruling), through the component: the entry model
// and the variant selection are not exported, so these load a notes file and read what renders.
//
// jsdom does no layout, so the measurements the variant selection reads are stood in for by
// `measure`, keyed on the `data-notes-part` each measured element carries; `animate` is stubbed
// because jsdom has none, and the stub records what the ticker asks of it.

interface FakeAnimation {
  playState: 'running' | 'paused' | 'finished'
  pause: ReturnType<typeof vi.fn>
  play: ReturnType<typeof vi.fn>
  cancel: ReturnType<typeof vi.fn>
  addEventListener: (type: string, listener: () => void) => void
  removeEventListener: (type: string, listener: () => void) => void
  finish: () => void
  keyframes: Keyframe[]
  options: KeyframeAnimationOptions
}

const measure = { boxWidth: 400, boxHeight: 18, wrappedHeight: 18, lineWidth: 400 }
const animations: FakeAnimation[] = []

function partOf(element: Element): string | null {
  return element.getAttribute('data-notes-part')
}

function defineMeasure(
  property: 'clientWidth' | 'clientHeight' | 'offsetHeight' | 'offsetWidth',
  read: (part: string | null) => number,
) {
  Object.defineProperty(HTMLElement.prototype, property, {
    configurable: true,
    get(this: HTMLElement) {
      return read(partOf(this))
    },
  })
}

function installLayoutDoubles() {
  defineMeasure('clientWidth', (part) => (part === 'entry' ? measure.boxWidth : 0))
  defineMeasure('clientHeight', (part) => (part === 'entry' ? measure.boxHeight : 0))
  defineMeasure('offsetHeight', (part) => (part === 'measurer' ? measure.wrappedHeight : 0))
  defineMeasure('offsetWidth', (part) => (part === 'track' ? measure.lineWidth : 0))
  Object.defineProperty(HTMLElement.prototype, 'animate', {
    configurable: true,
    writable: true,
    value: (keyframes: Keyframe[], options: KeyframeAnimationOptions) => {
      const listeners = new Set<() => void>()
      const animation: FakeAnimation = {
        playState: 'running',
        pause: vi.fn(() => {
          animation.playState = 'paused'
        }),
        play: vi.fn(() => {
          animation.playState = 'running'
        }),
        cancel: vi.fn(),
        addEventListener: (_type, listener) => listeners.add(listener),
        removeEventListener: (_type, listener) => listeners.delete(listener),
        finish: () => {
          animation.playState = 'finished'
          listeners.forEach((listener) => listener())
        },
        keyframes,
        options,
      }
      animations.push(animation)
      return animation
    },
  })
}

function removeLayoutDoubles() {
  for (const property of ['clientWidth', 'clientHeight', 'offsetHeight', 'offsetWidth', 'animate']) {
    delete (HTMLElement.prototype as unknown as Record<string, unknown>)[property]
  }
}

interface Served {
  notes: unknown
  images?: unknown
  imagesStatus?: number
}

// A fetch that serves the notes file at the default name, the listing route, and the probe.
function serve({ notes, images = [], imagesStatus = 200 }: Served) {
  const requested: string[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      requested.push(url)
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      if (url.includes('terminal-enabled')) return json({ terminal_enabled: true })
      if (url.includes('/workbench/list?path=ts%2Fpublic') || url.includes('path=ts/public')) {
        return json([{ name: 'talking-points.json', path: 'ts/public/talking-points.json', is_dir: false }])
      }
      if (url.includes('/workbench/list')) return json(images, imagesStatus)
      if (url.endsWith('/talking-points.json')) return json(notes)
      return json({}, 404)
    }),
  )
  return requested
}

// The animations still running: a notice shown while the file loads may have scrolled and been
// cancelled by the time the entry replaces it.
const live = () => animations.filter((animation) => animation.cancel.mock.calls.length === 0)

const entryBox = () => document.querySelector('[data-notes-part="entry"]') as HTMLElement
const track = () => document.querySelector('[data-notes-part="track"]') as HTMLElement | null

async function renderStrip(served: Served) {
  const requested = serve(served)
  render(<NotesStripRegion />)
  await waitFor(() => expect(screen.queryByText('Loading notes…')).toBeNull())
  return requested
}

beforeEach(() => {
  animations.length = 0
  Object.assign(measure, { boxWidth: 400, boxHeight: 18, wrappedHeight: 18, lineWidth: 400 })
  installLayoutDoubles()
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
  removeLayoutDoubles()
})

describe('text entries: plain or scrolling (R12)', () => {
  it('shows an entry that fits as it is, with nothing moving', async () => {
    await renderStrip({ notes: { points: ['A short note.'] } })
    expect(entryBox().getAttribute('data-notes-variant')).toBe('plain')
    expect(entryBox().textContent).toContain('A short note.')
    expect(track()).toBeNull()
    expect(live()).toHaveLength(0)
  })

  it('scrolls an entry too tall for the strip as one line, right to left', async () => {
    measure.wrappedHeight = 72
    measure.lineWidth = 1000
    await renderStrip({ notes: { points: ['First line\nSecond line'] } })
    expect(entryBox().getAttribute('data-notes-variant')).toBe('ticker')
    expect(track()?.textContent).toBe('First line  ·  Second line')
    expect(live()).toHaveLength(1)
    const [animation] = live()
    const transforms = animation.keyframes.map((frame) => frame.transform)
    // Holds at the start, travels line width less box width (600 px) to the left, holds at the end.
    expect(transforms).toEqual([
      'translateX(0)',
      'translateX(0)',
      'translateX(-600px)',
      'translateX(-600px)',
    ])
    expect(animation.options.iterations).toBe(Infinity)
  })

  it('does not animate a long entry whose one line fits the box', async () => {
    measure.wrappedHeight = 72
    measure.lineWidth = 300
    await renderStrip({ notes: { points: ['A\nB'] } })
    expect(entryBox().getAttribute('data-notes-variant')).toBe('ticker')
    expect(live()).toHaveLength(0)
  })
})

describe('pausing a scrolling entry (R12)', () => {
  async function scrolling() {
    measure.wrappedHeight = 72
    measure.lineWidth = 1000
    await renderStrip({ notes: { points: ['A long entry'] } })
    return live()[0]
  }

  it('pauses while the pointer is over the entry and resumes when it leaves', async () => {
    const animation = await scrolling()
    fireEvent.pointerEnter(entryBox())
    expect(animation.pause).toHaveBeenCalledTimes(1)
    fireEvent.pointerLeave(entryBox())
    expect(animation.play).toHaveBeenCalledTimes(1)
  })

  it('pauses while the entry has keyboard focus and resumes on blur', async () => {
    const animation = await scrolling()
    expect(entryBox().getAttribute('tabindex')).toBe('0')
    fireEvent.focus(entryBox())
    expect(animation.pause).toHaveBeenCalledTimes(1)
    fireEvent.blur(entryBox())
    expect(animation.play).toHaveBeenCalledTimes(1)
  })

  it('stays paused while either the pointer or focus remains', async () => {
    const animation = await scrolling()
    fireEvent.pointerEnter(entryBox())
    fireEvent.focus(entryBox())
    fireEvent.pointerLeave(entryBox())
    expect(animation.play).not.toHaveBeenCalled()
    fireEvent.blur(entryBox())
    expect(animation.play).toHaveBeenCalledTimes(1)
  })

  it('makes a plain entry no tab stop', async () => {
    await renderStrip({ notes: { points: ['Short.'] } })
    expect(entryBox().getAttribute('tabindex')).toBeNull()
  })
})

describe('image entries (R14)', () => {
  const listing = [
    { name: 'b-chart.png', path: '_public/pics/b-chart.png', is_dir: false },
    { name: 'sub', path: '_public/pics/sub', is_dir: true },
    { name: 'a_logo.svg', path: '_public/pics/a_logo.svg', is_dir: false },
  ]

  it('lists the named directory, keeps files only, and orders them by name', async () => {
    const requested = await renderStrip({
      notes: { imageDirectory: '_public/pics' },
      images: listing,
    })
    const listUrl = requested.find((url) => url.includes('path=_public%2Fpics'))
    expect(listUrl).toBeDefined()
    for (const ext of ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']) {
      expect(listUrl).toContain(`ext=${encodeURIComponent(ext)}`)
    }
    const image = entryBox().querySelector('img')
    expect(image?.getAttribute('src')).toBe('/workbench-file/_public/pics/a_logo.svg')
    expect(image?.getAttribute('alt')).toBe('a logo')
    expect(entryBox().getAttribute('data-notes-variant')).toBe('image')
  })

  it('sizes the image to the entry box without cropping or overflow', async () => {
    await renderStrip({ notes: { imageDirectory: '_public/pics' }, images: listing })
    const image = entryBox().querySelector('img') as HTMLImageElement
    expect(image.style.objectFit).toBe('contain')
    expect(image.style.width).toBe('100%')
    expect(image.style.height).toBe('100%')
    expect(entryBox().style.overflow).toBe('hidden')
  })

  it('rotates through the images with Next, as it does through text', async () => {
    await renderStrip({ notes: { imageDirectory: '_public/pics' }, images: listing })
    fireEvent.click(screen.getByRole('button', { name: '▾' }))
    expect(screen.getByText('1 / 2')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(entryBox().querySelector('img')?.getAttribute('src')).toBe(
      '/workbench-file/_public/pics/b-chart.png',
    )
    expect(screen.getByText('2 / 2')).toBeTruthy()
  })

  it('names a directory that holds no images', async () => {
    await renderStrip({ notes: { imageDirectory: '_public/empty' }, images: [] })
    expect(entryBox().textContent).toContain('No images in _public/empty.')
  })

  it('names a directory the listing route cannot serve', async () => {
    await renderStrip({
      notes: { imageDirectory: '_public/nowhere' },
      images: { detail: 'Not a directory' },
      imagesStatus: 404,
    })
    expect(entryBox().textContent).toContain('Image directory not available: _public/nowhere.')
  })

  it('falls back to the image name when the file does not load', async () => {
    await renderStrip({ notes: { imageDirectory: '_public/pics' }, images: listing })
    fireEvent.error(entryBox().querySelector('img') as HTMLImageElement)
    expect(entryBox().textContent).toBe('Image unavailable: a logo')
  })
})

describe('the mixing ruling (R14)', () => {
  it('rejects a file that lists text and names an image directory', async () => {
    const requested = await renderStrip({
      notes: { points: ['A note'], imageDirectory: '_public/pics' },
      images: [{ name: 'a.png', path: '_public/pics/a.png', is_dir: false }],
    })
    expect(entryBox().textContent).toContain('one rotation shows only one kind')
    expect(entryBox().querySelector('img')).toBeNull()
    // Rejected before the directory is read, so nothing was half-loaded.
    expect(requested.some((url) => url.includes('path=_public%2Fpics'))).toBe(false)
  })

  it('still rejects an empty or malformed file with the original message', async () => {
    await renderStrip({ notes: { points: [] } })
    expect(entryBox().textContent).toContain('Could not load "talking-points.json" as a notes file.')
    cleanup()
    await renderStrip({ notes: { points: [1, 2] } })
    expect(entryBox().textContent).toContain('Could not load "talking-points.json" as a notes file.')
  })
})

describe('rotating between entries never interrupts a scroll (R13)', () => {
  async function startAutoAdvance() {
    measure.wrappedHeight = 72
    measure.lineWidth = 1000
    await renderStrip({ notes: { points: ['A long entry', 'Next'] } })
    fireEvent.click(screen.getByRole('button', { name: '▾' }))
    vi.useFakeTimers()
    fireEvent.click(screen.getByRole('button', { name: /Auto-advance/ }))
    return live()[0]
  }

  it('scrolls once, not repeatedly, while the timed advance is on', async () => {
    const animation = await startAutoAdvance()
    // The animation is restarted for the changed rule: the one in force plays a single pass.
    expect(animation.options.iterations).toBe(1)
  })

  it('does not rotate when the interval ends mid-scroll, only once the pass finishes', async () => {
    const animation = await startAutoAdvance()
    act(() => {
      vi.advanceTimersByTime(7000)
    })
    expect(entryBox().textContent).toContain('A long entry')
    act(() => animation.finish())
    expect(entryBox().textContent).toContain('Next')
  })

  it('does not rotate a finished entry while it is held, only after release', async () => {
    const animation = await startAutoAdvance()
    fireEvent.pointerEnter(entryBox())
    act(() => animation.finish())
    act(() => {
      vi.advanceTimersByTime(7000)
    })
    expect(entryBox().textContent).toContain('A long entry')
    fireEvent.pointerLeave(entryBox())
    expect(entryBox().textContent).toContain('Next')
  })

  it('does not rotate before the interval, even when the pass has finished', async () => {
    const animation = await startAutoAdvance()
    act(() => animation.finish())
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(entryBox().textContent).toContain('A long entry')
    act(() => {
      vi.advanceTimersByTime(1500)
    })
    expect(entryBox().textContent).toContain('Next')
  })

  it('lets the dropdown move to the next entry at once, mid-scroll', async () => {
    await startAutoAdvance()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(entryBox().textContent).toContain('Next')
  })

  it('rotates a plain entry on the interval alone', async () => {
    await renderStrip({ notes: { points: ['One', 'Two'] } })
    fireEvent.click(screen.getByRole('button', { name: '▾' }))
    vi.useFakeTimers()
    fireEvent.click(screen.getByRole('button', { name: /Auto-advance/ }))
    act(() => {
      vi.advanceTimersByTime(6000)
    })
    expect(entryBox().textContent).toContain('Two')
  })
})
