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
1193 passed, 1 warning
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
- Fonts blocked (fonts.googleapis.com and fonts.gstatic.com aborted, fresh browser). The
  validator's own report of this check had no saved output behind its `document.fonts.size`
  figure (the review's major finding), so the session re-ran `verify_check5.js` itself and kept
  the output. Verbatim, minus the long fonts URL:

  ```
  "fontsRequestedCount": 1,
  "fontsAbortedCount": 1,
  "h1Rect": { "width": 578.578125, "height": 121.34375 },
  "bodyTextLength": 779,
  "bodyFontFamily": "Literata, Georgia, \"Times New Roman\", serif",
  "literataLoaded": true,
  "bricolageLoaded": true,
  "documentFontsSize": 0
  ```

  No font face was registered, the page laid out with visible text, and the computed family
  falls through to the system stack. `literataLoaded` and `bricolageLoaded` come from
  `document.fonts.check()`, which reports `true` in headless Chromium even with no face registered
  (`documentFontsSize: 0`). They are recorded here, not relied on.
- No `<script>` in any specimen. The content renders with JavaScript disabled.
- At 375px, `scrollWidth` is 375. The table scrolls inside `.tbl-wrap`.

## Acceptance

- REQ-036 R01 (byte-identical regeneration, no colour literal outside the generated CSS): **Met**.
  `test_committed_css_matches_regeneration`, `test_regenerating_twice_is_byte_identical`, both
  `--check` tests and the three `test_no_colour_literal_outside_the_generated_css` cases pass within
  the 1193.
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

## Review

Independent review by a `demo-adversary` agent over `dev...HEAD` (commits `093902d`, `40af15e`).
It recomputed the gallery file's sha256 (match), diffed every token and fixture value against the
raw gallery CSS (exact match), ran the house and tool-docs tests (36 passed), governance (OK),
ruff (clean) and `--check` (matches), and diffed a regenerated specimen byte-for-byte against the
one the browser validator used (identical). Its findings, as reported:

- **Major — session record cites a specific metric that no surviving artifact supports.** The
  record's fonts-blocked line stated `document.fonts.size === 0`, but the script that produced the
  saved browser output never computed it, and the script that does was written after that output,
  with no saved result. "It doesn't invalidate R05 — the structural test ... genuinely holds — but
  the record overstates its evidentiary basis for that one line." **Fixed:** the check was re-run
  and its output is pasted under Verification above.
- **Minor — `_blocks()` test helper mis-parses nested at-rule blocks.** The `@import` statement and
  the base `:root` block merged into one key, so a lookup of `':root'` would fail. "No current test
  looks up `blocks[':root']`, so nothing passes vacuously today." **Fixed:** the helper strips
  `@import` and the `@media` wrapper first, and a new test asserts all five rule keys parse. That
  test caught a second error in the first version of the fix (the fonts URL contains `;`).
- **Minor — demo numbers in `house-components.html` double as reference markup and real
  figures,** and the table named `phase-des-07` itself. "Cosmetic, not a REQ-036 violation."
  **Fixed:** the table uses example ids and the stat row is labelled as placeholders.

It reported no discrepancies in token-to-gallery fidelity, generator determinism, R03, R04 (both
the structural half and the browser half), R06, the OPS-027 reservation removal and generated
block, scope boundaries, or prose. Per-condition verdict: R01 Met, R02 Met, R03 Met, R04 Met, R05
Met ("on the structural/testable claim", with the evidence defect now fixed), R06 Met. No blocker.

## Decisions

The tokens were extracted from the gallery's published `index.html` by a script, not typed. The
fixture in the test file and the tokens file come from the same extraction, and the reviewer then
checked both against the raw file by hand. The phase scope required reading the artifact, and a
mechanical extraction removes transcription as a source of error.

The fixture lives inside `test/test_house_css.py`, not in a separate fixture file, because the
phase's declared deliverables name that one test file.

`house.css` loads Google Fonts with `@import` inside the generated sheet rather than a `<link>` in
the page template. All font configuration stays in the tokens file, and inlined pages keep the
import, which fails without breaking layout when offline.

Component rules went into a separate hand-written `house-components.css` that uses `var()` only,
instead of being generated. The tokens are data; the component rules are design code that changes
for different reasons.

`generate_house_css.py --specimen` writes a review page. It was added so the browser checks R04 and
R05 call for had a real page to load, and `phase-des-09` can use it as its reference rendering.

The validator used Playwright scripts rather than a browser MCP tool, because none was available
to it. The method is recorded with the evidence.

## Corrections

- The preflight `pytest` run in the worktree reported 2 failures in `test/test_tool_docs.py`. The
  session had written `tools/generate_house_css.py` while that run was in progress, and a tool with
  no paired operations document is exactly what those tests catch. After OPS-027 was written they
  passed (7 of 7), and the full suite has passed since.
- `fill()` first scanned its output for unfilled tokens, which failed on `{{INLINE_STYLES}}` text
  inside the inlined CSS comments. It now checks the template's own tokens.
- `test_google_fonts_is_the_only_external_request` first counted URLs in comments as requests. It
  now reads only `url()`, `href` and `src`.
- Writing OPS-027 failed governance because its code was reserved in `codes.yaml`, which was not
  in the phase's deliverables. This was a miss in the planning amendment that created the phase.
  The session stopped, the Session Manager relayed the owner's ruling, and `codes.yaml` was added to
  the deliverables of `phase-des-07` and `phase-des-09` on `dev` (`8d1bfcf`) before the reservation
  was removed.

## Left undone

- The Claude Design System mirror of the tokens, which the owner ruled for later.
- Moving any existing family or `_public/` page onto the house style, which is out of this phase's
  scope by its own terms.
- Contrast checks on the approved values. `000085` raised the question, and the owner approved the
  gallery as shown.
