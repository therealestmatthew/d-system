# D-System

A personal system for tracking people, projects, commitments, and tasks — reducing mental overhead by centralizing work responsibilities. It also serves as a platform for HTML generation, reporting, and agentic workflow triggering. 

**Model-Agnostic Design:** This system is built to be worked on interchangeably by Claude (Anthropic), GPT-4o (OpenAI), and Gemini (Google), and the repository owner.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.14.5, FastAPI, DuckDB (file-based), Pydantic v2
- **Frontend**: TypeScript, React 18, Vite
- **Package Managers**: uv (Python), npm (Node)

---

## 🚨 Critical Data Architecture Rule

**Source of truth = JSON/Markdown files. DuckDB is derived and gitignored.** Per
[ADR-009](docs/04-decisions/ADR-009-structure-content-boundary.md), only some of those files are
git-tracked: real portfolio content lives outside git, at `_private/portfolio/`.

- `_data/projects/*.json` ← fictional example set, tracked. Real projects go to
  `_private/portfolio/projects/*.json` instead (gitignored).
- `_data/commitments/*.json` ← same split. Tasks are separate records in `_data/tasks/`, not embedded.
- `_data/people/*.json` ← same split.
- `_data/tags.json` ← tag definitions — always tracked; shared taxonomy, not portfolio content.
- `brain/**/*.md` ← shared memory entries (Markdown + YAML frontmatter), always tracked.
- `data/d_system.duckdb` ← gitignored; query layer only, **never write directly**.

Set `D_SYSTEM_DATA_ROOT=_private/portfolio` to point tooling at the real records; leave it unset to
work against the tracked fictional set (the default, and what a fresh clone gets).

> **RULE**: Always edit JSON or Markdown files, then run `uv run python tools/rebuild_db.py`. Never `INSERT` directly into DuckDB — the next rebuild will overwrite your changes.

---

## 💻 Key Commands

### Setup & Dependencies
```bash
uv venv                          # create .venv (if not exists)
uv sync --extra dev              # install all deps including dev
cd ts && npm install             # frontend first-time setup
```

### Running the App
```bash
uv run uvicorn src.main:app --reload   # Backend API on :8000
cd ts && npm run dev                   # Frontend UI on :5173 (proxies /api → :8000)
```

### Data Management
```bash
uv run python tools/rebuild_db.py      # Sync source files (_data/ + brain/) → DuckDB
```

### AI Context Retrieval (Load Memory for Sessions)
```bash
uv run python tools/load_context.py --query "topic"
uv run python tools/load_context.py --project project-id
uv run python tools/load_context.py --type procedure
uv run python tools/load_context.py --tags python,frameworks
uv run python tools/load_context.py --all
```

### Testing & Quality
```bash
uv run pytest                                      # Run all tests
uv run pytest test/path/to/test_file.py::test_name # Run specific test
uv run ruff check src/ test/                       # Linting
uv run mypy src/                                   # Type-checking
cd ts && npm run build                             # Frontend build
```

---

## 🧠 Shared Brain / Memory System

`brain/` is a model-agnostic wiki. Any AI (Claude, GPT-4o, Gemini) or human can read and write entries. Each entry is a Markdown file with YAML frontmatter conforming to `schemas/memory.schema.json`.

**Key frontmatter fields:**
- `id`: `mem-<type>-<slug>` (permanent identifier)
- `title`: Human-readable name
- `type`: `concept` | `entity` | `procedure` | `episode` | `decision`
- `tags`: Array of IDs from `_data/tags.json`
- `source_model`: e.g., `anthropic/claude-sonnet-4-6`, `openai/gpt-4o`, `google/gemini-2.0-flash`, `human`
- `confidence`: `high` | `medium` | `low` | `uncertain`
- `scope`: `global` | `project` | `session`

*Current memory count: 7 entries spanning concepts, entities, procedures, and decisions.*

---

## 📂 Directory Structure

```text
src/              # FastAPI application (main.py, api/routes, db, models)
ts/               # React/TypeScript frontend (Vite)
js/               # Plain JavaScript utilities (browser automation, one-offs)
schemas/          # JSON Schema definitions for all data entities
sql/              # DuckDB DDL (001_schema.sql)
_data/            # Source-of-truth JSON files
brain/            # Shared model-agnostic memory (wiki / Open Brain)
templates/        # HTML page templates and CSS/style definitions
tools/            # CLI scripts (rebuild_db.py, load_context.py)
test/             # pytest test suite
docs/             # Plans, prompts, sessions, ADRs, requirements, architecture
_working/         # Scratchpad — gitignored, local only, never pruned without approval
_tmpagent/        # Shared agent files — tracked, claimed and released via claims.jsonl
_public/          # Shareable outputs
_private/         # Gitignored — credentials, raw dumps, personal notes
```

---

## 📊 Current Inventory

### Projects (34 Total)
Counts describe the owner's real portfolio, which lives at `_private/portfolio/projects/*.json`
(gitignored) since [ADR-009](docs/04-decisions/ADR-009-structure-content-boundary.md). Each project
is a JSON file with a permanent `id`, `name`, `status`, `category`, `type`, `tags`, `review_cadence`,
and `last_reviewed` date. The tracked `_data/projects/*.json` instead holds a small fictional example
set exercising every field.
- **Work**: 8 active, 2 inactive
- **System**: 12 active
- **Personal**: 8 active
- **Learning**: 3 active, 1 inactive

### Tag System (28 Tags)
Tags are the cross-cutting classification axis, stored in `_data/tags.json`. They span 6 categories: `client`, `platform`, `tech`, `domain`, `methodology`, and `context`. 
*Note: Tag IDs are permanent. Retire by setting `deprecated: true`, never by deleting.*

### DuckDB Tables
- `projects` (33 rows)
- `people` (0 rows)
- `tags` (28 rows)
- `project_tags` (junction)
- `project_people` (junction)
- `commitments` (0 rows)
- `tasks` (embedded in commitments)
- `memories` (7 rows)

---

## 🛠️ Code Generation Convention

When adding a new domain entity, execute in this exact order (see `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md`):

1. Define schema in `schemas/<entity>.schema.json`
2. Add DDL to `sql/001_schema.sql`
3. Add loader to `tools/rebuild_db.py`
4. Create `_data/<entity>/` directory
5. Add Pydantic model in `src/models/`
6. Add FastAPI route in `src/api/routes/`, register in `src/api/__init__.py`
7. Run `uv run python tools/rebuild_db.py`
8. Write tests in `test/`
9. Add React components in `ts/src/components/` (if UI in scope)

---

## 🚀 Planned But Not Yet Built

1. **Agent Memory System** (`docs/01-plans/PLAN-001-agent-memory-system.md`)
   - **Vault Scribe**: Sole writer to `brain/` (memory custodian).
   - **Chronicle**: Reads session transcripts, extracts candidates, hands to Vault Scribe.
   - **The Librarian**: Retrieval router (exact → tag → keyword → semantic/vector → agentic RAG).
2. **Mini-Systems Architecture** (`docs/01-plans/PLAN-002-mini-systems-proposal.md`)
   - **Tier 2 (SQL views)**: Project Health Signal, Cognitive Load Estimator, Stale Radar, Accountability Ledger, Commitment Velocity Tracker, Tag Cluster Analyzer.
   - **Tier 3 (AI-assisted)**: Context Pack, Session Briefing, Weekly Review, Portfolio Digest.
