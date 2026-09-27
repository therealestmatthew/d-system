---
schema_version: 1
id: doc-session-plugin-partition-sweep
code: SESS-2026-09-26-08
title: Idea-realization plugin partition sweep — corpus script, skill, agents, pack, record schema
kind: session
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-plugin-partition]
depends_on: [doc-idea-realization-plugin-partition]
---

# Idea-realization plugin partition sweep — corpus script, skill, agents, pack, record schema

## Phase

`phase-plug-03` — The partition sweep with its second audit unblocked. Claimed by
`agent-standby-builder` at `4edc1f1` on assignment from the Session Manager, with the owner's
approval in this session.

## Verification

Run in `../d-system-worktrees/phase-plug-03` on `agent/phase-plug-03`, rebased onto local `dev`
at `20febd5`, after the review fix `d1826be`.

```text
$ cd plugins/idea-realization && uv run pytest
490 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (1033 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 384 documents, 33 memories, 323 backlog phases
```

The repository gate, also run in the worktree after the rebase:

```text
$ uv run pytest
1115 passed, 1 warning

$ uv run ruff check src/ test/
All checks passed!

$ uv run mypy src/
Success: no issues found in 46 source files
```

A smoke run from an unrelated directory against a scratch repository
(`uv run --no-project --script`): `idea.py add` and `status … triaged`, then `idea_corpus.py
locate` (exit 0, `staging ignored: yes`), `build --status triaged` (corpus size 1) and
`prompt R4`, which printed the block with absolute paths into the scratch repository's staging
directory. The scratch repository's `git status` showed only the idea log the writer created.

## Acceptance

- **The corpus builder test reads the manifest's status selection for `--status open` on a
  fixture log** — Met. `test_status_open_selects_open_ideas_and_the_manifest_records_it` builds
  from a four-idea fixture log and asserts `manifest["status"] == ["open"]` and the one open id.
- **A fixture record validates; a record with a seven-digit id fails** — Met.
  `test_a_fixture_record_validates` and `test_a_record_with_a_seven_digit_id_fails`.
- **The skill's A2 step names an absolute path built from git worktree list, no step stops for a
  ruling this repository's copy stops for, and a non-ignored staging directory stops the skill
  before writing** — Met. Step 6 of the skill passes `name`'s absolute path, built from the first
  `git worktree list` entry; `test_the_second_audit_names_the_draft_by_its_absolute_primary_checkout_path`
  checks the path against `git worktree list` from a worktree, and
  `test_the_skill_does_not_stop_for_a_ruling_before_the_second_audit` checks the step's text.
  `test_a_staging_directory_that_is_not_gitignored_stops_the_sweep_before_writing` shows `locate`
  exit 1, `build` exit 1, `prompt` refusing, and no staging directory created.
- **The R02 check passes and fails on a pack that still names a source document** — Met.
  `test_plugin_names_no_source_instance` passes over the plugin tree;
  `test_the_source_reference_check_fails_on_a_pack_that_names_a_source_document` appends a
  document code to a copy of the pack and gets exactly one `document code` hit.

## Backlog

`status: active`, `session: doc-session-plugin-partition-sweep`. `next_action`: built on
`agent/phase-plug-03` and verified; every acceptance condition met at the close checkpoint;
waits for the owner's merge approval, then the completion edit on `dev`.

## Unresolved

- The peer phase building governance documents (`phase-plug-07`) adds `test/test_no_history.py`,
  which scans `plugins/idea-realization/docs/` for history words. Whichever branch merges second
  runs it over the other's docs after rebasing. `partition-pack.md` and this phase's
  `repository-layout.md` lines were written to pass it.

## Review

An independent `demo-adversary` agent reviewed `dev...HEAD` (then `2a525f1`, `f6ad374`,
`f67db21`) against the phase's scope and acceptance, and ran the four verification commands
itself. Its findings, condition by condition:

