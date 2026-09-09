---
schema_version: 1
id: doc-html-04-frontend-components
code: PLAN-003.04
title: "Frontend Components \u2014 Types, Layout, Pages, Blocks"
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

# Frontend Components — Types, Layout, Pages, Blocks

## TypeScript Types

### [NEW] `ts/src/types/schema.ts`

Discriminated union for type-safe block content. Ensures exhaustive switch handling in `BlockRenderer`.

```typescript
// --- Block content types ---

export interface HeroContent {
  headline: string;
  subheadline?: string;
  ctaText?: string;
  ctaLink?: string;
}

export interface TextContent {
  body: string;
  heading?: string;
}

export interface ImageContent {
  src: string;
  alt: string;
  caption?: string;
}

export interface ColumnsContent {
  columns: Array<{
    heading?: string;
    body: string;
  }>;
}

// --- Discriminated union for blocks ---

interface BaseBlock {
  id: string;
}

export type BlockData =
  | (BaseBlock & { type: 'hero'; content: HeroContent })
  | (BaseBlock & { type: 'text'; content: TextContent })
  | (BaseBlock & { type: 'image'; content: ImageContent })
  | (BaseBlock & { type: 'columns'; content: ColumnsContent });

// --- Page & Site types ---

export interface PageData {
  title: string;
  template: 'standard' | 'landing';
  description?: string;
  blocks: BlockData[];
}

export interface RouteConfig {
  path: string;
  pageId: string;
  label?: string;
}

export interface NavItem {
  label: string;
  path: string;
}

export interface SiteConfig {
  title: string;
  routes: RouteConfig[];
  navigation?: NavItem[];
}
```

> **Design Note**: Using a discriminated union (`BlockData`) instead of `content: any` gives exhaustive type checking in `BlockRenderer`'s switch statement. Adding a new block type to the union without adding a case will produce a compile-time error.

---

## Layout

### [NEW] `ts/src/layouts/RootLayout.tsx`

App shell with navigation bar, loading indicator, and `<Outlet>` for child routes.

```tsx
import { Outlet, Link, useNavigation } from 'react-router-dom'
import type { SiteConfig } from '../types/schema'

interface RootLayoutProps {
  config: SiteConfig;
}

export default function RootLayout({ config }: RootLayoutProps) {
  const navigation = useNavigation()
  const isLoading = navigation.state === 'loading'

  return (
    <div className="min-h-screen bg-surface text-text">
      <header className="bg-surface border-b border-secondary/20 px-6 py-4">
        <div className="max-w-[var(--container-max-width)] mx-auto flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-primary font-heading">
            {config.title}
          </Link>
          <nav className="flex gap-4">
            {(config.navigation ?? []).map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-text-muted hover:text-primary transition-colors"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        {isLoading && (
          <div className="h-0.5 bg-primary animate-pulse" />
        )}
      </header>

      <main className="max-w-[var(--container-max-width)] mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
```

---

## Pages

### [NEW] `ts/src/pages/DynamicPage.tsx`

Route component with a `loader` that fetches page config from FastAPI. Uses `request.signal` for automatic fetch cancellation on navigation.

```tsx
import { useLoaderData } from 'react-router-dom'
import type { LoaderFunctionArgs } from 'react-router-dom'
import type { PageData } from '../types/schema'
import BlockRenderer from '../components/BlockRenderer'

export async function pageLoader({ params, request }: LoaderFunctionArgs): Promise<PageData> {
  const pageId = params.pageId
  if (!pageId) {
    throw new Response('Page ID is required', { status: 400 })
  }

  const res = await fetch(`/api/v1/pages/${encodeURIComponent(pageId)}`, {
    signal: request.signal,
    headers: { Accept: 'application/json' },
  })

  if (res.status === 404) {
    throw new Response(`Page "${pageId}" not found`, { status: 404 })
  }
  if (!res.ok) {
    throw new Response(`Failed to load page: ${res.statusText}`, { status: res.status })
  }

  return res.json()
}

export default function DynamicPage() {
  const page = useLoaderData() as PageData

  return (
    <article>
      <h1 className="text-3xl font-bold font-heading mb-2">{page.title}</h1>
      {page.description && (
        <p className="text-text-muted mb-8">{page.description}</p>
      )}
      <div className="space-y-8">
        {page.blocks.map((block) => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </div>
    </article>
  )
}
```

---

### [NEW] `ts/src/pages/NotFoundPage.tsx`

Catch-all for unmatched routes.

```tsx
import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="text-center py-20">
      <h1 className="text-6xl font-bold text-text-muted">404</h1>
      <p className="text-xl text-text-muted mt-4">Page not found</p>
      <Link to="/" className="inline-block mt-6 text-primary hover:underline">
        ← Back to home
      </Link>
    </div>
  )
}
```

---

## Error Boundary

### [NEW] `ts/src/components/ErrorBoundary.tsx`

