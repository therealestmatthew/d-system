---
schema_version: 1
id: doc-troubleshooting
code: OPS-008
title: Troubleshooting
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: []
depends_on: []
---

# Troubleshooting

Common failures, each with its symptom, its cause and the fix. A fix is given only where the
repository's own tools or documents support it; anything else says "ask the owner". Commands run
from the control repository's root unless the entry says otherwise.

Two rules apply to every entry:

- A failing check or hook is a result to fix or report, never a step to retry until it goes quiet.
- Never commit with `--no-verify`, never force-push a shared branch, and never route around a hook.

## Git and the backlog

### A claim push is rejected

- **Symptom.** `git push` of the claim commit to control `dev` fails with `rejected` and
  `non-fast-forward` or `fetch first`.
- **Cause.** Another developer pushed to control `dev` after your last pull. Often they claimed a
  phase too.
- **Fix.**
  1. `git pull --rebase`. If `backlog/backlog.yaml` conflicts, see the next entry.
  2. Regenerate the catalog (`uv run plugins/idea-realization/scripts/cli.py catalog`) and run
     `uv run plugins/idea-realization/scripts/check.py`.
  3. If the check now rejects your claim (overlap with an active peer's systems, deliverables or
     dependency chain, `max_active` reached, or another developer's workstream), the claim is not
     safe: confirm `git status --short` shows nothing else, drop your claim commit
     (`git reset --hard origin/dev`, which then discards only your local claim) and choose another
     phase.
  4. If the check passes, `git push`.

  Source: the `session-start` skill, step 3.

### `backlog/backlog.yaml` has a merge conflict

- **Symptom.** A rebase or pull stops with a conflict in `backlog/backlog.yaml`.
- **Cause.** Two developers edited different phases, or the same `updated` line, in the same file.
  This is normal.
- **Fix.**
  1. Keep both sides: the peer's phases exactly as they are, and your own phase's edits.
  2. Set the backlog's `updated` to today.
  3. Never resolve the file with `--ours` or `--theirs`; either one deletes a peer's work.
  4. Do not merge `docs/catalog.md` by hand: regenerate it with
     `uv run plugins/idea-realization/scripts/cli.py catalog`.
  5. If both sides used the same document code, whoever integrates second allocates a new code,
     renames the file and updates every reference.
  6. Run the check, then `git rebase --continue`.

  If two phases conflict in **product source code**, their declared systems or deliverables were
  wrong. Stop and report it; do not force the merge.

  Source: the `session-start` skill, "If a rebase conflicts"; `plugins/idea-realization/docs/backlog-protocol.md`.

### The doctor reports drift

- **Symptom.** `uv run plugins/idea-realization/scripts/doctor.py` exits 1 and lists files as
  `drifted` or `missing`.
- **Cause.** The doctor compares each file the scaffold wrote with the hash it recorded then.
  - `drifted` on a data file (`backlog/backlog.yaml`, `docs/codes.yaml`, `docs/systems.yaml`, the
    idea files, `brain/index.md`) is expected once work has started.
  - `drifted` on a copied schema under `.idea-realization/schemas/` means the local copy differs
    from the plugin's.
  - `missing` means the file or directory was removed (for example `.idea-realization/staging/`,
    which is not tracked by git).
- **Fix.**
  - `missing`: run the scaffold again for that feature, for example
    `uv run plugins/idea-realization/scripts/scaffold.py --feature partition`. It writes only what is
    missing and never overwrites.
  - `drifted` on a data file: no action.
  - `drifted` on a schema: do not edit it back by hand. Ask the owner; the scaffold never
    overwrites an existing file, and there is no command that resets a record.

### A hook refuses a commit or a command

- **Symptom A: pre-commit.** `git commit` stops. The hook (`tools/git-hooks/pre-commit`) runs
  `tools/check_confidential.py` and then `check.py`; the output is either
  `check_confidential: FAILED` with one line per violation, or the check's error lines.
- **Fix A.**
  - Confidential violation: remove the identifier from the file, `git add` it again (the check
    reads the staged content, not the file on disk), and commit. A file under `.private/` must not
    be tracked: `git rm --cached <file>`.
  - Check failure: fix what it names. A stale catalog is fixed by
    `uv run plugins/idea-realization/scripts/cli.py catalog` and staging the result.
  - If you believe the check itself is wrong, stop and report it to the owner.
- **Symptom B: AWS guard.** A Bash command is refused with `aws_guard: refused: <reason>`.
- **Fix B.** The reason names the rule. Use `tools/aws-sandbox read ...` for reads. A create or
  update goes to the `aws-deploy` agent. Never set an `AWS_` variable or touch `~/.aws/`. If the
  guard blocks a command that is legitimate, report it to the owner; do not rephrase the command
  to get past it.
- **Symptom C: permission rule.** An edit to `CLAUDE.md`, `AGENTS.md`, `ideas/ideas.jsonl` or
  anything under `.private/` is denied.
- **Fix C.** These are denied on purpose. `CLAUDE.md` and `AGENTS.md` change only with the owner's
  approval of the exact text. The idea log changes only through `/idea-realization:idea`
  (`scripts/idea.py`).

### `check.py` reports files from the wrong repository

- **Symptom.** `check.py` (or `paths.py`, `doctor.py`) reports a `root:` that is not this
  repository, or errors about files that are not here.
- **Cause.** The scripts take the root from `--root`, then `IDEA_REALIZATION_ROOT`, then
  `CLAUDE_PROJECT_DIR`, then `git rev-parse --show-toplevel`. When this repository sits inside
  another git repository's working tree, or Claude Code was started in another directory, the
  later sources resolve to the wrong place.
- **Fix.** Set the root explicitly, from this repository's root:

  ```bash
  export IDEA_REALIZATION_ROOT=$PWD
  uv run plugins/idea-realization/scripts/paths.py    # the first line, root:, must be this repository
  ```

  or pass `--root <path>` to the one command.

## Pull requests and CI

### A pull request merge is refused by `--match-head-commit`

- **Symptom.** `gh pr merge <n> --merge --match-head-commit <sha>` fails and the pull request stays
  open.
- **Cause.** The branch's head is no longer the commit the gating review judged: a commit was
  pushed after the review. `--match-head-commit` makes GitHub refuse exactly this case.
- **Fix.**
  1. Do not merge without the flag, and do not pass the new head's hash in place of the reviewed
     one.
  2. See what changed: `git fetch` and `git log <reviewed_commit>..origin/agent/<phase-id>`.
  3. If the new commits belong in the phase, re-run the verification and a new gating review of
     the new head, record it as a second verdict (`...-2.json`), then merge with the new
     `reviewed_commit`.
  4. If they do not belong (pushed by mistake), ask the owner before rewriting the branch.

  Source: the `session-close` skill, merge steps.

### The required check `verify` is pending or failed

- **Symptom.** A product pull request to `dev` or `main` cannot be merged: `gh pr checks <n>`
  shows `verify` as pending, failed or missing.
- **Cause and fix.**
  - **Pending:** wait with `gh pr checks <n> --watch`.
  - **Failed:** read the failing step with `gh run view <run id> --log-failed`. Fix it on the
    branch and push. The head has moved, so the gating review must judge the new head before the
    merge (previous entry).
  - **Missing or never starts:** the workflow file (`ci_workflow` in
    `.idea-realization/product.yaml`, normally `product-ci.yml`) is not on the branch, or its job is
    not named `verify`, or GitHub Actions is not enabled for the repository. Check the first two in
    the repository. Enabling Actions and changing the ruleset are the owner's: ask the owner.

## AWS

### `AccessDenied` on `iam:CreateRole`

- **Symptom.** A deployment fails with an access-denied error naming `iam:CreateRole` (or another
  IAM change).
- **Cause.** The deploy role cannot create or change any IAM role or policy
  (`aws/iam/deploy-policy.json`, statement `DenyEveryIamChange`). The stack tries to create a role.
- **Fix.**
  1. The sandbox administrator creates the role under the path `/app/`, with its service's trust
     policy and only the permissions the function needs.
  2. Change the stack to reference the role by ARN (in CDK, `Role.fromRoleArn(...)`, not
     `new Role(...)`).
  3. Deploy again with `aws-deploy`. The deploy role may pass and read roles under `/app/` only.

  Source: `aws/README.md`, "What the deploy role can and cannot deploy".

### CDK cannot assume its bootstrap roles

- **Symptom.** `cdk deploy` (run through `tools/aws-sandbox exec`) fails because it could not
  assume a role named like `cdk-...-deploy-role-...`, or reports access denied on
  `sts:AssumeRole`.
- **Cause.** The default CDK synthesizer assumes bootstrap roles, and the deploy role denies
  `sts:AssumeRole`.
- **Fix.** Use `CliCredentialsStackSynthesizer` in the product's CDK app, so CDK deploys with the
  deploy profile's own credentials. The account is bootstrapped once by an administrator; if it is
  not, ask the owner.

  Source: `aws/README.md`, "CDK".

### Bedrock model access is denied

- **Symptom.** The deployed product's call to Bedrock fails with `AccessDeniedException`, or with a
  validation error saying the model id needs an inference profile.
- **Cause.** One of: the account has no access to that model in the region; the model is called by
  a model id where it must be called through an inference profile; the product's execution role
  under `/app/` lacks permission to invoke the model.
- **Fix.**
  1. Dispatch `bedrock-claude-advisor` to list the models and inference profiles the account can
     call, and the right id for the product's call. It never invokes a model.
  2. Enabling model access and changing the execution role's permissions are the sandbox
     administrator's (the deploy role cannot change IAM).
  3. Agents cannot test a call: the read role denies `bedrock:InvokeModel` and `Converse`. The
     advisor gives the smallest test request for a person to run.

### A `ce`, budget or billing command is refused

See the cost guardrails guide (`OPS-007`): budgets and billing are the sandbox administrator's.

## Local development

### The dev server's port is already in use

- **Symptom.** Starting a dev server fails with `EADDRINUSE` or `address already in use`.
- **Cause.** Another worktree's server, often a peer agent's on the same machine, holds the port.
- **Fix.** Find the holder with `ss -ltnp | grep :<port>` (or `lsof -i :<port>`). Do not stop a
  process you did not start. Start your server on a free port, given explicitly (for example
  `--port <free port>`). The `session-start` skill, step 5, requires choosing a port explicitly
  rather than assuming the default is free. Whether the team assigns port ranges per developer is
  the owner's decision: ask the owner.

## Not covered here

If a failure is not listed, record it with the `brain` skill as a `lesson` once it is solved, so
the next person finds it, and tell the owner if it should be added here.