- **Blocker** — "The staging-directory gitignore guard is bypassed whenever `staging_dir`
  resolves to a path outside any git repository." `is_ignored` returned `None` there, and
  `guard_write` and `_locate` refused only on `False`: `locate` exited 0 with `staging ignored: no
  checkout`, and `build --status open` wrote `corpus/` into the outside directory. Reproduced
  through the CLI. Minimal fix named: treat no enclosing repository as not ignored, and add the
  missing negative test.
- **Other areas attacked, no discrepancy found**: R02 provenance removal (the six blocks
  "unchanged in substance", every source path replaced by a placeholder or generic phrase); the
  control property of `corpus-R4.md` and the `R4` block; the schema fixture tests ("real, not
  vacuous"); the manifest status test; `start` only renames into `previous-<date>/`; the A2
  absolute path and the absence of a stop before it; primary-checkout resolution from a worktree;
  the pair check and `accept`'s refusal to overwrite; the skill's command block run verbatim; the
  widened deliverables matching the owner's ruling; all four verification commands clean.
- **Per condition**: 1 Met; 2 Met; 3 "Partially not met" (the A2 half met, the non-ignored half
  not met for a directory outside any checkout); 4 Met.

Fixed in `d1826be`. The same reviewer re-checked it against its own reproduction: "`locate` now
refuses (exit 1) and `build` now refuses (exit 1) and creates nothing", the ignored in-repository
case still exits 0, and the plugin suite ran `490 passed`. Verdict: "**Fixed.** No new finding
from this re-check."

## Decisions

- **The analysts and the adversary are plugin-local agents** (`agents/partition-analyst.md`,
  `agents/partition-adversary.md`), dispatched as `idea-realization:partition-analyst` and
  `idea-realization:partition-adversary`. This settles the child plan's open question: a plugin
  cannot depend on a target repository's agents. The owner chose to record it here rather than
  amend `PLAN-048.03`.
- **The sweep's helpers are subcommands of `scripts/idea_corpus.py`** (owner, this session):
  `locate`, `start`, `build`, `prompt`, `report`, `name`, `check`, `accept`. The source
  runner's four inline Python blocks became tested code. `build` keeps `--status` and `--out`,
  and takes `--exclude`, an optional file of idea ids, off by default.
- **The pack's blocks carry placeholders filled at extraction** (owner, this session):
  `{corpus_dir}`, `{idea_log}`, `{systems_registry}`, `{draft}`, `{check_command}`. `prompt`
  substitutes absolute paths in the primary checkout, refuses to emit a block with an unfilled
  placeholder, and saves exactly the sent text as `dispatch-<section>.txt`.
- **The accepted partition is copied to a new option, `partitions_dir`** (owner, this session;
  default `ideas/partitions`, outside `docs_root` so the document scan does not demand front
  matter). `accept` copies the pair there, marks the copy `accepted` and re-points its
  `markdown`. This widened the phase's deliverables with `plugin.json`, the README, the
  repository-layout reference and `test/test_paths.py`.
- **The draft lives in the primary checkout's staging directory** from synthesis on, per the
  child plan, so audit 2 reads it at an absolute path and the skill does not stop before it.
- **The corpus writes only `corpus-R1.md` and `corpus-R4.md`.** The pack dispatches no `R2` or
  `R3`. The manifest keeps `shuffle_seed` as the build's identifying number, because the run
  stamp and the record schema key on it.
- **The record schema's `markdown` pattern accepts any repository-relative directory**, since the
  draft's and the accepted copy's directories are both configurable.

## Corrections

- **The staging guard let a directory outside any checkout through.** `is_ignored` returned
  `None` when no enclosing repository existed, and `guard_write` and `locate` refused only on
  `False`, so a `staging_dir` outside every checkout passed `locate` and `build` wrote the corpus
  there. The independent review found it; `d1826be` makes anything but an accepted
  `git check-ignore` a refusal and adds the test for that case.
- **The tools reference went stale after a docstring edit.** It was regenerated before a
  one-line change to `idea_corpus.py`'s usage text; the rebase run caught it and `f67db21`
  regenerated it again.

## Left undone

- Running a sweep end to end with real dispatches is `phase-plug-08`'s exercise.
- Completion: the phase stays `active` until the owner approves the merge onto `dev`, which is the
  third condition for completing it.
