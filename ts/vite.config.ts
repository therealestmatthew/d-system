import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

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
    plugins: [react()],
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
