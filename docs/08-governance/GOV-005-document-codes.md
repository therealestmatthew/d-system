---
schema_version: 1
id: doc-document-code-protocol
code: GOV-005
title: Document code assignment protocol
kind: governance
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-21'
systems: [sys-governance]
depends_on: [doc-governance-protocol, doc-adr-document-codes]
---

# Document code assignment protocol

Every governed document carries a permanent `code` from the series registered for its kind. The
code is also the filename prefix. The rationale is in [ADR-006](../04-decisions/ADR-006-document-codes.md);
this document states the rules.

## Series

[codes.yaml](codes.yaml) is the only source of truth for prefix, numbering mode and permitted
locations. Do not duplicate this table in code.

| Series | Kind | Location | Numbering | Sub-codes |
|---|---|---|---|---|
| `PLAN` | plan | `docs/01-plans/` | counter | yes |
| `ADR` | adr | `docs/04-decisions/` | counter | no |
| `ARCH` | architecture | `docs/07-architecture/` | counter | no |
| `REQ` | requirement | `docs/06-requirements/` | counter | no |
| `PROMPT` | prompt | `docs/02-prompts/` | counter | no |
| `OPS` | operation | `docs/08-governance/` | counter | no |
| `GOV` | governance | `docs/08-governance/` | counter | no |
| `SESS` | session | `docs/03-sessions/` | dated | no |
| `WALK` | walkthrough | `docs/03-sessions/` | dated | no |

Counter codes read `PLAN-004`, with an optional two-digit sub-code as `PLAN-003.01`. Dated codes
read `SESS-2026-09-05-01`: the document's own `created` date, then a same-day sequence.

## Assigning a code

```bash
uv run python -m src.governance --next-code adr
uv run python -m src.governance --next-code plan --parent doc-html-00-overview
uv run python -m src.governance --next-code session
```

The command prints one code and nothing else. Put it in `code`, name the file `<code>-<slug>.md`,
and place it under a registered location. Never choose a code by reading the directory yourself; the
command also accounts for reservations and retirements, which a listing does not show.

`next(series)` is the highest number among governed documents, reservations and retirements, plus
one. `next(parent)` is the highest existing sub-code of that parent, plus one. A dated code takes
the lowest unused sequence for its date. Each is a pure function of committed state, so two agents
on the same commit compute the same answer.

## Multi-file plans

A plan set lives in a folder named for the parent code: `docs/01-plans/PLAN-003-dynamic-html-generation/`.
The overview holds the parent code; each child holds a sub-code and a `parent` pointing at the
overview. The sub-code and the `parent` field must imply each other — a sub-code without a parent
fails, and a child plan with a top-level code fails.

A plan set large enough that its children group into themes may put those children one level
deeper, inside an **area folder**. An area folder is named for the reader — `The Idea Lifecycle/`
— not for a code, because it labels a theme rather than holding one. Three rules bound it: the
plan folder above it still announces the parent code, only a sub-coded child may sit inside one,
and the nesting stops there. The overview stays at the plan folder's root, beside the area folders
rather than within one, so the entry point to a plan set is always in the same place.

Most plan sets do not need this. Reach for an area folder when the child list has become long
enough that a reader cannot see its shape, and not before — a flat folder is the cheaper default
and `PLAN-003` remains the worked example of one.

## Reservations and retirements

Reserve a code when the document is planned but not yet written, typically when a backlog phase names
it as a deliverable. Record it under `reserved` with the reason and the claiming phase. Allocation
skips reserved codes, and using one fails until the reservation is removed in the same change that
adds the document.

Retire a code when its document is deleted. Record it under `retired`; it is never reissued, so no
later document can inherit a withdrawn number's history.

## Permanence

A code is never reused and never renumbered once it reaches `main`. Superseded and deprecated
documents keep theirs — the code identifies the document, not its lifecycle state. Renaming a
document's slug is fine; changing its code is not.

## Concurrent agents

`--next-code` does not just compute a free code; it **takes** it. Computing and taking are one
operation from a peer's point of view, because anything less is the defect: an allocator that reads
only committed state gives two worktrees the same answer, and they find out at merge.

