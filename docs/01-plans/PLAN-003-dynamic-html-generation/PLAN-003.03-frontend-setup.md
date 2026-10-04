---
schema_version: 1
id: doc-html-03-frontend-setup
code: PLAN-003.03
title: "Frontend Setup \u2014 Dependencies, Tailwind, Router, Entry Point"
kind: plan
status: deprecated
owner: repository-owner
created: '2026-09-05'
updated: '2026-10-04'
systems:
- sys-html
depends_on: []
parent: doc-html-00-overview
---

> Delivery is approved in phases. The [accepted user choices](../../08-governance/GOV-003-backlog-decisions.md) resolve conflicting details below; the [session backlog](../../09-backlog/README.md) tracks execution and completion. This document is a design source, not evidence of implementation.

# Frontend Setup — Dependencies, Tailwind, Router, Entry Point

## Dependencies

### [MODIFY] `ts/package.json`

```bash
cd ts && npm install react-router-dom@^6.30.0
cd ts && npm install -D tailwindcss @tailwindcss/vite
```

| Package | Type | Purpose |
|---|---|---|
| `react-router-dom` | dependency | Client-side routing with data API |
| `tailwindcss` | devDependency | Tailwind CSS v4 engine |
| `@tailwindcss/vite` | devDependency | First-party Vite plugin (replaces PostCSS) |

> **Note**: No `postcss`, `autoprefixer`, or `@types/react-router-dom` needed. Tailwind v4 uses Lightning CSS internally, and React Router v6 ships its own TypeScript types.

---

## Vite Configuration

### [MODIFY] `ts/vite.config.ts`

Add the Tailwind v4 Vite plugin:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

---

## Tailwind CSS v4 — Design Tokens

### [NEW] `ts/src/index.css`

Tailwind v4 uses CSS-first configuration via `@theme` directives. No `tailwind.config.ts` needed.

```css
@import "tailwindcss";

@theme {
  /* Colors */
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;
  --color-secondary: #475569;
  --color-surface: #ffffff;
  --color-surface-alt: #f8fafc;
  --color-text: #0f172a;
  --color-text-muted: #64748b;
  --color-accent: #f59e0b;
  --color-danger: #ef4444;

  /* Fonts */
  --font-sans: "Inter", system-ui, -apple-system, sans-serif;
  --font-heading: "Georgia", serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Spacing overrides */
  --spacing-18: 4.5rem;
  --spacing-88: 22rem;

  /* Container */
  --container-max-width: 1200px;
}
```

The `@theme` block auto-generates utility classes: `--color-primary` creates `bg-primary`, `text-primary`, `border-primary`, etc.

---

## Router — Async Bootstrap

### [NEW] `ts/src/router.tsx`

Fetches site config from FastAPI at startup, dynamically builds the route tree.

```tsx
import { createBrowserRouter, RouteObject } from 'react-router-dom'
import RootLayout from './layouts/RootLayout'
import DynamicPage, { pageLoader } from './pages/DynamicPage'
import ErrorBoundary from './components/ErrorBoundary'
import NotFoundPage from './pages/NotFoundPage'
import type { SiteConfig } from './types/schema'

async function buildRouter(): Promise<ReturnType<typeof createBrowserRouter>> {
  const res = await fetch('/api/v1/pages/site-config')
  if (!res.ok) throw new Error(`Failed to load site config: ${res.statusText}`)
  const config: SiteConfig = await res.json()

  const pageRoutes: RouteObject[] = config.routes.map((route) => ({
    path: route.path === '/' ? undefined : route.path.replace(/^\//, ''),
    index: route.path === '/',
    element: <DynamicPage />,
    loader: (args) => pageLoader({ ...args, params: { ...args.params, pageId: route.pageId } }),
    errorElement: <ErrorBoundary />,
  }))

  return createBrowserRouter([
    {
      path: '/',
      element: <RootLayout config={config} />,
      errorElement: <ErrorBoundary />,
      children: [
        ...pageRoutes,
        { path: '*', element: <NotFoundPage /> },
      ],
    },
  ])
}

export const routerPromise = buildRouter()
```

### Key design choices:

- **Bootstrap pattern**: The router is created *after* fetching site config, so routes are fully dynamic.
- **Route-level loaders**: Each page route gets a `loader` that fetches its content from `/api/v1/pages/{pageId}` before rendering.
- **`pageId` injection**: The loader receives `pageId` via `params`, mapped from the site config's `routes[].pageId` field.

---

## Entry Point

### [MODIFY] `ts/src/main.tsx`

Replace static App mount with async router bootstrap:

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { routerPromise } from './router'

const root = createRoot(document.getElementById('root')!)

