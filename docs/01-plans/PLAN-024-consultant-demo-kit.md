---
schema_version: 1
id: doc-consultant-demo-kit
code: PLAN-024
title: Consultant demo kit build
kind: plan
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-13'
systems: [sys-demo-kit]
depends_on: [doc-consultant-demo-kit-requirements]
---

# Consultant demo kit build

Builds the 20 components `REQ-008` specifies: 6 commands, 6 skills, 6 prompts, 2 agents. Nothing
else. The roster reached this size through a blind adversarial triage of 23 proposed entries,
recorded on ideas `000171`-`000193`; this plan records what survived, what changed, and why.

## No running scenario: every component is general

**No component is written against a fictional company, engagement or person.** Each one is a general
tool a consultant can point at whatever they are actually working on. The owner supplies the real
material at the moment of use.

This reverses the originating brief, which called for one running scenario used across the whole kit,
and the reversal is the owner's on 2026-09-13. The reason is that a component welded to an invented
situation is a demo prop rather than a reusable tool: it demonstrates well once and is worthless on
Monday. A consultant watching a command operate on a fictional manufacturer has to translate it to
their own work before they can judge it; a consultant watching it operate on *their* engagement does
not.

Concretely, this means no component names an industry, a company shape, a headcount, a timeline or a
job title as its subject. Where a component needs something to work on — a draft, a set of notes, a
recommendation — it takes it as input. Where a teaching file needs to describe a change the reader
should look for, it describes the *kind* of change, not a specific one.

## What the triage changed

The blind triage cut seven entries from the roster that was proposed during the design round. On
2026-09-13 the owner replaced that roster's commands and skills wholesale with their own
(ideas `000222` and `000223`), so most of these components no longer exist in any form. The table is
kept because the *reasons* outlived the components: they are the failure modes any replacement has to
avoid, and three of them shaped the current roster directly — arguments belong to commands, a skill
firing on an unobservable event cannot work, and a component whose lesson is invisible teaches
nothing.

Each cut is recorded on its own idea, and none was discarded:

| Cut | Reason |
|---|---|
| `steelman-the-objection` | Duplicates `stakeholder-read`'s lesson; the objection panel agent teaches it better with three stakeholders |
| `house-style` skill | Fires during the context-file-off run and breaks the one-pager comparison, which is beat 1's strongest moment |
| `assumption-ledger` | Capability overlap with `load-bearing-details` is near-total; a ledger's value accrues over an engagement, not in a demo |
| `stakeholder-tone-check` | Fires on an unobservable send event, and depends on an entry that may itself be dropped |
| `client-ready` **as a skill** | Rebuilt as a command: arguments are a command affordance, and as a skill it could only teach its property by contradicting the definition of a skill |
| `deck-outliner` | A command wearing an agent costume; its lesson is invisible by construction |
| `long-draft-writer` | Cannot be scoped under the time budget, silently needs write access, and depends on a cut entry |

Three design changes to surviving entries:

**The prompt ladder is reordered.** As originally designed, the presenter revealed the human obstacle
at rung 4 — meaning the presenter already knew which detail was load-bearing, and the model never
demonstrated the capability the kit claims is its most important idea. The interview now runs first,
before the obstacle exists in the prompt, and the obstacle enters **because the model asked for it**.
Rung 2 also splits: situation and target are two ingredients, and the ladder's discipline is one per
rung.

**Skills announce themselves.** A command shows itself being typed and an agent shows itself
spawning, but a skill firing on recognition looks exactly like Claude being helpful. Every skill
names itself in its first output line, or the skills third of the roster teaches nothing the audience
can attribute.

**Nothing drafts a stand-in context file.** The earlier roster had a command whose subject was
the context file, which in this repository is `CLAUDE.md` — a file no agent may write. Resolving that
with a stand-in narrated as though it were the real one would have been a prop pretending to be the
thing the component existed to teach. The owner's roster settles it differently and better:
`demo-cmd-context-check` reports what Claude knows and what is missing, and never authors the file at
all. Noticing the gap is the lesson; filling it is the consultant's.

## Constraints this build works under

The kit is built into this repository's live `.claude/` directory, which the blind reviewers argued
against and the owner decided.

- **No kit component writes a repository file.** Components that produce an output file —
  `demo-skill-flowchart` and `demo-skill-scorecard`, which emit HTML — write only to their stated
  output location. Nothing writes into `docs/`, `.claude/`, `_data/` or any governed path, and
  nothing writes `CLAUDE.md`.
