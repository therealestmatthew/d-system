---
schema_version: 1
id: doc-troubleshooting
code: OPS-008
title: Troubleshooting
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Troubleshooting

Common failures, each with its symptom, its cause and the fix. A fix is given only where the
repository's own tools or documents support it; anything else says "ask the owner". Commands run
from the control repository's root unless the entry says otherwise.

Two rules apply to every entry:

- A failing check or hook is a result to fix or report, never a step to retry until it goes quiet.
- Never commit with `--no-verify` and never route around a hook. Never force-push `dev` or `main`;
  a feature branch may be force-pushed only with `--force-with-lease`, after a rebase.

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
     safe: confirm `git status --short` shows nothing and `git log --oneline origin/dev..HEAD`
     shows only your claim commit, then drop it (`git reset --hard origin/dev`, which then
     discards only your local claim) and choose another phase. If the log shows another unpushed
     commit, such as an idea, drop only the claim with `git revert` or ask for help instead.
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

### The doctor fails

- **Symptom.** `IDEA_REALIZATION_ROOT=$PWD uv run plugins/idea-realization/scripts/doctor.py`
  exits 1. Each recorded file is listed with a state.
- **Cause.** The doctor compares each file in `.idea-realization/install-state.json` with the disk.
  Only some states fail the run:
  - `unchanged`: matches the record. Does not fail.
  - `edited`: a data or configuration file people and agents edit by design (`backlog/backlog.yaml`,
    `docs/codes.yaml`, `docs/systems.yaml`, the idea files, `brain/index.md`, `product.yaml`,
    `project.yaml`) changed since the scaffold wrote it. This is normal use and does not fail;
    `check.py` validates the content.
  - `absent`: a recorded directory that git ignores, such as `.idea-realization/staging/`, is not
    there. A fresh clone never has it. Does not fail.
  - `stale`: a schema copy under `.idea-realization/schemas/` differs from the plugin's own copy.
    Fails.
  - `unrecorded`: a schema copy matches the plugin's, but the record still holds an older hash
    (the copy was updated by hand). Fails.
  - `drifted`: a schema copy that this plugin version no longer ships differs from the record, or
    `.gitignore` changed since the scaffold changed it with consent. Fails.
  - `missing`: a recorded file, or a recorded directory git does not ignore, was removed. Fails.
- **Fix.**
  - `stale` or `unrecorded`: run the command the doctor's line names, for example
    `IDEA_REALIZATION_ROOT=$PWD uv run plugins/idea-realization/scripts/scaffold.py --feature backlog --refresh-schemas`.
    It replaces the copy with the plugin's file (or only records the current hash when the content
    already matches) and never touches data files. Add `--dry-run` first to see what it would do.
    Commit the refreshed schema and `install-state.json` together.
  - `missing`: run the scaffold again for that feature, for example
    `IDEA_REALIZATION_ROOT=$PWD uv run plugins/idea-realization/scripts/scaffold.py --feature partition`.
    It writes only what is missing and never overwrites.
  - `drifted`: ask the owner.
  - `edited` and `absent`: no action.

  Source: the `doctor` and `scaffold` skills (`plugins/idea-realization/skills/`).

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
- **Symptom C: permission rule.** An edit to `CLAUDE.md`, `ideas/ideas.jsonl` or
  anything under `.private/` is denied.
- **Fix C.** These are denied on purpose. `CLAUDE.md` changes only with the owner's
  approval of the exact text. The idea log changes only through `/idea-realization:idea`
  (`scripts/idea.py`).

### `check.py` reports files from the wrong repository

- **Symptom.** `check.py` (or `paths.py`, `doctor.py`) reports a `root:` that is not this
  repository, or errors about files that are not here.
- **Cause.** The scripts take the root from `--root`, then `IDEA_REALIZATION_ROOT`, then
  `git rev-parse --show-toplevel` of the directory the command runs in, then `CLAUDE_PROJECT_DIR`
  (which comes first only when it is a folder inside that working tree and the command runs
  inside it). When this repository sits inside another git repository's working tree and the
  command runs outside Claude Code's project directory, or the command runs from another
  directory, the later sources resolve to the wrong place.
- **Fix.** Set the root on the one command, from this repository's root:

  ```bash
  IDEA_REALIZATION_ROOT=$PWD uv run plugins/idea-realization/scripts/paths.py   # root: must be this repository
  ```

  or pass `--root <path>` to the one command. Do not `export` the variable: with it set in the
  shell, `uv run pytest` fails, because the plugin tests build their own temporary repositories
  (`OPS-001`, section 7). If you exported it, `unset IDEA_REALIZATION_ROOT` before running tests.

## Pull requests and CI

### `gh` cannot reach the repository

- **Symptom.** `session-close` stops before merging and reports that `gh` cannot reach a
  repository whose `origin` is on GitHub: `gh repo view --json nameWithOwner` fails in that
  worktree because `gh` is not logged in, its token expired, the organization's single sign-on is
  not authorized for it, or you have no access to the repository.
