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
| The merge | product, then control | fast-forward, after a passing gating review |
| The completion edit | control | primary checkout, after both merges |

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
