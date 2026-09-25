---
schema_version: 1
id: doc-idea-realization-plugin-requirements
code: REQ-031
title: Idea-realization plugin requirements — the whole pipeline, its governance and its documents, packaged as one Claude Code plugin for private installation into other repositories
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin]
depends_on: [doc-realization-role-contracts, doc-plan-quality-standard, doc-governance-protocol, doc-document-code-protocol, doc-idea-node-classification, doc-repeatable-idea-partition-requirements, doc-idea-graph-lifecycle-requirements]
---

# Idea-realization plugin requirements

Observable statements for packaging this repository's idea-realization pipeline — idea capture,
triage, priority, partition, planning, phases, backlog, document governance, generators, repository
layout, the working agreement and the governance documents — as one Claude Code plugin named
`idea-realization`, for private installation into the owner's other repositories. The plan that
delivers them is [PLAN-048](../01-plans/PLAN-048-idea-realization-plugin/PLAN-048-overview.md).

## Observed problem and scope

The owner asked on 2026-09-25 which part of this repository would make an impactful, shareable
plugin, chose the idea capture and triage system (idea `000455`), and then widened the scope in the
same session to the whole pipeline and its governance (ideas `000456` to `000460`). Six read-only
analyses of the source areas were made before this document; they are in
`_working/session-manager/plugin-analysis/01` to `06` and their facts are cited below by file.

The failures that make the packaging non-trivial, each observed in the source:

1. **Every script derives its paths from its own location.** `src/db/ideas.py:19-21`,
   `tools/append_idea.py:73-77`, `tools/generate_ideas_md.py:30-32`, `src/governance/staleness.py:25-29`
   and `src/governance/regression.py:42-43` compute `ROOT` from `__file__` and hard-code
   `_data/ideas.jsonl`, `docs/00-working/ideas.md`, `docs/09-backlog/backlog.yaml` and the catalog
   path. Installed under `~/.claude/plugins/`, every one of them would look for its data inside the
   plugin directory (analysis 01 §2, 03 §3).
2. **The writer imports through the repository's `src` package.** `tools/append_idea.py:77-79`
   inserts the repository root on `sys.path` and imports `src.db.ideas`. A target repository with its
   own `src/` package resolves whichever comes first (analysis 01 §7 risk 1).
3. **The governance CLI is one inseparable entry point.** `src/governance/__main__.py:513-586` runs
   the document audit, the backlog audit, the idea-priority audit, code allocation and the catalog
   under one exit code, and `audit_backlog()` cannot run without the document audit's output
   (`__main__.py:359-366`). The pure modules underneath — `backlog.py`, `codes.py`, `idea_priority.py`,
   `src/db/ideas.py` — take dicts and paths as arguments and have no third-party imports (analysis
   03 §1, 04 §7).
4. **The workflows and agents name this repository's layout and documents.** The triage agent searches
   `docs/01-plans/`, `docs/06-requirements/`, `docs/04-decisions/` and `docs/09-backlog/backlog.yaml`
   by literal path (`agent-workflows/idea-triage-agent.md:35-36`); every workflow ends with
   `uv run python -m src.governance`; the partition pack cites `REQ-009`, `PLAN-025`, `GOV-008`,
   `GOV-014`, `GOV-017`, `phase-part-03` and idea ids as provenance (analysis 02 §3).
5. **The governance documents carry their history.** Between 5% and 40% of each portable governance
   document is incident narrative, dated provenance or superseded state; `GOV-003` is a 748-line
   dated ledger of which roughly ten entries are still-standing rules; `GOV-001:181,191` and
   `GOV-002:168,172` still name `main` as the trunk (analysis 05 §1–2).
6. **The partition sweep stops before its second audit.** The adversary runs in the primary checkout
   and cannot read a draft that exists only in the coordinator's worktree; the workflow's own text
   records the owner's 2026-09-23 ruling to stop there (`agent-workflows/partition-ideas.md:351-361`;
   analysis 02 §6).
7. **The install rulings are not on the idea that carries them.** The owner's 2026-09-25 rulings on
   installation (unit of installation, settings and hooks consent, tracking first) are recorded in
   `_working/session-manager/reports/rulings-000347.md:98`, not yet as annotations on idea `000439`
   (analysis 06 §1).

Scope: one plugin, private use, installed from this repository by local path. Everything the plugin
carries is a copy adapted for a target repository; nothing in this repository changes its own
behaviour because of the plugin (idea `000462` records the later question of whether it should).

