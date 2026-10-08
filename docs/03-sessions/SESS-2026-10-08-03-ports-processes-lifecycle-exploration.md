---
schema_version: 1
id: doc-session-ports-processes-lifecycle-exploration
code: SESS-2026-10-08-03
title: Ports and system processes lifecycle exploration (phase-arch-11)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-delivery]
depends_on: [doc-workbench-architecture-quality-requirements, doc-workbench-architecture-quality]
---

# Ports and system processes lifecycle exploration (phase-arch-11)

## Phase

`phase-arch-11` (ports and system processes: lifecycle exploration), claimed by `agent-builder-a`
(Session 1 - Builder A) under the Session Manager's `ASSIGN`, run 2026-10-08. Worked in
`/home/user/d-system-worktrees/phase-arch-11` on `agent/phase-arch-11`, cut from the run's
integration branch `ccr-b69b05b4-tdcrux`, which stands in for `dev` in this run. Documentation only;
no code changed.

## What changed

- `docs/00-working/ports-and-processes-lifecycle.md` (new, ungoverned, no front matter, per
  `ADR-010`): what the repository starts (7 process kinds), the three incident families with dated
  document citations, the port and process lifecycle with fresh Linux traces, recorded kill
  conditions and practices, the current management practices and their gaps, the tension between a
  kill action and `ADR-015`'s read-only posture (described, not resolved), what is not established,
  twelve questions for `phase-arch-12`, and a reproduction recipe.
- `docs/09-backlog/backlog.yaml`: this phase's `session`, `completion_evidence` and `result` only.
- `docs/08-governance/catalog.md`: regenerated for this record.

## Incidents cited

- The port-8000 conflict: `SESS-2026-09-10-07` (2026-09-10) and `SESS-2026-09-14-02`
  (2026-09-13/14); the standing explicit-port rule in `AGENTS.md` and `OPS-001`.
- Orphaned and stale dev servers: `SESS-2026-09-11-08`, `SESS-2026-09-10-12`, `SESS-2026-09-14-09`,
  `SESS-2026-10-04-09`; ideas `000138` and `000246`.
- PTY child reaping: ideas `000099` and `000129`; `SESS-2026-09-10-11`, `SESS-2026-09-12-02`,
  `SESS-2026-09-10-06`, `SESS-2026-10-04-11`.

## Fresh evidence gathered (Linux sandbox, 2026-10-08)

Not repository changes. Scripts were kept in the session scratchpad, outside the repository, and the
reproduction commands are in section 10 of the document. Findings that go beyond the earlier records:

- A SIGKILL to the parent of a `uvicorn --reload` server leaves the worker alive, reparented to
  PID 1, holding the port and answering requests. A SIGTERM to the process group clears it.
- "The port is bindable" differs with and without `SO_REUSEADDR`: a plain bind failed for about a
  minute after the listener exited because of TIME_WAIT sockets, where uvicorn's bind succeeded.
  `REQ-011` R18's verification needs to say which.
- `PosixPtyAdapter.close()`: SIGTERM alone did not stop the interactive bash; closing the master fd
  did (return code -1, SIGHUP). Children that ignore SIGHUP or left the session survived `close()`.
  An exited shell is a zombie until its `Popen` is polled or dropped.
- During the work, a `pgrep -f` pattern matched the launching shell and the probe signalled it. This
  repeated the two earlier recorded instances (`SESS-2026-09-14-02`, `SESS-2026-10-04-09`) by accident
  and cost one tool call.

## Verification

`uv run python -m src.governance` (the phase's verification command):

```
Governance OK: 45 systems, 456 documents, 37 memories, 347 backlog phases
```

Gate checks, run before this record was written:

- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 50 source files`
- `uv run pytest`: `5 failed, 1649 passed, 1 skipped, 1 warning`. See Unresolved.
- `cd ts && npm test`: not run. `ts/node_modules` is absent in this worktree and the phase touched
  nothing under `ts/`.

## Acceptance

- `REQ-011` R17 holds, lifecycle, kill conditions and management all covered, and all three
  repository incidents cited: **Met.** Lifecycle is section 4, kill conditions section 5,
  management section 6; the incidents are section 3.1 (port 8000), 3.2 (orphaned dev servers) and
  3.3 (PTY reaping, `000099`/`000129`).
- The exploration proposes no application: **Met.** Section 9 states questions for `phase-arch-12`
  and the facts they can rely on; it names no tool design, interface or implementation.

## Unresolved

- Five tests fail in this worktree, and they fail identically with the new document moved out of the
  tree, so they are not caused by this change:
  - `test_containment.py::test_repository_history_reports_the_known_phase_prog_cases`,
    `test_engine_pages.py::test_a_known_idea_traces_to_the_git_log_and_the_fold` and the two
    `test_idea_classification.py` tests read git history. This clone is shallow
    (`git rev-parse --is-shallow-repository` prints `true`, 51 commits), and `git show 0f142ce:...`
    exits 128.
  - `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` expects a permission
    refusal and the session runs as uid 0, so the directory is writable.
  Reported as a result, not retried. The Session Manager's baseline for the trunk should show the
  same five if the clone is the cause.
- Windows and macOS behavior of every item the document covers: owner-machine, not run.
- Vite's behavior without `--strictPort` was not reproduced: `ts/node_modules` is absent here.
- `000246` (terminal panel drops its connection) remains uninvestigated.

## Assumptions and decisions awaiting ratification

- No ADR was written, so nothing here awaits ratification. The kill-action versus `ADR-015` tension is
  described in section 7 of the document and left to `phase-arch-12`'s own ADR.
- Assumption: "incidents" was read to include every recorded stale or orphaned dev server, not only
  the one named in `SESS-2026-09-11-08`, so the document cites five such records.
- Assumption: the owner's phrase "the port-8000 conflict noted mid-session during the workbench builds"
  is the three records in section 3.1; no earlier mention of port 8000 was found in sessions, the
  backlog or the idea log.
- Judgement: the unrelated program on port 8000 is not named, following the `SESS-2026-09-14-02`
  review finding D1. The document records the constraint it creates for a listener display.
- The commit trailer follows the session's attribution reminder (Claude Sonnet 5.5), not the
  `Claude Fable 5.1` line in the builder contract, because that is the model that did the work.
