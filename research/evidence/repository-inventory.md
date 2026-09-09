# Repository inventory and review boundary

Reviewed 2026-09-09. The root was inventoried using `ls -la`, `git ls-files` and `rg`; executable source, schemas, SQL, prompt workflows, tests and configuration were inspected. Plans and historical records were used as intent and trace evidence, not assumed capabilities. No literature search was performed.

- `src/`: FastAPI shell, db connection/fold/source validation, raw capture, governance. `src/models/__init__.py` is empty; no ORM or domain Pydantic models.
- `tools/`: idea writer, capture CLI, database rebuild, context loader, generated idea/glossary/catalog/tool-doc support and confidentiality checker.
- `sql/`: only `001_schema.sql` and `003_capture_views.sql`; both are replayed during full rebuild. No migration runner/version table found. Local Git history records earlier edits; no missing `002` file is presumed to exist.
- `schemas/`: domain JSON Schema, idea events, memory, raw/staged capture/evidence, documents, systems, codes, backlog and idea queue.
- `ts/`: React/Vite scaffold; `js/` is a README. No alternate backend/frontend/package/database directory or implementation was found.
- `test/`: executable tests and synthetic fixtures, not `tests/`; `test/conftest.py` supplies TestClient.
- `.claude/`: triage agent, idea/triage/backlog/close commands and checkpoint skill. `.agents/` contains the untracked checkpoint skill; no active work was delegated or closed. These files were read as review evidence, not invoked.
- `docs/02-prompts/`: governed generation/design/review prompts; these are not an application LLM runtime. `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` orient/control repository work.
- `brain/`: model-independent Markdown memory and current terminology. `docs/07-architecture/`: current/draft architecture. `docs/06-requirements/`, `docs/04-decisions/`, `docs/01-plans/`, `docs/03-sessions/`, `docs/09-backlog/`: implementation trace material.
- `pyproject.toml`, `uv.lock`, `ts/package*.json`, TypeScript/Vite config, `.github/workflows/ci.yaml`, `.gitignore`: dependency/build/CI configuration. Existing environment is Python 3.14 despite a >=3.12 project floor.
- `_data/`: source locations inventoried; contents not copied or quoted. Only selected structural promotion metadata for idea 000007 was inspected for a real trace. Tests/governance read source data; output here contains no portfolio prose.
- `_private/`: NOT inspected. `data/`: live derived database NOT opened or rebuilt. `_working/`: local scratch, NOT treated as production or authoritative evidence. `_tmpagent/` payloads NOT read/claimed because this review does not use worktree coordination. Dependency trees/caches/build products and `.git` blobs are not alternate production source.
- No deployment environment or external model session was observed. Negative runtime/deployment claims mean no such mechanism in the reviewed repository, not proof none exists externally.

## Implementation and test paths

- `.claude/agents/idea-triage.md`
- `.claude/commands/backlog.md`
- `.claude/commands/idea-triage.md`
- `.claude/commands/idea.md`
- `.claude/commands/session-close.md`
- `.claude/skills/checkpoint/SKILL.md`
- `.github/workflows/ci.yaml`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `README.md`
- `pyproject.toml`
- `schemas/.gitkeep`
- `schemas/backlog.schema.json`
- `schemas/capture.schema.json`
- `schemas/codes.schema.json`
- `schemas/commitment.schema.json`
- `schemas/decision.schema.json`
- `schemas/development-event.schema.json`
- `schemas/document.schema.json`
- `schemas/evidence.schema.json`
- `schemas/idea-priority.schema.json`
- `schemas/idea.schema.json`
- `schemas/interaction.schema.json`
- `schemas/memory.schema.json`
- `schemas/person.schema.json`
- `schemas/project.schema.json`
- `schemas/staged-record.schema.json`
- `schemas/systems.schema.json`
- `schemas/tag.schema.json`
- `schemas/task.schema.json`
- `schemas/waiting-on.schema.json`
- `sql/.gitkeep`
- `sql/001_schema.sql`
- `sql/003_capture_views.sql`
- `src/__init__.py`
- `src/api/__init__.py`
- `src/capture/__init__.py`
- `src/capture/raw.py`
- `src/db/__init__.py`
- `src/db/connection.py`
- `src/db/ideas.py`
- `src/db/source_validation.py`
- `src/governance/__init__.py`
- `src/governance/__main__.py`
- `src/governance/backlog.py`
- `src/governance/codes.py`
- `src/governance/idea_priority.py`
- `src/main.py`
- `src/models/__init__.py`
- `templates/README.md`
- `templates/governance/document.md`
- `templates/html/.gitkeep`
- `templates/styles/.gitkeep`
- `test/__init__.py`
- `test/conftest.py`
- `test/test_backlog.py`
- `test/test_capture_contracts.py`
- `test/test_capture_intake.py`
- `test/test_codes.py`
- `test/test_glossary.py`
- `test/test_governance.py`
- `test/test_ideas.py`
- `test/test_load_context.py`
- `test/test_private_content.py`
- `test/test_rebuild.py`
- `test/test_schemas.py`
- `test/test_source_validation.py`
- `test/test_tool_docs.py`
- `tools/.gitkeep`
- `tools/append_idea.py`
- `tools/capture.py`
- `tools/check_no_private_content.py`
- `tools/generate_glossary.py`
- `tools/generate_ideas_md.py`
- `tools/generate_tool_docs.py`
- `tools/git-hooks/pre-commit`
- `tools/load_context.py`
- `tools/rebuild_db.py`
- `ts/index.html`
- `ts/package-lock.json`
- `ts/package.json`
- `ts/src/App.tsx`
- `ts/src/main.tsx`
- `ts/tsconfig.json`
- `ts/vite.config.ts`
- `uv.lock`

## Original research artifacts

- `research/implementation_glossary.md`
- `research/CLAUDE.codebase-review.md`
- `research/terminology_investigation.md`
- `research/research_expansion.md`
- `research/d-system-terminology-artifacts.zip`
- `research/knowledge_glossary.md`
- `research/two_system_architecture.md`
- `research/d-system-complete-chat-source-ledger.md`
- `research/d-system-research-starter.zip`
- `research/d-system-ideation-to-reality-pack.zip`
- `research/development_traceability_model.md`
- `research/CLAUDE.literature-review.md`
- `research/research_agent_addendum.md`
- `research/phase_context_contract.md`
- `research/development_evidence_matrix_template.csv`

## Research organization

All three ZIPs were safely extracted under `research/sources/archive-extractions/<zip-stem>/` retaining archive-internal paths and README files. Requested loose artifacts were preferred when present; every overlapping ZIP counterpart was byte-identical. All requested named copies were found. `organization_manifest.json` records origins, hashes and alternatives. The chat source seed is historical ideation material, **not a validated bibliography**.
