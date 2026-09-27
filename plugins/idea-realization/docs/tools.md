# idea-realization tools

Generated from the scripts themselves. Never edit this file by hand. Regenerate it,
from the directory its paths are relative to, with
`uv run scripts/generate_tool_docs.py --root . --tools scripts --reference docs/tools.md --title 'idea-realization tools' --invocation 'uv run "${CLAUDE_PLUGIN_ROOT}/scripts/{name}"' --preamble-from paths.py`;
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

``worktree_dir`` is the exception: it names a directory beside the repository rather than a file
in one checkout, so it resolves against the primary checkout, the first entry of
``git worktree list``, and ``<repository>`` in it is the primary checkout's directory name. Run
from any worktree, it names the same directory.

## `backlog.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"
```

Backlog consistency and derived session queues; no database or state mutations.

Pure rules: every function takes dicts and returns errors or text, with no file or git access.
``checks/backlog.py`` reads the files, runs the document scan and calls these.

No command-line arguments.

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

## `idea.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py"
```

The only sanctioned writer for the idea log.

Ideas are an append-only event log. Nothing in it is ever edited, so a malformed line is
permanent — there is no correction path, only a longer history containing the mistake.
That is the whole reason this script exists instead of a convention: an agent formatting
its own entries will eventually format one wrongly.

The caller supplies prose. This script generates the identifier, the timestamp and the
event shape, validates the result against the plugin's ``schemas/idea.schema.json``, and
appends it.

**There is deliberately no way to supply a timestamp.** A log whose times can be chosen is
not evidence of anything. The ``at`` values below are generated internally and the CLI
exposes no option that reaches them.

Usage (every subcommand also takes ``--root``, ``--ideas-path``, ``--docs-root``,
``--backlog-path`` and ``--exempt-files``):

    idea.py add --file idea.md          # title = first line, rest = body
    idea.py add                         # same, from stdin
    idea.py add --title "..." --body "..."
    idea.py status <id> reviewing
    idea.py status <id> promoted --promoted-to <document code>
    idea.py status <id> delivered --doc <document code> --commit <hash>
    idea.py revisit <id>
    idea.py amend <id> --title "corrected title"
    idea.py annotate <id> --author repository-owner --kind note --file note.txt
    idea.py amend-annotation <id> <eid> --file corrected.txt
    idea.py link <id> --type relates_to --target <other id>
    idea.py link <id> --type relates_to --target-code <document code>
    idea.py retract-link <id> <eid>
    idea.py classify <id> --author <name> --file classification.json
    idea.py list [--status open]        # read-only: id, status and effective title
    idea.py show <id>                   # read-only: one idea's folded state as JSON

**``amend`` corrects the idea's ``created`` event rather than rewriting it** — nothing in an
append-only log can be rewritten. It always targets that idea's ``created`` event by identity,
never a position, so the correction survives a rebase or a merge that interleaves two
branches' appended lines. Amending the same idea twice appends two corrections that both
survive (the fold merges a chain of amendments rather than keeping only the latest). Title
and body are the only amendable fields, and neither can be cleared — every idea must have
both.

**``status`` into ``delivered``, ``resolved`` or ``absorbed`` needs at least one pointer** —
``--doc``, ``--phase`` or ``--commit``, each repeatable — naming where the delivery happened.
Each must resolve: a code carried by a governed document under the document root, a phase id
in the backlog, or a commit in the repository's history. ``promoted`` is not terminal; it
moves on to ``delivered``.

**``annotate`` adds a note, finding, assessment or lineage; it is permitted on every idea,
terminal included** — it extends the record, not the state machine. A non-owner ``--author``
(an agent) is restricted to ``--kind finding``, so the owner's own voice in the log stays
unambiguous. ``amend-annotation`` corrects one annotation's text by its own ``eid`` (printed
when it was written); it never touches the others.

**``link`` asserts a typed, one-directional edge to another idea** — ``extends``,
``supersedes``, ``relates_to`` or ``component_of`` — and never mutates it afterward.
``--target-code`` points an ``extends`` or ``relates_to`` edge at a governed document instead;
the code must exist. ``retract-link`` is the one legal amendment: it clears the target by the
link's own ``eid``, so the retraction is recorded rather than the edge being silently repointed
or deleted. An ``extends`` cycle or a ``supersedes`` edge whose target is not ``discarded`` is
flagged to stderr, never refused — capture always wins.

**``classify`` records an idea's record kind and axis values**, read as a JSON object from
``--file`` or stdin, so reasons never pass through a shell argument. The latest classification
wins; an earlier one stays in the log. Any author may classify.

**Prose never belongs in a shell argument.** A ``--title``, ``--body`` or ``--text`` containing a
backtick or ``$(`` is evaluated by the calling shell before this script sees it, and the log
keeps whatever the shell produced. ``--file`` (or plain stdin) never puts prose in a shell
argument at all. Prefer it for anything longer than a short, plain-text title.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--title` | one-line summary; omit to read title and body together (see --file) |  |  |  |
| `--body` | the idea in full; read from stdin when omitted |  |  |  |
| `--file` | read the title (first line) and body (the rest) from a file — bypasses the shell entirely, so it is the safe route for prose that might contain backticks, $(...), quotes or newlines |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `to` |  |  |  |  |
| `--promoted-to` | one or more governed document codes, required when promoting |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--title` | the corrected title |  |  |  |
| `--body` | the corrected body |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--author` |  |  |  | yes |
| `--kind` |  |  |  | yes |
| `--text` | the contribution itself, for short plain text |  |  |  |
| `--file` | read the contribution from a file |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `eid` | identity of the annotation to correct |  |  |  |
| `--text` | the corrected text, for short plain text |  |  |  |
| `--file` | read the corrected text from a file |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--type` |  |  |  | yes |
| `--target` | six-digit idea id this edge points to |  |  |  |
| `--target-code` | governed document code this edge points to; extends and relates_to only |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `eid` | identity of the link to retract |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--author` |  |  |  | yes |
| `--file` | a JSON object of classification fields; read from stdin when omitted |  |  |  |
| `--status` | only ideas in this status |  |  |  |
| `idea` | six-digit idea id |  |  |  |

