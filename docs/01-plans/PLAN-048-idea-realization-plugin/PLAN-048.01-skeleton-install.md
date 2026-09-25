---
schema_version: 1
id: doc-idea-realization-plugin-skeleton-install
code: PLAN-048.01
title: Idea-realization plugin — skeleton, prerequisites, scaffold and doctor
kind: plan
status: approved
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-core]
depends_on: [doc-idea-realization-plugin]
parent: doc-idea-realization-plugin
---

# Skeleton, prerequisites, scaffold and doctor

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-01`. Covers `REQ-031` R01,
R03, R04, R05, R06, R07, R21 and the R02 check.

## Context and scope

Nothing under `plugins/` exists. The plugin manifest format, `userConfig`, `${CLAUDE_PLUGIN_ROOT}`
and `claude plugin validate` are documented at `code.claude.com/docs/en/plugins/` (checked
2026-09-25). The install concepts — an install-state record with a hash per file, an ownership
guard that never overwrites an unrecorded file, a doctor that reports drift — are described in
`_working/session-manager/scout/ext-ecc.md` §2 and summarised in analysis 06 §2; the owner's
consent ruling for settings and hooks is in `_working/session-manager/reports/rulings-000347.md:98`
(Q15).

## Decisions

- **The manifest declares one `userConfig` entry per configurable path**, each with a default:
  `ideas_path` (`ideas/ideas.jsonl`), `ideas_view_path` (`ideas/ideas.md`), `priority_path`
  (`ideas/priority.yaml`), `backlog_path` (`backlog/backlog.yaml`), `docs_root` (`docs`),
  `integration_branch` (`main`), `worktree_dir` (`../<repository>-worktrees`),
  `triage_search` (`docs`), `exempt_files` (empty), `staging_dir` (`.idea-realization/staging`,
  which must be gitignored — the partition skill checks). Rejected: an environment variable per
  path only (nothing prompts for them). Cost: ten prompts on first use, once.
- **`scripts/paths.py` is the only path resolver.** Precedence: flag, environment variable
  (`IDEA_REALIZATION_<KEY>`), `CLAUDE_PLUGIN_OPTION_<KEY>` (how the harness exports `userConfig`
  to processes), default. Rejected: per-script handling. Cost: one import in every script.
- **The install-state record lives at `<target>/.idea-realization/install-state.json`**, with the
  plugin version, the time, one entry per file (path, SHA-256, feature) and a `consent` list.
  Rejected: `${CLAUDE_PLUGIN_DATA}` (per machine, not per repository; a clone would not know what
  was installed). Cost: one dot-directory in the target.
- **The plugin is loaded with `--plugin-dir` during the build; no marketplace file here.** The
  adversary verified with the live CLI that a persistent install needs a marketplace and that
  `--plugin-dir` loads a plugin per session; the owner ruled at G3 that the plugin joins a
  marketplace elsewhere later. Rejected: verifying the loading path in the last phase (every
  earlier phase would build on an unverified manifest shape). Cost: this phase's first step is the
  loading check, before the manifest is fixed, and every session that uses the plugin during the
  build passes `--plugin-dir`.
- **Scaffold features are selectable** (`--feature ideas|partition|backlog|documents|all`) so a
  target that wants only the idea log gets only its files. This is the workflow-sized install the
  `000439` ruling asked for, inside the single plugin.

## Work and dependencies

1. The loading check: `claude --plugin-dir plugins/idea-realization`, skills visible in a new
   session, `${CLAUDE_PLUGIN_ROOT}` resolving. If it fails, stop and report; nothing else in this
   phase is built on a shape that does not load.
2. `plugin.json`, directories, README stub, `pyproject`-free pytest configuration (`conftest.py`
   sets the scripts path), the PEP 723 header, `scripts/check.py` and `scripts/cli.py` as
   dispatchers over `scripts/checks/`. Verify with `claude plugin validate --strict`.
3. `scripts/paths.py` and its test (all four precedence levels).
4. `scripts/prerequisites.py` (check; install on `--yes` only) and `skills/prerequisites/SKILL.md`.
5. `scripts/scaffold.py` (features, dry run, never-overwrite, record, consent-gated settings,
   hooks and gitignore) and `skills/scaffold/SKILL.md`; `scripts/doctor.py`.
6. `test/test_no_source_references.py`: the R02 grep list, run over the plugin tree.

Prerequisite: none. This phase can run beside `phase-idg-01`.

## Acceptance and verification

As the backlog entry states: validate passes and a fixture with a `license` field fails; the
scaffold tests show the record, the no-op second run, the byte-identical pre-existing file and the
empty dry run; prerequisites without `uv` exits 1 naming `uv`; R02 passes and fails on a fixture
containing a phase id. The case that must fail: a scaffold run over a directory holding a
`backlog.yaml` must not change it.

## Execution order

Runs alone on the plugin tree (its deliverable is the whole directory); phase-idg-01 may be active at the same time on its own system. Every later phase declares a subpath and its own sub-system, so they run in parallel where their dependencies allow; the overview's Execution order section gives the waves.

## Out of scope

Any feature's actual scripts (later phases), uninstall, repair, a SessionStart hook.

## Open questions

- Whether `worktree_dir`'s default should derive from the repository directory name at scaffold
  time or stay a literal the person edits. Planner, in this phase; leans to deriving.