### Two different things are called a reservation

They are unrelated, and confusing them will waste an afternoon.

| | **Register reservation** (`codes.yaml`) | **Pre-merge reservation** (allocation-time) |
|---|---|---|
| Lives in | `reserved:` in `codes.yaml`, tracked and committed | `<git common dir>/code-reservations/`, untracked |
| Lasts | Until the document is written, often weeks | Minutes, between `--next-code` and the document |
| Declares | "This planned document owns this code" | "An allocation is in flight; do not hand this out" |
| Written by | A person, deliberately, with a reason and a phase | `--next-code`, automatically |
| Survives a clone | Yes | No, and it should not |

The rest of this section is about the second kind. The first is described under *Reservations and
retirements* above and is unchanged.

### How a pre-merge reservation works

Each allocation creates one file named for the code, using `O_CREAT | O_EXCL`. The kernel admits
exactly one creator, so of two agents racing for `SESS-2026-09-21-01` exactly one is told it has it
and the other retries with `-02`. There is no lock file and nothing to repair after a crash.

The store sits in the **git common directory** — what `git rev-parse --git-common-dir` resolves to,
which is the same `.git` from the primary checkout and from every linked worktree. That is the only
place a reservation can live and still satisfy [REQ-013](../06-requirements/REQ-013-concurrency-git-safety.md)
R05's requirement that it be visible to the second caller *before the first has merged*:

- a tracked file is invisible until it merges, which is the defect restated;
- `codes.yaml` on `dev` cannot be written from a worktree at all, because a worktree cannot check
  out `dev` (`fatal: 'dev' is already used by worktree at ...`);
- `_tmpagent/` is tracked, so it has the first problem.

Being untracked and machine-local is correct rather than a compromise: a reservation is a statement
about work in flight on this machine, and it means nothing to a fresh clone.

### Releasing

**Expiry is the only automatic release.** Allocation prunes expired reservations before it
allocates, so an allocation abandoned without writing its document cannot hold a code forever. The
horizon is a fortnight, which only ever collects reservations whose session ended without writing.

Release one by hand when you allocated a code and decided not to write it:

```bash
uv run python -m src.governance --release-code SESS-2026-09-21-01
```

A reservation whose document *has* been written is deliberately left standing until it expires. The
obvious alternative — release it as soon as its code appears on a document — is unsafe, and was
built and removed during `phase-conc-03` rather than reasoned away:

> The scan walks the **local working tree**. An allocating worktree would therefore retire its own
> reservation while the document was still unmerged and invisible to every peer, and the next peer
> to allocate would be handed the same code — with nothing committed anywhere. That is the
> collision this mechanism exists to prevent, reopened by its own cleanup. It fires in ordinary
> single-machine use: a session that allocates a session code, writes the record, then allocates a
> second code for a plan or an ADR.

Leaving the reservation standing costs nothing, because the allocator would skip that code anyway
once the document carries it.

### What this replaces

Reserving the code in `codes.yaml` alongside the backlog claim was the standing workaround, and it
is no longer needed — it was a convention protecting against a mechanism defect, and the mechanism
is fixed. Doing it anyway is harmless, just redundant. Renumbering at integration remains the
correct response to a duplicate-code error, for the two cases this does not cover: two agents on
**different machines**, which share no git directory; or an allocation whose reservation expired
before its document was written, which takes a fortnight.

Codes stay free before merge and permanent after, and the register plus
`uv run python -m src.governance` remain the ledger and the check, exactly as
[ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md) treats the backlog.

Dated series do not contend across days, and contend within a day only between agents finishing on
that day — which is precisely when session codes collide, and why this repository renumbered a
session record twice before the mechanism existed.

## The catalog

[catalog.md](catalog.md) is generated by `--catalog` and committed so it can be read without a
checkout. Never edit it by hand. CI regenerates it into a temporary file and diffs, so a stale
catalog is a build failure rather than silent misinformation. Regenerate with:

```bash
uv run python -m src.governance --catalog
```

The flag writes the file directly — only when the audit is clean — and also prints it, so the
command above is complete on its own; no redirect is needed.
