---
schema_version: 1
id: doc-confidentiality-sweep
code: PLAN-006
title: Separate structure from content before the first remote push
kind: plan
status: complete
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-09'
completion_evidence:
- docs/03-sessions/SESS-2026-09-08-12-scrub-tracked-structure.md
- docs/03-sessions/SESS-2026-09-08-13-relocate-portfolio.md
- docs/03-sessions/SESS-2026-09-08-14-leak-check.md
- docs/03-sessions/SESS-2026-09-08-15-purge-course-identifier.md
- docs/03-sessions/SESS-2026-09-09-01-history-rewrite-and-remote.md
- tools/check_no_private_content.py
- test/test_private_content.py
systems: [sys-portfolio, sys-governance, sys-brain, sys-projection, sys-retrieval, sys-delivery]
depends_on: [doc-governance-protocol]
---

# Separate structure from content before the first remote push

## Context and scope

This repository has never been pushed. `git remote -v` is empty and all 15 commits are local, so
nothing has leaked and history is still free to rewrite at zero cost. That window closes at the
first push, and rewriting after a push means force-pushing over a published history and hoping no
one cloned or forked it in between.

The goal is that the remote carries the **system** — schemas, governance, tooling, the agent
workflow — and not the owner's portfolio content.

### Audit findings

Good news first. There are no credentials, keys or tokens in any tracked file: the three
secret-shaped matches are a path-traversal test case and two governance test fixtures. `_private/`
is gitignored and holds nothing tracked. Brain memories are all architectural concepts with no
personal content. No stakeholder records exist, so no third-party names are exposed. Only one file
has ever been deleted from history, and that was a rename during the code-system work.

The exposure is real but bounded, and it is **not confined to `_data/`**:

| Location | What it exposes |
|---|---|
| `_data/projects/*.json` (33 files) | Real project names, 33 descriptions, 8 notes. Includes three named client engagements, personal finances, health and a side gig |
| `_data/tags.json` | A client identifier as a first-class tag in the `client` category |
| `README.md` lines 115–116 | Eleven real project IDs listed by name, including client and side-gig work |
| `docs/07-architecture/ARCH-001-tagging-system.md` | The client identifier used as a worked example |
| `brain/concepts/tag-taxonomy.md`, `brain/index.md` | The client identifier in memory content |
| `tools/load_context.py` line 8 | A real client project ID in the usage docstring |

The last four matter most, because a plan that only gitignores `_data/` would leave the client name
in documentation, a memory and a source file — and would feel complete while doing so.

Personal categories are as sensitive as client ones. Of 33 projects, 12 are `system`, 10 `work`,
7 `personal` and 4 `learning`; the personal set covers finances, debt and health.

### Out of scope

Auditing `_private/` contents, choosing a hosting provider or its visibility setting, and any
retroactive licensing decision.

## Push gate

**No remote is added and nothing is pushed until `phase-priv-05` completes.** This holds even for
a private remote. Rewriting local history costs nothing today; rewriting after any push means
force-pushing over published refs, and unreachable objects can survive server-side until garbage
collection.

**Resolved 2026-09-09.** `phase-priv-05` completed: history was squashed to a single commit,
verified against every acceptance condition, and only then pushed to `origin`. The gate above has
done its job and no longer applies — the current publishing rule lives in `AGENTS.md`'s
*Confidentiality and publishing* section, which now reads "ask before pushing" rather than "never
push". This paragraph is kept as the record of why the gate existed; see
`docs/03-sessions/SESS-2026-09-09-01-history-rewrite-and-remote.md`.

The sweep is not sequenced ahead of the capture and reliability work — those proceed locally. It
gates *publishing*, not building. If a remote becomes urgent before the sweep is done, that is a
decision to revisit deliberately, not to make by habit.

## The tension to settle

`docs/08-governance/GOV-001-protocol.md` names `_data/` as the git-tracked source of truth, and
`sys-portfolio` lists `_data/projects` and `_data/tags.json` as existence-checked paths. The
governance validator reads `_data/tags.json` and `_data/projects/*.json` to resolve tag and project
references in documents and memories, and `tools/rebuild_db.py` loads the projection from there.

So `_data/` cannot simply be gitignored. A fresh clone would fail its own governance check with
`sys-portfolio: missing path _data/projects`, and CI would be red on arrival — the first thing a
reader sees. Whatever is decided has to keep a fresh clone green.

## Recommended approach

**Relocate the real portfolio rather than hiding it in place.** Real records move to
`_private/portfolio/`, which is already gitignored. `_data/` stays tracked and keeps its role in the
protocol, but holds a small fictional portfolio that exercises every schema. A `D_SYSTEM_DATA_ROOT`
environment variable, defaulting to `_data/`, points the loader, the validator and the retrieval CLI
at the real records on the owner's machine.

