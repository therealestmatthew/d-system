---
schema_version: 1
id: doc-session-plugin-config-validation
code: SESS-2026-10-04-14
title: Validate every configured plugin value centrally
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-plugin-core, sys-plugin-ideas, sys-plugin-partition, sys-plugin-backlog, sys-plugin-documents]
depends_on: [doc-plugin-audit-remediation]
---

# Validate every configured plugin value centrally

## Phase

`phase-plfx-02` — Validate every configured plugin value centrally: contained paths,
`worktree_dir` outside, a well-formed integration branch.

## Verification

Run in `/code/d-system-worktrees/phase-plfx-02` on `agent/phase-plfx-02`, rebased on dev `1d2e6ab`.

`cd plugins/idea-realization && uv run pytest`

```
530 passed
```

The previous phase left 509; this phase adds 21 tests and removes none. One existing test,
`test_partition.py::test_a_staging_directory_outside_any_checkout_stops_the_sweep`, changed its
expected exit code from 1 to 2 and its expected message from "not gitignored" to the option name
`staging_dir`: the outside staging directory is now refused when the configuration is read, before
the sweep's own gitignore check. Nothing is written either way. `test_partition.py` was added to
the phase's deliverables on dev (`1d2e6ab`) for this.

`claude plugin validate plugins/idea-realization --strict`

```
✔ Validation passed
```

`uv run python tools/check_no_private_content.py` (changes staged)

```
check_no_private_content: OK (1307 tracked files, 0 identifiers checked)
```

`uv run python -m src.governance`

```
Governance OK: 44 systems, 436 documents, 36 memories, 347 backlog phases
```

`uv run pytest`

```
1457 passed, 1 skipped, 1 warning
```

`uv run ruff check src/ test/`: `All checks passed!`. `uv run mypy src/`: `Success: no issues found
in 47 source files`.

### The new tests at the baseline (`PLAN-052` D10)

A detached worktree at `d8a635b` (`../d-system-worktrees/phase-plfx-02-baseline`) with the six
changed test files copied in, run with this branch's environment. Below is pytest's short summary
as captured; it truncates some reasons. Every new test fails on behavior, none on an import error:
the refusals are asserted as `ValueError`, which `PathError` subclasses, or as exit codes and
files.

```
test_paths.py::test_absolute_path_outside_the_root_is_refused - F...
test_paths.py::test_traversal_out_of_the_root_is_refused - Failed...
test_paths.py::test_symlink_escape_is_refused - Failed: DID NOT R...
test_paths.py::test_a_git_component_is_refused - Failed: DID NOT ...
test_paths.py::test_an_escaping_list_entry_is_refused - Failed: D...
test_paths.py::test_worktree_dir_inside_the_primary_checkout_is_refused
test_paths.py::test_a_malformed_integration_branch_is_refused[--output=x]
test_paths.py::test_a_malformed_integration_branch_is_refused[-x]
test_paths.py::test_a_malformed_integration_branch_is_refused[a..b]
test_paths.py::test_a_malformed_integration_branch_is_refused[with space]
test_manifest.py::test_worktree_dir_description_says_it_lives_outside_the_repository
test_scaffold.py::test_scaffold_refuses_an_outside_ideas_path_and_writes_nothing
test_scaffold.py::test_scaffold_refuses_an_outside_docs_root_and_writes_nothing
test_doctor.py::test_doctor_names_every_invalid_key_and_exits_one
test_regression.py::test_an_option_shaped_integration_branch_is_refused_and_writes_nothing
test_ideas.py::test_add_refuses_an_ideas_path_outside_the_root - ...
```

At the baseline the option-shaped branch test fails on its exit code: the check exited 0 after
`git show` reported `--output=<tmp>/out/x is unreadable, skipping the --output=<tmp>/out/x-relative
comparison` — git received the value as an option. No file appeared in `<tmp>/out` at the baseline
either, because the path git tried to write (`x:<backlog path>`) needed a directory that did not
exist. The same run also failed nine `test_ideas.py` tests that the previous phase added for its
own fixes; they are not this phase's. The baseline worktree's files were restored with
`git checkout -- .`.

The same tests on the branch before the fix (commit `105e5a3`, tests only): `16 failed`. On the
branch after the fix: all pass.

### The acceptance commands

From an empty repository (`git init` only):

- `idea.py add --title T --body B --ideas-path ../x.jsonl` → `error: ideas_path = '../x.jsonl':
  resolves outside the repository root <repo>`, exit 2, no `x.jsonl` beside the repository.
- `scaffold.py --feature all --consent gitignore --ideas-path <absolute outside path>` → exit 2;
  `scaffold.py ... --docs-root ../outside` → exit 2. The repository still holds only `.git`: no
  file, no install-state record, no `.gitignore` line.
- `doctor.py` with `IDEA_REALIZATION_IDEAS_PATH=../e.jsonl` and `IDEA_REALIZATION_DOCS_ROOT=<an
  outside directory>` → `invalid   ideas_path = ...`, `invalid   docs_root = ...`,
  `2 configured value(s) invalid`, exit 1, no traceback.
- `check.py --feature backlog --integration-branch=--output=<tmp>/x` in a repository with a
  backlog and a complete phase → exit 2 naming `integration_branch`, nothing in `<tmp>`
  (`test_an_option_shaped_integration_branch_is_refused_and_writes_nothing`). In a repository with
  no backlog, the backlog check never reads `integration_branch` and exits 0: values are validated
  when a script reads them, and `doctor` validates them all.

## Acceptance

- Each R04, R05 and R06 refusal test fails at `d8a635b` and passes on the branch, with both runs
  quoted: Met (the baseline list above; the plugin suite passes on the branch).
- `idea.py add --ideas-path ../x.jsonl` exits 2 and creates no file; the scaffold with an absolute
  outside `ideas_path`, and separately with `docs_root` `../outside`, exits 2 and leaves an empty
  repository empty: Met (commands above and the three tests).
- An absolute path inside the root still resolves, and the partition sweep's check command still
  runs: Met. `test_absolute_path_is_kept` is unchanged and passes;
  `test_the_sweeps_check_command_runs_with_its_absolute_paths` runs the command the sweep builds,
  which names every path absolutely, and it reports on the ideas feature rather than refusing.
- `integration_branch` set to `--output=<tmp>/x` exits 2 and no file appears in `<tmp>`: Met (the
  test above, in a repository where the value is used).
- The manifest's `worktree_dir` description no longer says relative to the repository root: Met
  (`test_worktree_dir_description_says_it_lives_outside_the_repository`).
- The plugin suite count is the previous phase's count plus this phase's new tests, with none
  removed: Met (509 + 21 = 530).

## Backlog

`status: active`. `next_action`: independent review, then READY and the owner's merge approval.

## Unresolved

- The detached baseline worktree `../d-system-worktrees/phase-plfx-02-baseline` is still present;
  its removal waits for the owner's approval.
