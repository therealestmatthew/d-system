---
schema_version: 1
id: doc-validating-mode
code: OPS-004
title: Validating mode
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Validating mode

How plans, phase branches, infrastructure and spend are reviewed, which reviewer does each, and what
a reviewer's verdict decides. Reviewers change nothing: every reviewer agent below is read-and-run
only and spawns no subagents. The one-page command list is in the mode cheat sheets (`OPS-009`).

Run `/idea-realization:start` and choose Validating. Then `git pull --rebase origin dev` in the control primary checkout
before any work.

## The rules every review follows

- **A fresh agent of a dedicated reviewer type.** Never a fork of the session that did the work,
  which carries its conclusions, and never a general-purpose agent.
- **Evidence, not rationale.** A verdict rests on commands the reviewer ran and their real output,
  or on diff hunks. The builder's explanation is not evidence
  (`plugins/idea-realization/docs/role-contracts.md`, section 2).
- **Every verdict on a phase diff is recorded** as a JSON file under `docs/reviews/`, named
  `<date>-<phase-id>-<reviewer type>.json`, valid against
  `.idea-realization/schemas/review-verdict.schema.json`. `reviewed_commit` is the full commit the
  reviewer judged; `gating` is `true` when the verdict decided the merge and `false` when it ran in
  shadow. Findings are copied as written.
- **Every finding is fixed or accepted** by the developer who owns the workstream it is in, with the
  disposition recorded. A fix that changes the diff needs a fresh review of the new commit.

## Which reviewer, when

| What is reviewed | Reviewer | When | What its verdict decides |
|---|---|---|---|
| A phase's product diff | `phase-adversary` | Every phase, in `session-close` step 3 | Gating: the phase may merge only on a pass |
| A narrow code change against one requirement | `validator-code` | Instead of `phase-adversary`, when the phase is that narrow | Gating |
| The same phase diff | `review-judge` | Beside every gating review | Nothing: shadow only |
| Mechanical gates on a branch | `validator-check` | Before a gating review, or whenever a branch's checks need running | Pass or fail per gate; no judgement |
| An infrastructure diff | `aws-infra-reviewer` | Every phase whose diff changes infrastructure code, before `aws-deploy` applies it | Ranked findings; each is fixed or accepted like any other finding |
| Sandbox spend and idle resources | `aws-cost-optimizer` | Once per working day | Recommendations only (`OPS-007`) |
| A plan and its requirement | `plan-adversary` | Each new plan, at three altitudes | Findings for the planner's dispositions; approval stays with the owner |
| A batch composition | `batch-validator` | Each proposed batch, before the owner approves it | Evidence for the owner; not approval |

## Phase reviews

### The gating review

The `session-close` skill runs it (step 3) after rebasing both branches and running the
verification. Its brief to the reviewer contains:

- the phase id with its `scope`, `acceptance`, `verification` and `deliverables` pasted in;
- the product worktree path and the range `origin/dev...HEAD`, and the control worktree path and the
  same range there, for the reviewer to diff and log itself;
- the paths of the phase's requirement and plan;
- the verification output, as evidence it may re-run but must not take on trust.

