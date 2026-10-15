---
schema_version: 1
id: doc-cost-guardrails
code: OPS-007
title: Cost guardrails
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Cost guardrails

How the team keeps the AWS sandbox's spend visible and bounded: a budget alarm, a daily cost
review, tags on every resource, and a teardown checklist. The AWS boundary itself (two roles, the
machine rule, the wrapper) is in `aws/README.md`.

## Who can do what

| Action | Who | Why |
|---|---|---|
| Create or change a budget, an alert, a cost allocation tag activation | The sandbox administrator (a person with administrator or billing access in the account) | `aws/iam/deploy-policy.json` denies `budgets:*`, `ce:*`, `cur:*`, `billing:*` and the other billing actions explicitly. The read role has `ReadOnlyAccess`, which grants no create or update action. `.claude/settings.json` also asks a person before any `tools/aws-sandbox write budgets`, `ce` or `cur` command. |
| Read spend and find idle resources | The `aws-cost-optimizer` agent, with the read role | It runs `tools/aws-sandbox read ce get-cost-and-usage ...` and describe/list calls. It changes nothing. |
| Stop or delete a resource | The `aws-deploy` agent with a person's approval per deletion, or a person | Only `aws-deploy` runs `write` and `exec`. Every delete, stop or destroy command prompts for approval. |
| Delete an execution role under `/app/` | The `aws-deploy` agent, as part of the stack's destroy; the sandbox administrator for a role a person created | The deploy role creates, changes and deletes `/app/` roles that carry the permission boundary (`aws/README.md`, "The roles and policies"), so the stack's own roles go with the stack. It cannot create, change or delete any other role. |

## Budget alarm

The sandbox administrator creates it once, before the first deployment, in the AWS Budgets console
or with their own administrator credentials. No agent and no sandbox role can.

1. A monthly cost budget for the sandbox account. The amount is the owner's decision: ask the
   owner.
2. Alerts on actual spend at 50%, 80% and 100% of the budget, and on forecast spend at 100%.
3. Alert recipients: the owner and the team channel's email address, if the channel has one. Ask
   the owner for the addresses; they are not written in this repository.
4. Record in the brain that the budget exists, its amount and who receives the alerts, with
   `uv run plugins/idea-realization/scripts/brain.py new decision ...` (no email addresses or
   account ids in the entry).

When an alert fires, the person who receives it runs the daily cost review below at once and posts
the result to the team.

## Daily cost review

Once per working day, a validator dispatches the `aws-cost-optimizer` agent with:

> What did the sandbox cost over the last seven days, grouped by service and by the `project` and
> `owner` tags? List resources that are idle or left over from a test, each with its estimated
> monthly cost and the evidence it is idle, and the change you recommend.

Then:

1. Post the spend figures and the candidate list to the team.
2. The owner of each candidate (from its `owner` tag) either keeps it, with a reason, or asks the
   `aws-deploy` agent to remove it. Removal prompts for approval per deletion.
3. A resource with no `owner` tag goes to the owner to decide.

Cost Explorer data lags by up to a day, so a resource created this morning may not show yet. Each
Cost Explorer API request is billed by AWS; one review a day is a small number of requests. If the
agent's `ce` read is refused, the read role lacks Cost Explorer access: ask the owner, who decides
whether the sandbox administrator grants it.

## Tags

Every resource the product creates carries two tags:

| Key | Value |
|---|---|
| `project` | The product's name. The value is the owner's decision: ask the owner, and use the same value everywhere. |
| `owner` | The handle of the developer whose phase created the resource (the handle `identity.py` prints). |

- In a CDK app, add both at the app or stack level so every resource inherits them, for example
  `Tags.of(app).add("project", "<project tag>")`, and the `owner` tag per stack.
- The `aws-infra-reviewer` agent, reviewing an infrastructure diff, reports resources without the
  tags the team uses. Name `project` and `owner` in its dispatch.
- Tags only appear in cost reports after the sandbox administrator activates `project` and `owner`
  as cost allocation tags in the Billing console. Activation takes effect for spend from that point
  on, so do it before the first deployment.

## Bedrock spend

- Model invocations are billed per token. The read role cannot invoke a model, so agents never
  spend on Bedrock; only the deployed product and people do.
- Never buy provisioned throughput for a model without the owner's decision: it is billed per hour
  whether or not it is used.
- Bedrock spend appears under its own service in the daily review. If it grows faster than the demo
  rehearsals explain, find the caller before the next rehearsal.

## Teardown checklist

Run after the demo, or when a feature's resources are no longer needed. The `aws-deploy` agent does
the removals; each one prompts for approval.

1. Run the daily cost review once more to get the current list of resources and spend.
2. Destroy each product stack through the wrapper (for CDK, `tools/aws-sandbox exec` with the
   destroy command). Approve each prompt only after reading what it deletes.
3. Check what a stack deletion leaves behind, because CloudFormation keeps resources whose removal
   policy is retain: S3 buckets, DynamoDB tables, CloudWatch log groups, ECR repositories and their
   images, EBS snapshots, KMS keys pending deletion. Remove each one the owner does not want kept.
4. Check for stacks in `DELETE_FAILED` (`tools/aws-sandbox read cloudformation list-stacks`) and
   resolve each before going on.
5. The stack destroy in step 2 removes the stack's own roles under `/app/`. The sandbox
   administrator deletes any role a person created for the product, and any provisioned
   throughput or quota increase that has a running cost.
6. Leave the budget alarm in place until the month's bill has closed.
7. Run the cost review again the next day: spend per day should fall to near zero. Report any
   service still charging.
8. Record what was removed and what was kept, with the reason, in the brain.
