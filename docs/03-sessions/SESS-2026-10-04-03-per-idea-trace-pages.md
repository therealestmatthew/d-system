---
schema_version: 1
id: doc-session-per-idea-trace-pages
code: SESS-2026-10-04-03
title: Build the per-idea trace pages
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Build the per-idea trace pages

## Phase

`phase-des-11` — Build the per-idea trace pages.

## Verification

`uv run pytest`

```text
1412 passed, 1 skipped, 1 warning
```

`uv run python -m src.governance`

```text
Governance OK: 43 systems, 425 documents, 36 memories, 347 backlog phases
```

`uv run python tools/check_no_private_content.py`

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (1280 tracked files, 0 identifiers checked)
```

The worktree cannot see `_private/portfolio/`, so the content half of that check read no
identifiers. It was rerun from the worktree with the 140 trace pages staged, taking the identifier
list from the primary checkout through the script's own `confidential_identifiers()` and
`check_content()`: `1288 tracked files (pages staged), 31 identifiers, 0 violations`.

Behavioural checks done by hand:

- The trace page for `000236` was rendered in headless Chrome with JavaScript disabled. Capture,
  plan, phases, delivery and the gate table all render (R12).
- The two dated entries on that page were checked against `git log` by hand. `PLAN-029` reads
  `draft` at `c7b2f62` and `active` at `3da1295` (2026-09-15), the date and commit the page gives
  for G3. `phase-idg-01` reads `active` at `ea3635a` and `complete` at `4a95e12` (2026-09-25), the
  date and commit the page gives for G4 and G5.
- Three mutations of the generator were run against the new tests, and each made a test fail:
  dating a phase by its latest `complete` commit instead of its earliest, accepting any plan status
  at G3, and dropping `promoted_to` from the traced set.

## Acceptance

- REQ-036 R19 (the set of trace pages equals the set of linked ideas): Met.
  `test_trace_pages_are_exactly_the_linked_ideas` compares the rendered `trace/` set with the
  ideas that carry `promoted_to` or appear in a phase's `ideas` field, read without the generator.
  `test_ledger_links_each_traced_idea_and_no_other` checks the ledger column for all of them.
  `main` removes a trace page whose idea lost its last link (`test_a_stale_trace_page_is_removed`).
  140 pages are committed.
- REQ-036 R20 (each gate entry for a known idea matches the git log and the fold): Met.
  `test_a_known_idea_traces_to_the_git_log_and_the_fold` covers `000236`. It checks G1 against
  `fold()`, G2 as not recorded, and G3 against a separate walk of `PLAN-029`'s file history. It
  checks G4 and G5 against a separate walk of every first-parent version of `backlog.yaml`, not
  only the generator's candidates, and the owner rulings against the fold's `assessment`
  annotations. The hand check above agrees.
- REQ-036 R07 to R13 still hold: Met. The byte-identical two-run test now compares every page,
  traces included. The colour-literal, house-family and no-script tests run over every page from
  `render_all`. The fold-only source test still passes. The private-content result is above.

## Backlog

`status: active`. The phase stays active until the branch is merged onto `dev` with the owner's
approval (the Session Manager's contract). The completion edit is made on `dev` after that merge.

## Unresolved

- A historical `dev` commit, `5ec45ea`, holds a `backlog.yaml` that does not parse as YAML. The
  generator's line scan reads it; a full YAML parse of that version fails. Nothing else in this
  phase depends on it.

## Review

A `demo-adversary` agent reviewed `c767045..edf2f46`. It stopped at its turn limit and was asked
to report from what it had. Its report, condition by condition:

- Verdict: PASS.
- R19: Met. An independent recount outside the generator gave 140 traced ideas, 140 pages on
  disk and an empty difference. Commit `befa13a` only adds trace pages.
- R20: Met, and verified beyond the one sampled idea. The known-idea test is a real second
  implementation: it rebuilds G3 by its own `--follow` walk with a front-matter regex, and G4 and
  G5 by its own walk of every first-parent version, not only the generator's `-G` candidates. The
  reviewer also YAML-parsed all 505 first-parent versions of `backlog.yaml` and compared every
  phase's earliest complete commit with `_phase_history()`. Both found 140 phases, with no phase
  only in one and no date mismatched. One version, `5ec45ea` (2026-09-22), failed to parse
  ("mapping values are not allowed here"), and the line scan reads it correctly. Merge commit
  `818f64b` is handled.
- R07 to R13: Met. `test/test_engine_pages.py` gave 51 passed. The private-content check in the
  worktree read 0 identifiers. The reviewer could not reproduce the "31 identifiers, 0
  violations" rerun from inside the worktree and took it on faith.
- Finding 1, minor: `NOT_REACHED = "not reached"` is vocabulary that neither R20 nor the phase
  scope specifies. It is applied consistently and tested, so it is a wording decision, not a
  correctness problem.
- Finding 2, minor: OPS-028's shallow-clone failure note is backed by a unit test on
  `trace_data` with a synthetic shallow history, not by a shallow clone run end to end.
- Also checked and holding: `000274`'s promotion to `REQ-025` renders as "not a plan document",
  "not recorded"; colour literals, script and house family over all 143 pages; CI's
  `fetch-depth: 0`; the stale-page removal and the 143-page output line in OPS-028.
- Not checked: plan history under renames or approved-to-draft-to-approved; determinism across
  two separate processes with a cold cache; every OPS-028 sentence line by line; the 31-identifier
  figure.

After the review, two of the unchecked items were run in this session:

- Two separate `uv run python tools/generate_engine_pages.py --out` runs produced identical
  output for all 143 pages.
- Every first-parent version of every plan file under `docs/01-plans/` was read, with front
  matter matched by regex, and each plan's earliest G3 commit compared with `_plan_history()`:
  `brute 43 gen 43 only brute set() only gen set() mismatch {}`.

Both findings are accepted. On finding 1 the owner chose to keep "not reached". Finding 2 is
accepted as unit-level evidence.

## Decisions

- Gate dates are read from `HEAD`'s first-parent history, the commit the stamp names, rather than
  from the `dev` ref. Two runs on one commit then agree (R07), and on `dev` the two are the same
  history.
- The owner kept "not reached" for a gate the record shows has not happened yet. "not recorded"
  stays for a gate with no record at all: G2, a `promoted_to` naming a document that is not a
  plan, and a shallow clone.
- A `promoted_to` that names something other than a plan (`000274` to `REQ-025`, `000317` to
  `doc-batch-orchestration-protocol`, which is `GOV-016`) appears in the plan table with G3
  "not recorded" and the reason, instead of being dropped.
- The generator's operations document, OPS-028, went stale with the docstring and output change.
  The owner chose to widen the phase's deliverables to include it (`cb3b42f` on `dev`, through a
  Session Manager turn) rather than narrow the change or edit it undeclared.
- Trace pages inline the house stylesheets like the other pages, so the 140 pages add about 2.3 MB
  to `_public/engine/`.

## Corrections

- The first full test run showed three failures. The session record had been written while that
  run was going, so the catalog was stale for it. After `--catalog` the suite passed: 1412 passed,
  1 skipped.
- The test's first walk of `backlog.yaml` history parsed each version as YAML and failed on
  `5ec45ea`. It now matches the phase block's status line with a regex.
- A `git log --diff-merges=first-parent` call in the test printed patches until `-s` was added.

## Left undone

- `phase-des-11` stays `active` until its branch is merged onto `dev` with the owner's approval.
  The completion edit is made on `dev` after that merge.
- The historical `backlog.yaml` at `5ec45ea` that does not parse is noted, not repaired. History
  is not rewritten.
