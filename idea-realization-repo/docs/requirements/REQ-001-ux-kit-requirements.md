---
schema_version: 1
id: doc-ux-kit-requirements
code: REQ-001
title: UX component kit requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-ui-kit]
depends_on: [doc-ux-design-guide]
---

# UX component kit requirements

## Observed problem and scope

Several developers will build screens and generated reports for one product over three weeks.
Without a shared kit each builds their own buttons, tables and overlays, and the screens differ in
look, keyboard behaviour and accessibility. The earlier workbench these patterns come from shows
the failure: its CSS had colour literals and no focus styles, and its menus and tree had no arrow-key
navigation.

These requirements cover the kit in `ui-kit/`: the token pipeline, the CSS, the React components,
the static behaviours, the gallery and the theme sheet. The design they check is the UX design guide
(`ARCH-001`); the choice of React Aria Components is the component kit decision (`ADR-001`).

Terms used below:

- **Gallery**: the pages under `ui-kit/gallery/`, including the theme sheet.
- **Candidate accent**: a named accent defined in `ui-kit/tokens/tokens.json` and selected with
  `data-accent` on the root element.
- **Script-free page**: a gallery or generated page that uses no declared `ui.js` behaviour.
- **Catalogue**: the canonical HTML markup for each component, shown in the gallery.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The token build is deterministic. Running `ui-kit/tools/build_tokens.py` twice on the same `tokens.json` produces byte-identical `ui-kit/dist/tokens.css`, and `--check` exits nonzero when `tokens.json` has changed without regenerating the CSS. | A Python test builds twice and compares bytes; it then edits a copy of `tokens.json` and asserts `--check` exits nonzero. Must fail: a stale `dist/tokens.css` passing `--check`. |
| R02 | Every contrast pair declared in `tokens.json` meets its threshold (4.5:1 for text, 3:1 for large text, interface parts and the focus ring) in the light theme and the dark theme, for every candidate accent. | A Python test computes the WCAG 2.2 contrast ratio for each pair × theme × accent and lists every failure. Must fail: a fixture pair below its threshold. |
| R03 | The dark theme sets colour only. The dark blocks of `dist/tokens.css` (the `prefers-color-scheme: dark` block and the `[data-theme="dark"]` block) declare only colour custom properties; density and variant blocks declare no colour property. | A Python test parses `dist/tokens.css` and checks each block's property names against the colour group in `tokens.json`. Must fail: a spacing property inside a dark block. |
| R04 | The theme follows the system setting unless overridden. With no `data-theme` attribute the page renders the theme the browser's `prefers-color-scheme` reports; `data-theme="light"` or `"dark"` on the root forces that theme; the theme toggle sets that attribute. | A browser test emulates each colour scheme with and without the attribute and reads a computed colour token. Must fail: a forced light theme rendering dark under a dark system setting. |
| R05 | Every candidate accent can be selected. Setting `data-accent="<name>"` on the root changes the accent tokens to that candidate's values in both themes; without the attribute the default candidate applies. The theme sheet (`ui-kit/gallery/theme-sheet.html`) shows every candidate in light and dark. | A browser test sets each candidate name and reads the computed accent token; it lists the candidates on the theme sheet and compares them with `tokens.json`. Must fail: a candidate in `tokens.json` missing from the theme sheet. |
| R06 | The kit makes no external request. Loading any gallery page, the theme sheet or a generated page issues no network request to an origin other than the page's own. Every font stack ends in a generic family. | A browser test records every request while loading each page and fails on a foreign origin; a Python test checks the last entry of each font stack. Must fail: a fixture page that links a webfont. |
| R07 | Every interactive element shows a focus ring. On each gallery page, moving focus with the keyboard to each focusable element produces a visible outline of at least `focus-width` (2px) whose colour meets 3:1 against the adjacent background. | A browser test tabs through each gallery page and reads each focused element's computed outline. Must fail: a fixture button with `outline: none`. |
| R08 | Automated accessibility checks find no serious or critical issue. axe reports zero violations of impact `serious` or `critical` on every gallery page, in light and in dark. | A browser test runs axe on each gallery page in both themes and lists the violations. Must fail: a fixture image without alternative text. |
| R09 | Each interactive widget follows its keyboard specification in ARCH-001's component set: toolbar, menu, tabs, dialog, popover, tooltip and toggletip, accordion, tree, command palette, DataTable sorting and toast. In every overlay, Escape closes the top overlay and returns focus to the element that opened it. | One browser test per widget, in the gallery, drives the keys its specification names and asserts focus position and ARIA state after each key. Must fail: a menu whose arrow keys do not move focus. |
| R10 | A script-free page contains no `<script>` element. A page that uses static behaviours includes only behaviours declared in the component manifest. | `ui-kit/tools/lint_html.py` checks each gallery and generated page, and a Python test runs it over fixtures. Must fail: a script-free fixture that contains a `<script>`. |
| R11 | The app shell fits the viewport. For each layout in `ui-kit/layouts/*.json`, at 1024x768, 1280x720, 1366x768 and 1920x1080, in both themes, the document's scroll height and scroll width do not exceed the viewport, so the page does not scroll. | A browser test loads the shell gallery page for each layout at each size and compares `scrollHeight`/`scrollWidth` with `innerHeight`/`innerWidth`. Must fail: a fixture panel with fixed oversized content outside a scroll container. |
| R12 | React components emit the catalogue's classes. For each component that has both a catalogue entry and a React component, the React-rendered DOM carries the same `ui-*` classes and the same state attributes as the catalogue markup for the same state. | A component test renders each React component in each catalogued state and compares its class and state-attribute set with the catalogue markup. Must fail: a React component that renders a class absent from the catalogue. |
| R13 | Component CSS contains no colour literal. No file under `ui-kit/src/css/` contains a hex, `rgb()`, `hsl()` or named colour value; colours come only from `--ui-` custom properties. | A Python test scans the CSS sources. Must fail: a fixture CSS file with a hex colour. |

## What each requirement is not

- **R01** does not require the tokens file to follow the W3C design tokens format, and does not
  require any particular token names beyond those ARCH-001 lists.
- **R02** covers the pairs declared in `tokens.json`. It does not prove every colour combination a
  developer could write is accessible; R13 and the class contract limit what they can write.
- **R03** does not forbid the dark theme from changing a shadow's colour; shadows that carry colour
  are colour tokens.
- **R04** does not require the chosen theme to be saved between visits.
- **R05** does not choose the accent. The owner chooses later from the theme sheet; this row only
  requires that every candidate works.
- **R06** does not cover the product app's own calls to its backend or to a model service; it
  covers the kit's pages and assets.
- **R07** does not require a focus ring after a mouse click (`:focus-visible` behaviour is
  correct), and does not cover elements that are not focusable.
- **R08** is an automated check. It does not replace a manual keyboard and screen reader pass, and
  it does not require zero `moderate` or `minor` findings.
- **R09** covers widgets as they appear in the gallery. It does not require custom keyboard
  shortcuts beyond those ARCH-001 names.
- **R10** does not forbid scripts in the product app; it covers gallery and generated pages.
- **R11** does not apply below 1024px wide, where ARCH-001 allows the shell to stack its panels
  and the page to scroll. Panels may scroll internally.
- **R12** does not require React components to match the catalogue's element structure beyond
  classes and state attributes; React Aria may add wrapper elements and ARIA attributes.
- **R13** does not cover `dist/tokens.css`, which is where colour values live, or generated
  gallery pages.
