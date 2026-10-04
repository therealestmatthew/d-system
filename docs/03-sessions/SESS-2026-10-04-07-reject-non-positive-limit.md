---
schema_version: 1
id: doc-session-reject-non-positive-limit
code: SESS-2026-10-04-07
title: Reject a non-positive --limit in load_context
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-retrieval]
depends_on: []
---

# Reject a non-positive --limit in load_context

## Phase

Unclaimed — owner-directed work, no backlog phase. `fix-load-context-limit` — make
`tools/load_context.py` reject `--limit 0` or a negative value with a clear argparse error instead
of a traceback, add tests, and regenerate OPS-003 if the help text changes (idea 000565).

## Verification

`uv run python -m src.governance`:

```
Governance OK: 44 systems, 429 documents, 36 memories, 347 backlog phases
```

`uv run pytest`:

```
1444 passed, 1 skipped, 1 warning
```

`uv run python tools/check_no_private_content.py` (changes staged):

```
check_no_private_content: OK (1285 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so 0 identifiers were checked here; the primary
checkout's pre-commit run checks all 31 at merge.

Behaviour, run directly against the worktree's projection:

```
--all --limit=0   -> load_context.py: error: argument --limit/-n: must be at least 1, got 0   (exit 2)
--all --limit=-1  -> load_context.py: error: argument --limit/-n: must be at least 1, got -1  (exit 2)
--all --limit=abc -> load_context.py: error: argument --limit/-n: invalid int value: 'abc'    (exit 2)
--all --limit=3   -> 3 memories (exit 0)
```

The new tests run against dev's `tools/load_context.py`: `6 failed, 24 passed`.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- `--limit 0` and negative values fail with a clear argparse error, not a traceback — `Met`.
  Exit 2 with `argument --limit/-n: must be at least 1`; the parametrized CLI test asserts exit
  code 2, the message, no `Traceback` and empty stdout, for `0`, `-1`, `-n -5`, `--limit=-1` and
  `--all --limit 0`.
- Tests added — `Met`. Eight new tests; six fail on the pre-change tool.
- OPS-003 regenerated because the help text changed — `Met`. `generate_tool_docs.py` reports 0
  updated after the commit; the failure section also names the new rejection.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.
Idea 000565's status was left alone, as instructed.

## Unresolved

None.
