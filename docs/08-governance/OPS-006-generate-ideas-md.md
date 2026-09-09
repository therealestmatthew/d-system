---
schema_version: 1
id: doc-ops-generate-ideas-md
code: OPS-006
title: Regenerate the parked-ideas view
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio]
depends_on: [doc-governance-operations]
---

# Regenerate the parked-ideas view

## Trigger

Run after `tools/append_idea.py` ([OPS-005](OPS-005-append-idea.md)) writes a new event to
`_data/ideas.jsonl`. `docs/00-working/ideas.md` is a rendered view of that log, not a second source
— it was the source of truth before `phase-idea-01` and is now generated only.

## Command

```bash
uv run python tools/generate_ideas_md.py           # write the file
uv run python tools/generate_ideas_md.py --check   # exit 1 if it is stale
```

## Expected result

`docs/00-working/ideas.md` is overwritten deterministically from the folded event log — the same
log always renders to the same bytes, which is what lets `--check` treat a hand edit as a failure
rather than something to merge.

## Failure and recovery

`--check` exits 1 when the committed file does not match a fresh render; regenerate it, never
hand-edit it. If the render itself looks wrong, the defect is in the event log or in
`append_idea.fold`, not in this script — fix the log via `tools/append_idea.py`, not this file.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_ideas_md.py`

Render docs/00-working/ideas.md from _data/ideas.jsonl.

The markdown list was the source of truth until phase-idea-01; it is now a view. The
source is the event log, and this renders it — same rule as docs/08-governance/catalog.md
and the glossary in PLAN-012: a header saying so, and a test failing on any difference from
regenerated output.

Rendering is deterministic. Given the same log it produces the same bytes, which is what
lets the test treat a hand edit as a failure rather than a merge.

    uv run python tools/generate_ideas_md.py           # write the file
    uv run python tools/generate_ideas_md.py --check   # exit 1 if it is stale

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--check` | fail if the file is stale |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
