---
schema_version: 1
id: doc-consultant-demo-kit
code: PLAN-024
title: Consultant demo kit build
kind: plan
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-demo-kit]
depends_on: [doc-consultant-demo-kit-requirements]
---

# Consultant demo kit build

Builds the 13 artefacts `REQ-008` specifies, in an order set by their dependencies rather than by
type. The roster reached this size through a blind adversarial triage of 23 proposed entries,
recorded on ideas `000171`-`000193`; this plan records what survived, what changed, and why.

## The running scenario

One fictional company across the whole kit: a mid-size manufacturer that has acquired three
subsidiaries and now runs three different month-end closes, consolidating onto one calendar and
cutting the close from twelve days to five. The human obstacle is the controller at the largest
subsidiary — long-tenured, well respected, reading standardisation as a judgement on their team.
Their close is the slowest **and** the most accurate, which is what makes the objection real rather
than an obstacle to be talked around.

The corpus must contain more than the presenter says aloud. Several entries only land if the model
surfaces something the presenter did not state; if the corpus holds exactly what is narrated, those
entries restate their input and the audience can say so.

## What the triage changed

Seven entries are cut, each recorded on its idea with the reason, none discarded:

| Cut | Reason |
|---|---|
| `steelman-the-objection` | Duplicates `stakeholder-read`'s lesson; the objection panel agent teaches it better with three stakeholders |
| `house-style` skill | Fires during the context-file-off run and breaks the one-pager comparison, which is beat 1's strongest moment |
| `assumption-ledger` | Capability overlap with `load-bearing-details` is near-total; a ledger's value accrues over an engagement, not in 90 seconds |
| `stakeholder-tone-check` | Fires on an unobservable send event, and depends on an entry that the cut line may remove |
| `client-ready` **as a skill** | Rebuilt as a command: arguments are a command affordance, and as a skill it could only teach its property by contradicting the definition of a skill |
| `deck-outliner` | A command wearing an agent costume; its lesson is invisible by construction |
| `long-draft-writer` | Cannot be scoped under the time budget, silently needs write access, and depends on a cut entry |

Two design changes to surviving entries:

**The prompt ladder is reordered.** As originally designed, the presenter revealed the human obstacle
at rung 4 — meaning the presenter already knew which detail was load-bearing, and the model never
demonstrated the capability the kit claims is its most important idea. The interview now runs at rung
3, before the obstacle exists in the prompt, and the obstacle enters **because the model asked for
it**. Rung 2 also splits: situation and target are two ingredients, and the ladder's discipline is
one per rung.

**Skills announce themselves.** A command shows itself being typed and an agent shows itself
spawning, but a skill firing on recognition looks exactly like Claude being helpful. Every skill in
the kit names itself in its first output line, or the skills third of the roster teaches nothing the
audience can attribute.

## Constraints this build works under

The kit is built into this repository's live `.claude/` directory, which the blind reviewers argued
against and the owner decided. Three consequences are handled rather than accepted:

1. **No kit entry writes a governed file.** The context-building command targets the kit's own
   context file. In this repository `CLAUDE.md` may not be written by an agent at all, and the
   command says plainly that in a real engagement this file is the consultant's `CLAUDE.md`.
2. **The kit is parkable.** `tools/demo_reset.py` currently parks one hardcoded skill and no agents.
   It is extended to park and restore the kit as a set, so `orient`'s command enumeration and the
   workbench agent picker are not polluted during ordinary D-System work.
3. **Two fifteen-minute runs now exist.** `REQ-006` R09 governs the D-System segment; `REQ-008`
   governs this one. Both are named explicitly wherever either is referenced.

## Build order

Fixtures first, because three entries cannot be built or rehearsed without them. The manifest and
facilitator guide come last, when the run of show is known rather than guessed.

1. **Corpus** — the fictional company's process documents, partly-sourced draft, and meeting notes.
2. **Commands** — `context-me`, `whats-load-bearing`, `stakeholder-read`, `capture-this`,
   `one-pager`, `client-ready`.
3. **Skills** — `load-bearing-details`, `notes-to-commitments`, both self-announcing.
4. **Prompts** — the reordered ladder and the anti-pattern gallery, with pinned outputs.
5. **Agents** — `objection-panel`, `evidence-checker`, tool lists explicit.
6. **Parking** — extend `tools/demo_reset.py` to cover the kit.
7. **Manifest, context file and facilitator guide** — including the cut record and the cut line.
8. **Rehearsal** — two timed runs, per-entry times recorded, fallbacks committed for every entry that
   cannot meet its timebox live.

## Open questions

- Whether the anti-pattern gallery ships four entries read from pinned output or three run live.
- Whether the paired-audience rung is two committed outputs or one live generation and one pinned.
- Whether the kit's context file lives beside the kit or at a path the presenter opens in an editor
  during beat 1.
