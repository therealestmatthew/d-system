---
description: Open a working session — claim the phase, cut the branch and worktree, isolate the environment, and set up the hand-off back to dev
argument-hint: "[phase-id]"
---

# Start the session

Run this **before writing any code or creating any document**. It puts the session in the state the
concurrency protocol assumes: a phase claimed on `dev`, a branch, a worktree of its own, and a known
route back to `dev` when the work is done.

This command is authoritative on the **branch, worktree, isolation and merge-back** half of the
protocol. It is deliberately *not* authoritative on preflight, backlog orientation or the claim's
content — `/backlog` already owns those, and restating them here would duplicate prose that drifts.
`AGENTS.md` governs everything either command says; where they differ, `AGENTS.md` wins.

## Where each step happens

Two directories are involved, and mixing them up is the failure this protocol exists to prevent.

| Step | Where | Why there |
|---|---|---|
| Preflight and orientation | primary checkout, `dev` | Reads only |
| The claim commit and the catalog regeneration it forces | primary checkout, `dev` | `backlog.yaml` on `dev` is the lock table peers read; a claim held anywhere else is invisible and is therefore not a lock |
| Everything else — the work, verification, checkpoints, session record | the worktree | Tests, rebuilds and dev servers must not touch a peer's run |

**The primary checkout's branch is never switched.** Do the two claim steps there, then return to the
worktree and stay there.

## 1. Preflight and orient — run `/backlog`

Run `/backlog` (or `/backlog <phase-id>` if `$ARGUMENTS` names one) and follow it through its
orientation and questions. It runs `uv run python -m src.governance` and `uv run pytest`, shows the
queue, reads the phase and plan, and asks what needs deciding.

**If preflight fails, stop.** Do not create a branch, do not create a worktree, do not claim
anything. Report the failure and nothing else.

**Do not pass `--claim` or `--go`.** Step 2 below is where claiming is decided.

## 2. Stop and confirm before the claim commit

The claim is a mutation that peers read as a lock. Ask, through the `AskUserQuestion` tool, whether
to claim the phase you oriented on — with your recommendation first. Report alongside it:

- the phase id and its **title**, and the plan it belongs to by title
- its `Conflicts` column from `--ready`; if that column is not `—`, say so and recommend a different
  phase, because a peer already holds one of your systems or paths
- anything that looked wrong during orientation — an acceptance condition nothing can verify, a
  missing deliverable, an undeclared dependency

Stop here until the answer comes back. An unanswered question is not a yes.

### Work with no backlog phase

Owner-directed work sometimes has no phase — a one-off document, a command like this one, a fix the
owner asked for directly. Then there is **nothing to claim**: skip steps 2 and 3 entirely, name the
branch and worktree after the work (`agent/<slug>`), and go straight to step 4. Say plainly in your
first report that the session is running unclaimed and that peers therefore hold no lock against it.

Do not manufacture a backlog phase to have something to claim.

## 3. The claim commit — in the primary checkout, on `dev`

Only once the owner has said yes:

```bash
git -C /code/d-system switch dev && git -C /code/d-system pull
```

