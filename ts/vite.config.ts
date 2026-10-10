import { spawnSync } from 'node:child_process'
import {
  closeSync,
  createReadStream,
  existsSync,
  fstatSync,
  lstatSync,
  openSync,
  readFileSync,
  readlinkSync,
  realpathSync,
} from 'node:fs'
import type { ServerResponse } from 'node:http'
import {
  basename,
  extname,
  isAbsolute,
  join,
  normalize,
  relative as relativePath,
  resolve,
  sep,
} from 'node:path'
import { defineConfig, loadEnv, type Connect, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { marked } from 'marked'

// The repo root, one directory above `ts/` (this file's own directory) — where `_public/` (the
// generated overview page's home, `phase-demo-04`) and `_data/` (repository data, including the
// workbench layout definitions, `phase-wb-02`) live.
const repoRoot = resolve(__dirname, '..')
const publicDir = join(repoRoot, '_public')
const workbenchLayoutsDir = join(repoRoot, '_data', 'workbench', 'layouts')
// The workbench data files the page imports rather than fetches (`slot-schemas.json` and
// `panel-elements.json`, ADR-031 decision 4): they sit one directory above the layouts, and the
// dev server may serve this directory and nothing else outside `ts/` (see `server.fs.allow`).
const workbenchDataDir = join(repoRoot, '_data', 'workbench')
// The directories the dev server may serve files from: `server.fs.allow` and
// `refuseSymlinkEscapes` both take this one list.
const devServerAllow = [__dirname, workbenchDataDir]

const GENERATED_OVERVIEW_PREFIX = '/generated-overview/'
const WORKBENCH_LAYOUTS_PREFIX = '/workbench-layouts/'
const WORKBENCH_FILE_PREFIX = '/workbench-file/'

// --- Serving a file only from a descriptor that was checked ------------------------------------
//
// Every file this dev server serves from `ts/`, `_data/workbench/` or `_public/` is opened first
// and checked second, and its bytes come from that same open descriptor. Checking a path and then
// opening it again leaves a window in which the name can be swapped for a symlink that points
// elsewhere: a probe that renamed a regular file and an outside-pointing symlink over one name
// while requests ran got the outside file back from every route (security review of
// `phase-arch-07`, 2026-10-09). An open descriptor cannot be swapped.

// A file opened and checked: the descriptor to read from and the path it really has.
export type CheckedFile = { fd: number; realPath: string }

// The directories, symlinks resolved; one that does not exist is dropped.
function realDirectories(directories: string[]): string[] {
  return directories.flatMap((directory) => {
    try {
      return [realpathSync(directory)]
    } catch {
      return []
    }
  })
}

function isWithin(path: string, directories: string[]): boolean {
  return directories.some((directory) => path === directory || path.startsWith(directory + sep))
}

// A path with a `node_modules` directory in it, on either separator.
const NODE_MODULES_SEGMENT = /[\\/]node_modules[\\/]/

const PROC_FD = '/proc/self/fd'
const hasProcFd = existsSync(PROC_FD)

// What opening a name found. `'absent'`: nothing could be opened there, or it is not a regular file
// (a directory, say), so the request is someone else's to answer. `'changed'`: a file was opened
// but the name no longer leads to it (a rename replaced it, or the name now differs from what the
// descriptor holds). `'forbidden'`: the opened file lies outside the directories.
export type OpenResult = CheckedFile | 'absent' | 'changed' | 'forbidden'

// Opens `path` and returns the descriptor only if the file it opened is a regular file whose real
// path lies inside one of `directories` (already resolved by `realDirectories`). On Linux the
// opened file's real path is read from `/proc/self/fd`, which names the file the descriptor holds,
// however the name changes afterwards. Elsewhere (macOS, Windows) the name is resolved again and
// the result must be a regular file, not a symlink, with the descriptor's device and inode. A file
// with more than one hard link is refused too: a hard link is a second name for the same file, so
// one placed inside the directories can name a file that lives outside them, and neither its path
// nor its inode shows that. Files under a `node_modules` directory are exempt, because package
// managers hard-link packages there. The caller owns a returned descriptor and must close it.
function openOnce(path: string, directories: string[]): OpenResult {
  let fd: number
  try {
    fd = openSync(path, 'r')
  } catch {
    return 'absent'
  }
  const refuse = (result: 'absent' | 'changed' | 'forbidden') => {
    closeSync(fd)
    return result
  }
  try {
    const opened = fstatSync(fd, { bigint: true })
    if (!opened.isFile()) return refuse('absent')
    let realPath: string
    if (hasProcFd) {
      realPath = readlinkSync(`${PROC_FD}/${fd}`)
      if (realPath.endsWith(' (deleted)')) return refuse('changed')
    } else {
      try {
        realPath = realpathSync(path)
      } catch {
        return refuse('changed')
      }
      const named = lstatSync(realPath, { bigint: true, throwIfNoEntry: false })
      if (!named?.isFile() || named.dev !== opened.dev || named.ino !== opened.ino) {
        return refuse('changed')
      }
    }
    if (!isWithin(realPath, directories)) return refuse('forbidden')
    if (opened.nlink > 1n && !NODE_MODULES_SEGMENT.test(realPath)) return refuse('forbidden')
    return { fd, realPath }
  } catch {
    return refuse('changed')
  }
}

// `openOnce`, tried again while the name keeps changing under it (an editor's save-by-rename, or
// a deliberate swap). A file still changing after the last try stays `'changed'`; callers answer
// that themselves and never hand the request on to code that would open the name again.
export function openChecked(path: string, directories: string[]): OpenResult {
  let result = openOnce(path, directories)
  for (let attempt = 1; result === 'changed' && attempt < 5; attempt += 1) {
    result = openOnce(path, directories)
  }
  return result
}

// Reads a checked file whole and closes its descriptor.
function readChecked(file: CheckedFile): Buffer {
  try {
    return readFileSync(file.fd)
  } finally {
    closeSync(file.fd)
  }
}

// Streams a checked file into `res`; the caller has set the status and headers. A read error
// before any byte is sent becomes a 404, one after is a dropped connection, and neither reaches
// the process as an unhandled `error` event. The descriptor closes when the stream ends, fails or
// the client goes away.
function streamChecked(res: ServerResponse, file: CheckedFile): void {
  const stream = createReadStream('', { fd: file.fd, autoClose: true })
  stream.on('error', () => {
    if (res.headersSent) {
      res.destroy()
    } else {
      res.statusCode = 404
      res.end()
    }
  })
  res.on('close', () => stream.destroy())
  stream.pipe(res)
}

// Request extensions Vite transforms rather than serves as they are; the guard leaves those to
// Vite's pipeline, where `load` below supplies the checked bytes.
const MODULE_EXTENSIONS = new Set([
  '.js',
  '.mjs',
  '.cjs',
  '.jsx',
  '.ts',
  '.tsx',
  '.mts',
  '.cts',
  '.css',
  '.scss',
  '.sass',
  '.less',
  '.styl',
  '.html',
  '.htm',
  '.vue',
  '.svelte',
  '.wasm',
])
// The module files `load` reads itself; anything else is left to Vite and its other plugins.
const LOADED_EXTENSIONS = new Set([
  '.js',
  '.mjs',
  '.cjs',
  '.jsx',
  '.ts',
  '.tsx',
  '.mts',
  '.cts',
  '.css',
  '.json',
])

// Keeps the dev server from serving any file that, symlinks resolved, lies outside the directories
// it may serve, or that a hard link names from inside them (see `openOnce`), by any route and
// under concurrent renames. Vite's own `server.fs.allow` check
// compares path prefixes and resolves no symlink, so a symlink inside `ts/` or `_data/workbench/`
// that points elsewhere (at `_private/`, say) was served through `/@fs/<absolute path>` and
// through a root-relative URL (security review of `phase-arch-07`, 2026-10-09). Three parts:
//
// - A middleware, attached directly in `configureServer` and first in `plugins`, so it runs before
//   Vite's internal middlewares and this file's other routes. For a GET or HEAD of a file Vite
//   would send unchanged (an extension it does not transform, no `?import`) it serves the file
//   itself from a checked descriptor, so Vite never reopens the name. For anything else it opens
//   and checks the file, refusing it with 403 if it leads outside, and then hands the request on.
// - A `load` hook (`enforce: 'pre'`) that gives Vite's transform pipeline the bytes of a source
//   module (`LOADED_EXTENSIONS`, outside `node_modules`) or of a `?raw` import from a checked
//   descriptor, so a module cannot be swapped between that check and Vite's read either.
// - A second middleware, after Vite's single-page fallback, that serves `.html` pages from a
//   checked descriptor through Vite's HTML transform.
// - `routes` maps this file's own URL prefixes that serve a directory inside the allow-list
//   (`/workbench-layouts/`) to that directory, so the middleware checks those URLs too; each such
//   route also serves only from a checked descriptor itself, which covers `/generated-overview/`,
//   whose `_public/` lies outside the list.
//
// Every request that names a file is checked by the first middleware, so a symlink or a hard link
// leading outside is refused (403) on every route, `node_modules` and every import query
// included. Two kinds of request are checked there but then read again by name by Vite or the
// plugin that owns them, so they are not protected against a swap between the check and the read:
// source modules under `node_modules` (`load` passes them through; npm writes that directory),
// and import queries other than `?raw` (`?inline`, `?worker`, `?url`). A URL naming no existing
// file passes through untouched, for Vite to answer as it would have. Exported for
// `vite.config.test.ts`.
// `test/test_workbench_slot_matcher.py` also refuses a tracked symlink under either directory, so
// one cannot be merged in the first place.
export function refuseSymlinkEscapes(
  root: string,
  allow: string[],
  routes: Record<string, string> = {},
): Plugin {
  // The files a request URL can name, in the order Vite looks: an absolute path after `/@fs`, a
  // route's own directory, or a path under the root's `public/` directory and then the root.
  const candidates = (urlPath: string): string[] => {
    if (urlPath.startsWith('/@fs/')) {
      const absolute = urlPath.slice('/@fs'.length)
      return [/^\/[A-Za-z]:/.test(absolute) ? absolute.slice(1) : absolute]
    }
    for (const [prefix, directory] of Object.entries(routes)) {
      if (urlPath.startsWith(prefix)) return [join(directory, urlPath.slice(prefix.length))]
    }
    return [join(root, 'public', urlPath), join(root, urlPath)]
  }
  // A file Vite would send as it is: a GET or HEAD of a non-module extension. For those Vite
  // transforms only an `?import` request (an asset imported from a module); any other query
  // (`?raw` fetched directly, `?t=`) is served from the file unchanged.
  const servesAsIs = (url: string, urlPath: string, method: string | undefined) =>
    (method === 'GET' || method === 'HEAD') &&
    !/[?&]import(?:[&=]|$)/.test(url) &&
    extname(urlPath) !== '' &&
    !MODULE_EXTENSIONS.has(extname(urlPath).toLowerCase()) &&
    !Object.keys(routes).some((prefix) => urlPath.startsWith(prefix))

  return {
    name: 'refuse-symlink-escapes',
    enforce: 'pre',
    configureServer(server) {
      // The file watcher reports a name that changes between a file and a symlink faster than it
      // can read it (`readlink` `EINVAL`) as an `error` event; with no listener that event is
      // thrown and ends the dev server. A watch error is logged and the server keeps running.
      server.watcher.on('error', (error) => {
        server.config.logger.warn(`file watcher: ${String(error)}`)
      })
      server.middlewares.use((req, res, next) => {
        const url = req.url ?? ''
        let urlPath: string
        try {
          urlPath = decodeURIComponent(url.split('?')[0] ?? '')
        } catch {
          next()
          return
        }
        const directories = realDirectories(allow)
        for (const candidate of candidates(urlPath)) {
          const file = openChecked(candidate, directories)
          if (file === 'absent') continue
          if (file === 'forbidden') {
            res.statusCode = 403
            res.end('Forbidden')
            return
          }
          if (file === 'changed') {
            res.statusCode = 404
            res.end('Not found')
            return
          }
          if (!servesAsIs(url, urlPath, req.method)) {
            closeSync(file.fd)
            next()
            return
          }
          const contentType = CONTENT_TYPE_BY_EXTENSION[extname(urlPath).toLowerCase()]
          res.statusCode = 200
          res.setHeader('Content-Type', contentType ?? 'application/octet-stream')
          res.setHeader('Cache-Control', 'no-cache')
          if (req.method === 'HEAD') {
            closeSync(file.fd)
            res.end()
            return
          }
          streamChecked(res, file)
          return
        }
        next()
      })
      // Registered after Vite's own middlewares (a returned function runs after them), which
      // includes the single-page fallback that rewrites a route to `/index.html`, and before
      // Vite's HTML middleware, which would read the page from its name again: an `.html` file
      // is served here from a checked descriptor, through Vite's own HTML transform.
      return () => {
        server.middlewares.use((req, res, next) => {
          let urlPath: string
          try {
            urlPath = decodeURIComponent((req.url ?? '').split('?')[0] ?? '')
          } catch {
            next()
            return
          }
          if (req.method !== 'GET' || extname(urlPath).toLowerCase() !== '.html') {
            next()
            return
          }
          const file = openChecked(join(root, urlPath), realDirectories(allow))
          if (file === 'absent') {
            next()
            return
          }
          if (file === 'forbidden' || file === 'changed') {
            res.statusCode = file === 'forbidden' ? 403 : 404
            res.end(file === 'forbidden' ? 'Forbidden' : 'Not found')
            return
          }
          const html = readChecked(file).toString('utf-8')
          server
            .transformIndexHtml(req.url ?? urlPath, html, req.originalUrl)
            .then((transformed) => {
              res.statusCode = 200
              res.setHeader('Content-Type', 'text/html; charset=utf-8')
              res.setHeader('Cache-Control', 'no-cache')
              res.end(transformed)
            })
            .catch(next)
        })
      }
    },
    load(id) {
      // `?raw` is answered here exactly as Vite's asset plugin answers it, so that plugin does not
      // read the file by its name; any other query belongs to the plugin that owns it.
      const raw = id.endsWith('?raw')
      const path = raw ? id.slice(0, -'?raw'.length) : id
      if (path.includes('\0') || path.includes('?') || !isAbsolute(path)) return null
      if (NODE_MODULES_SEGMENT.test(path)) return null
      if (!raw && !LOADED_EXTENSIONS.has(extname(path).toLowerCase())) return null
      const file = openChecked(path, realDirectories(allow))
      if (file === 'absent') return null
      if (file === 'forbidden') {
        throw new Error(`Refused: ${id} leads outside the directories the dev server may serve.`)
      }
      if (file === 'changed') throw new Error(`${id} kept changing while it was read; try again.`)
      const text = readChecked(file).toString('utf-8')
      return raw ? `export default ${JSON.stringify(text)}` : text
    },
  }
}

// Serves files under `_public/` at `/generated-overview/<path>` so `OverviewRegion` can embed
// the generated overview page (its actual location is reported at runtime by the backend's
// `overview-location` route, `src/api/routes/demo_stage.py`, not hardcoded here).
//
// This can't just be Vite's built-in `/@fs/` static-file route with `server.fs.allow`: verified
// against the installed Vite 6.4.3 that `/@fs/<missing-file>` falls through to the dev server's
// SPA history fallback and returns 200 with `index.html`'s content instead of 404 — which would
// make a not-yet-generated overview page (the default state until `phase-demo-04` runs) render
// the stage app's own shell inside the iframe, risking iframe self-recursion, instead of the
// absent-content message the requirement calls for. Registering this middleware directly inside
// `configureServer`/`configurePreviewServer` (rather than returning it as a post-hook function)
// runs it before Vite's internal middlewares, so a 404 here is a real 404, not a fallback.
// `directory` is a parameter so `vite.config.test.ts` can point the route at a scratch tree.
export function serveGeneratedOverview(directory: string = publicDir): Plugin {
  const attach = (middlewares: Connect.Server) => {
    middlewares.use(GENERATED_OVERVIEW_PREFIX, (req, res) => {
      const requestedPath = decodeURIComponent((req.url ?? '').split('?')[0] ?? '')
      const resolved = normalize(join(directory, requestedPath))
      // Refuse anything that escapes `_public/` (defends against `../` traversal).
      if (resolved !== directory && !resolved.startsWith(directory + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      // Opened once and checked; the bytes come from that descriptor (see `openChecked`).
      const file = openChecked(resolved, realDirectories([directory]))
      if (file === 'absent' || file === 'changed') {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Generated overview page not found at ${resolved}.`)
        return
      }
      if (file === 'forbidden') {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      res.statusCode = 200
      res.setHeader('Content-Type', 'text/html; charset=utf-8')
      streamChecked(res, file)
    })
  }

  return {
    name: 'serve-generated-overview',
    configureServer(server) {
      attach(server.middlewares)
    },
    configurePreviewServer(server) {
      attach(server.middlewares)
    },
  }
}

// Serves `_data/workbench/layouts/<id>.json` at `/workbench-layouts/<id>.json` so the workbench
// layout engine (`ts/src/workbench/`, `phase-wb-02`, ADR-016) loads layout definitions at
// runtime — never bundled — matching this file's own rule for the generated overview page and
// the existing `talking-points.json`/`demo-commands.json` runtime-fetch convention: editing a
// shipped layout file changes the page's geometry with no frontend rebuild.
// `directory` is a parameter so `vite.config.test.ts` can point the route at a scratch tree.
export function serveWorkbenchLayouts(directory: string = workbenchLayoutsDir): Plugin {
  const attach = (middlewares: Connect.Server) => {
    middlewares.use(WORKBENCH_LAYOUTS_PREFIX, (req, res) => {
      const requestedPath = decodeURIComponent((req.url ?? '').split('?')[0] ?? '')
      const resolved = normalize(join(directory, requestedPath))
      if (resolved !== directory && !resolved.startsWith(directory + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      // Opened once and checked; the bytes come from that descriptor (see `openChecked`).
      const file = openChecked(resolved, realDirectories([directory]))
      if (file === 'absent' || file === 'changed') {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Layout definition not found at ${resolved}.`)
        return
      }
      if (file === 'forbidden') {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      res.statusCode = 200
      res.setHeader('Content-Type', 'application/json; charset=utf-8')
      streamChecked(res, file)
    })
  }

  return {
    name: 'serve-workbench-layouts',
    configureServer(server) {
      attach(server.middlewares)
    },
    configurePreviewServer(server) {
      attach(server.middlewares)
    },
  }
}

// The content types this route ever answers with: the compatible documents themselves
// (`.html`/`.htm`/`.svg`, plus `.md` — served as `text/html`, since `serveRepositoryFiles` below
// renders markdown to HTML route-side rather than serving its raw source, idea 000119's ruling)
// and the ordinary assets a static page can link to relatively (stylesheets, scripts, images,
// fonts) — a `.html` page's own relative links resolve against this same prefix, so they need to
// be servable too, not just the page itself. Anything outside this map falls back to
// `application/octet-stream`.
const CONTENT_TYPE_BY_EXTENSION: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.md': 'text/html; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
}

// `git check-ignore`, one path per request — mirrors the backend workbench routes' own rule
// (ADR-015 rule 3: "Listings exclude private and derived content ... using the repository's
// ignore rules rather than a hand-kept list") applied here as this dev-server route's own
// security boundary, independent of whatever the HTML Viewer's dropdown happens to have listed
// (ADR-015 rule 2: "the in-app pickers ... are convenience, not the security boundary").
function isGitIgnored(repoRelativePath: string, root: string): boolean {
  const result = spawnSync('git', ['check-ignore', '-q', repoRelativePath], { cwd: root })
  return result.status === 0
}

// Serves any non-ignored file under the repository root at `/workbench-file/<repo-relative
// path>`, so the HTML Viewer panel (`ts/src/stage/HtmlViewerRegion.tsx`, REQ-007 W07) can embed a
// selected `.html`/`.svg` page (and that page's own relatively-linked assets) found via the
// workbench search/listing routes — those routes report paths only, never content (ADR-015), so
// this is the piece that actually serves bytes, the same role `serveGeneratedOverview` already
// plays for the narrower `_public/` case above. Repository-root-bounded and `.git`/ignored-path
// rejecting, the same two checks `src/api/routes/workbench.py`'s `resolve_repo_relative_path` and
// `_git_ignored_paths` apply server-side — this loopback-only dev tool holds itself to the same
// boundary the backend API does, even though nothing here is reachable off-machine.
//
// This is a workbench route (ADR-015 rule 1: "one gate, one binding"), so — mirroring
// `src/api/__init__.py`'s refusal to import `workbench.py` unless `D_SYSTEM_DEMO_TERMINAL=1` —
// it is only ever registered when that same flag is set in this process's own environment; see
// the gated entry in the `plugins` array below. Unregistered, `/workbench-file/*` falls through
// to Vite's normal middleware chain and 404s (or, under the dev server's history fallback,
// serves `index.html` like any other unknown route) — it does not exist, the same "unset means
// absent" property the backend route enjoys.
// Query param that selects the raw-bytes response for a wrapped raster image (see the
// `RASTER_IMAGE_EXTENSIONS` wrapper branch below) — read from the query string only, never from
// the path, so it cannot be spoofed by a path segment and never influences which file on disk
// gets resolved.
const RAW_IMAGE_QUERY_PARAM = 'raw'

// The six raster formats a bare `<img>` document renders top-left-anchored at natural size,
// un-scaled, in Chromium (browser-measured: a 900x560 image inside HtmlViewerRegion's ~739x262
// iframe showed only its top-left corner, roughly 47% of its height, with scrollbars inside the
// iframe) — wrapped in a small fitting/centring HTML document instead of served as bare bytes.
// `.svg` is deliberately excluded: it already scales to its container natively and that behaviour
// is browser-verified, so it is left untouched.
const RASTER_IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico'])

// `root` is a parameter so `vite.config.test.ts` can point the route at a scratch repository.
export function serveRepositoryFiles(root: string = repoRoot): Plugin {
  const attach = (middlewares: Connect.Server) => {
    middlewares.use(WORKBENCH_FILE_PREFIX, (req, res) => {
      // Split the query string off before decoding the path — `decodeURIComponent` must never see
      // (and so never be influenced by) the query, and the query itself is parsed separately below
      // so the `raw` flag can be read from it without ever touching path resolution.
      const [pathOnly, queryString] = (req.url ?? '').split('?')
      const requestedPath = decodeURIComponent(pathOnly ?? '')
      const query = new URLSearchParams(queryString ?? '')
      const relative = requestedPath.replace(/^\/+/, '')
      if (!relative) {
        res.statusCode = 400
        res.end('A repository-relative file path is required.')
        return
      }
      const resolved = normalize(join(root, relative))
      if (resolved !== root && !resolved.startsWith(root + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      // `.git` exclusion, checked on every path segment case-insensitively: the presentation
      // machine (`docs/00-working/demo-windows-setup.md`) is Windows, whose case-insensitive
      // filesystem would let a segment spelled `.GIT` reach this far were the comparison
      // case-sensitive, and `git check-ignore` (the `isGitIgnored` check below) does not flag
      // `.git` itself — it is not a tracked-vs-ignored question, it is always excluded, the same
      // rule the backend applies via `ALWAYS_EXCLUDED_NAMES`. Each segment is also stripped of
      // trailing dots/spaces before the comparison: Win32 silently strips trailing dots and
      // spaces from path components when resolving a path on disk, so a literal segment spelled
      // `.git.` or `.git ` never equals `.git` textually here but still resolves to the real
      // `.git` directory on that presentation machine — stripping first closes that gap even
      // though it cannot be exercised (and so verified) on this Linux worktree.
      if (
        relative
          .split('/')
          .some((segment) => segment.replace(/[. ]+$/, '').toLowerCase() === '.git')
      ) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      // Resolve symlinks before trusting the boundary check above: `resolved` there is only
      // textually normalized, so a symlink under the repository whose target lands outside it
      // passes that check untouched. The backend's own boundary (`src/api/routes/workbench.py`'s
      // `resolve_repo_relative_path`) follows symlinks for this reason (ADR-015 rule 2: "symlinks
      // whose resolved target leaves the root"). The file is opened once and checked, and every
      // check below and the bytes served use that descriptor and its real path, so the name
      // cannot be swapped between the check and the read (see `openChecked`). The symlink-resolved
      // root is the boundary, so a symlinked worktree checkout itself doesn't widen it.
      const realRoot = realpathSync(root)
      const file = openChecked(resolved, [realRoot])
      if (file === 'absent' || file === 'changed') {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Not found: ${relative}`)
        return
      }
      if (file === 'forbidden') {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      const realResolved = file.realPath
      // The ignore and `.git` checks run on the resolved path as well as the requested one: a
      // symlink in a tracked directory can lead to an ignored file (anything under `_private/`)
      // or into `.git/`, and `git check-ignore` judges only the path it is given (security review
      // of `phase-arch-07`, 2026-10-09). ADR-015 rule 3 runs it on resolved paths for this reason.
      const realRelative = relativePath(realRoot, realResolved).split(sep).join('/')
      if (
        realRelative
          .split('/')
          .some((segment) => segment.replace(/[. ]+$/, '').toLowerCase() === '.git')
      ) {
        closeSync(file.fd)
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      if (isGitIgnored(relative, root) || isGitIgnored(realRelative, root)) {
        closeSync(file.fd)
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Not found: ${relative}`)
        return
      }
      const contentType = CONTENT_TYPE_BY_EXTENSION[extname(resolved).toLowerCase()]
      res.statusCode = 200
      res.setHeader('Content-Type', contentType ?? 'application/octet-stream')
      // Never cached — the HTML Viewer's refresh control (REQ-007 W07) re-fetches the current
      // page on demand specifically so an on-disk edit shows up immediately, which a cached
      // response would defeat.
      res.setHeader('Cache-Control', 'no-store')
      // `Content-Security-Policy: sandbox` (no tokens, i.e. every restriction applied): unlike
      // the iframe's own `sandbox=""` attribute (`HtmlViewerRegion.tsx`), the "open page in a new
      // tab" fallback is a full top-level navigation, which an iframe attribute cannot reach — but
      // the CSP `sandbox` directive applies to top-level navigations the same way it applies to
      // frames (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/sandbox),
      // blocking script execution and giving the navigated document an opaque origin, so opening
      // any served repository file directly in a new tab can no longer read/write this app's
      // origin (its `localStorage`, `POST /api/v1/workbench/reveal`, etc.) even though it is
      // served same-origin. The generated overview page this route also serves has no `<script>`
      // tags (W04-W), so it keeps rendering under this header exactly as it does under the
      // iframe's `sandbox=""`. Applies to every response from this route, not just the fallback
      // path, since the same URL is reachable either way.
      res.setHeader('Content-Security-Policy', 'sandbox')
      // A bare raster image response renders as Chromium's built-in image document: top-left
      // anchored, at the image's natural size, never scaled to the iframe — the browser-measured
      // finding above. Wrapping it in a minimal HTML document with a single `<img>` fixes that
      // without touching `HtmlViewerRegion.tsx`: the component asks for the same path either way
      // and gets back something that fits. `?raw=1` (checked via `query`, never the path) is what
      // that wrapper's own `<img src>` points back at to fetch the actual bytes, one level down —
      // without it, wrapping would recurse into wrapping the wrapper.
      // The wrapper above is a presentation choice for a *top-level* view of an image (the HTML
      // Viewer's iframe, or a direct browser navigation) — it must never intercept an `<img>` that
      // is itself fetching this same URL for its bytes, which is exactly what a relative
      // `<img src="foo.png">` inside a rendered markdown file or a served `.html` page does (both
      // resolve against this same `/workbench-file/` prefix). Without this discriminator, every
      // raster URL always answers with the wrapper unless the caller happens to already know to
      // add `?raw=1`, which an ordinary `<img src>` written by a markdown or HTML author never
      // does — that `<img>` would render broken. `Sec-Fetch-Dest` is what browsers attach to every
      // fetch on a potentially-trustworthy origin (localhost qualifies) to say what kind of
      // request this is; `image` means "an `<img>`/`<picture>` etc. asked for this," so that case
      // always gets raw bytes. Node lowercases incoming header *names* itself, so
      // `req.headers['sec-fetch-dest']` already finds the header regardless of the casing it
      // arrived in; the value is lowercased here too for the same reason, even though the fetch
      // spec itself always sends it lowercase. A missing header (an older browser, curl, or any
      // client that omits it) is deliberately treated as "not an image sub-resource" — i.e. still
      // wrapped — so the demo path (an iframe/direct-navigation client that does send the header)
      // is never the case put at risk by a client that doesn't; `?raw=1` remains the explicit
      // escape hatch for exactly that gap, and is what the wrapper's own `<img>` relies on.
      // Do not "simplify" this away by dropping the header check: doing so reintroduces the
      // defect this branch exists to fix.
      const secFetchDest = (req.headers['sec-fetch-dest'] ?? '').toString().toLowerCase()
      const isImageSubResourceRequest = secFetchDest === 'image'
      const extensionLower = extname(realResolved).toLowerCase()
      if (
        RASTER_IMAGE_EXTENSIONS.has(extensionLower) &&
        !query.has(RAW_IMAGE_QUERY_PARAM) &&
        !isImageSubResourceRequest
      ) {
        const title = basename(realResolved)
        // Relative, not absolute: this document's own URL already carries whatever query
        // `HtmlViewerRegion`'s iframe added (its cache-busting `?v=<n>`), so a relative
        // `<basename>?raw=1` resolves against that same URL to
        // `/workbench-file/<dir>/<name>.png?raw=1` — the sibling request for the same file's raw
        // bytes — without this route needing to know its own full request path.
        // `encodeURIComponent` keeps a name containing a space or `#` correctly resolvable as a
        // URL.
        const imgSrc = `${encodeURIComponent(title)}?${RAW_IMAGE_QUERY_PARAM}=1`
        const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${title}</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    background: #111;
  }
  body {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  img {
    max-width: 100%;
    max-height: 100vh;
    object-fit: contain;
  }
</style>
</head>
<body>
<img src="${imgSrc}" alt="${title}">
</body>
</html>
`
        closeSync(file.fd)
        res.setHeader('Content-Type', 'text/html; charset=utf-8')
        res.end(html)
        return
      }
      // Markdown renders route-side, to HTML, rather than serving raw source (idea 000110, sited
      // here rather than in the frontend or a new backend route per idea 000119's ruling: both
      // `HtmlViewerRegion`'s sandboxed iframe and idea 000109's double-click-to-new-tab fetch this
      // same `/workbench-file/` URL, so rendering once at the route means there is one path to
      // keep correct, not two; ADR-015 scopes the FastAPI workbench API to reporting paths, never
      // content, so a backend route was never the right place). No client-side sanitizer
      // (DOMPurify or similar) is layered on top of `marked`'s output — the
      // `Content-Security-Policy: sandbox` header set just above already gives this response an
      // opaque origin and blocks script execution for both the iframe and the new-tab case, which
      // is what a sanitizer would otherwise exist to backstop.
      if (extname(realResolved).toLowerCase() === '.md') {
        try {
          const source = readChecked(file).toString('utf-8')
          // `{ async: false }` pins the synchronous overload — `marked.parse` is typed to return
          // `string | Promise<string>` because an async extension can make it asynchronous, but
          // none is registered here, so this is always the synchronous, string-returning path;
          // asserting the type keeps that guarantee visible without making this middleware (or
          // its surrounding `Connect` handler signature) `async`.
          const rendered = marked.parse(source, { async: false }) as string
          const title = basename(realResolved)
          const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${title}</title>
<style>
  body {
    max-width: 48rem;
    margin: 2.5rem auto;
    padding: 0 1.5rem 4rem;
    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
    font-size: 20px;
    line-height: 1.65;
    color: #1a1a1a;
    background: #fff;
  }
  h1, h2, h3, h4, h5, h6 {
    line-height: 1.25;
    margin: 1.6em 0 0.6em;
    font-weight: 600;
  }
  h1 { font-size: 2.2em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
  h2 { font-size: 1.7em; border-bottom: 1px solid #eee; padding-bottom: 0.25em; }
  h3 { font-size: 1.35em; }
  p, ul, ol, blockquote, pre, table { margin: 0.9em 0; }
  ul, ol { padding-left: 1.6em; }
  li { margin: 0.3em 0; }
  code {
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: 0.9em;
    background: #f2f2f2;
    padding: 0.15em 0.4em;
    border-radius: 4px;
  }
  pre {
    background: #1e1e1e;
    color: #f2f2f2;
    padding: 1em 1.25em;
    border-radius: 8px;
    overflow-x: auto;
  }
  pre code { background: none; padding: 0; color: inherit; }
  blockquote {
    border-left: 4px solid #ccc;
    margin-left: 0;
    padding: 0.2em 1.2em;
    color: #555;
    font-style: italic;
  }
  a { color: #0b5fff; text-decoration: underline; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ccc; padding: 0.5em 0.8em; text-align: left; }
  img { max-width: 100%; }
</style>
</head>
<body>
${rendered}
</body>
</html>
`
          res.end(html)
        } catch {
          res.statusCode = 500
          res.setHeader('Content-Type', 'text/plain; charset=utf-8')
          res.end(`Failed to render markdown: ${relative}`)
        }
        return
      }
      // Streamed from the descriptor the checks above judged, never from a name reopened here.
      streamChecked(res, file)
    })
  }

  return {
    name: 'serve-workbench-repository-files',
    configureServer(server) {
      attach(server.middlewares)
    },
    configurePreviewServer(server) {
      attach(server.middlewares)
    },
  }
}

// The proxy target is configurable so each worktree/demo launch can point at its own backend
// port without repointing the shared default. `VITE_API_TARGET` (read via `loadEnv`, not
// `import.meta.env`, since this file runs in Node at config-load time, not in the browser)
// defaults to the existing `:8000`; a demo launch sets it to `:8010`. The `/api` path
// convention — and `ws: true`, which lets the same proxy entry carry the terminal websocket
// upgrade (`/api/v1/demo/terminal/ws`) alongside ordinary HTTP `/api` calls — stay unchanged.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [
      refuseSymlinkEscapes(__dirname, devServerAllow, {
        [WORKBENCH_LAYOUTS_PREFIX]: workbenchLayoutsDir,
      }),
      react(),
      serveGeneratedOverview(),
      serveWorkbenchLayouts(),
      // Gated: `/workbench-file/*` serves raw bytes of any non-ignored repository file, the same
      // capability class ADR-015 rule 1 requires behind `D_SYSTEM_DEMO_TERMINAL=1` for every
      // workbench route. `env` here is `loadEnv`'s result, which reads both this process's own
      // environment and any `.env` file — a normal `npm run dev` (flag unset) never registers
      // this plugin, so the route does not exist, matching the backend's own "unimported means
      // absent" gate in `src/api/__init__.py`. A demo launch must set the flag for this frontend
      // process too (not only the backend's), not merely have it on the backend's environment.
      ...(env.D_SYSTEM_DEMO_TERMINAL === '1' ? [serveRepositoryFiles()] : []),
    ],
    server: {
      // `ts/` itself (the default) plus the workbench data directory: the page imports the slot
      // schema and panel element files from `_data/workbench/`. Vite checks this list by path
      // prefix only, so on its own it does not stop a symlink under either directory from serving
      // a file elsewhere; `refuseSymlinkEscapes` (first in `plugins`) refuses those requests.
      fs: { allow: devServerAllow },
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          ws: true,
        },
      },
    },
  }
})
