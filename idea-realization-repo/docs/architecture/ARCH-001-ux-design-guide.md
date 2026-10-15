---
schema_version: 1
id: doc-ux-design-guide
code: ARCH-001
title: UX design guide for the component kit
kind: architecture
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-ui-kit]
depends_on: []
---

# UX design guide for the component kit

## Purpose and scope

This guide states the design principles, the guidelines and the component set for the team's UX
component kit. It governs two consumers:

- **The product app**: a React 19 + Vite + TypeScript single-page app. Its components are built on
  React Aria Components (headless, unstyled behaviour) and styled with the kit's tokens and CSS.
- **Generated pages**: reports, run summaries and status pages written by Python generators or by
  Claude from a template. They use the kit's static HTML and CSS, plus a small declared script file
  (`ui.js`) only where a page needs a behaviour.

The kit lives in the top-level `ui-kit/` folder of this control repository for now. It is planned
to move to `product:packages/ui/` in the product repository later; paths in this guide are written
as `ui-kit/...` until then.

The architecture choice is recorded in the component kit decision (`ADR-001`). The observable
requirements are in the kit requirements (`REQ-001`), and the work is planned in the kit plan
(`PLAN-003`).

The patterns here were extracted from an earlier internal workbench and report generator. Where
this guide differs from that source, this guide is the authority.

## Owner rulings this guide follows

| Topic | Ruling |
|---|---|
| Kit base | Own kit on React Aria Components, styled with our tokens. Cloudscape's generative-AI patterns are the specification for the AI and agent set; Cloudscape components are not used. |
| App framework | React 19 + Vite + TypeScript single-page app. |
| Location | `ui-kit/` in the control repository now; `product:packages/ui/` later. |
| Theme | Light and dark from the start. The page follows the system setting, a toggle overrides it, and presentations run in light. |
| Accent | Not yet chosen. The kit ships named candidate accents, switched with `data-accent`, and a theme sheet (`ui-kit/gallery/theme-sheet.html`) for the owner to choose from. |
| Type | The system sans-serif stack everywhere. No webfonts. |
| Generators | Python. |
| Layout | A fixed layout-as-data shell. No runtime panel reassignment and no layout persistence. |
| Hosting | The app is hosted on AWS Amplify Hosting. The custom domain and AWS WAF are not yet decided. |
| Table sort control | The column header cell itself is the pressable sort control, with `aria-sort` on it (the React Aria form), not a button inside the header (2026-10-14). |
| Toast announcements | React Aria's toast announces every toast assertively. Accepted for now as a known gap; revisit when React Aria's toast is stable (2026-10-14). |

## Principles

Each principle has its reason and what to do and not do.

1. **One focal surface per screen, one accent per view.** A viewer has seconds to find the result.
   *Do:* one primary button per panel; use the accent only on the primary action, the active
   navigation item and links. *Don't:* use the accent for decoration or for status. Status uses the
   status colours.
2. **Dense in the app, generous in reports.** Operators scan tools; readers read reports. *Do:* app
   body text 13–14px on a 4px grid with 28–32px controls; report body text 16–17px with a 64ch
   measure. *Don't:* use report type sizes in a data table, or a 12px table in a report.
3. **Layout and look are data, not code.** Several developers produce consistent screens only when
   the kit makes the choices. *Do:* change `tokens/tokens.json` or a layout JSON file and
   regenerate. *Don't:* write a colour literal or pixel geometry in component CSS; a test fails it.
4. **Reveal in place; the app never scrolls as a page.** Context stays on screen. *Do:* use tabs,
   accordions, popovers and the panel maximize action. *Don't:* let the app shell scroll as a page
   or open new windows for detail.
5. **Every asynchronous surface has named states:** `idle`, `loading`, `empty`, `error` and
   `missing` (the capability is unavailable). A blank surface reads as broken. *Do:* show
   "Searching…" with `role="status"` within 100ms, and "not recorded" when data is absent.
   *Don't:* render a blank panel or a made-up zero.
