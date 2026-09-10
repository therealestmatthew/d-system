---
name: orient
description: Show what an agent can actually do in this repository right now — the quick-start prompts, slash commands, skills, tools, governance documents and current backlog state — enumerated from the live sources rather than a stored list. Run it at the start of a session, or whenever someone asks "what can I do here" or "what should I run".
---

# orient

Answers one question: **what can an agent do in this repository, and where does each of those things
live?**

Everything below is **enumerated from disk at run time**. Do not paste a remembered inventory, and do
not maintain a list inside this file. A hardcoded catalogue of prompts and commands is stale the day
someone adds one, and this repository has already lost a day to documents asserting a state of the
world that had changed underneath them. If a command in this skill returns nothing, report that it
returned nothing — an empty category is information.

This skill is read-only. It changes no file, claims no phase, and runs nothing destructive.

## 1. Read the working agreement first

If you have not already this session, read `AGENTS.md`. It governs how you work here regardless of
framework. Do not summarise it from memory — the rules that matter most (never edit `AGENTS.md` or
`CLAUDE.md` without approval; ask before integrating onto the trunk; never write a confidential
identifier into a tracked file) have all changed recently.

## 2. Gather

Run these and keep the real output:

```bash
# Where the work stands
uv run python -m src.governance --ready          # phases ready now; the Queue column is next_up
uv run python -m src.governance                  # must exit 0; document/phase/memory counts

# What exists to invoke
ls docs/02-prompts/PROMPT-*.md                   # reusable prompts
ls .claude/commands/*.md                         # slash commands
ls .claude/skills/*/SKILL.md                     # skills, including this one
ls .claude/agents/*.md                           # subagents
ls tools/*.py                                    # CLI tools
ls docs/08-governance/OPS-*.md                   # one operations doc per tool

# Repository state
git status --short && git branch -vv
```

For each prompt, command, skill and agent, read its front matter or first lines for the one-line
description. Do not invent a description for something whose own file does not carry one; say the
description is missing, which is itself worth reporting.

## 3. Present

Group the output under these headings, in this order. Lead with what something **is**, then give the
code or path as the lookup handle — `GOV-006` calls this out specifically, and a bare filename is
not a description.

**Where the work stands.** The first ready phase in rendered order — that is what "execute the next
task" means, no judgement required. Note `next_up`, the count of ready versus waiting phases, active
claims, and whether governance exits 0. If the tree is red, that is the first thing you report, not
a footnote.

**The four workflow prompts.** These form the idea-to-delivery path, and they run in order:

| Stage | Prompt | Use it to |
|---|---|---|
| Capture | `PROMPT-006` | Record new ideas, and scout open ones into `triaged` |
| Plan | `PROMPT-007` | Turn one triaged idea into a requirement, a plan and phases |
| Execute | `PROMPT-008` | Work a single backlog phase end to end |
| Audit | `PROMPT-009` | Read-only check of plans against what is actually implemented |

Read the actual files for their current descriptions rather than trusting this table's wording; if
the set has grown beyond four, report what you find.

**Slash commands and skills.** What each does in one line, and who may invoke it. Flag owner-only
ones explicitly — `session-close` is owner-only and is the only place a phase reaches
`status: complete`. An agent must never invoke it or reproduce its steps.

**Tools.** Each `tools/*.py` with its paired `OPS-*` document. Note which are the sanctioned write
paths: `append_idea.py` is the only way to write `_data/ideas.jsonl`, and `rebuild_db.py` is how
DuckDB is regenerated from source JSON. Never hand-edit either target.

**Governance.** Point at, do not restate: `AGENTS.md` (the working agreement), `GOV-001` (document
lifecycle), `GOV-002` (backlog protocol), `GOV-003` (accepted decisions, including when a worktree is
required), `GOV-005` (document codes), `GOV-006` (how to report). Give the catalog
(`docs/08-governance/catalog.md`) as the index of every document.

**Repository state.** Current branch, whether the working tree is clean, and how the branch sits
relative to its remote. Name anything uncommitted or untracked rather than passing over it.

## 4. Close with the next action

End with one concrete sentence naming what to do next and which prompt or command covers it — for
most sessions, the first ready phase and `PROMPT-008`. If the tree is red, or a phase is claimed and
unfinished, or governance does not exit 0, that is the next action instead.

Do not claim a phase, edit a file, or start work. Orienting is not doing; the owner picks what
happens next.