Shared configuration flags: every configured path and value, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1.

## `idea_corpus.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py"
```

Build and check the files of an idea partition sweep: corpus, prompts, reports and draft.

The partition-ideas skill runs every step of a sweep through this script, so no step depends on
a command typed out by hand. The subcommands, in the order a sweep uses them:

    idea_corpus.py locate                       # where the sweep's files live; exit 1 if unsafe
    idea_corpus.py start                        # resume a sweep, or move an earlier one aside
    idea_corpus.py build [--status open,triaged] [--seed N] [--exclude ids.txt] [--stats]
    idea_corpus.py prompt R1                    # one pack section, filled in, saved as sent
    idea_corpus.py report R1 --file reply.md    # write an agent's returned report, stamped
    idea_corpus.py name <corpus date>           # the draft's markdown and record paths
    idea_corpus.py check <draft.md> <draft.json>
    idea_corpus.py accept <draft.md> <draft.json>

**Where things live.** Subagents run in the primary checkout, whatever worktree the coordinator
is in, so every file an agent reads is in the primary checkout's staging directory
(``staging_dir``): the corpus, the reports and the synthesis draft. The primary checkout is the
first entry of ``git worktree list``. ``prompt`` fills each pack section with absolute paths
there, so the second audit reads the draft at a path it can open. The accepted partition is
copied by ``accept`` into ``partitions_dir`` in the current checkout, where it can be committed.

**The staging directory must be gitignored.** ``locate`` exits 1 when it is not, and every
subcommand that writes into it refuses to. ``locate`` also prints a digest of the primary
checkout's ``git status``; the skill compares it before and after its writes there.

**The corpus.** ``build`` selects the ideas whose folded status is in ``--status`` (one status or
a comma-separated list, default ``triaged``), minus the ids an optional ``--exclude`` file lists
(one six-digit id per line, ``#`` comments allowed; no file means no exclusions). It writes two
files that differ only in what they carry, so the control analyst cannot tell its input differs:

    corpus-R1.md   title, body, links, findings
    corpus-R4.md   title, body, links           <- the control

and ``manifest.json``: the corpus size, the status selection, the excluded ids, the ideas with
more than one finding, and a random seed that identifies the build. "Findings" are every
annotation of kind ``finding``, any author, in time order. ``--stats`` prints the manifest and
writes nothing.

**The run stamp.** Every file the sweep writes into the corpus directory, and the draft markdown,
starts with a stamp naming the build it belongs to. That is how ``start`` tells this sweep's
output from an earlier sweep's file at the same path.

Nothing here writes the idea log.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--status` | status or comma-separated statuses to select (default: triaged) |  |  |  |
| `--seed` | the build's seed; drawn at random if omitted |  |  |  |
| `--out` | output directory (default: <staging>/corpus in the primary checkout) |  |  |  |
| `--exclude` | file of idea ids to leave out, one per line; none by default |  |  |  |
| `--stats` | print the manifest; write nothing |  |  |  |
| `section` |  |  |  |  |
| `--draft` | the synthesis draft (S and A2) |  |  |  |
| `section` |  |  |  |  |
| `--file` | the returned text |  |  | yes |
| `date` | the corpus date, from locate |  |  |  |
| `markdown` |  |  |  |  |
| `record` |  |  |  |  |
| `markdown` |  |  |  |  |
| `record` |  |  |  |  |