6. **Contain errors, explain them, offer the next step.** One failing model call must not blank the
   screen. *Do:* a per-panel error boundary that says what failed, why if known, and offers Retry;
   throttling reads as "Claude is busy, retrying in 4s". *Don't:* show a global error page, a raw
   stack trace, or "Something went wrong" with no action.
7. **Destructive or irreversible actions confirm in place; reversible ones do not.** *Do:* an inline
   "Close session? This ends the shell. [Close] [Cancel]". *Don't:* confirm a restore, or use
   `window.confirm`.
8. **Hidden versus disabled.** An action that can never apply here is hidden. An action that applies
   but is unavailable now is disabled, with the reason shown. *Don't:* hide a primary action that is
   only temporarily unavailable.
9. **WCAG 2.2 AA is a build gate, not a review note.**
   - Contrast: text at least 4.5:1; large text and interface parts at least 3:1; the focus
     indicator at least 3:1 against adjacent colours. A token test checks every declared pair in
     both themes and for every candidate accent.
   - Focus: a visible `:focus-visible` ring on every interactive element; never hidden under a
     sticky bar (2.4.11); focus returns to the trigger when an overlay closes.
   - Keyboard: every action is reachable. Composite widgets (toolbar, menu, tabs, tree, grid,
     listbox) use roving focus and arrow keys. Escape closes the top overlay.
   - Target size: at least 24×24 CSS px (2.5.8). Every drag action has a non-drag alternative
     (2.5.7).
   - ARIA: native elements first (`button`, `details`, `dialog`, `table`); ARIA Authoring Practices
     patterns applied exactly; live regions polite for streaming, assertive only for blocking
     errors.
   - *Don't:* use `role="menu"` without arrow keys, a `div` as a button, or a tooltip as the only
     place essential information appears.
10. **Desktop-first app, fluid reports.** The product is shown on a laptop or projector. *Do:* test
    the shell at 1024x768, 1280x720, 1366x768 and 1920x1080, with compact density below 1100×800.
    Reports reflow down to 360px wide. *Don't:* promise a mobile app. Below 1024px wide the shell
    stacks its panels and page scroll is allowed.
11. **Motion is functional, 120–280ms, and off under `prefers-reduced-motion`.** *Do:* fade and
    scale popovers, slide toasts, show a streaming caret. *Don't:* use parallax, auto-playing
    marquees without a pause, or animation over 300ms on frequent actions.
12. **Light and dark are one token switch that changes colours only.** *Do:* follow
    `prefers-color-scheme`, allow a `data-theme` override, provide a toggle. *Don't:* write
    per-component dark rules or dark-only colour literals.
13. **Plain microcopy.** Sentence case, a verb on every button, specific nouns, and a plain
    statement of the system's limits. *Do:* "Generate report", "Claude is drafting (step 2 of 4)",
    "No findings yet. Upload a file to start." *Don't:* "Submit", "Oops!", "AI magic", or claims
    that the system understands or feels.
14. **Every number and every AI claim names its source and time.** *Do:* a stamp (source, model,
    time) on every generated artefact and citation chips on claims. *Don't:* estimate a missing
    value, or say "as of now" without a timestamp.
15. **Static first, script declared.** Generated reports must open anywhere: S3, email, offline.
    *Do:* script-free components by default (`details`, CSS-only tabs, static SVG); each script
    behaviour is declared in the component manifest. *Don't:* require script to read a report.
16. **No runtime external dependency.** Venue networks fail. *Do:* the system font stack, vendored
    icons, CSS inlined into generated reports. *Don't:* load webfonts or an icon CDN.
17. **Performance budgets**, measured rather than assumed:

    | Item | Budget |
    |---|---|
    | `ui.css` (tokens and components) | ≤25 KB gzip |
    | `ui.js` static behaviours | ≤8 KB gzip |
    | App initial JavaScript | ≤200 KB gzip |
    | Largest contentful paint on the demo laptop | ≤2.0s |
    | Interaction to next paint | ≤200ms |
    | Report page, excluding data | ≤150 KB |
    | Client-side filter of 1,000 rows | ≤50ms |
    | Table rows before virtualization | 500 |
    | Streaming | "Working" indicator ≤100ms after send; each token rendered when it arrives |

