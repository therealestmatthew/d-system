# AWS sandbox setup

How the team's sandbox account is set up so that agents can work in it safely. **The two IAM roles
below, together with the machine rule, are the security boundary.** The wrapper (`tools/aws-sandbox`), the PreToolUse hook
(`tools/hooks/aws_guard.py`) and the permission rules in `.claude/settings.json` keep agents on the
right path, but they match command text; what an agent can actually do is decided by the role its
profile assumes.

## The machine rule

**A machine that runs agents holds no default or ambient AWS credentials.** No `[default]` or
`[profile default]` section in `~/.aws/config` or `~/.aws/credentials`; no `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE` or container-credential variables in the
environment; no EC2 instance role, container task role or other credentials the instance metadata
service hands out. Only the two named sandbox profiles exist.

The AWS SDKs and CLI fall back to exactly those sources when no profile is named. With none of
them present, a command that gets past the hook or the permission rules finds no credentials at
all, or at most the deploy role, which cannot touch IAM, Organizations, account or billing.

Check it on each machine, after setup and whenever its AWS configuration changes:

```bash
uv run python tools/check_aws_machine.py --probe
```

It reports each default profile, ambient variable and reachable metadata service, and with
`--probe` asks AWS whom the default credential chain resolves to; it exits 1 if it finds anything.
`tools/aws-sandbox` runs the file and environment checks on every call and prints what it finds as
warnings.

## The two roles

| Role | Used by | Policies |
|---|---|---|
| **Read** | `tools/aws-sandbox read` and `whoami`; the agents `aws-infra-reviewer`, `aws-ops-inspector`, `bedrock-claude-advisor`, `aws-cost-optimizer` | AWS managed `ReadOnlyAccess`, plus `iam/read-only-guard-policy.json` |
| **Deploy** | `tools/aws-sandbox write` and `exec`; the agent `aws-deploy` only | `iam/deploy-policy.json` |

- `read-only-guard-policy.json` is a deny list added on top of `ReadOnlyAccess`: it refuses the
  reads that reveal a secret or a credential (secret values, decrypted parameters, login tokens,
  function environments) and the calls that cost money or run code (model invocation, Lambda
  invocation, assuming another role).
- `deploy-policy.json` allows everything in the account except IAM, Organizations, account,
  billing, budget, cost and identity-center actions and assuming another role. Of IAM it allows
  exactly three actions: `iam:PassRole` and `iam:GetRole` on roles under the path `/app/`, and
  `iam:ListRoles`. Explicit Denies, which no Allow can override, refuse every IAM change (create,
  delete, attach, put, update and the rest), passing or reading any role outside `/app/`, the
  Organizations, account, billing and identity actions, turning off CloudTrail, Config or
  GuardDuty, reading secret values, and any regional action outside the sandbox region.

## What the deploy role can and cannot deploy

**Execution roles are created by a person, under `/app/`.** The deploy role cannot create or change
any IAM role or policy. It can attach (pass) a role, and read it, only when the role's path is
`/app/` — for example `arn:aws:iam::<account>:role/app/orders-api-lambda`. So a stack that needs a
Lambda, ECS or Step Functions execution role works like this:

1. A person creates the role under the path `/app/`, with the trust policy for its service (for
   example `lambda.amazonaws.com`) and only the permissions the function needs.
2. The stack references that role by ARN instead of creating one.
3. `aws-deploy` deploys the stack; the deploy role passes the existing role to the service.

A stack that tries to create a role fails with an access-denied error naming `iam:CreateRole`;
`aws-deploy` reports it, and a person creates the role.

**CDK.** The default CDK synthesizer assumes bootstrap roles, which `sts:AssumeRole` denies. Use
`CliCredentialsStackSynthesizer` in the product's CDK app, so CDK deploys with the deploy profile's
own credentials; bootstrap the account once as an administrator. Reference execution roles with
`Role.fromRoleArn(...)` rather than `new Role(...)`.

**Secrets.** CloudFormation dynamic references to Secrets Manager
(`{{resolve:secretsmanager:...}}`) are resolved with the caller's permissions, which deny
`GetSecretValue`; give secrets to the application at run time instead.

## Setup (the owner, once per sandbox account)

1. In `iam/deploy-policy.json`, replace `REPLACE_WITH_SANDBOX_REGION` with the sandbox region.
2. Create the read role: attach `ReadOnlyAccess` and a customer-managed policy from
   `iam/read-only-guard-policy.json`.
3. Create the deploy role with a customer-managed policy from `iam/deploy-policy.json`.
4. Create the execution roles the product needs under the path `/app/` (section above), as the
   product's plans name them.
5. Let each developer's sandbox identity assume both roles: the roles' trust policies name the
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
3. Remove any default or ambient credentials (the machine rule above), then check:
   `uv run python tools/check_aws_machine.py --probe` must print OK.
4. Check the profiles: `tools/aws-sandbox whoami` prints both profile names and the read role's
   identity.

## What agents may do

- Reads run freely through `tools/aws-sandbox read`, with the read role.
- Only the `aws-deploy` agent runs `tools/aws-sandbox write` or `exec`, with the deploy role. The
  hook refuses them from any other agent and from the main session.
- Deleting anything prompts a person for approval each time. IAM changes, and Organizations,
  account and billing actions, are refused by the deploy role itself; it can only attach roles a
  person created under `/app/`.
- No agent reads or changes `~/.aws/`, sets an `AWS_` variable, or runs the AWS CLI, an AWS SDK or a
  deployment tool outside the wrapper; the hook refuses each of these.

## Residual risk

- **The hook is best effort.** It matches command text and reads the scripts it can see. A
  determined or confused agent can still find a command it does not recognise. The IAM roles and
  the machine rule are the boundary; the hook and the permission rules only keep agents on the
  intended path.
- **The deploy role can destroy data.** Deleting through `tools/aws-sandbox write` prompts a person,
  but a deploy script run with `tools/aws-sandbox exec`, or a stack update that replaces a
  resource, runs under the deploy role without a prompt. A delete or a destructive data call
  inside such a script is limited only by the deploy role's permissions. Keep nothing in the
  sandbox that cannot be recreated.
- **Read reaches data.** `ReadOnlyAccess` can read object contents and table items. Keep production
  or personal data out of the sandbox.

