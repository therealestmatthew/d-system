---
schema_version: 1
id: doc-session-house-style-tokens
code: SESS-2026-09-30-05
title: House-style tokens and the house family
kind: session
status: active
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-html]
depends_on: [doc-html-generation-design-system, doc-engine-pages-house-style-requirements]
---

# House-style tokens and the house family

## Phase

`phase-des-07` — Commit the house-style tokens and generate the house family.

## Verification

`uv run pytest`

```
1192 passed, 1 warning
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 409 documents, 34 memories, 347 backlog phases
```

`uv run ruff check src/ test/`

```
All checks passed!
```

Not in the phase's list, run as part of the merge gate: `uv run mypy src/` gave
`Success: no issues found in 46 source files`.

Browser checks for REQ-036 R04 and R05 (the requirement names a render, which no listed command
performs). A `demo-validator-web` agent loaded the nine specimen pages
(`tools/generate_house_css.py --specimen`, three variants × auto/light/dark) in headless Chromium.
It had no browser MCP tool, so it drove Chromium through Playwright scripts installed in the
scratch directory:

- Bounding boxes of h1, `.stats`, `.cols`, `.callout`, the pills paragraph and the table: max
  difference 0px between light and dark, in all three variants.
- Body colours: light `rgb(255, 255, 255)` on `rgb(20, 20, 20)`, dark `rgb(18, 16, 21)` on
  `rgb(241, 237, 244)`, in every variant.
- `-auto` pages follow emulated `prefers-color-scheme` both ways. `data-theme="light"` stays white
  under emulated dark.
- Variants: house Literata/17px, Swiss Archivo/15.5px, mono JetBrains Mono/14px. Background and
  kicker colour are identical across the three.
- Fonts blocked (fonts.googleapis.com and fonts.gstatic.com aborted, fresh browser):
  `document.fonts.size === 0`, h1 578.6 × 121.3px, 779 characters of body text, page readable in
  system fonts. `document.fonts.check('16px Literata')` returned `true` regardless, which the
  validator reports as a headless quirk and did not rely on.
- No `<script>` in any specimen. The content renders with JavaScript disabled.
- At 375px, `scrollWidth` is 375. The table scrolls inside `.tbl-wrap`.

## Acceptance

- REQ-036 R01 (byte-identical regeneration, no colour literal outside the generated CSS): **Met**.
  `test_committed_css_matches_regeneration`, `test_regenerating_twice_is_byte_identical`, both
  `--check` tests and the three `test_no_colour_literal_outside_the_generated_css` cases pass within
  the 1192.
- REQ-036 R02 (tokens match a fixture transcribed from the gallery, citing URL and artifact version):
  **Met**. `test_tokens_match_the_gallery` and `test_tokens_cite_the_gallery_they_were_read_from`
  pass. The fixture cites version `1790623455-daec` and the file's sha256.
- REQ-036 R03, R04 and R05 (variants set no colour, dark sets only colour, font tokens end in a
  generic family): **Met**. The parse tests pass, and the browser checks above show identical layout
  across modes and a readable page with fonts blocked.
- REQ-036 R06 (the README lists the family, its variants and how a page selects a variant and a
  mode): **Met**. `test_house_family_is_registered_in_the_readme` passes. The row names every file,
  both `data-variant` values, both `data-theme` values and `prefers-color-scheme`.

## Backlog

`status: active` (the completion edit is made on `dev` after the merge, per the Session Manager's
contract). `next_action`: all four acceptance conditions met. Waiting on the owner's merge
approval, after which the completion edit is made on `dev`.

## Unresolved

None.
