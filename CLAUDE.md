# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Writing Style
Mannered prose substitute metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.

## Read AGENTS.md first

**→ [AGENTS.md](AGENTS.md) is the working agreement and governs everything you do here.**

It carries the rules this file deliberately does not repeat: how to pick up work from the backlog
queue, the requirement-and-plan-before-code expectation, document code allocation, the governance
check, the concurrent-agent protocol, and the standing rule that **no agent pushes without asking**
and **never writes a confidential identifier into a tracked file**.

This file is orientation only — what the project is and where things live. If it ever contradicts
AGENTS.md, AGENTS.md wins.

## How to report to the owner

@docs/08-governance/GOV-006-conversation-guidelines.md

Imported rather than linked because it governs the first sentence of a session, not a step taken
partway through one. A link would be read after several messages had already broken it. The import
is a pointer — the document above is the only copy — and it is the reason that document must stay
short.

### What belongs in this file

Keep it to three things:

1. **Reference pointers** to the authoritative source — AGENTS.md, the governance protocol, a
   specific document. A pointer stays correct when the target changes; a copy does not.
2. **Explicit instructions** an agent must act on before it can do anything else, like reading
   AGENTS.md first.
3. **Mission-critical facts worth duplicating** despite the drift risk. The bar is that being
   unaware of it for one turn causes irreversible harm. The publishing rule above clears it: this
   repository now has a remote, and an agent that pushes without asking cannot take it back.
   Convenience never clears it.

   The no-remote rule that stood here until 2026-09-09 is the cautionary case for this whole
   section. It was correct when written and false the moment `phase-priv-05` pushed, and it sat
   stale in two files until someone went looking. Duplicating a fact means owning its drift.

Everything else — conventions, commands, workflow, lifecycle rules — belongs in AGENTS.md or under
`docs/08-governance/`, and is referenced from here rather than restated. When this file starts
answering "how do I work here" instead of "what is this and where is it", the content has drifted
into the wrong file. Prune it back.

## Verify before claiming ignorance

**If a tool can settle it, use the tool before saying you cannot.** "Not in my training data" and
"cannot be determined" are different claims, and only the first is ever true of a searchable fact.
Asserting the second when a web search was available is a false statement about your own capability,
not a limitation.

Triggers: any named model, product, library or version; anything dated after the knowledge cutoff;
any "is X real / what is X" question. Search first, answer second. Offering to search *instead of
searching* is the same error with better manners.

## When you get something wrong

1. **Say plainly that it is a correction**, in one sentence, then move on. Do not re-litigate and do
   not soften a wrong call into a partly-right one. `GOV-006` already requires this; it is repeated
   here because it governs a first-response reflex, not a step reached partway through a task.
2. **Fix the claim** and continue the work. No ruminating, no tallying past errors.
3. **Record it only if it could recur.** A situational slip needs no record. A slip caused by a
   standing habit gets an entry in `brain/procedures/` — model-agnostic by design, so the correction
   reaches whichever model works here next, not just this one.

The owner's standing requirement: **they must not have to correct the same thing twice.** A
correction that produces no durable change did not land.

## Project Purpose

Personal consulting management system for tracking people, projects, commitments, and tasks — reducing mental overhead by centralizing work responsibilities. Doubles as a platform for HTML generation, reporting, and agentic workflow triggering.

## Data Architecture

### Source of truth: `_data/` (tracked) and `_private/portfolio/` (real records, gitignored)

```
_data/
  tags.json              ← all tag definitions (reference list) — always here
  projects/               ← fictional example set (tracked)
  commitments/            ← fictional example set (tracked); tasks are separate files, not embedded
  people/                 ← fictional example set (tracked)
```

The owner's real projects/people/commitments/tasks live at `_private/portfolio/` instead, read when
`D_SYSTEM_DATA_ROOT=_private/portfolio` is set — see [ADR-009](docs/04-decisions/ADR-009-structure-content-boundary.md)
and `GOV-001`'s "The data root" section for the full rule.

### DuckDB: derived query layer (gitignored)

