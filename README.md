# D-System

A personal system for tracking people, projects, commitments, and tasks — reducing mental overhead by centralizing work responsibilities. It also serves as a platform for HTML generation, reporting, and agentic workflow triggering.

**Model-Agnostic Design:** This system is built to be worked on interchangeably by Claude (Anthropic), GPT-4o (OpenAI), and Gemini (Google), and the repository owner.

---

## 📋 Working Agreement

**[AGENTS.md](AGENTS.md) governs all work in this repository** — read it before changing anything.
`CLAUDE.md` and `GEMINI.md` are orientation only and defer to it.

- [GOV-007](docs/08-governance/GOV-007-repo-orientation.md) — repository orientation
- [docs/09-backlog/](docs/09-backlog/README.md) — the work queue; phases are claimed from here
- [catalog.md](docs/08-governance/catalog.md) — index of every governed document
- `.claude/` — skills, agents and slash commands

---

## 🏗️ Tech Stack

- **Backend**: Python ≥3.12 (3.14.5 in the current venv), FastAPI, DuckDB (file-based), Pydantic v2
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
- `_data/ideas.jsonl` ← append-only idea event log, always tracked. Written only by
  `tools/append_idea.py`; never edited by hand.
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
uv run python tools/rebuild_db.py      # Sync source files (_data/, ideas.jsonl, brain/) → DuckDB
```

### AI Context Retrieval (Load Memory for Sessions)
```bash
uv run python tools/load_context.py --query "topic"
uv run python tools/load_context.py --project project-id
uv run python tools/load_context.py --type procedure
uv run python tools/load_context.py --tags python,frameworks
uv run python tools/load_context.py --system sys-governance
uv run python tools/load_context.py --limit 25          # default 10
uv run python tools/load_context.py --all               # ignores other filters
```

Full options in [OPS-003](docs/08-governance/OPS-003-load-context.md). Every tool under `tools/`
is paired with an `OPS-*` document; the [catalog](docs/08-governance/catalog.md) lists them all.

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

`brain/index.md` lists the current entries. Adding one is a documented procedure —
`brain/procedures/add-brain-memory.md`.

---

## 📂 Directory Structure

```text
src/              # FastAPI application (main.py, api/routes, db, models, governance)
ts/               # React/TypeScript frontend (Vite)
js/               # Plain JavaScript utilities (browser automation, one-offs)
schemas/          # JSON Schema definitions for all data entities
sql/              # DuckDB DDL (001_schema.sql) and views (003_capture_views.sql)
_data/            # Tracked fictional example set + shared taxonomy and ideas.jsonl
brain/            # Shared model-agnostic memory (wiki / Open Brain)
templates/        # HTML page templates and CSS/style definitions
tools/            # CLI scripts — each paired with an OPS-* document
test/             # pytest test suite
docs/             # Plans, prompts, sessions, ADRs, requirements, governance, backlog
research/         # Reference material and review packs — tracked, ungoverned
.claude/          # Skills, agents and slash commands
data/             # Gitignored — the derived DuckDB file
_working/         # Scratchpad — gitignored, local only, never pruned without approval
_tmpagent/        # Shared agent files — tracked, claimed and released via claims.jsonl
_public/          # Shareable outputs (generated overview and HTML pages)
_private/         # Gitignored — credentials, raw dumps, notes, and portfolio/ (real records)
```

---

## 📊 Inventory

Counts are generated, never written down here — they describe whichever data root is in play, and a
hand-maintained number goes stale the moment a record is added:

```bash
uv run python tools/generate_overview.py   # → _public/overview/index.html
```

The tables and views the rebuild produces are defined in `sql/001_schema.sql` and
`sql/003_capture_views.sql`; read those rather than a list here.

Tags are the cross-cutting classification axis, stored in `_data/tags.json` and spanning six
categories: `client`, `platform`, `tech`, `domain`, `methodology`, and `context`.
*Note: Tag IDs are permanent. Retire by setting `deprecated: true`, never by deleting.*

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

## 🚀 What's Built and What Isn't

Design plans live in [docs/01-plans/](docs/01-plans/README.md); a plan being written is not evidence
it is implemented. Two records answer "is this built yet":

- [docs/09-backlog/](docs/09-backlog/README.md) — the phase queue and each phase's status. This is
  the only place a phase is marked complete.
- [systems.yaml](docs/08-governance/systems.yaml) — every system with a `status` of `implemented`,
  `scaffold` or `planned`, and the paths that make up each one.
