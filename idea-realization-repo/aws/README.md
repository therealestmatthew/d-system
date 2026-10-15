# AWS sandbox setup

How the team's sandbox account is set up so that agents can work in it safely. **The IAM roles
below, together with the machine rule, are the security boundary.** The wrapper (`tools/aws-sandbox`), the PreToolUse hook
(`tools/hooks/aws_guard.py`) and the permission rules in `.claude/settings.json` keep agents on the
right path, but they match command text; what an agent can actually do is decided by the role its
profile assumes.

The product this sandbox serves uses Step Functions; Bedrock (Claude Sonnet 5 for two agents,
Claude Opus 5.5 for two) with Guardrails; Bedrock Knowledge Bases on an OpenSearch Serverless vector
store; Textract; DynamoDB (one table set per tenant); S3 with one KMS key per tenant; KMS; a VPC with
PrivateLink endpoints; Cognito; CloudTrail with its logs in an S3 Object Lock bucket; and a React
examiner workbench on Amplify Hosting.

## The machine rule

**A machine that runs agents holds no default or ambient AWS credentials.** No `[default]` or
`[profile default]` section in `~/.aws/config` or `~/.aws/credentials`; no `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE` or container-credential variables in the
environment; no EC2 instance role, container task role or other credentials the instance metadata
service hands out. Only the two named sandbox profiles exist.

The AWS SDKs and CLI fall back to exactly those sources when no profile is named. With none of
them present, a command that gets past the hook or the permission rules finds no credentials at
all, or at most the deploy role, which cannot touch Organizations, account or billing, and can
change IAM only for roles under `/app/` that carry the permission boundary.

Check it on each machine, after setup and whenever its AWS configuration changes:

```bash
uv run python tools/check_aws_machine.py --probe
```

It reports each default profile, ambient variable and reachable metadata service, and with
`--probe` asks AWS whom the default credential chain resolves to; it exits 1 if it finds anything.
`tools/aws-sandbox` runs the file and environment checks on every call and prints what it finds as
warnings.

## The roles and policies

| Role | Used by | Policies |
|---|---|---|
| **Read** | `tools/aws-sandbox read` and `whoami`; the agents `aws-infra-reviewer`, `aws-ops-inspector`, `bedrock-claude-advisor`, `aws-cost-optimizer` | AWS managed `ReadOnlyAccess`, plus `iam/read-only-guard-policy.json`, plus (sandbox only) `iam/read-sandbox-data-policy.json` |
| **Deploy** | `tools/aws-sandbox write` and `exec`; the agent `aws-deploy` only | `iam/deploy-policy.json` |
| **Application roles** under `/app/` | The product's own services at run time (Step Functions, Lambda, the Knowledge Base, Textract notifications, Cognito, CloudTrail, flow logs, Amplify) | Whatever the stack grants, capped by the permission boundary `iam/app-permissions-boundary.json` |

`tools/aws-sandbox synth` uses no role at all (see "Synthesizing without credentials").

- `read-only-guard-policy.json` is a deny list added on top of `ReadOnlyAccess`: it refuses the
  reads that reveal a secret or a credential (secret values, decrypted parameters, login tokens,
  function environments), decrypting with KMS other than through S3 or DynamoDB, and the calls
  that cost money or run code (model invocation, agent and flow invocation, Knowledge Base
  retrieval, guardrail application, Textract analysis, Lambda invocation, assuming another role).
- `read-sandbox-data-policy.json` lets the read role decrypt tenant data through S3 and DynamoDB
  and read Textract results (`textract:Get*`, `List*`), neither of which `ReadOnlyAccess` grants.
  The decrypt is limited three ways: to keys in the sandbox account (the key ARN pattern and
  `aws:ResourceAccount`), to keys with a tenant alias `alias/<product>-tenant-*`
  (`kms:ResourceAliases`), and to calls S3 or DynamoDB make on the role's behalf
  (`kms:ViaService`). See the warning below.
