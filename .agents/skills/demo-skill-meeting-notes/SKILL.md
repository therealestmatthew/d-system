---
name: demo-skill-meeting-notes
description: "Turn raw meeting notes into a structured summary of decisions, owners, actions and risks. Fires on pasted rough notes — bullet fragments, names followed by what they said, dates and times, shorthand, half-sentences, \"notes from the call\", \"here's what came out of the workshop\". Must not fire on a written document that is already structured prose, on a transcript the person asked to be summarised rather than structured, or on a request to write notes for a meeting that has not happened."
---

# demo-skill-meeting-notes

Raw notes in, structured summary out. The most immediately relatable component in the kit, and the
one with the strictest rule about invention.

**First line of every run, before anything else:**

> **demo-skill-meeting-notes** — structuring your notes; anything missing is reported, not filled in.

## Never invent an owner. Never invent a date.

These two fields are protected. An invented owner sends work to someone who never agreed to it; an
invented date creates a commitment nobody made. Both are worse than a blank, because a blank is
visibly missing and a plausible guess is not.

- An action with no owner in the notes is reported with the owner field reading **missing**.
- An action with no date is reported with the date field reading **missing**.
- **Never derive an owner** from who was speaking, who usually does this, or who was in the room.
- **Never derive a date** from "next week", "before month end" or "soon" unless the notes state
  which day that is. Record the phrase as written and mark the date missing.
- List everything marked missing together at the end, so the person can close the gaps in one pass
  rather than hunting through the summary.

## Output sections

**Decisions.** What was actually decided — settled, not discussed. Each with who decided it, if the
notes say.

**Actions.** One row per action: what, owner, due date. Owner and date follow the rule above.

**Risks and open questions.** Anything raised that has no resolution. An open question is not an
action; keeping them apart stops questions turning into work nobody scoped.

**Treated as discussion.** Everything from the notes that landed in none of the sections above,
listed rather than dropped. This is the section that makes the skill trustworthy: the person can
see what was set aside instead of wondering what was lost.

## What it must never do

- **Never invent an owner or a date.** See above; this is the rule.
- **Never promote a discussion point to a decision** because it sounds conclusive. "We should
  probably" is discussion.
- **Never silently discard a fragment.** Unclear notes go under "treated as discussion", flagged as
  unclear.
- **Never write a file.** The structured summary is the output; the person decides where it goes.
- **Never add attendees, agenda items or context** that the notes do not contain.
