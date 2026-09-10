---
schema_version: 1
id: doc-ops-generate-overview
code: OPS-014
title: Render the D-System overview page
kind: operation
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-portfolio]
depends_on: [doc-governance-operations]
---

# Render the D-System overview page

## Trigger

Run to generate a self-contained HTML overview of the D-System state, including idea metrics, backlog phase counts, concept inventory, and systems registry. This tool does not compute any metrics itself; it runs `tools/overview_metrics.py` and `tools/overview_inventory.py` as subprocesses, parses their JSON output, and renders the results into HTML templates. Its output is fully deterministic: two runs against an unchanged repository produce byte-identical HTML, with no dependence on wall-clock time or external services.

## Command

```bash
uv run python tools/generate_overview.py               # write _public/overview/index.html
uv run python tools/generate_overview.py --out FILE     # write elsewhere instead
```

## Expected result

Exit 0. The HTML page is written to `_public/overview/index.html` (or the path specified by `--out`). The page is fully self-contained — all styles are inlined, no external resources — and contains eight metric sections, each with bars (normalized to the series' maximum value) and a fallback table view, plus three panels showing concept and system inventories.

The page's metadata header carries counts of ideas, events, backlog phases, concepts, terms, and systems — all figures copied verbatim from `tools/overview_metrics.py` and `tools/overview_inventory.py` output, never recomputed. The `{{GENERATED_AT}}` label is the reference timestamp from the metrics tool (the latest timestamp already in the idea log), not a render-time wall-clock timestamp, ensuring generation-to-generation identity.

## Failure and recovery

An error in either subprocess — failed metrics or inventory tool invocation, malformed JSON, schema violation in the source files — prints to stderr with exit 1. Fix the underlying source file (check `_data/ideas.jsonl` validity, `docs/09-backlog/backlog.yaml` YAML syntax, or `brain/` concept memories) and rerun. The tool never modifies any source file. If the page renders but looks malformed, verify all source files against their schemas and that the template files under `templates/html/` are present and valid.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_overview.py`

Render the D-System overview page from `tools/overview_metrics.py` and
`tools/overview_inventory.py` output.

This tool computes nothing itself. It runs the two phase-demo-03 tools as subprocesses —
exactly the way idea `000071` and REQ-006 R07 already verify them — parses their stdout JSON,
and fills the `templates/html/overview-*.html` + `templates/styles/overview.css` template
family with plain `{{TOKEN}}` string substitution, per the token contracts documented at the
top of each template. No figure on the page is computed here; every number is copied verbatim
from one of the two tools' own output (REQ-006 R08).

Deterministic end to end. `overview_metrics.py` and `overview_inventory.py` are themselves
deterministic (same inputs, same output bytes, no model or network call — see their own
docstrings), and this renderer adds no wall-clock or random input of its own: the page's
`{{GENERATED_AT}}` label is `overview_metrics.py`'s own `meta.reference_at` (the latest
timestamp already in the idea log, not `datetime.now()`), not a render-time timestamp — so
generating twice against an unchanged repository produces byte-identical bytes. This is a
narrower reading of `templates/html/overview-page.html`'s token-contract comment, which allows
`{{GENERATED_AT}}` to be wall-clock; the dispatched work item for this tool requires
generation-to-generation identity instead, so the wall clock is never consulted.

    uv run python tools/generate_overview.py               # write _public/overview/index.html
    uv run python tools/generate_overview.py --out FILE     # write elsewhere instead

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--out` | write the page here (default: _public/overview/index.html) |  |  |  |

Exit codes found in source: 0.

<!-- generated:tool-reference:end -->
