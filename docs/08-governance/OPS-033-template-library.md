---
schema_version: 1
id: doc-ops-template-library
code: OPS-033
title: Declare, inspect and render templates through the template library
kind: operation
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-html]
depends_on: [doc-governance-operations, doc-html-generation-design-system-requirements]
---

# Declare, inspect and render templates through the template library

## Trigger

Run this when any of these happens:

- a template is added to `templates/html/`;
- you need to know how a template is populated;
- you need to render one without writing generator code.

`REQ-021` R05 asks that adding a template need no generation-code change. R06 asks that each
template's population method be machine-readable, so a generator can dispatch on it. This tool
meets both: `templates/html/library.yaml` holds the declarations, and `tools/template_library.py`
reads them and dispatches on them.

## Command

```bash
uv run python tools/template_library.py list                    # every template, one JSON line each
uv run python tools/template_library.py show atlas-page.html    # one declaration and its slots
uv run python tools/template_library.py render house-page.html --data DATA.json --out PAGE.html
```

`--data` is a JSON object of slot names to strings. On a page whose family declares
`inline_styles`, `{{INLINE_STYLES}}` is filled from the declared stylesheets unless the data
supplies it.

## Expected result

`list` and `show` print each declaration as JSON: family, population method, `ai_slots`,
whether the template is a reference catalogue, whether it is a full page, its slots (read from
the template itself), and the generators that render the family today.

`render` dispatches on the declared method:

| Method | What `render` writes |
|---|---|
| `slot-fill` | The page or fragment, every slot filled. A slot missing from the data, or a key the template does not have, is an error |
| `ai-adaptation` | An adaptation brief (JSON) for an agent: the template, its slots and the data. Nothing is filled and no model is called |
| `both` | A brief with every deterministic slot already filled in `partial`; only the slots in `ai_slots` are left for the agent. A missing deterministic slot, or a value supplied for an `ai_slots` slot, is an error |

Reference catalogues (`reference: true`, such as `house-components.html` and
`atlas-components.html`) are declared and refused by `render`.

The existing generators — `generate_overview.py`, `generate_engine_pages.py`,
`generate_house_css.py` and `lit_report_render.py` — keep their own template loading. Their
output does not depend on this tool. `test/test_template_library.py` replays
`generate_overview.py`'s fills and both house-page fills (the engine pages and the `--specimen`) through `render()` and compares the
bytes.

## Adding a template

- **A file in an existing family:** name it to match the family's pattern (`overview-*.html`,
  `lit-report-*.html`). It is declared already, and `render` can fill it.
- **A file with its own method:** add a `file:` entry to its family in `library.yaml`. A
  `file:` entry overrides the family's `pattern:` entry.
- **A new family:** add a `families:` entry with its pattern or files, its population method,
  and, for pages, its `inline_styles`.

Document the template's slots in a leading `<!-- ... -->` comment. Every family does this, and
the comment is removed before filling.

## Failure and recovery

Every failure exits 1 with `template_library: <message>` on stderr and writes nothing.

| Failure | Cause | Fix |
|---|---|---|
| `undeclared template(s): ...` | A file in `templates/html/` matches no declaration | Rename it to a family's pattern, or add an entry to `library.yaml` |
| `... matches no file in templates/html/` | A `file:` or `pattern:` names nothing | Correct or remove the entry |
| `... declared twice at the same level` | Two patterns, or two `file:` entries, claim one file | Keep one; use a `file:` entry to override a pattern |
| `population must be one of ...` | A method other than `slot-fill`, `ai-adaptation` or `both` | Use one of the three |
| `ai_slots is required for both and allowed only there` | `ai_slots` on a non-`both` entry, or `both` without it | Add or remove `ai_slots` |
| `ai_slots not in the template: ...` | An `ai_slots` name the template does not contain | Correct the name, or add the slot to the template |
| `generator ... does not exist` / `stylesheet ... does not exist` | A family names a missing file | Correct the path |
| `unfilled slot(s): ...` / `template has no slot(s): ...` | The `--data` keys and the template's slots differ | Supply exactly the template's slots (`show` lists them) |
| `... is a reference catalogue, not rendered` | `render` on a `reference: true` template | Copy its markup into a page template instead |

<!-- generated:tool-reference:start -->

### Reference: `tools/template_library.py`

The template library: declared templates, and a renderer that dispatches on how each one is
populated — `REQ-021` R05 and R06, `phase-des-03`.

`templates/html/library.yaml` declares every template under `templates/html/`: its family, and
its population method — deterministic slot-filling, AI adaptation, or both. This module reads
that declaration, finds each template's `{{SLOT}}` names in the template itself, and renders by
dispatching on the declared method, so a caller never needs to know which templates an agent
populates:

- `slot-fill` fills every slot from the data, strictly: an unknown or missing slot is an error.
- `ai-adaptation` returns an adaptation brief — the template, its slots and the data — for an
  agent to work from. No page comes back and no model is called; the library stays
  deterministic.
- `both` fills the deterministic slots first, then returns a brief naming the slots in the
  declaration's `ai_slots`, which stay in the partly filled template for the agent.

Adding a template needs no change here. A file matching a family's pattern is declared already,
and a new family is a manifest entry. `load()` rejects an undeclared template, a declaration
that matches no file, and an `ai_slots` name the template lacks, so the declaration cannot
drift from the files.

The existing generators (`tools/generate_overview.py`, `tools/generate_engine_pages.py`,
`tools/generate_house_css.py`, `tools/lit_report_render.py`) keep their own template loading.
The library sits beside them and changes nothing they render; its tests replay
`generate_overview.py`'s fills through `render()` and compare the bytes.

Slot filling here is the same contract every family documents: the template's leading
`<!-- ... -->` comment is removed first, because it names the slots literally, and the fill is
one pass over the original text, so a value containing `{{...}}` is never re-substituted.

    uv run python tools/template_library.py list
    uv run python tools/template_library.py show overview-page.html
    uv run python tools/template_library.py render house-page.html --data DATA.json --out PAGE.html

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `template` | template file name under templates/html/ |  |  |  |
| `template` | template file name under templates/html/ |  |  |  |
| `--data` | JSON object: slot -> text |  |  | yes |
| `--out` | page, or brief (JSON) for AI |  |  | yes |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
