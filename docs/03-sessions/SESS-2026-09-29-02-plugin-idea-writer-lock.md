---
schema_version: 1
id: doc-session-plugin-idea-writer-lock
code: SESS-2026-09-29-02
title: Plugin idea writer serialized on a filelock lock, with the integration-branch warning
kind: session
status: active
owner: repository-owner
created: '2026-09-29'
updated: '2026-09-29'
systems: [sys-plugin-ideas]
depends_on: [doc-plugin-audit-remediation, doc-adr-plugin-idea-log-lock]
---

# Plugin idea writer serialized on a filelock lock, with the integration-branch warning

## Phase

`phase-plfx-01` — Serialize every idea-writer mutation in the plugin on a filelock lock, and warn
off the integration branch. Delivers `REQ-035` R01 to R03 under `PLAN-052`, with the lock as
`ADR-025` decides it. Session 1 - Builder A (`agent-builder-a`), overnight multi-session run,
in `../d-system-worktrees/phase-plfx-01` on `agent/phase-plfx-01`.

## Verification

Run in the worktree after rebasing onto dev at `5db0c00`.

```text
$ cd plugins/idea-realization && uv run pytest
509 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
check_no_private_content: OK (1088 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 399 documents, 34 memories, 341 backlog phases

$ uv run pytest
1157 passed, 1 warning

$ uv run ruff check src/ test/
All checks passed!

$ uv run mypy src/
Success: no issues found in 46 source files
```

The worktree has no `_private/portfolio/`, so the private-content run above checked 0 identifiers.
A separate run loaded the 31 identifiers from the primary checkout and checked every file this
branch changes against them, printing counts only: `31 identifiers, 16 changed files, 0 violations`.

Baseline runs at `d8a635b` (PLAN-052 D10). `git diff --stat d8a635b HEAD --
plugins/idea-realization/scripts` printed nothing before the build started. The two changed test
files were copied into a detached worktree at `d8a635b` and the new tests run there; the worktree was
then removed.

```text
FAILED test/test_ideas.py::test_two_adds_held_at_a_barrier_take_distinct_ids
E   ideas.IdeaError: 000001 was already created — a second created event follows it
FAILED test/test_ideas.py::test_two_concurrent_status_moves_admit_exactly_one
E   assert [0, 0] == [0, 1]
FAILED test/test_ideas.py::test_twenty_concurrent_add_processes_leave_twenty_ids
E   AssertionError: error: 000005 was already created — a second created event follows it
FAILED test/test_ideas.py::test_a_linked_worktree_warns_and_still_writes
E   AssertionError: assert ('ideas are recorded only on the integration branch in the primary checkout' in '')
FAILED test/test_ideas.py::test_the_primary_checkout_on_another_branch_warns
E   AssertionError: assert ('ideas are recorded only on the integration branch in the primary checkout' in '')
FAILED test/test_ideas.py::test_every_worktree_resolves_one_lock_under_the_git_common_directory
FAILED test/test_ideas.py::test_outside_a_git_repository_the_lock_sits_beside_the_log
FAILED test/test_ideas.py::test_a_held_lock_times_out_and_appends_nothing
FAILED test/test_ideas.py::test_a_writer_killed_while_holding_the_lock_does_not_block_the_next
9 failed, 3 passed, 120 deselected
```

The first five fail on the behaviour: duplicate ids, both status moves accepted, no warning. The
last four check a lock that does not exist at the baseline (`module 'idea' has no attribute
'lock_path'`, or `No module named 'filelock'`), so, as the phase scope says, they have no baseline
run. The three that pass are the no-warning control and the two pin tests, which pass with no
pinned package present.

## Acceptance

- R01 barrier test fails at `d8a635b` and passes on the branch, both runs quoted — **Met** (baseline
  block above; 509 passed on the branch).
- Twenty concurrent `idea.py add` subprocesses leave a log `list` reads with exit 0 and 20 distinct
  ids — **Met** (`test_twenty_concurrent_add_processes_leave_twenty_ids`).
- Two concurrent `status <id> reviewing` — exactly one succeeds, the other refused as an illegal
  transition, log folds; fails at `d8a635b` — **Met** (`[0, 0]` at the baseline; passes on the branch).
