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
- Every session starts with the `start` skill, which asks for the mode: **Planning**,
  **Implementing** or **Validating**.
- Demo: 2026-11-05. Code freeze: 2026-11-03.

**Skill names.** Each of the plugin's skills runs by its short name, such as `/start`, unless
another command already uses that name. The long form `/idea-realization:<skill>`, such as
`/idea-realization:start`, always works.

**Terms used on this page.**

- **Bookkeeping**: the small commits that go directly on control `dev` with no pull request: claims,
  completions, ideas and workstream claims (`OPS-001`, section 3), and your own entry in
  `docs/systems.yaml` (step 5 below).
- **Lock table**: `backlog/backlog.yaml` on control `dev`. A phase marked `active` there is locked
  by whoever claimed it.
- **Gating review**: the agent review in `session-close` whose passing verdict is the approval to
  merge. A **shadow** review runs alongside it and is recorded, but decides nothing.
- **Owner** has several meanings. *The owner* is the person who runs the team's repositories,
  assigns work and approves plans and merges to `main`. `owner:` on a backlog phase is the developer
  it is assigned to; `repository-owner` there means it is not assigned to anyone yet. A workstream's
  owner is the developer who claimed it. `owner:` on a document or system names the key in
  `docs/systems.yaml`'s `owners` map that is responsible for it.

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

Run every command below from the control repository's root. The scripts find the root from git, so
none of them needs `IDEA_REALIZATION_ROOT`. Do not `export` that variable: with it set,
`uv run pytest` fails (`OPS-001`, section 7). When a script does resolve the wrong root, set it on
that one command only (`OPS-008`, "check.py reports files from the wrong repository").

1. **Install the tools.**
   - `uv` (Python runs through it).
   - Claude Code (the `claude` command).
   - The GitHub CLI `gh`, then `gh auth login` to the team's GitHub organization.
     `session-close` opens and merges pull requests with `gh`, so it must be authenticated, and you
     need write access to both repositories. Ask the owner if you were not invited to both.
   - The AWS CLI v2 (the `aws` command). `tools/aws-sandbox` runs it; you never run `aws` yourself.
   - Node.js and npm, for product work: each product worktree runs `npm install`, and
     `tools/aws-sandbox synth` runs the CDK CLI from the product's `node_modules`.
2. **Clone the control repository** and enter it. Ask the owner for its URL.

   ```bash
   git clone <control repository URL>
   cd <control repository>
   git checkout dev
   uv sync --extra dev
   ```

3. **Install the git hooks**: `git config core.hooksPath tools/git-hooks`. The pre-commit hook
   runs the private-content check and the repository check. Install it before your first commit.
4. **Get the deny-list from the owner** and save it as `.private/deny-list.txt` in the primary
   checkout. `.private/` is gitignored. The pre-commit hook refuses any commit that contains a
   listed identifier; without the list it skips that part of the check. Never copy anything from
   it into a tracked file.
5. **Set your git identity and register it.**
   - `git config user.email <your work email>`.
   - Add yourself to the `owners` map in `docs/systems.yaml`: the key is your handle (lower-case
     letters and digits, starting with a letter, at most 16 characters), the value lists your git
     email. The handle is how every claim, idea and brain entry names you. A work email here is
     expected; it is not a confidential identifier.

     ```yaml
     owners:
       ana:
         description: Ana, user interface workstream.
         emails: ["<handle>@<work-domain>"]
     ```

   - Check it: `uv run plugins/idea-realization/scripts/identity.py` prints your handle.
   - Commit only `docs/systems.yaml` directly on control `dev` and push at once (the team workflow
     guide, `OPS-005`, section 1, treats it as bookkeeping). The hook from step 3 checks this
     commit. If the push is rejected, someone pushed first: `git pull --rebase origin dev`, then
     push again.
6. **Write your machine's configuration**: copy `.idea-realization/local.example.yaml` to
   `.idea-realization/local.yaml` (gitignored) and fill in what you know now. Delete a key you do
   not set; a value left as `REPLACE-WITH-...` counts as unset, and `onboard_check` reports it.
   - `handle`: your handle from step 5.
   - `control_remote` and `product_remote`: the git URLs of the two repositories, from the owner.
     They are not tracked, because a URL can name a confidential organization.
     `control_github` and `product_github` (`<org>/<repo>`) are optional and used by `gh`.
   - `product_root` comes in step 9, and `aws_read_profile`, `aws_deploy_profile` and, if the
     team's default does not apply, `aws_region` in step 8. Leave them until then.

   `local.yaml` is where this team keeps every per-machine value. A value is taken from, in order:
   a command-line flag, an `IDEA_REALIZATION_<KEY>` environment variable, `local.yaml`, a saved
   plugin option, the tracked `.idea-realization/project.yaml` or `product.yaml`, and the plugin's
   default. Do not set plugin options for this team: `local.yaml` covers every key.
   `uv run plugins/idea-realization/scripts/paths.py show` prints every value and where it came
   from.
7. **Scaffold and check the repository.**

   ```bash
   uv run plugins/idea-realization/scripts/scaffold.py --feature all   # never overwrites a file
   uv run plugins/idea-realization/scripts/doctor.py                   # must exit 0
   uv run plugins/idea-realization/scripts/check.py                    # must exit 0
   ```

