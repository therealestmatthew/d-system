# AGENTS.md

The working agreement for every agent in this repository, human-directed or autonomous. Framework-specific
orientation files (e.g., `CLAUDE.md`, `GEMINI.md`) orient you to what the project is and where things live;
this file governs how you work. Where the two ever disagree, this file wins.

## Never edit this file or CLAUDE.md without explicit approval

**No agent modifies `AGENTS.md` or `CLAUDE.md` for any reason without the owner's explicit approval
for that specific change.** There is no exception. Not to fix something you are certain is wrong.
Not to record something you learned this session. Not because a phase's scope appears to cover it.
Not because another document contradicts them. Not as tidy-up alongside a change you were asked to
make.

These two files are the instructions every agent reads before doing anything. An agent that edits
them rewrites its own governing rules and every future agent's, and the edit outlives the session
that made it — usually without anyone reviewing it, because it arrives inside a diff about something
else.

**If you believe either file is wrong, out of date, or missing something: say so and stop.** Describe
the problem, quote the passage, propose exact replacement wording, and let the owner decide. Reading
these files is your job; rewriting them is not.

This rule exists because it was broken. On 2026-09-09 an agent was asked to correct stale references
to a branch and a remote. While doing so it replaced this file's publishing policy with a standing
rule to "ask before pushing" — wording the owner had never requested, inferred from a single
one-time instruction not to push, and shipped inside a commit about unrelated staleness.

## Before you start

1. **Pick up work from the backlog.** Run `uv run python -m src.governance --ready` and take the
   **first ready phase in the rendered order**. `next_up` in `docs/09-backlog/backlog.yaml` is the
   front of the queue and overrides priority; the report shows it as the Queue column. When the
   owner says "execute the next task", that is the phase they mean — no judgment call needed. Use
   the phase's `scope`, `acceptance` and `verification` as the work boundary.
2. **Plan before implementing.** For any non-trivial change, write a `requirement` document
   (observable statements with verification methods) and a `plan` document, then add backlog phases,
   *before* writing implementation code. An open plan with no phases fails the governance check.
   Approval of one plan is not permission to skip the documents for the next piece of work.
3. **Allocate a code for every governed document** with
   `uv run python -m src.governance --next-code <kind>`. Never pick a number by reading a directory.
4. **Run `uv run python -m src.governance` before you finish.** It must exit 0.

## Confidentiality and publishing

- **The repository has a remote, and history is public-capable.** The confidentiality sweep
  ([PLAN-006](docs/01-plans/PLAN-006-confidentiality-sweep.md)) completed on 2026-09-09: history was
  squashed to a single commit, verified to name no confidential identifier in any path or blob, and
  only then pushed to `origin`.
- **Pushing your own branch to `origin` needs no approval.** Publish `agent/<phase-id>` freely;
  `git fetch`, `git pull` and `git push` all work. Backing up your own work is not publishing.
- **Ask before integrating a feature branch into the integration branch.** The merge that lands work
  on the trunk is the owner's call — not the push that backs it up. `dev` is the integration branch
  today; idea `000066` plans to gate `main` behind a pull request from `dev`.
- **Never write a confidential identifier into a tracked file** — not in code, a document, a commit
  message, or a session record *describing* the identifiers. `tools/check_no_private_content.py`
  reads `git ls-files`, so it cannot see a file until that file is staged. Run it **with your
  changes staged**, or the gate passes by not looking. This is not hypothetical: during the sweep,
  the record documenting the fix twice contained the client token, and only the staged run caught it.
- `_private/` is gitignored and holds the owner's real portfolio — named client engagements,
  personal finances and health. Never read or write there unless the owner directs you to.
- `_data/` is the tracked fictional example set, and `_data/tags.json` the shared taxonomy. The real
  records moved to `_private/portfolio/` in `phase-priv-03`; see
  [ADR-009](docs/04-decisions/ADR-009-structure-content-boundary.md).
- Rewriting local history is cheap; rewriting after a push is not. If history ever needs rewriting
  again, say so and stop rather than forcing anything to `origin`.

## Stack

- **Backend**: Python 3.12, FastAPI, DuckDB, Pydantic v2
- **Frontend**: TypeScript, React, Vite (lives in `ts/`)
- **Package manager**: uv (Python), npm (Node)

