// The compatible files: `.html`/`.htm`/`.svg`, which the HTML Viewer renders directly; `.md`, which
// `serveRepositoryFiles` (`ts/vite.config.ts`) now renders route-side to HTML before the HTML
// Viewer ever sees it (idea 000110, idea 000119's ruling) — the block idea 000118 put on `.md` in
// the HTML Viewer was only ever "until rendering lands," and it lands in the same change that adds
// `.md` to this list; and the six raster/vector image formats that same route already serves with
// correct image MIME types (`CONTENT_TYPE_BY_EXTENSION`) — an image needs no render step in the
// iframe, so widening this list to include them (idea 000232) was a one-line addition, no backend
// or vite.config change. Kept in this module, apart from `HtmlViewerRegion.tsx`, so the File
// Browser's right-click context menu (`FileBrowserRegion.tsx`, REQ-007 W09) can hide "Open in HTML
// Viewer" on an incompatible entry using this same list rather than a second, hand-kept copy of it.
export const COMPATIBLE_EXTENSIONS = [
  '.html',
  '.htm',
  '.svg',
  '.md',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.webp',
  '.ico',
]
