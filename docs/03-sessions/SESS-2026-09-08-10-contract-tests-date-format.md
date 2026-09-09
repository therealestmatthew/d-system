---
schema_version: 1
id: doc-session-contract-tests-date-format
code: SESS-2026-09-08-10
title: Make the contract tests and the source preflight agree about dates
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-contracts]
depends_on: [doc-reliability-follow-up]
---

# Make the contract tests and the source preflight agree about dates

## Phase

`phase-rel-11` — Make the contract tests and the source preflight agree about dates.

## Verification

`uv run pytest test/test_schemas.py test/test_source_validation.py`:

```
156 passed, 2 warnings
```

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 98 documents, 13 memories, 101 backlog phases
```

Also run, beyond the phase's own list, to confirm no regression: `uv run pytest` — 372 passed, 2
warnings. `uv run ruff check src/ test/` — one pre-existing failure in `src/governance/__main__.py`
(unsorted import block), confirmed present on `dev` before this branch via
`git show dev:src/governance/__main__.py` and untouched by this change. `uv run mypy src/` — clean,
15 files.

## Acceptance

- A malformed date in a schema fixture fails `test/test_schemas.py`, not only the preflight — Met.
  `test_malformed_date_fails_a_date_check_not_only_a_string_check` asserts `"created":
  "2026-13-45"` fails and names the `created` field; it is in the 156 passed above.
- Both suites reject the same values; no source file or schema changes — Met. Only
  `test/test_schemas.py` changed; `validator()` now passes
  `format_checker=Draft7Validator.FORMAT_CHECKER`, matching the preflight's existing behavior.

## Backlog

`phase-rel-11`: `status: active`, `agent: agent-rel11`. `next_action`: both acceptance conditions
are met and verification has been run in this worktree; ready for `/session-close`.

## Unresolved

None on this phase.

## Review

Independent sub-agent review, given the phase's scope/acceptance/verification, the commit range
`the commit “Claim phase-rel-11 for agent-rel11”..HEAD`, and this session record, with instructions to rerun everything itself rather than
trust the record. Reported verbatim:

> This confirms the preflight (`src/db/source_validation.py:87`) already used
> `format_checker=Draft7Validator.FORMAT_CHECKER` prior to this phase, and the test suite now
> matches it exactly — confirming "both suites reject the same values" is literally true via
> identical mechanism, not just similar outcome.
>
> **Acceptance condition 1** — "A malformed date in a schema fixture fails `test/test_schemas.py`,
> not only the preflight": **Verdict: Holds.**
> - `test/test_schemas.py:161-166` adds `test_malformed_date_fails_a_date_check_not_only_a_string_check`,
>   asserting `"created": "2026-13-45"` fails and names the `created` field.
> - I independently reverted the `FORMAT_CHECKER` wiring and reran just this test: it fails without
>   the fix (`AssertionError: assert 'created' in set()`), then restored the file and reran the full
>   suite — it passes. This proves the test is load-bearing, not a no-op.
> - Independently confirmed via a throwaway script that `Draft7Validator.FORMAT_CHECKER` genuinely
>   rejects `"2026-13-45"` against `{"type": "string", "format": "date"}` (raises `'2026-13-45' is
>   not a 'date'`), while a bare `{"type": "string"}` check passes it. This is a real check, not the
>   `date-time`/`rfc3339-validator` no-op the session record flags — confirmed the schemas here
>   (`schemas/commitment.schema.json:35`, `"created": {"type": "string", "format": "date"}`) use
>   `format: "date"` throughout, which `jsonschema`'s built-in format checker handles correctly
>   without extra dependencies (`date-time` is the one that needs `rfc3339-validator`).
>
> **Acceptance condition 2** — "Both suites reject the same values; no source file or schema
> changes": **Verdict: Holds.**
> - `git diff the commit “Claim phase-rel-11 for agent-rel11”..HEAD --name-only` touches only `test/test_schemas.py`,
>   `docs/03-sessions/SESS-2026-09-08-10-contract-tests-date-format.md`,
>   `docs/08-governance/catalog.md`, `docs/09-backlog/backlog.yaml` — confirmed no file under
>   `schemas/`, `src/`, or `sql/` changed.
> - `test/test_schemas.py`'s `validator()` (lines 30-35) now passes
>   `format_checker=Draft7Validator.FORMAT_CHECKER`, mirroring `src/db/source_validation.py:87`,
>   which already used the identical checker before this phase — so the two suites now use the exact
>   same mechanism, not just coincidentally-matching behavior.
>
> **Verification commands, rerun independently:**
> - `uv run pytest test/test_schemas.py test/test_source_validation.py` → `156 passed, 2 warnings`
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 98 documents, 13 memories, 101
>   backlog phases`
> - Extra checks the session record claims, also reran: `uv run pytest` → `372 passed, 2 warnings`
>   (matches); `uv run ruff check src/ test/` → 1 pre-existing unsorted-import error in
>   `src/governance/__main__.py`, confirmed untouched by this diff (matches); `uv run mypy src/` →
>   clean, 15 files (matches).
>
> **Minor non-blocking note:** the session record's embedded verification output shows "97
> documents" while catalog.md as committed (and my fresh rerun) shows 98 — the record's own diff
> bumps the catalog's document count from 97→98 (adding the session doc itself), so the session
> record must have captured that governance output before finalizing catalog.md. This is a
> sequencing artifact in the record, not a functional discrepancy — the code and tests are
> unaffected, and the currently committed state is internally consistent (catalog says 98,
> governance reports 98).
>
> **No discrepancies found** in the two acceptance conditions themselves, the "no source/schema
> changes" claim, or the backlog.yaml diff (which correctly shows the `rfc3339-validator`/
> `pyproject.toml` scope reverted, consistent with the session record's documented correction).

