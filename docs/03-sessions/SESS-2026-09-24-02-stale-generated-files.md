---
schema_version: 1
id: doc-session-stale-generated-files
code: SESS-2026-09-24-02
title: Stale generated files fail loudly
kind: session
status: active
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-24'
systems: [sys-governance, sys-gov-docs]
depends_on: [doc-deterministic-guards]
---

# Stale generated files fail loudly

## Phase

`phase-grd-01` — Stale generated files fail loudly: catalog and ideas.md checks in governance, the
CI catalog step, governance in pre-commit, and the completion edit.

## Verification

Run in `../d-system-worktrees/phase-grd-01` on `agent/phase-grd-01`.

```text
$ uv run pytest test/test_governance_staleness.py
10 passed, 1 warning

$ uv run python -m src.governance --catalog
exit 0

$ uv run python -m src.governance
Governance OK: 35 systems, 344 documents, 32 memories, 299 backlog phases

$ git diff --exit-code docs/08-governance/catalog.md
exit 0

$ uv run ruff check src/ test/
All checks passed!

$ uv run mypy src/
Success: no issues found in 46 source files
```

Acceptance runs (behavioural checks, each reverted afterwards with `git checkout --`):

- **Stale catalog.** `phase-sch-06` changed from `deferred` to `queued` in `backlog.yaml`, catalog
  not regenerated. Plain check: `ERROR docs/08-governance/catalog.md: differs from the rendered
  catalog`, followed by the `--catalog` regeneration instruction, exit 1. `--catalog`: exit 0. Plain check afterwards: `Governance OK`, exit 0. Plain check on the
  restored clean tree: exit 0, `git status --porcelain` empty.
- **Stale ideas.md.** One idea appended to the worktree's log with `tools/append_idea.py add`
  (the writer assigned `000419` in that scratch log; never committed). Plain check: `ERROR
  docs/00-working/ideas.md: differs from the rendered idea log`, followed by the
  `tools/generate_ideas_md.py` regeneration instruction, exit 1. After `tools/generate_ideas_md.py`:
  `Governance OK`, exit 0.
- **CI steps.** The python job's steps from `.github/workflows/ci.yaml`, run in order by a local
  script that stops at the first failure. On a scratch clone with a committed stale catalog
  (`phase-sch-06` status changed): sync exit 0, private-content exit 0, `Catalog is current` exit 1,
  job stopped there, before governance and pytest. On the branch tip (`dev` plus this phase):
  every step exit 0, pytest `1062 passed, 1 skipped`.
- **Repair path.** `test_catalog_flag_still_repairs_a_stale_catalog`: with both staleness checks
  reporting stale, `--catalog` still exits 0 and writes the catalog; the plain check exits 1
  naming both files.
