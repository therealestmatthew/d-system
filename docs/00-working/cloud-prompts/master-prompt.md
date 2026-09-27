# Master prompt: run the next cloud prompt

The owner pastes the kickoff at the end of this file into each fresh claude.ai/code cloud session,
unchanged. Each session runs exactly one prompt: the first row of [`status.md`](status.md) that is
not `merged`.

## Steps

1. **Get the latest `dev`.**

   ```bash
   git fetch origin
   git show origin/dev:docs/00-working/cloud-prompts/status.md
   ```

   Read the tracker from `origin/dev`, not from whatever branch the clone opened on.

2. **Work out what has merged.** A row counts as merged when its handoff file is on `origin/dev`,
   whatever its `Status` text says. The handoff file is
   `docs/00-working/cloud-prompts/handoff-<slug>.md`, where `<slug>` is the branch name without
   `agent/cloud-`:

   ```bash
   git cat-file -e origin/dev:docs/00-working/cloud-prompts/handoff-<slug>.md && echo merged
   ```

   Do not test the branch ref. The Session Manager may rebase a branch before merging it, or
   delete it afterwards, and either would make a ref check report "not merged" for merged work.
   You record the result in step 4, on your own branch.

3. **Pick the row.** Take the first row, in `Order`, that step 2 did not find merged.
   - If it is `not started`: it is yours. Continue.
   - If it is `ready`: the previous session has not been merged yet. **Stop.** Tell the owner
     which branch is waiting and that it must be merged into `dev`, and `dev` pushed to `origin`,
     before the next session starts. Change nothing.
   - If it is `in progress`: another session is running it, or died before finishing. **Stop**
     and ask the owner (AskUserQuestion) which. If the owner says it died, tell them to mark it
     `stopped` on its branch, or to re-run it from its prompt's direct-run kickoff. Change
     nothing yourself.
   - If it is `stopped`: stop and ask the owner (AskUserQuestion) whether to re-run it or skip it.
   - If every row is `merged`: tell the owner all prompts are done, and stop.

4. **Start the prompt.** Run the prompt file's *Setup* block now (it creates the row's branch from
   `origin/dev`). Then edit `docs/00-working/cloud-prompts/status.md` on that branch: mark every
   row that step 2 found merged as `merged` (fill its `Tip` from
   `git log -1 --format=%h origin/dev -- <its handoff file>`), set your row to `in progress`,
   commit (`Cloud prompts: start <prompt name>`), and push the branch.

5. **Run the prompt.** Read the row's prompt file from `docs/00-working/cloud-prompts/` and follow
   it exactly. Its rules govern the session. Skip its *Setup* block: step 4 ran it. Never
   recreate, reset or force-push your branch; the tracker commit from step 4 is on it.

6. **Finish.** Run the prompt's gates first, since the handoff file quotes their output. Then
   write the handoff file, set your row to `ready`, fill in `Handoff` with the handoff file's path
   and `Notes` with one line, commit both together, and push. Both files are ungoverned, so that
   commit does not change what the gates measured, and the pre-commit hook re-runs the
   governance check on it. Leave `Tip` blank: the handoff file records the tip, and the next
   session fills `Tip` when it marks the row `merged`. If you must end without a handoff file, set the row to
   `stopped`, say why in `Notes`, and push.

The local Session Manager re-runs the gates and relays the merge to the owner. After the merge,
`dev` must be pushed to `origin` before the next session starts, or step 3 will stop the next
session. The last row's `Status` text stays `ready` on `dev` until a later session marks it
`merged`; step 2 reads the handoff file, so the stale text blocks nothing.

## Kickoff (the owner pastes this into each fresh cloud session)

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run
`git fetch origin`, then read `docs/00-working/cloud-prompts/master-prompt.md` from `origin/dev`
(`git show origin/dev:docs/00-working/cloud-prompts/master-prompt.md`) and follow it exactly. It
picks the next prompt from the status tracker, runs it on its own `agent/cloud-<slug>` branch, and
keeps the tracker current. Run exactly one prompt in this session. Tests run only in this clone on
that branch, never on `dev`. Never commit to, merge into or push `dev`. Ask me questions with
AskUserQuestion, batched, with drafts in the message text and never in previews. Finish by pushing
your branch with the handoff file the prompt describes.
