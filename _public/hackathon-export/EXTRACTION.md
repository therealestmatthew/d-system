# Extracting the control and product repositories

This guide takes the export in this directory and turns it into two private GitHub repositories in
the work organization: the **control repository** (ideas, plans, backlog, review records, agents,
the plugin) and the **product repository** (the product's code and CI). It is written for the
repository owner, who does this once. Do the steps in order; each one says what success looks like
and what to do if it fails.

Built from dev commit 322d78f6

## Placeholders used below

Replace each one, including the angle brackets. No value you type here goes into a tracked file
unless a step says so.

**Names and paths**

| Placeholder | Meaning |
|---|---|
| `<export>` | The absolute path of this directory |
| `<org>` | The work organization's GitHub login |
| `<control-repo>` | The control repository's name (step 0.3) |
| `<product-repo>` | The product repository's name (step 0.3) |
| `<work>` | The directory that will hold both checkouts side by side, for example `~/work` |
| `<deny-list>` | The path of the deny-list file you already hold (one identifier per line) |

**You and your team**

| Placeholder | Meaning |
|---|---|
| `<owner-login>` | Your GitHub login in the work organization |
| `<your work name>` | The name your commits in the work organization carry |
| `<your work email>` | The email your commits in the work organization carry |
| `<handle>` | Your developer handle: lower-case letters and digits, starting with a letter, at most 16 characters |
| `<team-slug>` | A one-member team's slug, only if the organization refuses a user as main merger (step 4.2) |
| `<their-login>` | A developer's GitHub login (step 6.4) |

**AWS (step 5)**

| Placeholder | Meaning |
|---|---|
| `<account id>` | The sandbox account's 12-digit id |
| `<region>` | The sandbox region |
| `<trail name>` | The name of the account's baseline CloudTrail trail |
| `<product name>` | The product's short name: lowercase letters, digits and hyphens, starting with a letter. It replaces `REPLACE_WITH_PRODUCT_NAME`, prefixes the tenant key aliases, the stack names and the function, state machine and build project names, and is the value of the `project` tag |
| `<principal ARN>` | The ARN of a principal your developers sign in as (step 5.3) |
| `<read-role-name>`, `<deploy-role-name>` | The names you give the read role and the deploy role |
| `<read-guard-policy-name>`, `<read-sandbox-data-policy-name>`, `<deploy-policy-name>`, `<deploy-scope-policy-name>` | The names you give the four customer managed policies created from the repository's policy files (the fifth, `app-permissions-boundary`, has a fixed name) |
| `<your sandbox login profile>` | The AWS CLI profile you sign in to the sandbox with (step 5.9) |

**Values that commands print**

| Placeholder | Meaning |
|---|---|
| `<number>` | A pull request number, as `gh pr create` prints it |
| `<run id>` | A workflow run id, as `gh run list` prints it |
| `<id of control-main>`, `<id of product-main>`, `<id of demo-tags-create>`, `<id of demo-tags-protect>` | A ruleset's numeric id, as the first query for that repository in step 4.4 prints it |
| `<n>`, `<m>` | Counts in a success line; the step says what they must be |

**Other placeholders**

| Placeholder | Meaning |
|---|---|
| `<repo>` | Either repository's name, where a step applies to both |
| `<path to this export>` | In `owner-files/brain-drafts/index.md`: the same value as `<export>` (step 6.2) |
| `<product repository URL>`, `<product>` | In the developers' commands quoted in step 6.5: the product repository's git URL and the directory name of their product checkout |
| `<user name>` | An IAM user's name in the sandbox, only if your developers sign in as IAM users (step 5.3) |
| `<slug>`, `<id>` | A short branch-name suffix, and a workstream id, in text that describes the developers' own commands |
| Text in angle brackets inside a command's argument, such as `--body "<amount, ...>"` | What to write there, described in the step |

---

## 0. Before you start

### 0.1 What is in this directory

| Path | What it is |
|---|---|
| `control.bundle` | The control repository as a git bundle: one initial commit, branches `main` and `dev` at that commit. The repository is created from this file. |
| `product.bundle` | The product repository seed as a git bundle: one initial commit, `main` and `dev` at that commit. The repository is created from this file. |
| `control-repo/` | A plain copy of the control repository's files, for reading. It has no `.git` directory and no history. |
| `product-seed/` | A plain copy of the product seed's files, for reading. It has no `.git` directory and no history. |
| `owner-files/brain-drafts/` | 28 drafts of brain entries about the product, and `index.md` with one command to record each (step 6.2). |
| `owner-files/workstreams-proposal.yaml` | A draft of the five workstreams, for you to edit into `docs/workstreams.yaml` (step 6.3). |
| `EXTRACTION.md` | This guide. |

`control-repo/` and `product-seed/` are not git repositories, and nothing in this guide runs git in
them. Both repositories are created by cloning the bundles (steps 1.4 and 2.3). Each bundle carries
one initial commit, authored with the identity of the machine that built the export; you re-author
that commit before the first push (step 0.4). The plain copies hold the same files as that commit.

The export was verified before hand-over: in a clone of `control.bundle`, the folder tests (one
test is skipped when `shellcheck` is not installed), the plugin tests, the scaffold and doctor,
the repository check and the developer guidebook check passed. Step 1.7 runs the tests, the
repository check, the guidebook check and the private-content check again on the work machine.

### 0.2 What you need

- **The work machine.** Copy this directory to the machine you work on for the organization, and
  follow this guide there. Every step runs on the work machine except steps 5.2 to 5.7, which run
  in AWS CloudShell. The re-authoring of the initial commits (steps 1.5 and 2.4) and your developer
  registration (step 6.1) use the work identity configured on that machine.
- **GitHub:** owner or admin rights in the work organization (to create repositories, set secrets
  and apply rulesets). Rulesets on a private repository need a paid plan for the organization. An
  organization owner can check the plan before starting:

  ```bash
  gh api orgs/<org> --jq .plan.name
  ```

  `free` means rulesets cannot be applied to private repositories. If it prints `null` or nothing,
  your account cannot see the plan; you will then find out in step 4.3, where a plan without rulesets
  returns HTTP 403.
- **`gh`**, signed in to an account that administers the organization's repositories:

  ```bash
  gh auth status
  ```

  Success: it names your work account and `github.com`. If the organization uses SAML single
  sign-on, the token must be authorized for the organization; `gh auth login` again if API calls
  later return 403 with an SSO message.
- **AWS:** administrator access to the sandbox account, through the AWS console. Step 5 runs the
  administrator commands in AWS CloudShell, so no administrator credentials are stored on a
  machine that runs agents.
- **The deny-list file** (`<deny-list>`): one identifier per line, the identifiers that must never
  reach a tracked file. It must name at least one identifier; an empty list fails the check.
- **`uv`**, **`git`**, **`python3`** and **Claude Code** (`claude`) on the work machine, and the AWS
  CLI v2 for step 5.9.
- **Your work git identity**: the name and email your commits in the work organization should carry.
  Your work email is not confidential: it appears in your commits and in `docs/systems.yaml`
  (step 6.1). Do not put it in the deny-list, or the hooks refuse those commits. The organization
  name is different: it stays out of tracked files, and the repositories' URLs are kept only in the
  gitignored `.idea-realization/local.yaml` (step 3.3).

### 0.3 Choose the repository and directory names

Pick `<control-repo>` and `<product-repo>`, and clone each into a directory with the **same name as
the repository**. The worktree directories the steps below create are named after the checkout
(`<control-repo>-worktrees`, `<product-repo>-worktrees`).

Ordinary words are fine for the organization, the repository names, the checkout directories and
your git identity.

### 0.4 Re-author the initial commits on the work machine

Both bundles' initial commits carry the git identity of the machine that built the export: a
personal name and email. Before anything is pushed to the work organization, re-author them on the
work machine with your work identity. You do this in the fresh clone of each bundle on the work
machine, before the first push: step 1.5 for the control repository and step 2.4 for the product
repository. The commands are:

```bash
git config user.name "<your work name>"
git config user.email "<your work email>"
git checkout main
git commit --amend --reset-author --no-edit
git branch -f dev main
```

`--reset-author` replaces the author with the configured identity and the author date with now;
`git branch -f dev main` points `dev` at the new commit, so both branches stay identical. The old
commit stays only in the local reflog and is never pushed.

---

## 1. Create the control repository

All commands run from `<work>` unless a step says otherwise.

### 1.1 Check the bundle

```bash
git bundle list-heads <export>/control.bundle
```

Success: three lines with the same commit hash: `refs/heads/dev`, `refs/heads/main` and `HEAD`.
If it fails: the file is damaged or incomplete; copy it again.

### 1.2 Create the empty repository on GitHub

```bash
gh repo create <org>/<control-repo> --private
```

Success: it prints the repository's URL. Do not add a README, licence or `.gitignore`.
If it fails: "Name already exists" means choose another name; a permission error means your
account cannot create repositories in `<org>`: ask an organization owner for the right, or to
create the empty repository for you.

### 1.3 Set the deny-list secret before the first push

The control CI fails on every run while the `DENY_LIST` secret is missing, and the first push
starts a run. Set it now:

```bash
gh secret set DENY_LIST --repo <org>/<control-repo> < <deny-list>
gh secret list --repo <org>/<control-repo>
```

Success: the list shows `DENY_LIST`. If `gh secret set` is refused, your account is not an admin
of the repository.

### 1.4 Clone the bundle

```bash
mkdir -p <work>
cd <work>
git clone <export>/control.bundle <control-repo>
cd <control-repo>
git branch -a
```

Success: `* main`, plus `remotes/origin/dev` and `remotes/origin/main`. This clone becomes your
primary checkout of the control repository; you keep working in it.

### 1.5 Re-author the initial commit (step 0.4)

On the work machine, in `<work>/<control-repo>`:

```bash
git config user.name "<your work name>"
git config user.email "<your work email>"
git checkout main
git commit --amend --reset-author --no-edit
git branch -f dev main
git log --format='%h %an <%ae>' main dev
git rev-parse main dev
```

Success: `git log` shows one commit with your work identity; the two `rev-parse` lines are the same
hash. If `git branch -f dev main` says the branch is checked out, run `git checkout main` first.

The repository's git hooks are not installed yet, so this amend runs no checks. Step 3.2 installs
them; from then on every commit and push in either repository is checked.

### 1.6 Point `origin` at GitHub

The clone's `origin` is the bundle file. Replace it:

```bash
git remote remove origin
git remote add origin git@github.com:<org>/<control-repo>.git
git remote -v
```

Use `https://github.com/<org>/<control-repo>.git` instead if you push over HTTPS. Note the exact
URL you used: step 3.3 needs the same string.

### 1.7 Run the tests and the confidentiality check before pushing

```bash
uv sync --extra dev
uv run pytest -q test
(cd plugins/idea-realization && uv run pytest -q)
uv run plugins/idea-realization/scripts/check.py
uv run python tools/build_guidebook.py --check
PRIVATE_DENY_LIST=<deny-list> uv run python tools/check_confidential.py
```

Do not `export` `IDEA_REALIZATION_ROOT` in this shell: with it set, the plugin tests fail.

Success: the folder tests pass (one test may be skipped when `shellcheck` is not installed), the
plugin tests pass, `check.py` exits 0, `build_guidebook.py --check` ends with
`docs/guidebook.html matches its inputs`, and the last command prints
`check_confidential: OK (<n> tracked files, <m> identifiers checked)`, where `<m>` is the number of
identifiers in your deny-list and greater than 0. A count of 0 means the deny-list was not read.

If `check_confidential` prints `FAILED`, each line names a file and the identifier it contains. Do
not push: report it, because the export itself carries the identifier.

If `test_plugin_names_no_source_instance` fails, the line it prints names a plugin file that
contains your `<org>/<control-repo>` string. Do not push: report it.

### 1.8 Push both branches and set `dev` as the default branch

```bash
git push -u origin main dev
gh repo edit <org>/<control-repo> --default-branch dev
git switch dev
gh run list --repo <org>/<control-repo> --limit 4
```

`git switch dev` puts the primary checkout on `dev`, the branch every later step and every
session expects it to be on. From here on, never switch the primary checkout's branch: other work
happens in worktrees.

Success: both branches are pushed; the run list shows `control-ci` runs for `main` and `dev`.
Watch one to the end with `gh run watch --repo <org>/<control-repo>`.

These first runs are expected to fail. Control CI checks out the product repository with a
read-only token, and neither the product repository nor the token exists yet. Each run passes the
install, lint and doctor steps and then fails at `Product repository settings` with:

```
The repository secret PRODUCT_READ_TOKEN is not set (a pull request from a fork never receives it). The repository owner creates a read-only token for the product repository and sets it: gh secret set PRODUCT_READ_TOKEN. See docs/guides/OPS-001-branching-and-ci.md.
```

Step 2.7 sets the token and re-runs them; from then on control CI must finish green.

If a run fails earlier than that step:

- The run never starts, or fails at "Set up job" saying an action is not allowed: the organization
  restricts GitHub Actions. The workflow uses `actions/checkout` and `astral-sh/setup-uv`; allow
  both in the organization's or repository's Actions settings.
- Read any other failing step with `gh run view <run id> --repo <org>/<control-repo> --log-failed`.

---

## 2. Create the product repository

The same procedure, from `product.bundle`. The product CI's job is named `verify`; the product
rulesets will require it, and GitHub can only require a check it has seen report, so the first
runs must finish before step 4.3.

### 2.1 Check the bundle

```bash
git bundle list-heads <export>/product.bundle
```

Success: three lines with the same hash (`dev`, `main`, `HEAD`).

### 2.2 Create the repository and set its secret

```bash
gh repo create <org>/<product-repo> --private
gh secret set DENY_LIST --repo <org>/<product-repo> < <deny-list>
gh secret list --repo <org>/<product-repo>
```

Success and failure: as steps 1.2 and 1.3.

### 2.3 Clone the bundle

```bash
cd <work>
git clone <export>/product.bundle <product-repo>
cd <product-repo>
```

### 2.4 Re-author the initial commit (step 0.4)

On the work machine, in `<work>/<product-repo>`, the same commands as step 1.5:

```bash
git config user.name "<your work name>"
git config user.email "<your work email>"
git checkout main
git commit --amend --reset-author --no-edit
git branch -f dev main
git log --format='%h %an <%ae>' main dev
git rev-parse main dev
```

### 2.5 Check for confidential identifiers, then push

```bash
PRIVATE_DENY_LIST=<deny-list> python3 tools/check_confidential.py
git remote remove origin
git remote add origin git@github.com:<org>/<product-repo>.git
git push -u origin main dev
gh repo edit <org>/<product-repo> --default-branch dev
git switch dev
```

Success: the check prints `check_confidential: OK (<n> tracked files, <m> identifiers checked)`,
with `<m>` greater than 0, before anything is pushed. As in step 1.8, the primary checkout stays on
`dev` from here on.

### 2.6 Wait for `verify` to pass on both branches

```bash
gh run list --repo <org>/<product-repo> --limit 4
gh run watch --repo <org>/<product-repo>
```

Success: `product-ci` finished green for `main` and for `dev`. With no `package.json`,
`pyproject.toml` or `infra/cdk.json` yet, the job runs only the credential check, the confidential
check and the gitleaks secret scan; the stack steps are skipped.

If it fails: as step 1.8. The gitleaks step downloads a release from GitHub; a network or checksum
failure there is a runner problem, so re-run the job.

The product repository keeps `README-TEMPLATE.md` for now. It is removed by the first pull request
in step 8.2, which also tests the product rules.

### 2.7 Give control CI a read-only token for the product repository

Control CI checks out the product repository read-only, so that the repository check can confirm
that every recorded product merge exists in the product repository. Without a token for it, every
control CI run fails, as the runs in step 1.8 did. The authority is `OPS-001`, section 7.

Create the token in GitHub, signed in as your work account: a fine-grained personal access token
(**Settings > Developer settings > Personal access tokens > Fine-grained tokens**), or a GitHub App
installation token. Give it these settings and nothing more:

- **Resource owner:** `<org>`. If the organization requires approval of fine-grained tokens, the
  token stays pending until an organization administrator approves it, and the checkout fails until
  then.
- **Repository access:** **Only select repositories**, with `<org>/<product-repo>` as the only one.
- **Repository permissions:** **Contents: Read-only**. GitHub adds **Metadata: Read-only** itself as
  mandatory. No write permission, no other repository, no account or organization permission.
- **Expiration:** a date at most 366 days ahead (an organization policy can set a shorter maximum).
  Note the date.

A GitHub App token takes the same settings: installed on the product repository only, with Contents
read-only and Metadata read-only.

You own the token and its rotation. Before it expires, create a new one with the same settings,
replace the secret with the first command below, and delete the old token.

Set it, and the product repository's name, on the control repository. The name goes into the
repository variable `PRODUCT_GITHUB`: the workflow falls back to a `github:` field in
`.idea-realization/product.yaml`, and the export's `product.yaml` has none, because the name can
contain the organization's. The token goes only into the secret, never into a file; `gh secret set` prompts for the value, so it is not left in the shell
history:

```bash
gh secret set PRODUCT_READ_TOKEN --repo <org>/<control-repo>
gh variable set PRODUCT_GITHUB --repo <org>/<control-repo> --body <org>/<product-repo>
gh secret list --repo <org>/<control-repo>
gh variable list --repo <org>/<control-repo>
```

Then re-run the control runs from step 1.8, one for `dev` and one for `main`:

```bash
gh run list --repo <org>/<control-repo> --limit 4
gh run rerun <run id> --repo <org>/<control-repo>
gh run watch --repo <org>/<control-repo>
```

Success: the secret list shows `DENY_LIST` and `PRODUCT_READ_TOKEN`; the variable list shows
`PRODUCT_GITHUB` with the value `<org>/<product-repo>`; both re-runs finish green, and the
`Repository check` step's log shows `origin: matches` from `product.py verify`.

If a run fails:

| Step and message | Fix |
|---|---|
| `Product repository settings`: "The repository secret PRODUCT_READ_TOKEN is not set" | The secret is missing: run the `gh secret set PRODUCT_READ_TOKEN` command above |
| `Product repository settings`: "The product repository is not named" | The variable is missing: run the `gh variable set PRODUCT_GITHUB` command above |
| `Check out the product repository (read-only)`: `Bad credentials`, `Repository not found` or `could not read Username` | The token has expired or been revoked, is still pending the organization's approval, or does not include the product repository with Contents read-only. GitHub answers a token that cannot see a private repository with `Repository not found`. Create a new token with the settings above, set the secret again, delete the old token, and re-run |
| `Private-content check`: "The repository secret DENY_LIST is not set" | Step 1.3 was skipped: set it and re-run |

Do not remove the product steps from the workflow or widen the token's permissions to make a run
pass (`OPS-008`, "Control CI cannot read the product repository").

---

## 3. Configure your machine

Every developer does this once per machine; `ONBOARDING.md`, section 3, is their version. These are
your steps, as owner.

### 3.1 The deny-list in both primary checkouts

```bash
mkdir -p <work>/<control-repo>/.private <work>/<product-repo>/.private
cp <deny-list> <work>/<control-repo>/.private/deny-list.txt
cp <deny-list> <work>/<product-repo>/.private/deny-list.txt
```

`.private/` is gitignored in both repositories. Never copy anything from it into a tracked file.
Worktrees read the deny-list from the primary checkout, so it is needed only there.

### 3.2 Install the git hooks

```bash
git -C <work>/<control-repo> config core.hooksPath tools/git-hooks
cd <work>/<product-repo> && tools/install-hooks.sh
```

Both repositories keep their hooks in the tracked directory `tools/git-hooks/` and use them through
`core.hooksPath`, so every worktree of the clone uses the same hooks and a pull that changes a hook
updates it. In the control repository you set `core.hooksPath` yourself (the first command; it
prints nothing). In the product repository `tools/install-hooks.sh` sets it and makes the hooks
executable.

Success: `git -C <work>/<control-repo> config core.hooksPath` prints `tools/git-hooks`. The product
script prints `core.hooksPath set to tools/git-hooks` and `deny-list: .private/deny-list.txt`. If
it prints `WARNING: no deny-list found; the hook will only run the private-directory path check.`,
step 3.1 did not put the file in place.

What each hook enforces:

| Hook | Control repository | Product repository |
|---|---|---|
| `pre-commit` | `tools/check_confidential.py` on the staged files (no deny-listed identifier in any tracked path or content, no tracked file under `.private/`), then the repository check `check.py` (a stale catalog or idea view included) | `tools/check_confidential.py` on the staged files, the same checks |
| `commit-msg` | `check_confidential.py --message`: no deny-listed identifier in the commit message | The same |
| `pre-push` | `check_confidential.py --pre-push`: every commit the push sends that the remote does not have, on every ref including tags (its message, and the paths and lines it adds); then `check.py` on the checked-out tree | `check_confidential.py --pre-push`, the same commits; no repository check |

`pre-push` exists because a commit made by `git rebase`, `git pull --rebase`, `git cherry-pick` or
`git commit --no-verify` skips `pre-commit` and `commit-msg`. The control hooks run through
`uv run`; the product hooks run `python3`, or `uv run --no-project python` when `python3` is not
on the path.

**When `.private/deny-list.txt` is missing.** The hooks look for the deny-list in
`PRIVATE_DENY_LIST` if set, then in the checkout's `.private/deny-list.txt`, then in the primary
checkout's (worktrees have no `.private/` of their own). When none exists, every hook run prints a
banner on standard error, `WARNING: check_confidential found NO deny-list.` followed by
`Confidential identifiers were NOT checked.`, and passes with only the private-directory path
check. That warning on any commit means the identifiers were not checked: put the file in place
(step 3.1) before committing further. A deny-list that exists but names no identifier fails the
check. In CI there is no fallback: both workflows fail when the `DENY_LIST` secret is empty.

### 3.3 Write `.idea-realization/local.yaml`

In `<work>/<control-repo>`:

```bash
cp .idea-realization/local.example.yaml .idea-realization/local.yaml
```

Edit `.idea-realization/local.yaml`. It is gitignored. Every key is optional; a value that still
starts with `REPLACE-WITH-` counts as unset, but `tools/onboard_check.py` reports it as `FIX` on
its `local.yaml` line (`still a placeholder: ...`). Delete a key you do not set yet, as the
template's header says.

| Key | Value |
|---|---|
| `product_root` | The absolute path of `<work>/<product-repo>`. It must be outside the control checkout. |
| `control_remote` | The control repository's git URL, exactly as `git -C <work>/<control-repo> remote get-url origin` prints it |
| `control_github` | `<org>/<control-repo>` |
| `product_remote` | The product repository's git URL, exactly as `git -C <work>/<product-repo> remote get-url origin` prints it |
| `product_github` | `<org>/<product-repo>` |
| `handle` | `<handle>`, the same key you add to `docs/systems.yaml` in step 6.1 |
| `aws_read_profile` | The read profile's name in `~/.aws/config` (step 5.9). Delete the key until then: while neither AWS profile key is set, `onboard_check.py` shows its AWS lines as pending notes (step 6.5). |
| `aws_deploy_profile` | The deploy profile's name (step 5.9). Delete the key until then, as above. |
| `aws_region` | Optional: the sandbox region, if `aws.region` in `project.yaml` stays a placeholder (Appendix) |
| `dev_port_range` | Keep `3000-3099` unless the team assigns ranges per developer |
| `product_worktree_dir`, `worktree_dir` | Leave commented out; the defaults put worktrees beside each checkout |

`tools/github/apply_rulesets.sh` reads `control_github` and `product_github` from this file (or,
when one is unset, the GitHub repository in `control_remote` or `product_remote`) and refuses to
apply rulesets to any other repository, so set both before step 4.

### 3.4 Scaffold, then check

```bash
cd <work>/<control-repo>
uv run plugins/idea-realization/scripts/scaffold.py --feature all
git status --short
uv run plugins/idea-realization/scripts/doctor.py
uv run plugins/idea-realization/scripts/check.py
uv run plugins/idea-realization/scripts/paths.py show
uv run plugins/idea-realization/scripts/product.py verify
```

- The scaffold creates the gitignored `.idea-realization/staging/` directory and reports every
  tracked file as `skipped` or `unchanged`. `git status --short` must then print nothing. If it
  shows any change, stop and report it; do not commit or discard it.
- Success for the doctor: `32 recorded, 0 drifted, stale, unrecorded or missing` and
  `origin    matches control_remote (from local.yaml)`.
- `paths.py show` names `local.yaml` as the source of the URLs and GitHub names.
- `product.py verify` ends with `origin: matches`.

If `product.py verify` refuses, `product_root` names the wrong directory or `product_remote` is not
the exact string `git remote get-url origin` prints in the product checkout.

---

## 4. GitHub settings

### 4.1 Secrets

Both `DENY_LIST` secrets were set in steps 1.3 and 2.2, and `PRODUCT_READ_TOKEN` in step 2.7.
Check them:

```bash
gh secret list --repo <org>/<control-repo>
gh secret list --repo <org>/<product-repo>
```

Also set them as Dependabot secrets. A workflow run that Dependabot triggers receives only
Dependabot secrets, so without this a Dependabot pull request fails the private-content step. No
Dependabot configuration ships in either repository today, so this is a precaution:

```bash
gh secret set DENY_LIST --app dependabot --repo <org>/<control-repo> < <deny-list>
gh secret set DENY_LIST --app dependabot --repo <org>/<product-repo> < <deny-list>
gh secret list --app dependabot --repo <org>/<product-repo>
```

For the same reason, a Dependabot run of control CI needs its own copy of the product token. If you
set it, replace it as well each time you rotate the token (step 2.7):

```bash
gh secret set PRODUCT_READ_TOKEN --app dependabot --repo <org>/<control-repo>
```

### 4.2 Choose who may merge into `main`

The `main` rulesets let exactly one actor merge a pull request into `main`, and the same actor is
the only one who can create `demo-*` tags. Use your own account,
`user:<owner-login>`. If the organization's policy does not allow a user as a ruleset bypass actor,
create a team whose only member is you, give it at least write access to both repositories, and
use `team:<org>/<team-slug>` instead. Use the same value for both repositories.

The main merger must already have access to each repository before step 4.3: the script checks it
and refuses, before it changes any setting or sends any ruleset, when GitHub answers that the
account or team has no access. Check it for each repository (`<repo>` is `<control-repo>`, then
`<product-repo>`):

```bash
# user form
gh api repos/<org>/<repo>/collaborators/<owner-login> --silent && echo "has access"
# team form
gh api orgs/<org>/teams/<team-slug>/repos/<org>/<repo> --silent && echo "has access"
```

Your own account normally passes: you administer the repositories, and an organization owner also
counts as a collaborator. If a check prints an HTTP 404 error instead of `has access`, grant the
access first:

```bash
# user form
gh api --method PUT repos/<org>/<repo>/collaborators/<owner-login> -f permission=push
# team form
gh api --method PUT orgs/<org>/teams/<team-slug>/repos/<org>/<repo> -f permission=push
```

An account outside the organization receives an invitation instead, and has access only once it
accepts. Run the check again before step 4.3.

### 4.3 Apply the rulesets

From the control primary checkout (the script lives there and applies both repositories' rulesets).
Do the product repository only after step 2.6 shows `verify` green.

```bash
cd <work>/<control-repo>
tools/github/apply_rulesets.sh <org>/<control-repo> control user:<owner-login>
tools/github/apply_rulesets.sh <org>/<product-repo> product user:<owner-login>
```

The usage, from the script: `apply_rulesets.sh <owner/repo> <control|product> <user:<login>|team:<org>/<team-slug>>`.

Before it sends anything, the script checks the target repository against `local.yaml` (step 3.3)
and the main merger's access (step 4.2).

Success: for each repository it prints `repository: <org>/<repo> (control, matches control_github)`
(or `product` and `product_github`), `main merger: User <owner-login> (id ...), bypass mode
pull_request on main, always on demo-* tag creation`, `setting default branch to dev and merge
method to merge commit only` followed by `default_branch=dev merge_commit=true squash=false
rebase=false`, `created ruleset '...'` four times, and a final `done.` line. Running it again
prints `updated ruleset` instead and changes the rulesets in place.

If it fails:

| Message | Fix |
|---|---|
| `does not match the ... repository this machine is configured for` | `control_github` or `product_github` in `local.yaml` differs from the first argument (step 3.3) |
| `control_github is not set (nor a github.com control_remote)` (or `product_...`) | Set it in `local.yaml` |
| `GitHub user '...' not found` / `team '...' not found` | Check the third argument; a team must belong to the organization |
| `User '...' has no access to <org>/<repo>` (or `Team '...'`), "Nothing was changed on GitHub" | The main merger is not a collaborator, or the team does not have the repository: grant access (step 4.2) and run again (`OPS-008`, "`apply_rulesets.sh` says the main merger has no access") |
| `branch 'dev' does not exist` | Push both branches first (steps 1.8, 2.5) |
| `gh is not signed in` | `gh auth login` |
| HTTP 403 or 404 on `rulesets` | Your account is not an admin of the repository, or the organization's plan does not include rulesets on private repositories (step 0.2) |
| HTTP 422 on a `*-main.json` or `demo-tags-create.json` ruleset | The organization does not accept a user bypass actor: use the team form (step 4.2) |

### 4.4 Verify the rulesets

```bash
gh api repos/<org>/<control-repo>/rulesets --jq '.[] | "\(.id) \(.name) \(.enforcement)"'
gh api repos/<org>/<control-repo>/rulesets/<id of control-main> --jq '.bypass_actors'
gh api repos/<org>/<product-repo>/rulesets --jq '.[] | "\(.id) \(.name) \(.enforcement)"'
gh api repos/<org>/<product-repo>/rulesets/<id of product-main> --jq '.bypass_actors'
gh api repos/<org>/<control-repo>/rulesets/<id of demo-tags-create> --jq '.bypass_actors'
gh api repos/<org>/<control-repo>/rulesets/<id of demo-tags-protect> --jq '.bypass_actors'
gh api repos/<org>/<product-repo>/rulesets/<id of demo-tags-create> --jq '.bypass_actors'
gh api repos/<org>/<product-repo>/rulesets/<id of demo-tags-protect> --jq '.bypass_actors'
```

Success: the control repository lists `control-dev`, `control-main`, `demo-tags-create`,
`demo-tags-protect`; the product repository lists `product-dev`, `product-main`,
`demo-tags-create`, `demo-tags-protect`; all `active`. Each `*-main` query prints exactly one actor
with `"bypass_mode": "pull_request"`; each `demo-tags-create` query prints exactly one actor, the
same one, with `"bypass_mode": "always"`; each `demo-tags-protect` query prints `[]`.

Check the same in the web interface: each repository's **Settings > Rules > Rulesets** shows the
four rulesets; **Settings > General** shows `dev` as the default branch and, under "Pull
Requests", only "Allow merge commits" enabled.

| Ruleset | What it enforces |
|---|---|
| `control-dev` | No force-push or deletion. No pull request rule: bookkeeping commits go to control `dev` directly. |
| `control-main` | No force-push or deletion; only the main merger may update it, and only through a pull request; merge commits only |
| `product-dev` | No force-push or deletion; pull request required (0 approvals); merge commits only; required check `verify` |
| `product-main` | As `product-dev`, plus only the main merger may update it |
| `demo-tags-create` | Only the main merger can create a `demo-*` tag (bypass mode `always`, because GitHub accepts `pull_request` mode only on branch rulesets) |
| `demo-tags-protect` | Tags `demo-*` cannot be deleted, moved or force-pushed by anyone, the main merger included; no bypass actor |

They are two rulesets because a bypass actor bypasses every rule in its ruleset: one ruleset with
you on its bypass list would let you move and delete `demo-*` tags (`OPS-001`, section 9, "Who
creates `demo-*` tags").

Do not create a `demo-*` tag to test the tag rules: once pushed it can never be deleted.

### 4.5 Test that `main` refuses a direct push

Do this in each repository. Even you, the main merger, cannot push to `main` directly; your bypass
covers merging a pull request only. The test commit is made in a throwaway worktree, so the
primary checkout stays on `dev`.

Product repository:

```bash
cd <work>/<product-repo>
git fetch origin
git worktree add --detach ../<product-repo>-worktrees/ruleset-test origin/main
cd ../<product-repo>-worktrees/ruleset-test
git commit --allow-empty -m "Ruleset test: must be refused"
git push origin HEAD:main
git push origin HEAD:dev
cd <work>/<product-repo>
git worktree remove ../<product-repo>-worktrees/ruleset-test
```

Control repository, **only the `HEAD:main` push**: control `dev` accepts direct pushes by design,
so a `HEAD:dev` push there would land.

```bash
cd <work>/<control-repo>
git fetch origin
git worktree add --detach ../<control-repo>-worktrees/ruleset-test origin/main
cd ../<control-repo>-worktrees/ruleset-test
git commit --allow-empty -m "Ruleset test: must be refused"
git push origin HEAD:main
cd <work>/<control-repo>
git worktree remove ../<control-repo>-worktrees/ruleset-test
```

Success: every push is rejected with a message about repository rule violations. The pre-push
hook runs first and passes; the rejection comes from GitHub. `git worktree list` in each
repository then shows only the primary checkout.

If a push is accepted, the rulesets are not active: re-check step 4.4. The commit is empty, so
nothing changed on the branch except an empty commit; tell the team before they pull.

The test that a developer other than you cannot merge into `main` needs a second account and a
`dev` that is ahead of `main`; it is step 8.3.

---

## 5. AWS sandbox

The authority for this step is `aws/README.md` in the control repository, "Setup (the owner, once
per sandbox account)". The IAM roles and the machine rule are the security boundary; read that page
once before starting.

**What the product stores.** The product processes documents for several tenants. Each tenant's
documents and records are kept in S3 and DynamoDB, encrypted with that tenant's own KMS key, whose
alias is `alias/<product name>-tenant-*`. Textract extracts text from the uploaded documents. The
people whose claims the product processes are the claimants; their documents, names and
identifiers are "claimant data". The sandbox holds synthetic data only, and step 5.4 depends on
that.

**The sandbox account holds the product stack and nothing else.** The deploy role's scope policy
(step 5.5) limits its changes to the product's own Lambda functions, Step Functions state machines,
CloudFormation stacks, CodeBuild projects and Amplify apps. It can still change the resources of
every other service in the account, and some of those run code with an existing role. Do not create
other workloads, other teams' stacks or hand-made functions in the sandbox account; an
administrator's own resources (the baseline trail, the CDK bootstrap stack) are the only exceptions
(`aws/README.md`, "The deploy role changes only the product's own resources").

**Where to run the administrator commands.** Use AWS CloudShell in the sandbox account, signed in
as an administrator, in the sandbox region. Do not configure administrator credentials on a machine
that runs agents: the machine rule allows only the two named sandbox profiles there. Step 5.1 runs
on the work machine; steps 5.2 to 5.7 run in CloudShell, and every file they read is in
CloudShell's home directory.

### 5.1 Fill the `REPLACE_WITH_*` placeholders in local copies

On the work machine, copy the policy files out of the repository, so filled values are never
committed:

```bash
mkdir -p ~/sandbox-setup
cp <work>/<control-repo>/aws/iam/*.json ~/sandbox-setup/
cd ~/sandbox-setup
```

These are every `REPLACE_WITH_*` placeholder in the control repository (`grep -rn REPLACE_WITH`):

| Placeholder | Files | Value it needs |
|---|---|---|
| `REPLACE_WITH_SANDBOX_ACCOUNT_ID` | `deploy-policy.json` (3 places), `read-sandbox-data-policy.json` (2 places) | The sandbox account's 12-digit id |
| `REPLACE_WITH_SANDBOX_REGION` | `deploy-policy.json`, `app-permissions-boundary.json` | The sandbox region: a US region where the US inference profiles for Claude Sonnet 5 and Claude Opus 5.5 are offered |
| `REPLACE_WITH_BASELINE_TRAIL_NAME` | `deploy-policy.json` | The name of the account's baseline CloudTrail trail (created by an administrator, outside the product) |
| `REPLACE_WITH_PRODUCT_NAME` | `read-sandbox-data-policy.json` (1 place), `deploy-scope-policy.json` (6 places), `app-permissions-boundary.json` (6 places) | `<product name>`: lowercase letters, digits and hyphens, starting with a letter. It is the prefix of the tenant key aliases `alias/<product name>-tenant-*`, the prefix of the product's stack, function, state machine and build project names, and the value of the `project` tag (`OPS-007`) |

The same names also appear in `aws/README.md` (as text), in `docs/guidebook.html` (generated from
it) and in `test/test_aws_iam_policies.py`, which asserts the placeholders are still in the tracked
files. Leave all three unchanged: filling the tracked files would break that test and publish the
values.

Fill them with your values:

```bash
sed -i \
  -e 's/REPLACE_WITH_SANDBOX_ACCOUNT_ID/<account id>/g' \
  -e 's/REPLACE_WITH_SANDBOX_REGION/<region>/g' \
  -e 's/REPLACE_WITH_BASELINE_TRAIL_NAME/<trail name>/g' \
  -e 's/REPLACE_WITH_PRODUCT_NAME/<product name>/g' \
  *.json
grep -c REPLACE_WITH *.json
for f in *.json; do python3 -m json.tool "$f" > /dev/null && echo "valid $f"; done
```

Success: every `grep -c` count is 0 and every file is valid JSON. (On macOS, `sed -i ''` instead
of `sed -i`.)

There are five files: `app-permissions-boundary.json`, `deploy-policy.json`,
`deploy-scope-policy.json`, `read-only-guard-policy.json` and `read-sandbox-data-policy.json`.
Upload all five filled files to CloudShell with its "Upload file" action.

### 5.2 Create the permission boundary policy

In CloudShell, with the five files uploaded:

```bash
aws iam create-policy --policy-name app-permissions-boundary --path / \
  --policy-document file://app-permissions-boundary.json
```

The name must be exactly `app-permissions-boundary`: `deploy-policy.json` refers to it by ARN.
If it fails with `EntityAlreadyExists`, it exists; compare it with the file before reusing it.

### 5.3 Write the trust policy for the two roles

The roles' trust policies name the principals your developers sign in as: IAM Identity Center
permission-set roles, or IAM users in the sandbox. Which principals is your decision. A
permission-set role has a generated name; list them in CloudShell:

```bash
aws iam list-roles --path-prefix /aws-reserved/sso.amazonaws.com/ --query 'Roles[].Arn'
```

Use each ARN exactly as printed. An IAM user's ARN is `arn:aws:iam::<account id>:user/<user name>`.

In CloudShell, save this as `trust.json`, one ARN per principal:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": ["<principal ARN>", "<principal ARN>"] },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Do not create these two roles under the path `/app/`: that path is for the stack's own roles.

### 5.4 Create the read role

```bash
aws iam create-role --role-name <read-role-name> --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name <read-role-name> \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
aws iam create-policy --policy-name <read-guard-policy-name> \
  --policy-document file://read-only-guard-policy.json
aws iam attach-role-policy --role-name <read-role-name> \
  --policy-arn arn:aws:iam::<account id>:policy/<read-guard-policy-name>
aws iam create-policy --policy-name <read-sandbox-data-policy-name> \
  --policy-document file://read-sandbox-data-policy.json
aws iam attach-role-policy --role-name <read-role-name> \
  --policy-arn arn:aws:iam::<account id>:policy/<read-sandbox-data-policy-name>
```

`read-sandbox-data-policy.json` lets the read role decrypt tenant data and read Textract results,
so agents using the read role can see document contents. It is for the sandbox's synthetic data
only: before any real claimant data reaches the account, detach it and restore the `kms:Decrypt`
deny (`aws/README.md`, "The roles and policies").

The guard policy refuses the reads whose responses carry a secret or a value that may be one
(Lambda function configuration, Amplify apps, branches and webhooks, CodeBuild projects and builds,
ECS task definitions and tasks, Cognito client and identity-provider secrets, SSM parameter
history); `aws/README.md`, "Reads the guard refuses, and what to read instead", lists them and the
reads to use instead.

### 5.5 Create the deploy role

The deploy role gets two customer managed policies: `deploy-policy.json`, and
`deploy-scope-policy.json`, which limits its changes to the product's own resources.
`deploy-policy.json` is close to the size limit for a managed policy, so the scope rules are a
separate policy.

```bash
aws iam create-role --role-name <deploy-role-name> --assume-role-policy-document file://trust.json
aws iam create-policy --policy-name <deploy-policy-name> --policy-document file://deploy-policy.json
aws iam attach-role-policy --role-name <deploy-role-name> \
  --policy-arn arn:aws:iam::<account id>:policy/<deploy-policy-name>
aws iam create-policy --policy-name <deploy-scope-policy-name> \
  --policy-document file://deploy-scope-policy.json
aws iam attach-role-policy --role-name <deploy-role-name> \
  --policy-arn arn:aws:iam::<account id>:policy/<deploy-scope-policy-name>
```

Success for 5.4 and 5.5: each `create-*` prints the new resource's JSON; `attach-role-policy`
prints nothing. `aws iam list-attached-role-policies --role-name <read-role-name>` lists three
policies (`ReadOnlyAccess`, `<read-guard-policy-name>`, `<read-sandbox-data-policy-name>`), and
`aws iam list-attached-role-policies --role-name <deploy-role-name>` lists two
(`<deploy-policy-name>`, `<deploy-scope-policy-name>`). If `create-policy` fails with
`MalformedPolicyDocument`, a placeholder was missed or the JSON was damaged; repeat the check at
the end of step 5.1.

**What the product stack must do as a result** (`aws/README.md`, "The deploy role changes only the
product's own resources"). The scope policy denies changes to any Lambda function, Step Functions
state machine, CloudFormation stack or CodeBuild project whose name does not start with
`<product name>-`, and to any Amplify app or branch that does not carry the tag
`project=<product name>`. So every product stack:

1. is named `<product name>-<name>`;
2. tags every resource `project=<product name>` (`Tags.of(app).add('project', '<product name>')`);
3. gives every function, state machine and build project, including the ones CDK creates for
   itself, a name that starts with `<product name>-` (the README has an aspect that does this).

A resource created without the prefix fails with an access-denied error naming, for example,
`lambda:CreateFunction`; the fix is in the CDK app, not the policy.

### 5.6 Create the OpenSearch Serverless service-linked role

Once per account, as an administrator (the deploy role cannot create service-linked roles):

```bash
aws iam create-service-linked-role --aws-service-name observability.aoss.amazonaws.com
```

Success: it prints the role. If it fails with "has been taken in this account", the role already
exists; that is fine.

### 5.7 Bootstrap CDK and enable the models

```bash
npx aws-cdk bootstrap aws://<account id>/<region>
```

Success: it ends with the bootstrap stack created or updated. The product's CDK app must use
`CliCredentialsStackSynthesizer` (`aws/README.md`, "CDK settings every product stack uses"), because
the deploy role cannot assume the bootstrap roles.

Then, in the Bedrock console, in the sandbox region, enable model access for **Claude Sonnet 5** and
**Claude Opus 5.5**. The product calls them through the US inference profiles
`us.anthropic.claude-sonnet-5` and `us.anthropic.claude-opus-5-5`; the quota check is in
`OPS-006`, "Before the freeze".

### 5.8 Budget alarm and cost tags (`OPS-007`)

In the AWS Budgets console, as the sandbox administrator, before the first deployment:

1. A monthly cost budget for the sandbox account. The amount is your decision.
2. Alerts on actual spend at 50%, 80% and 100%, and on forecast spend at 100%.
3. Recipients: you, and the team channel's email address if it has one.

In the Billing console, activate `project` and `owner` as cost allocation tags. A user-defined tag
key appears there only after a resource carrying it exists, so if they are not listed yet, activate
them right after the first deployment.

`OPS-007` also asks for a brain entry recording the budget. The brain script needs your developer
handle, which step 6.1 registers, so the entry is written in step 6.2.

### 5.9 Your machine's AWS profiles

On the work machine (`aws/README.md`, "Setup (each developer, once per machine)"):

1. **Your sandbox login profile.** This is the AWS CLI profile you sign in to the sandbox account
   with, as yourself: for IAM Identity Center, the profile `aws configure sso` creates; for an IAM
   user, a profile with that user's keys. Give it a name that is not `default`, for example
   `sandbox-login`. The two role profiles below take their credentials from it. The machine check
   in item 4 accepts it, because it looks only for a `default` profile, `AWS_` variables and
   instance or container credentials; a named profile is used only when a command names it.
2. In `~/.aws/config`, two profiles, one per role, sourced from your sandbox login profile:

   ```ini
   [profile sandbox-read]
   role_arn = arn:aws:iam::<account id>:role/<read-role-name>
   source_profile = <your sandbox login profile>

   [profile sandbox-deploy]
   role_arn = arn:aws:iam::<account id>:role/<deploy-role-name>
   source_profile = <your sandbox login profile>
   ```

   No `[default]` or `[profile default]` section in `~/.aws/config` or `~/.aws/credentials`, and no
   `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` or `AWS_PROFILE` in your
   environment.
3. Set `aws_read_profile: sandbox-read` and `aws_deploy_profile: sandbox-deploy` in
   `.idea-realization/local.yaml` (and `aws_region` if `project.yaml` keeps its placeholder).
4. Check, from `<work>/<control-repo>`:

   ```bash
   uv run python tools/check_aws_machine.py --probe
   tools/aws-sandbox whoami
   ```

   Success: `check_aws_machine.py --probe` prints OK and exits 0; `whoami` prints both profile
   names and the read role's identity.

   If `--probe` fails, it names each default profile, ambient variable or reachable instance
   metadata service it found; remove each one. Do not run agents on an EC2 instance or any host
   with an instance or container role. If `whoami` fails, the profile names in `local.yaml` do not
   match `~/.aws/config`, you are not signed in with your sandbox login profile, or the trust
   policy (step 5.3) does not name your principal.

Deploying from GitHub Actions is not set up: deploys are local, through the `aws-deploy` agent.
The draft for CI deploys is `docs/plans/PLAN-002-ci-deploy-to-aws.md`; its open questions are in
the Appendix.

---

## 6. The team

### 6.1 Register yourself as a developer

Do this on the work machine, before the first claim: the claim and every session resolve your
handle from your git email through this entry. Add your entry to the `owners` map in
`docs/systems.yaml`. The key is `<handle>`; the email must be the `user.email` you set on the work
machine in step 1.5. Your work email is not confidential and is committed here. Keep the
`repository-owner` line.

```yaml
owners:
  repository-owner: The person accountable for this repository.
  <handle>:
    description: Repository owner.
    emails: ["<your work email>"]
    approves: [procedures]
```

`approves: [procedures]` marks who approves anti-pattern procedures; leave it out if that is not
you. Then, in the primary checkout on `dev`:

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
uv run plugins/idea-realization/scripts/identity.py
git add docs/systems.yaml
git commit -m "Register the owner's developer handle"
git push origin dev
```

Success: `identity.py` prints `<handle>`; the commit passes the pre-commit hook. A developer's own
entry in `docs/systems.yaml` is bookkeeping and goes directly on control `dev` (`ONBOARDING.md`,
section 1, "Bookkeeping"). If the push is rejected, `git pull --rebase origin dev` and push again.

**Why registration comes before any code or phase.** Document codes and phase ids carry the
handle of the developer who creates them
(`plugins/idea-realization/docs/document-codes.md` and `backlog-protocol.md`):

- A new document code in a scoped series reads `<SERIES>-<handle>-NNN`, for example
  `PLAN-<handle>-001`, numbered per handle; a dated code reads `<SERIES>-<handle>-YYYY-MM-DD-NN`.
  Every series in `docs/codes.yaml` is scoped except `GOV`, whose codes carry no handle
  (`GOV-NNN`). The `next-code` skill resolves the handle from `git config user.email` through
  `identity.py`, and refuses, reserving nothing, when no handle resolves.
- A new phase id reads `phase-<track>-<handle>-<NN>`, with the next unused number for that handle
  in its track, chosen by hand.
- A handle is valid only when it is an `owners` key with `emails` in `docs/systems.yaml`. A code or
  phase id that carries an unregistered handle fails the repository check, so the pre-commit hook
  refuses the commit. A developer who leaves the team keeps their entry, or every code and phase id
  carrying their handle fails.
- The codes and phase ids written before this rule have no handle and stay valid because they are
  listed: the `legacy:` list in `docs/codes.yaml` (`ADR-001`, `ARCH-001`, `ARCH-002`, `OPS-001` to
  `OPS-010`, `PLAN-001` to `PLAN-003`, `REQ-001`) and `legacy_phase_ids` in `backlog/backlog.yaml`
  (the 34 seed phases, frozen at transfer). Nothing new is added to either list; any other code or
  id without a handle fails the check.

So you, and every developer, register in `docs/systems.yaml` before allocating a code or adding a
phase. The seed `owners` map holds only `repository-owner`, which lists no emails and is not a
developer.

### 6.2 Record the sandbox budget and the product brain entries

The brain entry `OPS-007` asks for (step 5.8) is not bookkeeping. It reaches control `dev` on an
`agent/<handle>-<slug>` branch through a pull request (`OPS-005`, section 5), made in a control
worktree:

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
git worktree add --no-track -b agent/<handle>-sandbox-budget \
  ../<control-repo>-worktrees/sandbox-budget origin/dev
cd ../<control-repo>-worktrees/sandbox-budget
uv run plugins/idea-realization/scripts/brain.py new decision --title "Sandbox budget alarm" --body "<amount, thresholds, who receives the alerts by role>"
git add brain/
git commit -m "Record the sandbox budget alarm"
git push -u origin HEAD
gh pr create --repo <org>/<control-repo> --base dev --title "Record the sandbox budget alarm" --body "Owner setup, step 6.2."
gh pr merge <number> --repo <org>/<control-repo> --merge
```

Write no account id in the body. Your own work email may appear; name any other alert recipient by
role. `brain.py` prints
`recorded decisions/sandbox-budget-alarm.md; commit it with index.md`; `git add brain/` stages the
entry and `brain/index.md` together. Then remove the worktree and update the primary checkout:

```bash
cd <work>/<control-repo>
git worktree remove ../<control-repo>-worktrees/sandbox-budget
git pull --rebase origin dev
```

**The product brain drafts.** `owner-files/brain-drafts/` beside this guide holds 28 drafts of
brain entries about the product (its terms, the AWS services it uses, its four agents and its
design principles). None is recorded yet. `owner-files/brain-drafts/index.md` lists them and gives
one recording command for each, in the order to run them (an entry's `--links` must name entries
that already exist), and ends with `brain.py check`. Record them after you are registered
(step 6.1): `brain.py new` takes the author from your git email. Like the budget entry, they reach
control `dev` on a branch through a pull request, from a control worktree:

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
git worktree add --no-track -b agent/<handle>-product-brain \
  ../<control-repo>-worktrees/product-brain origin/dev
cd ../<control-repo>-worktrees/product-brain
export IDEA_REALIZATION_ROOT="$(pwd)"
DRAFTS=<export>/owner-files/brain-drafts
# run the 28 commands in owner-files/brain-drafts/index.md, in order, then:
uv run plugins/idea-realization/scripts/brain.py check
git add brain/
git commit -m "Record the product brain entries"
git push -u origin HEAD
gh pr create --repo <org>/<control-repo> --base dev --title "Record the product brain entries" --body "Owner setup, step 6.2."
gh pr merge <number> --repo <org>/<control-repo> --merge
cd <work>/<control-repo>
git worktree remove ../<control-repo>-worktrees/product-brain
git pull --rebase origin dev
```

The `export` and `DRAFTS=` lines are the two at the top of `index.md`; `<path to this export>` there is
`<export>`. Run the commands in the same shell, then close it: with `IDEA_REALIZATION_ROOT`
exported, the plugin tests fail (step 1.7).

Success: each command prints `recorded concepts/<id>.md; commit it with index.md` (or
`entities/<id>.md`); `brain.py check` exits 0; `git status --short` before the commit shows
`brain/index.md` and 28 new files under `brain/concepts/` and `brain/entities/`, and nothing else.
If a command prints `error: links to unknown entries: <id>`, an earlier command in the list was
skipped or failed: run that one, then continue.

### 6.3 Write the five workstreams

Do this before telling developers to start: their first-day checklist ends with claiming a
workstream from this list (`ONBOARDING.md`, section 4).

A workstream is a set of paths one developer owns. You write the list; each developer claims one.
A draft of the five workstreams is `owner-files/workstreams-proposal.yaml`, beside this guide:
`ui`, `api`, `agents`, `infra-data` and `demo-qa`, each `open` with an empty owner. Its paths are
placeholders for a product layout that does not exist yet; set the real ones. Paths must not
overlap. Edit it into `docs/workstreams.yaml`, which in the export holds `workstreams: []`. The
comment lines at the top of the proposal are notes for you; delete them from the copy. The proposal
passes `workstreams.py check` as it stands. The form is
(`plugins/idea-realization/docs/workstreams.md`):

```yaml
schema_version: 1
workstreams:
  - id: ui
    title: User interface
    owner: ""
    status: open
    paths:
      - product:web/
    interfaces: []
```

The workstream list is not bookkeeping (`OPS-001`, section 3), so it reaches control `dev` through
a pull request, from a control worktree:

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
git worktree add --no-track -b agent/<handle>-workstreams \
  ../<control-repo>-worktrees/workstreams origin/dev
cd ../<control-repo>-worktrees/workstreams
cp <export>/owner-files/workstreams-proposal.yaml docs/workstreams.yaml
# edit docs/workstreams.yaml: delete the top comment lines, set the real paths, make any other change
uv run plugins/idea-realization/scripts/workstreams.py check
uv run plugins/idea-realization/scripts/workstreams.py show
git add docs/workstreams.yaml
git commit -m "Define the five workstreams"
git push -u origin HEAD
gh pr create --repo <org>/<control-repo> --base dev --title "Define the five workstreams" --body "Owner setup, step 6.3."
gh pr merge <number> --repo <org>/<control-repo> --merge
cd <work>/<control-repo>
git worktree remove ../<control-repo>-worktrees/workstreams
git pull --rebase origin dev
```

Success: `workstreams.py check` prints nothing and exits 0; `show` lists the five workstreams as
`open`. Developers then claim with `workstreams.py claim <id>` and commit the claim directly on
control `dev` (`ONBOARDING.md`, section 4).

Once workstreams are claimed, fill the product repository's `.github/CODEOWNERS.example` from them,
rename it to `.github/CODEOWNERS`, and merge that through a pull request to product `dev`, from a
product worktree as in step 8.2.

### 6.4 Give each developer access to both repositories

Each developer needs write access to both repositories (to push branches and bookkeeping commits).
Either add them to an organization team that has write access to both, or per repository:

```bash
gh api --method PUT repos/<org>/<control-repo>/collaborators/<their-login> -f permission=push
gh api --method PUT repos/<org>/<product-repo>/collaborators/<their-login> -f permission=push
```

Do not give developers the admin role: an administrator can edit or delete the rulesets.

Send each developer, through a channel the organization trusts: both repositories' URLs and
`<org>/<repo>` names, the deny-list file, and their sandbox sign-in, including the name to give
their sandbox login profile (step 5.9). If their sandbox access is not ready yet, say so: they
finish the rest of the checklist and do the AWS step later (step 6.5).

Point them to `ONBOARDING.md`, to the developer guidebook `docs/guidebook.html`, and to the
day-one prompts (`OPS-010`). The guidebook is one self-contained HTML page, generated from
`ONBOARDING.md`, `CLAUDE.md`, the operating guides, `aws/README.md` and two plugin protocol
documents, in reading order; it loads no script and makes no request, so it opens directly from
the checkout in a browser. Where it and a source document differ, the document wins. Tell them
that registering in `docs/systems.yaml` (step 6.1) comes before they allocate a document code or
add a phase.

### 6.5 Each developer's first day

Each developer follows `ONBOARDING.md`, section 3 (the first-day checklist), on their own machine:
install the tools, clone the control repository, install the hooks, place the deny-list, set their
git identity and add their own entry to `docs/systems.yaml` (directly on control `dev`), write
`local.yaml`, scaffold and check, and set up AWS.

Next they clone the product repository beside the control repository, set `product_root` in
`local.yaml` to it, and check that it is the right repository (`ONBOARDING.md`, section 3,
step 9). From the control repository's root:

```bash
git clone <product repository URL> ../<product>
git -C ../<product> checkout dev
uv run plugins/idea-realization/scripts/product.py verify   # prints "origin: matches"
```

Then install the product repository's own hooks and give it the deny-list. Its hooks run its own
copy of `check_confidential.py`, which reads only `PRIVATE_DENY_LIST` or the product checkout's
`.private/deny-list.txt` (worktrees read the product's primary checkout's copy); it never finds
the control repository's file. Copy the file; exporting `PRIVATE_DENY_LIST` also works, but only
in a shell where it is set.

```bash
(cd ../<product> && tools/install-hooks.sh)                 # core.hooksPath -> tools/git-hooks
mkdir -p ../<product>/.private
cp .private/deny-list.txt ../<product>/.private/deny-list.txt   # gitignored there too
```

`onboard_check` checks both (the `product hooks` and `product deny-list` lines). Your own product
clone already has both from steps 3.1 and 3.2.

Then they start Claude Code and claim a workstream (`ONBOARDING.md`, section 4). The first prompt
in the day-one prompts (`OPS-010`, section 1) walks a Claude Code session through this checklist
with them. They run, until it exits 0:

```bash
uv run python tools/onboard_check.py
```

It takes no arguments other than `--root`. It prints one line per item: `OK`, `FIX` with what to
do, or `NOTE` for an AWS item that is pending. Then it lists the two steps it cannot run (they need
the network): `check_aws_machine.py --probe` and `tools/aws-sandbox whoami`. The last line is
`<n> to fix`, or `All checks OK`, followed by `(<n> pending the owner's AWS setup)` when there are
pending notes. It exits 1 when any line is `FIX`, and 0 otherwise; pending notes do not fail it.

**The AWS pending notes.** While neither `aws_read_profile` nor `aws_deploy_profile` is set (in
`local.yaml`, or through `IDEA_REALIZATION_AWS_READ_PROFILE` or
`IDEA_REALIZATION_AWS_DEPLOY_PROFILE`), the AWS CLI, AWS profile and AWS region lines that are not
OK print as `NOTE` with the text `pending: no AWS profile is configured on this machine yet, so the
AWS steps wait for the owner's setup (aws/README.md); then ...`. It means the developer cannot
have finished the AWS step yet, because the roles you create in step 5 come first. The rest of the
checklist does not depend on it. The notes clear when the developer names either profile, after
you have created the roles and sent their sandbox sign-in: from then on the AWS lines are checked
like the others, and a profile missing from `~/.aws/config`, a `default` profile name or one
profile used for both roles is a `FIX`. The `AWS machine rule` line (no `default` profile, no
`AWS_` variables) is checked in every case and is never pending.

### 6.6 Order the queue

`next_up` in `backlog/backlog.yaml` is empty and every phase's `owner` is `repository-owner`. Rank
`next_up` and set `owner: <handle>` on the phases you assign (`OPS-002`, step 10). This is planning
work, not bookkeeping, so it goes on a branch through a pull request (`OPS-002`, "Where the work is
committed"):

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
git worktree add --no-track -b agent/<handle>-queue-order \
  ../<control-repo>-worktrees/queue-order origin/dev
cd ../<control-repo>-worktrees/queue-order
# edit backlog/backlog.yaml: next_up, and owner: <handle> on assigned phases
uv run plugins/idea-realization/scripts/cli.py catalog
uv run plugins/idea-realization/scripts/check.py
uv run plugins/idea-realization/scripts/cli.py ready
git add backlog/backlog.yaml docs/catalog.md
git commit -m "Rank next_up and assign phases"
git push -u origin HEAD
gh pr create --repo <org>/<control-repo> --base dev --title "Rank next_up and assign phases" --body "Owner setup, step 6.6."
gh pr merge <number> --repo <org>/<control-repo> --merge
cd <work>/<control-repo>
git worktree remove ../<control-repo>-worktrees/queue-order
git pull --rebase origin dev
```

Success: `check.py` exits 0, and `cli.py ready` lists the queue in the order you set.

The 34 seed phases keep their ids without a handle (`phase-boot-01` and so on), because
`legacy_phase_ids` lists them. A phase you add yourself, here or later, takes
`phase-<track>-<handle>-<NN>` with your handle (step 6.1). The first seed phase, `phase-boot-01`
(author-scoped document codes, session codes and phase ids), is already implemented in the export;
its `next_action` says the team closes it through the review gate as its first exercise.

### 6.7 The team decisions log

The team decisions log is `docs/governance/GOV-003-team-decisions.md` (`GOV-003`). It is the
backlog's decision record: `backlog/backlog.yaml` names it in `decision_record`, and the repository
check reads it. It starts with no entries. Write an entry, in the same change as the event:

- when you, or whoever resolves a collision between phases, make a real choice: which phase
  yields, whether a boundary moves, whether a phase splits or widens its declarations, which
  implementation is kept. A mechanical keep-both merge of `backlog/backlog.yaml` needs no entry;
- whenever two phases declared disjoint conflict in source code, because the declarations the
  concurrency check relies on were wrong;
- when a phase leaves `complete`, or stays complete but loses `session`, `completion_evidence` or
  `result`, for example when you reopen a completed phase. Without an entry naming the phase in
  the same change, the repository check fails that change.

A commit message is not a record. The entry format is in the document: a heading
`### <date> <phase id(s)>: <what was decided>`, then `Decided by <handle>.` and the reason, newest
last, under `## Entries`. The rules behind it are `backlog-protocol.md`, sections 12 and 13.

---

## 7. Moving `ui-kit/` to the product repository (later, not now)

The ruling: the UX component kit stays in the control repository's `ui-kit/` for now and moves to
`product:packages/ui/` later (`ADR-001`; `PLAN-003`, open question 7, leans to moving it once the
product repository exists and before the app's first screens integrate). When you decide to move
it, register it as a phase and do it through the normal claim and review. What it involves:

**What moves:** the whole `ui-kit/` folder: `src/`, `dist/` (committed built CSS), `tokens/`,
`layouts/`, `gallery/`, `tools/` (Python generators), `test/` (Python tests), `index.html`,
`README.md`, `package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`,
`vitest.setup.ts` and its `.gitignore`. Its scripts and tests find their files relative to the kit
folder, so they do not depend on the control repository's layout.

**What to update:**

- Product repository: `ui-kit/.gitignore` re-includes `dist/`, which the product's root
  `.gitignore` ignores; keep that rule in `packages/ui/.gitignore`.
- Product CI (`product-ci.yml`): the Node steps run only for a `package.json` at the root, and the
  Python steps only for a root `pyproject.toml`. Add steps for `packages/ui/` (`npm ci`, `npm run
  typecheck`, `npm test`, `npm run build`, and the Python tests) so the kit stays tested.
- Control repository, `docs/systems.yaml`: `sys-ui-kit` paths `ui-kit/` become
  `product:packages/ui/`.
- Control repository, `backlog/backlog.yaml`: the UX phases' `deliverables` (`ui-kit/...` become
  `product:packages/ui/...`) and `verification` (drop the `control:` prefix and change the paths;
  for example `control: cd ui-kit && npx playwright test` becomes `cd packages/ui && npx playwright
  test`). Phases already complete keep their history.
- Control documents that name `ui-kit/`: `PLAN-003`, `REQ-001`, `ARCH-001` and `ADR-001` (its
  "Revisit when" list names this move).
- The workstream that owns the kit, if one exists, and the product's `CODEOWNERS`.
- Then delete `ui-kit/` from the control repository in the same change set.

---

## 8. Day-one verification

### 8.1 Control CI is green on `dev`

```bash
gh run list --repo <org>/<control-repo> --branch dev --limit 3
```

Success: the latest `control-ci` run on `dev` is green. A red run on `dev` is fixed forward with a
new commit.

One of its steps, `Guidebook is up to date`, runs `uv run python tools/build_guidebook.py --check`.
`docs/guidebook.html` is generated from the documents `tools/guidebook.yaml` lists (`ONBOARDING.md`,
`CLAUDE.md`, the guides `OPS-001` to `OPS-010`, `aws/README.md`, and the plugin's `two-repositories.md` and `workstreams.md`), and the page records
each input's SHA-256. A change to one of those documents without regenerating the page fails this
step. The fix is to regenerate and commit the page in the same branch:

```bash
uv run python tools/build_guidebook.py
git add docs/guidebook.html
```

Never edit `docs/guidebook.html` by hand. `--strict` additionally fails on any conversion warning;
CI does not use it.

### 8.2 Product CI `verify` is green on a first pull request

The first product pull request removes `README-TEMPLATE.md` (its steps are done) and fills the
`README.md` placeholders you already know. Work in a product worktree, never in the primary
checkout:

```bash
cd <work>/<product-repo>
git fetch origin
git worktree add --no-track -b agent/<handle>-remove-readme-template \
  ../<product-repo>-worktrees/first-pr origin/dev
cd ../<product-repo>-worktrees/first-pr
git rm README-TEMPLATE.md
# edit README.md: replace the REPLACE-WITH placeholders you can fill now
git add -A
git commit -m "Remove the template instructions and fill the README"
git push -u origin HEAD
gh pr create --repo <org>/<product-repo> --base dev --title "Remove the template instructions" --body "Owner setup, step 8.2."
gh pr checks <number> --repo <org>/<product-repo> --watch
gh pr merge <number> --repo <org>/<product-repo> --merge
```

Success: `verify` passes, and the merge creates a merge commit (squash and rebase are not offered).
Then clean up from the primary checkout and bring its `dev` up to date with a fast-forward:

```bash
cd <work>/<product-repo>
git worktree remove ../<product-repo>-worktrees/first-pr
git fetch origin
git merge --ff-only origin/dev
```

If `gh pr merge` is refused while `verify` is pending, wait for it. If `verify` never appears, the
workflow file is not on the branch or Actions is disabled (`OPS-008`, "The required check `verify`
is pending or failed"). If `git merge --ff-only` fails, the primary checkout holds commits origin
does not have: stop and report it rather than merging or resetting.

### 8.3 A developer other than you cannot merge into `main`

This step needs a second person: a developer with write access (not admin) and a signed-in `gh`.
If no developer has been invited yet, skip it now and run it once the first developer has access
(step 6.4). Nothing else depends on it.

Product `dev` is now one merge ahead of `main`, so a release pull request can be opened. You open
it; the developer tries to merge it:

```bash
# you
gh pr create --repo <org>/<product-repo> --base main --head dev --title "Ruleset test: main merger only" --body "Owner setup, step 8.3."
# the developer, on their machine
gh pr merge <number> --repo <org>/<product-repo> --merge
```

Success: the developer's merge is refused (the message says the branch is protected by a ruleset,
for example "Cannot update this protected ref"). Then choose: close it with
`gh pr close <number> --repo <org>/<product-repo>`, or merge it yourself with
`gh pr merge <number> --repo <org>/<product-repo> --merge`, which also confirms your bypass works.
Merging puts only the README change on `main`; do not tag it. When you do tag a release later,
only you can: GitHub refuses a `demo-*` tag push from anyone else (`demo-tags-create`), and nobody,
you included, can move or delete one (`demo-tags-protect`). The tagging commands are in `OPS-001`,
section 5.

If the developer's merge succeeds, the `product-main` ruleset is not enforcing: re-run step 4.3 and
re-check step 4.4. If your own merge is refused, the main merger is wrong (`OPS-008`, "A merge into
`main` is refused").

### 8.4 `/start` works

Bring both primary checkouts up to date, then start Claude Code in the control repository:

```bash
cd <work>/<control-repo>
git pull --rebase origin dev
git -C <work>/<product-repo> fetch origin
git -C <work>/<product-repo> merge --ff-only origin/dev
claude
```

No `--plugin-dir` flag is needed. The project settings, `.claude/settings.json`, declare this
repository as a plugin marketplace (`extraKnownMarketplaces`, `idea-realization-team`, read from
`.claude-plugin/marketplace.json`) and enable `idea-realization@idea-realization-team`
(`enabledPlugins`). The first time, Claude Code asks whether you trust the folder: accept, because
the project settings load the plugin only in a trusted folder. If `/start` does not exist after
that, run `/plugin` and check that `idea-realization@idea-realization-team` is enabled
(`ONBOARDING.md`, section 3, step 10). The same settings carry a `SessionStart` hook that prints
the session banner when the session starts.

Nothing else is added at launch. The product's primary checkout is never added to a session:
`session-start` creates a product worktree when a phase is claimed, and that worktree is added
then with `/add-dir` (`ONBOARDING.md`, section 3, step 10, and section 6, step 4).

In the session, run `/idea-realization:start` (or `/start`).

Success: the banner prints your handle, the product checkout and the days to the demo, and no line
reads `not set on this machine` or `(unavailable: ...)`. It asks for a mode (Planning,
Implementing or Validating) and names the guide and first command. Such a line names the setup
step not yet done: an unresolved handle means your git email is not in `docs/systems.yaml`
(step 6.1).

### 8.5 A dry-run claim

There is no dry-run flag. The claim skill asks before it writes the claim commit, so answer no at
that question:

1. In the session, run `/idea-realization:backlog` to see the ready queue. If `next_up` is empty
   (step 6.6 not done yet), the queue is in priority order.
2. Run `/idea-realization:session-start`. It pulls control `dev` and fast-forwards the product
   checkout's `dev`, reads the configuration, runs `identity.py` and `product.py verify`, orients
   on the first ready phase, then asks whether to claim.
3. Answer no.

Success: everything before the question ran without error, and no claim was made and no worktree
was created. The pull and fast-forward may legitimately bring in commits peers pushed; that is not
a failure. Check:

```bash
git -C <work>/<control-repo> status --short
git -C <work>/<control-repo> log origin/dev..dev --oneline
git -C <work>/<control-repo> worktree list
git -C <work>/<product-repo> worktree list
```

The first two print nothing: no change and no unpushed claim commit. Each `worktree list` shows
only the primary checkout. If `identity.py` or `product.py verify` fails, the session stops and
names the cause; fix it with steps 3.3 and 6.1.

Finish by running `uv run python tools/onboard_check.py`. Your AWS profiles are set (step 5.9), so
no line should be a pending `NOTE`; it exits 0 and ends with `All checks OK` when every item is
done.

Then open `docs/guidebook.html` from the control checkout in a browser and check that it shows the
table of contents and the Sources appendix. This is the page you point developers to (step 6.4).

---

## Appendix: open owner decisions

Values to fill and questions the documents leave to you. Tick each one off.

### Before pushing

- [ ] Re-author the initial commits on the work machine with your work identity (steps 0.4, 1.5,
      2.4). Decided: this is a step to do, not a choice.
- [ ] `<control-repo>` and `<product-repo>` names (step 0.3).

### GitHub

- [ ] The main merger: `user:<owner-login>`, or a one-member team (step 4.2).
- [ ] The product read token for control CI: fine-grained token or GitHub App, its expiry date, and
      a reminder to rotate it before then (step 2.7).
- [ ] The `DENY_LIST` and `PRODUCT_READ_TOKEN` Dependabot secrets (step 4.1, a precaution).
- [ ] Which developers get access, and through a team or per repository (step 6.4).

### Values in tracked files

These `REPLACE-WITH-` placeholders are in tracked files. A value that can name the organization
must not be committed; the private-content check refuses deny-listed identifiers only.

- [ ] `.idea-realization/project.yaml`: `urls.hackathon_portal`, `urls.demo_app`, `urls.team_chat`,
      and `aws.region`. Decide whether each may be tracked; otherwise leave the placeholder and
      have each developer set `aws_region` in `local.yaml`.
- [ ] Product `README.md`: product name, description, stack per directory, clone directory,
      install and run commands.
- [ ] Product `.github/CODEOWNERS.example`: your GitHub login and the workstream owners, then
      rename to `CODEOWNERS` (step 6.3).
- [ ] The product's issue and pull request templates keep their `REPLACE-WITH` markers: they are
      filled per issue and per pull request, not now.

### AWS (`aws/README.md`, `OPS-007`)

- [ ] `<account id>`, `<region>`, `<trail name>` and `<product name>` (step 5.1).
- [ ] `<read-role-name>`, `<deploy-role-name>`, `<read-guard-policy-name>`,
      `<read-sandbox-data-policy-name>`, `<deploy-policy-name>` and `<deploy-scope-policy-name>`
      (steps 5.4, 5.5).
- [ ] The `<principal ARN>` list in the roles' trust policy (step 5.3).
- [ ] Monthly budget amount and alert recipients (step 5.8).
- [ ] The `project` tag value: it must be `<product name>`, because the deploy role's scope policy
      allows Amplify changes only on resources tagged `project=<product name>` (step 5.5;
      `OPS-007`, "Tags").
- [ ] Standing: the sandbox account holds the product stack and nothing else (step 5).
- [ ] Whether the read role gets Cost Explorer access if the daily cost review is refused
      (`OPS-007`, "Daily cost review").
- [ ] Standing: before any real claimant data reaches the sandbox, remove
      `read-sandbox-data-policy.json` from the read role and restore the `kms:Decrypt` deny.
- [ ] If the product needs a secret at run time, a narrow allow for that secret in the boundary
      (`aws/README.md`, "Secrets").

### Deploy from CI (`PLAN-002`, draft)

`PLAN-002` was drafted by an agent ("the author" below) for a colleague you choose ("the
colleague"): the person who will set up the IAM identity provider, the CI role and the GitHub
environment for deploys from GitHub Actions.

- [ ] Accept or reject the plan. Until accepted, CI only verifies and deploys are local.
- [ ] Who the colleague is.
- [ ] A third role `ci-deploy` with the same two policies as the deploy role
      (`deploy-policy.json` and `deploy-scope-policy.json`; the plan's step 3), rather than letting
      the deploy role also trust GitHub (proposed by the author).
- [ ] Open question 1: should CI deploy before the demo, or only after it? (Author: set it up, keep
      it unused until a `demo-rc-*` tag exists.)
- [ ] Open question 2: the required reviewers for the `sandbox` environment.
- [ ] Open question 3: whether the product repository uses the immutable OIDC subject format. Not
      yours to decide: the colleague checks it in the plan's step 2.
- [ ] Open question 4: a tighter policy for `ci-deploy` than `deploy-policy.json`? (Author: same
      policy for the demo, tighten afterwards.)
- [ ] The prerequisites the plan lists for the colleague ("Prerequisites the colleague needs from
      the owner"): sandbox access, budget amount and alert address, among others.

### UX kit (`PLAN-003`)

- [ ] Open question 1: the accent, from the theme sheet.
- [ ] Open question 2: the product name and logo.
- [ ] Open question 3: one `sys-ui-kit` system, or split it so two developers can work on the kit
      in parallel.
- [ ] Open question 4: a kit workstream and its owner.
- [ ] Open question 5: the kit phases' verification commands (whoever integrates Kit v0).
- [ ] Open question 6: a pointer to the `ui-page` skill in `CLAUDE.md` (proposed wording is in the
      plan; `CLAUDE.md` changes only with your approval).
- [ ] Open question 7: when the kit moves to the product repository (step 7).

### Team and process

- [ ] The five workstreams (step 6.3).
- [ ] `next_up` order and phase owners (step 6.6).
- [ ] Demo-day role assignments, and where they are recorded (`OPS-006`, "Roles").
- [ ] The demo-day hotfix shortcut (`agent/<handle>-hotfix-<slug>`, skipping the claim but not the
      review): not a ruling yet (`OPS-006`, "Code freeze").
- [ ] Which flows the demo shows, for the smoke test (`OPS-006`).
- [ ] Whether developers get separate dev-server port ranges (`OPS-008`, "The dev server's port is
      already in use"; `dev_port_range` in `local.yaml`).
- [ ] `ARCH-002` open question: its Figure 1 (governance detail) is not yet recorded.

### Inconsistencies found while writing this guide

Not decisions, but worth a fix phase:

- `aws/README.md` ("The machine rule") says only the two named sandbox profiles exist on an agent
  machine, while its own profile example sources both from a third, sign-in profile (step 5.9).