18. **One table model.** Server ranking is the truth; client sort and filter are a view of it.
    *Do:* sticky header, right-aligned tabular numerals, monospace ids, a three-state header sort
    with `aria-sort`, filter chips with a result count ("42 of 310"), clear-all. *Don't:* re-rank
    client-side in a way that contradicts the server order, or paginate under 200 rows.
19. **The model's work is visible, interruptible, attributable and gated.**
    - Streaming renders incrementally with a Stop button and announces politely at a throttle (per
      sentence or each second), never per token.
    - Plans and tool calls show as a collapsible run timeline.
    - Citation chips link to the source (S3 object, knowledge-base chunk, URL).
    - Confidence is shown only when it is computed (retrieval score, evaluation), as a category
      with its basis, never as an invented percentage.
    - Any external side effect (send, write, deploy, spend) stops at an approval card with a
      preview or diff, Approve / Edit / Reject, and a record of who decided and when.
    - A model badge names the model ("Claude via Amazon Bedrock") and shows tokens, latency and
      cost when known.
    - Generated or model-written HTML is sanitized for inline display or shown in a sandboxed
      iframe.
    - *Don't:* stream into a live region per token, run a side effect without approval, or mix AI
      text and human text without a marker.

## Guidelines

### Design tokens

The single source is `ui-kit/tokens/tokens.json`. `ui-kit/tools/build_tokens.py` generates
`ui-kit/dist/tokens.css` from it, deterministically, with a `--check` mode that fails when the
committed CSS is stale. Every CSS variable is prefixed `--ui-`.

- **Colour roles**, defined for light and dark:
  - Surfaces: `bg`, `surface` (panels), `surface-2` (raised: menus, popovers), `sunken` (code,
    inputs).
  - Lines: `line`, `line-strong`.
  - Text: `text`, `muted` (at least 4.5:1 on `bg` and `surface`), `on-accent`.
  - Accent: `accent`, `accent-hover`, `accent-2` (a second series), `focus` (the focus ring).
  - Utility: `selection`, `overlay` (the scrim behind a modal).
  - Status: `ok`, `warn`, `info`, `err`, each with a `-bg` pair.
  - `ai`: a hue that marks machine-generated content and agent activity, distinct from the status
    colours.
  - A chart categorical palette, kept as a separate group.
- **Candidate accents.** The accent roles (`accent`, `accent-hover`, `on-accent`, `focus` where it
  derives from the accent) are defined once per named candidate, for light and dark. The root
  attribute `data-accent="<name>"` selects a candidate; without it the default candidate applies.
  The theme sheet, `ui-kit/gallery/theme-sheet.html`, shows every candidate in both themes so the
  owner can choose one. Once chosen, the others may be removed.
- **Type.** `font-sans` is the system sans-serif stack and is used for the app and for reports.
  `font-mono` is the system monospace stack. Both end in a generic family.
  - App scale: `fs-xs 12`, `sm 13`, `md 14`, `lg 16`, `xl 20`, `2xl 24`, `3xl 32` (px). Line height
    1.45 for interface text and 1.6 for prose. Weights 400, 600 and 700.
  - Report scale: body 17px, with larger headings.
- **Density and variants.** `data-density="compact|comfortable"` and
  `data-variant="report|app"`. These change type and spacing only and set no colour.
- **Spacing** on a 4px base: `space-0 0`, `1 2`, `2 4`, `3 8`, `4 12`, `5 16`, `6 24`, `7 32`,
  `8 48`, `9 64`. Control heights: `ctl-sm 24`, `ctl-md 32`, `ctl-lg 40`; 24 is the WCAG 2.5.8
  floor.
- **Radius:** `r-0 0`, `r-sm 4`, `r-md 6`, `r-lg 10`, `r-pill 999`.
- **Elevation:** `e0` border only (panels); `e1` menus, popovers, tooltips; `e2` dialogs; `e3`
  toasts. Light uses a shadow plus a border. Dark uses a lighter surface step plus a border, with
  little shadow.
