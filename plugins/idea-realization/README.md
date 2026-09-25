# idea-realization

A Claude Code plugin that carries an idea from capture through triage, partition, planning, phases
and backlog to governed documents, in any git repository.

This version ships the skeleton: the path resolver, the prerequisites check, the scaffold with its
install-state record, and the doctor. Later versions add each feature's scripts, skills and agents.

## Load the plugin

Load it for one session by pointing Claude Code at this directory:

```bash
claude --plugin-dir path/to/idea-realization
```

Its skills then appear as `idea-realization:<skill>`. A persistent install comes from adding the
plugin to a marketplace of your choosing; this directory carries no marketplace file.

## Skills

| Skill | What it does |
|---|---|
| `prerequisites` | Checks Python 3.12+, `uv`, `git` and, for triage and partition, the `claude` CLI; installs what is missing only after a yes |
| `scaffold` | Creates each chosen feature's directories and seed files, never overwriting, and records every file written |
| `doctor` | Reports every recorded file as unchanged, drifted or missing; changes nothing |

## Configuration

Every path a script reads is resolved by `scripts/paths.py`, in this order:

1. a command-line flag, such as `--ideas-path`;
2. the environment variable `IDEA_REALIZATION_<KEY>`, such as `IDEA_REALIZATION_IDEAS_PATH`;
3. the plugin option `CLAUDE_PLUGIN_OPTION_<KEY>`, which the skills set from your saved options;
4. the default in `.claude-plugin/plugin.json`.

Relative paths resolve against the repository root: `--root`, then `IDEA_REALIZATION_ROOT`, then
`CLAUDE_PROJECT_DIR`, then the git top level of the working directory. List options, such as
`triage_search`, are comma-separated, so a path in one cannot contain a comma.

| Option | Default |
|---|---|
| `ideas_path` | `ideas/ideas.jsonl` |
| `ideas_view_path` | `ideas/ideas.md` |
| `priority_path` | `ideas/priority.yaml` |
| `backlog_path` | `backlog/backlog.yaml` |
| `docs_root` | `docs` |
| `integration_branch` | `main` |
| `worktree_dir` | `../<repository>-worktrees`, with `<repository>` replaced by the repository directory's name |
| `triage_search` | `docs` |
| `exempt_files` | none |
| `staging_dir` | `.idea-realization/staging`, which must be gitignored |

`uv run scripts/paths.py` prints every resolved value.

## What the scaffold writes

| Feature | Paths |
|---|---|
| `ideas` | the idea log, the rendered view, the priority file, and the idea schemas |
| `partition` | the staging directory and the partition record schema; with `--consent gitignore`, a `.gitignore` line for the staging directory |
| `backlog` | the backlog and its schema |
| `documents` | the document root, `<docs_root>/codes.yaml`, `<docs_root>/systems.yaml`, and the document, code and systems schemas |

Schemas are copied to `.idea-realization/schemas/`. The install-state record is
`.idea-realization/install-state.json`: the plugin version, one entry per file written with its
SHA-256 and feature, one per directory created, and every consent given. Commit it, so a clone
knows what was installed.

## Scripts

Every script runs with `uv run scripts/<name>.py`, declares its dependencies inline (PEP 723:
`jsonschema` and `pyyaml` only), and prints its flags with `--help`. `prerequisites.py` uses only
the standard library, so it also runs with a bare `python3` when `uv` is missing.

`scripts/check.py` and `scripts/cli.py` are dispatchers. A feature adds a module
`scripts/checks/<feature>.py` defining `check(config)`, `COMMANDS`, or both, and both dispatchers
find it without being edited; `scripts/checks/__init__.py` states the contract.

## Tests

```bash
cd path/to/idea-realization && uv run pytest
```

The suite uses temporary fixtures only. `test/test_no_source_references.py` fails if any file in
the plugin names a particular repository, person, record id, commit or date.