- `deploy-policy.json` allows everything in the account except IAM, Organizations, account,
  billing, budget, cost and identity-center actions and assuming another role. Of IAM it allows:
  creating, changing and deleting roles under the path `/app/` **only when the role carries the
  permission boundary** `app-permissions-boundary` (for `CreateRole` and
  `PutRolePermissionsBoundary` the condition key `iam:PermissionsBoundary` is the boundary in the
  request; for `PutRolePolicy`, `AttachRolePolicy`, `DetachRolePolicy` and `DeleteRolePolicy` it is
  the boundary already attached to the role, per the IAM page of the AWS Service Authorization
  Reference); passing `/app/` roles to the product's
  services only (`iam:PassedToService`: Step Functions, Lambda, Bedrock, Textract, Cognito,
  CloudTrail, VPC flow logs, Amplify, EventBridge); reading `/app/` roles; listing roles; and
  reading the boundary and AWS managed policies. Explicit Denies, which no Allow can override,
  refuse: any IAM change outside `/app/` roles (users, groups, policies, service-linked roles,
  identity providers, the boundary policy itself); creating or changing an `/app/` role without
  the boundary; removing a boundary; passing or reading any role outside `/app/`; the
  Organizations, account, billing and identity actions; stopping, deleting or updating the
  account's **baseline** CloudTrail trail; turning off Config or GuardDuty; bypassing S3 Object
  Lock governance retention; reading secret values; invoking a model through any inference
  profile other than a US geographic one (`us.*`); and any regional action outside the sandbox
  region, except the cross-region model routing of a US inference profile.
- `app-permissions-boundary.json` caps every `/app/` role at what the deploy role itself may do,
  minus secret reads, key policy changes and key deletion, Object Lock changes, turning off the
  audit trail, and assuming roles. A role the deploy role creates therefore never has more power
  than the deploy role. The boundary lets an application role pass `/app/` roles to Textract and
  Bedrock (asynchronous Textract jobs and Bedrock jobs need it), and nothing else in IAM.

> **Revisit before real claimant data.** The read role can decrypt tenant data and read Textract
> results because the sandbox holds synthetic data only (owner ruling, 2026-10-14). Before any
> real claimant document, name or identifier reaches this account, remove
> `read-sandbox-data-policy.json` from the read role and add `kms:Decrypt` back to the guard's
> unconditional deny. Agents would otherwise read personal data into their transcripts.

## What the deploy role can and cannot deploy

**The stack creates its own roles, under `/app/` and with the boundary.** The deploy role may
create a role only when both hold: its path is `/app/` (for example
`arn:aws:iam::<account>:role/app/ClaimsStack-StateMachineRole-1A2B3C`) and its permission boundary
is `arn:aws:iam::<account>:policy/app-permissions-boundary`. It may attach inline or AWS managed
policies to such a role and delete it again. A role created without the path or the boundary fails
with an access-denied error naming `iam:CreateRole`; fix the CDK app (below), not the policy.

The deploy role cannot create customer managed policies (`AWS::IAM::ManagedPolicy`), users,
groups, instance profiles or service-linked roles. CDK grants (`table.grantReadWriteData(role)`)
produce inline policies (`AWS::IAM::Policy`), which are allowed on boundary roles.

**CDK settings every product stack uses.**

1. `CliCredentialsStackSynthesizer`. The default CDK synthesizer assumes bootstrap roles, which
   `sts:AssumeRole` denies. With this synthesizer CDK deploys with the deploy profile's own
   credentials; an administrator bootstraps the account once.
2. The permission boundary on every role, set once for the whole app. In `cdk.json`:

   ```json
   { "context": { "@aws-cdk/core:permissionsBoundary": { "name": "app-permissions-boundary" } } }
   ```

   or in code, `PermissionsBoundary.of(app).apply(ManagedPolicy.fromManagedPolicyName(app,
   'AppBoundary', 'app-permissions-boundary'))`. Either applies the boundary to every `Role` in
   the app, including the roles that constructs create implicitly.
3. The path `/app/` on every role, and the boundary again on roles CDK writes as raw
   `AWS::IAM::Role` resources (custom-resource providers such as `autoDeleteObjects`, which the
   context setting has missed in some CDK versions). An aspect covers both:

   ```ts
   import { Aspects, CfnResource, IAspect, Stack } from 'aws-cdk-lib';
   import { IConstruct } from 'constructs';

   class AppRoles implements IAspect {
     visit(node: IConstruct): void {
       if (node instanceof CfnResource && node.cfnResourceType === 'AWS::IAM::Role') {
         node.addPropertyOverride('Path', '/app/');
         node.addPropertyOverride('PermissionsBoundary', Stack.of(node).formatArn({
           service: 'iam', region: '', resource: 'policy',
           resourceName: 'app-permissions-boundary' }));
       }
     }
   }
   Aspects.of(app).add(new AppRoles());
   ```

   The product CI's `verify` job fails when a synthesized template has a role without this path
   and boundary, or a resource type the deploy role cannot create
   (`templates/product-repo/.github/workflows/product-ci.yml`).
