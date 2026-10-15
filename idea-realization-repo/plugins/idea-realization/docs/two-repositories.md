# Two repositories: control and product

A team that builds a product with this pipeline keeps two repositories.

- The **control repository** holds every governed record and every rule: ideas, requirements,
  plans, decisions, the backlog, session records, review records, agents, skills and this plugin.
  It is where work is decided, claimed and recorded. Every developer clones it from one shared
  remote.
- The **product repository** holds the product: its code, its tests and its CI. It carries as
  little process as possible.

Agent sessions start in the control repository, so its agents, skills and instruction files
(`CLAUDE.md`, and `AGENTS.md` where it has one) apply, and reach the product worktree with `--add-dir` (or `/add-dir` inside a session).

## Naming the product repository

`.idea-realization/product.yaml` is tracked in the control repository and says what is the same on
every machine:

```yaml
schema_version: 1
name: <product name>
integration_branch: dev
ci_workflow: product-ci.yml   # none only for a product with no CI
```

What differs per machine, or must not be tracked, is configured in each machine's untracked
`.idea-realization/local.yaml` (copy `local.example.yaml`; it is read from the primary checkout),
or with the environment variable, which takes precedence:

| Key | Environment variable | Meaning |
|---|---|---|
| `product_root` | `IDEA_REALIZATION_PRODUCT_ROOT` | This machine's product checkout; outside the control repository |
| `product_worktree_dir` | `IDEA_REALIZATION_PRODUCT_WORKTREE_DIR` | Where product worktrees go; default `../<product>-worktrees`, beside the product checkout |
| `product_remote` | `IDEA_REALIZATION_PRODUCT_REMOTE` | Git URL of the product repository |
| `product_github` | `IDEA_REALIZATION_PRODUCT_GITHUB` | The product repository on GitHub, as `<org>/<repo>` |
| `control_remote` | `IDEA_REALIZATION_CONTROL_REMOTE` | Git URL of the control repository |
| `control_github` | `IDEA_REALIZATION_CONTROL_GITHUB` | The control repository on GitHub, as `<org>/<repo>` |

The repository URLs live in `local.yaml` because a URL can name an organization that must not
appear in a tracked file. A team whose URLs may be tracked can set `remote` and `github` in
`product.yaml`, and `control.remote` and `control.github` in `project.yaml`, instead; a value in
`local.yaml` or the environment still overrides them.
`uv run plugins/idea-realization/scripts/paths.py show`
prints each value and the file or variable it came from.

`uv run plugins/idea-realization/scripts/product.py verify` prints the product checkout, its
integration branch and its worktree directory, and **refuses unless the checkout's `origin` is the
resolved `product_remote`**. While `product_remote` is not set it refuses and says to set it in
`local.yaml`. Every procedure that acts on the product repository runs it first, so a wrong
path cannot send work into the wrong repository.

Without `product_root`, everything that only reads or writes the control repository still works:
ideas, plans, the backlog, the checks. Anything that needs the product checkout says it is not
configured and stops.

## Branches

Both repositories have the same branches and names.

