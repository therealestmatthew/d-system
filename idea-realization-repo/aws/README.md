# AWS sandbox setup

How the team's sandbox account is set up so that agents can work in it safely. **The two IAM roles
below are the security boundary.** The wrapper (`tools/aws-sandbox`), the PreToolUse hook
(`tools/hooks/aws_guard.py`) and the permission rules in `.claude/settings.json` keep agents on the
right path, but they match command text; what an agent can actually do is decided by the role its
profile assumes.

## The two roles

| Role | Used by | Policies |
|---|---|---|
| **Read** | `tools/aws-sandbox read` and `whoami`; the agents `aws-infra-reviewer`, `aws-ops-inspector`, `bedrock-claude-advisor`, `aws-cost-optimizer` | AWS managed `ReadOnlyAccess`, plus `iam/read-only-guard-policy.json` |
| **Deploy** | `tools/aws-sandbox write` and `exec`; the agent `aws-deploy` only | `iam/deploy-policy.json` |

- `read-only-guard-policy.json` is a deny list added on top of `ReadOnlyAccess`: it refuses the
  reads that reveal a secret or a credential (secret values, decrypted parameters, login tokens,
  function environments) and the calls that cost money or run code (model invocation, Lambda
  invocation, assuming another role).
- `deploy-policy.json` allows everything in the account except: any IAM, Organizations, account,
  billing, budget, cost or identity-center action; assuming another role; turning off CloudTrail,
  Config or GuardDuty; reading secret values; and any regional action outside the sandbox region.
  An explicit Deny cannot be overridden by any Allow.

## Before you create the deploy role: one decision for the owner

The deploy role denies all of IAM, as ruled. Two consequences for what can be deployed with it:

1. **No stack can create or attach an IAM role.** A Lambda function, an ECS task or a Step
   Functions state machine needs an execution role. Creating one needs `iam:CreateRole`, and
   attaching an existing one needs `iam:PassRole`; both are denied. Options:
   - **(a)** Keep the full IAM deny. A person creates every role the product needs, by hand, before
     the deploy that uses it, and the deploy role is still unable to pass it. In practice this
     blocks Lambda, ECS and Step Functions deploys by agents.
   - **(b)** Narrow the deny to allow `iam:PassRole`, `iam:GetRole` and `iam:ListRoles` only on roles
     under the path `/app/`. A person creates those roles; agents can attach but not create or
     change them.
   - **(c)** Also allow `iam:CreateRole`, `iam:PutRolePolicy` and `iam:AttachRolePolicy` on roles
     under `/app/`, with a required permissions boundary that caps what any such role can do.
     Agents can then deploy normal serverless stacks; no role they create can exceed the boundary.
2. **CDK's default synthesizer assumes bootstrap roles**, which `sts:AssumeRole` denies. Use
   `CliCredentialsStackSynthesizer` in the product's CDK app, so CDK deploys with the deploy
   profile's own credentials, and bootstrap the account once as an administrator.

CloudFormation dynamic references to Secrets Manager (`{{resolve:secretsmanager:...}}`) are also
resolved with the caller's permissions, which deny `GetSecretValue`; pass secrets to the
application at run time instead.

## Setup (the owner, once per sandbox account)

1. In `iam/deploy-policy.json`, replace `REPLACE_WITH_SANDBOX_REGION` with the sandbox region.
2. Create the read role: attach `ReadOnlyAccess` and a customer-managed policy from
   `iam/read-only-guard-policy.json`.
3. Create the deploy role with a customer-managed policy from `iam/deploy-policy.json` (as decided
   above).
4. Let each developer's sandbox identity assume both roles: the roles' trust policies name the
   developers' principals (IAM Identity Center permission sets or IAM users in the sandbox).

## Setup (each developer, once per machine)

1. Add two profiles to `~/.aws/config`, one per role, for example:

   ```ini
   [profile sandbox-read]
   role_arn = arn:aws:iam::<sandbox-account-id>:role/<read-role-name>
   source_profile = <your sandbox login profile>

   [profile sandbox-deploy]
   role_arn = arn:aws:iam::<sandbox-account-id>:role/<deploy-role-name>
   source_profile = <your sandbox login profile>
   ```

   Never use the `default` profile for either; the wrapper refuses it, and refuses one profile used
   for both roles.
2. Tell the repository which profiles to use, outside version control: set
   `IDEA_REALIZATION_AWS_READ_PROFILE`, `IDEA_REALIZATION_AWS_DEPLOY_PROFILE` and
   `IDEA_REALIZATION_AWS_REGION` in your shell, or the plugin options `aws_read_profile`,
   `aws_deploy_profile` and `aws_region`. `uv run plugins/idea-realization/scripts/paths.py`
   prints what this machine resolves.
3. Check it: `tools/aws-sandbox whoami` prints both profile names and the read role's identity.

## What agents may do

- Reads run freely through `tools/aws-sandbox read`, with the read role.
- Only the `aws-deploy` agent runs `tools/aws-sandbox write` or `exec`, with the deploy role. The
  hook refuses them from any other agent and from the main session.
- Deleting anything prompts a person for approval each time. IAM, Organizations, account and
  billing changes are refused by the deploy role itself.
- No agent reads or changes `~/.aws/`, sets an `AWS_` variable, or runs the AWS CLI, an AWS SDK or a
  deployment tool outside the wrapper; the hook refuses each of these.
