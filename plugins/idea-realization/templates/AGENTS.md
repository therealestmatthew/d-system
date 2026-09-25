# AGENTS.md

The working agreement for every agent in this repository, human-directed or autonomous.
Framework-specific orientation files, such as `CLAUDE.md`, say what the project is and where things
live; this file governs how you work. Where the two disagree, this file wins.

<!-- Rendered from the idea-realization plugin's template. It carries only rules that hold in any
repository. Add this repository's own sections by hand below the last one: its stack, how to run
its tests and checks, its conventions, and anything it adds to these rules. -->

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
  permanent, propose it and let the owner decide.
- If a tool can settle a fact, use it before saying you do not know.
- When the owner corrects you and is right, say so in one sentence and move on.

## Before you start

1. **Open the session properly.** Any session that will write code or create a document claims its
   phase, cuts a branch and works in its own worktree; see the three *Concurrent agents* sections.
2. **Pick up work from the backlog.** Take the first ready phase in the order the backlog's `ready`
   command renders; the queue at its front overrides priority. Use the phase's scope, acceptance
   and verification as the boundary of the work.
3. **Plan before implementing.** For any non-trivial change, write a requirement document
   (observable statements with verification methods) and a plan document, then add backlog phases,
   before writing implementation code. Approval of one plan is not permission to skip the
   documents for the next piece of work.
4. **Allocate a code for every governed document** with the `next-code` command. Never pick a
   number by reading a directory, and never edit the code register by hand.
5. **Run the plugin's `check` before you finish.** It must exit 0.

## Confidentiality and publishing

- `{{confidential_dir}}` holds confidential material and is never tracked. Never read or write
  there unless the owner directs you to.
- **Never write a confidential identifier into a tracked file**: not in code, a document, a commit
  message, or a session record describing the identifiers.
- **Pushing your own branch needs no approval.** Backing up your own work is not publishing.
- **Ask before integrating a branch into `{{integration_branch}}`.** The merge that lands work on
  the trunk is the owner's call; a green branch is ready to integrate, not cleared to.
- `{{data_root}}` holds this repository's data. A file generated from it, or from any other
  source, is never edited by hand: change the source and regenerate. A generated file is committed
  only when a check regenerates it and fails on any difference.

## Working rules

- Prefer narrow diffs: one concern per commit.
- Report outcomes honestly. A failing check is a result to record, not a step to retry until
  quiet; paste the failure, not a summary of it.
- Plans describe proposed work; verify an implementation in code before claiming a capability
  exists.

## Concurrent agents: claim a phase

`{{integration_branch}}` is the integration branch: the trunk every agent claims on and integrates
back into. Agent work happens on `agent/<phase-id>` branches that are integrated and deleted. The
backlog on `{{integration_branch}}` is the lock table, and the plugin's `check` is the lock check.

- Pick your own agent id once and reuse it, lowercase `agent-<name>`. One agent holds at most one
  active phase.
- Start on an up-to-date `{{integration_branch}}`. Choose a ready phase whose conflicts column is
  empty; a non-empty one means a peer already holds one of its systems or paths. Pick something
  else, and never edit a peer's claim.
- Claim it on `{{integration_branch}}` in one small commit that changes nothing else: the phase's
  status and agent lines, and whatever generated files the claim moves. Run `check` first; it
  refuses a claim that overlaps a peer's systems, paths or dependency chain.
- If the push is rejected, pull with rebase, run `check` again, and confirm the claim is still
  safe: a peer claimed between your check and your push.
- Owner-directed work with no backlog phase has nothing to claim. Name the branch and worktree
  after the work, and say plainly that the session runs unclaimed. Never manufacture a phase to
  have something to claim.

## Concurrent agents: work in a worktree

**Every session works in its own worktree, and the primary checkout's branch is never switched.**
The only work done in the primary checkout is the claim commit and the regeneration it forces.

- The branch is `agent/<phase-id>`; the worktree is `{{worktree_dir}}/<phase-id>`, outside the
  repository, so no scanner or test run walks a second copy of the tree.
- Gitignored content, including every virtual environment and generated database, is per
  worktree. Install it there; never symlink a peer's. A merge never carries gitignored content,
  and removing a worktree destroys it: copy out anything that must survive first.
- Stay inside your phase's declared systems and deliverables. If the work needs a file outside
  them, stop: narrow the change, or widen the phase's declarations on `{{integration_branch}}`
  first so peers see the wider lock.
- Rebase onto `{{integration_branch}}`; never merge it in. Rebase whenever a peer integrates.

## Concurrent agents: complete and hand off

1. Run every verification command of the phase in your worktree and keep the real output.
2. Write a session record, a governed document with its own code, covering outcomes, evidence
   and anything unresolved.
3. Confirm each acceptance condition genuinely holds, and have an independent reviewer check the
   diff against them. A condition that does not hold leaves the phase open with an exact next
   action.
4. Rebase onto `{{integration_branch}}` and run the checks and tests again. This run, against your
   peers' merged work, decides whether the branch may integrate. Never integrate a red rebase.
5. Confirm the primary checkout is clean. Never stash or discard a peer's uncommitted work.
6. **Ask the owner before integrating.** On their yes, fast-forward `{{integration_branch}}` to
   your branch, record the phase complete with its evidence, then remove the worktree and the
   branch.

## Concurrent agents: resolve collisions

- **Backlog conflicts are normal.** Keep both sides: the peer's entries verbatim, and your own
  entry's edits. Never resolve that file with a whole-side choice; it deletes a peer's work.
- **A duplicate document code** means a peer took the same number. Codes are free before merge and
  permanent after, so whoever integrates second allocates again and renames.
- **A conflict in source code means the declarations were wrong.** Disjoint phases do not conflict
  in source. Stop, do not force the merge, and report it.
- **A branch that goes red after a rebase** means a peer changed behavior you relied on. Fix your
  branch; never revert the peer's work.
