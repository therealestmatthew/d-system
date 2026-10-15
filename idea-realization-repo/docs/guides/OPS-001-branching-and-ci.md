---
schema_version: 1
id: doc-branching-and-ci
code: OPS-001
title: Branching and CI
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: []
depends_on: []
---

# Branching and CI

How branches, pull requests, merges, release tags and GitHub CI work in the control repository
(this one) and the product repository.

**Deploy is local only for now.** No workflow here deploys anything. A developer deploys to the AWS
sandbox from their own machine with the `aws-deploy` agent. A draft plan for deploying from GitHub
Actions to AWS through OIDC is `PLAN-002` (`docs/plans/PLAN-002-ci-deploy-to-aws.md`); until the
owner accepts it, CI only verifies.

## 1. Branches

Both repositories have the same two long-lived branches:

| Branch | Role |
|---|---|
| `dev` | Integration branch and the default branch. Every finished phase lands here. |
| `main` | Release branch. Changes only through a release pull request from `dev`. |

Short-lived branches:

| Name | Use | Merged? |
|---|---|---|
| `agent/<phase-id>` | A claimed phase. The same name in both repositories. | Yes, to `dev` by pull request |
| `agent/<handle>-<slug>` | Work the owner directed that has no claimed phase. `<handle>` is the developer's handle. | Yes, to `dev` by pull request |
| `spike/<handle>-<slug>` | An experiment. | Never. Delete it or keep it unmerged. |

Cut every feature branch from `origin/dev` in both repositories. A hotfix is a phase, not a branch
type (section 6).

## 2. Before any work, and after any bookkeeping

- Always `git pull` origin `dev` before starting any work, in both repositories.
- Push right after a claim commit or any other bookkeeping commit. An unpushed claim is invisible
  to the rest of the team and lets two people claim the same phase.

## 3. What goes direct to control `dev`

Control bookkeeping is committed directly on control `dev` and pushed, with no pull request:

- claim commits (session-start),
- completion commits (session-close: `status: complete`, `product_merge`, regenerated catalog),
- idea commits,
- workstream claims.

If the push is rejected because someone else pushed first: `git pull --rebase origin dev`, run the
repository check again, then push. Never force-push.

Everything else, in both repositories, reaches `dev` through a pull request.

## 4. Merging a phase: pull request with a merge commit

Feature branches reach `dev` only through a pull request merged with a **merge commit**. Squash and
rebase merges are switched off in both repositories, because they create new commits and the
reviewed commit would no longer be in `dev`'s history.

The passing gating review is the approval for both merges. No separate owner approval is needed per
merge, and the rulesets require 0 approving reviews.

The sequence, as session-close runs it:

1. Rebase both feature branches onto `origin/dev`; run verification and the gating review.
2. Push both feature branches. Open (or reuse) a pull request to `dev` in each repository:
   `gh pr create --base dev`.
3. Control pull request:
   `gh pr merge <n> --merge --match-head-commit <control HEAD>`.
4. Product pull request: wait for the required check `verify` (`gh pr checks <n> --watch`), then
   `gh pr merge <n> --merge --match-head-commit <reviewed_commit>`.
   `--match-head-commit` makes GitHub refuse the merge if the branch head moved after the review.
5. **Second-parent check.** Fetch, then confirm in the product repository:

   ```bash
   git fetch origin
   git rev-parse <merge commit>^2    # must equal reviewed_commit
   ```

   The pull request head, the merge commit's second parent and the gating verdict's
   `reviewed_commit` must be the same commit. If they differ, stop and report it.
6. Completion commit direct to control `dev` (section 3): `status: complete`,
   `product_merge: <merge commit>`, catalog regenerated, check run, `git pull --rebase`, push.
7. If step 6 fails after the product merged, retry the pull, rebase and push. Never revert the
   product merge. The phase stays `active` until the completion commit lands.

A repository with no GitHub remote (tests, local-only use) uses a local fallback instead: `git merge
--no-ff` into `dev`, then push if a remote exists.

## 5. Releases: `dev` to `main`, and demo tags

For each demo release:

1. Open a pull request from `dev` to `main` and merge it with a merge commit. In the product
   repository the `verify` check must pass first.
2. Tag the merge on `main` with an annotated tag: `demo-rc-<n>`, counting up from 1.

   ```bash
   git fetch origin && git checkout main && git pull origin main
   git tag -a demo-rc-3 -m "Demo release candidate 3"
   git push origin demo-rc-3
   ```

3. Tag the release that is shown on demo day `demo-final` as well.

Tag the control repository's `main` with the same name at the same time, so the two repositories
can be matched to each other.

`demo-*` tags cannot be moved or deleted once pushed (the `demo-tags` ruleset). If a tag is wrong,
make a new release candidate with the next number.

**Rollback:** redeploy the previous `demo-rc-<n>` tag with the `aws-deploy` agent. Do not move or
delete tags and do not rewrite `main`.

