---
schema_version: 1
id: doc-plugin-audit-remediation-requirements
code: REQ-035
title: Plugin audit remediation requirements — idea-log locking, contained configured paths, shell-safe option passing, reservation holders, amend from a file, and documented human controls
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-plugin]
depends_on: [doc-idea-realization-plugin-requirements, doc-idea-realization-plugin]
---

# Plugin audit remediation requirements

Observable statements for fixing the defects an external adversarial audit found in the
idea-realization plugin (`plugins/idea-realization/`), as confirmed by an independent validation of
that audit and ruled on by the owner. The plan that delivers them is
[PLAN-052](../01-plans/PLAN-052-plugin-audit-remediation.md).

## Observed problem and scope

On 2026-09-27 the owner had ChatGPT audit the plugin adversarially
([the audit report](../00-working/chatgpt-plugin-audit-report.md)), then had the Session Manager
dispatch a read-only reviewer to validate every finding against the code. The validation is
`_working/session-manager/reports/plugin-audit-validation.md` (gitignored). It reproduced four
findings by running the plugin in a scratch clone at `d8a635b`, judged the rest by reading, and
reclassified several. The plugin code is unchanged since then:
`git diff --stat d8a635b HEAD -- plugins/idea-realization` prints nothing on this branch.

The failures, each with the plugin line that shows it (paths below are relative to
`plugins/idea-realization/`):

1. **Concurrent idea writes corrupt the log.** `idea.add` (`scripts/idea.py:315-319`) folds the log,
   picks the next id and appends, with no lock. Twelve parallel `idea.py add` calls in the
   validation wrote two `created` events for `000008`, after which every read of the log failed with
   `error: 000008 was already created`. Every read-then-write operation (`change_status`, `revisit`,
   `amend`, `annotate`, `amend_annotation`, `link`, `retract_link`, `classify`) has the same race.
   `docs/multi-session.md:7` says "The plugin supplies no lock".
2. **Configured paths escape the repository.** `_to_path` (`scripts/paths.py:147-150`) returns an
   absolute value unchanged and joins `..` without a check, and `Config.path` and `Config.paths` use
   it for every key. The validation wrote the idea log outside the repository through an absolute
   path, a `..` path and a symlinked directory. The manifest describes every one of these options as
   "relative to the repository root". No test covers an escaping path. The validation cited
   `test/test_paths.py:67-70` as asserting one, but that test (`test_absolute_path_is_kept`) sets
   the path to `tmp_path / "elsewhere.jsonl"`, inside the root, so it is the control R04 keeps.
   `scripts/scaffold.py` resolves and writes each seed in turn, so a refusal on any key after the
   first would leave the earlier seeds on disk.
3. **`integration_branch` reaches git unvalidated.** `scripts/regression.py` passes the branch into
   `git show "<ref>:<path>"`. The validation ran `git show "--output=<dir>/out:backlog/backlog.yaml"`
   and git created the file.
4. **A saved option can inject shell commands.** Every skill passes options as
   `CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'`, and Claude Code substitutes the saved value
   into the skill text before the shell reads it. A value containing `'` ends the quoting; the
   validation ran a value of `ideas'$(touch injected)'` and the file `injected` appeared. There are
   158 such sites: 156 in eleven skills and 2 in `docs/tools.md`. `test/test_skills.py:20-23`
   checks only that no option is double-quoted.
5. **The partition check command expands its paths.** `scripts/idea_corpus.py:188-190` builds the
   command with double-quoted paths, which still expand `$(…)`, backticks and `$VAR`.
6. **Worktree placeholders are unquoted.** `skills/session-start/SKILL.md:128` reads
   `git worktree add -b agent/<phase-id> <worktree directory>/<phase-id> <integration branch>`; a
   worktree directory containing a space splits into extra arguments when filled in unquoted.
7. **Reservations expire while their work is still live.** `scripts/reservations.py:58` sets a
   14-day TTL and `prune` (`:120`) removes by age alone, so a phase open longer than that loses its
   code to the next allocation. The validation reproduced it with a linked worktree. The duplicate
   is caught at integration, and `docs/document-codes.md` describes the risk wrongly as expiry
   "before its document was written".