Edit **only your own phase's lines** in `docs/09-backlog/backlog.yaml`: `status: active`, `agent:
agent-<name>`, and the catalog `updated` date. Pick your agent id once and reuse it across sessions —
lowercase `agent-<name>`. One agent holds at most one active phase.

Then, before committing:

```bash
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
uv run python -m src.governance
```

The validator rejects the claim if it overlaps a peer's systems, deliverable paths or dependency
chain, or if `max_active` is reached. **That rejection is the answer, not an obstacle** — pick a
different phase.

Commit the claim and the regenerated catalog together, in one commit that changes nothing else. The
catalog must go in the same commit; leaving it stale leaves `dev` red on
`test_committed_catalog_matches_regenerated_output`.

If a push is rejected as non-fast-forward: `git pull --rebase`, re-run the validator, and re-check
that the claim is still safe. A peer claimed between your check and your push, and their systems may
now collide with yours.

## 4. Cut the branch and the worktree

Still from the primary checkout, on an up-to-date `dev`:

```bash
git worktree add -b agent/<phase-id> ../d-system-worktrees/<phase-id> dev
cd ../d-system-worktrees/<phase-id>
```

- The branch is always `agent/<phase-id>`. The worktree directory is always
  `../d-system-worktrees/<phase-id>` — a **sibling** of the repository, never inside it, so `pytest`,
  `ruff`, `mypy` and the governance Markdown scanner never walk a second copy of the tree.
- Confirm with `git worktree list` and report the path back to the owner. Every later step in the
  session happens in this directory.

## 5. Isolate the environment

`.venv/`, `data/` and `ts/node_modules/` are gitignored, so each worktree needs its own. Install
them; never symlink a peer's.

```bash
uv venv && uv sync --extra dev
uv run python tools/rebuild_db.py
```

If the work touches the frontend, `cd ts && npm install` as well.

If you run a dev server, pick a free port explicitly — `uv run uvicorn src.main:app --reload --port
8010`. Do not assume `:8000` or `:5173` is yours.

Gitignored content does not travel between worktrees or through a merge. If the work needs
`_private/`, the owner must place it there deliberately, and anything written there must be copied
out by hand before the worktree is removed.

## 6. Claim shared files in `_tmpagent/`

An ignored file never reaches a sibling worktree. Anything an agent in another worktree must read
lives in `_tmpagent/`, which is tracked for exactly that reason, and is governed by
[`_tmpagent/AGENTS.md`](../../_tmpagent/AGENTS.md). The ledger is `_tmpagent/claims.jsonl` —
append-only, one JSON object per line, never edited and never reordered.

**Reading a file there requires a claim.** Append a `claimed` line naming the file, `kind: branch`,
`ref: agent/<phase-id>`, the RFC 3339 timestamp with offset, your agent id, and the branch you wrote
it from. Claim a plan dependency the same way with `kind: plan` and the plan's document id.

**Writing a new file there**: append `created` with a one-line `purpose`, edit it freely while it is
still a draft, then append `activated` before anyone reads it. After that its content is frozen — an
active file that must change gets a successor that names what it replaces.

Never delete a file with an open claim, and never close another agent's claim.

Every claim opened in this session is released in step 8. That is a promise no check enforces, which
is precisely why it has to be deliberate.

## 7. While the session runs

- Stay inside the phase's declared `systems` and `deliverables`. If the work genuinely requires a
  file outside them, **stop**: either narrow the change, or update the phase's declarations on `dev`
  and re-run the validator so peers see the wider lock before continuing.
- The only line of `backlog.yaml` you may touch is your own phase's, plus the catalog `updated` date.
- Commit narrow, atomic diffs — one concern per commit, on your branch only.
- **Rebase onto `dev`, never merge it in**: `git rebase dev`, whenever a peer integrates, not only at
  the end.
- Pushing `agent/<phase-id>` to `origin` needs no approval; backing up your own work is not
  publishing. Run `tools/check_no_private_content.py` **with your changes staged** — it reads
  `git ls-files`, so an unstaged run passes by not looking.
- Checkpoint with the `checkpoint` skill as often as useful. It never marks a phase complete.

## 8. Hand off — finish, then ask before integrating

Perform these in order, in the worktree. Do not skip ahead to the merge.

1. Run every command in the phase's `verification` list and keep the **real output**. A failing check
   is a result to record, not a step to retry until quiet.
2. Write the session record (`kind: session`), with its code from
   `uv run python -m src.governance --next-code session`.
3. **Release every `_tmpagent/` claim this session opened** — one `released` line per open
   `(file, kind, ref)` triple. A claim nobody closed blocks the file's deletion indefinitely.
4. `git rebase dev`, then re-run `uv run python -m src.governance` and `uv run pytest`. **This run —
   after the rebase, against peers' merged work — is the one that decides whether the branch may
   integrate.** If it fails, fix it on the branch; never integrate a red rebase.
5. Confirm the primary checkout is clean: `git -C /code/d-system status --short` shows nothing.
   **Never `git stash` a peer's uncommitted work and never force an integration around it.**
6. **Ask the owner before merging into `dev`.** The merge onto the trunk is the owner's call —
   `AGENTS.md`'s confidentiality section is explicit that this is the gate, and the push that backs
   up your branch is not. If the owner declines or is not present, leave the branch unmerged and
   report that it is ready for review, naming the command that shows it:
   `git diff dev..agent/<phase-id>`.

Marking the phase `status: complete` is **not** part of this. That happens only through the
owner-invoked `/session-close`, and only after its independent sub-agent review.

## 9. Integrate and clean up — only on the owner's yes

```bash
git -C /code/d-system merge --ff-only agent/<phase-id>    # fast-forward after the rebase
git worktree remove ../d-system-worktrees/<phase-id>
git branch -d agent/<phase-id>
```

Copy any gitignored content out of the worktree **before** removing it. A merge never carries it, and
the removal destroys it.

If the merge is not a fast-forward, the rebase in step 8 was not done or `dev` moved since. Rebase
again and re-run the validator; do not resolve it with a merge commit that skips the green run.

### If the merge conflicts

- **`backlog.yaml` conflicts are normal** — two agents edited different items in one file. Keep
  **both** sides: the peer's items verbatim, your own item's edits, `updated` set to today. **Never**
  resolve this file with `--ours` or `--theirs`; either silently deletes a peer's work.
- **A duplicate document code** means a peer took the same number. Codes are free before merge and
  permanent after, so whoever integrates second renumbers: allocate again, rename the file, update
  every reference.
- **A conflict in `src/`, `ts/`, `schemas/` or `sql/` means the safety rule was bypassed.** Stop, do
  not force the merge, and report it — the phases' declared `systems` or `deliverables` were wrong
  and need fixing before either phase completes.
- When resolving a collision requires an actual choice, record the decision and its reason in
  `docs/08-governance/GOV-003-backlog-decisions.md` in the same diff.

## What this command never does

- It never marks a phase `complete` — `/session-close` does, and only the owner invokes it.
- It never merges into `dev` without the owner saying so in this session.
- It never switches the primary checkout's branch away from `dev`.
- It never edits `AGENTS.md` or `CLAUDE.md`. If either looks wrong, quote the passage, propose exact
  wording, and stop.
