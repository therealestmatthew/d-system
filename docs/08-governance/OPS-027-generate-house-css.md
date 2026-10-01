---
schema_version: 1
id: doc-ops-generate-house-css
code: OPS-027
title: Regenerate the house family's token stylesheet
kind: operation
status: active
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-html]
depends_on: [doc-governance-operations, doc-engine-pages-house-style-requirements]
---

# Regenerate the house family's token stylesheet

## Trigger

Run after any edit to `templates/styles/house-tokens.json`. That file holds every value of the
house style the owner approved on 2026-09-30 ([REQ-036](../06-requirements/REQ-036-engine-pages-house-style.md)):
colour roles in light and dark, fonts, sizes, spacing, rules and radius. `templates/styles/house.css`
is generated from it and is never edited by hand. `test/test_house_css.py` fails while the two
disagree.

Run with `--specimen` to see the family: before reviewing a change to the tokens or to
`templates/styles/house-components.css`, and when a browser check of the modes or variants is
needed.

## Command

```bash
uv run python tools/generate_house_css.py                      # rewrite house.css from the tokens
uv run python tools/generate_house_css.py --check              # exit 1 if house.css is stale
uv run python tools/generate_house_css.py --specimen out.html  # a page showing every component
uv run python tools/generate_house_css.py --specimen out.html --variant swiss --theme dark
```

## Expected result

The default run prints `wrote templates/styles/house.css`. `--check` prints
`templates/styles/house.css matches the tokens` and exits 0, or names the stale file and exits 1.

`house.css` has five blocks in a fixed order: `:root` with the light colours and every
non-colour token, the dark colours under `prefers-color-scheme: dark` unless `data-theme="light"`,
the same dark colours under `data-theme="dark"`, and one block for each variant (`swiss`, `mono`).
The dark blocks set colour tokens and `color-scheme` only. The variant blocks set no colour. The
output depends only on the tokens file, so two runs give identical bytes.

`--specimen PATH` writes one self-contained page: `templates/html/house-page.html` filled with
both stylesheets inlined and `templates/html/house-components.html` as its body. `--variant` sets
`data-variant` on `<html>` (`house` sets none). `--theme` sets `data-theme` (`auto` sets none and
follows the viewer). The page's only external request is the Google Fonts stylesheet. The
specimen is written wherever `PATH` says, typically a scratch directory, and is not committed.

## Changing the house style

Edit `house-tokens.json`, regenerate, and update the gallery fixture in `test/test_house_css.py`
in the same change. The fixture is the transcription of what the owner approved, with the
gallery's URL, artifact version and file hash. A token that no longer matches it fails the test,
so a change to the approved values has to be visible in the diff and cannot happen by accident.

Component rules belong in `house-components.css` and refer to tokens through `var()` only. A colour
literal there, or in either house template, fails the test.

## Failure and recovery

- **`--check` exits 1.** Someone edited the tokens without regenerating, or edited `house.css` by
  hand. Run the tool without flags and commit the result. A hand edit to `house.css` is lost;
  move it into the tokens file first.
- **`ValueError: unfilled {{NAME}}` or `template has no {{NAME}}`.** `house-page.html`'s tokens
  and the values `render_specimen()` passes have drifted apart. Make the token contract in the
  template's header comment and the call agree.
- **`KeyError` reading the tokens.** The tokens file lost one of its top-level groups (`provenance`,
  `fonts_url`, `stacks`, `fonts`, `scale`, `colors`, `variants`). Restore it from git.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_house_css.py`

Generate the house family's token stylesheet from its tokens file — `REQ-036` R01-R05.

`templates/styles/house-tokens.json` is the only place the house style's values live: colour
roles in light and dark, fonts, sizes, spacing, rules and radius, transcribed from the round-two
gallery the owner approved on 2026-09-30. This tool turns that file into
`templates/styles/house.css`, which no one edits by hand. The component rules in
`templates/styles/house-components.css` refer to the tokens through `var()` only and carry no
value of their own.

The generated sheet has five blocks, always in this order:

    :root { stacks, fonts, scale, light colours }        the house style, light mode
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) { dark colours }   dark mode follows the viewer
    }
    :root[data-theme="dark"] { dark colours }            and an explicit override
    :root[data-variant="swiss"] { type and spacing }     the two variants, which set
    :root[data-variant="mono"]  { type and spacing }     no colour (R03)

Dark mode redefines colour tokens and `color-scheme` only (R04). A page selects a variant with
`data-variant` and a mode with `data-theme` on its `<html>` element; with neither, it renders the
house style following the viewer's colour scheme.

Determinism (R01). The output is a pure function of the tokens file: keys are emitted in the
file's own order, no clock or environment is read, and the same file always yields the same bytes.

    uv run python tools/generate_house_css.py                      # rewrite house.css
    uv run python tools/generate_house_css.py --check              # exit 1 if house.css is stale
    uv run python tools/generate_house_css.py --specimen out.html  # write a specimen page
    uv run python tools/generate_house_css.py --specimen out.html --variant mono --theme dark

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--check` | exit 1 if house.css differs from the tokens |  |  |  |
| `--specimen` | write a specimen page to PATH instead |  |  |  |
| `--variant` | specimen variant |  | house |  |
| `--theme` | specimen mode |  | auto |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
