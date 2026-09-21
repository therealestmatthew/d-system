---
name: demo-skill-scorecard
description: "Build a weighted comparison matrix for a decision between named alternatives. Fires when the input names two or more candidates and asks which to pick — \"should we go with A or B\", \"compare these three vendors\", \"we're choosing between two approaches\", \"help me decide between\". Must not fire when the options do not yet exist and need generating (that is demo-skill-brainstorm), when the decision is already made and the person wants it justified, or when only one candidate is named."
---

# demo-skill-scorecard

A weighted comparison whose conclusion is traceable to its weights. The point is not the winner; it
is that the person can see which weight produced the winner, and what happens when that weight is
wrong.

**First line of every run, before anything else:**

> **demo-skill-scorecard** — weights stated before scores.

## What it needs, and how it gets it

Call `demo-skill-ask-me` for the options and the criteria. Do not write questioning of your own.

**Say that you are calling it**, in the line after your own announcement — `calling demo-skill-ask-me
for the options and the criteria`. One component visibly using another is the thing being
demonstrated, and it is invisible unless the hand-off is stated.

Typically undetermined: which criteria genuinely matter here, how they weigh against one another,
which are hard constraints that disqualify rather than deduct, and who has to accept the decision.

## Weights first, scores second

**State the weights, in full, before a single score is written.** Weights agreed after the scores
are visible are weights fitted to a preferred answer, and the exercise becomes decoration.

- Show the criteria, their weights, and what each weight means, and get them confirmed before
  scoring.
- Say what each weight is based on — a stated constraint, a preference, an inference. An inferred
  weight is marked as inferred.
- A hard constraint is not a heavy weight. Handle it as a disqualifier, listed separately, and say
  which options it removes before any scoring happens.

## Check the arithmetic before reporting it

**Recompute every weighted total and every sensitivity claim before either appears in the output.**
A total that does not equal its own scores times its own weights destroys the one thing this
component offers, which is that the conclusion is traceable. The same applies to each claim about
reweighting: work out the alternative total and confirm it says what you are about to say it says.

This is not a theoretical risk. A scorecard produced while building this skill reported a winning
total of 4.10 against scores summing to 4.00, and the sensitivity paragraph beneath it was reasoning
from the wrong number.

## Name what the weights are doing

A single verdict hides the decision's shape. Every run reports:

- **The result under the agreed weights.**
- **Which option wins under a different plausible weighting**, and which criterion has to move for
  the answer to change.
- **How close the top two are.** A winner ahead by a rounding error is a tie, and saying so is more
  useful than declaring it.
- **Which score, if wrong, would change the outcome.** That is the one worth checking.

## Two outputs

**1. The standalone file — this is the component.**

Write one self-contained HTML file that opens by double-clicking it in any browser, on a machine
with no repository, no server and no network.

- Location: the directory the person names. When they name none, `~/demo-kit-output/`, created if
  it does not exist. Never the current directory, so running this inside a repository does not drop
  a file into someone's working tree.
- Filename: `<short-slug-of-the-decision>-scorecard.html`.
- The matrix is a plain HTML table with the CSS inlined in a `<style>` block. No `<script src>`, no
  stylesheet link, no web font, no external image. A file that needs the network is not
  self-contained.
- The page carries the weights, the scores, the weighted totals and the sensitivity statement —
  everything needed to re-argue the decision without the conversation it came from.
- Report the absolute path back, and say it can be emailed or copied to any machine as one file.

**2. The repository publish — a convenience, not the component.**

When the current directory is inside a repository that has a `_public/` directory, also write the
same page to `_public/demo-kit/<same-filename>`, creating `_public/demo-kit/` if needed. That is
where this repository's HTML Viewer can browse and render it.

When there is no such repository, skip this silently and say the standalone file is the output.

## What it must never do

- **Never write outside those two locations.** Not `docs/`, not `.Codex/`, not `_data/`, not
  `sql/`, not `schemas/`, not any governed document path, and not the repository root.
- **Never score before the weights are agreed.**
- **Never adjust a weight after seeing the result.** If a weight looks wrong, say so and ask; do not
  quietly correct it.
- **Never present a verdict without its sensitivity.**
- **Never supply the options or the criteria itself.** Both come from the person, through
  `demo-skill-ask-me`.
