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
| **Deploy** | `tools/aws-sandbox write` and `exec`; the agent `aws-deploy` only | `iam/deploy-policy.json`, plus `iam/deploy-scope-policy.json` |
| **Application roles** under `/app/` | The product's own services at run time (Step Functions, Lambda, the Knowledge Base, Textract notifications, Cognito, CloudTrail, flow logs, Amplify) | Whatever the stack grants, capped by the permission boundary `iam/app-permissions-boundary.json` |

`tools/aws-sandbox synth` uses no role at all (see "Synthesizing without credentials").

- `read-only-guard-policy.json` is a deny list added on top of `ReadOnlyAccess`: it refuses the
  reads that reveal a secret or a credential (secret values, parameter values and their history,
  login tokens, the environment variables of functions, Amplify apps and branches, CodeBuild
  projects and builds and ECS task definitions and tasks, Amplify basic-auth credentials and
  webhook URLs, Cognito app-client and identity-provider secrets; see "Reads the guard refuses"
  below), decrypting with KMS other than through S3 or DynamoDB, and the calls
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
- `deploy-scope-policy.json` limits the deploy role's changes to the product's own resources. It
  is a separate policy because `deploy-policy.json` is close to the 6,144-character limit for a
  managed policy. It denies creating, changing, publishing, invoking and deleting a Lambda
  function, a Step Functions state machine, a CloudFormation stack or a CodeBuild project whose
  name does not start with `<product>-`; changing, deploying to or deleting an Amplify app or
  branch that does not carry the tag `project=<product>`; adding or removing the `project` tag on
  any other Amplify resource; and starting an Amplify build job at all. `<product>` is the value
  that replaces `REPLACE_WITH_PRODUCT_NAME`. See "The deploy role changes only the product's own
  resources" below.
- `app-permissions-boundary.json` caps every `/app/` role at what the deploy role itself may do,
  minus secret reads, key policy changes and key deletion, Object Lock changes, turning off the
  audit trail, and assuming roles. It repeats every statement of `deploy-scope-policy.json`, so a
  role the stack creates cannot change another function, state machine, stack, build project or
  Amplify app either. A role the deploy role creates therefore never has more power
  than the deploy role. The boundary lets an application role pass `/app/` roles to Textract and
  Bedrock (asynchronous Textract jobs and Bedrock jobs need it), and nothing else in IAM.

### Reads the guard refuses, and what to read instead

The guard policy and the wrapper's `SECRET_OPERATIONS` refuse these reads, because their response
carries a secret or a value that may be one (checked against the AWS API references, 2026-10-15):

| Read (`tools/aws-sandbox read ...`) | What the response carries |
|---|---|
| `lambda get-function`, `get-function-configuration`, `list-functions`, `list-versions-by-function` | The function's environment variables (`ListFunctions` omits only the state fields) |
| `amplify get-app`, `list-apps`, `get-branch`, `list-branches` | Environment variables and basic-auth credentials of the app, its branches and its auto-branch settings |
| `amplify get-webhook`, `list-webhooks` | The webhook URL, which starts a build when called |
| `codebuild batch-get-projects`, `batch-get-builds`, `batch-get-build-batches` | Build environment variables, including `PLAINTEXT` values |
| `ecs describe-task-definition`, `describe-tasks` | Container environment variables, and a task's environment overrides |
| `cognito-idp describe-user-pool-client` | The app client secret |
| `cognito-idp describe-identity-provider` | The external provider's details, including its `client_secret` |
| `ssm get-parameter-history` | Each version's parameter value |

Reviewers and `aws-ops-inspector` lose these reads. Use instead:

- **What is deployed:** `read cloudformation describe-stack-resources --stack-name <stack>` (or
  `list-stack-resources`) for each function, state machine, Amplify app and branch and its
  physical id; `read resourcegroupstaggingapi get-resources --tag-filters Key=project,Values=<product>`
  for everything tagged.
- **How it is configured:** the synthesized template (`tools/aws-sandbox synth`) or the deployed
  one (`read cloudformation get-template`), which hold runtime, memory, timeout, role and the
  environment variables as the stack wrote them; dynamic references stay unresolved there.
- **Lambda health:** `read lambda list-aliases`, `get-alias`, `get-function-concurrency`,
  `get-policy`, `list-event-source-mappings`, the CloudWatch metrics (`Errors`, `Throttles`,
  `Duration`) and the function's log group.
- **Amplify deployments:** `read amplify list-jobs --app-id <id> --branch-name <branch>` and
  `get-job`, with the app id from the stack resources; `list-domain-associations`.
- **CodeBuild and ECS**, if the product ever uses them: `read codebuild list-projects` and
  `list-builds-for-project`; `read ecs describe-services` and `list-tasks`; and their logs.
- **Cognito:** `read cognito-idp list-user-pool-clients` (ids and names) and
  `describe-user-pool`.

Kept, after checking: `cloudformation describe-stacks` and `get-template` (parameters marked
`NoEcho` are masked in describe calls; a template holds what the repository holds, with dynamic
references unresolved; a secret in `Outputs` or `Metadata` would show, which `aws-infra-reviewer`
checks for); `stepfunctions describe-state-machine` (the definition, as in the repository);
`bedrock-agent get-knowledge-base` and `get-data-source` (a Secrets Manager ARN, not the secret).

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