8. **Set up AWS** as `aws/README.md`, "Setup (each developer, once per machine)", describes: two
   named profiles in `~/.aws/config`, one for the read role and one for the deploy role, and no
   `default` profile or `AWS_` credential variables. Ask the owner what your sandbox login profile
   is (the `source_profile` the two profiles use). Put the two profile names, and the region if it
   differs from the team's, in `local.yaml`. Then:

   ```bash
   uv run python tools/check_aws_machine.py --probe   # must print OK
   tools/aws-sandbox whoami                           # both profile names and the read identity
   ```

   If your sandbox access is not ready yet, skip this step and come back to it before your first
   phase that touches AWS. Until you name an AWS profile in `local.yaml`, `onboard_check` shows the
   AWS lines as `NOTE` (pending the owner's AWS setup) and they do not fail it; once you name one,
   they are checked and a problem is a `FIX`. The rest of the checklist does not depend on them.
9. **Clone the product repository** beside the control repository, set `product_root` in
   `local.yaml` to it, and check that it is the right repository:

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

   `onboard_check` checks both (the `product hooks` and `product deny-list` lines).

10. **Start Claude Code** in the control repository's primary checkout:

    ```bash
    claude
    ```

    The first time, Claude Code asks whether you trust the folder. Accept: the project settings
    (`.claude/settings.json`) load the plugin only in a trusted folder. `/start` then exists; if
    it does not, run `/plugin` and check that `idea-realization@idea-realization-team` is enabled.

    There is no product worktree yet, so nothing else is added at launch. `session-start` creates
    one when you claim a phase, and you add it then with `/add-dir` (section 6, step 4).

    The session banner prints your handle, the product checkout and the days to the demo. A line
    that reads `not set on this machine` or `(unavailable: ...)` is a setup step above that is not
    done yet.

Finish by running `uv run python tools/onboard_check.py` until it exits 0, or until only the AWS
lines of step 8 remain while your sandbox access is pending.

## 4. Claim your workstream

A workstream is a set of paths one developer owns, such as `product:web/`. The owner lists the
workstreams in `docs/workstreams.yaml`; each developer claims one.

```bash
uv run plugins/idea-realization/scripts/workstreams.py show
uv run plugins/idea-realization/scripts/workstreams.py claim <id>
```

If `show` prints nothing, the owner has not defined any workstreams yet; there is nothing to claim,
and you can come back to this section when they have.

`claim` only edits the file. It rewrites the whole file, so a comment in it is dropped; that line
in your diff is expected. Commit `docs/workstreams.yaml` directly on control `dev` and push at
once. If the push is rejected, someone pushed first: `git pull --rebase origin dev`, run
`workstreams.py check`, and push again if the workstream is still yours. Two claims of different
workstreams can still conflict, because `claim` rewrites the whole file. If the rebase stops on a conflict in `docs/workstreams.yaml`, keep both sides: each
workstream keeps the lines its own claim wrote, whichever side they came from. Never resolve it
with `--ours` or `--theirs`.

In the first two days each workstream writes the interface documents the others build against.
The team workflow guide (`OPS-005`, sections 1 and 2) has the details.

## 5. Pick a mode with `/start`

Before every session, in the primary checkout of each repository: `git pull --rebase origin dev`.
The `--rebase` keeps an unpushed bookkeeping commit on top instead of making a merge commit on
`dev`.

Then run `/start` and choose a mode:

| Mode | What you do | Guide |
|---|---|---|
| Planning | Turn captured ideas into approved plans and backlog phases | `docs/guides/OPS-002-planning-mode.md` |
| Implementing | Claim one phase, build it, verify it, merge it | `docs/guides/OPS-003-implementing-mode.md` |
| Validating | Review a plan, a peer's branch, infrastructure or spend; change nothing | `docs/guides/OPS-004-validating-mode.md` |

The one-page versions are in `docs/guides/OPS-009-mode-cheat-sheets.md`; prompts to paste for each mode are in `docs/guides/OPS-010-day-one-prompts.md`.

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
8. Record what the next session should know in the brain (`/idea-realization:brain`), in the
   control worktree, so the entry reaches `dev` in the phase's control pull request.
9. `/idea-realization:session-close`: rebases both branches, runs the gating review, opens and
   merges both pull requests with merge commits, and writes the completion commit on control
   `dev`.

## 7. Daily cadence

Morning sync (pull `dev` with `--rebase`, the owner ranks and assigns, agents claim), midday integration (rebase
open branches onto `origin/dev`, merge what passed review), end of day (close or checkpoint every
phase, record learnings in the brain, push every branch). The table is in `OPS-005`, section 5.

## 8. Rules that bite

- **Pull `origin dev` with `--rebase` before any work, and push right after any claim or bookkeeping commit.** An
  unpushed claim lets two people claim the same phase.
- **Every session works in its own worktree.** The primary checkout's branch is never switched.
- **Never write a confidential identifier into a tracked file**: no organization or client name,
  account id or repository URL in code, documents or commit messages. Your work email is not
  confidential: it belongs in your own `docs/systems.yaml` entry (section 3, step 5) and nowhere
  else.
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
- **The guidebook is generated.** `docs/guidebook.html` is built from the documents
  `tools/guidebook.yaml` lists (this page among them). When you change one of them, run
  `uv run python tools/build_guidebook.py` and commit the regenerated page with it: CI runs it with
  `--check` and fails on a stale guidebook.

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
| `docs/guides/` | The operating guides (`OPS-001` to `OPS-010`): branching and CI, the three modes, team workflow, demo day, cost, troubleshooting, cheat sheets, day-one prompts |
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
