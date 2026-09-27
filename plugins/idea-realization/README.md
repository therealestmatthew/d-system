# idea-realization

A Claude Code plugin that carries an idea from capture through triage, partition, planning, phases
and backlog to governed documents, in any git repository.

## Install

The plugin loads from a local path; this directory carries no marketplace file. Start Claude Code
in the target repository, or in one of its worktrees, with:

```bash
claude --plugin-dir path/to/idea-realization
```

Its skills then appear as `idea-realization:<skill>`, and its agents as
`idea-realization:<agent>`. A persistent install comes from adding the plugin to a marketplace of
your choosing.

Then, once per repository:

1. **Check the machine.** `/idea-realization:prerequisites` checks Python 3.12+, `uv`, `git` and,
   for triage and partition, the `claude` CLI. It installs nothing without a yes.
2. **Scaffold.** `/idea-realization:scaffold` asks which features to set up (`ideas`,
   `partition`, `backlog`, `documents`, or all four), shows a dry run, and asks separately before
   adding the staging directory to `.gitignore`. It never overwrites a file; running it again
   reports every path as `skipped … (exists)` and creates nothing.
3. **Confirm.** `/idea-realization:doctor` reports every recorded file as unchanged, drifted or
   missing. Right after a scaffold every line reads `unchanged`.
4. **Commit** the scaffolded files, `.gitignore` and `.idea-realization/install-state.json`.
5. **Bring the ignore rule to the primary checkout.** The partition sweep writes into the
   primary checkout's staging directory whichever worktree it runs from, and refuses to write
   while that directory is not gitignored there. If you scaffolded in a worktree, merge the
   scaffold commit into the branch the primary checkout has out before the first sweep.

## Use

The skills follow the pipeline in this order. Each one reads your saved plugin options and
otherwise uses the defaults under *Configuration*.

### Ideas

- **Record.** `/idea-realization:idea` records an idea as given, with a generated id and
  timestamp, and re-renders the view. The same skill amends, annotates, links and moves an idea's
  status; the log is append-only, and `idea.py show <id>` prints an idea's current state with
  every amendment applied.
- **Triage.** `/idea-realization:idea-triage <id>` triages one open idea per run: the triage agent
  searches `triage_search` and writes one finding, the skill checks the finding landed on that
  idea, then moves it to `triaged`. Proposed links and promotions are reported for you to run,
  never written.
- **Partition.** `/idea-realization:partition-ideas` groups the triaged ideas into programmes and
  fine groups. It builds a corpus, dispatches two analysts, an audit, a synthesis and a second
  audit, and stops at three gates for your ruling. If any idea is still open, it first asks
  whether to triage them or partition without them.
  Nothing reaches the idea log; on your acceptance, the partition is copied into
  `partitions_dir` for you to commit.

### Documents

Governed documents live under `docs_root`, in the folder `codes.yaml` names for their kind
(`plans/`, `requirements/`, `decisions/` and so on by default), each with YAML front matter.

1. Allocate the code with `/idea-realization:next-code <kind>`; never choose one by hand. The code
   is reserved against every other worktree of the repository, so two sessions never receive
   the same one.
2. Start from `templates/requirement.md` or `templates/plan.md`. Name the file
   `<CODE>-<slug>.md`, fill the front matter, and keep the headings.
3. Every system a document names must be registered in `<docs_root>/systems.yaml`. A system with
   no paths in the repository yet takes `status: planned`.
4. `/idea-realization:plan-check <plan>` checks a plan for the sections it needs.
5. `/idea-realization:catalog` regenerates `<docs_root>/catalog.md`. Run it after any document or
   backlog change; the check fails while the committed catalog is stale.

### Phases and sessions

- **Register a phase** by adding it to `backlog_path` against
  `.idea-realization/schemas/backlog.schema.json`, and name it in `next_up` to put it at the front
  of the queue. Regenerate the catalog afterwards.
- **Choose.** `/idea-realization:backlog` runs the checks, shows the ready queue with each phase's
  prerequisites and conflicts, and orients on one phase. It never claims.
- **Start.** `/idea-realization:session-start <phase>` asks before claiming, commits the claim on
  `integration_branch` in the primary checkout, and cuts the phase's branch and worktree under
  `worktree_dir`.
- **Record progress.** `/idea-realization:checkpoint` writes where the work stands into the
  session record and never completes the phase.
- **Close.** `/idea-realization:session-close` finalizes the session record, runs an independent
  review, and marks the phase complete only when verification is green and the review is clean.

### Checking and reference

`uv run scripts/check.py` runs every installed feature's check; `--feature <name>` runs one.
`/idea-realization:doctor` compares the install record with the disk. It reports a data file you
have edited since the scaffold, such as the idea log or the backlog, as drifted. The `tools`
skill answers which script does what from `docs/tools.md`, and `docs/` holds the protocol,
backlog, reporting and review documents the skills follow.

## Skills

| Skill | What it does |
|---|---|
| `prerequisites` | Checks Python 3.12+, `uv`, `git` and, for triage and partition, the `claude` CLI; installs what is missing only after a yes |
| `scaffold` | Creates each chosen feature's directories and seed files, never overwriting, and records every file written |
| `doctor` | Reports every recorded file as unchanged, drifted or missing; changes nothing |
| `idea` | Records an idea, or amends, annotates, links, classifies or moves one, through the idea writer |
| `idea-triage` | Triages one open idea with the triage agent and moves it to `triaged` |
| `partition-ideas` | Runs a partition sweep over the triaged ideas, stopping at each gate |
| `next-code` | Allocates and reserves the next free document code for a kind, or releases one |
| `plan-check` | Checks a plan draft for its required sections |
| `catalog` | Regenerates the document catalog |
| `backlog` | Checks the repository, shows the ready queue and orients on one phase |
| `session-start` | Claims a phase after a yes and cuts its branch and worktree |
| `checkpoint` | Records progress on the active phase without completing it |
| `session-close` | Finalizes the session record, runs the independent review, and completes the phase when it holds |
| `tools` | Answers which script does what from the generated tools reference |

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
| `worktree_dir` | `../<repository>-worktrees`, with `<repository>` replaced by the primary checkout's directory name; resolved against the primary checkout from any worktree |
| `triage_search` | `docs` |
| `exempt_files` | none |
| `staging_dir` | `.idea-realization/staging`, which must be gitignored |
| `partitions_dir` | `ideas/partitions` |

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
