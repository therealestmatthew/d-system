# AGENTS.md

The working agreement for every agent in this repository, human-directed or autonomous.
`CLAUDE.md` says what the repository is and where things live; this file governs how you work.
Where the two disagree, this file wins.

Configured values are written in angle brackets: `<integration branch>` (`main` by default),
`<worktree dir>`, `<product root>` and `<product worktree dir>`.
`uv run plugins/idea-realization/scripts/paths.py` prints each one as this machine resolves it.

## Never edit this file or CLAUDE.md without explicit approval

**No agent modifies `AGENTS.md` or `CLAUDE.md` for any reason without the owner's explicit approval
for that specific change.** There is no exception: not to fix something you are certain is wrong,
not to record something you learned this session, not because a phase's scope appears to cover it,
and not as tidy-up alongside a change you were asked to make.

These two files are the instructions every agent reads before doing anything. An agent that edits
them rewrites its own governing rules and every later agent's, and the edit outlives the session
that made it, usually unreviewed because it arrives inside a diff about something else.

**If you believe either file is wrong, out of date or missing something: say so and stop.** Quote
the passage, propose exact replacement wording, and let the owner decide.

## Do not assume, and do not invent rules

- When something is unclear, unstated or open to more than one reading, ask. Ask at the point the
  work reaches the uncertainty, not at the end. A question that can wait is stated as an
  assumption, and the work continues; an assumption that changes what gets built is a question.
- Do not turn a one-time instruction into a standing rule. If a pattern seems worth making
  permanent, propose it and let the owner decide. Standing rules are recorded only in
  `docs/governance/GOV-001-standing-rules.md`, and only after the owner signs each one off.
- If a tool can settle a fact, use it before saying you do not know.
- When the owner corrects you and is right, say so in one sentence and move on.

## Two repositories

This is the **control repository**: ideas, requirements, plans, decisions, the backlog, session
records, review records, agents and governance. The product is built in the **product
repository**, whose identity is in `.idea-realization/product.yaml` and whose local path is
configured per machine.

- Sessions start here, with the product worktree reachable through `--add-dir`, so this
  repository's agents, skills and rules apply while the code is written.
- A phase is claimed here; its code is built on a branch and worktree in the product repository;
  its session record and review records are written on a paired branch here.
- Verification commands run in the product worktree unless prefixed `control:`.
- A path in a phase's `deliverables` or `completion_evidence` that lives in the product repository
  carries the `product:` prefix.

The full protocol is `plugins/idea-realization/docs/two-repositories.md`.

## Workstreams

Several developers share this repository, each on their own machine. Each developer owns one
workstream: a set of paths declared in `docs/workstreams.yaml`. A phase you claim must keep its
deliverables inside your own workstream or in shared ground. Your agent id on a claim is
`<handle>/<agent>`, where the handle is your key in `docs/systems.yaml`'s `owners`. The protocol is
`plugins/idea-realization/docs/workstreams.md`.

## The brain

The team's shared memory is `brain/`: decisions, research, concepts, entities and learnings, one
markdown entry per file, each naming its author. `brain/README.md` says what goes where.

- At the start of a session, load what bears on the work with the `brain` skill
  (`brain.py load --query <subject>`, `brain.py load --kind decision`), and read it before planning.
- Before a session closes, record what it decided, found out or learned that the next session
  should know, with the `brain` skill (`brain.py new <kind>`), and commit the entry together with
  `brain/index.md`.
- An anti-pattern procedure enters only after the owner approves it; propose one as a `lesson`
  instead.

## Before you start

1. **Open the session properly.** Any session that will write code or a document runs the
   `session-start` skill first: claim the phase on `<integration branch>`, cut its branches, and
   work in worktrees. The concurrency sections below are the rule; the skill is the same rule as an
   ordered procedure.
2. **Pick up work from the backlog.** The `backlog` skill shows the ready phases. Take the first
   ready phase in the rendered order: `next_up` in `backlog/backlog.yaml` is the front of the queue
   and overrides priority. Use the phase's `scope`, `acceptance` and `verification` as the work
   boundary.
3. **Plan before implementing.** For any non-trivial change, write a requirement document
   (observable statements with verification methods) and a plan document, then add backlog phases,
   before writing implementation code. Approval of one plan is not permission to skip the documents
   for the next piece of work.
4. **Allocate a code for every governed document** with the `next-code` skill. Never pick a number
   by reading a directory: it cannot show reserved or retired codes.
5. **Run the repository check before you finish**:
   `uv run plugins/idea-realization/scripts/check.py`. It must exit 0.

## Confidentiality and publishing