4. A role a person created by hand (an older `/app/` role without the boundary) is imported with
   `Role.fromRoleArn(this, id, arn, { mutable: false })`. A mutable import makes CDK attach an
   inline policy to it, which the deploy role is refused for a role without the boundary; with
   `mutable: false` CDK grants are no-ops, so the person gives that role its permissions.

**Service-linked roles** are created by a person (setup step 5). OpenSearch Serverless needs one
before the first collection.

**Secrets.** CloudFormation dynamic references to Secrets Manager
(`{{resolve:secretsmanager:...}}`) are resolved with the caller's permissions, which deny
`GetSecretValue`; the boundary denies it to application roles too. If the product needs a secret at
run time, the owner adds a narrow allow for that secret's ARN to the boundary.

### Bedrock: US inference profiles

Neither model has an in-region endpoint in a US region, so the product calls both through the
**US geographic inference profiles** (owner ruling, 2026-10-14), which route to us-east-1,
us-east-2 and us-west-2:

| Model | Foundation model id | Inference profile id |
|---|---|---|
| Claude Sonnet 5 | `anthropic.claude-sonnet-5` | `us.anthropic.claude-sonnet-5` |
| Claude Opus 5.5 | `anthropic.claude-opus-5-5` | `us.anthropic.claude-opus-5-5` |

Only US profiles are allowed, by both the deploy policy and the boundary: the statement
`DenyInferenceProfilesOutsideTheUS` denies a model invocation whose `bedrock:InferenceProfileArn`
is not `arn:aws:bedrock:*:*:inference-profile/us.*`. It is an allow-list, so `global.`, `eu.`,
`apac.` and any profile prefix AWS adds later are denied without being named. A second statement,
`DenyDirectFoundationModelInvocation`, denies invoking a foundation model without a profile, so
every model call goes through a US profile, in the sandbox region as elsewhere. Quotas for the
profiles are the "Cross-region model inference ... for <model>" service quotas, requested in the
sandbox region, one pair per model.

**The runtime role grant has three parts.** A role that invokes a model through a US profile needs
`bedrock:InvokeModel` (and `InvokeModelWithResponseStream` if it streams; `Converse` is authorized
as `InvokeModel`) on:

1. the inference profile in the sandbox (source) region;
2. the foundation model in the source region;
3. the foundation model in every other region the profile routes to,

with parts 2 and 3 limited to calls made through that profile. For Sonnet 5 from a source region
`<region>` (repeat for `anthropic.claude-opus-5-5`):

```json
[
  { "Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
    "Resource": "arn:aws:bedrock:<region>:<account>:inference-profile/us.anthropic.claude-sonnet-5" },
  { "Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
    "Resource": [
      "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-5",
      "arn:aws:bedrock:us-east-2::foundation-model/anthropic.claude-sonnet-5",
      "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-sonnet-5" ],
    "Condition": { "StringEquals": { "bedrock:InferenceProfileArn":
      "arn:aws:bedrock:<region>:<account>:inference-profile/us.anthropic.claude-sonnet-5" } } }
]
```

Check the profile's current destination regions with `bedrock-claude-advisor` before writing the
grant; AWS can add regions to a profile.

**Why the region deny lets this through.** AWS evaluates the foundation model once per candidate
destination region, with `aws:RequestedRegion` set to that region and the condition key
`bedrock:InferenceProfileArn` set to the profile. The region deny in the deploy policy and in the
boundary carries `"ArnNotLike": {"bedrock:InferenceProfileArn":
"arn:aws:bedrock:*:*:inference-profile/us.*"}`, so it skips exactly the evaluations routed by a US
profile; a call without the key, or through any other profile, is still refused outside the
sandbox region. The originating call is still locked to the sandbox region: AWS evaluates the
inference profile resource with the source region and without that key (AWS Bedrock user guide,
"Geographic cross-Region inference", Service Control Policy requirements).

### Workbench hosting: Amplify Hosting

The React examiner workbench is a static build hosted on Amplify Hosting. The stack creates the
Amplify app and branch (`AWS::Amplify::App`, `AWS::Amplify::Branch`) without a repository
connection, so no source-control token is stored in AWS. `aws-deploy` publishes a build with
`tools/aws-sandbox write amplify create-deployment ...`, uploads the zip to the URL it returns, then
runs `write amplify start-deployment ...`. The deploy role allows `amplify:*` and may pass an
`/app/` role to `amplify.amazonaws.com` if the app ever needs a service role; the read role reads
apps, branches, jobs and domain associations through `ReadOnlyAccess`.

