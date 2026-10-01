---
schema_version: 1
id: doc-session-backlog-idea-field
code: SESS-2026-10-01-01
title: Give backlog phases a structured idea field and backfill it (phase-des-08)
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-backlog]
depends_on: [doc-html-generation-design-system]
---

# Give backlog phases a structured idea field and backfill it (phase-des-08)

## Phase

`phase-des-08` — Give backlog phases a structured idea field and backfill it. Run by Session 5 -
Batch Runner as agent `agent-coord`, claimed at 3a4e87e with the owner's approval, on branch
`agent/phase-des-08`.

## Verification

Run in the worktree, rebased onto dev 458ab36: pytest and mypy on 5014690, governance after
this record was added.

`uv run pytest`

```
1198 passed, 1 warning in 163.36s (0:02:43)
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 410 documents, 34 memories, 347 backlog phases
```

`uv run mypy src/`

```
Success: no issues found in 46 source files
```

Also run: `uv run ruff check src/ test/` gave `All checks passed!`, and
`uv run python -m src.governance --check-ideas` gave
`Idea field check: 100 phases name 167 ideas; 0 phases differ (0 missing, 0 extra)` with exit 0.

## Acceptance

- REQ-036 R17 holds (a fixture phase with a made-up id fails the validator naming it, and the
  committed backlog passes): Met. `test_ideas_field_rejects_an_id_the_idea_log_does_not_contain`
  asserts the exact error `phase-demo-01: ideas names 999999, which is not in _data/ideas.jsonl`,
  and the committed backlog, which now carries the field on 100 phases, passes governance above.
- REQ-036 R18 holds (the backfill's check mode reports no missing and no extra ids): Met.
  `--check-ideas` above reports 0 missing and 0 extra. `test_repository_idea_field_matches_its_backfill`
  asserts the same on every test run.

## Backlog

`status: active`, `agent: agent-coord`. `next_action`: built and verified; independent review of
the branch against REQ-036 R17 and R18, then READY to the Session Manager and the owner's merge
approval.

## Unresolved

- The backfill was run on dev 458ab36. Any later edit to a phase's scope, acceptance or next_action
  that names an idea id, merged before this branch, needs `--backfill-ideas` re-run after the rebase.
  The default governance run does not enforce the derived match; only `--check-ideas` reports it.

## Review

Independent review by a `demo-adversary` agent (Sonnet) over 458ab36..4bbbd21, recorded as it reported:

- REQ-036 R17: Met. On a scratch copy of the repository, id `888888` injected into phase-wbf-11's
  `ideas:` block made `uv run python -m src.governance` exit 1 with
  `ERROR phase-wbf-11: ideas names 888888, which is not in _data/ideas.jsonl`.
- REQ-036 R18: Met. `--check-ideas` reported `100 phases name 167 ideas; 0 phases differ (0 missing,
  0 extra)`, exit 0.
- Reruns: pytest 1198 passed; governance OK at 410 documents; mypy clean; `--catalog` byte-identical.
- backlog.yaml diff, parsed and compared phase by phase with `ideas` removed: the only other changes
  are phase-des-08's own `next_action` and the top-level `updated` date.
- `named_ideas()` over all 347 phases against an independent `\b\d{6}\b` scan intersected with
  fold(): 0 mismatches.
- Backfill guard: with `backfill_ideas_text` patched to also change a `priority`, `--backfill-ideas`
  exited 1 with `ERROR idea backfill would change more than the ideas fields; nothing written` and
  left the file byte-unchanged.
- Every idea-log read in `src/governance/` goes through `fold(load_events(...))`.
- GOV-002's new paragraph matches the code on all four claims it makes.
- Findings: none.

Evidence: `_working/session-manager/des-08-review.md`.

## Decisions

- The backfill rewrites `backlog.yaml` as text, inserting or removing only `ideas:` blocks just
  before each phase's `systems:` line, rather than dumping the parsed YAML. A dump would have
  reflowed every long string in a file of over 15,000 lines. The rewrite is re-parsed and compared
  before it is written, so it cannot change anything else.
- The idea log is read only when some phase carries the field, so test fixtures and other callers
  without the field need no idea log.
- The default governance run checks only that every id exists (R17). Whether each phase's field
  still matches its text is reported by `--check-ideas`, which exits 1 on any difference. Making the
  default run enforce the match would be a new rule nobody asked for.
- The owner approved writing the field into phase-idg-19, then active under Builder B, because
  R18 requires every phase naming an id to carry it. Builder B was told through the Session
  Manager. Builder B's completion landed first, so the branch was rebased and the backfill re-run
  on dev 458ab36 (167 links rather than the 164 found before the rebase).
- The work replaced phase-dgov-06, which the owner had approved claiming. The Session Manager
  relayed the owner's ruling that the pages come first and that the two phases collide on
  sys-backlog and src/governance/__main__.py; dgov-06 was never claimed.

## Corrections

- A test first asserted that a missing idea log produces a `backlog inputs` error. `load_events`
  reads a missing log as empty, so the id is reported as unknown instead, which is still a failure
  that names it; the test was corrected to assert that.

## Left undone

- Nothing in the phase's scope. The drift noted under Unresolved is by design: the field is
  maintained by re-running `--backfill-ideas`.
