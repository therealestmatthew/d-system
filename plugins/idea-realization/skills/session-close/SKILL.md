---
name: session-close
description: Finalize the session record, run an independent adversarial review of the branch against the phase's acceptance, and mark the phase complete only when verification ran green, the review found no unresolved discrepancy, and the branch is integrated with the owner's approval. Use when a phase's work is finished and ready to hand off or close.
---

# Close the session

Finishes the session record the `checkpoint` skill maintains, adds what a checkpoint skips, and is
the **only** procedure that may mark a phase complete.

## When a phase may be marked complete

An agent never completes a phase on its own judgement that the work looks finished. A coordinator
— the owner, or an agent running this skill — may set a phase to `status: complete` when, and only
when, **all three** of these hold:

1. **Verification ran green.** Every command in the phase's `verification` list ran, and its real
   output is recorded in the session record.
2. **An independent review found no unresolved discrepancy.** An adversarial review of the
   branch's diff against the phase's `acceptance` ran in a separate agent that did not share this
   session's context, and every finding is fixed or explicitly reported as accepted by the owner.
3. **The branch is integrated with the owner's approval.** The owner approved merging this
   branch into the integration branch, for this phase, and the merge happened.

Together these substitute for the owner's synchronous judgement, so none is optional. **Where any
one is unmet, the phase stays `active`** (or `queued`, if handed off unfinished): say plainly that
the session looks done, run `checkpoint` to record where it stands, and stop. The review in step 3
is never skipped, and the completion step exists nowhere else.

## Values

Commands carry the person's saved options; an option never saved appears as its `${user_config.…}`
text and the scripts use the documented default. Read the resolved values once:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_WORKTREE_DIR='${user_config.worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"
```

Use `backlog_path` as **the backlog** and `integration_branch` as **the integration branch**, exactly
as printed.

## 1. Identify the phase and run the checkpoint first

Use the named phase, or the session's one active phase; ask if more than one is plausible. With no
active phase the session is unclaimed: this skill still runs, judges the record's self-declared
conditions, and completes nothing. Never invent or retroactively claim a phase, and never re-run
this against a phase that already closed earlier in the conversation.

Run every step of the `checkpoint` skill now, against the current state, so `## Phase` through
`## Unresolved` reflect the repository as it stands at close.

## 2. Name the diff to review

- Work on `agent/<phase-id>` (or `agent/<slug>` for unclaimed work): the range is
  `<integration branch>...HEAD`.
- Work made directly on the integration branch: find the commit that set this phase active
  (`git log --oneline -- <the backlog>`) and use `<that commit>..HEAD`.

## 3. Run an independent review

Launch a **fresh agent that does not inherit this session's context** — never a fork of this
session, which carries its conclusions and defeats the point. Prefer a dedicated reviewer or
adversary agent type when the repository defines one. Give it, in its prompt:

- the phase id with its `scope`, `acceptance` and `verification` lists pasted in (for an unclaimed
  session: the owner's instruction as given, the self-declared conditions, and a plain statement
  that the session being reviewed wrote them, so the reviewer also judges whether they are a fair
  reading of the instruction);
- the exact range from step 2, with instructions to run `git diff` and `git log` on it itself;
- the session record's path and content;
- its job: decide independently, from the diff and its own run of the verification commands,
  whether each condition holds — not whether the record says so — and flag anything the record
  claims that the diff or a rerun does not support. "No discrepancies found" is a valid finding.

Wait for its report. Never paraphrase away an uncomfortable finding, and never proceed as if the
review passed before it returns.

## 4. Record the review verbatim

Add `## Review` after the sections `checkpoint` maintains, with the reviewer's findings condition
by condition, quoted rather than summarised, and each finding's disposition: fixed (with the
change), or accepted (with who accepted it).

## 5. Record what a checkpoint skips

- `## Decisions` — what was decided and why, including where the owner overrode a recommendation.
- `## Corrections` — mistakes made and fixed during the session; omit only if there were none.
- `## Left undone` — what remains and why it was left, for whoever picks it up next.

Write these as narrative someone could read in six months, not as a restatement of the scope.

## 6. Hand off for integration

Rebase onto the integration branch, re-run the check and the repository's tests, and ask the owner
whether to integrate, as the `session-start` skill's hand-off describes. Until the owner approves and
the merge happens, condition 3 is unmet and the phase stays `active`.

## 7. Decide completion — the only step that may write `status: complete`

After the owner-approved merge, and only if **all three** conditions above hold and the recomputed
acceptance verdicts are all `Met`: on the integration branch, set the phase's `status: complete`,
with `session`, `completion_evidence` (files that exist) and `result` (the actual verification and
review outcome), and remove it from `next_up`. Update the record's `## Backlog` to match.

An unclaimed session completes nothing, however clean its review: there is no phase line to write.

If any condition does not hold, the phase stays open with a `next_action` that names exactly what
remains, including anything the review surfaced. Closing honestly incomplete is a correct outcome.

## 8. Regenerate the catalog and confirm the check is green

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog

CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
```

Commit the completion edit and the regenerated catalog together. If the check fails, fix the cause
first; never close a session on a failing tree.

## 9. Report

State plainly whether the phase reached complete or stayed open and why, the review's actual
verdict, the session record's code, and the commits made. This is the one report in the session's
life that should read as a finished account.