| Branch | Holds | How work reaches it |
|---|---|---|
| `main` | released work | a pull request from `dev`, merged with a merge commit, per release |
| `dev` | the integration branch (`integration_branch` in `product.yaml` and in the control repository's configuration) | feature branches through a pull request merged with a merge commit; in the control repository, bookkeeping commits directly |
| `agent/<phase-id>` | one claimed phase; the same name in both repositories | cut from `origin/dev`, merged by `session-close` |
| `agent/<handle>-<slug>` | owner-directed work with no phase | cut from `origin/dev`, merged the same way |

Bookkeeping commits go directly onto control `dev`, never through a pull request: claim commits,
completion commits, idea commits and workstream claims. Pull `origin dev` before any work, and push
a bookkeeping commit as soon as it is made, so peers see it.

## Where each step happens

| Step | Repository | Where |
|---|---|---|
| Ideas, triage, partition, plans, requirements, decisions | control | as usual |
| The backlog, the claim commit, the catalog | control | primary checkout, control integration branch, pushed at once |
| The phase's code, tests and verification commands | product | `agent/<phase-id>` in `<product worktree dir>/<phase-id>` |
| The session record, checkpoints, review verdict records | control | the paired `agent/<phase-id>` in `<worktree dir>/<phase-id>` |
| The gating review | both | judges the product diff against the control documents |
| The control merge | control | pull request from `agent/<phase-id>` into the integration branch, merged with a merge commit |
| The product merge | product | pull request from `agent/<phase-id>`, merged with a merge commit after the required check passes; its second parent must be the reviewed commit |
| The completion record | control | one commit directly on the control integration branch, after the product merge, pushed at once |

The `session-start` and `session-close` skills carry out these steps in order. A repository with no
GitHub remote makes the same merges locally with `git merge --no-ff`.

## Paths in a phase

A path with the prefix `product:` is a path in the product repository; a path without one is a path
in the control repository. The prefix is used in a phase's `deliverables` and
`completion_evidence`, and in a system's `paths` in `systems.yaml`:

```yaml
deliverables:
  - product:src/api/
  - product:test/test_api.py
  - docs/decisions/<code>-api-shape.md
verification:
  - uv run pytest
  - "control: uv run plugins/idea-realization/scripts/check.py"
```

- The concurrency check compares declared paths as written, so two phases that both declare
  `product:src/api/` collide, and `product:src/` and `src/` do not.
- A `product:` completion evidence file is checked in the product checkout when this machine has
  one; without one, only its shape is checked. For a phase that names its `product_merge`, the
  file is read at that commit, not in the working tree, so a checkout that has not pulled the
  merge still finds it. When the checkout does not hold the commit, the check prints a
  `cannot tell` note: fetch the product checkout and run the check again.
- A verification command runs in the product worktree unless it starts with `control:`.

## Approval

A passing gating review approves the product merge and the control merge that carries the
phase's records. There is no separate per-merge approval. The owner keeps every decision the
backlog protocol reserves, such as accepting plans and ranking the queue.

## A merged phase without its completion record

`session-close` merges the product pull request before it writes the completion record, so the one
state a failed close can leave behind is product code merged on the product integration branch
while the control repository still records the phase `active`. Nothing is wrong with the merged
code: it passed the gating review, which is the approval.

Recover it by landing the completion commit, never by undoing the merge:

1. In the control primary checkout, `git pull --rebase`, regenerate the catalog, run the check, and
   `git push`. Repeat until the push lands. A backlog conflict keeps both sides.
2. The completion commit names the merge commit as `product_merge`. Read it from the pull request
   (`gh pr view <n> --json mergeCommit`) if the session that merged it has ended.
3. **Never revert the product merge** to make the two repositories agree. Until the completion
   commit lands, the phase stays `active` and its claim stays held.

## A stranded phase

The reverse state is a phase recorded `complete` whose `product_merge` is not on the product
integration branch. `session-close` does not produce it, because it records completion only after
the merge landed; it means the completion record was written by hand, or the product integration
branch lost the commit. The check reports it as `stranded` wherever a product checkout is
configured.

A product checkout that has not fetched does not know a peer's merge, so before reporting
`stranded` the check asks `origin` where the integration branch is now (`git ls-remote`, which
changes nothing). It reports `stranded` only when this checkout already holds origin's tip and the
commit is not in its history. When origin cannot be read, or has commits this checkout has not
fetched, it prints `cannot tell whether product_merge … landed` instead, which is not an error.

1. **Fetch the product checkout and run the check again** (`git -C <product checkout> fetch
   origin`). A `cannot tell` note, or a `stranded` line that goes away after the fetch, means the
   checkout was behind: the phase is complete and nothing else is done. Never reopen a phase on a
   `cannot tell` note.
2. Only if `stranded` remains after the fetch: confirm it on the forge, which is the record of what
   merged (`gh pr view <n> --json state,mergeCommit` in the product checkout, where `<n>` is the
   phase's product pull request). If the pull request merged as `product_merge`, the product
   integration branch lost the commit; stop and report it to the owner rather than reopening.
3. Otherwise reopen the phase in the control repository: set it back to `active` with a
   `next_action` naming the stranded merge, and remove its `product_merge`, in one commit directly
   on the control integration branch. Then rebase the product branch, run the verification, review
   the new `HEAD`, and close the session again.

Without any product checkout on this machine (control CI is one such place) the check cannot test
landing at all, and prints `product_merge … not checked: no product checkout is configured` for
each complete phase instead.

Never edit `product_merge` to a commit the recorded verdict did not judge: it is the commit the
verdict judged (a fast-forward) or a merge commit whose second parent is that commit.