**The deploy role changes only the product's own resources.** The deploy role's main allow
covers every service, so without `deploy-scope-policy.json` it could rewrite the code of any
Lambda function in the account, or the definition of any state machine, and so run code with that
resource's existing role; no `iam:PassRole` check applies, because the role is not changing. The
scope policy limits those changes to resources whose name, or for Amplify whose tag, marks them as
the product's. Two choices follow from the AWS Service Authorization Reference:

- **Name prefix, for Lambda, Step Functions, CloudFormation and CodeBuild.** The resource name is
  in the ARN, so a `NotResource` deny works whether or not an action supports tag conditions, and
  a name cannot be changed after creation. A tag condition would not be enough here: Lambda needs
  `lambda:TagResource` to tag a function at creation, so the deploy role must keep that action,
  and it could then tag another function `project=<product>` and change it.
- **Tag, for Amplify.** An Amplify app's ARN holds a generated app id, not its name, so the
  prefix cannot be written in advance. `UpdateApp`, `DeleteApp`, `UpdateBranch`, `DeleteBranch`,
  `CreateDeployment` and `StartDeployment` support `aws:ResourceTag`, so they are denied on an app
  or branch without `project=<product>`. Adding or removing the `project` tag is denied on any
  Amplify resource that does not already carry `project=<product>`, so the deploy role cannot tag
  another app into scope. `StartJob` supports no resource tag, and the product's app has no
  repository connection and needs no build job, so it is denied everywhere.

What every product stack does for this:

1. Name each stack `<product>-<name>` (`new Stack(app, 'Claims', { stackName:
   '<product>-claims' })`).
2. Tag everything: `Tags.of(app).add('project', '<product>')`. CDK adds the tag to every
   resource in the app whose type takes tags, including `AWS::Amplify::App` and
   `AWS::Amplify::Branch`; the Amplify rule depends on it.
3. Give every function, state machine and build project a `<product>-` name, including the ones
   CDK creates for itself (custom-resource providers, `autoDeleteObjects`, `BucketDeployment`).
   An aspect does it for all of them:

   ```ts
   import { Aspects, CfnResource, IAspect, Names } from 'aws-cdk-lib';
   import { IConstruct } from 'constructs';

   const PRODUCT = '<product>';
   const NAME_PROPERTY: Record<string, [string, number]> = {
     'AWS::Lambda::Function': ['FunctionName', 64],
     'AWS::StepFunctions::StateMachine': ['StateMachineName', 80],
     'AWS::CodeBuild::Project': ['Name', 150],
   };

   class ProductNames implements IAspect {
     visit(node: IConstruct): void {
       if (!(node instanceof CfnResource)) return;
       const entry = NAME_PROPERTY[node.cfnResourceType];
       if (!entry) return;
       const [property, maxLength] = entry;
       node.addPropertyOverride(property, `${PRODUCT}-${Names.uniqueResourceName(node,
         { maxLength: maxLength - PRODUCT.length - 1 })}`);
     }
   }
   Aspects.of(app).add(new ProductNames());
   ```

   A function or state machine created without the prefix fails with an access-denied error
   naming `lambda:CreateFunction` or `states:CreateStateMachine`; fix the CDK app, not the
   policy. A named resource cannot be replaced in place, so a change that needs replacement (for
   example a new name) needs the old resource removed first.

**The sandbox account holds the product stack and nothing else.** The scope policy covers the
services above. The deploy role can still change resources of every other service in the account,
and some of those run code with an existing role (an EC2 instance's user data, an ECS task, an SSM
document, a Glue job). Do not create other workloads, other teams' stacks or hand-made functions
in the sandbox account; an administrator's own resources (the baseline trail, the CDK bootstrap
stack) are the only exceptions.

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
runs `write amplify start-deployment ...`. The deploy role may change, deploy to and delete only
an app and branch tagged `project=<product>`, may not start a build job, and may pass an `/app/`
role to `amplify.amazonaws.com` if the app ever needs a service role. The read role reads jobs,
artifacts and domain associations through `ReadOnlyAccess`; it may not read the app or branch
itself, because those responses carry environment variables and basic-auth credentials.

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
   `read-sandbox-data-policy.json`, `deploy-scope-policy.json` and
   `app-permissions-boundary.json`) `REPLACE_WITH_PRODUCT_NAME`: the product's short name, which
   prefixes the tenant key aliases, the stack names and the function, state machine and build
   project names, and is the value of the `project` tag. Use lowercase letters, digits and
   hyphens, starting with a letter.
2. Create the customer managed policy `app-permissions-boundary` at the path `/` from
   `iam/app-permissions-boundary.json`. The name must match the ARN in `deploy-policy.json`.
3. Create the read role: attach `ReadOnlyAccess` and customer managed policies from
   `iam/read-only-guard-policy.json` and, in this sandbox only, `iam/read-sandbox-data-policy.json`.
4. Create the deploy role with two customer managed policies, from `iam/deploy-policy.json` and
   `iam/deploy-scope-policy.json`.
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
- **The deploy role can change any resource outside the scope policy's services.** The scope
  policy covers Lambda, Step Functions, CloudFormation, CodeBuild and Amplify. Every other
  service's resources in the account are open to the deploy role, including resources that run
  code with an existing role. This is safe only while the sandbox account holds the product stack
  and nothing else (see "The deploy role changes only the product's own resources").
- **The Amplify tag rule is not tested against AWS.** It assumes CloudFormation tags a new
  Amplify app and branch through `CreateApp` and `CreateBranch` and calls `TagResource` only on
  resources that already carry the tag. If the first deploy fails on `amplify:TagResource`, tell
  the owner; the fix is a change to `DenyOutsideTheProductAmplifyProjectTag`, not removing it.
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
