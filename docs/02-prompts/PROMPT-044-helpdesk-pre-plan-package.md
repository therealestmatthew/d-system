---
schema_version: 1
id: doc-prompt-helpdesk-pre-plan-package
code: PROMPT-044
title: HelpDesk pre-plan package — seed the planning session for the HelpDesk knowledge framework, agent and agent inventory
kind: prompt
status: active
owner: repository-owner
created: '2026-09-29'
updated: '2026-09-29'
systems: [sys-gov-docs, sys-memory-agents, sys-retrieval]
depends_on: [doc-prompt-pack-protocol, doc-three-altitude-review-procedure, doc-retrieval-knowledge-infrastructure, doc-agent-surface-audit]
---

# HelpDesk pre-plan package — seed the planning session for the HelpDesk knowledge framework, agent and agent inventory

The pre-plan package (`GOV-008` "Prompt A") for two ideas the owner raised on 2026-09-27:

- `000509` (HelpDesk Agent) — an agent that answers the owner's questions about any system,
  process or method in this repository, from a structured, human-readable knowledge source.
- `000510` (agent inventory) — a running list of the active and approved agents built, or planned,
  with the Claude Agent SDK, here and in other repositories.

This document is the owner's input to planning. It builds nothing and plans nothing itself. Its
last section is the prompt that drafts Prompt B, the pack-factory prompt, which a separate gate
reviews before it runs (`GOV-008` stages 2 and 3).

**Tests never run in the primary checkout** (`/code/d-system`). Every `pytest`, rebuild, `ruff`,
`mypy` and governance run happens in the planning session's own worktree. `test/test_codes.py`
overwrites the tracked `catalog.md` while it runs, so a run in the primary checkout breaks every
peer's view of `dev`.

## How this package was made, and what that means for the planning session

`GOV-008` says Prompt A is planned interactively with the owner. This one was written on
2026-09-29 during an overnight run while the owner was asleep, from what the owner had already
said. So:

- **Ratified decisions** below are only what the owner said, quoted from `000509` and `000510` as
  folded by `fold()`. Nothing is inferred into a decision.
- Everything else, including the Ideation session's dimension map, is **input**, and each choice it
  implies is an **open question** below.
- The owner reviews this package at merge. Any ruling the owner adds then goes into
  *Ratified decisions* with its date before the planning session starts.

## Ratified decisions (do not re-ask these)

From `000509`, the owner's words, 2026-09-27:

1. **Role.** The agent's "role is to answer questions about the repository". "The user can ask the
   HelpDesk Agent about any system in the repository, or any process, or any method by which the
   human user interacts with the agents in this system."
2. **What it knows**, named by the owner: "all the governance and protocols", "the plan structure
   and planning methodology", and "the 'Idea Management' system by which we use a sanctioned writer,
   append only event log design, the idea fold (calculations and process), idea metrics, and
   so-on."
3. **Answer format.** "short, direct structures - no long paragraphs and unnecessary prose. Simple
   one-to-two line statements, single line bullet points, and readability are key". It responds
   "with tact and clarity" and presents "all the requested information in a structured format".
4. **Knowledge lives outside the agent.** "The HelpDesk Agent will not be the harbourer of the
   information it presents (only the manner in which it interacts wtih the user). The information
   first needs to be structured as data source, targeted files to be ingested by the agent".
5. **Deterministic triggering and a contract.** "The HelpDesk Agent would have key-words that
   trigger what it shares with you deterministically and it would have structured input/output
   contract."
6. **Implementation basis.** The agent uses "it's system prompt and python harness with Claude
   AgentsSDK".
7. **A separate self-introduction command, paired with the agent.** "a /helpdeskhelp command could
   be separate from the agent, paired with the agent to present: HelpDesk Agent self-introduction
   on /helpdeskhelp or maybe "/hd_help" - something more abbreviated and simpler to type and
   remember." The command exists; its name is open (see open questions).
8. **First priority.** "First priority is planning the framework to be ingested by the HelpDesk
   Agent (the ideas and information it has around the repo, structured and organized so it could be
   used by the agent and it would be human readable."
9. **Knowledge planning questions the owner asked**, which the plan must answer: "How do we
   structure that data? Where is it saved?"

From `000510`, the owner's words, 2026-09-27:

10. **Agent inventory.** "we need a running list of Active/Approved Agents that we create (or plan
    to create) using the AgentsSDK and iterating on select agents cross the full inventory we have
    (here and in other repos)."

## Feature inventory

The owner's specification, itemized. Letters are for reference; the order is the owner's
priority where the owner gave one (decision 8).

### A. The knowledge framework (first priority)

- A structured data source the agent ingests and a person can read (decisions 4, 8).
- Covers every system, process and owner-agent interaction method (decision 1), including the
  topics named in decision 2.
