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

**Scope is 20 components and nothing else:** 6 commands, 6 skills, 6 prompts, 2 agents.

**Every component is general.** None is written against a fictional company, engagement or person.
Each is a tool the consultant points at their own work, and supplies their own material to. This
reverses the originating brief's single-running-scenario instruction, on the owner's decision of
2026-09-13: a component welded to an invented situation demonstrates once and is worthless
afterwards.

Explicitly out of scope, having been proposed and withdrawn on 2026-09-13: a fictional source
corpus, sample inputs, a manifest, a facilitator guide, fallback outputs held against a slow live
call, timed rehearsals, and any parking mechanism. The owner tests and demos the kit; this
requirement covers building it.

K10's recorded outputs are not that withdrawn item. A ladder rung's recorded output is the teaching
content of the file — what actually happened when the rung was run — not a standby copy kept in case
the live demo stalls.
Also out of scope: any change to `REQ-006`, which governs a different demo for a different audience
and separately claims a fifteen-minute run.

The design round proposed 23 entries, which a blind adversarial triage reduced to 16 (ideas
`000171`-`000193`, seven cuts with reasons recorded). On 2026-09-13 the owner replaced the command and
skill rosters wholesale with their own — ideas `000223` and `000222` — which is where the present six
and six come from. The prompts and agents are unchanged from the design round.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| K01 | No real client name, engagement, person or figure appears in any component. | Run `tools/check_no_private_content.py` with all kit files staged; read each component for identifiers. |
| K02 | Each command, skill and agent loads without error and appears in its surface: commands as slash commands, skills in the skill listing, agents in the agent listing. | Start a session with the kit present and confirm each entry is listed under its own name; invoke each command once. |
| K03 | No kit component writes a repository file. Components that emit an output file write only to their stated output location; nothing writes into `docs/`, `.claude/`, `_data/` or any governed path, and nothing writes `CLAUDE.md`. | Read every definition for a write target; run the components that emit files and confirm the only paths written are their declared output locations. |
| K04 | Exactly one capability ships twice — `demo-cmd-askme` and `demo-skill-ask-me` — so invocation is the only variable between them, and no other capability appears in two invocation models. | Read both definitions and confirm the capability matches; read the remaining entries for a second pair. |
| K05 | Every skill names itself in the first line of its output when it fires, so the audience can attribute the firing rather than mistaking it for ordinary helpfulness. | Provoke each skill and read the first line of output. |
| K06 | Each skill's description fires on a cue present in the input, not on an absence, an unobservable event, or a cue broad enough to match any consulting request, and states explicitly when it must not fire. | Read each description; for each skill, run three inputs that should fire it and three related inputs that should not, and record which fired. |
| K07 | Each agent declares its tool list and model explicitly, and any agent presented as read-only excludes `Bash` as well as every write tool. | Read each agent's frontmatter; confirm the read-only agent lists only `Read`, `Grep` and `Glob`. |
| K08 | Each agent's body states what it must never do and the condition under which it stops, matching the shape every existing agent in this repository uses. | Read each agent body against an existing definition in `.claude/agents/`. |
| K09 | The prompt ladder is five rungs plus the anti-pattern gallery, adds exactly one ingredient per rung, and the human constraint appears only as an answer to a question the model asked in the interview rung — never stated by the owner in any earlier rung. | Read the six prompt files in order; confirm each names the single ingredient it adds, and confirm no rung before the interview states a human constraint. |
| K10 | No ladder rung carries a fixed worked example or a pinned output. Each rung names the ingredient it adds and the change to watch for when it lands, and the rungs that state an expectation say what to do when it does not hold. | Read each rung; confirm it can be run against any engagement the reader supplies, and that no output is recorded as the rung's own. |
| K11 | The audience rung directs a paired run — the same prompt against two audiences, back to back — rather than a single output described as audience-dependent. | Read the rung and confirm it instructs two runs and names the comparison to make. |
| K12 | The anti-pattern gallery contains only failures that cost the user an outcome, not failures that cost only tokens, and each entry names the rung or component that addresses it. | Read each entry and confirm a stated consequence beyond verbosity and a pointer into the kit. |
| K13 | `demo-skill-ask-me` documents its parameters — question count, single versus multi-select, include or exclude recommendations — in a table in its body, and declares no `argument-hint`, because that affordance belongs to commands. Its default is to include a recommendation. | Read the skill body for the table; read its frontmatter and confirm no `argument-hint`; invoke it without specifying and confirm a recommendation is offered. |
| K14 | Every entry cut from the roster is recorded with the reason it was cut. | Read the cut annotations on ideas `000174`, `000178`, `000180`, `000181`, `000182`, `000192` and `000193`. |
| K15 | No component names an industry, company shape, headcount, timeline or job title as its subject, or depends on a fictional scenario. Anything a component operates on is taken as input. | Read each component and confirm it could be run unchanged against any consulting engagement. |
| K16 | Every component name carries its type prefix: `demo-cmd-`, `demo-skill-` or `demo-agent-`. | List the files in each directory and confirm the prefix. |
| K17 | `demo-skill-flowchart` and `demo-skill-scorecard` each produce two outputs: a self-contained HTML file that opens in any browser with no repository present, and a repository-specific publish into the HTML viewer. | Run each, open the standalone file from a directory outside the repository, and confirm it renders; confirm the viewer path publishes. |
| K18 | `demo-skill-brainstorm`, `demo-skill-scorecard` and `demo-skill-flowchart` call `demo-skill-ask-me` to gather what they need rather than each implementing its own questioning. | Read the three skill bodies for the call; confirm none contains its own elicitation sequence. |
| K19 | `demo-cmd-explain-this` accepts any artifact a consultant may be handed — a document, a spreadsheet, a system message, an error, a file — and its output contains no jargon, including none it invents to explain jargon. | Run it against a non-technical artifact and a technical one; read both outputs for unexplained terms. |

## Known accepted consequence

The kit is built into this repository's live `.claude/` directory, which every blind reviewer argued
against and the owner decided. Kit entries will therefore appear in `.claude/skills/orient`'s command
enumeration and the workbench agent picker during ordinary D-System work. No parking mechanism is in
scope; this is recorded as an accepted consequence rather than an open defect.