- **Pushing your own branch needs no approval.** Backing up your own work is not publishing.
- **Ask before integrating a control-repository branch into `<integration branch>`.** The merge
  that lands work on the trunk is the owner's call; a green branch is ready to integrate, not
  cleared to. A product-repository merge needs a passing gating review instead (see *Complete and
  hand off*).
- **Never write a confidential identifier into a tracked file**: not in code, a document, a commit
  message, or a session record describing the identifiers. `tools/check_confidential.py`
  checks every tracked file against the deny-list in `.private/deny-list.txt`. It reads
  `git ls-files`, so run it **with your changes staged**, or it passes by not looking. The
  pre-commit hook runs it for you once `git config core.hooksPath tools/git-hooks` is set.
- `.private/` is gitignored and holds per-machine confidential files, including the deny-list.
  Never read or write there unless the owner directs you to.
- Never commit with `--no-verify`. A failing hook is a finding to fix or report.

## AWS

- **The IAM roles and the machine rule are the boundary.** The sandbox has a read-only role and a
  deploy role with no IAM, Organizations, account or billing permissions (`aws/README.md`). Each
  machine has one named profile for each, in untracked configuration.
- **Machine rule: a machine that runs agents holds no default or ambient AWS credentials** — no
  `default` profile, no `AWS_` credential or profile variables, no instance or container role —
  only the two named sandbox profiles. Then a command that gets past the hook finds no credentials
  but the sandbox roles. `uv run python tools/check_aws_machine.py --probe` checks it, and
  `tools/aws-sandbox` warns on every call when it finds a default profile or `AWS_` variables.
- Every AWS command goes through `tools/aws-sandbox`, which runs `read` and `whoami` with the read
  profile and `write` and `exec` with the deploy profile, and refuses a missing or `default`
  profile or one profile used for both. Never run the AWS CLI, an AWS SDK or a deployment tool any
  other way, never pass `--profile` or `--region` yourself, never set an `AWS_` variable, and never
  read or change anything under `~/.aws/`.
- Reads (`tools/aws-sandbox read ...`) run freely, except the reads that reveal a secret.
- Only the `aws-deploy` agent runs `write` or `exec`.
- Deleting anything needs a person's approval each time; `.claude/settings.json` prompts for it.
  Say what will be deleted before the prompt appears. A refused prompt means stop.
- A PreToolUse hook (`tools/hooks/aws_guard.py`) refuses AWS commands outside the wrapper, and
  `write`/`exec` from anyone but `aws-deploy`; the permission rules repeat the main refusals. Both
  match command text: they are guardrails, not the boundary. Never route around one, and report a
  rule that blocks legitimate work.

## Running the checks

```bash
uv sync --extra dev
uv run pytest                                          # tools/ tests and the plugin's tests
uv run plugins/idea-realization/scripts/check.py       # ideas, backlog, documents, catalog
uv run plugins/idea-realization/scripts/doctor.py      # scaffolded files unchanged
uv run python tools/check_confidential.py              # with your changes staged
uv run ruff check tools/ test/
```

The product repository's own test, lint and build commands are its phases' `verification`
entries.

## Stack

<!-- The product's stack, once chosen: languages, frameworks, AWS services, and how to run the
product locally. -->

To be decided by the team.

## Plans: governed and ephemeral

- A **governed** plan is a document under `docs/plans/` with a code and front matter, approved by
  the owner, and decomposed into backlog phases. It is the only kind of plan work is claimed from.
- An **ephemeral** working plan — a scratch list for one session — lives under `_working/`, which is
  gitignored and ungoverned. Nothing claims work from it, and nothing there is deleted without the
  owner's approval.

## Documentation governance

- Follow `plugins/idea-realization/docs/protocol.md` for document front matter and lifecycle, and
  `plugins/idea-realization/docs/document-codes.md` for codes.
- Name each document `<code>-<slug>.md`, in a folder its series allows (`docs/codes.yaml`).
- Regenerate `docs/catalog.md` after changing any document (`catalog` skill); the check fails while
  it is stale.
- Update `docs/systems.yaml` when a component's responsibilities change.
- Plans describe proposed work; verify the code before claiming a capability exists.

## Session backlog

- Capture every approved plan's phases in `backlog/backlog.yaml` before implementing its work.
- Each phase is one session: one concrete outcome, with acceptance checks and its declared
  `systems` and `deliverables`.
- Up to `max_active` phases run at once.
- Remove a phase from `next_up` in the same change that completes it.
- Keep deferred work visible with a resume condition; split a phase that exceeds one session.
- Checkpoint progress with the `checkpoint` skill as often as useful. It never marks a phase
  complete; only `session-close` does, after its gating review.

## Concurrent agents: claim a phase

`<integration branch>` of this repository is the trunk every agent claims on and integrates back
into. `backlog/backlog.yaml` on it is the lock table, and the repository check is the lock check.

