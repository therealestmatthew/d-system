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

2. **Bring the tracker up to date with what has merged.** For every row marked `ready` or
   `in progress`, check whether its branch is on `origin/dev`:

   ```bash
   git merge-base --is-ancestor origin/<branch> origin/dev && echo merged
   ```

   A row whose branch is merged counts as `merged`. You record that in step 4, on your own branch.

3. **Pick the row.** Take the first row, in `Order`, that is not `merged`.
   - If it is `not started`: it is yours. Continue.
   - If it is `in progress` or `ready`: the previous session has not been merged yet. **Stop.** Tell
     the owner which branch is waiting and that it must be merged into `dev` and `dev` pushed to
     `origin` before the next session starts. Change nothing.
   - If it is `stopped`: stop and ask the owner (AskUserQuestion) whether to re-run it or skip it.
   - If every row is `merged`: tell the owner all prompts are done, and stop.

4. **Start the prompt.** Create the row's branch from `origin/dev` exactly as the prompt's setup
   section says. Then edit `docs/00-working/cloud-prompts/status.md` on that branch: mark every
   row whose branch step 2 found on `origin/dev` as `merged` (filling its `Tip`), set your row to `in progress`,
   commit (`Cloud prompts: start <prompt name>`), and push the branch.

5. **Run the prompt.** Read the row's prompt file from `docs/00-working/cloud-prompts/` and follow
   it exactly. Its rules govern the session.

6. **Finish.** Before the prompt's final gate run, set your row to `ready`, fill in `Handoff`
   with the handoff file's path and `Notes` with one line, and commit it with the handoff file.
   Then run the gates and push. Leave `Tip` blank: the handoff file records the tip, and the next
   session fills `Tip` from `git rev-parse --short origin/<branch>` when it marks the row
   `merged`. If you must end without a handoff file, set the row to
   `stopped`, say why in `Notes`, and push.

The local Session Manager re-runs the gates and relays the merge to the owner. After the merge,
`dev` must be pushed to `origin` before the next session starts, or step 3 will stop the next
session.

## Kickoff (the owner pastes this into each fresh cloud session)

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run
`git fetch origin`, then read `docs/00-working/cloud-prompts/master-prompt.md` from `origin/dev`
(`git show origin/dev:docs/00-working/cloud-prompts/master-prompt.md`) and follow it exactly. It
picks the next prompt from the status tracker, runs it on its own `agent/cloud-<slug>` branch, and
keeps the tracker current. Run exactly one prompt in this session. Tests run only in this clone on
that branch, never on `dev`. Never commit to, merge into or push `dev`. Ask me questions with
AskUserQuestion, batched, with drafts in the message text and never in previews. Finish by pushing
your branch with the handoff file the prompt describes.
