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

Builds the 16 components `REQ-008` specifies: 6 commands, 2 skills, 6 prompts, 2 agents. Nothing
else. The roster reached this size through a blind adversarial triage of 23 proposed entries,
recorded on ideas `000171`-`000193`; this plan records what survived, what changed, and why.

## The running scenario

One fictional company across the whole kit: a mid-size manufacturer that has acquired three
subsidiaries and now runs three different month-end closes, consolidating onto one calendar and
cutting the close from twelve days to five. The human obstacle is the controller at the largest
subsidiary — long-tenured, well respected, reading standardisation as a judgement on their team.
Their close is the slowest **and** the most accurate, which is what makes the objection real rather
than an obstacle to be talked around.

The scenario is the setting each component is written against. It is not a deliverable: no corpus,
sample inputs or fixture documents are built. The owner supplies whatever an entry operates on when
demonstrating it.

## What the triage changed

Seven entries are cut, each recorded on its idea with the reason, none discarded:

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

**`context-me` writes nothing.** Its subject is the context file, which in this repository is
`CLAUDE.md` — a file no agent may write. The resolution is not a stand-in file narrated as though it
were the real one; that would be a prop pretending to be the thing the entry exists to teach. The
command drafts the content to the screen and the consultant saves it themselves, which is both honest
and the better demonstration: the audience watches the file become theirs.

## Constraints this build works under

The kit is built into this repository's live `.claude/` directory, which the blind reviewers argued
against and the owner decided.

- **No kit component writes any file here.** This covers `context-me` and every other entry.
- **Kit entries will appear in `orient`'s command enumeration and the workbench agent picker** during
  ordinary D-System work. No parking mechanism is in scope. `REQ-008` records this as an accepted
  consequence, not an open defect.
- **Two fifteen-minute runs now exist.** `REQ-006` R09 governs the D-System segment; this kit is the
  other one. Both are named explicitly wherever either is referenced.

## Component specifications

Confirmed with the owner component by component on 2026-09-13. These are the features each one must
have; anything not listed is the builder's judgement, and anything contradicting them is a defect.

### Commands

**`/context-me`** — interviews the consultant and produces their context file.

- A hard cap of **three questions**, chosen by what would most change the output. The command that
  opens the demo models the load-bearing idea rather than only describing it.
- Covers **three fields**: who you are, who you write for, current engagement. House style is
  deliberately absent — `/one-pager` demonstrates voice better than a declared rule states it.
- Ends by **naming the file and where it goes**, stating plainly that it has written nothing and the
  saving is the consultant's.
- Emitting one complete paste-ready block was offered and not selected; the format of the content is
  the builder's judgement.

**`/whats-load-bearing`** — the kit's central idea, made executable.

- **Ranks** the missing details rather than listing them. The ranking carries the judgement; a flat
  list of everything absent is a checklist.
- Asks only the **top two or three** after ranking.
- Says **why** each detail is load-bearing — what the answer would change to, depending on the reply.
  Without this the audience sees questions and cannot tell they are the right ones.
- **Names what it will assume** for anything left unanswered, so declining is a choice rather than a
  dead end.

**`/stakeholder-read`** — a person's likely position and what would move them.

- **Positions and interests, never personality.** What they are protecting and what they would trade;
  no temperament, no motive-guessing.
- **Separates what it was told from what it inferred**, in two marked sections. Without the split a
  consultant can say it restated the input, and be right.
- **States what would change its read** — the fact that, if true, flips the assessment.
- Asks for the **relationship**, not just the role: someone overruled before reads standardisation
  differently from someone who has not been.

**`/capture-this`** — turns what just worked into something reusable.

- **Decides command or skill and says why** in one line — deliberate use means a command, recognition
  means a skill. It teaches the distinction at the moment it matters.
- **Names what it generalised and what it dropped.** A good prompt is specific and a reusable one is
  not; which specifics became parameters is the craft being taught.
- Takes an **optional argument** for what to capture, defaulting to the recent context, and
  **recommends the capture topic** from that context rather than guessing silently.
- **Clarifies through `AskUserQuestion`**, iterating over what kind of component it should become,
  what to call it, where it goes, and how it will be used later — every question carrying a
  recommendation, and multi-select unless a single choice is the correct display.
- **Shows the file content and writes nothing**, consistent with `/context-me` and `REQ-008` K03.

