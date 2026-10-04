---
schema_version: 1
id: doc-plugin-audit-remediation
code: PLAN-052
title: Plugin audit remediation — six phases fixing the confirmed findings of the idea-realization plugin audit
kind: plan
status: approved
owner: repository-owner
created: '2026-09-27'
updated: '2026-10-04'
systems: [sys-plugin]
depends_on: [doc-plugin-audit-remediation-requirements, doc-adr-plugin-idea-log-lock, doc-idea-realization-plugin, doc-plan-quality-standard, doc-three-altitude-review-procedure]
---

# Plugin audit remediation

Delivers [REQ-035](../06-requirements/REQ-035-plugin-audit-remediation.md). The lock mechanism is
recorded in [ADR-025](../04-decisions/ADR-025-plugin-idea-log-lock.md). Review record:
[`2026-09-27-plan-052`](../08-governance/reviews/2026-09-27-plan-052.json), dispositioned: ten
findings, all fixed by the planner, none escalated.

## Context and scope

On 2026-09-27 the owner had ChatGPT audit the idea-realization plugin (`plugins/idea-realization/`,
built under [PLAN-048](PLAN-048-idea-realization-plugin/PLAN-048-overview.md);
[the audit report](../00-working/chatgpt-plugin-audit-report.md)) and had the Session
Manager dispatch a read-only reviewer to validate the audit against the code. The validation is
`_working/session-manager/reports/plugin-audit-validation.md`, gitignored. It reproduced four
findings in a scratch clone at `d8a635b`, including 12 parallel idea adds that left the log
unreadable, and recorded the plugin suite baseline there: `497 passed`. The owner ruled on its five
design questions the same day; `REQ-035` records the rulings as D1 to D5.

The validation names its findings with labels. This plan uses the same labels so the phases can be
traced back to the report. Each one is defined here:

| Label | Finding | Validation's classification | REQ-035 rows |
|---|---|---|---|
| F1 | Configured paths write outside the repository | Confirmed, major; stays major (see below) | R04, R05, R07 |
| F2 | A saved option can inject shell commands | Confirmed mechanism, major; stays major (see below) | R08, R09 |
| F3 | Concurrent idea capture corrupts the log | Confirmed, blocker | R01, R02, R03 |
| F4 | Partition acceptance runs without the owner's ruling | Partially confirmed, minor | R15 |
| F5 | The backlog check accepts completion without review or integration | Not a defect; documentation only | R15 |
| F6 | Code reservations are reissued while their work is active | Partially confirmed, minor | R12, R13 |
| F7 | Worktree placeholders break on paths with spaces | Partially confirmed, minor | R11 |
| F8 | A test asserts the escaping behaviour | Confirmed, minor. Wrong: see below | R04 |
| a | The partition check command double-quotes its paths | Found in passing | R10 |
| b | `integration_branch` can inject git options | Found in passing, reproduced | R06 |
| d | `document-codes.md` states the reservation risk wrongly | Found in passing | R13 |
| e | `amend` has no `--file` (idea `000482`) | Found in passing | R14 |
| f | The scaffold writes a `.gitignore` line for a path outside the root | Found in passing; closed by F1 | R04 |

Found-in-passing item c, a test that depends on the shape of the git remote URL, is idea `000481`
and is out of scope (see below).

Two of the validation's statements do not hold, and the plan follows the corrected version:

- **F8 is not a defect.** The validation cites `test/test_paths.py:67-70` as asserting that an
  absolute path outside the root is accepted. That test, `test_absolute_path_is_kept`, sets the path
  to `tmp_path / "elsewhere.jsonl"`, which is inside the root `tmp_path`. It is the control R04
  keeps, and no test is deleted. The plan-review adversary found this (review record F01).
- **F1 and F2 do not rise to blocker.** The validation left that open on whether a committed
  `.claude/settings.json` can set plugin options (idea `000477`). The Scout settled on 2026-09-27
  that it cannot: since Claude Code 2.1.207, `pluginConfigs` is read only from user, `--settings`
  and managed settings. A committed `env` block can set `IDEA_REALIZATION_*` after trust, which
  redirects paths (F1) but crosses no boundary the person has not already crossed and cannot reach
  the skill text (F2). `REQ-035`'s Severity paragraph gives the sources.