- **Kit entries will appear in `orient`'s command enumeration and the workbench agent picker** during
  ordinary D-System work. No parking mechanism is in scope. `REQ-008` records this as an accepted
  consequence, not an open defect.
- **Two fifteen-minute runs now exist.** `REQ-006` R09 governs the D-System segment; this kit is the
  other one. Both are named explicitly wherever either is referenced.

## Component specifications

Confirmed with the owner component by component on 2026-09-13. These are the features each one must
have; anything not listed is the builder's judgement, and anything contradicting them is a defect.

### Commands

Six commands, owner-authored on 2026-09-13 (idea `000223`), replacing the set proposed during the
design round. Names carry the `demo-cmd-` prefix.

**`demo-cmd-teach-me`** — takes any topic and produces a tiered explanation with a hands-on exercise.

- **Tiered**: the same topic at increasing depth, so the reader stops where they are satisfied rather
  than reading to the end to find their level.
- **Ends in an exercise**, not a summary. The hands-on step is what separates this from an article.
- **Any topic**: it names no domain of its own and carries no worked example.

**`demo-cmd-askme`** — forces Claude to interview the consultant before acting. The flagship
do-not-guess demonstration, and the command half of the kit's one duplicated capability.

- **Interviews first, acts second.** It does not answer and then check; it asks and waits.
- **Asks only what would change the output**, and says why each question matters, so the reader can
  tell these are the right questions rather than a form to fill in.
- **Names what it will assume** for anything left unanswered.
- Pairs with `demo-skill-ask-me`. Identical stems, differing only by type prefix: the pairing is
  deliberate and the prefix is the only thing that says how each is invoked.

**`demo-cmd-explain-this`** — points at anything the consultant has in front of them and explains it
in plain business English.

- **Any artifact**: a document, a spreadsheet, a system message, an error, a file. Broadened from
  files, folders and errors so the command is not a developer tool wearing a business label, and so
  it satisfies the kit's no-code rule rather than forcing an exception to it.
- **No jargon in the output**, including no jargon it invents to explain jargon.
- **Says when it is unsure** what something is, instead of producing a confident wrong reading.

**`demo-cmd-context-check`** — shows what Claude currently knows about the project and what is
missing. Makes the invisible visible.

- **Two lists: known and missing.** The missing list is the useful half.
- **Ranks the gaps** by what they would change, so the reader knows which to close first.
- **Does not author the context file.** The kit deliberately teaches noticing the gap rather than
  filling it; showing what is missing implies what to write.

**`demo-cmd-rubber-duck`** — asks probing questions about a half-formed idea and offers no solutions
until invited.

- **Withholds solutions by default.** This is the rule that makes the command work, and the one a
  model will break without an explicit instruction not to.
- **Questions probe, not clarify** — what the idea assumes, what it would take to be wrong, what it
  rules out.
- **Offers to switch modes** once, rather than drifting into advice unasked.

**`demo-cmd-second-opinion`** — re-examines Claude's own previous answer adversarially and reports
what it would change.

- **Argues against its own prior output**, not a summary of it.
- **Reports what it would change and what it would keep.** An adversarial pass that overturns
  everything is as useless as one that overturns nothing.
- **States what evidence would settle it** where it is genuinely unsure.

### Skills

Six skills, owner-authored on 2026-09-13 (idea `000222`), replacing the set proposed during the
design round. Names carry the `demo-skill-` prefix. Every skill names itself in its first output line
so the audience can attribute the firing, and every description states both its firing cues and the
cases where it must not fire.

**`demo-skill-flowchart`** — turns a described process into a rendered diagram. The kit's best visual
payoff.

- **Fires when a process is described in sequence** — steps, hand-offs, conditions — which is a cue
  present in the text.
- **Produces two outputs**: a standalone self-contained HTML file that opens in any browser, which is
  what keeps the component general and portable, and a repository-specific path that publishes into
  the HTML viewer. The standalone file is the component; the viewer path is this repository's
  convenience.
- **Reflects the process as described**, including where it is incoherent. A diagram that silently
  fixes a gap hides the finding the consultant most needs.

**`demo-skill-brainstorm`** — structured divergent-then-convergent ideation with explicit option
scoring.

- **Diverges before it converges**, and says which phase it is in, so the consultant does not read
  early options as recommendations.
- **Scores explicitly** against stated criteria rather than ranking by feel.
- **Calls `demo-skill-ask-me`** to establish the criteria rather than assuming them.