## Running things

```bash
# Python dev server
uv run uvicorn src.main:app --reload

# Tests
uv run pytest
uv run pytest test/path/to/test_file.py::test_name

# Lint / type-check
uv run ruff check src/ test/
uv run mypy src/

# Governance — run before finishing any documentation change
uv run python -m src.governance                    # must exit 0
uv run python -m src.governance --ready            # what to work on next
uv run python -m src.governance --next-code plan   # allocate a document code
uv run python -m src.governance --catalog          # every document, code and phase state

# Data: rebuild DuckDB from source JSON
uv run python tools/rebuild_db.py

# Frontend dev server
cd ts && npm run dev
```

## Key conventions

- All Python source lives in `src/`. Treat it as a package (`from src.db.connection import ...`).
- DuckDB schemas live in `schemas/` (JSON/YAML definitions) and `sql/` (DDL migrations).
- Do not auto-create `data/` — it is gitignored and the app creates it at runtime.
- `_private/` is gitignored. Never read or write files there unless the user directs you to.
- `docs/04-decisions/` holds Architecture Decision Records (ADRs). Create one when making a non-obvious design choice.
- **Not ready to be either?** Park it in `docs/00-working/` — ungoverned, no code, no front matter
  ([ADR-010](docs/04-decisions/ADR-010-idea-staging.md)). Use it instead of inventing a plan to hold
  an idea; that is how four documents were manufactured on 2026-09-06.
- **Governed plan or ephemeral plan?** A plan that says how the system should work and outlives the
  work goes in `docs/01-plans/` with a code. A plan that says how one task gets done, and that would
  be *deleted* rather than *rewritten* once the work is finished, goes in `_working/` — ungoverned,
  gitignored, no code and no front matter. That test is how you tell the two apart; it is **not**
  permission to delete anything. **Nothing in `_working/` is deleted without the owner's explicit
  approval.**
- **Does an agent in a worktree need to read it?** Then it cannot live in `_working/`, because an
  ignored file never reaches a sibling worktree. Put it in `_tmpagent/`, which is tracked for exactly
  that reason, and follow the claims contract in
  [`_tmpagent/AGENTS.md`](_tmpagent/AGENTS.md): flip it to active before anyone reads it, claim it by
  naming your branch, and release every claim you hold before you finish. See
  [PLAN-015](docs/01-plans/PLAN-015-ephemeral-working-plans.md).

## Workflow expectations

- Prefer narrow diffs — one concern per commit.
- New API routes live under `src/api/routes/` and are registered in `src/api/__init__.py`.
- Never edit `data/` — it is derived and gitignored. Change `_data/` and rebuild.
- Report outcomes honestly. A failing check is a result to record, not a step to retry until quiet.
- How results are reported to the owner — naming work, output volume, when to ask — is in
  [GOV-006](docs/08-governance/GOV-006-conversation-guidelines.md). Framework-specific orientations
  may import it, but all agents should read it once at session start.

### Adding a domain entity

1. Define the schema in `schemas/<entity>.schema.json`.
2. Add DDL to `sql/001_schema.sql`.
3. Add a JSON loader to `tools/rebuild_db.py`.
4. Create the `_data/<entity>/` directory.
5. Add a Pydantic model in `src/models/`.
6. Add a route module in `src/api/routes/` and register it in `src/api/__init__.py`.

## Documentation governance

- Follow `docs/08-governance/GOV-001-protocol.md` for documentation metadata and lifecycle.
- Every governed document needs a `code`. Get it from
  `uv run python -m src.governance --next-code <kind>` (add `--parent <doc-id>` for a child
  plan), name the file `<code>-<slug>.md`, and never pick a number by reading the directory —
  it cannot show you reserved or retired codes. See `docs/08-governance/GOV-005-document-codes.md`.
- Regenerate `docs/08-governance/catalog.md` with `--catalog` after changing any document; CI
  diffs it and fails when it is stale.
- Run `uv run python -m src.governance` after changing governed documents or memories.
- Use `uv run python -m src.governance --inventory` for component maturity and open plans.
- Update `docs/08-governance/systems.yaml` when component responsibilities or maturity change.
- Plans describe proposed work; verify implementation in code before claiming a capability exists.
- A new tool under `tools/` ships with its own `OPS-*` operations document in
  `docs/08-governance/`, named `OPS-NNN-<tool-stem-with-hyphens>.md` so
  `tools/generate_tool_docs.py` can pair them by filename. Write the narrative by hand, leave the
  `<!-- generated:tool-reference:start/end -->` block empty, then run the generator to fill it.