- **Cause.** `session-close` merges a repository whose `origin` is on GitHub only through a pull
  request. When `gh` cannot reach it, the skill stops and reports; it never falls back to a local
  merge for a GitHub origin, because control `dev` has no pull-request rule and would accept a
  merge with no pull request. The local `git merge --no-ff` is only for a repository with no
  `origin`, or whose `origin` is a path on this machine: `product.py merge-route --checkout
  <worktree>` prints `local` for those, and treats every other `origin` as hosted.
- **Fix.**
  1. Fix the login: `gh auth login`, or authorize the token for the organization's single sign-on.
     Check with `gh auth status` and `gh repo view --json nameWithOwner` in both worktrees.
  2. If you lack write access to either repository, ask the owner for it.
  3. Run `session-close` again. Never merge or push to `dev` by hand to get past the stop.

  Source: the `session-close` skill, step 6, "Which path applies".

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

### CI fails with "The repository secret DENY_LIST is not set"

- **Symptom.** The `Private-content check` step (control) or `Confidential check` step (product)
  fails with that message.
- **Cause.** The workflow has no deny-list to check against. A missing secret fails the run in both
  repositories by design. A pull request from a fork never receives secrets, so it always fails here.
- **Fix.** The owner sets the secret: `gh secret set DENY_LIST --repo <org>/<repo> <
  .private/deny-list.txt`, then re-runs the job. Do not remove or weaken the step. A fork pull
  request is recreated as a branch in the repository instead.

  Source: `docs/guides/OPS-001-branching-and-ci.md`, section 7.

### Control CI cannot read the product repository

- **Symptom.** In control CI, the `Product repository settings` step fails with "The repository
  secret PRODUCT_READ_TOKEN is not set" or "The product repository is not named", or the
  `Check out the product repository (read-only)` step fails with an authentication error, `Bad
  credentials`, `Repository not found` or `could not read Username`.
- **Cause.**
  - The secret `PRODUCT_READ_TOKEN` is not set on the control repository, or the run is a pull
    request from a fork, which never receives secrets.
  - Neither the repository variable `PRODUCT_GITHUB` nor `github:` in
    `.idea-realization/product.yaml` names the product repository.
  - The token has expired or been revoked, is still pending an organization's approval, or does not
    include the product repository with Contents read-only. GitHub answers a token that cannot see
    a private repository with `Repository not found`, not with a permissions error.
- **Fix.** The owner creates a new token with the settings in `docs/guides/OPS-001-branching-and-ci.md`
  (section 7), sets it with `gh secret set PRODUCT_READ_TOKEN --repo <org>/<control-repo>`, deletes
  the old token, and re-runs the job (`gh run rerun <run id>`). For an unnamed product the owner sets
  `gh variable set PRODUCT_GITHUB --repo <org>/<control-repo> --body <org>/<repo>`. Do not remove
  the step, unset `IDEA_REALIZATION_REQUIRE_PRODUCT`, or widen the token's permissions. A fork pull
  request is recreated as a branch in the repository instead.

  Source: `docs/guides/OPS-001-branching-and-ci.md`, section 7.

### `apply_rulesets.sh` says the main merger has no access

- **Symptom.** `tools/github/apply_rulesets.sh` stops with
  `error: User '<login>' has no access to <org>/<repo>` (or `Team '<org>/<team-slug>'`), and says
  nothing was changed on GitHub.
- **Cause.** The script gives the bypass on `main` and on `demo-*` tag creation only to an actor
  that already has access to the repository. GitHub answered 404 to the access check: the user is
  not a collaborator, the team does not have the repository, or the name is misspelled.
- **Fix.** Check the third argument's spelling. If it is right, grant the account or team access to
  the repository first (a team needs at least write access), then run the script again.

  Source: `docs/guides/OPS-001-branching-and-ci.md`, section 9.

### A merge into `main` is refused

