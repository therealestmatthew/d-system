---
description: Interview me before you act, asking only the questions that would change the output
argument-hint: "<what you want done>"
---

# Interview me first

$ARGUMENTS

The task above is the thing to be done — **but not yet.** Ask first, act second.

This is the deliberate half of a pair. `demo-skill-ask-me` is the same capability firing on
recognition; this command is it invoked by name, when the person already knows they want to be
questioned. Nothing else about the two differs.

## Ask before you answer

1. **Find what is genuinely undetermined.** Read the task and identify the points where two
   different answers would produce two materially different outputs. Those are the questions.
2. **Ask only those.** A question whose answer would not change what you produce is a form to fill
   in, and it teaches the person that being interviewed is a tax rather than a benefit.
3. **Say why each question matters** — one line stating what changes depending on the answer. This
   is what lets the person judge that these are the right questions.
4. **Ask through the `AskUserQuestion` tool**, up to four questions in one batch, with a recommended
   option first and marked `(Recommended)`.
5. **Wait for the answers.** Do not produce a draft alongside the questions.
6. **Ask a second batch only if the first batch's answers opened something genuinely new.** Answers
   usually retire questions rather than raise them.

## Name what you will assume

Before doing the work, state every assumption you are making about anything that was not asked, or
was asked and left unanswered. One line each. The person can correct any of them before the work
starts, which is the cheapest moment.

## Never

- **Never answer first and check afterwards.** A question asked after the output exists is
  confirmation, and the output is already anchored.
- **Never guess at something that would change the result.** That is the entire point of the
  command.
- **Never ask about something the task already states.**
- **Never proceed on an unanswered question.** No answer is not a yes and is not a default.
- **Never write a file.** Not `CLAUDE.md`, not `AGENTS.md`, not any file in the repository. This
  command produces questions and then an answer in the conversation.
