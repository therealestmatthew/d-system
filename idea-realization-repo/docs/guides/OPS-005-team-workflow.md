---
schema_version: 1
id: doc-team-workflow
code: OPS-005
title: Team workflow
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: []
depends_on: []
---

# Team workflow

How a team of developers works in this repository, each on their own machine and each running
their own agents. It adds no mechanism: it says how the existing pieces fit together for a team.
The rules behind it are in the plugin's protocol documents, which this guide points to rather than
repeats:

- `plugins/idea-realization/docs/workstreams.md`: workstreams and developer handles;
- `plugins/idea-realization/docs/backlog-protocol.md`: claims, concurrency, completion, collisions;
- `plugins/idea-realization/docs/two-repositories.md`: the control and product repositories;
- the branching and CI guide (`OPS-001`): branch names, pull requests, merge commits, rulesets,
  CI checks, tags. The git mechanics of every step below are there.

Both repositories have two long-lived branches: `dev`, where finished work integrates, and `main`,
which receives `dev` once per demo release. "Control `dev`" and "product `dev`" below name the
`dev` branch of each repository.

## 1. Before the first day's work

Each developer, once:

1. **Add a developer entry** to the `owners` map in `docs/systems.yaml`: the key is your handle
   (lower-case letters and digits, starting with a letter, at most sixteen characters), the value
   lists your git author emails. `uv run plugins/idea-realization/scripts/identity.py` prints the
   handle your git email resolves to.

   ```yaml
   owners:
     ana:
       description: Ana, user interface workstream.
       emails: ["<handle>@<work-domain>"]
   ```

2. **Claim one workstream.** The owner writes the list of workstreams in `docs/workstreams.yaml`;
   developers claim them. A workstream is a set of paths one developer owns, such as `product:web/`.
   Other developers' phases keep their deliverables out of it unless the phase records your
   approval (`cross_workstream`).

   ```bash
   uv run plugins/idea-realization/scripts/workstreams.py show
   uv run plugins/idea-realization/scripts/workstreams.py claim <id>
   ```

   `claim` edits the file and never commits. Commit only `docs/workstreams.yaml` on control `dev`
   in the primary checkout and push at once. If the push is rejected, someone pushed first:
   `git pull --rebase`, run `workstreams.py check`, and push again if the workstream is still
   yours; if a peer took it, choose another.

The developer entry and the workstream claim are bookkeeping, so they go directly to control
`dev`, not through a pull request.

## 2. Interfaces first (the first two days)

During the first two days each workstream writes the documents that state what it provides to the
others: an architecture document (`ARCH`) or a decision (`ADR`) per interface, such as the API's
request and response shapes, the event formats between the agent orchestration and the backend, or
the data the infrastructure exposes. List them under the workstream's `interfaces` in
`docs/workstreams.yaml`.

From then on:

- **Build against merged contracts and mocks, never against a peer's branch.** If the API is not
  built yet, the user interface builds against a mock that follows the merged interface document.
- A peer's unmerged branch can be rebased, rewritten or abandoned; work built on it breaks when it
  does. Only what is on `dev` is a contract (`backlog-protocol.md`, section 7).
- Changing an interface is a change to its document, merged first, so every consumer sees it before
  the code that depends on it.

## 3. Claims

A phase is claimed on control `dev`, which holds the backlog (`backlog/backlog.yaml`), the lock
table every developer reads. The `session-start` skill carries these steps; this is what it does
and why.

1. **Pull first.** In the primary checkout, `git pull` origin `dev` before any work. A claim made
   against a stale backlog is checked against stale claims.
2. **One phase per agent.** An agent id is `<handle>/<agent>`. Each agent holds at most one active
   phase. One developer may run several agents, each with its own phase.
3. **The active-claim limit is `max_active: 15`** across the whole team. The check refuses a claim
   past it; a refusal means choosing other work, never waiting.
4. **The check decides whether a claim is safe.** It refuses a phase whose systems, deliverables
   or dependency chain overlap an active phase, or whose deliverables fall inside a workstream
   another developer owns.