## Session backlog

- Capture every open plan in `docs/09-backlog/backlog.yaml` before implementing its work.
- Each backlog item is one phase that fits one session, including acceptance checks and handoff.
- Read `docs/08-governance/GOV-003-backlog-decisions.md` for accepted choices that resolve older plan conflicts.
- Run `uv run python -m src.governance --ready` to select work; up to `max_active` phases run at once.
- Take the **first ready phase in the rendered order**. `next_up` in `backlog.yaml` is the front
  of the queue and overrides priority; the report prints it as the Queue column. When the owner
  says "execute the next task", that is the phase they mean — no judgment call needed.
- Remove a phase from `next_up` in the same change that completes it.
- Record the session, existing evidence files and actual results before marking a phase complete.
- Keep deferred work visible with a resume condition; split phases that exceed one session.
- Checkpoint your progress mid-session by writing updates to your phase's session record (e.g., using
  an available checkpoint skill). It is safe to record progress any number of times, but do not mark a phase complete;
  only the owner-invoked review (e.g., `/session-close`) does that. An agent must never invoke final closure itself.

## Concurrent agents: claim a phase

`dev` is the integration branch — the trunk every agent claims on and integrates back into. Agent
work happens on `agent/<phase-id>` branches that are integrated and deleted. Read any older
reference to `main` as `dev`: `main` was the trunk until 2026-09-09, when `phase-priv-05` squashed
history onto it and pushed; day-to-day work then moved to `dev`, and idea `000066` plans to gate
`main` behind pull requests from `dev`. Release tagging, if it is ever introduced, will use tags
rather than another long-lived branch.

A remote now exists, so `git fetch`, `git pull` and `git push` all work — but **ask the owner before
pushing** (see *Confidentiality and publishing*).

Several agents may work at once. `docs/09-backlog/backlog.yaml` on `dev` is the lock table, and
`uv run python -m src.governance` is the lock check. See [ADR-003](docs/04-decisions/ADR-003-multi-agent-concurrency.md).

- Pick your own agent ID once and reuse it: lowercase `agent-<name>`, e.g. `agent-blue`. One agent
  holds at most one active phase.
- Start on an up-to-date `dev`: `git switch dev && git pull`.
- Run `uv run python -m src.governance --ready`. Choose a phase whose **Conflicts** column is `—`.
  A non-empty Conflicts column means a peer already locked one of your systems or paths — pick
  something else; do not wait, and do not edit a peer's claim.
- Claim it on `dev` in one small commit that changes nothing else: set the phase `status: active`,
  add `agent: agent-<name>`, and bump the catalog `updated` date.
- Run `uv run python -m src.governance` before committing the claim. It rejects your claim if it
  overlaps a peer's systems, deliverable paths, or dependency chain, or if `max_active` is reached.
- Commit the claim on `dev`. If the push is rejected as non-fast-forward,
  `git pull --rebase`, re-run the validator, and re-check that your claim is still safe — a peer
  claimed between your check and your push, and their systems may now collide with yours.

## Concurrent agents: work in a worktree

A worktree is required, and the primary checkout's branch must never be switched, whenever a peer
holds an active claim or the phase touches `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`.
Each agent gets a physically separate directory, so tests, rebuilds and dev servers cannot corrupt a
peer's run. A solo agent on a documentation- or skill-only phase, with no peer claim and no
deliverable outside `docs/` or framework-specific directories (e.g., `.claude/`), may instead work directly in the primary checkout on
`dev` — see [GOV-003](docs/08-governance/GOV-003-backlog-decisions.md).

```bash
# from the primary checkout, on an up-to-date dev
git worktree add -b agent/phase-html-03 ../d-system-worktrees/phase-html-03 dev
cd ../d-system-worktrees/phase-html-03
uv venv && uv sync --extra dev            # each worktree has its own .venv
uv run python tools/rebuild_db.py         # each worktree has its own gitignored data/
```

