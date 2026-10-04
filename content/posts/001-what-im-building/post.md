# 001 — What I'm building

- **Status:** draft
- **Arc stage:** 1 Origin
- **Pillar:** Mechanism
- **Image:** AI image brief ([image.md](image.md))
- **Drafted against:** dev `518642d` (2026-10-04)
- **Posted:** —

## Single post

> I'm building D-System, an idea realization engine. An idea goes into an append-only log, gets
> triaged, grouped, planned, reviewed adversarially and built by AI coding agents, each in its own
> git worktree. I decide at five gates. This series covers how it works and what broke.

## Thread

1. I'm building D-System, an idea realization engine. It takes an idea from the moment I capture it
   to delivered, governed work. Most of the work is done by AI coding agents: Claude Code, Codex and
   Gemini work in the same repository. This series is about how it works.

2. The path: an idea is recorded in an append-only log, triaged by an agent, grouped with related
   ideas, turned into a requirement and a plan, reviewed by an adversarial agent, cut into
   one-session phases, and built by agents, each in its own git worktree.

3. I decide at five gates: which ideas enter, which groupings stand, which plans are approved, what
   merges, and what counts as complete. Gate decisions queue, so I clear them in batches instead of
   being interrupted for each one.

4. Most stages still run with me or a coordinating session driving them. Running them end to end is
   the next step. The portable version is a Claude Code plugin, the Idea Realization Engine (IRE),
   and its release is where this series ends.

5. A month in: 564 ideas captured and over 1,600 commits. Next post: why the idea log can never be
   edited.

## Sources

| Claim | Source |
|---|---|
| Idea realization engine; capture to delivered, governed work; the path of an idea; owner decides at gates; most stages still driven by a person or coordinating session | `README.md` lines 3-8 |
| Claude, OpenAI and Gemini models work in the repository | `README.md` lines 10-11 |
| Five gates and what each decides; gate decisions queue and are cleared in one sitting | `docs/07-architecture/ARCH-006-idea-realization-system.md`, "The gate model" |
| Each phase built in its own worktree | `AGENTS.md`, "Concurrent agents: work in a worktree" |
| The plugin is the portable form | `plugins/idea-realization/README.md` |
| "A month in": first architecture decisions dated 2026-09-05 | `ADR-001`, `ADR-002`, `ADR-003` front matter `created` |
| 564 ideas | `uv run python -c "from src.db import ideas; print(len(ideas.fold(ideas.load_events())))"` at `518642d` |
| Over 1,600 commits (1,648) | `git rev-list --count dev` at `518642d` |

## Notes for the owner

- "Gemini" in post 1 is from the README's model-agnostic line; drop it if you have not used Gemini
  models on this repository in practice.
- The commit count includes a squashed initial commit (`GOV-003`, "History is squashed, not
  filtered"), so it undercounts the work before 2026-09-09.
