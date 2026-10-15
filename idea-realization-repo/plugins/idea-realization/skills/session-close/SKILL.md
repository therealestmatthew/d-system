---
name: session-close
description: Finalize the session record, run the verification, have a dedicated gating reviewer judge the product diff against the phase's acceptance, merge the product and control branches only on a passing review, and mark the phase complete only when all three conditions hold. Use when a phase's work is finished and ready to hand off or close.
---

# Close the session

Finishes the session record the `checkpoint` skill maintains, runs the review gate, integrates on a
pass, and is the **only** procedure that may mark a phase complete.

**Two repositories.** The code is in the product worktree, on `agent/<phase-id>` in the product
repository; the session record and review records are in the control worktree, on
`agent/<phase-id>` in the control repository (see `session-start` and `${CLAUDE_PLUGIN_ROOT}/docs/two-repositories.md`).
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
3. **The branches are integrated.** After that pass, the control pull request (the session and
   review records) and then the product pull request were merged into their integration branches
   with merge commits (in a repository whose `origin` is a path on this machine, or that has
   none, `git merge --no-ff` locally), and
   the product merge commit's second parent is the reviewed commit. **A passing gating review is
   the approval for both merges**; no separate per-merge approval is asked for.

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
`## Unresolved` reflect the work as it stands at close. The `checkpoint` skill records the control
repository only: add the product branch's tip and the product verification output to the record
yourself.

## 2. Rebase both branches and run the verification

1. In the product worktree: `git fetch` and `git rebase origin/<product integration branch>`.
2. In the control worktree: `git fetch` and `git rebase origin/<control integration branch>`.
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
  the control worktree path and `origin/<control integration branch>...HEAD` there, with instructions to
  run `git diff` and `git log` on each itself;