8. **`amend` has no `--file`.** `scripts/idea.py:643-646` gives `amend` only `--title` and `--body`,
   while the same script's docstring says "Prose never belongs in a shell argument", and
   `skills/idea/SKILL.md` shows `amend <id> --title "corrected title"` as its example.
9. **Two owner controls are stated only as prose.** `idea_corpus.py accept` marks a partition
   accepted with no authorization input, and the backlog check accepts a completed phase without
   checking review or integration. `docs/protocol.md` §7 says approval authenticity is a human
   responsibility but does not name these two.

Severity. The validation rated failures 2 and 4 major, rising to blocker only if a repository's
committed `.claude/settings.json` could set the plugin's options (idea `000477`). The Scout settled
that on 2026-09-27 (`_working/session-manager/scout/pluginconfigs-project-scope.md`, gitignored): it
cannot. Since Claude Code 2.1.207, `pluginConfigs` is read only from user settings, the `--settings`
flag and managed settings; the settings reference gives its scope as "User or managed" and the
changelog cites shell injection from cloned repositories. Both stay major. A committed `env` block
can still set `IDEA_REALIZATION_*` variables once the person trusts the repository, which redirects
paths (failure 2) but crosses no boundary the person has not already crossed, and cannot reach the
skill text (failure 4).

Scope: the plugin only. This repository's own `src/`, `tools/` and governance documents do not
change, except that the repository's `dev` extra gains the lock library, because the plugin's test
suite runs in this repository's environment.

## Observable requirements and verification

"Fails at the baseline" below means the test is run against the plugin as it stood at `d8a635b`
and fails because of the behaviour the row describes (an assertion failure or a wrong exit code),
not only because it imports a name that does not exist yet.

