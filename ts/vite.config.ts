import { spawnSync } from 'node:child_process'
import { createReadStream, existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { basename, extname, join, normalize, resolve, sep } from 'node:path'
import { defineConfig, loadEnv, type Connect, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { marked } from 'marked'

// The repo root, one directory above `ts/` (this file's own directory) — where `_public/` (the
// generated overview page's home, `phase-demo-04`) and `_data/` (repository data, including the
// workbench layout definitions, `phase-wb-02`) live.
const repoRoot = resolve(__dirname, '..')
const publicDir = join(repoRoot, '_public')
const workbenchLayoutsDir = join(repoRoot, '_data', 'workbench', 'layouts')
// The symlink-resolved repo root — `serveRepositoryFiles`'s boundary check below must compare
// against this, not the textual `repoRoot`, so a symlinked worktree checkout itself doesn't
// widen the boundary it is meant to enforce.
const realRepoRoot = realpathSync(repoRoot)

const GENERATED_OVERVIEW_PREFIX = '/generated-overview/'
const WORKBENCH_LAYOUTS_PREFIX = '/workbench-layouts/'
const WORKBENCH_FILE_PREFIX = '/workbench-file/'

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
function serveGeneratedOverview(): Plugin {
  const attach = (middlewares: Connect.Server) => {
    middlewares.use(GENERATED_OVERVIEW_PREFIX, (req, res) => {
      const requestedPath = decodeURIComponent((req.url ?? '').split('?')[0] ?? '')
      const resolved = normalize(join(publicDir, requestedPath))
      // Refuse anything that escapes `_public/` (defends against `../` traversal).
      if (resolved !== publicDir && !resolved.startsWith(publicDir + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      if (!existsSync(resolved) || !statSync(resolved).isFile()) {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Generated overview page not found at ${resolved}.`)
        return
      }
      res.statusCode = 200
      res.setHeader('Content-Type', 'text/html; charset=utf-8')
      createReadStream(resolved).pipe(res)
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
function serveWorkbenchLayouts(): Plugin {
  const attach = (middlewares: Connect.Server) => {
    middlewares.use(WORKBENCH_LAYOUTS_PREFIX, (req, res) => {
      const requestedPath = decodeURIComponent((req.url ?? '').split('?')[0] ?? '')
      const resolved = normalize(join(workbenchLayoutsDir, requestedPath))
      if (resolved !== workbenchLayoutsDir && !resolved.startsWith(workbenchLayoutsDir + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      if (!existsSync(resolved) || !statSync(resolved).isFile()) {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Layout definition not found at ${resolved}.`)
        return
      }
      res.statusCode = 200
      res.setHeader('Content-Type', 'application/json; charset=utf-8')
      createReadStream(resolved).pipe(res)
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
function isGitIgnored(repoRelativePath: string): boolean {
  const result = spawnSync('git', ['check-ignore', '-q', repoRelativePath], { cwd: repoRoot })
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

function serveRepositoryFiles(): Plugin {
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
      const resolved = normalize(join(repoRoot, relative))
      if (resolved !== repoRoot && !resolved.startsWith(repoRoot + sep)) {
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
      if (!existsSync(resolved) || !statSync(resolved).isFile()) {
        res.statusCode = 404
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.end(`Not found: ${relative}`)
        return
      }
      // Resolve symlinks before trusting the boundary check above: `resolved` there is only
      // textually normalized (`normalize`/`join`, matching `serveGeneratedOverview`'s and
      // `serveWorkbenchLayouts`'s own string-containment checks), so a symlink under the
      // repository whose target lands outside it — e.g. `_public/evil-link.txt` pointing outside
      // the repo root — passes that check untouched and would still serve the outside file's
      // bytes. The backend's own boundary (`src/api/routes/workbench.py`'s
      // `resolve_repo_relative_path`) uses `Path.resolve()`, which follows symlinks, for exactly
      // this reason (ADR-015 rule 2: "symlinks whose resolved target leaves the root");
      // `realpathSync` is Node's equivalent, and by this point `existsSync` above has already
      // confirmed the symlink chain resolves to a real file, so this cannot throw for the paths
      // that reach it.
      const realResolved = realpathSync(resolved)
      if (realResolved !== realRepoRoot && !realResolved.startsWith(realRepoRoot + sep)) {
        res.statusCode = 403
        res.end('Forbidden')
        return
      }
      if (isGitIgnored(relative)) {
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
      const extensionLower = extname(realResolved).toLowerCase()
      if (RASTER_IMAGE_EXTENSIONS.has(extensionLower) && !query.has(RAW_IMAGE_QUERY_PARAM)) {
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
          const source = readFileSync(realResolved, 'utf-8')
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
      // Stream from the already-`realpathSync`-resolved path, not the textually-normalized
      // `resolved` re-opened here: re-deriving bytes from `resolved` after the symlink-boundary
      // check above passed would reopen the original (possibly symlinked) path, leaving a
      // TOCTOU window between the check and the read where the symlink target could change: the
      // check would have validated one file but the stream would read whatever `resolved` points
      // to at read time. `realResolved` is the same file the check just validated.
      createReadStream(realResolved).pipe(res)
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