**`demo-skill-ask-me`** — the elicitation engine, and the skill half of the kit's one duplicated
capability.

- **Parameterised** by question count, single versus multi-select, and whether to include
  recommendations. Parameters are read from how it is asked and **documented in a table in its body**
  — skills carry no `argument-hint`, which is the command affordance, so the parameters are prose and
  the table is the documentation.
- **Recommends by default.** Include-or-exclude recommendations is one of its parameters and the
  default is to include: a question offered with no recommendation moves the analysis back onto the
  person answering.
- **Other skills genuinely call it.** `flowchart`, `brainstorm` and `scorecard` invoke it to gather
  what they need instead of each writing its own questioning. This makes the kit compose, and makes
  this the most load-bearing component in it — a change here reaches three other skills.
- Pairs with `demo-cmd-askme`.

**`demo-skill-meeting-notes`** — raw notes in, structured summary with decisions, owners and risks
out. The most immediately relatable component in the kit.

- **Fires on pasted raw notes** — bullet fragments, names, dates — the most lexically recognisable
  cue in the set.
- **Never invents an owner and never invents a date.** Missing ones are reported missing. This rule
  is inherited deliberately from the component this one replaced, and this repository's own
  `schemas/commitment.schema.json` independently arrived at the same protected-field design.
- **Separates decisions, owners and risks**, and says what it treated as discussion rather than
  silently discarding it.

**`demo-skill-scorecard`** — a weighted comparison matrix for any decision: vendor, approach, tool.

- **Weights are explicit and stated before scoring**, so the conclusion is traceable to the weights
  rather than asserted.
- **Produces two outputs**, as `flowchart` does: a standalone HTML table and a repository-specific
  publish into the HTML viewer.
- **Calls `demo-skill-ask-me`** for the options and the criteria.
- **Names what the weights are doing** — which option wins under different weightings, so the
  consultant sees the decision's sensitivity rather than a single verdict.

**`demo-skill-make-it-a-skill`** — watches what was just done manually and drafts a reusable skill
from it. The moment that makes skills self-propagating, and the replacement for the capture-this
command.

- **Fires on a repeated or manual sequence** the consultant has just worked through by hand.
- **Names what it generalised and what it dropped.** A good sequence is specific and a reusable one
  is not; which specifics became parameters is the craft being taught.
- **Shows the draft and writes nothing.** The consultant saves it, which is both honest and the
  better demonstration.
- **Says why it is a skill rather than a command** — recognition versus deliberate invocation —
  teaching the distinction at the moment it is being decided.


### Agents

**`demo-agent-objection-panel`** — three stakeholders against a recommendation, in a separate context.

- **Three named roles, one of them sympathetic.** If everyone objects the output is a wall of
  resistance; the disagreement between panellists is what teaches sequencing.
- **Returns a summary, not three transcripts.** Delegation is right here because the thinking would
  flood the main conversation — returning all of it proves the opposite of its own lesson.
- **Ranks objections by what would actually stall the work**, turning complaints into a sequencing
  decision.
- **Declares its tool posture explicitly.** It needs no write access, and saying so keeps the
  scoping-is-deliberate lesson consistent across both agents.

**`demo-agent-evidence-checker`** — traces every number in a draft to a source.

- **Tools: `Read`, `Grep`, `Glob` — no `Bash`.** Bash is a write channel here, so excluding it is
  what makes the read-only claim true rather than decorative.
- **Never sees how the draft was written** — the draft and nothing else, no rationale, no history.
  Independence is the whole reason this is an agent, and it is the rule this repository's own
  session-close review runs on.
- **Reports unsupported numbers first.** The ones that trace are the boring half.
- **Distinguishes wrong from unsourced** — a number contradicted by a source and a number with no
  source are different problems, and collapsing them sends the consultant chasing the wrong one.

### Prompts

Six files: five ladder rungs and the anti-pattern gallery. The obstacle is **not** its own rung — it
arrives inside the interview rung, because it is no longer the presenter's move to make.

**No rung carries a fixed example, and none records a pinned output.** Each rung teaches *the
ingredient*: what it is, why it changes the answer, and what change to look for when it lands. The
owner supplies a real engagement and runs the ladder against it live. This is what keeps the ladder
usable by anyone, in any session, instead of only in one rehearsed performance — and it means a rung
cannot go stale when the model changes.

