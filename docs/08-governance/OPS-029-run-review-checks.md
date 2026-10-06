---
schema_version: 1
id: doc-ops-run-review-checks
code: OPS-029
title: Run a phase's declared checks at one commit for a build review
kind: operation
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-04'
systems: [sys-gov-docs]
depends_on: [doc-reviewer-contract-requirements, doc-reviewer-contract, doc-multi-session-coordination-protocol]
---

# Run a phase's declared checks at one commit for a build review

## Trigger

A build review needs the result of a phase's checks at a known commit, run by code rather than by
the reviewer or the builder (`REQ-030` R02, `PLAN-047` D1 and D2). Whoever dispatches the review
runs it. Under `PLAN-047` D3 that is the coordinator, today the Session Manager. The manifest it
prints is what the reviewer receives, and what `GOV-017`'s merge-gate step 2 re-run becomes.

## Command

```bash
uv run python tools/run_review_checks.py <phase-id> <commit>
```

Nothing else is accepted: no extra command, flag or path. A phase id and a commit are the whole
input, so the caller cannot add to or change what runs. Run it from any checkout of the repository.
It never runs anything in the checkout it is started from, only in its own temporary worktree.

## What it runs

1. It reads the phase from **`dev`'s** `docs/09-backlog/backlog.yaml` (`git show dev:…`), not from
   the commit under review. A branch that edits its own `verification` list cannot weaken the run.
   The manifest records which `dev` commit the list came from.
2. It creates a detached worktree at the commit, under `../d-system-worktrees/review-<phase-id>-…`.
3. It runs `uv sync --extra dev` and `cd ts && npm ci` there, each listed as a `setup` entry.
4. It runs each `verification` entry that is a command, in backlog order.
5. It runs each of the five `GOV-017` gate checks that the list does not already contain:
   `uv run python -m src.governance`, `uv run pytest`, `uv run ruff check src/ test/ tools/`,
   `uv run mypy src/` and `cd ts && npm test`. A gate check the list also names runs once, with kind `verification+gate`.
6. It removes the worktree, whether the run passed, failed or was interrupted.

**An entry is a command** when its first word, after any `NAME=value` assignments, is `cd` or a
program found on `PATH`. Every other entry is prose, such as "Run membership fixtures …; review the
ADR." Prose is listed in the manifest as `not run: not a command`, with no exit code. The reviewer
judges it by reading; the runner never passes prose to a shell (owner ruling, 2026-10-01).

Each command runs once through `bash -c` in the worktree, with no stdin, under the caller's
environment minus `VIRTUAL_ENV`, so `uv run` uses the worktree's own environment. **A failing
command is recorded with its exit code and never retried.** A command still running after 30
minutes is killed with its process group and recorded as exit 124, `timed out` (owner ruling,
2026-10-01).

## Expected result

The evidence goes to `_working/review-checks/<phase-id>/<commit12>/` in the checkout that ran the
tool. That path is gitignored, so it survives the worktree's removal and a reviewer without a shell
can read it there:

- one file per command that ran, `NN-<kind>.txt`, holding its combined stdout and stderr exactly as
  produced;
- `manifest.json`: the phase, the full commit, the `dev` commit the list came from, `passed` or
  `failed`, and per entry the kind, command, whether it ran, exit code, file path, sha256 of the
  file, and any note.

The same manifest is printed as a table. A second run for the same phase and commit replaces the
directory.

| Exit | Meaning |
|---|---|
| 0 | Every command that ran exited 0. Prose entries were listed, not run |
| 1 | At least one command exited non-zero or timed out; the manifest names it |
| 2 | Refused before anything ran: an unknown phase id, a commit that does not resolve, an extra argument, no readable `dev` backlog, or the worktree could not be created. Also an operating-system error that stopped a run partway; the worktree is still removed and no manifest is written |

Exit 0 is not a review verdict. It says the declared commands passed at that commit. Whether the
acceptance conditions hold, including every prose entry, is the reviewer's judgement.

## Failure and recovery

- **A prose entry that begins with a real program**, such as "grep both documents for …", is run
  and usually fails, typically with exit 2. That follows the rule above; the reviewer reads the
  evidence file and treats the entry as prose. Rewording the backlog entry as a real command fixes
  it at the source.
- **A shell builtin first**, such as `exit 3` or `source …`, is not a program on `PATH`, so the
  entry is listed as not run. Wrap it (`bash -c '…'`, `sh -c '…'`) in the backlog entry if it is
  meant to run.
- **Exit 2, `git worktree add failed`.** Usually a stale worktree registration. Run
  `git worktree prune` and retry. Nothing ran and nothing was left behind; the previous evidence
  for that phase and commit is untouched, because it is replaced only once a run starts.
- **Exit 2, `stopped: …`.** An operating-system error, such as a full disk, interrupted the run
  after it started. The worktree was removed. The evidence directory holds the files written
  before the error and no `manifest.json`, so treat it as incomplete and run again.
- **`uv sync` failed** (setup entry non-zero). The commands after it ran without the environment
  and their failures follow from it. Read `01-setup.txt` first.
- **The run was killed from outside** (the terminal closed, `kill -9`). The `finally` cleanup did
  not run. `git worktree list` shows the `review-<phase-id>-…` entry. Remove it with
  `git worktree remove --force <path>`.

<!-- generated:tool-reference:start -->

### Reference: `tools/run_review_checks.py`

Run a phase's declared checks at one commit in a detached worktree and record the evidence.

The build-review runner (REQ-030 R02, PLAN-047 D2). It takes a phase id and a commit and nothing
else:

    uv run python tools/run_review_checks.py <phase-id> <commit>

It reads the phase's `verification` list from `dev`'s `docs/09-backlog/backlog.yaml` (never from
the commit under review, so a branch cannot weaken its own list), creates a detached temporary
worktree at the commit, installs the environment there with `uv sync --extra dev` and, for the
frontend tests, `npm ci` in `ts/`, and runs:

- each `verification` entry that is a command, in the order the backlog lists it;
- then each of the five GOV-017 gate checks that the list does not already contain.

An entry is a command when its first word, after any `NAME=value` assignments, is `cd` or a
program found on PATH. Any other entry is prose and is listed as not run. Commands run through
`bash -c` in the worktree with no stdin, one at a time, each limited to 30 minutes; a command that
hits the limit is killed and recorded as exit 124. A failing command is recorded with its exit code
and never retried.

Each command's combined stdout and stderr is written to its own evidence file under
`_working/review-checks/<phase-id>/<commit12>/` in the checkout running the tool, replacing the
previous run's files for that phase and commit. The manifest (command, exit code, file path,
sha256) is printed and written there as `manifest.json`. The worktree is removed afterwards,
whether the commands passed, failed or the run was interrupted.

Exit codes: 0 when every command that ran exited 0; 1 when any command failed or timed out; 2 when
the run is refused (unknown phase id, unresolvable commit, an extra argument, no readable `dev`
backlog, or the worktree could not be created) or an operating-system error stopped it partway.
A refused run leaves the previous evidence for that phase and commit untouched.

See REQ-030 R02 and PLAN-047 D2 (docs/01-plans/PLAN-047-reviewer-contract.md), phase-asr-02.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `phase_id` | a phase id in dev's backlog, e.g. phase-asr-02 |  |  |  |
| `commit` | the commit to check out and run the checks at |  |  |  |

Exit codes found in source: 2.

<!-- generated:tool-reference:end -->