- **Stacking order:** `base 0`, `sticky 100`, `dock 200`, `dropdown 1000`, `overlay 1100`,
  `modal 1200`, `toast 1300`, `tooltip 1400`. Prefer the browser top layer (`<dialog>`, the
  `popover` attribute), which makes most of these unnecessary.
- **Motion:** `dur-fast 120ms`, `dur-base 180ms`, `dur-slow 280ms`,
  `ease-standard cubic-bezier(.2,0,0,1)`, `ease-exit cubic-bezier(.4,0,1,1)`. Under reduced motion
  durations are 0 and only opacity changes.
- **Focus:** `focus-width 2px`, `focus-offset 2px`, colour `focus`.
- **Contrast pairs** are declared in the tokens file and asserted by a test, in both themes and for
  every candidate accent: text/bg, text/surface, muted/bg, muted/surface, on-accent/accent, accent
  on bg as text, each status foreground on its `-bg`, and focus/bg (at least 3:1).

### Layout grid

- **App shell:** a full-viewport CSS grid whose `grid-template-areas` and fractional tracks come
  from a layout file in `ui-kit/layouts/*.json` (regions plus grid).
  - Standard regions: `header` (app bar), `nav` (rail or side), `main`, `inspector`, `dock`
    (bottom console), `strip` (status).
  - Every track is wrapped in `minmax(0, …)`. Each panel body kind declares a minimum size in
    content units.
  - Tracks are fractions, never pixels.
  - Zero page scroll at 1024×768 and above.
  - The layout is fixed for the life of the page: no runtime panel reassignment and no saved
    layout.
- **Report page:** one column, `max-width: 1140px`, `padding-inline: clamp(16px, 4vw, 52px)`.
  - Prose is capped at 64ch.
  - Card grids use `repeat(auto-fit, minmax(16rem, 1fr))`.
  - Stats are four across, falling to two below 860px.

### Icons

- One open set, Lucide (ISC licence), vendored as an SVG sprite. 16px in dense interface, 20px by
  default, stroke 1.75, `currentColor`.
- An icon-only button has an `aria-label` and a tooltip.
- Primary and destructive actions are never icon-only.

### Naming

- CSS classes are BEM-style with a prefix: `ui-toolbar`, `ui-toolbar__group`,
  `ui-button--primary`.
- **State is expressed with ARIA or data attributes, not classes:** `[aria-expanded="true"]`,
  `[aria-selected]`, `[aria-current]`, `[data-state="loading"]`. The visual state then cannot
  differ from what assistive technology announces.
- React components use the PascalCase of the same name (`<Toolbar>`).
- Tokens are `--ui-<group>-<name>`.

### File layout

```
ui-kit/
  tokens/tokens.json            single source: light, dark, candidate accents, densities, contrast pairs
  tools/build_tokens.py         tokens.json to dist/tokens.css, with --check
  dist/tokens.css               generated and committed, so Python generators inline it without Node
  src/css/base.css layout.css   reset, type, focus ring, reduced motion; the shell grid
  src/css/components/*.css      one file per component
  src/react/                    React components on React Aria Components
  layouts/*.json                fixed shell layouts
  gallery/                      every component in every state, both themes; theme-sheet.html
  test/                         token, contract, lint and browser tests
```

Planned additions: `src/behaviours/` and `dist/ui.js` (static behaviours), `components.yaml` (the
component manifest), `templates/`, `tools/render.py` and `tools/lint_html.py` (page generation).

### Generated, hand-built and embedded pages

- **Generated** pages (reports, run summaries, status pages) are skeleton templates filled by
  `ui-kit/tools/render.py`.
  - Deterministic slots are filled from data.
  - Narrative and summary slots are declared AI slots. Claude fills them using the catalogue's
    markup only.
  - Every output passes `ui-kit/tools/lint_html.py`: no unknown class, no inline colour, no
    `<script>` unless a declared behaviour is used.
  - CSS and script are inlined, giving one self-contained file that can be put on S3.
  - The stamp records the source, the data timestamp and the model id. The generation time is
    never presented as the data time.
- **Hand-built** screens in the product app use React components only. Feature code does not write
  raw `ui-*` markup, so the class contract has one owner.
