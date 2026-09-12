---
schema_version: 1
id: doc-session-2026-09-07-02
code: SESS-2026-09-07-02
title: Make the idea write path safe and single-source the replay
kind: session
status: active
owner: repository-owner
created: '2026-09-07'
updated: '2026-09-07'
systems: [sys-portfolio, sys-projection]
depends_on: [doc-idea-plan-writing-projection, doc-idea-plan-event-contract, doc-idea-plan-lifecycle-requirements]
---

# Make the idea write path safe and single-source the replay

## What happened

`phase-idea-04` was executed in a dedicated worktree (`agent-idea04`), concurrently with an
unrelated agent building the checkpoint skill and session-close command (`phase-ses-03`/`05`) in its
own worktree. Before either claim was made, the two phases' declared `.claude` deliverable paths
were narrowed (bare `.claude` → `.claude/skills/checkpoint` and `.claude/commands/session-close.md`)
to remove a false collision with this phase's `.claude/commands/idea.md`.

## What changed

**The safe write path replaces the dangerous documented one.** `tools/append_idea.py` gains
`--file PATH` (title = first line, body = the rest) and the same combined-blob form on bare stdin
when `--title` is omitted — the route `--title` never had before. `.claude/commands/idea.md` now
instructs writing the idea to a file via the Write tool and invoking `add --file`, rather than
inlining prose into a double-quoted `--body "..."` shell argument, which is exactly how idea `000019`
was corrupted. `--title`/`--body` remain for short, hand-typed, plain-text titles.

**One replay implementation.** `src/db/ideas.py` is new: `IdeaError`, `WORKING_STATES`,
`legal_transitions()`, `load_events()` and `fold()` all moved there from `tools/append_idea.py`,
which now imports them. `tools/rebuild_db.py`'s inline reimplementation of the fold (its own
`folded[idea] = {...}` state machine) is deleted in favor of importing the same `fold()`. Nothing
in `test/` reimplements it — `test/test_ideas.py` already only ever called `append_idea.fold`, which
now forwards to the shared module.

**`fold()` now validates history, not just replays it.** It raises `IdeaError` on a mismatched
`from`, an illegal `from -> to` pair, a duplicate `created`, an event for an idea with no preceding
`created`, and a second `revisited`. `src/db/source_validation.py`'s `validate_ideas()` now runs this
same `fold()` over every schema-valid line before `rebuild_db.py` drops a single table — previously
it only checked ordering (`created` precedes, no duplicate), not the `from`-check at all.

**Two tests were actually wrong, not just under-exercised.** All 19 real events in
`_data/ideas.jsonl` are `created`, so no existing test drove a second event through the projection.
`test_time_in_each_state_is_queryable_without_parsing_markdown`'s window ordered
`LEAD(occurred_at) OVER (PARTITION BY idea ORDER BY seq)` — `seq` is a per-idea append ordinal, not a
clock, and nothing guarantees it agrees with real time once two worktrees' appended lines are
interleaved by a merge. A new `projected_with_transitions` fixture adds two synthetic events to idea
`000001` (never written to the real log) whose `seq` is deliberately out of instant order — this
reproduces a real `-1800`-second duration under the old `ORDER BY seq`, confirmed by
`test_the_time_in_each_state...`'s own assertion of that exact value, and fixed by ordering the
window by `occurred_at` instead. `test_mixed_offsets_compare_as_the_same_instant`'s prior assertion
(`list(idea ORDER BY occurred_at) = list(idea ORDER BY idea)`) only ever passed because every idea
had exactly one event; it is replaced with an assertion that actually exercises mixed offsets against
the same synthetic fixture.

**Five negative fixtures prove the from-check fires before any write.** Hand-built, schema-shaped,
historically-impossible event lists — mismatched `from`, illegal transition, duplicate creation,
unknown idea, second revisit — each raise `IdeaError` from `fold()` directly, plus one test proving
`validate_sources()` catches a broken log in the rebuild preflight, before `rebuild_db.py:88-90`
would otherwise drop every table.

