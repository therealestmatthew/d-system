---
schema_version: 1
id: doc-session-branch-diff-guards
code: SESS-2026-10-04-12
title: 'Branch diff guards: test baseline, diff patterns and the plan check'
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-governance, sys-gov-docs]
depends_on: [doc-deterministic-guards]
---

# Branch diff guards: test baseline, diff patterns and the plan check

## Phase

`phase-grd-03` — Branch diff guards: the test-count baseline, the diff-pattern check and the
plan-versus-registered check.

## Verification

`uv run pytest test/test_check_test_baseline.py test/test_check_diff_patterns.py test/test_plan_phases.py`:

```
54 passed, 1 warning
```

`uv run python -m src.governance --catalog`: regenerated; `git diff --exit-code
docs/08-governance/catalog.md` is clean against the committed catalog.

`uv run python -m src.governance`:

```
Governance OK: 44 systems, 437 documents, 36 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0.

`uv run ruff check src/ test/ tools/check_test_baseline.py tools/check_diff_patterns.py`:

```
All checks passed!
```

`uv run mypy src/ tools/check_test_baseline.py tools/check_diff_patterns.py`:

```
Success: no issues found in 50 source files
```

The diff tool on `dev~20..dev`, as the acceptance requires, recorded whatever it reported. Two runs,
because `dev` moved during the session:

```
dev~20..dev at c1e406d..d50bda7:
Diff patterns OK: no added type-ignore, cast(Any, or broad except/pass in dev~20..dev.   (exit 0)

dev~20..dev at 52215f6..193c46e:
1 added lines match a refused pattern in dev~20..dev:
  test/test_demo_terminal.py:436: type-ignore: self.reserved_at_accept = len(self.module.RESERVED)  # type: ignore[attr-defined]
(exit 1)
```

The second finding is merged code from `phase-wbf-09`; it was sent to Ideation rather than changed
here.

The plan check on the repository, through `audit_plan_phases`:

```
errors: []
counts: plans 81, recent_plans 23, registered_phases_checked 42, phase_ids_named 457
```

The new READY procedure, run on this branch rebased on `dev` `193c46e`:

```
base (temporary git clone --shared of dev 193c46e): 1454 passed, 1 skipped, 1 warning
branch: 1508 passed, 1 skipped, 1 warning
check_test_baseline: Test baseline OK: 1454 tests passed in the base; none is missing or skipped in the branch (1509 tests in the branch, 1455 in the base).   (exit 0)
check_diff_patterns dev..HEAD: Diff patterns OK: no added type-ignore, cast(Any, or broad except/pass in dev..HEAD.   (exit 0)
governance --containment phase-grd-03: no undeclared changes (dev...agent/phase-grd-03)   (exit 0)
```

## Acceptance

- Baseline tool five cases — `Met`. `test_removed_test_fails` (1), `test_newly_skipped_test_fails`
  (1), `test_added_test_passes` (0), `test_unchanged_run_passes` (0), `test_skipped_in_both_passes`
  (0), plus a round trip through a real pytest JUnit report.
- Diff tool cases and the `dev~20..dev` run — `Met`. Each pattern added (1, nine variants);
  `type-ignore[import-untyped]` (0); `except FileNotFoundError: pass` (0); an unchanged existing
  ignore in context (0); a removed ignore (0). Both `dev~20..dev` runs are recorded above.
- Plan check cases and the repository — `Met`. A plan dated 2026-09-23 with an unnamed registered
  phase fails naming the plan and the phase; the same plan dated 2026-09-21 passes; a plan naming
  `phase-zzz-99` fails; the repository passes with the counts above, after PLAN-052's line naming
  the never-registered `phase-plug-10` was reworded (owner ruling).
- GOV-017 and PROMPT-037 show both tools in READY and the sign-off rule — `Met`. GOV-017's merge
  gate step 1 and PROMPT-037 item 4 (c) name both tools, the owner sign-off naming the tests or
  lines accepted, recorded in the session record, and the non-blocking `--containment` report for a
  claimed phase (`phase-dgov-06` is complete, so "once it exists" applies now).

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: every acceptance condition met on
`agent/phase-grd-03`; awaiting the owner-approved merge, then the completion edit on dev.

## Unresolved

None.