**Config point: custom domain and WAF (not set up now).** The app uses its default
`*.amplifyapp.com` domain and no web application firewall. To add either later:

- a custom domain is an `AWS::Amplify::Domain` resource in the stack; a certificate of your own
  must be in us-east-1 (ACM for CloudFront), which the region deny refuses, so either let Amplify
  manage the certificate or have an administrator create it;
- a firewall is an `AWS::WAFv2::WebACL` with scope `CLOUDFRONT` in us-east-1, associated with the
  Amplify app; the region deny exempts only classic `waf:*`, so `wafv2:*` and `acm:*` in us-east-1
  need an exemption in `deploy-policy.json`, or an administrator creates the web ACL.

`ampx` (the Amplify Gen 2 CLI) is guarded like `cdk`: only through `tools/aws-sandbox exec` from
`aws-deploy`. A Gen 2 backend (`ampx sandbox`, `ampx pipeline-deploy`) creates roles outside
`/app/` without the boundary, which the deploy role refuses; the product's back end is the CDK
stack instead.

### Tenant keys and tables

The stack creates each tenant's KMS key and DynamoDB table set at deploy time (owner ruling,
2026-10-14). Each tenant key gets the alias `alias/<product>-tenant-<tenant>`, where `<product>` is
the value that replaces `REPLACE_WITH_PRODUCT_NAME`; the read role decrypts only through keys with
such an alias, so a key without one is unreadable to it. The deploy role keeps `kms:PutKeyPolicy` and `kms:ScheduleKeyDeletion`. Each key
policy keeps the statement that delegates to IAM in the account, or the roles' IAM policies
(including the read role's decrypt) have no effect. Scheduling a key's deletion, or changing a key
policy, through `tools/aws-sandbox write` prompts a person (`.claude/settings.json`); the same
changes made by a `cdk deploy` through `exec` are not prompted. A key scheduled for deletion can be
recovered with `kms cancel-key-deletion` during its waiting period (7 to 30 days).

### Audit trail and Object Lock

- The account's **baseline trail** (created by an administrator, outside the product) cannot be
  stopped, deleted or updated by the deploy role. Its name replaces
  `REPLACE_WITH_BASELINE_TRAIL_NAME` in `deploy-policy.json`. The product stack's **own trail** is
  not covered by that deny, so stack updates and teardown work.
- The product trail's log bucket uses S3 Object Lock in **GOVERNANCE** mode with a **1-day**
  default retention in the sandbox (owner ruling, 2026-10-14). The deploy role is denied
  `s3:BypassGovernanceRetention`, so it cannot delete or overwrite a locked log version early; an
  administrator can, with `--bypass-governance-retention`. Tearing the stack down therefore fails
  on that bucket until the newest log object is a day old, or until an administrator empties it.
  Changing the bucket's lock configuration through `tools/aws-sandbox write` prompts a person.

## Synthesizing without credentials

`tools/aws-sandbox synth [--dir <cdk app dir>] [cdk args]` runs `cdk synth` with every AWS
credential source removed: all `AWS_` and `BOTO_` variables, the wrapper's profile names and
`CDK_DEFAULT_*` are dropped, `AWS_EC2_METADATA_DISABLED=true` is set, and `AWS_CONFIG_FILE` and
`AWS_SHARED_CREDENTIALS_FILE` point at `/dev/null`. It refuses `--profile` and `--role-arn`, needs
no profile configuration, and every agent may run it (`.claude/settings.json` allows it; the hook
lets it through). Use it to read the CloudFormation a change produces: IAM roles and their
boundary, trust policies, public endpoints, Object Lock settings. Context lookups fail under it, as
in CI; commit `cdk.context.json`.

## Setup (the owner, once per sandbox account)

1. In local copies of the policy files (never commit the values), replace
   `REPLACE_WITH_SANDBOX_REGION` (a US region where the US profiles are offered),
   `REPLACE_WITH_SANDBOX_ACCOUNT_ID`, `REPLACE_WITH_BASELINE_TRAIL_NAME` and (in
   `read-sandbox-data-policy.json`) `REPLACE_WITH_PRODUCT_NAME`, the prefix of the tenant key
   aliases.
2. Create the customer managed policy `app-permissions-boundary` at the path `/` from
   `iam/app-permissions-boundary.json`. The name must match the ARN in `deploy-policy.json`.
3. Create the read role: attach `ReadOnlyAccess` and customer managed policies from
   `iam/read-only-guard-policy.json` and, in this sandbox only, `iam/read-sandbox-data-policy.json`.
4. Create the deploy role with a customer managed policy from `iam/deploy-policy.json`.
5. Create the OpenSearch Serverless service-linked role, once per account, as an administrator
   (the deploy role cannot create service-linked roles):

   ```bash
   aws iam create-service-linked-role --aws-service-name observability.aoss.amazonaws.com
   ```

   It fails with "has been taken in this account" if the role already exists; that is fine.
6. Bootstrap CDK once as an administrator, and enable access to Claude Sonnet 5 and Claude Opus 5.5
   in Bedrock.
7. Let each developer's sandbox identity assume the read and deploy roles: the roles' trust
   policies name the developers' principals (IAM Identity Center permission sets or IAM users in
   the sandbox).

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
2. Tell the repository which profiles to use, outside version control: set `aws_read_profile`,
   `aws_deploy_profile` and, if the team's region in `.idea-realization/project.yaml` does not
   apply, `aws_region` in `.idea-realization/local.yaml` (gitignored; `ONBOARDING.md`, section 3,
   step 6). The environment variables `IDEA_REALIZATION_AWS_READ_PROFILE`,
   `IDEA_REALIZATION_AWS_DEPLOY_PROFILE` and `IDEA_REALIZATION_AWS_REGION` override it for one
   shell. `uv run plugins/idea-realization/scripts/paths.py show` prints what this machine resolves
   and where each value came from.
