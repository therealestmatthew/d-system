# Reporting to the owner

The working agreement (`AGENTS.md`) governs the work. This document governs how the work is
reported to the owner.

## Name things, then cite them

Lead with what a thing is. Its id or code goes in parentheses as the lookup handle, never as the
noun.

> **Raw capture contracts** (`phase-<track>-<NN>`): what a captured note looks like on disk, and
> the ignore rules that keep it untracked.

Never make a bare phase id or document code the subject of a sentence. A code is a filename, and
the owner cannot read it without opening a file. The first time a phase is mentioned in a session,
add a one-line gloss of what it does; the title alone is often not enough.

Governed documents take the same form: the document's title or role first, its code in
parentheses, as in "the capture routing decision (`ADR-<NNN>`)".

Names are looked up, not invented:

- A phase's title is its `title` field in the backlog.
- A document's title is the `title` field in its front matter.
- A track prefix's meaning is in the table of tracks beside the backlog, where the repository keeps
  one (see `repository-layout.md`).

## Ideas are named id first

An idea is the exception. Its six-digit id is the lookup handle and its title is prose, so the id
comes first and a short gloss follows in parentheses: `<id> (<short title>)`, not
"the <short title> (`<id>`)". This form applies wherever an idea is named: in prose, in commit
messages and in finding annotations.

## Show the output that carries information

- When the number or the message is the point (a row count, a failure, a diagnostic the owner
  would otherwise have to reproduce), paste the real output.
- When the output is a wall of passing checks, summarise it.
- A summary of a failure is not a result. The failure is the result.
- A failing check is a result to record, not a step to retry until it goes quiet, and it is
  reported as it happened.

## Do not block on a question that can wait

Ask when the answer changes what gets built, and ask at the point the work reaches the question.
Any other question is stated as an assumption: the work continues, and the assumption is listed at
the end.

Ambiguity is flagged, not interrupted for. An agent that asks about everything hands the
organising work back to the person it exists to relieve of it.

## Capture new asks as ideas, immediately

When the owner names a want outside the session's current work (a bug they noticed, a feature, an
audit, an item for a later planning session), record it at once through the `idea` skill, one idea
per distinct ask.

- Report each recorded id back to the owner, taken from the writer's own output line. Never guess
  an id.
- Never fold a new ask into the active task, and never hold it in conversation memory until the end
  of the session.
- Record an ask as given. Never decline it, merge it or reword it because it overlaps something
  that exists; note the overlap in its body and leave it for triage.
- Asks that belong together for one future session are linked to a shared anchor idea and
  annotated there, so they come up together.

While sessions run under `multi-session.md`, capturing an ask means sending it to the Ideation
session as an `IDEA` message; the immediacy and one-per-ask rules are unchanged.

The idea log is the capture path in every session and context. It keeps the current work
uninterrupted and makes sure the ask outlives the session.

## Say plainly when a correction is a correction

When the owner corrects something and is right, say so in one sentence and move on. Do not argue
the point again, and do not present a wrong call as partly right. A correction that is not stated
as one leaves the owner unsure whether it was taken on board.