| Id | Requirement | Verification |
|---|---|---|
| R01 | Every mutating operation of the idea writer (`add`, `status`, `revisit`, `amend`, `annotate`, `amend-annotation`, `link`, `retract-link`, `classify`) holds an exclusive lock across its whole read, validate and append, so concurrent writers on one machine never write events that fail to fold together. | A test runs two `add` calls in threads with `fold` held at a two-party barrier: afterwards the log folds and holds ids `000001` and `000002`. It fails at the baseline. Twenty `idea.py add` subprocesses run at once, then `idea.py list` exits 0 and lists 20 distinct ids. Two concurrent `status <id> reviewing` calls: exactly one succeeds, the other fails with the illegal-transition error, and the log still folds. |
| R02 | The lock is the `filelock` library, pinned to one exact version in the inline dependency header of every script that imports it and in this repository's `dev` extra. The lock file is in `<git common directory>/idea-realization/`, so every worktree of a repository shares it and it needs no ignore rule. A writer that cannot take the lock within its timeout exits non-zero, names the lock file and appends nothing. | A test resolves the lock path from the primary checkout and from a linked worktree and reads the same path, under `git rev-parse --git-common-dir`. With the lock held by the test, `idea.py add` exits non-zero naming the lock file and the log is byte-identical. A process killed with `SIGKILL` while holding the lock does not block the next `add`. These R02 tests check a lock that does not exist at the baseline, so none of them has a baseline run. The plugin's portability test allows `filelock` and fails if two headers pin different versions. |
| R03 | The idea writer, run anywhere other than the integration branch in the primary checkout, writes a warning to stderr that names the current branch or checkout and says ideas are recorded only on the integration branch in the primary checkout, then writes the event. `docs/protocol.md` and `docs/multi-session.md` state that rule. | In a linked worktree, `idea.py add` prints the warning and the event is in that worktree's log. In the primary checkout on another branch, the warning prints. In the primary checkout on the integration branch, no warning prints (control). A grep of both documents finds the rule. |
| R04 | Every configured path key and every entry of a list key resolves, after following symlinks and collapsing `..`, inside the root it is taken from and contains no `.git` component. An absolute path that resolves inside the root is accepted. Otherwise the script exits 2 with a message naming the key, and writes nothing: the scaffold resolves every key it will write before its first write. | Tests for `Config.path("ideas_path")` with an absolute path outside the root, with `../x.jsonl`, and with `ideas/link/x.jsonl` where `ideas/link` points outside: each is refused, and each fails at the baseline. An entry of `triage_search` and of `exempt_files` that escapes is refused. An absolute path inside the root is kept (control; passes before and after). `idea.py add --ideas-path ../x.jsonl` exits 2 and creates no file. `scaffold.py --ideas-path <absolute path outside>` exits 2 and writes nothing, including no install-state record and no `.gitignore` line. `scaffold.py --docs-root ../outside` in an empty repository exits 2 and leaves the repository empty, which also fails at the baseline, because `ideas_path` is the scaffold's first seed and `docs_root` a later one. |
| R05 | `worktree_dir` must resolve outside the primary checkout; a value inside it is refused with exit 2. The manifest's description of `worktree_dir` says it must be outside the repository, not "relative to the repository root". | `worktree_dir` = `wt` is refused, which fails at the baseline. The manifest default is accepted (control). A test reads the manifest's `worktree_dir` description and finds no "relative to the repository root", which also fails at the baseline. |
| R06 | `integration_branch` must not start with `-` and must pass `git check-ref-format --branch`, or the script exits 2. Every git call the plugin makes with a ref argument puts `--end-of-options` before it. | `integration_branch` = `--output=<tmp>/x` is refused with exit 2 and no file appears in `<tmp>`, which fails at the baseline. `dev` and `main` are accepted (control). The existing regression-check tests pass unchanged. |
| R07 | `doctor` reports every invalid configured key with its reason and exits 1, instead of stopping at the first. | With two keys set to escaping paths, `doctor` names both, exits 1 and prints no traceback. With valid keys, its output is unchanged (control). |
| R08 | Every skill passes each plugin option to its script through a quoted heredoc (`<<'IR_OPTION'`), with `${user_config.<key>}` alone on its own line inside it, and no option is substituted inside single or double quotes. | A static test finds no `'${user_config.` in any skill and every `${user_config.` alone on a line inside an `IR_OPTION` heredoc; it fails at the baseline on all eleven skills that pass options. An execution test renders every bash fence in every skill with the value `a'$(touch P)'"$(touch Q)"`, with `uv run` replaced by `printenv`: neither `P` nor `Q` exists afterwards and the printed value is byte-identical. An unsubstituted `${user_config.ideas_path}` still reaches the script literally and counts as unset (control). |
| R09 | The heredoc form has been run once in a live Claude Code session, and the result is recorded. | The session record quotes, for a saved `ideas_path` of `ideas/it's.jsonl` and for the hostile value in R08, the rendered command, the value the script received, and whether an allow rule that permitted the single-quoted form still permits the heredoc form without a prompt. If it does not, the phase stops before READY and reports to the owner. |
| R10 | The partition check command quotes each argument with `shlex.quote`. | With a root path containing `$(touch P)`, the printed command run through `bash -c` creates no `P` and passes the path through verbatim. This fails at the baseline. With a plain path, the command's behaviour is unchanged (control). |
| R11 | In every shell fence of the plugin's skills and documents, `<worktree directory>` and `<integration branch>` appear inside double quotes, and the text tells the reader to keep the quotes when filling them in. | A test finds every bash-fence occurrence of either placeholder inside double quotes. It fails at the baseline on `skills/session-start/SKILL.md:128`. |
| R12 | A code reservation records its branch and its worktree as separate fields. `prune` keeps a reservation whose worktree is still listed by `git worktree list` on that branch, whatever its age. A reservation without those fields keeps the age rule. | A test reserves from a linked worktree and prunes at the present time plus 15 days: the code is still held, which fails at the baseline. After `git worktree remove`, the same prune removes it. A reservation whose worktree is still listed but now on another branch is pruned (must not be kept). A reservation written without the new fields is pruned after 15 days (control). |
| R13 | `docs/document-codes.md` states that a reservation protects a code until its document merges, not until it is written. | A grep finds the corrected sentence, and the phrase "expired before its document was written" is absent. |
| R14 | `idea.py amend` accepts `--file`, with the same title and body split as `add --file`; `--file` together with `--title` or `--body` is refused. A field equal to its current value is not recorded, and an amendment that changes nothing is refused. The idea skill's amend example uses `--file`. | An amend from a file whose body contains `'`, `"` and `$(touch P)` records the body byte-identical and creates no `P`. `amend --file f --title t` exits non-zero and appends nothing. An amend from a file whose title equals the current title records only the body; one whose title and body both equal the current values exits non-zero and appends nothing. A grep of `skills/idea/SKILL.md` finds no `amend` example with a quoted title or body. |
| R15 | `docs/protocol.md` §7 names partition acceptance and phase completion as human controls that no script verifies. The plugin README recommends Claude Code `ask` permission rules for the partition `accept` command and for edits to the configured backlog file, which is how a phase is marked complete. `skills/partition-ideas/SKILL.md` says that `accept` does not check for the owner's ruling. | A test reads §7's table and finds a row for each control. A grep of the README finds both recommended rules, and a grep of the partition skill finds the sentence. |
| R16 | Every row above is fixed by a phase whose new or changed tests were first recorded failing at the baseline, where the row says so. The plugin suite, 497 tests at the baseline, loses no test except the one a fix replaces: `test_no_option_is_double_quoted`. `test_absolute_path_is_kept` stays, as R04's control. | Each phase's session record quotes its failing baseline run and its passing run. Each phase's `pytest` count is the previous count plus its new tests, less a replaced test when it replaces one. |