- **Hook, run directly** (`sh tools/git-hooks/pre-commit` in the worktree; a `git commit` there runs
  the primary checkout's old hook). Stale catalog staged (`phase-sch-06` status changed): private
  check OK, then `ERROR docs/08-governance/catalog.md: differs from the rendered catalog; ...`,
  exit 1. Catalog regenerated and staged: `Governance OK`, exit 0. In a scratch clone under the
  session scratchpad, with a fictional project `zqx-fixture-alpha` under that clone's
  `_private/portfolio/projects/`: a staged file naming it gave `check_no_private_content: FAILED -
  scratch-fixture.md: matches confidential identifier 'zqx-fixture-alpha'`, exit 1; the fixture
  force-added under `_private/` gave `tracked file under a private path`, exit 1; the clean clone
  exit 0.
- **Hook run time.** Median of 10 in the worktree: 0.05 s with `dev`'s hook, 2.24 s with the new
  hook.
- **Added governance run time.** In process, median of 10: catalog render and compare 3 ms,
  `ideas.md` render and compare 19 ms. Whole command, median of 10: 2.20 s on `dev` (primary
  checkout), 2.41 s on this branch.

## Acceptance

- Scratch branch, stale catalog fails naming catalog.md, passes after --catalog, plain check
  leaves git status empty: Met (acceptance run "Stale catalog").
- Scratch idea without regenerating fails naming ideas.md, passes after regeneration: Met
  (acceptance run "Stale ideas.md").
- CI Python steps fail at the catalog step on a stale-catalog commit and exit 0 on dev: Met
  (acceptance run "CI steps").
- New hook run directly exits nonzero on a staged stale catalog with the governance error shown,
  0 once regenerated, nonzero on a staged private-identifier fixture: Met (acceptance run "Hook,
  run directly").
- `grep -n "governance only"` in PROMPT-037 returns no completion-edit line: Met; the grep returns
  nothing (exit 1). Item 4(iii) and the builder roles' step 5 now name `--catalog`, as does GOV-017
  merge-gate step 6.
- Added governance run time and hook run time recorded: Met (acceptance runs "Hook run time" and
  "Added governance run time").
- GOV-017 and the hook's operations document state the no-bypass rule: Met; GOV-017's merge gate
  carries the owner ruling of 2026-09-23, and OPS-009's new section "The pre-commit hook also runs
  governance" states it, as does the hook's header comment.
- AGENTS.md shows approved text, or the record states approval was not given and the lines are
  unchanged: Met. Asked with the exact old text and a drafted replacement on 2026-09-24; the owner
  chose "No change": lines 155-156 stay as they are, since this phase's CI step makes "CI diffs it
  and fails when it is stale" true. AGENTS.md is unchanged.

## Backlog

`status: active`. `next_action`: Review done (all 8 Met; F1 fixed in 799f1c3, F2 and F3
accepted). Next, rebase onto dev, run the four gate checks and send READY.

## Unresolved

- The pre-commit hook runs the governance check against the working tree, not the staged index,
  because that is what the governance command reads. Recorded in OPS-009 as a known limitation;
  not changed by this phase.

## Review

Independent review by a `demo-adversary` agent on 2026-09-24, given the diff range
`dev...agent/phase-grd-01` (tip `ebfa460`), REQ-028, PLAN-045 and the phase's scope, acceptance and
verification lists; it read this record only for acceptance 6 and 8. It stopped at its turn limit
once and was asked to report from what it had run. Its report, verbatim except for line wrapping:

Acceptance verdicts:

| # | Verdict | Evidence (as reported) |
|---|---|---|
| 1 | Met | In a throwaway clone, `phase-sch-06` status changed: `ERROR docs/08-governance/catalog.md: differs from the rendered catalog; ...`, exit 1. After `--catalog`: `Governance OK`, exit 0. On the unmodified worktree `git status --porcelain` empty before and after the plain check. |
| 2 | Met | `tools/append_idea.py add` in the scratch log (created `000419`, never committed), then governance: `ERROR docs/00-working/ideas.md: differs from the rendered idea log; ...`, exit 1. After `tools/generate_ideas_md.py`: `Governance OK`, exit 0. |
| 3 | Met | The new "Catalog is current" step on the stale clone: `git diff exit: 1`, before governance and pytest. On a fresh `dev` clone: `git diff exit: 0`, governance exit 0. |
| 4 | Met | `sh tools/git-hooks/pre-commit` with a staged stale `backlog.yaml`: private check OK, then the catalog error, exit 1. Regenerated catalog staged: exit 0. Fictional `_private/portfolio/projects/zqx-fixture-alpha.md` force-staged: `tracked file under a private path`, exit 1. |
| 5 | Met | `grep -n "governance only"` in PROMPT-037: exit 1, no match. Item 4(iii), the builder role's step 5 and GOV-017 merge-gate step 6 name `--catalog`. |
| 6 | Met | This record's run-time entries; spot check `time uv run python -m src.governance` real 2.174 s. |
| 7 | Met | GOV-017 owner ruling paragraph; OPS-009 "Never bypass a failing hook with `--no-verify`"; the hook's header comment. |
| 8 | Met (observable proxy only) | `git diff dev...agent/phase-grd-01 -- AGENTS.md` empty; this record states the owner chose "No change". The exchange with the owner is not in the repository and could not be verified. |

Full suite `1064 passed, 1 skipped`; staleness tests `10 passed`; ruff `All checks passed!`; mypy
`Success: no issues found in 46 source files`; `test/test_ideas.py` and
`test/test_governance_staleness.py` together `72 passed`, no module-cache collision.

Findings:

1. Note, `src/governance/__main__.py` ideas.md check: the except clause did not include
   `src.db.ideas.IdeaError`, which `fold`/`load_events` raise on a malformed idea log. On a
   corrupt scratch log governance crashed with a traceback, but from the pre-existing
   `audit_idea_priority(ROOT)` call, which runs first on the same fold; so the narrower clause was
   dead code for that input, not a new regression. Worth widening for consistency.
2. Note, workflow outside the phase's declared scope: with the new hook, a `tools/append_idea.py`
   commit is refused unless `tools/generate_ideas_md.py` has been run first. The error names the
   fix. Neither GOV-006 nor AGENTS.md's idea-capture text mentions the precondition.
3. Note, verified not a bug: the catalog comparison runs only when no other error was found,
   while the ideas.md comparison always runs in plain mode. A commit that both regresses a status
   and leaves the catalog stale reports only the regression until it is fixed. The combined
   fixture was not run (turn limit).
4. No discrepancies found in the CI step, the hook's ordering and `set -e`, the query modes'
   exemption, the shared `fold`/`load_events`, trailing-newline handling, and the files touched.

Not checked: the combined regression-plus-stale fixture; CRLF and `D_SYSTEM_DATA_ROOT`
permutations beyond reading the code; a real GitHub Actions run and its checkout's branches.

Dispositions: finding 1 fixed in `799f1c3` (the ideas.md check now catches `IdeaError` and reports
it as a governance error). Finding 2 accepted: the refusal is the behaviour R04 asks for and its
message names the fix; the writer leaving `ideas.md` stale is idea `000155`, and Ideation's
procedure already regenerates the view before committing. Finding 3 accepted as designed.

## Decisions

- The staleness checks run only in the plain governance mode. `--catalog` is the repair for a
  stale catalog, so failing it on staleness would block the fix; the query modes (`--ready`,
  `--next-code` and the rest) are run mid-edit, before regeneration. A test pins the repair path.
- The ideas.md renderer is imported from `tools/generate_ideas_md.py` by path, from the repository
  holding the code, so governance and the generator cannot render differently.
- The CI catalog step discards `--catalog`'s stdout and compares with `git diff --exit-code`,
  as PLAN-045 D4 specifies.
- The hook's operations document is OPS-009, the document that already describes the hook.
- The private-content fixtures ran in a scratch clone under the session scratchpad with a
  fictional project id, so nothing was written to this repository's `_private/`.
- AGENTS.md lines 155-156: the owner was asked with the exact old text and a drafted replacement,
  and chose "No change", as the Scout also suggested (the CI fix makes the line true).

## Corrections

- The first R01 scratch attempts changed a status to `blocked`, then `cancelled`; both raised
  unrelated governance errors (missing `blocked_reason`, a cancelled phase in `next_up`). The run
  that isolates the check changed `phase-sch-06` from `deferred` to `queued`.
- The staleness module first loaded the renderer from the root being checked, which has no
  `tools/` in a test fixture, and left a half-initialised module in `sys.modules` on failure.
  Fixed in `0ecfcd6` before any merge.
- The Session Manager's assignment said PLAN-045 carried the exact AGENTS.md replacement text; it
  does not, so the draft was written in this session and put to the owner.

## Left undone

- Rebase onto `dev`, the four gate checks, `READY`, and after `GRANTED merge` the completion edit
  with `--catalog`. The phase stays `active` until then.
- Review finding 2 (document the regenerate-before-commit precondition in the idea-capture text)
  is outside this phase's deliverables; `000155` covers the writer's side.
