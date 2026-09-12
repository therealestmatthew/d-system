---
id: mem-proc-ask-through-the-tool
title: A Question You Want Answered Belongs in the Tool, Not in Your Closing Paragraph
type: procedure
tags: [knowledge-base, agentic-systems, ai-tools]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-12
updated: 2026-09-12
confidence: high
related: [mem-proc-audit-your-own-corrections, mem-proc-scope-dispatches-to-the-turn-budget]
scope: project
---

## The situation

You are mid-session. The work is going well, the owner is engaged, and you reach something you
genuinely need them to decide. You write it into the closing paragraph of your reply: "Next is
either your read of the document, or Workstream A — which would you prefer?"

This feels correct. The question is short, the context is right there, and opening a tool call for
one decision feels heavier than the decision deserves.

The characteristic failure is that **the question does not get answered**. The owner replies to
something else in the message, or answers three questions with one sentence, or asks what you meant
by a term — and the decision you needed is still open a turn later. On 2026-09-12 the owner had to
say "AskUserQuestion tool" three separate times in one session to get questions moved out of prose.
Their standing instruction: *"if you want to ask a question and for it to be answered, always always
always use the AskUserQuestion tool."*

## Why it happens even when you know the rule

The rule is usually learned as *ask decisions up front, in the opening investigation*. That framing
makes it feel scoped to a phase of the session, and every failure below happens outside that phase:

- **The question arrives late.** You finish a document and want to know what to do next. The opening
  investigation is long over, so the rule feels inapplicable.
- **The question feels too small.** One binary choice does not seem to warrant a tool call. But
  `AskUserQuestion` accepts a single question, and a one-question batch is cheap.
- **You already wrote the context.** The reply explains the tradeoff well, so appending the question
  feels like the natural close rather than a separate act.
- **You are reporting, not asking.** You finish a status summary and end with an offer. An offer the
  owner must choose between *is* a question, even when it is phrased as a menu.
- **The turn has several questions.** They get compressed into a paragraph because four tool
  questions feels like an interrogation. Four is the batch size; that is what it is for.

## What to do

1. **Before ending any turn, scan your reply for questions.** If any of them is one you want
   answered, it does not ship in prose. Move it to a tool call.
2. **Apply the rule at any point in a session**, not only during opening investigation: mid-task, at
   a gate, during close-out, when flagging something you found.
3. **A single question is enough for a tool call.** Do not hold a decision back waiting for three
   more to batch with it.
4. **Distinguish rhetorical from real.** Questions raised to make the owner think, or to show your
   reasoning, are fine in prose. Anything whose answer changes what you do next is not.
5. **An offer is a question.** "Next is either A or B" needs the tool exactly as much as "should I
   do A or B?"
6. **Put your recommendation first**, marked `(Recommended)`, and send one batch at a time — answers
   to a batch frequently retire the questions you were about to ask underneath them.

## Worked example (2026-09-12)

The idea-batching planning session used `AskUserQuestion` correctly four times — for the demo cut,
the pack scope, the agent roster, the seeding design, the granularity target and the descope ladder.
Every one of those returned a clean decision per question, and several returned better answers than
any option offered.

Between those batches, four turns ended with a question in prose instead:

- "Ready to start Workstream A — or would you rather I draft Prompt A first?"
- "Next is either your read of `PROMPT-025`, or Workstream A."  *(twice, in consecutive turns)*
- A five-item review list closing with which three "I'd want settled before Prompt B encodes them."

The first produced an answer. The others produced "What do you mean workstations A as an option?",
"What do you mean by my read of the document?", and finally "AskUserQuestions tool" — three turns
spent clarifying prose that one tool call would have rendered unambiguous, because the tool forces
each option to carry a label and a description.

The lesson is not that the prose was badly written. It is that a tool call makes the options
explicit and returns a decision per question, and a paragraph does neither.