## 6. Code freeze and hotfixes

Code freeze is **2026-11-03** (demo day is 2026-11-05). After the freeze, only hotfix phases are
built.

A hotfix is a normal phase: the fix is recorded as an idea, the owner registers a phase for it at
the front of `next_up`, and it goes through the usual claim, gating review and pull request merge.
It then goes to `main` in a new release pull request and gets the next `demo-rc-<n>` tag.

## 7. CI: the control repository

Workflow: `.github/workflows/control-ci.yml`. One job, `verify`.

Triggers: every pull request to `dev` or `main`, and every push to `dev`, `main` or `agent/**`.
Runs are grouped per ref; a new push cancels the run still in progress for the same ref.

Steps, in order:

| Step | Command |
|---|---|
| Install | `astral-sh/setup-uv` with Python 3.12, cache keyed on `uv.lock`; `uv sync --locked --extra dev` |
| Lint | `uv run ruff check tools/ test/` |
| Scaffold | `uv run plugins/idea-realization/scripts/scaffold.py --feature all` |
| Doctor | `uv run plugins/idea-realization/scripts/doctor.py` |
| Repository check | `uv run plugins/idea-realization/scripts/check.py` |
| Folder tests | `uv run pytest -q test` |
| Plugin tests | `uv run pytest -q`, from `plugins/idea-realization/` |
| Private-content check | `uv run python tools/check_confidential.py` with the deny-list |

Scaffold, doctor and check run with `IDEA_REALIZATION_ROOT=$GITHUB_WORKSPACE`, so the scripts
resolve this checkout. The test steps run without it: the plugin tests build temporary repositories
and fail when that variable points them at the checkout. No product root is configured in CI, so
the product checks are skipped by design. The scaffold runs first because it recreates the
gitignored `.idea-realization/staging/` directory, which doctor otherwise reports missing.

The deny-list comes from the repository secret `DENY_LIST`, one identifier per line. The workflow
masks each entry in the log, writes the list to `$RUNNER_TEMP`, passes its path in
`PRIVATE_DENY_LIST`, and deletes it after the check. Without the secret (for example on a pull
request from a fork), only the path check runs and the run shows a warning. The owner sets the
secret once:

```bash
gh secret set DENY_LIST --repo <org>/<control-repo> < .private/deny-list.txt
```

The control job is not a required check: bookkeeping commits go to `dev` directly and must not wait
for CI. A red run on `dev` or `main` is an alarm; fix it forward with a new commit.

## 8. CI: the product repository

The product workflow, `.github/workflows/product-ci.yml`, ships in the product-repository template
(`templates/product-repo/`). Its job is also named `verify`, and it never deploys or calls AWS or
Bedrock. The rulesets require a check named exactly `verify` reported by GitHub Actions, so the job
must keep that id and must not set a different `name:`.

## 9. Rulesets

Branch and tag protection is defined as GitHub repository rulesets in `.github/rulesets/`:

| File | Repository | Protects | Rules |
|---|---|---|---|
| `control-dev.json` | control | `dev` | block force-push and deletion; no pull request requirement (bookkeeping is direct) |
| `control-main.json` | control | `main` | block force-push and deletion; pull request required, 0 approvals, merge commit only |
| `product-dev.json` | product | `dev` | block force-push and deletion; pull request required, 0 approvals, merge commit only; required check `verify` |
| `product-main.json` | product | `main` | same as `product-dev.json` |
| `demo-tags.json` | both | tags `demo-*` | block deletion, update and force-push |

No ruleset requires linear history, because merges are merge commits. The bypass list is empty in
every ruleset. The required check does not require the branch to be up to date with `dev`
(`strict_required_status_checks_policy: false`): updating the branch would change its head and
break `--match-head-commit <reviewed_commit>`. Session-close rebases onto `origin/dev` before the
review instead.

Repository settings applied with the rulesets: default branch `dev`; merge commits allowed; squash
and rebase merges switched off.

**The owner applies them.** Nothing runs this automatically. Push both `dev` and `main` to the new
repository first, then:

```bash
tools/github/apply_rulesets.sh <org>/<control-repo> control
tools/github/apply_rulesets.sh <org>/<product-repo> product
```

The script needs `gh` signed in as an administrator of the repository. It is safe to run again: a
ruleset whose name already exists on the repository is updated in place, otherwise it is created.
It prints each action it took.

**Plan requirement:** rulesets on a private repository need a paid GitHub plan for the
organization. Both repositories live in the owner's work organization, and its plan applies.

**Who merges to `main`:** `control-main.json` requires a pull request with an empty bypass list,
but a ruleset cannot by itself limit *who* merges a pull request. Releasing to `main` is the owner's
job by agreement. Enforcing it would need a ruleset `update` rule with the owner as a bypass actor,
which this kit does not do.
