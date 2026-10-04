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
Governance OK: 44 systems, 430 documents, 36 memories, 347 backlog phases
```

`uv run pytest`:

```
1450 passed, 1 skipped, 1 warning
```

`uv run python tools/check_no_private_content.py` (changes staged):

```
check_no_private_content: OK (1286 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so 0 identifiers were checked here; the primary
checkout's pre-commit run checks all 31 at merge.

Behaviour, run directly against the worktree's projection:

```
--all --limit=0                    -> error: argument --limit/-n: must be at least 1, got 0    (exit 2)
--all --limit=-1                   -> error: argument --limit/-n: must be at least 1, got -1   (exit 2)
--all --limit=abc                  -> error: argument --limit/-n: invalid int value: 'abc'     (exit 2)
--all --limit 9223372036854775808  -> error: argument --limit/-n: must be at most 9223372036854775807, got 9223372036854775808  (exit 2)
--all --limit=3                    -> 3 memories (exit 0)
```

Before the change, on dev: `--limit -1` crashed with a raw `duckdb.BinderException`; `--limit 0`
did not crash but printed "No memories matched the query." and exited 0; a value above
9223372036854775807 crashed with a raw `ConversionException`. The new tests run against dev's
`tools/load_context.py`: `11 failed, 25 passed`.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- `--limit 0` and negative values fail with a clear argparse error, not a traceback — `Met`.
  Exit 2 with `argument --limit/-n: must be at least 1`; the parametrized CLI test asserts exit
  code 2, the message, no `Traceback` and empty stdout for `0`, `-1`, `-n -5`, `-n-1`,
  `--limit=-1`, `--all --limit 0`, `abc` and 2**63. A value above DuckDB's BIGINT maximum is
  rejected the same way, and `load()` raises `ValueError` for any limit outside 1..2**63-1.
- Tests added — `Met`. Thirteen new test cases (8 parametrized CLI rejections, the `positive_int`
  messages, a limit of 1, the largest BIGINT limit, and 3 parametrized `load()` rejections); 11
  fail on the pre-change tool.
- OPS-003 regenerated because the help text changed — `Met`. `generate_tool_docs.py` reports 0
  updated; the failure section names the rejection and the upper bound.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.
Idea 000565's status was left alone, as instructed.

## Unresolved

None.

## Review

Independent adversarial review by a fresh `demo-adversary` sub-agent (a demo-track reviewer type,
used because the roster has no retrieval-specific adversary), two rounds.

Round 1, range `dev...HEAD` at `ae3e11a`, as reported:

- **Condition 1 — Met, for exactly that literal scope.** Every negative spelling, including
  `-n-1`, and `--all --limit 0` exit 2, stderr only, empty stdout. Premise checked against dev:
  `--limit -1` crashes there, but `--limit 0` does not — it prints "No memories matched the query."
  and exits 0. Implementing both as a usage error is a fair reading of the instruction, but "not a
  traceback" is not an accurate account of what dev did for `0`.
- **Condition 2 — Met.** 8 new tests; focused suite 37 passed.
- **Condition 3 — Met, but the added narrative overstates the fix.**
- **Blocker:** `positive_int` had no upper bound. `--all --limit 9223372036854775808` reached
  DuckDB and crashed with `ConversionException: ... out of range for the destination type INT64`,
  exit 1 — the failure class the idea was filed to remove — which made OPS-003's new sentence
  ("A `--limit` below 1, or one that is not an integer, is rejected the same way ... no query run")
  false.
- **Minor:** the fix was CLI-only; `load(limit=-1)` still raised a raw `BinderException` and
  `load(limit=0)` still returned no results. Latent: nothing else calls `load()` with a supplied
  limit.
- No discrepancy: idea 000565 untouched, backlog untouched, catalog consistent, ruff and mypy clean.

Round 2, `ae3e11a..e2840f0`, as reported:

- **Blocker — Resolved.** 9223372036854775807 succeeds; 9223372036854775808 and
  99999999999999999999 exit 2 with `must be at most 9223372036854775807`. OPS-003's sentence is
  now true.
- **Minor — Resolved.** `load()` raises `ValueError: limit must be between 1 and
  9223372036854775807` for 0, -1 and 2**63; 2**63-1 works.
- Focused suite 43 passed; `generate_tool_docs.py` 0 updated; ruff, mypy, governance clean; idea
  and backlog untouched.
- **New, minor:** the session record had not been updated for the fix. Resolved by this revision of
  the record.

## Decisions

The owner's instruction named 0 and negative values together, so both are usage errors, although
dev only crashed on negatives. The review's blocker was fixed rather than accepted: an upper bound
at 2**63-1, DuckDB's BIGINT `LIMIT` maximum, closes the same "reaches DuckDB raw" failure the idea
was about. The minor finding was fixed too, because one guard in `load()` costs a line and makes
the programmatic path give the same answer as the CLI. Idea 000565's status was left alone, as
instructed.

## Corrections

The record and the first commit message described `--limit 0` as a crash. It was not: dev returned
an empty result with exit 0. The first OPS-003 sentence claimed every bad limit was rejected before
any query ran, which was false for values past the BIGINT maximum until `e2840f0`.

## Left undone

Nothing within the instruction. Moving idea 000565's status is left to whoever owns it.
