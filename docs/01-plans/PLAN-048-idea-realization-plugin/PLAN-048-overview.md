---
schema_version: 1
id: doc-idea-realization-plugin
code: PLAN-048
title: Idea-realization plugin — overview
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin]
depends_on: [doc-idea-realization-plugin-requirements, doc-realization-role-contracts, doc-plan-quality-standard, doc-three-altitude-review-procedure]
---

# Idea-realization plugin

Delivers [REQ-031](../../06-requirements/REQ-031-idea-realization-plugin.md). One plugin,
`plugins/idea-realization/`, carrying the whole idea-realization pipeline and its governance for
private installation into the owner's other repositories. Eight phases, `phase-plug-01` to
`phase-plug-08`, one per child plan in this folder.

## Context and scope

The owner chose on 2026-09-25 to package this repository's idea capture and triage system as a
Claude Code plugin (idea `000455`), then widened the scope to the whole pipeline — priority queue,
four-axis classification, partition, planning and phases, backlog and ordering, the full property
vocabulary (`000456`); document governance, generators, repository layout and the working agreement
(`000457`); a scaffold skill (`000458`); a prerequisites skill (`000459`); and the governance
documents rewritten as absolutes (`000460`). `REQ-031`'s problem section lists the seven observed
failures that make the packaging more than a copy, with the analysis file and line for each; the
six analyses are in `_working/session-manager/plugin-analysis/`.

In scope: everything `REQ-031` R01 to R23 names. The plugin is a copy adapted for a target
repository. This repository keeps its own `src/governance`, tools, workflows and documents unchanged
(idea `000462` records the later question of whether it should consume the plugin instead).

## Decisions

Each decision names the alternative rejected and what it would have cost. The owner made D1 to D8
on 2026-09-25 in the Session Manager session; D9 to D12 are the planner's, open to the adversary
and to G3.

- **D1. One plugin.** Rejected: several plugins in one marketplace, one per workflow, which the
  2026-09-25 ruling on idea `000439` (the unit of installation is a workflow) would have suggested.
  Cost of the rejected option: a marketplace file, inter-plugin dependency declarations, and a
  target that installs the backlog without the document governance it needs. The owner chose one
  plugin knowing the departure; `REQ-031`'s accepted decisions record it.
- **D2. Private use, installed by local path, no marketplace file, no licence.** Rejected: a
  marketplace in this repository or a new public repository. Cost: publication work and a licence
  decision for something only the owner installs.
- **D3. `uv run` with PEP 723 inline dependencies.** Rejected: stdlib-only scripts (a second
  validation implementation to keep in sync with the schema) and a pip-installed package with a
  SessionStart install hook (a hook the owner's consent ruling would gate, and a persistent
  install to maintain). Cost of the chosen option: `uv` must be present, which the prerequisites
  skill checks.