The plugin has not changed since the audited commit: `git diff --stat d8a635b HEAD --
plugins/idea-realization` prints nothing on this branch, cut from `dev` at `270e688`.

## Decisions

The owner ruled D1 to D5 on 2026-09-27 in the Session Manager session. D6 to D11 are the planner's,
open to the adversary and to G3.

- **D1. Configured paths are contained; `worktree_dir` must be outside.** Ruled. Rejected: an
  explicit `--allow-outside` flag, which keeps an escape route every script must honour and test.
  Also rejected: keeping today's behaviour and changing the manifest wording, which leaves an
  absolute path copied from another clone writing silently into that clone. Cost of the chosen
  option: anyone who deliberately configured an outside path gets exit 2 after upgrading.
- **D2. `filelock`, pinned, lock file in the git common directory.** Ruled. The alternatives and
  their costs are in `ADR-025`.
- **D3. Ideas are recorded only on the integration branch in the primary checkout; the writer warns
  elsewhere.** Ruled. Rejected: collision-resistant ids, which break the six-digit id format that
  the schemas, the corpus parser (`scripts/idea_corpus.py`, the `^## (\d{6}) — ` pattern) and the
  partition packs rely on. Also rejected: detection at merge alone, the previous state, which the
  audit shows is not enough. Cost: a warning, not a refusal, so the rule still depends on the
  session following it.
- **D4. Partition acceptance and phase completion are documented as human controls; checks come
  later.** Ruled. Rejected: recorded-ruling fields in the schemas. A script run by the same agent
  cannot verify an approval that agent could not forge, so the field would record a claim rather
  than an approval. Cost: nothing enforces the two controls until the later checks
  (idea `000488`).
- **D5. A quoted heredoc per option.** Ruled. Rejected: an options file written with the Write tool
  and read with `--options-file`, which adds a file-writing step to every skill invocation. Also
  rejected: single quotes plus a `doctor` warning, which cannot prevent execution because the shell
  parses the command before any script runs. Cost: every command grows by about four lines (59
  sites in `partition-ideas` alone), and Bash permission matching may change (see D11).
- **D6. A new requirement, not rows added to `REQ-031`.** `REQ-031` R01 to R25 are delivered and
  verified by nine completed phases. Rows added there would make it read as partly undelivered, and
  would mix the audit's evidence into a requirement whose problem section is about packaging.
  `REQ-031` gets one dated note under its accepted decisions: R03's dependency list now includes
  `filelock`, per `REQ-035` R02. Rejected: amending `REQ-031` in place. Cost of the chosen option:
  two requirement documents describe the plugin, linked in both directions.
- **D7. A new track, `phase-plfx-*`, under this plan.** Rejected: continuing the `phase-plug-*` track past `phase-plug-09`,
  which would put phases of a different plan under a track row that points at `PLAN-048`. Cost: one
  more row in the backlog README.
- **D8. The phases run in the validation's dependency order, one at a time.** The order, as the
  Session Manager set it: F3, then F1 with b and f (F8 turned out not to be a defect; see Context), then F2 with F7 and a, then F6 with d, then
  e, then F4 and F5. The chain is also forced by files. `docs/tools.md` is generated from script
  docstrings and changes in five of the six phases, and `docs/protocol.md` changes in four.
  Rejected: running F6 and e beside F1, which would collide on `docs/tools.md` and on `idea.py`.
- **D9. The F3 lock lands before path containment.** The validation suggested landing F1 first
  because the lock would be taken on the validated log path. Under D2 the lock is in the git common
  directory, not on the log path, so it does not depend on F1. The blocker lands first. Cost of the
  rejected order: the only blocker-severity defect would stay live for one more phase, for no
  remaining technical reason.
- **D10. How "failing at the baseline" is shown.** Each phase writes its tests first. It adds a
  detached worktree at `d8a635b` beside its own (`git worktree add --detach
  ../d-system-worktrees/<phase-id>-baseline d8a635b`), copies the new and changed test files in,
  runs them there, and quotes the failures in its session record. It then removes that worktree. A
  test that fails only on an import error does not count. Where a new name is needed, the failing
  check is made at the command-line level (an exit code, a file that appears) so the behaviour is
  what fails. Rejected: running the tests at the phase's own branch point. For phases after the
  first, that point already contains earlier fixes, so it would not show the audited behaviour the
  Session Manager asked to see.
