# Repository layout

The files and directories the idea-realization features create or read in a repository, where each
lives by default, and why it exists. Every path marked *configurable* is a plugin option; the
tools reference (`docs/tools.md`) states how a configured value is resolved. Paths are relative to
the repository root.

The `scaffold` skill creates what each feature needs and never overwrites a file that exists.

## The tree

```
<repository>/
├── ideas/
│   ├── ideas.jsonl          idea log (ideas_path)
│   ├── ideas.md             rendered view of the log (ideas_view_path)
│   ├── priority.yaml        ideas that jump the queue (priority_path)
│   └── partitions/          accepted idea partitions (partitions_dir)
├── backlog/
│   └── backlog.yaml         phase catalog and lock table (backlog_path)
├── docs/                    document root (docs_root)
│   ├── codes.yaml           code register
│   ├── systems.yaml         systems registry and owner directory
│   ├── catalog.md           generated catalog of every governed document
│   ├── plans/               PLAN documents, and PLAN folders for multi-file plans
│   ├── requirements/        REQ documents
│   ├── decisions/           ADR documents
│   ├── architecture/        ARCH documents
│   ├── prompts/             PROMPT documents
│   ├── governance/          GOV and OPS documents
│   └── sessions/            SESS and WALK records
├── agent-workflows/         optional: workflow manifest and sources
└── .idea-realization/
    ├── install-state.json   what the scaffold wrote, with hashes
    ├── schemas/             copies of the plugin's schemas
    └── staging/             partition drafts and corpora (staging_dir), gitignored

<repository>-worktrees/      one worktree per session (worktree_dir), outside the repository
```

## Why each exists

**`ideas/`** — The idea log is append-only: every capture, status move, amendment, annotation and
link is one event line, and the current state is replayed from them, so nothing is ever edited in
place. The rendered view is generated from the log and never edited by hand. The priority file is
the one hand-ordered list: ideas that should be looked at before the rest. `partitions/` holds
each partition the owner accepted at the end of a partition sweep: its markdown and its JSON
record, copied there from the staging directory so they can be committed. It is not under the
document root, because a partition is not a governed document.

**`backlog/backlog.yaml`** — The phase catalog. Each phase fits one session and declares the
systems and paths it will touch; on the integration branch this file is also the lock table that
concurrent sessions read before claiming. The queue at its front (`next_up`) overrides priority.

**The document root** — Governed documents carry YAML front matter with a code. Each document
kind has a series in `codes.yaml`, which fixes its code prefix, its numbering (a counter, or the
document's date plus a same-day sequence) and the folders it may live in. A code is allocated
with `next-code`, never chosen by hand, and a code's file name starts with it. Most series put
the allocating developer's handle in the code (`document-codes.md`). A plan
that spans several files lives in a folder named for its code, with child plans taking dotted
sub-codes. `systems.yaml` names the independently changeable parts of the repository and the
owners accountable for them; documents and phases refer to both. `catalog.md` is generated and
checked, never edited. Markdown files that are not governed documents, such as a folder's
`README.md`, are listed in the `exempt_files` option.

**`agent-workflows/`** — Present only when the repository renders its own host adapters with
`generate_workflows.py`: a manifest (start from the plugin's `templates/workflows.yaml`) and one
Markdown source per workflow. The adapters it writes under `.claude/`, `.agents/` or `.codex/` are
generated and never edited by hand.

**`.idea-realization/`** — The plugin's own state in the repository. `install-state.json` records
every file the scaffold wrote, and whether the plugin or the repository owns it, so the `doctor`
skill can report a stale schema copy or a missing file. `schemas/` holds copies of the plugin's
schemas for people and other tools; the plugin's scripts validate against their own, and
`scaffold.py --refresh-schemas` brings the copies back in line after a plugin update.
`staging/` holds partition drafts and corpora and is added to `.gitignore` only with the person's
consent. A partition sweep writes there in the primary checkout, where its subagents run.

**The worktree directory** — Every session works in its own worktree on its own branch, outside the
repository so no scanner or test run walks a second copy. Pre-merge code reservations live under
the git common directory, which every worktree shares, so two sessions allocating the same kind of
document receive different codes before either merges.

## Phase ids

A phase id is `phase-<track>-<handle>-<NN>`: a short lowercase track prefix naming the stream of
work, the handle of the developer who adds the phase, and a two-digit sequence counting that
developer's phases in the track, allocated by hand as the next unused number. The handle keeps two
developers adding phases to one track offline from choosing the same id. An id without a handle,
written before handles, stays valid only when the backlog's `legacy_phase_ids` lists it; a new
id without a handle fails the check. Keep a table
of tracks, each with a one-line description, in a README beside the backlog, so a reader can tell
what a track prefix means without opening a plan.
