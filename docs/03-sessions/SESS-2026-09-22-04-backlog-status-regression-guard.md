---
schema_version: 1
id: doc-session-backlog-status-regression-guard
code: SESS-2026-09-22-04
title: Fail the governance check when a phase silently leaves complete
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems:
- sys-backlog
- sys-governance
depends_on:
- doc-backlog-status-regression-guard-plan
- doc-backlog-status-regression-guard
- doc-backlog-decisions
---

# Fail the governance check when a phase silently leaves complete

## Phase

`phase-gov-05` — Fail the governance check when a phase silently leaves `status: complete`.
Claimed as `agent-coord`, worked on `agent/phase-gov-05` in
`/code/d-system-worktrees/phase-gov-05`, per `PLAN-038` and `REQ-010`.

## What was built

`src/governance/regression.py` (new): the status-regression guard `REQ-010` specifies. Given the
current backlog catalog and a git ref, it compares every phase present in both states and flags
two things — a phase that leaves `status: complete` (R1), and a phase that stays `complete` while
losing `session`, `completion_evidence` or `result` (R2). A finding is excused (R3) when the
working copy of `GOV-003-backlog-decisions.md` names the phase and the version committed at that
ref does not — the escape hatch is a search for the phase id, not a parse of the entry's shape, so
an ordinary sentence recording the reopen is enough. An unreadable prior state (mid-rebase, shallow
clone, initial commit, or the ref not existing at all) is treated as "no comparison possible": skip
it, print one line, do not fail.

**R6's dual-base behaviour.** The check runs twice, against `HEAD` and against `dev`, with
different severities:

- **`HEAD` is a hard failure.** It catches a bad edit before it is committed, in the tree that
  makes it — the way the `5ecb203` incident `REQ-010` documents actually happened.
- **`dev` is a warning that never changes the exit code.** It catches the same regression arriving
  by rebase or merge, which `HEAD` structurally cannot see by the time it lands. It cannot be a
  hard failure: every agent branch that legitimately completes a phase differs from `dev` by
  exactly the transition this guard looks for, so failing on it would fire on the normal case.

`src/governance/__main__.py` wiring: `main()` now calls `audit_status_regression(ROOT, catalog)`
once the backlog schema validates, and folds its errors and warnings into the existing lists before
they print — the same command (`uv run python -m src.governance`) agents already run before
finishing, per R5.

## Adversarial review

An independent adversarial review of the diff (`a03704c..1fb884a`) returned two confirmed
findings. Both are recorded here as findings that were caught and fixed, not smoothed over.

**Finding 1 — HIGH, confirmed and reproduced.** `is_recorded` (R3's escape hatch) was a bare
substring test. A `GOV-003` entry naming a *different* phase id that merely contained the target
as a prefix (`phase-lit-070` silenced `phase-lit-07`), or a mention hidden inside a commented-out
line, fully silenced the hard failure for a real regression — directly against R3's intent.

*Fix:* `is_recorded` now requires the phase id to appear as a whole identifier, not a substring —
a differently-named phase that happens to contain the target as a prefix or suffix no longer
matches — and strips HTML/markdown comments before searching, so a mention nobody would see
rendered no longer counts as a recorded decision. A bare, ordinary prose mention still counts,
by design (`PLAN-038`'s "a grep, not a parse"): the goal is to force the reason to be written
down, not to validate its shape. Six new tests cover the prefix collision, the suffix collision,
the commented-out mention (alone and surrounded by visible text), and the still-permitted bare
prose mention.

**Finding 2 — MEDIUM, confirmed by mutation test.** The guard's wiring into
`python -m src.governance` was invisible to the test suite: every existing test exercised
`src.governance.regression` directly, so neutering the wiring call in `__main__.py` left all 17
tests green while the real command silently stopped reporting a seeded regression.

*Fix:* added `test_main_reports_a_status_regression_through_the_real_entry_point`, which calls the
real `main()` against this repository's own, already-valid `ROOT`, with only the `HEAD` copy of
`backlog.yaml` faked (via a monkeypatched `read_text_at`) to claim a real, currently-non-complete
phase was `complete`. Verified by mutation: the wiring block was manually deleted from
`__main__.py`, the test was re-run and failed (`assert exit_code != 0` → `0 != 0`), and the file
was restored and the test confirmed green again.

**Both findings were independently re-attacked after the fix** — the adversary re-ran the
substring bypasses and the mutation test itself — and confirmed fixed.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 312 documents, 29 memories, 293 backlog phases
```

```
$ uv run pytest
763 passed, 2 warnings in 67.04s
```

```
$ uv run ruff check src/ test/
Found 10 errors.
```

All 10 are pre-existing and none are in this phase's files (`src/governance/regression.py`,
`src/governance/__main__.py`'s wiring diff, `test/test_backlog_status_regression.py`). The one
hit inside `src/` is `E501` at `src/governance/__main__.py:435`, byte-identical on `dev` — a
pre-existing long line the phase's diff shifted by two lines without touching. The rest are
pre-existing `E501`/`F841` hits in `test/test_governance.py` and `test/test_idea_dispatch.py`,
neither of which this phase touched.

```
$ uv run mypy src/
Success: no issues found in 26 source files
```

## Acceptance

- **A seeded `complete` → `queued` transition makes the check exit non-zero and name the phase —
  Met.** Exercised both directly against `regression.audit` and end-to-end through `main()`.
- **A phase left at `complete` with `completion_evidence` removed exits non-zero — Met.**
- **The same transition with a `GOV-003` entry naming the phase exits 0; an entry naming a
  different phase does not — Met**, and now correctly resistant to a prefix/suffix collision or a
  commented-out mention after the adversarial fix.
- **An unreadable prior state exits 0 with a note — Met.** Covered for a repository with no
  commits yet (no `HEAD` to read).
- **A `dev`-relative-only finding warns and exits 0; a `HEAD`-relative finding still exits
  non-zero with the warning present; an unreachable `dev` notes and does not suppress `HEAD` —
  Met**, each covered by its own test against a real two-branch git repository.

## Unresolved

Two of the adversary's hypotheses were not independently reproduced and are recorded here as
**inferred, not verified**:

- **A conflicted mid-rebase state.** The guard treats a failed `git show <ref>:path` as "no
  comparison possible" regardless of *why* it failed, so a rebase conflict should degrade the same
  way a shallow clone does — but no test constructs an actual conflicted rebase to confirm it.
- **A shallow clone or detached `HEAD` in production conditions.** The unit tests simulate
  unreadability by pointing at a ref or path that does not exist, which exercises the same
  `subprocess.CalledProcessError` path a shallow clone would hit, but a real shallow clone was not
  built and run against.

Both are structurally covered by the same `except (OSError, subprocess.CalledProcessError)` branch
already tested against other causes of unreadability, but that is an inference from the code path,
not a direct observation.

## Backlog

`phase-gov-05` stays as the coordinator finds it; this session does not edit
`docs/09-backlog/backlog.yaml`. The completion edit, and the integration decision, are the
coordinator's to make on `dev`.
