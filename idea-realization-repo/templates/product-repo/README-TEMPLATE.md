# Starting the product repository from this template

This directory is the starting content of the **product repository**. The repository owner runs
these steps once. Delete this file from the product repository once step 9 is done.

## What the template contains

| File | Purpose |
|---|---|
| `CLAUDE.md` | Pointer: sessions start in the control repository; branch rules |
| `README.md` | Skeleton with placeholders: product name, stack, run, test |
| `.github/workflows/product-ci.yml` | CI; one job `verify`, the required status check. Never calls AWS or Bedrock |
| `.github/pull_request_template.md` | Phase id, gating verdict record, reviewed commit, verification output |
| `.github/ISSUE_TEMPLATE/blocker.md`, `question.md` | Issue forms for a blocked phase and an open question |
| `.github/CODEOWNERS.example` | Filled from the control repository's `docs/workstreams.yaml`, then renamed |
| `tools/check_confidential.py` | Copy of the control repository's confidential check (standard library only) |
| `tools/git-hooks/pre-commit`, `tools/install-hooks.sh` | Pre-commit hook running that check, and its installer |
| `.gitignore` | Node, Python, CDK output, `.private/`, `.env` files |

There is no deploy workflow. Deploying is done from a developer machine by the control
repository's `aws-deploy` agent.

## Steps

Run from the control repository's root. `<org>/<product>` stands for the product repository's
GitHub name.

1. **Create the empty repository** on GitHub, private, in the team's organization, with no README,
   licence or `.gitignore` (the template provides them).

2. **Copy the template** into a new directory, keeping file modes (the hook and scripts are
   executable), and make the first commit on `main`:

   ```bash
   cp -a templates/product-repo/. ../<product>/
   cd ../<product>
   git init -b main
   git add -A
   git commit -m "Start the product repository from the control repository's template"
   ```

3. **Fill the placeholders** that are known now (every `REPLACE-WITH` in `README.md`; never put
   the repository's URL or `<org>/<product>` name in it, step 9), and remove
   the stack sections of `.github/workflows/product-ci.yml` that will never apply, or leave them:
   a stack's steps are skipped while its manifest file is absent. Commit.

4. **Set the deny-list secret** before the first push; the `verify` job fails without it. Use the
   same deny-list as the control repository (`.private/deny-list.txt`, one identifier per line):

   ```bash
   gh secret set DENY_LIST --repo <org>/<product> < <path to the control repository>/.private/deny-list.txt
   ```

5. **Push `main`, then create `dev` from it:**

   ```bash
   git remote add origin <product repository git URL>
   git push -u origin main
   git switch -c dev
   git push -u origin dev
   ```

   Set `dev` as the default branch in the repository settings, so pull requests target it.

6. **Wait for `verify` to pass** on both pushes (`gh run list --repo <org>/<product>`). A ruleset
   can only require a check GitHub has already seen report.

7. **Apply the rulesets** with the control repository's `tools/github/apply_rulesets.sh`. The script
   refuses unless your own `.idea-realization/local.yaml`, in the control repository's primary
   checkout, names this repository: set `product_github` to `<org>/<product>` and `product_remote`
   to its git URL there first, as step 10 describes for every developer. Then, from the control
   repository's root:

   ```bash
   tools/github/apply_rulesets.sh <org>/<product> product user:<owner-login>
   ```

   The third argument is required: it names the only account (`user:<login>`) or team
   (`team:<org>/<team-slug>`) allowed to merge into `main`. Use the same value as for the control
   repository (the branching guide, `docs/guides/OPS-001-branching-and-ci.md`, section 9). The
   result, as that guide states it:
   - `dev`: no force-push or deletion; pull request required with 0 approvals (the gating review
     is the approval); required status check `verify`; merge commits only.
   - `main`: the same, restricted to the repository owner.
   - Tags `demo-*`: no deletion or update.

8. **Fill CODEOWNERS** from `docs/workstreams.yaml` once the workstreams are claimed: edit
   `.github/CODEOWNERS.example` as its comment says and rename it to `.github/CODEOWNERS`. This
   goes through a pull request to `dev` like any other change.

9. **Check the control repository's product record**, `.idea-realization/product.yaml`: it keeps
   `integration_branch: dev` and `ci_workflow: product-ci.yml`, and carries no URL. The product
   repository's URL and `<org>/<product>` name can contain the organization's name, so they are
   never committed: each developer sets them in step 10. If `product.yaml` needed a change,
   commit it directly to control `dev` and push. The confidential check runs on that commit: a
   value that contains a deny-listed identifier is refused, and must not be forced past the hook.

10. **Each developer**, once per machine: clone the product repository, run
    `tools/install-hooks.sh`, put the deny-list at `.private/deny-list.txt` (or export
    `PRIVATE_DENY_LIST`), and copy the control repository's `.idea-realization/local.example.yaml`
    to `.idea-realization/local.yaml` (untracked) in its primary checkout. Set `product_root` to the
    clone's path, `product_remote` to the product repository's git URL, `product_github` to
    `<org>/<product>`, and `control_remote` and `control_github` to the control repository's.
    `uv run plugins/idea-realization/scripts/product.py verify` in the control repository must
    then succeed, and `uv run plugins/idea-realization/scripts/paths.py show` names `local.yaml`
    as the source of each URL.

## What CI checks

The `verify` job, on every pull request to and push to `dev` and `main`:

1. No AWS credential variable is set in the job.
2. The confidential check, with the deny-list from the `DENY_LIST` secret written to
   `$RUNNER_TEMP` and passed in `PRIVATE_DENY_LIST`. Each identifier is masked in the log first.
3. gitleaks over the whole history, from a pinned release whose checksum is verified.
4. Node (when `package.json` exists): install, `lint`, `test`, `build` where the scripts exist.
5. Python (when `pyproject.toml` exists): `uv sync`, `ruff check`, `pytest`.
6. CDK (when `infra/cdk.json` exists): `cdk synth` without AWS credentials. The app must use
   `CliCredentialsStackSynthesizer` and commit `cdk.context.json` for any context lookup.
7. CDK template check: every synthesized `AWS::IAM::Role` has the path `/app/` and the permission
   boundary `app-permissions-boundary`, and no template creates a customer managed policy, user,
   group, instance profile or service-linked role (the sandbox deploy role cannot).