3. Remove any default or ambient credentials (the machine rule above), then check:
   `uv run python tools/check_aws_machine.py --probe` must print OK.
4. Check the profiles: `tools/aws-sandbox whoami` prints both profile names and the read role's
   identity.

## What agents may do

- Reads run freely through `tools/aws-sandbox read`, with the read role.
- Every agent may run `tools/aws-sandbox synth`; it uses no credentials.
- Only the `aws-deploy` agent runs `tools/aws-sandbox write` or `exec`, with the deploy role. The
  hook refuses them from any other agent and from the main session.
- Deleting anything prompts a person for approval each time, and so do scheduling a key's deletion,
  changing a key policy and changing an Object Lock configuration through `write`. Organizations,
  account and billing actions, and IAM changes other than to `/app/` roles with the boundary, are
  refused by the deploy role itself.
- No agent reads or changes `~/.aws/`, sets an `AWS_` variable, or runs the AWS CLI, an AWS SDK or a
  deployment tool (CDK, `ampx`, SAM, Terraform) outside the wrapper; the hook refuses each of these.

## Residual risk

- **The hook is best effort.** It matches command text and reads the scripts it can see. A
  determined or confused agent can still find a command it does not recognise. The IAM roles and
  the machine rule are the boundary; the hook and the permission rules only keep agents on the
  intended path.
- **The deploy role can destroy data.** Deleting through `tools/aws-sandbox write` prompts a person,
  but a deploy script run with `tools/aws-sandbox exec`, or a stack update that replaces a
  resource, runs under the deploy role without a prompt. That includes deleting a tenant's table,
  scheduling a tenant key's deletion and replacing a key policy. Keep nothing in the sandbox that
  cannot be recreated.
- **The deploy role can create roles.** Each `/app/` role is capped by the boundary at about what
  the deploy role itself may do, so no role it creates gains IAM, account or billing power. Neither
  the boundary nor any condition key limits a role's **trust policy**, though: a stack could create
  an `/app/` role that another account may assume. `aws-infra-reviewer` checks that every trust
  policy names only AWS service principals.
- **`aws-sandbox exec` runs whatever it is given** (owner ruling, accepted). The guard hook does not
  stop `tools/aws-sandbox exec bash -c '...'` from running arbitrary commands with the deploy
  role's credentials; it checks who calls `exec`, not what `exec` runs. This is accepted because the
  IAM roles are the boundary: anything run that way can do no more than the deploy role allows.
- **The hook does not block the instance metadata service** (owner ruling, accepted under the machine
  rule). A command can reach `169.254.169.254` directly; the hook does not look for it. The machine
  rule is what makes this safe: there are no instance credentials to find.
- **Agents must not run on an EC2 instance, or on any host that has an instance role or
  instance-metadata credentials** (container task roles included). On such a host the two risks
  above are no longer covered by the machine rule. `tools/check_aws_machine.py --probe` reports a
  reachable metadata service.
- **Read reaches data.** `ReadOnlyAccess` reads object contents and table items, and with
  `read-sandbox-data-policy.json` that includes data encrypted with the tenant keys, and Textract
  results. Keep production or personal data out of the sandbox, and see the warning under "The
  roles and policies".
