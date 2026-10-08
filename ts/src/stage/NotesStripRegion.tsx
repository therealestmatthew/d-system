import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import Tooltip from './Tooltip'
import BarElement from '../workbench/BarElement'
import Popover from './Popover'
import { useActiveSchemaVersion } from '../workbench/schemaVersionContext'
import { loadActiveNotesFile, saveActiveNotesFile } from '../workbench/storage'
import { fetchWorkbench } from './useTerminalEnabled'

// The fixed notes directory (REQ-007 W01) — repository-relative, passed to the workbench
// listing route below. Never walked directly by this component.
const NOTES_DIRECTORY = 'ts/public'
const NOTES_FILE_EXTENSION = '.json'
const NOTES_FILE_LIST_URL = `/api/v1/workbench/list?path=${NOTES_DIRECTORY}&ext=${NOTES_FILE_EXTENSION}`

// The notes strip's own fallback file, used when nothing valid has ever been persisted or the
// persisted choice's content no longer loads — the same file the previous talking-points panel
// defaulted to, and the one the backend's `demo_stage.py` route still names as its own default.
const DEFAULT_NOTES_FILENAME = 'talking-points.json'

// Auto-advance interval for the optional timed advance. Not configurable from the data file —
// the data file carries content only (REQ-006 R01), never behavior.
const AUTO_ADVANCE_INTERVAL_MS = 6000

// Horizontal scrolling of a long text entry (REQ-012 R12): the speed in pixels per second and the
// hold at each end, so the first and last words stay readable before the line moves or rotates.
const TICKER_SPEED_PX_PER_SECOND = 60
const TICKER_END_HOLD_MS = 1000

// Image entries (REQ-012 R14) come from a repository-relative directory the notes file names, read
// through the workbench listing route and served by Vite's `/workbench-file/` route — the same two
// pieces the HTML Viewer uses, so both need `D_SYSTEM_DEMO_TERMINAL=1` (ADR-015 rule 1).
const IMAGE_DIRECTORY_LIST_URL = '/api/v1/workbench/list'
const IMAGE_FILE_PREFIX = '/workbench-file/'
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']

type ContentLoadState = 'loading' | 'loaded' | 'missing' | 'error'
type FileListState = 'loading' | 'loaded' | 'error'

/**
 * One entry of the rotator: a union of the two kinds the strip can show.
 *
 * - `text` — a string from the notes file's `points`. Shown as it is when it fits the strip;
 *   otherwise as one line that scrolls right to left (the text variants, below).
 * - `image` — one file from the directory the notes file names in `imageDirectory`.
 *
 * Mixing ruling (REQ-012 R14; proposed, awaiting the owner's ratification, pre-approved run
 * 2026-10-08): one rotation shows text entries or image entries, never both. A notes file that
 * lists `points` and names an `imageDirectory` is rejected with a message, not half-shown. The
 * not-mixing answer is the safer one because it is the reversible one: allowing mixing later only
 * relaxes a check, while allowing it now and forbidding it later would orphan files authors had
 * already written. It also avoids a rule nobody has stated, which is where the directory's images
 * fall among the points.
 */
type NotesEntry =
  | { kind: 'text'; text: string }
  | { kind: 'image'; src: string; alt: string }

type NotesSource =
  | { kind: 'text'; entries: string[] }
  | { kind: 'images'; directory: string }

type ParsedNotes =
  | { ok: true; source: NotesSource }
  | { ok: false; reason: 'invalid' | 'empty' | 'mixed' }

interface NotesFileEntry {
  name: string
}

/** Reads the notes file's shape: `points` (text), or `imageDirectory` (images), never both. */
function parseNotesFile(value: unknown): ParsedNotes {
  if (typeof value !== 'object' || value === null) return { ok: false, reason: 'invalid' }
  const { points, imageDirectory } = value as { points?: unknown; imageDirectory?: unknown }
  const hasDirectory = imageDirectory !== undefined
  if (hasDirectory && (typeof imageDirectory !== 'string' || imageDirectory.trim() === '')) {
    return { ok: false, reason: 'invalid' }
  }
  const texts = points === undefined && hasDirectory ? [] : points
  if (!Array.isArray(texts) || !texts.every((point) => typeof point === 'string')) {
    return { ok: false, reason: 'invalid' }
  }
  if (hasDirectory) {
    return texts.length > 0
      ? { ok: false, reason: 'mixed' }
      : { ok: true, source: { kind: 'images', directory: (imageDirectory as string).trim() } }
  }
  return texts.length === 0
    ? { ok: false, reason: 'empty' }
    : { ok: true, source: { kind: 'text', entries: texts as string[] } }
}

