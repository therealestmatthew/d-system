---
name: demo-skill-ask-me
description: "Interview the person before answering, using multiple-choice questions that each carry a recommendation. Fires when the request explicitly asks to be questioned first — \"ask me what you need\", \"interview me\", \"what do you need to know before you start\", \"don't guess\" — or when another skill invokes it to gather its inputs. Must not fire on a request that already carries what the answer needs, on a direct factual question, or when the person says to proceed on assumptions, guess, or just answer; in those cases answer and state the assumptions instead."
---

# demo-skill-ask-me

The elicitation engine. It asks before it acts, and it is the only component in this kit that
gathers input. `demo-skill-flowchart`, `demo-skill-brainstorm` and `demo-skill-scorecard` call it
rather than writing questioning of their own.

**First line of every run, before anything else:**

> **demo-skill-ask-me** — interviewing you before I answer.

When another skill calls this one, that skill announces itself and then states that it is calling
`demo-skill-ask-me`, so the audience can see one component using another.

## Parameters

Skills carry no `argument-hint` — that affordance belongs to commands. These parameters are read
from how the skill is asked for, in plain language. Nothing needs to be named exactly; "just two
questions", "let me pick several", "no recommendations" all set them.

| Parameter | What it controls | Values | Default | How it is set |
|---|---|---|---|---|
| Question count | How many questions one batch asks | 1–4 | 3 | "ask me two things", "one question only", "ask me everything you need" (→ 4) |
| Selection mode | Whether an answer takes one option or several | single-select, multi-select | single-select | "let me pick more than one", "multi-select", "one answer each" |
| Recommendations | Whether each question marks a recommended option | include, exclude | **include** | "no recommendations", "don't steer me", "tell me what you'd pick" |

Four is the hard ceiling on question count: the `AskUserQuestion` tool takes at most four questions
per call. A fifth question is a second batch, not a wider first one.

**Recommendations are included by default and the default is deliberate.** A question offered with
no recommendation moves the analysis back onto the person answering, which is the opposite of what
this skill is for. Exclude them only when asked to.

## How it runs

1. **Work out what is actually undetermined.** Read the request and name the points where two
   different answers would produce two different outputs. Those are the questions. Everything else
   is already decided.
2. **Ask only those.** A question whose answer would not change the output is a form to fill in.
   Drop it.
3. **Say why each question matters** — one line per question, stating what changes depending on the
   answer. This is what lets the person tell these are the right questions rather than a
   questionnaire.
4. **Ask through the `AskUserQuestion` tool**, in one batch, honouring the parameters above. Put the
   recommended option first and mark it `(Recommended)` unless recommendations are excluded.
5. **Wait.** Do not answer alongside the questions, and do not proceed on a prediction of the answer.
6. **Ask a second batch only if the first batch's answers opened something new.** They often retire
   questions rather than raising them.
7. **Name what is still assumed.** Anything that was not asked, or was asked and left unanswered,
   gets stated as an explicit assumption before the answer is given.

## What it must never do

- **Never answer first and check afterwards.** Asking after the output is written is confirmation,
  not elicitation, and the output is already anchored.
- **Never ask more than four questions in one batch.** Batch two comes after batch one's answers.
- **Never ask what the request already answers.** Re-asking a stated fact reads as not having read
  it.
- **Never write a file.** This skill produces questions and then an answer in the conversation.
- **Never proceed on an unanswered question.** No answer is not a yes, and it is not a default.

## When another skill calls it

A calling skill passes three things: what it needs to know, why each item is needed, and its
parameter choices. It does not pass a pre-written list of questions — working out which questions
are load-bearing is what this skill does.

The calling skill then uses the answers directly. It does not re-ask, re-confirm, or second-guess
them.
