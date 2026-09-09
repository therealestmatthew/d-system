---
description: Finalize this session's record and, only if acceptance genuinely holds after an independent sub-agent review, mark the phase complete
argument-hint: "[phase-id]"
---

# Close the session

Finishes the session record `checkpoint` (`.claude/skills/checkpoint/SKILL.md`) created or updated,
adds the depth a checkpoint deliberately skips, and is the **only** place a phase reaches
`status: complete`.

## This command is owner-only, on purpose

**An agent must never invoke this on its own judgement that a session is finished.** That decision
belongs to the owner. If you are an agent and you believe a session is done, say so and run
`checkpoint` to record where things stand — do not reach for this command yourself, and do not
reproduce its completion step inside `checkpoint` or anywhere else. The whole reason `session-close`
is a command rather than a skill is that a command is something the owner types; nothing here should
be restructured to make it agent-reachable.

## 1. Identify the phase and run the checkpoint procedure first

If `$ARGUMENTS` names a phase, use it; otherwise use the session's active phase — ask if more than
one is plausible.

Run every step of `.claude/skills/checkpoint/SKILL.md` now, in full, against the current state.
Follow that document directly rather than repeating its steps here — this command extends the same
session record, and `## Phase` through `## Unresolved` must reflect the repository **as it stands at
close**, not as it stood at the last mid-session checkpoint. Do not proceed past this step until the
checkpoint procedure's own acceptance verdicts (step 4 there) are freshly recomputed.

This step already guarantees the session record is the one `checkpoint` created — its own step 2
finds and edits the existing file rather than creating another. If it created the record for the
first time just now (no prior checkpoint ran this session), that is fine and is still the one and
only record; nothing here creates a second.

## 2. Identify the actual diff to review

Work out the exact commit range this session produced, and state it explicitly for the reviewer in
step 3 — do not make it guess:

- **Work done on `agent/<phase-id>`:** the range is `dev...HEAD` (or `dev...agent/<phase-id>` if not
  yet merged).
- **Work done directly on `dev`** (the GOV-003 primary-checkout exception): find the commit that set
  this phase's `status: active` — `git log --oneline -- docs/09-backlog/backlog.yaml` will show it —
  and use `<that commit>..HEAD`.

## 3. Launch an independent sub-agent review

Use the **Agent tool with a fresh, non-fork subagent** (never `subagent_type: fork` — a fork inherits
this session's own context and conclusions, which defeats the entire point of a second opinion). Give
it, in the prompt itself since it starts with nothing:

- The phase id, its `scope`, `acceptance` and `verification` lists from `docs/09-backlog/backlog.yaml`
  (paste them; do not just name the file).
- The exact commit range from step 2, and instructions to run `git diff <range>` and `git log
  <range>` itself.
- The session record's current path and content.
- Its job, stated plainly: independently decide, from the diff and its own run of the verification
  commands, whether each acceptance condition actually holds — not whether the session record *says*
  it holds. Flag anything the record claims that the diff or a rerun does not support. Report clean
  findings explicitly when that is the honest result; "no discrepancies found" is a valid finding, not
  a failure to find one.

Wait for its report. Do not paraphrase away an uncomfortable finding, and do not proceed to step 6 by
assuming the review passed before it actually returns.

## 4. Record the review verbatim

Add a `## Review` section to the session record, after the sections `checkpoint` maintains. Paste the
sub-agent's findings — condition by condition — rather than your own summary of them. If it found
nothing wrong, the section says exactly that.

## 5. Record the depth a checkpoint skips

Add the sections a checkpoint has no reason to write, covering the session as a whole rather than the
moment of one run:

- `## Decisions` — what was decided during the session and why, including anything the owner directed
  that overrode your own recommendation.
- `## Corrections` — mistakes made and fixed mid-session; omit only if there genuinely were none.
- `## Left undone` — what remains, and why it was left rather than finished, for whoever picks this up
  next.

Write these as narrative, the way an owner would want to read them in six months — not as a
restatement of the backlog's `scope` bullets.

## 6. Decide completion — the only step that may write `status: complete`

Mark the phase complete **only if both hold**:

- The checkpoint procedure's own step 4 (redone in step 1 above) found every `acceptance` condition
  `Met`.
- The sub-agent review in step 3 corroborates that and raised no unresolved discrepancy.

If both hold: set `status: complete`, `session:`, `completion_evidence:` (real files), and `result:`
(the actual verification and review outcome) on the phase in `backlog.yaml`. Remove it from
`next_up` if present.

**If either does not hold, the phase stays `queued` or `active`.** This is not a failure state to
paper over — write an exact `next_action` that names precisely what remains, including anything the
sub-agent review surfaced, and say so plainly in your final report. A session that closes honestly
incomplete is the correct outcome the acceptance conditions were written to allow.

## 7. Regenerate the catalog and confirm governance is green

```bash
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
uv run python -m src.governance
uv run pytest
```

If any of these fail, fix the cause before finishing — do not close a session on top of a red tree.

## 8. Commit — primary-checkout sessions only

**Skip this step entirely if the session worked in a worktree.** That case has its own commit and
integration procedure — `AGENTS.md`'s "Concurrent agents: complete and hand off" — and this step
would duplicate or conflict with it.

If the session worked directly on `dev` (the GOV-003 primary-checkout exception), `git status` at
this point still shows every change uncommitted — claiming the phase, doing the work, and closing
it are not committed as they happen, only recorded in files. Leaving that for "later" is how two
sessions in a row reached this point with a growing pile of uncommitted work and no natural place to
notice it. Commit it now, as the last mechanical step before reporting:

```bash
git add -A
git status --short   # confirm what is about to be committed matches what this session actually did
git commit -m "<message>"
```

Write the message the way this repository's history already does: name the phase(s) closed and the
one or two sentences of *why*, not a restatement of the diff. If the session closed more than one
phase and their diffs do not cleanly separate (shared files touched by both), one commit covering
all of them is fine — `PLAN-006` already establishes that this repository's reasoning lives in ADRs
and session records, not commit messages, precisely so commit granularity here is not load-bearing.
Never use `--no-verify`; if a pre-commit hook rejects the commit, that is a real finding to fix, not
a check to bypass.

This step commits. It does not push, and it does not add a remote — those remain gated exactly as
`AGENTS.md`'s confidentiality section states, regardless of how this step goes.

## 9. Report

State plainly: whether the phase reached `status: complete` or was left open and why, the sub-agent
review's actual verdict (not a rosier restatement of it), the session record's code, and whether step
8 committed (and its commit hash) or was skipped because the session worked in a worktree. This is
the one report in the session lifecycle that should read as a finished account, not a status ping.