function isNotesFile(value: unknown): boolean {
  return parseNotesFile(value).ok
}

/** The image entries of a directory listing: files only, by name, each served from the repository. */
function imageEntriesFromListing(listing: unknown): NotesEntry[] | null {
  if (
    !Array.isArray(listing) ||
    !listing.every(
      (item) =>
        typeof item === 'object' &&
        item !== null &&
        typeof (item as { name?: unknown }).name === 'string' &&
        typeof (item as { path?: unknown }).path === 'string',
    )
  ) {
    return null
  }
  return (listing as { name: string; path: string; is_dir?: boolean }[])
    .filter((item) => item.is_dir !== true)
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((item) => ({
      kind: 'image' as const,
      src: IMAGE_FILE_PREFIX + item.path.split('/').map(encodeURIComponent).join('/'),
      alt: item.name.replace(/\.[^.]+$/, '').replace(/[-_]+/g, ' '),
    }))
}

/** A long entry on one line: line breaks become a separator so nothing is lost by not wrapping. */
function asOneLine(text: string): string {
  return text
    .split(/\s*\n\s*/)
    .filter((line) => line !== '')
    .join('  ·  ')
}

function isNotesFileEntryList(value: unknown): value is NotesFileEntry[] {
  return (
    Array.isArray(value) &&
    value.every(
      (entry) =>
        typeof entry === 'object' &&
        entry !== null &&
        typeof (entry as { name?: unknown }).name === 'string',
    )
  )
}

// What the entry box keeps in every variant: it is stretched to the strip's row so its height is
// the strip's own (a box that grew with its content could never be measured as overflowing), and
// it clips whatever a variant does not move into view. `minHeight` keeps one line (or a small
// image) usable in a strip whose padded row is shorter than a line, as layout 1's is (REQ-037
// floors a region at 16 px). The stylesheet's rules still apply on top.
const ENTRY_BOX_STYLE = { alignSelf: 'stretch', overflow: 'hidden', minHeight: '1.4em' } as const

// The invisible copy of a text entry laid out wrapped, at the entry box's width. Its height says
// whether the plain variant fits, and its scroll width whether one unbroken word is wider than the
// box. It is a sibling of the entry box, not inside it, so the entry's own text is never doubled;
// `position: fixed` keeps it out of the row's layout and of every scrollable overflow. The entry
// box's font is copied onto it when it is measured.
const MEASURER_STYLE = {
  position: 'fixed',
  top: 0,
  left: 0,
  visibility: 'hidden',
  pointerEvents: 'none',
  whiteSpace: 'pre-line',
} as const

interface TextEntryViewProps {
  text: string
  // True when nothing will rotate the entry away (the timed advance is off, or there is no other
  // entry to rotate to): the scroll then repeats, not once.
  loop: boolean
  // The running scroll animation, or `null` when there is none. The rotation reads it to wait.
  onScroll: (animation: Animation | null) => void
  // True while the pointer is over the entry or it has keyboard focus. `resume` is false only for
  // the release that comes from the entry being removed.
  onHold: (held: boolean, resume?: boolean) => void
  // The scroll's single pass ended.
  onPassFinished: () => void
}

/**
 * A text entry (REQ-012 R12). Two variants, chosen by measuring:
 *
 * - plain — the text wrapped, as before, when that fits the entry box;
 * - ticker — otherwise one line that scrolls right to left. It holds at the start, moves until the
 *   line's end is in view, holds there, and (when `loop`) starts again. The motion is a transform
 *   animation, so the line is never clipped for a reader who waits, and the box never grows.
 *
 * Hovering over the entry, or focusing it from the keyboard, pauses the scroll; leaving it
 * resumes. With reduced motion requested nothing moves: the line sits in a box that scrolls
 * horizontally by hand.
 */