- the paths of the requirement and plan documents the phase names, in the control worktree;
- the step 2 output, as evidence it may re-run but must not take on trust;
- its job: decide independently, from the diffs and its own run of the verification, whether each
  acceptance condition holds, and begin its reply with the line `VERDICT: pass` or
  `VERDICT: reject` (the schema's `verdict` values), followed by the phase id and the reviewed
  commit.
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

## 6. Merge both branches — only on a passing verdict

Only on a passing verdict, and only when the product worktree's `HEAD`
(`git -C <product worktree> rev-parse HEAD`) still equals the verdict's `reviewed_commit`. If it
does not, the branch gained a commit after the review: go back to step 2.

**Which path applies.** The `origin` URL decides it, never whether `gh` happens to work. Run, for
each repository's worktree:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/product.py" merge-route --checkout <worktree>
```

- `pull-request`: the `origin` is a hosted repository and `gh` reaches it. Use 6a to 6d.
- `local`: the worktree has no `origin`, or its `origin` is a path on this machine (a test
  repository, local-only use). Use the local merge at the end of this step.
- **Exit 1** (`gh repo view` failed for a hosted `origin`: `gh` missing, logged out, or not
  authorised for the organization's SSO): **stop and report it.** Do not merge either repository,
  and never use the local merge instead: merged and pushed locally, the branch lands on the
  integration branch without its pull request. Leave the phase `active`; once `gh auth status`
  passes, re-run `merge-route` and continue from here.

Say in the session record which path each repository took.

Every `gh` command below runs inside the worktree it names, so `gh` resolves the repository from
that worktree's `origin`.

### 6a. Push both branches and open the pull requests

```bash
git -C <control worktree> push --force-with-lease -u origin agent/<phase-id>
git -C <product worktree> push --force-with-lease -u origin agent/<phase-id>
```

`--force-with-lease` is needed only because step 2 rebased a branch you may have pushed before; it
applies to your own `agent/<phase-id>` branch and never to the integration branch or the release branch, which
are never force-pushed (`${CLAUDE_PLUGIN_ROOT}/docs/protocol.md`, section 10).

In each worktree, reuse the open pull request for `agent/<phase-id>` if there is one
(`gh pr view agent/<phase-id> --json number,state,headRefOid`), and otherwise open one against
that repository's integration branch:

```bash
gh pr create --base <control integration branch> --head agent/<phase-id> \
  --title "<phase-id>: <phase title>" --body "<session record code>; verdict <verdict record path>"
gh pr create --base <product integration branch> --head agent/<phase-id> \
  --title "<phase-id>: <phase title>" --body "<session record code>; verdict <verdict record path>"
```

The first runs in the control worktree, the second in the product worktree. Keep both pull request
numbers.

### 6b. Merge the control pull request

The control pull request carries the session record and the verdict records. Merge it with a merge
commit, pinned to the commit you pushed:

```bash
gh pr merge <control pr> --merge --match-head-commit "$(git -C <control worktree> rev-parse HEAD)"
```

`--match-head-commit` makes GitHub refuse the merge if the branch head moved after you pushed it.
The phase is still `active`: this merge records the review, it does not complete the phase.

### 6c. Merge the product pull request

When `product.yaml` names a `ci_workflow` other than `none`, wait for the required check (the
`verify` job) to finish and pass first:

```bash
gh pr checks <product pr> --watch --required --fail-fast
```

A non-zero exit means the required check failed or is missing: do not merge. Fix the cause on the
branch, which changes the product diff, and go back to step 2 for a fresh review. Then merge,
pinned to the reviewed commit:

```bash
gh pr merge <product pr> --merge --match-head-commit <reviewed_commit>
```

If GitHub refuses the merge (the head moved, the check failed, or the branch conflicts with the
integration branch), nothing landed in the product repository. Go back to step 2: rebase, re-run
the verification and review the new `HEAD`; the new review records reach the control repository
through a new control pull request.

### 6d. Confirm the product merge

```bash
gh pr view <product pr> --json mergeCommit --jq .mergeCommit.oid
git -C <product worktree> fetch origin
git -C <product worktree> rev-parse <merge commit>^2
git -C <product worktree> merge-base --is-ancestor <merge commit> origin/<product integration branch>
```

The second parent must equal the verdict's `reviewed_commit`, and the merge commit must be on the
product integration branch. Together they show that the pull request head, the merge commit's
second parent and the reviewed commit are one commit. The merge commit is the **product merge**.
If either test fails, stop and report it; do not record completion.

### Local merge: a repository whose route is `local`

Only for a repository `merge-route` printed `local` for, in place of 6a to 6d for that repository: confirm its
primary checkout is clean (`git -C <checkout> status --short` shows nothing; never stash a peer's
uncommitted work and never force an integration around it) and is on its integration branch, then:

```bash
git -C <checkout> pull --rebase                   # only when the branch has an upstream
git -C <checkout> merge --no-ff -m "Merge agent/<phase-id>" agent/<phase-id>
git -C <checkout> rev-parse HEAD HEAD^2
git -C <checkout> push                            # only when the branch has an upstream
```

Merge the control repository first, then the product repository. In the product repository,
`HEAD^2` must equal the verdict's `reviewed_commit`; `HEAD` is the **product merge**. If the merge
conflicts, abort it (`git -C <checkout> merge --abort`) and go back to step 2.

## 7. Record completion directly on the control integration branch — the only step that may write `status: complete`

The completion record is bookkeeping, so it goes straight onto the control integration branch in
the control primary checkout, not through a pull request. Only if **all three** conditions hold:
confirm the control primary checkout is clean and on its integration branch, bring it up to date,
and edit the backlog there:

```bash
git pull --rebase
```

Set the phase's `status: complete`, with `session`, `completion_evidence` (files that exist;
product files written `product:<path>`), `product_merge` (the full product merge commit from step
6) and `result` (the actual verification and review outcome), and remove it from `next_up`; if
that empties the list, write `next_up: []`, because a key with no entries reads as null and the
schema refuses it. Update the session record's `## Backlog` to match in the same commit. The check refuses a complete phase
without a passing gating verdict whose `reviewed_commit` equals its `product_merge` or that merge
commit's second parent.

Regenerate the catalog and run the check, with the product checkout configured:

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

Commit the completion edit, the session record's `## Backlog` update and the catalog together in
one commit that changes nothing else, then push it at once:

```bash
git pull --rebase
git push
```

If the pull brought in a peer's commit, regenerate the catalog and run the check again before the
push. If the push is rejected, repeat the pull, regenerate, check and push. A backlog conflict in
the rebase is resolved as `session-start` describes: keep both sides.

**The product merge has already landed, so it is never reverted.** Until the completion commit
lands, the phase stays `active` with its code merged; follow *A merged phase without its completion
record* in `${CLAUDE_PLUGIN_ROOT}/docs/two-repositories.md` if the push keeps failing.

An unclaimed session completes nothing, however clean its review: there is no phase line to write.
If any condition does not hold, the phase stays open with a `next_action` that names exactly what
remains, including anything the review surfaced. Closing honestly incomplete is a correct outcome.

## 8. Clean up

Fetch the product checkout (`git -C <product checkout> fetch origin`), then run the check once
more, with the product checkout configured: it must not report the phase as stranded, and must
print no `cannot tell` note for it. If it does either, follow *A stranded phase* in
`${CLAUDE_PLUGIN_ROOT}/docs/two-repositories.md`, whose first step is to fetch and check again, before doing anything
else.

Remove both worktrees and both local `agent/<phase-id>` branches, copying any ignored content out
first. Delete each remote `agent/<phase-id>` branch (`git push origin --delete agent/<phase-id>`)
unless the repository already deletes merged pull request branches.

## 9. Report

State plainly whether the phase reached complete or stayed open and why, the review's actual
verdict and record path, the session record's code, and the commits made in each repository. This
is the one report in the session's life that should read as a finished account.
