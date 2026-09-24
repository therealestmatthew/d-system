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
  catalog; regenerate it with ``uv run python -m src.governance --catalog`` and commit the result`,
  exit 1. `--catalog`: exit 0. Plain check afterwards: `Governance OK`, exit 0. Plain check on the
  restored clean tree: exit 0, `git status --porcelain` empty.
- **Stale ideas.md.** One idea appended to the worktree's log with `tools/append_idea.py add`
  (the writer assigned `000419` in that scratch log; never committed). Plain check: `ERROR
  docs/00-working/ideas.md: differs from the rendered idea log; regenerate it with ``uv run python
  tools/generate_ideas_md.py`` and commit the result`, exit 1. After `tools/generate_ideas_md.py`:
  `Governance OK`, exit 0.
- **CI steps.** The python job's steps from `.github/workflows/ci.yaml`, run in order by a local
  script that stops at the first failure. On a scratch clone with a committed stale catalog
  (`phase-sch-06` status changed): sync exit 0, private-content exit 0, `Catalog is current` exit 1,
  job stopped there, before governance and pytest. On the branch tip (`dev` plus this phase):
  every step exit 0, pytest `1062 passed, 1 skipped`.
- **Repair path.** `test_catalog_flag_still_repairs_a_stale_catalog`: with both staleness checks
  reporting stale, `--catalog` still exits 0 and writes the catalog; the plain check exits 1
  naming both files.
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
- New hook run directly: Not met; the hook is not yet changed.
- `grep -n "governance only"` in PROMPT-037 returns no completion-edit line: Not met; the
  procedure text is not yet changed.
- Added governance run time and hook run time recorded: Not met; governance time recorded, hook
  time not yet measured.
- GOV-017 and the hook's operations document state the no-bypass rule: Not met; not yet written.
- AGENTS.md shows approved text, or the record states approval was not given and the lines are
  unchanged: Met. Asked with the exact old text and a drafted replacement on 2026-09-24; the owner
  chose "No change": lines 155-156 stay as they are, since this phase's CI step makes "CI diffs it
  and fails when it is stale" true. AGENTS.md is unchanged.

## Backlog

`status: active`. `next_action`: Governance staleness check, tests and CI step are done. Next:
add governance to `tools/git-hooks/pre-commit` and test it directly; write the no-bypass rule in
GOV-017 and the hook's operations document; name `--catalog` in GOV-017 merge-gate step 6 and
PROMPT-037 item 4(iii) and builder step 5.

## Unresolved

- The pre-commit hook will run the governance check against the working tree, not the staged
  index, because that is what the governance command reads. An unstaged stale file, including a
  peer's uncommitted work in the primary checkout, can therefore refuse a commit. To be recorded
  in the hook's operations document.