The one note raised (the record's embedded `## Verification` snippet said "97 documents" before
this close regenerated it to "98") is fixed above by refreshing that snippet to match the current,
correct governance output. No other discrepancy stood.

## Decisions

- Orienting on the backlog queue surfaced that `phase-idea-02` (front of `next_up`) cannot meet its
  own acceptance as scoped — it requires attaching triage findings to an idea, and no mechanism for
  that exists yet; `PLAN-017.04` (draft) says as much and is still unsettled. Asked the owner, who
  chose to skip it for this session rather than fix its metadata or work the open design questions.
  `phase-idea-02` was left untouched.
- Chose `phase-rel-11` as the next phase in queue order.

## Corrections

While orienting on `phase-rel-11`, I initially proposed adding `rfc3339-validator` to
`pyproject.toml` as part of the phase's scope, reasoning from a test against `format: "date-time"`
(`Draft7Validator.FORMAT_CHECKER` silently accepts a malformed `date-time` string without that
package installed). I asked the owner and they approved adding it. Before implementing, I tested
the format this phase actually touches — every schema `test/test_schemas.py` validates (`task`,
`interaction`, `decision`, `waiting-on`, `development-event`, `evidence`, `commitment`, `project`)
uses `format: "date"`, not `date-time` — and confirmed plain `date` format-checking works correctly
with no extra dependency. The `date-time` gap is real but belongs to `idea.schema.json`, which
`test_schemas.py` never validates. I said so as a correction and reverted the scope/deliverables
addition before writing any implementation code, so `pyproject.toml` was never touched. The
sub-agent review independently confirmed this distinction (`format: "date"` needs no extra
dependency; `format: "date-time"` does).

## Left undone

Nothing on `phase-rel-11` itself. Two things noticed but out of scope for this phase, left for the
owner or a future session:

- The primary checkout held a git stash (`WIP on dev: the commit “Close phase-plc-01 via /session-close” Close phase-plc-01 via
  /session-close`, based on a commit not reachable from current `dev`) and an untracked
  `docs/00-working/gemini-knowledge-retrieval-report.md`, neither created by this session. Left
  untouched; may indicate concurrent activity on the primary checkout worth the owner's attention.
- `phase-idea-02` remains queued with a stale `next_action` ("Deferred until phase-idea-01 lands")
  even though `phase-idea-01` is complete; its real blocker is the unsettled `PLAN-017.04` design
  work, not that stale text. Not corrected this session since the owner chose to skip rather than
  fix it.
