---
schema_version: 1
id: doc-branching-and-ci
code: OPS-001
title: Branching and CI
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
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

**Force-pushing.** A feature branch may be force-pushed with `git push --force-with-lease` after it
has been rebased onto `origin/dev`; session-close does this before it opens the pull request.
`dev` and `main` are never force-pushed, and the rulesets refuse it (section 9). Plain
`--force` is not used on any branch.

## 2. Before any work, and after any bookkeeping

- Always `git pull --rebase origin dev` before starting any work, in both repositories. `--rebase`
  keeps an unpushed bookkeeping commit on top instead of making a merge commit on `dev`.
- Push right after a claim commit or any other bookkeeping commit. An unpushed claim is invisible
  to the rest of the team and lets two people claim the same phase.

## 3. What goes direct to control `dev`

Control bookkeeping is committed directly on control `dev` and pushed, with no pull request:

- claim commits (session-start),
- completion commits (session-close: `status: complete`, `product_merge`, regenerated catalog),
- idea commits,
- workstream claims,
- a developer's own entry in `docs/systems.yaml` (`ONBOARDING.md`, section 3, step 5).

If the push is rejected because someone else pushed first: `git pull --rebase origin dev`, run the
repository check again, then push. Never force-push.

Everything else, in both repositories, reaches `dev` through a pull request.

On control `dev` this is a rule you follow, not a rule GitHub enforces. Control `dev` has no pull
request requirement, because bookkeeping commits go there directly, so GitHub would accept a
feature branch pushed or merged straight to it. Do not do that: a control feature branch goes
through a pull request like a product one. Product `dev` does enforce it.

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

A repository with no `origin`, or whose `origin` is a path on this machine (tests, local-only use),
is merged locally instead: `git merge --no-ff` into `dev`, then push if a remote exists.
`product.py merge-route` decides from the `origin` URL. A hosted `origin` always takes the pull
request: if `gh` cannot reach it, session-close stops and reports instead of merging locally.

## 5. Releases: `dev` to `main`, and demo tags

For each demo release:

1. The release developer (`OPS-006`, "Roles") opens a pull request from `dev` to `main`; the
   owner merges it with a merge commit. In the
   product repository the `verify` check must pass first. Only the owner can merge into `main`;
   GitHub refuses the merge for anyone else (section 9, "Who merges to `main`").
2. Tag the merge on `main` with an annotated tag: `demo-rc-<n>`, counting up from 1.

   ```bash
   git fetch origin
   git tag -a demo-rc-3 origin/main -m "Demo release candidate 3"
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
| Doctor | `uv run plugins/idea-realization/scripts/doctor.py` |
| Repository check | `uv run plugins/idea-realization/scripts/check.py` |
| Folder tests | `uv run pytest -q test` |
| Plugin tests | `uv run pytest -q`, from `plugins/idea-realization/` |
| Private-content check | `uv run python tools/check_confidential.py` with the deny-list |

Doctor and check run with `IDEA_REALIZATION_ROOT=$GITHUB_WORKSPACE`, so the scripts resolve this
checkout. The test steps run without it: the plugin tests build temporary repositories and fail
when that variable points them at the checkout. No product root is configured in CI, so the product
checks are skipped by design.

There is no scaffold step. A fresh checkout has no `.idea-realization/staging/` directory, because
it is gitignored; doctor reports it as `absent` and does not fail on it. Running the scaffold in CI
would also rewrite the tracked `.idea-realization/install-state.json`.

The deny-list comes from the repository secret `DENY_LIST`, one identifier per line. The workflow
masks each entry in the log, writes the list to `$RUNNER_TEMP`, passes its path in
`PRIVATE_DENY_LIST`, and deletes it after the check. **A missing secret fails the run**, in this
repository and in the product repository alike: a run that could not look for the identifiers has
not shown that none are present. A pull request from a fork gets no secrets, so its run fails too.
The owner sets the secret once in each repository:

```bash
gh secret set DENY_LIST --repo <org>/<control-repo> < .private/deny-list.txt
gh secret set DENY_LIST --repo <org>/<product-repo> < .private/deny-list.txt
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
| `control-main.json` | control | `main` | block force-push and deletion; restrict updates (only the main merger); pull request required, 0 approvals, merge commit only |
| `product-dev.json` | product | `dev` | block force-push and deletion; pull request required, 0 approvals, merge commit only; required check `verify` |
| `product-main.json` | product | `main` | same as `product-dev.json`, plus restrict updates (only the main merger) |
| `demo-tags.json` | both | tags `demo-*` | block deletion, update and force-push |

