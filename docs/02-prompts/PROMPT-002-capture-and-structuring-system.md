---
schema_version: 1
id: doc-capture-system-prompt
code: PROMPT-002
title: Define the capture and structuring system
kind: prompt
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-portfolio, sys-contracts, sys-brain]
depends_on: [doc-governance-protocol]
---

# Define the capture and structuring system

## How to use this

Open a fresh session in this repository and say:

> Read `docs/02-prompts/PROMPT-002-capture-and-structuring-system.md` and follow it.

The session's job is to **define** this system with me, not to build it. It ends with governed
documents and backlog phases, not with code.

## Repository context

This repository is a personal productivity and consulting management system. Source data is
git-tracked JSON under `_data/`, projected into DuckDB on demand by `tools/rebuild_db.py`.
Documentation is governed: every document carries a code, a lifecycle status and validated front
matter, checked by `uv run python -m src.governance`. Read `AGENTS.md`,
`docs/08-governance/GOV-001-protocol.md` and `docs/08-governance/GOV-005-document-codes.md` before
writing anything.

Current real state, not aspiration:

| Entity | Records | Notes |
|---|---|---|
| projects | 33 | Populated, with tags, status, category, type, cadence |
| tags | 28 | Six categories: client, context, domain, methodology, platform, tech |
| people | **0** | Loader and schema exist; no records |
| commitments | **0** | Loader and schema exist; no records |
| tasks | **0** | Embedded in commitments; none exist |
| brain memories | 7 | Markdown with typed YAML front matter under `brain/` |

Existing entity shapes — treat these as the current model, not as settled:

- `project`: id, name, status, category, type, description, tags, stakeholders, started,
  target_date, last_reviewed, commitment_cadence, notes
- `commitment`: id, project_id, description, promised_to, due_date, status, priority, created,
  completed, notes, tasks[]
- `person`: id, name, role, organization, email, projects, notes
- `tag`: id, label, category, description, related, deprecated

Existing tooling: `tools/rebuild_db.py` (drop and recreate the projection),
`tools/load_context.py` (read-only memory retrieval by keyword, project, type, tags).

## The gap this session must close

The repository can *store* people, commitments and tasks. Nothing defines **how information gets
in**. There is no capture workflow, no intake format, no rule for how raw thought becomes a
structured record, and no phase anywhere in the 59-item backlog that covers authoring real people or
commitment records. Every one of the 53 remaining phases assumes this data arrives from somewhere
that was never specified.

This matters concretely. Of the six planned SQL signals, the Accountability Ledger, Cognitive Load
Estimator and Commitment Velocity all read commitments, as do all four synthesis workflows —
fourteen backlog phases that would currently be built and verified against empty tables.

The owner is the sole contributor. The system's value therefore depends almost entirely on whether
capture is low-friction enough that it actually happens, and on how much organizing work the agents
absorb rather than hand back.

## Your task

Define the capture and structuring system as governed documents. Specifically:

1. **Interview the owner first.** Do not assume answers to the questions below. Ask them in small
   batches, take the answers as decisions, and record them. Where the owner has no strong view,
   recommend a default and say why.
2. **Write the requirements** as a `requirement` document: observable statements, each with a
   verification method. This is the contract.
3. **Write the plan** as a `plan` document: the phases, in order, each sized to one session.
4. **Add backlog phases** to `docs/09-backlog/backlog.yaml`. This is mandatory, not optional — an
   open plan with no phases fails the governance check.
5. **Record any non-obvious design choice as an ADR.**

Allocate every code with `uv run python -m src.governance --next-code <kind>` and name each file
`<code>-<slug>.md`. Never pick a number by reading the directory.

## Questions to resolve with the owner

Ask these. They are ordered so that early answers constrain later ones.

### 1. What comes back out

Start here, because what the system must *return* determines what must be captured. Everything else
is downstream of this answer.

- At what moments do you want this system to speak to you — morning, end of day, weekly review,
  before a client call, when something goes stale?
- What question do you most often fail to answer from memory today? ("What did I promise whom?"
  "What has gone quiet?" "What did we decide and why?")
- What would you have to see for this to have changed a decision in the last month?
- What does a good week look like, expressed as something countable?

### 2. How raw information arrives

