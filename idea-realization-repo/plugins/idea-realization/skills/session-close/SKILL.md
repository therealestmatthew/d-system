---
name: session-close
description: Finalize the session record, run the verification, have a dedicated gating reviewer judge the product diff against the phase's acceptance, merge the product and control branches only on a passing review, and mark the phase complete only when all three conditions hold. Use when a phase's work is finished and ready to hand off or close.
---

# Close the session

Finishes the session record the `checkpoint` skill maintains, runs the review gate, integrates on a
pass, and is the **only** procedure that may mark a phase complete.

**Two repositories.** The code is in the product worktree, on `agent/<phase-id>` in the product
repository; the session record and review records are in the control worktree, on
`agent/<phase-id>` in the control repository (see `session-start` and `docs/two-repositories.md`).
A repository with no `.idea-realization/product.yaml` has only the control branch: skip every
product step below.

## When a phase may be marked complete

An agent never completes a phase on its own judgement that the work looks finished. It may set a
phase to `status: complete` when, and only when, **all three** of these hold:

1. **Verification ran green.** Every command in the phase's `verification` list ran, after the
   rebase, and its real output is recorded in the session record.
2. **A gating review passed.** A dedicated reviewer agent that did not share this session's context
   judged the diff against the phase's `acceptance` and returned `pass`, and every finding is fixed
   or explicitly accepted by the developer who owns the workstream, with the disposition recorded.
3. **The branches are integrated.** The product branch was fast-forwarded into the product
   integration branch, and the control branch into the control integration branch, after that
   pass. **A passing gating review is the approval for both merges**; no separate per-merge
   approval is asked for.

Where any one is unmet, the phase stays `active` (or `queued`, if handed off unfinished): say
plainly that the session looks done, run `checkpoint` to record where it stands, and stop. The
review is never skipped, and the completion step exists nowhere else.

## Values