- **Embedded** generated HTML inside the app is shown either as a scoped fragment (selectors under
  `.ui-fragment`) when our own generator produced it, or in a sandboxed iframe when a model wrote
  it.

### Behaviour: static pages and the app

- **The app** gets all behaviour from React Aria Components: menus, tabs, dialog, popover,
  tooltip, combobox, table, tree and toast.
- **Static generated pages** get a small set of behaviours from `ui.js`, attached through
  `data-ui="tabs|menu|toolbar|tooltip|table|search|theme|copy|sections"`. Each behaviour is
  declared in the component manifest, so a page that uses none ships no `<script>`.
- About eight behaviours therefore exist twice. The static set is kept small (sections, CSS-only
  tabs, table sort and filter, in-page search, toggletip, copy, theme); the command palette, tree
  and dialogs are app-only.

## Component set

Each entry gives purpose, anatomy, variants, states, keyboard and ARIA, and what it is not for.
"Script" marks a component whose static form needs a declared `ui.js` behaviour.

### Shell and layout

1. **App shell and regions**
   - Purpose: the fixed-viewport frame.
   - Anatomy: a grid of named regions from a layout file.
   - Variants: `ide` (nav, main, inspector, dock), `dashboard` (header, cards, main), `focus` (main
     only).
   - States: compact density below 1100×800; stacked below 1024px wide.
   - Keyboard and ARIA: landmarks `header`, `nav`, `main`, `aside`, `footer`; a skip link; F6
     cycles between regions.
   - Not for: report pages.
2. **Panel (frame)**
   - Purpose: the container for any content in a region.
   - Anatomy: exactly one header with sub-slots `identity` (title or switcher), `help`, `controls`
     (at most five typed bar elements: help, action, choice, toggle, status) and `frame-actions`
     (maximize, collapse); then the body, of kind `document`, `tree`, `table`, `stream`, `form`,
     `terminal`, `ticker` or `chart`.
   - A panel never draws its own header. It places controls through typed bar elements; an
     element type the slot does not admit throws, and the panel's error boundary shows it.
   - Variants: `standard` (stacked header and body), `compact` (one inline row).
   - States: `empty` ("Nothing here yet" plus the next step), `loading`, `error` (error boundary
     plus Retry), `maximized` (transient, never saved), `collapsed` (header only).
   - Maximize and collapse never remount the panel's content; its live state survives.
   - Keyboard and ARIA: `section` with `aria-labelledby` pointing at the identity. Maximize is a
     toggle button with `aria-pressed`. Escape leaves the maximized state.
   - Not for: small grouped content inside a panel (use a card).
3. **Panel types** (each is a body kind plus default bar elements)
   - *Side or nav panel:* a navigation list or tree with `aria-current`. Not for actions.
   - *Explorer tree:* the ARIA Authoring Practices tree view (`tree`/`treeitem`; arrows expand and
     collapse; Home/End; typeahead), with a filter that hides folders with no match.
   - *Viewer:* a tabbed document frame (sandboxed iframe for generated HTML, markdown, PDF), a
     freshness badge, a refresh action and open-in-new-tab.
   - *Inspector:* properties of the current selection as a read-only description list, switching
     to a form on Edit, with sticky Save and Cancel. Not for primary workflows.
   - *Dock:* a bottom region with tabs (Console, Logs, Runs), collapsible to its tab strip.
   - *Split:* two panels with a resizable divider (window splitter pattern: `role="separator"`,
     `aria-valuenow`, arrow keys step 5%), clamped by the body kinds' minimum sizes. Not for more
     than three panes.
   - *Console:* a log stream (monospace, virtualized, level filter, copy, autoscroll paused when the
     user scrolls up, `role="log"`).
   - *Agent panel:* a conversation or run stream (see the AI and agent set).
4. **Status strip**
   - Purpose: one line of ambient status (environment, region, model, connection, last sync) or
     rotating announcements.
   - Anatomy: a compact frame with help, items and an optional choice.
   - States: overflowing text scrolls as a bounded marquee that pauses on hover or focus and is
     static under reduced motion.
   - Keyboard and ARIA: `role="status"` only for changes that matter. Rotation is not announced.
   - Not for: errors that need action (use a toast or an inline alert).

