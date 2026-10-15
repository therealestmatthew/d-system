---
schema_version: 1
id: doc-ci-deploy-to-aws
code: PLAN-002
title: Deploy the product to the AWS sandbox from GitHub Actions through OIDC
kind: plan
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-control-tools, sys-agents]
depends_on: []
---

# Deploy the product to the AWS sandbox from GitHub Actions through OIDC

## Context and scope

Today the product deploys to the sandbox account only from a developer machine: the `aws-deploy`
agent runs `tools/aws-sandbox write` or `exec` with the deploy role (`aws/README.md`). The owner
decided that this stays the way the team deploys for now, and that this draft goes to a colleague
who will set up the pieces a deploy from GitHub Actions needs: the IAM identity provider and role,
the account pre-configuration, and the GitHub environment and workflow.

Goal: a person can deploy a chosen commit of the product repository to the sandbox from GitHub
Actions, using short-lived credentials issued through GitHub's OpenID Connect (OIDC) provider.

Non-goals:

- No long-lived AWS keys anywhere: no access key in a GitHub secret, a file or a developer's shell.
- Agents never get CI credentials. The CI role trusts only GitHub's OIDC tokens for one environment
  whose deployments a person approves; no agent profile, wrapper mode or hook gains a path to it.
- No production account, no destroy from CI, no change to the local deploy path.

## Decisions

- **A third role, `ci-deploy`, separate from the two sandbox roles.** Its permissions are the same
  `aws/iam/deploy-policy.json`, so CI can do exactly what `aws-deploy` can and nothing more. That
  is the policy as the owner settled it on 2026-10-14: it may create IAM roles under `/app/` only
  with the permission boundary `app-permissions-boundary` attached, may pass `/app/` roles only to
  the product's services, may not touch the account's baseline CloudTrail trail or bypass Object
  Lock governance retention, and its region deny exempts the cross-region routing of the US
  Bedrock inference profiles (`aws/README.md`). Whatever the owner changes in that policy later,
  `ci-deploy` takes too. The
  alternative, letting the existing deploy role also trust GitHub, would mix developer and CI
  principals in one trust policy and make an audit of either harder. Proposed by the plan author;
  the owner decides.
- **The trust policy is restricted to the `sandbox` environment of the product repository.** When a
  job names an environment, GitHub puts the environment in the token's `sub` claim, so the branch or
  tag rule is enforced by the environment's deployment rules (only `demo-*` tags and manual runs
  from `dev`), not by the trust policy. A ref-based trust statement for `demo-*` tags without the
  environment would skip the required reviewer, so this plan does not include one.
- **The existing deploy role cannot set any of this up.** Its policy denies every IAM change
  except to `/app/` roles under the permission boundary, and denies budgets and billing, so
  creating the OIDC provider, the `ci-deploy` role (outside `/app/`, without the boundary) and the
  budget needs an administrator in the sandbox account.
- **The workflow is a sketch in this plan, not a file in the product repository,** until the owner
  approves the plan.

## Prerequisites the colleague needs from the owner

| Item | Value (placeholder) |
|---|---|
| Access in the sandbox account | Administrator, or permissions to create an IAM OIDC provider, IAM roles and policies, and budgets |
| Sandbox account id | `<sandbox-account-id>` |
| Region | `REPLACE-WITH-SANDBOX-REGION` (the same value as in `deploy-policy.json`; a US region where the US Bedrock inference profiles are offered) |
| Baseline trail name | `REPLACE-WITH-BASELINE-TRAIL-NAME` (the same value as in `deploy-policy.json`) |
| Product repository | `<org>/<product>`, plus its numeric owner and repository ids (see step 2) |
| GitHub access | Admin on the product repository (environments, variables, OIDC settings) |
| Required reviewers | The GitHub handles who approve sandbox deployments |
| Budget | Monthly limit `<amount>` and the alert recipient `<alert-address>` |

## Work and dependencies

