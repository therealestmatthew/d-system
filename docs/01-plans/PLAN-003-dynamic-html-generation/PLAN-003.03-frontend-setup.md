---
schema_version: 1
id: doc-html-03-frontend-setup
code: PLAN-003.03
title: "Frontend Setup \u2014 Dependencies, Tailwind, Router, Entry Point"
kind: plan
status: approved
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
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