## Observable requirements and verification

| Id | Requirement | Verification |
|---|---|---|
| R01 | The plugin is one directory, `plugins/idea-realization/`, with `.claude-plugin/plugin.json` naming it `idea-realization`, no `license` field, a `userConfig` block for every configurable path, and the component directories `skills/`, `agents/`, `scripts/`, `schemas/`, `templates/`, `docs/`. | `claude plugin validate plugins/idea-realization --strict` exits 0. A fixture copy with a `license` field or an unknown top-level key fails `--strict`. |
| R02 | No file in the plugin names the source repository, its owner, any person, any idea id, any backlog phase id, any document code of this repository, any session record, any commit hash, or any dated incident. Only concepts that hold in any repository using the framework appear. | A check script in the plugin's test suite greps the plugin tree for the source repository's name, `_private`, `[0-9]{6}` idea ids, `phase-[a-z]+-[0-9]+`, `(PLAN\|REQ\|ADR\|GOV\|OPS\|PROMPT\|SESS\|ARCH)-[0-9]`, `SESS-`, seven-plus-hex commit hashes and calendar dates in prose, and returns nothing; the same script run on a fixture file containing a phase id fails. |
| R03 | Every script runs with `uv run <script>` from any working directory, carries PEP 723 inline metadata naming only `jsonschema` and `pyyaml`, lives in a flat `scripts/` package that never imports a `src` package, and takes every data path from a CLI flag, an environment variable or the plugin's `userConfig`, in that precedence, never from its own location. | Each script's `--help` lists its path flags. A test copies the scripts to a temporary directory and runs each against a temporary data root; a test greps `scripts/` for `parents[` and `from src` and finds nothing. |
| R04 | A `prerequisites` skill checks Python ≥ 3.12, `uv`, `git` and, for the partition and triage workflows, the `claude` CLI; reports each missing item with the exact install command; and runs an install only after the person answers yes. Its check mode changes nothing. | A test runs the check script with a `PATH` lacking `uv` and reads a report naming `uv` and its install command, with exit code 1 and no file or package changed; the same run with everything present exits 0. |
| R05 | A `scaffold` skill creates, in the target repository, the directories and seed files each feature needs (the idea log, its rendered view, the priority file, the backlog file, the document tree, the code register, the systems registry, the schemas) and writes an install-state record with the plugin version and a SHA-256 per file written. It never overwrites a file that exists, reports every path created and every path skipped, and offers a dry run that writes nothing. | A test scaffolds into an empty temporary repository and reads the record with one entry per created file; a second run over the same repository creates nothing and reports every path as skipped; a run over a repository holding a pre-existing `backlog.yaml` leaves that file byte-identical and reports it skipped; `--dry-run` leaves the directory empty. |
| R06 | The scaffold writes the target's `.claude/settings.json`, any hook, or `.gitignore` only when the person gives a separate consent for that write, and the consent is recorded in the install-state record. | A test runs the scaffold without consent and finds no settings, hook or gitignore change; with consent, the record's `consent` entry names the file written and the record's file hash matches the file. |
| R07 | A `doctor` script compares every file the install-state record names against the disk and reports each as unchanged, drifted (hash differs) or missing, and changes nothing. | A test edits one scaffolded file and deletes another; `doctor` names both with the right state, exits 1, and a directory listing before and after is identical. |
| R08 | The idea writer supports `add`, `status`, `revisit`, `amend`, `annotate`, `amend-annotation`, `link` and `retract-link` over the configured log, generates ids and timestamps itself, exposes no way to supply a timestamp, and refuses every transition the schema does not list. | The existing writer's transition tests, ported to run against a temporary log through the plugin's script: an `open → promoted` without `--promoted-to` is refused; a second discard after the one revisit is refused; `--help` shows no time or date option. |
| R09 | `fold` replays the log into effective state (amendments applied, links with derived inverses, annotations resolved), and `render` writes the Markdown view with the priority queue first; rendering twice produces identical output, and a `check` reports a stale rendered view. | A test folds a fixture log with an amend and reads the amended title; renders twice and diffs to nothing; edits the rendered file and reads the staleness error from `check`. |
| R10 | A vocabulary document in the plugin lists every status and legal transition, every event kind, every annotation kind with its authorship rule, every link type with its inverse, and the four classification axes with their values, tie-break rules and the record kinds — and a test proves the document's enumerations equal the schema's. | A test parses the vocabulary document's tables and compares each set to the corresponding `enum` in `schemas/idea.schema.json`; a fixture document missing one status fails the test. |
| R11 | The priority queue is a file of idea ids in the target repository; `check` rejects a queue naming an unknown idea, an idea whose status is not `open` or `triaged`, or a future `updated` date. | Three fixture queues, one per error, each fails `check` naming the id or the date; a valid queue passes. |
| R12 | The `idea-triage` agent and its driver skill triage one open idea at a time, search a configurable list of directories and files for related material, write one `finding` annotation through the command they are handed, and never write a `linked` event or a `promoted` status. | A test reads the agent file's front matter and finds `Edit` and `Write` absent from its tools; a grep of the agent and skill for `link ` and `status .* promoted` as commands finds only the prohibitions; the search list is a `userConfig` value with a documented default. |
| R13 | The `partition-ideas` skill runs the sweep — corpus build with a status flag, two analyst dispatches (one a control never told it is a control), an adversary audit, a synthesis, a second adversary audit, a gate checklist — with an owner stop at each gate, and the second audit runs because the synthesis draft is written to an absolute path in the primary checkout that the adversary is given. | A transcript of one sweep in the scratch repository (R22) shows all four dispatches and the second audit's findings; the record validates against the plugin's partition-record schema; a test runs the corpus builder against a fixture log with `--status open` and reads the manifest's status selection. |
| R14 | The backlog `check` enforces every rule `inspect_backlog` enforces today: unique ids, `next_up` entries known and not finished, `max_active`, one active phase per agent, no collisions between active phases on systems, deliverable paths or dependency chain, `depends_on` resolvable and acyclic, `blocked`/`deferred` reasons and resume conditions, completion fields present only in claimed states and all present when complete, every open plan covered by a phase. `ready` prints the queue in `next_up` order then priority, with a conflicts column. | The existing backlog tests, ported to run against fixture catalogs through the plugin's script; a fixture with two active phases sharing a system fails `check` naming both. |
| R15 | The claim, worktree, checkpoint and completion procedures are skills — `session-start`, `checkpoint`, `session-close` — with the integration branch and worktree directory taken from `userConfig`; `checkpoint` cannot write `status: complete`; `session-close` writes it only after every verification command ran with recorded output, an independent review found no unresolved discrepancy, and the branch is integrated with the owner's approval. | A grep of the `checkpoint` skill finds `status: complete` only in a prohibition; the `session-close` skill states the three conditions; the integration branch name appears in no skill as a literal. |
| R16 | Document governance ships as a `check` over the target's document tree (front matter against the schema, kinds and lifecycle statuses, acyclic `depends_on`, owner keys from the systems registry, a code register), a `next-code` allocator with the same pre-merge reservation mechanism (exclusive files under the git common directory, TTL, `release-code`), and a `catalog` renderer whose committed output `check` compares against a fresh render. | The existing code and reservation tests, ported; a fixture document with an unknown kind fails `check`; two `next-code` calls from two worktrees of one temporary repository return different codes; a hand-edited catalog fails `check`. |
| R17 | The requirement and plan templates and a `plan-check` script that implements the mechanical section check (the accepted headings, fenced lines ignored, the two conditional sections) ship in the plugin. | `plan-check` on the plugin's own plan template exits 0; on a fixture missing the boundaries section exits 1 naming it. |
| R18 | Two generators ship: one that fills a tool's operations document between fixed markers from the tool's docstring, arguments and exit codes, and one that renders host adapters (Claude skill, command and agent files) from a workflow manifest; both take their input and output roots as arguments and are deterministic. | The existing generator tests, ported; each generator run twice over a fixture produces identical output; a hand edit inside the generated block is reported. |
| R19 | A repository-layout reference and templates for the working agreement (`AGENTS.md`) and the orientation file (`CLAUDE.md`) ship with placeholders for the integration branch, the worktree directory, the data root and the confidential directory, and no other repository-specific content. | A test renders both templates with a placeholder set and greps the output for `{{`; R02's check runs over the rendered output. |
| R20 | The governance documents ship rewritten as current rules with no history: the core protocol, backlog protocol and document codes; the reporting rules; the prompt-pack, research-pack, coordinator and batch protocols; the role contracts, the review procedure and the adversary dispatch prompt; the multi-session coordination protocol and its starter messages. Every still-standing rule of the source decision ledger is inlined into the document it amends, and a trace table in this repository maps each plugin rule to its source passage. | R02's check passes over `docs/`; a reviewer reads the trace table and finds each source rule listed present in the named plugin document; a grep of the plugin's `docs/` for `until 20`, `was broken`, `incident`, `replaces` and `precedent` finds nothing. |
| R21 | The plugin's own pytest suite runs from the plugin directory against temporary fixtures only, reads no file of the source repository outside the plugin, and passes. | `cd plugins/idea-realization && uv run pytest` exits 0; a grep of the suite for `parents[2]`, `_data/` and `docs/09-backlog` finds nothing. |
| R22 | The plugin has been installed by local path into a scratch repository and exercised once end to end: prerequisites checked, scaffold run, an idea recorded, folded and rendered, triaged, a partition sweep run, a requirement and plan written and checked, a phase registered and claimed, a document code allocated, the catalog rendered, `doctor` run. The transcript and outputs are recorded in a session record. | The session record names the scratch repository, quotes each command's real output, and lists the files the scaffold created. |
| R23 | The four-axis classification fields ship in the plugin's idea schema exactly as this repository's schema defines them after `phase-idg-01` lands. | A test asserts the plugin's `idea.schema.json` `enum` sets for record kind and each axis equal the source schema's at the commit the plugin phase branched from. |