- **D11. The builder runs the live-session check for F2 headless.** The plugin-skeleton session
  (`SESS-2026-09-25-02`) settled option substitution with `claude --plugin-dir` and `--settings`
  carrying `pluginConfigs`, in a scratch repository. `phase-plfx-03` repeats that first, on the idea skill alone, before converting the
  other ten, so a stop costs one skill's work: a scratch repository, a settings file with an allow rule matching the single-quoted form, one run with
  `ideas/it's.jsonl` and one with the hostile value. Rejected: an owner-run check, because the owner
  works from a phone and the check needs no owner judgment until it finds a difference. If the
  heredoc form is prompted or denied where the single-quoted form was allowed, the phase stops
  before READY and puts the choice to the owner.

## Implementation phases

| Phase | Findings | Delivers | Depends on |
|---|---|---|---|
| `phase-plfx-01` | F3 | The lock around every idea-writer mutation (`ADR-025`), the integration-branch warning, the `filelock` pin in the headers and in the `dev` extra, and the corrected lock statements in `docs/multi-session.md` and `docs/protocol.md` | — |
| `phase-plfx-02` | F1, b, f | Central validation in `scripts/paths.py`: containment, `worktree_dir` outside the primary checkout (and its manifest description corrected), `integration_branch` format, `PathError` handled as exit 2 in every script with the scaffold validating every key before its first write, `--end-of-options` on ref arguments, and `doctor` reporting every invalid key | `phase-plfx-01` |
| `phase-plfx-03` | F2, F7, a | Heredoc option passing across the eleven skills, quoted path placeholders, `shlex.quote` in the partition check command, the static and execution tests, and the live-session check | `phase-plfx-02` |
| `phase-plfx-04` | F6, d | Reservation payloads with branch and worktree fields, `prune` keeping reservations of live worktrees, and the corrected `document-codes.md` wording | `phase-plfx-03` |
| `phase-plfx-05` | e | `idea.py amend --file` and the idea skill's example | `phase-plfx-04` |
| `phase-plfx-06` | F4, F5 | Partition acceptance and phase completion named as human controls in `protocol.md` §7, the README's `ask` permission rules, and the partition skill's sentence | `phase-plfx-05` |

Each phase's scope, acceptance, verification and deliverables are in `docs/09-backlog/backlog.yaml`.
All six are queued and none is in `next_up`. The owner places them there.

## Requirement coverage

| Requirement | Phase |
|---|---|
| R01, R02, R03 | `phase-plfx-01` |
| R04, R05, R06, R07 | `phase-plfx-02` |
| R08, R09, R10, R11 | `phase-plfx-03` |
| R12, R13 | `phase-plfx-04` |
| R14 | `phase-plfx-05` |
| R15 | `phase-plfx-06` |
| R16 | Every phase: each records its baseline failures and its test count |

Every row maps to a phase and every phase to at least one row.

## Execution order and real concurrency

The six phases form one chain, and at most one runs at a time. The chain is forced by files, not
only by the order the Session Manager set:

- `plugins/idea-realization/docs/tools.md` is generated from script docstrings. Phases 01
  (`idea.py`), 02 (`paths.py` and every script), 03 (`paths.py` docstring), 04 (`reservations.py`)
  and 05 (`idea.py`) all change it.
- `plugins/idea-realization/docs/protocol.md` changes in 01 (idea rule), 02 (§7 containment row),
  03 (quoted placeholders) and 06 (§7 human controls).
- `scripts/idea.py` changes in 01, 02 and 05, and `scripts/paths.py` in 02 and 03.

Each phase declares these paths in `deliverables`, so the governance check refuses a second claim
while one is active. None of the six collides with a phase outside this plan today. No other queued
phase declares a `plugins/idea-realization/` path or any `sys-plugin-*` system, and `phase-plfx-01`
is the only one that touches `pyproject.toml` and `uv.lock`.

## Acceptance and verification

