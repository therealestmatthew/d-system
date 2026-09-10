---
schema_version: 1
id: doc-ops-overview-inventory
code: OPS-012
title: Generate JSON inventories of concepts and systems
kind: operation
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-portfolio]
depends_on: [doc-governance-operations]
---

# Generate JSON inventories of concepts and systems

## Trigger

Run to generate consolidated inventories for reference or indexing. This tool reads from two sources: concept memories under `brain/` (using the same reading conventions as `tools/generate_glossary.py`) and the systems registry at `docs/08-governance/systems.yaml`. Its output is fully deterministic: two runs against an unchanged repository produce byte-identical JSON, with no dependence on wall-clock time or external services.

## Command

```bash
uv run python tools/overview_inventory.py               # print to stdout
uv run python tools/overview_inventory.py --out FILE     # write to FILE instead
```

## Expected result

Exit 0. A JSON document is emitted, deterministically ordered by key and sorted across every list. The document carries metadata (concept count, term count, system count), followed by three inventory sections:

- `concepts`: One row per `type: concept` brain memory, with id, title, tags, and systems
- `terms`: One row per `### Term` heading found in a concept's body (grouped glossary entries), with term name, concept id, and concept title
- `systems`: One row per entry in the systems registry, with id, name, domain, status, and dependency edges

Concepts and terms are sorted by id and term name respectively; systems are sorted by id. A concept memory with no `### ` headings in its body contributes no rows to the terms section — its own entry in concepts already stands for it.

## Failure and recovery

An error in reading `brain/` (malformed front matter, invalid schema) or `docs/08-governance/systems.yaml` (invalid YAML) prints to stderr with exit 1; fix the source file and rerun. The tool never modifies any source file. If `systems.yaml` is missing, the systems section appears empty; if `brain/` has no concept memories, the concepts section appears empty — neither is an error.

<!-- generated:tool-reference:start -->

### Reference: `tools/overview_inventory.py`

Consolidated JSON inventories of the repository's concepts and its systems registry.

Two sections, each read from its own single source of truth. Concepts and terminology come
from `brain/`'s `concept` memories, read exactly the way `tools/generate_glossary.py` reads
them — this module imports that script's `load_concepts()` rather than re-parsing front matter
a second time — plus every `### Term` heading found inside a concept's body, since several
concept memories (`brain/concepts/terms-*.md`) are themselves grouped glossaries of individual
terms. Systems come from `docs/08-governance/systems.yaml`: id, name, domain, status and the
`depends_on` dependency edges, one row per registry entry, nothing inferred or reconciled
against actual imports.

The tool makes no model or network call and asks the wall clock for nothing: every value is a
pure function of `brain/` and `docs/08-governance/systems.yaml`. Two runs against an unchanged
repository produce byte-identical output — every list is sorted and every dict key is emitted
in sorted order (`json.dumps(..., sort_keys=True)`).

    uv run python tools/overview_inventory.py               # print to stdout
    uv run python tools/overview_inventory.py --out FILE     # write to FILE instead

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--out` | write the JSON here instead of stdout |  |  |  |

Exit codes found in source: 0.

<!-- generated:tool-reference:end -->