## What each requirement is not

- R01 does not require publication or a version-bump procedure. A marketplace file at this
  repository's root, added by local path, is the install mechanism the CLI supports (PLAN-048 D2);
  it is private because it is never published.
- R02 does not forbid the framework's own concepts (idea, phase, plan, requirement, adversary,
  coordinator); it forbids instances — this repository's ids, codes, names and dates.
- R03 does not require the scripts to work without `uv`; the prerequisites skill (R04) is where a
  missing `uv` is reported.
- R04 does not install anything without a yes, and does not run at session start.
- R05 and R06 do not require an uninstall; `doctor` (R07) reports, it does not repair.
- R08 to R11 do not project the log into a database; the derived query layer stays in this
  repository.
- R12 does not automate triage across ideas (no dispatcher, no watcher); one idea per invocation.
- R13 does not resolve this repository's own second-audit block; that is the owner's ruling here.
- R14 does not allocate phase ids; they stay a manual track convention documented in the layout
  reference.
- R15 does not port the multi-session lock relay; `session-close` is the coordinator-completion rule
  stated as the current rule.
- R16 does not validate memories (`brain/`) or a systems registry's `paths` against disk.
- R20 does not ship the orientation document or the surface audit of this repository, and does not
  keep the decision ledger as a document.
- R21 does not require the source repository's tests to change.
- R23 does not let the plugin define fields ahead of `phase-idg-01`; if that phase has not landed
  when the idea phase starts, the idea phase waits.