**`/one-pager`** — messy notes into a client-ready page.

- **States which context it used**, in a short line. This is what makes the context-file-on/off
  comparison legible: with the file absent, that line says so and the audience sees the difference
  instead of being told about it.
- **Fixed structure, stated up front**: situation, recommendation, what it costs, what happens next.
  A predictable shape is what lets the two comparison runs differ in substance rather than layout.
- **Flags what it had to invent** — anything filled in that the notes did not contain, so nobody
  sends a document containing a fabricated figure.
- Takes notes as `$ARGUMENTS` or from the conversation.

**`/client-ready`** — adapts a draft for an audience. The component that carries arguments.

- **Three arguments documented in a table**: audience, length, format, declared in `argument-hint`.
  This is why it is a command and not a skill.
- **Shows what changed and why** after the adapted draft — what moved, what was cut, what was
  softened, and which argument drove each. Otherwise the audience sees a second draft and cannot tell
  what the arguments did.
- **Refuses to change substance.** It adapts form, length and emphasis and never alters a number, a
  commitment or a recommendation. Stated as a rule with its reason: a consultant must be able to
  trust that adapting for an audience did not quietly change the advice.
- **Defaults every argument**, so a live run cannot fail on a typo and the arguments can be added one
  at a time to show their effect.

### Skills

**`load-bearing-details`** — the recognition-fired twin of `/whats-load-bearing`.

- **Names itself in its first output line.** Without this the firing is indistinguishable from
  Claude being ordinarily helpful, and half the command-versus-skill lesson is invisible.
- Its **description lists both firing and non-firing phrasings.** The trigger is an absence, which a
  description cannot match directly; naming the request shapes that should fire it — and the
  already-specific ones that must not — is the workaround.
- Asks **at most two** questions, against the command's three. It arrives uninvited, so it costs
  less than the one you chose to run, and the asymmetry gives the presenter something concrete to
  point at.
- **Defers when work is already underway**, noting the gap in a line rather than interrupting.

**`notes-to-commitments`** — fires on pasted meeting notes.

- **Never invents an owner or a date.** Missing ones are reported missing. This repository's own
  `schemas/commitment.schema.json` independently arrived at the same protected-field rule.
- **Unowned commitments are the headline output**, presented first rather than buried in a table.
  That list is the finding a consultant recognises from their own meetings.
- **Names itself in its first output line.**
- **Separates commitments from discussion**, saying which it treated as which, so the consultant can
  correct it rather than trusting a filtered list they cannot audit.

### Agents

**`objection-panel`** — three stakeholders against a recommendation, in a separate context.

- **Three named roles, one of them sympathetic.** If everyone objects the output is a wall of
  resistance; the disagreement between panellists is what teaches sequencing.
- **Returns a summary, not three transcripts.** Delegation is right here because the thinking would
  flood the main conversation — returning all of it proves the opposite of its own lesson.
- **Ranks objections by what would actually stall the work**, turning complaints into a sequencing
  decision.
- **Declares its tool posture explicitly.** It needs no write access, and saying so keeps the
  scoping-is-deliberate lesson consistent across both agents.

**`evidence-checker`** — traces every number in a draft to a source.

- **Tools: `Read`, `Grep`, `Glob` — no `Bash`.** Bash is a write channel here, so excluding it is
  what makes the read-only claim true rather than decorative.
- **Never sees how the draft was written** — the draft and nothing else, no rationale, no history.
  Independence is the whole reason this is an agent, and it is the rule this repository's own
  session-close review runs on.
- **Reports unsupported numbers first.** The ones that trace are the boring half.
- **Distinguishes wrong from unsourced** — a number contradicted by a source and a number with no
  source are different problems, and collapsing them sends the consultant chasing the wrong one.

## Build order

Four independent phases, one per component type. Nothing depends on anything else, because the
fixture work that would have created a dependency is out of scope.

1. **Commands** — `context-me`, `whats-load-bearing`, `stakeholder-read`, `capture-this`,
   `one-pager`, `client-ready`.
2. **Skills** — `load-bearing-details`, `notes-to-commitments`, both self-announcing.
3. **Prompts** — the reordered ladder and the anti-pattern gallery.
4. **Agents** — `objection-panel`, `evidence-checker`, tool lists explicit.

Testing and demonstration are the owner's, and are not phases here.
