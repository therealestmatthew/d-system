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

Run in the worktree, rebased onto dev 8bd31ea.

`uv run pytest test/test_containment.py`

```
18 passed, 1 warning in 10.00s
```

`uv run python -m src.governance --containment` (exit 0)

```
Containment: 133 phases, 91 checked, 42 not located, 75 with findings (1192 files, 45 with other phases' backlog entries)
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 414 documents, 34 memories, 347 backlog phases
```

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
