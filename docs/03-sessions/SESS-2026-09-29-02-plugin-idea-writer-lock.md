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

`phase-plfx-01` — serialize every idea-writer mutation in the plugin on a pinned `filelock` lock,
test-first, and warn when writing off the integration branch. Delivers `REQ-035` R01 to R03 under
`PLAN-052`, with the lock as `ADR-025` decides it.

Session 1 - Builder A, agent `agent-builder-a`, in the overnight multi-session run of 2026-09-29,
working in `../d-system-worktrees/phase-plfx-01` on `agent/phase-plfx-01`.

## Approvals

- **Claim.** The owner pre-approved this claim for the overnight run (`overnight-2026-09-29`); the
  Session Manager relayed that approval, and the owner confirmed it in the Session Manager session.
  It was not given in this session. Later in the night the owner approved commits as needed for the
  overnight run in this session. Claim commit `95ce893` on dev, in a turn the Session Manager
  granted; not pushed (the owner ruled no pushes tonight).
- **Deliverables widened by one file.** `plugins/idea-realization/README.md` said every script's
  inline dependencies are "`jsonschema` and `pyyaml` only", which the pin makes false. The Session
  Manager approved adding it to the phase's deliverables on dev (option 1 of the question this
  session raised).

## Open owner ruling: the lock outside a git repository

`ADR-025` puts the lock under the git common directory. The plugin also supports a root that is
not a git repository (`paths.primary_checkout` returns the root itself there), and about 20
existing `idea.py` CLI tests run in a plain `tmp_path`. Neither `ADR-025` nor `REQ-035` covers that
case. Three options went to the owner through the Session Manager's morning report:

- **A (built, recommended).** Outside git the lock is the log's path plus `.lock`. "Never write
  without the lock" still holds and no existing test changes.
- **B.** Refuse outside git, as `reservations.py` does. About 20 fixtures would need a `git init`.
- **C.** No lock outside git, which breaks "never writes without the lock".

The Session Manager ruled to build A and note it in `docs/protocol.md` only; `ADR-025` is not
touched without the owner's OK. The Session Manager parks the merge until the owner rules.

## Assumptions stated, not asked

- **No warning outside a git repository.** There is no branch to be on there, so the D3 warning
  does not print. Inside a repository a detached HEAD warns.
- **Operating-system lock only.** `filelock` 4.x falls back to a marker-file lock where `flock` is
  not supported. That lock would survive a crashed writer, which is the property `ADR-025` rejected
  the `O_CREAT|O_EXCL` alternative for, so the writer passes `fallback_to_soft=False` and
  `preserve_lock_file=True` (the lock file stays on disk after release, as `ADR-025` records).
- **Pinned version 4.0.6.** `ADR-025` records 4.0.4 as current on 2026-09-27; PyPI listed 4.0.6 on
  2026-09-29, and the ADR pins "one exact version" without naming it.
- **Inputs are read before the lock.** `--file` and stdin are read before the lock is taken, so a
  slow input never holds other writers.

## What was built

- `scripts/idea.py`: `lock_path`, `writer_lock` and `off_integration_warning`. `main` reads every
  input, prints the D3 warning when it applies, then runs the operation inside the lock. `list`
  and `show` take no lock. On timeout (`LOCK_TIMEOUT_SECONDS`, 30) the writer exits 1 with
  "another writer holds the idea-log lock <path>; gave up after 30 seconds and appended nothing".
  `idea.py` now takes `--integration-branch`. The PEP 723 header pins `filelock==4.0.6`.
- `pyproject.toml` and `uv.lock`: `filelock==4.0.6` in the `dev` extra.
- `test/test_scripts_portable.py`: `filelock` allowed; a pinned package must carry one `==`
  version across every header, with a test that two differing pins are reported.
- `docs/protocol.md` §7 (two rows) and §11 (recording ideas added to the primary-checkout work,
  and the lock and D3 rule), `docs/multi-session.md` (the "supplies no lock" sentence corrected,
  and the D3 rule under §7 Ideas), `skills/idea/SKILL.md` (passes `integration_branch`; states
  where ideas are recorded), `README.md` (the dependency sentence), and `docs/tools.md`
  regenerated.

## Baseline runs at d8a635b (PLAN-052 D10)

`git diff --stat d8a635b HEAD -- plugins/idea-realization/scripts` printed nothing. The two changed
test files were copied into a detached worktree at `d8a635b` and run there with the new tests
selected; the worktree was then removed.

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
last four check a lock that does not exist at the baseline (`AttributeError: module 'idea' has no
attribute 'lock_path'`, or `No module named 'filelock'`), so, as the phase scope says, they have no
baseline run. The three that pass are the no-warning control and the two pin tests, which pass
vacuously with no pinned package.

## Verification

POST_REBASE_VERIFICATION

## Test count

497 at the baseline, plus 12 new: 10 in `test_ideas.py` and 2 in `test_scripts_portable.py`. None
removed. `test_inline_metadata_names_only_allowed_packages` is kept and now parses version
specifiers.

## Ideas

None raised this session.
