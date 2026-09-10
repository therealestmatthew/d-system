---
schema_version: 1
id: doc-session-portable-workflow-foundation
code: SESS-2026-09-09-03
title: Canonical workflows and portable skill adapters
kind: session
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems: [sys-governance, sys-delivery]
depends_on: [doc-portable-agent-workflows]
---

# Canonical workflows and portable skill adapters

## Phase

`phase-port-01` — Establish canonical workflows and portable skill adapters.

## Verification

`uv run python tools/generate_agent_workflows.py --check`

```text
4 workflow adapter(s) current
```

`uv run pytest test/test_agent_workflows.py`

```text
10 passed, 2 warnings
```

`uv run python -m src.governance`

```text
Governance OK: 16 systems, 117 documents, 15 memories, 105 backlog phases
```

`uv run pytest`

```text
405 passed, 2 warnings
```

Additional targeted quality checks:

```text
uv run ruff check tools/generate_agent_workflows.py test/test_agent_workflows.py
All checks passed!

uv run mypy src/ tools/generate_agent_workflows.py
Success: no issues found in 16 source files
```

A broader `uv run ruff check src/ test/ tools/generate_agent_workflows.py` run reported one existing
import-order failure in `src/governance/__main__.py:6`; this phase did not change that file. The
targeted generator and test files pass Ruff.

## Acceptance

- **Met:** Orientation and checkpoint have one body each under `agent-workflows/`; the generator
  produces current Claude and Open Agent Skills representations from those bodies.
- **Met:** Contract tests refuse owner-only workflows on agent-discoverable targets and refuse a
  required capability without a mapping or explicit unsupported declaration.
- **Met:** Contract tests detect adapter tampering, render deterministically, reject path traversal,
  and reject missing or out-of-tree canonical sources.
- **Met:** PROMPT-008 names the canonical checkpoint workflow and plain-prompt fallback, retains the
  owner-only completion boundary, and contains no Claude checkpoint path.

## Backlog

- Status: `active`
- Next action: Implementation and declared verification are complete; the owner can invoke
  session-close for independent review and the completion decision.
- Evidence: canonical workflow sources and manifest, four generated adapters, generator and tests,
  OPS-010, updated PROMPT-008, and this session record.

## Unresolved

Independent review and the owner-controlled completion transition remain. The unrelated existing
Ruff import-order finding in `src/governance/__main__.py` remains outside this phase.