### Command surfaces

5. **Toolbar**
   - Purpose: a group of controls for the current panel.
   - Anatomy: `role="toolbar"` with `aria-label`; groups separated by dividers; an overflow `…`
     menu.
   - Variants: panel header bar; floating selection toolbar.
   - States: items disabled with the reason shown.
   - Keyboard and ARIA: one Tab stop, then roving focus with arrows and Home/End.
   - Script: yes.
   - Not for: app navigation, or more than about seven items (use a menu).
6. **Menu, context menu and overflow menu**
   - Anatomy: a trigger (`aria-haspopup="menu"`, `aria-expanded`) and a popup `menu` of `menuitem`,
     `menuitemcheckbox` and `menuitemradio`, with groups, separators and submenus.
   - States: hidden when inapplicable, disabled when unavailable; destructive items last, in the
     error colour, confirming in place.
   - Keyboard and ARIA: the first item takes focus on open; arrows, Home/End and typeahead; Escape
     closes and returns focus to the trigger; Shift+F10 or the Menu key opens a context menu; the
     position is clamped to the viewport.
   - Script: yes.
   - Not for: navigation links (use nav) or form choices (use a select).
7. **Command palette**
   - Purpose: Ctrl/Cmd+K search and actions across the app.
   - Anatomy: a modal dialog holding a combobox and a grouped listbox (recent, actions, entities,
     "Ask Claude…").
   - States: an empty query shows recent items; "No matches"; loading for asynchronous sources.
   - Keyboard and ARIA: the combobox pattern with `aria-activedescendant`; arrows; Enter runs;
     Escape closes; shortcuts shown with `aria-keyshortcuts`.
   - App only. Static pages use in-page search instead.
   - Not for: the only route to a feature. Everything is also in visible interface.
8. **Buttons**
   - Variants: `primary` (one per view), `secondary`, `ghost`, `danger`, `icon` (needs an
     `aria-label` and a tooltip), `split`, `toggle` (`aria-pressed`), link-style button.
   - Sizes: sm 24, md 32, lg 40.
   - States: hover, active, focus-visible, disabled (the real `disabled` attribute, with the reason
     on a wrapper), loading (spinner, `aria-busy`, width kept, label such as "Generating…").
   - Not for: navigation (use `<a>`).

### Overlays and disclosure

9. **Tooltip and toggletip**
   - *Tooltip:* a short label for an icon-only control, shown on hover or focus after 300–500ms,
     `role="tooltip"` linked by `aria-describedby`. Never interactive. Escape dismisses it (WCAG
     1.4.13). The pointer can move into it. It closes on leave.
   - *Toggletip:* the "?" control. Click or Enter opens a small non-modal popover with explanatory
     content and a live region.
   - Script: yes.
   - Not for: essential information or form errors.
10. **Popover**
    - Purpose: anchored, non-modal content (filters, pickers, the panel switcher).
    - Anatomy: a trigger, then an `e1` surface with an optional title and close button.
    - Keyboard and ARIA: the native `popover` attribute where possible; `role="dialog"` with a
      label when it contains controls; focus moves in on open and returns on close; Escape, an
      outside click and the close button dismiss it.
    - Placement: by measured fit, at most 60% of the viewport height, at least 8px from the
      viewport edge.
    - Script: yes.
    - Not for: blocking decisions (use a dialog).
11. **Dialog**
    - Variants: `info` (title, body, one "Got it" button), `confirm` (destructive: names the object
      and the consequence, with the danger button on the right), `form` (short), `full` (sheet).
    - Keyboard and ARIA: native `<dialog>` with `showModal()`. Focus moves to the first field or the
      safe button and is held by the top layer. Escape closes unless there is unsaved work.
      `aria-labelledby` and `aria-describedby`. Focus returns to the trigger.
    - Not for: confirming reversible actions, or anything a popover or an inline expansion can do.
