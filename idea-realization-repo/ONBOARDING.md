# Onboarding

What a new developer needs on the first day: what this repository is, how to set up a machine, how
to take on work, and where to look when something fails. `uv run python tools/onboard_check.py`
checks most of the first-day checklist on your machine.

This page is not a governed document. The rules it summarises live in `CLAUDE.md` and the guides
under `docs/guides/`; where this page and those differ, they win.

## 1. The system in 60 seconds

- The team works in **two repositories**. This one, the **control repository**, holds the ideas,
  plans, backlog, review records and the agents that move work along. The **product repository**
  holds the code that is demonstrated.
- Work moves through a pipeline: an idea is captured, triaged, grouped into tracks, planned,
  reviewed, and split into **phases** in `backlog/backlog.yaml`. One phase is one session of work.
- A developer **claims** a phase on control `dev`, builds it in a product worktree, and closes it
  with `session-close`. A passing **gating review** by an agent is the approval to merge.
- Both repositories have `dev` (where work integrates) and `main` (one merge per demo release).
  Phase branches reach `dev` through a pull request merged with a merge commit.
- Every session starts with `/start`, which asks for the mode: **Planning**, **Implementing** or
  **Validating**.
- Demo: 2026-11-05. Code freeze: 2026-11-03.

## 2. The two repositories

```
            control repository  (this one)                product repository
  +---------------------------------------------+   +------------------------------+
  | ideas/        idea log                      |   | the product's code, tests,   |
  | backlog/      phases = claims (lock table)  |   | infrastructure               |
  | docs/         plans, requirements, guides,  |   |                              |
  |               reviews, workstreams          |   | .github/workflows/           |
  | brain/        shared memory                 |   |   product-ci.yml  (verify)   |
  | .claude/      agents, permissions           |   |                              |
  | plugins/      the idea-realization plugin   |   |                              |
  +---------------------------------------------+   +------------------------------+
     branches: main, dev                                branches: main, dev
     claim and completion commits: direct to dev        every change: pull request to dev
     other changes: pull request to dev                 required check: verify

  One phase, one session:

     control dev ---- claim commit ------------------------------- completion commit
          |                                                               ^
          +-- agent/<phase-id>  (control worktree: session record) --PR--+
                                                                          |
     product dev -----------------------------------------------------merge commit
          |                                                               ^
          +-- agent/<phase-id>  (product worktree: the code) ---gating review, PR
```

The full account is `plugins/idea-realization/docs/two-repositories.md`, and the branch and pull
request rules are the branching and CI guide (`OPS-001`).

## 3. First-day checklist

Do these once per machine, in order. Run `uv run python tools/onboard_check.py` at any point: it
prints `OK` or `FIX` for each item it can check, and the commands it cannot run for you.

1. **Install the tools.**
   - `uv` (Python runs through it).
   - Claude Code (the `claude` command).
   - The GitHub CLI `gh`, then `gh auth login` to the team's GitHub organization.
     `session-close` opens and merges pull requests with `gh`, so it must be authenticated.
2. **Clone the control repository** and enter it. Ask the owner for its URL.

   ```bash
   git clone <control repository URL>
   cd <control repository>
   git checkout dev
   uv sync --extra dev
   ```

3. **Set your git identity and register it.**
   - `git config user.email <your work email>`.
   - Add yourself to the `owners` map in `docs/systems.yaml`: the key is your handle (lower-case
     letters and digits, starting with a letter, at most 16 characters), the value lists your git
     email. The handle is how every claim, idea and brain entry names you.

     ```yaml
     owners:
       ana:
         description: Ana, user interface workstream.
         emails: [ana@example.com]
     ```

   - Check it: `uv run plugins/idea-realization/scripts/identity.py` prints your handle.
   - Commit only `docs/systems.yaml` directly on control `dev` and push at once (it is
     bookkeeping; `OPS-001`, section 3).
4. **Install the git hooks**: `git config core.hooksPath tools/git-hooks`. The pre-commit hook
   runs the private-content check and the repository check.
5. **Get the deny-list from the owner** and save it as `.private/deny-list.txt` in the primary
   checkout. `.private/` is gitignored. The pre-commit hook refuses any commit that contains a
   listed identifier. Never copy anything from it into a tracked file.