The alternative — gitignore `_data/` and track `_data.example/` — was considered and is weaker on
the point that matters. It leaves real files sitting at a path the tooling expects and `.gitignore`
merely excludes, so one `git add -f`, one careless `.gitignore` edit or one tool that writes there
re-exposes everything. Moving the content to a different path removes the failure mode instead of
guarding it, and a fresh clone needs no bootstrap step.

Trade-off, stated plainly: the owner runs with an env var set, and two data roots exist. That is the
price of the tracked tree never containing real content at any commit.

## Work and dependencies

Five phases, tracked as `phase-priv-*`. Phases 1–4 are ordinary work; **phase 5 must be last** and
must not run until 1–4 are merged and verified.

### Phase 1 — decide and record the boundary

Write the ADR ([ADR-009](../04-decisions/ADR-009-structure-content-boundary.md)) defining what is structure and what is content, why the
portfolio relocates rather than hides, and the fresh-clone-stays-green constraint. Amend
`GOV-001-protocol.md` where it calls `_data/` the source of truth, so the protocol and the code agree
rather than contradicting each other.

### Phase 2 — scrub identifiers from tracked structure

Remove client and personal identifiers from `README.md`, `ARCH-001-tagging-system.md`,
`brain/concepts/tag-taxonomy.md`, `brain/index.md` and `tools/load_context.py`. Replace the real
project list in the README with counts by category, and use fictional IDs in every example. Replace
the `client` tag with a generic identifier, keeping the category so the taxonomy shape survives.

Grep is the acceptance test, not judgment: no tracked file may match the client identifier, and no
tracked file outside `_private/` may match a real project ID.

### Phase 3 — relocate the portfolio and seed the example set

Move the 33 real project files and `tags.json`'s client entries to `_private/portfolio/`. Write a
fictional portfolio into `_data/` covering every schema field in use, including at least one person
and one commitment with tasks — which the existing tree has never had, so this also gives the
`phase-sig-*` and `phase-syn-*` tracks something to develop against.

Add `D_SYSTEM_DATA_ROOT` support to `tools/rebuild_db.py`, `tools/load_context.py` and the
governance validator, defaulting to `_data/` so CI is unaffected. Verify the owner's real data still
rebuilds from `_private/portfolio/`.

### Phase 4 — harden the ignore rules and add a leak check

Extend `.gitignore` to cover the new private paths explicitly rather than relying on `_private/`
alone. Add a `tools/check_no_private_content.py` that fails when a tracked file matches the
confidential-identifier list, and wire it into CI and a `pre-commit` hook.

A rule that only lives in `.gitignore` protects against accident, not against `git add -f`. The
check is what makes the boundary enforceable.

### Phase 5 — rewrite history, then push

The first four phases clean the working tree. History still contains every real project file across
36 file-touches and the identifiers in `README.md` and `brain/`, and `git log -p` would surface all
of it on the remote.

**Recommended: squash to a single initial commit.** Verifiable in one command, no residue possible,
and no dependency on an external tool. The cost is 15 commit messages — acceptable here precisely
because this repository records its reasoning in ADRs and session documents rather than in commit
messages, which is the whole point of the governance system.

**Alternative if history must survive:** `uv pip install git-filter-repo`, then purge `_data/` by
path and scrub the identifier strings by content in the same pass. More faithful, more moving parts,
and it demands verification that the content filter caught every variant and casing.

Either way, before adding a remote: confirm `git log --all --name-only` names no private path, and
`git grep -i` over every commit finds no identifier. Add the remote only after that passes.

## Acceptance and verification

```bash
uv run python -m src.governance          # fresh-clone equivalence: must exit 0 unmodified
uv run python tools/rebuild_db.py        # must build from the fictional set
uv run pytest
uv run python tools/check_no_private_content.py
git grep -Ii -e "<client-id>" -- .       # must return nothing
git log --all --name-only | grep -c "_data/projects"   # must be 0 after phase 5
```

The decisive test is a clone into a clean directory with no environment variables set: governance
exits 0, tests pass, the database rebuilds, and nothing in the tree or its history names a real
client, project or personal concern.

## Open questions

- Whether the remote should be private regardless. This plan makes the repository *safe* to publish;
  it does not argue that it *should* be. A private remote plus these measures is the stronger
  position, since the sweep then protects against a future visibility change rather than being the
  only thing standing between the content and the public.
- Whether the fictional portfolio should be generated or hand-written. Hand-written reads better in
  a README; generated is easier to keep exercising new schema fields.
- Whether `_public/` should hold a sanitized export of real portfolio structure, which is what the
  directory was created for and currently holds only a `.gitkeep`.
