# idea-realization tools

Generated from the scripts themselves. Never edit this file by hand. Regenerate it,
from the directory its paths are relative to, with
`generate_tool_docs.py --root . --tools scripts --reference docs/tools.md --title 'idea-realization tools' --invocation 'uv run "${CLAUDE_PLUGIN_ROOT}/scripts/{name}"' --preamble-from paths.py`;
`--check` with the same arguments compares the committed file with a fresh render.

## Configuration

The one place a script resolves a configured value.

Every key is resolved with one precedence:

1. a command-line flag (``--ideas-path``),
2. the environment variable ``IDEA_REALIZATION_<KEY>``,
3. the plugin option ``CLAUDE_PLUGIN_OPTION_<KEY>``,
4. the default declared in ``.claude-plugin/plugin.json``.

Claude Code exports ``CLAUDE_PLUGIN_OPTION_<KEY>`` to hooks only. A skill passes the saved option
to a script by prefixing the command with ``CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'``,
single-quoted because the shell rejects the unsubstituted text inside double quotes.
When the option was never saved, Claude Code leaves that text unsubstituted, so a value that still
reads ``${user_config.`` counts as unset.

Relative paths resolve against the repository root: ``--root``, then ``IDEA_REALIZATION_ROOT``,
then ``CLAUDE_PROJECT_DIR``, then the git top level of the working directory, then the working
directory. No path is ever derived from a script's own location except the plugin's own files.

## `check.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
```

Run every installed feature's check against the target repository.

Each feature contributes ``check(config)`` from ``scripts/checks/<feature>.py``. Exit 0 when every
check is clean, 1 when any reports a problem, 2 when a named feature has no check.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--feature` |  |  |  |  |

Shared configuration flags: every configured path and value, resolved by the shared configuration precedence rule.

Exit codes found in source: 2.

## `cli.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py"
```

Run one feature command, such as ``ready``, ``next-code`` or ``catalog``.

Each feature contributes ``COMMANDS`` from ``scripts/checks/<feature>.py``; the command receives
every argument after its name. Exit 2 when the command is unknown.

No command-line arguments.

Exit codes found in source: 0, 2.

## `codes.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/codes.py"
```

Document code series, allocation, register consistency and the catalog.

Two numbering modes exist. Counter series take the next free three-digit number in the series,
with an optional ``.NN`` sub-code under a parent plan; dated series derive their code from the
document's own date plus a same-day sequence, so kinds written by several sessions at once never
contend on one counter.

Run directly, this script is the ``next-code`` command: it scans the document root, then
allocates the next free code for a kind and holds it with a pre-merge reservation (see
``reservations.py``) before printing it, so two worktrees allocating the same kind before either
merges receive different codes. Never choose a code by hand.

Exit codes: 0 with the code printed; 1 when the document tree fails its check or no code can be
allocated; 2 on a usage error.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `kind` | document kind, as the code register's series names it |  |  |  |
| `--parent` | allocate a sub-code under this plan's code |  |  |  |

Shared configuration flags: `--root`, `--docs-root`, `--exempt-files`, `--backlog-path`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1.

## `doctor.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py"
```

Compare every path the install-state record names against the disk. Changes nothing.

Each recorded file is reported as unchanged, drifted (its SHA-256 differs from the record) or
missing; each recorded directory as unchanged or missing. A file changed under recorded consent,
such as ``.gitignore``, is reported the same way but marked as consented, since people edit it.

Exit codes: 0 when every recorded file and directory is unchanged, 1 when any has drifted or is
missing, 2 when there is no install-state record.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--root` |  |  |  |  |

Exit codes found in source: 2.

## `documents.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/documents.py"
```

Scan the governed document tree, check it, and render its catalog.

Run directly, this script is the ``catalog`` command: it scans the document root and, when the
tree is clean, writes ``<docs_root>/catalog.md``. The ``check`` command compares that committed
file with a fresh render, so a hand-edited or stale catalog fails.

What the scan reads, all under the configured document root (``docs_root``):

- every Markdown file, except ``catalog.md`` and the configured ``exempt_files``, as a governed
  document whose YAML front matter must satisfy ``schemas/document.schema.json``;
- ``codes.yaml``, the code register (``schemas/codes.schema.json``);
- ``systems.yaml``, the systems registry and owner directory (``schemas/systems.schema.json``).

**The contract other features rely on.** ``scan(config)`` returns a ``Scan``:

- ``documents`` — ``{document id: front matter}`` for every governed document, each mapping
  carrying two added keys: ``path``, the file's path relative to the repository root, and
  ``location``, its path relative to the document root;
- ``systems`` — ``{system id: registry entry}``;
- ``owners`` — ``{owner key: accountable role}``;
- ``register`` — the parsed code register;
- ``errors`` — every problem found, one line each; empty when the tree is clean.

A consumer, such as the backlog check, resolves document ids, system ids and owner keys against
these three mappings rather than scanning the tree itself, so there is one scanner.

Exit codes: 0 when the catalog was written; 1 when the document tree fails its check, in which
case nothing is written; 2 on a usage error.

Shared configuration flags: `--root`, `--docs-root`, `--exempt-files`, `--backlog-path`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1.

## `generate_tool_docs.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/generate_tool_docs.py"
```

Generate tool reference documentation from each script's docstring, arguments and exit codes.

Every script is read with ``ast`` and never imported, so documenting a script never runs it. Two
modes share one renderer:

- **Paired documents** (the default). Each script in ``--tools`` is paired with the operations
  document in ``--docs`` whose filename matches ``--pattern`` with the script's stem, underscores
  as hyphens, in place of ``{slug}``. The narrative half of that document is hand-written and never
  touched; the reference half lives between two markers this script owns::

      <!-- generated:tool-reference:start -->
      <!-- generated:tool-reference:end -->

  A script with no paired document is reported and left alone; writing one is a person's decision.
- **One reference document** (``--reference``). Writes a whole document with one section per
  script, in name order: its purpose, its invocation, its arguments and its exit codes. A script
  named by ``--preamble-from`` has its docstring stated once at the top instead of a section; a
  script that adds the shared path flags (``paths.add_arguments``) lists them and refers back to it.

Either mode with ``--check`` writes nothing and reports every stale or unpaired file. Relative
paths resolve against the repository root.

Exit codes: 0 when everything was written or is current; 1 under ``--check`` when a file is stale
or a script is unpaired, naming each file; 2 on a usage error, such as a paired document with no
generated block.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--tools` | directory holding the scripts to document |  | tools |  |
| `--docs` | directory holding the paired operations documents |  | docs/governance |  |
| `--pattern` | filename pattern of a paired document; {slug} is the script stem |  | OPS-*-{slug}.md |  |
| `--reference` | write one reference document to FILE instead of paired documents |  |  |  |
| `--title` | title of the reference document |  | Tools reference |  |
| `--invocation` | how to run a script, shown in the reference; {name} is its filename |  | uv run {name} |  |
| `--preamble-from` | script whose docstring opens the reference instead of a section |  |  |  |
| `--exclude` | script filename to leave out; repeatable |  | [] |  |
| `--check` | write nothing; exit 1 if any output is stale or a script unpaired |  |  |  |

Shared configuration flags: `--root`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1, 2.

## `generate_workflows.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/generate_workflows.py"
```

Render host-specific workflow adapters from canonical workflow sources and a manifest.

The manifest names one Markdown source per workflow and declares its authority, the capabilities
it requires, and the adapters to generate: Claude skills, commands and agents, Open Agent Skills,
and Codex agents. This script validates that contract, then writes each adapter deterministically.
Generated adapters are never edited by hand; ``--check`` reports any that are missing or differ.

An owner-only workflow may not target an agent-discoverable kind (skill, agent or command), and a
capability a workflow requires must be mapped or explicitly declared unsupported on every target.

Start from the plugin's empty manifest template, ``templates/workflows.yaml``. Every path in the
manifest is relative to the repository root.

Exit codes: 0 when every adapter was written or is current; 1 under ``--check`` when an adapter is
missing or stale, naming each; 2 when the manifest is invalid.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--manifest` | the workflow manifest, relative to the repository root |  | agent-workflows/workflows.yaml |  |
| `--sources` | directory every workflow source must live in; default: the manifest's directory |  |  |  |
| `--output-root` | directory the adapters' paths are relative to; default: the repository root |  |  |  |
| `--check` | write nothing; exit 1 if an adapter is missing or stale |  |  |  |

Shared configuration flags: `--root`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1, 2.

## `plan_check.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py"
```

The mechanical section check for a plan draft.

A section is present when the draft has a line of ``## `` or ``### `` followed by one of that
section's accepted headings, exactly, case-sensitive, with nothing after it. Lines inside a fenced
code block do not count. Six sections are always required; two are conditional:

- ``Requirement coverage``, when ``depends_on`` names a document of kind ``requirement`` (looked
  up under the document root). A plan paired with a requirement satisfies Verification with the
  same heading.
- ``Concurrency``, when the draft names two or more distinct backlog phase ids, outside fenced
  lines.

It reads headings only; whether the sections say anything useful is a reviewer's judgement.

Exit codes: 0 when every draft has every section it needs; 1 when any section is missing, one
``<draft>: missing: <section>`` line each; 2 when a draft cannot be read.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `drafts` | plan draft files to check |  |  |  |

Shared configuration flags: `--root`, `--docs-root`, `--exempt-files`, resolved by the shared configuration precedence rule.

Exit codes found in source: 2.

## `prerequisites.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/prerequisites.py"
```

Check what the plugin's scripts need on this machine, and install what is missing on --yes.

Checks Python 3.12 or later, ``uv`` and ``git``; with ``--feature triage`` or ``--feature
partition`` also the ``claude`` CLI. Each missing item is reported with the exact command that
installs it. Without ``--yes`` nothing is installed and no file is changed.

Uses only the standard library, so it runs with a bare ``python3`` on a machine without ``uv``.

Exit codes: 0 when everything required is present, 1 when something is still missing.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--feature` | the features that will be used; triage and partition need claude | ideas, triage, partition, backlog, documents, all | [] |  |
| `--yes` | install every missing required item; without it nothing is installed |  |  |  |

Exit codes found in source: 0, 1.

## `render_template.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py"
```

Render one of the plugin's templates, such as the working agreement, by filling its placeholders.

A placeholder is ``{{name}}``. Four are known: ``integration_branch`` and ``worktree_dir``, which
default to the configured values, and ``data_root`` and ``confidential_dir``, which have no
default and must be given with ``--set``. A template naming any other placeholder is refused
before anything is written, and so is a rendering that would leave a ``{{`` behind.

The rendered file is written to ``--output`` (relative to the repository root), or printed when
none is given. An existing file is never overwritten: a repository that already has one keeps it,
and a person merges the rendered text by hand.

Exit codes: 0 when the file was rendered; 1 when a placeholder is unknown or has no value, or the
output file exists; 2 on a usage error.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `template` | the template file, such as templates/AGENTS.md |  |  |  |
| `--set` | a placeholder value; repeatable |  | [] |  |
| `--output` | file to write, relative to the repository root; printed when omitted |  |  |  |

Shared configuration flags: `--root`, `--integration-branch`, `--worktree-dir`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1, 2.

## `reservations.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reservations.py"
```

Pre-merge reservations for document codes, shared by every worktree of one repository.

Allocating a code from committed state alone is not enough: two worktrees that allocate the same
kind before either merges read the same committed state and compute the same code, and the
second discovers the collision only at merge. A reservation has to be visible to the second
caller before the first has merged, which rules out every tracked file, the code register
included: a reservation committed on one branch is invisible on another until it merges.

The one location every worktree of a repository already shares, with no commit and no merge, is
the git common directory: ``git rev-parse --git-common-dir`` resolves to the same ``.git`` from
the primary checkout and from every linked worktree. Reservations live there, untracked, and
never enter history. A reservation is machine-local state about work in flight, meaningless to a
fresh clone.

Mutual exclusion is the filesystem's. Each reservation is one file created with
``O_CREAT | O_EXCL``, which the kernel guarantees to be atomic: of two callers racing for the
same code, exactly one create succeeds and the loser tries the next candidate. A crash between the
create and the write leaves an empty file, which still holds its code; ``prune`` falls back to the
file's mtime so such a reservation still expires.

**A reservation is released by time or by hand, never by observing that the document exists.**
The document scan reads the local working tree, so an allocating worktree would retire its own
reservation while its document is still unmerged and invisible to peers, and the next peer would
be handed the same code. A reservation whose document has landed costs nothing: the allocator
skips that code anyway.

Run directly, this script lists the reservations held, or releases one that ``next-code`` took
for a document that will never be written.

Exit codes: 0 on success; 1 when ``--release`` names a code no reservation holds, or outside a
git repository; 2 on a usage error.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `code` | the code to release; omit to list reservations |  |  |  |

Shared configuration flags: `--root`, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1, 2.

## `scaffold.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py"
```

Create the directories and seed files each feature needs in the target repository.

Never overwrites a file that exists: every such path is reported as skipped and left
byte-identical. Every file written is recorded, with its SHA-256, in
``.idea-realization/install-state.json``. ``--dry-run`` reports the same plan and writes nothing.

The target's ``.gitignore`` is changed only with ``--consent gitignore``, and that consent is
recorded. The scaffold never writes ``.claude/settings.json`` or a hook.

Exit codes: 0 on success, 2 on a usage error.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--feature` | feature to scaffold; repeatable |  |  |  |
| `--dry-run` | report the plan; write nothing |  |  |  |
| `--consent` | allow the scaffold to change this file; recorded in the state | gitignore | [] |  |

Shared configuration flags: every configured path and value, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 2.