- Branch name is always `agent/<phase-id>`. Worktree directory is always
  `../d-system-worktrees/<phase-id>` — a sibling of the repository, never inside it, so that
  `pytest`, `ruff`, `mypy` and the governance Markdown scanner never walk a second copy of the tree.
- `.venv/`, `data/` and `ts/node_modules/` are gitignored and therefore per-worktree. Install them
  in the worktree; do not symlink a peer's.
- If you run a dev server, pick a free port explicitly
  (`uv run uvicorn src.main:app --reload --port 8010`). Do not assume `:8000` or `:5173` is yours.
- Stay inside your phase's declared `systems` and `deliverables`. If the work genuinely requires a
  file outside them, stop: either narrow the change, or update the phase's declarations on `dev`
  and re-run the validator so peers see the wider lock before you continue.
- Commit narrow, atomic diffs — one concern per commit, on your branch only.
- The only line of `backlog.yaml` you may touch is your own phase's, plus the catalog `updated` date.
- Rebase onto `dev` rather than merging it in: `git rebase dev`. Do this whenever a peer integrates,
  not only at the end.

## Concurrent agents: complete and hand off

Perform these in order. Do not mark a phase complete before the post-rebase validator run passes.

1. Run every command in the phase's `verification` list inside your worktree and keep the real
   output. Record actual results — a failing check is a result, not a reason to skip the step.
2. Write a session record with governed front matter (`kind: session`), covering outcomes, evidence
   and anything unresolved. Allocate its code with
   `uv run python -m src.governance --next-code session` and name the file `<code>-<topic>.md`; the
   code's date must equal the document's `created` date.
3. Confirm each `acceptance` condition is genuinely met. If any is not, leave the phase `active` or
   return it to `queued` with an exact `next_action` — and release your `agent` claim when you do.
4. Update your phase: `status: complete`, `session:`, `completion_evidence:` (files that exist now),
   and `result:` summarizing the actual verification output. Keep the `agent` field as the record of
   who did the work.
5. `git rebase dev`, then re-run `uv run python -m src.governance` and
   `uv run pytest`. This run — after the rebase, against your peers' merged work — is the one that
   decides whether the branch may integrate. If it fails, fix it on your branch; never integrate a
   red rebase.
6. Check that the primary `dev` checkout is completely clean (`git status` shows no unstaged changes).
   **Never use `git stash` or force an integration if a peer agent has left uncommitted work.**
7. If `dev` is clean, integrate the branch onto `dev` (fast-forward after the rebase), then clean up:
   `git worktree remove ../d-system-worktrees/<phase-id>` and `git branch -d agent/<phase-id>`.
   If `dev` is dirty or manual review is required, leave your branch unmerged. Report that the work is ready
   for review so the owner (or a peer) can `git diff dev..agent/<phase-id>` and merge it manually.

## Concurrent agents: resolve collisions

- **`backlog.yaml` conflicts are normal.** Two agents edited different items in one file. Keep *both*
  sides: take the peer's items verbatim, keep only your own item's edits, set `updated` to today.
  Never resolve with `--ours` or `--theirs` on this file — either one silently deletes a peer's work.
- **A duplicate-code error means you and a peer took the same number.** Codes are free before
  merge and permanent after, so the agent integrating second renumbers: allocate again, rename
  the file, and update any reference you added. Reserve your code in `codes.yaml` alongside your
  backlog claim to avoid the race entirely.
- **A conflict in `src/`, `ts/`, `schemas/` or `sql/` means the safety rule was bypassed.** Disjoint
  phases should not produce source conflicts. Stop, do not force a merge, and report it: the phases'
  declared `systems` or `deliverables` were wrong, and the declarations need fixing before either
  phase completes.
- **A green branch that fails after rebase** means a peer changed behavior you depended on. Fix your
  branch against current `dev`; do not revert the peer's commit.
- When resolving a collision requires an actual choice — which phase yields, whether a boundary
  moves, whether a phase splits — record the decision and its reason in
  `docs/08-governance/GOV-003-backlog-decisions.md` in the same diff. Do not encode a resolution only in a
  commit message.
- If you are working an area adjacent to a peer's — your system `depends_on` theirs in
  `systems.yaml` — treat their contract as frozen at the commit you branched from. Build against
  merged `dev`, never against a peer's unmerged branch.
