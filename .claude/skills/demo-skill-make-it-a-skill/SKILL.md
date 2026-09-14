---
name: demo-skill-make-it-a-skill
description: "Draft a reusable skill from a sequence the person has just worked through by hand. Fires when the input says the sequence repeats or was manual — \"I do this every month\", \"that's the third time I've asked for that\", \"I always have to explain the format first\", \"can we make that reusable\". Must not fire on a one-off request, on a first occurrence with nothing to generalise from, or when the person asks how skills work in general rather than about a sequence they just ran."
---

# demo-skill-make-it-a-skill

Watches a sequence someone has just done by hand and drafts the reusable version. This is the
component that makes the rest of the kit self-propagating: the consultant leaves able to build the
next one themselves.

**First line of every run, before anything else:**

> **demo-skill-make-it-a-skill** — drafting a reusable version of what you just did by hand.

## The craft being taught: what generalises and what does not

A sequence that just ran was specific. A reusable one is not. Which specifics become parameters and
which get dropped is the whole skill, so the draft is always accompanied by both lists:

- **Generalised** — each specific that became a parameter, named, with what it varies over. "The
  quarter" became a date range; "that spreadsheet" became any tabular input.
- **Dropped** — each specific that was left out, with why. Usually because it was a one-off
  correction, or because it belongs to this instance rather than the pattern.

State both lists before the draft, not after. They are how the person judges whether the draft
captured the right thing.

## Skill or command — say which, and why

Decide and explain the decision, because the person is making this choice for real for the first
time:

- **A skill** fires on recognition. The model notices a cue in what was said and offers the
  capability without being asked for it by name. Right when the person will not remember it exists
  at the moment they need it.
- **A command** is invoked deliberately by name. Right when they will know they want it, and when
  firing unasked would be intrusive.

Name which this sequence is, and give the reason in one line. If it genuinely could be either, say
so and say what would settle it.

## Show the draft. Write nothing.

Output the complete draft — frontmatter and body — in the conversation, formatted so it can be
copied straight into a file. Say where it would go and what to name it.

**Do not create the file.** The person saves it. That is honest about who owns their configuration,
and it is the better demonstration: they see the artifact and make the decision.

## What it must never do

- **Never write a file.** Not the drafted skill, not a scratch copy, not anywhere. It shows.
- **Never draft from a single occurrence** presented as a pattern. Say there is not yet enough to
  generalise from, and name what a second occurrence would reveal.
- **Never hide what it dropped.** A draft that silently loses a step the person relied on will fail
  the first time they use it, and they will not know why.
- **Never invent a domain.** Everything in the draft comes from the sequence that just ran.
