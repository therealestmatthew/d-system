---
id: mem-proc-yield-and-renumber-a-collided-identifier
title: When You and a Peer Take the Same Identifier, the One Integrating Second Renumbers
type: procedure
tags: [agentic-systems, knowledge-base, automation]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-13
updated: 2026-09-13
confidence: high
related: [mem-proc-check-that-cannot-fail, mem-proc-runtime-behavior-needs-runtime-evidence]
scope: global
---

## The rule

Identifiers in this repository are allocated by reading the current state of a file — the code
register for document codes, `_data/ideas.jsonl` for idea ids. A branch that has not integrated is
not part of that state, so two agents working at the same time can be issued the same identifier and
both be correct at the moment they ask.

**The agent integrating second yields and renumbers.** Whoever is already on the integration branch
keeps the identifier. This is not a judgement about whose work matters more; it is the only rule
that terminates, because the first party's id is already referenced by merged commits and the
second's is referenced only by its own branch.

`AGENTS.md` writes this rule for document codes. **Idea ids have the same race and no written rule,
no reservation step, and no guard.** A duplicate document code raises a governance error. A
duplicate idea id raises nothing.

## Why the idea log is the dangerous case

`_data/ideas.jsonl` is append-only. Two branches appending different lines produce **no conflict**
when they merge — git takes both additions, which is the correct behaviour for an append-only file
and exactly the wrong outcome here. The log then contains two `created` events carrying the same id,
and the reader that folds events into ideas has no way to tell them apart. Two unrelated ideas
become one, and any annotation written against that id lands on whichever one wins.

So the failure mode is not the conflict. The conflict is the lucky case. Both observed collisions
were caught by accident: the first because the two appends happened to touch adjacent lines, the
second because the branch was reset onto the integration branch rather than merged. Neither
detection was a check.

**Check before you rely on an id crossing a branch boundary.** Before integrating work that
allocated an identifier, re-read the destination's state on the integration branch and confirm your
id is still free. Do not infer it from the absence of a conflict — absence of a conflict is not
evidence here.

## The recovery, for an idea id

1. **Never hand-edit `_data/ideas.jsonl`.** It is append-only and `tools/append_idea.py` is its only
   sanctioned writer. Editing the file to change one id produces a log that no longer records what
   happened, and there is no correction path afterwards.
2. **Drop your own events** from your branch — the `created` line and every event you appended
   against the colliding id. You are removing work that has not integrated, never a peer's.
3. **Re-append through the writer** and take the new id from the writer's own output. Do not predict
   it, do not compute it as "the last one plus one": the next allocation depends on state you have
   just changed, and a guessed id sends the write somewhere else.
4. **Re-apply every annotation and link** to the new id, then **read the record back** and confirm
   the text landed on the record you meant. A misdirected annotation is silent.
5. **Update every file that referenced the old id** — handoff documents, priority files, prompts,
   commit messages you have not yet written. Grep for the old id rather than recalling where you
   used it.
6. **Regenerate the derived view**: `uv run python tools/generate_ideas_md.py`. `docs/00-working/ideas.md`
   is generated and a test fails on any difference.

A batch renumbers the same way, whole. Every id in the batch shifts, so step 5 is the expensive one
and the one most likely to be done partially.

## Worked example (2026-09-12 and 2026-09-13)

Both instances are recorded in `GOV-003`'s Concurrency collisions table.

**First.** Two sessions allocated `000153` — a hand-off idea at 12:16:28 on an unintegrated branch,
and a peer's idea about the hand-off protocol drifting across three documents at 14:47:02, already
integrated. The branch's session renumbered to `000157` and recorded the missing guard as `000158`.

**Second, one day later.** A peer landed thirty-six ideas as `000159`–`000194` in one commit — a
batch that had itself just shifted up by two because of the first collision — while another session
held `000159` on its branch. That session renumbered to `000195`. The recurrence was annotated onto
`000158` rather than opened as a new idea, because the same defect already had a record.

**The generalisable lesson:** the first collision's cost was a renumber. The second's would have
been silent data loss had the branch merged normally instead of being reset. When a race has no
guard, the cost of an instance is set by how it happens to be detected, not by how bad it is.

## Why this is model-agnostic

Filed in `brain/` deliberately. The race is a property of allocating identifiers from a file that a
peer's unmerged branch is not part of. Any agent, under any model, that reads the current state and
takes the next number will hit it, and both observed instances had to rediscover the rule from
`AGENTS.md`'s document-code wording rather than reading it where it applied.