## Accepted decisions

Owner, 2026-09-25, in the Session Manager session:

- The plugin lives in this repository, for private use, installed by local path. The owner's
  answer was "no marketplace file"; the adversary verified the CLI installs persistently only from
  a marketplace, so PLAN-048 D2 carries a private marketplace file for the owner's ruling at G3.
- Version 1 is the whole pipeline: capture, fold, render, triage, priority queue, four-axis schema,
  partition, planning and phases, backlog and ordering, the full property vocabulary, document
  governance, generators, repository layout, the working agreement, and the governance and protocol
  documents rewritten as absolutes.
- One plugin with everything. This departs from the 2026-09-25 ruling on idea `000439` that the unit
  of installation is a workflow; the owner chose the single plugin knowing that.
- Scripts run with `uv` and PEP 723 inline dependencies; a prerequisites skill checks and installs
  what is missing, on a yes.
- Ideas live at `ideas/ideas.jsonl` with the rendered view beside it, configurable through
  `userConfig`.
- The four-axis fields are built here first (`phase-idg-01`), then ported.
- The plugin's engine is a new thin CLI over the portable modules; this repository's
  `src/governance` is untouched.
- The orientation document and the surface audit are excluded from the absolute document set.
- The plugin's partition sweep resolves the second-audit block by writing the draft where the
  adversary can read it.
- Nothing in the plugin references this repository, its people, its systems or its ideas; only
  concepts that hold in any repository.
- The plugin is named `idea-realization`, with no licence stated.
- The analysis and planning work is distributed across the agent crew; the build phases dispatch
  per-family work the same way.