- The lock path from the primary checkout and from a linked worktree is one file under
  `git rev-parse --git-common-dir` — **Met**
  (`test_every_worktree_resolves_one_lock_under_the_git_common_directory`).
- With the lock held, `idea.py add` exits non-zero naming the lock file, log byte-identical — **Met**
  (`test_a_held_lock_times_out_and_appends_nothing`).
- A linked worktree prints the D3 warning; the primary checkout on the integration branch prints
  none — **Met** (the two warning tests and the control).
- Plugin suite count is 497 plus this phase's new tests, none removed — **Met** (509 = 497 + 10 in
  `test_ideas.py` + 2 in `test_scripts_portable.py`).

## Backlog

`status: active`, agent `agent-builder-a`, on dev since `95ce893`; deliverables widened by the
plugin README at `5db0c00`. Under the Session Manager's contract the phase stays active until the
owner approves the merge; the completion edit is made on dev after the fast-forward. Next action:
merge to dev (the owner approved it in this session), then the completion edit on dev.

## Unresolved

None. The owner ruled option A on the morning of 2026-09-29, in the Session Manager session (see
Decisions), and approved the merge in this session.

## Review

Independent adversarial review by a fresh `demo-adversary` subagent, given the phase's scope,
acceptance and verification lists and the range `dev...HEAD` (`f59b7f9`, `444aaff`, `74d23a4`,
`ad9bbdd`). Its findings, condition by condition:

1. R01 barrier test — **Met.** It reproduced the baseline itself in a detached worktree at
   `d8a635b`: the same 9 test names failed (`9 failed, 10 passed`); `509 passed` on the branch.
2. Twenty concurrent `add` subprocesses — **Met.** "genuinely spawns 20 real subprocesses against a
   shared lock file, not an in-process fake."
3. Two concurrent status moves — **Met.** Confirmed by the baseline run and by tracing the barrier:
   "flock is per-open-file-description, so it genuinely blocks a second thread of the same process
   … Not a vacuous test."
4. One lock path under `--git-common-dir` — **Met.**
5. Held lock times out, log byte-identical — **Met.** "the exception path (`Timeout` → `IdeaError`
   before `operation()` runs) makes 'appended nothing' true."
6. Warning in a linked worktree, none on the integration branch — **Met**, plus manual probes: a
   detached HEAD warns and does not crash; the primary checkout through a symlinked path, and
   `--root` at a subdirectory, give no spurious warning.
7. Count 497 + new, none removed — **Met.** 497 + 10 + 2 = 509.

Verification rerun by the reviewer: all seven commands green, with the same outputs as above
(`1157 passed, 1 warning` repo-wide). Lock coverage: all nine mutating subcommands run through
`_operation()` inside `with writer_lock(config)`; `list` and `show` return before it. Deviations
judged: the fallback outside git "sound given the stated open ruling"; `fallback_to_soft=False` and
`preserve_lock_file=True` verified against the installed 4.0.6 signature; the 4.0.6 pin consistent
across `pyproject.toml`, `uv.lock` and the header; the README within the declared deliverables.

Findings, both minor:

- **No test ties the `dev` extra's pin in `pyproject.toml` to the script header's pin.**
  Disposition: accepted, not fixed. The plugin's tests must run from a copy outside this repository
  (`test_scripts_portable.py`, `test_no_source_references.py`), so a plugin test cannot read this
  repository's `pyproject.toml`; the acceptance asks only that two headers be compared.
- **The warning said "writing anyway" before the lock was taken,** so a run that then timed out
  printed a claim of a write that never happened. Disposition: fixed. The warning now ends "this run
  is on <branch> in <checkout>"; the plugin suite still passes (509).

"No further discrepancies found": no unlocked mutating subcommand, no test that passes without a
real lock, no flakiness from the 2-second barrier against the 30-second lock timeout, no
unsupported claim in the docs, skill, README or record, and no file outside the declared
deliverables apart from the catalog regeneration a new session document forces.

The reviewer was told to make no git state changes, but it added and then force-removed a detached
worktree from the primary checkout to reproduce the baseline. The primary checkout was checked
afterwards: `git status` clean, and no stray worktree in `git worktree list`.

## Decisions

