---
schema_version: 1
id: doc-ux-kit-on-react-aria
code: ADR-001
title: Build our own UX kit on React Aria Components and a token pipeline
kind: adr
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-ui-kit]
depends_on: []
---

# Build our own UX kit on React Aria Components and a token pipeline

## Context

The team is building one product for a demonstration in about three weeks. Several developers will
build screens at the same time, and agents will generate report pages from templates. Both need one
look, one keyboard model and one accessibility standard.

Two kinds of page need the kit:

- **The product app**, a React 19 + Vite + TypeScript single-page app.
- **Generated pages**: reports and run summaries produced by Python generators or by Claude filling
  a template. These must open anywhere (S3, email, offline), so they cannot depend on a JavaScript
  build.

An earlier internal workbench showed what goes wrong without a kit: hand-written CSS with colour
literals and no focus styles, and hand-written menus and a tree with no arrow-key navigation. Its
token pipeline (one JSON file generating CSS deterministically, with light and dark themes) and its
template filler worked well and are reused.

The owner decided the following on 2026-10-14: an own kit on headless primitives, styled with our
tokens; Cloudscape's generative-AI patterns as the specification only; React 19 + Vite +
TypeScript; React Aria Components as the behaviour library; Python generators; the kit built now in
`ui-kit/` in the control repository and moved to `product:packages/ui/` later.

## Decision

1. **Tokens.** `ui-kit/tokens/tokens.json` is the single source of colour, type, spacing, radius,
   elevation, motion and focus values, for light and dark and for each candidate accent.
   `ui-kit/tools/build_tokens.py` generates `ui-kit/dist/tokens.css` from it deterministically.
2. **CSS class contract.** Hand-written component CSS under `ui-kit/src/css/` uses only `--ui-`
   custom properties and expresses state through ARIA and data attributes.
3. **The app** uses React components in `ui-kit/src/react/` that take their behaviour from React
   Aria Components and render the class contract.
4. **Generated pages** use the same classes as static HTML, plus a small `ui.js` of declared
   behaviours; a page that declares none ships no script.
5. **The AI and agent components** follow Cloudscape's generative-AI patterns as their
   specification (loading states, progressive steps, user-authorized actions, output label, support
   prompts, artifact previews). Cloudscape's components are not used.

## Alternatives considered

| Alternative | What it would give | What it would cost |
|---|---|---|
| Adopt Cloudscape wholesale | Apache-2.0 React components, chat components, WCAG conformance, dark mode and compact density with no build effort. | Theming is limited to brand colours, typeface and radius, so the product looks like the AWS console. The package is heavy. It does not serve generated static pages, and it clashes with the workbench-style shell and panel model. |
| Radix Primitives, or shadcn/ui with Tailwind | Fast, polished React with code the team owns and correct ARIA behaviour. | Radix lacks table and tree. With shadcn/ui and Tailwind, generated static pages need a Tailwind build or utility classes that cannot be checked against a class allowlist, tokens are defined twice, and the existing token and template pipeline is dropped. This is the main credible alternative if the team already knows it. |
| React only, with static pages rendered by `renderToStaticMarkup` | One implementation. | Generated reports need a Node render step, so Python generators and Claude-written pages cannot use the kit directly, and static pages lose interactivity unless hydrated. |
| Plain HTML, CSS and vanilla JavaScript only (or Lit web components) | One implementation for both consumers. | React developers wrap imperative widgets and keep state in sync by hand. Accessibility behaviour is hand-written again, which is exactly where the earlier workbench failed. |

## Consequences

- About eight behaviours exist twice: once in React Aria for the app and once in `ui.js` for static
  pages. The static set is kept small (sections, CSS-only tabs, table sort and filter, in-page
  search, toggletip, copy, theme), and the command palette, tree and dialogs are app-only. A test
  that compares React output with the catalogue markup (REQ-001 R12) keeps the two on one class
  contract.
- The app depends on `react-aria-components`. Its bundle size counts against the 200 KB initial
  JavaScript budget in the design guide.
- The kit's look is ours and can follow the accent the owner chooses from the theme sheet.
- Python generators and Claude can produce on-system pages without Node, because `dist/tokens.css`
  is committed.
- Building the kit in the control repository puts product code in the process repository for a
  time. The move to `product:packages/ui/` is a later change that updates this repository's
  system paths and phase deliverables.

## Revisit when

- React Aria Components lacks a widget the product needs, or its bundle pushes the app past its
  JavaScript budget.
- The team decides the product should look like the AWS console, which would favour Cloudscape.
- The static and React behaviours drift and the catalogue comparison test cannot hold them
  together.
- The kit moves to the product repository.