`phase-adversary` replies with a first line `VERDICT: pass` or `VERDICT: reject`, the phase id and the reviewed
commit, then a judgement per acceptance condition, then ranked findings. The session records it with
`gating: true` (the schema's `verdict` values are `pass` and `reject`). A passing gating verdict is
the approval for merging both the product and the control pull requests. Two rejects in a row on the
same finding: the phase stays `active` and goes to the owner.

### The shadow judge: `review-judge`

`review-judge` judges the same diff without a shell. It has no tool that runs a command, so its
brief must carry everything: the phase's `scope`, `acceptance` and `verification`, the commit range
and its diff, and evidence files holding the captured output of each verification command and gate
check, each with its command and exit code. It is briefed by the session running the review, never
by the session that built the phase.

Its verdict is recorded with `gating: false` and decides nothing. It runs in shadow until the owner
decides whether to promote it, by comparing its verdicts with the gating reviewer's.

**What exists today:** the `session-close` skill's text names only the gating reviewer. Dispatching
`review-judge` and writing its evidence files is a step the reviewing session does by hand, after
the gating review's verification run, against the same `reviewed_commit`. This repository has no
script that writes the evidence files.

### Mechanical gates: `validator-check`

Dispatch it with an absolute worktree path and the exact checklist, usually:

- `IDEA_REALIZATION_ROOT=<control worktree> uv run plugins/idea-realization/scripts/check.py`;
- `uv run python tools/check_confidential.py`, with the changes staged first, because it reads
  `git ls-files`;
- the test commands, and the product's own test and lint commands for the product worktree;
- drift checks such as a regenerated catalog that must diff clean.

It reports each gate's real result, with failures verbatim.

## Infrastructure and spend

### `aws-infra-reviewer`

Dispatch it for every phase whose product diff touches infrastructure code, before `aws-deploy`
applies the change, with the diff and the phase's acceptance or requirement. It reads the sandbox
through `tools/aws-sandbox` with the read role, compares live resources with the code where the
change is already deployed, and reports ranked findings: IAM scope, public exposure, encryption,
secrets, tags, alarms and logging, idle cost, and resources a later deploy would replace. Findings
are fixed or accepted by the workstream's owner, like gating findings. It does not replace the
gating review of the phase.

### `aws-cost-optimizer`

Once per working day, a validator dispatches it with the prompt in `OPS-007`, "Daily cost review",
posts the spend and the idle-resource list to the team, and each resource's owner keeps it with a
reason or asks `aws-deploy` to remove it.

## Plan and batch reviews

- **Plans:** `plan-adversary`, once per altitude (plan, phase, later-added-phase), with the filled
  prompt from `plugins/idea-realization/docs/adversary-prompt.md`, after the plan passes the
  `plan-check` skill. The procedure and the review record are in
  `plugins/idea-realization/docs/plan-review.md`, section 3; the order within planning is in
  `OPS-002`.
- **Queued phases under a review pack:** a review session working under a prompt pack the owner
  approved may edit the in-scope queued phases' backlog lines, never `next_up`, `status` or `agent`
  (`plan-review.md`, section 4, and `plugins/idea-realization/docs/prompt-packs.md`).
- **Batches:** `batch-validator`, which runs `plugins/idea-realization/scripts/batch_check.py
  <batch-id>` and the repository check, then judges the rules in
  `plugins/idea-realization/docs/batches.md`. Its first line is `VERDICT: pass <batch-id>` or
  `VERDICT: reject <batch-id>`.

## Reviewing a peer's ready branch

**What exists today:** there is no `review` skill. The gating review is run by the `session-close`
skill inside the session that holds the phase, and it is that session that records the gating
verdict and merges. A second developer can still review a peer's pushed branch by hand, with the
same agents. Such a review does not replace the gating review in the peer's `session-close`.

1. In each primary checkout, `git fetch origin` and confirm the peer has pushed
   `agent/<phase-id>`. If not, ask them to push it; pushing their own branch needs no approval.
2. Create a detached review worktree in each repository, outside the repository, at the pushed
   commit, so nothing you do moves the peer's branch:

   ```bash
   git -C <product checkout> worktree add --detach <product worktree dir>/review-<phase-id> origin/agent/<phase-id>
   git worktree add --detach <worktree dir>/review-<phase-id> origin/agent/<phase-id>
   ```

   Install the product worktree's own environment there; never link the peer's.
3. Note the product commit you will review: `git -C <product review worktree> rev-parse HEAD`.
4. Dispatch a fresh `phase-adversary` (or `validator-code`) with the brief `session-close` step 3
   describes: the phase's `scope`, `acceptance`, `verification` and `deliverables` from the backlog
   on control `dev`, both review worktree paths with the range `origin/dev...HEAD`, and the
   requirement and plan paths. Give it no explanation from the peer.
5. Send the peer the full reply, with the reviewed commit, so they can fix or accept each finding.
   Do not commit a verdict record on the peer's branch: their branch, their records.
6. Remove both review worktrees from the primary checkouts with `git worktree remove`.

Whether a peer's review may stand as the gating review, and how it would be recorded, is not
settled; until the owner decides, the gating verdict is the one `session-close` records.