- In what form does the information exist when you first have it — a thought between meetings, a
  call you just finished, an email thread, a Slack message, a notebook page, a voice memo?
- What is your realistic friction budget for capture? Seconds, or is a five-minute end-of-day dump
  more honest?
- Do you want to write into a file, talk to an agent conversationally, drop notes in an inbox
  directory, or something else? Would you actually do it?
- Batch or continuous? Both, with different paths?

### 3. Where the agent's judgment starts and stops

This is the core of the design. The owner writes unstructured; the agent structures. Locate the
boundary precisely.

- When you write "call Dave about the model before Thursday," should the agent decide by itself
  whether that is a commitment, a task under an existing commitment, or a note?
- When it cannot tell, what should happen: guess and flag, queue it for your review, or ask you
  immediately?
- How much should it infer — project association, priority, due date from "before Thursday,"
  stakeholder identity from a first name?
- What must it never invent? Name these explicitly; they become validation rules.

### 4. Review and trust

- `_data/` is the git-tracked source of truth. Should an agent write there directly, or into a
  staging area you approve first?
- If staging: what does approval look like, and how do you review a batch without re-reading
  everything?
- How do you correct a mistake the agent made three weeks ago and only noticed now?
- Should the raw capture be kept alongside the structured record, so a bad interpretation can be
  re-derived rather than lost?

### 5. Identity and tagging

- "Dave" appears in a note. How does the agent decide whether that is an existing person, a new
  person, or too ambiguous to record?
- The tag taxonomy has 28 tags in six categories. When should the agent propose a new tag rather
  than force-fit an existing one, and who approves it?
- Do people need to be real records, or is a name string enough until a person matters?

### 6. Whether the entity model is right

Challenge the existing shapes rather than assuming them.

- Does `commitment` cover what you actually track, or do you also need meetings, interactions,
  decisions, waiting-on items, someday/maybe, and open questions?
- Is a task always under a commitment, or do standalone tasks exist?
- Do you need any notion of energy, focus, context or time-of-day, given "cognitive load" is already
  a planned signal?
- Does `project.commitment_cadence` mean anything if no commitments exist yet?

### 7. Confidentiality

- The tag taxonomy includes a client tag (`client-a`). What client information may live in a
  git-tracked file, and what belongs in gitignored `_private/`?
- Should capture default to private and be promoted deliberately, or the reverse?

## Design tensions to resolve explicitly

Name these in the ADR rather than letting them resolve by accident.

- **Friction versus fidelity.** The richest capture format is the one least likely to be used. The
  system is worth nothing if the owner stops feeding it in week three.
- **Agent autonomy versus trust.** An agent that asks about everything moves the load back onto the
  owner. An agent that guesses silently corrupts the record in ways discovered late.
- **Structure versus premature commitment.** Structuring early makes data queryable; it also forces
  a shape onto something not yet understood. Consider keeping raw text permanently.
- **This repository's own rule.** `docs/08-governance/GOV-001-protocol.md` forbids duplicate
  bookkeeping. A capture system that requires maintaining the same fact in two places violates the
  principle the repository is built on.

## Constraints

- Follow the governance protocol. Run `uv run python -m src.governance` before finishing; it must
  exit 0. Regenerate `docs/08-governance/catalog.md` with `--catalog`.
- Do not edit `data/` directly; it is derived and gitignored. Change `_data/` and rebuild.
- Do not read or write `_private/` unless the owner directs it.
- Schema changes go to `schemas/` first, then `sql/`, then the loader, then Pydantic models.
- Any new capability that can change independently needs an entry in
  `docs/08-governance/systems.yaml`.
- Do not write implementation code in this session. If the owner asks for a prototype to make a
  choice concrete, keep it a throwaway and say so.

## Definition of done

- The owner's answers are recorded as decisions, with the reasoning, in a governed document.
- A requirement document states observable requirements with verification methods.
- A plan document describes phases in dependency order, each sized to one session.
- Backlog phases exist for every phase of that plan, and the governance check passes.
- The plan states explicitly how the resulting data unblocks the `phase-sig-*` and `phase-syn-*`
  tracks, which currently depend on commitments that do not exist.
- Anything the owner deferred is written down as an open question with the condition for revisiting
  it — not silently dropped.