**1. Create the GitHub OIDC identity provider (administrator, once per account).**
Provider URL `https://token.actions.githubusercontent.com`, audience `sts.amazonaws.com`. A
thumbprint is no longer needed: AWS checks the provider's TLS certificate against its own trusted
root authorities, and when the provider is created with the CLI or API without a thumbprint, IAM
retrieves one itself (AWS IAM user guide, "Obtain the thumbprint for an OpenID Connect identity
provider"). For example:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
```

If the account already has this provider, reuse it.

**2. Find the exact subject claim the product repository will send.** Since 2026-07-15 GitHub puts
immutable owner and repository ids in the default `sub` claim of every repository created after
that date (and of any renamed or transferred one), in the form
`repo:<org>@<org-id>/<product>@<repo-id>:...`. Older repositories keep `repo:<org>/<product>:...`
unless opted in. Read the repository's OIDC settings (or GitHub's subject-claim preview API) and use
the value it shows. The policy below uses the immutable form.

**3. Create the `ci-deploy` role (administrator).** Attach a customer-managed policy made from
`aws/iam/deploy-policy.json` (region already replaced). Maximum session duration one hour. Trust
policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsSandboxEnvironmentOnly",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<sandbox-account-id>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:<org>@<org-id>/<product>@<repo-id>:environment:sandbox"
        }
      }
    }
  ]
}
```

Use `StringEquals`, not `StringLike` with a wildcard, so no other repository or environment
matches.

**4. AWS pre-configuration (administrator, once).**
- CDK bootstrap the account in the sandbox region as an administrator
  (`cdk bootstrap aws://<sandbox-account-id>/REPLACE-WITH-SANDBOX-REGION`). The product's CDK app
  uses `CliCredentialsStackSynthesizer` (`aws/README.md`), because the deploy policy denies
  `sts:AssumeRole` and so cannot assume the bootstrap roles.
- A monthly AWS Budget on the account with alerts at 50, 80 and 100 percent of `<amount>`, sent to
  `<alert-address>`.
- Tags on every stack: `project=<product>`, `environment=sandbox`, `deployed-by=ci` (set in the
  workflow with `--tags`), and the `project` tag activated as a cost-allocation tag.
- The permission boundary policy `app-permissions-boundary` exists, created from
  `aws/iam/app-permissions-boundary.json`; the stacks create their own `/app/` roles under it, as
  for local deploys. The product's CI `verify` job already fails a template whose roles lack the
  path or the boundary.
- The OpenSearch Serverless service-linked role exists (`aws iam create-service-linked-role
  --aws-service-name observability.aoss.amazonaws.com`, once, by an administrator); neither
  deploy role can create it.
- Bedrock model access is enabled for Claude Sonnet 5 and Claude Opus 5.5, and the quotas
  "Cross-region model inference requests per minute" and "tokens per minute" for each model's US
  profile (`us.anthropic.claude-sonnet-5`, `us.anthropic.claude-opus-5-5`) cover the demo load.
  The runtime roles the stack creates carry the three-part grant in `aws/README.md`, "Bedrock: US
  inference profiles". The US profiles route to us-east-1, us-east-2 and us-west-2; the owner has
  accepted that routing for the sandbox.
- The examiner workbench is hosted on Amplify Hosting. The stack creates the Amplify app with no
  repository connection; CI publishes the web build to it after `cdk deploy` (step 6). No custom
  domain or WAF: adding either needs us-east-1 resources the region deny refuses
  (`aws/README.md`, "Workbench hosting").

**5. GitHub configuration (repository admin).**
- Environment `sandbox`: required reviewers set, "prevent self-review" on, deployment branches and
  tags limited to `dev` and the tag pattern `demo-*`.
- Repository variable `AWS_CI_DEPLOY_ROLE_ARN` =
  `arn:aws:iam::<sandbox-account-id>:role/ci-deploy`, and `AWS_REGION`. These are variables, not
  secrets: neither is a credential.

**6. Workflow `deploy-sandbox.yml` (sketch; created only after the owner approves this plan).**

```yaml
name: deploy-sandbox
on:
  workflow_dispatch:
  push:
    tags: ['demo-*']

permissions:
  id-token: write   # lets the job request a GitHub OIDC token
  contents: read

concurrency:
  group: deploy-sandbox
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: sandbox          # required reviewer; puts environment:sandbox in the sub claim
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA when the file is created
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - uses: aws-actions/configure-aws-credentials@v6   # pin to a commit SHA
        with:
          role-to-assume: ${{ vars.AWS_CI_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
          role-session-name: deploy-sandbox-${{ github.run_id }}
      - run: npm ci && npm run build      # the workbench build for Amplify Hosting
        working-directory: web
      - run: npm ci
        working-directory: infra
      - run: npx cdk deploy --all --require-approval never --tags deployed-by=ci --outputs-file cdk-outputs.json
        working-directory: infra
      # Publish the workbench build to Amplify Hosting: zip web/dist, then
      # `aws amplify create-deployment --app-id <from cdk-outputs.json> --branch-name <branch>`,
      # upload the zip to the returned zipUploadUrl, and `aws amplify start-deployment` with the
      # returned jobId. The app id and branch come from the stack's outputs.
```

Step order: 1 before 3; 2 before 3; 3 and 4 before 6; 5 before 6. The `infra` directory and Node
setup follow the product's stack, which is not chosen yet; adjust them then.

## Acceptance and verification

- A manual run of `deploy-sandbox` from `dev` waits for a reviewer, then the
  `configure-aws-credentials` step succeeds and `aws sts get-caller-identity` in the job shows
  `assumed-role/ci-deploy/deploy-sandbox-<run-id>`.
- `cdk deploy` completes; CloudTrail shows the stack changes made by that session name.
- **Cases that must fail:** a run from a branch other than `dev` is refused by the environment's
  deployment rule; a job without `environment: sandbox` fails at `AssumeRoleWithWebIdentity`
  (access denied); a step in the job that calls `iam:CreateRole` for a role outside `/app/`, or
  without the permission boundary, is denied by the deploy policy.
- No GitHub secret holds an AWS key; `tools/check_aws_machine.py --probe` still passes on every
  developer machine (nothing in this plan changes them).

## Rollback

- To redeploy an earlier version, run the workflow on the previous `demo-*` tag, or deploy it
  locally with `aws-deploy`.
- To turn CI deploys off at once, remove the trust statement from `ci-deploy` (or delete the role),
  or disable the workflow. Local deploys are unaffected.
- Deleting stacks is not done from CI; a person approves each delete through the local path.

## Out of scope

Production deployment, destroy from CI, preview environments per pull request, and moving the
local deploy path to CI. The owner decided deploy is local only for now.

## Open questions

1. Should CI deploy at all before the demo, or only after it? The owner decides; the author leans to
   setting it up but keeping it unused until a `demo-rc-*` tag exists.
2. Who are the required reviewers for the `sandbox` environment? The owner decides.
3. Does the product repository use the immutable subject format (created after 2026-07-15, or opted
   in)? The colleague checks in step 2.
4. Should `ci-deploy` get a tighter policy than `deploy-policy.json` (for example limited to
   CloudFormation, S3 assets and the product's services)? The owner decides; the author leans to
   the same policy for the demo and tightening afterwards.
