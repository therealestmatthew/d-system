---
schema_version: 1
id: doc-document-code-protocol
code: GOV-005
title: Document code assignment protocol
kind: governance
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
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

A code is never reused and never renumbered once it reaches `dev`. Superseded and deprecated
documents keep theirs — the code identifies the document, not its lifecycle state. Renaming a
document's slug is fine; changing its code is not.

## Concurrent agents

The register on `dev` is the ledger and `uv run python -m src.governance` is the check, exactly as
[ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md) treats the backlog. Two agents that
independently take the same counter code collide at the second agent's post-rebase run, as a
duplicate-code error naming both files.

The later-integrating agent renumbers. Codes are free before merge and permanent after, so this
costs one edit and never rewrites history. An agent that knows it will write a document should
reserve the code in the same small commit as its backlog claim, which removes the race entirely.

Dated series do not contend across days, and contend within a day only between agents finishing on
that day.

## The catalog

[catalog.md](catalog.md) is generated by `--catalog` and committed so it can be read without a
checkout. Never edit it by hand. CI regenerates it into a temporary file and diffs, so a stale
catalog is a build failure rather than silent misinformation. Regenerate with:

```bash
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
```
