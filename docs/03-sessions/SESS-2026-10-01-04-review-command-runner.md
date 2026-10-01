---
schema_version: 1
id: doc-session-review-command-runner
code: SESS-2026-10-01-04
title: A fixed command runner for build reviews
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-gov-docs]
depends_on: [doc-reviewer-contract]
---

# A fixed command runner for build reviews

## Phase

`phase-asr-02` — A fixed command runner for build reviews.

Assigned by Session Manager to Session 2 - Builder B (agent-builder-b). Claimed on dev at `80a545d`
inside a granted turn. Work is on `agent/phase-asr-02` in `../d-system-worktrees/phase-asr-02`.

## Verification

Run in this worktree on `agent/phase-asr-02` rebased onto dev `a91a8e3`:

```
$ uv run pytest test/test_run_review_checks.py
22 passed, 1 warning
$ uv run ruff check src/ test/ tools/run_review_checks.py
All checks passed!
$ uv run mypy src/ tools/run_review_checks.py
Success: no issues found in 48 source files
$ uv run python -m src.governance --catalog
417 documents — adr: 23, architecture: 12, governance: 19, operation: 25, plan: 81, prompt: 43, requirement: 35, session: 179.
$ uv run python -m src.governance
Governance OK: 43 systems, 417 documents, 34 memories, 347 backlog phases
$ git diff --exit-code docs/08-governance/catalog.md
(no output, exit 0)
```

Supporting checks: `uv run python tools/generate_tool_docs.py --check` reports
`24 tool document(s) current`. `uv run python -m src.governance --containment phase-asr-02` reports
`phase-asr-02: no undeclared changes (dev...agent/phase-asr-02)`.

## Acceptance

- Fixtures: **Met.**
  - A phase whose commands run lists each with its exit code
    (`test_a_phase_whose_commands_run_lists_each_with_its_exit_code`).
  - A failing command is recorded and not retried (`test_a_failing_command_is_recorded_and_the_rest_still_run`,
    `test_a_failing_command_is_not_retried`, which counts the attempts).
  - An unknown phase id is refused (`test_an_unknown_phase_id_is_refused_before_anything_is_created`,
    `test_the_cli_refuses_an_unknown_phase_id`).
  - An extra command argument is refused (`test_the_cli_refuses_an_extra_command_argument`,
    `test_the_cli_refuses_an_option_it_does_not_define`).
  - All pass in the run above.
- After each run, `git worktree list` shows no worktree left behind: **Met.**
  `test_no_worktree_is_left_behind` covers a passing, a failing and a timed-out phase;
  `test_the_worktree_is_removed_when_the_run_is_interrupted` covers an interrupted run.
  The real run below left none.
- Run for one completed phase against its completion commit, with the manifest recorded here:
  **Met.**

Run of `uv run python tools/run_review_checks.py phase-idg-19 458ab36` from this worktree at
`b7687a0` (exit 0):

```
phase phase-idg-19 at 458ab360d7fc6a54c7c6dc28680253486e1e013f (verification list from dev 8340c90ca52f1c79e04bcc7a1c9c284c17180594): passed

| # | Kind | Command | Exit | File | sha256 |
|---|---|---|---|---|---|
| 1 | setup | `uv sync --extra dev` | 0 | _working/review-checks/phase-idg-19/458ab360d7fc/01-setup.txt | d5236108c9154ce025dbbecfe13b3cf64d20ca66b4fd26f11a62fe80eedfe5b1 |
| 2 | verification+gate | `uv run pytest` | 0 | _working/review-checks/phase-idg-19/458ab360d7fc/02-verification+gate.txt | e0bb309e123c5d6f7f3362a0af3700699c3dc3c18b47e868ab2871c38cb49a7b |
| 3 | verification+gate | `uv run python -m src.governance` | 0 | _working/review-checks/phase-idg-19/458ab360d7fc/03-verification+gate.txt | 17a87b89ab2de93adb1dd6a965b16c047410016a3786bdcb1a052004800630f4 |
| 4 | gate | `uv run ruff check src/ test/` | 0 | _working/review-checks/phase-idg-19/458ab360d7fc/04-gate.txt | 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18 |
| 5 | gate | `uv run mypy src/` | 0 | _working/review-checks/phase-idg-19/458ab360d7fc/05-gate.txt | a97cee1ee1bdb5e2d1ca7098f7b33a6c6a21263225643192fdeb78654687ed89 |
```

The evidence files' last lines: `1187 passed, 1 warning`; `Governance OK: 43 systems, 409
documents, 34 memories, 347 backlog phases`; `All checks passed!`; `Success: no issues found in 46
source files`. `sha256sum 02-verification+gate.txt` matches the manifest. `git worktree list`
afterwards showed no `review-phase-idg-19-…` entry.

## Backlog

`phase-asr-02`: `status: active`, `agent: agent-builder-b`. `next_action`: all acceptance
conditions met and verification green on `agent/phase-asr-02`; awaiting the `/session-close`
independent review, READY to Session Manager, and the owner's merge approval.

## Unresolved

None.
