import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// The playground (index.html -> src/react/playground/main.tsx) and the React unit tests.
// Port 5199 with strictPort so the playground never silently lands on another server's port.
export default defineConfig({
  plugins: [react()],
  server: { port: 5199, strictPort: true },
  preview: { port: 5199, strictPort: true },
  build: { outDir: 'playground-dist', emptyOutDir: true },
  test: {
    environment: 'jsdom',
    include: ['src/react/**/*.test.tsx'],
    setupFiles: ['./vitest.setup.ts'],
    // axe over the full playground composite takes several seconds under a parallel run.
    testTimeout: 30000,
  },
})