- **Symptom.** A pull request from `dev` to `main` cannot be merged, or a push to `main` is
  rejected, with a message that the ref is protected by a ruleset (for example "Cannot update
  this protected ref").
- **Cause.** Only the owner can update `main` (the `update` rule in `control-main.json` and
  `product-main.json`, with the owner as the only bypass actor), and only through a pull request.
- **Fix.** Ask the owner to merge the release pull request. If the owner's own merge is refused,
  the rulesets were applied without the main merger or with the wrong one: the owner re-runs
  `tools/github/apply_rulesets.sh` with the right third argument.

  Source: `docs/guides/OPS-001-branching-and-ci.md`, section 9.

### A push of a `demo-*` tag is refused

- **Symptom.** `git push origin demo-rc-<n>` (or `demo-final`) is rejected with a message that the
  ref is protected by a ruleset (for example "Cannot create ref due to creations being
  restricted" or "Cannot update this protected ref").
- **Cause.** Two rulesets cover `refs/tags/demo-*`. `demo-tags-create` restricts creation to the
  owner, the only bypass actor. `demo-tags-protect` refuses moving or deleting an existing tag for
  everyone, the owner included.
- **Fix.**
  - **You are not the owner:** do not retry and do not push the tag under another name. Ask the
    owner to create and push it (`OPS-006`, "Release candidate", step 3). Delete your local tag
    with `git tag -d <tag>` so it does not differ from the one the owner pushes.
  - **The owner's push of a new tag is refused:** the rulesets were applied without the main
    merger or with the wrong one. Re-run `tools/github/apply_rulesets.sh` with the right third
    argument; the bypass list of `demo-tags-create` must show one actor with `bypass_mode`
    `always`.
  - **The tag already exists on the remote:** it cannot be moved or deleted. Make the next
    release candidate, `demo-rc-<n+1>`, instead.

  Source: `docs/guides/OPS-001-branching-and-ci.md`, section 9, "Who creates `demo-*` tags".

## AWS

### `AccessDenied` on `iam:CreateRole`

- **Symptom.** A deployment fails with an access-denied error naming `iam:CreateRole`,
  `iam:PutRolePolicy` or another IAM change.
- **Cause.** The deploy role creates and changes IAM roles only under the path `/app/` and only
  with the permission boundary `app-permissions-boundary` attached
  (`aws/iam/deploy-policy.json`, statements `AllowChangingAppRolesOnlyUnderTheBoundary`,
  `DenyAppRoleChangesWithoutTheBoundary` and `DenyEveryIamChangeOutsideAppRoles`). The stack
  creates a role without the path or the boundary, or a resource the deploy role never creates (a
  customer managed policy, user, group or service-linked role), or a CDK grant attaches a policy to
  a person-created role imported as mutable.
- **Fix.**
  1. Synthesize with `tools/aws-sandbox synth --dir <app dir>` and find the role in `cdk.out/`
     that lacks `"Path": "/app/"` or `PermissionsBoundary`.
  2. Apply the CDK settings in `aws/README.md` ("CDK settings every product stack uses"): the
     `@aws-cdk/core:permissionsBoundary` context key and the aspect that sets the path. Import a
     person-created role with `Role.fromRoleArn(this, id, arn, { mutable: false })`.
  3. A service-linked role (for example OpenSearch Serverless's) is created once by the sandbox
     administrator (`aws/README.md`, "Setup (the owner, once per sandbox account)", step 5).
  4. Deploy again with `aws-deploy`.

  Source: `aws/README.md`, "What the deploy role can and cannot deploy".

### A script that imports an AWS SDK is refused

- **Symptom.** `python lambdas/handler.py` or `node infra/bin/app.js` is refused with
  `aws_guard: refused: the script ... uses boto3` (or `@aws-sdk`, `aws-cdk-lib`).
- **Cause.** The hook refuses running any script by path that loads an AWS SDK, so product code
  that calls Bedrock or Textract cannot be run directly.
- **Fix.** Run tests through the test runner (`uv run pytest`, `npm test`, `npx vitest`), which the
  hook does not inspect for SDK imports, with the AWS clients mocked. To see a CDK app's
  CloudFormation, use `tools/aws-sandbox synth`. Only `aws-deploy` runs SDK code against AWS,
  through `tools/aws-sandbox exec`.

### CDK cannot assume its bootstrap roles

- **Symptom.** `cdk deploy` (run through `tools/aws-sandbox exec`) fails because it could not
  assume a role named like `cdk-...-deploy-role-...`, or reports access denied on
  `sts:AssumeRole`.
- **Cause.** The default CDK synthesizer assumes bootstrap roles, and the deploy role denies
  `sts:AssumeRole`.
- **Fix.** Use `CliCredentialsStackSynthesizer` in the product's CDK app, so CDK deploys with the
  deploy profile's own credentials. The account is bootstrapped once by an administrator; if it is
  not, ask the owner.

  Source: `aws/README.md`, "What the deploy role can and cannot deploy", "CDK settings every
  product stack uses", item 1.

### Bedrock model access is denied

- **Symptom.** The deployed product's call to Bedrock fails with `AccessDeniedException`, or with a
  validation error saying the model id needs an inference profile.
- **Cause.** One of: the account has no access to that model in the region; the model is called by
  its model id (`anthropic.claude-sonnet-5`) where it must be called through the US inference
  profile (`us.anthropic.claude-sonnet-5`), since neither Claude Sonnet 5 nor Claude Opus 5.5 has
  an in-region endpoint in a US region; the product's execution role under `/app/` lacks one of
  the three parts of the inference-profile grant (`aws/README.md`, "Bedrock: US inference
  profiles"); or the call uses a profile other than a `us.` one (`global.`, `eu.`, `apac.` ...), which the
  deploy policy and the boundary deny.
- **Fix.**
  1. Dispatch `bedrock-claude-advisor` to list the models and inference profiles the account can
     call, and the right id for the product's call. It never invokes a model.
  2. Enabling model access is the sandbox administrator's. A missing grant is fixed in the stack
     that creates the execution role, and deployed by `aws-deploy`.
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
