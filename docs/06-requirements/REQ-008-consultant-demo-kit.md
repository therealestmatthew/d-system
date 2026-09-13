---
schema_version: 1
id: doc-consultant-demo-kit-requirements
code: REQ-008
title: Consultant demo kit requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-13'
systems: [sys-demo-kit]
depends_on: [doc-live-demo-requirements]
---

# Consultant demo kit requirements

## Observed problem and scope

The owner presents a live Claude Code demo to Finance Transformation consultants, most of whom have
minimal coding background and have never opened a terminal. This requirement covers the components
they will be shown: commands, skills, prompts and agents that a consultant would use in their own
work, with no code, git, debugging or repository content in any of them.

"Components" is the generic term throughout, matching Anthropic's plugin documentation, which groups
a plugin's contents as skills, agents, hooks and MCP servers. "Artifacts" is avoided deliberately: it
names a different Claude feature.

**Scope is 16 components and nothing else:** 6 commands, 2 skills, 6 prompts, 2 agents.

Explicitly out of scope, having been proposed and withdrawn on 2026-09-13: a fictional source
corpus, sample inputs, a manifest, a facilitator guide, pinned fallback outputs, timed rehearsals,
and any parking mechanism. The owner tests and demos the kit; this requirement covers building it.
Also out of scope: any change to `REQ-006`, which governs a different demo for a different audience
and separately claims a fifteen-minute run.

The roster was reduced from 23 proposed entries to 16 by a blind adversarial triage recorded on
ideas `000171`-`000193`. Seven entries were cut with reasons recorded; the count targets in the
originating brief were not treated as binding.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| K01 | No real client name, engagement, person or figure appears in any component. | Run `tools/check_no_private_content.py` with all kit files staged; read each component for identifiers. |
| K02 | Each command, skill and agent loads without error and appears in its surface: commands as slash commands, skills in the skill listing, agents in the agent listing. | Start a session with the kit present and confirm each entry is listed under its own name; invoke each command once. |
| K03 | No kit component writes any file in this repository. `context-me` outputs the context file's content for the reader to save and never states or implies that it wrote a file. | Read every definition for a write target; invoke `context-me` and confirm nothing is written and nothing claims to have been. |
| K04 | Exactly one capability ships twice — once as a command and once as a skill — and no other capability appears in two invocation models. | Read both definitions and confirm the capability matches; read the remaining entries for a second pair. |
| K05 | Every skill names itself in the first line of its output when it fires, so the audience can attribute the firing rather than mistaking it for ordinary helpfulness. | Provoke each skill and read the first line of output. |
| K06 | Each skill's description fires on a cue present in the input, not on an absence, an unobservable event, or a cue broad enough to match any consulting request, and states explicitly when it must not fire. | Read each description; for each skill, run three inputs that should fire it and three related inputs that should not, and record which fired. |
| K07 | Each agent declares its tool list and model explicitly, and any agent presented as read-only excludes `Bash` as well as every write tool. | Read each agent's frontmatter; confirm the read-only agent lists only `Read`, `Grep` and `Glob`. |
| K08 | Each agent's body states what it must never do and the condition under which it stops, matching the shape every existing agent in this repository uses. | Read each agent body against an existing definition in `.claude/agents/`. |
| K09 | The prompt ladder adds exactly one ingredient per rung, and the rung that invites the model to interview the consultant precedes the rung that states the human obstacle, so the obstacle enters because the model asked for it. | Read the six prompt files in order and confirm each names the single ingredient it adds and that the interview rung comes first. |
| K10 | The anti-pattern gallery contains only failures that cost the user an outcome, not failures that cost only tokens. | Read each entry and confirm a stated consequence beyond verbosity. |
| K11 | `client-ready` is a command, not a skill, and declares its arguments in frontmatter and documents them in a table. | Read the file's location and frontmatter; confirm the argument table exists. |
| K12 | Every entry cut from the roster is recorded with the reason it was cut. | Read the cut annotations on ideas `000174`, `000178`, `000180`, `000181`, `000182`, `000192` and `000193`. |

## Known accepted consequence

The kit is built into this repository's live `.claude/` directory, which every blind reviewer argued
against and the owner decided. Kit entries will therefore appear in `.claude/skills/orient`'s command
enumeration and the workbench agent picker during ordinary D-System work. No parking mechanism is in
scope; this is recorded as an accepted consequence rather than an open defect.
