import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Unit tests for the React stage, run with `npm test`. Kept apart from vite.config.ts, whose dev
// server plugins read the repository at startup and have no place in a test run.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.tsx'],
  },
})
