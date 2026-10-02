---
schema_version: 1
id: doc-session-review-judge-agent-build
code: SESS-2026-10-02-01
title: The reviewer-judge agent type, in shadow — build
kind: session
status: active
owner: repository-owner
created: '2026-10-02'
updated: '2026-10-02'
systems: [sys-governance]
depends_on: [doc-reviewer-contract]
---

# The reviewer-judge agent type, in shadow — build

## Phase

`phase-asr-01` — The reviewer-judge agent type, in shadow, with a test that its tools stay
read-only. Continues `SESS-2026-10-01-06`, which checkpointed the phase before any deliverable was
written.

## Verification

`uv run pytest test/test_agent_tools.py`

```
5 passed, 1 warning
```

`grep -n "session record" .claude/agents/review-judge.md`

```
71:- Never read the builder's session record or report, or anything else the builder wrote about
```

`uv run ruff check src/ test/`

```
All checks passed!
```

`uv run python -m src.governance --catalog`, `uv run python -m src.governance` and
`git diff --exit-code docs/08-governance/catalog.md` run when this record is committed: the catalog
is regenerated in the same commit and the pre-commit hook runs governance.

The full suite in the worktree, after the rebase onto `dev` at `440190c`, gave
`1296 passed, 1 warning`. `uv run mypy src/` gave `Success: no issues found in 47 source files`.

## Acceptance

- `uv run pytest test/test_agent_tools.py` passes on the agent file, and the same assertion fails on
  a fixture copy that adds Bash: **Met**. 5 passed: the real file, fixture copies adding `Bash`,
  `Edit` and `Write`, and a copy with no `tools` field.
- The agent's description says it runs in shadow and does not decide a merge: **Met**. The
  description reads "Runs in shadow until the owner promotes it in GOV-003; its verdict is recorded
  and does not decide a merge."
- `grep -n "session record"` on the agent file returns only the never-do line: **Met**. One match,
  line 71, the first never-do.

## Backlog

`status: active`, `agent: agent-builder-a`. `next_action`: Both deliverables written and verified
(SESS-2026-10-02-01, branch agent/phase-asr-01); independent review run (demo-adversary, one minor
finding fixed); READY to the Session Manager next. The owner ruled on 2026-10-01 that there is no
.codex mirror for now. New agent types appear in running sessions after a delay; check review-judge is listed before its first
dispatch.

## Unresolved

None.

## Review

`demo-adversary`, a fresh non-fork sub-agent, dispatched with the phase's `scope`, `acceptance` and
`verification`, the range `440190c..HEAD`, REQ-030, PLAN-047 and OPS-029. It received no session
record, by the owner's choice for this review (the 2026-09-23 ruling "session-close reviewer gets no
session record", ahead of `phase-asr-04` writing it into `/session-close` step 3). Its findings,
condition by condition:

1. `uv run pytest test/test_agent_tools.py` passes, and the assertion fails on a Bash fixture —
   **MET**. "5 passed, 1 warning … The Bash-fixture test genuinely exercises the failure path
   (`pytest.raises(AssertionError, match="Bash")`), not a vacuous assertion — it builds the fixture
   by string-replacing the real `tools:` line and asserts the real `_assert_read_only` raises on it."
2. The description says it runs in shadow and does not decide a merge — **MET**. "Both clauses
   REQ-030 R06 asks for are present verbatim in the front-matter `description:` field itself, not
   just the body."
3. `grep -n "session record"` returns only the never-do line — **MET**. "single hit, line 69."

Verification it ran: the new test (5 passed), the grep (one line), ruff ("All checks passed!"),
`--catalog` then `git diff --exit-code` on the catalog (exit 0), governance ("Governance OK: 43
systems, 419 documents, 34 memories, 347 backlog phases"), and `uv run mypy src/` ("Success: no
issues found in 47 source files"). It did not run the full suite. It confirmed the diff touches only
the two deliverables, two session records, the catalog rows and this phase's `next_action` and the
backlog date, and that no `.codex` mirror was added.

Findings:

- **Minor.** "`review-judge.md`'s 'Your inputs' section … tells the judge it receives 'the path to
  the runner's manifest.json' and to 'Read each evidence file the manifest names,' but never states
  what the evidence-file paths are relative to … Minimal fix: add one sentence to 'Your inputs,' e.g.
  'Each entry's `file` is relative to the directory holding `manifest.json`; join them to get the
  file to read.'"

"No other findings survive attack."

**Disposition.** Fixed, but not with the suggested wording, which is wrong:
`tools/run_review_checks.py` line 241 writes `entry.file = path.relative_to(repo).as_posix()`, so
the path is relative to the root of the checkout that ran the runner, not to the manifest's
directory. The added sentence says that, and that every evidence file sits beside `manifest.json`.
The fix moved the never-do line from 69 to 71; the verification above is from after the fix.

## Decisions

- The agent file follows `partition-analyst.md`'s front matter (`model: sonnet`, `effort: high`,
  `maxTurns: 60`), as the scope says to write it from that file.
- The charter says the coordinator's brief carries the diff as well as the manifest path. A judge
  with no shell cannot produce a diff, and the runner does not write one, so the brief has to.
  `REQ-030` R03 names "the commit range"; whether the brief carries the diff itself is for
  `phase-asr-04`, which writes the brief rule into `GOV-017`.
- The test's fixtures cover `Edit` and `Write` as well as the `Bash` the scope names, because R01
  bars all three, and a copy with no `tools` field, because an agent without the field gets every
  tool.
- The checkpoint contract requires a new record on a new day, so this record continues
  `SESS-2026-10-01-06` rather than editing it.
- No `.codex` mirror, per the owner's ruling of 2026-10-01.

## Corrections

None.

## Left undone

The merge onto `dev`, which needs the owner's approval, and the completion edit that follows it.
`phase-asr-04` wires the judge into dispatch and records its first shadow verdict.