12. **Collapsible section (accordion)**
    - Anatomy: native `<details><summary>` with the heading inside the summary, a number, a chevron
      and an optional one-line summary. Expand-all and collapse-all for long pages. A deep link
      (`#id`) opens its target.
    - Keyboard and ARIA: native. The `name` attribute makes an exclusive group.
    - Script: none; deep-link opening and expand-all are an optional behaviour.
    - Not for: hiding primary content on page load.
13. **Tabs**
    - Anatomy: `tablist`, `tab`, `tabpanel`; an optional close `×` and `+ New` with a cap.
    - Variants: panel tabs (viewer sessions), page tabs, and CSS-only tabs (the radio technique) for
      script-free reports.
    - Keyboard and ARIA: arrows move; automatic activation for cheap panels and manual (Enter) for
      expensive ones; Home/End; Delete closes, with a confirmation if the tab holds live work.
    - Not for: sequential steps (use a stepper) or more than about seven tabs (use a select or
      nav).

### Content and data

14. **Cards**
    - Anatomy: an optional kicker, title, body, meta and an actions footer. The whole card is
      clickable only when it has a single action.
    - Variants: neutral, `accent` (attention), `leaf` (state), stat card, AI result card.
    - Not for: tabular comparison (use a table).
15. **Stat row**
    - Anatomy: label, value, delta or description.
    - Rules: values are computed and sourced ("not recorded" when absent), in tabular numerals.
16. **Callout and inline alert**
    - Variants: info, ok, warn, err, and a note with its source.
    - Keyboard and ARIA: `role="alert"` only when it appears in response to an action.
17. **Table and DataTable**
    - Anatomy: a toolbar (search, filter chips, column menu, view toggle, count "42 of 310"); a
      table with a sticky header; sortable headers (the header cell itself is the pressable
      control, with `aria-sort` on it, cycling ascending, descending, then the server order; the
      static form styles the same header); row selection (checkbox column,
      `aria-selected`); a footer.
    - States: skeleton rows while loading; empty, and with filters "No rows match" plus clear
      filters; error; virtualized above 500 rows.
    - Keyboard and ARIA: a semantic `<table>`; the grid pattern only when cells are interactive.
    - Script: sort and filter in the static form.
    - Not for: fewer than about four rows (use a description list) or layout.
18. **Forms and inputs**
    - Elements: text field, textarea (autosize; the prompt input submits on Ctrl+Enter), select,
      combobox, checkbox, radio group, switch (`role="switch"`), segmented control (a radio group),
      slider, file drop zone (with a button alternative, WCAG 2.5.7), search field.
    - Anatomy: a visible label, a hint, the field, and an error message linked by
      `aria-describedby`, with `aria-invalid`.
    - Validation: on blur and on submit, never on each keystroke. Long forms show an error summary
      at the top.
    - Not for: a placeholder used as the label.
19. **Pills, badges and chips**
    - *Status pill:* text, a dot and a pale fill. The status is always in words, never colour
      alone.
    - *Count badge.*
    - *Filter chip:* removable; a button labelled "Remove filter: X".
    - *Tag.*
    - *Gate badge:* marks a human approval point.
    - Not for: actions other than removing a chip.
20. **Breadcrumbs**
    - Anatomy: `nav aria-label="Breadcrumb"` with an `ol`; the last item has
      `aria-current="page"`; long trails collapse the middle to `…`.
    - Not for: flat apps of one or two levels.
21. **Toasts**
    - Variants: success (dismisses itself after 5s, paused on hover or focus), info, error
      (persistent, with an action such as Retry or View).
    - Anatomy: a stack at the bottom right, at most three visible.
    - Keyboard and ARIA: a polite `status` region (`alert` for errors); never takes focus; reachable
      with a shortcut (F8).
    - Known gap: the React toast is built on React Aria's toast, which gives every toast
      `role="alertdialog"` and so announces success and info assertively. The owner accepted this on
      2026-10-14 until React Aria's toast is stable; then success and info move to a polite region.
    - Not for: errors that block the current task (show them inline) or confirmations (use a
      dialog).