Handles errors from loaders (thrown `Response` objects) and component rendering (JS errors).

```tsx
import { useRouteError, isRouteErrorResponse, Link, useNavigate } from 'react-router-dom'

export default function ErrorBoundary() {
  const error = useRouteError()
  const navigate = useNavigate()

  let status = 500
  let message = 'An unexpected error occurred.'

  if (isRouteErrorResponse(error)) {
    status = error.status
    message = typeof error.data === 'string' ? error.data : error.statusText
  } else if (error instanceof Error) {
    message = error.message
  }

  return (
    <div className="text-center py-20">
      <h1 className="text-4xl font-bold text-danger">{status}</h1>
      <p className="text-text-muted mt-2">{message}</p>
      <div className="mt-6 flex gap-4 justify-center">
        <button
          onClick={() => navigate(0)}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
        >
          Retry
        </button>
        <Link to="/" className="px-4 py-2 text-primary hover:underline">
          Home
        </Link>
      </div>
    </div>
  )
}
```

---

## Block Renderer — Factory

### [NEW] `ts/src/components/BlockRenderer.tsx`

Maps block `type` → React component. Uses TypeScript exhaustiveness checking via the `never` type in the default case.

```tsx
import type { BlockData } from '../types/schema'
import HeroBlock from './blocks/HeroBlock'
import TextBlock from './blocks/TextBlock'
import ImageBlock from './blocks/ImageBlock'
import ColumnsBlock from './blocks/ColumnsBlock'

interface BlockRendererProps {
  block: BlockData;
}

export default function BlockRenderer({ block }: BlockRendererProps) {
  switch (block.type) {
    case 'hero':
      return <HeroBlock content={block.content} />
    case 'text':
      return <TextBlock content={block.content} />
    case 'image':
      return <ImageBlock content={block.content} />
    case 'columns':
      return <ColumnsBlock content={block.content} />
    default: {
      const _exhaustive: never = block
      return <div className="text-danger">Unknown block type: {(_exhaustive as BlockData).type}</div>
    }
  }
}
```

---

## Block Components

### [NEW] `ts/src/components/blocks/HeroBlock.tsx`

```tsx
import type { HeroContent } from '../../types/schema'

export default function HeroBlock({ content }: { content: HeroContent }) {
  return (
    <section className="bg-primary text-white rounded-lg px-8 py-16 text-center">
      <h2 className="text-4xl font-bold font-heading">{content.headline}</h2>
      {content.subheadline && (
        <p className="text-xl mt-4 opacity-90">{content.subheadline}</p>
      )}
      {content.ctaText && content.ctaLink && (
        <a
          href={content.ctaLink}
          className="inline-block mt-8 px-6 py-3 bg-white text-primary font-semibold rounded hover:bg-surface-alt transition-colors"
        >
          {content.ctaText}
        </a>
      )}
    </section>
  )
}
```

---

### [NEW] `ts/src/components/blocks/TextBlock.tsx`

```tsx
import type { TextContent } from '../../types/schema'

export default function TextBlock({ content }: { content: TextContent }) {
  return (
    <section className="prose max-w-none">
      {content.heading && (
        <h3 className="text-2xl font-bold font-heading mb-3">{content.heading}</h3>
      )}
      <p className="text-text leading-relaxed whitespace-pre-line">{content.body}</p>
    </section>
  )
}
```

---

### [NEW] `ts/src/components/blocks/ImageBlock.tsx`

```tsx
import type { ImageContent } from '../../types/schema'

export default function ImageBlock({ content }: { content: ImageContent }) {
  return (
    <figure className="rounded-lg overflow-hidden">
      <img
        src={content.src}
        alt={content.alt}
        className="w-full h-auto"
        loading="lazy"
      />
      {content.caption && (
        <figcaption className="text-sm text-text-muted mt-2 text-center">
          {content.caption}
        </figcaption>
      )}
    </figure>
  )
}
```

---

### [NEW] `ts/src/components/blocks/ColumnsBlock.tsx`

```tsx
import type { ColumnsContent } from '../../types/schema'

export default function ColumnsBlock({ content }: { content: ColumnsContent }) {
  const colCount = content.columns.length
  return (
    <section
      className="grid gap-6 grid-cols-1"
      style={{ gridTemplateColumns: `repeat(${colCount}, minmax(0, 1fr))` }}
    >
      {content.columns.map((col, i) => (
        <div key={i} className="bg-surface-alt rounded-lg p-6">
          {col.heading && (
            <h4 className="text-lg font-bold mb-2">{col.heading}</h4>
          )}
          <p className="text-text-muted">{col.body}</p>
        </div>
      ))}
    </section>
  )
}
```

> **Note**: Uses inline `style` for `gridTemplateColumns` instead of dynamic Tailwind `grid-cols-${n}` classes, which would require safelisting. The `grid-cols-1` class serves as the mobile-first fallback, overridden by the inline style on wider screens.