No ruleset requires linear history, because merges are merge commits. The bypass list is empty in
every ruleset file; the apply script adds the main merger to the two `*-main.json` rulesets when it
applies them, and nothing else has a bypass actor. The required check does not require the branch to be up to date with `dev`
(`strict_required_status_checks_policy: false`): updating the branch would change its head and
break `--match-head-commit <reviewed_commit>`. Session-close rebases onto `origin/dev` before the
review instead.

Repository settings applied with the rulesets: default branch `dev`; merge commits allowed; squash
and rebase merges switched off.

**The owner applies them.** Nothing runs this automatically. Push both `dev` and `main` to the new
repository first, then:

```bash
tools/github/apply_rulesets.sh <org>/<control-repo> control user:<owner-login>
tools/github/apply_rulesets.sh <org>/<product-repo> product user:<owner-login>
```

The third argument names who may merge into `main` (below). Use the same value for both
repositories.

Before it calls GitHub, the script checks that `<org>/<repo>` is the repository this machine's
`.idea-realization/local.yaml` names for that kind: `control_github` for `control`, `product_github`
for `product` (or, when those are unset, the GitHub repository in `control_remote` or
`product_remote`). It refuses when the value is unset or differs, so the control rulesets cannot be
applied to the product repository or the reverse.

The script needs `gh` signed in as an administrator of the repository. It is safe to run again: a
ruleset whose name already exists on the repository is updated in place, otherwise it is created.
It prints each action it took.

**Plan requirement:** rulesets on a private repository need a paid GitHub plan for the
organization. Both repositories live in the owner's work organization, and its plan applies.

### Who merges to `main`

Only the owner merges `dev` into `main`, in both repositories, and GitHub enforces it:

- Both `*-main.json` rulesets carry the `update` rule (shown as "Restrict updates" in GitHub's
  settings): only an actor on the ruleset's bypass list may change `main` at all, and merging a pull
  request into `main` is such a change.
- The apply script puts exactly one actor on that bypass list, the main merger, with bypass mode
  `pull_request`. The main merger can merge a pull request into `main` but cannot push to it
  directly; the pull request rule still applies to them. Everyone else, including other
  administrators acting through a pull request, is refused.
- As committed, the bypass list is empty, so applying a `*-main.json` file by hand (without the
  script) leaves `main` closed to everyone until the script is run.

The actor is given as the script's third argument and its numeric id is looked up on GitHub when
the script runs. No account or team name is written into this repository.

**What the owner sets up**, once:

1. Choose the main merger. The direct form is your own account: `user:<owner-login>`. GitHub has
   accepted individual users as bypass actors on repository rulesets since May 2026 (actor type
   `User`). If the organization's policy does not allow a user bypass, create a team in the
   organization whose only member is you, give it at least write access to both repositories, and
   pass `team:<org>/<team-slug>` instead. Keep that team to one member: everyone in it can merge to
   `main`.
2. Push `dev` and `main` to both repositories, then run the two commands above with that argument.
3. Confirm the result:

   ```bash
   gh api repos/<org>/<control-repo>/rulesets --jq '.[] | "\(.id) \(.name)"'
   gh api repos/<org>/<control-repo>/rulesets/<id of control-main> --jq '.bypass_actors'
   ```

   The second command must print one actor, with `bypass_mode` `pull_request`.
4. If the main merger changes, re-run the script with the new argument. It replaces the bypass list.

What this does not stop: an organization owner or repository administrator can edit or delete the
ruleset itself. That is a GitHub limit; keep the administrator role to the owner.
