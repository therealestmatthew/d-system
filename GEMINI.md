# GEMINI.md

This file provides orientation and behavioral configuration specifically for Gemini agents (and the Google Antigravity framework) operating in this repository.

## Repository Orientation
- The general rules for every agent (worktrees, backlog lock, etc.) are in **[AGENTS.md](AGENTS.md)**.
- The high-level architecture and directory layout is in **[docs/08-governance/GOV-007-repo-orientation.md](docs/08-governance/GOV-007-repo-orientation.md)**.

## Gemini's Role (Focus Areas)
*(To be expanded as focus areas are identified by the owner)*

As a Gemini agent in this repository, your primary focus areas are:
1. **Data Pipelines & Analytics:** Focus on `_data/` ingestion, JSON schemas (`schemas/`), and DuckDB extraction (`tools/rebuild_db.py`).
2. **Governance Verification:** Leverage deep context to perform comprehensive reviews of document lifecycles, run `src.governance` checks, and identify architectural drift.
3. **Autonomous Execution:** When invoked autonomously via SDK scripts, strictly adhere to the `backlog.yaml` queue logic described in `AGENTS.md`.

## Handling Framework-Specific Skills
- **Session Checkpoints:** Claude uses `.claude/skills/checkpoint`. Until this is abstracted into `tools/checkpoint.py`, if you need to record a mid-session checkpoint, manually draft your progress into the relevant session document in `docs/03-sessions/` instead of attempting to run a `.claude` skill.
- **Session Close:** Claude uses a specific command `/session-close`. When you finish a task, ensure the phase in `backlog.yaml` is updated and the outcome is documented according to the manual steps in `AGENTS.md`.
