---
schema_version: 1
id: doc-session-lifecycle
code: PLAN-008
title: Session opening and closing protocols by session type
kind: plan
status: draft
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-06'
systems: [sys-governance, sys-delivery]
depends_on: [doc-governance-protocol]
---

# Session opening and closing protocols by session type

## Context and scope

Sessions currently start cold and end by improvisation. `AGENTS.md` opens with four things every
agent must do, but they are the same four regardless of what the session is for, and there is no
close procedure that matches how the owner actually works.

Two concrete gaps prompted this plan.

**Nothing distinguishes session types.** A planning session touches only documentation and needs the
governance rules, the document-code scheme and the planning methodology. A brainstorming session
needs room to be wrong and should not be bound by the same strictness — but nothing says so, so an
agent either applies full governance to exploratory thinking or applies none of it to work that
needed it. An implementation session needs the repository's code style and testing conventions,
which a planning session should not have to carry. Today every session loads the same context and
the agent guesses the rest.

**The one closing procedure that exists does not fit.** `AGENTS.md` has a six-step "complete and
hand off" sequence, but steps 5 and 6 assume a worktree, an `origin` remote and a rebase. When this plan was written
there was no remote, and the owner works in the primary checkout. (An `origin` remote exists as of
2026-09-09; the primary-checkout half of the mismatch is unchanged and is what this plan addresses.) So the section that should govern every
session close is unusable for the sessions actually being run, and closing has instead been done
from memory each time — which is how `AGENTS.md` came to instruct agents to name session records in
a format the validator rejects.

`.claude/` currently holds only `settings.local.json`. No skills or slash commands exist, so this is
a clean slate rather than a migration.

### Owner's stated intent

Recorded here so phase 1 starts from it rather than rediscovering it:

| Session type | Needs |
|---|---|
| Planning | Planning methodology and documentation governance; no code conventions |
| Brainstorming | Deliberately looser; not bound by the strict planning rules |
| Implementation | Repository code style and best practices, plus governance for any docs it touches |
| Any type, at close | Cleanup and a record of everything the session did |

The mechanism the owner has in mind is a skill or slash command invoked at session start that loads
exactly the rules that session type needs.

### Out of scope

Changing the governance protocol itself, and any per-session-type relaxation of the rules that
protect the repository — confidentiality, the push gate and code allocation apply to every session
type including brainstorming.

## This is an investigation plan

Phase 1 is analysis and decision, not construction. The taxonomy is the hard part: too few types and
the rules stay generic, too many and nobody remembers which to invoke. The build phases follow from
what it concludes and may be renegotiated once it lands.

## Work and dependencies

### Phase 1 — define the session type taxonomy and what each type loads

Decide the set of session types, and for each one: what an agent must read, what it may skip, what
it must produce, and what it must never do. Write it as a requirements document with observable
statements.

Resolve explicitly:

- Whether brainstorming produces any governed artifact at all, or whether its output is a normal
  input to a later planning session. If nothing is recorded, the thinking is lost; if everything is
  recorded, brainstorming inherits the strictness it exists to avoid.
- How a session that changes type mid-flight behaves. A brainstorm that reaches a decision, or a
  planning session that turns into implementation, is the common case, not the exception.
- Which rules are universal. Confidentiality, code allocation and the push gate are candidates and
  should not be negotiable per type.
- Whether the type is declared by the owner at start, inferred from the phase being claimed, or
  both.

### Phase 2 — build the opening entry points

Implement one entry point per session type under `.claude/`, as skills or slash commands, each
loading only the context its type needs. Keep each one a pointer to the authoritative document
rather than a copy of its rules — the same discipline `CLAUDE.md` follows — so the entry points
cannot drift from `AGENTS.md` and the governance documents.

### Phases 3 and 5 — the checkpoint skill and the session-close command

**Revised 2026-09-06 at the owner's direction.** This was originally one closing procedure run once
at the end of a session. It is two things, because they have different invocation rules and only one
of them is the owner's to trigger.

