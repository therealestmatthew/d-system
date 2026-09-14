# Ruling: where markdown-to-HTML rendering happens (idea `000119`)

**Ruled by the repository owner, 2026-09-14.** Written for `phase-prog-02` (finalize the workbench
features and defects plan, `PLAN-027`, programme P11), whose own `next_action` reads "Rule on
`000119`'s render location first."

This file is settled input. It is not a proposal to re-litigate.

## The ruling

**Markdown-to-HTML rendering happens route-side, inside `serveRepositoryFiles` in
`ts/vite.config.ts`** — the plugin that already serves repository file bytes at
`/workbench-file/<path>`. Not in the frontend component, and not in a new backend route.

This matches the recommendation in `000119`'s own text ("route-side rendering makes both surfaces
consistent").

## Why

- **The bytes are already served there**, in both dev and preview — the plugin attaches through
  `configureServer` *and* `configurePreviewServer`. There is no FastAPI route serving file content
  at all: `ADR-015` deliberately scopes the workbench API to reporting paths, never content. This
  ruling leaves that rule intact and adds no new gated route surface.
- **One render path removes the collision by construction.** The sandboxed iframe in
  `HtmlViewerRegion` and idea `000109`'s double-click-to-new-tab both fetch the same
  `/workbench-file/` URL, so both get the same rendered output. `000119` exists precisely because a
  frontend-only render would leave `000109` showing raw markdown source for the one file type the
  same batch adds rendering for. Rendering at the route means there are not two paths to keep in
  agreement.
- **The security half needs no new work.** The plugin already sets
  `Content-Security-Policy: sandbox` on every response it serves, so a top-level navigation to a
  rendered `.md` inherits the same restrictions the iframe's `sandbox=""` attribute applies. This
  was already true and is unchanged by the ruling.

## Consequences for `phase-prog-02`'s requirement rows

These follow from the ruling and should be reflected in the P11 requirement rather than
rediscovered:

1. **`000110`'s verification is a browser assertion, not a unit test.** `ts/vite.config.ts` is not
   covered by `pytest`. The observable statement should be of the form "point the viewer at a known
   `.md` file and assert formatted output renders — headings, lists, code blocks and links — rather
   than raw source text", verified in a real browser.
2. **`CONTENT_TYPE_BY_EXTENSION` gains `.md` → `text/html; charset=utf-8`**, because the route now
   returns HTML in response to a markdown request. The map currently holds 16 entries and falls
   back to `application/octet-stream`.
3. **Close the `.htm` gap in the same pass.** `.htm` is already served by
   `CONTENT_TYPE_BY_EXTENSION` but is *not* selectable in the viewer, because
   `COMPATIBLE_EXTENSIONS` lists `.html` only. It is a one-word fix and it belongs with this work,
   not in its own phase.
4. **`000118` still sequences after rendering lands.** Adding `.md` to `COMPATIBLE_EXTENSIONS`
   (`ts/src/stage/HtmlViewerRegion.tsx:18`) before the route renders it would surface raw source in
   the viewer. `depends_on` must encode this; it is the whole reason `000118` was raised separately
   from `000110`.
5. **The markdown library is a serve-time dependency, not a runtime bundle import.** It is used
   inside the Vite config, so it does not ship in the application bundle. Do not size the work
   assuming a bundle-size cost or a client-side sanitization requirement — the CSP sandbox header
   already covers the latter.

## Ground truth these rows must describe

Verified against the repository at `9ea0eaf` on 2026-09-14:

- `ts/src/stage/HtmlViewerRegion.tsx:18` — `COMPATIBLE_EXTENSIONS = ['.html', '.svg']`. Single
  source for both the viewer's dropdown filter and the File Browser's "Open in HTML Viewer"
  visibility; `FileBrowserRegion.tsx:4` imports it rather than keeping a second copy.
- `src/api/routes/workbench.py` — `GET /api/v1/workbench/search` is extension-agnostic and filters
  on whatever `ext` values the caller passes. **No backend change is needed to widen the viewer's
  file types.** The two-type limit is entirely a frontend decision.
- `ts/vite.config.ts` — `serveRepositoryFiles` enforces the repository boundary with
  `realpathSync`, excludes `.git` case-insensitively with trailing-dot/space stripping, honours
  `git check-ignore`, and sets `Cache-Control: no-store` so the viewer's refresh control works.
  Rendering must be inserted **after** all of those checks, never before.

## Note for whoever edits `ts/vite.config.ts`

As of 2026-09-14 the primary checkout carried an uncommitted one-line change to this file — the
proxy target moved from `http://localhost:8000` to `http://127.0.0.1:8000`. It was left in place,
unowned by this ruling. Check whether it has landed before branching from `dev`, so the change is
not lost or duplicated.

## Scope boundary

This ruling decides **where** the rendering goes. It does not choose the markdown library, does not
specify the rendered output's styling, and does not do the work. Those belong to the implementation
phases `phase-prog-02` creates.
