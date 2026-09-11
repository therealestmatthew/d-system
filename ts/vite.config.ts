import { createReadStream, existsSync, statSync } from 'node:fs'
import { join, normalize, resolve, sep } from 'node:path'
import { defineConfig, loadEnv, type Connect, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

// The repo root, one directory above `ts/` (this file's own directory) — where `_public/` (the
// generated overview page's home, `phase-demo-04`) and `_data/` (repository data, including the
// workbench layout definitions, `phase-wb-02`) live.
const repoRoot = resolve(__dirname, '..')
const publicDir = join(repoRoot, '_public')
const workbenchLayoutsDir = join(repoRoot, '_data', 'workbench', 'layouts')

const GENERATED_OVERVIEW_PREFIX = '/generated-overview/'
const WORKBENCH_LAYOUTS_PREFIX = '/workbench-layouts/'

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

// The proxy target is configurable so each worktree/demo launch can point at its own backend
// port without repointing the shared default. `VITE_API_TARGET` (read via `loadEnv`, not
// `import.meta.env`, since this file runs in Node at config-load time, not in the browser)
// defaults to the existing `:8000`; a demo launch sets it to `:8010`. The `/api` path
// convention — and `ws: true`, which lets the same proxy entry carry the terminal websocket
// upgrade (`/api/v1/demo/terminal/ws`) alongside ordinary HTTP `/api` calls — stay unchanged.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET || 'http://localhost:8000'

  return {
    plugins: [react(), serveGeneratedOverview(), serveWorkbenchLayouts()],
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