function TextEntryView({ text, loop, onScroll, onHold, onPassFinished }: TextEntryViewProps) {
  const boxRef = useRef<HTMLParagraphElement>(null)
  const measurerRef = useRef<HTMLSpanElement>(null)
  const trackRef = useRef<HTMLSpanElement>(null)
  const animationRef = useRef<Animation | null>(null)
  const holdRef = useRef({ hover: false, focus: false })
  const [variant, setVariant] = useState<'plain' | 'ticker'>('plain')
  // How far the line must travel for its end to be in view; 0 when it fits, so nothing moves.
  const [travel, setTravel] = useState(0)
  const [reducedMotion] = useState(
    () =>
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  )

  const measure = useCallback(() => {
    const box = boxRef.current
    const measurer = measurerRef.current
    if (box === null || measurer === null) return
    const style = window.getComputedStyle(box)
    const contentWidth =
      box.clientWidth - (parseFloat(style.paddingLeft) || 0) - (parseFloat(style.paddingRight) || 0)
    measurer.style.width = `${Math.max(contentWidth, 0)}px`
    measurer.style.font = style.font
    // Fits when the wrapped text is no taller than the box and no unbroken word is wider than it.
    if (measurer.offsetHeight <= box.clientHeight + 1 && measurer.scrollWidth <= contentWidth + 1) {
      setVariant('plain')
      setTravel(0)
      return
    }
    setVariant('ticker')
    const track = trackRef.current
    setTravel(track === null ? 0 : Math.max(0, Math.ceil(track.offsetWidth - contentWidth)))
  }, [])

  // Measured before paint, again when the variant changes (the line's width is only known once
  // it is on screen) and when the box is resized.
  useLayoutEffect(() => {
    measure()
    const box = boxRef.current
    if (box === null || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(measure)
    observer.observe(box)
    return () => observer.disconnect()
  }, [measure, text, variant])

  useEffect(() => {
    const track = trackRef.current
    if (
      variant !== 'ticker' ||
      travel <= 0 ||
      reducedMotion ||
      track === null ||
      typeof track.animate !== 'function'
    ) {
      return
    }
    const moveMs = (travel / TICKER_SPEED_PX_PER_SECOND) * 1000
    const totalMs = moveMs + 2 * TICKER_END_HOLD_MS
    const animation = track.animate(
      [
        { transform: 'translateX(0)', offset: 0 },
        { transform: 'translateX(0)', offset: TICKER_END_HOLD_MS / totalMs },
        { transform: `translateX(-${travel}px)`, offset: (TICKER_END_HOLD_MS + moveMs) / totalMs },
        { transform: `translateX(-${travel}px)`, offset: 1 },
      ],
      { duration: totalMs, iterations: loop ? Infinity : 1, fill: 'forwards', easing: 'linear' },
    )
    animationRef.current = animation
    if (holdRef.current.hover || holdRef.current.focus) animation.pause()
    animation.addEventListener('finish', onPassFinished)
    onScroll(animation)
    return () => {
      animation.removeEventListener('finish', onPassFinished)
      animation.cancel()
      animationRef.current = null
      onScroll(null)
    }
  }, [variant, travel, reducedMotion, loop, onScroll, onPassFinished])

  // An entry that goes away while held must not leave the rotation held. Releasing here must not
  // also advance: the entry is already going away (a manual Previous or Next, say), and a second
  // step on top of the reader's would skip an entry.
  useEffect(() => () => onHold(false, false), [onHold])

  const setHold = (part: 'hover' | 'focus', on: boolean) => {
    holdRef.current[part] = on
    const held = holdRef.current.hover || holdRef.current.focus
    const animation = animationRef.current
    if (animation !== null) {
      if (held && animation.playState === 'running') animation.pause()
      if (!held && animation.playState === 'paused') animation.play()
    }
    onHold(held)
  }

  const scrolls = variant === 'ticker' && travel > 0
  return (
    <>
      <p
        ref={boxRef}
        className="stage-notes-strip__current"
        data-notes-part="entry"
        data-notes-variant={variant}
        style={{
          ...ENTRY_BOX_STYLE,
          // Scrolled by hand, with the scrollbar hidden: a classic 15 px scrollbar would take the
          // height the line needs in a strip as short as layout 1's. Wheel, drag, touch and the
          // arrow keys (the entry is a tab stop) still move it.
          ...(reducedMotion && scrolls ? { overflowX: 'auto', scrollbarWidth: 'none' } : null),
        }}
        tabIndex={scrolls ? 0 : undefined}
        onPointerEnter={() => setHold('hover', true)}
        onPointerLeave={() => setHold('hover', false)}
        onFocus={() => setHold('focus', true)}
        onBlur={() => setHold('focus', false)}
      >
        {variant === 'plain' ? (
          text
        ) : (
          <span
            ref={trackRef}
            data-notes-part="track"
            style={{ display: 'inline-block', whiteSpace: 'nowrap' }}
          >
            {asOneLine(text)}
          </span>
        )}
      </p>
      <span ref={measurerRef} aria-hidden="true" data-notes-part="measurer" style={MEASURER_STYLE}>
        {text}
      </span>
    </>
  )
}

/**
 * A message in the entry's place (loading, a missing file, a rejected file). It does not scroll:
 * it is the strip saying why there is nothing to rotate, and the full text is on hover. The
 * stylesheet's own overflow rule (vertical scroll) is left to apply, in a box bounded by the strip.
 */
function NoticeView({ text }: { text: string }) {
  return (
    <p
      className="stage-notes-strip__current"
      data-notes-part="notice"
      title={text}
      style={{ alignSelf: 'stretch', minHeight: '1.4em' }}
    >
      {text}
    </p>
  )
}

/**
 * An image entry (REQ-012 R14). Sizing rule: the image fills the entry box — the strip's height
 * less its padding, and the width left between the `?` and the dropdown — scaled to sit entirely
 * inside it with its proportions kept (`object-fit: contain`). It is letterboxed, never cropped,
 * stretched or overflowing, and a small image is scaled up to fill.
 *
 * Image entries are meant for a strip at least 100 px tall (layout 2's is 205 px; measured). In
 * layout 1 the strip is 28 to 57 px high and the same rule yields an image about 18 px high, a
 * thumbnail, not a figure a reader can read. The rule holds there; the strip is what limits it.
 */
function ImageEntryView({ src, alt }: { src: string; alt: string }) {
  // The source that failed to load, so a different entry starts fresh without an effect.
  const [failedSrc, setFailedSrc] = useState<string | null>(null)
  return (
    <p
      className="stage-notes-strip__current"
      data-notes-part="entry"
      data-notes-variant="image"
      style={{ ...ENTRY_BOX_STYLE, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
    >
      {failedSrc === src ? (
        `Image unavailable: ${alt}`
      ) : (
        <img
          src={src}
          alt={alt}
          onError={() => setFailedSrc(src)}
          style={{ display: 'block', width: '100%', height: '100%', objectFit: 'contain' }}
        />
      )}
    </p>
  )
}

/**
 * The notes strip (REQ-007 W01), replacing the earlier talking-points panel: a short, wide,
 * display-only strip showing the active entry from an owner-authored notes file — content
 * loaded at runtime, never hardcoded in this component. The `?` tooltip sits at the strip's far
 * left; every control — next/previous cycling, the timed advance, and the notes-file picker —
 * lives behind the single dropdown at the right, opened by a standard downward-triangle
 * affordance. The strip surface itself triggers nothing.
 *
 * The picker's candidates come from the workbench listing route (`GET /api/v1/workbench/list`,
 * `src/api/routes/workbench.py`, `phase-wb-01`), filtered to `.json` under the fixed notes
 * directory (`ts/public/`) — never a hardcoded file list and never a client-side directory walk.
 * Listing alone only proves a file is JSON, not that it is a *notes* file (REQ-007 W01 requires
 * the picker to list compatible files): every candidate is additionally fetched and probed with
 * `isNotesFile` before it is offered, so an incompatible JSON file living in the same directory
 * (e.g. `CommandPanel`'s `demo-commands.json`) never appears in the dropdown, even though it
 * appears in the raw listing. Once a file is chosen, its content is fetched directly from Vite's
 * static serving of `ts/public/` (the same runtime-fetch convention `CommandPanel` uses), so both
 * the dropdown's enumeration and the strip's content come from disk, not page code.
 *
 * The chosen file persists across reloads under the ADR-016 selections key
 * (`ts/src/workbench/storage.ts`'s `saveActiveNotesFile`/`loadActiveNotesFile`), namespaced by the
 * schema version `StagePage` provides via `useActiveSchemaVersion` (the same single version
 * `useWorkbenchLayouts` resolves for the layout engine's own selections — never a hardcoded copy
 * of it), sharing that key via a merge-on-write so this component's writes never clobber the
 * layout engine's, and vice versa.
 *
 * Rotator variants (REQ-012 R12 to R14, `phase-wbf-06`). The rotation is a list of `NotesEntry`
 * values (text or image), and these rules are stated here and observed in the browser:
 *
 * - A text entry too long for the strip scrolls horizontally, right to left, instead of clipping
 *   (`TextEntryView`). Hovering over it or focusing it pauses the scroll; leaving or blurring
 *   resumes. This satisfies the contract's `marquee` alternative (REQ-037 notes-strip row).
 * - Scrolling within an entry and rotating between entries: the timed advance never rotates an
 *   entry away mid-scroll. It moves on only once the entry has been shown for the full interval,
 *   its scroll has finished one pass, and it is not held by the pointer or focus. The dropdown's
 *   Previous and Next apply at once, because a click is the reader's own choice. With the timed
 *   advance off, a scrolling entry repeats until the reader moves on.
 * - Images come from a directory the notes file names (`imageDirectory`), sized by the rule on
 *   `ImageEntryView`. A rotation is all text or all images (the ruling on `NotesEntry`).
 */
export default function NotesStripRegion() {
  // Resolved once, from the layout files, by `useWorkbenchLayouts` and provided by `StagePage` —
  // see `schemaVersionContext.ts`. `null` only before layouts have loaded, which this component
  // never observes in practice since `Slot.tsx` mounts panels only once `loadState === 'loaded'`.
  const schemaVersion = useActiveSchemaVersion()
  const [activeFile, setActiveFile] = useState<string>(
    () =>
      (schemaVersion !== null ? loadActiveNotesFile(schemaVersion) : null) ?? DEFAULT_NOTES_FILENAME,
  )
  // The settled content state names the file it belongs to, so choosing a file reads as
  // 'loading' until that file's fetch settles, without resetting state inside the effect.
  const [settledContent, setSettledContent] = useState<{
    file: string
    state: Exclude<ContentLoadState, 'loading'>
    notice?: string
  } | null>(null)
  const contentState: ContentLoadState =
    settledContent?.file === activeFile ? settledContent.state : 'loading'
  const [entries, setEntries] = useState<NotesEntry[]>([])
  const [current, setCurrent] = useState(0)
  const [autoAdvance, setAutoAdvance] = useState(false)
  const [fileListState, setFileListState] = useState<FileListState>('loading')
  const [fileList, setFileList] = useState<NotesFileEntry[]>([])
  const contentFetchGeneration = useRef(0)
  // The rotation's wait on the current entry (the R13 rule): the running scroll animation, whether
  // the pointer or focus holds the entry, and whether the interval has elapsed since it appeared.
  const scrollRef = useRef<Animation | null>(null)
  const heldRef = useRef(false)
  const intervalElapsedRef = useRef(false)

  // The compatible-file list for the dropdown's picker: every `.json` candidate the workbench
  // listing route returns, then narrowed to the ones whose *content* actually shapes up as a
  // notes file (REQ-007 W01) — the listing route only knows extensions, not schemas, so a
  // co-located but incompatible JSON file (e.g. `CommandPanel`'s `demo-commands.json`) would
  // otherwise appear in the picker and yield a reachable error state once selected. The candidate
  // count under `ts/public/` is small, so probing each one with a direct fetch is cheap; this
  // still never hardcodes a file list — every name still comes from the listing route.
  useEffect(() => {
    let cancelled = false
    fetchWorkbench(NOTES_FILE_LIST_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json()
      })
      .then(async (body: unknown) => {
        if (!isNotesFileEntryList(body)) {
          if (!cancelled) setFileListState('error')
          return
        }
        const probed = await Promise.all(
          body.map(async (entry) => {
            try {
              const response = await fetch(`/${entry.name}`, { cache: 'no-store' })
              if (!response.ok) return null
              const content: unknown = await response.json()
              return isNotesFile(content) ? entry : null
            } catch {
              return null
            }
          }),
        )
        if (cancelled) return
        setFileList(probed.filter((entry): entry is NotesFileEntry => entry !== null))
        setFileListState('loaded')
      })
      .catch(() => {
        if (!cancelled) setFileListState('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  // The active file's content — served as a static asset at the site root (Vite's default
  // `ts/public/` handling), refetched whenever the chosen file changes. A file that names an image
  // directory has that directory listed here too, so the rotation is a list of entries either way.
  useEffect(() => {
    const generation = ++contentFetchGeneration.current
    const stale = () => generation !== contentFetchGeneration.current
    const settle = (state: Exclude<ContentLoadState, 'loading'>, notice?: string) =>
      setSettledContent({ file: activeFile, state, notice })
    const loadImages = async (directory: string) => {
      const extensions = IMAGE_EXTENSIONS.map((ext) => `&ext=${encodeURIComponent(ext)}`).join('')
      const response = await fetchWorkbench(
        `${IMAGE_DIRECTORY_LIST_URL}?path=${encodeURIComponent(directory)}${extensions}`,
      )
      if (stale()) return
      if (!response.ok) {
        settle('missing', `Image directory not available: ${directory}.`)
        return
      }
      const images = imageEntriesFromListing(await response.json())
      if (stale()) return
      if (images === null) {
        settle('error', `Could not list images in ${directory}.`)
      } else if (images.length === 0) {
        settle('missing', `No images in ${directory}.`)
      } else {
        setEntries(images)
        setCurrent(0)
        settle('loaded')
      }
    }
    const load = async () => {
      const response = await fetch(`/${activeFile}`, { cache: 'no-store' })
      if (stale()) return
      if (response.status === 404) {
        settle('missing')
        return
      }
      if (!response.ok) {
        settle('error')
        return
      }
      const parsed = parseNotesFile(await response.json())
      if (stale()) return
      if (!parsed.ok) {
        settle(
          'error',
          parsed.reason === 'mixed'
            ? `Could not load "${activeFile}": it lists text points and names an image directory, and one rotation shows only one kind.`
            : undefined,
        )
      } else if (parsed.source.kind === 'images') {
        await loadImages(parsed.source.directory)
      } else {
        setEntries(parsed.source.entries.map((text) => ({ kind: 'text', text })))
        setCurrent(0)
        settle('loaded')
      }
    }
    load().catch(() => {
      if (!stale()) settle('error')
    })
  }, [activeFile])

  const entryCount = entries.length
  const entryCountRef = useRef(entryCount)
  useEffect(() => {
    entryCountRef.current = entryCount
  }, [entryCount])

  // Moves the timed advance on when every condition of the R13 rule holds: the entry has been
  // shown for the full interval, its scroll (if it scrolls) has finished its pass, and the
  // pointer and focus are not on it. Called again whenever one of those conditions changes.
  const advanceIfDue = useCallback(() => {
    if (!intervalElapsedRef.current || heldRef.current) return
    if (scrollRef.current !== null && scrollRef.current.playState !== 'finished') return
    intervalElapsedRef.current = false
    setCurrent((value) => (value + 1) % entryCountRef.current)
  }, [])

  // Optional timed advance: only runs with more than one entry, while enabled. The interval
  // restarts for every entry, so each is shown for at least a full interval.
  useEffect(() => {
    if (!autoAdvance || entryCount < 2) return
    intervalElapsedRef.current = false
    const timer = window.setTimeout(() => {
      intervalElapsedRef.current = true
      advanceIfDue()
    }, AUTO_ADVANCE_INTERVAL_MS)
    return () => window.clearTimeout(timer)
  }, [autoAdvance, entryCount, current, advanceIfDue])

  const holdEntry = useCallback(
    (held: boolean, resume = true) => {
      heldRef.current = held
      if (!held && resume) advanceIfDue()
    },
    [advanceIfDue],
  )
  const trackScroll = useCallback((animation: Animation | null) => {
    scrollRef.current = animation
  }, [])

  const selectFile = (fileName: string) => {
    setActiveFile(fileName)
    if (schemaVersion !== null) saveActiveNotesFile(schemaVersion, fileName)
  }

  const notice =
    contentState === 'loading'
      ? 'Loading notes…'
      : contentState === 'missing'
        ? (settledContent?.notice ?? `Notes file not found: ${activeFile}.`)
        : contentState === 'error'
          ? (settledContent?.notice ?? `Could not load "${activeFile}" as a notes file.`)
          : null
  const entry = contentState === 'loaded' ? (entries[current] ?? null) : null

  const cyclingDisabled = contentState !== 'loaded' || entries.length < 2

  return (
    <section className="stage-panel stage-notes-strip" aria-label="Notes">
      {/* The top bar is the slot's (ADR-031 decision 1): this panel supplies its elements only,
          the `?` to the strip's help place and the one controls dropdown to its controls place. */}
      <BarElement type="help">
        <Tooltip label="About the notes strip">
          Cycles owner-authored notes loaded at runtime from a chosen JSON file under{' '}
          <code>ts/public/</code>. Every control — cycling, the timed advance, and the file
          picker — lives in the dropdown at the right.
        </Tooltip>
      </BarElement>
      <div className="stage-notes-strip__row">
        {entry === null ? (
          <NoticeView key={contentState} text={notice ?? ''} />
        ) : entry.kind === 'image' ? (
          <ImageEntryView key={current} src={entry.src} alt={entry.alt} />
        ) : (
          <TextEntryView
            key={current}
            text={entry.text}
            // Nothing rotates the entry away unless the timed advance is on and there is somewhere
            // to go; the advance control is disabled below two entries but keeps its setting.
            loop={!(autoAdvance && entryCount >= 2)}
            onScroll={trackScroll}
            onHold={holdEntry}
            onPassFinished={advanceIfDue}
          />
        )}
      </div>
      <BarElement type="choice">
        <Popover triggerLabel="▾" title="Notes controls">
          {() => (
            <div className="stage-notes-strip__menu">
              <div className="stage-notes-strip__menu-nav">
                <button
                  type="button"
                  disabled={cyclingDisabled}
                  onClick={() =>
                    setCurrent((value) => (value - 1 + entries.length) % entries.length)
                  }
                >
                  Previous
                </button>
                <span className="stage-notes-strip__menu-index">
                  {contentState === 'loaded' ? `${current + 1} / ${entries.length}` : '—'}
                </span>
                <button
                  type="button"
                  disabled={cyclingDisabled}
                  onClick={() => setCurrent((value) => (value + 1) % entries.length)}
                >
                  Next
                </button>
              </div>
              <button
                type="button"
                className="stage-notes-strip__menu-auto-advance"
                aria-pressed={autoAdvance}
                disabled={cyclingDisabled}
                onClick={() => setAutoAdvance((value) => !value)}
              >
                Auto-advance: {autoAdvance ? 'On' : 'Off'}
              </button>
              <label className="stage-notes-strip__menu-picker">
                Notes file
                <select value={activeFile} onChange={(event) => selectFile(event.target.value)}>
                  {!fileList.some((entry) => entry.name === activeFile) ? (
                    <option value={activeFile}>{activeFile}</option>
                  ) : null}
                  {fileList.map((entry) => (
                    <option key={entry.name} value={entry.name}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              {fileListState === 'error' ? (
                <p className="stage-notes-strip__menu-list-error" role="alert">
                  Could not list notes files from <code>ts/public/</code>.
                </p>
              ) : null}
            </div>
          )}
        </Popover>
      </BarElement>
    </section>
  )
}
