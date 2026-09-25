---
schema_version: 1
id: doc-idea-realization-plugin-end-to-end
code: PLAN-048.08
title: Idea-realization plugin — the end-to-end exercise and handover
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin]
depends_on: [doc-idea-realization-plugin]
parent: doc-idea-realization-plugin
---

# The end-to-end exercise and handover

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-08`. Covers `REQ-031` R22.

## Context and scope

Every earlier phase proves its part against fixtures. None proves that the plugin installs into a
repository that is not this one and that the parts work together from a person's seat. The brief
for this build (`_working/session-manager/plugin-build-2026-09-25.md` §5) sets the done condition:
installed and exercised once in a scratch repository, with the output shown to the owner.

## Decisions

- **The scratch repository is created outside this repository and its worktrees**, empty, with
  `git init`, and the plugin is added by local path (`/plugin marketplace add <path>` needs a
  marketplace file; the documented alternative for a local plugin directory is checked in this
  phase and the README records the one that works). Rejected: exercising inside a worktree of this
  repository (the R02 and R21 checks would not be exercised against a foreign layout).
- **The exercise runs every feature once, in pipeline order**, and the record quotes real output.
  Rejected: a checklist of "ran, passed".
- **Small defects are fixed in this phase with a test; the rest become ideas.** Rejected: fixing
  everything found (an unbounded phase).

## Work and dependencies

1. Scratch repository; install; prerequisites; scaffold `--feature all`; doctor.
2. Record, fold, render, triage an idea; run one partition sweep on a corpus of a few ideas
   (audit 2 must run); write a requirement and plan from the templates and `plan-check` them;
   register and claim a phase; allocate a code; render the catalog; doctor again.
3. README install and use sections; session record (`--next-code session`); the handover note
   appended to `_working/session-manager/restart-2026-09-25.md` and the board line.

Prerequisites: `phase-plug-03` and `phase-plug-07` (everything else is upstream of them).

## Acceptance and verification

As the backlog entry states. The case that must fail: a scaffold over the scratch repository's
second run creating a file; audit 2 not running.

## Execution order

Runs last, after phase-plug-03 and phase-plug-07, alone on sys-plugin. Every plugin phase shares `sys-plugin` and the `plugins/idea-realization/` deliverable path, so the validator allows one at a time; the overview's Execution order section gives the full sequence.

## Out of scope

Installing into any of the owner's real repositories; that is the owner's own step after this
plan, tracked under idea `000440`'s per-repository file.

## Open questions

- Which of the owner's repositories is the first real target, and when. Owner, after this plan;
  not a question for the plugin.