- Your agent id is `<handle>/<agent>`. One agent holds at most one active phase.
- Start on an up-to-date `<integration branch>` in the primary checkout.
- Choose a ready phase whose conflicts column is empty. A conflict means a peer already locked one
  of your systems or paths: pick something else; do not wait, and do not edit a peer's claim.
- Claim it in one small commit that changes nothing else: `status: active`, your `agent` id, and
  the regenerated catalog. Run the repository check before committing; it rejects a claim that
  overlaps a peer's systems, deliverables or dependency chain, a claim outside your workstream, or
  one past `max_active`.
- If the push is rejected as non-fast-forward, pull with rebase, re-run the check, and confirm the
  claim is still safe: a peer claimed between your check and your push.

**Owner-directed work with no backlog phase** has nothing to claim. Name the branch and worktree
after the work (`agent/<slug>`), and say in your first report that the session is running
unclaimed, so peers hold no lock against it. Do not invent a phase to have something to claim.

## Concurrent agents: work in a worktree

**Every session works in a worktree, and the primary checkout's branch is never switched.** This
holds whatever the work touches; a documentation-only change is not an exception.

The only work done in the primary checkout is what the lock requires there: the claim commit and
the catalog regeneration it forces, and later the completion edit. Everything else happens in
worktrees and reaches the trunk by integration.

- In the control repository, the branch is `agent/<phase-id>` and the worktree is
  `<worktree dir>/<phase-id>`, outside the repository.
- In the product repository, the branch is `agent/<phase-id>` and the worktree is
  `<product worktree dir>/<phase-id>`.
- Each worktree installs its own environment (`uv sync --extra dev`, `npm install`); never symlink a
  peer's.
- **Ignored content never travels.** A merge does not carry it and removing a worktree destroys it;
  copy out anything that must survive first.
- Pick a free port explicitly for any dev server; do not assume a default port is yours.
- Stay inside your phase's declared `systems` and `deliverables`. If the work needs a file outside
  them, stop: narrow the change, or widen the declaration on the trunk and re-run the check so
  peers see the wider lock first.
- Commit narrow diffs, one concern per commit, on your branch only.
- Rebase onto the integration branch rather than merging it in, whenever a peer integrates.

## Concurrent agents: complete and hand off

Perform these in order.

1. Run every command in the phase's `verification` list in the worktree it belongs to and keep the
   real output. A failing check is a result, not a reason to skip the step.
2. Write the session record (`kind: session`) with its code from `next-code`, on the control
   branch.
3. Confirm each `acceptance` condition. If one does not hold, leave the phase active or return it to
   `queued` with an exact `next_action`, releasing your claim.
4. Rebase both branches onto their integration branches and re-run the repository check and the
   product's tests. This run decides whether the branch may integrate; never integrate a red
   rebase.
5. Run `session-close`: it dispatches the gating reviewer (`phase-adversary`), with `review-judge`
   in shadow, and records the verdicts under `docs/reviews/`. Fix or explicitly accept every
   finding, and re-review after a fix.
6. Confirm both primary checkouts are clean. **Never stash or overwrite a peer's uncommitted work.**
7. **Product repository:** on a passing gating verdict, fast-forward the product branch onto the
   product integration branch.
8. **Control repository:** ask the owner before integrating the control branch; on their yes,
   fast-forward it, then make the completion edit (status, `session`, `completion_evidence`,
   `result` naming the product merge commit) with the catalog regenerated in the same commit.
9. Remove your worktrees and branches once their content has merged.

If a merge is not a fast-forward, the rebase was not done or the trunk moved. Rebase again and
re-run the checks; never paper over it with a merge commit.

## Concurrent agents: resolve collisions

- **`backlog.yaml` conflicts are normal**: two agents edited different phases in one file. Keep
  both sides: the peer's phases verbatim and your own phase's edits. Never resolve this file with
  `--ours` or `--theirs`; either one silently deletes a peer's work.
- **A duplicate document code** means a peer on another machine took the same number. Codes are
  free before merge and permanent after, so whoever integrates second renumbers: allocate again,
  rename the file and update every reference.
- **A source conflict between two phases** means their declared `systems` or `deliverables` were
  wrong. Stop, do not force the merge, and report it; the declarations are fixed before either
  phase completes.
- **A branch that goes red after a rebase** means a peer changed something you depended on. Fix your
  branch against the current trunk; do not revert the peer's commit.
- Build against merged work only, never against a peer's unmerged branch.

## Working rules

- Prefer narrow diffs: one concern per commit.
- Report outcomes honestly, per `plugins/idea-realization/docs/reporting.md`.
- New asks that arise mid-session are recorded as ideas at once (`idea` skill), not folded into the
  current work.
