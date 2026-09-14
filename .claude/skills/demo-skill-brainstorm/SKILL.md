---
name: demo-skill-brainstorm
description: "Generate options first, then score them against stated criteria. Fires when the input asks for options or approaches to something not yet decided — \"what are our options\", \"how could we approach this\", \"give me some ideas for\", \"what else could we do here\". Must not fire when the person has already chosen and wants the choice executed, when they name two or more fixed options and want them compared (that is demo-skill-scorecard), or when they ask a question with one correct answer."
---

# demo-skill-brainstorm

Diverges, then converges, and says out loud which of the two it is doing. The failure this prevents
is a reader treating the third option generated during divergence as a recommendation.

**First line of every run, before anything else:**

> **demo-skill-brainstorm** — diverging first, converging second.

## What it needs, and how it gets it

Call `demo-skill-ask-me` to establish the criteria. Do not write questioning of your own, and do not
assume the criteria — assumed criteria produce a ranking the person cannot argue with because they
never agreed to what it optimises for.

Typically undetermined: what a good outcome looks like here, which constraints are hard and which
are preferences, who has to accept the result, and how much scope for change actually exists.

Criteria are established **before** divergence begins, and are not revised after the options are on
the table. Revising them afterwards is fitting the criteria to a favourite.

## Phase 1 — diverge

Announce the phase: `Diverging — these are candidates, not recommendations.`

- Generate options across genuinely different approaches, not variants of one approach with
  different labels.
- Include at least one option that is uncomfortable or unlikely, and say which it is. A divergence
  set with no uncomfortable entry was a convergence in disguise.
- **Score nothing here.** No ordering, no "the obvious one is", no numbering that implies rank.

## Phase 2 — converge

Announce the phase: `Converging — scoring against the criteria we agreed.`

- Score every option against every criterion established in the interview, explicitly, and show the
  scores as a table.
- Say what each score is based on. A score with no basis is a feeling with a number attached.
- **Name what would change the ranking** — which criterion, if weighted differently, puts a
  different option on top. A ranking presented without its sensitivity reads as a verdict.
- Say which options you would drop entirely and why, rather than leaving a long list ranked.

## What it must never do

- **Never blur the phases.** Recommending during divergence collapses the whole method.
- **Never score against criteria the person did not agree to.**
- **Never write a file.** The output is the conversation. For a persisted comparison, that is
  `demo-skill-scorecard`.
- **Never supply the subject matter.** Every option is about what the person brought.
