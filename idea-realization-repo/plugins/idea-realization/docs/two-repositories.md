# Two repositories: control and product

A team that builds a product with this pipeline keeps two repositories.

- The **control repository** holds every governed record and every rule: ideas, requirements,
  plans, decisions, the backlog, session records, review records, agents, skills and this plugin.
  It is where work is decided, claimed and recorded. Every developer clones it from one shared
  remote.
- The **product repository** holds the product: its code, its tests and its CI. It carries as
  little process as possible.

Agent sessions start in the control repository, so its agents, skills, `CLAUDE.md` and `AGENTS.md`
apply, and reach the product worktree with `--add-dir` (or `/add-dir` inside a session).

## Naming the product repository

`.idea-realization/product.yaml` is tracked in the control repository and says what is the same on
every machine:

```yaml
schema_version: 1
name: <product name>
remote: <git URL of the product repository>
integration_branch: main
ci_workflow: none
```

Where the product checkout sits differs per machine, so it is configured and never tracked:

| Key | Environment variable | Meaning |
|---|---|---|
| `product_root` | `IDEA_REALIZATION_PRODUCT_ROOT` | This machine's product checkout; outside the control repository |
| `product_worktree_dir` | `IDEA_REALIZATION_PRODUCT_WORKTREE_DIR` | Where product worktrees go; default `../<product>-worktrees`, beside the product checkout |

`uv run plugins/idea-realization/scripts/product.py verify` prints the product checkout, its
integration branch and its worktree directory, and **refuses unless the checkout's `origin` is the
tracked `remote`**. Every procedure that acts on the product repository runs it first, so a wrong
path cannot send work into the wrong repository.

Without `product_root`, everything that only reads or writes the control repository still works:
ideas, plans, the backlog, the checks. Anything that needs the product checkout says it is not
configured and stops.

## Where each step happens

| Step | Repository | Where |
|---|---|---|
| Ideas, triage, partition, plans, requirements, decisions | control | as usual |
| The backlog, the claim commit, the catalog | control | primary checkout, control integration branch |
| The phase's code, tests and verification commands | product | `agent/<phase-id>` in `<product worktree dir>/<phase-id>` |
| The session record, checkpoints, review verdict records | control | the paired `agent/<phase-id>` in `<worktree dir>/<phase-id>` |
| The gating review | both | judges the product diff against the control documents |
| The product merge, prepared | product | fast-forwarded locally, not yet pushed |
| The completion record | control | on the control branch, merged and pushed first |
| The product push | product | after the control push |

The `session-start` and `session-close` skills carry out these steps in order.

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
  one; without one, only its shape is checked.
- A verification command runs in the product worktree unless it starts with `control:`.

## Approval

A passing gating review approves the product merge and the control merge that carries the
phase's records. There is no separate per-merge approval. The owner keeps every decision the
backlog protocol reserves, such as accepting plans and ranking the queue.

## A stranded phase

`session-close` pushes the control record before the product merge, so product code never lands
without a record. The one state that can be left behind is the reverse: the control repository
records a phase complete with a `product_merge` that is not on the product integration branch,
because the product push failed. The check reports it as `stranded` wherever a product checkout is
configured.

Recover it in this order:

1. If the product checkout still holds the prepared merge (`git -C <product checkout> log -1`
   shows the `product_merge` commit) and the integration branch has not moved, push it. The check
   then reports nothing.
2. Otherwise, reopen the phase in the control repository: set it back to `active` with a
   `next_action` naming the stranded merge, and remove its `product_merge`, in one commit. Then
   rebase the product branch, run the verification, review the new `HEAD`, and close the session
   again.

Never edit `product_merge` to a commit the recorded verdict did not judge.
