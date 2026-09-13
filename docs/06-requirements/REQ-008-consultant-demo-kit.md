---
schema_version: 1
id: doc-consultant-demo-kit-requirements
code: REQ-008
title: Consultant demo kit requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-demo-kit]
depends_on: [doc-live-demo-requirements]
---

# Consultant demo kit requirements

## Observed problem and scope

The owner presents a 15-20 minute live Claude Code demo to Finance Transformation consultants, most
of whom have minimal coding background and have never opened a terminal. The existing live demo
(`REQ-006`) is a different artefact for a different audience: it demonstrates *this repository* to an
audience being taught skills and agents, through a stage page with an embedded terminal. This
requirement covers a content kit — commands, skills, prompts and agents that a consultant would use
in their own work — with no code, git, debugging or repository content anywhere in it.

The two must not be confused, and both claim "fifteen minutes". `REQ-006` R09 governs the D-System
segment. This requirement governs the consultant kit's run. Nothing here changes `REQ-006`.

Scope: 13 artefacts (5 commands plus 1 converted from a skill, 2 skills, 6 prompts, 2 agents), a
fictional source corpus they operate on, a manifest the owner's IDE reads, a context file, and a
facilitator guide. Out of scope: the stage page, the terminal capability, deployment, and any change
to `REQ-006`'s segment.

The roster was reduced from 23 proposed entries to 13 by a blind adversarial triage recorded on ideas
`000171`-`000193`. Seven entries were cut with reasons recorded; the count targets in the originating
brief were not treated as binding.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| K01 | A fictional source corpus exists for one company, used by every entry that needs source material: per-subsidiary close process documents, a draft containing numbers of which some trace to a stated source and some do not, and raw meeting notes containing commitments of which at least two have neither owner nor date. | Open each file and confirm the stated content is present; confirm one company name and one set of figures across all files; confirm `tools/check_no_private_content.py` passes with the corpus staged. |
| K02 | No real client name, engagement, person or figure appears anywhere in the kit. | Run `tools/check_no_private_content.py` with all kit files staged; read the corpus and every artefact for identifiers. |
| K03 | Each of the kit's commands, skills and agents loads without error and appears in its surface: commands as slash commands, skills in the skill listing, agents in the agent listing. | Start a session with the kit present and confirm each entry is listed under its own name; invoke each command once and confirm it runs. |
| K04 | The kit's entries do not appear in `.claude/skills/orient`'s command enumeration or the workbench agent picker during ordinary D-System work, and `tools/demo_reset.py` parks and restores them as a set. | Run the orient skill and the workbench agent listing with the kit parked and confirm no kit entry appears; unpark, confirm every entry appears; re-park and confirm the listing returns to its parked state. |
| K05 | No kit entry writes `CLAUDE.md`, `AGENTS.md`, or any governed document. The context-building command writes only to the kit's own context file. | Read every command, skill and agent definition for a write target; invoke the context-building command and confirm the only file written is the kit's context file. |
| K06 | Exactly one capability ships twice — once as a command and once as a skill — and the skill names itself in the first line of its output so the audience can attribute the firing. | Read both definitions and confirm the capability matches; provoke the skill and confirm its first output line identifies it by name; confirm no other capability appears in two invocation models. |
| K07 | Every skill in the kit names itself in its first line of output when it fires. | Provoke each skill and read the first line of output. |
| K08 | Each skill's description fires on a cue that is present in the input rather than on an absence, an unobservable event, or a cue so broad it matches any consulting request. | For each skill, run three inputs that should fire it and three related inputs that should not, and record which fired. |
| K09 | Each agent in the kit declares its tool list explicitly, and any agent presented to the audience as read-only excludes `Bash` as well as every write tool. | Read each agent's frontmatter; confirm the read-only agents list only `Read`, `Grep` and `Glob`. |
| K10 | Every live entry in the run of show completes within its stated timebox, and every entry whose timebox cannot be met live has a pre-run recorded output committed as its fallback. | Two timed rehearsals with per-entry times recorded in the kit's runbook; confirm a committed fallback artefact exists for each entry marked pre-baked. |
| K11 | The prompt ladder adds exactly one ingredient per rung, the interview rung runs before the human obstacle is stated, and the obstacle enters the conversation because the model asked for it. | Read the six prompt files in order and confirm each names the single ingredient it adds; run the ladder end to end and confirm the interview rung's output asks for the obstacle before any rung states it. |
| K12 | The prompt ladder's rungs marked pre-baked carry pinned outputs, and the rung whose claim is that the recommendation inverts carries the recorded before-and-after that demonstrates it. | Open the pinned output files; compare the recorded rung-3 and rung-4 outputs and confirm the recommendation differs in substance, not only in wording. |
| K13 | `demo-kit-manifest.json` contains one array per type, each entry carrying id, slug, label, type, file path, blurb under 90 characters, demo beat and headline flag, and every file path resolves to a file that exists. | Parse the manifest, assert the field set and the blurb length on every entry, and assert every path exists on disk. |
| K14 | The manifest marks no more than five entries as headline. | Count headline entries in the manifest. |
| K15 | Every entry cut from the kit is recorded with the reason it was cut, and the record is reachable from the kit's own documentation. | Read the cut record and confirm one entry per cut item with a stated reason. |
| K16 | The facilitator guide states a run of show across the four teaching beats with a per-entry timebox, and a 15-minute cut line that removes no beat-1 entry. | Read the guide; confirm the cut line is stated and that no entry it removes is assigned beat 1. |
| K17 | Every entry in the manifest is assigned the beat whose lesson it actually teaches, and beat 1 is defended by more than one entry after the cut line is applied. | Read each entry's stated lesson against its assigned beat; apply the cut line and count surviving beat-1 entries. |

## Out of scope

- Any change to `REQ-006`'s fifteen-minute D-System segment, its stage page or its terminal.
- Deployment of the kit anywhere outside the presentation machine.
- The seven cut entries, which remain recorded as triaged ideas and are not built.
