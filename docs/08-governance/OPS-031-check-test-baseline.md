---
schema_version: 1
id: doc-ops-check-test-baseline
code: OPS-031
title: Compare a branch's test run with its base before READY
kind: operation
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-governance]
depends_on: [doc-deterministic-guards-requirements, doc-deterministic-guards, doc-multi-session-coordination-protocol]
---

# Compare a branch's test run with its base before READY

## Trigger

A builder runs it after the post-rebase gate checks and before sending `READY`
([GOV-017](GOV-017-multi-session-coordination-protocol.md)'s merge gate, `PROMPT-037` item 4).
It exists because a branch can pass `pytest` by deleting or skipping a test: the suite's pass count
does not show which tests stopped running (idea `000409`, `REQ-028` R07, `PLAN-045` D7).

## Command

Both reports are produced by the builder (owner rulings, 2026-10-04, recorded in `GOV-003`). The
base is `dev`'s tip, run in a temporary `git clone --shared` that is deleted afterwards; the branch
is the rebased branch, run in its own worktree. Write both reports under the branch worktree's
`_working/`, which is gitignored:

```bash
# From the branch worktree, after `git rebase dev`:
mkdir -p _working/junit
base=$(mktemp -d)
git clone -q --shared --branch dev "$(git rev-parse --path-format=absolute --git-common-dir)" "$base/repo"
(cd "$base/repo" && uv sync --extra dev && uv run python tools/rebuild_db.py \
  && uv run pytest -q -p no:cacheprovider --junitxml="$OLDPWD/_working/junit/base.xml")
rm -rf "$base"
uv run pytest -q --junitxml=_working/junit/branch.xml
uv run python tools/check_test_baseline.py _working/junit/base.xml _working/junit/branch.xml
```

The base copy is a clone, not a worktree, so removing it needs no approval under `GOV-003`'s
worktree-removal rule; nothing in it is kept. It has to carry git data: 78 tests read the
repository's own history, branches or ignore rules (the engine pages, the overview stamp, the demo
reset tool, the containment report among them), and in a `git archive` snapshot they fail, so the
baseline would never cover them (measured 2026-10-04: 36 failed, 42 errors). The clone gets its own
`.venv`. The branch run can be the same run whose tail `READY` already carries, with `--junitxml`
added. One pytest run at a time per worktree still applies.

## Expected result

| Exit | Meaning | What happens |
|---|---|---|
| 0 | Every test that passed on `dev` is present in the branch and not skipped there | `READY` carries the OK line |
| 1 | One or more tests passed on `dev` and are missing or skipped in the branch; each is listed as `missing` or `skipped` | `READY` carries the list; the merge proceeds only with the owner's recorded sign-off naming the tests it accepts (`REQ-028` R10, `PLAN-045` D9) |
| 2 | A report could not be read or parsed, or holds no testcase | No result: fix the run and repeat it |

A test is `classname::name` from the JUnit report, so each parametrized case counts on its own.
Added tests, and tests that were already skipped or failing on `dev`, never fail the check. A test
that passes on `dev` and fails on the branch is not reported here, because the branch's own `pytest`
run already fails.

## Failure and recovery

- **A test renamed or moved.** It appears as `missing` under its old id. The owner's sign-off names
  the old id and where it went; the check does not try to match renames.
- **A deliberate deletion or skip.** Same route: the sign-off names the tests and the reason.
- **Exit 2 on `base.xml`.** Usually the base run failed before writing a report — read its output
  before deleting the temporary clone.

<!-- generated:tool-reference:start -->

### Reference: `tools/check_test_baseline.py`

Refuse a branch whose test run drops a test that passed on its base (REQ-028 R07).

A builder runs the suite twice before `READY` and compares the two JUnit XML reports
(GOV-017's merge gate, PROMPT-037 item 4):

    uv run pytest -q --junitxml=<base.xml>     # in a temporary clone of dev's tip
    uv run pytest -q --junitxml=<branch.xml>   # in the rebased branch worktree
    uv run python tools/check_test_baseline.py <base.xml> <branch.xml>

A test is identified by its JUnit `classname` and `name`, written `classname::name`, so a
parametrized case is its own test. Its outcome is `skipped` when the testcase carries a
`<skipped>` element, `failed` when it carries `<failure>` or `<error>`, and `passed` otherwise.

- exit 0: every test that passed in the base is present in the branch and not skipped there.
  Added tests, and tests already skipped or failing in the base, never fail the check.
- exit 1: one or more tests passed in the base and are missing from the branch or skipped there;
  each is printed with which of the two it is.
- exit 2: a report could not be read or parsed, or holds no testcase at all.

A test that passed in the base and fails in the branch is not this check's business: the
branch's own pytest run already fails on it. A nonzero result blocks the merge unless the owner
signs off naming the tests it accepts (REQ-028 R10, PLAN-045 D9).

See PLAN-045 D7 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-03.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `base` | JUnit XML report of the base run (dev's tip) |  |  |  |
| `branch` | JUnit XML report of the rebased branch run |  |  |  |

Exit codes found in source: 0, 1, 2.

<!-- generated:tool-reference:end -->