|  | `checkpoint` | `session-close` |
|---|---|---|
| **Form** | Skill | Command |
| **Who invokes** | The owner *or* the agent, whenever either sees value | **The owner only** |
| **How often** | Repeatedly, throughout a long session | Once, at the end |
| **Depth** | Records what has happened and leaves the tree honest | Thorough, including third-party review |
| **Output** | The session record | The same session record |

**Both write the same session record.** A checkpoint creates it on first run and updates it
thereafter; `session-close` finalises the same file. There is one output product per session, not a
trail of partial ones, and the closing step is therefore never starting from a blank page.

**The agent must never decide that a session is closed.** That is the whole reason for the split.
Checkpointing is safe to do unprompted — it records, it does not conclude — so an agent noticing that
a lot has happened since the last one should just run it. Declaring a session over is a judgement
about whether the work is done, and it belongs to the owner. `session-close` is a command precisely
so that it cannot be reached by an agent deciding on its own that it is finished.

`checkpoint` is a skill rather than a command for the same reason: a skill can be invoked by either
party, where a command is the owner typing something. **`CLAUDE.md` and `AGENTS.md` must both
reference it**, or the agent-invoked half never happens — an agent that does not know the skill
exists will not choose to run it.

#### Phase 3 — the checkpoint skill

Safe and correct to run any number of times. It records verification output as actually observed,
creates or updates the session record with a correctly allocated code, updates backlog phase status
and evidence, prunes `next_up` of anything genuinely complete, regenerates the catalog, and leaves
the governance check green.

**It never claims completion that is not there.** A phase whose acceptance conditions are not all met
stays `queued` or `active` with an honest `next_action`, which is the *ordinary* path here rather
than an error branch: most checkpoints happen mid-work. This is the same requirement the original
plan buried as "what to do when a session ends incomplete", promoted to the main case.

It must work in the primary checkout, and must not assume a worktree. Repair or replace the existing "complete and
hand off" section of `AGENTS.md` so the worktree and rebase steps apply only where a worktree is in
use, rather than being presented as the universal close.

Because it runs repeatedly, **it must be idempotent in the way that matters**: a checkpoint that
changes nothing should produce no diff, so a run is cheap and the record does not accumulate noise
from being run often.

#### Phase 5 — the session-close command

Everything the checkpoint does, plus the work that is only worth doing once:

- **Third-party review.** A sub-agent reviews the session's work against what was claimed — the
  acceptance conditions actually met, the verification output actually observed, whether the record
  matches the diff. An agent reviewing its own session is the weakest possible check on it.
- **Depth the checkpoint deliberately skips.** The full narrative of what was decided and why,
  corrections made, what was left undone and why, and anything the next session needs that is not
  derivable from the code.
- **Finalisation.** The phase reaches `complete` only here, and only when acceptance genuinely holds.

The open question below — whether the close should be enforced by a check rather than a written
procedure — applies mostly to this phase, and idea `000014` (hooks) is where the enforcement
mechanism is being investigated.

### Phase 4 — dogfood and correct

Runs after phases 3 and 5, since it exercises both.

Run each session type at least once against real backlog work, and correct the protocols from what
actually happened rather than from what was intended. The test is whether a session opened cold by
an agent with no prior context produces the same quality of work as one opened with a full
conversation behind it.

## Acceptance and verification

```bash
uv run python -m src.governance
uv run python -m src.governance --catalog
```

The decisive check is behavioural, not mechanical: open a fresh session, invoke the entry point for
a given type, and confirm the agent loads the right rules, does the work within them, and closes
without being told the steps. A protocol that needs the owner to prompt each step has failed, since
avoiding exactly that is the point.

## Open questions

- Whether these entry points belong in `.claude/` (tool-specific) or in a tool-neutral location that
  `AGENTS.md` references, given `AGENTS.md` is explicitly written for any agent and not only Claude
  Code. Phase 1 should decide this before phase 2 builds anything.
- Whether the closing protocol should be enforced by a check rather than a written procedure. A
  documented step that is skipped leaves no trace; a check that fails does. This may be the
  difference between a protocol that holds and one that decays.