`data/d_system.duckdb` is rebuilt on demand from `_data/` JSON by `tools/rebuild_db.py`. Never edit the DB directly — edit the JSON files, then rebuild.

### Schema files: `schemas/` (JSON Schema for validation)

`project.schema.json`, `commitment.schema.json`, `person.schema.json`, `tag.schema.json`

### DDL: `sql/001_schema.sql`

Tables: `projects`, `people`, `project_people`, `tags`, `project_tags`, `commitments`, `tasks`

Key relationships:
- Tasks are embedded in commitment JSON but get their own `tasks` table in DuckDB (unpacked by rebuild)
- `tags` field on project JSON is denormalized into both the `projects.tags` array column and the `project_tags` junction table
- `project_people` is populated from the `projects` array inside each person's JSON

## Backend Layout

```
src/
  main.py          # FastAPI app, CORS, router registration
  api/
    __init__.py    # APIRouter at /api/v1 — register route modules here
    routes/        # one file per domain (projects.py, commitments.py, etc.)
  db/
    connection.py  # get_db() context manager — yields a DuckDB connection
  models/          # Pydantic models (request/response shapes)
```

- `get_db()` opens a fresh connection per call; DuckDB is file-based, no pool needed at this scale.
- All routes live under `/api/v1`.

## Frontend Layout

```
ts/
  src/
    main.tsx        # React root
    App.tsx         # root component
  vite.config.ts    # proxies /api → :8000, no CORS issues in dev
```

## HTML Generation Framework

Source data (`_data/`) → templates (`templates/html/`, `templates/styles/`) → generation scripts (`tools/` or `src/`) → React UI (`ts/`) + FastAPI (`src/`). The UI supports:
- Triggering agentic workflows
- Viewing/managing source data and transformations
- Generating reports, charts, summaries
- Composable multi-page frameworks

## Directory Reference

| Directory | Purpose |
|---|---|
| `src/` | FastAPI application |
| `ts/` | React/TypeScript frontend |
| `js/` | Plain JS utilities (browser automation, one-off scripts) |
| `schemas/` | JSON Schema definitions for all data entities |
| `sql/` | DuckDB DDL migrations |
| `_data/` | Tracked fictional example set + shared taxonomy (`tags.json`). Real portfolio content is not here — see `_private/` |
| `templates/html/` | HTML page and component templates |
| `templates/styles/` | CSS / style definitions for template families |
| `test/` | pytest test suite |
| `tools/` | CLI and helper scripts (rebuild_db.py, etc.) |
| `docs/00-working/` | Ungoverned staging for parked ideas ([ADR-010](docs/04-decisions/ADR-010-idea-staging.md)) |
| `docs/01-plans/` | Implementation plans (`PLAN-NNN-topic.md`) |
| `docs/02-prompts/` | AI prompt templates |
| `docs/03-sessions/` | Session logs |
| `docs/04-decisions/` | Architecture Decision Records (`ADR-NNN-topic.md`) |
| `docs/05-memories/` | Persistent cross-session context |
| `docs/06-requirements/` | Feature requirements |
| `docs/07-architecture/` | Architecture diagrams and docs |
| `.claude/skills/checkpoint/` | Mid-session progress recording skill — see `SKILL.md` there, invoked per `AGENTS.md`'s Session backlog section |
| `.claude/commands/session-close.md` | Owner-only `/session-close` command — finalizes the session record and is the only place a phase reaches `status: complete` |
| `_working/` | Ephemeral working plans and task detail. Gitignored and ungoverned by design; never deleted without the owner's explicit approval ([PLAN-015](docs/01-plans/PLAN-015-ephemeral-working-plans.md)) |
| `_tmpagent/` | Files agents in sibling worktrees must read. Tracked, ungoverned, read-only once active; claimed and released through `_tmpagent/claims.jsonl` ([contract](_tmpagent/AGENTS.md)) |
| `_public/` | Shareable outputs |
| `_private/` | Gitignored — credentials, raw dumps, personal notes, and `portfolio/`: the owner's real projects/people/commitments/tasks (ADR-009) |