- Keyword triggers that select what is shared, deterministically (decision 5).
- An answer to "How do we structure that data? Where is it saved?" (decision 9).

### B. The HelpDesk agent

- A system prompt that holds how it answers, not what it knows (decision 4).
- A Python harness on the Claude Agent SDK (decision 6).
- A structured input/output contract (decision 5).
- Answers in the owner's format (decision 3).

### C. The self-introduction command

- Separate from the agent and paired with it; presents the agent's self-introduction (decision 7).

### D. The agent inventory (`000510`)

- A running list of active and approved agents built, or planned, with the Agent SDK (decision 10).
- Covers this repository and other repositories (decision 10).

## Input: what Ideation and triage found (not decisions)

- `docs/00-working/helpdesk-dimension-map.md` (Ideation, 2026-09-27): twelve dimensions of
  repository knowledge with where each lives and what is missing; a proposed structure (a
  schema-validated topic index plus one short card per topic, pointing to sources rather than
  copying them, with a staleness check); and a proposed document list. Its own words: "Nothing here
  is decided."
- The triage findings on `000509` and `000510` (read through `fold()`): no question-answering agent
  or agent registry exists; the Agent SDK is not a dependency; `src/orchestrator/dispatch.py` names
  the Agent SDK adapter as not built and refuses rather than guess at a binding; `GOV-001` line 194
  says the claim system "adds no scheduler, agent registry, service or lock daemon".
- Related governed work: the retrieval and knowledge infrastructure plan and requirement
  (`PLAN-033`, `REQ-018`, phases `phase-ret-*`); the agent memory system plan (`PLAN-001`, with the
  planned Librarian role in `sys-memory-agents`); the realization role contracts (`GOV-014`); the
  agent surface audit (`GOV-015`); the LangGraph orchestration decision (`ADR-018`).
- Related ideas: `000494` (an agent tracking artifacts, protocols, governance and documents),
  `000495` (an agent tracking paths and finding things), `000497` (the monitoring artifact, with
  its own investigation pack `PROMPT-042`), `000126` (audit of commands, skills and agents),
  `000436` (tracking repositories one file each).

## What the planning session must produce, in order

Through Prompt B and the `GOV-008` pipeline. Nothing is built until the owner signs off the
coordinator prompt (`GOV-008` stage 7).

1. **Prompt B**, the pack-factory prompt (`--next-code prompt`), drafted from this package. Stop
   for its adversarial review and the owner's sign-off (`GOV-008` stage 3).
2. Then, by executing Prompt B:
   1. **Requirement** (`--next-code requirement`): observable rows with verification methods for
      every item A to D, including the answer format (decision 3) as checkable rules and the
      keyword triggering (decision 5) as a deterministic, testable mapping.
   2. **Decision records** (`--next-code decision`), at least: where the knowledge framework lives;
      adding the Claude Agent SDK as a dependency and how the harness relates to
      `src/orchestrator/dispatch.py` and `ADR-018`; whether an agent inventory needs a
      clarification of `GOV-001` line 194.
   3. **Architecture** (`--next-code architecture`) for the knowledge framework: its record shape,
      how it points to sources, how it is generated or written, and how drift is caught.
   4. **Schemas** under `schemas/` for the framework's machine-readable parts and for the inventory.
   5. **Plan** (`--next-code plan`) with backlog phases sized one session each, dependency-ordered,
      the knowledge framework first (decision 8). The plan follows the plan-folder rulings the owner
      made on 2026-09-28 (see *Standing constraints*) and goes through `GOV-018`'s three-altitude
      review before the owner's G3 approval.
   6. **Agent-roster deltas**: the HelpDesk agent's own definition and any creators, validators or
      orchestrators the build needs.
   7. **Delegation pack**, **coordinator prompt** and **kick-off record**, per `GOV-008` stages 4 to 8.

## Open questions the planning session resolves with the owner (do not guess)

Ask with `AskUserQuestion`, batched, one batch at a time, at the point each matters. The owner is
often on a phone: put drafts and content in the message text, never in option previews.

**Required by `GOV-008`**

1. **Gate check-in.** Should the build session stop at gates for check-in, or push through to
   close-out? (Asked up front, always.)
2. **Deadline.** Is there a date this must meet? None is recorded.

**Knowledge framework**

3. **Where it lives** (decision 9, "Where is it saved?"): a new governed folder, an extension of
   `brain/`, or elsewhere.
4. **First coverage.** All twelve dimensions in the Ideation map in the first build, or a starting
   subset, and which.
5. **Written or generated.** Which parts are generated from their sources and which are
   hand-written; whether a drift check runs in CI like the catalog's.
6. **Human-readable form.** What the person-facing view is: the same files, a generated page, or
   both.
7. **Keywords.** Who owns the keyword list per topic, and what happens when a question matches no
   keyword or several topics.