Commands carry the person's saved options; an option never saved appears as its `${user_config.…}`
text and the scripts use the documented default. Read the resolved values once:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_WORKTREE_DIR='${user_config.worktree_dir}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_WORKTREE_DIR='${user_config.product_worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"

CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_WORKTREE_DIR='${user_config.product_worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/product.py" verify
```

Use `backlog_path` as **the backlog** and `integration_branch` as **the control integration
branch**; from `product.py verify`, `root` as **the product checkout** and `integration_branch` as
**the product integration branch**, exactly as printed. If `product.py verify` fails, stop and
report it: nothing below may act on a product checkout it refuses.

## 1. Identify the phase and run the checkpoint first

Use the named phase, or the session's one active phase; ask if more than one is plausible. With no
active phase the session is unclaimed: this skill still runs, judges the record's self-declared
conditions, and completes nothing. Never invent or retroactively claim a phase, and never re-run
this against a phase that already closed earlier in the conversation.

Run every step of the `checkpoint` skill now, against the current state, so `## Phase` through
`## Unresolved` reflect both repositories as they stand at close.

## 2. Rebase both branches and run the verification

1. In the product worktree: `git fetch` and `git rebase origin/<product integration branch>`.
2. In the control worktree: `git rebase <control integration branch>` after pulling it in the
   control primary checkout.
3. Run every command in the phase's `verification` list and keep the real output. A command runs in
   the product worktree unless it starts with `control:`, which runs the rest in the control
   worktree. A failing check is a result to record, not a step to retry until quiet.
4. Run the control check (the `backlog` skill's check command) in the control worktree.

**This run, after the rebase and against peers' merged work, is the one the review judges.** If it
fails, fix it on the branch and run it again before going on.

## 3. Run the gating review

Launch a **fresh agent of a dedicated reviewer type** — `phase-adversary` for most phases,
`validator-code` when the phase is a narrow code change judged against one requirement. Never a fork
of this session, which carries its conclusions, and never a general-purpose agent. Give it, in its
prompt:

- the phase id with its `scope`, `acceptance`, `verification` and `deliverables` pasted in (for an
  unclaimed session: the instruction as given, the self-declared conditions, and a plain statement
  that the session being reviewed wrote them);
- the product worktree path and the range `origin/<product integration branch>...HEAD` there, and
  the control worktree path and `<control integration branch>...HEAD` there, with instructions to
  run `git diff` and `git log` on each itself;
- the paths of the requirement and plan documents the phase names, in the control worktree;
- the step 2 output, as evidence it may re-run but must not take on trust;
- its job: decide independently, from the diffs and its own run of the verification, whether each
  acceptance condition holds, and end its reply with `VERDICT: pass` or `VERDICT: reject`.
  "No findings" is a valid result.

Wait for its reply. Never paraphrase away an uncomfortable finding, and never proceed as if the
review passed before it returns.

## 4. Record the verdict

Write the reply as a verdict record in the control worktree:
`<docs_root>/reviews/<date>-<phase-id>-<reviewer type>.json`, valid against
`.idea-realization/schemas/review-verdict.schema.json`. `repository` is `product`,
`reviewed_commit` is the full product `HEAD` the reviewer judged, `gating` is `true`,
`definition_sha256` is `sha256sum` of the reviewer's agent definition file, and the findings are
copied as written. Then:

- **Fix or accept every finding.** A fix is a new commit on the branch; a fix that changes the
  product diff needs a fresh review of the new `HEAD`, recorded as a second record (`…-2.json`). An
  acceptance names who accepted it — the developer who owns the workstream the finding is in.
  Record each finding's `disposition`.
- **A `reject` stands until a later review passes.** Two rejects in a row on the same finding: stop,
  leave the phase `active`, and report it to the owner rather than trying a third time.

Add `## Review` to the session record with the reviewer's findings quoted, not summarised, the
record's path, and each disposition. Commit the record and the session record on the control branch.

## 5. Record what a checkpoint skips

- `## Decisions` — what was decided and why, including where a recommendation was overridden.
- `## Corrections` — mistakes made and fixed during the session; omit only if there were none.
- `## Left undone` — what remains and why it was left, for whoever picks it up next.

Write these as narrative someone could read in six months, not as a restatement of the scope.

## 6. Integrate — only on a passing verdict

Confirm each primary checkout is clean (`git -C <checkout> status --short` shows nothing). Never
stash a peer's uncommitted work and never force an integration around it.

**Product first**, from the product primary checkout on its integration branch:

```bash
git -C <product checkout> pull --ff-only
git -C <product checkout> merge --ff-only agent/<phase-id>
git -C <product checkout> push
```

**Then control**, from the control primary checkout on its integration branch:

```bash
git pull --ff-only
git merge --ff-only agent/<phase-id>
```

If either merge is not a fast-forward, its integration branch moved since the rebase: go back to
step 2, rebase, re-run the verification, and if the product diff changed, review again. Never
resolve it with a merge commit that skips the green run.

## 7. Decide completion — the only step that may write `status: complete`

Only if **all three** conditions hold: on the control integration branch, set the phase's
`status: complete`, with `session`, `completion_evidence` (files that exist; product files written
`product:<path>`) and `result` (the actual verification and review outcome, naming the product
merge commit), and remove it from `next_up`. Update the record's `## Backlog` to match.

An unclaimed session completes nothing, however clean its review: there is no phase line to write.

If any condition does not hold, the phase stays open with a `next_action` that names exactly what
remains, including anything the review surfaced. Closing honestly incomplete is a correct outcome.

## 8. Regenerate the catalog, confirm the check is green, push

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog

CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
```

Commit the completion edit and the regenerated catalog together and push the control integration
branch. If the check fails, fix the cause first; never close a session on a failing tree. Then
remove both worktrees and both `agent/<phase-id>` branches, copying any ignored content out first.

## 9. Report

State plainly whether the phase reached complete or stayed open and why, the review's actual
verdict and record path, the session record's code, and the commits made in each repository. This
is the one report in the session's life that should read as a finished account.
