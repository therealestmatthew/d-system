---
schema_version: 1
id: doc-session-containment-check
code: SESS-2026-10-01-03
title: Diff a phase's change set against its declared paths (phase-dgov-06)
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-governance, sys-backlog]
depends_on: [doc-document-backlog-governance]
---

# Diff a phase's change set against its declared paths (phase-dgov-06)

## Phase

`phase-dgov-06` — Diff a phase's change set against its declared paths, for completed phases and
active branches. Run by Session 5 - Batch Runner as agent `agent-coord`, claimed at 00955c6 with
the owner's approval, on branch `agent/phase-dgov-06`.

## Verification

Run in the worktree, rebased onto dev 6b873bf, after the review fix.

`uv run pytest test/test_containment.py`

```
19 passed, 1 warning in 7.91s
```

`uv run python -m src.governance --containment` (exit 0)

```
Containment: 133 phases, 91 checked, 42 not located, 75 with findings (1192 files, 45 with other phases' backlog entries)
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 415 documents, 34 memories, 347 backlog phases
```

The full suite gave `1265 passed, 1 warning in 139.97s`; `uv run ruff check src/ test/` gave
`All checks passed!` and `uv run mypy src/` gave `Success: no issues found in 47 source files`.

The full repository run is saved at `_working/session-manager/dgov-06-containment-run.txt`
(gitignored). Of the 1192 files, 46 lie inside one of the phase's declared systems and 1146 outside
them. The 42 phases not located: 38 entered the backlog already complete, before claims were
committed on `dev`, and 4 went from `queued` straight to `complete`. Run in active-branch mode on
this phase's own branch, the check reports `phase-dgov-06: no undeclared changes
(dev...agent/phase-dgov-06)`.

## Acceptance

- REQ-015 R12 holds (run against a phase with a known undeclared path, the check names the phase
  and the file in both modes; the run against every completed phase is recorded): Met.
  `test_completed_mode_names_the_phase_and_its_undeclared_files` and
  `test_branch_mode_names_the_undeclared_file` check both modes against fixture histories. The
  repository run above is recorded, and it is not a zero-finding run.
- REQ-015 R13 holds (the output distinguishes a too-narrow declaration from genuine strays, and
  nothing writes to backlog.yaml): Met. Each finding says either `inside declared system <id>:
  declaration may be too narrow` or `outside declared systems; owned by <id>` (or `no system owns
  it`). `test_report_only_cli_exits_zero_on_findings_and_writes_nothing` checks exit 0 on findings
  and that neither the tree nor any ref changes. The module runs only `git log`, `git show`,
  `git diff` and `git merge-base`.
- The phase-prog-* case appears, including phase-prog-04 (3da1295) and phase-prog-05 (744d4c8),
  while a phase's own status edits do not: Met. The repository run reports phase-prog-04 editing
  16 other phases' entries and phase-prog-05 editing 7, each within a range that contains the named
  commit; `test_repository_history_reports_the_known_phase_prog_cases` checks this on every run,
  and that neither phase's own id is reported.
- Run in active-branch mode against a scratch branch with one undeclared file, it names that file:
  Met. `test_branch_mode_names_the_undeclared_file`.

## Backlog

`status: active`, `agent: agent-coord`. `next_action`: built and verified; independent review,
then READY to the Session Manager and the owner's merge approval.

## Unresolved

- The claim-to-completion range sweeps in other sessions' commits that name no phase, or name a
  phase that is not active. That is most of the 1192 files: phase-demo-07's range alone is 403
  commits. The rule is the owner's (REQ-015 R12, narrowed on 2026-10-01); exact attribution needs a
  recorded range, captured as idea 000523.
- REQ-015 R12's text still says "except those whose message names a different phase id". The
  owner's ruling of 2026-10-01 narrows it to phases active at that commit; the requirement document
  is not one of this phase's deliverables and was not amended.

## Review

Independent review by a `demo-adversary` agent (Sonnet) over dev...agent/phase-dgov-06 at 04b1596,
recorded as it reported:

- R12: Met. The rerun of `--containment` was byte-identical to the recorded run. Claim and
  completion commits for phase-plfx-01, phase-cap-05 and phase-gov-01 were checked by hand against
  `git log -p` on backlog.yaml and were correct.
- R13: Met on "no write": only `git log`, `git show`, `git diff` and `git merge-base` run, and
  `git status` and `git show-ref` were unchanged. The too-narrow versus stray distinction is
  evidence derived from the systems registry, not a label. Undermined in practice by the blocker.
- phase-prog-04 and phase-prog-05: Met against live history; 3da1295 and 744d4c8 fall inside the
  ranges.
- Scratch branch with one undeclared file: Met.
- The owner's 2026-10-01 peer-drop ruling is implemented exactly as stated.
- BLOCKER, `src/governance/containment.py:253`: branch mode exempted every file under
  `docs/03-sessions/`, unlike completed mode, which exempts only the phase's own record. Reproduced:
  a branch editing another phase's session record reported "no undeclared changes".
- MINOR, `containment.py:39-40`: the phase-id patterns assume exactly two digits.
- MINOR, `containment.py:116`: a commit whose body merely mentions an active phase is dropped as
  that phase's work (phase-cap-05's `32c55d0`, dropped as phase-idg-10's). Across all 188 dropped
  commits with non-exempt files, every such case genuinely belonged to the named phase.
- Disclosed: REQ-015 R12's text still reads "names a different phase id".

Resolution:

- Blocker: fixed in 048af24. Branch mode now exempts the phase's recorded session path and the
  session records the branch adds; an edit to an existing record is reported.
  `test_branch_mode_reports_an_edit_to_another_session_record` reproduces the reviewer's case.
- First minor: accepted. `schemas/backlog.schema.json` requires `^phase-[a-z]+-[0-9]{2}$`, so a
  three-digit id cannot exist.
- Second minor: accepted. It is the owner's rule ("its message names" a phase), and the reviewer
  found no case where it misattributed a file.

## Decisions

- The claim and completion commits are found from the phase's own status changes in backlog.yaml,
  read revision by revision along dev's first-parent history (476 revisions, about 5 seconds),
  rather than from commit subjects, which the Scout found unreliable for 42 of 129 phases.
- The owner ruled the completed-phase filter in this session. R12 as written drops any commit
  naming a different phase id, which drops the two commits acceptance item 3 requires (3da1295
  names only phase-prog-01; 744d4c8 names four other phases and not phase-prog-05). The check
  drops a commit only when its message names another phase active before or after that commit and
  does not name this one.
- A phase that cannot be located is reported with the reason and no change set, never a guessed
  range.
- Each finding carries whether the file lies inside a declared system, so a person can judge a
  too-narrow declaration from stray work. The check does not decide which.
- The phase replaced the earlier assignment of phase-des-08 and was claimed after it merged; the
  owner approved this claim separately.

## Corrections

- One fixture assertion expected one dropped peer commit; the peer's claim commit is a second, and
  correctly dropped. The test was corrected.
- The review's blocker above, fixed in 048af24.

## Left undone

- Exact attribution of a phase's own commits needs its integrated range recorded at completion
  (idea 000523). Until then most findings are other sessions' unlabelled commits within a long
  range, which a reader has to set aside by hand.
- REQ-015 R12 still states the broader filter; amending it is the owner's call.