**Claim approval.** The owner pre-approved this claim for the overnight run
(`overnight-2026-09-29`), relayed by the Session Manager and confirmed by the owner in the Session
Manager session, not in this one. Later that night the owner approved commits as needed for the
overnight run, in this session. The claim commit and the deliverables widening were each made on
dev inside a turn the Session Manager granted, and neither was pushed (owner ruling: no pushes
tonight).

**Deliverables widened by `plugins/idea-realization/README.md`.** The README said every script's
inline dependencies are "`jsonschema` and `pyyaml` only", which the pin makes false. The session
asked the Session Manager for the widening, and the Session Manager approved it. It was committed on
dev at `5db0c00`.

**The lock outside a git repository (open, for the owner).** `ADR-025` puts the lock under the git
common directory. The plugin also supports a root that is not a git repository
(`paths.primary_checkout` returns the root itself there), and about 20 existing `idea.py` CLI tests
run in a plain `tmp_path`. Neither `ADR-025` nor `REQ-035` covers the case. Three options went to
the owner through the Session Manager's morning report. A (built, recommended): outside git, the lock
is the log's path plus `.lock`; "never write without the lock" holds and no existing test changes.
B: refuse outside git, as `reservations.py` does, at the cost of a `git init` in about 20 fixtures.
C: no lock outside git, which breaks "never writes without the lock". The Session Manager directed
A, noted in `docs/protocol.md` only, with `ADR-025` untouched until the owner rules. The owner ruled
option A as built on the morning of 2026-09-29, in the Session Manager session: the lock is
`<ideas_path>.lock` beside the log outside git, noted in `docs/protocol.md` only, and `ADR-025` is
unchanged.

**Assumptions the session stated rather than asked.**

- No D3 warning outside a git repository, where there is no branch to be on. Inside a repository, a
  detached HEAD warns.
- Operating-system locks only. `filelock` 4.x falls back to a marker-file lock where `flock` is
  unsupported. That lock would survive a crashed writer, the property `ADR-025` rejected the
  `O_CREAT|O_EXCL` alternative for. So the writer passes `fallback_to_soft=False`, and
  `preserve_lock_file=True` so the file stays after release, as `ADR-025` records.
- `filelock==4.0.6`. `ADR-025` recorded 4.0.4 as current on 2026-09-27, and PyPI listed 4.0.6 on
  2026-09-29. The ADR requires one exact version without naming one.
- Every input (`--file`, stdin) is read before the lock is taken, so a slow input never holds other
  writers. The timeout is `LOCK_TIMEOUT_SECONDS`, 30 seconds.

**What was built.** `scripts/idea.py` gains `lock_path`, `writer_lock` and `off_integration_warning`.
`main` reads every input, prints the warning when it applies, and runs the operation inside the lock.
`list` and `show` take no lock, and `idea.py` now accepts `--integration-branch`. The pin is in
`idea.py`'s PEP 723 header and in the repository's `dev` extra (`pyproject.toml`, `uv.lock`).
`test/test_scripts_portable.py` allows `filelock` and reports a package pinned to different
versions, or pinned without `==`. The rule is stated in `docs/protocol.md` §7 (two rows) and §11 (recording ideas
joins the primary-checkout work; the lock and the warning), in `docs/multi-session.md` (the "supplies
no lock" sentence corrected; the rule under §7 Ideas), in `skills/idea/SKILL.md` (which now passes
`integration_branch`) and in the README. `docs/tools.md` is regenerated.

## Corrections

- The first draft of the idea skill's new section told the agent to "stop and tell the person" on
  the warning. That is a rule D3 does not contain (D3: warn, then write). It was narrowed, before
  commit, to passing the warning on.
- The TURN DONE for the widening named a commit hash (`2b3d3a8`) before the commit had printed its
  own. The real hash is `5db0c00`, and a correction went to the Session Manager.
- The first commit of the README fix was refused by the pre-commit governance check. The uncommitted
  draft of this record made the catalog stale. It was reported BLOCKED, and on the Session Manager's
  OK, the README fix and this record were committed together with the catalog regenerated.

- The review's warning-wording finding was fixed after the review, in the commit that adds this
  section.

## Left undone

- The Windows lock path has no test run. It is out of scope under `PLAN-052`, idea `000484`.
- `ADR-025` does not mention the fallback location outside git, by the owner's ruling.