## What each requirement is not

- R01 and R02 do not stop two worktrees or two machines from each adding `00000N` and merging.
  Ideas are recorded only on the integration branch in the primary checkout (R03, owner ruling D3),
  and a duplicate that still happens is detected when the log fails to fold.
- R02 does not add Windows CI. `filelock` handles Windows, and no Windows run of it exists
  (idea `000484`).
- R03 does not refuse a write. It warns, because the owner ruled that the writer warns elsewhere.
- R04 does not refuse an absolute path. The partition sweep's check command passes absolute paths
  inside the root, and those must keep working.
- R04 is a breaking change for anyone who configured a path outside the repository on purpose. The
  README says so.
- R07 does not add the full per-key report of resolved locations proposed in idea `000483`. It
  reports only invalid keys.
- R08 does not close a value that contains a newline followed by `IR_OPTION`. A single-line option
  set through the settings interface cannot contain one.
- R09 does not re-test whether a repository's committed `.claude/settings.json` can set plugin
  options. The Scout settled that it cannot (idea `000477`; see Severity above).
- R12 does not protect a reservation across machines. Cross-machine duplicates remain caught at
  integration.
- R15 does not add a check. The merged-branch and review-section checks are later work
  (owner ruling D4; idea `000488`).
- None of these rows changes the test that depends on the shape of the git remote URL
  (idea `000481`). The plugin suite runs in worktrees of this repository, whose remote passes it.

## Accepted decisions

Owner, 2026-09-27, in the Session Manager session, on the validation's five open design questions:

- **D1.** Configured paths are contained inside the repository; absolute paths inside it still
  work; `worktree_dir` must resolve outside the primary checkout.
- **D2.** The idea-log lock is the `filelock` library, pinned through the scripts' inline
  dependency header, using the OS lock on Linux and macOS (`fcntl`) and Windows (`msvcrt`) on a
  separate lock file in the shared git common directory, so no `.gitignore` entry is needed.
  Recorded in [ADR-025](../04-decisions/ADR-025-plugin-idea-log-lock.md).
- **D3.** Ideas are recorded only on the integration branch in the primary checkout; the writer
  warns elsewhere.
- **D4.** Partition acceptance and phase completion are documented as human controls in
  `protocol.md` §7, with `ask` permission rules recommended in the README now; the merged-branch
  and review-section checks come later.
- **D5.** Options are passed through a quoted heredoc per option.

Owner, 2026-09-27, in the planning session, on the plan's open questions:

- `amend --file` omits fields equal to their current value, and refuses an amendment that changes
  nothing (R14).
- The README's phase-completion `ask` rule targets Edit of the configured backlog file (R15).