Shared configuration flags: every configured path and value, resolved by the shared configuration precedence rule.

Exit codes found in source: 0, 1.

## `ideas.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/ideas.py"
```

The one replay of the idea log: load its events and fold them into current state.

Imported by the writer (``idea.py``, which folds the log before every append), the renderer
(``render_ideas.py``) and the ideas check (``checks/ideas.py``). Every reader of idea state goes
through ``fold``; reading the raw log shows pre-amendment text and skips the history rules.

The log path is always an argument. The one path this module derives itself is the plugin's own
schema, where the transition table is declared.

No command-line arguments.

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

## `regression.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/regression.py"
```

Fail when a phase silently leaves ``status: complete`` in the backlog.

Every other backlog rule reads the current catalog alone, so none of them can see a phase moving
backwards — a backlog rewritten from a stale copy, reverting finished phases and deleting their
``session``, ``completion_evidence`` and ``result``, passes them all. This check compares the
current catalog with a prior committed state.

**Two bases, two severities:**

- ``HEAD`` catches a bad edit before it is committed, in the tree that makes it. A finding here
  is an **error**.
- The integration branch catches the same regression arriving by rebase or merge, which
  ``HEAD`` structurally cannot see. It cannot be a hard failure: every branch that legitimately
  completes a phase differs from the integration branch by exactly the transition this check
  looks for. A finding here is a **warning** that never changes the exit code.

**The escape hatch is a grep, not a parse** (``is_recorded``): the check looks for the phase id
as a whole identifier in the working copy of the decisions document and not in the version
committed at the comparison ref — i.e. the entry was added by this change. The goal is to force
the reason for a reopen to be written down somewhere durable, not to validate its shape.

**The decisions document is the one the catalog's ``decision_record`` names**, resolved to a
path by the caller through the document scan, never a literal filename. A catalog without
``decision_record`` has no escape hatch, so the caller does not run this check and says so.

**An unreadable prior state is not a failure.** ``git show <ref>:<path>`` fails during a rebase,
in a shallow clone, on the initial commit, or when ``ref`` itself does not exist. All of these
mean no comparison is possible: skip that base, note it in one line, and let the other base run.

No command-line arguments.

## `render_ideas.py`

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/render_ideas.py"
```

Render the Markdown view of the idea log, priority queue first.

The log is the source; the view is generated from it. Rendering is deterministic: the same log
and priority file produce the same bytes, which is what lets ``check`` treat a hand edit as a
failure rather than a merge.

    render_ideas.py           # write the view
    render_ideas.py --check   # exit 1 if the committed view differs from a fresh render

The header is the text the scaffold seeds, so an empty log renders to exactly the seeded file.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--check` | fail if the view is stale |  |  |  |

Shared configuration flags: every configured path and value, resolved by the shared configuration precedence rule.

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
