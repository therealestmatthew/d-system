---
schema_version: 1
id: doc-ops-generate-tool-docs
code: OPS-007
title: Regenerate the per-tool reference blocks
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance]
depends_on: [doc-governance-operations]
---

# Regenerate the per-tool reference blocks

## Trigger

Run after changing any tool's module docstring, `argparse` arguments, or a literal exit code —
whatever this script itself reads out of a tool's source. This tool documents every tool under
`tools/`, itself included: it parses `tools/generate_tool_docs.py`'s own source with the same
static `ast` reader it uses on every other tool, so a change to this file's own docstring or
arguments goes stale in this document exactly the way a change anywhere else goes stale in its
document.

## Command

```bash
uv run python tools/generate_tool_docs.py           # update every paired doc in place
uv run python tools/generate_tool_docs.py --check   # exit 1 if any paired doc is missing or stale
```

## Expected result

Every tool under `tools/` is paired with its `OPS-*` document by the `OPS-NNN-<tool-stem>.md`
filename convention, and the generated block inside each is rewritten from that tool's real
source — module docstring, `argparse` flags/help/choices/default/required, and any literal `return`
or `SystemExit` exit code. Nothing outside the `<!-- generated:tool-reference:start/end -->`
markers is touched; a tool's hand-written narrative is never regenerated.

## Failure and recovery

`no OPS document found for: <name>` means a tool exists with no paired document yet — write one by
hand (narrative plus an empty marker block), following AGENTS.md's convention, then rerun. This
script never creates that document itself. `--check` exits 1 and names any document whose generated
block does not match a fresh render; regenerate it, never hand-edit the block between the markers.
Static extraction has one known limit: an argument's `choices=` computed at parse time rather than
written as a literal (see `tools/append_idea.py`'s `status` subcommand) renders as an empty cell,
since `ast.literal_eval` cannot evaluate a function call — the hand-written narrative is the place to
name those values instead.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_tool_docs.py`

Regenerate the generated-reference block inside each tool's OPS document.

Each tool under `tools/` is paired with an `OPS-*` document in `docs/08-governance/` by the
repository's own `<code>-<slug>.md` filename convention: `tools/rebuild_db.py` pairs with
whichever `docs/08-governance/OPS-*-rebuild-db.md` exists. The narrative half of that document
(what the tool is for, its contract, its failure modes) is hand-written and never touched here.
The reference half — the tool's module docstring, its `argparse` arguments and the exit codes its
source actually returns or raises — is mechanical and lives between two HTML comment markers this
script owns exclusively:

    <!-- generated:tool-reference:start -->
    ...
    <!-- generated:tool-reference:end -->

This script never creates a document. A tool with no matching OPS document is reported and left
alone; writing one, with its narrative half, is a human decision (PLAN-013).

    uv run python tools/generate_tool_docs.py           # update every paired doc in place
    uv run python tools/generate_tool_docs.py --check   # exit 1 if any paired doc is stale

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--check` | Exit 1 if any paired doc is missing or stale |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
