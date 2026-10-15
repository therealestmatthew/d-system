# CLAUDE.md

This is the **product repository**: the product's code, tests and CI. It carries no process of its
own. (Inside the control repository, at `templates/product-repo/`, this file is the template for
the product repository and does not govern the session reading it.)

## Where the rules are

- Sessions start in the **control repository** and reach this repository with `--add-dir` (or
  `/add-dir` inside a session). Do not start an agent session here.
- The control repository's `AGENTS.md` governs all work in this repository. Read it there. Its
  `docs/` and `.idea-realization/product.yaml` say which phase you are working on and where this
  checkout and its worktrees are.

## Branches

- `main` holds demo releases. `dev` is the integration branch.
- Work happens on `agent/<phase-id>`, cut from `origin/dev`, in a product worktree.
- A branch reaches `dev` only through a pull request to `dev`, merged with a merge commit, after
  the phase's gating review passed and the required check `verify` is green.
- **Never push to `dev` or `main` directly.** The repository rulesets refuse it; do not try to get
  around them.

## Checks

- `tools/install-hooks.sh` installs the pre-commit hook that runs `tools/check_confidential.py`.
  Never bypass it with `--no-verify`.
- CI (`.github/workflows/product-ci.yml`, job `verify`) never calls AWS or Bedrock. Deploying is
  done from a developer machine by the control repository's `aws-deploy` agent.