6. **Write your machine's configuration**: copy `.idea-realization/local.example.yaml` to
   `.idea-realization/local.yaml` (gitignored) and fill it in.
   - `product_root`: the absolute path of your product checkout (step 9).
   - `control_remote` and `product_remote`: the git URLs of the two repositories, from the owner.
     They are not tracked, because a URL can name a confidential organization.
     `control_github` and `product_github` (`<org>/<repo>`) are optional and used by `gh`.
   - `aws_read_profile`, `aws_deploy_profile` and, if the team's default does not apply,
     `aws_region` (step 8).
   - `handle`: your handle from step 3.

   `uv run plugins/idea-realization/scripts/paths.py show` prints every value and where it came
   from.
7. **Scaffold and check the repository.**

   ```bash
   uv run plugins/idea-realization/scripts/scaffold.py --feature all   # never overwrites a file
   uv run plugins/idea-realization/scripts/doctor.py                   # must exit 0
   uv run plugins/idea-realization/scripts/check.py                    # must exit 0
   ```

8. **Set up AWS** as `aws/README.md`, "Setup (each developer)", describes: two named profiles in
   `~/.aws/config`, one for the read role and one for the deploy role, and no `default` profile or
   `AWS_` credential variables. Then:

   ```bash
   uv run python tools/check_aws_machine.py --probe   # must print OK
   tools/aws-sandbox whoami                           # both profile names and the read identity
   ```

9. **Clone the product repository** beside the control repository, set `product_root` to it, and
   check that it is the right repository:

   ```bash
   git clone <product repository URL> ../<product>
   git -C ../<product> checkout dev
   uv run plugins/idea-realization/scripts/product.py verify   # prints "origin: matches"
   ```

10. **Start Claude Code** in the control repository with the plugin loaded:

    ```bash
    claude --plugin-dir plugins/idea-realization
    ```

    The session banner prints your handle, the product checkout and the days to the demo. A line
    marked `(unavailable: ...)` is a setup step above that is not done yet.

Finish by running `uv run python tools/onboard_check.py` until it exits 0.

## 4. Claim your workstream

A workstream is a set of paths one developer owns, such as `product:web/`. The owner lists the
workstreams in `docs/workstreams.yaml`; each developer claims one.

```bash
uv run plugins/idea-realization/scripts/workstreams.py show
uv run plugins/idea-realization/scripts/workstreams.py claim <id>
```

`claim` only edits the file. Commit `docs/workstreams.yaml` directly on control `dev` and push at
once. If the push is rejected, someone pushed first: `git pull --rebase`, run
`workstreams.py check`, and push again if the workstream is still yours.

In the first two days each workstream writes the interface documents the others build against.
The team workflow guide (`OPS-005`, sections 1 and 2) has the details.

## 5. Pick a mode with `/start`

Before every session, in the primary checkout of each repository: `git pull origin dev`.

Then run `/start` and choose a mode:

| Mode | What you do | Guide |
|---|---|---|
| Planning | Turn captured ideas into approved plans and backlog phases | `docs/guides/OPS-002-planning-mode.md` |
| Implementing | Claim one phase, build it, verify it, merge it | `docs/guides/OPS-003-implementing-mode.md` |
| Validating | Review a plan, a peer's branch, infrastructure or spend; change nothing | `docs/guides/OPS-004-validating-mode.md` |

The one-page versions are in `docs/guides/OPS-009-mode-cheat-sheets.md`.

## 6. Your first phase, end to end

The implementing-mode guide (`OPS-003`) is the full procedure. In short:

1. `/start`, choose Implementing. Pull `dev` first.
2. `/idea-realization:backlog`: see the ready queue. Take the first ready phase in `next_up` order,
   preferring one assigned to you (`owner: <your handle>`).
3. `/idea-realization:session-start`: it asks before claiming, then commits the claim directly on
   control `dev` and pushes at once, and cuts `agent/<phase-id>` worktrees in both repositories
   from `origin/dev`.
4. Add the product worktree to the session: `/add-dir <product worktree>`. Run the product's
   tests once before changing anything.
5. Build inside the phase's declared `systems` and `deliverables`. Commit small diffs. Push your
   own branch whenever you like.
6. `/idea-realization:checkpoint` whenever you stop: it records progress and never marks the phase
   complete.