Common to every phase, in addition to the phase's own acceptance in the backlog:

- The new and changed tests are written first and recorded failing at `d8a635b` (D10), for the
  reason the requirement row gives.
- `cd plugins/idea-realization && uv run pytest` passes. The count equals the previous phase's
  count plus this phase's new tests, less any test the phase replaces. The chain starts from 497.
- `claude plugin validate plugins/idea-realization --strict` exits 0.
- `uv run python tools/check_no_private_content.py`, run with the changes staged, reports OK.
- After rebasing onto `dev`: `uv run python -m src.governance`, `uv run pytest`,
  `uv run ruff check src/ test/` and `uv run mypy src/` are all clean.
- An independent review from a validator or adversary agent type finds no unresolved blocker or
  major before READY.
- Where a docstring changed, `docs/tools.md` is regenerated with the plugin's
  `generate_tool_docs.py`, and `test_generate_tool_docs.py` passes.

## Linked ideas

The owner's §7 ideas from the validation, 000477 (anchor) to 000488, and where each stands against
this plan. No status is moved by this plan.

| Idea | Relation to this plan |
|---|---|
| `000477` (whether committed project settings can set plugin options) | Settled by the Scout: they cannot. F1 and F2 stay major. It changed no fix |
| `000478` (shell-rendering harness for skill bash fences) | Delivered in part by `phase-plfx-03`'s execution test (R08). The harness as a reusable tool is not |
| `000479` (concurrency tests for every plugin writer) | Delivered for the idea log by `phase-plfx-01`. Catalog, reservations and backlog stay open |
| `000480` (repair path for a malformed idea-log tail) | Out of scope. The lock prevents the tail; repairing one already written is separate work |
| `000481` (remote-URL-independent source-reference test) | Out of scope. Worktrees of this repository pass the test |
| `000482` (`amend --file`) | Delivered by `phase-plfx-05` (R14) |
| `000483` (doctor report of every configured path) | Delivered in part by `phase-plfx-02` (R07, invalid keys only) |
| `000484` (Windows CI for the plugin scripts) | Out of scope. `ADR-025` records the untested Windows path |
| `000485` (audit-rubric note on "declared paths") | Delivered in part by `phase-plfx-02`'s §7 row for configured paths, which sits beside the declared-paths row |
| `000486` (structured reservation holder fields) | Delivered in part by `phase-plfx-04` (R12). Listing stale reservations by branch is not |
| `000487` (permission rules for owner-gated commands) | Delivered for partition accept and phase completion by `phase-plfx-06` (R15) |
| `000488` (check that a completed phase's branch is merged) | Out of scope. The owner ruled it a later check (D4) |

## Out of scope

- The Windows lock path in CI, because no Windows runner exists here (`000484`).
- Cross-machine or cross-branch idea-id collisions. D3 makes them a rule with a warning, and fold
  still detects them.
- The merged-branch and review-section checks for phase completion, and any recorded-ruling field
  for partition acceptance. The owner ruled these later (D4).
- This repository's own idea writer, `tools/append_idea.py`. The audit covered only the plugin, and
  this repository's writes are serialized by the Session Manager's turn protocol.
- The remote-URL-dependent test (`000481`) and the malformed-tail repair path (`000480`). Neither
  blocks a fix here.
- Any change to `AGENTS.md` or `CLAUDE.md`.

## Open questions

1. **What does `amend --file` do with a title that has not changed?** Answered by the owner on
   2026-09-27, in this planning session: omit unchanged fields. `phase-plfx-05` records only the
   fields that differ from the current value, and refuses the amendment if none does, matching the
   existing "must correct at least one" rule (`scripts/idea.py:398`). REQ-035 R14 carries it.
2. **What does the README's phase-completion rule target?** Answered by the owner on 2026-09-27, in
   this planning session: edits to the backlog file. The README recommends an `ask` rule on Edit of
   the configured backlog path, because it applies however the edit is made. `phase-plfx-06` still
   checks the exact rule syntax against the current Claude Code documentation before writing it.
3. **Does the heredoc form change Bash permission matching?** Open. `phase-plfx-03` answers this with the
   live check (D11). If it does, the owner chooses between accepting the prompts and a different
   passing form, before that phase merges.