**The safe route is proven against the real CLI, and against a live subprocess.** Two new tests
drive `append_idea.main()` (real argparse parsing and dispatch, not the underlying function) with a
monkeypatched `LOG`, feeding prose containing backticks, `$(...)`, quotes, a newline and non-ASCII
through `--file` and through stdin; both assert the stored event matches byte-for-byte and that a
sentinel file the embedded commands would have created does not exist. This required a small,
otherwise-unrelated fix: `main()` previously called `add()`/`change_status()`/`revisit()` relying on
their `log: Path = LOG`-bound defaults, which are frozen at function-definition time and cannot be
redirected by patching the module's `LOG` attribute; `main()` now passes `log=LOG` explicitly at each
call so it reads the current module global. Beyond the automated tests, this was also verified live:
a real subprocess invocation against the actual committed log (immediately reverted afterward, never
committed) stored the dangerous prose unchanged and created no sentinel file.

## A mistake caught and corrected mid-session

Regenerating `docs/08-governance/catalog.md` with `uv run python -m src.governance --catalog
>/dev/null 2>&1` silently discarded the output — `--catalog` prints to stdout; it does not write the
file in place. This meant the claim commit for `phase-ses-03`/`phase-idea-04` (made before this
phase's substantive work began) carried a stale catalog showing zero active phases. It was caught by
`test/test_codes.py::test_committed_catalog_matches_regenerated_output` failing in this worktree,
diagnosed against `dev` (where the concurrent agent had already regenerated the file correctly as
part of its own work), and fixed here with the correct form: `--catalog > docs/08-governance/catalog.md`.

## Verification

```
$ uv run pytest test/test_ideas.py
30 passed, 2 warnings

$ uv run ruff check src/ test/ tools/
Found 1 error.  (tools/load_context.py:101, F541 — pre-existing, untouched by this phase)

$ uv run mypy src/
Success: no issues found in 12 source files

$ uv run pytest
299 passed, 2 warnings
```

`_data/ideas.jsonl`, `schemas/idea.schema.json` and `sql/001_schema.sql` are byte-identical
(`git diff --stat` empty for all three) — this phase writes no production idea data and changes no
schema, matching its acceptance.

## Acceptance

- **Prose containing backticks, `$(...)`, quotes, newlines and non-ASCII survives the real CLI
  unchanged, and no sentinel command executes.** Met — `test_dangerous_prose_survives_the_real_cli_via_file`,
  `..._via_stdin`, and the live manual subprocess check above.
- **One replay implementation and one transition table have all consumers; no copy remains in
  `test/`.** Met — `src/db/ideas.py` is the only definition; verified by grep for the fold's
  characteristic state-machine lines outside that file.
- **A mismatched `from`, an illegal transition, a duplicate creation, an unknown idea and a second
  revisit each fail before the log or the database is touched.** Met — five `fold()`-level tests plus
  `test_a_broken_log_fails_the_rebuild_preflight_before_any_table_drops`.
- **No event or document schema changed, and the existing log is byte-identical.** Met.

All four acceptance conditions hold; `phase-idea-04` is complete.

## What the next session should know

`phase-idea-07` ("Add event identity and the amendment fold") depends on this phase and now has a
single `fold()` to extend rather than three. The `eid`/`amended`/identity work described in
`PLAN-017.03` was explicitly out of scope here and untouched.

## Review

This phase was marked `status: complete` directly in `backlog.yaml` before `session-close`
(`phase-ses-05`) existed — it was built concurrently, in a peer worktree, by the same session. Once
`session-close` landed, the owner asked for it to be run retroactively against this phase's
completion claim. A fresh, non-fork sub-agent independently reviewed the four commits
(the commit “Single-source the idea event replay and check history, not just shape”, the commit “Give idea prose a route into the writer that never touches a shell”, the commit “Repair two tests that only passed because every idea had one event”, the commit “Complete phase-idea-04: the idea write path is safe and single-sourced”), re-ran every verification command itself, and
independently judged each acceptance condition from the diff rather than this record's prose.
Pasted verbatim:

> I read all four commits' full diffs, ran all four verification commands myself, and independently
> checked the four acceptance conditions against the diff rather than the session record's prose.
> Summary: the phase's substantive work is real and the verification commands match the record
> exactly. I found one genuine gap the record does not mention.
>
> **Verification commands — my own run**
> ```
> uv run pytest test/test_ideas.py      → 30 passed, 2 warnings
> uv run ruff check src/ test/ tools/   → 1 error: tools/load_context.py:101 F541 (pre-existing, unrelated)
> uv run mypy src/                      → Success: no issues found in 12 source files
> uv run pytest                         → 299 passed, 2 warnings
> ```
> All four numbers match the session record's Verification section exactly. Working tree is clean.
>
> **1. Dangerous prose survives the real CLI unchanged, no sentinel executes — HOLDS.**
> `test/test_ideas.py:218` and `:249` drive `append_idea.main()` (real argparse dispatch, not the
> bare function) with a monkeypatched `LOG`, feeding a title/body containing backticks,
> `$(touch <sentinel>)`, single/double quotes, a newline and non-ASCII (`Ünïcødé 日本語`). They
> assert `exit_code == 0`, `not sentinel.exists()`, and that the stored JSON matches byte-for-byte.
> This is a real test, not a weak one — it goes through `main()`'s actual arg parsing, and the
> `log=LOG` fix in `tools/append_idea.py` (main() now passes `log=LOG` explicitly at each call
> instead of relying on frozen `log: Path = LOG` defaults) is what makes the monkeypatch actually
> take effect — a subtle, correct, and necessary fix that's called out honestly in the record.
>
> **2. One replay implementation, one transition table, no copy in test/ — HOLDS.**
> `grep -rln "def fold"` across the repo returns only `src/db/ideas.py` (definition),
> `tools/append_idea.py` (imports it), `test/test_ideas.py` (calls it). `tools/rebuild_db.py`'s prior
> inline state machine is gone, replaced by `fold_ideas(events)` imported from `src/db/ideas.py`. The
> transition table lives only in `schemas/idea.schema.json`'s `oneOf` list; `legal_transitions()` is
> its only reader, confirmed by `test_the_transition_table_comes_from_the_schema`.
>
> **3. The five negative cases fail before the log or database is touched — HOLDS.**
> Five direct tests call `append_idea.fold(events)` on hand-built, in-memory, schema-shaped-but-
> historically-impossible event lists — none ever create or touch a log file. A sixth test,
> `test_a_broken_log_fails_the_rebuild_preflight_before_any_table_drops`, exercises the actual
> preflight path that guards `rebuild_db.py`'s table drop, not a synthetic stand-in.
>
> **4. No schema/DDL changed, log byte-identical — HOLDS.**
> A diff from “Single-source the idea event replay and check history, not just shape” to
> “Complete phase-idea-04: the idea write path is safe and single-sourced”, over
> `_data/ideas.jsonl`, `schemas/idea.schema.json` and `sql/001_schema.sql`, returns empty. Confirmed
> independently.
>
> **General findings.** Session record accuracy: everything I checked — commit contents,
> verification numbers, the `log=LOG` fix rationale, the 19-created-events claim, idea `000019`'s
> corruption still visible and unrepaired — checks out. I found nothing the record overstates or
> misrepresents.
>
> **One real defect the record does not mention (scope gap, not an acceptance failure):** the
> phase's scope says "rewrite the example in the idea command so the form an agent copies is the
> safe one," and `.claude/commands/idea.md` was correctly rewritten. But `tools/generate_ideas_md.py`
> — itself in this phase's declared file list — still hardcoded the old dangerous form into the
> header template it writes into `docs/00-working/ideas.md`. Since `.claude/commands/idea.md`'s own
> "Afterwards" step instructs regenerating that file, the dangerous example persisted as a second,
> still-live copy of "the example an agent might copy." `docs/00-working/README.md` had the same
> stale example. This doesn't break any of the four literal acceptance bullets, but it undercuts the
> stated purpose of the phase.

**Disposition:** the one gap raised is a real, fair catch. Fixed in this same session, after the
review returned — see Corrections below. No other finding stood; the four acceptance conditions are
independently confirmed to hold.

## Decisions

- Delegated `phase-ses-03`/`phase-ses-05` to a separate agent working concurrently in its own
  worktree, while working `phase-idea-04` directly, per the owner's explicit direction to split the
  session this way.
- Narrowed both phases' declared `.claude` deliverable paths before either claim landed, rather than
  leaving the bare `.claude` collision to surface later — a small, targeted backlog correction judged
  safe to make unprompted since it only removed a false conflict, not any real scope.
- Chose to give `--title` a *combined* stdin/file route (first line = title, rest = body) rather than
  a second `--title-file` flag alongside `--body-file`, since stdin can only be read once per
  invocation and the plan document's own open question recommended "both stdin and a file" without
  specifying the shape — this was the simplest design that actually closes the gap ("`--title` has no
  stdin path at all") the source plan identified.
- Reproduced the `seq`-vs-`occurred_at` ordering defect with a *deliberately* time-inverted synthetic
  fixture (seq 2 chronologically after seq 3) rather than a naturally-ordered one, after an initial
  fixture attempt turned out not to actually exercise the bug — verified against both the old and new
  `ORDER BY` clause before committing, so the regression test is provably meaningful rather than
  incidentally passing.

## Corrections

- **`--catalog` output redirected to `/dev/null` instead of the file.** `--catalog` prints to stdout;
  it does not write in place. The first claim commit for this phase and `phase-ses-03` therefore
  carried a stale catalog. Caught by `test_committed_catalog_matches_regenerated_output` failing in
  this worktree; fixed with the correct form (`--catalog > docs/08-governance/catalog.md`) before
  continuing, and again at rebase/completion time.
- **A real test-log write during manual CLI verification.** A live smoke test of `--file` against the
  actual CLI wrote a throwaway idea (`000020`, since reused by the unrelated real idea recorded
  later) into the real, committed `_data/ideas.jsonl`. Caught immediately after the smoke test
  (the point of running it was to observe the write), reverted with `git checkout -- _data/ideas.jsonl`
  before anything else touched the file, confirmed clean.
- **Stale unsafe example left in two generated/documentation files.** Caught by the retroactive
  independent review above, not by this session's own verification — `tools/generate_ideas_md.py`'s
  `HEADER` template and `docs/00-working/README.md` still showed `--title "..." --body "..."` as the
  example, even though `.claude/commands/idea.md` had been correctly rewritten. Both now show
  `--file` as the primary example, with `--title`/`--body` noted as existing only for short,
  hand-typed, plain-text titles. `docs/00-working/ideas.md` regenerated afterward;
  `uv run pytest test/test_ideas.py` (30 passed) and the full suite (299 passed) confirmed green
  after the fix.
- **A duplicate session-code allocation across concurrent agents.** Both this session and the
  peer agent independently allocated `SESS-2026-09-07-01` for their own session records. Resolved
  per `AGENTS.md`'s collision rule (the agent integrating second renumbers) by renumbering this one
  to `SESS-2026-09-07-02` during rebase, and updating the one `backlog.yaml` reference to it.

## Left undone

None known beyond the already-declared next step: `phase-idea-07` extends the single `fold()` this
phase created with `eid`/identity/amendment support, which was explicitly out of scope here. No
acceptance condition, scope item, or reviewer finding remains open.
