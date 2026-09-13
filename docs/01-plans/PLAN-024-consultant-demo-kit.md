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

Builds the 16 artefacts `REQ-008` specifies: 6 commands, 2 skills, 6 prompts, 2 agents. Nothing
else. The roster reached this size through a blind adversarial triage of 23 proposed entries,
recorded on ideas `000171`-`000193`; this plan records what survived, what changed, and why.

## The running scenario

One fictional company across the whole kit: a mid-size manufacturer that has acquired three
subsidiaries and now runs three different month-end closes, consolidating onto one calendar and
cutting the close from twelve days to five. The human obstacle is the controller at the largest
subsidiary — long-tenured, well respected, reading standardisation as a judgement on their team.
Their close is the slowest **and** the most accurate, which is what makes the objection real rather
than an obstacle to be talked around.

The scenario is the setting each artefact is written against. It is not a deliverable: no corpus,
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

- **No kit artefact writes any file here.** This covers `context-me` and every other entry.
- **Kit entries will appear in `orient`'s command enumeration and the workbench agent picker** during
  ordinary D-System work. No parking mechanism is in scope. `REQ-008` records this as an accepted
  consequence, not an open defect.
- **Two fifteen-minute runs now exist.** `REQ-006` R09 governs the D-System segment; this kit is the
  other one. Both are named explicitly wherever either is referenced.

## Build order

Four independent phases, one per artefact type. Nothing depends on anything else, because the
fixture work that would have created a dependency is out of scope.

1. **Commands** — `context-me`, `whats-load-bearing`, `stakeholder-read`, `capture-this`,
   `one-pager`, `client-ready`.
2. **Skills** — `load-bearing-details`, `notes-to-commitments`, both self-announcing.
3. **Prompts** — the reordered ladder and the anti-pattern gallery.
4. **Agents** — `objection-panel`, `evidence-checker`, tool lists explicit.

Testing and demonstration are the owner's, and are not phases here.