- **D4. A new thin CLI over the portable modules.** Rejected: refactoring `src/governance` here
  first (a phase of its own before any plugin phase could start) and copying the monolith with its
  paths made configurable (carries the coupling and this repository's checks into every target).
  Cost of the chosen option: two copies of the pure modules until `000462` is decided.
- **D5. Four-axis fields come from `phase-idg-01`, then port.** Rejected: the plugin defining the
  fields first (two schemas until idg-01 adopts them) and vocabulary only (a plugin that cannot
  classify). Cost: `phase-plug-02` waits for `phase-idg-01`.
- **D6. Data paths through `userConfig`, default `ideas/ideas.jsonl`.** Rejected: this
  repository's paths as the default (`_data/`, `docs/00-working/`), which would carry its layout
  into every target. Cost: this repository, if it ever installs the plugin, sets the paths.
- **D7. The orientation document and the surface audit are excluded.** Neither is a protocol.
  Cost: none; the scaffold's README and the layout reference cover orientation.
- **D8. The plugin's partition sweep resolves the second-audit block.** The draft is written to the
  primary checkout's staging directory and its absolute path is passed in the A2 dispatch.
  Rejected: shipping the gap (a sweep that stops short of its own procedure) and dropping the
  second audit (contradicts the four-dispatch shape). Cost: this repository's copy stays blocked
  until the owner rules on it here; the two copies differ on this point.
- **D9. A flat `scripts/` package with a single `paths.py`.** Every script imports siblings
  relatively and resolves each path through one function with one precedence (flag, environment
  variable, `userConfig`, default). Rejected: copying `src/` (the package-name collision in
  `REQ-031` problem 2) and per-script path handling (eight places to get one rule wrong).
- **D10. The R02 check is a test in the plugin's own suite, run from `phase-plug-01` on.**
  Rejected: a one-time review at the end. Cost of the rejected option: every later phase could
  reintroduce a reference and nothing would say so until `phase-plug-08`.
- **D11. Document governance before backlog.** `phase-plug-05` precedes `phase-plug-04` because
  the backlog check needs the documents, systems and owners the document scan produces
  (`REQ-031` problem 3). Rejected: a backlog check with its own minimal registry (a second
  document scanner).
- **D12. The absolute rewrite is dispatched per family and traced.** Six analyst dispatches, one
  per family from analysis 05 §5, each returning one-line absolutes with source lines; the plugin
  documents are written from those; a trace table in this repository maps each rule to its source.
  Rejected: one session rewriting 3,800 lines by reading (no way to check completeness) and
  keeping the source documents with history stripped by hand (the same, slower).

## Implementation phases

| Phase | Child plan | Delivers |
|---|---|---|
| `phase-plug-01` | [PLAN-048.01](PLAN-048.01-skeleton-install.md) | Skeleton, `paths.py`, prerequisites, scaffold with install-state record, doctor, the R02 check |
| `phase-plug-02` | [PLAN-048.02](PLAN-048.02-idea-system.md) | Writer, fold, render, priority queue, vocabulary, triage agent and skill |
| `phase-plug-03` | [PLAN-048.03](PLAN-048.03-partition.md) | Corpus builder, partition pack, analyst and adversary agents, the sweep with audit 2 |
| `phase-plug-04` | [PLAN-048.04](PLAN-048.04-backlog-sessions.md) | Backlog check and ready report, status regression, session-start, checkpoint, session-close |
| `phase-plug-05` | [PLAN-048.05](PLAN-048.05-document-governance.md) | Document check, next-code with reservations, catalog, plan-check, templates |
| `phase-plug-06` | [PLAN-048.06](PLAN-048.06-generators-layout.md) | Two generators, layout reference, AGENTS.md and CLAUDE.md templates |
| `phase-plug-07` | [PLAN-048.07](PLAN-048.07-absolute-documents.md) | The governance documents as absolutes, the trace table |
| `phase-plug-08` | [PLAN-048.08](PLAN-048.08-end-to-end.md) | Scratch-repository exercise, README, session record, handover |

Prerequisites: `phase-idg-01` (queued, first in the ready order) must land before `phase-plug-02`.
Every phase runs in its own worktree on `agent/<phase-id>`; every phase's verification includes the
plugin's pytest suite, `claude plugin validate --strict`, the staged private-content check and the
governance check.

## Requirement coverage

| Requirement | Phase |
|---|---|
| R01, R03, R04, R05, R06, R07, R21 | `phase-plug-01` |
| R02 | `phase-plug-01` (the check), every later phase (passes it), `phase-plug-07` (extended) |
| R08, R09, R10, R11, R12, R23 | `phase-plug-02` |
| R13 | `phase-plug-03` |
| R14, R15 | `phase-plug-04` |
| R16, R17 | `phase-plug-05` |
| R18, R19 | `phase-plug-06` |
| R20 | `phase-plug-07` |
| R22 | `phase-plug-08` |

Every row maps to a phase and every phase to at least one row.

## Execution order and real concurrency

All eight phases declare `sys-plugin` only and deliver under `plugins/idea-realization/` (plus one
trace document under this plan folder and one session record), so the validator will not let two
of them be active at once: they share a system and a deliverable path. The order is therefore the
dependency order, run one at a time:

1. `phase-idg-01` (already registered; locks `sys-governance`, not `sys-plugin`, so it may run
   alongside `phase-plug-01`).
2. `phase-plug-01`.
3. `phase-plug-05`, then `phase-plug-02` (after idg-01), in either order.
4. `phase-plug-04` and `phase-plug-06` (both after 05), then `phase-plug-03` (after 02).
5. `phase-plug-07` (after 04 and 06).
6. `phase-plug-08` (after 03 and 07).

The owner ranks `next_up`; the planner proposes, at G3, that the eight phases follow
`phase-idg-01` at the front of the queue in the order above, since the owner ruled that the
coordination work stays paused until the plugin ships.

Failure paths: a phase whose verification fails stays `active` with the failure in its checkpoint
and is not integrated; a phase that finds `phase-idg-01`'s schema changed after it branched
rebases and re-runs the R23 test; a phase that cannot fit one session returns to `queued` with an
exact `next_action` and the split is recorded in the decision ledger.

## Acceptance and verification

The plan is complete when all eight phases are `complete`, `REQ-031` R22's session record exists,
and `cd plugins/idea-realization && uv run pytest` passes on `dev`. Per-phase acceptance is in the
backlog entries and restated in each child plan.

## Out of scope

- Publishing the plugin, a marketplace file, a licence, versioning beyond the manifest's `version`.
- Changing this repository's own `src/governance`, tools, workflows or documents (idea `000462`).
- Resolving this repository's own partition second-audit block (owner ruling pending here).
- Projecting the idea log into a database; memory (`brain/`) validation; the multi-session lock
  relay; phase-id allocation; an uninstall or repair command.
- Posting the 2026-09-25 install rulings onto idea `000439` — the batch-F follow-up in
  `_working/session-manager/restart-2026-09-25.md` §3 owns it; `REQ-031` cites the ruling log.

## Open questions

- **Q1. `next_up` placement.** Owner, at G3. The planner leans to the order in Execution order,
  directly after `phase-idg-01`.
- **Q2. Whether `phase-plug-07` fits one session.** Planner, decided at phase-fit after the
  adversary's phase-altitude review. It dispatches six analysts and writes from their output; the
  planner leans to one session because the extraction is parallel and the writing is
  consolidation, and names the split (families A–C in one phase, D–F in another) if not.
- **Q3. The `claude` CLI as a prerequisite.** Planner, in `phase-plug-01`. Triage and partition
  dispatch subagents through the harness, not the CLI; the planner leans to listing `claude` as
  required only for the workflows that shell to it, which today is none in the plugin.
