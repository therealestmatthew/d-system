---
schema_version: 1
id: doc-demo-day-runbook
code: OPS-006
title: Demo day runbook
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: []
depends_on: []
---

# Demo day runbook

The steps from code freeze to the demo: release pull request, tags, local deployment, smoke test,
rollback and the recorded fallback. The demo is on 2026-11-05; the code freeze is 2026-11-03. Both
dates are also in `.idea-realization/project.yaml` (`demo.date`, `demo.freeze`).

Branching and CI rules are in the branching and CI guide (`OPS-001`). The AWS boundary is in
`aws/README.md`. Neither is restated here.

## Roles

Roles, not names. The owner assigns a person to each role before the freeze and records the
assignment where the team agrees (ask the owner where).

| Role | Does |
|---|---|
| Owner | Approves each release pull request into `main`, creates the tags, chooses `demo-final`, decides on rollback. Only the owner merges into `main`. |
| Release developer | Opens the release pull requests, runs the `aws-deploy` agent on their machine, keeps the deployment log. |
| Validator | Runs the smoke test against each deployed release candidate and records the result. |
| Sandbox administrator | The person with administrator access to the sandbox account. Creates execution roles under `/app/`, enables Bedrock model access, raises quotas. The deploy role cannot do any of these. |
| Presenter | Runs the demo and decides on the day whether to switch to the recorded video. |

One person may hold several roles. The release developer and the validator should be different
people, so the smoke test is not run by the person who deployed.

## Before the freeze (until 2026-11-03)

1. **Bedrock quota check.** Dispatch the `bedrock-claude-advisor` agent with: "List the Anthropic
   models and inference profiles this account can call in its region, and the Bedrock service
   quotas for the model the product uses (requests per minute, tokens per minute)." It reads them
   with `tools/aws-sandbox read bedrock list-foundation-models`, `list-inference-profiles` and
   `service-quotas list-service-quotas --service-code bedrock`. Compare the quota with the load of
   the demo (presenter plus audience). If it is too low, the sandbox administrator requests an
   increase; quota increases can take days, so do this at least a week before the demo.
2. **Model access.** If the advisor reports a model the account lists but cannot call, the sandbox
   administrator enables access. No agent can do this.
3. **Execution roles.** Every role the product's stacks reference exists under `/app/`
   (`aws/README.md`, "What the deploy role can and cannot deploy").
4. **Smoke test written down.** The validator writes the smoke test as a numbered list of checks
   with the expected result of each (URL, action, what must appear). Keep it in the product
   repository next to the deployment instructions. Which flows the demo shows is the owner's call.

## Code freeze (2026-11-03)

After the freeze, only fixes reach `dev`, and each fix is a backlog phase:

1. Record the problem as an idea (`/idea-realization:idea`).
2. The owner registers a phase for it and puts it first in `next_up`.
3. A developer claims it, builds it and closes it with `session-close` as usual. The gating review
   is never skipped.

The team kit plan also proposes a demo-day shortcut (an `agent/<handle>-hotfix-<slug>` branch that
skips the claim but not the review). That shortcut is not a ruling yet: ask the owner before using
it.

## Release candidate

Do this in **both** repositories (control and product), in the same order.

1. **Release pull request.** From `dev` to `main`:

   ```bash
   gh pr create --base main --head dev --title "Release demo-rc-<n>" --body "<what changed since demo-rc-<n-1>>"
   ```

   In the product repository the required check `verify` must pass first:
   `gh pr checks <number> --watch`.
2. **Merge.** The owner merges with a merge commit:

   ```bash
   gh pr merge <number> --merge
   ```

3. **Tag.** On the merge commit on `main`, an annotated tag, pushed:

   ```bash
   git fetch origin
   git tag -a demo-rc-<n> origin/main -m "Demo release candidate <n>"
   git push origin demo-rc-<n>
   ```

   `<n>` starts at 1 and increases by one per candidate. The two repositories carry the same
   `demo-rc-<n>` for the same release. Tags matching `demo-*` cannot be deleted or moved once the
   rulesets are applied, so check the commit before pushing the tag.

## Local deployment

Deployment runs on the release developer's machine through the `aws-deploy` agent. There is no CI
deployment (a draft plan for one is `PLAN-002`).

1. Check the machine: `uv run python tools/check_aws_machine.py --probe` prints OK, and
   `tools/aws-sandbox whoami` prints both profiles and the read role's identity.
2. Check out the tag in a separate product worktree, so no working branch is touched:

   ```bash
   git -C <product checkout> fetch --tags
   git -C <product checkout> worktree add --detach <product worktree directory>/demo-rc-<n> demo-rc-<n>
   ```

3. Dispatch `aws-deploy` with: the worktree path, the tag, the product's deploy command, and the
   smoke test's first check as the verification. The agent shows a diff or change set before it
   applies anything, and asks a person to approve every deletion.
4. Keep its report (what was created or updated, and the verification output) in the session
   record or wherever the owner asks.

## Smoke test

The validator runs the written smoke test against the deployed candidate and records, per check,
pass or fail with the real output or a screenshot. Then dispatch `aws-ops-inspector` to read the
deployed resources' state and recent errors. A failed check is a fix phase (see Code freeze), not a
change made on the deployed stack.

## Choosing demo-final

When a candidate has passed the smoke test, the owner tags the same commit `demo-final` in both
repositories:

```bash
git tag -a demo-final demo-rc-<n>^{commit} -m "Demo final: demo-rc-<n>"
git push origin demo-final
```

`demo-final` is created once. If a later candidate replaces it before the demo, ask the owner: the
tag rule blocks moving it.

## Rollback

Rollback is redeploying the previous candidate, never reverting commits on `main`:

1. The owner decides to roll back and names the tag (`demo-rc-<n-1>`).
2. The release developer checks out that tag in its own worktree (Local deployment, step 2) and
   dispatches `aws-deploy` with it.
3. The validator runs the smoke test again.

A stack change that replaces or deletes a resource prompts for approval; say what will be deleted
before approving. Data written by the newer version is not rolled back.

## Recorded fallback video

1. After the first candidate passes the smoke test, the presenter records the full demo flow
   against it. Record again after `demo-final` is chosen.
2. Store the video outside both repositories (it is large, and may show account details). Ask the
   owner where.
3. Check before recording that the screen shows no account id, credential, email address or other
   confidential identifier.
4. The presenter switches to the video when the live demo fails and a rollback will not finish in
   time.

## On the day (2026-11-05)

1. One hour before: the validator runs the smoke test against the deployed `demo-final`.
2. The release developer runs `tools/aws-sandbox whoami` on the deploying machine, so a rollback
   does not start with an expired login.
3. The presenter has the video open and ready.
4. No deployments except a rollback the owner orders.

## After the demo

Run the teardown checklist in the cost guardrails guide (`OPS-007`).
