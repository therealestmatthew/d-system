---
schema_version: 1
id: doc-ops-generate-agent-workflows
code: OPS-010
title: Generate portable agent workflow adapters
kind: operation
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems: [sys-governance]
depends_on: [doc-portable-agent-workflows, doc-governance-operations]
---

# Generate portable agent workflow adapters

## Trigger

Run after changing the canonical workflow manifest or any canonical workflow body under
`agent-workflows/`. Also run after changing the generator itself so its generated tool reference in
this document remains current.

## Command

```bash
uv run python tools/generate_agent_workflows.py
uv run python tools/generate_agent_workflows.py --check
```

## Expected result

The default command validates workflow authority, capabilities, sources, and target paths, then
rewrites every declared Claude or Open Agent Skills adapter deterministically. `--check` writes
nothing and exits zero only when every expected adapter exists and matches a clean render.

## Failure and recovery

An invalid-manifest result names the failed authority, capability, source, or path contract and exits
2; correct the canonical manifest rather than an adapter. A missing-or-stale result exits 1; run the
write form and review the generated diff. Never edit a generated `SKILL.md` directly.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_agent_workflows.py`

Render host-specific workflow adapters from canonical agent workflow sources.

The manifest at `agent-workflows/workflows.yaml` names one Markdown source per workflow and declares
its authority, required capabilities, and generated targets. This tool validates that contract and
then writes deterministic Claude and Open Agent Skills adapters. Generated adapters are never edited
by hand.

    uv run python tools/generate_agent_workflows.py
    uv run python tools/generate_agent_workflows.py --check

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--check` | Exit 1 if an adapter is missing or stale |  |  |  |

Exit codes found in source: 0, 1, 2.

<!-- generated:tool-reference:end -->