The discipline the rungs replace pinned outputs with is **stating the expected change in advance**,
so the owner can tell the room whether it happened, including when it did not.

**Rung 1 — the floor.** A bare, under-specified ask.

- Characterises the kind of ask that belongs here — the one a consultant would genuinely type on a
  Monday, not a strawman — so the reader recognises their own habit rather than watching a setup.
- **Says what is wrong with the output**, not merely that it is weak: advice generic enough to fit any
  client and any year. Fluent text reads as good text, so the failure has to be named.
- **Names what a consultant really does next** — gives up on the tool and writes it themselves, which
  is the habit the ladder exists to interrupt.

**Rung 2 — adds situation.** Who is involved, what the arrangement is, what constrains it.

- **Situation only**: no objective, no target figure. The split only works if this rung is disciplined
  about not leaking the goal.
- **Names the comparison to make** against rung 1, since the ladder teaches by difference rather than
  by any single output.
- **Names what the model still does not know**, which sets up the rungs that follow.
- **Says the expected gain is modest**, and tells the owner to say so out loud if it is. Situation
  alone usually moves the answer less than the objective does, and a ladder that oversells its second
  rung loses the room for its third.

**Rung 3 — adds the objective.** Current state and target state.

- **The objective only.**
- **Names the change to watch for**: advice in general becomes advice about a specific gap, with
  tradeoffs a consultant could argue with.
- **States the expectation that this rung outperforms rung 2**, so the owner can confirm or deny it in
  front of the room. A teaching file that states a prediction and invites its test teaches more than
  one that only asserts.
- **Warns that an objective invites false precision**: stating a number makes the model produce
  confident plans built on it, which is useful and is also the moment to check the number is real.

**Rung 4 — adds the audience.** Who receives it and what they do with it.

- **Run as a pair** — the same prompt against two audiences, back to back. A single output cannot
  demonstrate that audience changes form; without the pair the owner is asserting it.
- **Shows form changing, not only tone**: what gets led with, what is cut, what becomes an appendix.
- **Names what the audience will do with it.** A document for approval and a document for information
  are different things, and the decision is what drives the form.
- **Names the comparison to make** between the two runs. The earlier roster had a command that
  automated this and the owner's roster does not, so the rung stands on its own rather than pointing
  at a component.

**Rung 5 — the interview, where the constraint arrives.** The rung the reordering exists for.

- **The owner never types the human constraint first.** It enters only as an answer to the model's
  question. This is where the kit's central claim is demonstrated instead of described.
- **Tells the owner to hold something back** going in — a known obstacle they have deliberately not
  stated — so there is something for the model to find. Without that, the rung cannot succeed.
- **Names the change to watch for**: the recommendation inverting rather than merely softening. A plan
  that routes around a person becomes a plan that makes them part of it.
- **States the fallback** for when the model asks about systems or process instead of people: what the
  rung then teaches, which is weaker, and what the owner says in that case.

**The anti-pattern gallery.** Four entries; politeness padding is cut for costing only tokens.

- **Four entries, each with a cost the user pays**: stacked questions, be-comprehensive, manufactured
  urgency, and asking-for-an-opinion-then-arguing-with-it. Each names the failure, shows it, and
  states the fix in one line.
- **Leads with opinion-then-argue** — the model capitulates and the consultant concludes it agreed
  with them. It destroys value rather than wasting time, and it is the one the room least expects.
- **Every entry is one actually observed.** The original design note set this bar and recorded no
  evidence of meeting it; any entry that cannot be traced to a real occurrence is cut rather than
  invented.
- **Pairs each anti-pattern with the rung or component that fixes it**, so the gallery closes the kit
  by pointing back into it rather than ending on a list of mistakes.

## Build order

Four independent phases, one per component type. Nothing depends on anything else, because the
fixture work that would have created a dependency is out of scope.

1. **Commands** — `teach-me`, `askme`, `explain-this`, `context-check`, `rubber-duck`,
   `second-opinion`, all `demo-cmd-` prefixed.
2. **Skills** — `flowchart`, `brainstorm`, `ask-me`, `meeting-notes`, `scorecard`,
   `make-it-a-skill`, all `demo-skill-` prefixed and all self-announcing. Build `ask-me` first:
   three of the others call it.
3. **Prompts** — the reordered ladder and the anti-pattern gallery.
4. **Agents** — `demo-agent-objection-panel`, `demo-agent-evidence-checker`, tool lists explicit.

Testing and demonstration are the owner's, and are not phases here.
