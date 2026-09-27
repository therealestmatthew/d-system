# Adversarial audit of `plugins/idea-realization`

Audit scope: `plugins/idea-realization/` only. The repository was not modified while performing
the audit. Reproductions ran only against a copy under `/tmp` using Python 3.12.

## Blocker — Configured paths can write outside the target repository

Files: `scripts/paths.py:147-150`, `scripts/scaffold.py:170-177`, `scripts/idea.py:304-309`,
`docs/protocol.md:133`, `test/test_paths.py:67-70`

Scenario: Set `ideas_path` to an absolute path outside the repository, then run
`scaffold --feature ideas` or `idea.py add`. The scripts create and append to that external log.
This was reproduced with `ideas_path=/tmp/.../outside/ideas.jsonl`; both scaffold and add wrote
there.

Evidence:

> `return path if path.is_absolute() else (root / path)`

> `with target.open("xb") as handle:`

> `with log.open("a", encoding="utf-8") as handle:`

> `Declared paths are repository-relative, never escape the repository`

> `assert config.path("ideas_path") == other`

Reproduced by execution.

Suggested fix: Centrally reject absolute paths, `..` traversal, and symlink escapes for every
repository-content option. Treat `worktree_dir` as a separately validated exception with a
constrained allowed location.

## Blocker — A saved plugin option can inject shell commands

Files: `scripts/paths.py:14-18`, `skills/idea-triage/SKILL.md:18-20`

Scenario: Save an `ideas_path` containing a single quote and shell substitution, such as
`ideas'$(touch injected)'`. Substitution into the documented single-quoted assignment terminates
the quote and executes the command before Python runs. The equivalent rendered shell line was
reproduced in scratch; it created `injected`.

Evidence:

> `CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'`

> `single-quoted because the shell rejects the unsubstituted text inside double quotes.`

> `CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \\`

Reproduced by execution.

Suggested fix: Do not interpolate option values into shell source. Pass configuration through a
non-shell channel, or use a trusted wrapper that supplies environment values without reparsing them
as shell syntax.

## Blocker — Concurrent idea capture permanently corrupts the append-only log

Files: `scripts/idea.py:304-319`

Scenario: Two sessions run `idea.py add` against the same log concurrently. Each folds the same old
state, calculates `000001`, then appends a separate `created` event. The fold thereafter rejects
the log, with no sanctioned repair path. Twelve concurrent scratch adds produced two writes, both
for `000001`, and later reads failed with “a second created event follows it.”

Evidence:

> `state = fold(load_events(log))`

> `event = build_created(_next_id(state), title.strip(), body.strip(), _now(), new_eid())`

> `with log.open("a", encoding="utf-8") as handle:`

Reproduced by execution.

Suggested fix: Hold an advisory lock spanning read, ID allocation, validation, and append;
alternatively use collision-resistant IDs and make the ordering/replay rules tolerate concurrent
creation.

## Major — Partition acceptance can be invoked without the owner’s ruling

Files: `skills/partition-ideas/SKILL.md:291-307`, `scripts/idea_corpus.py:586-607`

Scenario: A coordinator or user invokes `idea_corpus.py accept` before Gate 3. A syntactically valid
staged pair is copied into the tracked partitions directory and marked `accepted`; the script
receives no approval evidence and performs no authorization check.

Evidence:

> `Only on the owner's explicit acceptance:`

> `Run only on the owner's explicit acceptance.`

> `shutil.copyfile(markdown_path, target_md)`

> `record["state"] = "accepted"`

Found by reading.

Suggested fix: Require an explicit, non-forgeable approval artifact or capability passed only after
the owner gate; otherwise rename the operation and documentation so it does not claim enforcement.

## Major — The backlog check accepts completion without verification, review, or integration

Files: `docs/backlog-protocol.md:159-172`, `scripts/backlog.py:223-245`

Scenario: Edit a phase to `complete`, reference any valid session document, list existing files as
evidence, and provide a non-empty `result`. The check accepts it even if no verification command
ran, no independent review exists, and no approved integration occurred.

Evidence:

> `only when all three conditions hold:`

> `every verification command ran green, and its real output is in the session record;`

> `an independent adversarial review`

> `the branch is integrated onto the integration branch with the owner's approval.`

> `if not item.get("session") or not item.get("completion_evidence"):`

> `if not item.get("result", "").strip():`

Found by reading.

Suggested fix: Require structured, machine-checkable session metadata for verification and review,
plus integration commit/ref evidence. For approval, either validate a recorded authorization artifact
or explicitly state it remains solely a human control.

## Major — Document-code reservations can be reissued while the original work is still active

Files: `scripts/reservations.py:55-58`, `scripts/reservations.py:120-132`,
`scripts/codes.py:364-375`, `docs/document-codes.md:100-104`

Scenario: A valid branch remains active or blocked for more than 14 days after receiving a code but
before merging its document. A later allocation prunes its reservation and receives the same code.
The collision is only discovered during later integration.

Evidence:

> `TTL_SECONDS = 14 * 24 * 60 * 60`

> `Drop expired reservations`

> `reservations.prune(root)`

> `Expiry after 14 days is the only automatic release.`

> `A duplicate code arises ... from a pre-merge reservation that expired before its document was written.`

Found by reading.

Suggested fix: Do not expire reservations that identify a live branch/worktree or active claim;
require explicit release or a verified abandoned-claim workflow.

## Major — Worktree creation fails for configured paths containing spaces

Files: `skills/session-start/SKILL.md:123-134`

Scenario: Configure `worktree_dir` to a valid directory containing spaces. The instructed
`git worktree add` command substitutes the path unquoted, splitting it into multiple shell arguments
and failing or using the wrong argument positions.

Evidence:

> `git worktree add -b agent/<phase-id> <worktree directory>/<phase-id> <integration branch>`

> `Use those exact values everywhere below`

Found by reading.

Suggested fix: Quote every substituted shell argument, including branch, worktree path, and
integration branch.

## Minor — The path test codifies behavior that violates the containment rule

Files: `test/test_paths.py:67-70`, `docs/protocol.md:133`

Scenario: A regression test passes specifically when an absolute path escapes the repository, so the
suite preserves the containment defect rather than detecting it.

Evidence:

> `def test_absolute_path_is_kept`

> `assert config.path("ideas_path") == other`

> `Declared paths are repository-relative, never escape the repository`

Found by reading.

Suggested fix: Replace this test with rejection tests for absolute paths, traversal, and symlink
escapes across all configured repository paths.

Scaffolding: inspected repeated-run, drift-record, and partial-write handling; no additional finding.

Backlog claims, active-claim limits, dependency cycles, and stale-claim reporting: inspected; no
additional finding beyond the completion-gate bypass.

## Could not verify

- Full pytest suite: Python 3.12 and the required YAML/schema packages were available, but `pytest`
  was unavailable and could not be installed from cache with network disabled.
- Actual Claude plugin loading and the runtime representation of `multiple: true` user options:
  requires a Claude CLI/plugin runtime.
- Cross-machine code-reservation behavior: requires independent clones or hosts.
