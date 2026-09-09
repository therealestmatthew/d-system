---
schema_version: 1
id: doc-ops-generate-glossary
code: OPS-004
title: Generate the glossary from brain concepts
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-brain]
depends_on: [doc-governance-operations]
---

# Generate the glossary from brain concepts

## Trigger

Run after adding or editing a `type: concept` memory under `brain/concepts/`. `docs/08-governance/GLOSSARY.md`
is a generated view of those memories, never a second place to define a term, and it drifts the
moment a concept changes without a regeneration.

## Command

```bash
uv run python tools/generate_glossary.py                    # write the full glossary
uv run python tools/generate_glossary.py --check             # exit 1 if stale
uv run python tools/generate_glossary.py --tag frameworks --out /tmp/g.md   # a filtered slice
```

## Expected result

The unfiltered form overwrites `docs/08-governance/GLOSSARY.md` deterministically — the same
concepts always render to the same bytes — and only that unfiltered file is committed. A filtered
glossary (`--tag`/`--system`) requires `--out`, since a scoped slice is never the committed file.

## Failure and recovery

`--check` exits 1 and names the file when the committed glossary does not match a fresh render;
regenerate it, never hand-edit it. A missing `brain/` directory is not an error — it renders an
empty glossary.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_glossary.py`

Render a glossary from brain/'s `concept` memories.

Definitions are canonical in brain/ (PLAN-012); this renders them deterministically into a
generated Markdown document — never hand-written, same rule as docs/08-governance/catalog.md and
docs/00-working/ideas.md: a header says so, and a test fails on any difference from regenerated
output. Filterable by tag or system, so a targeted glossary ("everything about sys-brain") doesn't
require reading the whole knowledge base.

    uv run python tools/generate_glossary.py                     # write the full glossary
    uv run python tools/generate_glossary.py --tag frameworks    # a filtered glossary, to --out
    uv run python tools/generate_glossary.py --system sys-brain --out /tmp/g.md
    uv run python tools/generate_glossary.py --check             # exit 1 if stale

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--tag` | Only terms carrying this tag |  |  |  |
| `--system` | Only terms carrying this system |  |  |  |
| `--out` | Write to a different path — required for a filtered glossary |  |  |  |
| `--check` | Exit 1 if the target file is stale |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