// Show loading state while site config loads
root.render(
  <StrictMode>
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-text-muted">Loading D-System...</p>
    </div>
  </StrictMode>,
)

// Once router is ready, mount the app
routerPromise.then((router) => {
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}).catch((err) => {
  root.render(
    <StrictMode>
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-danger">Failed to load D-System</h1>
          <p className="text-text-muted mt-2">{String(err)}</p>
        </div>
      </div>
    </StrictMode>,
  )
})
```

---

## Cleanup

### [DELETE] `ts/src/App.tsx`

The existing `App.tsx` is a placeholder (`<h1>D-System</h1>`). Its responsibilities are now handled by `RootLayout` + `RouterProvider`. No longer imported anywhere.

## Audit disposition (`phase-des-01`, 2026-10-04)

This plan is deprecated. On 2026-10-04 the owner retired the authored YAML content site that `PLAN-003` describes; [ADR-027](../../04-decisions/ADR-027-retire-plan-003.md) records the decision and what it leaves behind. Every requirement this document states is listed below with its disposition, as `REQ-021` R01 requires. Line numbers refer to this document above this section. An accomplished or superseded row names the shipped work, by file and commit or phase (`REQ-021` R03); a retired row gives the reason nothing will be built.

24 requirements: 2 accomplished, 3 superseded, 19 retired.

| Id | Line | Requirement | Disposition | Evidence or reason |
|---|---|---|---|---|
| 03-R1 | 26, 32 | Install `react-router-dom@^6.30.0` | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R2 | 27, 33 | Install `tailwindcss` (v4) as a dev dependency | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R3 | 27, 34 | Install `@tailwindcss/vite` | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R4 | 36 | No `postcss`, `autoprefixer` or `@types/react-router-dom` | retired | A constraint on an install that will not happen |
| 03-R5 | 44-55 | Add `tailwindcss()` to `ts/vite.config.ts` before `react()` | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R6 | 56-60 | Keep the `/api` proxy to the backend | accomplished | `ts/vite.config.ts` `server.proxy['/api']`, from b2b564b, defaulted to 127.0.0.1 in e1ab509, with an overridable target and `ws: true` for the demo terminal |
| 03-R7 | 68-73 | NEW `ts/src/index.css` with `@import "tailwindcss"`, no `tailwind.config.ts` | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R8 | 75-86 | `@theme` colour tokens (primary, secondary, surface, text, accent, danger and variants) | superseded | Colour roles for generated pages: `templates/styles/house-tokens.json` and the generated `templates/styles/house.css` (49b0ca2, `phase-des-07`) |
| 03-R9 | 89-91 | Font tokens: Inter, Georgia, JetBrains Mono | superseded | Font tokens `--display`, `--body`, `--label`, `--mono` in `templates/styles/house-tokens.json` and the generated `templates/styles/house.css` (49b0ca2, `phase-des-07`) |
| 03-R10 | 94-95 | Spacing overrides `--spacing-18`, `--spacing-88` | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R11 | 98 | `--container-max-width: 1200px` | superseded | The house page shell's width (`max-width: 1140px`, `templates/styles/house-components.css` line 35, 49b0ca2) |
| 03-R12 | 102 | `@theme` generates `bg-primary`-style utilities | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 03-R13 | 108 | NEW `ts/src/router.tsx` | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R14 | 110, 121-122 | Bootstrap: fetch `/api/v1/pages/site-config`, throw on failure | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 03-R15 | 125-127 | Map `config.routes` to route objects, `/` as the index | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R16 | 129, 152-153 | Each route's loader injects its `pageId` | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R17 | 130 | Each page route has `errorElement: <ErrorBoundary/>` | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R18 | 133-143 | Root route renders `RootLayout`, with a catch-all to `NotFoundPage` | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R19 | 146, 151 | `routerPromise` built once at module load | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R20 | 159-168, 185 | `main.tsx` imports `index.css` and mounts `RouterProvider` | retired | `ts/src/main.tsx` mounts `App`, which renders the stage (b30b685); the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 03-R21 | 172-179 | "Loading D-System..." while the site configuration loads | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 03-R22 | 188-199 | Bootstrap failure screen "Failed to load D-System" | retired | no `/api/v1/pages` backend will exist (ADR-027). The stage's missing error handling is idea 000569 |
| 03-R23 | 164, 174 | Keep `<StrictMode>` | accomplished | `ts/src/main.tsx` line 6, unchanged since b2b564b |
| 03-R24 | 206-208 | DELETE `ts/src/App.tsx` as an unused placeholder | retired | The premise is false: `ts/src/App.tsx` renders the stage (b30b685) and is `sys-ui` evidence |
