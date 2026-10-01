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

Run in this worktree on `agent/phase-asr-02` rebased onto dev `2f25d7a`:

```
$ uv run pytest test/test_run_review_checks.py
26 passed, 1 warning
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
  `test_the_worktree_is_removed_when_the_run_is_interrupted` covers an interrupted run, and
  `test_an_os_error_partway_exits_2_and_still_removes_the_worktree` an operating-system error.
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

## Review

Independent adversarial review by a `demo-adversary` sub-agent (fresh context, not a fork) over
`dev...agent/phase-asr-02` with dev at `a91a8e3`, given the phase's scope, acceptance, verification,
deliverables and the four owner rulings. Its findings, as reported:

- **Acceptance 1** (fixtures): **Met.** `22 passed, 1 warning` on its own run. It re-derived the
  scenarios against disposable repositories under `/tmp` with the same outcomes.
- **Acceptance 2** (no worktree left behind): **Met for the paths tested.** The passing, failing,
  timed-out and interrupted runs, a forced `git worktree add` failure and a forced
  `PermissionError` left no `git worktree list` entry. Finding 1 concerns the evidence directory,
  not the worktree.
- **Acceptance 3** (real run recorded): **Met.** All five sha256 values recomputed from the files
  under `_working/review-checks/phase-idg-19/458ab360d7fc/` match the manifest. The four
  `GATE_CHECKS` strings match `GOV-017`'s merge gate character for character.
- **Finding 1, major:** `run()` wiped and recreated the evidence directory before
  `add_worktree()`. When `git worktree add` failed, the refusal left an empty evidence directory
  with no manifest. That contradicted OPS-029's "nothing was left behind". Reproduced by occupying
  the worktree path.
- **Finding 2, minor:** `main()` caught only `Refused`. A `PermissionError` creating the worktree
  parent produced a traceback instead of the documented exit 2. A malformed `dev` backlog would
  likewise raise. Reproduced with a `0o500` parent.
- **No injection path found.** It tried the commit strings `--upload-pack=touch /tmp/pwned`, `-h`,
  `--output=x`, `dev; echo injected` and `$(echo dev)`. All were refused as "does not resolve", and
  no file was created. The phase-id pattern rejects path and shell characters before any git or
  filesystem use.
- **Confirmed:**
  - Deduplication and order match the real manifest.
  - `passed` and exit 0 are impossible when a run entry failed or timed out.
  - Each sha256 is taken over the exact bytes written, including the timeout note.
  - OPS-029 matches the code apart from the two findings.
  - `generate_tool_docs.py --check` is current.
  - Governance, ruff and mypy reproduced.
- **Session-record claims:** none unsupported.
- **Probes not reached:**
  - a failure partway through writing an evidence file;
  - a malformed backlog on the real repository;
  - two concurrent runs of the same phase and commit racing on the fixed evidence path, noted as a
    design point, not reproduced.
- **Worktree:** left clean.

Disposition:
- **Both findings fixed in `a706a28`.**
  - The evidence directory is replaced only after the worktree exists, so a refused run leaves the
    previous evidence untouched.
  - Failing to create the worktree directory and an unparsable `dev` backlog are refusals (exit 2).
  - An operating-system error after the run starts exits 2 with `stopped: …`, after the worktree is
    removed.
  - Four new tests cover these. OPS-029's exit table and failure list are updated, and its
    reference block regenerated.
- **The concurrent-run note is accepted, not fixed.** Under `PLAN-047` D3 one coordinator runs the
  tool, so two runs of the same phase and commit at once are not an expected use. The OPS document
  says a second run replaces the directory.

## Decisions

The owner ruled four design points in this session, each through AskUserQuestion, because the
phase did not settle them:
- **Prose entries.** An entry runs only when its first word, past `NAME=value` assignments, is `cd`
  or a program on `PATH`; other entries are listed as not run. About 100 of the backlog's 901
  verification entries are prose, and some contain backticks, so passing them to a shell was
  rejected.
- **Evidence location.** Evidence goes to `_working/review-checks/<phase-id>/<commit12>/` in the
  running checkout: gitignored, it outlives the worktree, and a reviewer without a shell can read
  it.
- **Which backlog.** The verification list is read from `dev`'s backlog, not from the commit, so a
  branch cannot weaken its own list. A test proves a weakened branch list is ignored.
- **Timeout.** A fixed 30-minute timeout per command, recorded as exit 124. The tool takes no
  options, so the limit is a constant.

Two scope changes to the claim, both owner-approved:
- **At the claim**, the deliverable `docs/08-governance/` was narrowed to the OPS-029 file, with
  OPS-029 reserved in `codes.yaml`. The whole directory path-conflicted with `phase-des-09`, which
  was active then.
- **During the build**, `docs/08-governance/codes.yaml` was added (`a91a8e3`). Governance requires
  the document's own change to remove its reservation.

Smaller choices made without asking, stated here:
- a gate check the list also names runs once;
- `uv sync --extra dev` runs as a listed `setup` entry;
- commands run with no stdin, so a prose entry starting with `grep … -` cannot hang;
- `VIRTUAL_ENV` is dropped so `uv run` uses the worktree's environment.

## Corrections

- **Worktree location.** The default worktree parent was first computed from the running checkout's
  parent. Started from a worktree, that nests under `d-system-worktrees/d-system-worktrees/`. I
  caught it before the real run and fixed it in its own commit: the parent now comes from the
  common git directory, with a test.
- **A stray code reservation.** At the claim I re-ran `--next-code operation`, which reserved
  OPS-030 in the machine-local store on top of my earlier OPS-029. I released OPS-030 at once and
  reported it to Session Manager.
- **A fixture built on a shell builtin.** `exit 3` is a bash builtin, not a program on `PATH`, so
  the owner-ruled rule correctly treats it as prose. The fixture now uses `sh -c 'exit 3'`, and an
  `is_command` case pins the builtin behaviour.

## Left undone

- **Not yet wired into the merge gate.** `GOV-017`'s merge-gate step 2 still describes the Session
  Manager's own re-run, and nothing yet routes reviews through this runner. That is the dispatch
  rule in `REQ-030` R03 and R04, in later phases of `PLAN-047`.
- **The completion edit.** It happens on dev after the owner approves the merge.