22. **Empty, loading, error, missing and not-recorded states**
    - *Empty:* says what goes here, plus one primary action.
    - *Loading:* a skeleton for known shapes, a spinner with text otherwise, `role="status"`, shown
      after a 150ms delay to avoid a flash.
    - *Error:* what failed, why, and Retry, with `role="alert"`.
    - *Missing:* the capability is off ("Agent service not configured in this environment"). Not
      styled as an error.
    - *Not recorded:* the data is absent.
23. **Progress**
    - Variants: determinate bar (`progressbar` with a value), indeterminate, stepper for a
      multi-step agent run ("Step 2 of 4: Retrieving documents"), ring for small spaces.
    - Not for: waits under one second.
24. **Code and JSON viewer**
    - Anatomy: a header (label, language, copy button, wrap toggle) and a `pre` with token spans,
      optional line numbers. The JSON viewer is a collapsible tree (`details` per object in the
      static form, tree keyboard in the app) with path copy and search highlight.
    - States: a large payload truncates with "Show all (12,340 lines)".
    - Not for: editing.
25. **In-page search and filter**
    - Anatomy: a `type="search"` field with the `/` shortcut, and a result count in a polite live
      region.
    - States: no match.
    - Script: yes.
26. **Diagram** (static SVG)
    - Anatomy: `role="img"` with `<title>` and `aria-label`; nodes may be focusable to highlight
      neighbours (optional script); static by default.
27. **Section navigation (table of contents with scroll-spy)**
    - Report pages only.
    - Script: yes.

### AI and agent set

Cloudscape's generative-AI patterns are the specification for this set: generative-AI loading
states, progressive steps, user-authorized actions, the generative-AI output label, support
prompts and artifact previews (cloudscape.design/gen-ai/patterns/). The components are our own,
built on React Aria Components and our tokens.

28. **Stream output**
    - Anatomy: an incremental, sanitized markdown renderer, a caret while streaming, Stop, Copy and
      Regenerate.
    - States: `queued`, `thinking` (processing), `streaming` (generating), `stopped`, `done`,
      `error` (partial output kept), `throttled` (retrying with a countdown).
    - Keyboard and ARIA: the container is `aria-busy` while streaming; the polite announcement is
      throttled to a sentence or to completion. Focus never moves.
29. **Run timeline**
    - Anatomy: an ordered list of steps (plan, tool call, retrieval, generation), each collapsible
      to show inputs and outputs (JSON viewer), with duration and a status pill.
30. **Citation chip and source drawer**
    - Anatomy: an inline numbered chip opening a popover with title, source (S3 key,
      knowledge-base document, URL), excerpt and "Open"; a page-level Sources list.
    - Every generated artefact carries a stamp: data source and timestamp, model id, and prompt or
      version id.
31. **Confidence indicator**
    - Only for scores with a defined basis. Shown as a category (High, Medium, Low) plus its basis
      ("Based on: 3 matching sources"), with an explanation on hover or focus.
    - Not for: a model's own self-assessment presented as a probability.
32. **Approval card**
    - Anatomy: what the agent proposes, why, a preview or diff, the impact (cost, recipients,
      resources), Approve / Edit / Reject and an optional comment.
    - States: pending; approved by a named person at a time; rejected; expired.
    - Friction matches risk: light approval for routine actions; typed confirmation for
      irreversible ones; the card says whether the action can be undone.
    - Keyboard and ARIA: a region with a heading. Approve is not the default Enter action when the
      impact is destructive.
33. **AI output label**
    - A consistent label on machine-generated content, with a popover that explains how it was
      produced.
34. **Model and usage badge**
    - "Claude via Amazon Bedrock · model id", input and output tokens, latency, estimated cost. Sits
      in the status strip or a run footer.

### Deferred

- **Embedded terminal (PTY):** needs a server-side terminal process; no product need yet.
- **Runtime panel reassignment and layout persistence:** excluded by the fixed-layout ruling.
- **Menu bar:** the command palette covers the same commands.
- **Rich code editor.**
- **Drag-and-drop layout.**

## Brand

The product name and logo are not yet chosen. AWS and Anthropic marks appear only as an official
"Built with" badge, never by copying their palettes.