8. **Confidential content.** Confirm the framework never covers `_private/` or the real portfolio.

**The agent and command**

9. **Command name.** The owner suggested `/helpdeskhelp` or `/hd_help` and asked for "something
   more abbreviated and simpler to type and remember". Existing commands in `.claude/commands/` are
   lowercase kebab-case, so `/hd_help` does not fit that convention; candidates are `/hd` and
   `/helpdesk`.
10. **Where the agent runs.** A standalone Python command, a workbench panel, an API route, a Claude
    Code agent definition as well as the SDK harness, or a combination.
11. **Model and credentials.** Which model the harness uses by default, and how its API key is
    supplied without being written into a tracked file.
12. **Freshness.** Does the agent answer only from the framework, or may it also read the live
    source file a topic points to?

**The agent inventory (`000510`)**

13. **What it lists.** Only agents built or planned on the Agent SDK, or every agent (`.claude/agents/`,
    `.codex/agents/`, the plugin's agents) with the SDK ones marked. The owner's sentence names
    the SDK and also "the full inventory we have".
14. **"Iterating on select agents".** What the inventory must support for that: a status field, a
    revision history, links to the phases that change an agent, or something else.
15. **Other repositories.** Which ones, and how their agents are discovered (`000436`, and the
    planned cross-repo awareness phase, are related).
16. **One plan or two.** Is the inventory part of the HelpDesk plan, or its own plan the HelpDesk
    reads from?

**Overlap**

17. **Existing work.** Does this plan absorb, depend on, or stay separate from the retrieval plan
    (`PLAN-033`), the planned Librarian role (`PLAN-001`), and ideas `000494`, `000495` and `000497`?

## Standing constraints

- `AGENTS.md` governs. Plan before code. Every governed document takes its code from
  `uv run python -m src.governance --next-code <kind>`.
- **Tests never run in the primary checkout.** The planning session works in its own worktree,
  and every document it produces says the same for the sessions it plans.
- The idea log is written only through the sanctioned writer. Under the multi-session coordination
  contract (`GOV-017`), a session sends new ideas to the Ideation session rather than recording them.
- `AGENTS.md` and `CLAUDE.md` are never edited without the owner's explicit approval for that change.
- Integration into `dev` is the owner's call each time; merges go through the Session Manager's
  READY and GRANTED exchange.
- Never write a confidential identifier into a tracked file; run
  `tools/check_no_private_content.py` with changes staged.
- Every new plan goes through `GOV-018`'s three-altitude review, dispatched on an adversary agent
  type, never `general-purpose`.
- **The owner's plan-folder rulings of 2026-09-28** (`docs/00-working/cloud-prompts/owner-rulings-2026-09-28.md`,
  from `docs/00-working/plan-anatomy/proposed-standard.md`) apply to new plans: every new plan is a
  folder with `PLAN-NNN-overview.md` as its entry point; decisions are a one-line ruling in the plan
  with the record in an uncoded `decisions.md` member; one-time prompts go in a `prompts/` member
  folder; tracked evidence goes in an `evidence/` member. Check `dev` for how far that standard has
  been adopted into governance before relying on it, and follow the governed version where the two
  differ.
- `GOV-008`'s cost policy: Sonnet for judgment work, Haiku for mechanical gates, Opus never
  pre-assigned.
- Adding a dependency to `pyproject.toml` is a decision the owner approves (decision record above).

## Deadline context

None is recorded. Open question 2 asks.

---

## The prompt

> You are the planner for the HelpDesk knowledge framework, agent and agent inventory (ideas
> `000509` and `000510`). Read `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`,
> then `docs/08-governance/GOV-008-prompt-pack-protocol.md`, then this document
> (`docs/02-prompts/PROMPT-044-helpdesk-pre-plan-package.md`) in full. It carries the owner's
> ratified decisions, the feature inventory, and the open questions. Read ideas only through
> `fold()` in `src/db/ideas.py`. Work in your own worktree on an `agent/<slug>` branch; tests never
> run in the primary checkout. Your job in this session is `GOV-008` stage 2: draft **Prompt B**,
> the pack-factory prompt, as a governed prompt document (`--next-code prompt`), carrying this
> package's ratified decisions and open questions forward and naming, in order, the artifacts its
> "What the planning session must produce" section lists. Resolve with the owner, through
> AskUserQuestion, only the open questions whose answers change what Prompt B says, one batch at a
> time; leave the rest in Prompt B's open-questions protocol. Do not re-ask a ratified decision. Do
> not write the requirement, plan or any code, and do not run Prompt B. Stop when Prompt B exists,
> governance exits 0, an adversary agent type (never `general-purpose`) has reviewed it and every
> finding is fixed or explicitly accepted, and the owner has the review summary for sign-off.