7. Run every command in the phase's `verification` list and keep the real output.
8. `/idea-realization:session-close`: rebases both branches, runs the gating review, opens and
   merges both pull requests with merge commits, and writes the completion commit on control
   `dev`.
9. Record what the next session should know in the brain (`/idea-realization:brain`).

## 7. Daily cadence

Morning sync (pull `dev`, the owner ranks and assigns, agents claim), midday integration (rebase
open branches onto `origin/dev`, merge what passed review), end of day (close or checkpoint every
phase, record learnings in the brain, push every branch). The table is in `OPS-005`, section 5.

## 8. Rules that bite

- **Pull `origin dev` before any work, and push right after any claim or bookkeeping commit.** An
  unpushed claim lets two people claim the same phase.
- **Every session works in its own worktree.** The primary checkout's branch is never switched.
- **Never write a confidential identifier into a tracked file**: no organization or client name,
  account id, email or repository URL in code, documents or commit messages.
- **Never commit with `--no-verify`, never force-push `dev` or `main`, never route around a hook.**
  A failing check is a result to fix or report.
- **Every AWS command goes through `tools/aws-sandbox`.** No `default` profile, no `AWS_`
  variables, no bare `aws`. Only the `aws-deploy` agent writes; every delete asks a person.
- **A `backlog/backlog.yaml` conflict is normal**: keep both sides. Never resolve it with `--ours`
  or `--theirs`.
- **Build against merged interfaces and mocks**, never against a peer's unmerged branch.
- **Never edit `CLAUDE.md`** without the owner's approval of that change.
- **A new ask that comes up mid-session is recorded as an idea** (`/idea-realization:idea`), not
  folded into the phase in progress.
- **The control repository's CI fails when the `DENY_LIST` secret is missing.** The owner sets it;
  tell the owner if CI reports it absent.

## 9. Help

- **Something failed**: the troubleshooting guide (`docs/guides/OPS-008-troubleshooting.md`) covers
  rejected pushes, backlog conflicts, doctor drift, hook refusals, pull request and CI failures,
  AWS access errors and port clashes.
- **Why was something decided, and what does a term mean**: the brain.
  `uv run plugins/idea-realization/scripts/brain.py load --query <word>`, or `brain/index.md`.
- **Demo day**: `docs/guides/OPS-006-demo-day-runbook.md`. **AWS cost**:
  `docs/guides/OPS-007-cost-guardrails.md`.
- **Anything else**: ask the owner. Raise a blocker or question with the issue templates in
  `.github/ISSUE_TEMPLATE/`.

## 10. Directory map

| Path | What it holds |
|---|---|
| `CLAUDE.md` | The instructions for every agent: orientation and the rules |
| `ONBOARDING.md` | This page |
| `ideas/` | The append-only idea log, its rendered view, the priority list and accepted partitions |
| `backlog/backlog.yaml` | Phases, one session each; on `dev` it is also the lock table |
| `backlog/batches.yaml` | Owner-approved, ordered batches of phases grouped into stages |
| `docs/` | Governed documents: `plans/`, `requirements/`, `decisions/`, `architecture/`, `governance/`, `sessions/`, `prompts/`, plus `codes.yaml`, `systems.yaml`, `workstreams.yaml` and the generated `catalog.md` |
| `docs/guides/` | The operating guides (`OPS-001` to `OPS-009`): branching and CI, the three modes, team workflow, demo day, cost, troubleshooting, cheat sheets |
| `docs/reviews/` | Review verdict records |
| `brain/` | The team's shared memory: decisions, research, concepts, entities, learnings |
| `.claude/agents/` | The planner, the review-gate agents and the AWS agents |
| `.claude/settings.json` | Permission rules, including the AWS rules |
| `plugins/idea-realization/` | The plugin: scripts, skills, schemas, templates, protocol documents and its tests |
| `.idea-realization/` | Shared project and product settings, the local configuration template, install state and schema copies |
| `.github/` | CI workflow, rulesets, the pull request template and issue templates |
| `templates/product-repo/` | The starting files for the product repository |
| `tools/` | The confidentiality check, the onboarding check, the AWS sandbox wrapper and machine check, the AWS PreToolUse hook and the git hooks |
| `aws/` | The sandbox's two IAM role policies and their setup page |
| `test/` | Tests for `tools/` |
| `.private/` | Untracked: the deny-list and other per-machine confidential files |
