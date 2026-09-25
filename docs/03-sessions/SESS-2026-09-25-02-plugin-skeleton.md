---
schema_version: 1
id: doc-session-plugin-skeleton
code: SESS-2026-09-25-02
title: Idea-realization plugin skeleton, prerequisites, scaffold and doctor
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-core]
depends_on: [doc-idea-realization-plugin-skeleton-install]
---

# Idea-realization plugin skeleton, prerequisites, scaffold and doctor

## Phase

`phase-plug-01` — Plugin skeleton, prerequisites skill, scaffold with install-state record, and
doctor.

## Verification

Run in `../d-system-worktrees/phase-plug-01` on `agent/phase-plug-01`, Claude Code 2.1.280.

```text
$ cd plugins/idea-realization && uv run pytest
63 passed

$ claude plugin validate plugins/idea-realization --strict
Validating plugin manifest: .../plugins/idea-realization/.claude-plugin/plugin.json
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (938 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 359 documents, 32 memories, 318 backlog phases
```

The worktree has no `_private/`, so the staged check ran its path check only. The content check was
run separately from the primary checkout: its `confidential_identifiers()` against every file under
`plugins/idea-realization/` in this worktree, printing counts only —
`31 identifiers, 27 plugin files, 0 problems`.

Repository gates, same worktree: `uv run ruff check src/ test/` — `All checks passed!`;
`uv run mypy src/` — `Success: no issues found in 46 source files`; `uv run pytest` —
`1080 passed, 1 warning`; `git diff --exit-code docs/08-governance/catalog.md` — no change.

Loading check (behavioural), run headless from a scratch git repository outside this one:
`claude -p "<prompt>" --plugin-dir .../plugins/idea-realization "--allowedTools=Bash(uv run:*)"`.
The session listed the skills as `idea-realization:doctor`, `idea-realization:prerequisites`,
`idea-realization:scaffold`; quoted the doctor skill's command with the root substituted,
`uv run "/code/d-system-worktrees/phase-plug-01/plugins/idea-realization/scripts/doctor.py"`; and
ran `uv run <root>/scripts/paths.py --root .`, whose output began `root: <scratch repository>` and
`ideas_path: <scratch repository>/ideas/ideas.jsonl` and listed all ten keys with their defaults.

Manifest facts checked with the same CLI before the manifest was fixed, on scratch fixtures:
a manifest with `"license": "MIT"` gives `✔ Validation passed` and exit 0 under `--strict`; one with
an unknown top-level key gives `bogus: Unknown field 'bogus'. Claude Code ignores it at load time.`,
`✘ Validation failed (--strict treats warnings as errors)`, exit 1. A saved option substitutes into
skill text (`--settings` with `pluginConfigs["idea-realization@inline"]` gave `custom/x.jsonl`); an
unsaved one stays literal as `${user_config.ideas_path}`, the manifest default is not substituted;
a `multiple` option substitutes comma-joined (`docs/a b.md,x.md`).

## Acceptance

- `validate --strict` exits 0; a fixture with a license field or an unknown key fails --strict —
  Met for validation and the unknown key (`test_manifest.py`, run against the live CLI). The
  license half cannot hold: `license` is a valid manifest field and `--strict` passes it. Owner
  ruling this session: enforce "no license" with the plugin's own test
  (`test_manifest_names_the_plugin_and_has_no_licence`) and correct the wording (Unresolved).
- `--plugin-dir` lists the skills in a new session and `${CLAUDE_PLUGIN_ROOT}` resolves — Met, see
  the loading check above.
- Scaffold: one hash per created file, a no-op second run reporting skipped, a pre-existing
  `backlog.yaml` byte-identical, a dry run that writes nothing — Met (`test_scaffold.py`).
- Prerequisites without `uv` exits 1 naming `uv` and its install command and changes no file; only
  `--yes` installs — Met (`test_prerequisites.py`: a subprocess run with `PATH` holding only `git`,
  and in-process runs with a recording installer).
- R02 check passes over the plugin tree and fails on a fixture containing a phase id — Met
  (`test_no_source_references.py`).
- Scripts copied to a temporary directory run against a temporary data root; no `parents[` or
  `from src` in `scripts/` — Met (`test_scripts_portable.py`).

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: run `/session-close` up to its
independent review, then send READY to the Session Manager; the phase completes only after the
owner-approved merge. `session: doc-session-plugin-skeleton`; `completion_evidence` cites
`plugin.json`, `paths.py`, `scaffold.py`, the scaffold and R02 tests, and this record; `result`
describes the build as not yet reviewed or merged.

## Unresolved

- **Wording correction awaiting approval** (owner chose "own test + fix wording"). Proposed text:
  - backlog acceptance, first entry: "claude plugin validate plugins/idea-realization --strict exits
    0; a fixture manifest with an unknown top-level key fails --strict; a test asserts plugin.json
    has no license key."
  - `REQ-031` R01 verification: "`claude plugin validate plugins/idea-realization --strict` exits 0.
    A fixture copy with an unknown top-level key fails `--strict`. A test asserts `plugin.json` has
    no `license` field."
- **Decisions made in this phase that later plugin phases inherit:**
  - Owner: the code register and systems registry are scaffolded at `<docs_root>/codes.yaml` and
    `<docs_root>/systems.yaml`; schemas are copied to `.idea-realization/schemas/`.
  - Owner: the scaffold's consent-gated write is `.gitignore` only (the staging directory line); it
    never writes `.claude/settings.json` or a hook. A later phase that needs one adds it.
  - Skills pass saved options as `CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'`,
    single-quoted: bash rejects the unsubstituted text inside double quotes ("bad substitution"),
    and `CLAUDE_PLUGIN_OPTION_*` is not exported to the Bash tool. `paths.py` treats unsubstituted
    text as unset. `test_skills.py` enforces the quoting.
  - Feature modules in `scripts/checks/<feature>.py` expose `check(config)` and/or `COMMANDS`;
    `check.py` and `cli.py` discover them.
  - Planner calls (PLAN-048 Q3 and the child plan's open question): `claude` is required only with
    `--feature triage|partition|all`, as `REQ-031` R04 states, otherwise reported optional;
    `worktree_dir` defaults to `../<repository>-worktrees`, derived from the repository directory's
    name at resolve time.
  - Seed files follow this repository's current schemas' required fields (priority:
    `schema_version`, `updated`, `next_up`; backlog: `schema_version`, `updated`, `max_active`,
    `next_up`, `items`, without `decision_record`). `phase-plug-02` and `phase-plug-04` own those
    formats; if their schemas differ, the seeds need an edit in `scripts/scaffold.py`, which is
    outside their declared deliverables.
