# HelpDesk Agent — initial dimension map

Staging, ungoverned (ADR-010). Written by the Ideation session, 2026-09-27, as the triage output
for idea 000509 (HelpDesk Agent) and idea 000510 (agent inventory). Input for the
framework planning session. Nothing here is decided.

## What the owner asked for

- An agent that answers questions about any system, process or owner-agent interaction method.
- Short, structured answers: one-to-two line statements, single-line bullets.
- The agent holds how it answers, not what it knows. The knowledge lives in data source files.
- Keywords trigger what it shares, deterministically. Structured input/output contract.
- A self-introduction command (owner suggested `/helpdeskhelp` or `/hd_help`).
- Built as a Python harness on the Claude Agent SDK.
- First priority: plan the knowledge framework, readable by the agent and by a person.

## Dimensions of repository knowledge

Each row: what the owner would ask about, where the facts already live, and what is missing.

| # | Dimension | Where the facts live now | Missing for a HelpDesk |
|---|---|---|---|
| 1 | Governance and protocols | GOV-001 to GOV-020, AGENTS.md, CLAUDE.md, `catalog.md` | a short card per protocol |
| 2 | Document system | `codes.yaml`, `schemas/document.schema.json`, GOV-005, ADR-006 | a card on codes and kinds |
| 3 | Systems | `docs/08-governance/systems.yaml` (43 systems) | a plain-language card per system |
| 4 | Planning methodology | `backlog.yaml`, `docs/09-backlog/README.md`, `batches/`, GOV-002, GOV-010, GOV-016, GOV-018, GOV-020 | one "how planning works" card |
| 5 | Idea management | `_data/ideas.jsonl`, `schemas/idea.schema.json`, `fold()` in `src/db/ideas.py`, `tools/append_idea.py`, ARCH-005, ADR-010, `tools/overview_metrics.py`, OPS-005, OPS-006, OPS-011 | cards on the writer, the event log, the fold, statuses, metrics |
| 6 | Session coordination | GOV-017, GOV-013, PROMPT-037, `/session-start`, `/session-close` | a card per role and message type |
| 7 | Agent surface | `.claude/agents/` (15), `.codex/agents/` (14), `plugins/idea-realization/agents/` (3), GOV-014, GOV-015, ~13 agents planned in backlog phases | a registry (idea 000510) |
| 8 | Commands, skills, tools | `.claude/commands/`, `.claude/skills/`, plugin skills, OPS runbooks, `agent-workflows/workflows.yaml` | a user-facing command index |
| 9 | Memory, terms, lessons | `brain/` (via `tools/load_context.py`), `GLOSSARY.md` | nothing structural |
| 10 | Decisions and history | ADRs, SESS records | a decision digest |
| 11 | Data architecture | `_data/`, `schemas/`, `sql/`, ARCH-004, ARCH-008 | nothing structural |
| 12 | Owner interaction methods | GOV-006, AGENTS.md standing rules, the Session Manager message contract | a "how you work with the agents" card |

## Proposed structure (for planning to decide)

- **Topic index**: one machine-readable file. Per topic: id, dimension, trigger keywords, source
  file paths, generator (if any), answer shape. Validated by its own JSON schema.
- **Topic cards**: one short Markdown card per topic, human-readable, in the owner's answer format.
  Generated from the sources where a generator exists; hand-written only where none does.
- **Point, do not copy.** A card cites its source files, so it stays correct when they change
  (the same rule CLAUDE.md applies to itself). A staleness check, like the one for `ideas.md` and
  `catalog.md`, would catch a card that drifted.
- **The agent** holds only its system prompt, the I/O contract and the keyword router. The pack
  holds the facts.
- **Location**: open question. Candidates: a new governed folder, or an extension of `brain/`.

## Key documents to create (codes allocated at planning time with `--next-code`)

| Kind | Purpose |
|---|---|
| REQ | HelpDesk Agent requirements: scope, answer format, I/O contract, keyword triggering |
| PLAN | The knowledge-pack framework (first priority), then the agent and its command |
| ARCH | Topic index and card structure; how cards are generated and checked for staleness |
| schema | `helpdesk-topic.schema.json` for the topic index |
| ADR | Where the pack lives; whether an agent inventory is consistent with GOV-001's "adds no ... agent registry" (that sentence is about claim identities, so this may be a clarification rather than a reversal) |
| registry + schema | The agent inventory (idea 000510): name, host (Claude, Codex, plugin, Agent SDK), status (planned, approved, active, retired), repo, source phase |
| agent + command | The HelpDesk agent definition and its intro command. Existing command names are lowercase kebab-case, so `/hd` or `/helpdesk` fits; `/hd_help` does not |

## Existing work to read before planning

- PLAN-033 / REQ-018 (retrieval and knowledge infrastructure, `phase-ret-*`).
- sys-memory-agents (planned "Librarian" role, PLAN-001).
- `docs/00-working/gemini-knowledge-retrieval-*.md` (retrieval design reports).
- `plugins/idea-realization/skills/tools/SKILL.md` (answers "which script does what" from generated docs).
- `tools/overview_inventory.py` (deterministic JSON inventory of concepts, terms and systems).
- Ideas 000494, 000495 (repo-tracking agents), 000497 (monitoring artifact), 000126 (agent surface audit).
- `src/orchestrator/dispatch.py` (the Agent SDK dispatch point, currently a stub; the SDK is not yet a dependency).