5. **Claim directly on control `dev` and push immediately.** The claim commit changes only the
   phase's `status: active` and `agent`, the backlog's `updated`, and the regenerated catalog.
6. **A rejected push means a peer claimed between your check and your push.** Run
   `git pull --rebase`, re-run the check, and confirm the claim is still safe before pushing again.
   If the check now refuses it, release it and choose another phase.

Then the work happens on `agent/<phase-id>` branches cut from `origin/dev` in both repositories,
each in its own worktree (`CLAUDE.md`, "work in a worktree").

### Assignment

The owner assigns a phase to a developer by setting `owner: <handle>` on that phase in the backlog.
Anyone may still claim it: the check **warns** when the claimant is not the phase's owner and
never refuses. Treat the warning as a question to ask the assigned developer before going further.

## 4. Review and merge

The `session-close` skill carries this sequence; `OPS-001` has the git and GitHub commands.

1. Run the phase's verification. Rebase both feature branches onto `origin/dev` and re-run the
   check and the product's tests.
2. The **gating review** (`phase-adversary`, with `review-judge` in shadow) judges the product diff
   against the phase's control documents. Every finding is fixed or explicitly accepted; a fix is
   re-reviewed.
3. **A passing gating review is the approval** to merge both the product branch and the control
   branch. There is no separate per-merge approval.
4. The session pushes both feature branches and opens a pull request to `dev` in each repository.
   It merges each with a **merge commit** (never squash or rebase merge), pinned to the commit that
   was reviewed so GitHub refuses the merge if the branch moved after the review. The product pull
   request waits for its required check `verify` first.
5. The **completion commit** goes directly to control `dev`: the phase's `status: complete`, the
   product merge commit, the regenerated catalog. `git pull --rebase`, then push.

If the completion push fails after the product merged, retry the pull, rebase and push. Never revert
the product merge. Until the completion commit lands, the phase stays `active`
(`two-repositories.md`, "A stranded phase").

## 5. Daily cadence

| When | What |
|---|---|
| Morning, 15 minutes | Sync: everyone pulls `dev` in both repositories. Render the backlog; the owner ranks `next_up` and assigns phases (`owner: <handle>`); each developer's agents claim. Name any interface that is about to change. |
| Midday | Integrate: rebase every open feature branch onto `origin/dev` in both repositories and re-run the check and tests, so conflicts surface while they are small. Merge whatever has passed its gating review. |
| End of day | Each phase is either closed through `session-close` or checkpointed with the `checkpoint` skill, so the next session can resume from the record. Record what the day decided or learned in the brain (`brain.py new <kind>`, committed with `brain/index.md`). Push every feature branch, so no work exists only on one machine. The owner reviews the day's ideas. |

Ideas raised during the day are recorded with the `idea` skill, not folded into the phase in
progress.

## 6. Conflicts

- **`backlog/backlog.yaml` conflicts are normal**: two developers edited different phases in one
  file. Keep both sides: the peer's phases verbatim and your own phase's edits, with `updated` set to
  today. Never resolve it with `--ours` or `--theirs`; either one deletes a peer's work.
- **A duplicate document code** means a developer on another machine took the same number before
  either merged. Whoever integrates second renumbers: allocate a new code, rename the file and
  update every reference (`backlog-protocol.md`, section 12).
- **A source conflict between two phases declared disjoint** means a declaration is wrong. Stop,
  do not force the merge, and fix the declarations before either phase completes; record the choice
  in the decision record.
- **Never revert a peer's commit.** A branch that goes red after a rebase means a peer changed
  something it depended on: fix your branch against the current `dev`.

## 7. Release

- A demo release goes from `dev` to `main` through a pull request merged with a merge commit, in
  each repository.
- Each release candidate gets an annotated tag on `main`: `demo-rc-<n>`. The one shown at the demo
  is also tagged `demo-final`.
- **Code freeze: 2026-11-03.** After the freeze only fixes for the demo are merged, each as a phase
  through the same claim and gating review.
- Release mechanics and tag protection are in `OPS-001`.
