---
description: Preflight the repo, show the top priority phases, and orient on one without claiming it
argument-hint: "[phase-id] [--claim|--go]"
---

# Resume work from the backlog

Orient me on what to work on next. Named `/backlog` rather than `/resume` because Claude Code already
owns `/resume`.

## Modes

Parse `$ARGUMENTS` for a phase id and a mode flag. Either may appear alone, together, or not at all.

| Invocation | Behaviour |
|---|---|
| `/backlog` | Orient on the recommendation, **stop and ask**. The default. |
| `/backlog phase-idea-01` | Orient on that phase instead of the recommendation, stop and ask. |
| `/backlog --claim` | Orient, **claim** the phase, then stop and ask before working. |
| `/backlog --go` | Orient, claim, and **begin the first action** without pausing. |
| `/backlog phase-idea-01 --go` | Same, on a named phase. |

**The default is stop-and-ask, and an unrecognised argument falls back to it.** Never infer `--go`
from urgency in the prompt, from a phase looking obvious, or from the owner having run `--go` last
time. It is typed or it does not happen.

`--claim` writes `status: active` and the `agent` field. `--go` does that and then starts. Both are
mutations the concurrency protocol treats as a lock, which is why neither is the default.

**Every mode runs the preflight, and every mode stops dead if it fails** — `--go` most of all.
Starting work automatically on a repository that is already red is the worst available outcome,
because the resulting failures arrive tangled with someone else's.

## 1. Preflight — stop if the repository is not green

Run both, in this order, and report the real output:

```bash
uv run python -m src.governance
uv run pytest
```

**If either fails, stop here.** Report the failure and nothing else. Do not orient, do not summarise a
phase, do not offer to continue past it.

A session once opened on a governance failure inherited from a previous session. Finding that before
any edits is a fix; finding it three edits in is a debugging session where someone else's breakage is
tangled with yours. A failing check is a result to report, not a step to retry until quiet.

## 2. Show the top of the queue

```bash
uv run python -m src.governance --ready
```

Present the **top 5 ready phases** in queue order. For each, one row with:

- the phase id and its **title** — lead with the title, the id is the lookup handle
- its `priority` and whether it is in `next_up`
- the plan it belongs to, by title not just code
- its `next_action`, verbatim

Fewer than five ready? Show what there is. Say how many, so the number is not mistaken for the whole
backlog.

**Recommend the first one**, and say in a sentence why it is first — `next_up` position, priority, or
that everything ahead of it is blocked. If the recommendation looks wrong given what the owner said
they want to do, say so; the queue encodes yesterday's intent.

### If nothing is ready

Not the same as "no work exists" — `--ready` already falls back to priority then id when `next_up`
empties, so an empty result means everything is **blocked, complete or deferred**.

Report which, with the blockers named:

```bash
uv run python -m src.governance --ready
```

Then say plainly that a backlog review and re-prioritisation is needed, and that the recipe for one
is **not yet defined**. Do not invent a prioritisation process on the spot. Do not un-defer phases to
manufacture something to do.

## 3. Orient on the chosen phase

If `$ARGUMENTS` names a phase, use that one instead of the recommendation — the owner has already
decided.

Read, in this order:

1. **The phase** in `docs/09-backlog/backlog.yaml` — scope, acceptance, verification, deliverables,
   `depends_on`.
2. **The plan** named in its `plan` field.
3. **`AGENTS.md`** — the working agreement, always.
4. **Conditionally**, and only when they bear on this phase:
   - the phase's `sources`, when they are documents the plan does not already restate
   - the `systems.yaml` entries the phase touches, when it changes their paths or status
   - any governed document the phase names as a deliverable, when it is being amended rather than
     created

Do **not** read session records. They are narrative and long, and their carried-forward content
belongs in phases. The exception is an adversarial review after work is done, where the record of
what was decided and corrected is the point.

## 4. Summarise what you found

Report:

- **What the phase wants**, in your own words, not its scope bullets pasted back
- **The first concrete action**, from `next_action`
- **What "done" means** — the acceptance conditions, and how each will actually be checked
- **Anything that looks wrong**: an acceptance condition no listed verification can observe, a
  deliverable list missing a file the scope clearly requires, a dependency that is not declared. Say
  it now. Both cost far more once the work has started.

## 5. Ask with the tool, in batches, one batch at a time

**Every question raised during orientation goes through the `AskUserQuestion` tool**, not prose in
the reply. A question buried in a paragraph gets one answer covering three things, or none at all;
the tool returns a decision per question, attributable and unambiguous.

- **Batch up to four questions per call** — the tool's limit — and **send one batch at a time**.
  Wait for the answers, then decide whether a further batch is warranted. Answers change what is
  worth asking next: a decision to cut a scope bullet retires every question underneath it.
- **Ask during orientation, before any work starts.** This is the cheap moment. The same question
  asked halfway through is a rewrite, and the owner is then deciding under sunk cost.
- **Put the recommendation first** and mark it `(Recommended)`. Orienting means having a view;
  offering four options with no view moves the analysis back onto the owner.
- **Do not ask what the phase, the plan or `AGENTS.md` already answers.** Read first. A question
  whose answer is in a document you were told to read is a failure to orient, not diligence.
- **Do not batch trivia with substance.** If only one thing genuinely needs a decision, ask one
  question. Padding a batch to four dilutes the one that matters.

The defects found at step 4 are the usual subjects: whether a stale scope bullet is corrected before
the phase is claimed, whether an unverifiable acceptance condition gains a check or loses the claim,
whether a plan's open question is settled now or deferred.

**This applies in every mode, `--go` included.** `--go` skips the confirmation to begin, not the
questions that decide what gets built.

## 6. Then, according to the mode

**Default** — ask whether to proceed, through the tool as step 5 requires, and stop there. Do not
set `status: active`. Do not set the `agent` field. Claiming should follow the owner's decision, not
precede it.

**`--claim`** — set `status: active` and the `agent` field on the phase, bump `updated`, then stop and
ask. Useful when the owner wants the lock held while they think, or while another agent might
otherwise take it.

**`--go`** — claim as above, then begin the phase's `next_action`.

Even under `--go`, surface anything that looked wrong at step 4 **before** starting rather than after.
A defect found while orienting is a question; the same defect found halfway through the work is a
rewrite. If something is wrong enough that the phase should not be executed as written — an
acceptance condition nothing can verify, a missing deliverable, an undeclared dependency — say so and
stop, whatever the mode. `--go` means the owner has skipped the confirmation, not that they have
waived judgement.
